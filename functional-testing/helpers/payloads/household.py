"""Household register intake section payloads."""

from __future__ import annotations

import copy
from typing import Any

from helpers.config import (
    HH_COMPOSITION_HEADSHIP_SECTION_ID,
    HH_DWELLING_SECTION_ID,
    HH_LOCATION_SECTION_ID,
    REGISTER_HOUSEHOLD,
)

HOUSEHOLD_SECTION_DEFS: dict[str, dict[str, Any]] = {
    HH_COMPOSITION_HEADSHIP_SECTION_ID: {
        "section_register_id": REGISTER_HOUSEHOLD,
        "payload": {
            "household_head_name": "Placeholder",
            "headship_type": "MALE_HEADED",
            "size_total": 4,
            "size_adults": 2,
            "size_children_u5": 1,
        },
    },
    HH_LOCATION_SECTION_ID: {
        "section_register_id": REGISTER_HOUSEHOLD,
        "payload": {
            "address_line_1": "Kebele 05, House 12",
            "postal_code": "1000",
            "country_code": "ET",
        },
    },
    HH_DWELLING_SECTION_ID: {
        "section_register_id": REGISTER_HOUSEHOLD,
        "payload": {
            "dwelling_type": "PERMANENT",
            "tenure_status": "OWNED",
        },
    },
}


def build_household_section_payload(section_id: str, head_name: str) -> dict:
    defn = HOUSEHOLD_SECTION_DEFS.get(section_id)
    if not defn:
        return {}
    payload = copy.deepcopy(defn["payload"])
    if section_id == HH_COMPOSITION_HEADSHIP_SECTION_ID:
        payload["household_head_name"] = head_name
    if section_id == HH_LOCATION_SECTION_ID:
        # Unique address avoids fuzzy-match collision with seed household h001.
        payload["address_line_1"] = f"{head_name} Lane"
    return payload
