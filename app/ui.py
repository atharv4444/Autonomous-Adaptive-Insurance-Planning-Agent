"""Streamlit UI — Full redesign: centered User Profile form + multi-tab agent dashboard."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import altair as alt
import pandas as pd
import streamlit as st
from pydantic import ValidationError

from app.main import recommender
from app.models import RecommendationResponse, UserInput


# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsureAI — Autonomous Planning Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #0b0b18; }

    /* collapse sidebar toggle */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* Remove default padding */
    .block-container { padding-top: 2rem !important; }

    /* Section labels */
    .section-label {
        color: #a78bfa;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin: 20px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(167,139,250,0.2);
    }

    /* Card wrappers */
    .glass-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
    }

    /* Metric override */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 16px !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: rgba(255,255,255,0.55);
        font-size: 13px;
        padding: 10px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(124,58,237,0.35) !important;
        color: white !important;
    }

    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #7c3aed, #3b82f6);
    }

    h1, h2, h3 { color: #f4f4f4 !important; }
    p, li, label { color: rgba(255,255,255,0.8) !important; }
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        padding: 14px !important;
        font-size: 15px !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 30px rgba(124,58,237,0.5) !important;
        transform: translateY(-1px) !important;
    }
    .stDivider { border-color: rgba(255,255,255,0.07) !important; }
    .stExpander { border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; }
    code { color: #a78bfa !important; background: rgba(167,139,250,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
POLICY_GOAL_MAP: Dict[str, str] = {
    "Health Insurance": "health_security",
    "Life Insurance": "family_protection",
    "Car Insurance": "car_insurance",
    "Home Insurance": "home_insurance",
}

RISK_COLORS = {"low": "#22c55e", "moderate": "#f59e0b", "high": "#ef4444"}

SCENARIO_META: Dict[str, Dict[str, str]] = {
    "medical_emergency": {
        "icon": "🏥",
        "color": "#ef4444",
        "title": "Medical Emergency",
        "desc": "Sudden hospitalisation, surgery, or critical illness requiring large immediate outlay.",
        "animation": "🔴",
    },
    "accident": {
        "icon": "🚗",
        "color": "#f59e0b",
        "title": "Accident",
        "desc": "Road accident or physical injury causing treatment costs and potential third-party liability.",
        "animation": "🟡",
    },
    "income_loss": {
        "icon": "💼",
        "color": "#8b5cf6",
        "title": "Income Loss",
        "desc": "Job loss or business disruption halting regular salary and EMI payment capacity.",
        "animation": "🟣",
    },
}

# ─────────────────────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────────────────────
for key, default in [
    ("result", None),
    ("user_payload", None),
    ("user_name", ""),
    ("profile_pic_bytes", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────
def render_header() -> None:
    _, hcol, _ = st.columns([1, 2, 1])
    with hcol:
        st.markdown("""
        <div style='text-align:center;padding:32px 0 24px 0;'>
            <div style='font-size:52px;'>🛡️</div>
            <h1 style='font-size:34px;font-weight:900;margin:8px 0 4px;
                background:linear-gradient(135deg,#a78bfa,#60a5fa,#34d399);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;'>InsureAI</h1>
            <p style='color:rgba(255,255,255,0.35);font-size:12px;letter-spacing:4px;
                text-transform:uppercase;margin:0;'>Autonomous Adaptive Planning Agent</p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Profile Form (Centered)
# ─────────────────────────────────────────────────────────────
def render_profile_form() -> None:
    _, form_col, _ = st.columns([1, 3, 1])

    with form_col:
        st.markdown('<div class="section-label">👤 User Profile</div>', unsafe_allow_html=True)

        with st.form("profile_form", clear_on_submit=False):

            # ── Profile picture + name/address ──────────────────────
            pic_col, info_col = st.columns([1, 2])
            with pic_col:
                uploaded_pic = st.file_uploader(
                    "Photo", type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed",
                )
                if uploaded_pic is not None:
                    st.session_state.profile_pic_bytes = uploaded_pic.read()
                if st.session_state.profile_pic_bytes:
                    st.image(st.session_state.profile_pic_bytes, width=110)
                else:
                    st.markdown("""
                    <div style='width:110px;height:110px;border-radius:50%;
                        background:linear-gradient(135deg,#7c3aed,#3b82f6);
                        display:flex;align-items:center;justify-content:center;
                        font-size:38px;'>👤</div>
                    """, unsafe_allow_html=True)
                st.caption("Click to upload")

            with info_col:
                name = st.text_input("Full Name *", placeholder="e.g. Rajesh Kumar")
                address = st.text_area("Address", placeholder="City, State, Country", height=78)

            st.divider()

            # ── Basic Info ───────────────────────────────────────────
            st.markdown('<div class="section-label">📋 Basic Information</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                age = st.number_input("Age", min_value=18, max_value=70, value=30, step=1)
            with b2:
                income = st.number_input(
                    "Annual Income (₹)",
                    min_value=0,
                    value=600000,
                    step=10000,
                    format="%d",
                    help="Total yearly income before tax in Indian Rupees",
                )
                if income > 0:
                    st.caption(f"₹ {income:,.0f} / year  ·  ₹ {income/12:,.0f} / month")

            st.divider()

            # ── Dependents ──────────────────────────────────────────
            st.markdown('<div class="section-label">👨‍👩‍👧‍👦 Dependents</div>', unsafe_allow_html=True)
            d1, d2, d3 = st.columns(3)
            with d1:
                parents = st.number_input(
                    "👴 Parents", min_value=0, max_value=4, value=0, step=1,
                    help="Number of financial dependent parents",
                )
            with d2:
                children = st.number_input(
                    "👶 Children", min_value=0, max_value=10, value=0, step=1,
                    help="Number of dependent children",
                )
            with d3:
                has_spouse = st.selectbox("💑 Spouse", options=["No", "Yes"], index=0)

            spouse_n = 1 if has_spouse == "Yes" else 0
            total_dependents = parents + children + spouse_n

            dep_parts = []
            if parents:
                dep_parts.append(f"{parents} parent{'s' if parents > 1 else ''}")
            if children:
                dep_parts.append(f"{children} child{'ren' if children > 1 else ''}")
            if spouse_n:
                dep_parts.append("spouse")
            dep_label = " + ".join(dep_parts) if dep_parts else "none"
            st.info(f"👥 Total Dependents: **{total_dependents}** ({dep_label})")

            st.divider()

            # ── Assets ──────────────────────────────────────────────
            st.markdown('<div class="section-label">🏦 Assets</div>', unsafe_allow_html=True)
            st.caption("Check all that apply. Leave unchecked if not applicable.")

            has_bank = st.checkbox("🏦 Bank / FD / Savings Account", value=True)
            bank_bal = 0
            if has_bank:
                bank_bal = st.number_input("Bank Balance (₹)", min_value=0, value=0, step=10000, format="%d")

            has_realestate = st.checkbox("🏠 Real Estate / Property")
            realestate_val = 0
            if has_realestate:
                realestate_val = st.number_input("Property Market Value (₹)", min_value=0, value=0, step=100000, format="%d")

            has_vehicles = st.checkbox("🚗 Vehicles")
            vehicle_val = 0
            if has_vehicles:
                vc1, vc2 = st.columns(2)
                with vc1:
                    n_vehicles = st.number_input("Number of Vehicles", min_value=1, max_value=20, value=1, step=1)
                with vc2:
                    vehicle_val = st.number_input("Total Vehicle Value (₹)", min_value=0, value=0, step=50000, format="%d")

            has_investments = st.checkbox("📈 Stocks / Mutual Funds / Gold / Crypto")
            invest_val = 0
            if has_investments:
                invest_val = st.number_input("Total Investment Value (₹)", min_value=0, value=0, step=10000, format="%d")

            total_assets = bank_bal + realestate_val + vehicle_val + invest_val
            if total_assets > 0:
                st.success(f"💰 Total Assets: **₹ {total_assets:,.0f}**")

            st.divider()

            # ── Liabilities ─────────────────────────────────────────
            st.markdown('<div class="section-label">📉 Liabilities</div>', unsafe_allow_html=True)

            st.caption("Enter 0 if a loan does not apply to you.")
            l1, l2, l3 = st.columns(3)
            with l1:
                home_loan = st.number_input(
                    "🏠 Home Loan / Mortgage (₹)",
                    min_value=0, value=0, step=50000, format="%d",
                    help="Outstanding home loan or mortgage amount",
                )
            with l2:
                car_loan = st.number_input(
                    "🚗 Vehicle Loan (₹)",
                    min_value=0, value=0, step=10000, format="%d",
                    help="Outstanding vehicle loan amount",
                )
            with l3:
                personal_loan = st.number_input(
                    "💳 Personal / CC Debt (₹)",
                    min_value=0, value=0, step=5000, format="%d",
                    help="Personal loan plus credit card debt",
                )

            total_liabilities = home_loan + car_loan + personal_loan
            if total_liabilities > 0:
                st.warning(f"⚠️ Total Liabilities: **₹ {total_liabilities:,.0f}**")

            st.divider()

            # ── Insurance Policy ────────────────────────────────────
            st.markdown('<div class="section-label">🛡️ Insurance Policy</div>', unsafe_allow_html=True)
            insurance_policy = st.selectbox(
                "What type of insurance are you looking for?",
                options=["Health Insurance", "Life Insurance", "Car Insurance", "Home Insurance"],
                help="Select the primary policy type you need.",
            )

            st.divider()

            # ── Submit ──────────────────────────────────────────────
            submitted = st.form_submit_button(
                "🚀 Run Agent Pipeline",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            mapped_goal = POLICY_GOAL_MAP[insurance_policy]
            payload: Dict[str, Any] = {
                "age": int(age),
                "income": float(income),
                "dependents": int(total_dependents),
                "assets": float(total_assets),
                "liabilities": float(total_liabilities),
                "insurance_goal": mapped_goal,
            }
            with st.spinner("⚙️ Running the multi-agent insurance planning pipeline…"):
                try:
                    validated = UserInput(**payload)
                    result = recommender.recommend(validated)
                    st.session_state.result = result
                    st.session_state.user_payload = {
                        **payload,
                        "insurance_policy": insurance_policy,
                        "address": address,
                    }
                    st.session_state.user_name = name or "User"
                    st.rerun()
                except ValidationError as exc:
                    st.error("Invalid input — please check your values.")
                    st.code(str(exc))
                except Exception as exc:
                    st.error("Pipeline error — please try again.")
                    st.code(str(exc))


# ─────────────────────────────────────────────────────────────
# Results View
# ─────────────────────────────────────────────────────────────
def render_results(result: RecommendationResponse, meta: Dict[str, Any]) -> None:
    # Top profile bar
    name = st.session_state.user_name
    ip = meta.get("insurance_policy", "")

    hc1, hc2, hc3 = st.columns([1, 5, 1])
    with hc1:
        if st.session_state.profile_pic_bytes:
            st.image(st.session_state.profile_pic_bytes, width=60)
        else:
            st.markdown("<div style='font-size:42px;'>👤</div>", unsafe_allow_html=True)
    with hc2:
        p = result.user_profile
        st.markdown(f"### {name}")
        st.caption(
            f"Age {p.age}  ·  ₹{p.income:,.0f}/yr  ·  {ip}  ·  "
            f"{p.life_stage.replace('_',' ').title()}  ·  "
            f"{p.dependents} Dependent{'s' if p.dependents != 1 else ''}"
        )
    with hc3:
        if st.button("✏️ Edit Profile", key="edit_btn"):
            st.session_state.result = None
            st.session_state.user_payload = None
            st.rerun()

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⚡ Risk Analysis",
        "🎲 Scenario Simulation",
        "📊 Policy Evaluation",
        "🏆 Final Recommendation",
        "🔍 Critic Insights",
        "🔗 Pipeline Trace",
    ])

    with tab1:
        render_risk_analysis(result)
    with tab2:
        render_scenario_simulation(result)
    with tab3:
        render_policy_evaluation(result)
    with tab4:
        render_final_recommendation(result)
    with tab5:
        render_critic_insights(result)
    with tab6:
        render_agent_trace(result)


# ─────────────────────────────────────────────────────────────
# Tab 1 — Risk Analysis
# ─────────────────────────────────────────────────────────────
def render_risk_analysis(result: RecommendationResponse) -> None:
    st.subheader("⚡ Risk Analysis")
    st.caption(
        "Your risk score is calculated by the **Risk Analysis Agent** using a transparent "
        "rule-based model. Each factor contributes to the 0–100 risk score."
    )

    r_color = RISK_COLORS.get(result.risk_label, "#fff")
    m1, m2, m3 = st.columns(3)
    m1.metric("Risk Score", f"{result.risk_score:.1f} / 100")
    m2.metric("Risk Label", result.risk_label.upper())
    m3.metric("Confidence", f"{result.confidence_score:.1f}%")

    st.divider()
    st.markdown("#### 📐 Score Breakdown — How Each Factor Contributes")

    p = result.user_profile
    age_score = 15 if p.age < 30 else 20 if p.age < 50 else 12
    dep_score = min(p.dependents * 10, 30)
    lib_score = round(min(p.liability_ratio * 25, 25), 2)
    inc_score = 20 if p.income < 500000 else 12 if p.income < 1200000 else 6
    nw_score = 15 if p.net_worth <= 0 else 10 if p.net_worth < 1000000 else 5

    breakdown = pd.DataFrame({
        "Factor": ["Age", "Dependents", "Liability Ratio", "Income", "Net Worth"],
        "Your Score": [age_score, dep_score, lib_score, inc_score, nw_score],
        "Max Possible": [20, 30, 25, 20, 15],
        "Your Value": [
            f"Age {p.age}",
            f"{p.dependents} dependents",
            f"Ratio {p.liability_ratio:.2f}",
            f"₹{p.income:,.0f}",
            f"₹{p.net_worth:,.0f}",
        ],
    })

    # Grouped bar chart: your score vs max
    base = alt.Chart(breakdown)
    your_bars = base.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("Your Score:Q", scale=alt.Scale(domain=[0, 32])),
        y=alt.Y("Factor:N", sort=None, title=None),
        color=alt.value("#7c3aed"),
        tooltip=["Factor:N", "Your Score:Q", "Max Possible:Q", "Your Value:N"],
    )
    max_bars = base.mark_bar(
        cornerRadiusTopLeft=6, cornerRadiusTopRight=6, opacity=0.15,
    ).encode(
        x=alt.X("Max Possible:Q"),
        y=alt.Y("Factor:N", sort=None),
        color=alt.value("#a78bfa"),
    )
    score_labels = base.mark_text(dx=6, color="white", fontSize=13, fontWeight=600).encode(
        x="Your Score:Q",
        y=alt.Y("Factor:N", sort=None),
        text="Your Score:Q",
    )
    chart = (max_bars + your_bars + score_labels).properties(
        height=240, title="Risk Score by Factor (purple = your score, faint = maximum possible)"
    )
    st.altair_chart(chart, use_container_width=True)

    # Donut-style gauge via progress bar
    st.markdown("#### 🎯 Overall Risk Gauge")
    gauge_pct = result.risk_score / 100
    st.progress(float(min(gauge_pct, 1.0)), text=f"Risk Score {result.risk_score:.1f}/100 — **{result.risk_label.upper()}**")

    # Factor details table
    st.markdown("#### 📋 Factor Details")
    disp = breakdown[["Factor", "Your Score", "Max Possible", "Your Value"]].copy()
    disp["Your Score"] = disp["Your Score"].map(lambda x: f"{x:.1f}")
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # Formula
    with st.expander("📖 Risk Score Formula"):
        st.code(f"""
Risk Score = Age Score + Dependent Score + Liability Score + Income Score + Net Worth Score

  Age Score       = {age_score}   →  <30: 15 pts | 30–49: 20 pts | 50+: 12 pts
  Dependent Score = {dep_score}   →  dependents × 10 (max 30)
  Liability Score = {lib_score:.2f}  →  liability_ratio × 25 (max 25)
  Income Score    = {inc_score}   →  <5L: 20 pts | 5L–12L: 12 pts | >12L: 6 pts
  Net Worth Score = {nw_score}   →  ≤0: 15 pts | <10L: 10 pts | ≥10L: 5 pts
  ─────────────────────────────────────────────────────
  Total           = {result.risk_score:.2f} / 100  →  {result.risk_label.upper()}
        """, language=None)


# ─────────────────────────────────────────────────────────────
# Tab 2 — Scenario Simulation
# ─────────────────────────────────────────────────────────────
def render_scenario_simulation(result: RecommendationResponse) -> None:
    st.subheader("🎲 Scenario Simulation")
    st.caption(
        "The **Scenario Simulation Agent** uses **trained Logistic Regression** (probability) "
        "and **Linear Regression** (cost) models — learned from 3,000 synthetic actuarial samples — "
        "to predict personalised financial risk for your exact profile."
    )


    st.metric("💥 Total Expected Annual Loss", f"₹ {result.expected_loss:,.0f}",
              help="Weighted sum of expected losses across all simulated scenarios.")
    st.divider()

    for item in result.scenario_breakdown:
        m = SCENARIO_META.get(item.scenario_name, {
            "icon": "⚠️", "color": "#fff",
            "title": item.scenario_name, "desc": "", "animation": "⚪",
        })

        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.03);
            border:1px solid {m["color"]}30;border-left:4px solid {m["color"]};
            border-radius:16px;padding:24px;margin-bottom:8px;'>
            <div style='display:flex;align-items:center;gap:16px;margin-bottom:16px;'>
                <div style='font-size:44px;'>{m["icon"]}</div>
                <div>
                    <div style='color:{m["color"]};font-size:20px;font-weight:700;'>{m["title"]}</div>
                    <div style='color:rgba(255,255,255,0.45);font-size:13px;max-width:480px;'>{m["desc"]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Probability", f"{item.probability:.1%}")
        sc2.metric("Estimated Cost", f"₹{item.cost:,.0f}")
        sc3.metric("Expected Impact", f"₹{item.expected_impact:,.0f}")

        st.progress(
            float(min(item.probability, 1.0)),
            text=f"Likelihood of {m['title']}: {item.probability:.1%}",
        )

        with st.expander("🔢 Calculation Detail"):
            st.code(
                f"Expected Impact  =  Probability  ×  Cost\n"
                f"               =  {item.probability:.4f}  ×  ₹{item.cost:,.0f}\n"
                f"               =  ₹{item.expected_impact:,.0f}",
                language=None,
            )

        st.divider()

    # Summary comparison chart
    st.markdown("#### 📊 Scenario Impact Comparison")
    sdf = pd.DataFrame([{
        "Scenario": SCENARIO_META.get(s.scenario_name, {}).get("title", s.scenario_name),
        "Expected Impact (₹)": s.expected_impact,
        "Full Cost if it Happens (₹)": s.cost,
        "Probability (%)": round(s.probability * 100, 2),
    } for s in result.scenario_breakdown])

    bars = alt.Chart(sdf).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
        x=alt.X("Scenario:N", title=None),
        y=alt.Y("Expected Impact (₹):Q"),
        color=alt.Color(
            "Scenario:N",
            scale=alt.Scale(range=["#ef4444", "#f59e0b", "#8b5cf6"]),
            legend=None,
        ),
        tooltip=["Scenario:N", "Expected Impact (₹):Q", "Full Cost if it Happens (₹):Q", "Probability (%):Q"],
    ).properties(height=280)
    st.altair_chart(bars, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Tab 3 — Policy Evaluation
# ─────────────────────────────────────────────────────────────
def render_policy_evaluation(result: RecommendationResponse) -> None:
    st.subheader("📊 Policy Evaluation")
    st.caption(
        "The **Policy Evaluation Agent** scores all 15 policies across four dimensions: "
        "Utility, Suitability, Coverage Fit, and Affordability."
    )

    medals = ["🥇", "🥈", "🥉"]
    final_name = result.final_recommendation.policy.policy_name

    for i, rp in enumerate(result.top_policies):
        badge = medals[i] if i < 3 else f"#{i+1}"
        is_final = rp.policy.policy_name == final_name

        with st.expander(
            f"{badge} {rp.policy.policy_name}  ·  Total Score: {rp.total_score:.2f}"
            + ("  ✅ RECOMMENDED" if is_final else ""),
            expanded=(i == 0),
        ):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Coverage", f"₹{rp.policy.coverage:,.0f}")
            c2.metric("Annual Premium", f"₹{rp.policy.premium:,.0f}")
            c3.metric("Utility Score", f"{rp.utility_score:.1f}")
            c4.metric("AI Match", f"{rp.ai_score:.1f}")
            c5.metric("Prem/Inc", f"{rp.premium_ratio:.2%}")

            score_df = pd.DataFrame({
                "Dimension": ["Standard Utility", "Suitability", "Coverage", "Affordability", "AI/RL Match"],
                "Score": [rp.utility_score, rp.suitability_score, rp.coverage_score, rp.affordability_score, rp.ai_score],
            })

            score_chart = (
                alt.Chart(score_df)
                .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                .encode(
                    x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100])),
                    y=alt.Y("Dimension:N", sort=None, title=None),
                    color=alt.value("#7c3aed"),
                    tooltip=["Dimension:N", "Score:Q"],
                )
                .properties(height=160)
            )
            st.altair_chart(score_chart, use_container_width=True)

            st.caption(f"**Policy Type:** {rp.policy.policy_type.replace('_',' ').title()}")
            st.caption(f"**Coverage Gap:** ₹{rp.coverage_gap:,.0f}")
            st.caption(f"**Tradeoff:** {rp.tradeoff_summary}")
            st.markdown("**Why this policy:**")
            for pt in rp.explanation_points:
                st.markdown(f"&nbsp;&nbsp;• {pt}")

    # Comparison scatter chart
    if len(result.top_policies) > 1:
        st.divider()
        st.markdown("#### 📈 Coverage vs Premium Comparison")
        cdf = pd.DataFrame([{
            "Policy": rp.policy.policy_name,
            "Coverage (₹)": rp.policy.coverage,
            "Annual Premium (₹)": rp.policy.premium,
            "Utility Score": rp.utility_score,
        } for rp in result.top_policies])
        scatter = (
            alt.Chart(cdf)
            .mark_circle(size=200)
            .encode(
                x=alt.X("Annual Premium (₹):Q"),
                y=alt.Y("Coverage (₹):Q"),
                size=alt.Size("Utility Score:Q", scale=alt.Scale(range=[100, 600])),
                color=alt.Color("Policy:N", scale=alt.Scale(scheme="purples")),
                tooltip=["Policy:N", "Coverage (₹):Q", "Annual Premium (₹):Q", "Utility Score:Q"],
            )
            .properties(height=300, title="Bubble size = Utility Score")
        )
        st.altair_chart(scatter, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Tab 4 — Final Recommendation
# ─────────────────────────────────────────────────────────────
def render_final_recommendation(result: RecommendationResponse) -> None:
    fp = result.final_recommendation
    st.subheader("🏆 Final Recommendation")

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(59,130,246,0.15));
        border:1px solid rgba(124,58,237,0.4);border-radius:20px;
        padding:32px;text-align:center;margin-bottom:24px;'>
        <div style='font-size:50px;'>🏆</div>
        <div style='font-size:26px;font-weight:800;color:#fff;margin:12px 0 4px;'>{fp.policy.policy_name}</div>
        <div style='color:rgba(255,255,255,0.45);font-size:14px;'>
            {fp.policy.policy_type.replace("_"," ").title()}
              ·  Confidence {result.confidence_score:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Coverage", f"₹{fp.policy.coverage:,.0f}")
    c2.metric("Annual Premium", f"₹{fp.policy.premium:,.0f}")
    c3.metric("Premium/Income", f"{fp.premium_ratio:.2%}")
    c4.metric("Coverage Gap", f"₹{fp.coverage_gap:,.0f}")

    st.divider()
    st.success(f"🤖 **Agent Explanation:** {result.explanation}")
    st.caption(f"📝 Notes: {fp.policy.notes}")


# ─────────────────────────────────────────────────────────────
# Tab 5 — Critic Insights
# ─────────────────────────────────────────────────────────────
def render_critic_insights(result: RecommendationResponse) -> None:
    st.subheader("🔍 Critic Agent Insights")
    st.caption(
        "The **Critic Agent** independently validates the top-ranked policies, "
        "flags issues, and reranks when a safer alternative exists."
    )

    if not result.critic_issues:
        st.success("✅ Critic found no issues.")
        return

    for issue in result.critic_issues:
        low = issue.lower()
        if "no major issues" in low:
            st.success(f"✅ {issue}")
        elif any(kw in low for kw in ["underinsured", "overpriced", "mismatch"]):
            st.error(f"🚨 {issue}")
        else:
            st.warning(f"⚠️ {issue}")

    top_name = result.top_policies[0].policy.policy_name if result.top_policies else ""
    final_name = result.final_recommendation.policy.policy_name

    st.divider()
    if top_name and top_name != final_name:
        st.warning(
            f"🔄 **Reranked by Critic:** `{top_name}` was swapped for `{final_name}` "
            "due to detected issues."
        )
    else:
        st.info("✅ Critic accepted the top-ranked policy without reranking.")


# ─────────────────────────────────────────────────────────────
# Tab 6 — Pipeline Trace
# ─────────────────────────────────────────────────────────────
def render_agent_trace(result: RecommendationResponse) -> None:
    st.subheader("🔗 Agent Pipeline Trace")
    st.caption("Live execution log — every agent step with inputs, outputs, and timing.")

    if not result.agent_trace:
        st.warning("No trace data available.")
        return

    total_ms = sum(e.duration_ms for e in result.agent_trace)
    st.metric("⏱ Total Pipeline Execution Time", f"{total_ms:.1f} ms")
    st.divider()

    ICONS = {
        "UserProfilingAgent": "👤",
        "RiskAnalysisAgent": "⚡",
        "ScenarioSimulationAgent": "🎲",
        "PolicyEvaluationAgent": "📊",
        "CriticAgent": "🔍",
        "MemoryStore": "💾",
    }

    for i, entry in enumerate(result.agent_trace, 1):
        icon = ICONS.get(entry.agent_name, "🤖")
        with st.expander(
            f"Step {i}: {icon} {entry.agent_name}  —  {entry.duration_ms:.1f} ms",
            expanded=False,
        ):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**📥 Input Received:**")
                st.code(entry.input_summary, language=None)
            with c2:
                st.markdown("**📤 Output Produced:**")
                st.code(entry.output_summary, language=None)

    # Execution time chart
    st.divider()
    st.markdown("#### ⏱ Execution Time per Agent")
    tdf = pd.DataFrame([{
        "Agent": e.agent_name.replace("Agent", "").replace("Store", " Store"),
        "Duration (ms)": e.duration_ms,
    } for e in result.agent_trace])
    tchart = (
        alt.Chart(tdf)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("Duration (ms):Q"),
            y=alt.Y("Agent:N", sort=None, title=None),
            color=alt.Color("Duration (ms):Q", scale=alt.Scale(scheme="purples"), legend=None),
            tooltip=["Agent:N", "Duration (ms):Q"],
        )
        .properties(height=220)
    )
    st.altair_chart(tchart, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main() -> None:
    render_header()

    if st.session_state.result is None:
        render_profile_form()
    else:
        render_results(st.session_state.result, st.session_state.user_payload or {})


if __name__ == "__main__":
    main()
