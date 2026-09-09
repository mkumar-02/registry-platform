"""Register profiles for Individual + Household functional API scenarios."""

from __future__ import annotations

from dataclasses import dataclass

from helpers.config import (
    CR_FIELD_HOUSEHOLD,
    CR_FIELD_INDIVIDUAL,
    DEMOGRAPHIC_SECTION_ID,
    HH_COMPOSITION_HEADSHIP_SECTION_ID,
    HOUSEHOLD_INTAKE_FORM_ID,
    HOUSEHOLD_INTAKE_TAB_ID,
    INDIVIDUAL_INTAKE_FORM_ID,
    INDIVIDUAL_INTAKE_TAB_ID,
    REGISTER_HOUSEHOLD,
    REGISTER_INDIVIDUAL,
    SEARCH_MARKER_HOUSEHOLD,
    SEARCH_MARKER_INDIVIDUAL,
)


@dataclass(frozen=True)
class RegisterProfile:
    key: str
    register_id: str
    intake_form_id: str
    intake_tab_id: str
    cr_section_id: str
    cr_field: str
    search_marker: str
    # Subject identity field used for search + DB lookup
    identity_field: str
    # Extra subject fields that must match between API get_subject_record and DB
    match_fields: tuple[str, ...]
    needs_linked_household: bool


INDIVIDUAL = RegisterProfile(
    key="individual",
    register_id=REGISTER_INDIVIDUAL,
    intake_form_id=INDIVIDUAL_INTAKE_FORM_ID,
    intake_tab_id=INDIVIDUAL_INTAKE_TAB_ID,
    cr_section_id=DEMOGRAPHIC_SECTION_ID,
    cr_field=CR_FIELD_INDIVIDUAL,
    search_marker=SEARCH_MARKER_INDIVIDUAL,
    identity_field="first_name",
    match_fields=("first_name", "middle_name", "last_name"),
    needs_linked_household=True,
)

HOUSEHOLD = RegisterProfile(
    key="household",
    register_id=REGISTER_HOUSEHOLD,
    intake_form_id=HOUSEHOLD_INTAKE_FORM_ID,
    intake_tab_id=HOUSEHOLD_INTAKE_TAB_ID,
    cr_section_id=HH_COMPOSITION_HEADSHIP_SECTION_ID,
    cr_field=CR_FIELD_HOUSEHOLD,
    search_marker=SEARCH_MARKER_HOUSEHOLD,
    identity_field="household_head_name",
    match_fields=("household_head_name", "headship_type", "address_line_1"),
    needs_linked_household=False,
)

ALL_PROFILES: tuple[RegisterProfile, ...] = (INDIVIDUAL, HOUSEHOLD)


def profile_id(profile: RegisterProfile) -> str:
    return profile.key
