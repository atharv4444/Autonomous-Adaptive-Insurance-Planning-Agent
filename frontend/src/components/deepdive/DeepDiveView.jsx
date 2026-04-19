import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import ProfilePanel from './ProfilePanel';
import OverviewTab from './OverviewTab';
import RiskAnalysisTab from './RiskAnalysisTab';
import ScenarioSimulationTab from './ScenarioSimulationTab';
import PolicyEvaluationTab from './PolicyEvaluationTab';
import RecommendationTab from './RecommendationTab';
import CriticInsightsTab from './CriticInsightsTab';
import PipelineTraceTab from './PipelineTraceTab';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'risk', label: 'Risk' },
  { id: 'scenario', label: 'Scenarios' },
  { id: 'policies', label: 'Policies' },
  { id: 'recommendation', label: 'Result' },
  { id: 'critic', label: 'Critic' },
  { id: 'trace', label: 'Pipeline' },
];

const DeepDiveView = ({ result, onBack }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const renderTab = () => {
    switch (activeTab) {
      case 'overview': return <OverviewTab result={result} />;
      case 'risk': return <RiskAnalysisTab result={result} />;
      case 'scenario': return <ScenarioSimulationTab result={result} />;
      case 'policies': return <PolicyEvaluationTab result={result} />;
      case 'recommendation': return <RecommendationTab result={result} />;
      case 'critic': return <CriticInsightsTab result={result} />;
      case 'trace': return <PipelineTraceTab result={result} />;
      default: return <OverviewTab result={result} />;
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="max-w-7xl mx-auto">
      <button onClick={onBack}
        className="inline-flex items-center gap-2 text-sm font-medium text-white/25 hover:text-indigo-400 mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="flex gap-8">
        {/* Left — Profile panel (sticky within scroll) */}
        <div className="w-80 flex-shrink-0 hidden lg:block">
          <div className="sticky top-0">
            <ProfilePanel profile={result.user_profile} riskScore={result.risk_score} riskLabel={result.risk_label} />
          </div>
        </div>

        {/* Right — Tabs */}
        <div className="flex-1 min-w-0">
          {/* Tab bar */}
          <div className="glass-strong rounded-2xl p-2 flex gap-1 mb-8 overflow-x-auto">
            {TABS.map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`relative px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 whitespace-nowrap
                  ${activeTab === tab.id ? 'text-indigo-300' : 'text-white/20 hover:text-white/40 hover:bg-white/[0.03]'}`}>
                {activeTab === tab.id && (
                  <motion.div layoutId="active-tab-deep"
                    className="absolute inset-0 bg-indigo-500/10 border border-indigo-500/20 rounded-xl"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }} style={{ zIndex: 0 }} />
                )}
                <span className="relative z-10">{tab.label}</span>
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.div key={activeTab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
              {renderTab()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};

export default DeepDiveView;
