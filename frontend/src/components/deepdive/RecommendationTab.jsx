import { motion } from 'framer-motion';
import { Info, Shield, IndianRupee, Percent, TrendingUp, Bot } from 'lucide-react';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { getPolicyTypeLabel } from '../../adapters/responseAdapter';

const RecommendationTab = ({ result }) => {
  const fp = result.final_recommendation;

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h2 className="text-[32px] font-black text-white tracking-tight mb-1">Final Recommendation</h2>
        <p className="text-[13px] text-white/20 font-medium">Top-ranked policy after full agent pipeline</p>
      </motion.div>

      {/* Hero card */}
      <motion.div
        initial={{ opacity: 0, y: 25, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ delay: 0.1, ease: [0.4, 0, 0.2, 1] }}
        className="result-hero-card"
      >
        <div className="flex items-center justify-between">
          {/* Score */}
          <div className="text-center">
            <p className="text-3xl font-black font-mono-num text-white" style={{ textShadow: '0 0 20px rgba(99,102,241,0.3)' }}>
              {fp.total_score.toFixed(1)}
            </p>
            <p className="text-[10px] font-bold uppercase tracking-[2px] text-white/25 mt-1">Score</p>
          </div>

          {/* Center — Trophy & Name */}
          <div className="text-center flex-1 px-8">
            <motion.div
              initial={{ scale: 0, rotate: -15 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: 'spring', stiffness: 180, damping: 14, delay: 0.3 }}
              className="text-5xl mb-3 inline-block"
            >
              🏆
            </motion.div>
            <motion.h3
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              className="text-2xl font-extrabold text-white tracking-tight mb-1"
            >
              {fp.policy.policy_name}
            </motion.h3>
            <p className="text-sm text-white/25 font-medium">{getPolicyTypeLabel(fp.policy.policy_type)}</p>
          </div>

          {/* Confidence */}
          <div className="text-center">
            <p className="text-3xl font-black font-mono-num text-white" style={{ textShadow: '0 0 20px rgba(99,102,241,0.3)' }}>
              {result.confidence_score.toFixed(1)}%
            </p>
            <p className="text-[10px] font-bold uppercase tracking-[2px] text-white/25 mt-1">Confidence</p>
          </div>
        </div>
      </motion.div>

      {/* Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-4 gap-4"
      >
        <ResultMetric icon={Shield} label="Coverage" value={formatCurrency(fp.policy.coverage)} color="#6366f1" />
        <ResultMetric icon={IndianRupee} label="Premium" value={formatCurrency(fp.policy.premium)} color="#8b5cf6" />
        <ResultMetric icon={Percent} label="Prem./Income Ratio" value={formatPercent(fp.premium_ratio)} color="#a78bfa" />
        <ResultMetric icon={TrendingUp} label="Gap" value={formatCurrency(fp.coverage_gap)} color="#818cf8" />
      </motion.div>

      {/* AI Agent Insights */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="result-insights-card"
      >
        <div className="flex items-center gap-3 mb-4">
          <Bot className="w-5 h-5 text-white/30" />
          <h3 className="text-base font-bold text-white/70">AI Agent Insights</h3>
        </div>

        <div>
          <p className="text-[13px] font-semibold text-white/40 mb-3">Why this policy is optimal:</p>
          <div className="space-y-2.5">
            {(result.explanation || '').split('.').filter(s => s.trim()).map((sentence, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <span className="text-indigo-400/30 mt-0.5 flex-shrink-0">•</span>
                <p className="text-[13px] text-white/30 leading-relaxed">{sentence.trim()}.</p>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* IRDAI Disclaimer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="result-disclaimer"
      >
        <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-white/10" />
        <p className="text-[11px] text-white/15 leading-relaxed">{result.regulatory_note}</p>
      </motion.div>
    </div>
  );
};

const ResultMetric = ({ icon: Icon, label, value, color }) => (
  <div className="result-metric-cell">
    <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-2"
      style={{ background: `${color}10` }}>
      <Icon className="w-4.5 h-4.5" style={{ color }} />
    </div>
    <p className="text-[10px] text-white/20 uppercase tracking-wider font-bold mb-1">{label}</p>
    <p className="text-lg font-bold font-mono-num text-white/70">{value}</p>
  </div>
);

export default RecommendationTab;
