"""Helper utilities for loading data and shaping explanation text."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.models import Policy


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_policies() -> List[Policy]:
    """Load the local dummy policy catalog from JSON."""
    policies_path = DATA_DIR / "policies.json"
    with policies_path.open("r", encoding="utf-8") as file:
        raw_policies = json.load(file)
    return [Policy(**policy) for policy in raw_policies]


def round_money(value: float) -> float:
    """Return a compact rounded monetary value for responses."""
    return round(value, 2)


def build_explanation(best_policy_name: str, risk_label: str, reasons: List[str]) -> str:
    """Create a short human-readable recommendation summary."""
    reason_text = " ".join(reasons[:3])
    return (
        f"{best_policy_name} is recommended because the user has a {risk_label} risk profile. "
        f"{reason_text}"
    )
