# A2 master todo list - rubric-aligned CI/CD plan

## How to use this checklist

- Complete tasks in order. Do not automate a step until it works manually.
- `**[Excellent]**` means a scope-expanding or advanced task. It can be deferred while the core pipeline is unstable, but skipping it lowers the likely mark ceiling, especially for the 7-point Advanced Requirements category.
- Capture evidence as you work: command output, Jenkins stage results, test reports, AWS resource screens, failure notifications, health/version endpoints, and deployed pages.
- This is an AI-assisted brainstorming/planning aid under the assignment's Condition 3 rules. Do not submit it as report text or copy AI-produced code/configuration into the assignment. Make the final choices, implementations, report, diagrams, and presentation yourselves, and record this AI use in the team declaration.

## 1. What the assignment is actually asking for

The web store is already implemented. The assessed product is the DevOps pipeline and its evidence, not new storefront features. The supplied application has three tiers:

- Vue 3/Vite frontend, built into static files and normally served by Nginx.
- Django 5/REST backend, run as a WSGI application with Gunicorn.
- PostgreSQL 14+ database, with schema changes applied by Django migrations.

All nine core requirements must be addressed: AWS integration, containerisation, webhook-triggered CI, staging-to-production CD, four kinds/aspects of testing, Jenkins or similar automation, Ansible or similar configuration management, failure email notifications, and Docker Swarm or Kubernetes orchestration.

The grading rubric awards 35 points: Main Requirements 10, Advanced Requirements 7, Report 6, Video 7, and Code/GitHub/Submission 5. "Very Good" generally means almost all criteria work with at most one improvement identified in a rubric category; "Excellent" means all criteria work with almost no improvement identifiable.

## 2. Resolve administrative and scope issues first
- [ ] Use meaningful feature/fix branches and regular commits spread across the project period.
- [ ] Add the required RMIT comment header to every submitted source file that supports comments; JSON is explicitly exempt.
- [ ] Keep the Condition 3 AI declaration log from day one, member by member.
- [ ] Disable inline AI coding completion while working on the assessment repository.

## 3. Testing technology decision

### What the course materials teach

The Week 5 Jenkins lab discusses testing tools: Selenium for browser/end-to-end testing; JUnit/TestNG, Mockito, Spring Boot Test, and JaCoCo for Java; Cypress/Playwright as modern browser-testing alternatives; and Jenkins test-report plugins. The Week 8 Ansible lab also mentions an end-to-end pipeline simulation. There is no evidence of a dedicated hands-on Django/Vue testing lab in the supplied tutorial files.

The Java tools are not a good fit here: this application is not Java and has no Maven build or JUnit code. Selenium is technically usable, but Playwright is simpler for a new Vue end-to-end suite and is explicitly suggested by both the assignment and application README.

### Required testing stack for the 3.5-week schedule

- Backend unit and API/database integration: `pytest`, `pytest-django`, and `pytest-cov`.
- Web UI/end-to-end: Playwright. Do not also add Selenium or Cypress without a justified need.
- Deployment/smoke: lightweight HTTP checks for `/healthz/`, `/readyz/`, `/api/version/`, the frontend, and one product API path.
- Jenkins reporting: JUnit XML and coverage output from pytest, plus Playwright results/artifacts; archive/publish results even on failures.

This provides four distinct testing aspects without four separate frameworks: backend unit, backend/API integration, Web UI/end-to-end, and deployment smoke testing.

### Minimum test backlog

The assignment requires at least four different kinds/aspects, not merely four test cases. Implement a balanced set such as:

- [ ] Backend unit test: simulated payment validation/brand/decline logic in isolation.
- [ ] Backend unit test: server-side subtotal, taxable-only 5% tax, and total calculation.
- [ ] Backend integration test: successful checkout creates one order and decrements stock exactly once.
- [ ] Backend integration test: declined card creates no order and does not change stock.
- [ ] Backend integration/security test: anonymous/member/merchant/admin permissions return the expected status codes and ownership isolation holds.
- [ ] Web UI test: shop renders products, proving frontend-to-backend-to-database connectivity.
- [ ] Web UI test: register, sign in, add products, declined purchase, approved purchase, and order verification.
- [ ] Deployment smoke test: liveness, readiness, build version/commit, frontend status, and product API status.
- [ ] Failure-mode test: wrong API URL, database unavailable, invalid `ALLOWED_HOSTS`, missing static files, or inaccessible storage causes the expected pipeline/deployment failure.
- [ ] Define and justify realistic coverage thresholds; fail CI below them.
- [ ] Prove a deliberately failing test blocks production deployment and triggers notification.
- [ ] **[Excellent]** Add Vitest, `@vue/test-utils`, jsdom, and Vitest coverage for a few high-value frontend unit/component tests, such as cart merging/quantity clamping or card-input formatting.
- [ ] **[Excellent]** Add `factory_boy` only if backend test-data setup becomes repetitive enough to justify the dependency.
- [ ] **[Excellent]** Automate additional README journeys/failure modes after the required pipeline, orchestration, rollback, evidence, and video path are reliable.

## 4. Understand and run the application manually

- [ ] Read the complete application `README.md`, especially Plans A-F, S3, health checks, tests, verification journeys, and troubleshooting.
- [ ] Run PostgreSQL and create the local database/user.
- [ ] Create the Python environment and install `server/requirements.txt`.
- [ ] Configure the backend environment without committing secrets.
- [ ] Run migrations and `seed_demo`; verify it is idempotent.
- [ ] Start Django locally and verify `/healthz/`, `/readyz/`, `/api/version/`, `/api/docs/`, and `/admin/`.
- [ ] Install frontend dependencies, run the Vite development server, and complete at least the anonymous browsing journey.
- [ ] Run `npm run build` and serve the resulting `client/dist/` as a production-style static bundle.
- [ ] Manually deploy the three tiers to one EC2 instance before writing Ansible or Docker automation.
- [ ] Record the exact manual deployment order: dependencies, configuration, migrations, static collection, frontend build, service start/restart, and verification.

## 5. Design the target architecture and release flow

- [ ] Draw the runtime architecture yourselves: browser/load balancer, frontend service, backend replicas, PostgreSQL/RDS, S3 media, monitoring, and network/security boundaries.
- [ ] Draw the CI/CD sequence yourselves: GitHub webhook -> Jenkins checkout -> build/test -> image registry -> staging -> smoke/E2E -> production -> post-deploy verification/rollback -> notification.
- [ ] Record and justify the selected orchestrator: Docker Swarm, using the course-aligned one-manager/two-worker production topology.
- [ ] Separate staging and production environments, URLs, configuration, and data.
- [ ] Decide where Jenkins runs and ensure it has enough memory to build the Vue bundle; the README warns that a `t3.micro` build can run out of memory.
- [ ] Decide how migrations run exactly once and before code that depends on the new schema receives traffic.
- [ ] Decide how rollback handles both application images and forward-only database migrations.
- [ ] Use immutable version tags based on commit SHA/build number; never rely only on `latest`.
- [ ] Promote the same tested image/artifact from staging to production rather than rebuilding it.

## 6. Containerise all application tiers

- [ ] Create a backend image that installs Python dependencies and runs Django with Gunicorn.
- [ ] Keep secrets and environment-specific configuration out of images.
- [ ] Define where `migrate` and `collectstatic` run; do not run competing migrations in every replica.
- [ ] Create a multi-stage frontend image: Node builds the Vue bundle, then Nginx serves only the static artifact; the final image must not contain Node.
- [ ] Make `client/public/config.js` environment-specific at runtime so the same frontend image can be promoted unchanged.
- [ ] Use the official PostgreSQL image for local/Compose testing or RDS in AWS.
- [ ] Add health checks and sensible restart behavior.
- [ ] Use Docker Compose locally to prove the complete system and service dependencies.
- [ ] Verify an image built on the CI node runs unchanged in staging and production.

## 7. Provision and configure AWS

- [ ] Provision exactly five EC2 instances for the agreed topology shown below.

| EC2 | Suggested name | Purpose |
|---|---|---|
| 1 | `jenkins-ansible` | Jenkins controller/build host and Ansible control node. |
| 2 | `staging` | Isolated staging deployment and smoke/Playwright target. |
| 3 | `prod-swarm-manager` | Production Swarm control node. |
| 4 | `prod-swarm-worker-1` | Production application workloads. |
| 5 | `prod-swarm-worker-2` | Production application workloads and failover capacity. |

- [ ] Size `jenkins-ansible` with enough memory for the Vue build; do not assume a `t3.micro` is sufficient because the application README warns it can run out of memory.
- [ ] Plan security groups using least privilege: public HTTP/HTTPS only where needed, Jenkins access restricted, backend/database internal where possible, PostgreSQL never open to the internet.
- [ ] Keep Jenkins/Ansible off the production Swarm and keep staging isolated from production.
- [ ] Configure the three production nodes as one Swarm with one manager and two workers.
- [ ] Place the production manager in `drain` availability if application workloads should run only on the two workers.
- [ ] Prefer Amazon RDS PostgreSQL for the database; otherwise document and back up a self-managed database.
- [ ] Create an ECR repository for frontend/backend images or justify an alternative registry.
- [ ] Create an S3 bucket for uploaded product media.
- [ ] Attach an EC2 instance role/profile that permits only the required S3 operations; do not store long-lived AWS keys in `.env` or Jenkins source.
- [ ] If Learner Lab restricts IAM creation, determine whether the provided `LabRole` can be attached and document the constraint.
- [ ] Configure `USE_S3=True`, bucket name, and region in the backend environment.
- [ ] Decide how browsers read media objects: narrowly scoped public reads for `media/*`, or private S3 behind CloudFront/signed access. Do not make write access public.
- [ ] Verify upload from a merchant/admin, database storage of the object key, direct rendering in the storefront, and access from more than one backend replica.
- [ ] Preserve the frontend's bundled UI assets separately; moving all `client/public/images/` to S3 is not required.
- [ ] Configure an Application Load Balancer/target group if using multiple production backends, and account for private-IP `Host` headers in Django `ALLOWED_HOSTS`.

## 8. Automate server configuration with Ansible

- [ ] Create inventories for staging and production.
- [ ] Make playbooks idempotent and demonstrate that a second run reports no unnecessary changes.
- [ ] Install/configure Docker and required host packages.
- [ ] Configure users, directories, firewall/security-related host settings, service files, and deployment prerequisites.
- [ ] Configure/join Docker Swarm nodes or deploy the selected orchestrator prerequisites.
- [ ] Keep secrets in Jenkins credentials, Ansible Vault, SSM Parameter Store, Secrets Manager, or orchestrator secrets—not plaintext inventory.
- [ ] Add Ansible smoke verification using readiness/version endpoints.

## 9. Build the Jenkins CI/CD pipeline

- [ ] Configure GitHub webhook authentication and prove every relevant GitHub update automatically triggers Jenkins.
- [ ] Add stages for checkout and build metadata (`APP_VERSION`, `GIT_COMMIT`).
- [ ] Install backend/frontend test dependencies in isolated build environments.
- [ ] Run backend unit/integration suites and publish JUnit/coverage results.
- [ ] **[Excellent]** If the optional Vitest suite is implemented, run it and publish its results.
- [ ] Build the frontend and backend container images.
- [ ] Scan or validate artifacts before publishing where practical.
- [ ] Push commit-tagged images to ECR/registry only after required CI gates pass.
- [ ] Deploy the exact images to staging.
- [ ] Run database migrations once, readiness checks, smoke tests, and Playwright against staging.
- [ ] Automatically deploy the same images to production only if every staging gate passes.
- [ ] Verify production `/healthz/`, `/readyz/`, `/api/version/`, frontend, and product path after deployment.
- [ ] Send email to the team for build, test, staging deployment, and production deployment failures, including job/build/commit context.
- [ ] Ensure credentials are masked and not printed in console logs.
- [ ] Demonstrate that a bad commit/test failure never updates production.

## 10. Orchestration, scaling, and recovery

- [ ] Define frontend, backend, and supporting services in Docker Swarm stack files or Kubernetes manifests.
- [ ] Run more than one backend replica and prove requests and uploaded images work through the load balancer.
- [ ] Configure liveness and readiness appropriately; do not restart a healthy backend merely because the database is briefly unavailable.
- [ ] Demonstrate self-healing by stopping a container/node and showing service recovery.
- [ ] Demonstrate scaling under a simple traffic spike and record evidence.
- [ ] Document what state is externalised: PostgreSQL/RDS and S3, not container-local disk.
- [ ] Test a failed deployment and a return to the last stable application version.

## 11. Excellent-mark extensions

- [ ] **[Excellent]** Provision EC2, RDS, S3, IAM roles/policies, security groups, load balancer, and related networking with AWS CloudFormation.
- [ ] **[Excellent]** Add real-time monitoring with CloudWatch or Prometheus/Grafana, including useful application/infrastructure metrics, dashboards, and actionable alerts.
- [ ] **[Excellent]** Implement and thoroughly test blue-green or canary deployment, using `/api/version/` to prove the active commit and safe traffic switching.
- [ ] **[Excellent]** Add automatic rollback when post-deploy health/error thresholds fail.
- [ ] **[Excellent]** Create and test a PostgreSQL backup and restore procedure, not just a backup job.
- [ ] **[Excellent]** Add static analysis, dependency vulnerability scanning, secret scanning, and container image scanning as CI gates.
- [ ] **[Excellent]** Put CloudFront/CDN in front of the frontend and/or S3 media with a justified cache/invalidation strategy.
- [ ] **[Excellent]** Centralise structured logs and make them searchable by timestamp, service, environment, and commit/build.
- [ ] **[Excellent]** Document and test a zero-downtime, backward-compatible database migration procedure.

## 12. Evidence, report, video, and submission

- [ ] Maintain an evidence matrix mapping every core/advanced requirement to implementation, test, screenshot/log, and demo timestamp.
- [ ] Capture genuine evidence only from the team's running system; the brief prohibits AI-generated or fabricated proof.
- [ ] Write the PDF report yourselves, professionally formatted and within 25 pages excluding the listed exclusions.
- [ ] Include title page, contents, problem/solution, tools/features, every requirement, testing strategy and justification, both architecture diagrams, known problems, self-evaluation/reflection, responsibilities, conclusion, references, and appendices.
- [ ] Explain design decisions and trade-offs, not just configuration steps.
- [ ] Include a runtime architecture diagram and CI/CD pipeline sequence diagram created by the team using a non-generative drawing tool.
- [ ] Prepare one unlisted YouTube video, no longer than 20 minutes, with every member presenting their own work if team work is confirmed.
- [ ] Demonstrate both staging and production, an automatic webhook trigger, a failing change stopping release and sending email, a successful staging-to-production release, and rollback/advanced deployment in action.
- [ ] Rehearse with a timed runbook and pre-created safe good/bad commits.
- [ ] Create a clean source folder identical to the assigned repository's final commit and include all pipeline/test/IaC/orchestration files plus a from-scratch README.
- [ ] Add `Github.txt` with the complete assigned private repository URL.
- [ ] Add `Youtube.txt` with the unlisted video URL.
- [ ] Add the completed and team-acknowledged `COSC2767_Condition3_Declaration_[YourGroupName].pdf`, even if no AI was used.
- [ ] Build one ZIP containing source code, `Document.pdf`, `Github.txt`, `Youtube.txt`, and the AI declaration.
- [ ] Verify the ZIP from scratch on a clean/lab machine, compare it with the final Git commit, and submit an early draft before the final submission.
