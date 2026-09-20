import { useEffect, useMemo, useState } from 'react';
import { api, type SkillProfileItem, ApiError } from '../lib/api';
import { LoadingState, ErrorState, EmptyState } from '../components/States';
import { BandBadge, StatusBadge } from '../components/SkillBits';

export default function Skills() {
  const [items, setItems] = useState<SkillProfileItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setError(null);
    api.get<SkillProfileItem[]>('/skills/profile')
      .then(setItems)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load your skill profile.'));
  }
  useEffect(load, []);

  const grouped = useMemo(() => {
    if (!items) return {};
    return items.reduce<Record<string, SkillProfileItem[]>>((acc, item) => {
      (acc[item.skill.category] ??= []).push(item);
      return acc;
    }, {});
  }, [items]);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!items) return <LoadingState label="Loading your skill intelligence…" />;

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="font-display mb-2 text-3xl">Skill Intelligence</h1>
      <p className="mb-6 text-sm text-[var(--slate)]">
        Every skill here is backed by evidence you've provided — resumes, projects, GitHub activity, or assessments.
        Claims alone never become "Verified".
      </p>

      {items.length === 0 ? (
        <EmptyState
          title="No skills tracked yet"
          description="Upload a resume or add project evidence to start building your skill profile."
        />
      ) : (
        Object.entries(grouped).map(([category, skills]) => (
          <section key={category} className="mb-8">
            <h2 className="font-display mb-3 text-lg">{category}</h2>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {skills.map((item) => (
                <div key={item.skill.id} className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">{item.skill.name}</span>
                    <BandBadge band={item.band} level={item.level} />
                  </div>
                  <StatusBadge status={item.status} />
                  <div className="mt-2 flex flex-wrap gap-2 text-xs text-[var(--slate)]">
                    {item.has_resume_evidence && <EvidenceTag label="Resume" />}
                    {item.has_project_evidence && <EvidenceTag label="Project" />}
                    {item.has_github_evidence && <EvidenceTag label="GitHub" />}
                    {item.has_certification && <EvidenceTag label="Certification" />}
                    {item.has_practical_evidence && <EvidenceTag label="Practical" />}
                    {item.best_assessment_percent != null && (
                      <EvidenceTag label={`Assessment ${Math.round(item.best_assessment_percent)}%`} />
                    )}
                  </div>
                  {item.latest_evidence_excerpt && (
                    <div className="mt-3 text-xs italic text-[var(--slate)] border-l-2 border-[var(--teal)] pl-2">
                      "{item.latest_evidence_excerpt}"
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  );
}

function EvidenceTag({ label }: { label: string }) {
  return (
    <span className="rounded-full border border-[var(--line)] px-2 py-0.5">
      ✓ {label}
    </span>
  );
}
