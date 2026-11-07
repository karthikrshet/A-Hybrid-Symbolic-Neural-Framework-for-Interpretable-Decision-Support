import { LuArrowDown, LuArrowRight, LuBrain, LuFileText, LuGitMerge, LuMessagesSquare, LuScale, LuShieldCheck, LuSparkles } from "react-icons/lu";
import type { IconType } from "react-icons";

export const AGENTS: { icon: IconType; name: string; short: string; text: string }[] = [
  { icon: LuGitMerge, name: "Coordinator Agent", short: "Routes & fuses", text: "Understands the task, selects the domain and agents, manages communication and fuses neural and symbolic results into one decision." },
  { icon: LuBrain, name: "Neural Agent", short: "Predicts patterns", text: "A feed-forward neural network trained per domain predicts the outcome with a confidence score and a feature attribution." },
  { icon: LuScale, name: "Reasoning Agent", short: "Applies rules", text: "Evaluates the domain's IF-THEN knowledge base — thresholds, constraints and policies — with full traceability." },
  { icon: LuShieldCheck, name: "Validation Agent", short: "Checks reliability", text: "Validates inputs, verifies consistency with mandatory rules, checks confidence and flags cases for human review." },
  { icon: LuFileText, name: "Explanation Agent", short: "Explains why", text: "Turns every agent's evidence into a human-readable justification, counterfactuals and recommendations." },
];

export function PipelineFlow() {
  const step = (Icon: IconType, title: string, text: string, accent = false) => (
    <div className={`flex min-w-0 flex-1 flex-col items-center rounded-2xl border p-4 text-center ${accent ? "border-brand-600 bg-brand-600 text-white shadow-lift" : "border-slate-200 bg-white"}`}>
      <span className={`grid h-10 w-10 place-items-center rounded-xl text-lg ${accent ? "bg-white/15" : "bg-brand-50 text-brand-600"}`}><Icon /></span>
      <div className={`mt-2 text-sm font-bold ${accent ? "text-white" : "text-ink"}`}>{title}</div>
      <div className={`mt-0.5 text-[11.5px] ${accent ? "text-brand-100" : "text-ink-muted"}`}>{text}</div>
    </div>
  );
  const arrow = (
    <div className="flex items-center justify-center text-brand-300">
      <LuArrowRight className="hidden text-xl lg:block" />
      <LuArrowDown className="text-xl lg:hidden" />
    </div>
  );
  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-stretch">
      {step(LuMessagesSquare, "User question", "Chat or structured form")}
      {arrow}
      {step(LuGitMerge, "Coordinator", "Intent, domain & parameters", true)}
      {arrow}
      <div className="flex flex-1 flex-col gap-2 lg:min-w-[190px]">
        <div className="flex flex-1 items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand-50 text-brand-600"><LuBrain /></span><div className="text-left"><div className="text-sm font-bold text-ink">Neural Agent</div><div className="text-[11px] text-ink-muted">Prediction + confidence</div></div></div>
        <div className="flex flex-1 items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand-50 text-brand-600"><LuScale /></span><div className="text-left"><div className="text-sm font-bold text-ink">Reasoning Agent</div><div className="text-[11px] text-ink-muted">IF-THEN rules</div></div></div>
      </div>
      {arrow}
      {step(LuShieldCheck, "Fusion + validation", "Weighted fusion, rule override, checks")}
      {arrow}
      {step(LuSparkles, "Explained answer", "Decision + reasoning + evidence + confidence", true)}
    </div>
  );
}
