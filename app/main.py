"""FastAPI app and CLI entrypoint for the insurance planning prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.agents.recommendation import RecommendationAgent
from app.models import RecommendationResponse, UserInput


STATIC_DIR = Path(__file__).resolve().parent / "static"

# Load local env vars from .env if present (kept out of git via .gitignore).
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

app = FastAPI(
    title="InsuraX",
    description=(
        "A lightweight student prototype for personalized insurance recommendations. "
        "For academic use only; any real deployment in India should be reviewed against current IRDAI "
        "regulations and product disclosures."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (login page assets)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

recommender = RecommendationAgent()


@app.get("/", response_class=HTMLResponse)
def login_page() -> HTMLResponse:
    """Serve the animated login page as the root."""
    login_html = STATIC_DIR / "login.html"
    return HTMLResponse(content=login_html.read_text(encoding="utf-8"))


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    """Simple health endpoint."""
    return {"message": "Insurance planning agent is running."}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(user_input: UserInput) -> RecommendationResponse:
    """Return a personalized policy recommendation."""
    return recommender.recommend(user_input)


def run_cli() -> None:
    """CLI demo for quick local testing without starting the API server."""
    parser = argparse.ArgumentParser(description="Insurance planning recommendation demo")
    parser.add_argument("--age", type=int, default=30)
    parser.add_argument("--income", type=float, default=600000)
    parser.add_argument("--dependents", type=int, default=0)
    parser.add_argument("--assets", type=float, default=0)
    parser.add_argument("--liabilities", type=float, default=0)
    parser.add_argument(
        "--insurance-goal",
        type=str,
        default="family_protection",
        choices=["family_protection", "health_security", "wealth_protection", "tax_savings"],
    )
    # Health profile flags
    parser.add_argument("--smoker", action="store_true", default=False, help="User is a regular smoker")
    parser.add_argument(
        "--alcohol",
        type=str,
        default="none",
        choices=["none", "occasional", "moderate", "heavy"],
        help="Alcohol consumption frequency",
    )
    parser.add_argument("--severe-health", action="store_true", default=False, help="Has severe pre-existing health conditions")
    args = parser.parse_args()

    payload = UserInput(
        age=args.age,
        income=args.income,
        dependents=args.dependents,
        assets=args.assets,
        liabilities=args.liabilities,
        insurance_goal=args.insurance_goal,
        is_smoker=args.smoker,
        alcohol_consumption=args.alcohol,
        has_severe_health_issues=args.severe_health,
    )

    result = recommender.recommend(payload)
    print(json.dumps(_response_to_dict(result), indent=2))


def _response_to_dict(response: RecommendationResponse) -> Dict[str, Any]:
    """Convert the pydantic response to a plain dict for CLI output."""
    return response.model_dump()


if __name__ == "__main__":
    run_cli()
