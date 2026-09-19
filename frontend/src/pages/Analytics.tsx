import { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { api, type AnalyticsOut, ApiError } from '../lib/api';
import { LoadingState, ErrorState, EmptyState } from '../components/States';

export default function Analytics() {
  const [data, setData] = useState<AnalyticsOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setError(null);
    api.get<AnalyticsOut>('/analytics/progress')
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load analytics.'));
  }
  useEffect(load, []);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return <LoadingState label="Crunching your progress data…" />;

  const verified = data.verified_vs_unverified.verified ?? 0;
  const unverified = data.verified_vs_unverified.unverified ?? 0;

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="font-display mb-6 text-3xl">Progress Analytics</h1>

      <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-3 text-lg">Readiness trend</h2>
        {data.readiness_trend.length === 0 ? (
          <EmptyState title="No readiness history yet" description="Run a gap analysis or complete an assessment to start tracking your trend." />
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={data.readiness_trend}>
              <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="overall_readiness" stroke="var(--amber-deep)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </section>

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
        <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
          <h2 className="font-display mb-3 text-lg">Skill category distribution</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.category_distribution} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
              <YAxis dataKey="category" type="category" width={110} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="average_level" fill="var(--teal)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
          <h2 className="font-display mb-3 text-lg">Verified vs. unverified</h2>
          <div className="flex items-center justify-center gap-10 py-8">
            <div className="text-center">
              <p className="font-mono text-4xl" style={{ color: 'var(--teal)' }}>{verified}</p>
              <p className="text-sm text-[var(--slate)]">Verified</p>
            </div>
            <div className="text-center">
              <p className="font-mono text-4xl text-[var(--slate)]">{unverified}</p>
              <p className="text-sm text-[var(--slate)]">Unverified</p>
            </div>
          </div>
        </section>
      </div>

      {data.assessment_scores.length > 0 && (
        <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
          <h2 className="font-display mb-3 text-lg">Assessment scores</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.assessment_scores}>
              <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
              <XAxis dataKey="skill" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="percent" fill="var(--amber)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      )}

      {data.top_remaining_gaps.length > 0 && (
        <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
          <h2 className="font-display mb-3 text-lg">Top remaining gaps</h2>
          <ol className="list-decimal pl-5 text-sm">
            {data.top_remaining_gaps.map((g) => <li key={g}>{g}</li>)}
          </ol>
        </section>
      )}
    </div>
  );
}
