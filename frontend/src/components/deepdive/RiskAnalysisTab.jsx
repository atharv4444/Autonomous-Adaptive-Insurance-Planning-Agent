import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, animate } from 'framer-motion';
import { buildRiskBreakdown, getRiskColor } from '../../adapters/responseAdapter';
import { getAgeExplanation, getDependentsExplanation, getLiabilityExplanation, getIncomeExplanation, getNetWorthExplanation, getHealthExplanation } from '../../utils/riskHelpers';
import { ShieldAlert, Target, Info, ChevronRight } from 'lucide-react';

/* ── Neon Maps ── */
const NEON = {
  low: { color: '#10B981', glow: 'rgba(16,185,129,0.3)', bg: 'rgba(16,185,129,0.06)', label: 'LOW RISK' },
  moderate: { color: '#F59E0B', glow: 'rgba(245,158,11,0.3)', bg: 'rgba(245,158,11,0.06)', label: 'MODERATE RISK' },
  high: { color: '#EF4444', glow: 'rgba(239,68,68,0.3)', bg: 'rgba(239,68,68,0.06)', label: 'HIGH RISK' },
};

/* ── Digital Counter ── */
const AnimatedCounter = ({ value, duration = 1.5 }) => {
  const ref = useRef(null);
  useEffect(() => {
    const controls = animate(0, value, {
      duration,
      ease: [0.4, 0, 0.2, 1],
      onUpdate: (v) => { if (ref.current) ref.current.textContent = v.toFixed(1); },
    });
    return () => controls.stop();
  }, [value, duration]);
  return <span ref={ref}>0.0</span>;
};

/* ── Sculptural Progress Ring ── */
const SculpturalRing = ({ value, max = 100, size = 140, strokeWidth = 8, gradientId, colors }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);

  return (
    <div className="relative animate-ring-breathe" style={{ width: size, height: size, '--ring-glow': `${colors[1]}60` }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={colors[0]} />
            <stop offset="100%" stopColor={colors[1]} />
          </linearGradient>
          <filter id={`glow-${gradientId}`}>
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth={strokeWidth} />
        <motion.circle
          cx={size/2} cy={size/2} r={radius} fill="none"
          stroke={`url(#${gradientId})`} strokeWidth={strokeWidth} strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference * (1 - pct) }}
          transition={{ duration: 1.8, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
          filter={`url(#glow-${gradientId})`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-black font-mono-num text-white animate-counter-tick" style={{ textShadow: `0 0 20px ${colors[1]}80` }}>
          <AnimatedCounter value={value} />
        </span>
        <span className="text-[10px] text-white/20 mt-1 font-medium tracking-widest">/ {max}</span>
      </div>
    </div>
  );
};

/* ── Multi-color Gauge Meter ── */
const GaugeMeter = ({ value, max }) => {
  const pct = max > 0 ? Math.min(value / max, 1) : 0;
  const totalBlocks = 10;
  const filledCount = Math.round(pct * totalBlocks);

  // Each block gets a color along green → yellow → orange → red
  const getBlockColor = (index, total) => {
    const ratio = index / (total - 1);
    if (ratio < 0.3) return { bg: '#10B981', glow: 'rgba(16,185,129,0.4)' };
    if (ratio < 0.5) return { bg: '#22D3EE', glow: 'rgba(34,211,238,0.4)' };
    if (ratio < 0.7) return { bg: '#F59E0B', glow: 'rgba(245,158,11,0.4)' };
    if (ratio < 0.85) return { bg: '#F97316', glow: 'rgba(249,115,22,0.4)' };
    return { bg: '#EF4444', glow: 'rgba(239,68,68,0.4)' };
  };

  return (
    <div className="flex gap-[5px] my-4">
      {Array.from({ length: totalBlocks }).map((_, i) => {
        const isFilled = i < filledCount;
        const colors = getBlockColor(i, totalBlocks);
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, scaleY: 0.3 }}
            animate={{ opacity: 1, scaleY: 1 }}
            transition={{ delay: 0.5 + i * 0.04, duration: 0.25 }}
            className="flex-1 h-[14px] rounded-[4px]"
            style={{
              background: isFilled ? colors.bg : 'rgba(255,255,255,0.04)',
              boxShadow: isFilled ? `0 0 8px ${colors.glow}` : 'none',
            }}
          />
        );
      })}
    </div>
  );
};

/* ── Factor Icon Map ── */
const FACTOR_ICONS = {
  'Age': '🎂',
  'Dependents': '👥',
  'Liability Ratio': '📊',
  'Income': '💰',
  'Net Worth': '🏦',
  'Health': '❤️',
};

/* ── Dimension Card (3x2 grid, larger) ── */
const DimensionCard = ({ b, index, insightDetail, fullExplanation }) => {
  const [expanded, setExpanded] = useState(false);
  const pct = b.max > 0 ? b.score / b.max : 0;

  let level = 'low';
  if (pct > 0.7) level = 'high';
  else if (pct > 0.4) level = 'moderate';

  const cTheme = NEON[level];
  const emoji = FACTOR_ICONS[b.factor] || '📋';

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 + index * 0.08, ease: [0.4, 0, 0.2, 1] }}
      className="risk-dimension-card group"
      style={{ '--dot-color': cTheme.color }}
    >
      <div className="p-6">
        {/* Header row */}
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lg"
              style={{ background: `${cTheme.color}10`, border: `1px solid ${cTheme.color}20` }}>
              {emoji}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[14px] font-extrabold text-white/75 uppercase tracking-wide">{b.factor}:</span>
              <span className="text-[12px] font-bold uppercase tracking-wider" style={{ color: cTheme.color }}>
                {cTheme.label}
              </span>
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-[18px] font-black font-mono-num" style={{ color: cTheme.color, textShadow: `0 0 10px ${cTheme.glow}` }}>
              {b.score.toFixed(1)}
            </span>
            <span className="text-[11px] text-white/20 font-mono-num">/ {b.max}</span>
          </div>
        </div>

        {/* Colored gauge meter */}
        <GaugeMeter value={b.score} max={b.max} />

        {/* Insight preview */}
        <p className="text-[13px] text-white/30 leading-relaxed line-clamp-2 min-h-[40px]">
          <span className="font-semibold text-white/50">Preview:</span>{' '}
          {insightDetail}
        </p>

        {/* "Click for Full AI Reasoning" button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-2 mt-4 py-3 rounded-xl
            border border-white/[0.04] hover:border-white/[0.08] bg-white/[0.01] hover:bg-white/[0.025]
            text-[12px] font-semibold text-white/25 hover:text-white/40 transition-all"
        >
          Click for Full AI Reasoning
          <motion.div animate={{ x: expanded ? 4 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronRight className="w-3.5 h-3.5" />
          </motion.div>
        </button>
      </div>

      {/* Expanded detail */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-1 border-t border-white/[0.03]">
              <div className="bg-black/30 rounded-xl p-4 border border-white/[0.02]">
                <div className="flex items-start gap-2.5">
                  <Info className="w-4 h-4 mt-0.5 text-indigo-400/50 flex-shrink-0" />
                  <div className="space-y-1.5">
                    {Array.isArray(fullExplanation) ? (
                      fullExplanation.map((exp, i) => (
                        <p key={i} className="text-[12px] text-white/35 leading-relaxed">{exp}</p>
                      ))
                    ) : (
                      <p className="text-[12px] text-white/35 leading-relaxed">{fullExplanation}</p>
                    )}
                  </div>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between text-[10px] text-white/15">
                <span className="font-mono">Input: {b.value}</span>
                <span className="font-mono">Contribution: {((b.score / (b.max || 1)) * 100).toFixed(0)}%</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

/* ═══════════════ MAIN COMPONENT ═══════════════ */
const RiskAnalysisTab = ({ result }) => {
  const profile = result.user_profile;
  const breakdown = buildRiskBreakdown(profile);

  const neon = NEON[result.risk_label] || NEON.moderate;

  const today = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  const explanations = {
    'Age': getAgeExplanation(profile.age),
    'Dependents': getDependentsExplanation(profile.dependents),
    'Liability Ratio': getLiabilityExplanation(profile.liability_ratio),
    'Income': getIncomeExplanation(profile.income),
    'Net Worth': getNetWorthExplanation(profile.net_worth),
    'Health': getHealthExplanation(profile),
  };

  const getInsightLine = (factor) => {
    const exp = explanations[factor];
    if (Array.isArray(exp)) return exp[0].replace(/\*\*/g, '').split('.')[0] + '.';
    return exp.split('.')[0] + '.';
  };

  // Confidence level label
  const confidenceLabel = result.confidence_score >= 80 ? 'HIGH CONFIDENCE' :
    result.confidence_score >= 50 ? 'MODERATE CONFIDENCE' : 'LOW CONFIDENCE';

  // Risk description text
  const riskDescription = result.risk_label === 'low'
    ? 'Comprehensive low-risk profile based on current multi-dimensional data.'
    : result.risk_label === 'moderate'
    ? 'Moderate risk profile — some factors require attention and monitoring.'
    : 'Elevated risk profile — multiple dimensions contribute to high risk exposure.';

  const confidenceDescription = result.confidence_score >= 80
    ? 'Strong cross-referencing and logic validation across all input vectors.'
    : result.confidence_score >= 50
    ? 'Moderate confidence in cross-referencing with room for validation improvement.'
    : 'Lower confidence — additional data or review may strengthen recommendations.';

  return (
    <div className="space-y-10 pb-10">

      {/* ── Header ── */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="flex items-start justify-between"
      >
        <div>
          <h2 className="text-[32px] font-black text-white tracking-tight mb-1">Risk Intelligence</h2>
          <p className="text-[13px] text-white/20 font-medium">
            Personal multi-dimensional risk profiling and Critic AI logic integrity validation.
          </p>
        </div>
        <div className="text-right flex-shrink-0 mt-1">
          <span className="text-xs text-white/20 font-medium">Risk Intelligence Dashboard</span>
          <span className="text-xs text-white/10 mx-2">|</span>
          <span className="text-xs text-white/15 font-mono">{today}</span>
        </div>
      </motion.div>

      {/* ── Top Section: Risk & AI Stats ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Overall Risk Score */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className="risk-hero-card group"
        >
          <div className="absolute top-0 right-0 w-64 h-64 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3 opacity-15"
            style={{ background: neon.glow }} />
          <div className="flex items-center justify-between relative z-10">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <ShieldAlert className="w-4 h-4 text-white/25" />
                <span className="text-[10px] font-bold uppercase tracking-[3px] text-white/25">Overall Computed Risk</span>
              </div>
              <h3 className="text-5xl font-black uppercase tracking-tight mb-2"
                style={{ color: neon.color, textShadow: `0 0 30px ${neon.glow}` }}>
                {result.risk_label}
              </h3>
              <p className="text-xs font-semibold text-white/40 mb-1">
                CLASSIFICATION: <span style={{ color: neon.color }}>{neon.label}</span>
              </p>
              <p className="text-[11px] text-white/20 max-w-[280px] leading-relaxed mt-2">
                {riskDescription}
              </p>
            </div>
            <div className="flex-shrink-0" style={{ '--ring-glow': neon.glow }}>
              <SculpturalRing
                value={result.risk_score} max={100} size={140} strokeWidth={8}
                gradientId="grad-risk"
                colors={result.risk_label === 'low' ? ['#059669', '#10B981'] : result.risk_label === 'moderate' ? ['#B45309', '#F59E0B'] : ['#991B1B', '#EF4444']}
              />
            </div>
          </div>
        </motion.div>

        {/* AI Confidence */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="risk-hero-card"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3 opacity-20" />
          <div className="flex items-center justify-between relative z-10">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-4 h-4 text-indigo-300/25" />
                <span className="text-[10px] font-bold uppercase tracking-[3px] text-indigo-300/25">Critic AI Logic Validation</span>
              </div>
              <h3 className="text-5xl font-black text-white tracking-tight mb-2" style={{ textShadow: '0 0 30px rgba(129,140,248,0.3)' }}>
                Critic AI
              </h3>
              <p className="text-xs font-semibold text-white/40 mb-1">
                INTEGRITY: <span className="text-indigo-400">{confidenceLabel}</span>
              </p>
              <p className="text-[11px] text-white/20 max-w-[280px] leading-relaxed mt-2">
                {confidenceDescription}
              </p>
            </div>
            <div className="flex-shrink-0" style={{ '--ring-glow': 'rgba(129,140,248,0.3)' }}>
              <SculpturalRing
                value={result.confidence_score} max={100} size={140} strokeWidth={8}
                gradientId="grad-ai" colors={['#4F46E5', '#818CF8']}
              />
            </div>
          </div>
        </motion.div>
      </div>

      {/* ── Dimensional Analysis Grid ── */}
      <div>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-6"
        >
          <h3 className="text-xl font-black text-white/90 mb-1">Dimensional Analysis</h3>
          <p className="text-[13px] text-white/20">
            Detailed Dimensional Risk Breakdown.{' '}
            <span className="text-white/12">Click any parameter to expand full AI reasoning.</span>
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {breakdown.map((b, i) => (
            <DimensionCard
              key={b.factor}
              b={b}
              index={i}
              insightDetail={getInsightLine(b.factor)}
              fullExplanation={explanations[b.factor]}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default RiskAnalysisTab;
