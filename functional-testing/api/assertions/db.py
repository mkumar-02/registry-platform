"""Postgres assertions for Individual + Household register rows."""

from __future__ import annotations

import time
from typing import Any, Callable, Optional

import pytest

try:
    import psycopg
except ImportError:  # pragma: no cover
    psycopg = None  # type: ignore


def query(dsn: str, sql: str, params: tuple | None = None) -> list[dict[str, Any]]:
    if psycopg is None:
        pytest.skip("psycopg not installed")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if cur.description is None:
                return []
            cols = [c.name for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_intake_submission(dsn: str, submission_id: str) -> Optional[dict[str, Any]]:
    rows = query(
        dsn,
        """
        SELECT submission_id, form_id, register_id,
               draft_status, approval_status, finalized_at, approved_at,
               number_of_verifications_required, number_of_verifications_done
        FROM g2p_intake_form_submissions
        WHERE submission_id = %s
        """,
        (submission_id,),
    )
    return rows[0] if rows else None


def fetch_individual_by_id(dsn: str, internal_record_id: str) -> Optional[dict[str, Any]]:
    rows = query(
        dsn,
        """
        SELECT internal_record_id, first_name, middle_name, last_name,
               gender, birth_date, marital_status, record_status
        FROM g2p_register_individuals
        WHERE internal_record_id = %s
        """,
        (internal_record_id,),
    )
    return rows[0] if rows else None


def fetch_individual_by_first_name(dsn: str, first_name: str) -> Optional[dict[str, Any]]:
    rows = query(
        dsn,
        """
        SELECT internal_record_id, first_name, middle_name, last_name,
               gender, birth_date, marital_status, record_status
        FROM g2p_register_individuals
        WHERE first_name = %s
        ORDER BY created_at DESC NULLS LAST
        LIMIT 1
        """,
        (first_name,),
    )
    return rows[0] if rows else None


def fetch_household_by_id(dsn: str, internal_record_id: str) -> Optional[dict[str, Any]]:
    rows = query(
        dsn,
        """
        SELECT internal_record_id, household_head_name, headship_type,
               size_total, address_line_1, country_code, record_status,
               record_name
        FROM g2p_register_households
        WHERE internal_record_id = %s
        """,
        (internal_record_id,),
    )
    return rows[0] if rows else None


def fetch_household_by_head_name(dsn: str, household_head_name: str) -> Optional[dict[str, Any]]:
    rows = query(
        dsn,
        """
        SELECT internal_record_id, household_head_name, headship_type,
               size_total, address_line_1, country_code, record_status,
               record_name
        FROM g2p_register_households
        WHERE household_head_name = %s
        ORDER BY created_at DESC NULLS LAST
        LIMIT 1
        """,
        (household_head_name,),
    )
    return rows[0] if rows else None


def fetch_change_request(dsn: str, change_request_id: str) -> Optional[dict[str, Any]]:
    rows = query(
        dsn,
        """
        SELECT change_request_id, internal_record_id, section_id, tab_id,
               approval_status, register_id
        FROM g2p_register_change_requests
        WHERE change_request_id = %s
        """,
        (change_request_id,),
    )
    return rows[0] if rows else None


def fetch_individual_middle_name(dsn: str, internal_record_id: str) -> Optional[str]:
    row = fetch_individual_by_id(dsn, internal_record_id)
    if not row:
        return None
    return row.get("middle_name")


def fetch_household_head_name(dsn: str, internal_record_id: str) -> Optional[str]:
    row = fetch_household_by_id(dsn, internal_record_id)
    if not row:
        return None
    return row.get("household_head_name")


def wait_until(
    predicate: Callable[[], Any],
    *,
    timeout_s: float = 60.0,
    interval_s: float = 2.0,
    description: str = "condition",
) -> Any:
    """Poll until predicate returns a truthy value or timeout."""
    deadline = time.time() + timeout_s
    last: Any = None
    while time.time() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(interval_s)
    raise AssertionError(f"timed out waiting for {description} after {timeout_s}s (last={last!r})")
