import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, type Career } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { LoadingState } from '../components/States';

const HOURS_OPTIONS = ['1-3', '3-5', '5-10', '10+'];
const STYLE_OPTIONS = ['Visual', 'Reading/Docs', 'Hands-on Projects', 'Mixed'];

export default function Onboarding() {
  const { refreshUser } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [careers, setCareers] = useState<Career[]>([]);
  const [loadingCareers, setLoadingCareers] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeMessage, setResumeMessage] = useState<string | null>(null);
  // Canonical skill names (loaded lazily when Step 3 is first shown)
  const [canonicalSkills, setCanonicalSkills] = useState<string[] | null>(null);

  const [targetCareerId, setTargetCareerId] = useState('');
  const [weeklyHours, setWeeklyHours] = useState('5-10');
  const [learningStyle, setLearningStyle] = useState('Mixed');
  const [interests, setInterests] = useState<string[]>([]);
  const [skillsText, setSkillsText] = useState('Python:60, Git:50');

  useEffect(() => {
    api.get<Career[]>('/careers').then((data) => {
      setCareers(data);
      setLoadingCareers(false);
    }).catch(() => setLoadingCareers(false));
  }, []);

  function toggleInterest(name: string) {
    setInterests((cur) => (cur.includes(name) ? cur.filter((i) => i !== name) : [...cur, name]));
  }

  // Load canonical skill names the first time Step 3 is shown
  useEffect(() => {
    if (step === 3 && canonicalSkills === null) {
      api.get<{ name: string }[]>('/skills')
        .then((data) => setCanonicalSkills(data.map((s) => s.name.toLowerCase())))
        .catch(() => setCanonicalSkills([])); // fail silently — warning simply won't show
    }
  }, [step, canonicalSkills]);

  // Compute which entered skill names are not in the canonical list
  const unrecognisedSkills = useMemo(() => {
    if (!canonicalSkills) return [];
    return skillsText
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((entry) => entry.split(':')[0].trim())
      .filter((name) => name && !canonicalSkills.includes(name.toLowerCase()));
  }, [skillsText, canonicalSkills]);

  function parseSkills() {
    return skillsText
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((entry) => {
        const [name, level] = entry.split(':').map((p) => p.trim());
        return { name, level: Number(level) || 30 };
      });
  }

  async function finish() {
    setSubmitting(true);
    setError(null);
    try {
      await api.post('/onboarding', {
        target_career_id: targetCareerId,
        weekly_hours: weeklyHours,
        preferred_learning_style: learningStyle,
        career_interests: interests,
        current_skills: parseSkills(),
      });

      if (resumeFile) {
        const form = new FormData();
        form.append('file', resumeFile);
        try {
          const result = await api.upload<{ message: string }>('/resumes/upload', form);
          setResumeMessage(result.message);
        } catch {
          setResumeMessage('Resume could not be processed automatically — you can add skills manually on the Skills page.');
        }
      }

      await refreshUser();
      navigate('/dashboard');
    } catch {
      setError('Could not save your profile. Please check your selections and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  const steps = ['Career interests', 'Target career', 'Current skills', 'Availability', 'Resume'];

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10" style={{ background: 'var(--ink)' }}>
      <div className="w-full max-w-xl rounded-2xl p-8" style={{ background: 'var(--paper-raised)' }}>
        <p className="font-mono mb-1 text-xs text-[var(--slate)]">STEP {step} OF {steps.length}</p>
        <h1 className="font-display mb-6 text-2xl">{steps[step - 1]}</h1>

        {step === 1 && (
          <div>
            <p className="mb-4 text-sm text-[var(--slate)]">What kinds of roles interest you? Pick as many as you like.</p>
            {loadingCareers ? <LoadingState /> : (
              <div className="grid grid-cols-2 gap-2">
                {careers.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => toggleInterest(c.name)}
                    className={`focus-ring rounded-lg border px-3 py-2 text-left text-sm ${
                      interests.includes(c.name) ? 'border-[var(--ink)] bg-[var(--ink)] text-white' : 'border-[var(--line)]'
                    }`}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {step === 2 && (
          <div>
            <p className="mb-4 text-sm text-[var(--slate)]">
              Choose one primary target career. This drives your gap analysis and roadmap.
            </p>
            <div className="flex flex-col gap-2">
              {careers.map((c) => (
                <label
                  key={c.id}
                  className={`focus-ring flex cursor-pointer flex-col rounded-lg border px-3 py-2 text-sm ${
                    targetCareerId === c.id ? 'border-[var(--ink)]' : 'border-[var(--line)]'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="target"
                      checked={targetCareerId === c.id}
                      onChange={() => setTargetCareerId(c.id)}
                    />
                    <span className="font-medium">{c.name}</span>
                  </span>
                  <span className="ml-6 text-xs text-[var(--slate)]">{c.description}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <p className="mb-3 text-sm text-[var(--slate)]">
              List your current skills as <span className="font-mono">Name:Level</span> (0-100), comma-separated.
              You'll be able to add more evidence later.
            </p>
            <textarea
              value={skillsText}
              onChange={(e) => setSkillsText(e.target.value)}
              rows={3}
              className="focus-ring w-full rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
              placeholder="Python:60, Git:50, Docker:20"
            />
            <p className="mt-1 text-xs text-[var(--slate)]">
              Use canonical skill names (e.g. Python, Docker, React). Aliases like K8s, Postgres, NLP also work.
              Unrecognised names are ignored.
            </p>
            {unrecognisedSkills.length > 0 && (
              <p className="mt-2 rounded-lg border border-[var(--amber)] bg-[var(--amber)]/10 px-3 py-2 text-xs text-[var(--ink-text)]">
                <span className="font-medium">Not recognised (will be ignored):</span>{' '}
                {unrecognisedSkills.join(', ')}
              </p>
            )}
          </div>
        )}

        {step === 4 && (
          <div className="flex flex-col gap-5">
            <div>
              <p className="mb-2 text-sm text-[var(--slate)]">How many hours per week can you dedicate to learning?</p>
              <div className="flex gap-2">
                {HOURS_OPTIONS.map((h) => (
                  <button
                    key={h}
                    type="button"
                    onClick={() => setWeeklyHours(h)}
                    className={`focus-ring rounded-full border px-3 py-1.5 text-sm ${
                      weeklyHours === h ? 'border-[var(--ink)] bg-[var(--ink)] text-white' : 'border-[var(--line)]'
                    }`}
                  >
                    {h} hrs/week
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm text-[var(--slate)]">Preferred learning style</p>
              <div className="flex flex-wrap gap-2">
                {STYLE_OPTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setLearningStyle(s)}
                    className={`focus-ring rounded-full border px-3 py-1.5 text-sm ${
                      learningStyle === s ? 'border-[var(--ink)] bg-[var(--ink)] text-white' : 'border-[var(--line)]'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 5 && (
          <div>
            <p className="mb-3 text-sm text-[var(--slate)]">
              Upload a resume (PDF or DOCX) so we can extract your skills automatically. Optional — you can skip this.
            </p>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
              className="text-sm"
            />
            {resumeMessage && <p className="mt-3 text-sm text-[var(--teal)]">{resumeMessage}</p>}
          </div>
        )}

        {error && <p className="mt-4 text-sm text-[var(--coral)]">{error}</p>}

        <div className="mt-8 flex justify-between">
          <button
            type="button"
            disabled={step === 1}
            onClick={() => setStep((s) => s - 1)}
            className="focus-ring rounded-full border border-[var(--line)] px-4 py-2 text-sm disabled:opacity-40"
          >
            Back
          </button>
          {step < steps.length ? (
            <button
              type="button"
              disabled={step === 2 && !targetCareerId}
              onClick={() => setStep((s) => s + 1)}
              className="focus-ring rounded-full px-5 py-2 text-sm font-medium text-white disabled:opacity-40"
              style={{ background: 'var(--ink)' }}
            >
              Continue
            </button>
          ) : (
            <button
              type="button"
              disabled={submitting}
              onClick={finish}
              className="focus-ring rounded-full px-5 py-2 text-sm font-medium text-white disabled:opacity-60"
              style={{ background: 'var(--amber-deep)' }}
            >
              {submitting ? 'Generating your profile…' : 'Generate My Career Profile'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
