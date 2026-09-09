"""Pytest fixtures for registry-platform functional API tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import pytest

_FUNC_ROOT = Path(__file__).resolve().parents[1]
if str(_FUNC_ROOT) not in sys.path:
    sys.path.insert(0, str(_FUNC_ROOT))

from helpers.config import Config
from helpers.http import StaffClient
from helpers.profiles import RegisterProfile
from helpers.provision import provision_household


@pytest.fixture(scope="session")
def cfg() -> Config:
    config = Config.from_env()
    config.require_api()
    config.require_db()
    return config


@pytest.fixture(scope="session")
def staff(cfg: Config):
    client = StaffClient.login(cfg)
    yield client
    client.close()


@pytest.fixture
def step():
    """Lightweight step logger for readable -s output."""

    def _step(message: str) -> None:
        print(f"\n  -> {message}")

    return _step


@pytest.fixture(scope="session")
def linked_household(staff: StaffClient, cfg: Config) -> str:
    """Approved Household internal_record_id for Individual intake linkage.

    Prefer an API-provisioned household so Individual tests do not depend on
    the compose SQL fixture alone. Falls back to FUNC_HOUSEHOLD_ID if set and
    provision fails (should not happen on a healthy gate).
    """

    def _step(message: str) -> None:
        print(f"\n  [linked_household] {message}")

    try:
        rec = provision_household(staff, cfg, step=_step)
        return rec.internal_record_id
    except Exception as exc:
        if cfg.household_id:
            print(f"\n  [linked_household] provision failed ({exc}); using FUNC_HOUSEHOLD_ID")
            return cfg.household_id
        raise


@pytest.fixture
def household_id_for(profile: RegisterProfile, linked_household: str) -> Optional[str]:
    """Household link id when the profile needs one (Individual); else None."""
    return linked_household if profile.needs_linked_household else None
