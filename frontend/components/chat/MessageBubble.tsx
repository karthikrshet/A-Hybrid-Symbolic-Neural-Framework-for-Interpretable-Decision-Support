"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  LuBot,
  LuCheck,
  LuCopy,
  LuExternalLink,
  LuMaximize2,
  LuPencil,
  LuRotateCcw,
  LuSparkles,
  LuThumbsDown,
  LuThumbsUp,
  LuUser,
} from "react-icons/lu";
import DomainForm from "@/components/DomainForm";
import { AgentTrace } from "@/components/DecisionView";
import { ConfidenceRing, Markdown, ProbBars } from "@/components/primitives";
import { api } from "@/lib/api";
import { TONE, cx, domainIcon, fmtValue, pct } from "@/lib/ui";
import type { ChatMessage, DomainDetail, Inputs } from "@/lib/types";

const domainCache = new Map<string, Promise<DomainDetail>>();
export function loadDomain(id: string): Promise<DomainDetail> {
  if (!domainCache.has(id)) domainCache.set(id, api.domain(id));
  return domainCache.get(id)!;
}

function RoutingStrip({ m }: { m: ChatMessage }) {
  const r = m.routing;
  if (!r) return null;
  const Icon = r.domain ? domainIcon(r.domain) : LuSparkles;
  if (m.kind === "nudge") return null;
  const extracted = Object.entries(r.extracted ?? {});
  return (
    <div className="mb-2 flex flex-wrap items-center gap-1.5 text-[11px]">
      <span className="chip bg-brand-50 text-brand-700 ring-1 ring-brand-100" title={`Intent detected by ${r.method}`}>
        <LuSparkles /> intent: {r.intent} · {pct(r.intent_confidence)}
      </span>
      {r.domain && (
        <span className="chip bg-white text-ink-soft ring-1 ring-slate-200" title="Domain routed by the Coordinator Agent">
          <Icon className="text-brand-600" /> {r.domain.replace("_", " ")} · {pct(r.domain_confidence)}
        </span>
      )}
      {r.what_if && <span className="chip bg-violet-50 text-violet-700 ring-1 ring-violet-100">what-if follow-up</span>}
      {r.llm && (r.llm.used
        ? <span className="chip bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100" title={r.llm.label}>LLM-assisted · {r.llm.label.split(" · ")[0]}</span>
        : <span className="chip bg-amber-50 text-amber-800 ring-1 ring-amber-100" title={r.llm.error ?? ""}>LLM unavailable — offline answer</span>)}
      {extracted.slice(0, 8).map(([k, v]) => (
        <span key={k} className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[10.5px] text-ink-soft" title="Parameter extracted from your message">
          {k}={fmtValue(v)}
        </span>
      ))}
    </div>
  );
}

function DecisionCard({ m, showTrace, onOpen }: { m: ChatMessage; showTrace: boolean; onOpen: () => void }) {
  const r = m.decision!;
  const fd = r.final_decision;
  const t = TONE[fd.tone];
  return (
    <div className="mt-3 overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <div className={cx("flex items-center gap-4 border-b p-4", t.bg, t.border)}>
        <ConfidenceRing value={fd.confidence} tone={fd.tone} size={64} />
        <div className="min-w-0 flex-1">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-ink-muted">{r.domain_name} · final decision</div>
          <div className={cx("text-lg font-extrabold", t.text)}>{fd.label}</div>
          <div className="text-xs text-ink-muted">{r.fusion.strategy}{r.fusion.override_applied ? ` (${r.fusion.override_rule_ids.join(", ")})` : ""}</div>
        </div>
        <button onClick={onOpen} className="btn-secondary !px-3 !py-1.5 text-xs"><LuMaximize2 /> Full analysis</button>
      </div>
      <div className="grid gap-4 p-4 sm:grid-cols-3">
        <div>
          <div className="mb-2 text-[11px] font-bold uppercase tracking-wider text-ink-muted">Neural agent</div>
          <ProbBars probs={r.neural_prediction.probabilities} highlight={r.neural_prediction.label} />
        </div>
        <div>
          <div className="mb-2 text-[11px] font-bold uppercase tracking-wider text-ink-muted">Reasoning agent</div>
          <ProbBars probs={r.symbolic_reasoning.distribution} highlight={r.symbolic_reasoning.rule_label} />
        </div>
        <div>
          <div className="mb-2 text-[11px] font-bold uppercase tracking-wider text-ink-muted">Fused result</div>
          <ProbBars probs={r.fusion.fused_probabilities} highlight={fd.label} />
        </div>
      </div>
      {r.symbolic_reasoning.triggered_rules.length > 0 && (
        <div className="flex flex-wrap gap-1.5 border-t border-slate-100 px-4 py-3">
          {r.symbolic_reasoning.triggered_rules.map((x) => (
            <span key={x.id} title={x.condition_text} className={cx("chip", x.severity === "hard" ? "bg-rose-50 text-rose-700 ring-1 ring-rose-100" : "bg-amber-50 text-amber-700 ring-1 ring-amber-100")}>
              {x.id} · {x.name}
            </span>
          ))}
        </div>
      )}
      {m.accuracy && (
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-slate-100 bg-brand-50/50 px-4 py-2.5 text-[11.5px] text-ink-soft" title="Measured on held-out test cases never used for training">
          <span className="font-semibold text-brand-800">Measured accuracy · {m.accuracy.test_samples.toLocaleString()} test cases</span>
          <span>Hybrid <b className="text-ink">{pct(m.accuracy.hybrid_accuracy, 1)}</b></span>
          <span>F1 <b className="text-ink">{m.accuracy.hybrid_f1.toFixed(3)}</b></span>
          <span>Rule-consistent <b className="text-ink">{pct(m.accuracy.hybrid_consistency)}</b></span>
          <span className="text-ink-muted">Neural alone {pct(m.accuracy.neural_accuracy, 1)}</span>
        </div>
      )}
      {showTrace && (
        <div className="border-t border-slate-100 bg-slate-50/60 p-4">
          <div className="mb-3 text-[11px] font-bold uppercase tracking-wider text-ink-muted">Agent collaboration trace</div>
          <AgentTrace steps={r.agent_trace} />
        </div>
      )}
    </div>
  );
}

function InlineForm({ domainId, initial, missing, onSubmit, busy, label }: { domainId: string; initial: Inputs; missing: string[]; onSubmit: (d: string, v: Inputs) => void; busy: boolean; label: string }) {
  const [domain, setDomain] = useState<DomainDetail | null>(null);
  const [values, setValues] = useState<Inputs>(initial);
  useEffect(() => {
    loadDomain(domainId).then(setDomain).catch(() => setDomain(null));
  }, [domainId]);
  if (!domain) return <div className="mt-3 text-xs text-ink-muted">Loading form…</div>;
  return (
    <div className="mt-3 rounded-2xl border border-brand-100 bg-brand-50/40 p-4">
      <div className="mb-3 text-xs font-semibold text-brand-800">{domain.title} — highlighted fields were not in your message</div>
      <DomainForm dense features={domain.features} values={values} onChange={setValues} highlight={missing} loading={busy} submitLabel={label} onSubmit={() => onSubmit(domainId, values)} />
    </div>
  );
}

interface Props {
  m: ChatMessage;
  showTrace: boolean;
  busy: boolean;
  isLast: boolean;
  onSuggestion: (s: string) => void;
  onStructured: (domain: string, inputs: Inputs) => void;
  onOpenDecision: (m: ChatMessage) => void;
  onRegenerate: () => void;
}

export default function MessageBubble({ m, showTrace, busy, isLast, onSuggestion, onStructured, onOpenDecision, onRegenerate }: Props) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<number | null>(m.feedback ?? null);
  const [editing, setEditing] = useState(false);

  if (m.role === "user") {
    return (
      <div className="flex animate-fade-up justify-end gap-3">
        <div className="max-w-[80%] rounded-2xl rounded-tr-md bg-brand-600 px-4 py-2.5 text-[15px] leading-relaxed text-white shadow-sm">
          <div className="whitespace-pre-wrap">{m.content}</div>
          {m.structured && <div className="mt-1 text-[11px] text-brand-100">Submitted via form · {Object.keys(m.structured.inputs).length} parameters</div>}
        </div>
        <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-200 text-ink-soft"><LuUser /></div>
      </div>
    );
  }

  const copy = async () => {
    await navigator.clipboard.writeText(m.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  const vote = async (v: number) => {
    const next = feedback === v ? null : v;
    setFeedback(next);
    try {
      await api.messageFeedback(m.id, next);
      if (m.decision_id && next !== null) await api.feedback(m.decision_id, next === 1 ? 5 : 2);
    } catch {
      /* non-critical */
    }
  };

  return (
    <div className="flex animate-fade-up gap-3">
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-500 to-brand-800 text-white shadow-lift"><LuBot /></div>
      <div className="min-w-0 flex-1">
        {m.error ? (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{m.content}</div>
        ) : (
          <>
            <RoutingStrip m={m} />
            <Markdown>{m.content}</Markdown>
            {m.kind === "decision" && m.decision && <DecisionCard m={m} showTrace={showTrace} onOpen={() => onOpenDecision(m)} />}
            {m.kind === "clarify" && m.form && (
              <InlineForm domainId={m.form.domain} initial={m.form.inputs} missing={m.form.missing} busy={busy} label="Analyse with these values" onSubmit={onStructured} />
            )}
            {m.kind === "decision" && m.form && editing && (
              <InlineForm domainId={m.form.domain} initial={m.form.inputs} missing={[]} busy={busy} label="Re-run analysis" onSubmit={(d, v) => { setEditing(false); onStructured(d, v); }} />
            )}
          </>
        )}

        <div className="mt-2 flex flex-wrap items-center gap-1 text-ink-muted">
          <button onClick={copy} className="rounded-lg p-1.5 hover:bg-slate-100 hover:text-ink" title="Copy">{copied ? <LuCheck className="text-emerald-600" /> : <LuCopy />}</button>
          {!m.error && (
            <>
              <button onClick={() => vote(1)} className={cx("rounded-lg p-1.5 hover:bg-slate-100", feedback === 1 && "text-brand-600")} title="Helpful explanation"><LuThumbsUp /></button>
              <button onClick={() => vote(-1)} className={cx("rounded-lg p-1.5 hover:bg-slate-100", feedback === -1 && "text-rose-600")} title="Not helpful"><LuThumbsDown /></button>
            </>
          )}
          {m.kind === "decision" && m.form && (
            <button onClick={() => setEditing((v) => !v)} className="rounded-lg p-1.5 hover:bg-slate-100 hover:text-ink" title="Edit parameters & re-run"><LuPencil /></button>
          )}
          {isLast && <button onClick={onRegenerate} disabled={busy} className="rounded-lg p-1.5 hover:bg-slate-100 hover:text-ink" title="Regenerate"><LuRotateCcw /></button>}
          {m.decision_id && (
            <Link href={`/history/${m.decision_id}`} className="ml-1 inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs hover:bg-slate-100 hover:text-brand-700"><LuExternalLink /> Saved to history</Link>
          )}
          <span className="ml-auto text-[11px]">{new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
        </div>

        {isLast && m.suggestions && m.suggestions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {m.suggestions.map((s) => (
              <button key={s} disabled={busy} onClick={() => onSuggestion(s)} className="rounded-full border border-brand-200 bg-white px-3 py-1.5 text-left text-xs font-medium text-brand-700 transition hover:bg-brand-50">
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
