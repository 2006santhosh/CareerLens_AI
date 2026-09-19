import { useEffect, useState } from 'react';
import { UploadCloud, GitBranch, Trash2 } from 'lucide-react';
import { api, type Evidence as EvidenceType, type ResumeAnalysisOut, ApiError } from '../lib/api';
import { LoadingState, EmptyState } from '../components/States';

type ResumeAnalysisOutLocal = ResumeAnalysisOut;

export default function Evidence() {
  const [items, setItems] = useState<EvidenceType[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);
  const [githubUsername, setGithubUsername] = useState('octocat');
  const [githubBusy, setGithubBusy] = useState(false);
  const [manualForm, setManualForm] = useState({ type: 'project', title: '', description: '', skills: '' });
  const [manualBusy, setManualBusy] = useState(false);

  function load() {
    setError(null);
    api.get<EvidenceType[]>('/evidence')
      .then(setItems)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load your evidence.'));
  }
  useEffect(load, []);

  async function handleUpload(file: File) {
    setUploading(true);
    setUploadMsg(null);
    setError(null);
    const form = new FormData();
    form.append('file', file);
    try {
      const result = await api.upload<ResumeAnalysisOutLocal>('/resumes/upload', form);
      setUploadMsg(result.message);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not process this resume.');
    } finally {
      setUploading(false);
    }
  }

  async function handleGithub() {
    setGithubBusy(true);
    setError(null);
    try {
      await api.post(`/github/analyze?username=${encodeURIComponent(githubUsername)}`);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'GitHub analysis failed.');
    } finally {
      setGithubBusy(false);
    }
  }

  async function handleManualSubmit() {
    if (!manualForm.title.trim()) return;
    setManualBusy(true);
    setError(null);
    try {
      await api.post('/evidence', {
        type: manualForm.type,
        title: manualForm.title,
        description: manualForm.description,
        skill_names: manualForm.skills.split(',').map((s) => s.trim()).filter(Boolean),
      });
      setManualForm({ type: 'project', title: '', description: '', skills: '' });
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not save this evidence.');
    } finally {
      setManualBusy(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await api.del(`/evidence/${id}`);
      load();
    } catch {
      setError('Could not delete this evidence.');
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display mb-6 text-3xl">Projects / Evidence</h1>

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
        <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
          <h2 className="font-display mb-3 flex items-center gap-2 text-lg"><UploadCloud size={18} /> Upload resume</h2>
          <input
            type="file"
            accept=".pdf,.docx"
            disabled={uploading}
            onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
            className="text-sm"
          />
          {uploading && <p className="mt-2 text-sm text-[var(--slate)]">Analyzing your resume…</p>}
          {uploadMsg && <p className="mt-2 text-sm text-[var(--teal)]">{uploadMsg}</p>}
        </section>

        <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
          <h2 className="font-display mb-3 flex items-center gap-2 text-lg"><GitBranch size={18} /> GitHub (optional)</h2>
          <p className="mb-2 text-xs text-[var(--slate)]">
            We only analyze public repositories as supporting evidence — this does not by itself prove expertise.
          </p>
          <div className="flex gap-2">
            <input
              value={githubUsername}
              onChange={(e) => setGithubUsername(e.target.value)}
              className="focus-ring flex-1 rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
            />
            <button
              onClick={handleGithub}
              disabled={githubBusy}
              className="focus-ring rounded-full border border-[var(--line)] px-4 py-2 text-sm hover:border-[var(--ink)]"
            >
              {githubBusy ? 'Analyzing…' : 'Analyze'}
            </button>
          </div>
        </section>
      </div>

      <section className="mb-8 rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-3 text-lg">Add manual evidence</h2>
        <div className="grid grid-cols-2 gap-3">
          <select
            value={manualForm.type}
            onChange={(e) => setManualForm((f) => ({ ...f, type: e.target.value }))}
            className="focus-ring col-span-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm sm:col-span-1"
          >
            <option value="project">Project</option>
            <option value="certification">Certification</option>
            <option value="github">GitHub project</option>
            <option value="self_reported">Self-reported</option>
          </select>
          <input
            placeholder="Title"
            value={manualForm.title}
            onChange={(e) => setManualForm((f) => ({ ...f, title: e.target.value }))}
            className="focus-ring col-span-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm sm:col-span-1"
          />
          <input
            placeholder="Related skills (comma separated, e.g. Docker, CI/CD)"
            value={manualForm.skills}
            onChange={(e) => setManualForm((f) => ({ ...f, skills: e.target.value }))}
            className="focus-ring col-span-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
          />
          <textarea
            placeholder="Description"
            value={manualForm.description}
            onChange={(e) => setManualForm((f) => ({ ...f, description: e.target.value }))}
            className="focus-ring col-span-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm"
            rows={2}
          />
        </div>
        <button
          onClick={handleManualSubmit}
          disabled={manualBusy}
          className="focus-ring mt-3 rounded-full px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          style={{ background: 'var(--ink)' }}
        >
          {manualBusy ? 'Saving…' : 'Add evidence'}
        </button>
      </section>

      {error && <p className="mb-4 text-sm text-[var(--coral)]">{error}</p>}

      <section>
        <h2 className="font-display mb-3 text-lg">Your evidence</h2>
        {!items ? (
          <LoadingState />
        ) : items.length === 0 ? (
          <EmptyState title="No evidence yet" description="Upload a resume or add a project above to get started." />
        ) : (
          <ul className="flex flex-col gap-2">
            {items.map((ev) => (
              <li key={ev.id} className="flex items-center justify-between rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-4">
                <div>
                  <p className="text-sm font-medium">{ev.title}</p>
                  <p className="text-xs text-[var(--slate)]">{ev.type} · {new Date(ev.created_at).toLocaleDateString()}</p>
                </div>
                <button onClick={() => handleDelete(ev.id)} className="focus-ring text-[var(--slate)] hover:text-[var(--coral)]">
                  <Trash2 size={16} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
