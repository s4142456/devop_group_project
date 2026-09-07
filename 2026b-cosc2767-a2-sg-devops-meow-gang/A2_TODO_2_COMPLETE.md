# A2 TODO 2 — Combined Roadmap

> **Current status:** TODO 1 is complete. TODO 2 starts from Phase 7, and the team is currently working on Phase 7.
>
> Continue from Phase 7. Keep completed work and do not restart completed tasks.

---

# A2 TODO — Team Roadmap, Ownership, Progress & Handoff

> **Purpose:** Single source of truth for team implementation progress and handoff.
>
> This file helps every teammate answer:
>
> 1. What are we building?
> 2. What phase are we currently in?
> 3. Who owns each phase?
> 4. What exactly does each member need to do?
> 5. What depends on what?
> 6. What evidence should be captured?
> 7. What should the next teammate continue?
>
> ## Source priority
>
> 1. `DevOps_Assignment_2.md` — authoritative assignment requirements
> 2. `APPLICATION_README.md` — application deployment/runtime guidance
> 3. Current source code and infrastructure
> 4. `README.md`
> 5. `A2_TODO.md` — planning/progress/handoff only
>
> The phase names in this document are **team implementation phases** created to organise the work. They are not official phase names from the assignment brief.

---

# 0. Project roadmap

## Full implementation flow

```text
PHASE 0
Audit + Architecture
      │
      ▼
PHASE 1 — Member 1 ✅
Manual Staging Deployment
      │
      ▼
PHASE 2 — Member 1 ✅
Docker Containerisation + Compose
      │
      ├──────────────────┬──────────────────┐
      ▼                  ▼                  ▼
PHASE 3              PHASE 4            PHASE 5
Testing              S3 Media           Ansible
Member 2             Member 3           Member 4
      │                  │                  │
      └──────────────┬───┴──────────────────┘
                     ▼
                 PHASE 6
                 Jenkins CI
                 Member 5
                     │
                     ▼
                 PHASE 7
          Automated Staging → Production
              Member 5 + Member 4
                     │
                     ▼
                 PHASE 8
                Orchestration
              Member 4 + Team
                     │
                     ▼
                 PHASE 9
          Failure + Rollback + Integration
                     │
                     ▼
                PHASE 10
         Report + Evidence + Demo
                All Members
```

---

# 1. Phase ownership summary

| Phase | Goal | Primary owner | Status | Depends on |
|---|---|---|---|---|
| Phase 0 | Audit application + architecture decisions | Team | ✅ Baseline done | — |
| Phase 1 | Manual staging deployment | Member 1 | ✅ Complete | Phase 0 |
| Phase 2 | Docker containerisation + Compose | Member 1 | ✅ Complete | Phase 1 |
| Phase 3 | Automated testing | Member 2 | ⏳ Next | Phase 2 |
| Phase 4 | S3/shared media | Member 3 | ⏳ Next | Phase 2 |
| Phase 5 | Ansible/configuration management | Member 4 | ⏳ Next | Phase 2 |
| Phase 6 | Jenkins Continuous Integration | Member 5 | ⏳ Pending | Phase 3 |
| Phase 7 | Automated staging → production CD | Member 5 + Member 4 | ⏳ Pending | Phases 3, 5, 6 |
| Phase 8 | Docker Swarm/Kubernetes orchestration | Member 4 + Team | ⏳ Pending | Phase 5 |
| Phase 9 | Failure handling + rollback + final integration | Team | ⏳ Pending | Phases 6–8 |
| Phase 10 | Report + evidence + demo + submission | All members | ⏳ Pending | Final system |

---

# 2. Member ownership — quick reference

## Member 1 — Staging + Docker ✅ COMPLETE

```text
Manual EC2 deployment
        ↓
PostgreSQL
        ↓
Gunicorn + Nginx
        ↓
Backend Docker
        ↓
Frontend Docker
        ↓
PostgreSQL Docker
        ↓
Docker Compose
        ↓
Single-host media integration
```

Main responsibility:

- manual staging baseline;
- Docker containerisation;
- Compose integration;
- initial deployment evidence.

---

## Member 2 — Testing ⏳

```text
Audit existing tests
        ↓
Unit tests
        ↓
API/database integration tests
        ↓
JUnit + coverage reports
        ↓
Provide test commands/reports to Jenkins
```

Main responsibility:

- backend test foundation;
- unit testing;
- integration testing;
- test reporting;
- failure cases.

---

## Member 3 — S3/shared media ⏳

```text
Audit image lifecycle
        ↓
Understand Django storage
        ↓
Configure S3
        ↓
Seed/upload media
        ↓
Verify browser access
        ↓
Verify media works across replicas
```

Main responsibility:

- shared uploaded media;
- Amazon S3;
- IAM/storage configuration;
- multi-replica media verification.

---

## Member 4 — Ansible + infrastructure + orchestration ⏳

```text
EC2 topology
      ↓
SSH/inventory
      ↓
Ansible configuration
      ↓
Idempotent playbooks
      ↓
Production hosts
      ↓
Docker Swarm/Kubernetes support
```

Main responsibility:

- configuration management;
- repeatable host setup;
- production infrastructure configuration;
- orchestration support.

---

## Member 5 — Jenkins CI/CD ⏳

```text
GitHub webhook
      ↓
Jenkins CI
      ↓
Tests
      ↓
Build Docker images
      ↓
Publish images
      ↓
Deploy staging
      ↓
Deployment gates
      ↓
Promote production
      ↓
Failure email
```

Main responsibility:

- Jenkins;
- GitHub webhook;
- CI;
- CD;
- failure notification;
- staging → production promotion.

---

# 3. Phase 0 — Audit and architecture

**Owner:** Team  
**Status:** ✅ Baseline complete

## Goal

Understand the supplied application before automating anything.

## Application stack

```text
Vue 3 / Vite
    ↓
Nginx
    ↓
Django REST Framework
    ↓
Gunicorn
    ↓
PostgreSQL
```

## Decisions

- [ ] Do not use Tomcat.
- [ ] Do not use Maven/WAR deployment.
- [ ] Backend deployable artifact = Docker image.
- [ ] Frontend deployable artifact = multi-stage Docker image with Nginx runtime.
- [ ] PostgreSQL = separate stateful service.
- [ ] Manual deployment must work before automation.
- [ ] Final production database architecture confirmed.
- [ ] Final production orchestrator confirmed.
- [ ] Final production media architecture confirmed.

## Recommended production direction

```text
Frontend replicas
        ↓
Load balancing
        ↓
Backend replicas
        ↓
Shared PostgreSQL
        +
Shared S3 media
```

---

# 4. Phase 1 — Manual staging deployment

**Owner:** Member 1  
**Status:** ✅ COMPLETE  
**Depends on:** Phase 0

## Goal

Prove the application works manually on one EC2 instance before introducing Docker/Jenkins/Ansible.

## Infrastructure

- [ ] Create staging EC2.
- [ ] Configure staging Security Group.
- [ ] Allow required HTTP access.
- [ ] Allow SSH access.
- [ ] Keep PostgreSQL `5432` non-public.
- [ ] Remove temporary development ports after setup.

## Runtime

- [ ] Python application virtual environment:
  - Python 3.11.15
- [ ] Node.js:
  - v22.23.2
- [ ] PostgreSQL:
  - 16.14

## PostgreSQL

- [ ] Initialise PostgreSQL.
- [ ] Enable PostgreSQL service.
- [ ] Verify PostgreSQL is active.
- [ ] Create role:

  ```text
  rmit
  ```

- [ ] Create database:

  ```text
  rmit_store
  ```

- [ ] Configure password authentication.
- [ ] Verify database access using:

  ```sql
  SELECT 1;
  ```

## Django

- [ ] Create virtual environment.
- [ ] Install backend dependencies.
- [ ] Configure runtime environment.
- [ ] Run migrations.
- [ ] Seed demo data.

Verified seed baseline:

```text
Categories : 15
Brands     : 16
Products   : 47
Reviews    : 160
Users      : 3
```

## Gunicorn

- [ ] Configure Gunicorn.
- [ ] Configure Gunicorn systemd service.
- [ ] Verify service:

  ```text
  active (running)
  ```

## Nginx

- [ ] Build Vue frontend.
- [ ] Serve Vue production build with Nginx.
- [ ] Proxy backend routes.
- [ ] Proxy `/admin/`.
- [ ] Configure health/readiness routes.
- [ ] Configure static/media handling.

## Verification

- [ ] `/healthz/`
- [ ] `/readyz/`
- [ ] `/api/version/`
- [ ] `/api/docs/`
- [ ] `/shop`
- [ ] Product catalogue renders.
- [ ] Product images render.

## Phase 1 result

```text
Browser
   ↓
Nginx :80
   ├── Vue frontend
   │
   └── Django API
          ↓
       Gunicorn
          ↓
      PostgreSQL
```

---

# 5. Phase 2 — Docker containerisation + Compose

**Owner:** Member 1  
**Status:** ✅ COMPLETE  
**Depends on:** Phase 1

## Goal

Convert the known-working manual deployment into repeatable containers.

## 5.1 Backend container

- [ ] Create backend `Dockerfile`.
- [ ] Create backend `.dockerignore`.
- [ ] Base image:

  ```text
  python:3.11-slim
  ```

- [ ] Install requirements.
- [ ] Run Gunicorn inside container.
- [ ] Build backend image successfully.

## 5.2 PostgreSQL container

- [ ] Use PostgreSQL 16 container.
- [ ] Configure Docker network.
- [ ] Configure persistent DB volume.
- [ ] Verify backend → PostgreSQL connectivity.
- [ ] Verify backend:

  ```text
  /healthz/  → OK
  /readyz/   → database/storage OK
  ```

- [ ] Verify API returns 47 products.

## 5.3 Frontend container

- [ ] Create multi-stage Dockerfile.

Build stage:

```text
node:22-alpine
```

Runtime stage:

```text
nginx:alpine
```

- [ ] Build Vue production files.
- [ ] Final image contains no Node runtime.
- [ ] Configure SPA fallback.
- [ ] Configure `/api/` proxy.
- [ ] Build frontend image successfully.

## 5.4 Manual three-container integration

Verified:

```text
Frontend container
       ↓
Backend container
       ↓
PostgreSQL container
```

- [ ] All three containers running.
- [ ] API through frontend works.
- [ ] Product count = 47.

## 5.5 Docker Compose

- [ ] Add `compose.yml`.
- [ ] Define:
  - `db`
  - `backend`
  - `frontend`
- [ ] PostgreSQL healthcheck.
- [ ] Backend waits for healthy database.
- [ ] Backend runs migrations on startup.
- [ ] Backend runs `collectstatic`.
- [ ] Full stack starts with:

  ```bash
  docker compose up -d --build
  ```

- [ ] Verify:

  ```text
  rmit-store-db         healthy
  rmit-store-backend    running
  rmit-store-frontend   running
  ```

## 5.6 Proxy host fix

Problem:

```text
Request:
127.0.0.1:8080

Generated API URL:
127.0.0.1
```

Fix:

```nginx
proxy_set_header Host $http_host;
```

- [ ] Pagination URLs preserve `:8080`.
- [ ] Media URLs preserve `:8080`.

## 5.7 Single-host Compose media

Current Compose environment:

```text
Backend
  ↓ read/write
rmit-store-media
  ↑ read-only
Frontend Nginx
```

Backend mount:

```text
rmit-store-media:/app/media
```

Frontend mount:

```text
rmit-store-media:/usr/share/nginx/html/media:ro
```

- [ ] Backend media volume created.
- [ ] Frontend sees same files.
- [ ] Seed catalogue writes media to volume.
- [ ] Verify actual image response:

  ```text
  HTTP/1.1 200 OK
  Content-Type: image/jpeg
  ```

- [ ] Verify storefront through SSH tunnel.
- [ ] Verify all product images render.

> This shared Docker volume is only appropriate for the current single-host Compose deployment.
>
> Phase 4 will replace this limitation with shared object storage for multi-replica deployments.

## Member 1 implementation branch

```text
feature/nhu-docker-integration
```

## Relevant commits

```text
2f3614b build(docker): add backend container configuration
cde9e84 build(docker): add frontend container configuration
3f21599 build(docker): add compose stack
4a93b90 fix(docker): support media sharing and proxy host
0db2ac0 chore(evidence): restructure evidence folder structure
```

## Member 1 evidence

```text
docs/evidence/member-1/
```

```text
m1-01-staging-security-group.png
m1-02-runtime-postgresql.png
m1-03-database-access.png
m1-04-nginx-backend-health.png
m1-05-staging-shop-port80.png
m1-06-staging-swagger-api-docs.png
m1-07-gunicorn-systemd-service.png
m1-08-backend-image-build.png
m1-09-backend-container-health.png
m1-10-frontend-image-build.png
m1-11-full-docker-stack.png
m1-12-compose-stack-healthy.png
m1-13-compose-shop-browser.png
```

**Member 1 status: ✅ COMPLETE / READY FOR HANDOFF**

---

# 6. Phase 3 — Automated testing

**Owner:** Member 2  
**Status:** ⏳ NEXT  
**Depends on:** Phase 2

## Goal

Build independent automated tests before Jenkins uses them.

## 6.1 Audit first

- [ ] Inspect existing backend tests.
- [ ] Inspect backend test dependencies.
- [ ] Locate payment validation.
- [ ] Locate subtotal logic.
- [ ] Locate tax logic.
- [ ] Locate total logic.
- [ ] Locate checkout/order logic.
- [ ] Identify permission/role boundaries.

## 6.2 Test tooling

Recommended stack:

```text
pytest
pytest-django
pytest-cov
```

- [ ] Create separate test requirements if appropriate.
- [ ] Configure Django test discovery.
- [ ] Configure JUnit XML.
- [ ] Configure coverage report.

## 6.3 Unit tests

- [ ] Valid payment input.
- [ ] Invalid payment input.
- [ ] Subtotal calculation.
- [ ] Tax calculation.
- [ ] Total calculation.

## 6.4 API/database integration tests

- [ ] Successful checkout.
- [ ] Correct stock reduction.
- [ ] Declined payment.
- [ ] Declined payment creates no order.
- [ ] Declined payment changes no stock.
- [ ] Important role/ownership rules.

## 6.5 Web UI / E2E

Recommended:

```text
Playwright
```

- [ ] Anonymous shop browsing.
- [ ] Product browsing.
- [ ] High-value purchase journey.
- [ ] Declined → approved payment flow if practical.

## 6.6 Deployment smoke tests

Create lightweight checks for:

- [ ] frontend
- [ ] `/healthz/`
- [ ] `/readyz/`
- [ ] `/api/version/`
- [ ] product API
- [ ] media/image endpoint

## 6.7 Failure testing

- [ ] Add an intentional test failure.
- [ ] Test meaningful failure scenario.
- [ ] Prepare failure command/scenario for Jenkins demonstration.

## Member 2 deliverables

```text
Tests
+ exact commands
+ JUnit reports
+ coverage reports
+ failure scenario
+ Jenkins handoff
```

Evidence:

```text
docs/evidence/member-2/
```

Naming:

```text
m2-<sequence>-<description>.png
```

---

# 7. Phase 4 — S3 / shared media

**Owner:** Member 3  
**Status:** ⏳ CAN RUN IN PARALLEL WITH PHASE 3 & 5  
**Depends on:** Phase 2

## Goal

Replace instance/container-local media with shared storage suitable for multiple backend replicas.

## 7.1 Image lifecycle audit

Classify:

- [ ] `client/public/images/`
- [ ] `server/seed_assets/products/`
- [ ] runtime `server/media/`

Trace:

- [ ] `Product.image`
- [ ] `seed_demo`
- [ ] Django storage backend
- [ ] generated object paths

## 7.2 Existing S3 support

- [ ] Confirm `django-storages`.
- [ ] Inspect S3 configuration.
- [ ] Identify:

  ```text
  USE_S3
  AWS_STORAGE_BUCKET_NAME
  AWS_S3_REGION_NAME
  ```

- [ ] Identify additional required settings.

## 7.3 AWS configuration

- [ ] Create/select S3 bucket.
- [ ] Prefer same AWS region where practical.
- [ ] Keep credentials out of Git.
- [ ] Investigate Learner Lab IAM limitations.
- [ ] Prefer IAM role/instance profile where available.
- [ ] Decide browser read-access strategy.

## 7.4 Application verification

- [ ] Enable S3.
- [ ] Run `seed_demo`.
- [ ] Verify product objects appear in S3.
- [ ] Verify application generates S3 media URLs.
- [ ] Verify browser images render.

## 7.5 Multi-replica verification

Later with orchestration:

- [ ] Run multiple backend replicas.
- [ ] Verify all replicas access same media.
- [ ] Restart/replace one backend.
- [ ] Verify media survives.

Evidence:

```text
docs/evidence/member-3/
```

Naming:

```text
m3-<sequence>-<description>.png
```

---

# 8. Phase 5 — Ansible / configuration management

**Owner:** Member 4  
**Status:** ⏳ CAN RUN IN PARALLEL WITH PHASE 3 & 4  
**Depends on:** Phase 2

## Goal

Replace manual server setup with repeatable configuration management.

## 8.1 Infrastructure planning

- [ ] Confirm final EC2 topology.
- [ ] Confirm hostnames.
- [ ] Confirm security groups.
- [ ] Confirm SSH users.
- [ ] Confirm staging/production separation.

## 8.2 Ansible connectivity

- [ ] Configure inventory.
- [ ] Verify normal SSH.
- [ ] Verify:

  ```bash
  ansible-inventory --list
  ```

- [ ] Verify:

  ```bash
  ansible <group> -m ping
  ```

## 8.3 Playbooks

Automate:

- [ ] packages
- [ ] Docker installation
- [ ] Docker configuration
- [ ] required users/groups
- [ ] directories
- [ ] deployment prerequisites
- [ ] staging configuration
- [ ] production configuration

## 8.4 Idempotency

- [ ] Run playbook once.
- [ ] Run same playbook again.
- [ ] Verify second run produces no unnecessary changes.

## Member 4 deliverables

```text
Inventory
+ playbooks
+ successful ansible ping
+ idempotent second run
+ staging/production host setup
```

Evidence:

```text
docs/evidence/member-4/
```

Naming:

```text
m4-<sequence>-<description>.png
```

---

# 9. Phase 6 — Jenkins Continuous Integration

**Owner:** Member 5  
**Status:** ⏳ PENDING  
**Depends on:** Phase 3 test commands/results

## Goal

Automatically build and test every GitHub update.

## Target flow

```text
GitHub push
      ↓
Webhook
      ↓
Jenkins
      ↓
Checkout exact commit
      ↓
Run tests
      ↓
Build frontend
      ↓
Build Docker images
      ↓
Tag immutable artifacts
      ↓
Publish successful images
```

## 9.1 GitHub integration

- [ ] Configure webhook.
- [ ] Verify GitHub push triggers Jenkins automatically.

## 9.2 Checkout

- [ ] Checkout exact commit.
- [ ] Record:

  ```text
  GIT_COMMIT
  APP_VERSION
  ```

## 9.3 Tests

- [ ] Run Member 2 backend unit tests.
- [ ] Run integration tests.
- [ ] Publish JUnit results.
- [ ] Publish coverage results.
- [ ] Stop pipeline on failure.

## 9.4 Build

- [ ] Build frontend.
- [ ] Build backend Docker image.
- [ ] Build frontend Docker image.

## 9.5 Immutable image tags

Use:

```text
Git commit SHA
and/or
Jenkins build number
```

Do not rely only on:

```text
latest
```

## 9.6 Registry

- [ ] Select registry/ECR.
- [ ] Push successful backend image.
- [ ] Push successful frontend image.

Evidence:

```text
docs/evidence/member-5/
```

---

# 10. Phase 7 — Automated CD: staging → production

**Owners:** Member 5 + Member 4  
**Status:** ⏳ PENDING  
**Depends on:** Phases 3, 5, 6

## Goal

Production must only change after staging successfully passes all gates.

## Target pipeline

```text
Successful CI
     ↓
Deploy exact images to staging
     ↓
Run migrations
     ↓
Readiness checks
     ↓
Smoke tests
     ↓
Integration / Web UI tests
     ↓
 ┌───────────────┐
 │     FAIL      │
 └───────────────┘
        ↓
Stop pipeline
        ↓
Notify team
        ↓
Production unchanged


 ┌───────────────┐
 │     PASS      │
 └───────────────┘
        ↓
Promote SAME tested images
        ↓
Production
        ↓
Production verification
```

## Staging

- [ ] Automated deployment.
- [ ] `/healthz/`.
- [ ] `/readyz/`.
- [ ] `/api/version/`.
- [ ] product API.
- [ ] media endpoint.
- [ ] required automated tests.

## Failure path

- [ ] Pipeline stops automatically.
- [ ] Production remains unchanged.
- [ ] Team receives automated email.

## Production path

- [ ] Promote same tested image digest/tag.
- [ ] Do not rebuild different production images.
- [ ] Verify health.
- [ ] Verify readiness.
- [ ] Verify deployed version.
- [ ] Verify user-facing application.

---

# 11. Phase 8 — Production orchestration

**Owner:** Member 4 + Team  
**Status:** ⏳ PENDING

**Assignment requirement:** Docker Swarm or Kubernetes.

Recommended simple course-aligned option:

```text
Docker Swarm
```

## Tasks

- [ ] Confirm orchestrator.
- [ ] Initialise manager.
- [ ] Join workers.
- [ ] Deploy frontend service.
- [ ] Deploy backend service.
- [ ] Run multiple backend replicas.
- [ ] Configure shared database.
- [ ] Configure S3 shared media.
- [ ] Configure service health.
- [ ] Configure external access/load balancing.

## Required demonstrations

- [ ] Scaling.
- [ ] Multiple replicas.
- [ ] Failed container replacement/self-healing.
- [ ] Service discovery.
- [ ] Shared media across replicas.

---

# 12. Phase 9 — Failure handling + rollback + final integration

**Owner:** Team  
**Status:** ⏳ PENDING

## Failure notification

- [ ] Configure automated email notification.
- [ ] Trigger safe intentional pipeline failure.
- [ ] Confirm email automatically sent.
- [ ] Confirm production unchanged.

## Rollback

- [ ] Keep previous known-good image tags/digests.
- [ ] Define rollback procedure.
- [ ] Test rollback.
- [ ] Verify restored version using:

  ```text
  /api/version/
  ```

## Reliability

- [ ] Verify `/healthz/`.
- [ ] Verify `/readyz/`.
- [ ] Verify orchestrator replaces failed container.
- [ ] Verify media persists after backend replacement.

## Optional advanced work

Only after the required pipeline works:

- [ ] Blue-green deployment.
- [ ] Canary deployment.
- [ ] Automatic rollback.
- [ ] CloudFormation.
- [ ] CloudFront.
- [ ] CloudWatch.
- [ ] Prometheus/Grafana.
- [ ] Database backup/restore.
- [ ] Dependency scanning.
- [ ] Secret scanning.
- [ ] Container image scanning.

---

# 13. Evidence structure

Use one evidence folder per member:

```text
docs/evidence/
├── member-1/
├── member-2/
├── member-3/
├── member-4/
└── member-5/
```

## Naming convention

```text
m<member>-<sequence>-<short-description>.png
```

Examples:

```text
m1-01-staging-security-group.png
m2-01-backend-unit-tests.png
m3-01-s3-media.png
m4-01-ansible-ping.png
m5-01-jenkins-webhook.png
```

## Evidence rules

For every significant requirement:

```text
Requirement
    ↓
Implementation
    ↓
Verification
    ↓
Evidence
```

Prefer:

```text
1 strong screenshot
```

over:

```text
many repetitive screenshots
```

Do not screenshot:

- `.env`
- passwords
- secret keys
- private SSH keys
- tokens
- AWS credentials
- sensitive account information unless necessary

Use genuine screenshots/logs only.

---

# 14. Assignment requirement coverage

| Requirement | Owner(s) | Current status |
|---|---|---|
| AWS/cloud integration | Team / M1 / M3 / M4 | 🟡 Partial |
| Containerised services | Member 1 | ✅ Baseline complete |
| Continuous Integration | Member 5 | ⏳ |
| Continuous Delivery | Member 5 + Member 4 | ⏳ |
| Testing | Member 2 | ⏳ |
| Jenkins automation | Member 5 | ⏳ |
| Configuration management | Member 4 | ⏳ |
| Failure email alert | Member 5 | ⏳ |
| Container orchestration | Member 4 + Team | ⏳ |

Do not mark the assignment complete until all mandatory rows have:

```text
implementation + verification + evidence
```

---

# 15. Current team checkpoint

## Completed

```text
Phase 0 — Audit / architecture          ✅
Phase 1 — Manual staging                ✅ Member 1
Phase 2 — Docker + Compose              ✅ Member 1
```

## Current parallel work

These can proceed at the same time:

```text
Phase 3 — Testing                       ⏳ Member 2
Phase 4 — S3/shared media               ⏳ Member 3
Phase 5 — Ansible                       ⏳ Member 4
```

Member 5 can prepare Jenkins infrastructure/webhook in parallel, but the complete CI pipeline should consume the stable test commands produced by Member 2.

## Upcoming integration

```text
Phase 6 — Jenkins CI                    ⏳ Member 5
Phase 7 — Staging → Production CD       ⏳ M5 + M4
Phase 8 — Orchestration                 ⏳ M4 + Team
Phase 9 — Failure + Rollback            ⏳ Team
Phase 10 — Final report/demo            ⏳ All
```

---

# 16. Member handoff rules

Before a member declares their task complete, provide:

- [ ] branch name;
- [ ] relevant commits;
- [ ] files changed;
- [ ] commands used;
- [ ] verification result;
- [ ] evidence filenames;
- [ ] known limitations;
- [ ] what the next phase depends on;
- [ ] anything teammates must not overwrite/remove.

Recommended handoff format:

```text
Owner:
Phase:
Status:

Branch:
Commits:

Implemented:
- ...

Verified:
- ...

Evidence:
- ...

Known limitations:
- ...

Next dependency:
- ...
```

---

# 17. Member 1 handoff checkpoint

**Owner:** Member 1  
**Status:** ✅ COMPLETE

Branch:

```text
feature/nhu-docker-integration
```

Implemented:

```text
Manual staging
Docker backend
Docker frontend
Docker PostgreSQL
Docker Compose
Single-host shared media
Nginx proxy host fix
```

Verified:

```text
Health/readiness
47 products
Frontend → backend → DB
Real image/jpeg media
Browser storefront
```

Evidence:

```text
docs/evidence/member-1/
m1-01 → m1-13
```

Known limitation:

```text
Docker media volume is single-host only.
Use S3 when multiple backend replicas are introduced.
```

Next dependency:

```text
Member 2 → testing
Member 3 → S3
Member 4 → Ansible
```

---

# 18. Phase 10 — Final report, demo and submission

**Owner:** All members

## Repository

- [ ] Final code matches final GitHub commit.
- [ ] Dockerfiles included.
- [ ] Compose/orchestration configuration included.
- [ ] Jenkins pipeline included.
- [ ] Ansible included.
- [ ] Tests included.
- [ ] Infrastructure configuration included where implemented.
- [ ] README explains reproducible deployment/pipeline.

## Final evidence audit

- [ ] AWS/cloud.
- [ ] Containers.
- [ ] CI.
- [ ] CD.
- [ ] Testing.
- [ ] Jenkins.
- [ ] Ansible.
- [ ] Failure email.
- [ ] Orchestration.
- [ ] Advanced features attempted.

## Demo

Show:

```text
GitHub change
      ↓
automatic Jenkins trigger
      ↓
tests
      ↓
build
      ↓
staging
      ↓
verification
      ↓
production
```

Also show:

```text
Bad change
   ↓
Pipeline fails
   ↓
Email sent
   ↓
Production unchanged
```

And:

```text
Good change
   ↓
Tests pass
   ↓
Staging passes
   ↓
Same artifact promoted
   ↓
Production updated
```

## Each member

- [ ] Presents their own contribution.
- [ ] Understands how their phase connects to the full pipeline.
- [ ] Can explain evidence.
- [ ] Can explain one important design decision.

## Submission

- [ ] `Document.pdf`
- [ ] `Github.txt`
- [ ] `Youtube.txt`
- [ ] Condition 3 declaration PDF
- [ ] Final ZIP prepared exactly as required

---

# 19. Final priority rule

Do not overengineer.

Complete mandatory path first:

```text
Manual deployment                   ✅
        ↓
Docker                              ✅
        ↓
Testing
        ↓
Ansible
        ↓
Jenkins CI
        ↓
Automated staging
        ↓
Production promotion
        ↓
Orchestration
        ↓
Failure + rollback
        ↓
Final evidence/report/demo
```

Only after this works reliably should the team spend time on:

```text
CloudFormation
CloudFront
Canary
Blue-green
Monitoring dashboards
Advanced security scanning
Other optional improvements
```
# A2 TODO — Phase 2 v2
## Three-Day Complete Delivery Roadmap, Guidance and Checklist

> **Team:** DevOps Meow Gang  
> **Starting point:** The team is already working from Phase 7 of the previous TODO.  
> **Goal:** Finish the nine core requirements and four selected advanced areas in three focused days.  
> **Working rule:** Audit the delta, keep valid work, and continue. Do not restart completed phases.

---

# 1. Read this first

## 1.1 How to move from v1 to v2

1. Keep the current branch and all working code, AWS resources, tests and evidence.
2. Read the frozen decisions in Section 2.
3. Compare only your current task with your member checklist for today.
4. Mark each relevant item `KEEP`, `MODIFY`, `ADD` or `BLOCKED`.
5. Fix only the missing or conflicting items, verify them, then continue.

Do not redo a completed task unless it violates the assignment, conflicts with a frozen decision, blocks another required task, or cannot be demonstrated reliably.

## 1.2 Work that remains valid

- Manual local and EC2 deployment.
- Dockerfiles and local/staging Docker Compose.
- Staging PostgreSQL container and its persistent volume.
- Existing unit, integration, Web UI/E2E and smoke tests.
- Existing S3, Ansible, Jenkins, CloudFormation, CloudWatch or Swarm work.
- Existing screenshots that still prove the final implementation.

## 1.3 Environment distinction

| Environment | Runtime | Database | Required software |
|---|---|---|---|
| Windows local | Docker Compose | PostgreSQL container | Docker Desktop; direct PostgreSQL install not required |
| Staging EC2 | Docker Compose | PostgreSQL container | Docker Engine + Compose plugin |
| Production AWS | Docker Swarm | Private RDS PostgreSQL | Docker Engine on Swarm nodes |

Commands may be typed in VS Code Terminal, PowerShell, SSH or another shell. Docker runs the services; the terminal is only the interface used to issue commands.

---

# 2. Frozen decisions — do not redesign during the sprint

| # | Area | Final decision |
|---:|---|---|
| 1 | Production database | Private Amazon RDS PostgreSQL; fallback only when Learner Lab demonstrably blocks it |
| 2 | Registry | Amazon ECR |
| 3 | Image identity | Immutable Git SHA tags and recorded image digests; never deploy `latest` |
| 4 | Artifact policy | Build once and promote the same backend/frontend images unchanged |
| 5 | Staging | EC2 + Docker Compose + staging PostgreSQL container |
| 6 | Production | EC2 Docker Swarm + RDS + S3 |
| 7 | Secrets | Jenkins Credentials + Ansible Vault; SSM/Secrets Manager only if reliable |
| 8 | Migration owner | One controlled Jenkins/Ansible step before rollout |
| 9 | Testing | Unit + integration + Web UI/E2E + deployment smoke |
| 10 | Orchestrator | Docker Swarm: one manager and two workers |
| 11 | Advanced deployment | Blue-Green |
| 12 | Monitoring | CloudWatch + application metrics endpoint + at least one alarm |
| 13 | IaC | CloudFormation for the AWS resources actually used |
| 14 | Rollback | Automatic rollback to a known-good immutable digest |
| 15 | Failure notification | Notify build, test and deployment failures |
| 16 | Evidence | One naming convention and one owner per proof; no separate tracker file |
| 17 | Final branch | One exact integration branch used by Jenkins and submission |
| 18 | Production traffic | ALB endpoint; listener switches between Blue and Green target groups |
| 19 | Demo | Safe, reversible and rehearsed scenarios only |
| 20 | Stop rule | No optional enhancement until core 9/9 and four selected advanced areas are green |

RDS is the production choice because it provides a shared durable database for replicated backend tasks and meaningful AWS integration. The assignment does not explicitly name RDS, so the fallback is acceptable only with honest proof of a Learner Lab restriction.

## 2.1 Fill this integration contract once — M1 owns it

```text
Integration/Jenkins/submission branch:
AWS account/lab and region:
Staging URL:
Production ALB URL:
Blue target group / published port:
Green target group / published port:
Current live colour:
ECR backend repository:
ECR frontend repository:
S3 media bucket:
RDS identifier/endpoint name (no password):
CloudFormation stack:
CloudWatch dashboard/alarm:
Ansible inventory path:
Staging deployment command:
Production deployment command:
Production migration command:
Smoke/E2E command:
Known-good Git SHA and image digests:
```

Any change to this contract must be announced to all members before merge or deployment.

---

# 3. Target architecture and delivery flow

```text
GitHub integration branch
→ Jenkins checks out exact SHA and runs tests
→ build images once, push to ECR and record digests
→ Ansible deploys same digests to staging Compose
→ staging smoke/E2E PASS
→ controlled production migration
→ deploy inactive Swarm colour from same digests
→ verify inactive target group
→ ALB switches traffic
→ post-switch monitoring
→ on failure: automatic switch-back, verify known-good and notify
```

Production state is shared outside replaceable application tasks:

- PostgreSQL data → private RDS;
- uploaded media → S3;
- images → ECR;
- logs, metrics and alarms → CloudWatch;
- infrastructure definition → CloudFormation.

---

# 4. Guidance for the frozen decisions

## 4.1 ECR, immutable identity and build-once promotion

- [ ] Create/select separate backend and frontend ECR repositories.
- [ ] Give Jenkins or its AWS role only the ECR actions it needs.
- [ ] Checkout the exact commit and calculate `GIT_SHA` once.
- [ ] Build each image once, tag with `GIT_SHA`, push once and record its digest.
- [ ] Set `APP_VERSION` and `GIT_COMMIT` so `/api/version/` identifies the release.
- [ ] Deploy the same digest references to staging, Blue and Green.
- [ ] Save the previous successful digest pair as `KNOWN_GOOD`.
- [ ] Never rebuild between environments or deploy `latest`.

**Done when:** Jenkins logs and `/api/version/` prove one commit and unchanged immutable images moved through staging to production.

## 4.2 Private RDS PostgreSQL

- [ ] Confirm RDS permission, quota, region and budget before creation.
- [ ] Create PostgreSQL in the production VPC with `Publicly accessible = No`.
- [ ] Use appropriate subnets and a dedicated security group.
- [ ] Allow 5432 only from the production Swarm/backend security group.
- [ ] Create a production database/user; never commit or screenshot the password/full URL.
- [ ] Inject `DATABASE_URL` securely and test from authorised production compute.
- [ ] Remove PostgreSQL from the production Swarm stack.
- [ ] Verify all replicas use one database and data survives task replacement.

If Learner Lab blocks RDS:

- [ ] Capture sanitised proof and notify M1.
- [ ] Use one PostgreSQL service with persistent storage and node placement constraint.
- [ ] Document the limitation; never claim the fallback is RDS.

**Done when:** `/readyz/` is healthy and production data survives backend task replacement.

## 4.3 S3 shared media

- [ ] Use a dedicated/approved bucket in the agreed region.
- [ ] Configure least-privilege IAM access, preferably through an EC2 role.
- [ ] Inject bucket/region settings without embedding AWS keys in images or Git.
- [ ] Upload/read a known media object through the application.
- [ ] Replace a backend task and verify the same media remains accessible.
- [ ] Ensure production does not depend on a local media volume.

**Done when:** media works across multiple replicas and survives task replacement.

## 4.4 Secrets and environment separation

- [ ] Use Jenkins Credentials for CI/CD credentials and Ansible Vault for deployment secrets.
- [ ] Keep staging and production variables separate.
- [ ] Prefer IAM roles for EC2 access to ECR, S3 and CloudWatch.
- [ ] Mask pipeline values and use `no_log` for secret-bearing Ansible tasks.
- [ ] Keep `.env`, passwords, AWS keys, tokens and full database URLs out of Git, logs and screenshots.
- [ ] Use SSM/Secrets Manager only if setup, access and recovery are tested in time.

**Done when:** the pipeline works without committed secrets or leaked values.

## 4.5 Controlled database migration

```text
staging PASS
→ save current live version and known-good digests
→ run one production migration job/command
→ stop if migration fails
→ deploy inactive colour
```

- [ ] M4 exposes one repeatable migration command; M5 calls it once.
- [ ] Do not run `migrate` independently inside every Swarm replica.
- [ ] Prevent concurrent production migrations.
- [ ] Use backward-compatible schema changes for the Blue-Green/rollback demo.
- [ ] State clearly that image rollback does not reverse a database migration.

**Done when:** one visible controlled migration precedes rollout and failure blocks deployment.

## 4.6 Four tests and production gate

| Type | Minimum proof |
|---|---|
| Unit | Isolated payment, tax, cart or formatting logic |
| Integration | API ↔ PostgreSQL, order/stock, decline safety or authorisation |
| Web UI/E2E | Real browser journey such as shop, login or purchase |
| Deployment smoke | Frontend + `/healthz/` + `/readyz/` + `/api/version/` + product API |

- [ ] Commands are deterministic, isolated and return non-zero on failure.
- [ ] Jenkins publishes test results and coverage where available.
- [ ] Staging smoke/E2E runs against the deployed staging URL.
- [ ] Inactive-colour smoke runs before traffic switching.
- [ ] Post-switch smoke runs through the production ALB URL.
- [ ] A deliberate safe failure blocks production and triggers notification.

**Done when:** all four types run automatically and no failed gate can update production.

## 4.7 Jenkins staging-first CD and notifications

- [ ] GitHub update to the exact integration branch triggers Jenkins automatically.
- [ ] Pipeline checks out the triggering SHA, runs tests and publishes results.
- [ ] Pipeline builds/pushes once, then deploys the same digests to staging.
- [ ] Production requires successful staging smoke/E2E.
- [ ] Build, test, staging and production failures notify the team.
- [ ] Notification identifies job, build, stage, commit and result without secrets.
- [ ] A bad release leaves production `/api/version/` unchanged.

**Done when:** a good commit progresses automatically and a bad commit stops, notifies and protects production.

## 4.8 Docker Swarm production

- [ ] Establish one manager and two workers; verify with `docker node ls`.
- [ ] Restrict Swarm ports to trusted cluster nodes.
- [ ] Pull immutable ECR images on every required node.
- [ ] Deploy frontend/backend services with multiple backend replicas.
- [ ] Configure health checks, restart policy, update order and rollback policy.
- [ ] Do not use fixed `container_name` or host-local production media volumes.
- [ ] Scale backend up/down and verify availability.
- [ ] Remove one safe task and verify desired state/self-healing.
- [ ] Verify every replica uses RDS and S3.

**Done when:** scaling and self-healing work without losing database or media state.

## 4.9 Blue-Green traffic switch

Use two production colours of the Swarm application, not two databases. Both colours share RDS and S3 and must be schema-compatible.

- [ ] Publish Blue and Green through different agreed ports/entry services.
- [ ] Register them with separate ALB target groups.
- [ ] Keep one target group live and deploy the new digest to the inactive colour.
- [ ] Wait until inactive targets are healthy.
- [ ] Verify health, readiness, version and a user journey before switch.
- [ ] Switch the ALB listener default action to the inactive target group.
- [ ] Run post-switch smoke and observe CloudWatch for a fixed validation window.
- [ ] Keep the previous colour intact until release acceptance.

**Done when:** the ALB listener proves a reversible Blue↔Green switch with the expected version.

## 4.10 CloudWatch monitoring and alarm

- [ ] Expose and document a usable application metrics endpoint.
- [ ] Send application/container/system logs to CloudWatch Logs.
- [ ] Create a compact dashboard for useful health/performance signals.
- [ ] Create at least one meaningful alarm with SNS/email action.
- [ ] Confirm the notification subscription.
- [ ] Trigger the alarm safely, observe notification and restore healthy state.
- [ ] Use monitoring in the post-deployment decision.

**Done when:** the team can see health/performance and a rehearsed alarm produces a notification.

## 4.11 CloudFormation for actual AWS resources

- [ ] Template the resources the final architecture actually uses, not a parallel fictional design.
- [ ] Cover as much as Learner Lab permits: networking/security, EC2/roles, ECR, S3, RDS, ALB/target groups and CloudWatch/SNS.
- [ ] Parameterise environment/names and output endpoints/resource IDs.
- [ ] Keep secrets out of templates and parameter files.
- [ ] Validate and deploy/update the stack successfully.
- [ ] Run a safe stack update to prove repeatability.
- [ ] If an existing manual resource cannot be migrated safely in three days, template its intended equivalent and document the exact gap.

**Done when:** a deployed stack owns or reproducibly defines actual AWS infrastructure within stated lab limits.

## 4.12 Automatic rollback

```text
save live colour + known-good digests
→ deploy and verify inactive colour
→ switch ALB
→ post-switch check
→ failure: switch back automatically
→ verify known-good version
→ notify
```

- [ ] Persist known-good colour, commit and digests before release.
- [ ] Make rollback an automatic Jenkins/Ansible failure path.
- [ ] Switch traffic back; redeploy known-good only if the previous colour is unavailable.
- [ ] Verify version, health/readiness and one user journey after rollback.
- [ ] Use a safe app/config failure; do not corrupt RDS or delete resources.
- [ ] Notify the team of deployment failure and rollback result.

**Done when:** a rehearsed failed release automatically returns traffic to the known-good immutable version.

---

# 5. Three-day execution plan

| Day | Priority | End-of-day team outcome |
|---|---|---|
| Day 1 | Integrate and stabilise | Exact branch triggers Jenkins; four tests gate staging; ECR build-once and notifications work; AWS prerequisites are ready |
| Day 2 | Finish all core requirements | Swarm production runs on RDS + S3; same digests are promoted; scaling, self-healing and controlled migration work |
| Day 3 | Finish advanced areas and freeze | CloudFormation, CloudWatch, Blue-Green and automatic rollback work; final acceptance/demo pass |

Parallel work is encouraged inside a day, but no member may bypass a shared gate.

---

# 6. Day 1 — Stable CI, staging and prerequisites

## Day 1 team gate

- [ ] Integration/Jenkins/submission branch is frozen.
- [ ] GitHub trigger checks out the exact SHA.
- [ ] Four test methodologies run as reliable gates.
- [ ] ECR images use SHA tags/digests and are built once.
- [ ] Same digests deploy to verified staging.
- [ ] Bad release is blocked; production remains unchanged; notification arrives.
- [ ] RDS permission is confirmed or fallback declared.
- [ ] Swarm inventory, ALB approach and AWS resource names are frozen.

## M1 Nhu — Integration lead

- [ ] Collect each member's branch, completed work, blocker and next deliverable.
- [ ] Fill and announce the integration contract.
- [ ] Merge valid Phase 7 work one branch at a time and rerun relevant checks.
- [ ] Freeze production URL and ALB Blue/Green routing mechanism.
- [ ] Record current production version before promotion.
- [ ] Coordinate good-path and bad-path staging demonstrations.
- [ ] Reject duplicate redesigns, leaked secrets and unsupported “done” claims.

**Done:** integrated baseline is stable and every Day 2 dependency has an owner.

## M2 Long — Testing lead

- [ ] Audit existing tests and fill only missing methodology gaps.
- [ ] Finalise one stable command for each of the four test types.
- [ ] Ensure failures exit non-zero and provide Jenkins-readable result paths.
- [ ] Verify staging frontend, health, readiness, version and product API.
- [ ] Run one safe failure with M5 and prove production stays unchanged.
- [ ] Give M4/M5 inactive-colour and production smoke commands.

**Done:** Jenkins can treat all four test types as dependable release gates.

## M3 Minh — S3/shared-state lead

- [ ] Verify staging S3 and retain existing valid work.
- [ ] Freeze bucket, region, variable names and IAM approach without secrets.
- [ ] Upload/read one known media object and record a safe identifier.
- [ ] Give M4/M5 the production S3 configuration interface.
- [ ] Prepare Day 2 replica-replacement persistence check.
- [ ] Support S3/IAM CloudFormation work for Day 3.

**Done:** S3 is verified and reusable by production replicas.

## M4 Trung — Infrastructure/Ansible lead

- [ ] Finalise non-interactive, idempotent staging deployment; give M5 one command.
- [ ] Confirm Swarm inventory, SSH path, ports and security-group needs.
- [ ] Confirm RDS permission/quota/region/budget; report blockers immediately.
- [ ] Freeze private RDS networking and ALB target-group design.
- [ ] Prepare separate staging/production variables.
- [ ] Prepare one controlled migration and one Swarm deployment command.
- [ ] Align CloudFormation with actual architecture; do not duplicate resources blindly.

**Done:** staging is repeatable and Day 2 production prerequisites are actionable.

## M5 Win — Jenkins/CD lead

- [ ] Complete automatic trigger for the exact integration branch/SHA.
- [ ] Integrate M2's four test commands and publish results.
- [ ] Build once, tag with SHA, push to ECR and record digests.
- [ ] Call M4's staging deployment with those exact digests.
- [ ] Run staging smoke/E2E and gate all production stages.
- [ ] Configure build, test and deployment failure notifications.
- [ ] Demonstrate one good and one safely failed path with M1/M2.

**Done:** Jenkins reliably delivers to staging and cannot promote a failed release.

**If behind:** finish integration branch → tests → ECR build once → staging → gate → notification. Do not start Blue-Green while these are red.

---

# 7. Day 2 — Production core on AWS

## Day 2 team gate — core 9/9

- [ ] AWS: EC2, ECR, RDS, S3 and supporting services work.
- [ ] Containerised frontend/backend run; production DB is RDS or documented fallback.
- [ ] CI builds both tiers and runs/publishes tests from GitHub updates.
- [ ] Staging-first CD promotes only after PASS.
- [ ] Four test methodologies work.
- [ ] Jenkins automates the defined stages.
- [ ] Ansible configures/deploys repeatably.
- [ ] Build, test and deployment notifications work.
- [ ] Swarm scales, manages desired state and self-heals.

## M1 Nhu — Production acceptance

- [ ] Control merge/deploy order and freeze unrelated changes.
- [ ] Accept RDS, S3, Swarm and production URL proofs.
- [ ] Confirm staging and production use the same digests.
- [ ] Coordinate scaling, replacement and persistence scenarios.
- [ ] Check all nine core requirements against working behaviour.
- [ ] Record known-good SHA/digests and declare core freeze.

**Done:** core 9/9 is green or an external lab blocker is precisely documented.

## M2 Long — Production verification

- [ ] Run production smoke tests.
- [ ] Verify RDS-backed read/write or stable data marker.
- [ ] Test during/after backend scaling and task replacement.
- [ ] Verify health, readiness, version, user journey and S3 media.
- [ ] Supply Day 3 pre-switch/post-switch/rollback checks.

**Done:** production functionality and persistence are independently verified.

## M3 Minh — Production S3 validation

- [ ] Verify intended S3 bucket and IAM path.
- [ ] Verify known media from multiple replicas.
- [ ] Replace/restart a task with M4 and verify the same media.
- [ ] Confirm no production dependency on local media storage.
- [ ] Finalise S3/IAM CloudFormation inputs.

**Done:** media survives scaling and replaceable compute.

## M4 Trung — Swarm and RDS lead

- [ ] Establish/verify one manager and two workers.
- [ ] Create/configure private RDS or approved fallback.
- [ ] Configure ECR and production secrets safely.
- [ ] Run controlled migration exactly once.
- [ ] Deploy frontend and multiple backend replicas from immutable digests.
- [ ] Demonstrate scale up/down, convergence and self-healing.
- [ ] Verify replicas use RDS and S3.
- [ ] Prepare Blue/Green entry points and ALB target registration.

**Done:** repeatable orchestration and durable shared state work.

## M5 Win — Production promotion

- [ ] Call migration/deployment interfaces in the correct order.
- [ ] Pass production variables and digests securely.
- [ ] Promote exact staging-tested images without rebuilding.
- [ ] Wait for convergence and call production checks.
- [ ] Save successful commit/digests as known-good state.
- [ ] Confirm deployment failure notification.
- [ ] Scaffold Day 3 Blue-Green and rollback stages.

**Done:** Jenkins promotes a tested immutable release safely into Swarm.

**If behind:** prioritise RDS/S3 → Swarm → migration → smoke → scale/self-heal → known-good state. Start advanced work only after core 9/9.

---

# 8. Day 3 — Advanced delivery, rollback and freeze

## Day 3 team gate — four advanced areas

- [ ] CloudFormation represents/deploys actual AWS infrastructure within lab limits.
- [ ] CloudWatch receives useful data; dashboard and tested alarm work.
- [ ] Blue-Green switches ALB between healthy target groups.
- [ ] Failed verification automatically restores known-good traffic/version.
- [ ] Core 9/9 still passes.
- [ ] Final branch, URL, evidence ownership and demo order are unambiguous.

## M1 Nhu — Final audit/demo coordinator

- [ ] Verify core 9/9 and four advanced areas against live behaviour.
- [ ] Ensure each proof has one filename and owner.
- [ ] Verify final branch equals Jenkins and submission branch.
- [ ] Freeze production URL, current colour, known-good SHA/digests.
- [ ] Run a timed, reversible demo rehearsal.
- [ ] Stop enhancements and approve final freeze.

**Done:** one coherent and defensible system/demo is ready.

## M2 Long — Advanced acceptance

- [ ] Finalise pre-switch, post-switch and rollback smoke suites.
- [ ] Verify inactive colour before ALB switch and new version after switch.
- [ ] Trigger the agreed safe failure and verify automatic restoration.
- [ ] Confirm version, journey, RDS data and S3 media after rollback.
- [ ] Support CloudWatch alarm testing and final regression.

**Done:** tests objectively prove Blue-Green and rollback.

## M3 Minh — CloudWatch/S3 support

- [ ] Verify S3 persistence after Blue-Green and rollback.
- [ ] Help connect application/runtime logs and metrics to CloudWatch.
- [ ] Help build the minimal dashboard and alarm view.
- [ ] Observe one reversible alarm scenario and restore normal state.
- [ ] Verify S3/IAM in CloudFormation matches deployment.

**Done:** media and observability remain healthy through release/recovery.

## M4 Trung — IaC/Blue-Green infrastructure

- [ ] Validate and deploy/update CloudFormation for actual resources.
- [ ] Finish Blue/Green Swarm entry points and ALB target groups.
- [ ] Verify target health and deterministic listener switch command.
- [ ] Keep previous colour live during validation.
- [ ] Give safe switch-back commands to M5.
- [ ] Verify CloudWatch infrastructure and alarm dependencies.

**Done:** infrastructure, observability and traffic switch are repeatable.

## M5 Win — Blue-Green/automatic rollback

- [ ] Deploy new digest to inactive colour only.
- [ ] Call inactive-colour checks before switching.
- [ ] Switch ALB listener and run post-switch checks.
- [ ] Monitor the defined health/alarm validation window.
- [ ] On failure, switch back automatically and verify known-good.
- [ ] Notify deployment failure and rollback result.
- [ ] Run one successful release and one safe failed-release rollback.

**Done:** Jenkins completes a reversible, observable Blue-Green deployment.

**If behind:** finish CloudFormation proof → CloudWatch alarm → successful switch → automatic rollback → core regression. Document real lab limits; do not fake completion.

---

# 9. Requirements traceability and final acceptance

## 9.1 Core requirements

| Requirement | Primary proof | Owner |
|---|---|---|
| AWS integration | EC2/ECR/RDS/S3 live architecture | M4 + M3 |
| Containerised services | Compose/Swarm images and services | M4 + M5 |
| Continuous Integration | GitHub-triggered Jenkins build/tests | M5 + M2 |
| Continuous Deployment | Staging PASS then production | M5 |
| Testing framework | Four distinct automated types | M2 |
| Automation tool | Full Jenkins pipeline | M5 |
| Configuration management | Repeatable Ansible run | M4 |
| Automated alerting | Build/test/deploy notifications | M5 |
| Orchestration | Swarm replicas, scaling, self-healing | M4 + M2 |

## 9.2 Selected advanced areas

| Area | Primary proof | Owner |
|---|---|---|
| Infrastructure as Code | Deployed/updated CloudFormation stack | M4 |
| Monitoring and alerting | Metrics/logs, dashboard, tested alarm | M3 + M4 |
| Advanced deployment | ALB Blue↔Green switch and version | M4 + M5 |
| Additional enhancement | Automatic known-good rollback | M5 + M2 |

## 9.3 Final checks

- [ ] Production ALB serves the expected version.
- [ ] Health, readiness, version, frontend and product API pass.
- [ ] All four test types pass.
- [ ] RDS data and S3 media survive replacement and rollback.
- [ ] Staging/production digests match the intended release.
- [ ] Ansible reruns safely; CloudFormation validate/update succeeds.
- [ ] CloudWatch alarm/notification works.
- [ ] Blue-Green and automatic rollback are rehearsed.
- [ ] No secrets appear in Git, logs, screenshots or submitted configuration.

---

# 10. Evidence and demo rules

No separate evidence tracker `.md` is required. Save strong screenshots in each member's existing evidence folder:

```text
docs/evidence/member-<n>/m<n>-p<phase>-<sequence>-<description>.png
```

Capture action plus result where possible. Configuration alone is not proof that a service works. Prioritise: triggered pipeline/SHA; four tests; ECR digests; failed gate/notification/unchanged production; idempotent Ansible; private RDS/readiness; Swarm scale/self-heal; S3 persistence; CloudFormation update; CloudWatch alarm; ALB colour switch; and known-good version after rollback.

Demo failures must be safe and reversible. Never delete RDS, corrupt data, expose secrets, terminate the only manager, or destroy the CloudFormation stack during the demo.

---

# 11. Use this TODO with AI

Give AI: this TODO; member/day/task; branch/status/recent commits; relevant changed files; latest output; sanitised AWS state; existing evidence names; and current blocker. Never provide secrets.

```text
Read A2_TODO_Phase2_v2.md. Focus only on my member role and today's
checklist. Audit the delta between my implementation and the relevant
Done/Day Gate criteria. Classify work as KEEP, MODIFY, ADD or BLOCKED.
Do not restart or refactor valid completed work.

Return first:
CURRENT STATUS
KEEP
MODIFY/ADD
BLOCKERS AND DEPENDENCIES
NEXT 3 ACTIONS
VERIFICATION
EVIDENCE OPPORTUNITY
DONE WHEN

Then guide the next action. Distinguish defined in code, created in AWS,
configured, connected and verified. Warn before unsafe AWS actions and
never request secret values.
```

Audit is not the task. Continue implementation, test, capture the strongest safe proof, update the checklist and move to the next dependency.

---

# 12. Phase 7 detailed playbook — CI and staging-first CD

## 12.1 Phase objective

Convert the team's separate CI, test, S3, Ansible and Docker work into one automatic path:

```text
GitHub update
→ Jenkins triggered automatically
→ exact commit checked out
→ tests pass
→ immutable images built once and pushed to ECR
→ same images deployed to staging by Ansible
→ deployed smoke/E2E pass
→ production promotion becomes eligible
```

Phase 7 is not complete because a Jenkins build is green. It is complete only when a real GitHub update reaches verified staging automatically and a bad release cannot touch production.

## 12.2 Required repository interfaces

Confirm or create equivalent files; do not rename working files only to match this example:

```text
Jenkinsfile                         # pipeline and failure behaviour
docker-compose.yml                  # local/staging services
docker-stack.yml                    # production Swarm definition
server/Dockerfile                   # immutable backend image
client/Dockerfile                   # immutable frontend image
ansible/inventory/...               # staging and production hosts
ansible/playbooks/...               # configure/deploy/migrate interfaces
scripts/smoke_test.py               # deployed smoke gate, if already used
tests/ or existing test locations   # four test methodologies
infra/ or cloudformation/            # actual AWS templates
```

One function must have one owner. Jenkins orchestrates; it should call stable test and Ansible interfaces instead of duplicating their logic inside shell blocks.

## 12.3 Freeze the Jenkins contract

M2, M4 and M5 agree on these inputs/outputs before editing the pipeline:

| Interface | Provider | Consumer | Required result |
|---|---|---|---|
| Four test commands | M2 | M5 | Exit `0` pass; non-zero fail; report path known |
| Staging deploy command | M4 | M5 | Accepts immutable backend/frontend image refs |
| Production migration command | M4 | M5 | Runs once and returns a reliable exit code |
| Swarm deploy/update command | M4 | M5 | Accepts colour and immutable image refs |
| Smoke commands | M2 | M5 | Accept target URL and expected Git SHA |
| S3 variables | M3 | M4/M5 | Names and IAM method, never secret values |
| Acceptance decision | M1 | All | PASS/BLOCKED with reason |

## 12.4 Recommended Jenkins stage order

```text
1. Checkout exact triggering SHA
2. Set version and image names
3. Backend unit/integration tests
4. Frontend unit tests
5. Web UI/E2E preparation or test stage
6. Publish test results
7. Build backend/frontend images once
8. Authenticate and push to ECR
9. Resolve/store digests
10. Deploy staging through Ansible
11. Staging smoke + Web UI/E2E
12. Mark artifact eligible for production
13. Notify result in post/failure handling
```

Production deployment may be defined in the Jenkinsfile during Phase 7, but it stays gated until Phase 8 is ready.

## 12.5 Image and version procedure

Use environment-specific names supplied through Jenkins, not hard-coded examples:

```bash
GIT_SHA="$(git rev-parse HEAD)"
aws ecr get-login-password --region "$AWS_REGION" |
  docker login --username AWS --password-stdin "$ECR_REGISTRY"
docker build -t "$BACKEND_REPO:$GIT_SHA" server
docker build -t "$FRONTEND_REPO:$GIT_SHA" client
docker push "$BACKEND_REPO:$GIT_SHA"
docker push "$FRONTEND_REPO:$GIT_SHA"
```

The implementation must additionally query/record digests and deploy `repository@sha256:...` where practical. Do not print credentials. Do not copy these commands without first defining and validating every variable.

## 12.6 Staging deployment procedure

1. Jenkins passes the exact image references and non-secret configuration to Ansible.
2. Ansible authenticates the staging host to ECR using its role or a protected mechanism.
3. Ansible renders/updates staging configuration without committing `.env`.
4. Compose pulls the referenced images and recreates only changed services.
5. Staging keeps its PostgreSQL container and named data volume.
6. Ansible waits for services to become ready.
7. Jenkins runs external smoke and E2E checks against the staging URL.

Minimum operator checks:

```bash
docker compose config
docker compose pull
docker compose up -d
docker compose ps
curl -fsS "$STAGING_URL/healthz/"
curl -fsS "$STAGING_URL/readyz/"
curl -fsS "$STAGING_URL/api/version/"
```

`docker compose config` may reveal resolved secrets; do not capture or publish its secret-bearing output.

## 12.7 Required negative path

Use a reversible test failure or safe staging-only misconfiguration:

1. Record production `/api/version/`.
2. Trigger the pipeline with the agreed bad change.
3. Confirm the relevant stage fails.
4. Confirm all production stages are skipped.
5. Confirm the team receives notification.
6. Query production `/api/version/` again and prove it is unchanged.
7. Revert the bad change and restore a green baseline.

Do not break the production database, delete resources or expose a deliberately vulnerable public endpoint.

## 12.8 Phase 7 completion gate

- [ ] Webhook-triggered run requires no manual `Build Now` action.
- [ ] Jenkins reports the same SHA as the GitHub update.
- [ ] All four test types have stable commands and expected result handling.
- [ ] ECR contains backend/frontend SHA-tagged images and recorded digests.
- [ ] Staging reports the expected SHA through `/api/version/`.
- [ ] Staging readiness confirms database and storage.
- [ ] Bad path stops before production and sends notification.
- [ ] Production version remains unchanged after the bad path.
- [ ] M1 declares Phase 7 PASS.

---

# 13. Phase 8 detailed playbook — production orchestration and shared state

## 13.1 Phase objective

Deploy a scalable production system where application tasks are replaceable but database and media state remain durable.

```text
Swarm manager + worker 1 + worker 2
→ replicated frontend/backend services
→ shared private RDS PostgreSQL
→ shared S3 media
→ desired state, health checks, rolling updates and self-healing
```

## 13.2 Infrastructure readiness order

1. Verify VPC/subnets, security groups and IAM roles.
2. Verify manager/worker inventory and internal reachability.
3. Create/verify private RDS and S3 access.
4. Install/configure Docker idempotently through Ansible.
5. Initialise Swarm and join workers securely.
6. Authenticate nodes to ECR.
7. Validate the production stack configuration.
8. Run the single controlled migration.
9. Deploy services and verify convergence.
10. Run external acceptance, scaling and self-healing tests.

## 13.3 Minimum network rules

| Traffic | Source | Destination | Principle |
|---|---|---|---|
| HTTP/HTTPS | ALB/client as designed | production entry service | Only published application traffic |
| PostgreSQL 5432 | Swarm/backend security group | RDS security group | Never `0.0.0.0/0` |
| Swarm management 2377 | trusted manager/node SG | manager | Cluster only |
| Swarm node communication 7946 TCP/UDP | cluster SG | cluster nodes | Cluster only |
| Overlay networking 4789 UDP | cluster SG | cluster nodes | Cluster only |
| SSH 22 | approved administration source | EC2 | Restrict as lab permits |

Do not open all ports between the internet and production to “make it work.” Diagnose the exact missing path.

## 13.4 RDS execution steps

1. Check the Learner Lab console/API before changing the architecture.
2. Create a subnet group across suitable subnets if required.
3. Create PostgreSQL with public access disabled and a dedicated security group.
4. Store the endpoint separately from username/password.
5. Put credentials in the selected secret path.
6. Test DNS and port reachability from an authorised node.
7. Test authenticated database connection without exposing the password.
8. Run `python manage.py migrate` through the controlled interface once.
9. Deploy replicas using the same database connection.
10. Test a harmless data marker before and after task replacement.

RDS “Available” proves resource creation, not application connectivity. `/readyz/` and a database-backed application journey prove the connection.

## 13.5 Swarm stack rules

- Use ECR image references supplied at deployment time.
- Do not include the staging `db` service when RDS is active.
- Do not use `build:` in the production stack.
- Do not use fixed `container_name`.
- Do not bind production media to one node's local path.
- Configure replica count, restart policy and update/rollback behaviour.
- Use service/container health checks compatible with the image.
- Keep secrets outside the committed stack file.

Representative verification commands:

```bash
docker node ls
docker stack services "$STACK_NAME"
docker stack ps "$STACK_NAME" --no-trunc
docker service inspect "$BACKEND_SERVICE" --pretty
curl -fsS "$PRODUCTION_URL/healthz/"
curl -fsS "$PRODUCTION_URL/readyz/"
curl -fsS "$PRODUCTION_URL/api/version/"
```

## 13.6 Scaling test

1. Record current replica count and expected version.
2. Scale the backend to the agreed higher replica count.
3. Wait until desired and running replicas match.
4. Run repeated health, readiness and product requests.
5. Verify RDS-backed data and known S3 media.
6. Scale back only if that is the agreed final configuration.

Example interface:

```bash
docker service scale "$BACKEND_SERVICE=$TARGET_REPLICAS"
```

## 13.7 Self-healing test

1. Choose one application task, not the sole manager or database.
2. Record task ID/node and replica count.
3. stop/remove that task through the agreed safe method.
4. Observe Swarm create a replacement task.
5. Confirm desired/running counts converge.
6. Verify health, readiness, version, RDS data and S3 media.

Self-healing proof must show both failure and restored desired state.

## 13.8 Phase 8 completion gate

- [ ] One manager and two workers are `Ready`.
- [ ] Production services use ECR immutable images.
- [ ] Multiple backend replicas run successfully.
- [ ] Private RDS is connected, or approved fallback is documented.
- [ ] S3 media works from replaceable tasks.
- [ ] Controlled migration ran once.
- [ ] Scaling converges and site remains functional.
- [ ] Swarm replaces a failed task.
- [ ] Data and media persist after replacement.
- [ ] M1 declares core requirement 9 and Phase 8 PASS.

---

# 14. Phase 9 detailed playbook — release protection and recovery

## 14.1 Phase objective

Prove that a failed release is detected, production is protected and the known-good version can be restored automatically without damaging shared state.

## 14.2 Known-good release record

Before every production change, the pipeline records:

```text
Release timestamp/build number
Live colour
Git commit SHA
Backend ECR repository + digest
Frontend ECR repository + digest
Database migration identifier/status
Production /api/version/ result
```

Store this as protected pipeline state or an auditable small deployment manifest without secrets. A mutable `latest` tag is not a rollback record.

## 14.3 Safe failure scenarios

Choose one scenario that exercises the deployment gate without risking persistent data:

| Scenario | Expected detection | Recovery |
|---|---|---|
| New image fails health check | target/service never healthy | Keep/switch to previous colour |
| Wrong non-secret runtime setting on inactive colour | readiness or smoke fails | Do not switch traffic |
| Post-switch user journey fails | post-switch smoke fails | ALB switches back |
| Test intentionally fails before deploy | Jenkins test stage fails | Production never changes |

Do not use destructive schema changes, RDS deletion, bucket deletion, leaked credentials or manager termination as the demo failure.

## 14.4 Rollback state machine

```text
CURRENT_KNOWN_GOOD
→ deploy candidate to inactive colour
→ candidate healthy?
   no  → abort + notify; live colour unchanged
   yes → switch ALB
→ post-switch checks pass?
   yes → candidate becomes KNOWN_GOOD
   no  → switch ALB back automatically
         verify old version and notify rollback result
```

Only update `KNOWN_GOOD` after the validation window passes. Otherwise the pipeline may accidentally record the broken candidate as the recovery target.

## 14.5 Recovery verification

After rollback, test all of the following:

- [ ] ALB routes to the previous colour.
- [ ] `/api/version/` reports the previous Git SHA/version.
- [ ] `/healthz/` and `/readyz/` pass.
- [ ] Frontend and product API pass.
- [ ] One Web UI user journey passes.
- [ ] Pre-existing RDS data remains.
- [ ] Known S3 media remains.
- [ ] Team receives failure and rollback outcome notification.

## 14.6 Migration limitation

Application rollback does not automatically reverse PostgreSQL schema. The three-day implementation therefore requires backward-compatible migrations for the demo:

- add before remove;
- deploy code that tolerates old/new schema during the switch;
- avoid renaming/dropping required columns in the rollback scenario;
- document a forward-fix or separate tested database recovery procedure for destructive changes.

Do not claim full database rollback unless it was genuinely implemented and rehearsed.

## 14.7 Phase 9 completion gate

- [ ] Known-good state is recorded before deployment.
- [ ] Pre-switch failure leaves production untouched.
- [ ] Post-switch failure invokes automatic switch-back.
- [ ] Restored version is proven externally.
- [ ] RDS and S3 state remain correct.
- [ ] Notifications describe failure and recovery result.
- [ ] The scenario is safe and can be repeated for the demo.
- [ ] M1 declares Phase 9 PASS.

---

# 15. Phase 10 detailed playbook — four advanced areas

## 15.1 Start gate

Begin this phase only after the Day 2 core 9/9 gate passes. Existing partial advanced work may continue in parallel only if it does not block core owners or change frozen interfaces.

## 15.2 CloudFormation work package — M4 primary

### Goal

Define the infrastructure the project truly uses so creation and updates are repeatable and reviewable.

### Implementation sequence

1. Inventory current AWS resources and identify manual versus IaC-owned resources.
2. Freeze logical names, parameters and outputs.
3. Split templates/modules only where it improves clarity; one maintainable template is acceptable.
4. Define permitted networking, security groups, IAM roles, EC2, ECR, S3, RDS, ALB/target groups and monitoring resources.
5. Reference secrets securely; never put plaintext credentials in parameters committed to Git.
6. Run template validation.
7. Create/update a real stack.
8. Perform one safe change and update the stack.
9. Compare outputs with the integration contract.
10. Document manual exceptions and Learner Lab limitations.

### Verification examples

```bash
aws cloudformation validate-template --template-body file://"$TEMPLATE_FILE"
aws cloudformation describe-stacks --stack-name "$STACK_NAME"
aws cloudformation describe-stack-events --stack-name "$STACK_NAME"
```

### Done criteria

- [ ] Template is valid and committed.
- [ ] Real stack reaches a successful state.
- [ ] A safe update succeeds.
- [ ] Outputs match resources used by deployment.
- [ ] No plaintext secrets exist in template/history.
- [ ] Manual exceptions are explicit and honest.

## 15.3 CloudWatch work package — M3 + M4

### Goal

Provide operational visibility and a working alarm, not only a dashboard screenshot.

### Implementation sequence

1. Select a minimal signal set: EC2 CPU/disk/memory where available, ALB target health/5xx, application logs and application metric/health signal.
2. Expose/document the application metrics endpoint.
3. Configure log/metric collection through IAM roles.
4. Set log group naming and retention intentionally.
5. Build one compact dashboard tied to production resources.
6. Define one alarm with a meaningful threshold/evaluation period.
7. Connect the alarm to SNS/email and confirm subscription.
8. Trigger the condition safely.
9. Observe `ALARM`, receive notification and restore `OK`.
10. Add the monitoring check to release validation.

### Done criteria

- [ ] Current production data appears in CloudWatch.
- [ ] Application metrics endpoint responds.
- [ ] Dashboard identifies the correct environment/resources.
- [ ] Alarm changes state under a safe test.
- [ ] Notification is received and state returns to normal.
- [ ] Monitoring supports a deployment decision.

## 15.4 Blue-Green work package — M4 + M5

### Goal

Release a candidate without replacing the serving version until it passes acceptance.

### Implementation sequence

1. Confirm the current live colour and target group.
2. Deploy candidate digests to the inactive Swarm colour/entry port.
3. Register/refresh inactive targets.
4. Wait for ALB target health.
5. Run M2's checks directly against the inactive route.
6. Switch the ALB listener default action.
7. Query `/api/version/` through the public production URL.
8. Run post-switch smoke/E2E and observe CloudWatch.
9. Accept the new colour only after the validation window.
10. Leave the previous colour intact until acceptance.

### Done criteria

- [ ] Blue and Green are independently addressable for verification.
- [ ] Target groups report the expected health.
- [ ] Candidate version is proven before and after switch.
- [ ] ALB switch is scripted/repeatable.
- [ ] Previous colour remains available during validation.
- [ ] The team can reverse the switch safely.

## 15.5 Automatic rollback work package — M5 + M2

### Goal

Make recovery an automatic consequence of failed post-deployment validation.

### Implementation sequence

1. Load the last accepted deployment manifest.
2. Deploy and verify the inactive colour.
3. Switch traffic only after pre-switch PASS.
4. Run post-switch checks and monitoring window.
5. On non-zero result/unhealthy signal, invoke switch-back automatically.
6. Verify known-good version and functional checks.
7. Notify failure plus rollback success/failure.
8. Only on full PASS, update the known-good manifest.

### Done criteria

- [ ] Failure path is implemented in pipeline logic, not performed manually after failure.
- [ ] Known-good identity uses digests.
- [ ] Safe failure triggers the path.
- [ ] Traffic returns to known-good automatically.
- [ ] Recovery verification passes.
- [ ] Shared state remains intact.

## 15.6 Phase 10 completion gate

- [ ] CloudFormation Done criteria pass.
- [ ] CloudWatch Done criteria pass.
- [ ] Blue-Green Done criteria pass.
- [ ] Automatic rollback Done criteria pass.
- [ ] Core 9/9 regression still passes.
- [ ] Final demo scenarios are rehearsed in the same order as the pipeline.
- [ ] M1 declares Phase 10 and implementation freeze PASS.

---

# 16. Team operations, handoff and Definition of Done

## 16.1 Branch and merge workflow

1. Each member continues their current feature branch unless M1 announces another branch.
2. Pull/fetch the frozen integration branch before substantial integration work.
3. Keep commits small and scoped to one meaningful change.
4. Open a pull request with purpose, files, verification and dependencies.
5. M1 merges one integration-sensitive change at a time.
6. Re-run affected tests after each merge.
7. Delete/retire duplicate configuration only after the replacement is proven.
8. Jenkins deploys only the frozen integration branch.

Do not commit generated secrets, `.env`, private keys, Ansible Vault passwords, raw Jenkins credentials or exported AWS credentials.

## 16.2 Member handoff template

```text
Member / branch:
Day and phase:
Status: KEEP / MODIFY / ADD / BLOCKED
What now works:
Files changed:
AWS resources affected:
Exact command/interface for next owner:
Required variables (names only):
Latest verification result:
Known limitation/blocker:
Strong evidence filename:
Next owner and requested action:
```

A handoff is incomplete if the next owner must guess the command, inputs, expected output or environment.

## 16.3 Definition of Done for every task

A checkbox is done only when all applicable statements are true:

- [ ] Implementation exists in the correct branch/environment.
- [ ] The intended service/resource is actually created or updated.
- [ ] Connectivity is proven from the real caller.
- [ ] Functional verification passes with a repeatable command or journey.
- [ ] Failure behaviour is understood and safe.
- [ ] No secrets are committed or exposed.
- [ ] Required downstream owner received the stable interface.
- [ ] One strong proof is captured if the claim needs evidence.
- [ ] M1 can map the result to a requirement or dependency.

`Defined`, `created`, `configured`, `connected` and `verified` are different states. Only `verified` satisfies Done.

## 16.4 Daily stand-up format

Keep the update short and operational:

```text
Yesterday/last checkpoint:
Today's required Day Gate item:
Current status:
Next concrete action:
Dependency/owner needed:
Blocker and decision deadline:
```

## 16.5 Critical risks and response

| Risk | Early signal | Response |
|---|---|---|
| Learner Lab blocks RDS/ALB/IAM | Access denied, quota or unsupported service | Capture sanitised proof, notify M1, apply only the documented fallback |
| Pipeline rebuilding images | Different digest per environment | Stop promotion; centralise build and pass recorded digest |
| Concurrent migrations | Multiple replicas/pipelines call migrate | Single locked Jenkins/Ansible migration stage |
| Blue/Green schema incompatibility | Old colour fails after migration | Use backward-compatible migration; do not switch |
| ECR pull fails on workers | tasks rejected/pull denied | Verify node role/login, region, repository URI and token freshness |
| ALB targets unhealthy | 400/timeout/failed health | Check SG, port, path, `ALLOWED_HOSTS` and health endpoint |
| Local media dependency | images disappear between replicas | Stop release; fix S3 configuration/IAM |
| Secrets in logs/evidence | URL/password/token visible | Stop sharing, rotate compromised secret and recapture sanitised proof |
| Too much parallel redesign | conflicting files/interfaces | Freeze contract; M1 chooses one source of truth |
| Day Gate missed | multiple unverified tasks remain | Apply the published catch-up priority; stop enhancements |

## 16.6 What each member should do first after receiving v2

| Member | First action | First handoff |
|---|---|---|
| M1 Nhu | Fill/freeze integration contract and collect status | Exact branch, URLs, owners and Day Gate |
| M2 Long | Produce four stable test/smoke interfaces | Commands, report paths and expected exits to M5 |
| M3 Minh | Verify S3 runtime and known media marker | Variable names and persistence test to M4/M5 |
| M4 Trung | Verify staging deploy, RDS feasibility and Swarm inventory | Stable deploy/migrate interfaces to M5 |
| M5 Win | Align Jenkins trigger/stages with frozen interfaces | Good/bad pipeline result to M1 |

---

# 17. Stop rule

The sprint is complete only when core 9/9, CloudFormation, CloudWatch, Blue-Green, automatic rollback, final regression, branch, URL and demo rehearsal are green.

Until then, do not add optional scanning, CDN, backup tooling, extra dashboards, cosmetic refactoring or storefront features. **The pipeline is the deliverable.**
