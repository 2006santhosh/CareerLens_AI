import { Loader2, AlertTriangle, Inbox } from 'lucide-react';

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-[var(--slate)]">
      <Loader2 className="animate-spin" size={28} strokeWidth={1.5} />
      <p className="font-mono text-sm">{label}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <AlertTriangle className="text-[var(--coral)]" size={28} strokeWidth={1.5} />
      <p className="max-w-sm text-sm text-[var(--ink-text)]">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="focus-ring mt-1 rounded-full border border-[var(--line)] px-4 py-1.5 text-sm hover:border-[var(--ink)]"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-[var(--line)] py-16 text-center">
      <Inbox className="text-[var(--slate)]" size={26} strokeWidth={1.5} />
      <p className="font-display text-lg">{title}</p>
      {description && <p className="max-w-sm text-sm text-[var(--slate)]">{description}</p>}
      {action}
    </div>
  );
}
