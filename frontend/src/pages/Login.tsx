import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../lib/api';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('demo.student@careerlens.ai');
  const [password, setPassword] = useState('DemoPass123!');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not log in. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center" style={{ background: 'var(--ink)' }}>
      <div className="w-full max-w-sm rounded-2xl p-8" style={{ background: 'var(--paper-raised)' }}>
        <div className="mb-6 flex items-center gap-2">
          <span className="font-mono text-xl" style={{ color: 'var(--amber-deep)' }}>◈</span>
          <span className="font-display text-xl">CareerLens AI</span>
        </div>
        <h1 className="font-display mb-1 text-2xl">Welcome back</h1>
        <p className="mb-6 text-sm text-[var(--slate)]">
          Sign in to see where you stand against your target career.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1 text-sm">
            Email
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="focus-ring rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Password
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="focus-ring rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
            />
          </label>
          {error && <p className="text-sm text-[var(--coral)]">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="focus-ring mt-2 rounded-full py-2 text-sm font-medium text-white disabled:opacity-60"
            style={{ background: 'var(--ink)' }}
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <p className="mt-5 text-center text-xs text-[var(--slate)]">
          Demo account pre-filled above — just click Sign in.
        </p>
        <p className="mt-3 text-center text-sm">
          New here?{' '}
          <Link to="/register" className="font-medium underline">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
