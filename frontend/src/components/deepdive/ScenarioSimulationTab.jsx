import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Stethoscope, Car, Briefcase, ChevronDown, ChevronRight } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';
import { adaptScenario } from '../../adapters/responseAdapter';

const ICON_MAP = { Stethoscope, Car, Briefcase };

/* ═══════════════════════════════════════════
   ANIMATED SCENARIO VISUALS
   Abstract SVG animations for each scenario
   ═══════════════════════════════════════════ */

/* ── EKG / Heartbeat Line ── */
const EKGAnimation = () => (
  <div className="scenario-visual scenario-visual-medical">
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
      {/* Pulsing heart glow */}
      <motion.div
        className="absolute w-16 h-16 rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(239,68,68,0.15), transparent 70%)' }}
        animate={{ scale: [1, 1.4, 1], opacity: [0.4, 0.8, 0.4] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
      />
      {/* EKG line */}
      <svg viewBox="0 0 400 100" className="w-full h-full absolute" preserveAspectRatio="none">
        <defs>
          <linearGradient id="ekg-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#EF4444" stopOpacity="0" />
            <stop offset="30%" stopColor="#EF4444" stopOpacity="0.8" />
            <stop offset="70%" stopColor="#EF4444" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#EF4444" stopOpacity="0" />
          </linearGradient>
          <filter id="ekg-glow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
        <motion.path
          d="M 0,50 L 60,50 L 80,50 L 100,50 L 120,20 L 140,80 L 155,10 L 170,90 L 185,50 L 200,50 L 220,50 L 240,50 L 260,50 L 280,20 L 300,80 L 315,10 L 330,90 L 345,50 L 360,50 L 400,50"
          fill="none"
          stroke="url(#ekg-grad)"
          strokeWidth="2"
          filter="url(#ekg-glow)"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: [0, 1], opacity: 1 }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'linear' }}
        />
      </svg>
      {/* Grid lines */}
      <svg viewBox="0 0 400 100" className="w-full h-full absolute opacity-5">
        {Array.from({ length: 20 }).map((_, i) => (
          <line key={`v${i}`} x1={i * 20} y1="0" x2={i * 20} y2="100" stroke="white" strokeWidth="0.5" />
        ))}
        {Array.from({ length: 5 }).map((_, i) => (
          <line key={`h${i}`} x1="0" y1={i * 20 + 10} x2="400" y2={i * 20 + 10} stroke="white" strokeWidth="0.5" />
        ))}
      </svg>
    </div>
    <SimLabel text="EKG SIMULATION ACTIVE" color="#EF4444" />
  </div>
);

/* ── Crash / Impact Rings ── */
const CrashAnimation = () => (
  <div className="scenario-visual scenario-visual-accident">
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
      {/* Impact rings */}
      {[0, 0.6, 1.2].map((delay, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full border"
          style={{ borderColor: `rgba(245,158,11,${0.3 - i * 0.08})` }}
          initial={{ width: 10, height: 10, opacity: 0.8 }}
          animate={{
            width: [10, 180],
            height: [10, 180],
            opacity: [0.6, 0],
            borderWidth: [3, 0.5],
          }}
          transition={{ duration: 2, delay, repeat: Infinity, ease: 'easeOut' }}
        />
      ))}
      {/* Center flash */}
      <motion.div
        className="absolute w-4 h-4 rounded-full"
        style={{ background: '#F59E0B', boxShadow: '0 0 20px rgba(245,158,11,0.5)' }}
        animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
      {/* Flying debris particles */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i / 8) * Math.PI * 2;
        return (
          <motion.div
            key={`p${i}`}
            className="absolute w-1 h-1 rounded-full bg-amber-400"
            style={{ left: '50%', top: '50%' }}
            animate={{
              x: [0, Math.cos(angle) * 60],
              y: [0, Math.sin(angle) * 40],
              opacity: [0.8, 0],
              scale: [1, 0.3],
            }}
            transition={{ duration: 1.5, delay: i * 0.1, repeat: Infinity, ease: 'easeOut' }}
          />
        );
      })}
      {/* Skid marks */}
      <svg viewBox="0 0 400 100" className="w-full h-full absolute opacity-10">
        <motion.line x1="50" y1="80" x2="350" y2="80" stroke="#F59E0B" strokeWidth="2" strokeDasharray="8 6"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
          transition={{ duration: 1.5, repeat: Infinity }} />
      </svg>
    </div>
    <SimLabel text="CRASH SIMULATION ACTIVE" color="#F59E0B" />
  </div>
);

/* ── Cash Flow / Declining Graph ── */
const CashFlowAnimation = () => (
  <div className="scenario-visual scenario-visual-income">
    <div className="absolute inset-0 flex items-end justify-center overflow-hidden px-6 pb-4">
      {/* Animated bar chart (declining) */}
      <div className="flex items-end gap-[6px] h-full w-full pt-8">
        {[85, 78, 72, 60, 52, 38, 30, 22, 15, 10, 6, 3].map((h, i) => (
          <motion.div
            key={i}
            className="flex-1 rounded-t-sm"
            style={{
              background: `linear-gradient(180deg, rgba(139,92,246,${0.3 + (h / 100) * 0.4}), rgba(139,92,246,0.05))`,
              boxShadow: h > 40 ? `0 0 6px rgba(139,92,246,0.2)` : 'none',
            }}
            initial={{ height: 0 }}
            animate={{ height: `${h}%` }}
            transition={{ duration: 0.6, delay: 0.8 + i * 0.08, ease: [0.4, 0, 0.2, 1] }}
          />
        ))}
      </div>
      {/* Declining trend line */}
      <svg viewBox="0 0 400 100" className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id="flow-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.1" />
          </linearGradient>
        </defs>
        <motion.path
          d="M 20,20 C 80,22 120,30 160,40 C 200,50 240,60 280,72 C 320,80 360,88 390,92"
          fill="none" stroke="url(#flow-grad)" strokeWidth="1.5" strokeDasharray="4 3"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
          transition={{ duration: 2, delay: 0.5, ease: [0.4, 0, 0.2, 1] }}
        />
      </svg>
      {/* Cash symbols floating down */}
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="absolute text-violet-400/15 text-xl font-bold pointer-events-none select-none"
          style={{ left: `${25 + i * 25}%` }}
          animate={{ y: ['-20%', '110%'], opacity: [0, 0.3, 0] }}
          transition={{ duration: 3, delay: i * 0.8, repeat: Infinity, ease: 'easeIn' }}
        >
          ₹
        </motion.span>
      ))}
    </div>
    <SimLabel text="CASH FLOW SIMULATION ACTIVE" color="#8B5CF6" />
  </div>
);

/* ── Simulation Label Badge ── */
const SimLabel = ({ text, color }) => (
  <div className="absolute top-3 left-3 flex items-center gap-2 z-10">
    <motion.div
      className="w-1.5 h-1.5 rounded-full"
      style={{ background: color, boxShadow: `0 0 6px ${color}` }}
      animate={{ opacity: [1, 0.3, 1] }}
      transition={{ duration: 1.5, repeat: Infinity }}
    />
    <span className="text-[9px] font-bold uppercase tracking-[2px]" style={{ color: `${color}90` }}>
      {text}
    </span>
  </div>
);

/* Map scenario names to their animation component */
const ANIMATION_MAP = {
  medical_emergency: EKGAnimation,
  accident: CrashAnimation,
  income_loss: CashFlowAnimation,
};

/* ═══════════════════════════════════════════
   MAIN COMPONENT
   ═══════════════════════════════════════════ */
const ScenarioSimulationTab = ({ result }) => {
  const [expandedIdx, setExpandedIdx] = useState(null);

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div>
          <h2 className="text-[32px] font-black text-white tracking-tight mb-1">Scenario Simulation</h2>
          <p className="text-sm text-white/20 font-medium">ML models &middot; 3,000 actuarial samples &middot; Personalised risk</p>
        </div>
        <div className="text-right flex-shrink-0 mt-1">
          <span className="text-xs text-white/20 font-medium">Monte Carlo Engine</span>
          <span className="text-xs text-white/10 mx-2">|</span>
          <span className="text-xs text-white/15 font-mono">
            {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </span>
        </div>
      </motion.div>

      {/* Total expected loss hero */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="scenario-hero-card"
      >
        <p className="text-[10px] text-white/20 uppercase tracking-[4px] mb-2 font-bold">Total Expected Annual Loss</p>
        <p className="text-5xl font-black font-mono-num gradient-text">{formatCurrency(result.expected_loss)}</p>
      </motion.div>

      {/* Scenario cards */}
      {result.scenario_breakdown.map((item, idx) => {
        const scenario = adaptScenario(item);
        const Icon = ICON_MAP[scenario.icon] || Briefcase;
        const isOpen = expandedIdx === idx;
        const AnimComponent = ANIMATION_MAP[item.scenario_name];

        return (
          <motion.div
            key={scenario.scenario_name}
            initial={{ opacity: 0, y: 25, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.2 + idx * 0.12, ease: [0.4, 0, 0.2, 1] }}
            className="scenario-card"
          >
            {/* Title row */}
            <div className="p-6 pb-0 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ background: `${scenario.color}10` }}>
                <Icon className="w-5 h-5" style={{ color: scenario.color, filter: `drop-shadow(0 0 6px ${scenario.color}40)` }} />
              </div>
              <div>
                <h4 className="text-lg font-bold text-white/80">{scenario.title}</h4>
                <p className="text-[12px] text-white/20">{scenario.description}</p>
              </div>
            </div>

            {/* Content: Animation + Stats */}
            <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-5">
              {/* Left — Animated visual */}
              <div className="relative">
                {AnimComponent && <AnimComponent />}
              </div>

              {/* Right — Stats + Bar */}
              <div className="flex flex-col justify-center">
                <div className="grid grid-cols-3 gap-3 mb-4">
                  {[
                    { l: 'Probability', v: `${(item.probability * 100).toFixed(1)}%` },
                    { l: 'Estimated Cost', v: formatCurrency(item.cost) },
                    { l: 'Expected Impact', v: formatCurrency(item.expected_impact) },
                  ].map((m) => (
                    <div key={m.l} className="stat-cell">
                      <p className="text-[9px] text-white/20 uppercase tracking-wider mb-1 font-bold">{m.l}</p>
                      <p className="text-lg font-bold font-mono-num text-white/80">{m.v}</p>
                    </div>
                  ))}
                </div>

                {/* Risk bar */}
                <div className="w-full h-2 rounded-full bg-white/[0.04] overflow-hidden"
                  style={{ boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.3)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(item.probability * 100, 100)}%` }}
                    transition={{ duration: 1, delay: 0.4 + idx * 0.1, ease: [0.4, 0, 0.2, 1] }}
                    className="h-full rounded-full"
                    style={{
                      background: `linear-gradient(90deg, ${scenario.color}, ${scenario.color}80)`,
                      boxShadow: `0 0 10px ${scenario.color}30`,
                    }}
                  />
                </div>

                {/* View reasoning button */}
                {item.reasons && item.reasons.length > 0 && (
                  <button
                    onClick={() => setExpandedIdx(isOpen ? null : idx)}
                    className="mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl
                      border border-white/[0.04] hover:border-white/[0.08] bg-white/[0.01] hover:bg-white/[0.02]
                      text-[12px] font-semibold text-white/25 hover:text-white/40 transition-all"
                  >
                    View Reasoning
                    <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
                      <ChevronDown className="w-3.5 h-3.5" />
                    </motion.div>
                  </button>
                )}
              </div>
            </div>

            {/* Expandable AI Reasoning */}
            <AnimatePresence>
              {isOpen && item.reasons && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25 }}
                  className="overflow-hidden"
                >
                  <div className="px-6 pb-6 border-t border-white/[0.03] pt-4">
                    <div className="flex items-center gap-2 mb-3">
                      <ChevronRight className="w-3.5 h-3.5 text-indigo-400/40" />
                      <span className="text-[10px] font-bold uppercase tracking-[2px] text-white/20">AI Reasoning</span>
                    </div>
                    <ul className="space-y-2.5 ml-5">
                      {item.reasons.map((r, ri) => (
                        <li key={ri} className="text-[12px] text-white/25 flex items-start gap-2.5 leading-relaxed">
                          <span className="text-indigo-400/40 text-[10px] mt-0.5 flex-shrink-0">▸</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
};

export default ScenarioSimulationTab;
