# UI functional tests (E2E)

Playwright E2E for the staff portal against the **reference extension**
(Individual fixtures today). Journeys mirror the API lifecycle: home →
register → intake → change request.

Data is **API-seeded** via `global-setup` (`scripts/provision_fixture.py` →
`fixtures/provisioned.json`). Specs then drive the browser. Approve steps
prefer a visible UI **Approve** button and fall back to
`helpers/api-bridge.ts` when the control is absent.

For API + DB truth, see [`../api/README.md`](../api/README.md).

## Mental model

```
ui/
├── helpers/           # fixture load, Keycloak auth, API approve bridge
├── pages/             # browser navigation (register / intake / CR)
├── scripts/           # Python provision + approve (uses functional-testing/helpers)
├── fixtures/          # provisioned.json (generated)
├── tests/
│   ├── auth.setup.ts  # storageState login
│   ├── home/
│   ├── register/
│   ├── intake/
│   └── change-request/
├── global-setup.ts
└── playwright.config.ts
```

### Journey map

| Folder | Specs | What it proves in the UI |
|--------|-------|---------------------------|
| `home/` | `home.spec.ts` | Authenticated shell renders |
| `register/` | `register-read*.spec.ts` | Search/open subject; pending CR visible |
| `intake/` | `intake-queue`, `intake-approve` | Find pending intake; approve → APPROVED |
| `change-request/` | `…-queue`, `…-approve` | Find pending CR; approve → field on register |

### Where to change what

- New page navigation → `pages/`
- Fixture shape / locale paths → `helpers/fixture.ts`
- Login / top-bar search → `helpers/auth.ts`
- Approve fallback → `helpers/api-bridge.ts` + `scripts/approve_fixture.py`
- New E2E journey → `tests/<domain>/`
- Later: fill intake in the browser → extend `pages/intake.ts` + new intake spec

## How to run

Prefer the compose gate (builds staff-ui from `ui/staff-ui` Dockerfile):

```bash
cd registry-platform
FUNC_SKIP_API=1 ./functional-testing/docker/run-compose-gate.sh
```

Reuse stack:

```bash
FUNC_SKIP_STACK=1 FUNC_SKIP_API=1 FUNC_SKIP_TEARDOWN=1 \
  ./functional-testing/docker/run-compose-gate.sh
```

Manual (stack up, `.env` set):

```bash
cd functional-testing/ui
npm ci && npx playwright install chromium
npx playwright test
npx playwright test tests/intake
```

Skip re-provision (reuse `fixtures/provisioned.json`):

```bash
FUNC_UI_SKIP_PROVISION=1 npx playwright test
```
