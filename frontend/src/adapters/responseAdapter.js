/* ═══════════════════════════════════════════════════════════════════════════
   adapters/responseAdapter.js — Backend → Frontend Transformer
   ═══════════════════════════════════════════════════════════════════════════
   Transforms the monolithic RecommendationResponse from FastAPI into
   clean, component-ready data objects. Each function returns exactly
   what a specific component needs — nothing more.
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Format a number as Indian ₹ currency string.
 * @param {number} value
 * @returns {string} e.g. "₹8,00,000"
 */
export function formatCurrency(value) {
  if (value == null) return '₹0';
  return '₹' + Number(value).toLocaleString('en-IN');
}

/**
 * Extract the 4 headline metric cards from the response.
 * @param {object} res — full RecommendationResponse
 * @returns {Array<{label, value, sublabel, variant}>}
 */
export function extractMetrics(res) {
  if (!res) return [];

  const p = res.user_profile;
  let riskDetails = null;
  if (p) {
    const ageScore = p.age < 30 ? 10 : p.age < 50 ? 15 : 8;
    const depScore = Math.min(p.dependents * 7, 20);
    const libScore = Math.min((p.liability_ratio || 0) * 15, 15).toFixed(2);
    const incScore = p.income < 500000 ? 15 : p.income < 1200000 ? 9 : 4;
    const nwScore = p.net_worth <= 0 ? 10 : p.net_worth < 1000000 ? 7 : 3;
    const healthScore = (p.health_risk_score || 0).toFixed(1);
    
    riskDetails = {
      formula: "Age + Dependents + Liability Ratio + Income + Net Worth + Health",
      breakdown: [
        { label: "Age", score: ageScore, max: 15, value: p.age },
        { label: "Dependents", score: depScore, max: 20, value: p.dependents },
        { label: "Liability Ratio", score: libScore, max: 15, value: `Liabilities ÷ Income = ${(p.liability_ratio || 0).toFixed(2)}` },
        { label: "Income", score: incScore, max: 15, value: formatCurrency(p.income) },
        { label: "Net Worth", score: nwScore, max: 10, value: formatCurrency(p.net_worth) },
        { label: "Health", score: healthScore, max: 25, value: "Profile based" }
      ],
      total: res.risk_score?.toFixed(1)
    };
  }

  return [
    {
      label: 'Risk Score',
      value: res.risk_score?.toFixed(1) ?? '—',
      sublabel: res.risk_label ?? 'unknown',
      variant: res.risk_label ?? 'low',
      details: riskDetails
    },
    {
      label: 'Expected Loss',
      value: formatCurrency(res.expected_loss),
      sublabel: 'Annual estimate',
      variant: 'neutral',
    },
    {
      label: 'Suggested Premium',
      value: formatCurrency(res.final_recommendation?.policy?.premium),
      sublabel: res.final_recommendation?.policy?.policy_type?.replace(/_/g, ' ') ?? '',
      variant: 'neutral',
    },
    {
      label: 'AI Confidence',
      value: (res.confidence_score ?? 0).toFixed(0) + '%',
      sublabel: res.critic_issues?.length > 0 ? `${res.critic_issues.length} issue(s)` : 'No issues',
      variant: (res.confidence_score ?? 0) >= 80 ? 'success' : (res.confidence_score ?? 0) >= 50 ? 'warning' : 'danger',
    },
  ];
}

/**
 * Extract ranked policies for the main table.
 * @param {object} res — full RecommendationResponse
 * @returns {Array<object>}
 */
export function extractPolicies(res) {
  if (!res?.top_policies) return [];
  return res.top_policies.map((rp) => ({
    name: rp.policy.policy_name,
    type: rp.policy.policy_type?.replace(/_/g, ' '),
    coverage: formatCurrency(rp.policy.coverage),
    premium: formatCurrency(rp.policy.premium),
    utilityScore: rp.utility_score?.toFixed(2),
    totalScore: rp.total_score?.toFixed(2),
    aiScore: rp.ai_score?.toFixed(2),
    tradeoff: rp.tradeoff_summary,
    explanationPoints: rp.explanation_points ?? [],
    // Raw object for detail modals
    _raw: rp,
  }));
}

/**
 * Extract user profile summary.
 * @param {object} res — full RecommendationResponse
 * @returns {object}
 */
export function extractProfile(res) {
  if (!res?.user_profile) return null;
  const p = res.user_profile;
  return {
    age: p.age,
    income: formatCurrency(p.income),
    dependents: p.dependents,
    netWorth: formatCurrency(p.net_worth),
    lifeStage: p.life_stage?.replace(/_/g, ' '),
    affordability: p.affordability_band,
    goal: p.insurance_goal?.replace(/_/g, ' '),
    riskLabel: res.risk_label,
    healthRiskScore: p.health_risk_score?.toFixed(1),
  };
}

/**
 * Extract agent trace for the pipeline view.
 * @param {object} res — full RecommendationResponse
 * @returns {Array<{agent, input, output, durationMs}>}
 */
export function extractTrace(res) {
  if (!res?.agent_trace) return [];
  return res.agent_trace.map((t) => ({
    agent: t.agent_name,
    input: t.input_summary,
    output: t.output_summary,
    durationMs: t.duration_ms?.toFixed(0),
  }));
}

/**
 * Extract scenario breakdown for the risk simulator.
 * @param {object} res — full RecommendationResponse
 * @returns {Array<{name, probability, cost, impact, reasons}>}
 */
export function extractScenarios(res) {
  if (!res?.scenario_breakdown) return [];
  return res.scenario_breakdown.map((s) => ({
    name: s.scenario_name?.replace(/_/g, ' '),
    probability: (s.probability * 100).toFixed(1) + '%',
    cost: formatCurrency(s.cost),
    impact: formatCurrency(s.expected_impact),
    reasons: s.reasons ?? [],
  }));
}
