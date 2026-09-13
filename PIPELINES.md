# DevOps Pipelines — Reference

Reference doc for the CI/CD, provisioning, orchestration and monitoring
setup. Purpose: a single page a marker or new team member can read before
diving into any specific file.

---

## Fleet topology

| EC2 role | Count | What runs on it | Provisioned by |
|---|---|---|---|
| **Jenkins** | 1 | Jenkins server, single-node | Manual |
| **Staging** | 1 | Application (Docker Swarm, single-node) + `node_exporter` + `promtail` | `Jenkinsfile.provision-staging` |
| **Prod swarm manager** | 1 | Swarm manager + `db` container + central monitoring (Prometheus, Loki, blackbox, node_exporter, promtail) | `Jenkinsfile.provision-prod` |
| **Prod swarm workers** | 2+ | Swarm workers + `backend`/`frontend` + `node_exporter` + `promtail` | `Jenkinsfile.provision-prod` |
| **Grafana** | 1 | Grafana only (dedicated observability box) — queries Prometheus + Loki on prod-manager over the VPC | `Jenkinsfile.provision-monitoring` |

Jenkins and every target EC2 share the **same AWS VPC** so Jenkins reaches
all hosts via **private IP** (no `_PUBLIC_IP` params anywhere).

**Data flow:**
```
[staging]  [prod-worker-1]  [prod-worker-2]
promtail    promtail          promtail
   \___________|_______________/
               |  HTTP push :3100
               v
       [prod-manager]  <---- Prometheus scrapes node_exporter:9100 on every host
       - Loki:3100                 (self via Docker DNS + others via SG)
       - Prometheus:9090   <---- [Grafana EC2] queries via VPC private IP
       - blackbox:9115                          on :9090 (metrics) + :3100 (logs)
       - node_exporter                          User browser -> :3000 Grafana UI
```

---

## The four Jenkins pipelines

| Jenkinsfile | Purpose | Trigger | Reads inventory |
|---|---|---|---|
| `Jenkinsfile` | Main CI/CD — tests, builds, publishes images, deploys to staging AND prod | GitHub webhook OR manual | `inventories/{staging,prod}.ini` |
| `Jenkinsfile.provision-staging` | Provision staging EC2 | GitHub webhook OR manual | `inventories/staging.ini` + reads `prod.ini` (for Loki target) |
| `Jenkinsfile.provision-prod` | Provision (or grow) prod fleet: 1 manager + N workers | GitHub webhook OR manual | `inventories/prod.ini` + reads `staging.ini` (for scrape config) |
| `Jenkinsfile.provision-monitoring` | Provision Grafana EC2 | GitHub webhook OR manual | `inventories/monitoring.ini` + reads `prod.ini` (for datasource URLs) |

All 4 pipelines run automatically on every push to `main` (via `triggers { githubPush() }`).

### `Jenkinsfile` — main CI/CD

Stages:
```
Checkout → Validate Repo → Show Info → Backend Tests → Controlled Failure Gate
  → Frontend Build → Docker Build → Playwright E2E → Publish to ECR
  → Validate Staging Connectivity → Deploy to Staging
  → Validate Production Connectivity → Deploy to Production
```

Params:

| Param | Default | Effect |
|---|---|---|
| `DEMO_INTENTIONAL_FAILURE` | false | Runs a designed-to-fail test. Proves a bad commit blocks staging + prod. |
| `DEMO_STAGING_HEALTH_FAILURE` | false | Passes `-e allowed_hosts=badhost.example.com` to the staging deploy → Django rejects health probe → staging red → prod stages skipped. |

**No IP params.** Targets come from `ansible/inventories/{staging,prod}.ini`.
Edit inventory + push to repoint.

Post-block:
- `failure` → HTML email + attached log to `personal-email-recipients` (swap to `jenkins-failure-email-recipients` before submission)
- `fixed` → "green again" email

### `Jenkinsfile.provision-staging` (7 stages)

1. Checkout
2. Verify SSH to `[staging]`
3. Setup Host — `setup-hosts.yml` (Docker + Compose plugin + workspace)
4. Init Single-Node Swarm — `init-swarm.yml` (`advertise_addr` defaults to inventory `ansible_host` = private IP)
5. Fetch Prod Manager IP (Loki target) — reads `[swarm_manager]` from `prod.ini`
6. Deploy Monitoring Exporters — `monitoring.yml` `role=exporters env=staging` (node_exporter + promtail; promtail ships to prod-manager Loki using the IP from step 5)
7. Report

### `Jenkinsfile.provision-prod` (9 stages)

1. Checkout
2. Verify SSH to `[production]` (manager + workers)
3. Setup Hosts on ALL — `setup-hosts.yml`
4. Init Swarm on manager — `init-swarm.yml`
5. Fetch Manager IP + Join Token — reads `[swarm_manager]` from `prod.ini`, SSHes to grab worker token
6. Join Workers to Swarm — `join-swarm.yml` on `[swarm_workers]` (idempotent — already-joined workers skipped)
7. Deploy Exporters on Workers — `monitoring.yml` `role=exporters env=prod` (ships to manager Loki)
8. Deploy Central Monitoring on Manager — `monitoring.yml` `role=central env=prod`; passes prod.ini + staging.ini so `prometheus.yml.j2` renders scrape targets for both envs and both blackbox probe sets
9. Verify Fleet — `docker node ls` must report N+1 nodes

### `Jenkinsfile.provision-monitoring` (5 stages)

1. Checkout
2. Verify SSH to `[monitoring]`
3. Setup Host — `setup-hosts.yml`
4. Deploy Grafana — `monitoring.yml` `role=grafana env=monitoring`; passes monitoring.ini + prod.ini so `datasources.yml.j2` renders with prod-manager private IP baked in
5. Report

**Prerequisite:** prod fleet already provisioned (Grafana needs Prometheus + Loki reachable).

---

## End-to-end operation (from zero to running)

### One-time setup

1. **Launch 5 EC2s** — staging, prod-manager, prod-worker-1, prod-worker-2, grafana. All `t3.small`, Amazon Linux 2023, same VPC, same SSH key pair. Attach appropriate SG (see matrix below).
2. **Note each host's private IP.**
3. **Edit inventories** with the private IPs (see "Inventory files" below).
4. **Optional but recommended**: allocate **Elastic IPs** to Jenkins, prod-manager, staging, grafana so their public IPs survive stop/start. If you use EIPs, also set `public_ip=` in `staging.ini` and `prod.ini` so Django's `ALLOWED_HOSTS` includes them.
5. **git commit + push.** All four pipelines fire simultaneously via GitHub webhooks:

| Pipeline | Runs against |
|---|---|
| `Configure-rmit-store-sever-staging` | `[staging]` |
| `Configure-rmit-store-sever-prod` | `[swarm_manager]` + `[swarm_workers]` |
| `Configure-rmit-store-sever-monitoring` | `[monitoring]` |
| `Fork-rmit-store-cicd-new` (main) | staging then prod |

**Order matters only if the app deploy races the provision:** the main pipeline's `Deploy to Staging` stage assumes staging swarm is already initialised. On a totally cold start, disable the main pipeline's webhook trigger, run the 3 provision pipelines first, then enable the main pipeline and push again.

### Day-to-day operation (fleet already provisioned)

1. **Developer pushes code to `main`.**
2. GitHub webhook fires — Jenkins runs `Jenkinsfile`:
   - Tests → build images → push to ECR
   - Deploy to staging → wait for `/healthz` → deploy to prod → wait for `/healthz`
3. The 3 provision pipelines also run on every push (idempotent — they exit early if nothing changed on host).

### Adding a new prod worker

1. Launch new EC2 in same VPC + SG + key pair.
2. Append to `[swarm_workers]` in `ansible/inventories/prod.ini`:
   ```ini
   meowgang-prod-swarm-worker-3 ansible_host=<NEW_PRIVATE_IP>
   ```
3. Commit + push.
4. `Configure-rmit-store-sever-prod` re-runs:
   - Sets up Docker on the new host, skips existing
   - Joins new worker to swarm, skips existing
   - Installs exporters on new worker
   - Re-renders `prometheus.yml` on manager with new worker's scrape target
5. Grafana automatically picks up the new host (dashboards filter by `{env="prod"}`).

### Replacing an EC2 (e.g. stop/start rotated public IP)

1. If it's a **new** private IP: edit the relevant inventory file with the new value.
2. If just a **new** public IP: edit `public_ip=` in the inventory file (only staging + prod-manager need this for `ALLOWED_HOSTS`).
3. Commit + push. The right pipeline re-runs against the new IP.

Recommend allocating EIPs to skip step 2 forever.

### Regular deploy verifies success by

- `Deploy to Staging` waits for `curl http://127.0.0.1/healthz/` → 200
- `Deploy to Production` waits for `docker service ls` to show all replicas + `curl http://127.0.0.1/healthz/` → 200
- Blackbox probes from prod-manager confirm both envs' `/`, `/healthz`, `/readyz`, `/api/version` return 200 → visible on Grafana `App Health` dashboards

---

## Inventory files

Single source of truth. `ansible/ansible.cfg` sets no default inventory — every caller passes `-i` explicitly.

### `ansible/inventories/staging.ini`
```ini
[staging]
meowgang-store-staging ansible_host=<PRIVATE_IP> public_ip=<PUBLIC_IP>

[all:vars]
ansible_user=ec2-user
```
- `ansible_host` — REQUIRED. Jenkins SSHes here (VPC private).
- `public_ip` — OPTIONAL. Leave empty (`public_ip=`) and the deploy still succeeds: the container's `/healthz` check hits `127.0.0.1` which is always in `ALLOWED_HOSTS`. Only fill in when you need users to browse the app via the public IP without getting a Django HTTP 400 "Invalid HTTP_HOST", or want outbound email links (password reset, order confirmation) to point at the real public URL. Recommend allocating an EIP first so the value doesn't rotate.

### `ansible/inventories/prod.ini`
```ini
[swarm_manager]
meowgang-prod-swarm-manager ansible_host=<PRIVATE_IP> public_ip=<PUBLIC_IP>

[swarm_workers]
meowgang-prod-swarm-worker-1 ansible_host=<PRIVATE_IP>
meowgang-prod-swarm-worker-2 ansible_host=<PRIVATE_IP>

[production:children]
swarm_manager
swarm_workers

[all:vars]
ansible_user=ec2-user
```
- Only manager needs `public_ip` — same "optional" semantics as staging (see above). Workers never need it (swarm ingress lands on the manager).

### `ansible/inventories/monitoring.ini`
```ini
[monitoring]
meowgang-monitoring ansible_host=<PRIVATE_IP>

[all:vars]
ansible_user=ec2-user
```

---

## Ansible playbooks

| File | When it runs | What it does |
|---|---|---|
| `setup-hosts.yml` | Provision (per host) | Docker, Compose v2 plugin, ec2-user in docker group, workspace dir |
| `init-swarm.yml` | Provision (manager or staging) | `docker swarm init --advertise-addr <private-ip>`. Idempotent. |
| `join-swarm.yml` | Provision (each worker) | Joins the manager using the worker token. Skips if already joined. |
| `monitoring.yml` | Provision (per host) | 3 roles — `central` (Prometheus + Loki + blackbox + node_exporter + promtail on prod-manager), `exporters` (node_exporter + promtail on workers/staging), `grafana` (Grafana on the dedicated EC2). Also creates 2 GB swap. |
| `deploy-staging-swarm.yml` | Every app deploy | Copies `stack.staging.yml`, `docker stack deploy` with env vars from inventory, waits for services + `/healthz`. |
| `deploy-prod-swarm.yml` | Every app deploy | Same as staging, but with `stack.prod.yml`. |
| `deploy-staging.yml`, `deploy-prod.yml` | Fallback only | Compose-based deploy. Kept for emergency redeploy without Swarm. |

**ALLOWED_HOSTS + CLIENT_URL** are computed by the deploy playbooks from inventory:
```yaml
allowed_hosts: "127.0.0.1,localhost,{{ ansible_host }},{{ public_ip | default('') }}"
client_url: "http://{{ public_ip | default('localhost') }}"
```
Extra-var `-e allowed_hosts=...` overrides this (used by `DEMO_STAGING_HEALTH_FAILURE`).

---

## Application stack files

| File | Deployed by | Orchestrator | Purpose |
|---|---|---|---|
| `stack.staging.yml` | `deploy-staging-swarm.yml` | Docker Swarm | Staging (single-node swarm) |
| `stack.prod.yml` | `deploy-prod-swarm.yml` | Docker Swarm | Prod (multi-node swarm) |
| `compose.staging.yml`, `compose.prod.yml` | Fallback | Docker Compose | Emergency redeploy without Swarm |
| `compose.yml` | Local dev only | Docker Compose | Developer laptops |
| `compose.ci.yml` | Jenkinsfile Playwright stage | Docker Compose | Ephemeral E2E env |

### Swarm-specific notes

- `container_name` removed — Swarm names containers itself (`rmit-store_backend.1.<taskid>`).
- `depends_on.condition: service_healthy` removed — Swarm ignores it. Startup handled by healthchecks + restart_policy.
- `restart: unless-stopped` moved to `deploy.restart_policy`.
- `db` pinned to `node.role == manager` (its volume follows); `backend` + `frontend` pinned to `node.role == worker`.
- Network alias `rmit-store-backend` on the `backend` service so `client/nginx.conf`'s hardcoded `proxy_pass http://rmit-store-backend:8000;` works.

---

## Monitoring stack

| Component | Runs on | Role |
|---|---|---|
| Prometheus | Prod-manager | Scrapes node_exporter on every host + blackbox probes |
| Loki | Prod-manager | Receives log pushes from every host's promtail |
| blackbox_exporter | Prod-manager | HTTP probes for `/`, `/healthz`, `/readyz`, `/api/version` (both envs) |
| node_exporter | Every host | Host CPU/mem/disk |
| promtail | Every host | Ships Docker container logs to Loki |
| **Grafana** | **Dedicated monitoring EC2** | Single UI; queries Prometheus + Loki over VPC |

### Layout
```
monitoring/
├── compose.monitoring.yml       Central stack for prod-manager (prometheus,
│                                 loki, blackbox, node_exporter, promtail)
├── compose.grafana.yml          Grafana-only stack for the dedicated EC2
├── shared/
│   ├── loki-config.yml
│   ├── promtail-config.yml.j2   For central stack (ships to local loki)
│   └── blackbox.yml             Overrides Host header to 127.0.0.1
├── grafana/
│   ├── dashboards/{prod,staging}/{app-health,host-resources,logs}.json
│   └── provisioning/
│       ├── datasources/datasources.yml.j2   Templated — Prometheus + Loki
│       │                                     URLs = prod-manager private IP
│       └── dashboards/dashboards.yml        Two providers: "RMIT Store Prod"
│                                             + "RMIT Store Staging"
├── prod/prometheus.yml.j2       Rendered on prod-manager — scrape targets
│                                 for prod fleet + staging + blackbox probes
│                                 (with `component=frontend|backend` labels)
└── exporters/
    ├── compose.exporters.yml    node_exporter + promtail (workers, staging)
    └── promtail-config.yml.j2   Ships to prod-manager Loki
```

### Grafana dashboards

Two folders auto-provisioned from the two `dashboards.yml` providers:
- `RMIT Store Prod` — filter `{env="prod"}`
- `RMIT Store Staging` — filter `{env="staging"}`

Each folder has 3 dashboards:

- **`app-health`** — 4 gauges (Frontend `/`, Backend `/healthz`, `/readyz`, `/api/version`) + HTTP status table + probe latency
- **`host-resources`** — CPU %, memory %, disk %, load per host
- **`logs`** — dynamic dropdown of live containers (Loki `label_values({env=...}, container)` regex `^rmit.*`), single-select

### Runtime tuning (t3.small — 2 GB RAM budget)

- Prometheus: 24h retention, 500MB max, scrape 30s, `mem_limit: 400m`
- Loki: filesystem, 24h retention, `mem_limit: 300m`
- Grafana: `mem_limit: 300m`
- promtail: `mem_limit: 100m`
- node_exporter / blackbox_exporter: `mem_limit: 40m` each

---

## Security groups

### `sg-prod` (attached to manager + all workers)
| Type | Proto | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 2377 | self | Swarm cluster management |
| Custom TCP | TCP | 7946 | self | Node-to-node gossip |
| Custom UDP | UDP | 7946 | self | Node-to-node gossip |
| Custom UDP | UDP | 4789 | self | VXLAN overlay (containers on different nodes) |
| Custom TCP | TCP | 9100 | self | Manager's Prometheus scrapes workers' node_exporter |
| Custom TCP | TCP | 3100 | self | Workers' promtail push to manager's Loki |
| Custom TCP | TCP | 9090 | `sg-grafana` | Grafana reads Prometheus |
| Custom TCP | TCP | 3100 | `sg-grafana` | Grafana reads Loki |
| Custom TCP | TCP | 9100 | `sg-staging` | (if needed for cross-env probe) |
| SSH | TCP | 22 | `sg-jenkins` | Ansible playbooks |
| HTTP | TCP | 80 | 0.0.0.0/0 | Public app (Swarm ingress) |
| Custom TCP | TCP | 9090 | admin IP | Prometheus UI (debug) |

### `sg-staging`
| Type | Proto | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 9100 | `sg-prod` | Prometheus (on prod-manager) scrapes staging |
| SSH | TCP | 22 | `sg-jenkins` | Ansible |
| HTTP | TCP | 80 | 0.0.0.0/0 | Public app + blackbox probes from prod-manager |

### `sg-grafana`
| Type | Proto | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 3000 | 0.0.0.0/0 (or admin IP) | Grafana UI |
| SSH | TCP | 22 | `sg-jenkins` | Ansible |

Egress default (all-out) is fine everywhere.

### `sg-jenkins`
Inbound: 22 (admin), 8080 (admin + GitHub webhook — 0.0.0.0/0 for demo). Outbound: default.

### IAM role
`LabRole` on staging + prod fleet (needs ECR read + S3 access). Not needed on Grafana EC2.

---

## Jenkins credentials

| Credential ID | Type | Purpose |
|---|---|---|
| `staging-ec2-ssh-key` | SSH private key | ec2-user login on ALL EC2s |
| `staging-postgres-password` | Secret text | Postgres password (same for staging + prod) |
| `staging-django-secret-key` | Secret text | Django `SECRET_KEY` |
| `jenkins-smtp-gmail` | Username + password | Gmail SMTP (App Password) |
| `personal-email-recipients` | Secret text | Failure emails during dev |
| `jenkins-failure-email-recipients` | Secret text | Failure emails in "prod" (team list) |

---

## Known operational quirks

### Cold-start DNS race — backend/frontend stuck at 0/1
Symptom: `nginx: [emerg] host not found in upstream "rmit-store-backend"` OR `django.db.utils.OperationalError: failed to resolve host 'db'`.

Cause: nginx/Django resolve DNS at container start. If the upstream service (`backend`, `db`) isn't in Swarm's overlay DNS yet, the container dies. Restart policy retries a few times then gives up.

Fix: `docker service update --force rmit-store_<service>` — re-schedules the task after the upstream is registered. Alternatively bump `restart_policy.max_attempts` in `stack.*.yml` to 20+ (already done for frontend).

### "No such container" on postgres — db stuck at 0/1
Symptom: `docker service ps rmit-store_db` shows `Failed` with `"No such container: rmit-store_db.1.<id>"` across multiple attempts.

Cause: usually **disk pressure** on manager (`df -h` shows >80% full). Docker reaps partially-created containers when disk is low.

Fix: `sudo docker system prune -a` (safe — doesn't touch volumes). Then `sudo docker service update --force rmit-store_db`.

### Grafana empty even though pipeline succeeded
Symptom: Grafana UI shows no dashboards.

Cause: (usually solved now) `ansible.builtin.copy` copies a directory instead of its contents when `src:` has no trailing slash → files end up at `.../dashboards/dashboards/...`, Grafana finds nothing at the configured provider path.

Fix: current playbook uses `src: ".../{{ item }}/"` (trailing slash) — flat layout. If you hit this after modifying the playbook, `sudo rm -rf /home/ec2-user/monitoring/grafana` on the Grafana EC2 then re-run `provision-monitoring`.

### Grafana metrics work but no logs / no data for staging
Cause: promtail on staging couldn't reach prod-manager Loki. Usually SG (`sg-prod` inbound 3100 from `sg-staging`) OR wrong `manager_private_ip` in the promtail config (stale from an older render — re-run `provision-staging`).

### Public IP rotated → users get Django 400
Symptom: browser shows `Bad Request (400) — Invalid HTTP_HOST header` after stop/start of staging or prod-manager.

Cause: EC2 got a new public IP; `public_ip=` in inventory is stale → `ALLOWED_HOSTS` in the deployed .env doesn't include the new IP.

Fix: allocate an Elastic IP OR update `public_ip=` in inventory + push (triggers redeploy).

### Grafana datasources point at stale manager IP
Symptom: Grafana dashboards blank after prod-manager EC2 replaced.

Cause: `datasources.yml.j2` embeds prod-manager's private IP at render time.

Fix: update `prod.ini` with new manager IP, push. `provision-monitoring` re-renders and restarts Grafana.

---

## GitHub webhook → Jenkins

Setup on Github on tab Webohook with `http://<jenkins-ip>:8080/github-webhook/` to able auto push commit to Github for enable auto trigger

**Allocate an Elastic IP to Jenkins** — stop/start otherwise invalidates the webhook URL (Learner Lab instances lose their public IP on stop).

---

## TODOs before submission

- Swap `personal-email-recipients` → `jenkins-failure-email-recipients` in `Jenkinsfile`'s `post { failure {} }` + `post { fixed {} }`.
- `stack.prod.yml` `AWS_STORAGE_BUCKET_NAME` still points at `meowgang-media-staging-01`. Can provision a dedicated prod bucket.
- Allocate Elastic IPs to Jenkins, prod-manager, staging, Grafana (avoids IP-rotation problems).
- Bump backend's `restart_policy.max_attempts` to 20 in both stack files (matches frontend — survives cold-start DNS race without manual `--force`).
- Curently, we don't test on init a new worker node then join a exist node swarm at the moment yet 
- Also, on UI jenkins at the moment you will see there are 4 pipelines Configure-rmit-store-sever-staging,  Configure-rmit-store-sever-monitoring, Configure-rmit-store-sever-prod, Fork-rmit-store-cicd-new, at the moment this pipeline still trigger to build on different branch not main branch. You can click on Configure tab of Jenkins job to switch on Branch Specifier from the current branch to */main or the branch you want to buil
