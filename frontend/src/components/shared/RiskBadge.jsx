const RiskBadge = ({ label, score, size = 'md' }) => {
  const config = {
    low: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20', dot: 'bg-emerald-400' },
    moderate: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20', dot: 'bg-amber-400' },
    high: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20', dot: 'bg-red-400' },
  };
  const c = config[label] || config.moderate;
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full border ${c.bg} ${c.text} ${c.border} ${sizeClasses[size]}`}>
      <span className={`w-2 h-2 rounded-full ${c.dot} animate-pulse`} />
      {label?.toUpperCase()}
      {score !== undefined && <span className="opacity-60">({score})</span>}
    </span>
  );
};

export default RiskBadge;
