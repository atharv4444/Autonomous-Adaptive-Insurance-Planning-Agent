"""Gemini LLM client — uses the current google-genai SDK with retry and graceful fallback."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load .env if python-dotenv is available
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Attempt to import google-genai (new SDK)
# ---------------------------------------------------------------------------
try:
    from google import genai  # type: ignore
    from google.genai import types  # type: ignore
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False
    logger.warning("google-genai not installed. LLM features disabled.")

_MODEL_NAME = "gemini-2.5-flash-lite"
_MAX_RETRIES = 2
_RETRY_DELAY = 5.0

_client: Any = None


def _get_client() -> Any | None:
    """Return (and lazily init) the Gemini client, or None if unavailable."""
    global _client
    if _client is not None:
        return _client
    if not _GENAI_AVAILABLE:
        return None
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Running in local-only mode.")
        return None
    try:
        _client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialised (model: %s).", _MODEL_NAME)
        return _client
    except Exception as exc:
        logger.error("Failed to initialise Gemini client: %s", exc)
        return None


def is_available() -> bool:
    """Return True if Gemini is reachable and an API key is configured."""
    return _get_client() is not None


def chat(prompt: str, *, temperature: float = 0.3) -> Optional[str]:
    """
    Send a prompt to Gemini and return the text response.
    Returns None on any failure so callers can fall back to local logic.
    """
    client = _get_client()
    if client is None:
        return None

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=2048,
    )

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=_MODEL_NAME,
                contents=prompt,
                config=config,
            )
            return response.text.strip()
        except Exception as exc:
            err = str(exc).lower()
            if "quota" in err or "429" in err:
                if attempt < _MAX_RETRIES:
                    logger.warning("Quota hit, retrying in %.0fs…", _RETRY_DELAY)
                    time.sleep(_RETRY_DELAY)
                    continue
            logger.error("Gemini call failed (attempt %d): %s", attempt + 1, exc)
            return None

    return None


def chat_json(prompt: str, *, temperature: float = 0.2) -> Optional[Dict[str, Any]]:
    """
    Send a prompt expecting a JSON response.
    Strips markdown fences and returns a parsed dict, or None on failure.
    """
    raw = chat(prompt, temperature=temperature)
    if raw is None:
        return None
    # Strip ```json … ``` markdown fences
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()
    # Extract first JSON object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse LLM JSON: %s\nRaw: %s", exc, raw[:300])
        return None
