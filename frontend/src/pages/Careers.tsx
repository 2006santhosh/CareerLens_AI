import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, type Career, ApiError } from '../lib/api';
import { LoadingState, ErrorState } from '../components/States';

export default function Careers() {
  const [careers, setCareers] = useState<Career[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setError(null);
    api.get<Career[]>('/careers')
      .then(setCareers)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load careers.'));
  }
  useEffect(load, []);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!careers) return <LoadingState label="Loading career catalog…" />;

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="font-display mb-2 text-3xl">Career Explorer</h1>
      <p className="mb-6 text-sm text-[var(--slate)]">Browse curated career paths and see how your profile matches each one.</p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {careers.map((c) => (
          <Link
            key={c.id}
            to={`/careers/${c.id}`}
            className="focus-ring rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5 transition-shadow hover:shadow-md"
          >
            <h2 className="font-display text-lg">{c.name}</h2>
            <p className="mt-1 text-sm text-[var(--slate)]">{c.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
