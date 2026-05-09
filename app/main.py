"""FastAPI app and CLI entrypoint for the insurance planning prototype."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.recommendation import RecommendationAgent
from app.models import RecommendationResponse, UserInput


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

recommender = RecommendationAgent()


@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint — API is alive."""
    return {"message": "InsuraX API is running. Use POST /recommend for recommendations."}


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    """Simple health endpoint."""
    return {"message": "Insurance planning agent is running."}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(user_input: UserInput) -> RecommendationResponse:
    """Return a personalized policy recommendation."""
    return recommender.recommend(user_input)


@app.post("/explain-scores")
def explain_scores(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI insights for each score component using OpenAI or Gemini (fallback).

    Expects the full RecommendationResponse as JSON in the body.
    Returns a dict of insight strings keyed by score type.
    """
    from app.llm.openai_explainer import generate_score_insights, openai_key_present
    from app.llm.gemini_explainer import generate_explanation_with_gemini, gemini_key_present

    # 1. Prepare the rich prompt (shared between both models)
    risk_score = payload.get("risk_score", 0)
    risk_label = payload.get("risk_label", "unknown")
    expected_loss = payload.get("expected_loss", 0)
    confidence = payload.get("confidence_score", 0)
    user_name = payload.get("user_profile", {}).get("name", "") or "the user"

    best = payload.get("best_policy", {}) or payload.get("final_recommendation", {})
    policy_name = best.get("policy", {}).get("policy_name", "N/A")
    policy_type = best.get("policy", {}).get("policy_type", "N/A")
    total_score = best.get("total_score", 0)
    utility_score = best.get("utility_score", 0)
    ai_score = best.get("ai_score", 0)
    suitability = best.get("suitability_score", 0)
    affordability = best.get("affordability_score", 0)
    coverage_score = best.get("coverage_score", 0)
    tradeoff = best.get("tradeoff_summary", "")
    critic_issues = payload.get("critic_issues", [])

    scenarios = payload.get("scenario_breakdown", [])
    scenario_text = "\n".join(
        f"  - {s.get('scenario_name','?')}: probability={s.get('probability',0)}, "
        f"cost=₹{s.get('cost',0):,.0f}, expected_impact=₹{s.get('expected_impact',0):,.0f}"
        for s in scenarios
    )

    prompt = f"""Here is the insurance recommendation data for {user_name}:

Risk Score: {risk_score}/100 (label: {risk_label})
Expected Annual Loss: ₹{expected_loss:,.0f}
AI Confidence: {confidence:.0f}%

Recommended Policy: {policy_name} ({policy_type})
  Total Score: {total_score:.2f}
  Utility Score: {utility_score:.2f}
  AI/DQN Score: {ai_score:.2f}
  Suitability: {suitability:.2f}
  Affordability: {affordability:.2f}
  Coverage Fit: {coverage_score:.2f}
  Tradeoff: {tradeoff}

Scenario Breakdown:
{scenario_text}

Critic Issues: {'; '.join(critic_issues) if critic_issues else 'None'}

Please provide a JSON object with these keys, each containing 1-3 sentence insights:
- "risk_score": Why is the risk score this value?
- "expected_loss": What does this expected loss mean for the user?
- "confidence": Why is the AI confidence at this level?
- "policy_recommendation": Why was this specific policy chosen?
- "utility_score": What does the utility score reflect?
- "overall_summary": A brief overall summary of the recommendation.

Return ONLY the JSON object, no markdown fences."""

    raw = None
    provider = "None"

    # 2. Try OpenAI first
    if openai_key_present():
        model_oa = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        raw = generate_score_insights(prompt=prompt, model=model_oa)
        if raw:
            provider = "OpenAI"

    # 3. Fallback to Gemini if OpenAI failed or is not configured
    if not raw and gemini_key_present():
        model_gem = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        # Reuse the existing Gemini explainer but with our specific prompt
        raw = generate_explanation_with_gemini(prompt=prompt, model=model_gem)
        if raw:
            provider = "Gemini"

    # 4. Handle cases where both failed
    if not raw:
        return {"available": False, "insights": {}, "provider": "None"}

    # 5. Parse the JSON response
    import json as _json
    try:
        # Clean up any potential markdown fences
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Try to handle ```json ... ``` or just ``` ... ```
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        
        insights = _json.loads(cleaned)
    except Exception as e:
        print(f"JSON Parsing Error for {provider} output: {e}")
        # If parsing fails, return the raw text as overall_summary
        insights = {"overall_summary": raw}

    return {"available": True, "insights": insights, "provider": provider}


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
