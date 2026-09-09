"""Result dataclasses returned by intake / provision / CR flows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IntakeResult:
    submission_id: str
    identity_value: str
    fields: dict[str, Any]

    # UI / older callers expect Individual name attributes
    @property
    def first_name(self) -> str:
        return str(self.fields.get("first_name") or self.identity_value)

    @property
    def middle_name(self) -> str:
        return str(self.fields.get("middle_name") or "")

    @property
    def last_name(self) -> str:
        return str(self.fields.get("last_name") or "")


@dataclass
class ProvisionedRecord:
    internal_record_id: str
    identity_value: str
    fields: dict[str, Any]
    submission_id: str

    @property
    def first_name(self) -> str:
        return str(self.fields.get("first_name") or self.identity_value)

    @property
    def middle_name(self) -> str:
        return str(self.fields.get("middle_name") or "")

    @property
    def last_name(self) -> str:
        return str(self.fields.get("last_name") or "")


@dataclass
class ChangeRequestResult:
    change_request_id: str
    identity_value: str
    new_value: str
    section_id: str
    field_name: str

    @property
    def first_name(self) -> str:
        return self.identity_value
