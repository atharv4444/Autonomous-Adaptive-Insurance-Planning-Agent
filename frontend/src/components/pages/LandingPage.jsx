/* ═══════════════════════════════════════════════════════════════════════════
   components/pages/LandingPage.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Public landing page shown before login.
   Sections: Navbar → Hero → Features → How It Works → CTA Footer
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState } from 'react';
import {
  ShieldCheck, Brain, Activity, FileText,
  ChevronRight, ArrowRight, Star, Zap, Lock
} from 'lucide-react';
import LoginView from './LoginView';

/* ── Feature cards data ─────────────────────────────────────────────────── */
const FEATURES = [
  {
    icon: Brain,
    color: 'var(--color-info)',
    bg: '#EEF4FB',
    title: 'Multi-Agent Pipeline',
    desc: 'Seven specialised agents — profiling, risk, simulation, evaluation, critic, compliance, and memory — work in sequence to produce a transparent recommendation.',
  },
  {
    icon: ShieldCheck,
    color: 'var(--color-success)',
    bg: '#EAF5EE',
    title: 'Critic & Validation',
    desc: 'A dedicated critic agent reviews every recommendation for underinsurance, premium pressure, and risk mismatch before it reaches you.',
  },
  {
    icon: Activity,
    color: 'var(--color-warning)',
    bg: '#FEF6EC',
    title: 'Scenario Simulation',
    desc: 'Medical emergency, accident, and income loss scenarios are simulated to compute your real expected annual loss — not just a guess.',
  },
  {
    icon: FileText,
    color: 'var(--color-sand-dark)',
    bg: '#F7F2EA',
    title: 'Full Explainability',
    desc: 'Every score, every decision, and every agent step is exposed in the dashboard trace — no black boxes.',
  },
  {
    icon: Zap,
    color: 'var(--color-danger)',
    bg: '#FCEEED',
    title: 'Adaptive Learning',
    desc: 'The system updates its internal model weights from critic feedback in real time, improving with every run.',
  },
  {
    icon: Lock,
    color: 'var(--color-espresso)',
    bg: '#F0EDEC',
    title: 'IRDAI-Style Compliance',
    desc: 'Deterministic compliance checks modelled on IRDAI guidelines are run on every recommendation before delivery.',
  },
];

/* ── Pipeline steps ─────────────────────────────────────────────────────── */
const STEPS = [
  { num: '01', label: 'Profile', desc: 'Enter your age, income, dependents, and health details.' },
  { num: '02', label: 'Risk Score', desc: 'A transparent rule-based score is computed from your profile.' },
  { num: '03', label: 'Simulation', desc: 'Three loss scenarios are simulated to estimate your annual exposure.' },
  { num: '04', label: 'Evaluation', desc: 'Policies are ranked by suitability, affordability, and utility.' },
  { num: '05', label: 'Critique', desc: 'The critic agent validates the top pick and can trigger replanning.' },
  { num: '06', label: 'Recommendation', desc: 'You receive the best policy with a full explanation and trace.' },
];

export default function LandingPage({ onLogin }) {
  const [showLogin, setShowLogin] = useState(false);

  if (showLogin) {
    return <LoginView onLogin={onLogin} />;
  }

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: 'var(--color-cream)', fontFamily: 'var(--font-sans)' }}
    >
      {/* ══════════════════════════════════════════════════════════════
          NAVBAR
      ══════════════════════════════════════════════════════════════ */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4"
        style={{
          backgroundColor: 'rgba(248, 246, 240, 0.92)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid var(--color-border-soft)',
        }}
      >
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold"
            style={{
              background: 'linear-gradient(135deg, var(--color-espresso), var(--color-espresso-light))',
              color: 'var(--color-sand)',
            }}
          >
            AI
          </div>
          <div>
            <span
              className="text-[16px] font-bold tracking-tight"
              style={{ color: 'var(--color-espresso)', fontFamily: 'var(--font-serif)' }}
            >
              InsuraX
            </span>
            <span
              className="ml-2 text-[10px] font-semibold uppercase tracking-widest"
              style={{ color: 'var(--color-text-muted)' }}
            >
              Adaptive Agent
            </span>
          </div>
        </div>

        {/* Nav links */}
        <div className="hidden md:flex items-center gap-8">
          {['Features', 'How It Works'].map((item) => (
            <a
              key={item}
              href={`#${item.toLowerCase().replace(/ /g, '-')}`}
              className="text-[13px] font-medium transition-colors hover:opacity-70"
              style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}
            >
              {item}
            </a>
          ))}
        </div>

        {/* CTA */}
        <button
          onClick={() => setShowLogin(true)}
          className="btn-primary text-[13px]"
          style={{ padding: '8px 20px' }}
        >
          Sign In
          <ChevronRight size={14} />
        </button>
      </nav>

      {/* ══════════════════════════════════════════════════════════════
          HERO
      ══════════════════════════════════════════════════════════════ */}
      <section
        className="relative flex flex-col items-center justify-center text-center px-6 pt-40 pb-28"
        style={{ minHeight: '100vh' }}
      >
        {/* Background decoration */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(196,168,130,0.12) 0%, transparent 70%)',
          }}
        />

        {/* Badge */}
        <div
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-[11px] font-semibold uppercase tracking-widest mb-6"
          style={{
            backgroundColor: 'var(--color-cream-dark)',
            color: 'var(--color-espresso-muted)',
            border: '1px solid var(--color-border-soft)',
          }}
        >
          <Star size={10} fill="currentColor" />
          Academic Prototype · Multi-Agent AI
        </div>

        {/* Headline */}
        <h1
          className="text-[52px] md:text-[68px] font-bold leading-[1.08] tracking-tight mb-6 max-w-4xl"
          style={{ color: 'var(--color-espresso)', fontFamily: 'var(--font-serif)' }}
        >
          Insurance planning,{' '}
          <span style={{ color: 'var(--color-sand-dark)' }}>explained</span>{' '}
          by agents.
        </h1>

        {/* Subheadline */}
        <p
          className="text-[17px] leading-relaxed max-w-xl mb-10"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          InsuraX runs a transparent multi-agent pipeline — profiling, risk scoring,
          scenario simulation, policy evaluation, and critic validation — to give you
          a recommendation you can actually understand.
        </p>

        {/* CTAs */}
        <div className="flex items-center gap-4 flex-wrap justify-center">
          <button
            onClick={() => setShowLogin(true)}
            className="btn-primary flex items-center gap-2"
            style={{ padding: '13px 28px', fontSize: '15px' }}
          >
            Get Your Recommendation
            <ArrowRight size={16} />
          </button>
          <a
            href="#how-it-works"
            className="btn-soft flex items-center gap-2"
            style={{ padding: '13px 24px', fontSize: '14px', textDecoration: 'none' }}
          >
            See How It Works
          </a>
        </div>

        {/* Floating stat pills */}
        <div className="flex items-center gap-4 mt-14 flex-wrap justify-center">
          {[
            { label: '7 Agents', sub: 'in the pipeline' },
            { label: '3 Scenarios', sub: 'simulated per run' },
            { label: 'Full Trace', sub: 'every decision logged' },
            { label: 'IRDAI-style', sub: 'compliance checks' },
          ].map(({ label, sub }) => (
            <div
              key={label}
              className="px-5 py-3 rounded-2xl text-center"
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border-soft)',
                boxShadow: 'var(--shadow-card)',
              }}
            >
              <p className="text-[14px] font-bold" style={{ color: 'var(--color-espresso)' }}>{label}</p>
              <p className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>{sub}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          FEATURES
      ══════════════════════════════════════════════════════════════ */}
      <section
        id="features"
        className="px-6 py-24"
        style={{ backgroundColor: 'var(--color-cream-dark)' }}
      >
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p
              className="text-[11px] font-bold uppercase tracking-widest mb-3"
              style={{ color: 'var(--color-sand-dark)' }}
            >
              What's Inside
            </p>
            <h2
              className="text-[38px] font-bold"
              style={{ color: 'var(--color-espresso)', fontFamily: 'var(--font-serif)' }}
            >
              Built for transparency
            </h2>
            <p
              className="text-[15px] mt-3 max-w-lg mx-auto"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Every component of the recommendation pipeline is visible, auditable, and explainable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map(({ icon: Icon, color, bg, title, desc }) => (
              <div
                key={title}
                className="card p-6"
                style={{ backgroundColor: 'var(--color-surface)' }}
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                  style={{ backgroundColor: bg }}
                >
                  <Icon size={18} style={{ color }} />
                </div>
                <h3
                  className="text-[15px] font-semibold mb-2"
                  style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-text-primary)' }}
                >
                  {title}
                </h3>
                <p className="text-[13px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          HOW IT WORKS
      ══════════════════════════════════════════════════════════════ */}
      <section id="how-it-works" className="px-6 py-24">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <p
              className="text-[11px] font-bold uppercase tracking-widest mb-3"
              style={{ color: 'var(--color-sand-dark)' }}
            >
              The Pipeline
            </p>
            <h2
              className="text-[38px] font-bold"
              style={{ color: 'var(--color-espresso)', fontFamily: 'var(--font-serif)' }}
            >
              Six steps, zero guesswork
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {STEPS.map(({ num, label, desc }, i) => (
              <div
                key={num}
                className="card p-5 flex items-start gap-4"
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-[13px] font-bold"
                  style={{
                    background: 'linear-gradient(135deg, var(--color-espresso), var(--color-espresso-light))',
                    color: 'var(--color-sand)',
                  }}
                >
                  {num}
                </div>
                <div>
                  <p
                    className="text-[14px] font-semibold mb-1"
                    style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-serif)' }}
                  >
                    {label}
                  </p>
                  <p className="text-[12.5px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                    {desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          BOTTOM CTA
      ══════════════════════════════════════════════════════════════ */}
      <section
        className="px-6 py-24 text-center"
        style={{ backgroundColor: 'var(--color-espresso)' }}
      >
        <div className="max-w-2xl mx-auto">
          <div
            className="w-14 h-14 rounded-2xl mx-auto mb-6 flex items-center justify-center text-xl font-bold"
            style={{
              background: 'linear-gradient(135deg, var(--color-sand), var(--color-sand-dark))',
              color: 'var(--color-espresso)',
              fontFamily: 'var(--font-serif)',
            }}
          >
            AI
          </div>
          <h2
            className="text-[38px] font-bold mb-4"
            style={{ color: 'var(--color-cream)', fontFamily: 'var(--font-serif)' }}
          >
            Ready to see your recommendation?
          </h2>
          <p
            className="text-[15px] mb-10 leading-relaxed"
            style={{ color: 'var(--color-sand-light)' }}
          >
            Create a free account and run the full agent pipeline in under a minute.
          </p>
          <div className="flex items-center gap-4 justify-center flex-wrap">
            <button
              onClick={() => setShowLogin(true)}
              className="flex items-center gap-2 font-semibold rounded-xl transition-all hover:-translate-y-0.5"
              style={{
                padding: '13px 28px',
                fontSize: '15px',
                backgroundColor: 'var(--color-sand)',
                color: 'var(--color-espresso)',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(196,168,130,0.3)',
              }}
            >
              Get Started Free
              <ArrowRight size={16} />
            </button>
            <button
              onClick={() => setShowLogin(true)}
              className="flex items-center gap-2 font-medium rounded-xl transition-all hover:opacity-80"
              style={{
                padding: '13px 24px',
                fontSize: '14px',
                backgroundColor: 'transparent',
                color: 'var(--color-sand-light)',
                border: '1px solid rgba(196,168,130,0.3)',
                cursor: 'pointer',
              }}
            >
              Sign In
            </button>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          FOOTER
      ══════════════════════════════════════════════════════════════ */}
      <footer
        className="px-8 py-6 flex items-center justify-between flex-wrap gap-4"
        style={{
          backgroundColor: 'var(--color-charcoal)',
          borderTop: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <p className="text-[12px]" style={{ color: 'var(--color-text-muted)' }}>
          © 2026 InsuraX · Academic prototype · Not a licensed insurance advisor
        </p>
        <p className="text-[12px]" style={{ color: 'var(--color-text-muted)' }}>
          IRDAI Note: For academic use only. Real deployment requires regulatory review.
        </p>
      </footer>
    </div>
  );
}
