import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, type GapAnalysis as GapAnalysisType, ApiError } from '../lib/api';
import { LoadingState, ErrorState, EmptyState } from '../components/States';
import { ImportanceTag } from '../components/SkillBits';

export default function GapAnalysis() {
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<GapAnalysisType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  function load() {
    setLoading(true);
    setError(null);
    api.post<GapAnalysisType>('/gap-analysis')
      .then(setAnalysis)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not run gap analysis.'))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  async function generateRoadmap() {
    setGenerating(true);
    try {
      await api.post('/roadmaps/generate');
      navigate('/roadmap');
    } catch {
      setError('Could not generate a roadmap right now.');
    } finally {
      setGenerating(false);
    }
  }

  if (loading) return <LoadingState label="Comparing your profile against the career requirements…" />;
  if (error) {
    if (error.toLowerCase().includes('target career')) {
      return (
        <EmptyState
          title="No target career selected"
          description="Choose a target career in Career Explorer to run a skill gap analysis."
        />
      );
    }
    return <ErrorState message={error} onRetry={load} />;
  }
  if (!analysis) return null;

  return (
    <div className="mx-auto max-w-3xl">
      <p className="font-mono mb-1 text-xs text-[var(--slate)]">TARGET CAREER</p>
      <h1 className="font-display mb-6 text-3xl">{analysis.career.name}</h1>

      <div className="mb-8 grid grid-cols-4 gap-4 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <Stat label="Skill coverage" value={`${Math.round(analysis.skill_coverage)}%`} />
        <Stat label="Strong skills" value={String(analysis.strong_skills)} color="var(--teal)" />
        <Stat label="Partial skills" value={String(analysis.partial_skills)} color="var(--amber)" />
        <Stat label="Critical gaps" value={String(analysis.critical_gaps)} color="var(--coral)" />
      </div>

      <section className="mb-8">
        <h2 className="font-display mb-3 text-lg">Skill-by-skill breakdown</h2>
        <ul className="flex flex-col gap-3">
          {analysis.gaps.map((g) => (
            <li key={g.skill.id} className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-4">
              <div className="mb-1 flex items-center justify-between">
                <span className="font-medium">{g.skill.name}</span>
                <div className="flex items-center gap-3">
                  <ImportanceTag importance={g.importance} />
                  <span className="font-mono text-sm text-[var(--slate)]">
                    {g.current_level} / {g.required_level}
                  </span>
                </div>
              </div>
              <div className="mb-2 h-1.5 w-full overflow-hidden rounded-full bg-[var(--line)]">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${Math.min(100, (g.current_level / g.required_level) * 100)}%`,
                    background: g.gap === 0 ? 'var(--teal)' : g.gap > 40 ? 'var(--coral)' : 'var(--amber)',
                  }}
                />
              </div>
              <p className="text-sm text-[var(--slate)]">{g.reason}</p>
            </li>
          ))}
        </ul>
      </section>

      <button
        onClick={generateRoadmap}
        disabled={generating}
        className="focus-ring rounded-full px-5 py-2.5 text-sm font-medium text-white disabled:opacity-60"
        style={{ background: 'var(--amber-deep)' }}
      >
        {generating ? 'Generating…' : 'Generate Personalized Roadmap'}
      </button>
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <p className="font-mono text-2xl" style={{ color }}>{value}</p>
      <p className="text-xs text-[var(--slate)]">{label}</p>
    </div>
  );
}
