import { motion, AnimatePresence } from 'framer-motion';
import InputForm from './InputForm';
import MetricCards from './MetricCards';
import PolicyTable from './PolicyTable';
import LoadingState from '../shared/LoadingState';
import ErrorState from '../shared/ErrorState';

const DashboardView = ({ result, loading, error, onSubmit, onReset, onSelectPolicy }) => {
  return (
    <AnimatePresence mode="wait">
      {loading ? (
        <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <LoadingState />
        </motion.div>
      ) : error ? (
        <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <ErrorState message={error} onRetry={onReset} />
        </motion.div>
      ) : result ? (
        <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="max-w-6xl mx-auto">
          {/* Profile bar */}
          <div className="glass-strong rounded-2xl p-5 flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full gradient-brand-vivid flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/20">
                {(result._name || 'U').charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-base font-semibold text-white">{result._name || 'User'}</p>
                <p className="text-sm text-white/30">
                  Age {result.user_profile.age} · ₹{result.user_profile.income.toLocaleString('en-IN')}/yr
                  · {result.user_profile.life_stage.replace(/_/g, ' ')}
                  · {result.user_profile.dependents} dependent{result.user_profile.dependents !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <button
              onClick={onReset}
              className="text-sm font-medium text-indigo-400 hover:text-indigo-300 px-5 py-2.5 rounded-xl
                border border-indigo-500/20 hover:border-indigo-500/40 hover:bg-indigo-500/10 transition-all"
            >
              ← Edit Profile
            </button>
          </div>

          <MetricCards result={result} />
          <PolicyTable
            policies={result.top_policies}
            finalPolicyName={result.final_recommendation.policy.policy_name}
            onSelectPolicy={onSelectPolicy}
          />
        </motion.div>
      ) : (
        <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <InputForm onSubmit={onSubmit} loading={loading} />
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default DashboardView;
