import { motion } from 'framer-motion';
import { User, Heart, IndianRupee, Calendar, Users, Briefcase, TrendingDown, Activity } from 'lucide-react';
import RiskBadge from '../shared/RiskBadge';
import { formatCurrency } from '../../utils/formatters';
import { getGoalLabel, getLifeStageLabel } from '../../adapters/responseAdapter';

const ProfilePanel = ({ profile, riskScore, riskLabel }) => {
  const healthIndicators = [];
  if (profile.is_smoker) healthIndicators.push({ label: 'Smoker', color: 'text-red-400' });
  if (profile.alcohol_consumption !== 'none') healthIndicators.push({ label: `${profile.alcohol_consumption} alcohol`, color: 'text-amber-400' });
  if (profile.has_severe_health_issues) healthIndicators.push({ label: 'Severe conditions', color: 'text-red-400' });

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-strong rounded-2xl glow-border p-7 space-y-6"
    >
      <div className="text-center">
        <div className="w-16 h-16 rounded-full gradient-brand-vivid flex items-center justify-center mx-auto mb-4 text-white font-bold text-xl shadow-lg shadow-indigo-500/20">
          <User className="w-7 h-7" />
        </div>
        <RiskBadge label={riskLabel} score={riskScore} size="md" />
      </div>

      <div className="h-px bg-white/5" />

      <div className="space-y-4">
        <InfoRow icon={Calendar} label="Age" value={`${profile.age} years`} />
        <InfoRow icon={Briefcase} label="Life Stage" value={getLifeStageLabel(profile.life_stage)} />
        <InfoRow icon={IndianRupee} label="Income" value={`${formatCurrency(profile.income)}/yr`} />
        <InfoRow icon={Users} label="Dependents" value={profile.dependents} />
        <InfoRow icon={IndianRupee} label="Net Worth" value={formatCurrency(profile.net_worth)} />
        <InfoRow icon={TrendingDown} label="Liability" value={`${(profile.liability_ratio * 100).toFixed(0)}%`} />
        <InfoRow icon={Activity} label="Band" value={profile.affordability_band?.toUpperCase()} />
      </div>

      {healthIndicators.length > 0 && (
        <>
          <div className="h-px bg-white/5" />
          <div>
            <p className="text-xs font-bold text-white/20 uppercase tracking-[2px] mb-3">Health</p>
            <div className="flex flex-wrap gap-2">
              {healthIndicators.map((h) => (
                <span key={h.label} className={`text-xs px-3 py-1.5 rounded-full bg-red-500/8 border border-red-500/15 ${h.color} font-medium`}>{h.label}</span>
              ))}
            </div>
          </div>
        </>
      )}

      <div className="h-px bg-white/5" />
      <div>
        <p className="text-xs font-bold text-white/20 uppercase tracking-[2px] mb-2">Goal</p>
        <p className="text-sm font-semibold text-indigo-400">{getGoalLabel(profile.insurance_goal)}</p>
      </div>
    </motion.div>
  );
};

const InfoRow = ({ icon: Icon, label, value }) => (
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-2.5 text-white/30">
      <Icon className="w-4 h-4" />
      <span className="text-sm">{label}</span>
    </div>
    <span className="text-sm font-semibold text-white/60">{value}</span>
  </div>
);

export default ProfilePanel;
