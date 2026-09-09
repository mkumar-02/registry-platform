# registry-platform functional testing (API + UI)

Functional test suite for the registry-platform staff portal against the
**reference extension** (Individual and Household registers).

- **API tests** (pytest): intake create/approve, register browse, change-request
  create/approve — parametrized for **Individual + Household**, with mandatory
  **response + DB** validation. See [`api/README.md`](api/README.md).
- **UI tests** (Playwright E2E): same lifecycle in the browser (API-seeded
  fixtures; Individual today). See [`ui/README.md`](ui/README.md).

Extension-specific API tests (e.g. farmer payloads) live in each extension repo.

## Quick start (Docker Compose gate)

```bash
cd registry-platform
chmod +x functional-testing/docker/run-compose-gate.sh
./functional-testing/docker/run-compose-gate.sh
```

Platform images are built from local Dockerfiles on every gate run.
Commons (Keycloak, IAM, AWE, …) still pull from Docker Hub.

### Subsets

```bash
FUNC_SKIP_UI=1 ./functional-testing/docker/run-compose-gate.sh   # API only
FUNC_SKIP_API=1 ./functional-testing/docker/run-compose-gate.sh  # UI only
FUNC_SKIP_TEARDOWN=1 ./functional-testing/docker/run-compose-gate.sh  # keep stack
FUNC_SKIP_STACK=1 FUNC_SKIP_UI=1 ./functional-testing/docker/run-compose-gate.sh  # reuse stack
```

GitHub Actions: `.github/workflows/functional-gate.yml`.

## Manual run

```bash
# Stack up (or FUNC_SKIP_STACK=1 against a running gate stack)
pip install -r functional-testing/requirements.txt

# API
cd functional-testing
PYTHONPATH=. pytest -c api/pytest.ini api/scenarios -v

# UI
cd functional-testing/ui
npm ci && npx playwright install chromium && npx playwright test
```

## Project structure

```
functional-testing/
├── api/                 # pytest API suite — see api/README.md
│   ├── scenarios/       # lifecycle scenarios × Individual + Household
│   ├── assertions/      # response + DB + dual validators
│   ├── profile_params.py
│   ├── conftest.py
│   └── pytest.ini
├── helpers/             # shared by API tests + UI fixture scripts
│   ├── config.py, profiles.py, auth.py, http.py
│   ├── payloads/        # section builders (individual / household)
│   ├── flows/           # intake, register, change_request
│   ├── models.py, util.py
│   └── provision.py     # façade re-exports for UI scripts
├── docker/              # Compose gate
├── scripts/             # Keycloak seed
├── ui/                  # Playwright UI E2E — see ui/README.md
│   ├── helpers/         # fixture, auth, api-bridge
│   ├── pages/           # register / intake / change-request
│   ├── tests/           # home, register, intake, change-request
│   └── scripts/         # provision / approve fixtures
└── requirements.txt
```
