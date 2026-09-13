# DevOps Pipelines — Reference

Summary of the CI/CD, provisioning, orchestration and monitoring artefacts
delivered on the `provision-and-restructure` branch. Purpose: give a marker
(or a future team member) a single page they can read before diving into any
specific file.

---

## The three Jenkins pipelines

| Jenkinsfile | Purpose | Trigger | Runs against |
|---|---|---|---|
| `Jenkinsfile` | **Main CI/CD** — tests, builds, publishes images, deploys to staging AND production | GitHub webhook (`push`) OR manual "Build with Parameters" | Existing hosts in `ansible/inventory.ini`, or IPs supplied at build time |
| `Jenkinsfile.provision-staging` | **One-shot** provisioning of a fresh staging EC2 | Manual "Build with Parameters" | The IPs you type in |
| `Jenkinsfile.provision-prod` | **One-shot** provisioning of a fresh 3-EC2 prod fleet (1 manager + 2 workers) | Manual "Build with Parameters" | The 6 IPs you type in |

### `Jenkinsfile` — main CI/CD (13 stages)

```
Checkout → Validate Repo → Show Info → Backend Tests → Controlled Failure Gate
  → Frontend Build → Docker Build → Playwright E2E → Publish to ECR
  → Validate Staging Connectivity → Deploy to Staging
  → Validate Production Connectivity → Deploy to Production
```

Runtime knobs (all optional):

| Param | Default | Effect |
|---|---|---|
| `DEMO_INTENTIONAL_FAILURE` | `false` | Runs `server/tests/failure/test_pipeline_failure.py` which is designed to fail. Proves a bad commit blocks staging + prod. |
| `DEMO_STAGING_HEALTH_FAILURE` | `false` | Deploys staging with a deliberately broken `ALLOWED_HOSTS`. Django rejects the health probe → staging goes red → prod stages skipped. Proves the staging health gate. |
| `STAGING_HOST_IP` | empty | If set, staging deploy targets THAT public IP instead of `ansible/inventory.ini [staging]`. Lets a freshly provisioned staging EC2 receive the app without editing inventory. |
| `PROD_MANAGER_IP` | empty | Same idea for prod swarm manager (`[swarm_manager]` fallback). |

Failure handling in `post {}`:
- `failure` → sends HTML email + attached log to recipients from Jenkins credential `personal-email-recipients` (TODO before submission: swap to `jenkins-failure-email-recipients` which holds the team distribution list).
- `fixed` → sends "green again" email when a build passes after previous failure.

### `Jenkinsfile.provision-staging` (6 stages)

Takes `STAGING_PUBLIC_IP` + `STAGING_PRIVATE_IP`. Runs `setup-hosts.yml` (Docker + Compose plugin) then `monitoring.yml` (role=central env=staging). Reports Grafana URL + inventory line to paste.

### `Jenkinsfile.provision-prod` (10 stages)

Takes 6 IPs (public + private for manager, worker-1, worker-2). Runs:

1. Setup Docker on all 3 hosts
2. Init Swarm on manager (captures worker join token)
3. Deploy central monitoring on manager (with worker IPs baked into `prometheus.yml`)
4. Join worker-1 to Swarm + deploy exporters-only stack
5. Join worker-2 to Swarm + deploy exporters-only stack
6. Verify `docker node ls` reports 3 nodes
7. Print Grafana URL + inventory lines

All playbooks are idempotent — re-running after fixing an error is safe.

---

## Ansible playbooks

| File | When it runs | What it does |
|---|---|---|
| `ansible/setup-hosts.yml` | **Provision** (once per host) | Installs Docker, Docker Compose v2 plugin, adds ec2-user to docker group, creates `/home/ec2-user/app` |
| `ansible/init-swarm.yml` | **Provision** (once, manager only) | `docker swarm init --advertise-addr <private-ip>`. Idempotent — skips if swarm already active. |
| `ansible/join-swarm.yml` | **Provision** (once per worker) | Joins the manager using the worker token. Skips if already joined. |
| `ansible/monitoring.yml` | **Provision** (once per host) | Two roles: `central` (Prometheus + Grafana + Loki + Promtail + node_exporter + blackbox_exporter) OR `exporters` (node_exporter + Promtail shipping to central Loki). Also creates a 2 GB swap file and sets `vm.swappiness=10`. |
| `ansible/deploy-staging.yml` | **Every deploy** | Copies `compose.staging.yml` + renders `.env` on host, `docker compose pull && up -d`, waits for `/healthz`. |
| `ansible/deploy-prod-swarm.yml` | **Every deploy** | Copies `stack.prod.yml`, `docker stack deploy` with env vars, waits for services to converge + `/healthz`. |
| `ansible/deploy-prod.yml` | Fallback only | Same as staging but targets prod manager. Kept for emergency compose-based redeploy. |

Both deploy playbooks read `hosts:` from a variable that defaults to their expected inventory group (`staging` / `swarm_manager`). When Jenkins overrides the target IP via `STAGING_HOST_IP` / `PROD_MANAGER_IP`, it also passes `-e target_hosts=all` so the single-host inline inventory matches.

### Inventory files

- `ansible/inventory.ini` — flat file with `[staging]`, `[swarm_manager]`, `[swarm_workers]`, `[production:children]`. Read by the main Jenkinsfile pipelines.
- `ansible/inventories/staging.ini` — staging group only.
- `ansible/inventories/prod.ini` — prod groups only.

The inventories/ folder is provided for cleanliness (a single-env playbook run doesn't need to know about the other env). The main pipeline still uses `inventory.ini` because that's what the existing Jenkins jobs point at.

---

## Application stack files

| File | Deployed by | Orchestrator | Purpose |
|---|---|---|---|
| `compose.staging.yml` | `deploy-staging.yml` | Docker Compose | Staging app — single-node, hardcoded container names, `depends_on: service_healthy` |
| `compose.prod.yml` | `deploy-prod.yml` (fallback) | Docker Compose | Prod compose fallback |
| `stack.prod.yml` | `deploy-prod-swarm.yml` | **Docker Swarm** | Prod on 3-node swarm |
| `compose.yml` | (local dev only) | Docker Compose | Untouched — kept for developer laptops |
| `compose.ci.yml` | Jenkinsfile Playwright stage | Docker Compose | Ephemeral env for E2E tests during CI |

### `stack.prod.yml` — Swarm-specific notes

Because Swarm silently ignores several Compose features, this file differs from `compose.prod.yml`:

- **No `container_name`** — Swarm names containers itself (`rmit-store_<service>.<slot>.<id>`).
- **No `depends_on.condition: service_healthy`** — Swarm ignores it. Startup ordering handled by container healthchecks + restart policy.
- **`restart: unless-stopped` moved to `deploy.restart_policy`** — Compose-style restart is ignored.
- **`deploy:` block per service** — `replicas`, `restart_policy`, `update_config`, `rollback_config`, `placement.constraints`.

Placement:
- `db` pinned to `node.role == manager` (its volume follows the manager).
- `backend` + `frontend` pinned to `node.role == worker`.

Network alias fix on `backend`:
```yaml
networks:
  rmit-store-net:
    aliases:
      - rmit-store-backend
```
Reason: `client/nginx.conf` hardcodes `proxy_pass http://rmit-store-backend:8000;` which was the Compose container_name. Under Swarm the service is named `backend`, so we alias it back to the old name so the frontend image works unchanged.

### Known Swarm quirk on cold start

nginx resolves DNS at container start. If the frontend container comes up before Swarm's embedded DNS has fully registered the backend, nginx errors "host not found in upstream" and the container dies. `restart_policy.max_attempts` on frontend is set to a value big enough (>3) to survive this race — after backend is registered, a subsequent restart succeeds. If frontend still shows `0/1` after a fresh `docker stack deploy`, run `docker service update --force rmit-store_frontend` to give it another kick.

---

## Monitoring stack

Central stack lives in `monitoring/compose.monitoring.yml`; per-node exporter stack lives in `monitoring/exporters/compose.exporters.yml`.

### Layout

```
monitoring/
├── compose.monitoring.yml         Central stack (prometheus, grafana, loki,
│                                   promtail, node_exporter, blackbox_exporter)
├── shared/
│   ├── loki-config.yml            filesystem storage, 24h retention
│   ├── promtail-config.yml        tails Docker container logs, ships to Loki
│   └── blackbox.yml               HTTP prober with Host: 127.0.0.1 header
│                                   override (so Django accepts the probe)
├── grafana/
│   ├── dashboards/
│   │   ├── app-health.json        /healthz + /readyz + /api/version + status
│   │   │                           codes + probe latency
│   │   ├── host-resources.json    CPU %, Memory %, Disk %, load avg
│   │   └── logs.json              Live tail with per-container filter
│   └── provisioning/
│       ├── datasources/           Prometheus (uid=prometheus) + Loki (uid=loki)
│       └── dashboards/            Auto-load provider config
├── staging/
│   └── prometheus.yml             Scrapes localhost node_exporter + blackbox
│                                   probes against host.docker.internal
├── prod/
│   └── prometheus.yml.j2          Jinja template — rendered with worker
│                                   IPs at provision time to scrape all 3 nodes
└── exporters/
    ├── compose.exporters.yml      Just node_exporter + promtail (for workers)
    └── promtail-config.yml.j2     Jinja template — clients.url points at the
                                   manager's Loki
```

### Deployment topology

| Env | Where central stack runs | Where exporters run |
|---|---|---|
| Staging | Single EC2 (co-located with app) | Same EC2 (built into central compose) |
| Prod | Manager EC2 (co-located with `db`) | Manager + both workers |

Grafana admin password: `RmitMonitor2767!` (hardcoded in `compose.monitoring.yml` env for the demo — in a real project this would be a secret from Ansible Vault or Docker secrets).

### Runtime tuning (fits t3.small — 2 GB RAM)

- Prometheus: `24h` retention, `500MB` max, scrape interval `30s`, `mem_limit: 400m`
- Loki: filesystem storage, 24h retention, `mem_limit: 300m`
- Grafana: `mem_limit: 200m`
- Promtail: `mem_limit: 100m`
- Node exporter + Blackbox exporter: `mem_limit: 40m` each
- 2 GB swap file + `vm.swappiness=10` provisioned by `ansible/monitoring.yml`

Total memory ceiling ~1.1 GB — leaves headroom for the app on the same host.

---

## Security group configuration

The 3 prod EC2s must sit in a security group with these inbound rules for Swarm + monitoring to work. Same SG is attached to all 3 hosts.

### Swarm cluster ports — MUST be self-referential (source = the SG itself)

| Type | Protocol | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 2377 | self-SG | Swarm cluster management (managers listen; workers connect) |
| Custom TCP | TCP | 7946 | self-SG | Node-to-node gossip |
| Custom UDP | UDP | 7946 | self-SG | Node-to-node gossip (both required — MISSING THIS ONE was a bug we hit) |
| Custom UDP | UDP | 4789 | self-SG | VXLAN overlay data plane (containers on different nodes talking) |

**Symptom if any of these is missing**: swarm nodes see each other in `docker node ls` (that only needs TCP 2377), but containers on workers can't reach the DB on the manager. Django prints `psycopg.errors.ConnectionTimeout`. Same failure mode regardless of which port is blocked.

### Monitoring ports — self-referential (only prod/worker nodes need these)

| Type | Protocol | Port | Source | Why |
|---|---|---|---|---|
| Custom TCP | TCP | 3100 | self-SG | Workers' promtail push logs to manager's Loki |
| Custom TCP | TCP | 9100 | self-SG | Manager's Prometheus scrapes workers' node_exporter |

### External access — from your admin IP

| Type | Protocol | Port | Source | Why |
|---|---|---|---|---|
| SSH | TCP | 22 | your IP | Ansible + operator access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Public application access (via Swarm ingress) |
| Custom TCP | TCP | 3000 | your IP | Grafana UI (admin/RmitMonitor2767!) |
| Custom TCP | TCP | 9090 | your IP | Prometheus UI (debugging only) |

### Staging (single EC2) SG

Same as above minus the swarm ports (2377/7946/4789) since staging isn't a swarm. Loki 3100 not needed either (no remote promtails).

### IAM role attached to each EC2 (via instance profile)

`LabRole` (or equivalent) with these permissions:
- `sts:GetCallerIdentity`
- `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer` (all EC2s pull images)
- `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` on `meowgang-media-staging-01` (backend uploads product images)

Missing the IAM role is the second most common startup failure — `aws sts get-caller-identity` fails inside the container and boto3 refuses to init.

---

## Jenkins credential inventory

| Credential ID | Type | Purpose |
|---|---|---|
| `staging-ec2-ssh-key` | SSH private key | ec2-user login on ALL environments (staging + prod fleet). Public half must be on the EC2 at provision time. |
| `staging-postgres-password` | Secret text | Postgres password used in staging + prod (same value for now — swap to per-env before submission) |
| `staging-django-secret-key` | Secret text | Django SECRET_KEY (same story) |
| `jenkins-smtp-gmail` | Username with password | Gmail SMTP auth. Username = bot Gmail address, password = 16-char Gmail App Password. Used by Extended E-mail Notification globally. |
| `personal-email-recipients` | Secret text | Where failure emails go DURING TESTING. Value = your personal Gmail. |
| `jenkins-failure-email-recipients` | Secret text | Where failure emails go IN PRODUCTION. Value = team distribution list. Swap this into the Jenkinsfile in place of `personal-email-recipients` before submission. |

---

## GitHub webhook → Jenkins

The main pipeline (`Jenkinsfile`) is push-triggered via `triggers { githubPush() }`. That block does nothing by itself — GitHub has to be told where to POST when a push happens, and Jenkins has to be reachable from GitHub's servers.

### One-time setup

**1. Jenkins side (plugin + endpoint)**

- **Manage Jenkins → Plugins**: verify **GitHub plugin** is installed (usually shipped with the "Blue Ocean" bundle).
- Jenkins automatically exposes `POST /github-webhook/` when the plugin is enabled. Nothing to configure in Jenkins itself for the plain webhook path.
- Each pipeline job that should react to pushes must have **"GitHub hook trigger for GITScm polling"** ticked under Build Triggers (this is what the `triggers { githubPush() }` declarative block enables when using "Pipeline script from SCM").

**2. GitHub side (webhook)**

Fork's repo → **Settings → Webhooks → Add webhook**:

| Field | Value |
|---|---|
| Payload URL | `http://<jenkins-public-ip>:8080/github-webhook/` (trailing slash matters) |
| Content type | `application/json` |
| Secret | (leave blank for the demo; add a shared secret + configure it in Jenkins for real prod) |
| Which events | "Just the push event" |
| Active | ✅ |

Click **Add webhook**. GitHub sends a ping — should return HTTP 200. If it returns 403/404/timeout, the URL or Jenkins auth is wrong.

**3. Verify**

Push any commit → GitHub → Webhook page → "Recent Deliveries" tab → most recent delivery shows `200 OK` and Jenkins triggers a build within a few seconds.

### The IP-stability problem

Jenkins is running on an EC2 instance. AWS assigns a **new public IP every time the instance stops → starts** (a reboot keeps the IP; a stop/start does not). Consequences:

- Webhook payload URL points at the old IP → GitHub POSTs into the void → **no builds are triggered on push** and no error is obvious (GitHub reports timeout in "Recent Deliveries", but if you're not looking, you'll just wonder why the pipeline isn't running).
- Manual fix each time: edit the webhook, replace the IP, save.

### Solutions

Three options, in the order I'd try them.

#### Option 1 — Allocate an Elastic IP (recommended)

Elastic IPs (EIP) are static public IPv4 addresses in AWS. They stay associated with the instance across stop/start.

**Cost**: free while attached to a running instance. Charged only when the EIP is unassociated (e.g., instance terminated). AWS typically allows a small quota by default; Learner Lab usually allows at least one EIP.

**Steps**:
1. AWS Console → EC2 → **Elastic IPs** → **Allocate Elastic IP address** → allocate.
2. Select the new EIP → **Actions → Associate Elastic IP address** → pick the Jenkins instance → Associate.
3. Update the GitHub webhook's Payload URL to `http://<elastic-ip>:8080/github-webhook/` — this is the LAST time you should have to touch it.
4. Update Jenkins global config's "System Admin e-mail address" and any documented URLs that reference Jenkins.

After this, stop/start the Jenkins EC2 as many times as you want — the public IP stays the same.

**Note**: if you terminate the Jenkins instance you must re-associate the EIP with its replacement (or release the EIP to avoid the small hourly charge for an unassociated one).

You can lower the interval (`H/1` = ~1 min) but not below because GitHub API rate limits.

#### Option 2 — Use a stable DNS name

If you have a domain, point an A record at the Jenkins EIP (or a CNAME at the AWS-generated `ec2-…compute-1.amazonaws.com` hostname — but the CNAME-target also changes on stop/start, so this only helps with EIP).

The GitHub webhook then uses `http://jenkins.mydomain.com/github-webhook/` and doesn't need touching even if the underlying IP moves.

For this assessment: overkill. Option 1 is enough.

### Recommended action

Do **Option 1 right now** — takes 2 minutes in the AWS console, and permanently removes an annoying failure mode that would otherwise silently break the "push-to-deploy" story every time the Jenkins instance is stopped for cost/lab reasons.

Document in the report: "The Jenkins host is assigned an Elastic IP so that the GitHub webhook survives instance stop/start cycles, which is a common issue in academic AWS Learner Lab environments where instances are shut down at the end of each session."

---

## Provisioning a fresh staging EC2 — end-to-end

1. In AWS console, launch a `t3.small` EC2 with:
   - Amazon Linux 2023 AMI
   - Public IP enabled
   - Key pair whose PRIVATE half is stored in Jenkins credential `staging-ec2-ssh-key`
   - Attached to a SG open on 22, 80, 3000, 9090 (from your IP) + 9100 self-ref
   - IAM instance profile with ECR read + S3 access
2. Note the public IP and private IP.
3. In Jenkins, open `Configure-rmit-store-sever-staging` → **Build with Parameters**:
   - `STAGING_PUBLIC_IP` = public IP
   - `STAGING_PRIVATE_IP` = private IP
   - Build
4. When green, browse `http://<public-ip>:3000` → login `admin/RmitMonitor2767!` → verify dashboards load.
5. To deploy the app to this new host, open `Fork-rmit-store-cicd-new` → Build with Parameters → set `STAGING_HOST_IP=<public-ip>` → Build. The pipeline builds + tests + deploys to that IP.

## Provisioning a fresh prod fleet — end-to-end

1. Launch 3 EC2s. Attach them ALL to the same SG that has:
   - Ports 22, 80 (from anywhere), 3000, 9090 (from your IP)
   - Ports 2377/tcp, 7946/tcp+udp, 4789/udp — self-referential (SG source = the SG itself)
   - Ports 3100/tcp, 9100/tcp — self-referential
   - IAM role (same as staging)
2. Note all 6 IPs (public + private for each).
3. In Jenkins, open `Configure-rmit-store-sever-prod` → Build with Parameters → fill in the 6 IPs → Build.
4. When green, browse `http://<manager-public>:3000` → Grafana should show all 3 hosts under host-resources dashboard.
5. To deploy the app: open `rmit-store-cicd` → Build with Parameters → set `PROD_MANAGER_IP=<manager-public>` → Build.

---

## Running Ansible directly from your laptop (CLI fallback)

Sometimes you need to invoke a playbook without going through Jenkins — for example when a Jenkins job hasn't been created yet, when Jenkins is unreachable, or when you want to iterate on a single playbook run without waiting for the full pipeline. This section shows the raw `ansible-playbook` commands that the pipelines execute internally.

### Prerequisites (one-time on your laptop)

```bash
# Ansible core
brew install ansible                    # macOS
# or: sudo apt install ansible          # Ubuntu/Debian

# SSH key file at the repo root, chmod 600
chmod 600 ./meowgang-store-staging-key.pem

# Sanity check: from repo root, ping any host by its PUBLIC IP
ANSIBLE_CONFIG=ansible/ansible.cfg ansible all \
  -i "<HOST_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -m ping
# Expected: <ip> | SUCCESS => {"ping": "pong"}
```

### Gotcha: the trailing comma

`-i "<ip>,"` (with a trailing comma) tells Ansible to treat the argument as an inline single-host inventory. **Without the comma**, Ansible looks for a file named `<ip>` and fails with `"[WARNING]: Unable to parse ... as an inventory source"` followed by `"skipping: no hosts matched"`. Always include the comma.

### Provision a fresh staging EC2

Equivalent to running `Jenkinsfile.provision-staging`. Two playbooks: host bootstrap + monitoring stack.

```bash
cd /path/to/repo

# 1. Docker + Compose plugin + workspace dir + Grafana swap tuning
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<STAGING_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  ansible/setup-hosts.yml

# 2. Central monitoring stack (Prometheus + Grafana + Loki + exporters)
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<STAGING_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e role=central \
  -e env=staging \
  ansible/monitoring.yml
```

Verify: `curl http://<STAGING_PUBLIC_IP>:3000/api/health` returns 200.

### Provision the prod fleet — manager first

Order matters: manager must be initialised before workers can join. All 5 commands below need to complete successfully in sequence.

```bash
cd /path/to/repo

# ---------- 1. Bootstrap Docker on ALL 3 hosts (one playbook, one command) ----------
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<MANAGER_PUBLIC_IP>,<WORKER_1_PUBLIC_IP>,<WORKER_2_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  ansible/setup-hosts.yml

# ---------- 2. Initialise Swarm on the manager ----------
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<MANAGER_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e advertise_addr=<MANAGER_PRIVATE_IP> \
  ansible/init-swarm.yml

# ---------- 3. Central monitoring stack on the manager ----------
# Worker IPs are baked into prometheus.yml scrape targets at render time.
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<MANAGER_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e role=central \
  -e env=prod \
  -e worker_1_private_ip=<WORKER_1_PRIVATE_IP> \
  -e worker_2_private_ip=<WORKER_2_PRIVATE_IP> \
  ansible/monitoring.yml

# ---------- 4. Get the worker join token from the manager ----------
# The pipeline captures this automatically; from CLI you run it yourself.
JOIN_TOKEN=$(ssh -i ./meowgang-store-staging-key.pem \
    ec2-user@<MANAGER_PUBLIC_IP> \
    'sudo docker swarm join-token worker -q')
echo "Join token: $JOIN_TOKEN"

# ---------- 5a. Worker 1 — join swarm + install exporters ----------
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<WORKER_1_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e manager_private_ip=<MANAGER_PRIVATE_IP> \
  -e join_token=$JOIN_TOKEN \
  ansible/join-swarm.yml

ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<WORKER_1_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e role=exporters \
  -e env=prod \
  -e manager_private_ip=<MANAGER_PRIVATE_IP> \
  ansible/monitoring.yml

# ---------- 5b. Worker 2 — same as worker 1 ----------
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<WORKER_2_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e manager_private_ip=<MANAGER_PRIVATE_IP> \
  -e join_token=$JOIN_TOKEN \
  ansible/join-swarm.yml

ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<WORKER_2_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e role=exporters \
  -e env=prod \
  -e manager_private_ip=<MANAGER_PRIVATE_IP> \
  ansible/monitoring.yml
```

Verify:
```bash
# All 3 nodes joined swarm
ssh -i ./meowgang-store-staging-key.pem ec2-user@<MANAGER_PUBLIC_IP> \
    'sudo docker node ls'
# Expect 3 rows.

# All 3 node_exporters scraped
curl -s "http://<MANAGER_PUBLIC_IP>:9090/api/v1/query?query=up" | python3 -c "
import json, sys
for r in json.load(sys.stdin)['data']['result']:
    print('  host=%s instance=%s up=%s' % (
        r['metric'].get('host','-'),
        r['metric'].get('instance','-'),
        r['value'][1]))
"
# Expect 3 lines all with up=1.
```

If a worker shows `up=0`, its security group is missing an inbound rule for TCP 9100 from the manager's private IP (or the manager's SG blocks outbound — either direction can be the cause).

### Common failure — dashboard shows only 1 host

The Host Resources dashboard shows only the manager's stats when the workers' `node_exporter` isn't reachable. Symptoms:
- Grafana Home → Prometheus data source → Query `up` → only 1 series returned
- Prometheus UI → Status → Targets → workers listed as DOWN with `connection refused` or timeout

Root cause is almost always one of:
1. **Skipped step** — you ran the central stack against the manager but never ran `role=exporters` against the workers. Fix: run steps 5a and 5b above.
2. **Security group** — TCP 9100 not open on workers from manager's private IP. Fix in AWS console.
3. **Wrong worker private IP** — the value you passed to `worker_1_private_ip` at central-stack render time doesn't match the worker's actual private IP. Fix: re-render + reload Prometheus (`docker exec monitoring-prometheus wget -qO- http://localhost:9090/-/reload` or restart the container).

### Deploy the app manually (bypass Jenkins)

```bash
# STAGING (Compose) — needs env vars for secrets
cd /path/to/repo
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<STAGING_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e aws_region=us-east-1 \
  -e aws_account_id=<AWS_ACCOUNT_ID> \
  -e build_commit=<A_REAL_COMMIT_SHA_IN_ECR> \
  -e app_version=manual \
  -e postgres_password=<YOUR_PASSWORD> \
  -e secret_key=<YOUR_DJANGO_SECRET> \
  -e allowed_hosts='127.0.0.1,localhost,<PRIVATE_IP>,<PUBLIC_IP>' \
  -e client_url='http://<PUBLIC_IP>' \
  ansible/deploy-staging.yml

# PROD (Swarm) — same var set, different playbook
ANSIBLE_CONFIG=ansible/ansible.cfg ansible-playbook \
  -i "<MANAGER_PUBLIC_IP>," \
  --private-key ./meowgang-store-staging-key.pem \
  -u ec2-user \
  -e target_hosts=all \
  -e aws_region=us-east-1 \
  -e aws_account_id=<AWS_ACCOUNT_ID> \
  -e build_commit=<A_REAL_COMMIT_SHA_IN_ECR> \
  -e app_version=manual \
  -e postgres_password=<YOUR_PASSWORD> \
  -e secret_key=<YOUR_DJANGO_SECRET> \
  -e allowed_hosts='127.0.0.1,localhost,<PRIVATE_IP>,<PUBLIC_IP>' \
  -e client_url='http://<PUBLIC_IP>' \
  ansible/deploy-prod-swarm.yml
```

Manual deploys are useful for one-off tests but should NOT replace the Jenkins pipeline for regular workflow — the pipeline enforces the CI gates (tests + build + ECR publish) that these commands skip.

---

## Known TODOs before submission

- Swap `personal-email-recipients` → `jenkins-failure-email-recipients` in the Jenkinsfile `post { failure {} }` and `post { fixed {} }` blocks.
- `stack.prod.yml` `AWS_STORAGE_BUCKET_NAME` still points at `meowgang-media-staging-01`. Provision a dedicated prod bucket and switch it.
- Consider allocating an Elastic IP to the staging + prod-manager EC2s so a stop/start doesn't invalidate `ALLOWED_HOSTS` and `CLIENT_URL`.
- `ansible/inventory.ini` still has hardcoded IPs from the original fleet. When you provision a new fleet via the pipeline, either update this file or rely on the `STAGING_HOST_IP` / `PROD_MANAGER_IP` overrides for subsequent deploys.



#ToDo
Switch from target_hosts to swarm_manager as we control the swarm node base on inventory as we don't do to for stag, prod
Switch to 1 Grafana 