"""FastAPI app and CLI entrypoint for the insurance planning prototype."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from fastapi import FastAPI

from app.agents.recommendation import RecommendationAgent
from app.models import RecommendationResponse, UserInput


app = FastAPI(
    title="Autonomous Adaptive Insurance Planning Agent",
    description="A lightweight student prototype for personalized insurance recommendations.",
    version="0.1.0",
)

recommender = RecommendationAgent()


@app.get("/")
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
    args = parser.parse_args()

    payload = UserInput(
        age=args.age,
        income=args.income,
        dependents=args.dependents,
        assets=args.assets,
        liabilities=args.liabilities,
        insurance_goal=args.insurance_goal,
    )

    result = recommender.recommend(payload)
    print(json.dumps(_response_to_dict(result), indent=2))


def _response_to_dict(response: RecommendationResponse) -> Dict[str, Any]:
    """Convert the pydantic response to a plain dict for CLI output."""
    return response.model_dump()


if __name__ == "__main__":
    run_cli()
