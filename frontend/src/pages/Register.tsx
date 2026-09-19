import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../lib/api';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: '', email: '', password: '', college: '', degree: '', department: '', graduation_year: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function set<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register({
        ...form,
        graduation_year: form.graduation_year ? Number(form.graduation_year) : undefined,
      });
      navigate('/onboarding');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not create your account.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center py-10" style={{ background: 'var(--ink)' }}>
      <div className="w-full max-w-md rounded-2xl p-8" style={{ background: 'var(--paper-raised)' }}>
        <div className="mb-6 flex items-center gap-2">
          <span className="font-mono text-xl" style={{ color: 'var(--amber-deep)' }}>◈</span>
          <span className="font-display text-xl">CareerLens AI</span>
        </div>
        <h1 className="font-display mb-1 text-2xl">Create your account</h1>
        <p className="mb-6 text-sm text-[var(--slate)]">Start building your evidence-based career profile.</p>
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-3">
          <Field label="Full name" full>
            <input required value={form.full_name} onChange={(e) => set('full_name', e.target.value)} className="fld" />
          </Field>
          <Field label="Email" full>
            <input type="email" required value={form.email} onChange={(e) => set('email', e.target.value)} className="fld" />
          </Field>
          <Field label="Password" full>
            <input type="password" required minLength={6} value={form.password} onChange={(e) => set('password', e.target.value)} className="fld" />
          </Field>
          <Field label="College">
            <input value={form.college} onChange={(e) => set('college', e.target.value)} className="fld" />
          </Field>
          <Field label="Degree">
            <input value={form.degree} onChange={(e) => set('degree', e.target.value)} className="fld" placeholder="B.Tech" />
          </Field>
          <Field label="Department">
            <input value={form.department} onChange={(e) => set('department', e.target.value)} className="fld" />
          </Field>
          <Field label="Graduation year">
            <input type="number" value={form.graduation_year} onChange={(e) => set('graduation_year', e.target.value)} className="fld" placeholder="2027" />
          </Field>
          {error && <p className="col-span-2 text-sm text-[var(--coral)]">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="focus-ring col-span-2 mt-2 rounded-full py-2 text-sm font-medium text-white disabled:opacity-60"
            style={{ background: 'var(--ink)' }}
          >
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>
        <p className="mt-5 text-center text-sm">
          Already have an account?{' '}
          <Link to="/login" className="font-medium underline">
            Sign in
          </Link>
        </p>
      </div>
      <style>{`.fld { border: 1px solid var(--line); border-radius: 0.5rem; padding: 0.5rem 0.75rem; font-size: 0.875rem; width: 100%; }`}</style>
    </div>
  );
}

function Field({ label, children, full }: { label: string; children: React.ReactNode; full?: boolean }) {
  return (
    <label className={`flex flex-col gap-1 text-sm ${full ? 'col-span-2' : ''}`}>
      {label}
      {children}
    </label>
  );
}
