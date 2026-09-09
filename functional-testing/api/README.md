# API functional tests

Pytest suite for the staff portal API against the **reference extension**
(Individual + Household registers). Every scenario validates the **API response
and the database** (strict field match).

## Mental model

```
helpers/                 shared by API tests + UI fixture scripts
├── config.py            env + register / section IDs
├── profiles.py          RegisterProfile (Individual / Household contract)
├── auth.py, http.py     OIDC + staff API client
├── payloads/            section payload builders per register
├── flows/               lifecycle steps (intake → register → CR)
│   ├── intake.py
│   ├── register.py
│   └── change_request.py
├── models.py            IntakeResult, ProvisionedRecord, ChangeRequestResult
├── util.py              response_payload, assert_ok, unique names
└── provision.py         thin re-export façade (prefer flows/ in new code)

api/
├── scenarios/           one file per lifecycle step (parametrized × 2 registers)
├── assertions/          response / db / dual (API↔DB) validators
├── profile_params.py    @with_register_profiles
└── conftest.py          cfg, staff, linked_household, household_id_for
```

### Scenario map (10 tests = 5 × 2 profiles)

| File | What it proves |
|------|----------------|
| `test_intake_create.py` | Finalize → draft FINAL / approval PENDING (API + DB) |
| `test_intake_approve.py` | Verify + approve → register row; `match_fields` equal |
| `test_register_read.py` | Summary, subject, tabs, pending CR list |
| `test_cr_create.py` | CR PENDING; subject field **unchanged** |
| `test_cr_approve.py` | CR APPROVED; subject field **applied** on API + DB |

### Register profiles

Defined in `helpers/profiles.py`:

| | Individual | Household |
|---|---|---|
| Identity / search | `first_name` | `household_head_name` |
| CR field | `middle_name` | `household_head_name` |
| Strict match fields | first/middle/last name | head name, headship, address |
| Needs linked HH | yes | no |

Add `@with_register_profiles` (from `profile_params`) so a scenario runs for both.

### Where to change what

- New env / IDs → `helpers/config.py`
- New register variant → `helpers/profiles.py` + `helpers/payloads/<name>.py`
- New HTTP lifecycle step → `helpers/flows/`
- New check → `api/assertions/`
- New scenario → `api/scenarios/` + `@with_register_profiles`

## How to run

Prefer the compose gate (starts stack, seeds Keycloak, runs pytest):

```bash
cd registry-platform
FUNC_SKIP_UI=1 ./functional-testing/docker/run-compose-gate.sh
```

Reuse an already-up stack:

```bash
FUNC_SKIP_STACK=1 FUNC_SKIP_UI=1 FUNC_SKIP_TEARDOWN=1 \
  ./functional-testing/docker/run-compose-gate.sh
```

Manual pytest (stack must be up; `.env` filled):

```bash
cd functional-testing
PYTHONPATH=. pytest -c api/pytest.ini api/scenarios -v
PYTHONPATH=. pytest -c api/pytest.ini api/scenarios -k household -v
PYTHONPATH=. pytest -c api/pytest.ini api/scenarios/test_intake_create.py -v
```
