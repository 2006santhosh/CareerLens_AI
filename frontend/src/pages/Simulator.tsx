import { useEffect, useState } from 'react';
import { api, type SimulatorSkillOverride, type SimulatorResponse, type Dashboard, ApiError } from '../lib/api';
import { LoadingState, ErrorState } from '../components/States';
import { Gauge } from '../components/Gauge';

export default function Simulator() {
  const [targetCareerId, setTargetCareerId] = useState<string | null>(null);
  const [baseGaps, setBaseGaps] = useState<any[]>([]);
  const [overrides, setOverrides] = useState<Record<string, SimulatorSkillOverride>>({});
  const [result, setResult] = useState<SimulatorResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    // Load initial gaps from dashboard to know what to simulate
    api.get<Dashboard>('/dashboard')
      .then((data) => {
        if (data.target_career) {
          setTargetCareerId(data.target_career.id);
          api.get<any>(`/gap-analysis/${data.target_career.id}`).then(gapData => {
            setBaseGaps(gapData.gaps);
            setLoading(false);
          });
        } else {
          setLoading(false);
        }
      })
      .catch((e) => {
        setError(e instanceof ApiError ? e.message : 'Could not load base data.');
        setLoading(false);
      });
  }, []);

  async function runSimulation() {
    if (!targetCareerId) return;
    setSimulating(true);
    try {
      const payload = {
        career_id: targetCareerId,
        overrides: Object.values(overrides).filter(o => Object.keys(o).length > 1),
      };
      const res = await api.post<SimulatorResponse>('/simulator/simulate', payload);
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Simulation failed.');
    } finally {
      setSimulating(false);
    }
  }

  function handleOverride(skillId: string, updates: Partial<SimulatorSkillOverride>) {
    setOverrides(prev => ({
      ...prev,
      [skillId]: { ...prev[skillId], skill_id: skillId, ...updates }
    }));
  }

  if (loading) return <LoadingState label="Preparing simulator..." />;
  if (error) return <ErrorState message={error} />;

  if (!targetCareerId) {
    return (
      <div className="mx-auto max-w-2xl text-center pt-10">
        <h1 className="font-display text-2xl">No Target Career Selected</h1>
        <p className="text-[var(--slate)] mt-2">Please select a target career in the Career Explorer to use the simulator.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl flex flex-col md:flex-row gap-8">
      <div className="flex-1">
        <h1 className="font-display mb-2 text-3xl">Career Simulator</h1>
        <p className="mb-6 text-sm text-[var(--slate)]">
          "What-if" Analysis: Tweak your skill levels and verified status below to see how they impact your overall readiness and gap priority score. These changes are temporary and will not be saved.
        </p>

        <div className="bg-[var(--paper-raised)] border border-[var(--line)] rounded-xl overflow-hidden mb-6">
          <table className="w-full text-sm text-left">
            <thead className="bg-[var(--paper)] border-b border-[var(--line)] text-xs text-[var(--slate)]">
              <tr>
                <th className="px-4 py-3 font-medium">Skill</th>
                <th className="px-4 py-3 font-medium">Req Level</th>
                <th className="px-4 py-3 font-medium w-1/3">Simulated Level</th>
                <th className="px-4 py-3 font-medium text-center">Verified?</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--line)]">
              {baseGaps.map(g => {
                const currentOverride = overrides[g.skill.id];
                const simLevel = currentOverride?.level ?? g.current_level;
                const simVerified = currentOverride?.status === 'verified';

                return (
                  <tr key={g.skill.id} className="hover:bg-[var(--line)]/30">
                    <td className="px-4 py-3 font-medium">{g.skill.name}</td>
                    <td className="px-4 py-3 text-[var(--slate)]">{g.required_level}</td>
                    <td className="px-4 py-3">
                      <input 
                        type="range" 
                        min="0" max="100" 
                        value={simLevel}
                        onChange={(e) => handleOverride(g.skill.id, { level: parseInt(e.target.value) })}
                        className="w-full accent-[var(--teal)]"
                      />
                      <div className="text-xs text-right text-[var(--slate)] mt-1">{simLevel} / 100</div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <input 
                        type="checkbox" 
                        checked={simVerified}
                        onChange={(e) => handleOverride(g.skill.id, { status: e.target.checked ? 'verified' : 'self_reported' })}
                        className="w-4 h-4 accent-[var(--teal)] rounded"
                      />
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        <button
          onClick={runSimulation}
          disabled={simulating}
          className="focus-ring rounded-full px-6 py-2 text-sm font-medium text-white disabled:opacity-60"
          style={{ background: 'var(--ink)' }}
        >
          {simulating ? 'Simulating...' : 'Run Simulation'}
        </button>
      </div>

      <div className="w-full md:w-80">
        <div className="sticky top-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-6">
          <h2 className="font-display text-lg mb-4">Simulation Results</h2>
          
          {result ? (
            <div className="flex flex-col items-center">
              <Gauge value={result.readiness.overall_readiness} label="New Readiness" size={160} />
              
              <div className="mt-6 w-full">
                <h3 className="font-medium text-sm mb-2 border-b border-[var(--line)] pb-1">Updated Top Gaps</h3>
                <ul className="flex flex-col gap-2 text-sm">
                  {result.gap_analysis.gaps.slice(0, 3).map((g, i) => (
                    <li key={g.skill.id} className="flex justify-between items-center">
                      <span>{i+1}. {g.skill.name}</span>
                      <span className="font-mono text-xs text-[var(--slate)]">Priority {Math.round(g.priority_score)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-sm text-[var(--slate)]">
              Adjust sliders and click "Run Simulation" to see the impact.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
