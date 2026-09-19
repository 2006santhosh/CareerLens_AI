export function Gauge({ value, label, size = 168 }: { value: number; label: string; size?: number }) {
  const radius = size / 2 - 12;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, value));
  const offset = circumference * (1 - pct / 100);
  const color = pct >= 70 ? 'var(--teal)' : pct >= 40 ? 'var(--amber)' : 'var(--coral)';

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--line)" strokeWidth={10} />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={10}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-mono text-3xl font-semibold" style={{ color }}>
            {Math.round(pct)}%
          </span>
        </div>
      </div>
      <span className="text-center text-sm text-[var(--slate)]">{label}</span>
    </div>
  );
}
