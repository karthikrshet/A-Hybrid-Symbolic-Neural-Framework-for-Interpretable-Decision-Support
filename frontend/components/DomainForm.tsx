"use client";

import { LuPlay, LuLoader } from "react-icons/lu";
import { cx } from "@/lib/ui";
import type { FeatureSpec, Inputs } from "@/lib/types";

interface Props {
  features: FeatureSpec[];
  values: Inputs;
  onChange: (v: Inputs) => void;
  onSubmit: () => void;
  loading?: boolean;
  highlight?: string[];
  submitLabel?: string;
  dense?: boolean;
}

export default function DomainForm({ features, values, onChange, onSubmit, loading, highlight = [], submitLabel = "Run multi-agent analysis", dense }: Props) {
  const groups = features.reduce<Record<string, FeatureSpec[]>>((acc, f) => {
    (acc[f.group] ??= []).push(f);
    return acc;
  }, {});

  const set = (name: string, v: string | number) => onChange({ ...values, [name]: v });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      className="space-y-5"
    >
      {Object.entries(groups).map(([group, fs]) => (
        <fieldset key={group}>
          <legend className="mb-2 text-[11px] font-bold uppercase tracking-wider text-brand-700">{group}</legend>
          <div className={cx("grid gap-3", dense ? "grid-cols-2 sm:grid-cols-3" : "sm:grid-cols-2")}>
            {fs.map((f) => (
              <label key={f.name} className={cx("block rounded-xl transition", highlight.includes(f.name) && "ring-2 ring-amber-300 ring-offset-2")}>
                <span className="label">
                  {f.label}
                  {f.unit && <span className="ml-1 font-normal text-ink-muted">({f.unit})</span>}
                </span>
                {f.kind === "select" ? (
                  <select className="input" value={String(values[f.name] ?? f.default)} onChange={(e) => set(f.name, e.target.value)}>
                    {f.options.map((o) => <option key={o}>{o}</option>)}
                  </select>
                ) : (
                  <input
                    type="number"
                    className="input font-mono"
                    value={values[f.name] ?? ""}
                    min={f.min ?? undefined}
                    max={f.max ?? undefined}
                    step={f.step ?? "any"}
                    onChange={(e) => set(f.name, e.target.value === "" ? "" : Number(e.target.value))}
                  />
                )}
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? <LuLoader className="animate-spin" /> : <LuPlay />}
        {loading ? "Agents are collaborating…" : submitLabel}
      </button>
    </form>
  );
}
