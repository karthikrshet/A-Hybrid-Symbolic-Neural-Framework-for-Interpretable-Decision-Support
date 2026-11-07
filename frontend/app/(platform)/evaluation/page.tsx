"use client";

import { useEffect, useState } from "react";
import { LuChartBar, LuLoader, LuRefreshCw } from "react-icons/lu";
import { ErrorBox, PageHeader, Spinner, StatCard } from "@/components/primitives";
import { api, ApiError } from "@/lib/api";
import { cx, domainIcon, pct } from "@/lib/ui";
import type { EvaluationRun, Stats, SystemMetrics } from "@/lib/types";

const SYSTEMS = [
  { key: "neural", label: "Neural network only", color: "bg-slate-400", text: "text-slate-600" },
  { key: "symbolic", label: "Symbolic rules only", color: "bg-sky-300", text: "text-sky-700" },
  { key: "hybrid", label: "Hybrid neuro-symbolic", color: "bg-brand-600", text: "text-brand-700" },
] as const;

const METRICS: { key: keyof SystemMetrics; label: string }[] = [
  { key: "accuracy", label: "Accuracy" },
  { key: "precision", label: "Precision" },
  { key: "recall", label: "Recall" },
  { key: "f1", label: "F1-score" },
  { key: "hard_rule_consistency", label: "Rule consistency" },
  { key: "soft_rule_agreement", label: "Rule agreement" },
];

function GroupedBars({ run }: { run: EvaluationRun }) {
  return (
    <div className="grid grid-cols-3 gap-x-4 gap-y-6 sm:grid-cols-6">
      {METRICS.map((m) => (
        <div key={m.key}>
          <div className="flex h-40 items-end justify-center gap-1.5 border-b border-slate-200 px-1">
            {SYSTEMS.map((s) => {
              const v = run.systems[s.key][m.key] as number;
              return (
                <div key={s.key} className="group relative flex w-5 flex-col items-center justify-end" style={{ height: "100%" }}>
                  <span className="absolute -top-5 hidden whitespace-nowrap rounded bg-ink px-1.5 py-0.5 text-[10px] text-white group-hover:block">{pct(v, 1)}</span>
                  <div className={cx("w-full rounded-t-md transition-all duration-700", s.color)} style={{ height: `${Math.max(v * 100, 2)}%` }} />
                </div>
              );
            })}
          </div>
          <div className="mt-2 text-center text-xs font-semibold text-ink-soft">{m.label}</div>
          <div className="text-center font-mono text-[11px] text-brand-700">{pct(run.systems.hybrid[m.key] as number, 1)}</div>
        </div>
      ))}
    </div>
  );
}

function Confusion({ title, matrix, labels }: { title: string; matrix: number[][]; labels: string[] }) {
  const max = Math.max(...matrix.flat(), 1);
  return (
    <div>
      <div className="mb-2 text-xs font-bold text-ink-soft">{title}</div>
      <div className="overflow-x-auto">
        <table className="text-xs">
          <thead><tr><th className="p-1 text-left text-[10px] font-medium text-ink-muted">true ↓ / pred →</th>{labels.map((l) => <th key={l} className="p-1 text-[10px] font-semibold text-ink-muted">{l}</th>)}</tr></thead>
          <tbody>
            {matrix.map((row, i) => (
              <tr key={i}>
                <td className="whitespace-nowrap p-1 pr-2 text-[10px] font-semibold text-ink-muted">{labels[i]}</td>
                {row.map((v, j) => (
                  <td key={j} className="p-0.5">
                    <div className={cx("grid h-11 w-16 place-items-center rounded-md font-mono font-semibold", i === j ? "text-white" : v > 0 ? "text-rose-800" : "text-slate-400")}
                      style={{ background: i === j ? `rgba(37,99,235,${0.35 + 0.65 * (v / max)})` : v > 0 ? `rgba(244,63,94,${0.08 + 0.5 * (v / max)})` : "#f8fafc" }}>{v}</div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function EvaluationPage() {
  const [runs, setRuns] = useState<EvaluationRun[] | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [active, setActive] = useState("overview");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.evaluation().then(setRuns).catch((e: ApiError) => setError(e.message));
    api.stats().then(setStats).catch(() => undefined);
  }, []);

  const rerun = async () => {
    setRunning(true);
    setError(null);
    try {
      setRuns(await api.runEvaluation());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Benchmark failed");
    } finally {
      setRunning(false);
    }
  };

  if (error) return <ErrorBox message={error} />;
  if (!runs) return <Spinner label="Computing benchmark…" />;

  const avg = (k: keyof SystemMetrics, s: "neural" | "hybrid") => runs.reduce((a, r) => a + (r.systems[s][k] as number), 0) / runs.length;
  const run = runs.find((r) => r.domain === active);

  return (
    <>
      <PageHeader icon={<LuChartBar />} title="Evaluation: Hybrid vs Conventional Neural Network"
        subtitle="All metrics are computed live on held-out test sets (25% of each domain's data, never used for training or tuning). Accuracy, precision, recall and F1 measure predictive quality; consistency measures agreement with domain rules; evidence measures interpretability."
        actions={<button onClick={rerun} disabled={running} className="btn-primary">{running ? <LuLoader className="animate-spin" /> : <LuRefreshCw />} Run benchmark</button>} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Avg. F1 (hybrid)" value={avg("f1", "hybrid").toFixed(3)} hint={`Neural only: ${avg("f1", "neural").toFixed(3)}`} />
        <StatCard label="Avg. accuracy (hybrid)" value={pct(avg("accuracy", "hybrid"), 1)} hint={`Neural only: ${pct(avg("accuracy", "neural"), 1)}`} />
        <StatCard label="Rule consistency" value={pct(avg("hard_rule_consistency", "hybrid"), 1)} hint={`Neural only: ${pct(avg("hard_rule_consistency", "neural"), 1)}`} />
        <StatCard label="Explanation rating" value={stats?.avg_feedback ? `${stats.avg_feedback.toFixed(1)}/5` : "—"} hint={`${stats?.feedback_count ?? 0} user ratings (interpretability)`} />
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <button onClick={() => setActive("overview")} className={cx("rounded-xl px-4 py-2 text-sm font-semibold transition", active === "overview" ? "bg-brand-600 text-white" : "bg-white text-ink-soft ring-1 ring-slate-200 hover:text-brand-700")}>Overview</button>
        {runs.map((r) => {
          const Icon = domainIcon(r.domain);
          return <button key={r.domain} onClick={() => setActive(r.domain)} className={cx("inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition", active === r.domain ? "bg-brand-600 text-white" : "bg-white text-ink-soft ring-1 ring-slate-200 hover:text-brand-700")}><Icon />{r.domain_name}</button>;
        })}
      </div>

      {active === "overview" && (
        <div className="card mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wider text-ink-muted">
              <tr><th className="px-4 py-3">Domain</th><th className="px-4 py-3">Test cases</th><th className="px-4 py-3">Accuracy NN → Hybrid</th><th className="px-4 py-3">F1 NN → Hybrid</th><th className="px-4 py-3">Recall NN → Hybrid</th><th className="px-4 py-3">Rule consistency NN → Hybrid</th><th className="px-4 py-3">Evidence items</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {runs.map((r) => {
                const n = r.systems.neural, h = r.systems.hybrid;
                const delta = (a: number, b: number) => <span className={cx("ml-1 text-[11px] font-semibold", b - a >= 0 ? "text-emerald-600" : "text-rose-600")}>({b - a >= 0 ? "+" : ""}{((b - a) * 100).toFixed(1)})</span>;
                return (
                  <tr key={r.domain} className="hover:bg-brand-50/40">
                    <td className="px-4 py-3 font-semibold text-ink">{r.domain_name}</td>
                    <td className="px-4 py-3 font-mono text-xs">{r.test_samples}</td>
                    <td className="px-4 py-3 font-mono text-xs">{pct(n.accuracy, 1)} → <b className="text-brand-700">{pct(h.accuracy, 1)}</b>{delta(n.accuracy, h.accuracy)}</td>
                    <td className="px-4 py-3 font-mono text-xs">{n.f1.toFixed(3)} → <b className="text-brand-700">{h.f1.toFixed(3)}</b>{delta(n.f1, h.f1)}</td>
                    <td className="px-4 py-3 font-mono text-xs">{n.recall.toFixed(3)} → <b className="text-brand-700">{h.recall.toFixed(3)}</b>{delta(n.recall, h.recall)}</td>
                    <td className="px-4 py-3 font-mono text-xs">{pct(n.hard_rule_consistency, 1)} → <b className="text-brand-700">{pct(h.hard_rule_consistency, 1)}</b></td>
                    <td className="px-4 py-3 font-mono text-xs">{n.avg_evidence_items} → <b className="text-brand-700">{h.avg_evidence_items}</b></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p className="border-t border-slate-100 px-4 py-3 text-xs text-ink-muted">
            Values in brackets are percentage-point changes. Fusion weights were tuned on the training split only. Evidence items = feature attributions (neural) + rule checks and fusion rationale (hybrid).
          </p>
        </div>
      )}

      {run && (
        <div className="mt-4 space-y-4">
          <div className="card p-5">
            <div className="mb-5 flex flex-wrap items-center gap-4">
              <h2 className="text-base font-bold text-ink">{run.domain_name} — {run.test_samples} held-out test cases</h2>
              <div className="ml-auto flex flex-wrap gap-3 text-xs">{SYSTEMS.map((s) => <span key={s.key} className="flex items-center gap-1.5 text-ink-soft"><span className={cx("h-2.5 w-2.5 rounded-sm", s.color)} />{s.label}</span>)}</div>
            </div>
            <GroupedBars run={run} />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="card space-y-5 p-5">
              <Confusion title="Neural network only" matrix={run.systems.neural.confusion_matrix} labels={run.classes} />
              <Confusion title="Hybrid neuro-symbolic" matrix={run.systems.hybrid.confusion_matrix} labels={run.classes} />
            </div>
            <div className="card p-5">
              <h3 className="mb-3 text-sm font-bold text-ink">Per-class F1 & interpretability</h3>
              <table className="w-full text-xs">
                <thead className="text-left text-ink-muted"><tr><th className="py-1.5">Class</th><th>Support</th><th>Neural F1</th><th>Hybrid F1</th></tr></thead>
                <tbody className="divide-y divide-slate-100">
                  {run.systems.hybrid.per_class.map((c, i) => (
                    <tr key={c.label}><td className="py-2 font-medium text-ink">{c.label}</td><td className="font-mono">{c.support}</td><td className="font-mono">{run.systems.neural.per_class[i].f1.toFixed(3)}</td><td className="font-mono font-bold text-brand-700">{c.f1.toFixed(3)}</td></tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-5 grid grid-cols-2 gap-3 text-center">
                {[
                  ["Conflicts detected", pct(run.systems.hybrid.conflict_rate ?? 0, 1)],
                  ["Rule overrides", pct(run.systems.hybrid.override_rate ?? 0, 1)],
                  ["Symbolic justification", pct(run.systems.hybrid.symbolic_justification, 0)],
                  ["Evidence / decision", `${run.systems.neural.avg_evidence_items} → ${run.systems.hybrid.avg_evidence_items}`],
                ].map(([k, v]) => (
                  <div key={k} className="rounded-xl bg-slate-50 p-3"><div className="text-lg font-extrabold text-ink">{v}</div><div className="text-[11px] text-ink-muted">{k}</div></div>
                ))}
              </div>
              <p className="mt-4 text-[11px] text-ink-muted">Generated {new Date(run.generated_at).toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
