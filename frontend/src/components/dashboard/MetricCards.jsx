import { motion } from 'framer-motion';
import { ShieldAlert, TrendingDown, Target, Award } from 'lucide-react';
import AnimatedCard from '../shared/AnimatedCard';
import { formatCurrency } from '../../utils/formatters';
import { getRiskColor } from '../../adapters/responseAdapter';

const MetricCards = ({ result }) => {
  const metrics = [
    {
      label: 'Risk Score',
      value: `${result.risk_score.toFixed(1)}`,
      sub: `/ 100 — ${result.risk_label.toUpperCase()}`,
      icon: ShieldAlert,
      color: getRiskColor(result.risk_label),
    },
    {
      label: 'Expected Loss',
      value: formatCurrency(result.expected_loss),
      sub: 'Annual across all scenarios',
      icon: TrendingDown,
      color: '#f87171',
    },
    {
      label: 'AI Confidence',
      value: `${result.confidence_score.toFixed(1)}%`,
      sub: 'Critic validation',
      icon: Target,
      color: '#818cf8',
    },
    {
      label: 'Best Policy',
      value: result.final_recommendation.policy.policy_name,
      sub: `Score: ${result.final_recommendation.total_score.toFixed(1)}`,
      icon: Award,
      color: '#a78bfa',
      isText: true,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      {metrics.map((m, i) => {
        const Icon = m.icon;
        return (
          <AnimatedCard key={m.label} delay={i * 0.08} className="p-6">
            <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4" style={{ background: `${m.color}12` }}>
              <Icon className="w-5 h-5" style={{ color: m.color }} />
            </div>
            <p className="text-[11px] font-bold text-white/25 uppercase tracking-[2px] mb-1.5">{m.label}</p>
            <p className={`${m.isText ? 'text-lg' : 'text-3xl'} font-extrabold text-white leading-tight`}>{m.value}</p>
            <p className="text-xs text-white/20 mt-1.5">{m.sub}</p>
          </AnimatedCard>
        );
      })}
    </div>
  );
};

export default MetricCards;
