import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User, Calendar, IndianRupee, Users, Heart, Building2,
  Car, PiggyBank, CreditCard, Home, Rocket, Shield,
  CheckCircle2, ChevronRight, ChevronLeft, Sparkles,
  CircleDot, Info, Minus, Plus
} from 'lucide-react';

/* ───── Step definitions ───── */
const STEPS = [
  { id: 'welcome', label: 'Welcome', icon: Sparkles },
  { id: 'profile', label: 'Profile & Family', icon: User },
  { id: 'financials', label: 'Financials', icon: PiggyBank },
  { id: 'health', label: 'Health', icon: Heart },
  { id: 'review', label: 'Review', icon: CheckCircle2 },
];

const GOAL_OPTIONS = [
  { value: 'family_protection', label: 'Life Insurance', emoji: '👨‍👩‍👧‍👦', desc: "Protect your family\u2019s future" },
  { value: 'health_security', label: 'Health Insurance', emoji: '🏥', desc: 'Cover medical emergencies' },
  { value: 'car_insurance', label: 'Car Insurance', emoji: '🚗', desc: 'Protect your vehicle' },
  { value: 'home_insurance', label: 'Home Insurance', emoji: '🏠', desc: 'Secure your property' },
];

const InputForm = ({ onSubmit, loading }) => {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    name: '', age: 30, income: 600000,
    parents: 0, children: 0, hasSpouse: false, otherDependents: 0,
    bankBalance: 0, realEstate: 0, vehicleValue: 0, investments: 0,
    homeLoan: 0, carLoan: 0, personalDebt: 0,
    isSmoker: false, alcohol: 'none', hasSevereHealth: false,
    insuranceGoal: 'family_protection',
  });

  const totalDependents = form.parents + form.children + (form.hasSpouse ? 1 : 0) + form.otherDependents;
  const totalAssets = form.bankBalance + form.realEstate + form.vehicleValue + form.investments;
  const totalLiabilities = form.homeLoan + form.carLoan + form.personalDebt;

  const handleChange = useCallback((field, value) =>
    setForm(prev => ({ ...prev, [field]: value })), []);

  const nextStep = () => setStep(s => Math.min(s + 1, STEPS.length - 1));
  const prevStep = () => setStep(s => Math.max(s - 1, 0));

  const handleSubmit = () => {
    onSubmit({
      age: form.age, income: form.income, dependents: totalDependents,
      assets: totalAssets, liabilities: totalLiabilities,
      insurance_goal: form.insuranceGoal, is_smoker: form.isSmoker,
      alcohol_consumption: form.alcohol, has_severe_health_issues: form.hasSevereHealth,
      _name: form.name,
    });
  };

  const currentStep = STEPS[step];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      className="wizard-container max-w-5xl mx-auto relative">

      {/* ── Header ── */}
      <div className="flex items-start justify-between mb-2">
        <div>
          <motion.h1
            key={currentStep.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-extrabold text-white tracking-tight"
          >
            {step === 0 ? 'Welcome to InsureAI' :
             step === 1 ? "Let's Get Your Personal Details." :
             step === 2 ? 'Your Financial Picture' :
             step === 3 ? 'Health & Lifestyle' :
             'Review & Submit'}
          </motion.h1>
          <motion.p
            key={`sub-${currentStep.id}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="mt-2"
          >
            <span className="text-white/60 font-semibold text-[15px]">Get Your Personalized Insurance Plan.</span>
            <br />
            <span className="text-white/25 text-sm">Secure your family&apos;s future with AI-driven analysis.</span>
          </motion.p>
        </div>

        {/* Step indicator pill */}
        <div className="flex-shrink-0 mt-1">
          <div className="step-indicator-pill">
            <span className="text-white/50 text-xs font-semibold">Step {step + 1} of {STEPS.length}: {currentStep.label}</span>
            <div className="step-progress-bar mt-1.5">
              <motion.div
                className="step-progress-fill"
                animate={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
                transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* ── Main content area with vertical stepper + form ── */}
      <div className="flex gap-8 mt-6">

        {/* Vertical Stepper */}
        <div className="flex-shrink-0 w-[100px]">
          <div className="flex flex-col items-center">
            {STEPS.map((s, i) => {
              const StepIcon = s.icon;
              const isActive = i === step;
              const isCompleted = i < step;
              return (
                <div key={s.id} className="flex flex-col items-center">
                  {/* Step circle */}
                  <motion.button
                    onClick={() => i <= step && setStep(i)}
                    whileHover={i <= step ? { scale: 1.08 } : undefined}
                    whileTap={i <= step ? { scale: 0.95 } : undefined}
                    className={`stepper-circle ${isActive ? 'stepper-active' : isCompleted ? 'stepper-completed' : 'stepper-pending'}`}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <StepIcon className="w-5 h-5" />
                    )}
                  </motion.button>
                  {/* Label */}
                  <span className={`text-[11px] font-semibold mt-2 text-center leading-tight
                    ${isActive ? 'text-white/80' : isCompleted ? 'text-indigo-400/60' : 'text-white/15'}`}>
                    {s.label}
                  </span>
                  {/* Connector line */}
                  {i < STEPS.length - 1 && (
                    <div className={`stepper-line ${isCompleted ? 'stepper-line-done' : ''}`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Step content */}
        <div className="flex-1 min-w-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep.id}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            >
              {step === 0 && <WelcomeStep form={form} onChange={handleChange} />}
              {step === 1 && <ProfileStep form={form} onChange={handleChange} />}
              {step === 2 && <FinancialsStep form={form} onChange={handleChange} totalAssets={totalAssets} totalLiabilities={totalLiabilities} />}
              {step === 3 && <HealthStep form={form} onChange={handleChange} />}
              {step === 4 && <ReviewStep form={form} totalDependents={totalDependents} totalAssets={totalAssets} totalLiabilities={totalLiabilities} />}
            </motion.div>
          </AnimatePresence>

          {/* ── Navigation buttons ── */}
          <div className="flex gap-4 mt-8">
            {step > 0 && (
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={prevStep}
                className="wizard-btn-back flex-1"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </motion.button>
            )}
            {step < STEPS.length - 1 ? (
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={nextStep}
                className={`wizard-btn-next ${step === 0 ? 'flex-1' : 'flex-1'}`}
              >
                Continue to {STEPS[step + 1]?.label}
                <ChevronRight className="w-4 h-4" />
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={handleSubmit}
                disabled={loading}
                className="wizard-btn-submit flex-1"
              >
                <Rocket className="w-4 h-4" />
                {loading ? 'Analyzing…' : 'Run Agent Pipeline'}
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Decorative sparkle */}
      <div className="absolute bottom-4 right-4 pointer-events-none">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          className="text-indigo-500/10"
        >
          <Sparkles className="w-16 h-16" />
        </motion.div>
      </div>
    </motion.div>
  );
};

/* ═══════════════════════════════════════════════
   STEP 0 — Welcome
   ═══════════════════════════════════════════════ */
const WelcomeStep = ({ form, onChange }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {/* Left — Goal selection */}
    <div className="wizard-card">
      <CardHeader icon={Shield} label="Insurance Goal" />
      <p className="text-white/25 text-sm mb-5">What do you want to protect?</p>
      <div className="grid grid-cols-2 gap-3">
        {GOAL_OPTIONS.map((opt) => {
          const isActive = form.insuranceGoal === opt.value;
          return (
            <motion.button
              key={opt.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onChange('insuranceGoal', opt.value)}
              className={`goal-card ${isActive ? 'goal-card-active' : ''}`}
            >
              <span className="text-3xl block mb-2">{opt.emoji}</span>
              <span className="text-[13px] font-bold text-white/80 block">{opt.label}</span>
              <span className="text-[10px] text-white/25 mt-0.5 block">{opt.desc}</span>
            </motion.button>
          );
        })}
      </div>
    </div>

    {/* Right — Intro card */}
    <div className="wizard-card flex flex-col justify-center items-center text-center">
      <motion.div
        initial={{ scale: 0, rotate: -10 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: 'spring', stiffness: 160, damping: 14 }}
        className="w-20 h-20 rounded-2xl gradient-brand-vivid flex items-center justify-center mb-6 animate-pulse-glow"
        style={{ boxShadow: '0 0 40px rgba(99,102,241,0.15)' }}
      >
        <Shield className="w-10 h-10 text-white" />
      </motion.div>
      <h3 className="text-xl font-bold text-white mb-2">AI-Powered Analysis</h3>
      <p className="text-sm text-white/25 max-w-[280px] leading-relaxed">
        Our autonomous agents analyze your profile, simulate risk scenarios, and recommend the best policy — powered by ML and reinforcement learning.
      </p>
      <div className="flex items-center gap-2 mt-6 px-4 py-2 rounded-full border border-indigo-500/15 bg-indigo-500/5">
        <CircleDot className="w-3 h-3 text-indigo-400" />
        <span className="text-[10px] font-bold tracking-wider uppercase text-indigo-400/70">6 AI Agents Working For You</span>
      </div>
    </div>
  </div>
);

/* ═══════════════════════════════════════════════
   STEP 1 — Profile & Family
   ═══════════════════════════════════════════════ */
const ProfileStep = ({ form, onChange }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {/* Personal Info */}
    <div className="wizard-card">
      <CardHeader icon={User} label="Personal Info" />
      <div className="space-y-5">
        <WizardField label="Full Name" icon={User} type="text" value={form.name}
          onChange={(v) => onChange('name', v)} placeholder="e.g. Rajesh Kumar" />

        <div>
          <label className="wizard-label">Age</label>
          <div className="flex items-center gap-4">
            <input type="range" min={18} max={70} value={form.age}
              onChange={(e) => onChange('age', Number(e.target.value))}
              className="wizard-range flex-1" />
            <div className="wizard-age-badge">{form.age}</div>
          </div>
        </div>

        <div>
          <WizardField label="Annual Income (₹)" icon={IndianRupee} value={form.income}
            onChange={(v) => onChange('income', v)} step={10000} />
          {form.income > 0 && (
            <p className="text-[11px] text-white/20 mt-1.5 ml-1 font-mono">
              ₹{form.income.toLocaleString('en-IN')}/yr, ₹{Math.round(form.income / 12).toLocaleString('en-IN')}/mo
            </p>
          )}
        </div>
      </div>
    </div>

    {/* Family */}
    <div className="wizard-card">
      <CardHeader icon={Users} label="Family" />
      <p className="text-white/25 text-sm mb-5">Your Dependents</p>
      <div className="grid grid-cols-2 gap-4">
        <DependentCard label="Parents" emoji="👴👵" value={form.parents}
          onChange={(v) => onChange('parents', v)} max={4} />
        <DependentCard label="Children" emoji="👦👧" value={form.children}
          onChange={(v) => onChange('children', v)} max={10} />
        <SpouseCard hasSpouse={form.hasSpouse}
          onChange={(v) => onChange('hasSpouse', v)} />
        <DependentCard label="Other" emoji="👤" value={form.otherDependents}
          onChange={(v) => onChange('otherDependents', v)} max={5} />
      </div>
    </div>
  </div>
);

/* ═══════════════════════════════════════════════
   STEP 2 — Financials
   ═══════════════════════════════════════════════ */
const FinancialsStep = ({ form, onChange, totalAssets, totalLiabilities }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {/* Assets */}
    <div className="wizard-card">
      <CardHeader icon={PiggyBank} label="Assets" />
      <div className="space-y-4">
        <WizardField label="Bank / FD / Savings (₹)" icon={Building2} value={form.bankBalance}
          onChange={(v) => onChange('bankBalance', v)} step={10000} />
        <WizardField label="Real Estate Value (₹)" icon={Home} value={form.realEstate}
          onChange={(v) => onChange('realEstate', v)} step={100000} />
        <WizardField label="Vehicle Value (₹)" icon={Car} value={form.vehicleValue}
          onChange={(v) => onChange('vehicleValue', v)} step={50000} />
        <WizardField label="Investments (₹)" icon={PiggyBank} value={form.investments}
          onChange={(v) => onChange('investments', v)} step={10000} />
      </div>
      {totalAssets > 0 && (
        <div className="wizard-summary-pill wizard-summary-green mt-5">
          💰 Total Assets: ₹{totalAssets.toLocaleString('en-IN')}
        </div>
      )}
    </div>

    {/* Liabilities */}
    <div className="wizard-card">
      <CardHeader icon={CreditCard} label="Liabilities" />
      <div className="space-y-4">
        <WizardField label="Home Loan (₹)" icon={Home} value={form.homeLoan}
          onChange={(v) => onChange('homeLoan', v)} step={50000} />
        <WizardField label="Vehicle Loan (₹)" icon={Car} value={form.carLoan}
          onChange={(v) => onChange('carLoan', v)} step={10000} />
        <WizardField label="Personal Debt (₹)" icon={CreditCard} value={form.personalDebt}
          onChange={(v) => onChange('personalDebt', v)} step={5000} />
      </div>
      {totalLiabilities > 0 && (
        <div className="wizard-summary-pill wizard-summary-amber mt-5">
          ⚠️ Total Liabilities: ₹{totalLiabilities.toLocaleString('en-IN')}
        </div>
      )}

      {/* Net Worth Summary */}
      <div className="mt-6 pt-5 border-t border-white/[0.04]">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-white/30 uppercase tracking-wider">Net Worth</span>
          <span className={`text-lg font-extrabold font-mono ${(totalAssets - totalLiabilities) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ₹{(totalAssets - totalLiabilities).toLocaleString('en-IN')}
          </span>
        </div>
      </div>
    </div>
  </div>
);

/* ═══════════════════════════════════════════════
   STEP 3 — Health
   ═══════════════════════════════════════════════ */
const HealthStep = ({ form, onChange }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {/* Lifestyle */}
    <div className="wizard-card">
      <CardHeader icon={Heart} label="Lifestyle" />
      <div className="space-y-5">
        <div>
          <label className="wizard-label">Smoking Status</label>
          <div className="grid grid-cols-2 gap-3">
            <ToggleCard
              active={!form.isSmoker}
              onClick={() => onChange('isSmoker', false)}
              emoji="🚭" label="Non-Smoker" />
            <ToggleCard
              active={form.isSmoker}
              onClick={() => onChange('isSmoker', true)}
              emoji="🚬" label="Smoker" />
          </div>
        </div>

        <div>
          <label className="wizard-label">Alcohol Consumption</label>
          <div className="grid grid-cols-2 gap-3">
            {['none', 'occasional', 'moderate', 'heavy'].map((level) => (
              <ToggleCard
                key={level}
                active={form.alcohol === level}
                onClick={() => onChange('alcohol', level)}
                label={level.charAt(0).toUpperCase() + level.slice(1)}
                emoji={level === 'none' ? '🚫' : level === 'occasional' ? '🍷' : level === 'moderate' ? '🍺' : '⚠️'}
                small
              />
            ))}
          </div>
        </div>
      </div>
    </div>

    {/* Medical */}
    <div className="wizard-card">
      <CardHeader icon={Shield} label="Medical History" />
      <div className="health-condition-card">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
            <Info className="w-5 h-5 text-indigo-400/60" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-white/60">Pre-existing severe conditions...</p>
            <p className="text-[11px] text-white/20 mt-0.5">Diabetes, heart disease, cancer, etc.</p>
          </div>
          <button
            onClick={() => onChange('hasSevereHealth', !form.hasSevereHealth)}
            className={`toggle-switch ${form.hasSevereHealth ? 'toggle-switch-on' : ''}`}
          >
            <motion.div
              className="toggle-thumb"
              animate={{ x: form.hasSevereHealth ? 20 : 0 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </button>
        </div>
      </div>

      {/* Health score preview */}
      <div className="mt-6 p-5 rounded-xl border border-white/[0.04] bg-white/[0.01]">
        <p className="text-[10px] font-bold text-white/20 uppercase tracking-[2px] mb-3">Health Risk Preview</p>
        <div className="space-y-2.5">
          <HealthBar label="Smoking" value={form.isSmoker ? 10 : 0} max={10} color="#ef4444" />
          <HealthBar label="Alcohol" value={form.alcohol === 'none' ? 0 : form.alcohol === 'occasional' ? 2 : form.alcohol === 'moderate' ? 5 : 8} max={8} color="#f59e0b" />
          <HealthBar label="Conditions" value={form.hasSevereHealth ? 7 : 0} max={7} color="#8b5cf6" />
        </div>
      </div>
    </div>
  </div>
);

/* ═══════════════════════════════════════════════
   STEP 4 — Review
   ═══════════════════════════════════════════════ */
const ReviewStep = ({ form, totalDependents, totalAssets, totalLiabilities }) => {
  const goalLabel = GOAL_OPTIONS.find(g => g.value === form.insuranceGoal);
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Summary */}
      <div className="wizard-card">
        <CardHeader icon={User} label="Profile Summary" />
        <div className="space-y-3">
          <ReviewRow label="Name" value={form.name || 'Not provided'} />
          <ReviewRow label="Age" value={`${form.age} years`} />
          <ReviewRow label="Annual Income" value={`₹${form.income.toLocaleString('en-IN')}`} />
          <ReviewRow label="Dependents" value={`${totalDependents} person${totalDependents !== 1 ? 's' : ''}`} />
          <ReviewRow label="Insurance Goal" value={goalLabel?.label || form.insuranceGoal} emoji={goalLabel?.emoji} />
        </div>
      </div>

      {/* Financials & Health */}
      <div className="wizard-card">
        <CardHeader icon={PiggyBank} label="Financial & Health" />
        <div className="space-y-3">
          <ReviewRow label="Total Assets" value={`₹${totalAssets.toLocaleString('en-IN')}`} color="text-emerald-400" />
          <ReviewRow label="Total Liabilities" value={`₹${totalLiabilities.toLocaleString('en-IN')}`} color="text-amber-400" />
          <ReviewRow label="Net Worth" value={`₹${(totalAssets - totalLiabilities).toLocaleString('en-IN')}`}
            color={(totalAssets - totalLiabilities) >= 0 ? 'text-emerald-400' : 'text-red-400'} />
          <div className="pt-2 border-t border-white/[0.04]" />
          <ReviewRow label="Smoker" value={form.isSmoker ? 'Yes' : 'No'} />
          <ReviewRow label="Alcohol" value={form.alcohol.charAt(0).toUpperCase() + form.alcohol.slice(1)} />
          <ReviewRow label="Severe Conditions" value={form.hasSevereHealth ? 'Yes' : 'No'} />
        </div>

        {/* Ready pill */}
        <div className="mt-6 p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/15 flex items-center gap-3">
          <Rocket className="w-5 h-5 text-indigo-400" />
          <div>
            <p className="text-sm font-semibold text-indigo-300">Ready to analyze</p>
            <p className="text-[11px] text-white/20">Click "Run Agent Pipeline" to get your recommendation</p>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
   Shared sub-components
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ */

const CardHeader = ({ icon: Icon, label }) => (
  <div className="flex items-center gap-3 mb-5">
    <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center">
      <Icon className="w-4.5 h-4.5 text-indigo-400/60" />
    </div>
    <span className="text-base font-bold text-white/80">{label}</span>
  </div>
);

const WizardField = ({ label, value, onChange, icon: Icon, type = 'number', step = 1, min = 0, max, placeholder }) => (
  <div>
    <label className="wizard-label">{label}</label>
    <div className="relative">
      {Icon && <Icon className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/15" />}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(type === 'number' ? Number(e.target.value) : e.target.value)}
        step={step} min={min} max={max} placeholder={placeholder}
        className={`input-dark ${Icon ? 'pl-12' : ''}`}
      />
    </div>
  </div>
);

const DependentCard = ({ label, emoji, value, onChange, max }) => (
  <div className="dependent-card">
    <span className="text-lg block mb-1">{emoji}</span>
    <span className="text-xs font-semibold text-white/50 block mb-2">{label}</span>
    <div className="flex items-center gap-2">
      <button onClick={() => onChange(Math.max(0, value - 1))}
        className="counter-btn">
        <Minus className="w-3 h-3" />
      </button>
      <input type="number" value={value} min={0} max={max}
        onChange={(e) => onChange(Math.min(max, Math.max(0, Number(e.target.value))))}
        className="counter-input" />
      <button onClick={() => onChange(Math.min(max, value + 1))}
        className="counter-btn">
        <Plus className="w-3 h-3" />
      </button>
    </div>
    <span className="text-lg font-bold text-white/60 mt-1 block">{value}</span>
  </div>
);

const SpouseCard = ({ hasSpouse, onChange }) => (
  <div className="dependent-card">
    <span className="text-lg block mb-1">👫</span>
    <span className="text-xs font-semibold text-white/50 block mb-2">Spouse</span>
    <div className="flex gap-2 mt-1">
      <button onClick={() => onChange(false)}
        className={`spouse-toggle ${!hasSpouse ? 'spouse-toggle-active' : ''}`}>
        No
      </button>
      <button onClick={() => onChange(true)}
        className={`spouse-toggle ${hasSpouse ? 'spouse-toggle-active' : ''}`}>
        Yes
      </button>
    </div>
  </div>
);

const ToggleCard = ({ active, onClick, emoji, label, small }) => (
  <button onClick={onClick}
    className={`toggle-card ${active ? 'toggle-card-active' : ''} ${small ? 'py-3' : 'py-4'}`}>
    <span className={`${small ? 'text-lg' : 'text-2xl'} block mb-1`}>{emoji}</span>
    <span className="text-[12px] font-semibold">{label}</span>
  </button>
);

const HealthBar = ({ label, value, max, color }) => (
  <div className="flex items-center gap-3">
    <span className="text-[11px] text-white/30 w-20 text-right font-medium">{label}</span>
    <div className="flex-1 h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: max > 0 ? `${(value / max) * 100}%` : '0%' }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="h-full rounded-full"
        style={{ background: color }}
      />
    </div>
    <span className="text-[11px] font-mono text-white/25 w-8">+{value}</span>
  </div>
);

const ReviewRow = ({ label, value, emoji, color }) => (
  <div className="flex items-center justify-between py-2 border-b border-white/[0.03] last:border-0">
    <span className="text-sm text-white/30">{label}</span>
    <span className={`text-sm font-semibold ${color || 'text-white/70'} flex items-center gap-1.5`}>
      {emoji && <span>{emoji}</span>}
      {value}
    </span>
  </div>
);

export default InputForm;
