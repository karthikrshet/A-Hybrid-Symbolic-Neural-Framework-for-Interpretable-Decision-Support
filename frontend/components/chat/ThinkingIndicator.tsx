"use client";

import { useEffect, useState } from "react";
import { LuBot } from "react-icons/lu";
import { agentIcon, cx } from "@/lib/ui";

const STEPS = [
  { agent: "Coordinator Agent", text: "Understanding the task & routing" },
  { agent: "Validation Agent", text: "Checking inputs" },
  { agent: "Neural Analysis Agent", text: "Recognising patterns" },
  { agent: "Symbolic Reasoning Agent", text: "Applying domain rules" },
  { agent: "Coordinator Agent", text: "Fusing evidence" },
  { agent: "Explanation Agent", text: "Writing the explanation" },
];

export default function ThinkingIndicator() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((x) => Math.min(x + 1, STEPS.length - 1)), 380);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="flex animate-fade-up gap-3">
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-500 to-brand-800 text-white"><LuBot /></div>
      <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
        <div className="flex items-center gap-1.5">
          {STEPS.map((s, idx) => {
            const Icon = agentIcon(s.agent);
            return (
              <span key={idx} className={cx("grid h-7 w-7 place-items-center rounded-lg text-sm transition", idx < i ? "bg-brand-100 text-brand-700" : idx === i ? "bg-brand-600 text-white shadow-lift" : "bg-slate-100 text-slate-400")}>
                <Icon />
              </span>
            );
          })}
        </div>
        <div className="mt-2 flex items-center gap-2 text-xs text-ink-muted">
          <span className="flex gap-0.5">
            <span className="h-1.5 w-1.5 animate-blink rounded-full bg-brand-500" />
            <span className="h-1.5 w-1.5 animate-blink rounded-full bg-brand-500 [animation-delay:.2s]" />
            <span className="h-1.5 w-1.5 animate-blink rounded-full bg-brand-500 [animation-delay:.4s]" />
          </span>
          <b className="font-semibold text-ink-soft">{STEPS[i].agent}</b> — {STEPS[i].text}
        </div>
      </div>
    </div>
  );
}
