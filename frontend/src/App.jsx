import { useState, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Layout from './components/layout/Layout';
import InputForm from './components/dashboard/InputForm';
import RiskAnalysisTab from './components/deepdive/RiskAnalysisTab';
import ScenarioSimulationTab from './components/deepdive/ScenarioSimulationTab';
import PolicyEvaluationTab from './components/deepdive/PolicyEvaluationTab';
import CriticInsightsTab from './components/deepdive/CriticInsightsTab';
import RecommendationTab from './components/deepdive/RecommendationTab';
import PipelineTraceTab from './components/deepdive/PipelineTraceTab';
import LoadingState from './components/shared/LoadingState';
import ErrorState from './components/shared/ErrorState';
import { useRecommendation } from './hooks/useRecommendation';

function App() {
  const { result, loading, error, submitRecommendation, reset } = useRecommendation();
  const [activeTab, setActiveTab] = useState('risk');
  const [userName, setUserName] = useState('');

  const hasResults = !!result && !loading;

  const handleSubmit = useCallback((payload) => {
    setUserName(payload._name || 'User');
    const { _name, ...apiPayload } = payload;
    submitRecommendation(apiPayload);
    setActiveTab('risk'); // default to Risk Analysis after submit
  }, [submitRecommendation]);

  const handleReset = useCallback(() => {
    reset();
    setUserName('');
    setActiveTab('risk');
  }, [reset]);

  const handleNavigate = useCallback((view) => {
    if (view === 'form') {
      handleReset();
    }
  }, [handleReset]);

  const handleTabChange = useCallback((tabId) => {
    setActiveTab(tabId);
  }, []);

  const enrichedResult = result ? { ...result, _name: userName } : null;

  const renderTab = () => {
    if (!enrichedResult) return null;
    switch (activeTab) {
      case 'risk': return <RiskAnalysisTab result={enrichedResult} />;
      case 'scenario': return <ScenarioSimulationTab result={enrichedResult} />;
      case 'policies': return <PolicyEvaluationTab result={enrichedResult} />;
      case 'critic': return <CriticInsightsTab result={enrichedResult} />;
      case 'recommendation': return <RecommendationTab result={enrichedResult} />;
      case 'trace': return <PipelineTraceTab result={enrichedResult} />;
      default: return <RiskAnalysisTab result={enrichedResult} />;
    }
  };

  const currentView = loading ? 'loading' : error ? 'error' : hasResults ? 'results' : 'form';

  return (
    <Layout
      currentView={currentView}
      activeTab={activeTab}
      onNavigate={handleNavigate}
      onTabChange={handleTabChange}
      hasResults={hasResults}
    >
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <LoadingState />
          </motion.div>
        ) : error ? (
          <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <ErrorState message={error} onRetry={handleReset} />
          </motion.div>
        ) : hasResults ? (
          <motion.div key={`tab-${activeTab}`} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.25 }}>
            {renderTab()}
          </motion.div>
        ) : (
          <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <InputForm onSubmit={handleSubmit} loading={loading} />
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
}

export default App;
