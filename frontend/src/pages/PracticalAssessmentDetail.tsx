import { useState, useEffect, type FormEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, type PracticalAssessmentOut, type PracticalAssessmentResult, ApiError } from '../lib/api';
import { LoadingState, ErrorState } from '../components/States';
import { CheckCircle2, XCircle } from 'lucide-react';

export default function PracticalAssessmentDetail() {
  const { id } = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<PracticalAssessmentOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<PracticalAssessmentResult | null>(null);
  const [dockerfileContent, setDockerfileContent] = useState('');

  function load() {
    setError(null);
    api.get<PracticalAssessmentOut>(`/assessments/practical/${id}`)
      .then(setAssessment)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load assessment.'));
  }
  useEffect(load, [id]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.post<PracticalAssessmentResult>(`/assessments/practical/${id}/submit`, {
        files: {
          Dockerfile: dockerfileContent,
        },
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Failed to submit.');
    } finally {
      setSubmitting(false);
    }
  }

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!assessment) return <LoadingState label="Loading assessment…" />;

  if (result) {
    return (
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="font-display mb-4 text-3xl">Results</h1>
        <div className={`mb-6 inline-flex h-20 w-20 items-center justify-center rounded-full ${result.passed ? 'bg-[var(--teal)] text-white' : 'bg-[var(--coral)] text-white'}`}>
          <span className="text-2xl font-bold">{Math.round(result.score)}%</span>
        </div>
        <p className="mb-8 text-lg font-medium">
          {result.passed ? 'Assessment Passed! Skill Verified.' : 'Assessment Failed. Keep practicing!'}
        </p>

        <div className="text-left bg-[var(--paper-raised)] p-6 rounded-xl border border-[var(--line)] mb-8">
          <h2 className="font-medium mb-4">Feedback Breakdown</h2>
          <ul className="flex flex-col gap-3">
            {result.feedback.map((f, i) => (
              <li key={i} className="flex items-center gap-2 text-sm">
                {f.status === 'pass' ? <CheckCircle2 size={16} className="text-[var(--teal)]" /> : <XCircle size={16} className="text-[var(--coral)]" />}
                <span className={f.status === 'pass' ? 'text-[var(--teal)]' : 'text-[var(--coral)]'}>{f.check}</span>
              </li>
            ))}
          </ul>
        </div>

        {result.roadmap_updated && (
          <div className="mb-8 rounded-lg border border-[var(--teal)] bg-[var(--teal)]/10 p-4 text-sm text-[var(--teal)]">
            Your roadmap has been updated based on this verified skill!
          </div>
        )}

        <div className="flex justify-center gap-4">
          <Link
            to="/assessments"
            className="focus-ring rounded-full border border-[var(--line)] px-5 py-2 font-medium hover:bg-[var(--line)]"
          >
            Back to Assessments
          </Link>
          <Link
            to="/dashboard"
            className="focus-ring rounded-full px-5 py-2 font-medium text-white"
            style={{ background: 'var(--ink)' }}
          >
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-display mb-2 text-3xl">{assessment.title}</h1>
      <p className="mb-6 text-sm text-[var(--slate)]">
        {assessment.description}
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {assessment.validation_type === 'docker_containerize' && (
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium">Dockerfile Content</span>
            <span className="text-xs text-[var(--slate)] mb-2">Paste your Dockerfile contents here for validation.</span>
            <textarea
              className="focus-ring min-h-[200px] rounded-lg border border-[var(--line)] bg-[var(--paper-raised)] p-3 font-mono text-sm"
              value={dockerfileContent}
              onChange={(e) => setDockerfileContent(e.target.value)}
              required
              placeholder={`FROM python:3.9\n...\nCMD ["python", "app.py"]`}
            />
          </label>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="focus-ring mt-4 rounded-full px-4 py-2 font-medium text-white disabled:opacity-50"
          style={{ background: 'var(--ink)' }}
        >
          {submitting ? 'Evaluating...' : 'Submit Practical Check'}
        </button>
      </form>
    </div>
  );
}
