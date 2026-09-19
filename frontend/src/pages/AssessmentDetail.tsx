import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, type AssessmentDetail as AssessmentDetailType, type AssessmentResult, ApiError } from '../lib/api';
import { LoadingState, ErrorState } from '../components/States';

export default function AssessmentDetail() {
  const { id } = useParams();
  const [assessment, setAssessment] = useState<AssessmentDetailType | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function load() {
    if (!id) return;
    setError(null);
    api.get<AssessmentDetailType>(`/assessments/${id}`)
      .then(setAssessment)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load this assessment.'));
  }
  useEffect(load, [id]);

  async function submit() {
    if (!id || !assessment) return;
    if (Object.keys(answers).length < assessment.questions.length) {
      setError('Please answer every question before submitting.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.post<AssessmentResult>(`/assessments/${id}/submit`, { answers });
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not submit your answers.');
    } finally {
      setSubmitting(false);
    }
  }

  if (error && !assessment) return <ErrorState message={error} onRetry={load} />;
  if (!assessment) return <LoadingState label="Loading assessment…" />;

  if (result) {
    return (
      <div className="mx-auto max-w-xl text-center">
        <h1 className="font-display mb-2 text-3xl">Assessment complete</h1>
        <p className="font-mono mb-6 text-5xl" style={{ color: result.percent >= 70 ? 'var(--teal)' : 'var(--amber)' }}>
          {result.score}/{result.total}
        </p>
        <p className="mb-2 text-sm text-[var(--slate)]">
          {assessment.skill.name} skill level: {result.previous_skill_level} → <strong>{result.updated_skill_level}</strong>
        </p>
        <p className="mb-6 text-sm text-[var(--slate)]">New status: <strong>{result.new_status.replace('_', ' ')}</strong></p>
        {result.roadmap_updated && (
          <p className="mb-6 rounded-lg border border-[var(--line)] bg-[var(--paper-raised)] px-4 py-3 text-sm">
            Your roadmap has been updated based on your latest assessment.
          </p>
        )}
        <div className="flex justify-center gap-3">
          <Link to="/roadmap" className="focus-ring rounded-full px-4 py-2 text-sm font-medium text-white" style={{ background: 'var(--ink)' }}>
            View updated roadmap
          </Link>
          <Link to="/dashboard" className="focus-ring rounded-full border border-[var(--line)] px-4 py-2 text-sm">
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <p className="font-mono mb-1 text-xs text-[var(--slate)]">{assessment.skill.name.toUpperCase()}</p>
      <h1 className="font-display mb-6 text-3xl">{assessment.title}</h1>
      <div className="flex flex-col gap-6">
        {assessment.questions.map((q, idx) => (
          <div key={q.id} className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-4">
            <p className="mb-3 text-sm font-medium">{idx + 1}. {q.prompt}</p>
            <div className="flex flex-col gap-2">
              {q.options.map((opt, oi) => (
                <label key={oi} className={`focus-ring flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
                  answers[q.id] === oi ? 'border-[var(--ink)]' : 'border-[var(--line)]'
                }`}>
                  <input
                    type="radio"
                    name={q.id}
                    checked={answers[q.id] === oi}
                    onChange={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
      {error && <p className="mt-4 text-sm text-[var(--coral)]">{error}</p>}
      <button
        onClick={submit}
        disabled={submitting}
        className="focus-ring mt-6 rounded-full px-5 py-2.5 text-sm font-medium text-white disabled:opacity-60"
        style={{ background: 'var(--amber-deep)' }}
      >
        {submitting ? 'Submitting…' : 'Submit assessment'}
      </button>
    </div>
  );
}
