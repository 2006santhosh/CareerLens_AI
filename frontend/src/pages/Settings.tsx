import { useState } from 'react';
import { api, type JobDescriptionMatchOut, ApiError } from '../lib/api';

export default function Settings() {
  const [jobText, setJobText] = useState('');
  const [result, setResult] = useState<JobDescriptionMatchOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function analyze() {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.post<JobDescriptionMatchOut>('/job-description/analyze', { text: jobText });
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not analyze this job description.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-display mb-6 text-3xl">Settings</h1>

      <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-2 text-lg">Job Description Matcher</h2>
        <p className="mb-3 text-sm text-[var(--slate)]">
          Paste a job description to see how your current skill profile matches, and what's missing.
        </p>
        <textarea
          value={jobText}
          onChange={(e) => setJobText(e.target.value)}
          rows={5}
          placeholder="Paste a job description here…"
          className="focus-ring w-full rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
        />
        <button
          onClick={analyze}
          disabled={busy || !jobText.trim()}
          className="focus-ring mt-3 rounded-full px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          style={{ background: 'var(--ink)' }}
        >
          {busy ? 'Analyzing…' : 'Analyze match'}
        </button>
        {error && <p className="mt-3 text-sm text-[var(--coral)]">{error}</p>}
        {result && (
          <div className="mt-4 rounded-lg border border-[var(--line)] p-4">
            <p className="font-mono text-2xl">{result.match_percent}% match</p>
            <p className="mt-2 text-sm"><strong>Matched:</strong> {result.matched_skills.join(', ') || '—'}</p>
            <p className="mt-1 text-sm"><strong>Missing:</strong> {result.missing_skills.join(', ') || '—'}</p>
          </div>
        )}
      </section>

      <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-2 text-lg">About CareerLens AI</h2>
        <p className="text-sm text-[var(--slate)]">
          Career Readiness is a transparent measure of demonstrated skill coverage against your selected
          target role — not a prediction or guarantee of a job offer. All gap, roadmap, and readiness
          calculations are deterministic and explainable; AI is used only for resume understanding and
          natural-language explanations.
        </p>
      </section>
    </div>
  );
}
