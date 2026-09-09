"""Change-request create / approve flows."""

from __future__ import annotations

from typing import Optional

from helpers.config import Config
from helpers.http import StaffClient
from helpers.models import ChangeRequestResult
from helpers.profiles import INDIVIDUAL, RegisterProfile
from helpers.util import assert_ok, noop, response_payload, unique_cr_value, StepFn


def create_field_cr(
    staff: StaffClient,
    cfg: Config,
    profile: RegisterProfile,
    *,
    subject_internal_record_id: str,
    identity_value: str,
    new_value: Optional[str] = None,
    step: StepFn = noop,
) -> ChangeRequestResult:
    section_id = profile.cr_section_id
    field_name = profile.cr_field
    if new_value is None:
        prefix = "FuncHead" if profile.key == "household" else "FuncMid"
        new_value = unique_cr_value(prefix)

    step("get_all_sections")
    sections_body = staff.post_json(
        "/register-section-metadata/get_all_sections",
        {"register_id": profile.register_id},
    )
    assert_ok(sections_body, "get_all_sections")
    sections = response_payload(sections_body)
    meta = next(
        (
            s
            for s in (sections if isinstance(sections, list) else [])
            if s.get("section_id") == section_id
        ),
        None,
    )
    assert meta, f"section {section_id} not in get_all_sections"
    section_register_id = meta.get("section_register_id")
    is_core = bool(meta.get("is_core_section"))

    step("get_all_tabs")
    tabs_body = staff.post_json(
        "/register-tab-metadata/get_all_tabs",
        {"register_id": profile.register_id},
    )
    assert_ok(tabs_body, "get_all_tabs")
    tabs = response_payload(tabs_body) if isinstance(response_payload(tabs_body), list) else []
    tab_ids = [
        t["tab_id"]
        for t in sorted(tabs, key=lambda t: t.get("tab_order", 0))
        if t.get("tab_id")
    ]

    tab_id = None
    for tid in tab_ids:
        sb = staff.post_json("/register-tab-metadata/get_sections", {"tab_id": tid})
        assert_ok(sb, f"get_sections:{tid}")
        sp = response_payload(sb)
        sids = [
            s.get("section_id")
            for s in (
                sp
                if isinstance(sp, list)
                else sp.get("sections", [])
                if isinstance(sp, dict)
                else []
            )
        ]
        if section_id in sids:
            tab_id = tid
            break
    assert tab_id, f"section {section_id} not on any tab"

    step("get_tab_records")
    tab_records = staff.post_json(
        "/register-data/get_tab_records",
        {
            "subject_register_id": profile.register_id,
            "subject_record_id": subject_internal_record_id,
            "tab_id": tab_id,
        },
    )
    assert_ok(tab_records, "get_tab_records")
    groups = response_payload(tab_records) if isinstance(response_payload(tab_records), list) else []
    record_id = None
    for g in groups:
        if g.get("section_register_id") != section_register_id:
            continue
        recs = g.get("records") or []
        if recs:
            record_id = recs[0].get("internal_record_id")
    assert record_id, f"no record for section_register_id={section_register_id}"

    change_payload = [
        {"internal_record_id": record_id, "edit_action": "UPDATE", field_name: new_value}
    ]
    request_payload = {
        "register_id": profile.register_id,
        "tab_id": tab_id,
        "section_id": section_id,
        "section_register_id": section_register_id,
        "internal_record_id": subject_internal_record_id,
        "change_payload": change_payload,
    }

    if is_core:
        step("create_change_request_for_core_data")
        cr_body = staff.post_json(
            "/change-requests-core-data/create_change_request_for_core_data",
            request_payload,
        )
    else:
        step("create_change_request")
        cr_body = staff.post_json(
            "/change-requests/create_change_request",
            request_payload,
        )
    assert_ok(cr_body, "create_cr")
    cr_payload = response_payload(cr_body)
    cr_id = cr_payload.get("change_request_id") if isinstance(cr_payload, dict) else None
    assert cr_id, f"no change_request_id in response: {cr_body}"

    step(f"created CR {cr_id}: {field_name} -> {new_value!r}")
    return ChangeRequestResult(
        change_request_id=cr_id,
        identity_value=identity_value,
        new_value=new_value,
        section_id=section_id,
        field_name=field_name,
    )


def create_middle_name_cr(
    staff: StaffClient,
    cfg: Config,
    *,
    subject_internal_record_id: str,
    first_name: str,
    new_middle_name: Optional[str] = None,
    step: StepFn = noop,
) -> ChangeRequestResult:
    """Back-compat wrapper for Individual middle_name CR (UI fixtures)."""
    return create_field_cr(
        staff,
        cfg,
        INDIVIDUAL,
        subject_internal_record_id=subject_internal_record_id,
        identity_value=first_name,
        new_value=new_middle_name,
        step=step,
    )


def verify_and_approve_cr(
    staff: StaffClient, change_request_id: str, step: StepFn = noop
) -> None:
    step("add_verification_for_change_request")
    assert_ok(
        staff.post_json(
            "/change-requests/add_verification_for_change_request",
            {"change_request_id": change_request_id, "is_approved": True},
        ),
        "add_verification_for_cr",
    )
    step("approve_change_request")
    assert_ok(
        staff.post_json(
            "/change-requests/approve_change_request",
            {"change_request_id": change_request_id},
        ),
        "approve_cr",
    )
