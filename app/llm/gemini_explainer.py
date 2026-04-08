"""Optional Gemini-based explanation generator.

This module is intentionally best-effort: if the key is missing or the SDK
isn't available, callers should fall back to template explanations.
"""

from __future__ import annotations

import os
from typing import Optional


def gemini_key_present() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def generate_explanation_with_gemini(*, prompt: str, model: str) -> Optional[str]:
    """Return an explanation string, or None if unavailable/failed."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai  # type: ignore
    except Exception:
        return None

    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(model=model, contents=prompt)

        text = getattr(resp, "text", None)
        if not text:
            return None
        text = str(text).strip()
        return text or None
    except Exception:
        return None

