"""Intake create / finalize / approve flows."""

from __future__ import annotations

from typing import Optional

from helpers.config import Config
from helpers.http import StaffClient
from helpers.models import IntakeResult, ProvisionedRecord
from helpers.payloads import (
    build_household_section_payload,
    build_individual_section_payload,
    extract_tab_sections,
    merge_accumulated,
    section_defs_for,
)
from helpers.profiles import HOUSEHOLD, INDIVIDUAL, RegisterProfile
from helpers.util import (
    assert_ok,
    noop,
    response_payload,
    unique_household_head_name,
    unique_individual_name,
    StepFn,
)


def create_and_finalize_intake(
    staff: StaffClient,
    cfg: Config,
    profile: RegisterProfile = INDIVIDUAL,
    *,
    household_id: Optional[str] = None,
    step: StepFn = noop,
) -> IntakeResult:
    section_defs = section_defs_for(profile)

    if profile.key == "individual":
        link_hh = household_id or cfg.household_id
        if not link_hh:
            cfg.require_household()
            link_hh = cfg.household_id
        name = unique_individual_name(profile.search_marker)
        first, middle, last = name
        identity = first
        fields = {
            "first_name": first,
            "middle_name": middle,
            "last_name": last,
        }
    else:
        link_hh = None
        name = None
        head = unique_household_head_name(profile.search_marker)
        identity = head
        fields = {
            "household_head_name": head,
            "headship_type": "MALE_HEADED",
            "address_line_1": f"{head} Lane",
            "size_total": 4,
        }

    step(f"render intake form {profile.intake_form_id} ({profile.key})")
    render = staff.post_json(
        "/intake-form-metadata/render_intake_form",
        {"form_id": profile.intake_form_id},
    )
    assert_ok(render, "render_intake_form")
    tab_sections = extract_tab_sections(render, profile.intake_tab_id)
    assert tab_sections, f"no sections for tab {profile.intake_tab_id}"

    section_ids = [s["section_id"] for s in tab_sections]
    step(f"sections ({len(section_ids)}): {section_ids}")

    submission_id: Optional[str] = None
    accumulated: dict = {}

    for section_id in section_ids:
        defn = section_defs.get(section_id)
        if not defn:
            step(f"skip unknown section {section_id}")
            continue

        if profile.key == "individual":
            own = build_individual_section_payload(section_id, link_hh, name)  # type: ignore[arg-type]
        else:
            own = build_household_section_payload(section_id, identity)

        merged = merge_accumulated(defn["section_register_id"], own, accumulated)

        step(f"save section {section_id}")
        save = staff.post_json(
            "/intake-form-data/save_intake_form_submission",
            {
                "submission_id": submission_id,
                "section_id": section_id,
                "section_payload": [merged],
                "section_register_id": defn["section_register_id"],
                "form_id": profile.intake_form_id,
                "register_id": profile.register_id,
            },
        )
        assert_ok(save, f"save:{section_id}")
        if submission_id is None:
            submission_id = response_payload(save).get("submission_id")
            assert submission_id, "first save must return submission_id"
            step(f"submission_id={submission_id}")

    assert submission_id
    step("finalize")
    assert_ok(
        staff.post_json(
            "/intake-form-data/finalize_intake_form_submission",
            {"submission_id": submission_id},
        ),
        "finalize",
    )
    return IntakeResult(submission_id=submission_id, identity_value=identity, fields=fields)


def verify_and_approve_intake(
    staff: StaffClient, submission_id: str, step: StepFn = noop
) -> None:
    step(f"get submission {submission_id}")
    assert_ok(
        staff.post_json(
            "/intake-form-data/get_intake_form_submission",
            {"submission_id": submission_id},
        ),
        "get submission",
    )
    step("add_verification")
    assert_ok(
        staff.post_json(
            "/verifications/add_verification",
            {"submission_id": submission_id, "is_approved": True},
        ),
        "add_verification",
    )
    step("approve")
    assert_ok(
        staff.post_json(
            "/intake-form-data/approve_intake_form_submission",
            {"submission_id": submission_id},
        ),
        "approve",
    )


def provision_record(
    staff: StaffClient,
    cfg: Config,
    profile: RegisterProfile = INDIVIDUAL,
    *,
    household_id: Optional[str] = None,
    step: StepFn = noop,
) -> ProvisionedRecord:
    from helpers.flows.register import wait_for_register_record

    created = create_and_finalize_intake(
        staff, cfg, profile, household_id=household_id, step=step
    )
    verify_and_approve_intake(staff, created.submission_id, step=step)
    hit = wait_for_register_record(staff, profile, created.identity_value)
    return ProvisionedRecord(
        internal_record_id=hit["internal_record_id"],
        identity_value=created.identity_value,
        fields=created.fields,
        submission_id=created.submission_id,
    )


def provision_individual(
    staff: StaffClient, cfg: Config, step: StepFn = noop
) -> ProvisionedRecord:
    """Provision an approved Individual (UI fixtures + API scenarios)."""
    return provision_record(staff, cfg, INDIVIDUAL, step=step)


def provision_household(
    staff: StaffClient, cfg: Config, step: StepFn = noop
) -> ProvisionedRecord:
    return provision_record(staff, cfg, HOUSEHOLD, step=step)
