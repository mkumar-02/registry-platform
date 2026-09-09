#!/usr/bin/env python3
"""Provision Individual / intake / CR fixtures for Playwright UI tests.

Writes fixtures/provisioned.json and prints the same JSON to stdout.
Progress logs go to stderr so they never pollute the fixture file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HELPERS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HELPERS_ROOT))

from helpers.config import Config  # noqa: E402
from helpers.http import StaffClient  # noqa: E402
from helpers.provision import (  # noqa: E402
    create_and_finalize_intake,
    create_middle_name_cr,
    provision_individual,
)

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "provisioned.json"


def main() -> int:
    cfg = Config.from_env()
    cfg.require_api()
    cfg.require_household()

    with StaffClient.login(cfg) as staff:
        print("-> provision approved individual for register browse", file=sys.stderr)
        record = provision_individual(staff, cfg, step=lambda m: print(f"  {m}", file=sys.stderr))

        print("-> provision finalized (pending) intake for intake queue", file=sys.stderr)
        pending_intake = create_and_finalize_intake(staff, cfg, step=lambda m: print(f"  {m}", file=sys.stderr))

        print("-> provision pending change request", file=sys.stderr)
        cr = create_middle_name_cr(
            staff,
            cfg,
            subject_internal_record_id=record.internal_record_id,
            first_name=record.first_name,
            step=lambda m: print(f"  {m}", file=sys.stderr),
        )

    fixture = {
        "register_mnemonic": "Individual",
        "locale": "en",
        "individual": {
            "internal_record_id": record.internal_record_id,
            "first_name": record.first_name,
            "middle_name": record.middle_name,
            "last_name": record.last_name,
            "submission_id": record.submission_id,
        },
        "pending_intake": {
            "submission_id": pending_intake.submission_id,
            "first_name": pending_intake.first_name,
            "middle_name": pending_intake.middle_name,
            "last_name": pending_intake.last_name,
        },
        "pending_cr": {
            "change_request_id": cr.change_request_id,
            "first_name": cr.first_name,
            "new_middle_name": cr.new_value,
            "section_id": cr.section_id,
        },
    }
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(fixture, indent=2) + "\n"
    FIXTURE_PATH.write_text(payload, encoding="utf-8")
    print(payload, end="")
    print(f"-> wrote {FIXTURE_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
