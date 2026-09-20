import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api, type CareerDetail as CareerDetailType, ApiError } from '../lib/api';
import { LoadingState, ErrorState } from '../components/States';
import { ImportanceTag } from '../components/SkillBits';
import { CareerGraph } from '../components/CareerGraph';

export default function CareerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [career, setCareer] = useState<CareerDetailType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [settingTarget, setSettingTarget] = useState(false);

  function load() {
    if (!id) return;
    setError(null);
    api.get<CareerDetailType>(`/careers/${id}`)
      .then(setCareer)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load this career.'));
  }
  useEffect(load, [id]);

  async function analyzeGap() {
    if (!id) return;
    setSettingTarget(true);
    try {
      await api.put('/profile', { target_career_id: id });
      navigate('/gap-analysis');
    } catch {
      setError('Could not set this as your target career.');
    } finally {
      setSettingTarget(false);
    }
  }

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!career) return <LoadingState label="Loading career details…" />;

  const strong = career.skills.filter((s) => s.required_level === 0).length;
  const requiredCount = career.skills.length;

  return (
    <div className="mx-auto max-w-3xl">
      <p className="font-mono mb-1 text-xs text-[var(--slate)]">TARGET CAREER</p>
      <h1 className="font-display mb-2 text-3xl">{career.name}</h1>
      <p className="mb-6 text-sm text-[var(--slate)]">{career.description}</p>

      <div className="mb-6 grid grid-cols-3 gap-4 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <Stat label="Your current match" value={`${Math.round(career.match_percent ?? 0)}%`} />
        <Stat label="Required skills" value={String(requiredCount)} />
        <Stat label="Strong skills" value={String(strong)} />
      </div>

      {career.responsibilities && (
        <section className="mb-6">
          <h2 className="font-display mb-2 text-lg">Typical responsibilities</h2>
          <ul className="list-disc pl-5 text-sm text-[var(--slate)]">
            {career.responsibilities.split('\n').filter(Boolean).map((r) => <li key={r}>{r}</li>)}
          </ul>
        </section>
      )}

      <section className="mb-8">
        <h2 className="font-display mb-3 text-lg">Skill Dependency Graph</h2>
        <CareerGraph careerId={career.id} />
      </section>

      <section className="mb-8">
        <h2 className="font-display mb-3 text-lg">Required skills</h2>
        <ul className="divide-y divide-[var(--line)] rounded-xl border border-[var(--line)] bg-[var(--paper-raised)]">
          {career.skills.map((cs) => (
            <li key={cs.skill.id} className="flex items-center justify-between px-4 py-3">
              <span className="text-sm font-medium">{cs.skill.name}</span>
              <div className="flex items-center gap-3">
                <ImportanceTag importance={cs.importance} />
                <span className="font-mono text-sm text-[var(--slate)]">target {cs.required_level}</span>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <button
        onClick={analyzeGap}
        disabled={settingTarget}
        className="focus-ring rounded-full px-5 py-2.5 text-sm font-medium text-white disabled:opacity-60"
        style={{ background: 'var(--ink)' }}
      >
        {settingTarget ? 'Setting up…' : 'Analyze My Skill Gap'}
      </button>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-mono text-2xl">{value}</p>
      <p className="text-xs text-[var(--slate)]">{label}</p>
    </div>
  );
}
