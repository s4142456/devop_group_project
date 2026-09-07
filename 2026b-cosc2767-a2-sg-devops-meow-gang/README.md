RMIT University Vietnam
Course: COSC2767 Systems Deployment and Operations
Semester: 2026B
Assessment: Assignment 2
Author: Ngo Hoang Long
ID: s4142456
Created date: 3/9/2026
Last modified: dd/mm/yyyy
Acknowledgement: Official assignment brief; Django, pytest, pytest-django and pytest-cov documentation; OpenAI Codex used for test-setup guidance

# RMIT Store CI/CD Pipeline

## 1. Project and team information
## 2. Architecture overview
## 3. Prerequisites
## 4. Repository structure
## 5. Required environment configuration
## 6. AWS provisioning order
## 7. Ansible inventory and playbook order
## 8. Jenkins installation and configuration
## 9. Required Jenkins credentials
## 10. Triggering a deployment
## 11. Verifying staging and production
## 12. Triggering a rollback
## 13. Running tests locally

### Backend testing

#### Test tooling

The Django backend test suite uses:

- pytest 9.1.1
- pytest-django 4.14.0
- pytest-cov 7.1.0

Test dependencies are separated from runtime dependencies in
`server/requirements-dev.txt`.

#### Install backend test dependencies

From the repository root on Linux or an AWS/Jenkins host:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r server/requirements-dev.txt
```
## 14. Failure recovery
## 15. Cleanup
## 16. Known limitations



---
Private key.pem for all servers to ssh: check .pem file in the team's Google Drive

Server 1: meowgang-store-staging
- Public IPv4 address: 32.193.86.95
- Private IPv4 address: 172.31.34.225
- Public DNS: ec2-32-193-86-95.compute-1.amazonaws.com

