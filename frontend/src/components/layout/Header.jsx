/* ═══════════════════════════════════════════════════════════════════════════
   components/layout/Header.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Minimal page header. Shows the page title (serif) and a session status
   pill badge on the right.
   ═══════════════════════════════════════════════════════════════════════════ */

import { Circle } from 'lucide-react';

const PAGE_TITLES = {
  dashboard: 'Agent Dashboard',
  profile:   'User Profiling',
  risk:      'Risk Simulator',
  trace:     'Agent Trace',
  scenarios: 'Scenario Simulation',
};

export default function Header({ activePage, status, user, onLogout }) {
  const title = PAGE_TITLES[activePage] ?? 'Dashboard';

  /* Status dot color */
  const dotColor =
    status === 'success' ? 'var(--color-success)' :
    status === 'loading' ? 'var(--color-warning)' :
    status === 'error'   ? 'var(--color-danger)'  :
                           'var(--color-text-muted)';

  const statusLabel =
    status === 'success' ? 'Results Ready' :
    status === 'loading' ? 'Processing…' :
    status === 'error'   ? 'Error' :
                           'Awaiting Input';

  return (
    <header id="page-header" className="flex items-center justify-between mb-6">
      <div>
        <h2
          className="text-2xl font-semibold tracking-tight"
          style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-text-primary)' }}
        >
          {title}
        </h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>
          InsuraX — Autonomous Adaptive Insurance Planning
        </p>
      </div>

      {/* Session status pill & Auth */}
      <div className="flex items-center gap-4">
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-semibold"
          style={{
            border: '1px solid var(--color-border-soft)',
            color: 'var(--color-text-secondary)',
            backgroundColor: 'var(--color-surface)',
          }}
        >
          <Circle size={7} fill={dotColor} stroke={dotColor} />
          {statusLabel}
        </div>

        {user && (
          <div className="flex items-center gap-3">
            <span className="text-[12px] font-medium" style={{ color: 'var(--color-espresso)' }}>
              {user.email}
            </span>
            <button
              onClick={onLogout}
              className="text-[11px] font-bold uppercase tracking-wider hover:underline"
              style={{ color: 'var(--color-danger)' }}
            >
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
