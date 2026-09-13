# DevOps Pipelines — Reference

Reference doc for the CI/CD, provisioning, orchestration and monitoring
setup. Purpose: a single page a marker or new team member can read before
diving into any specific file.

---

## Fleet topology

| EC2 role | How many | What runs on it | Provisioned by |
|---|---|---|---|
| **Jenkins** | 1 | Jenkins server (agent = master, single-node) | Manual |
| **Staging** | 1 | Application (Compose, single-node) + monitoring exporters | `Jenkinsfile.provision-staging` |
| **Prod swarm manager** | 1 | Docker Swarm manager + application `db` + central monitoring (Prometheus, Loki, blackbox, node_exporter, promtail) | `Jenkinsfile.provision-prod` |
| **Prod swarm workers** | 2+ | Docker Swarm workers + application `backend`/`frontend` + monitoring exporters | `Jenkinsfile.provision-prod` |
| **Grafana** | 1 | Grafana ONLY (dedicated observability box) — queries Prometheus + Loki on prod manager over the VPC | `Jenkinsfile.provision-monitoring` |

Jenkins and every target EC2 are in the **same AWS VPC** so Jenkins reaches
all hosts via **private IP** (no `_PUBLIC_IP` params).

---

## The four Jenkins pipelines

| Jenkinsfile | Purpose | Trigger | Target hosts read from |
|---|---|---|---|
| `Jenkinsfile` | **Main CI/CD** — tests, builds, publishes images to ECR, deploys to staging AND prod | GitHub webhook (`push`) OR manual | `ansible/inventories/{staging,prod}.ini` |
| `Jenkinsfile.provision-staging` | **Provision** a fresh staging EC2 | GitHub webhook OR manual | `ansible/inventories/staging.ini` |
| `Jenkinsfile.provision-prod` | **Provision** a fresh (or grow an existing) prod fleet: 1 manager + N workers | GitHub webhook OR manual | `ansible/inventories/prod.ini` |
| `Jenkinsfile.provision-monitoring` | **Provision** the dedicated Grafana EC2 | GitHub webhook OR manual | `ansible/inventories/monitoring.ini` (+ `prod.ini` for datasource lookup) |

### Adding / replacing a host

Edit the private IP in the relevant inventory file, commit + push, and the
corresponding provision pipeline re-runs. Playbooks are idempotent — hosts
that are already provisioned are skipped, new hosts are set up.

### `Jenkinsfile` — main CI/CD (13 stages)

```
Checkout → Validate Repo → Show Info → Backend Tests → Controlled Failure Gate
  → Frontend Build → Docker Build → Playwright E2E → Publish to ECR
  → Validate Staging Connectivity → Deploy to Staging
  → Validate Production Connectivity → Deploy to Production
```

Params:

| Param | Default | Effect |
|---|---|---|
| `DEMO_INTENTIONAL_FAILURE` | `false` | Runs a test designed to fail. Proves a bad commit blocks staging + prod. |
| `DEMO_STAGING_HEALTH_FAILURE` | `false` | Deploys staging with a broken `ALLOWED_HOSTS`. Django rejects the health probe → staging goes red → prod stages skipped. |

Target hosts: no IP params — the pipeline reads
`ansible/inventories/staging.ini` for the `Deploy to Staging` stage and
`ansible/inventories/prod.ini` for the `Deploy to Production` stage.
To repoint at a different EC2, edit the inventory and push.

Failure handling in `post {}`:
- `failure` → sends HTML email + attached log to `personal-email-recipients` (TODO before submission: swap to `jenkins-failure-email-recipients`).
- `fixed` → sends "green again" email.

### `Jenkinsfile.provision-staging` (5 stages)

1. Checkout
2. Verify SSH to `[staging]`
3. `setup-hosts.yml`      — Docker + Compose plugin
4. `init-swarm.yml`       — single-node swarm (advertise_addr defaults to `ansible_host` / private IP)
5. `monitoring.yml`       — `role=exporters env=staging`; promtail ships logs to prod-manager Loki

### `Jenkinsfile.provision-prod` (9 stages)

1. Checkout
2. Verify SSH to `[production]` (manager + workers)
3. `setup-hosts.yml` on ALL hosts
4. `init-swarm.yml` on manager
5. Fetch manager private IP + worker join token
6. `join-swarm.yml` on `[swarm_workers]` (idempotent — already-joined workers skipped)
7. `monitoring.yml` `role=exporters env=prod` on `[swarm_workers]` (ships to manager Loki)
8. `monitoring.yml` `role=central env=prod` on `[swarm_manager]` (Prometheus + Loki + blackbox + node_exporter + promtail; passes prod.ini + staging.ini so scrape config includes both envs)
9. Verify `docker node ls` reports all nodes

Add a new worker: append to `[swarm_workers]` in `prod.ini`, push. The
pipeline re-runs, joins the new worker, installs its exporters, and
re-renders `prometheus.yml` on the manager so the scrape config includes it.

### `Jenkinsfile.provision-monitoring` (4 stages)

1. Checkout
2. Verify SSH to `[monitoring]`
3. `setup-hosts.yml`     — Docker + Compose plugin
4. `monitoring.yml` `role=grafana env=monitoring` — copies `compose.grafana.yml`, renders `datasources.yml.j2` with prod-manager private IP (looked up from prod.ini), copies dashboards, starts Grafana

Prerequisite: prod fleet must be provisioned first (Grafana needs Prometheus + Loki reachable).

---

## Ansible playbooks

| File | When it runs | What it does |
|---|---|---|
| `ansible/setup-hosts.yml` | Provision (once per host) | Docker, Docker Compose v2 plugin, adds ec2-user to docker group, creates workspace dir |
| `ansible/init-swarm.yml` | Provision (once per swarm manager / single-node staging) | `docker swarm init --advertise-addr <private-ip>`. Idempotent. |
| `ansible/join-swarm.yml` | Provision (once per prod worker) | Joins the manager using the worker token. Skips if already joined. |
| `ansible/monitoring.yml` | Provision (once per host) | Three roles: `central` (Prometheus + Loki + blackbox + node_exporter + promtail on prod manager), `exporters` (node_exporter + promtail on workers / staging), `grafana` (Grafana on the dedicated observability EC2). Also creates a 2 GB swap file. |
| `ansible/deploy-staging.yml` | Every app deploy | Copies `compose.staging.yml`, renders `.env`, `docker compose pull && up -d`, waits for `/healthz`. |
| `ansible/deploy-prod-swarm.yml` | Every app deploy | Copies `stack.prod.yml`, `docker stack deploy` with env vars, waits for services + `/healthz`. |
| `ansible/deploy-prod.yml` | Fallback only | Compose-based prod deploy. Kept for emergency redeploy. |

`hosts:` in every playbook is a variable that defaults to the expected
inventory group (`staging` / `swarm_manager` / `swarm_workers` / `monitoring`).
Pipelines pass `-e target_hosts=<group>` for explicitness.

### Inventory files

- `ansible/inventories/staging.ini` — `[staging]` group (private IPs)
- `ansible/inventories/prod.ini`    — `[swarm_manager]`, `[swarm_workers]`, `[production:children]`
- `ansible/inventories/monitoring.ini` — `[monitoring]` group (the dedicated Grafana box)

**Single source of truth**. Every pipeline + playbook reads private IPs
from here. `ansible/ansible.cfg` no longer sets a default inventory —
callers pass `-i` explicitly.

---

## Application stack files

| File | Deployed by | Orchestrator | Purpose |
|---|---|---|---|
| `compose.staging.yml` | `deploy-staging.yml` | Docker Compose | Staging — single-node |
| `stack.prod.yml` | `deploy-prod-swarm.yml` | **Docker Swarm** | Prod — 3-node swarm |
| `compose.prod.yml` | `deploy-prod.yml` (fallback) | Docker Compose | Compose fallback |
| `compose.yml` | (local dev only) | Docker Compose | Untouched — developer laptops |
| `compose.ci.yml` | Jenkinsfile Playwright stage | Docker Compose | Ephemeral env for E2E tests |

### `stack.prod.yml` — Swarm-specific notes

- No `container_name` — Swarm names containers itself.
- No `depends_on.condition: service_healthy` — Swarm ignores it.
- `restart: unless-stopped` moved to `deploy.restart_policy`.
- `deploy:` block per service: `replicas`, `restart_policy`, `update_config`, `rollback_config`, `placement.constraints`.
- `db` pinned to `node.role == manager`; `backend`/`frontend` pinned to `node.role == worker`.
- Network alias `rmit-store-backend` on the `backend` service so `client/nginx.conf`'s hardcoded `proxy_pass http://rmit-store-backend:8000;` works under swarm (where the actual service name is `backend`).

---

## Monitoring stack

| Component | Runs on | Purpose |
|---|---|---|
| Prometheus | Prod swarm manager | Scrapes node_exporter (all hosts) + blackbox probes |
| Loki | Prod swarm manager | Receives log pushes from every host's promtail |
| blackbox_exporter | Prod swarm manager | HTTP probes for `/healthz`, `/readyz`, `/api/version` |
| node_exporter | Every host | Host CPU/mem/disk metrics |
| promtail | Every host | Ships Docker container logs to Loki |
| **Grafana** | **Dedicated monitoring EC2** | Single UI serving both env dashboards; queries Prometheus + Loki over VPC |

### Layout

```
monitoring/
├── compose.monitoring.yml        Central stack (prometheus + loki + blackbox +
│                                  node_exporter + promtail). NOT grafana.
├── compose.grafana.yml           Grafana-only stack (for the dedicated EC2).
├── shared/
│   ├── loki-config.yml
│   ├── promtail-config.yml.j2    Rendered on prod manager with env=prod label
│   └── blackbox.yml
├── grafana/
│   ├── dashboards/{prod,staging}/{app-health,host-resources,logs}.json
│   └── provisioning/
│       ├── datasources/datasources.yml.j2   Templated — Prometheus + Loki URLs
│       │                                    embed prod-manager private IP
│       └── dashboards/dashboards.yml        Two providers: "RMIT Store Prod"
│                                            + "RMIT Store Staging" folders
├── prod/prometheus.yml.j2        Rendered on prod manager — scrapes prod
│                                  workers (from prod.ini) + staging (from
│                                  staging.ini)
└── exporters/
    ├── compose.exporters.yml     node_exporter + promtail
    └── promtail-config.yml.j2    Rendered per env; ships to prod-manager Loki
```

### Grafana dashboards

Two folders in Grafana, each filtered by `env`:

- `RMIT Store Prod` — `{env="prod"}` in every panel
- `RMIT Store Staging` — `{env="staging"}` in every panel

Each folder has 3 dashboards: `app-health`, `host-resources`, `logs`.
Logs dashboard restricts `compose_service` to `backend|frontend|db` so
monitoring containers don't pollute application log tails.

### Runtime tuning (fits t3.small — 2 GB RAM)

- Prometheus: `24h` retention, `500MB` max, scrape interval `30s`, `mem_limit: 400m`
- Loki: filesystem, 24h retention, `mem_limit: 300m`
- Grafana: `mem_limit: 300m` (has its own EC2 now — could raise if needed)
- Promtail: `mem_limit: 100m`
- node_exporter / blackbox_exporter: `mem_limit: 40m` each

---

## Security group configuration

### Prod fleet SG (attached to manager + all workers)

**Self-referential** = source is the SG itself.

| Type | Protocol | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 2377 | self-SG | Swarm cluster management |
| Custom TCP | TCP | 7946 | self-SG | Node-to-node gossip |
| Custom UDP | UDP | 7946 | self-SG | Node-to-node gossip |
| Custom UDP | UDP | 4789 | self-SG | VXLAN overlay data plane |
| Custom TCP | TCP | 9100 | monitoring SG | Prometheus (on manager) scrapes node_exporter on workers; Grafana host doesn't scrape but the manager also needs to reach its own workers |
| Custom TCP | TCP | 3100 | self-SG | Workers' promtail push logs to manager's Loki |
| Custom TCP | TCP | 9090 | monitoring SG | Grafana reads Prometheus |
| Custom TCP | TCP | 3100 | monitoring SG | Grafana reads Loki |
| SSH | TCP | 22 | Jenkins SG | Jenkins runs Ansible playbooks |
| HTTP | TCP | 80 | 0.0.0.0/0 | Public application access (via Swarm ingress) |
| Custom TCP | TCP | 9090 | your admin IP | Prometheus UI (debugging only) |

### Staging SG

| Type | Protocol | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 9100 | prod-manager SG | Central Prometheus scrapes staging node_exporter |
| Custom TCP | TCP | 80 | 0.0.0.0/0 | Public app + blackbox probes from prod manager |
| SSH | TCP | 22 | Jenkins SG | Ansible |

### Monitoring (Grafana) SG

| Type | Protocol | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 3000 | 0.0.0.0/0 (or your admin IP) | Grafana UI |
| SSH | TCP | 22 | Jenkins SG | Ansible |

Egress: to prod-manager SG on 9090 + 3100 (default allow-all egress is fine).

### Jenkins SG

Outbound: to every other SG on 22 (SSH). Inbound: 8080 from admin IP + GitHub webhook (open 8080 to 0.0.0.0/0 or GitHub's IP ranges).

### IAM role attached to each EC2

`LabRole` (or equivalent) with:
- `sts:GetCallerIdentity`
- `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer`
- `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` on `meowgang-media-staging-01`

Not needed on Grafana EC2 (doesn't pull ECR images or touch S3).

---

## Jenkins credential inventory

| Credential ID | Type | Purpose |
|---|---|---|
| `staging-ec2-ssh-key` | SSH private key | ec2-user login on ALL environments |
| `staging-postgres-password` | Secret text | Postgres password (same for staging + prod for now) |
| `staging-django-secret-key` | Secret text | Django SECRET_KEY |
| `jenkins-smtp-gmail` | Username with password | Gmail SMTP auth (App Password) |
| `personal-email-recipients` | Secret text | Failure emails during dev (personal Gmail) |
| `jenkins-failure-email-recipients` | Secret text | Failure emails in "prod" (team distribution list) |

---

## GitHub webhook → Jenkins

Every pipeline uses `triggers { githubPush() }`. GitHub POSTs to
`http://<jenkins-ip>:8080/github-webhook/` on every push and Jenkins
runs the matching jobs (matched by SCM URL + branch).

**IP stability**: allocate an **Elastic IP** to the Jenkins EC2 so
stop/start doesn't invalidate the webhook URL. In Learner Lab this is
free while the instance is running.

---

## Provisioning end-to-end (order matters)

Launch 4 EC2s (staging, prod-manager, prod-worker-1, prod-worker-2,
+ monitoring), each `t3.small`, Amazon Linux 2023, with the appropriate
SG (see matrix above). Note each host's **private** IP.

Edit the three inventory files with the current private IPs, commit + push. Then run the pipelines in this order:

1. `Configure-rmit-store-sever-staging` → Build (uses `staging.ini`)
2. `Configure-rmit-store-sever-prod` → Build (uses `prod.ini`)
3. `Configure-rmit-store-sever-monitoring` → Build (uses `monitoring.ini` + reads `prod.ini` for datasources)

Then any `push` to the app repo triggers `rmit-store-cicd` which deploys
the app to staging then prod.

Verify at the end:
- Grafana: `http://<monitoring-public-ip>:3000` (`admin` / `RmitMonitor2767!`)
- Both dashboard folders show data for their env
- App: `http://<prod-manager-public-ip>/` and `http://<staging-public-ip>/`

---

## Local Ansible testing (test.sh)

`test.sh` at the repo root reproduces every pipeline stage from your
laptop against fresh EC2s. Fill in the private IPs at the top, ensure
the SSH key is at `./meowgang-store-staging-key.pem`, then `./test.sh`.
If everything passes locally, the Jenkins pipelines will succeed too.

Note: `test.sh` runs from your laptop, which is OUTSIDE the VPC. It
falls back to public IPs for SSH connectivity, but private IPs for
scrape targets / promtail push URLs (via inventory). Jenkins runs
inside the VPC and uses private IPs everywhere.

---

## Known TODOs before submission

- Swap `personal-email-recipients` → `jenkins-failure-email-recipients` in `Jenkinsfile`'s `post { failure {} }` and `post { fixed {} }`.
- `stack.prod.yml` `AWS_STORAGE_BUCKET_NAME` still points at `meowgang-media-staging-01`. Provision a dedicated prod bucket.
- `STAGING_ALLOWED_HOSTS` / `PROD_ALLOWED_HOSTS` in `Jenkinsfile` still hardcode IPs. When an EC2 is replaced, Django will 400 on the health probe. Options: read from inventory at deploy time, or attach EIPs so the public IP never changes.
- `datasources.yml.j2` embeds prod-manager private IP at render time. If the manager EC2 is replaced, re-run `Jenkinsfile.provision-monitoring` to re-render Grafana's datasources.
