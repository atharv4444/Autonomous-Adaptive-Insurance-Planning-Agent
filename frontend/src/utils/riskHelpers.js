/**
 * Risk score explanation helpers — mirrors the display logic in the Streamlit UI.
 * These are for UI explanations ONLY — they don't recompute any backend values.
 */

export function getAgeExplanation(age) {
  if (age < 30) return 'Younger individuals (<30) have a lower risk of severe medical emergencies but may have less stability, leading to a moderate score (10 pts).';
  if (age < 50) return 'Middle-aged individuals (30-49) face increasing family responsibilities and rising health risks, leading to the highest score (15 pts).';
  return 'Older individuals (50+) face higher health risks, but often have fewer dependents or lower income-loss impact, leading to a lower risk score (8 pts).';
}

export function getDependentsExplanation(deps) {
  if (deps === 0) return 'With 0 dependents, you have minimal financial liability towards others, keeping your dependent risk score at 0.';
  return `With ${deps} dependent(s), you carry a higher financial responsibility in case of income loss or emergencies. Each dependent adds 7 points (max 20).`;
}

export function getLiabilityExplanation(ratio) {
  if (ratio === 0) return 'You have no significant liabilities (loans/debt), meaning you face 0 risk from debt obligations.';
  if (ratio < 0.3) return 'Your liability ratio is low. A smaller portion of your income goes towards debt, so the risk score is relatively low.';
  if (ratio < 0.6) return 'Your liability ratio is moderate. A significant portion of your income is committed to debt, leading to a moderate score.';
  return 'Your liability ratio is high. A large portion of your income goes to debt, making you vulnerable to income loss, leading to a high score.';
}

export function getIncomeExplanation(income) {
  if (income < 500000) return 'An income below ₹5,00,000 leaves little buffer for sudden large expenses, representing the highest risk score (15 pts).';
  if (income < 1200000) return 'A moderate income between ₹5L-12L provides some safety net, but still limits capacity for major emergencies (9 pts).';
  return 'An income above ₹12,00,000 provides a strong safety net for emergencies, reducing financial risk significantly (4 pts).';
}

export function getNetWorthExplanation(nw) {
  if (nw <= 0) return 'Your net worth is zero or negative. You have no assets to fall back on in emergencies, representing the highest risk (10 pts).';
  if (nw < 1000000) return 'Your net worth is under ₹10 Lakhs. You have some cushion, but a major event could wipe it out (7 pts).';
  return 'Your net worth is above ₹10 Lakhs. You have significant assets to cushion financial hits, reducing your risk score (3 pts).';
}

export function getHealthExplanation(profile) {
  const parts = [];
  if (profile.is_smoker) {
    parts.push('**Smoking (+10 pts):** Tobacco use is the single largest modifiable health risk factor. Smokers face 2-4x higher risk of heart disease.');
  } else {
    parts.push('**Smoking (+0 pts):** You are a non-smoker, which significantly reduces your baseline health risk.');
  }

  const alcoholDesc = {
    none: '**Alcohol (+0 pts):** No alcohol consumption — no additional risk.',
    occasional: '**Alcohol (+2 pts):** Occasional drinking adds a small health risk factor.',
    moderate: '**Alcohol (+5 pts):** Moderate alcohol consumption increases risk of liver-related diseases.',
    heavy: '**Alcohol (+8 pts):** Heavy alcohol consumption significantly increases the likelihood of liver disease and chronic health issues.',
  };
  parts.push(alcoholDesc[profile.alcohol_consumption] || alcoholDesc.none);

  if (profile.has_severe_health_issues) {
    parts.push('**Pre-existing Conditions (+7 pts):** Severe conditions sharply increase both the probability and cost of future medical events.');
  } else {
    parts.push('**Pre-existing Conditions (+0 pts):** No severe conditions reported — this keeps your health risk contribution low.');
  }

  return parts;
}
