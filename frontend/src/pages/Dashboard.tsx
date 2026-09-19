import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import { api, type Dashboard as DashboardType, ApiError } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { LoadingState, ErrorState, EmptyState } from '../components/States';
import { Gauge } from '../components/Gauge';
import { ImportanceTag } from '../components/SkillBits';

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 18) return 'Good afternoon';
  return 'Good evening';
}

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    setError(null);
    api.get<DashboardType>('/dashboard')
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load your dashboard.'))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  if (loading) return <LoadingState label="Building your dashboard…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return null;

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl">{greeting()}, {user?.full_name?.split(' ')[0]}</h1>
          {data.target_career ? (
            <p className="mt-1 text-sm text-[var(--slate)]">
              Target career: <span className="font-medium text-[var(--ink-text)]">{data.target_career.name}</span>
            </p>
          ) : (
            <p className="mt-1 text-sm text-[var(--slate)]">No target career selected yet.</p>
          )}
        </div>
        {data.ai_mode === 'demo' && (
          <span className="font-mono flex items-center gap-1.5 rounded-full border border-[var(--line)] px-3 py-1 text-xs text-[var(--slate)]">
            <Sparkles size={13} /> Demo AI mode
          </span>
        )}
      </div>

      {!data.target_career ? (
        <EmptyState
          title="Select a target career to get started"
          description="Your dashboard, gap analysis, and roadmap all key off a target career."
          action={<Link to="/careers" className="mt-2 rounded-full px-4 py-2 text-sm font-medium text-white" style={{ background: 'var(--ink)' }}>Browse careers</Link>}
        />
      ) : (
        <>
          <div className="mb-8 grid grid-cols-1 gap-6 rounded-2xl border border-[var(--line)] bg-[var(--paper-raised)] p-6 sm:grid-cols-4">
            <Gauge value={data.readiness?.overall_readiness ?? 0} label="Career readiness" />
            <Gauge value={data.readiness?.skill_coverage ?? 0} label="Skill coverage" size={140} />
            <StatBlock
              value={`${data.verified_skills_count} / ${data.total_profile_skills}`}
              label="Verified skills"
            />
            <StatBlock value={`${Math.round(data.roadmap_progress_percent)}%`} label="Roadmap progress" />
          </div>

          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <section>
              <h2 className="font-display mb-3 text-lg">Top skill gaps</h2>
              {data.top_gaps.length === 0 ? (
                <p className="text-sm text-[var(--slate)]">No open gaps for your top-priority skills right now.</p>
              ) : (
                <ul className="divide-y divide-[var(--line)] rounded-xl border border-[var(--line)] bg-[var(--paper-raised)]">
                  {data.top_gaps.map((g) => (
                    <li key={g.skill.id} className="flex items-center justify-between px-4 py-3">
                      <div>
                        <p className="text-sm font-medium">{g.skill.name}</p>
                        <ImportanceTag importance={g.importance} />
                      </div>
                      <span className="font-mono text-sm text-[var(--slate)]">{g.current_level} → {g.required_level}</span>
                    </li>
                  ))}
                </ul>
              )}
              <Link to="/gap-analysis" className="mt-3 inline-flex items-center gap-1 text-sm font-medium underline">
                See full gap analysis <ArrowRight size={14} />
              </Link>
            </section>

            <section>
              <h2 className="font-display mb-3 text-lg">Your next best action</h2>
              <div className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-4">
                <p className="text-sm">{data.next_best_action}</p>
                <Link to="/roadmap" className="mt-3 inline-flex items-center gap-1 text-sm font-medium underline">
                  Go to roadmap <ArrowRight size={14} />
                </Link>
              </div>

              {data.roadmap_weeks.length > 0 && (
                <div className="mt-5">
                  <h3 className="font-display mb-2 text-base">Roadmap progress</h3>
                  <ol className="flex flex-col gap-1">
                    {data.roadmap_weeks.slice(0, 6).map((w) => (
                      <li key={w.week} className="flex items-center gap-2 text-sm">
                        <span
                          className="h-2 w-2 rounded-full"
                          style={{
                            background:
                              w.status === 'completed' ? 'var(--teal)' : w.status === 'in_progress' ? 'var(--amber)' : 'var(--line)',
                          }}
                        />
                        Week {w.week}: {w.skill}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </section>
          </div>

          {data.readiness && (
            <section>
              <h2 className="font-display mb-3 text-lg">Readiness breakdown</h2>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
                {(
                  [
                    ['Technical skills', data.readiness.technical_skills],
                    ['Project evidence', data.readiness.project_evidence],
                    ['Assessment', data.readiness.assessment_performance],
                    ['Skill coverage', data.readiness.skill_coverage],
                    ['Verification', data.readiness.verification],
                  ] as [string, number][]
                ).map(([label, val]) => (
                  <div key={label} className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-3">
                    <p className="font-mono text-xl">{Math.round(val)}%</p>
                    <p className="text-xs text-[var(--slate)]">{label}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}

function StatBlock({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2">
      <span className="font-mono text-3xl font-semibold">{value}</span>
      <span className="text-center text-sm text-[var(--slate)]">{label}</span>
    </div>
  );
}
