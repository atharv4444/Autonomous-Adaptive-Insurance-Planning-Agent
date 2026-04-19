import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertTriangle, XCircle, ArrowRightLeft, ChevronDown, ShieldCheck } from 'lucide-react';

const CriticInsightsTab = ({ result }) => {
  const topName = result.top_policies.length > 0 ? result.top_policies[0].policy.policy_name : '';
  const finalName = result.final_recommendation.policy.policy_name;
  const wasReranked = topName && topName !== finalName;
  const issueCount = result.critic_issues.length;

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between">
        <div>
          <h2 className="text-[32px] font-black text-white tracking-tight mb-1">Critic Agent</h2>
          <p className="text-[13px] text-white/20 font-medium">
            Independent validation &middot; Issue detection &middot; Reranking
          </p>
        </div>
        <div className="text-right flex-shrink-0 mt-2">
          <span className="text-xs text-white/15 font-mono">
            Validation Confidence: <span className="text-white/40 font-bold">{result.confidence_score.toFixed(1)}%</span>
          </span>
        </div>
      </motion.div>

      {/* Detected Issues */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white/80">Detected Issues &amp; Risks</h3>
          <span className="text-xs font-semibold text-white/20">
            {issueCount === 0 ? 'No Issues' : `${issueCount} Issue${issueCount > 1 ? 's' : ''} Found`}
          </span>
        </div>

        <div className="space-y-3">
          {issueCount === 0
            ? <IssueCard type="success" message="Critic found no issues with the recommendation." />
            : result.critic_issues.map((issue, i) => {
                const lower = issue.toLowerCase();
                let type = 'warning';
                if (lower.includes('no major issues')) type = 'success';
                else if (lower.includes('underinsured') || lower.includes('critical') || lower.includes('overpriced')) type = 'error';
                return <IssueCard key={i} type={type} message={issue} delay={i * 0.06} />;
              })
          }
        </div>
      </motion.div>

      {/* Reranking Decision */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
        <h3 className="text-lg font-bold text-white/80 mb-4">Reranking Decision</h3>

        {wasReranked ? (
          <div className="critic-decision-card critic-decision-reranked">
            <div className="flex items-center gap-3 mb-3">
              <ArrowRightLeft className="w-5 h-5 text-amber-400" />
              <span className="text-base font-bold text-amber-300/80">Reranked by Critic</span>
            </div>
            <p className="text-sm text-white/30 leading-relaxed">
              The critic re-evaluated and changed the recommendation from{' '}
              <span className="font-semibold text-white/50">{topName}</span> to{' '}
              <span className="font-semibold text-white/50">{finalName}</span>.
            </p>
          </div>
        ) : (
          <div className="critic-decision-card critic-decision-accepted">
            <div className="flex items-center gap-3 mb-3">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <span className="text-base font-bold text-emerald-300/70">No Reranking</span>
            </div>
            <p className="text-sm text-white/25 leading-relaxed">
              No significant reranking required. Critic accepts the top-ranked policy,{' '}
              <span className="font-semibold text-white/50">&apos;{finalName}&apos;</span>.
            </p>
            <p className="text-[12px] text-white/15 mt-2">
              The overall score for &apos;{finalName}&apos; ({result.final_recommendation.total_score.toFixed(2)}) is considered acceptable despite detected concerns. Proceed with current ranking.
            </p>
          </div>
        )}
      </motion.div>

      {/* Confidence Bar */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
        <div className="critic-confidence-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-white/35">Critic Confidence</span>
            <span className="text-xl font-black font-mono-num text-white/80">
              {result.confidence_score.toFixed(1)}<span className="text-sm text-white/20">%</span>
            </span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-white/[0.04] overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(result.confidence_score, 100)}%` }}
              transition={{ duration: 1, delay: 0.4, ease: [0.4, 0, 0.2, 1] }}
              className="h-full rounded-full"
              style={{
                background: result.confidence_score >= 70
                  ? 'linear-gradient(90deg, #10B981, #059669)'
                  : result.confidence_score >= 50
                  ? 'linear-gradient(90deg, #F59E0B, #D97706)'
                  : 'linear-gradient(90deg, #EF4444, #DC2626)',
              }}
            />
          </div>
        </div>
      </motion.div>
    </div>
  );
};

const IssueCard = ({ type, message, delay = 0 }) => {
  const [expanded, setExpanded] = useState(false);
  const c = {
    success: { icon: CheckCircle, color: '#10B981', bg: 'rgba(16,185,129,0.03)', border: 'rgba(16,185,129,0.08)' },
    warning: { icon: AlertTriangle, color: '#F59E0B', bg: 'rgba(245,158,11,0.03)', border: 'rgba(245,158,11,0.08)' },
    error: { icon: XCircle, color: '#EF4444', bg: 'rgba(239,68,68,0.03)', border: 'rgba(239,68,68,0.08)' },
  }[type];
  const Icon = c.icon;

  // Split message into title and detail if possible
  const parts = message.split(':');
  const title = parts.length > 1 ? parts[0].trim() : '';
  const detail = parts.length > 1 ? parts.slice(1).join(':').trim() : message;

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="rounded-xl border overflow-hidden"
      style={{ background: c.bg, borderColor: c.border }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-4 px-5 py-4 text-left"
      >
        <Icon className="w-4 h-4 flex-shrink-0" style={{ color: c.color }} />
        <div className="flex-1 min-w-0">
          {title ? (
            <span className="text-[13px] leading-relaxed">
              <span className="font-bold" style={{ color: c.color }}>{title}:</span>{' '}
              <span className="text-white/40">{detail.split('.')[0]}.</span>
            </span>
          ) : (
            <span className="text-[13px] text-white/40">{detail}</span>
          )}
        </div>
        <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown className="w-4 h-4 text-white/15" />
        </motion.div>
      </button>
      <AnimatePresence>
        {expanded && detail.split('.').length > 1 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-4 pl-13">
              <p className="text-[12px] text-white/25 leading-relaxed ml-8">{detail}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default CriticInsightsTab;
