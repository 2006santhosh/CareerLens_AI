import { useEffect, useState } from 'react';
import { api, type ProfileOut, type Career, ApiError } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { LoadingState, ErrorState } from '../components/States';

const HOURS_OPTIONS = ['1-3', '3-5', '5-10', '10+'];

export default function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileOut | null>(null);
  const [careers, setCareers] = useState<Career[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  function load() {
    setLoading(true);
    Promise.all([api.get<ProfileOut>('/profile'), api.get<Career[]>('/careers')])
      .then(([p, c]) => { setProfile(p); setCareers(c); })
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load your profile.'))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  async function saveField(update: Record<string, unknown>) {
    if (!profile) return;
    setSaving(true);
    setSavedMsg(null);
    try {
      const updated = await api.put<ProfileOut>('/profile', update);
      setProfile(updated);
      setSavedMsg('Saved.');
    } catch {
      setError('Could not save your changes.');
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <LoadingState label="Loading your profile…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!profile) return null;

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-display mb-6 text-3xl">My Profile</h1>

      <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-3 text-lg">Personal & academic</h2>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <Row label="Full name" value={user?.full_name} />
          <Row label="Email" value={user?.email} />
          <Row label="College" value={user?.college} />
          <Row label="Degree" value={user?.degree} />
          <Row label="Department" value={user?.department} />
          <Row label="Graduation year" value={user?.graduation_year?.toString()} />
        </dl>
      </section>

      <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-3 text-lg">Target career</h2>
        <select
          value={profile.target_career_id ?? ''}
          onChange={(e) => saveField({ target_career_id: e.target.value })}
          className="focus-ring w-full rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
        >
          <option value="" disabled>Select a career…</option>
          {careers.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </section>

      <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-3 text-lg">Weekly learning availability</h2>
        <div className="flex gap-2">
          {HOURS_OPTIONS.map((h) => (
            <button
              key={h}
              onClick={() => saveField({ weekly_hours: h })}
              className={`focus-ring rounded-full border px-3 py-1.5 text-sm ${
                profile.weekly_hours === h ? 'border-[var(--ink)] bg-[var(--ink)] text-white' : 'border-[var(--line)]'
              }`}
            >
              {h} hrs/week
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-3 text-lg">GitHub username</h2>
        <GithubField initial={profile.github_username ?? ''} onSave={(v) => saveField({ github_username: v })} />
      </section>

      {saving && <p className="mt-4 text-sm text-[var(--slate)]">Saving…</p>}
      {savedMsg && !saving && <p className="mt-4 text-sm text-[var(--teal)]">{savedMsg}</p>}
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs text-[var(--slate)]">{label}</dt>
      <dd className="font-medium">{value || '—'}</dd>
    </div>
  );
}

function GithubField({ initial, onSave }: { initial: string; onSave: (v: string) => void }) {
  const [value, setValue] = useState(initial);
  return (
    <div className="flex gap-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="e.g. octocat"
        className="focus-ring flex-1 rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
      />
      <button
        onClick={() => onSave(value)}
        className="focus-ring rounded-full border border-[var(--line)] px-4 py-2 text-sm hover:border-[var(--ink)]"
      >
        Save
      </button>
    </div>
  );
}
