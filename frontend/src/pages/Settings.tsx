export default function Settings() {
  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-display mb-6 text-3xl">Settings</h1>

      <section className="rounded-xl border border-[var(--line)] bg-[var(--paper-raised)] p-5">
        <h2 className="font-display mb-2 text-lg">About CareerLens AI</h2>
        <p className="text-sm text-[var(--slate)]">
          Career Readiness is a transparent measure of demonstrated skill coverage against your selected
          target role — not a prediction or guarantee of a job offer. All gap, roadmap, and readiness
          calculations are deterministic and explainable; AI is used only for resume understanding and
          natural-language explanations.
        </p>
      </section>
    </div>
  );
}
