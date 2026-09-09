"""Shared dual-validation helpers for API scenarios."""

from __future__ import annotations

from typing import Any

from assertions import db as db_assert
from assertions.response import assert_values_equal
from helpers.profiles import RegisterProfile
from helpers.provision import get_subject_record
from helpers.http import StaffClient


def fetch_subject_db(dsn: str, profile: RegisterProfile, internal_record_id: str) -> dict[str, Any]:
    if profile.key == "household":
        row = db_assert.fetch_household_by_id(dsn, internal_record_id)
    else:
        row = db_assert.fetch_individual_by_id(dsn, internal_record_id)
    assert row, f"{profile.key} {internal_record_id} missing in DB"
    return row


def fetch_subject_db_by_identity(
    dsn: str, profile: RegisterProfile, identity: str
) -> dict[str, Any]:
    if profile.key == "household":
        row = db_assert.fetch_household_by_head_name(dsn, identity)
    else:
        row = db_assert.fetch_individual_by_first_name(dsn, identity)
    assert row, f"{profile.key} identity={identity!r} missing in DB"
    return row


def assert_api_db_subject_match(
    staff: StaffClient,
    cfg_dsn: str,
    profile: RegisterProfile,
    internal_record_id: str,
    *,
    expected_fields: dict[str, Any] | None = None,
    context: str = "",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load subject via API + DB and require profile.match_fields to be equal."""
    api_record = get_subject_record(staff, profile, internal_record_id)
    db_row = fetch_subject_db(cfg_dsn, profile, internal_record_id)
    label = context or f"{profile.key}:{internal_record_id}"

    for field in profile.match_fields:
        api_val = api_record.get(field)
        db_val = db_row.get(field)
        if expected_fields and field in expected_fields:
            assert_values_equal(
                expected_fields[field], api_val, field=f"API.{field}", context=label
            )
            assert_values_equal(
                expected_fields[field], db_val, field=f"DB.{field}", context=label
            )
        assert_values_equal(api_val, db_val, field=field, context=label)

    return api_record, db_row


def assert_intake_api_db(
    dsn: str,
    submission_id: str,
    *,
    form_id: str,
    register_id: str,
    draft_status: str,
    approval_status: str,
    api_payload: dict[str, Any],
    context: str = "",
) -> dict[str, Any]:
    """Strictly match intake submission API payload against DB row."""
    row = db_assert.fetch_intake_submission(dsn, submission_id)
    assert row, f"{context}: submission {submission_id} not in DB"

    assert_values_equal(
        api_payload.get("draft_status"),
        row.get("draft_status"),
        field="draft_status",
        context=context,
    )
    assert_values_equal(
        api_payload.get("approval_status"),
        row.get("approval_status"),
        field="approval_status",
        context=context,
    )
    assert str(row.get("form_id")) == form_id, (
        f"{context}: form_id DB={row.get('form_id')!r} expected {form_id!r}"
    )
    assert str(row.get("register_id")) == register_id, (
        f"{context}: register_id DB={row.get('register_id')!r} expected {register_id!r}"
    )
    assert str(row.get("draft_status") or "").upper() == draft_status.upper()
    assert str(row.get("approval_status") or "").upper() == approval_status.upper()
    if draft_status.upper() == "FINAL":
        assert row.get("finalized_at") is not None, f"{context}: finalized_at missing"
    return row
