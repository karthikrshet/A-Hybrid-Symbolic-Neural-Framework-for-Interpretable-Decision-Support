"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { LuArrowLeft, LuArrowLeftRight } from "react-icons/lu";
import { DecisionHero } from "@/components/DecisionView";
import { ErrorBox, PageHeader, ProbBars, Spinner } from "@/components/primitives";
import { api, ApiError } from "@/lib/api";
import { cx, fmtValue } from "@/lib/ui";
import type { DecisionResult } from "@/lib/types";

function Compare() {
  const p = useSearchParams();
  const [pair, setPair] = useState<[DecisionResult, DecisionResult] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const a = p.get("a"), b = p.get("b");
    if (!a || !b) { setError("Select two decisions in the history first."); return; }
    Promise.all([api.decision(a), api.decision(b)]).then(([x, y]) => setPair([x, y])).catch((e: ApiError) => setError(e.message));
  }, [p]);
  if (error) return <ErrorBox message={error} />;
  if (!pair) return <Spinner />;
  const [a, b] = pair;
  const keys = Array.from(new Set([...Object.keys(a.inputs), ...Object.keys(b.inputs)]));
  const sameDomain = a.domain === b.domain;
  return (
    <>
      <Link href="/history" className="mb-4 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-700 hover:underline"><LuArrowLeft /> Back to history</Link>
      <PageHeader icon={<LuArrowLeftRight />} title="Compare decisions" subtitle={sameDomain ? "Changed inputs are highlighted so you can see how they affected each agent." : "These decisions come from different domains."} />
      <div className="grid gap-5 lg:grid-cols-2">
        {[a, b].map((r) => (
          <div key={r.id} className="space-y-4">
            <DecisionHero r={r} />
            <div className="card p-5"><div className="mb-2 text-xs font-bold uppercase tracking-wider text-ink-muted">Neural vs fused</div>
              <div className="grid grid-cols-2 gap-4"><ProbBars probs={r.neural_prediction.probabilities} highlight={r.neural_prediction.label} /><ProbBars probs={r.fusion.fused_probabilities} highlight={r.final_decision.label} /></div>
            </div>
            <div className="card p-5"><div className="mb-2 text-xs font-bold uppercase tracking-wider text-ink-muted">Triggered rules</div>
              {r.symbolic_reasoning.triggered_rules.length === 0 ? <p className="text-sm text-emerald-700">All rules passed</p> :
                <ul className="space-y-1 text-sm">{r.symbolic_reasoning.triggered_rules.map((x) => <li key={x.id}><span className="font-mono text-xs text-ink-muted">{x.id}</span> {x.name}</li>)}</ul>}
            </div>
          </div>
        ))}
      </div>
      {sameDomain && (
        <div className="card mt-5 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wider text-ink-muted"><tr><th className="px-4 py-2.5">Input</th><th className="px-4 py-2.5">Decision A</th><th className="px-4 py-2.5">Decision B</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {keys.map((k) => {
                const diff = String(a.inputs[k]) !== String(b.inputs[k]);
                return <tr key={k} className={cx(diff && "bg-amber-50/70")}><td className="px-4 py-2 text-ink-soft">{k.replace(/_/g, " ")}</td><td className="px-4 py-2 font-mono">{fmtValue(a.inputs[k] ?? "—")}</td><td className={cx("px-4 py-2 font-mono", diff && "font-bold text-amber-800")}>{fmtValue(b.inputs[k] ?? "—")}</td></tr>;
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default function ComparePage() {
  return <Suspense fallback={<Spinner />}><Compare /></Suspense>;
}
