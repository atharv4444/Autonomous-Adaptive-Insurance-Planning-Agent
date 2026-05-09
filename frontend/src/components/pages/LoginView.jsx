/* ═══════════════════════════════════════════════════════════════════════════
   components/pages/LoginView.jsx
   ═══════════════════════════════════════════════════════════════════════════
   Authentication page with Supabase integration.
   Toggles between Sign In and Sign Up.
   Matches the requested soft, warm aesthetic.
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState } from 'react';
import { ShieldCheck, Loader } from 'lucide-react';
import { supabase } from '../../api/supabase';

export default function LoginView({ onLogin }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (!import.meta.env.VITE_SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL.includes('YOUR_SUPABASE')) {
        throw new Error('Supabase is not configured. Please add keys to frontend/.env');
      }

      let data, err;
      if (isSignUp) {
        const res = await supabase.auth.signUp({ email, password });
        data = res.data;
        err = res.error;
        if (!err && data?.user) {
          // Auto-login or show success message depending on confirm email settings
          // For now, assuming email confirmation is disabled for prototyping
          onLogin(data.user);
        }
      } else {
        const res = await supabase.auth.signInWithPassword({ email, password });
        data = res.data;
        err = res.error;
        if (!err && data?.user) {
          onLogin(data.user);
        }
      }

      if (err) throw err;

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-cream-dark)' }}>
      <div className="card w-full max-w-md p-10 bg-white shadow-2xl relative" style={{ borderRadius: '20px' }}>
        
        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-14 h-14 rounded-full flex items-center justify-center shadow-inner" style={{ backgroundColor: 'var(--color-espresso)' }}>
            <ShieldCheck size={28} style={{ color: 'var(--color-sand)' }} />
          </div>
        </div>

        {/* Headings */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold mb-2 text-gray-900" style={{ fontFamily: 'var(--font-serif)' }}>
            {isSignUp ? 'Create Account' : 'Welcome Back'}
          </h1>
          <p className="text-sm font-medium" style={{ color: 'var(--color-text-secondary)' }}>
            InsuraX Planning Dashboard
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg text-sm bg-red-50 text-red-600 border border-red-100 text-center">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--color-espresso-muted)' }}>
              Email Address
            </label>
            <input
              type="email"
              required
              className="w-full px-4 py-3 rounded-md text-sm border focus:ring-2 outline-none transition-all"
              style={{
                backgroundColor: 'var(--color-cream)',
                borderColor: 'var(--color-border-soft)',
                color: 'var(--color-text-primary)'
              }}
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--color-espresso-muted)' }}>
              Password
            </label>
            <input
              type="password"
              required
              className="w-full px-4 py-3 rounded-md text-sm border focus:ring-2 outline-none transition-all"
              style={{
                backgroundColor: 'var(--color-cream)',
                borderColor: 'var(--color-border-soft)',
                color: 'var(--color-text-primary)'
              }}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-md text-sm font-bold shadow-md transition-transform flex items-center justify-center gap-2 hover:-translate-y-0.5"
            style={{
              backgroundColor: 'var(--color-espresso-light)',
              color: 'var(--color-cream)',
            }}
          >
            {loading ? <Loader size={16} className="animate-spin" /> : (isSignUp ? 'Sign Up' : 'Sign In')}
          </button>
        </form>

        <div className="mt-8 text-center text-[12px] font-medium" style={{ color: 'var(--color-text-secondary)' }}>
          {isSignUp ? 'Already have an account? ' : 'New user? '}
          <button
            onClick={() => { setIsSignUp(!isSignUp); setError(null); }}
            className="hover:underline font-bold"
            style={{ color: 'var(--color-espresso)' }}
          >
            {isSignUp ? 'Sign in' : 'Create an account'}
          </button>
        </div>
      </div>
    </div>
  );
}
