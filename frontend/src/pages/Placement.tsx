import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { LoadingState } from '../components/States';

interface PlacementData {
  note: string;
  most_common_skill_gaps: { skill: string; students_affected: number }[];
  total_students: number;
}

export default function Placement() {
  const [data, setData] = useState<PlacementData | null>(null);

  useEffect(() => {
    api.get<PlacementData>('/placement/analytics').then(setData).catch(() => setData(null));
  }, []);

  if (!data) return <LoadingState label="Loading aggregate insights…" />;

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-display mb-2 text-3xl">Placement Insights</h1>
      <p className="mb-6 text-sm text-[var(--slate)]">{data.note}</p>

      <div className="mb-6 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <p className="font-mono text-3xl">{data.total_students}</p>
        <p className="text-sm text-[var(--slate)]">Students tracked on the platform</p>
      </div>

      <section>
        <h2 className="font-display mb-3 text-lg">Most common skill gaps</h2>
        <ol className="flex flex-col gap-2">
          {data.most_common_skill_gaps.map((g, i) => (
            <li key={g.skill} className="flex items-center justify-between rounded-lg border border-[var(--line)] bg-[var(--paper-raised)] px-4 py-2 text-sm">
              <span>{i + 1}. {g.skill}</span>
              <span className="font-mono text-[var(--slate)]">{g.students_affected} students</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
