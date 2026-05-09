/* ═══════════════════════════════════════════════════════════════════════════
   components/layout/Sidebar.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Dark espresso sidebar with navigation items and a user profile tag.
   Uses Lucide icons. Pure CSS transitions — no Framer Motion.
   ═══════════════════════════════════════════════════════════════════════════ */

import {
  LayoutDashboard,
  UserCircle,
  ShieldAlert,
  Activity,
  Workflow,
  ShieldCheck,
} from 'lucide-react';

/* Navigation items — each maps to a "page" key consumed by App.jsx */
const NAV_ITEMS = [
  { key: 'dashboard',  label: 'Dashboard',      icon: LayoutDashboard },
  { key: 'profile',    label: 'User Profiling',  icon: UserCircle },
  { key: 'risk',       label: 'Risk Simulator',  icon: ShieldAlert },
  { key: 'scenarios',  label: 'Scenarios',       icon: Activity },
  { key: 'critic',     label: 'Critic Agent',    icon: ShieldCheck },
  { key: 'trace',      label: 'Agent Trace',     icon: Workflow },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside
      id="sidebar"
      className="fixed top-0 left-0 h-screen w-[240px] flex flex-col justify-between py-6 px-4 z-50"
      style={{ backgroundColor: 'var(--color-espresso)' }}
    >
      {/* ── Brand ──────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center gap-3 px-2 mb-10">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold"
            style={{
              background: 'linear-gradient(135deg, var(--color-sand), var(--color-sand-dark))',
              color: 'var(--color-espresso)',
            }}
          >
            AI
          </div>
          <div>
            <h1
              className="text-[15px] font-bold tracking-tight"
              style={{ color: 'var(--color-cream)', fontFamily: 'var(--font-serif)' }}
            >
              InsuraX
            </h1>
            <p className="text-[10px] tracking-widest uppercase" style={{ color: 'var(--color-sand-light)' }}>
              Adaptive Agent
            </p>
          </div>
        </div>

        {/* ── Navigation Links ─────────────────────────────────────── */}
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map(({ key, label, icon: Icon }) => {
            const isActive = activePage === key;
            return (
              <button
                key={key}
                id={`nav-${key}`}
                onClick={() => onNavigate(key)}
                className="flex items-center gap-3 w-full text-left px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200 cursor-pointer"
                style={{
                  color: isActive ? 'var(--color-cream)' : 'var(--color-text-muted)',
                  backgroundColor: isActive ? 'var(--color-espresso-light)' : 'transparent',
                }}
              >
                <Icon size={17} strokeWidth={isActive ? 2 : 1.5} />
                {label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* ── User Tag ────────────────────────────────────────────────── */}
      <div
        className="flex items-center gap-3 px-3 py-3 rounded-xl"
        style={{ backgroundColor: 'var(--color-espresso-light)' }}
      >
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
          style={{
            background: 'linear-gradient(135deg, var(--color-sand), var(--color-sand-dark))',
            color: 'var(--color-espresso)',
          }}
        >
          U
        </div>
        <div>
          <p className="text-[12px] font-semibold" style={{ color: 'var(--color-cream)' }}>
            User Session
          </p>
          <p className="text-[10px]" style={{ color: 'var(--color-text-muted)' }}>
            Active
          </p>
        </div>
      </div>
    </aside>
  );
}
