# RMIT DevOps Group Project

This repository keeps the original RMIT Store application and the current DevOps group project together so a new teammate can compare the starting point with the system the team has developed.

## Directory guide

### `COSC2767-RMIT-Store-Django-Vue/`

This is the **initial web application** supplied as the project's starting point. It contains the original Django backend and Vue frontend before the team's Assignment 2 DevOps work.

Use this directory when you need to:

- understand the original application;
- compare the starting code with the team's changes; or
- review the original application documentation and expected behaviour.

### `2026b-cosc2767-a2-sg-devops-meow-gang/`

This is the **current web application and DevOps project** that the team has been working on. It contains the team's testing, Docker, Jenkins, Ansible, AWS/S3, staging and deployment work, together with project documentation and evidence.

Use this directory for current development, testing, deployment, report evidence and the final Assignment 2 deliverables.

## AWS Learner's Lab
- https://awsacademy.instructure.com/login/canvas
- email: projectcookit@gmail.com
- password: @Meowgang26
- private key to ssh to EC2 servers: meowgang-store-staging-key.pem

## Getting started

1. Read this file to identify the correct directory.
2. For the original application, open `COSC2767-RMIT-Store-Django-Vue/README.md`.
3. For the current team project, open `2026b-cosc2767-a2-sg-devops-meow-gang/README.md` and `2026b-cosc2767-a2-sg-devops-meow-gang/APPLICATION_README.md`.
4. Create local environment files from the supplied `.env.example` files. Actual `.env` files and credentials are not stored in this repository.
5. Read A2_TODO_2_COMPLETE.md in 026b-cosc2767-a2-sg-devops-meow-gang/
6. Install dependencies from the relevant Python requirements and npm lock files rather than committing `.venv` or `node_modules` directories.

## Repository note

The two directories are source snapshots within one repository. Their former nested `.git` directories and private credentials are intentionally not included.
