/**
 * Adapter layer: transforms backend RecommendationResponse into UI-ready structures.
 * DOES NOT recompute or modify any backend values — only reformats for rendering.
 */

const SCENARIO_META = {
  medical_emergency: {
    title: 'Medical Emergency',
    description: 'Sudden hospitalisation, surgery, or critical illness requiring a large immediate financial outlay.',
    icon: 'Stethoscope',
    color: '#ef4444',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-600',
  },
  accident: {
    title: 'Accident',
    description: 'Road accident or physical injury causing treatment costs and potential third-party liability.',
    icon: 'Car',
    color: '#f59e0b',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    textColor: 'text-amber-600',
  },
  income_loss: {
    title: 'Income Loss',
    description: 'Job loss or business disruption halting regular salary and EMI payment capacity.',
    icon: 'Briefcase',
    color: '#8b5cf6',
    bgColor: 'bg-violet-50',
    borderColor: 'border-violet-200',
    textColor: 'text-violet-600',
  },
};

const GOAL_LABELS = {
  family_protection: 'Family Protection',
  health_security: 'Health Security',
  wealth_protection: 'Wealth Protection',
  tax_savings: 'Tax Savings',
  car_insurance: 'Car Insurance',
  home_insurance: 'Home Insurance',
};

/**
 * Build risk breakdown from user profile (replicates display logic from risk_analysis.py).
 * These scores are for DISPLAY only — the actual risk_score comes from the backend.
 */
export function buildRiskBreakdown(profile) {
  const ageScore = profile.age < 30 ? 10 : profile.age < 50 ? 15 : 8;
  const depScore = Math.min(profile.dependents * 7, 20);
  const libScore = Math.round(Math.min(profile.liability_ratio * 15, 15) * 100) / 100;
  const incScore = profile.income < 500000 ? 15 : profile.income < 1200000 ? 9 : 4;
  const nwScore = profile.net_worth <= 0 ? 10 : profile.net_worth < 1000000 ? 7 : 3;
  const healthScore = profile.health_risk_score;

  return [
    { factor: 'Age', score: ageScore, max: 15, value: `Age ${profile.age}` },
    { factor: 'Dependents', score: depScore, max: 20, value: `${profile.dependents} dependents` },
    { factor: 'Liability Ratio', score: libScore, max: 15, value: `Ratio ${profile.liability_ratio.toFixed(2)}` },
    { factor: 'Income', score: incScore, max: 15, value: `₹${profile.income.toLocaleString('en-IN')}` },
    { factor: 'Net Worth', score: nwScore, max: 10, value: `₹${profile.net_worth.toLocaleString('en-IN')}` },
    { factor: 'Health', score: healthScore, max: 25, value: buildHealthLabel(profile) },
  ];
}

function buildHealthLabel(profile) {
  const parts = [];
  if (profile.is_smoker) parts.push('Smoker');
  if (profile.alcohol_consumption !== 'none') parts.push(`${capitalize(profile.alcohol_consumption)} alcohol`);
  if (profile.has_severe_health_issues) parts.push('Severe condition');
  return parts.length > 0 ? parts.join(', ') : 'Healthy';
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/**
 * Adapt a scenario breakdown item for display.
 */
export function adaptScenario(item) {
  const meta = SCENARIO_META[item.scenario_name] || {
    title: item.scenario_name,
    description: '',
    icon: 'AlertTriangle',
    color: '#64748b',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    textColor: 'text-gray-600',
  };
  return { ...item, ...meta };
}

/**
 * Get a human-readable label for insurance goals.
 */
export function getGoalLabel(goal) {
  return GOAL_LABELS[goal] || goal;
}

/**
 * Get the life stage label.
 */
export function getLifeStageLabel(stage) {
  return stage ? stage.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '';
}

/**
 * Get the policy type label.
 */
export function getPolicyTypeLabel(type) {
  return type ? type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '';
}

/**
 * Map risk label to color.
 */
export function getRiskColor(label) {
  const map = { low: '#22c55e', moderate: '#f59e0b', high: '#ef4444' };
  return map[label] || '#64748b';
}

export function getRiskBgClass(label) {
  const map = { low: 'bg-green-50 text-green-700 border-green-200', moderate: 'bg-amber-50 text-amber-700 border-amber-200', high: 'bg-red-50 text-red-700 border-red-200' };
  return map[label] || 'bg-gray-50 text-gray-700 border-gray-200';
}
