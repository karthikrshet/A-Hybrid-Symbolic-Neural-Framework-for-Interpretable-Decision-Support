import { LuCode, LuDatabase, LuLayers, LuListChecks } from "react-icons/lu";
import { PageHeader } from "@/components/primitives";
import { AGENTS, PipelineFlow } from "@/components/Pipeline";

const LAYERS = [
  ["Input processing", "Health data", "Financial data", "Transaction data", "System metrics", "Student data"],
  ["Neural agent", "Risk prediction", "Credit risk", "Fraud detection", "Failure prediction", "Performance prediction"],
  ["Reasoning agent", "Clinical screening rules", "Lending policy rules", "AML / KYC rules", "SRE monitoring rules", "Academic regulations"],
  ["Coordinator", "Decision fusion", "Decision fusion", "Decision fusion", "Decision fusion", "Decision fusion"],
  ["Explanation agent", "Risk explanation", "Eligibility explanation", "Fraud explanation", "Failure explanation", "Performance explanation"],
  ["Final output", "Risk category", "Risk category", "Fraud category", "Failure category", "Performance category"],
];

const METHOD = [
  ["Requirement analysis & domain selection", "Five decision tasks selected; inputs, rules and outputs defined per domain."],
  ["Data collection & preprocessing", "Domain datasets with missing-value handling, one-hot encoding and standard scaling."],
  ["Neural prediction module", "MLP (64-32, ReLU, softmax) per domain with early stopping; outputs class probabilities."],
  ["Symbolic knowledge base", "IF-THEN rules with mandatory / advisory severity and derived facts (e.g. debt-to-income)."],
  ["Multi-agent design", "Coordinator, Neural, Reasoning, Validation and Explanation agents with strict Pydantic contracts."],
  ["Decision fusion", "Confidence-weighted fusion; rule override whenever a mandatory rule is violated; conflict detection."],
  ["Explanation generation", "Triggered rules, feature attributions, confidence, counterfactuals and recommendations."],
  ["Implementation", "Python · FastAPI · scikit-learn · rule engine · Next.js chat and dashboard interface."],
  ["Evaluation", "Hybrid vs neural-only: accuracy, precision, recall, F1, rule consistency and interpretability."],
];

export default function ArchitecturePage() {
  return (
    <>
      <PageHeader icon={<LuLayers />} title="Framework Architecture" subtitle="A reusable decision engine: the orchestration, fusion and explanation layers are shared, while each domain contributes only its dataset, model, input schema and knowledge base." />

      <section className="card p-6">
        <h2 className="mb-5 section-title">Multi-agent decision pipeline</h2>
        <PipelineFlow />
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {AGENTS.map(({ icon: Icon, name, text }) => (
          <div key={name} className="card p-5">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-brand-600 text-lg text-white"><Icon /></span>
            <h3 className="mt-3 font-bold text-ink">{name}</h3>
            <p className="mt-1 text-sm text-ink-muted">{text}</p>
          </div>
        ))}
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="mb-3 section-title">Decision fusion</h2>
          <div className="rounded-xl bg-brand-950 p-4 font-mono text-sm leading-relaxed text-brand-100">
            <div><span className="text-brand-300">P_fused</span> = w<sub>n</sub> · P<sub>neural</sub> + w<sub>s</sub> · P<sub>symbolic</sub></div>
            <div className="mt-2 text-xs text-brand-300">w<sub>s</sub> = 0.10 if conf ≥ 0.85 · 0.25 if conf ≥ 0.60 · 0.40 otherwise</div>
            <div className="mt-2">level = argmax(P_fused)</div>
            <div>if level &lt; hard_rule_level: <span className="text-amber-300">level = hard_rule_level</span>  <span className="text-xs text-brand-300"># rule override</span></div>
          </div>
          <ul className="mt-4 space-y-2 text-sm text-ink-soft">
            <li>• <b className="text-ink">Advisory rules</b> form a symbolic belief (&quot;at least level L&quot;) that is blended with the neural probabilities.</li>
            <li>• <b className="text-ink">Mandatory rules</b> are constraints: the outcome can never be less severe than they require.</li>
            <li>• <b className="text-ink">Conflicts</b> (neural vs rules) are detected, resolved and recorded for the reviewer.</li>
          </ul>
        </div>
        <div className="card p-6">
          <h2 className="mb-3 section-title">Standard decision object</h2>
          <pre className="overflow-x-auto rounded-xl bg-slate-50 p-4 text-[12px] leading-relaxed text-ink-soft">{`{
  "domain": "finance",
  "neural_prediction": { "result": "LOW_RISK", "confidence": 0.89, "attributions": [...] },
  "symbolic_reasoning": { "status": "PASSED", "triggered_rules": [], "violations": [] },
  "validation": { "consistency_ok": true, "requires_human_review": false },
  "fusion": { "strategy": "Confidence-weighted fusion", "conflict": {...} },
  "final_decision": { "result": "LOW_RISK", "confidence": 0.93 },
  "explanation": { "summary": "The prediction is consistent with the configured rules." },
  "recommendations": [...],
  "agent_trace": [...]
}`}</pre>
        </div>
      </section>

      <section className="card mt-6 overflow-x-auto p-6">
        <h2 className="mb-4 section-title">Common layer vs domain layer</h2>
        <table className="w-full min-w-[760px] text-sm">
          <thead className="text-left text-xs font-semibold uppercase tracking-wider text-ink-muted">
            <tr><th className="py-2">Common component</th><th>Healthcare</th><th>Finance</th><th>Cyber security</th><th>IT</th><th>Education</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {LAYERS.map(([c, ...cells]) => (
              <tr key={c}><td className="py-2.5 font-semibold text-brand-700">{c}</td>{cells.map((x, i) => <td key={i} className="pr-3 text-ink-soft">{x}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
        <div className="card p-6">
          <h2 className="mb-4 flex items-center gap-2 section-title"><LuListChecks /> Methodology</h2>
          <ol className="space-y-3">
            {METHOD.map(([t, d], i) => (
              <li key={t} className="flex gap-3"><span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-brand-50 text-xs font-bold text-brand-700">{i + 1}</span><div><div className="text-sm font-semibold text-ink">{t}</div><div className="text-xs text-ink-muted">{d}</div></div></li>
            ))}
          </ol>
        </div>
        <div className="space-y-4">
          <div className="card p-6">
            <h2 className="mb-3 flex items-center gap-2 section-title"><LuCode /> Technology</h2>
            <div className="flex flex-wrap gap-2">{["Python 3.10+", "FastAPI", "Pydantic v2", "scikit-learn MLP", "Rule engine", "SQLite", "Next.js 14", "TypeScript", "Tailwind CSS", "React Icons"].map((t) => <span key={t} className="chip bg-brand-50 text-brand-800">{t}</span>)}</div>
          </div>
          <div className="card p-6">
            <h2 className="mb-3 flex items-center gap-2 section-title"><LuDatabase /> Adding a new domain</h2>
            <ol className="list-decimal space-y-1 pl-5 text-sm text-ink-soft">
              <li>Create <code className="rounded bg-slate-100 px-1 text-xs">backend/app/domains/&lt;name&gt;/</code></li>
              <li><code className="rounded bg-slate-100 px-1 text-xs">config.py</code> — input schema, classes, dataset</li>
              <li><code className="rounded bg-slate-100 px-1 text-xs">rules.py</code> — IF-THEN knowledge base</li>
              <li><code className="rounded bg-slate-100 px-1 text-xs">chat.py</code> — vocabulary for the assistant</li>
              <li>Restart — the Domain Manager discovers and trains it automatically.</li>
            </ol>
          </div>
        </div>
      </section>
    </>
  );
}
