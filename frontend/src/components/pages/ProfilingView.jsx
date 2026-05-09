/* ═══════════════════════════════════════════════════════════════════════════
   components/pages/ProfilingView.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Full-page User Profiling tab. This is the ONLY place where the user
   enters their data. Includes name, financial details, insurance goal,
   and health profile. No hardcoded data — all from controlled state.
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState, useCallback, useEffect } from 'react';
import { Send, RotateCcw, User, Wallet, Heart, Loader } from 'lucide-react';
import { supabase } from '../../api/supabase';

/* Default values matching the backend's UserInput defaults */
const DEFAULTS = {
  name: '',
  age: '',
  income: '',
  dependents: '',
  assets: '',
  liabilities: '',
  insurance_goal: 'family_protection',
  is_smoker: false,
  alcohol_consumption: 'none',
  has_severe_health_issues: false,
};

const GOALS = [
  { value: 'family_protection', label: 'Family Protection' },
  { value: 'health_security',   label: 'Health Security' },
  { value: 'wealth_protection', label: 'Wealth Protection' },
  { value: 'tax_savings',       label: 'Tax Savings' },
  { value: 'car_insurance',     label: 'Car Insurance' },
  { value: 'home_insurance',    label: 'Home Insurance' },
];

const ALCOHOL_OPTIONS = [
  { value: 'none',       label: 'None' },
  { value: 'occasional', label: 'Occasional' },
  { value: 'moderate',   label: 'Moderate' },
  { value: 'heavy',      label: 'Heavy' },
];

/* ── Shared input styles ─────────────────────────────────────────────── */
const inputClass =
  'w-full px-3 py-2.5 text-sm rounded-xl border transition-colors duration-200 outline-none ' +
  'focus:ring-2 focus:ring-[var(--color-sand-light)]';

const inputStyle = {
  borderColor: 'var(--color-border-soft)',
  backgroundColor: 'var(--color-surface)',
  color: 'var(--color-text-primary)',
};

export default function ProfilingView({ user, onSubmit, isLoading, hasResults, onViewResults }) {
  const [form, setForm] = useState({ ...DEFAULTS });
  const [isFetchingProfile, setIsFetchingProfile] = useState(true);

  /* Load user profile from Supabase */
  useEffect(() => {
    async function loadProfile() {
      if (!user) {
        setIsFetchingProfile(false);
        return;
      }
      try {
        const { data, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single();
        
        if (data && !error) {
          // Remove id from form state before merging
          const { id, ...profileData } = data;
          setForm((prev) => ({ ...prev, ...profileData }));
        }
      } catch (err) {
        console.error('Could not load profile from Supabase. Table might not exist yet.', err);
      } finally {
        setIsFetchingProfile(false);
      }
    }
    loadProfile();
  }, [user]);

  /* Update a single field */
  const set = useCallback((key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  }, []);

  /* Submit handler — coerce numerics before sending */
  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      age: Number(form.age) || 30,
      income: Number(form.income) || 0,
      dependents: Number(form.dependents) || 0,
      assets: Number(form.assets) || 0,
      liabilities: Number(form.liabilities) || 0,
    };

    /* Background sync to Supabase */
    if (user) {
      try {
        const { error } = await supabase
          .from('profiles')
          .upsert({ id: user.id, ...payload });
        
        if (error) {
          console.error('Supabase Upsert Error:', error.message, error.details);
          alert(`Failed to save to database: ${error.message}\n(Make sure the 'profiles' table exists and RLS is disabled/configured)`);
        } else {
          console.log('Profile saved to Supabase successfully.');
        }
      } catch (err) {
        console.error('Network/Unexpected error during Supabase sync', err);
      }
    }

    onSubmit(payload);
  };

  const handleReset = () => setForm({ ...DEFAULTS });

  if (isFetchingProfile) {
    return (
      <div className="flex flex-col items-center justify-center py-20" style={{ color: 'var(--color-text-muted)' }}>
        <Loader size={24} className="animate-spin mb-4" />
        <p className="text-sm">Loading your profile...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl" id="profiling-view">
      {/* ── Success banner ───────────────────────────────────────── */}
      {hasResults && (
        <div
          className="card flex items-center justify-between px-5 py-3 mb-5"
          style={{ borderLeft: '3px solid var(--color-success)' }}
        >
          <p className="text-[13px] font-medium" style={{ color: 'var(--color-text-primary)' }}>
            ✓ Recommendation ready. You can update inputs and re-run, or view results.
          </p>
          <button className="btn-soft text-[11px]" onClick={onViewResults}>
            View Results →
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* ── Section 1: Personal Information ─────────────────────── */}
        <div className="card p-6 mb-4">
          <div className="flex items-center gap-2 mb-5">
            <User size={16} style={{ color: 'var(--color-info)' }} />
            <h3
              className="text-base font-semibold"
              style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-text-primary)' }}
            >
              Personal Information
            </h3>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Name */}
            <label className="flex flex-col gap-1.5 col-span-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Full Name
              </span>
              <input
                id="input-name"
                type="text"
                placeholder="Enter your name"
                className={inputClass}
                style={inputStyle}
                value={form.name}
                onChange={(e) => set('name', e.target.value)}
              />
            </label>

            {/* Age */}
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Age
              </span>
              <input
                id="input-age"
                type="number"
                min={18}
                max={70}
                placeholder="30"
                className={inputClass}
                style={inputStyle}
                value={form.age}
                onChange={(e) => set('age', e.target.value)}
              />
            </label>

            {/* Dependents */}
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Dependents
              </span>
              <input
                id="input-dependents"
                type="number"
                min={0}
                max={10}
                placeholder="0"
                className={inputClass}
                style={inputStyle}
                value={form.dependents}
                onChange={(e) => set('dependents', e.target.value)}
              />
            </label>

            {/* Insurance Goal */}
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Insurance Goal
              </span>
              <select
                id="input-goal"
                className={inputClass}
                style={inputStyle}
                value={form.insurance_goal}
                onChange={(e) => set('insurance_goal', e.target.value)}
              >
                {GOALS.map((g) => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </label>
          </div>
        </div>

        {/* ── Section 2: Financial Details ────────────────────────── */}
        <div className="card p-6 mb-4">
          <div className="flex items-center gap-2 mb-5">
            <Wallet size={16} style={{ color: 'var(--color-sand-dark)' }} />
            <h3
              className="text-base font-semibold"
              style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-text-primary)' }}
            >
              Financial Details
            </h3>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Income */}
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Annual Income (₹)
              </span>
              <input
                id="input-income"
                type="number"
                min={0}
                placeholder="600000"
                className={inputClass}
                style={inputStyle}
                value={form.income}
                onChange={(e) => set('income', e.target.value)}
              />
            </label>

            {/* Assets */}
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Total Assets (₹)
              </span>
              <input
                id="input-assets"
                type="number"
                min={0}
                placeholder="0"
                className={inputClass}
                style={inputStyle}
                value={form.assets}
                onChange={(e) => set('assets', e.target.value)}
              />
            </label>

            {/* Liabilities */}
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Total Liabilities (₹)
              </span>
              <input
                id="input-liabilities"
                type="number"
                min={0}
                placeholder="0"
                className={inputClass}
                style={inputStyle}
                value={form.liabilities}
                onChange={(e) => set('liabilities', e.target.value)}
              />
            </label>
          </div>
        </div>

        {/* ── Section 3: Health Profile ───────────────────────────── */}
        <div className="card p-6 mb-5">
          <div className="flex items-center gap-2 mb-5">
            <Heart size={16} style={{ color: 'var(--color-danger)' }} />
            <h3
              className="text-base font-semibold"
              style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-text-primary)' }}
            >
              Health Profile
            </h3>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Smoker */}
            <label className="flex items-center gap-3 cursor-pointer card px-4 py-3">
              <input
                id="input-smoker"
                type="checkbox"
                checked={form.is_smoker}
                onChange={(e) => set('is_smoker', e.target.checked)}
                className="accent-[var(--color-sand)] w-4 h-4"
              />
              <div>
                <p className="text-[12px] font-medium" style={{ color: 'var(--color-text-primary)' }}>Smoker</p>
                <p className="text-[10px]" style={{ color: 'var(--color-text-muted)' }}>Regular tobacco use</p>
              </div>
            </label>

            {/* Severe Health Issues */}
            <label className="flex items-center gap-3 cursor-pointer card px-4 py-3">
              <input
                id="input-severe-health"
                type="checkbox"
                checked={form.has_severe_health_issues}
                onChange={(e) => set('has_severe_health_issues', e.target.checked)}
                className="accent-[var(--color-sand)] w-4 h-4"
              />
              <div>
                <p className="text-[12px] font-medium" style={{ color: 'var(--color-text-primary)' }}>Severe Issues</p>
                <p className="text-[10px]" style={{ color: 'var(--color-text-muted)' }}>Pre-existing conditions</p>
              </div>
            </label>

            {/* Alcohol */}
            <label className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>
                Alcohol Consumption
              </span>
              <select
                id="input-alcohol"
                className={inputClass}
                style={inputStyle}
                value={form.alcohol_consumption}
                onChange={(e) => set('alcohol_consumption', e.target.value)}
              >
                {ALCOHOL_OPTIONS.map((a) => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            </label>
          </div>
        </div>

        {/* ── Actions ─────────────────────────────────────────────── */}
        <div className="flex items-center gap-3">
          <button
            id="btn-submit"
            type="submit"
            disabled={isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={14} />
            {isLoading ? 'Processing…' : 'Get Recommendation'}
          </button>
          <button
            id="btn-reset"
            type="button"
            onClick={handleReset}
            className="btn-soft"
          >
            <RotateCcw size={14} />
            Reset
          </button>
        </div>
      </form>
    </div>
  );
}
