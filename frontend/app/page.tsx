import Link from "next/link";
import {
  LuArrowRight,
  LuBadgeCheck,
  LuBrain,
  LuChartBar,
  LuCircleCheck,
  LuEye,
  LuGitMerge,
  LuGraduationCap,
  LuHeartPulse,
  LuHistory,
  LuLandmark,
  LuMessagesSquare,
  LuScale,
  LuServerCog,
  LuShieldAlert,
  LuShieldCheck,
  LuSparkles,
  LuTriangleAlert,
  LuWorkflow,
} from "react-icons/lu";
import { Logo } from "@/components/primitives";
import { AGENTS, PipelineFlow } from "@/components/Pipeline";

const DOMAINS = [
  { icon: LuHeartPulse, name: "Healthcare", title: "Health risk assessment", text: "Blood pressure, glucose, BMI and lipids checked against clinical screening rules." },
  { icon: LuLandmark, name: "Finance", title: "Loan eligibility & credit risk", text: "Credit score bands, debt-to-income limits, income and employment policy." },
  { icon: LuShieldAlert, name: "Cyber Security", title: "Transaction fraud detection", text: "Velocity, device, location, KYC and sanctions rules for suspicious payments." },
  { icon: LuServerCog, name: "IT Troubleshooting", title: "Failure detection & recovery", text: "CPU, memory, latency and error-rate monitoring with suggested actions." },
  { icon: LuGraduationCap, name: "Education", title: "Student performance", text: "Attendance requirements, pass marks and backlogs to identify students needing support." },
];

const FEATURES = [
  { icon: LuMessagesSquare, title: "ChatGPT-style assistant", text: "Ask in plain language. The Coordinator detects intent and domain, extracts parameters and remembers context for what-if follow-ups." },
  { icon: LuGitMerge, title: "Neural + symbolic fusion", text: "Confidence-weighted fusion of learned predictions and rule-based reasoning, with mandatory-rule override." },
  { icon: LuEye, title: "Explainable by design", text: "Every answer lists the rules triggered, feature attributions, confidence, counterfactuals and recommendations." },
  { icon: LuShieldCheck, title: "Validated decisions", text: "A Validation Agent checks inputs, rule consistency and confidence — and flags uncertain cases for human review." },
  { icon: LuHistory, title: "Decision history", text: "All decisions are stored with their full evidence trail; compare two cases side by side and rate explanations." },
  { icon: LuChartBar, title: "Live evaluation", text: "Benchmark the hybrid system against a conventional neural network on accuracy, precision, recall, F1 and consistency." },
];

const OBJECTIVES = [
  "Develop a multi-agent decision-support system using symbolic and neural AI",
  "Use neural models to analyse complex and unstructured data",
  "Use symbolic rules and knowledge bases for logical reasoning",
  "Design specialised agents for reasoning, validation and explanation",
  "Enable agents to communicate and collaborate on a final decision",
  "Provide human-readable explanations for every decision",
  "Evaluate accuracy, consistency and interpretability",
];

function HeroPreview() {
  return (
    <div className="relative">
      <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-br from-brand-200/60 via-brand-100/40 to-transparent blur-2xl" />
      <div className="card overflow-hidden shadow-lift">
        <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-300" /><span className="h-2.5 w-2.5 rounded-full bg-amber-300" /><span className="h-2.5 w-2.5 rounded-full bg-emerald-300" />
          <span className="ml-2 text-xs font-medium text-ink-muted">AI Assistant</span>
        </div>
        <div className="space-y-4 p-5">
          <div className="ml-auto max-w-[85%] rounded-2xl rounded-tr-md bg-brand-600 px-4 py-2.5 text-sm text-white">
            Is this transaction suspicious? ₹85,000 at 2 AM from a new device, abroad. Average spend is ₹4,000.
          </div>
          <div className="flex flex-wrap gap-1.5 text-[11px]">
            <span className="chip bg-brand-50 text-brand-700"><LuSparkles /> intent: analyze · 100%</span>
            <span className="chip bg-white text-ink-soft ring-1 ring-slate-200"><LuShieldAlert className="text-brand-600" /> fraud detection</span>
          </div>
          <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4">
            <div className="flex items-center gap-3">
              <div className="grid h-14 w-14 place-items-center rounded-full border-[5px] border-rose-400 bg-white text-sm font-extrabold text-ink">95%</div>
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wider text-ink-muted">Final decision</div>
                <div className="text-lg font-extrabold text-rose-700">Likely Fraud</div>
                <div className="text-xs text-ink-muted">Confidence-weighted fusion · 3 rules triggered</div>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {["FR-03 Large amount, new device", "FR-04 Unusual amount", "FR-07 Odd-hour international"].map((x) => (
                <span key={x} className="chip bg-white text-[10.5px] text-rose-700 ring-1 ring-rose-100">{x}</span>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-5 gap-1.5">
            {AGENTS.map(({ icon: Icon, name }) => (
              <div key={name} className="flex flex-col items-center gap-1 rounded-xl bg-slate-50 py-2 text-center">
                <Icon className="text-brand-600" />
                <span className="text-[9.5px] font-semibold leading-tight text-ink-soft">{name.replace(" Agent", "")}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="bg-white">
      {/* ------------------------------------------------ nav */}
      <header className="sticky top-0 z-40 border-b border-slate-100 bg-white/85 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-6 px-4 py-3 sm:px-6 lg:px-8">
          <Logo />
          <nav className="ml-6 hidden items-center gap-6 text-sm font-medium text-ink-soft md:flex">
            <a href="#how" className="hover:text-brand-700">How it works</a>
            <a href="#domains" className="hover:text-brand-700">Domains</a>
            <a href="#features" className="hover:text-brand-700">Features</a>
            <a href="#objectives" className="hover:text-brand-700">Objectives</a>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <Link href="/dashboard" className="btn-ghost hidden sm:inline-flex">Dashboard</Link>
            <Link href="/chat" className="btn-primary whitespace-nowrap">Launch<span className="hidden sm:inline"> assistant</span> <LuArrowRight /></Link>
          </div>
        </div>
      </header>

      {/* ------------------------------------------------ hero */}
      <section className="relative overflow-hidden">
        <div className="grid-bg absolute inset-0 -z-10 [mask-image:radial-gradient(ellipse_at_top,black,transparent_70%)]" />
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 pb-20 pt-16 sm:px-6 lg:grid-cols-2 lg:px-8 lg:pt-24">
          <div>
            <span className="chip border border-brand-200 bg-brand-50 text-brand-700"><LuSparkles /> Neuro-symbolic · Multi-agent · Explainable</span>
            <h1 className="mt-5 text-4xl font-extrabold leading-[1.1] tracking-tight text-ink sm:text-5xl lg:text-[3.4rem]">
              A Hybrid Symbolic-Neural Framework for <span className="bg-gradient-to-r from-brand-600 to-brand-800 bg-clip-text text-transparent">Interpretable Decision Support</span>
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-ink-muted">
              An AI assistant where a team of specialised agents — neural prediction, rule-based reasoning, validation and explanation —
              collaborate to give answers that are <b className="text-ink-soft">accurate, validated and transparent</b>.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/chat" className="btn-primary !px-6 !py-3 text-base"><LuMessagesSquare /> Start a conversation</Link>
              <Link href="/analyze" className="btn-secondary !px-6 !py-3 text-base">Try the domain analyzer</Link>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-sm text-ink-muted">
              {["5 decision domains", "5 collaborating agents", "47 knowledge-base rules", "100% rule-consistent decisions"].map((t) => (
                <span key={t} className="flex items-center gap-1.5"><LuCircleCheck className="text-brand-600" />{t}</span>
              ))}
            </div>
          </div>
          <HeroPreview />
        </div>
      </section>

      {/* ------------------------------------------------ problem */}
      <section className="border-y border-slate-100 bg-slate-50/70">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
          <div className="card p-6">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-amber-50 text-lg text-amber-600"><LuBrain /></span>
            <h3 className="mt-4 font-bold text-ink">Neural networks are black boxes</h3>
            <p className="mt-1 text-sm text-ink-muted">They learn complex patterns and predict accurately, but cannot easily explain why a decision was made.</p>
          </div>
          <div className="card p-6">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-amber-50 text-lg text-amber-600"><LuScale /></span>
            <h3 className="mt-4 font-bold text-ink">Symbolic AI is rigid</h3>
            <p className="mt-1 text-sm text-ink-muted">Rules are transparent and easy to follow, but brittle with noisy, incomplete or unstructured data.</p>
          </div>
          <div className="card border-brand-200 bg-brand-600 p-6 text-white">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-white/15 text-lg"><LuBadgeCheck /></span>
            <h3 className="mt-4 font-bold">The hybrid framework combines both</h3>
            <p className="mt-1 text-sm text-brand-100">Neural learning for prediction, symbolic reasoning for logic and validation, and collaborating agents for clear, trustworthy decisions.</p>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------ how it works */}
      <section id="how" className="mx-auto max-w-7xl scroll-mt-20 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <div className="section-title">How it works</div>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-ink sm:text-4xl">A team of AI specialists, not a single model</h2>
          <p className="mt-3 text-ink-muted">The Coordinator understands your question and hands it to the right agents. Their outputs are fused, verified and explained before you see the answer.</p>
        </div>
        <div className="mt-12"><PipelineFlow /></div>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {AGENTS.map(({ icon: Icon, name, text }, i) => (
            <div key={name} className="card p-5 transition hover:-translate-y-0.5 hover:shadow-lift">
              <div className="flex items-center gap-2">
                <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-50 text-brand-600"><Icon /></span>
                <span className="font-mono text-xs text-ink-muted">0{i + 1}</span>
              </div>
              <h3 className="mt-3 font-bold text-ink">{name}</h3>
              <p className="mt-1 text-sm text-ink-muted">{text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ------------------------------------------------ domains */}
      <section id="domains" className="scroll-mt-20 bg-gradient-to-b from-brand-950 to-brand-900 text-white">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="grid gap-10 lg:grid-cols-[1fr_1.6fr]">
            <div>
              <div className="text-sm font-bold uppercase tracking-wider text-brand-300">One engine · many domains</div>
              <h2 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">A reusable decision engine</h2>
              <p className="mt-4 text-brand-100">
                Orchestration, fusion and explanation are shared. Each domain only contributes its own dataset, trained neural model,
                input schema and knowledge base — so new domains plug in without changing the agents.
              </p>
              <Link href="/architecture" className="btn mt-6 bg-white text-brand-800 hover:bg-brand-50"><LuWorkflow /> Explore the architecture</Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {DOMAINS.map(({ icon: Icon, name, title, text }) => (
                <div key={name} className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur transition hover:bg-white/10">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-white text-lg text-brand-700"><Icon /></span>
                  <div className="mt-3 text-xs font-semibold uppercase tracking-wider text-brand-300">{name}</div>
                  <h3 className="font-bold">{title}</h3>
                  <p className="mt-1 text-sm text-brand-100/80">{text}</p>
                </div>
              ))}
              <div className="flex flex-col justify-center rounded-2xl border border-dashed border-white/20 p-5">
                <div className="font-bold">+ Your domain</div>
                <p className="mt-1 text-sm text-brand-100/80">Add a folder with config, rules and vocabulary — the Domain Manager discovers it automatically.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------ features */}
      <section id="features" className="mx-auto max-w-7xl scroll-mt-20 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <div className="section-title">Platform features</div>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-ink sm:text-4xl">Accurate, validated and transparent answers</h2>
        </div>
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, text }) => (
            <div key={title} className="card p-6">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-xl text-white shadow-lift"><Icon /></span>
              <h3 className="mt-4 text-lg font-bold text-ink">{title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ------------------------------------------------ objectives */}
      <section id="objectives" className="scroll-mt-20 border-t border-slate-100 bg-slate-50/70">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-20 sm:px-6 lg:grid-cols-2 lg:px-8">
          <div>
            <div className="section-title">Project objectives</div>
            <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">What the framework delivers</h2>
            <ul className="mt-6 space-y-3">
              {OBJECTIVES.map((o) => (
                <li key={o} className="flex gap-3 text-ink-soft"><LuCircleCheck className="mt-0.5 shrink-0 text-lg text-brand-600" />{o}</li>
              ))}
            </ul>
          </div>
          <div className="card self-start p-6">
            <div className="flex items-center gap-2 text-sm font-bold text-ink"><LuTriangleAlert className="text-amber-500" /> Example: when the agents disagree</div>
            <p className="mt-3 text-sm text-ink-muted">
              Suppose the neural network sees a strong income and a clean repayment record and predicts <b className="text-ink-soft">Low Risk</b> —
              but the credit score is 560, below the mandatory minimum of 600.
            </p>
            <div className="mt-4 space-y-2 text-sm">
              <div className="flex items-center gap-2 rounded-xl bg-slate-50 p-3"><LuBrain className="text-brand-600" /> Neural Agent → <b>Low Risk</b></div>
              <div className="flex items-center gap-2 rounded-xl bg-slate-50 p-3"><LuScale className="text-brand-600" /> Reasoning Agent → FN-01 violated → <b>at least High Risk</b></div>
              <div className="flex items-center gap-2 rounded-xl bg-brand-50 p-3 text-brand-900"><LuGitMerge className="text-brand-600" /> Coordinator → rule override → <b>High Risk</b>, explained</div>
            </div>
            <Link href="/analyze?domain=finance" className="btn-primary mt-5 w-full">Try it yourself <LuArrowRight /></Link>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------ CTA */}
      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-600 to-brand-800 px-8 py-14 text-center text-white shadow-lift">
          <div className="grid-bg absolute inset-0 opacity-30" />
          <h2 className="relative text-3xl font-extrabold tracking-tight sm:text-4xl">Ask your first question</h2>
          <p className="relative mx-auto mt-3 max-w-xl text-brand-100">Describe a patient, a loan, a transaction, a server or a student — and see how the agents reason.</p>
          <div className="relative mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/chat" className="btn bg-white !px-6 !py-3 text-base text-brand-800 hover:bg-brand-50"><LuMessagesSquare /> Open the assistant</Link>
            <Link href="/evaluation" className="btn border border-white/30 !px-6 !py-3 text-base text-white hover:bg-white/10"><LuChartBar /> See the evaluation</Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-100">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-6 px-4 py-8 text-sm text-ink-muted sm:px-6 lg:px-8">
          <Logo />
          <div className="leading-relaxed">A Hybrid Symbolic-Neural Framework for Interpretable Decision Support</div>
          <div className="ml-auto text-xs">Decision-support output only — not medical, financial or legal advice.</div>
        </div>
      </footer>
    </div>
  );
}
