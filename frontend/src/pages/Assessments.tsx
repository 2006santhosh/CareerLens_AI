import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, type AssessmentListItem, ApiError } from '../lib/api';
import { LoadingState, ErrorState } from '../components/States';

export default function Assessments() {
  const [items, setItems] = useState<AssessmentListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setError(null);
    api.get<AssessmentListItem[]>('/assessments')
      .then(setItems)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load assessments.'));
  }
  useEffect(load, []);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!items) return <LoadingState label="Loading assessments…" />;

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display mb-2 text-3xl">Assessments</h1>
      <p className="mb-6 text-sm text-[var(--slate)]">
        Pass an assessment to move a skill from self-reported toward Verified.
      </p>
      <ul className="flex flex-col gap-3">
        {items.map((a) => (
          <li key={a.id} className="flex items-center justify-between rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-4">
            <div>
              <p className="font-medium">{a.title}</p>
              <p className="text-xs text-[var(--slate)]">
                {a.question_count} questions · {a.attempts} attempt{a.attempts === 1 ? '' : 's'}
                {a.best_percent != null && ` · best score ${Math.round(a.best_percent)}%`}
              </p>
            </div>
            <Link
              to={`/assessments/${a.id}`}
              className="focus-ring rounded-full px-4 py-1.5 text-sm font-medium"
              style={{ background: 'var(--ink)', color: 'white' }}
            >
              {a.attempts > 0 ? 'Retake' : 'Start'}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
