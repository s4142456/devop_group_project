/*
RMIT University Vietnam
Course: COSC2767/COSC2805 Systems Deployment and Operations
Semester: 2026B
Assessment: Assignment 2
Author: Nyan Win Naing
ID: s4115096
Created date: 03/09/2026
Last modified: 05/09/2026
Acknowledgement: Jenkins documentation, Docker documentation,
pytest documentation, COSC2767 Week 5 Jenkins lab,
and team project documentation.
*/

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        timeout(time: 30, unit: 'MINUTES')
    }

    parameters {
        booleanParam(
            name: 'DEMO_INTENTIONAL_FAILURE',
            defaultValue: false,
            description: 'Enable only to prove that Jenkins blocks a failing release.'
        )
        booleanParam(
            name: 'DEMO_STAGING_HEALTH_FAILURE',
            defaultValue: false,
            description: 'Enable to simulate a deploy that passes CI but fails the staging health check (Django rejects the probe because ALLOWED_HOSTS is broken). Prod deploy stages are then skipped.'
        )
    }

    triggers {
        githubPush()
    }

    environment {
        AWS_REGION = 'us-east-1'
        ANSIBLE_NOCOLOR = '1'
        BACKEND_IMAGE_NAME = 'meowgang/rmit-store-backend'
        FRONTEND_IMAGE_NAME = 'meowgang/rmit-store-frontend'
        // ALLOWED_HOSTS + CLIENT_URL are now derived by the deploy playbooks
        // from ansible/inventories/{staging,prod}.ini (ansible_host +
        // public_ip). Update those files when EC2 IPs change.

        // Declared params are only populated in the build's shell environment
        // when the build is started via "Build with Parameters". A run
        // started any other way (e.g. the githubPush() trigger below) never
        // sets it at all, so `${DEMO_STAGING_HEALTH_FAILURE}` under
        // `set -u` in the Deploy to Staging stage fails with "unbound
        // variable" before staging is ever touched. Binding it here from
        // params guarantees it is always a defined "true"/"false" string,
        // regardless of how the build started, with no change to the
        // demo behaviour itself.
        DEMO_STAGING_HEALTH_FAILURE = "${params.DEMO_STAGING_HEALTH_FAILURE}"
    }

    stages {
        stage('Checkout') {
            steps {
                // Remove files left by older builds before checking out the commit.
                deleteDir()
                checkout scm

                script {
                    env.BUILD_COMMIT = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    env.SHORT_COMMIT = sh(
                        script: 'git rev-parse --short=8 HEAD',
                        returnStdout: true
                    ).trim()

                    env.APP_VERSION =
                        "jenkins-${env.BUILD_NUMBER}-${env.SHORT_COMMIT}"
                }

                echo "Building commit: ${env.BUILD_COMMIT}"

                echo "Application version: ${env.APP_VERSION}"
            }
        }

        stage('Validate Repository') {
            steps {
                sh '''
                    set -eu

                    test -f APPLICATION_README.md
                    test -f A2_MASTER_TODO.md
                    test -f server/requirements.txt
                    test -f server/requirements-dev.txt
                    test -f server/pytest.ini
                    test -f server/manage.py
                    test -d server/tests/unit
                    test -d server/tests/integration
                    test -f server/tests/unit/test_payment.py
                    test -f server/tests/unit/test_pricing.py
                    test -f server/tests/integration/test_orders_api.py

                    test -f server/tests/failure/test_pipeline_failure.py

                    test -f client/package.json
                    test -f client/package-lock.json
                    test -f client/vite.config.js

                    test -f client/playwright.config.js
                    test -f client/tests/e2e/storefront.spec.js
                    test -f compose.ci.yml

                    test -f ansible/ansible.cfg
                    test -f ansible/inventories/staging.ini
                    test -f ansible/inventories/prod.ini
                    test -f ansible/setup-hosts.yml

                    echo "Required project and test files are present."
                '''
            }
        }

        stage('Show Project Information') {
            steps {
                sh '''
                    set -eu

                    echo "Git commit:"
                    git rev-parse HEAD

                    echo "Docker version:"
                    docker --version

                    echo "Frontend project:"
                    if command -v node >/dev/null 2>&1; then
                        node -e "const p = require('./client/package.json'); console.log(p.name, p.version)"
                    else
                        echo "Node.js is not installed on the Jenkins host."
                    fi
                '''
            }
        }

        stage('Backend Unit and Integration Tests') {
            steps {
                sh '''
                    set -eu

                    mkdir -p reports

                    docker run --rm \
                        --user "$(id -u):$(id -g)" \
                        --env HOME=/tmp \
                        --volume "$WORKSPACE:/workspace" \
                        --workdir /workspace \
                        python:3.11-slim \
                        sh -c '
                            set -eu

                            python -m venv /tmp/venv

                            /tmp/venv/bin/python -m pip install \
                                --disable-pip-version-check \
                                --no-cache-dir \
                                -r server/requirements-dev.txt

                           /tmp/venv/bin/python -m pytest \
                            server/tests/unit \
                            server/tests/integration
                        '
                '''
            }
            post {
                always {
                    junit(
                        allowEmptyResults: true,
                        testResults: 'reports/junit.xml'
                    )

                    archiveArtifacts(
                        allowEmptyArchive: true,
                        artifacts: 'reports/coverage.xml, reports/htmlcov/**',
                        fingerprint: true
                    )
                }
            }
        }

                stage('Controlled Failure Gate') {
            when {
                expression {
                    return params.DEMO_INTENTIONAL_FAILURE
                }
            }

            steps {
                echo 'The controlled CI failure demonstration is enabled.'

                sh '''
                    set -eu

                    mkdir -p reports

                    docker run --rm \
                        --user "$(id -u):$(id -g)" \
                        --env HOME=/tmp \
                        --env DEMO_INTENTIONAL_FAILURE=1 \
                        --volume "$WORKSPACE:/workspace" \
                        --workdir /workspace \
                        python:3.11-slim \
                        sh -c '
                            set -eu

                            python -m venv /tmp/venv

                            /tmp/venv/bin/python -m pip install \
                                --disable-pip-version-check \
                                --no-cache-dir \
                                -r server/requirements-dev.txt

                            DEMO_INTENTIONAL_FAILURE=1 \
                                /tmp/venv/bin/python -m pytest \
                                server/tests/failure/test_pipeline_failure.py \
                                --junitxml=reports/controlled-failure-junit.xml
                        '
                '''
            }

            post {
                always {
                    junit(
                        allowEmptyResults: true,
                        testResults: 'reports/controlled-failure-junit.xml'
                    )

                    archiveArtifacts(
                        allowEmptyArchive: true,
                        artifacts: 'reports/controlled-failure-junit.xml',
                        fingerprint: true
                    )
                }
            }
        }

        stage('Frontend Production Build') {
            steps {
                sh '''
                    set -eu

                    docker run --rm \
                        --user "$(id -u):$(id -g)" \
                        --env HOME=/tmp \
                        --volume "$WORKSPACE/client:/app" \
                        --workdir /app \
                        node:22-alpine \
                        sh -c '
                            set -eu

                            npm ci \
                                --cache /tmp/npm-cache \
                                --no-audit \
                                --no-fund

                            npm run build
                        '

                    test -f client/dist/index.html
                    test -d client/dist/assets
                    test -n "$(find client/dist/assets -type f -print -quit)"

                    echo "Frontend production bundle created successfully."
                    du -sh client/dist
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    set -eu

                    BACKEND_COMMIT_IMAGE="${BACKEND_IMAGE_NAME}:${BUILD_COMMIT}"
                    BACKEND_BUILD_IMAGE="${BACKEND_IMAGE_NAME}:build-${BUILD_NUMBER}"
                    FRONTEND_COMMIT_IMAGE="${FRONTEND_IMAGE_NAME}:${BUILD_COMMIT}"
                    FRONTEND_BUILD_IMAGE="${FRONTEND_IMAGE_NAME}:build-${BUILD_NUMBER}"

                    echo "Building backend images:"
                    echo "  ${BACKEND_COMMIT_IMAGE}"
                    echo "  ${BACKEND_BUILD_IMAGE}"

                    docker build \
                        --label "org.opencontainers.image.revision=${BUILD_COMMIT}" \
                        --label "org.opencontainers.image.version=${APP_VERSION}" \
                        --tag "${BACKEND_COMMIT_IMAGE}" \
                        --tag "${BACKEND_BUILD_IMAGE}" \
                        ./server

                    echo "Building frontend images:"
                    echo "  ${FRONTEND_COMMIT_IMAGE}"
                    echo "  ${FRONTEND_BUILD_IMAGE}"

                    docker build \
                        --label "org.opencontainers.image.revision=${BUILD_COMMIT}" \
                        --label "org.opencontainers.image.version=${APP_VERSION}" \
                        --tag "${FRONTEND_COMMIT_IMAGE}" \
                        --tag "${FRONTEND_BUILD_IMAGE}" \
                        ./client

                    docker image inspect "${BACKEND_COMMIT_IMAGE}" >/dev/null
                    docker image inspect "${BACKEND_BUILD_IMAGE}" >/dev/null
                    docker image inspect "${FRONTEND_COMMIT_IMAGE}" >/dev/null
                    docker image inspect "${FRONTEND_BUILD_IMAGE}" >/dev/null

                    BACKEND_REVISION="$(docker image inspect \
                        "${BACKEND_COMMIT_IMAGE}" \
                        --format='{{index .Config.Labels "org.opencontainers.image.revision"}}')"

                    FRONTEND_REVISION="$(docker image inspect \
                        "${FRONTEND_COMMIT_IMAGE}" \
                        --format='{{index .Config.Labels "org.opencontainers.image.revision"}}')"

                    BACKEND_VERSION="$(docker image inspect \
                        "${BACKEND_COMMIT_IMAGE}" \
                        --format='{{index .Config.Labels "org.opencontainers.image.version"}}')"

                    FRONTEND_VERSION="$(docker image inspect \
                        "${FRONTEND_COMMIT_IMAGE}" \
                        --format='{{index .Config.Labels "org.opencontainers.image.version"}}')"

                    test "${BACKEND_REVISION}" = "${BUILD_COMMIT}"
                    test "${FRONTEND_REVISION}" = "${BUILD_COMMIT}"
                    test "${BACKEND_VERSION}" = "${APP_VERSION}"
                    test "${FRONTEND_VERSION}" = "${APP_VERSION}"

                    mkdir -p reports

                    {
                        echo "Git commit: ${BUILD_COMMIT}"
                        echo "Jenkins build: ${BUILD_NUMBER}"
                        echo "Application version: ${APP_VERSION}"
                        echo "Backend commit image: ${BACKEND_COMMIT_IMAGE}"
                        echo "Backend build image: ${BACKEND_BUILD_IMAGE}"
                        echo "Backend revision label: ${BACKEND_REVISION}"
                        echo "Backend version label: ${BACKEND_VERSION}"
                        echo "Frontend commit image: ${FRONTEND_COMMIT_IMAGE}"
                        echo "Frontend build image: ${FRONTEND_BUILD_IMAGE}"
                        echo "Frontend revision label: ${FRONTEND_REVISION}"
                        echo "Frontend version label: ${FRONTEND_VERSION}"

                        docker image inspect \
                            "${BACKEND_COMMIT_IMAGE}" \
                            --format='Backend image ID: {{.Id}}'

                        docker image inspect \
                            "${FRONTEND_COMMIT_IMAGE}" \
                            --format='Frontend image ID: {{.Id}}'
                    } | tee reports/docker-images.txt

                    echo "Both Docker images were built and verified successfully."
                '''
            }

            post {
                success {
                    archiveArtifacts(
                        artifacts: 'reports/docker-images.txt',
                        fingerprint: true
                    )
                }
            }
        }

                stage('Frontend Web UI Tests') {
                    steps {
                        sh '''
                            set -eu

                            export BACKEND_IMAGE="${BACKEND_IMAGE_NAME}:${BUILD_COMMIT}"
                            export FRONTEND_IMAGE="${FRONTEND_IMAGE_NAME}:${BUILD_COMMIT}"
                            export COMPOSE_PROJECT_NAME="rmit-store-e2e-${BUILD_NUMBER}"

                            cleanup_e2e() {
                                echo "Removing temporary Web UI test environment."

                                docker compose \
                                    --file compose.ci.yml \
                                    down \
                                    --volumes \
                                    --remove-orphans || true
                            }

                            trap cleanup_e2e EXIT INT TERM

                            cleanup_e2e

                            rm -rf \
                                client/reports \
                                client/test-results

                            mkdir -p client/reports

                            echo "Starting isolated Web UI test environment."

                            docker compose \
                                --file compose.ci.yml \
                                up \
                                --detach

                            echo "Waiting for the temporary storefront."

                            STOREFRONT_READY=0

                            for ATTEMPT in $(seq 1 60)
                            do
                                if curl \
                                    --fail \
                                    --silent \
                                    --show-error \
                                    http://127.0.0.1:5173/shop \
                                    >/dev/null
                                then
                                    STOREFRONT_READY=1
                                    break
                                fi

                                echo "Storefront is not ready yet: attempt ${ATTEMPT}/60"
                                sleep 2
                            done

                            if [ "${STOREFRONT_READY}" -ne 1 ]; then
                                echo "The temporary storefront did not become ready."

                                docker compose \
                                    --file compose.ci.yml \
                                    ps

                                docker compose \
                                    --file compose.ci.yml \
                                    logs \
                                    --no-color

                                exit 1
                            fi

                            echo "Temporary storefront is ready."
                            echo "Running Playwright Chromium tests."

                            docker run \
                                --rm \
                                --network host \
                                --ipc host \
                                --user "$(id -u):$(id -g)" \
                                --env HOME=/tmp \
                                --volume "$WORKSPACE/client:/work" \
                                --workdir /work \
                                mcr.microsoft.com/playwright:v1.62.1-noble \
                                sh -c '
                                    set -eu

                                    npm ci \
                                        --cache /tmp/npm-cache \
                                        --no-audit \
                                        --no-fund

                                    npm run test:e2e
                                '

                            echo "Playwright Web UI tests passed."
                        '''
                    }

            post {
                always {
                    junit(
                        allowEmptyResults: true,
                        testResults: 'client/reports/playwright-junit.xml'
                    )

                    archiveArtifacts(
                        allowEmptyArchive: true,
                        artifacts: 'client/reports/playwright-report/**, client/test-results/**',
                        fingerprint: true
                    )
                }
            }
        }

        stage('Publish Images to ECR') {
            steps {
                sh '''
                    set -eu

                    AWS_ACCOUNT_ID="$(aws sts get-caller-identity \
                        --query Account \
                        --output text)"

                    test -n "${AWS_ACCOUNT_ID}"
                    test "${AWS_ACCOUNT_ID}" != "None"

                    ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

                    BACKEND_LOCAL_COMMIT="${BACKEND_IMAGE_NAME}:${BUILD_COMMIT}"
                    BACKEND_LOCAL_BUILD="${BACKEND_IMAGE_NAME}:build-${BUILD_NUMBER}"
                    FRONTEND_LOCAL_COMMIT="${FRONTEND_IMAGE_NAME}:${BUILD_COMMIT}"
                    FRONTEND_LOCAL_BUILD="${FRONTEND_IMAGE_NAME}:build-${BUILD_NUMBER}"

                    BACKEND_ECR_COMMIT="${ECR_REGISTRY}/${BACKEND_IMAGE_NAME}:${BUILD_COMMIT}"
                    BACKEND_ECR_BUILD="${ECR_REGISTRY}/${BACKEND_IMAGE_NAME}:build-${BUILD_NUMBER}"
                    FRONTEND_ECR_COMMIT="${ECR_REGISTRY}/${FRONTEND_IMAGE_NAME}:${BUILD_COMMIT}"
                    FRONTEND_ECR_BUILD="${ECR_REGISTRY}/${FRONTEND_IMAGE_NAME}:build-${BUILD_NUMBER}"

                    echo "Authenticating Jenkins to ${ECR_REGISTRY}"

                    aws ecr get-login-password \
                        --region "${AWS_REGION}" |
                        docker login \
                            --username AWS \
                            --password-stdin \
                            "${ECR_REGISTRY}"

                    trap 'docker logout "${ECR_REGISTRY}" >/dev/null 2>&1 || true' EXIT

                    docker tag "${BACKEND_LOCAL_COMMIT}" "${BACKEND_ECR_COMMIT}"
                    docker tag "${BACKEND_LOCAL_BUILD}" "${BACKEND_ECR_BUILD}"
                    docker tag "${FRONTEND_LOCAL_COMMIT}" "${FRONTEND_ECR_COMMIT}"
                    docker tag "${FRONTEND_LOCAL_BUILD}" "${FRONTEND_ECR_BUILD}"

                    push_if_missing() {
                        repository_name="$1"
                        image_tag="$2"
                        image_uri="$3"

                        if aws ecr describe-images \
                            --region "${AWS_REGION}" \
                            --repository-name "${repository_name}" \
                            --image-ids "imageTag=${image_tag}" \
                            >/dev/null 2>&1
                        then
                            echo "ECR image already exists; immutable tag retained:"
                            echo "  ${image_uri}"
                        else
                            echo "Publishing immutable image:"
                            echo "  ${image_uri}"
                            docker push "${image_uri}"
                        fi
                    }

                    push_if_missing \
                        "${BACKEND_IMAGE_NAME}" \
                        "${BUILD_COMMIT}" \
                        "${BACKEND_ECR_COMMIT}"

                    push_if_missing \
                        "${BACKEND_IMAGE_NAME}" \
                        "build-${BUILD_NUMBER}" \
                        "${BACKEND_ECR_BUILD}"

                    push_if_missing \
                        "${FRONTEND_IMAGE_NAME}" \
                        "${BUILD_COMMIT}" \
                        "${FRONTEND_ECR_COMMIT}"

                    push_if_missing \
                        "${FRONTEND_IMAGE_NAME}" \
                        "build-${BUILD_NUMBER}" \
                        "${FRONTEND_ECR_BUILD}"

                    BACKEND_DIGEST="$(aws ecr describe-images \
                        --region "${AWS_REGION}" \
                        --repository-name "${BACKEND_IMAGE_NAME}" \
                        --image-ids "imageTag=${BUILD_COMMIT}" \
                        --query 'imageDetails[0].imageDigest' \
                        --output text)"

                    FRONTEND_DIGEST="$(aws ecr describe-images \
                        --region "${AWS_REGION}" \
                        --repository-name "${FRONTEND_IMAGE_NAME}" \
                        --image-ids "imageTag=${BUILD_COMMIT}" \
                        --query 'imageDetails[0].imageDigest' \
                        --output text)"

                    test -n "${BACKEND_DIGEST}"
                    test "${BACKEND_DIGEST}" != "None"
                    test -n "${FRONTEND_DIGEST}"
                    test "${FRONTEND_DIGEST}" != "None"

                    mkdir -p reports

                    {
                        echo "Git commit: ${BUILD_COMMIT}"
                        echo "Jenkins build: ${BUILD_NUMBER}"
                        echo "Application version: ${APP_VERSION}"
                        echo "AWS region: ${AWS_REGION}"
                        echo "ECR registry: ${ECR_REGISTRY}"
                        echo "Backend image: ${BACKEND_ECR_COMMIT}"
                        echo "Backend build alias: ${BACKEND_ECR_BUILD}"
                        echo "Backend digest: ${BACKEND_DIGEST}"
                        echo "Frontend image: ${FRONTEND_ECR_COMMIT}"
                        echo "Frontend build alias: ${FRONTEND_ECR_BUILD}"
                        echo "Frontend digest: ${FRONTEND_DIGEST}"
                    } | tee reports/ecr-images.txt

                    echo "Both tested images were published and verified in ECR."
                '''
            }

            post {
                success {
                    archiveArtifacts(
                        artifacts: 'reports/ecr-images.txt',
                        fingerprint: true
                    )
                }
            }
        }

        stage('Validate Staging Connectivity') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'staging-ec2-ssh-key',
                        keyFileVariable: 'STAGING_SSH_KEY',
                        usernameVariable: 'STAGING_SSH_USER'
                    )
                ]) {
                    sh '''
                        set -eu
                        export ANSIBLE_CONFIG="${WORKSPACE}/ansible/ansible.cfg"

                        mkdir -p reports
                        REPORT_FILE="reports/ansible-staging-connectivity.txt"

                        echo "Pinging [staging] from ansible/inventories/staging.ini." | tee "${REPORT_FILE}"

                        set +e
                        ansible staging \
                            --inventory ansible/inventories/staging.ini \
                            --module-name ping \
                            --user "${STAGING_SSH_USER}" \
                            --private-key "${STAGING_SSH_KEY}" \
                            >> "${REPORT_FILE}" 2>&1
                        ANSIBLE_STATUS="$?"
                        set -e

                        cat "${REPORT_FILE}"

                        if [ "${ANSIBLE_STATUS}" -ne 0 ]; then
                            echo "Staging connectivity failed with exit code ${ANSIBLE_STATUS}."
                            exit "${ANSIBLE_STATUS}"
                        fi

                        echo "Staging connectivity validated successfully." | tee -a "${REPORT_FILE}"
                    '''
                }
            }

            post {
                always {
                    archiveArtifacts(
                        allowEmptyArchive: true,
                        artifacts: 'reports/ansible-staging-connectivity.txt',
                        fingerprint: true
                    )
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'staging-ec2-ssh-key',
                        keyFileVariable: 'STAGING_SSH_KEY',
                        usernameVariable: 'STAGING_SSH_USER'
                    ),
                    string(
                        credentialsId: 'staging-postgres-password',
                        variable: 'STAGING_POSTGRES_PASSWORD'
                    ),
                    string(
                        credentialsId: 'staging-django-secret-key',
                        variable: 'STAGING_SECRET_KEY'
                    )
                ]) {
                    sh '''
                        set -euo pipefail

                        export ANSIBLE_CONFIG="${WORKSPACE}/ansible/ansible.cfg"

                        AWS_ACCOUNT_ID="$(aws sts get-caller-identity \
                            --query Account \
                            --output text)"

                        test -n "${AWS_ACCOUNT_ID}"
                        test "${AWS_ACCOUNT_ID}" != "None"

                        # Demo hook: when DEMO_STAGING_HEALTH_FAILURE is true,
                        # override allowed_hosts with a value Django will reject
                        # so the container health probe fails. Proves that a bad
                        # staging deploy prevents production stages from running.
                        # Extra-vars have highest precedence in Ansible, so this
                        # overrides the playbook's inventory-derived default.
                        DEMO_OVERRIDE=""
                        if [ "${DEMO_STAGING_HEALTH_FAILURE}" = "true" ]; then
                            echo "DEMO_STAGING_HEALTH_FAILURE=true: forcing bad ALLOWED_HOSTS."
                            DEMO_OVERRIDE="-e allowed_hosts=badhost.example.com"
                        fi

                        EXTRA_VARS_FILE="$(mktemp)"
                        trap 'rm -f "${EXTRA_VARS_FILE}"' EXIT
                        chmod 600 "${EXTRA_VARS_FILE}"

                        cat > "${EXTRA_VARS_FILE}" <<EOF
{
  "aws_region": "${AWS_REGION}",
  "aws_account_id": "${AWS_ACCOUNT_ID}",
  "build_commit": "${BUILD_COMMIT}",
  "app_version": "${APP_VERSION}",
  "postgres_password": "${STAGING_POSTGRES_PASSWORD}",
  "secret_key": "${STAGING_SECRET_KEY}"
}
EOF

                        mkdir -p reports
                        REPORT_FILE="reports/ansible-deploy-staging.txt"

                        ansible-playbook \
                            --inventory ansible/inventories/staging.ini \
                            --limit staging \
                            --user "${STAGING_SSH_USER}" \
                            --private-key "${STAGING_SSH_KEY}" \
                            --extra-vars "@${EXTRA_VARS_FILE}" \
                            ${DEMO_OVERRIDE} \
                            ansible/deploy-staging-swarm.yml \
                            | tee "${REPORT_FILE}"
                    '''
                }
            }

            post {
                always {
                    archiveArtifacts(
                        allowEmptyArchive: true,
                        artifacts: 'reports/ansible-deploy-staging.txt',
                        fingerprint: true
                    )
                }
            }
        }

        stage('Validate Production Connectivity') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'staging-ec2-ssh-key',
                        keyFileVariable: 'PROD_SSH_KEY',
                        usernameVariable: 'PROD_SSH_USER'
                    )
                ]) {
                    sh '''
                        set -eu
                        export ANSIBLE_CONFIG="${WORKSPACE}/ansible/ansible.cfg"

                        mkdir -p reports
                        REPORT_FILE="reports/ansible-prod-connectivity.txt"

                        echo "Pinging [swarm_manager] from ansible/inventories/prod.ini." | tee "${REPORT_FILE}"

                        set +e
                        ansible swarm_manager \
                            --inventory ansible/inventories/prod.ini \
                            --module-name ping \
                            --user "${PROD_SSH_USER}" \
                            --private-key "${PROD_SSH_KEY}" \
                            >> "${REPORT_FILE}" 2>&1
                        ANSIBLE_STATUS="$?"
                        set -e

                        cat "${REPORT_FILE}"

                        if [ "${ANSIBLE_STATUS}" -ne 0 ]; then
                            echo "Production connectivity failed with exit code ${ANSIBLE_STATUS}."
                            exit "${ANSIBLE_STATUS}"
                        fi

                        echo "Production connectivity validated successfully." | tee -a "${REPORT_FILE}"
                    '''
                }
            }

            post {
                always {
                    archiveArtifacts(
                        allowEmptyArchive: true,
                        artifacts: 'reports/ansible-prod-connectivity.txt',
                        fingerprint: true
                    )
                }
            }
        }

        stage('Deploy to Production') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'staging-ec2-ssh-key',
                        keyFileVariable: 'PROD_SSH_KEY',
                        usernameVariable: 'PROD_SSH_USER'
                    ),
                    string(
                        credentialsId: 'staging-postgres-password',
                        variable: 'PROD_POSTGRES_PASSWORD'
                    ),
                    string(
                        credentialsId: 'staging-django-secret-key',
                        variable: 'PROD_SECRET_KEY'
                    )
                ]) {
                    sh '''
                        set -euo pipefail

                        export ANSIBLE_CONFIG="${WORKSPACE}/ansible/ansible.cfg"

                        AWS_ACCOUNT_ID="$(aws sts get-caller-identity \
                            --query Account \
                            --output text)"

                        test -n "${AWS_ACCOUNT_ID}"
                        test "${AWS_ACCOUNT_ID}" != "None"

                        EXTRA_VARS_FILE="$(mktemp)"
                        trap 'rm -f "${EXTRA_VARS_FILE}"' EXIT
                        chmod 600 "${EXTRA_VARS_FILE}"

                        cat > "${EXTRA_VARS_FILE}" <<EOF
{
  "aws_region": "${AWS_REGION}",
  "aws_account_id": "${AWS_ACCOUNT_ID}",
  "build_commit": "${BUILD_COMMIT}",
  "app_version": "${APP_VERSION}",
  "postgres_password": "${PROD_POSTGRES_PASSWORD}",
  "secret_key": "${PROD_SECRET_KEY}"
}
EOF

                        mkdir -p reports
                        REPORT_FILE="reports/ansible-deploy-prod.txt"

                        ansible-playbook \
                            --inventory ansible/inventories/prod.ini \
                            --limit swarm_manager \
                            --user "${PROD_SSH_USER}" \
                            --private-key "${PROD_SSH_KEY}" \
                            --extra-vars "@${EXTRA_VARS_FILE}" \
                            ansible/deploy-prod-swarm.yml \
                            | tee "${REPORT_FILE}"
                    '''
                }
            }

            post {
                always {
                    archiveArtifacts(
                        allowEmptyArchive: true,
                        artifacts: 'reports/ansible-deploy-prod.txt',
                        fingerprint: true
                    )
                }
            }
        }

    }

    post {
        success {
            echo "CI passed, images were published, staging was deployed, and production was deployed for ${env.SHORT_COMMIT}."
        }

        failure {
            echo 'Pipeline failed. Deployment stages must not run.'
            echo 'Inspect the failed stage, test result and console output.'
            script {
                // TODO before submission: swap credentialsId to
                // 'jenkins-failure-email-recipients' (team distribution list).
                withCredentials([string(credentialsId: 'personal-email-recipients', variable: 'FAILURE_RECIPIENTS')]) {
                    emailext(
                        subject: "[FAILED] ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.SHORT_COMMIT ?: 'unknown'})",
                        body: """\
<p>The RMIT Store pipeline failed.</p>
<ul>
  <li><b>Job:</b> ${env.JOB_NAME}</li>
  <li><b>Build:</b> #${env.BUILD_NUMBER}</li>
  <li><b>Commit:</b> ${env.BUILD_COMMIT ?: 'unknown'}</li>
  <li><b>Result:</b> ${currentBuild.currentResult}</li>
  <li><b>Console:</b> <a href="${env.BUILD_URL}console">open</a></li>
  <li><b>Blue Ocean:</b> <a href="${env.RUN_DISPLAY_URL}">open</a></li>
</ul>
<p>Full console log is attached (compressed).</p>
""",
                        mimeType: 'text/html',
                        to: "${FAILURE_RECIPIENTS}",
                        attachLog: true,
                        compressLog: true
                    )
                }
            }
        }

        fixed {
            script {
                withCredentials([string(credentialsId: 'personal-email-recipients', variable: 'FAILURE_RECIPIENTS')]) {
                    emailext(
                        subject: "[FIXED] ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.SHORT_COMMIT ?: 'unknown'})",
                        body: """\
<p>The pipeline is green again after a previous failure.</p>
<ul>
  <li><b>Build:</b> #${env.BUILD_NUMBER}</li>
  <li><b>Commit:</b> ${env.BUILD_COMMIT ?: 'unknown'}</li>
  <li><b>Console:</b> <a href="${env.BUILD_URL}console">open</a></li>
</ul>
""",
                        mimeType: 'text/html',
                        to: "${FAILURE_RECIPIENTS}"
                    )
                }
            }
        }

        always {
            echo "Jenkins build ${env.BUILD_NUMBER} finished."
        }
    }
}
