"""Individual register intake section payloads."""

from __future__ import annotations

import copy
from datetime import date
from typing import Any

from helpers.config import (
    DEMOGRAPHIC_SECTION_ID,
    HOUSEHOLD_LOOKUP_SECTION_ID,
    REGISTER_INDIVIDUAL,
)

BIRTH_DATE = "1990-01-01"


def _age() -> int:
    born = date.fromisoformat(BIRTH_DATE)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


INDIVIDUAL_SECTION_DEFS: dict[str, dict[str, Any]] = {
    HOUSEHOLD_LOOKUP_SECTION_ID: {
        "section_register_id": REGISTER_INDIVIDUAL,
        "payload": {"link_internal_record_id": ""},
    },
    DEMOGRAPHIC_SECTION_ID: {
        "section_register_id": REGISTER_INDIVIDUAL,
        "payload": {
            "first_name": "Placeholder",
            "middle_name": "",
            "last_name": "Placeholder",
            "birth_date": BIRTH_DATE,
            "estimated_age": _age(),
            "gender": "FEMALE",
            "marital_status": "MARRIED",
        },
    },
    "in_contact_details": {
        "section_register_id": REGISTER_INDIVIDUAL,
        "payload": {
            "phone_number": "+251911000000",
            "email": "",
        },
    },
    "in_location_details": {
        "section_register_id": REGISTER_INDIVIDUAL,
        "payload": {
            "address_line_1": "Kebele 05, House 12",
            "postal_code": "1000",
            "country_code": "ET",
        },
    },
    "in_relationship_to_head": {
        "section_register_id": REGISTER_INDIVIDUAL,
        "payload": {
            "relationship_to_head": "HEAD",
        },
    },
}


def build_individual_section_payload(
    section_id: str, household_id: str, name: tuple[str, str, str]
) -> dict:
    defn = INDIVIDUAL_SECTION_DEFS.get(section_id)
    if not defn:
        return {}
    payload = copy.deepcopy(defn["payload"])
    if section_id == HOUSEHOLD_LOOKUP_SECTION_ID:
        payload["link_internal_record_id"] = household_id
    if section_id == DEMOGRAPHIC_SECTION_ID:
        payload["first_name"], payload["middle_name"], payload["last_name"] = name
    return payload
