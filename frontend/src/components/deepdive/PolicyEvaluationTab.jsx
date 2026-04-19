import { useState, useEffect, useRef } from 'react';
import { motion, animate } from 'framer-motion';
import { Trophy, Shield, IndianRupee, Zap, Brain, Percent, Filter, ArrowUpDown } from 'lucide-react';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { getPolicyTypeLabel } from '../../adapters/responseAdapter';

const SCORE_COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd'];

/* ── Animated score counter ── */
const ScoreCounter = ({ value, color }) => {
  const ref = useRef(null);
  useEffect(() => {
    const controls = animate(0, value, {
      duration: 1.2,
      ease: [0.4, 0, 0.2, 1],
      onUpdate: (v) => { if (ref.current) ref.current.textContent = v.toFixed(2); },
    });
    return () => controls.stop();
  }, [value]);
  return (
    <span ref={ref} className="text-2xl font-black font-mono-num"
      style={{ color, textShadow: `0 0 15px ${color}40` }}>
      0.00
    </span>
  );
};

/* ── Mini radial score ring ── */
const ScoreRing = ({ value, max = 100, size = 44, color }) => {
  const radius = (size - 4) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="3" />
        <motion.circle
          cx={size/2} cy={size/2} r={radius} fill="none"
          stroke={color} strokeWidth="3" strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference * (1 - pct) }}
          transition={{ duration: 1.2, delay: 0.3, ease: [0.4, 0, 0.2, 1] }}
          style={{ filter: `drop-shadow(0 0 4px ${color}60)` }}
        />
      </svg>
    </div>
  );
};

/* ── Metric Cell ── */
const MetricCell = ({ icon: Icon, label, value, color }) => (
  <div className="policy-metric-cell">
    <div className="w-8 h-8 rounded-lg flex items-center justify-center mb-1.5"
      style={{ background: `${color}12` }}>
      <Icon className="w-3.5 h-3.5" style={{ color, filter: `drop-shadow(0 0 4px ${color}50)` }} />
    </div>
    <p className="text-[9px] text-white/20 uppercase tracking-wider font-bold mb-0.5">{label}</p>
    <p className="text-sm font-bold font-mono-num text-white/70">{value}</p>
  </div>
);

/* ── Horizontal Bar with label ── */
const HBar = ({ label, value, max = 100, color, delay = 0 }) => (
  <div className="flex items-center gap-3 mb-2">
    <span className="text-[11px] text-white/25 w-16 text-right font-medium flex-shrink-0">{label}</span>
    <div className="flex-1 h-[10px] rounded-full bg-white/[0.03] overflow-hidden" style={{ boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.3)' }}>
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${Math.min((value / max) * 100, 100)}%` }}
        transition={{ duration: 0.8, delay, ease: [0.4, 0, 0.2, 1] }}
        className="h-full rounded-full"
        style={{ background: color, boxShadow: `0 0 8px ${color}30` }}
      />
    </div>
  </div>
);

/* ── Axis labels row ── */
const AxisLabels = () => (
  <div className="flex items-center gap-3 mb-3">
    <span className="w-16 flex-shrink-0" />
    <div className="flex-1 flex justify-between px-0.5">
      {[0, 25, 50, 75, 100].map((v) => (
        <span key={v} className="text-[9px] text-white/10 font-mono">{v}</span>
      ))}
    </div>
  </div>
);

/* ═══════════════════════════════════════════
   MAIN COMPONENT
   ═══════════════════════════════════════════ */
const PolicyEvaluationTab = ({ result }) => {
  const finalName = result.final_recommendation.policy.policy_name;
  const [sortBy, setSortBy] = useState('score');

  const sortedPolicies = [...result.top_policies].sort((a, b) => {
    if (sortBy === 'score') return b.total_score - a.total_score;
    if (sortBy === 'coverage') return b.policy.coverage - a.policy.coverage;
    if (sortBy === 'premium') return a.policy.premium - b.policy.premium;
    return b.total_score - a.total_score;
  });

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div>
          <h2 className="text-[32px] font-black text-white tracking-tight mb-1">Policy Evaluation</h2>
          <p className="text-sm text-white/20 font-medium">
            Utility &middot; Suitability &middot; Coverage &middot; Affordability &middot; AI/RL
          </p>
        </div>
        <div className="flex items-center gap-3 mt-1">
          {/* Sort control */}
          <div className="flex items-center gap-2">
            <ArrowUpDown className="w-3.5 h-3.5 text-white/20" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-xs font-semibold text-white/40 bg-white/[0.02] border border-white/[0.06] rounded-lg px-3 py-1.5 outline-none cursor-pointer appearance-none"
              style={{ minWidth: '90px' }}
            >
              <option value="score">Sort: Score</option>
              <option value="coverage">Sort: Coverage</option>
              <option value="premium">Sort: Premium</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Policy Cards */}
      {sortedPolicies.map((rp, i) => {
        const isFinal = rp.policy.policy_name === finalName;
        const premiumRatio = rp.premium_ratio || (rp.policy.premium / (result.user_profile?.income || 1));
        const scoreColor = SCORE_COLORS[i % SCORE_COLORS.length];

        return (
          <motion.div
            key={rp.policy.policy_name}
            initial={{ opacity: 0, y: 25, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.1 + i * 0.1, ease: [0.4, 0, 0.2, 1] }}
            className="policy-eval-card"
          >
            {/* ── Card Header ── */}
            <div className="px-7 py-5 flex items-center justify-between border-b border-white/[0.03]">
              <div className="flex items-center gap-4">
                <span className="text-xl font-black font-mono-num text-indigo-400/60">#{i + 1}</span>
                <div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-lg font-bold text-white/80">{rp.policy.policy_name}</span>
                    {isFinal && (
                      <span className="policy-best-badge">
                        <Trophy className="w-2.5 h-2.5" /> BEST
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-white/20">{getPolicyTypeLabel(rp.policy.policy_type)}</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <ScoreRing value={rp.total_score} max={100} size={44} color={scoreColor} />
                <ScoreCounter value={rp.total_score} color={scoreColor} />
              </div>
            </div>

            {/* ── Card Body ── */}
            <div className="p-7">
              {/* Metric cells row */}
              <div className="grid grid-cols-5 gap-3 mb-6">
                <MetricCell icon={Shield} label="Coverage" value={formatCurrency(rp.policy.coverage)} color="#6366f1" />
                <MetricCell icon={IndianRupee} label="Premium" value={formatCurrency(rp.policy.premium)} color="#8b5cf6" />
                <MetricCell icon={Zap} label="Utility" value={rp.utility_score.toFixed(1)} color="#a78bfa" />
                <MetricCell icon={Brain} label="AI Match" value={rp.ai_score.toFixed(1)} color="#818cf8" />
                <MetricCell icon={Percent} label="Performance" value={formatPercent(premiumRatio)} color="#c4b5fd" />
              </div>

              {/* Horizontal bar chart */}
              <div className="mb-6 p-5 rounded-xl border border-white/[0.03] bg-white/[0.008]">
                <HBar label="Utility" value={rp.utility_score} color="#6366f1" delay={0.2 + i * 0.05} />
                <HBar label="Coverage" value={rp.coverage_score} color="#8b5cf6" delay={0.3 + i * 0.05} />
                <HBar label="AI/RL" value={rp.ai_score} color="#a78bfa" delay={0.4 + i * 0.05} />
                <AxisLabels />
              </div>

              {/* Gap & Tradeoff */}
              <div className="space-y-2 mb-5">
                <p className="text-sm">
                  <span className="font-bold" style={{ color: rp.coverage_gap <= 0 ? '#10B981' : '#EF4444' }}>
                    Gap: {formatCurrency(Math.abs(rp.coverage_gap))}
                  </span>
                </p>
                <p className="text-[13px] text-white/25">
                  <span className="font-semibold text-white/35">Tradeoff:</span> {rp.tradeoff_summary}
                </p>
              </div>

              {/* Explanation points */}
              <div>
                <p className="text-[13px] font-semibold text-white/35 mb-2">Why this policy:</p>
                <ul className="space-y-1.5">
                  {rp.explanation_points.map((pt, pi) => (
                    <li key={pi} className="text-[12px] text-white/25 flex items-start gap-2.5 leading-relaxed">
                      <span className="text-indigo-400/40 mt-0.5 flex-shrink-0">•</span>
                      <span>{pt}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default PolicyEvaluationTab;
