# Member 2 Testing Handoff

RMIT University Vietnam  
Course: COSC2767 Systems Deployment and Operations  
Semester: 2026B  
Assessment: Assignment 2  
Author: Ngo Hoang Long  
ID: s4142456  
Created and last modified: 03/09/2026  
Acknowledgement: pytest, Playwright and Jenkins documentation; OpenAI Codex used for testing-workflow guidance.

## Normal CI commands

Run from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r server/requirements-dev.txt
.venv/bin/python -m pytest server/tests

cd client
npm ci
npx playwright install --with-deps chromium
npm run test:e2e
cd ..

python3 scripts/smoke_test.py --base-url "$STAGING_URL"
```

For local verification with separate Vite and Django development servers:

```bash
python3 scripts/smoke_test.py \
  --frontend-url http://localhost:5173 \
  --api-url http://localhost:8000
```

Publish these machine-readable reports even when a test fails:

```text
reports/junit.xml
reports/coverage.xml
client/reports/playwright-junit.xml
client/reports/playwright-report/
client/test-results/
```

## Controlled failure demonstration

The normal backend suite skips the intentional failure. For one recorded Jenkins
demonstration, run the following command in the test stage. It must return a
non-zero exit status, stop later deployment stages, and trigger the configured
failure notification:

```bash
DEMO_INTENTIONAL_FAILURE=1 .venv/bin/python -m pytest \
  server/tests/failure/test_pipeline_failure.py
```

After capturing evidence, remove the environment variable or disable the
temporary demonstration parameter. Do not commit a permanently failing pipeline.

## Meaningful deployment failure scenario

The smoke test returns a non-zero exit status when the deployment is unavailable
or unhealthy. This safe command uses a deliberately unreachable local port:

```bash
python3 scripts/smoke_test.py --base-url http://127.0.0.1:1 --timeout 1
```

Jenkins must treat the non-zero result as a failed staging gate and must not
promote the images to production.
