"""Simple file-backed memory store for profiles and recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.models import RankedPolicy, UserProfile


class MemoryStore:
    """Persist user profiles and recommendation history in a local JSON file."""

    def __init__(self, storage_path: Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent.parent / "data" / "memory_store.json"
        self.storage_path = storage_path or default_path

    def save_user_profile(self, profile: UserProfile) -> str:
        """Save a user profile and return its deterministic signature."""
        store = self._read_store()
        profile_signature = self._build_profile_signature(profile)
        store["profiles"].append(
            {
                "profile_signature": profile_signature,
                "profile": profile.model_dump(),
            }
        )
        self._write_store(store)
        return profile_signature

    def save_recommendation(self, profile_signature: str, recommendation: RankedPolicy) -> None:
        """Save a recommendation linked to a profile signature."""
        store = self._read_store()
        store["recommendations"].append(
            {
                "profile_signature": profile_signature,
                "recommendation": recommendation.model_dump(),
            }
        )
        self._write_store(store)

    def get_previous_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent recommendation history, failing safely on malformed data."""
        store = self._read_store()
        recommendations = store.get("recommendations", [])
        return recommendations[-limit:]

    def _build_profile_signature(self, profile: UserProfile) -> str:
        """Create a lightweight deterministic signature from core inputs."""
        return (
            f"{profile.age}-{int(profile.income)}-{profile.dependents}-"
            f"{int(profile.liabilities)}-{profile.insurance_goal}"
        )

    def _read_store(self) -> Dict[str, List[Dict[str, Any]]]:
        """Read the store or initialize an empty structure when needed."""
        if not self.storage_path.exists():
            return self._empty_store()

        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                raw_data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return self._empty_store()

        profiles = raw_data.get("profiles", [])
        recommendations = raw_data.get("recommendations", [])
        return {
            "profiles": profiles if isinstance(profiles, list) else [],
            "recommendations": recommendations if isinstance(recommendations, list) else [],
        }

    def _write_store(self, store: Dict[str, List[Dict[str, Any]]]) -> None:
        """Persist the memory store to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(store, file, indent=2)

    def _empty_store(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return the default store structure."""
        # TODO: Add session-aware memory and richer retrieval strategies.
        # TODO: Support vector memory or external persistence backends.
        return {"profiles": [], "recommendations": []}
