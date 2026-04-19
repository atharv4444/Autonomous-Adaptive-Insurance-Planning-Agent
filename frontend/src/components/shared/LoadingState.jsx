import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

const LoadingState = ({ message = 'Running the multi-agent insurance pipeline…' }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center py-24 gap-6"
    >
      <div className="relative">
        <div className="w-20 h-20 rounded-2xl gradient-brand-vivid flex items-center justify-center animate-pulse-glow">
          <Loader2 className="w-9 h-9 text-white animate-spin" />
        </div>
      </div>

      <div className="text-center space-y-2">
        <p className="text-lg font-semibold text-white">{message}</p>
        <p className="text-sm text-white/30">Profiling → Risk Analysis → Scenario Simulation → Policy Evaluation → Critic</p>
      </div>

      <div className="w-full max-w-lg grid grid-cols-3 gap-3 mt-4">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-24 rounded-xl bg-gradient-to-r from-white/[0.02] via-white/[0.05] to-white/[0.02] animate-shimmer"
          />
        ))}
      </div>
    </motion.div>
  );
};

export default LoadingState;
