import Sidebar from './Sidebar';

const Layout = ({ children, currentView, activeTab, onNavigate, onTabChange, hasResults }) => {
  return (
    <div className="h-screen bg-[#0A0A0A] flex overflow-hidden relative">
      {/* Grain texture */}
      <div className="grain-overlay" />

      {/* Ambient glows */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[-300px] left-[30%] w-[800px] h-[800px] bg-indigo-600/[0.015] rounded-full blur-[200px]" />
        <div className="absolute bottom-[-300px] right-[20%] w-[700px] h-[700px] bg-violet-600/[0.01] rounded-full blur-[200px]" />
      </div>

      <Sidebar
        currentView={currentView}
        activeTab={activeTab}
        onNavigate={onNavigate}
        onTabChange={onTabChange}
        hasResults={hasResults}
      />

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 relative z-10 h-screen overflow-hidden">
        <main className="flex-1 overflow-y-auto">
          <div className="px-12 lg:px-20 py-12 flex justify-center">
            <div className="w-full max-w-5xl">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
