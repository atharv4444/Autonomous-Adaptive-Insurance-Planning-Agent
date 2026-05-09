/* ═══════════════════════════════════════════════════════════════════════════
   App.jsx — Application Shell
   ═══════════════════════════════════════════════════════════════════════════
   Layout: Fixed sidebar (240px) + scrollable main content area.
   Pages:
     - dashboard:  Results only (metrics, policies, insights)
     - profile:    Full input form (User Profiling tab)
     - risk:       Scenario simulation breakdown
     - trace:      Agent execution trace
     - scenarios:  Same as risk (alias)
   State is managed via useRecommendation() — single source of truth.
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState, useCallback, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import DashboardView from './components/dashboard/DashboardView';
import ProfilingView from './components/pages/ProfilingView';
import ScenarioView from './components/pages/ScenarioView';
import RiskView from './components/pages/RiskView';
import CriticView from './components/pages/CriticView';
import TraceView from './components/pages/TraceView';
import LoginView from './components/pages/LoginView';
import LandingPage from './components/pages/LandingPage';
import { useRecommendation } from './hooks/useRecommendation';
import { supabase } from './api/supabase';

export default function App() {
  const [activePage, setActivePage] = useState('profile');
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  /* Check active session on mount */
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setAuthLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  /* Central recommendation state — single source of truth */
  const rec = useRecommendation();

  /* Navigate to dashboard after submission */
  const handleSubmit = useCallback(async (userInput) => {
    await rec.submit(userInput);
    setActivePage('dashboard');
  }, [rec.submit]);

  /* Navigate to profiler from dashboard idle state */
  const goToProfiler = useCallback(() => setActivePage('profile'), []);
  const goToDashboard = useCallback(() => setActivePage('dashboard'), []);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-cream)' }}>
        <div className="animate-spin w-8 h-8 rounded-full border-4 border-solid border-[var(--color-sand)] border-t-transparent"></div>
      </div>
    );
  }

  if (!user) {
    return <LandingPage onLogin={setUser} />;
  }

  /* ── Page Content Renderer ─────────────────────────────────────── */
  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return (
          <DashboardView
            status={rec.status}
            metrics={rec.metrics}
            policies={rec.policies}
            explanation={rec.explanation}
            criticIssues={rec.criticIssues}
            regulatoryNote={rec.regulatoryNote}
            insights={rec.insights}
            insightsLoading={rec.insightsLoading}
            userName={rec.userName}
            onGoToProfiler={goToProfiler}
          />
        );
      case 'profile':
        return (
          <ProfilingView
            user={user}
            onSubmit={handleSubmit}
            isLoading={rec.status === 'loading'}
            hasResults={rec.status === 'success'}
            onViewResults={goToDashboard}
          />
        );
      case 'risk':
        return <RiskView metrics={rec.metrics} />;
      case 'scenarios':
        return <ScenarioView scenarios={rec.scenarios} />;
      case 'critic':
        return <CriticView rawResponse={rec.rawResponse} />;
      case 'trace':
        return <TraceView trace={rec.trace} />;
      default:
        return null;
    }
  };

  return (
    <div className="flex min-h-screen" style={{ backgroundColor: 'var(--color-cream)' }}>
      {/* ── Sidebar ────────────────────────────────────────────────── */}
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      {/* ── Main Content ───────────────────────────────────────────── */}
      <main
        className="flex-1 min-h-screen"
        style={{ marginLeft: '240px', padding: '28px 32px' }}
      >
        <Header activePage={activePage} status={rec.status} user={user} onLogout={() => supabase.auth.signOut()} />
        {renderPage()}
      </main>
    </div>
  );
}
