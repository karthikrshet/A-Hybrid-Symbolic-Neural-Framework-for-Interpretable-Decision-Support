"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { LuBookOpen, LuBrain, LuLoader, LuRefreshCw } from "react-icons/lu";
import { ErrorBox, PageHeader, Spinner, ToneBadge } from "@/components/primitives";
import { api, ApiError } from "@/lib/api";
import { cx, domainIcon, pct } from "@/lib/ui";
import type { DomainDetail, DomainSummary, ModelInfo } from "@/lib/types";

const OP: Record<string, string> = { gt: ">", gte: "≥", lt: "<", lte: "≤", eq: "=", neq: "≠", in: "in" };

function LossCurve({ values }: { values: number[] }) {
  if (values.length < 2) return null;
  const max = Math.max(...values), min = Math.min(...values);
  const pts = values.map((v, i) => `${(i / (values.length - 1)) * 300},${90 - ((v - min) / (max - min || 1)) * 80}`).join(" ");
  return (
    <svg viewBox="0 0 300 100" className="h-24 w-full">
      <polyline points={pts} fill="none" stroke="#2563EB" strokeWidth="2" strokeLinejoin="round" />
      <polyline points={`0,100 ${pts} 300,100`} fill="rgba(37,99,235,0.08)" stroke="none" />
    </svg>
  );
}

function KB() {
  const params = useSearchParams();
  const [domains, setDomains] = useState<DomainSummary[]>([]);
  const [active, setActive] = useState(params.get("domain") ?? "healthcare");
  const [detail, setDetail] = useState<DomainDetail | null>(null);
  const [model, setModel] = useState<ModelInfo | null>(null);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { api.domains().then(setDomains).catch((e: ApiError) => setError(e.message)); }, []);
  useEffect(() => {
    setDetail(null); setModel(null);
    api.domain(active).then(setDetail).catch((e: ApiError) => setError(e.message));
    api.model(active).then(setModel).catch(() => undefined);
  }, [active]);

  const retrain = async () => {
    setTraining(true);
    try { setModel((await api.retrain(active)).model); } catch (e) { setError(e instanceof ApiError ? e.message : "Training failed"); } finally { setTraining(false); }
  };

  return (
    <>
      <PageHeader icon={<LuBookOpen />} title="Knowledge Base & Models" subtitle="Each domain plugs into the common engine with its own input schema, IF-THEN knowledge base and trained neural network. Mandatory rules can override the neural prediction; advisory rules shift the fused belief." />
      <div className="mb-5 flex flex-wrap gap-2">
        {domains.map((d) => {
          const Icon = domainIcon(d.id);
          return <button key={d.id} onClick={() => setActive(d.id)} className={cx("inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition", active === d.id ? "bg-brand-600 text-white" : "bg-white text-ink-soft ring-1 ring-slate-200 hover:text-brand-700")}><Icon />{d.name}</button>;
        })}
      </div>
      {error && <ErrorBox message={error} />}
      {!detail ? <Spinner /> : (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
          <div className="card overflow-x-auto">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
              <div><h2 className="font-bold text-ink">{detail.title} — {detail.rules.length} rules</h2><p className="text-xs text-ink-muted">{detail.disclaimer}</p></div>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wider text-ink-muted"><tr><th className="px-4 py-2.5">ID</th><th className="px-4 py-2.5">Rule (IF … THEN)</th><th className="px-4 py-2.5">Implies</th><th className="px-4 py-2.5">Type</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {detail.rules.map((r) => {
                  const cls = detail.classes[r.implies_level];
                  return (
                    <tr key={r.id} className="align-top hover:bg-brand-50/30">
                      <td className="px-4 py-3 font-mono text-xs text-ink-muted">{r.id}</td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-ink">{r.name} <span className="ml-1 text-[11px] font-normal text-ink-muted">· {r.category}</span></div>
                        <div className="mt-1 font-mono text-[11.5px] text-brand-800">
                          IF {r.conditions.map((c) => `${detail.features.find((f) => f.name === c.feature)?.label ?? c.feature} ${OP[c.op]} ${Array.isArray(c.value) ? c.value.join("/") : c.value}`).join(r.logic === "all" ? " AND " : " OR ")}
                        </div>
                        <div className="mt-1 text-xs text-ink-soft">→ {r.recommendation}</div>
                      </td>
                      <td className="px-4 py-3"><ToneBadge tone={cls.tone}>{cls.label}</ToneBadge></td>
                      <td className="px-4 py-3"><span className={cx("chip", r.severity === "hard" ? "bg-rose-50 text-rose-700" : "bg-slate-100 text-ink-muted")}>{r.severity === "hard" ? "Mandatory" : "Advisory"}</span></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="space-y-4">
            <div className="card p-5">
              <div className="mb-3 flex items-center gap-2"><span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-50 text-brand-600"><LuBrain /></span><h3 className="text-sm font-bold text-ink">Neural model</h3>
                <button onClick={retrain} disabled={training} className="btn-secondary ml-auto !px-2.5 !py-1.5 text-xs">{training ? <LuLoader className="animate-spin" /> : <LuRefreshCw />} Retrain</button></div>
              {!model ? <Spinner /> : (
                <div className="space-y-2 text-xs">
                  <div className="rounded-lg bg-slate-50 p-2.5 font-mono text-[11px] text-ink-soft">{model.architecture}</div>
                  {[["Test accuracy", pct(model.test_accuracy, 1)], ["Macro F1", model.test_f1_macro.toFixed(3)], ["Training samples", model.train_samples], ["Test samples", model.test_samples], ["Epochs (early stopping)", model.epochs], ["Trained", new Date(model.trained_at).toLocaleString()]].map(([k, v]) => (
                    <div key={String(k)} className="flex justify-between"><span className="text-ink-muted">{k}</span><span className="font-semibold text-ink">{v}</span></div>
                  ))}
                  <div className="pt-2 text-[11px] font-semibold text-ink-muted">Training loss</div>
                  <LossCurve values={model.loss_curve} />
                  <div className="text-[11px] font-semibold text-ink-muted">Class distribution (train)</div>
                  <div className="flex flex-wrap gap-1.5">{Object.entries(model.class_distribution).map(([k, v]) => <span key={k} className="chip bg-slate-100 text-ink-soft">{k}: {v}</span>)}</div>
                </div>
              )}
            </div>
            <div className="card p-5">
              <h3 className="mb-3 text-sm font-bold text-ink">Input schema ({detail.features.length})</h3>
              <ul className="space-y-1.5 text-xs">
                {detail.features.map((f) => <li key={f.name} className="flex justify-between gap-2"><span className="text-ink-soft">{f.label}</span><span className="font-mono text-ink-muted">{f.kind === "select" ? f.options.join(" / ") : `${f.min}–${f.max} ${f.unit}`}</span></li>)}
              </ul>
              {Object.keys(detail.derived_features).length > 0 && (
                <>
                  <h4 className="mb-1.5 mt-4 text-xs font-bold text-brand-700">Derived facts</h4>
                  <ul className="space-y-1 text-[11px] text-ink-muted">{Object.entries(detail.derived_features).map(([k, v]) => <li key={k}>• {v}</li>)}</ul>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function KnowledgeBasePage() {
  return <Suspense fallback={<Spinner />}><KB /></Suspense>;
}
