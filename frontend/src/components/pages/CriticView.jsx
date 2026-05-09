/* ═══════════════════════════════════════════════════════════════════════════
   components/pages/CriticView.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Critic Agent page — shows the full critic output:
   - Verdict (validated / issues found / replanning triggered)
   - Critic issues list
   - Confidence score
   - Compliance report
   - Top policy explanation points
   ═══════════════════════════════════════════════════════════════════════════ */

import { ShieldCheck, AlertTriangle, CheckCircle, XCircle, FileText, Star } from 'lucide-react';

function Section({ icon: Icon, iconColor, title, children }) {
  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-4">
        <Icon size={15} style={{ color: iconColor }} />
        <h4
          className="text-sm font-semibold"
          style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-text-primary)' }}
        >
          {title}
        </h4>
      </div>
      {children}
    </div>
  );
}

export default function CriticView({ rawResponse }) {
  if (!rawResponse) {
    return (
      <div className="card p-8 text-center" style={{ color: 'var(--color-text-muted)' }}>
        <ShieldCheck size={32} className="mx-auto mb-3 opacity-40" />
        <p className="text-sm">Submit a recommendation request to view the critic agent output.</p>
      </div>
    );
  }

  const criticIssues = rawResponse.critic_issues ?? [];
  const confidence = rawResponse.confidence_score ?? 0;
  const compliance = rawResponse.compliance_report ?? null;
  const finalPolicy = rawResponse.final_recommendation ?? rawResponse.best_policy;
  const explanationPoints = finalPolicy?.explanation_points ?? [];
  const tradeoff = finalPolicy?.tradeoff_summary ?? '';
  const policyName = finalPolicy?.policy?.policy_name ?? 'N/A';

  const hasIssues = criticIssues.length > 0;
  const confidenceColor =
    confidence >= 80 ? 'var(--color-success)' :
    confidence >= 50 ? 'var(--color-warning)' :
    'var(--color-danger)';

  const verdictLabel = !hasIssues ? 'Validated' : confidence >= 60 ? 'Issues Found' : 'Replanning Triggered';
  const verdictColor = !hasIssues ? 'var(--color-success)' : confidence >= 60 ? 'var(--color-warning)' : 'var(--color-danger)';
  const VerdictIcon = !hasIssues ? CheckCircle : confidence >= 60 ? AlertTriangle : XCircle;

  return (
    <div className="space-y-4 max-w-3xl" id="critic-view">

      {/* ── Verdict banner ───────────────────────────────────────── */}
      <div
        className="card p-5 flex items-center justify-between"
        style={{ borderLeft: `3px solid ${verdictColor}` }}
      >
        <div className="flex items-center gap-3">
          <VerdictIcon size={22} style={{ color: verdictColor }} />
          <div>
            <p className="text-[13px] font-bold" style={{ color: verdictColor }}>{verdictLabel}</p>
            <p className="text-[12px]" style={{ color: 'var(--color-text-secondary)' }}>
              Critic reviewed <strong>{policyName}</strong> — {hasIssues ? `${criticIssues.length} issue(s) flagged` : 'no issues found'}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[28px] font-bold leading-none" style={{ color: confidenceColor }}>
            {confidence.toFixed(0)}%
          </p>
          <p className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
            Confidence
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* ── Critic Issues ──────────────────────────────────────── */}
        <Section icon={AlertTriangle} iconColor="var(--color-warning)" title="Critic Issues">
          {hasIssues ? (
            <ul className="space-y-2.5">
              {criticIssues.map((issue, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span
                    className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ backgroundColor: 'var(--color-warning)' }}
                  />
                  <span className="text-[12.5px]" style={{ color: 'var(--color-text-secondary)' }}>
                    {issue}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-2" style={{ color: 'var(--color-success)' }}>
              <CheckCircle size={14} />
              <p className="text-[12.5px] font-medium">No issues detected. Policy passed all checks.</p>
            </div>
          )}
        </Section>

        {/* ── Policy Explanation Points ───────────────────────────── */}
        <Section icon={Star} iconColor="var(--color-sand-dark)" title="Why This Policy">
          {explanationPoints.length > 0 ? (
            <ul className="space-y-2.5">
              {explanationPoints.map((pt, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span
                    className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ backgroundColor: 'var(--color-sand-dark)' }}
                  />
                  <span className="text-[12.5px]" style={{ color: 'var(--color-text-secondary)' }}>
                    {pt}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[12.5px]" style={{ color: 'var(--color-text-muted)' }}>
              No explanation points available.
            </p>
          )}
          {tradeoff && (
            <p
              className="mt-3 text-[11px] italic px-3 py-2 rounded-lg"
              style={{
                backgroundColor: 'var(--color-cream)',
                color: 'var(--color-text-muted)',
                border: '1px solid var(--color-border-soft)',
              }}
            >
              Tradeoff: {tradeoff}
            </p>
          )}
        </Section>
      </div>

      {/* ── Compliance Report ──────────────────────────────────────── */}
      {compliance && Object.keys(compliance).length > 0 && (
        <Section icon={FileText} iconColor="var(--color-info)" title="Compliance Report">
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(compliance).map(([key, value]) => {
              const passed = value === true || value === 'pass' || value === 'compliant';
              const failed = value === false || value === 'fail' || value === 'non-compliant';
              const statusColor = passed ? 'var(--color-success)' : failed ? 'var(--color-danger)' : 'var(--color-text-secondary)';
              const StatusIcon = passed ? CheckCircle : failed ? XCircle : null;

              const isLongField = key === 'regulations_referenced' || key === 'issues' || (typeof value === 'string' && value.length > 35);

              return (
                <div
                  key={key}
                  className={`px-3 py-2.5 rounded-lg ${
                    isLongField ? 'col-span-2 flex flex-col items-start gap-1.5' : 'flex items-center justify-between'
                  }`}
                  style={{ backgroundColor: 'var(--color-cream)', border: '1px solid var(--color-border-soft)' }}
                >
                  <p className="text-[11px] font-medium capitalize" style={{ color: 'var(--color-text-primary)' }}>
                    {key.replace(/_/g, ' ')}
                  </p>
                  <div className="flex items-center gap-1.5">
                    {StatusIcon && <StatusIcon size={12} style={{ color: statusColor }} />}
                    <p className={`text-[11px] ${isLongField ? 'font-normal leading-relaxed' : 'font-semibold capitalize'}`} style={{ color: statusColor }}>
                      {String(value)}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </Section>
      )}
    </div>
  );
}
