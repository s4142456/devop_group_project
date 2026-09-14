<!--
RMIT University Vietnam
Course: COSC2767|COSC2805 Systems Deployment and Operations
Semester: 2026B
Assessment: Assignment 2
Author: Nhu Phan
ID: s4117555
Created date: 14/09/2026
Last modified: 14/09/2026
Acknowledgement: AWS CloudFormation User Guide and CLI reference, team
project documentation. Claude Code (Anthropic) assisted with implementation.
-->

# Infrastructure as Code — AWS CloudFormation

`main.yaml` defines the reusable AWS resources for the RMIT Store. It is deployed as
the stack **`meowgang-a2-infra`** in **`us-east-1`**. The main Jenkins pipeline reads
the stack's outputs, so resource names live in one place:

```
main.yaml ──deploy──▶ stack meowgang-a2-infra ──Outputs──▶ Jenkinsfile ──extra vars──▶ Ansible ──▶ Swarm stack
                                                         (Resolve CloudFormation Outputs)
```

## Scope

| Resource | Status | Used by |
|---|---|---|
| S3 `meowgang-media-staging-<account-id>` (+ TLS-only bucket policy) | **CloudFormation-managed** | Staging backend (`AWS_STORAGE_BUCKET_NAME`) |
| ECR `meowgang-a2/rmit-store-backend` | **CloudFormation-managed** | Jenkins push, staging + prod pull |
| ECR `meowgang-a2/rmit-store-frontend` | **CloudFormation-managed** | Jenkins push, staging + prod pull |
| Security group `meowgang-swarm-node-cfn` (+ 6 member-only ingress rules) | **CloudFormation-managed**, not attached | Baseline for the next host replacement |
| EC2 instances (Jenkins, staging, prod manager + 2 workers, Grafana) | Manually managed | Configured by Ansible |
| Security groups `sg-prod`, `sg-staging`, `sg-grafana`, `sg-jenkins` | Manually managed | Attached to running hosts |
| S3 `meowgang-media-staging-01` (live product images) | Manually managed | Production backend |
| ECR `meowgang/rmit-store-backend`, `meowgang/rmit-store-frontend` | Manually managed, no longer pushed to | Previous images, Swarm rollback history |
| IAM `LabRole` / `LabInstanceProfile` | Externally managed (AWS Academy) | EC2 access to S3 and ECR |

### Why the rest is not migrated

- **EC2 and attached security groups:** CloudFormation can't adopt them without
  replacing or importing live Swarm nodes. That would risk the running environments,
  including the production PostgreSQL volume.
- **Legacy media bucket:** it holds production's live product images. Moving production
  to a new empty bucket would break every image.
- **Legacy ECR repositories:** Jenkins now pushes to the CloudFormation repositories.
  The old repositories are left in place, so earlier images stay available.
- **IAM:** in AWS Academy Learner Lab, IAM role creation is restricted. Hosts use
  the provided `LabInstanceProfile`, so the template creates no IAM resources and needs
  no `CAPABILITY_IAM`.

## Design notes

- **Retention:** the bucket and both repositories use `DeletionPolicy: Retain` and
  `UpdateReplacePolicy: Retain`. Deleting the stack, or changing a parameter that forces
  replacement, never deletes media or images.
- **Media bucket:**
  - Settings: versioned, SSE-S3 encrypted, all four Block Public Access settings on,
    ACLs disabled, non-TLS requests denied.
  - Browser access: staging serves images through pre-signed URLs
    (`AWS_S3_QUERYSTRING_AUTH=True` in `stack.staging.yml`), so no public read policy
    is needed.
- **ECR:** immutable tags, same as the legacy repositories and what Jenkins'
  `push_if_missing` expects. Scan-on-push is on. The lifecycle policy expires untagged
  images after 7 days and keeps the newest `ImageRetentionCount` images.
- **Security group:** only port 80 is reachable from `AllowedHttpCidr`. SSH is limited to
  `AllowedSshCidr`, and a template `Rule` rejects `0.0.0.0/0`. Swarm (2377, 7946, 4789),
  node_exporter (9100) and Loki (3100) accept traffic only from members of the same
  group. PostgreSQL (5432) is not opened at all.
- **Unique names:** every physical name is new, so the stack can't collide with the
  hand-made resources. `Jenkinsfile.provision-infra` checks this before the first create.

## Prerequisites

- AWS CLI v2, with credentials from the Jenkins instance role, AWS CloudShell, or the
  Learner Lab "AWS Details → AWS CLI" session. Never commit credentials.
- Region `us-east-1`.
- Permissions: `cloudformation:*` on the stack, S3 bucket create/configure,
  `ecr:CreateRepository`/`PutLifecyclePolicy`, `ec2:*SecurityGroup*`,
  `ec2:DescribeInstances`/`DescribeVpcs`. `LabRole` grants these.

## Deploy with Jenkins (recommended)

1. Create a Pipeline job (e.g. `Provision-rmit-store-infra`) with script path
   `Jenkinsfile.provision-infra`.
2. **Build with Parameters.** The pipeline:
   1. validates the template;
   2. resolves `VpcId` and the VPC CIDR from the staging host in
      `ansible/inventories/staging.ini`;
   3. checks for name conflicts;
   4. deploys;
   5. asserts `CREATE_COMPLETE` or `UPDATE_COMPLETE`;
   6. verifies every resource.
3. Run the main pipeline. Its **Resolve CloudFormation Outputs** stage fails fast if
   the stack is missing.

Reports are archived as `reports/cloudformation-*.{json,txt}`.

## Deploy with the CLI (e.g. AWS CloudShell)

```bash
export AWS_REGION=us-east-1
STACK=meowgang-a2-infra
TEMPLATE=infrastructure/cloudformation/main.yaml

# 1. Validate
aws cloudformation validate-template --region "$AWS_REGION" --template-body "file://$TEMPLATE"

# 2. Resolve network parameters from the staging host (private IP from staging.ini)
VPC_ID=$(aws ec2 describe-instances --region "$AWS_REGION" \
  --filters "Name=private-ip-address,Values=<staging-private-ip>" \
  --query 'Reservations[0].Instances[0].VpcId' --output text)
VPC_CIDR=$(aws ec2 describe-vpcs --region "$AWS_REGION" --vpc-ids "$VPC_ID" \
  --query 'Vpcs[0].CidrBlock' --output text)

# 3. Deploy (creates the stack, or updates it if it already exists)
aws cloudformation deploy --region "$AWS_REGION" \
  --template-file "$TEMPLATE" --stack-name "$STACK" \
  --parameter-overrides "VpcId=$VPC_ID" "AllowedSshCidr=$VPC_CIDR" \
  --no-fail-on-empty-changeset

# 4. Status, outputs, resources
aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$STACK" \
  --query 'Stacks[0].[StackName,StackStatus]' --output table
aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$STACK" \
  --query 'Stacks[0].Outputs' --output table
aws cloudformation describe-stack-resources --region "$AWS_REGION" --stack-name "$STACK" \
  --query 'StackResources[].[LogicalResourceId,ResourceType,ResourceStatus]' --output table
```

`parameters.example.json` lists every parameter in the `create-stack` format, for the
console or `aws cloudformation create-stack --parameters file://...`.

## Update and repeatability

- **Safe in-place update:** re-run the Jenkins job with `IMAGE_RETENTION_COUNT=40`, or
  add `ImageRetentionCount=40` to the CLI overrides. This changes only the ECR
  lifecycle policies and ends in `UPDATE_COMPLETE`. Run it again with `50` to restore.
- **Repeatability:** re-run with no change. `deploy` prints
  `No changes to deploy. Stack meowgang-a2-infra is up to date` and the status is
  unchanged.
- **Drift check:**
  ```bash
  ID=$(aws cloudformation detect-stack-drift --stack-name meowgang-a2-infra --query StackDriftDetectionId --output text)
  aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id "$ID"
  ```

## Delete (read first)

`aws cloudformation delete-stack --stack-name meowgang-a2-infra` removes the stack
record and the security group. Because of `Retain`, **the media bucket and both ECR
repositories stay in the account**. Remove them by hand only after confirming nothing
references them.

Don't delete the stack while the main pipeline depends on it; its **Resolve
CloudFormation Outputs** stage fails immediately.

## Migrating production media later (not performed)

1. Add a production bucket to the template and deploy.
2. `aws s3 sync s3://meowgang-media-staging-01/media/ s3://<new-bucket>/media/`
3. Point `stack.prod.yml` at the new bucket (from outputs), and set pre-signed URLs or
   a read strategy.
4. Redeploy through Jenkins and verify `/readyz` and product images.

## Limitations

- EC2 hosts, their attached security groups, the legacy bucket and IAM stay outside
  CloudFormation (see *Why the rest is not migrated*).
- `SwarmNodeSecurityGroup` codifies the documented `sg-prod` rules but isn't attached to
  running hosts. Rules that reference the hand-made `sg-grafana`/`sg-staging` groups are
  not included.
- The Compose fallback playbooks (`deploy-staging.yml`, `deploy-prod.yml`) now need
  `-e backend_repository=... -e frontend_repository=...`. `compose.staging.yml` still
  uses the legacy bucket.
