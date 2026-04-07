"""Streamlit UI for the Autonomous Insurance Planning Agent."""

from __future__ import annotations

from typing import Dict, List

import streamlit as st
from pydantic import ValidationError

from app.main import recommender
from app.models import RecommendationResponse, UserInput


GOAL_MAPPING = {
    "health": "health_security",
    "life": "wealth_protection",
    "family_protection": "family_protection",
    "savings": "tax_savings",
}


def run_pipeline(user_payload: Dict[str, float | int | str]) -> RecommendationResponse:
    """Validate UI payload and run the backend recommendation pipeline."""
    validated_input = UserInput(**user_payload)
    return recommender.recommend(validated_input)


def build_top_policy_rows(result: RecommendationResponse) -> List[Dict[str, float | str]]:
    """Prepare top policy rows for table and chart display."""
    rows: List[Dict[str, float | str]] = []
    for ranked_policy in result.top_policies:
        rows.append(
            {
                "Policy Name": ranked_policy.policy.policy_name,
                "Coverage": ranked_policy.policy.coverage,
                "Premium": ranked_policy.policy.premium,
                "Utility Score": ranked_policy.utility_score,
            }
        )
    return rows


def render_user_summary(input_payload: Dict[str, float | int | str]) -> None:
    """Render user input summary in a clean two-column layout."""
    st.header("User Summary")
    left_col, right_col = st.columns(2)

    with left_col:
        st.write(f"**Age:** {input_payload['age']}")
        st.write(f"**Income:** {input_payload['income']:,.0f}")
        st.write(f"**Dependents:** {input_payload['dependents']}")

    with right_col:
        st.write(f"**Assets:** {input_payload['assets']:,.0f}")
        st.write(f"**Liabilities:** {input_payload['liabilities']:,.0f}")
        st.write(f"**Insurance Goal:** {input_payload['insurance_goal']}")


def render_risk_and_scenarios(result: RecommendationResponse) -> None:
    """Render risk analysis and scenario simulation outputs."""
    st.header("Risk Analysis")
    risk_col, expected_loss_col, confidence_col = st.columns(3)

    with risk_col:
        st.metric("Risk Score", f"{result.risk_score:.2f}", result.risk_label.title())
    with expected_loss_col:
        st.metric("Expected Loss", f"{result.expected_loss:,.0f}")
    with confidence_col:
        st.metric("Confidence Score", f"{result.confidence_score:.2f}")

    st.header("Scenario Simulation")
    scenario_rows = [
        {
            "Scenario": item.scenario_name.replace("_", " ").title(),
            "Probability": item.probability,
            "Cost": item.cost,
            "Expected Impact": item.expected_impact,
        }
        for item in result.scenario_breakdown
    ]
    st.table(scenario_rows)

    st.caption("Expected loss is computed from simulated medical emergency, accident, and income loss scenarios.")


def render_top_policies(result: RecommendationResponse) -> None:
    """Render the top three policies with a comparison chart."""
    st.header("Top Policies")
    top_policy_rows = build_top_policy_rows(result)
    st.table(top_policy_rows)
    st.subheader("Coverage vs Premium Comparison")
    render_policy_comparison_bars(top_policy_rows)


def render_policy_comparison_bars(top_policy_rows: List[Dict[str, float | str]]) -> None:
    """Render a lightweight comparison visual without chart dependencies."""
    max_coverage = max(float(row["Coverage"]) for row in top_policy_rows) if top_policy_rows else 1.0
    max_premium = max(float(row["Premium"]) for row in top_policy_rows) if top_policy_rows else 1.0

    for row in top_policy_rows:
        policy_name = str(row["Policy Name"])
        coverage = float(row["Coverage"])
        premium = float(row["Premium"])
        utility_score = float(row["Utility Score"])

        st.write(f"**{policy_name}**  |  Utility Score: {utility_score:.2f}")

        coverage_ratio = int((coverage / max_coverage) * 100) if max_coverage else 0
        premium_ratio = int((premium / max_premium) * 100) if max_premium else 0

        coverage_col, premium_col = st.columns(2)
        with coverage_col:
            st.caption(f"Coverage: {coverage:,.0f}")
            st.progress(max(coverage_ratio, 1), text=f"Coverage strength: {coverage_ratio}%")
        with premium_col:
            st.caption(f"Premium: {premium:,.0f}")
            st.progress(max(premium_ratio, 1), text=f"Premium level: {premium_ratio}%")


def render_final_recommendation(result: RecommendationResponse) -> None:
    """Highlight the final recommendation clearly for demo use."""
    final_policy = result.final_recommendation

    st.header("Final Recommendation")
    st.success(
        f"{final_policy.policy.policy_name} selected as the final recommendation with confidence "
        f"{result.confidence_score:.2f}."
    )

    detail_col_1, detail_col_2, detail_col_3 = st.columns(3)
    with detail_col_1:
        st.write(f"**Policy Name:** {final_policy.policy.policy_name}")
        st.write(f"**Coverage:** {final_policy.policy.coverage:,.0f}")
    with detail_col_2:
        st.write(f"**Premium:** {final_policy.policy.premium:,.0f}")
        st.write(f"**Utility Score:** {final_policy.utility_score:.2f}")
    with detail_col_3:
        st.write(f"**Premium / Income:** {final_policy.premium_ratio:.2%}")
        st.write(f"**Coverage Gap:** {final_policy.coverage_gap:,.0f}")

    st.subheader("Explanation")
    st.info(result.explanation)


def render_critic_insights(result: RecommendationResponse) -> None:
    """Render critic issues and reranking commentary."""
    st.header("Critic Insights")

    if not result.critic_issues:
        st.success("The critic did not find any issues with the final recommendation.")
        return

    for issue in result.critic_issues:
        if issue.lower().startswith("no major issues"):
            st.success(issue)
        else:
            st.warning(issue)

    top_policy_name = result.top_policies[0].policy.policy_name if result.top_policies else ""
    final_policy_name = result.final_recommendation.policy.policy_name
    if top_policy_name and top_policy_name != final_policy_name:
        st.warning(
            f"The critic reranked the recommendation from {top_policy_name} to {final_policy_name} "
            "after validation."
        )
    else:
        st.caption("The critic accepted the top-ranked policy after validation.")


def main() -> None:
    """Run the Streamlit UI."""
    st.set_page_config(page_title="Autonomous Insurance Planning Agent", layout="wide")
    st.title("🤖 Autonomous Insurance Planning Agent")
    st.write(
        "A demo-friendly multi-agent insurance planning interface that shows profiling, risk analysis, "
        "scenario simulation, policy ranking, critic validation, and the final recommendation."
    )

    with st.sidebar:
        st.header("User Inputs")
        with st.form("recommendation_form"):
            age = st.number_input("Age", min_value=18, max_value=70, value=30, step=1)
            income = st.number_input("Income", min_value=0.0, value=600000.0, step=10000.0)
            dependents = st.number_input("Dependents", min_value=0, max_value=10, value=0, step=1)
            assets = st.number_input("Assets", min_value=0.0, value=0.0, step=10000.0)
            liabilities = st.number_input("Liabilities", min_value=0.0, value=0.0, step=10000.0)
            insurance_goal = st.selectbox(
                "Insurance Goal",
                options=["health", "life", "family_protection", "savings"],
                index=2,
            )
            submitted = st.form_submit_button("Get Recommendation")

    if not submitted:
        st.caption("Enter the user details and click 'Get Recommendation' to run the agentic pipeline.")
        return

    user_payload: Dict[str, float | int | str] = {
        "age": int(age),
        "income": float(income),
        "dependents": int(dependents),
        "assets": float(assets),
        "liabilities": float(liabilities),
        "insurance_goal": GOAL_MAPPING[insurance_goal],
    }

    try:
        with st.spinner("Running the multi-agent insurance planning pipeline..."):
            result = run_pipeline(user_payload)
    except ValidationError as error:
        st.error("Invalid input detected. Please review the values and try again.")
        st.code(str(error))
        return
    except Exception as error:  # pragma: no cover - safety fallback for interactive demo use.
        st.error("The recommendation system could not generate a result.")
        st.code(str(error))
        return

    if not result.top_policies:
        st.warning("No recommendation could be generated for the provided inputs.")
        return

    render_user_summary(
        {
            **user_payload,
            "insurance_goal": insurance_goal,
        }
    )
    render_risk_and_scenarios(result)
    render_top_policies(result)
    render_final_recommendation(result)
    render_critic_insights(result)
    st.caption("Run the app with: streamlit run app/ui.py")


if __name__ == "__main__":
    main()
