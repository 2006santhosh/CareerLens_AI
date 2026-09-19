import { CheckCircle2, Circle, FileSearch, ClipboardCheck } from 'lucide-react';

const BAND_COLORS: Record<string, string> = {
  Beginner: 'var(--coral)',
  Basic: 'var(--amber-deep)',
  Developing: 'var(--amber)',
  Proficient: 'var(--teal)',
  Advanced: 'var(--teal)',
};

export function BandBadge({ band, level }: { band: string; level: number }) {
  const color = BAND_COLORS[band] ?? 'var(--slate)';
  return (
    <span
      className="font-mono inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs"
      style={{ borderColor: color, color }}
    >
      {level} · {band}
    </span>
  );
}

const STATUS_CONFIG: Record<string, { label: string; icon: typeof Circle; color: string }> = {
  self_reported: { label: 'Self-reported', icon: Circle, color: 'var(--slate)' },
  evidence_found: { label: 'Evidence found', icon: FileSearch, color: 'var(--amber-deep)' },
  assessed: { label: 'Assessed', icon: ClipboardCheck, color: 'var(--amber)' },
  verified: { label: 'Verified', icon: CheckCircle2, color: 'var(--teal)' },
};

export function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.self_reported;
  const Icon = cfg.icon;
  return (
    <span className="inline-flex items-center gap-1.5 text-xs" style={{ color: cfg.color }}>
      <Icon size={14} strokeWidth={2} />
      {cfg.label}
    </span>
  );
}

export function ImportanceTag({ importance }: { importance: string }) {
  const color = importance === 'High' ? 'var(--coral)' : importance === 'Medium' ? 'var(--amber-deep)' : 'var(--slate)';
  return (
    <span className="text-xs font-medium" style={{ color }}>
      {importance} priority
    </span>
  );
}
