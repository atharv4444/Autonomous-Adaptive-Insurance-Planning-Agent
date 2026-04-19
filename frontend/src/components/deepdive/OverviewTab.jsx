import { motion } from 'framer-motion';
import { Info } from 'lucide-react';
import AnimatedCard from '../shared/AnimatedCard';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { getPolicyTypeLabel } from '../../adapters/responseAdapter';

const OverviewTab = ({ result }) => {
  const fp = result.final_recommendation;
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <AnimatedCard className="overflow-hidden" hover={false}>
        <div className="gradient-brand-vivid p-10 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.06),transparent)]" />
          <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-white/5 rounded-full blur-3xl" />
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 200, damping: 12, delay: 0.2 }} className="text-6xl mb-4">🏆</motion.div>
          <h3 className="text-3xl font-extrabold text-white mb-2">{fp.policy.policy_name}</h3>
          <p className="text-white/40 text-base">{getPolicyTypeLabel(fp.policy.policy_type)} · Confidence {result.confidence_score.toFixed(1)}%</p>
        </div>
        <div className="p-8">
          <div className="grid grid-cols-4 gap-5 mb-8">
            <MetricBox label="Coverage" value={formatCurrency(fp.policy.coverage)} />
            <MetricBox label="Premium" value={formatCurrency(fp.policy.premium)} />
            <MetricBox label="Prem/Income" value={formatPercent(fp.premium_ratio)} />
            <MetricBox label="Gap" value={formatCurrency(fp.coverage_gap)} />
          </div>
          <div className="p-5 rounded-2xl bg-emerald-500/[0.06] border border-emerald-500/15 text-base text-emerald-300/80">
            <strong className="text-emerald-300">🤖 Agent:</strong> {result.explanation}
          </div>
        </div>
      </AnimatedCard>

      <div className="glass-strong rounded-2xl flex items-start gap-4 p-5 text-base text-blue-300/60">
        <Info className="w-5 h-5 mt-0.5 flex-shrink-0 text-blue-400/40" />
        <p>{result.regulatory_note}</p>
      </div>
    </motion.div>
  );
};

const MetricBox = ({ label, value }) => (
  <div className="text-center p-4 rounded-2xl bg-white/[0.03] border border-white/5">
    <p className="text-xs text-white/25 mb-1.5">{label}</p>
    <p className="text-base font-bold text-white">{value}</p>
  </div>
);

export default OverviewTab;
