/* ═══════════════════════════════════════════════════════════════════════════
   components/dashboard/MetricCards.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Row of 4 metric cards: Risk Score, Expected Loss, Suggested Premium,
   AI Confidence. Each is a tactile .card with a colored top accent border.
   ═══════════════════════════════════════════════════════════════════════════ */

import { ShieldCheck, TrendingDown, Wallet, Brain } from 'lucide-react';

/* Icon mapping by index (matches the order from extractMetrics) */
const ICONS = [ShieldCheck, TrendingDown, Wallet, Brain];

/* Top accent colors */
const ACCENT_COLORS = [
  'var(--color-info)',
  'var(--color-danger)',
  'var(--color-sand-dark)',
  'var(--color-success)',
];

export default function MetricCards({ metrics }) {
  if (!metrics || metrics.length === 0) return null;

  return (
    <div className="grid grid-cols-4 gap-4 mb-6" id="metric-cards">
      {metrics.map((m, i) => {
        const Icon = ICONS[i] ?? ShieldCheck;
        return (
          <div
            key={m.label}
            className="card p-4 relative overflow-hidden"
            style={{ borderTop: `3px solid ${ACCENT_COLORS[i]}` }}
          >
            {/* Icon + Label */}
            <div className="flex items-center gap-2 mb-3">
              <Icon size={16} style={{ color: ACCENT_COLORS[i] }} />
              <span
                className="text-[11px] font-semibold uppercase tracking-wider"
                style={{ color: 'var(--color-text-muted)' }}
              >
                {m.label}
              </span>
            </div>

            {/* Value */}
            <p
              className="text-2xl font-bold tracking-tight"
              style={{ fontFamily: 'var(--font-sans)', color: 'var(--color-text-primary)' }}
            >
              {m.value}
            </p>

            {/* Sublabel / Badge */}
            <div className="mt-2">
              {m.variant !== 'neutral' ? (
                <span className={`badge badge-${m.variant}`}>
                  {m.sublabel}
                </span>
              ) : (
                <span className="text-[11px]" style={{ color: 'var(--color-text-secondary)' }}>
                  {m.sublabel}
                </span>
              )}
            </div>

            {/* Dropdown for Details */}
            {m.details && (
              <details className="mt-4 text-[11px]" style={{ color: 'var(--color-text-secondary)' }}>
                <summary className="cursor-pointer font-medium hover:text-[var(--color-info)] transition-colors">
                  View Formula & Calculation
                </summary>
                <div className="mt-2 p-2 rounded bg-[var(--color-cream-dark)] border border-[var(--color-border-soft)]">
                  <div className="mb-2">
                    <span className="font-semibold">Formula:</span> {m.details.formula}
                  </div>
                  <div className="space-y-1">
                    {m.details.breakdown.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="text-[10px]">{item.label} (Max {item.max}):</span>
                        <span className="font-medium text-[var(--color-text-primary)]">
                          {item.score} <span className="text-[9px] text-[var(--color-text-muted)]">({item.value})</span>
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-2 pt-1 border-t border-[var(--color-border-soft)] flex justify-between font-semibold text-[var(--color-text-primary)]">
                    <span>Total Risk Score:</span>
                    <span>{m.details.total}</span>
                  </div>
                </div>
              </details>
            )}
          </div>
        );
      })}
    </div>
  );
}
