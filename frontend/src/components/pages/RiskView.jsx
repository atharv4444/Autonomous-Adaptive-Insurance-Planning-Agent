/* ═══════════════════════════════════════════════════════════════════════════
   components/pages/RiskView.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Risk Simulator page — shows the transparent risk score breakdown:
   how each factor (age, dependents, liability, income, net worth, health)
   contributes to the final score, with a visual bar per factor.
   ═══════════════════════════════════════════════════════════════════════════ */

import { ShieldAlert } from 'lucide-react';

function RiskBar({ label, score, max, value }) {
  const pct = Math.min((score / max) * 100, 100);
  const color =
    pct >= 75 ? 'var(--color-danger)' :
    pct >= 45 ? 'var(--color-warning)' :
    'var(--color-success)';

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-2">
        <div>
          <p className="text-[12px] font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {label}
          </p>
          <p className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>{value}</p>
        </div>
        <div className="text-right">
          <p className="text-[18px] font-bold" style={{ color }}>{score}</p>
          <p className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
            / {max} pts
          </p>
        </div>
      </div>
      <div className="w-full h-2 rounded-full" style={{ backgroundColor: 'var(--color-border-soft)' }}>
        <div
          className="h-2 rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export default function RiskView({ metrics }) {
  // metrics is the array from extractMetrics — first item is Risk Score
  const riskMetric = metrics?.[0];
  const details = riskMetric?.details;

  if (!details) {
    return (
      <div className="card p-8 text-center" style={{ color: 'var(--color-text-muted)' }}>
        <ShieldAlert size={32} className="mx-auto mb-3 opacity-40" />
        <p className="text-sm">Submit a recommendation request to view the risk breakdown.</p>
      </div>
    );
  }

  const score = parseFloat(details.total);
  const riskLabel = riskMetric.sublabel;
  const labelColor =
    riskLabel === 'high' ? 'var(--color-danger)' :
    riskLabel === 'moderate' ? 'var(--color-warning)' :
    'var(--color-success)';

  return (
    <div className="space-y-5 max-w-2xl" id="risk-view">

      {/* ── Summary card ─────────────────────────────────────────── */}
      <div className="card p-6 flex items-center justify-between">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-wider mb-1"
            style={{ color: 'var(--color-text-muted)' }}>
            Overall Risk Score
          </p>
          <p className="text-[42px] font-bold leading-none" style={{ color: labelColor }}>
            {details.total}
          </p>
          <p className="text-[13px] font-semibold mt-1 capitalize" style={{ color: labelColor }}>
            {riskLabel} risk
          </p>
        </div>
        <div className="text-right">
          <p className="text-[11px] font-semibold uppercase tracking-wider mb-2"
            style={{ color: 'var(--color-text-muted)' }}>
            Formula
          </p>
          <p className="text-[12px]" style={{ color: 'var(--color-text-secondary)' }}>
            {details.formula}
          </p>
        </div>
      </div>

      {/* ── Per-factor breakdown ─────────────────────────────────── */}
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-wider mb-3"
          style={{ color: 'var(--color-text-muted)' }}>
          Score Breakdown
        </p>
        <div className="grid grid-cols-2 gap-3">
          {details.breakdown.map((item) => (
            <RiskBar
              key={item.label}
              label={item.label}
              score={item.score}
              max={item.max}
              value={item.value}
            />
          ))}
        </div>
      </div>

      {/* ── Factor legend ────────────────────────────────────────── */}
      <div className="card p-4">
        <p className="text-[11px] font-semibold uppercase tracking-wider mb-3"
          style={{ color: 'var(--color-text-muted)' }}>
          How Each Factor Is Scored
        </p>
        <div className="grid grid-cols-2 gap-x-8 gap-y-2">
          {[
            { factor: 'Age', rule: 'Under 30 → 10 pts · 30–49 → 15 pts · 50+ → 8 pts' },
            { factor: 'Dependents', rule: 'Dependents × 7, capped at 20 pts' },
            { factor: 'Liability Ratio', rule: 'Liabilities ÷ Income × 15 (not dependents)' },
            { factor: 'Income', rule: 'Under ₹5L → 15 pts · ₹5–12L → 9 pts · Above → 4 pts' },
            { factor: 'Net Worth', rule: '≤ 0 → 10 pts · Under ₹10L → 7 pts · Above → 3 pts' },
            { factor: 'Health', rule: 'Smoker / alcohol / severe conditions add up to 25 pts' },
          ].map(({ factor, rule }) => (
            <div key={factor} className="flex flex-col gap-0.5">
              <p className="text-[11px] font-semibold" style={{ color: 'var(--color-text-primary)' }}>{factor}</p>
              <p className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>{rule}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Interpretation ───────────────────────────────────────── */}
      <div className="card p-5">
        <p className="text-[11px] font-semibold uppercase tracking-wider mb-2"
          style={{ color: 'var(--color-text-muted)' }}>
          Interpretation
        </p>
        <p className="text-[13px]" style={{ color: 'var(--color-text-secondary)' }}>
          {score >= 60
            ? 'High risk profile. Multiple compounding factors detected. A comprehensive policy with broad coverage is strongly recommended.'
            : score >= 35
            ? 'Moderate risk profile. Some factors require attention. A balanced policy covering key risks is advisable.'
            : 'Low risk profile. Your financial and health indicators are stable. A basic or term policy may be sufficient.'}
        </p>
      </div>
    </div>
  );
}
