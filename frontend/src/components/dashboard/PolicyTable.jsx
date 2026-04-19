import { motion } from 'framer-motion';
import { Trophy, ChevronRight } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';
import { getPolicyTypeLabel } from '../../adapters/responseAdapter';

const MEDALS = ['🥇', '🥈', '🥉'];

const PolicyTable = ({ policies, finalPolicyName, onSelectPolicy }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="glass-strong rounded-2xl glow-border overflow-hidden"
    >
      <div className="px-7 py-5 border-b border-white/5 flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-white">Top Ranked Policies</h3>
          <p className="text-sm text-white/20 mt-0.5">Click a policy to explore detailed AI analysis</p>
        </div>
        <span className="text-xs font-semibold text-white/15 tracking-wider">{policies.length} POLICIES</span>
      </div>

      <div className="divide-y divide-white/[0.04]">
        {policies.map((rp, i) => {
          const isFinal = rp.policy.policy_name === finalPolicyName;
          return (
            <motion.div
              key={rp.policy.policy_name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.35 + i * 0.1 }}
              onClick={() => onSelectPolicy(i)}
              className={`px-7 py-5 flex items-center gap-5 cursor-pointer transition-all duration-300 group
                ${isFinal ? 'bg-indigo-500/[0.04]' : 'hover:bg-white/[0.02]'}`}
            >
              <div className="text-2xl w-10 text-center flex-shrink-0">{MEDALS[i] || `#${i + 1}`}</div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-base text-white truncate">{rp.policy.policy_name}</span>
                  {isFinal && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-indigo-500/12 border border-indigo-500/20 text-indigo-300 text-[10px] font-bold uppercase tracking-wider">
                      <Trophy className="w-3 h-3" /> Recommended
                    </span>
                  )}
                </div>
                <span className="text-sm text-white/20 mt-0.5">{getPolicyTypeLabel(rp.policy.policy_type)}</span>
              </div>

              <div className="hidden md:flex items-center gap-8 text-right">
                <div>
                  <p className="text-xs text-white/20">Coverage</p>
                  <p className="text-base font-semibold text-white/70">{formatCurrency(rp.policy.coverage)}</p>
                </div>
                <div>
                  <p className="text-xs text-white/20">Premium</p>
                  <p className="text-base font-semibold text-white/70">{formatCurrency(rp.policy.premium)}</p>
                </div>
                <div>
                  <p className="text-xs text-white/20">Score</p>
                  <p className="text-base font-bold text-indigo-400">{rp.total_score.toFixed(1)}</p>
                </div>
              </div>

              <ChevronRight className="w-5 h-5 text-white/10 group-hover:text-indigo-400 transition-colors flex-shrink-0" />
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default PolicyTable;
