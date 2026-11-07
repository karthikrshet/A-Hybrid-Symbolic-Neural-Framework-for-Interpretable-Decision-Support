"use client";

import { useState } from "react";
import {
  LuBrain,
  LuCircleCheck,
  LuChevronDown,
  LuCircleX,
  LuFileText,
  LuGitMerge,
  LuLightbulb,
  LuListChecks,
  LuScale,
  LuShieldCheck,
  LuTriangleAlert,
  LuWorkflow,
} from "react-icons/lu";
import { ConfidenceRing, ProbBars, ToneBadge } from "@/components/primitives";
import { TONE, agentIcon, cx, fmtValue, pct } from "@/lib/ui";
import type { AgentStep, DecisionResult, FeatureAttribution, RuleEvaluation } from "@/lib/types";

function renderBold(text: string) {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((p, i) => (i % 2 ? <strong key={i} className="font-semibold text-ink">{p}</strong> : <span key={i}>{p}</span>));
}

export function AttributionChart({ items }: { items: FeatureAttribution[] }) {
  const max = Math.max(...items.map((a) => Math.abs(a.contribution)), 0.01);
  return (
    <div className="space-y-2.5">
      {items.map((a) => {
        const w = (Math.abs(a.contribution) / max) * 50;
        const pos = a.contribution >= 0;
        return (
          <div key={a.feature} className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)_52px] items-center gap-3 text-xs">
            <div className="truncate">
              <span className="font-medium text-ink">{a.label}</span>
              <span className="ml-1 text-ink-muted">= {fmtValue(a.value)}</span>
            </div>
            <div className="relative h-3 rounded bg-slate-100">
              <div className="absolute left-1/2 top-0 h-full w-px bg-slate-300" />
              <div
                className={cx("absolute top-0 h-full rounded", pos ? "bg-brand-500" : "bg-slate-400")}
                style={pos ? { left: "50%", width: `${w}%` } : { right: "50%", width: `${w}%` }}
              />
            </div>
            <div className={cx("text-right font-mono font-semibold", pos ? "text-brand-700" : "text-ink-muted")}>
              {pos ? "+" : ""}{(a.contribution * 100).toFixed(1)}
            </div>
          </div>
        );
      })}
      <p className="pt-1 text-[11px] text-ink-muted">Change (percentage points) in the predicted class probability when the feature is replaced by its training-data baseline. Blue = pushes towards the prediction.</p>
    </div>
  );
}

export function RuleRow({ rule }: { rule: RuleEvaluation }) {
  const fired = rule.status === "TRIGGERED";
  const hard = rule.severity === "hard";
  return (
    <div className={cx("rounded-xl border p-3", fired ? (hard ? "border-rose-200 bg-rose-50/60" : "border-amber-200 bg-amber-50/60") : "border-slate-200 bg-white")}>
      <div className="flex items-start gap-2.5">
        <span className={cx("mt-0.5 text-base", fired ? (hard ? "text-rose-600" : "text-amber-600") : "text-emerald-600")}>
          {fired ? (hard ? <LuCircleX /> : <LuTriangleAlert />) : <LuCircleCheck />}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-[11px] font-semibold text-ink-muted">{rule.id}</span>
            <span className="text-sm font-semibold text-ink">{rule.name}</span>
            <span className={cx("chip !py-0 text-[10px]", hard ? "bg-rose-100 text-rose-700" : "bg-slate-100 text-ink-muted")}>{hard ? "Mandatory" : "Advisory"}</span>
            {fired && <span className="chip !py-0 bg-white text-[10px] text-ink-soft ring-1 ring-slate-200">→ at least {rule.implies_label}</span>}
          </div>
          <div className="mt-1 font-mono text-[11px] text-brand-800">{rule.condition_text}</div>
          <div className="mt-1 text-xs text-ink-soft">{fired ? rule.description : rule.message}</div>
          {Object.keys(rule.observed).length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {Object.entries(rule.observed).map(([k, v]) => (
                <span key={k} className="rounded-md bg-white px-1.5 py-0.5 font-mono text-[10.5px] text-ink-soft ring-1 ring-slate-200">{k} = {fmtValue(v)}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function AgentTrace({ steps }: { steps: AgentStep[] }) {
  return (
    <ol className="relative space-y-3 pl-1">
      {steps.map((s, i) => {
        const Icon = agentIcon(s.agent);
        return (
          <li key={s.order} className="relative flex gap-3">
            {i < steps.length - 1 && <span className="absolute left-[17px] top-9 h-[calc(100%-18px)] w-px bg-brand-100" />}
            <span className={cx("relative z-10 grid h-9 w-9 shrink-0 place-items-center rounded-xl text-base", s.status === "warning" ? "bg-amber-50 text-amber-600 ring-1 ring-amber-200" : "bg-brand-50 text-brand-600 ring-1 ring-brand-100")}>
              <Icon />
            </span>
            <div className="min-w-0 flex-1 pb-1">
              <div className="flex flex-wrap items-baseline gap-x-2">
                <span className="text-sm font-semibold text-ink">{s.action}</span>
                <span className="text-xs text-ink-muted">{s.agent}</span>
                <span className="ml-auto font-mono text-[10.5px] text-ink-muted">{s.sender} → {s.receiver} · {s.duration_ms.toFixed(1)} ms</span>
              </div>
              <p className="mt-0.5 text-xs text-ink-soft">{s.summary}</p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

function Panel({ icon, title, children, right }: { icon: React.ReactNode; title: string; children: React.ReactNode; right?: React.ReactNode }) {
  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-50 text-brand-600">{icon}</span>
        <h3 className="text-sm font-bold text-ink">{title}</h3>
        {right && <div className="ml-auto">{right}</div>}
      </div>
      {children}
    </div>
  );
}

export function DecisionHero({ r }: { r: DecisionResult }) {
  const fd = r.final_decision;
  const t = TONE[fd.tone];
  return (
    <div className={cx("rounded-2xl border p-5", t.border, t.bg)}>
      <div className="flex flex-wrap items-center gap-5">
        <ConfidenceRing value={fd.confidence} tone={fd.tone} size={88} />
        <div className="min-w-0 flex-1">
          <div className="text-xs font-semibold uppercase tracking-wider text-ink-muted">{r.domain_name} · final decision</div>
          <div className={cx("mt-0.5 text-2xl font-extrabold tracking-tight", t.text)}>{fd.label}</div>
          <p className="mt-1 text-sm text-ink-soft">{r.explanation.summary}</p>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <span className="chip bg-white text-ink-soft ring-1 ring-slate-200"><LuGitMerge /> {r.fusion.strategy}</span>
          {r.fusion.override_applied && <span className="chip bg-rose-100 text-rose-700">Rule override: {r.fusion.override_rule_ids.join(", ")}</span>}
          {r.validation.requires_human_review ? (
            <span className="chip bg-amber-100 text-amber-800"><LuTriangleAlert /> Human review advised</span>
          ) : (
            <span className="chip bg-emerald-100 text-emerald-700"><LuShieldCheck /> Validated</span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DecisionView({ r }: { r: DecisionResult }) {
  const [showPassed, setShowPassed] = useState(false);
  const n = r.neural_prediction;
  const s = r.symbolic_reasoning;
  const f = r.fusion;

  return (
    <div className="space-y-4">
      <DecisionHero r={r} />

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel icon={<LuBrain />} title="Neural Agent" right={<ToneBadge tone={n.level === 0 ? "success" : n.level === 1 ? "warning" : "danger"}>{n.label}</ToneBadge>}>
          <ProbBars probs={n.probabilities} highlight={n.label} />
          <p className="mt-3 text-[11px] text-ink-muted">{n.model}</p>
        </Panel>
        <Panel icon={<LuScale />} title="Reasoning Agent" right={<ToneBadge tone={s.status === "PASSED" ? "success" : s.status === "WARNINGS" ? "warning" : "danger"}>{s.triggered_rules.length}/{s.rules_evaluated} triggered</ToneBadge>}>
          <ProbBars probs={s.distribution} highlight={s.rule_label} />
          <p className="mt-3 text-[11px] text-ink-muted">Rules imply at least <b className="text-ink-soft">{s.rule_label}</b></p>
        </Panel>
        <Panel icon={<LuGitMerge />} title="Coordinator · fusion" right={<span className="font-mono text-[11px] text-ink-muted">w<sub>n</sub>={f.neural_weight} · w<sub>s</sub>={f.symbolic_weight}</span>}>
          <ProbBars probs={f.fused_probabilities} highlight={r.final_decision.label} />
          <p className={cx("mt-3 text-[11px]", f.conflict.detected ? "text-amber-700" : "text-ink-muted")}>
            {f.conflict.detected ? `⚠ ${f.conflict.description}` : f.conflict.description}
          </p>
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="space-y-4 lg:col-span-3">
          <Panel icon={<LuListChecks />} title="Symbolic evidence — knowledge-base rules"
            right={<button onClick={() => setShowPassed((v) => !v)} className="text-xs font-semibold text-brand-700 hover:underline">{showPassed ? "Hide" : "Show"} passed ({s.passed_rules.length})</button>}>
            <div className="space-y-2">
              {s.triggered_rules.length === 0 && <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">All {s.rules_evaluated} rules passed — no predefined risk condition found.</div>}
              {s.triggered_rules.map((rule) => <RuleRow key={rule.id} rule={rule} />)}
              {showPassed && s.passed_rules.map((rule) => <RuleRow key={rule.id} rule={rule} />)}
            </div>
          </Panel>
          <Panel icon={<LuBrain />} title="Neural evidence — feature attribution">
            <AttributionChart items={n.attributions} />
          </Panel>
        </div>
        <div className="space-y-4 lg:col-span-2">
          <Panel icon={<LuFileText />} title="Explanation">
            <div className="space-y-3 text-sm leading-relaxed text-ink-soft">
              <p>{renderBold(r.explanation.neural)}</p>
              <p>{renderBold(r.explanation.symbolic)}</p>
              <p>{renderBold(r.explanation.fusion)}</p>
            </div>
            {r.explanation.counterfactuals.length > 0 && (
              <div className="mt-4 rounded-xl bg-brand-50/70 p-3">
                <div className="mb-1.5 text-xs font-bold text-brand-800">What would change the outcome?</div>
                <ul className="space-y-1 text-xs text-ink-soft">{r.explanation.counterfactuals.map((c) => <li key={c}>• {c}</li>)}</ul>
              </div>
            )}
            <p className="mt-3 text-[11px] italic text-ink-muted">{r.explanation.disclaimer}</p>
          </Panel>
          <Panel icon={<LuLightbulb />} title="Recommendations">
            <ul className="space-y-2">
              {r.recommendations.map((rec) => (
                <li key={rec} className="flex gap-2 text-sm text-ink-soft"><LuCircleCheck className="mt-0.5 shrink-0 text-brand-600" />{rec}</li>
              ))}
            </ul>
          </Panel>
          <Panel icon={<LuShieldCheck />} title="Validation Agent">
            <ul className="space-y-1.5 text-xs text-ink-soft">{r.validation.checks.map((c) => <li key={c}>{c}</li>)}</ul>
            {[...r.validation.input_issues, ...r.validation.out_of_distribution].length > 0 && (
              <ul className="mt-3 space-y-1 rounded-lg bg-amber-50 p-2.5 text-[11px] text-amber-800">
                {[...r.validation.input_issues, ...r.validation.out_of_distribution].map((x) => <li key={x}>• {x}</li>)}
              </ul>
            )}
          </Panel>
        </div>
      </div>

      <details className="card group p-5" open>
        <summary className="flex cursor-pointer list-none items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-50 text-brand-600"><LuWorkflow /></span>
          <h3 className="text-sm font-bold text-ink">Multi-agent communication trace</h3>
          <span className="ml-2 text-xs text-ink-muted">{r.agent_trace.length} messages · {r.processing_ms.toFixed(0)} ms</span>
          <LuChevronDown className="ml-auto text-ink-muted transition group-open:rotate-180" />
        </summary>
        <div className="mt-4"><AgentTrace steps={r.agent_trace} /></div>
      </details>

      <div className="text-right font-mono text-[11px] text-ink-muted">Decision ID {r.id} · {new Date(r.timestamp).toLocaleString()} · confidence {pct(r.final_decision.confidence, 1)}</div>
    </div>
  );
}
