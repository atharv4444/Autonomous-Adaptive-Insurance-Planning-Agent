import { motion } from 'framer-motion';
import {
  Shield, LayoutDashboard, ClipboardList, BarChart3, ShieldAlert, Zap,
  MessageSquareWarning, Trophy, GitBranch, PlusCircle, Activity
} from 'lucide-react';

const ANALYSIS_TABS = [
  { id: 'risk', label: 'Risk Analysis', icon: ShieldAlert },
  { id: 'scenario', label: 'Scenarios', icon: Activity },
  { id: 'policies', label: 'Policies', icon: ClipboardList },
  { id: 'critic', label: 'Critic', icon: MessageSquareWarning },
  { id: 'recommendation', label: 'Result', icon: Trophy },
  { id: 'trace', label: 'Pipeline', icon: GitBranch },
];

const Sidebar = ({ currentView, activeTab, onNavigate, onTabChange, hasResults }) => {
  const isFormView = !hasResults || currentView === 'form';

  return (
    <div className="sidebar-container">
      {/* Logo */}
      <div className="px-5 mb-8 flex items-center gap-3">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="w-10 h-10 rounded-xl gradient-brand-vivid flex items-center justify-center flex-shrink-0 animate-pulse-glow"
        >
          <Shield className="w-5 h-5 text-white" />
        </motion.div>
        <span className="text-[16px] font-bold text-white/90 tracking-tight">InsureAI</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3">
        {/* OVERVIEW section */}
        <SectionLabel text="Overview" />
        <NavItem icon={LayoutDashboard} label="Dashboard"
          active={isFormView && currentView !== 'form'}
          onClick={() => onNavigate('dashboard')} />
        <NavItem icon={ClipboardList} label="Planning"
          active={isFormView && (currentView === 'form' || (!hasResults && currentView !== 'results'))}
          onClick={() => onNavigate('form')} />

        {/* ANALYSIS section */}
        {hasResults && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
            <SectionLabel text="Analysis" />
            <NavItem icon={BarChart3} label="Analyze"
              active={false}
              onClick={() => onTabChange('risk')}
              disabled={!hasResults} />
            {ANALYSIS_TABS.map((tab, i) => (
              <motion.div key={tab.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.12 + i * 0.035, ease: [0.4, 0, 0.2, 1] }}>
                <NavItem icon={tab.icon} label={tab.label}
                  active={activeTab === tab.id && !isFormView}
                  onClick={() => onTabChange(tab.id)}
                  indent />
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* WORKFLOW section */}
        {hasResults && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
            <SectionLabel text="Workflow" />
            <button
              onClick={() => onNavigate('form')}
              className="sidebar-new-btn"
            >
              <PlusCircle className="w-4 h-4 text-indigo-400" />
              <span>New Analysis</span>
            </button>
          </motion.div>
        )}
      </nav>

      <div className="px-5 pb-4">
        <p className="text-[8px] font-mono text-white/6 tracking-[4px]">v0.1.0</p>
      </div>
    </div>
  );
};

const SectionLabel = ({ text }) => (
  <p className="sidebar-section-label">{text}</p>
);

const NavItem = ({ icon: Icon, label, active, onClick, muted, disabled, indent }) => (
  <button onClick={onClick} disabled={disabled}
    className={`sidebar-nav-item ${active ? 'sidebar-nav-active' : ''} ${muted ? 'sidebar-nav-muted' : ''} ${disabled ? 'sidebar-nav-disabled' : ''} ${indent ? 'sidebar-nav-indent' : ''}`}>
    {active && (
      <motion.div layoutId="sidebar-active-bg"
        className="sidebar-active-highlight"
        transition={{ type: 'spring', stiffness: 400, damping: 30 }} />
    )}
    <Icon className={`w-[18px] h-[18px] flex-shrink-0 relative z-10 transition-all duration-300
      ${active ? 'text-indigo-400' : ''}`}
      style={active ? { filter: 'drop-shadow(0 0 5px rgba(129,140,248,0.4))' } : {}} />
    <span className="relative z-10">{label}</span>
  </button>
);

export default Sidebar;
