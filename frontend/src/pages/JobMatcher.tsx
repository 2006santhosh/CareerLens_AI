import { useState } from 'react';
import { api, type JobDescriptionMatchOut, ApiError } from '../lib/api';

export default function JobMatcher() {
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
      <h1 className="font-display mb-6 text-3xl">Job Description Matcher</h1>

      <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <p className="mb-4 text-sm text-[var(--slate)]">
          Paste a job description to see how your current skill profile matches. The AI will extract the required skills, generate a custom target career for this specific job, and allow you to build an adaptive roadmap for it.
        </p>
        <textarea
          value={jobText}
          onChange={(e) => setJobText(e.target.value)}
          rows={8}
          placeholder="Paste a job description here…"
          className="focus-ring w-full rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
        />
        <button
          onClick={analyze}
          disabled={busy || !jobText.trim()}
          className="focus-ring mt-3 rounded-full px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          style={{ background: 'var(--ink)' }}
        >
          {busy ? 'Analyzing…' : 'Analyze Match & Build Custom Roadmap'}
        </button>
        {error && <p className="mt-3 text-sm text-[var(--coral)]">{error}</p>}
        {result && (
          <div className="mt-6 rounded-lg border border-[var(--line)] p-5">
            <p className="font-mono text-3xl mb-2">{result.match_percent}% match</p>
            <p className="mt-2 text-sm text-[var(--teal)] font-medium"><strong>Matched:</strong> {result.matched_skills.join(', ') || 'None'}</p>
            <p className="mt-1 text-sm text-[var(--coral)] font-medium"><strong>Missing:</strong> {result.missing_skills.join(', ') || 'None'}</p>
            {result.career_id && (
              <a 
                href={`/careers/${result.career_id}`} 
                className="mt-6 inline-block focus-ring rounded-full px-5 py-2 text-sm font-medium text-white shadow-sm"
                style={{ background: 'var(--teal)' }}
              >
                View Target Profile & Build Roadmap
              </a>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
