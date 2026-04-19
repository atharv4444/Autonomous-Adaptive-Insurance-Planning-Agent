import { Sparkles } from 'lucide-react';

const Header = () => {
  return (
    <header
      className="h-14 flex items-center justify-end px-8 sticky top-0 z-40 flex-shrink-0"
      style={{
        background: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(30px) saturate(130%)',
        WebkitBackdropFilter: 'blur(30px) saturate(130%)',
        borderBottom: '1px solid rgba(255,255,255,0.03)',
      }}
    >
      <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full glass border border-indigo-500/10">
        <Sparkles className="w-3 h-3 text-indigo-400" />
        <span className="text-[10px] font-bold tracking-widest uppercase text-indigo-400/70">AI-Powered</span>
      </div>
    </header>
  );
};

export default Header;
