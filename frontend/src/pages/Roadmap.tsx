import { useEffect, useState } from 'react';
import { CheckCircle2, Circle, PlayCircle } from 'lucide-react';
import { api, type Roadmap as RoadmapType, ApiError } from '../lib/api';
import { LoadingState, ErrorState, EmptyState } from '../components/States';

const STATUS_CYCLE: Record<string, string> = {
  pending: 'in_progress',
  in_progress: 'completed',
  completed: 'pending',
};

const STATUS_ICON: Record<string, typeof Circle> = {
  pending: Circle,
  in_progress: PlayCircle,
  completed: CheckCircle2,
};

export default function Roadmap() {
  const [roadmap, setRoadmap] = useState<RoadmapType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);

  function load() {
    setError(null);
    setNotFound(false);
    api.get<RoadmapType>('/roadmaps/current')
      .then(setRoadmap)
      .catch((e) => {
        if (e instanceof ApiError && e.status === 404) setNotFound(true);
        else setError(e instanceof ApiError ? e.message : 'Could not load your roadmap.');
      });
  }
  useEffect(load, []);

  async function generate() {
    setGenerating(true);
    try {
      const r = await api.post<RoadmapType>('/roadmaps/generate');
      setRoadmap(r);
      setNotFound(false);
      setBanner('Your personalized roadmap has been generated based on your current skill gap analysis.');
    } catch {
      setError('Could not generate a roadmap. Make sure you have selected a target career.');
    } finally {
      setGenerating(false);
    }
  }

  async function cycleStatus(itemId: string, current: string) {
    if (!roadmap) return;
    const next = STATUS_CYCLE[current];
    const updatedItems = roadmap.items.map((i) => (i.id === itemId ? { ...i, status: next } : i));
    setRoadmap({ ...roadmap, items: updatedItems });
    try {
      await api.patch(`/roadmaps/items/${itemId}`, { status: next });
    } catch {
      load();
    }
  }

  if (error) return <ErrorState message={error} onRetry={load} />;

  if (notFound) {
    return (
      <EmptyState
        title="No roadmap yet"
        description="Generate a personalized, prerequisite-aware learning path from your current skill gap analysis."
        action={
          <button onClick={generate} disabled={generating} className="mt-2 rounded-full px-5 py-2 text-sm font-medium text-white" style={{ background: 'var(--ink)' }}>
            {generating ? 'Generating…' : 'Generate Personalized Roadmap'}
          </button>
        }
      />
    );
  }

  if (!roadmap) return <LoadingState label="Loading your roadmap…" />;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-2 flex items-center justify-between">
        <h1 className="font-display text-3xl">Learning Roadmap</h1>
        <span className="font-mono text-xs text-[var(--slate)]">v{roadmap.version}</span>
      </div>
      <p className="mb-1 text-sm text-[var(--slate)]">Target: {roadmap.career.name}</p>
      {roadmap.generated_reason && (
        <p className="mb-6 rounded-lg border border-[var(--line)] bg-[var(--paper-raised)] px-3 py-2 text-sm text-[var(--slate)]">
          {roadmap.generated_reason}
        </p>
      )}
      {banner && <p className="mb-6 text-sm text-[var(--teal)]">{banner}</p>}

      <div className="mb-6 flex items-center gap-2">
        <div className="h-2 flex-1 overflow-hidden rounded-full bg-[var(--line)]">
          <div className="h-full rounded-full" style={{ width: `${roadmap.progress_percent}%`, background: 'var(--teal)' }} />
        </div>
        <span className="font-mono text-sm">{Math.round(roadmap.progress_percent)}%</span>
      </div>

      <ol className="relative ml-3 flex flex-col gap-6 border-l border-[var(--line)] pl-6">
        {roadmap.items.map((item) => {
          const Icon = STATUS_ICON[item.status];
          return (
            <li key={item.id} className="relative">
              <button
                onClick={() => cycleStatus(item.id, item.status)}
                className="focus-ring absolute -left-[31px] top-0 rounded-full bg-[var(--paper)]"
                title="Click to update status"
              >
                <Icon
                  size={20}
                  strokeWidth={1.75}
                  style={{ color: item.status === 'completed' ? 'var(--teal)' : item.status === 'in_progress' ? 'var(--amber)' : 'var(--slate)' }}
                />
              </button>
              <p className="font-mono mb-0.5 text-xs text-[var(--slate)]">{item.phase_label} · {item.estimated_hours}h</p>
              <h3 className="font-display mb-2 text-lg">{item.skill.name}</h3>
              <dl className="flex flex-col gap-1.5 text-sm">
                <DL term="Why this topic?" val={item.why} />
                <DL term="What to learn" val={item.what_to_learn} />
                <DL term="What to build" val={item.what_to_build} />
                <DL term="How to prove it" val={item.how_to_prove} />
              </dl>
            </li>
          );
        })}
      </ol>

      <button
        onClick={generate}
        disabled={generating}
        className="focus-ring mt-8 rounded-full border border-[var(--line)] px-4 py-2 text-sm hover:border-[var(--ink)]"
      >
        {generating ? 'Regenerating…' : 'Regenerate roadmap from latest gap analysis'}
      </button>
    </div>
  );
}

function DL({ term, val }: { term: string; val: string }) {
  return (
    <div>
      <dt className="font-medium text-[var(--slate)]">{term}</dt>
      <dd>{val}</dd>
    </div>
  );
}
