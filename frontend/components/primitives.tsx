"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { LuCircleAlert, LuLoader } from "react-icons/lu";
import { TONE, cx, pct, toneForIndex } from "@/lib/ui";
import type { Tone } from "@/lib/types";

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <Link href="/" className="flex items-center gap-2.5">
      <span className="relative grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-800 shadow-lift">
        <svg viewBox="0 0 24 24" className="h-5 w-5 text-white" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
          <circle cx="6" cy="7" r="2.2" />
          <circle cx="18" cy="7" r="2.2" />
          <circle cx="12" cy="17" r="2.2" />
          <path d="M8 8.2 10.6 15M16 8.2 13.4 15M8.2 7h7.6" />
        </svg>
      </span>
      {!compact && (
        <span className="leading-tight">
          <span className="block text-[15px] font-extrabold tracking-tight text-ink">NeuroSymbolic<span className="text-brand-600">AI</span></span>
          <span className="block text-[10.5px] font-medium text-ink-muted">Interpretable Decision Support</span>
        </span>
      )}
    </Link>
  );
}

export function ToneBadge({ tone, children, size = "sm" }: { tone: Tone; children: ReactNode; size?: "sm" | "lg" }) {
  const t = TONE[tone];
  return (
    <span className={cx("chip border", t.bg, t.text, t.border, size === "lg" && "px-3 py-1 text-sm")}>
      <span className={cx("h-1.5 w-1.5 rounded-full", t.dot)} />
      {children}
    </span>
  );
}

export function ProbBars({ probs, highlight }: { probs: Record<string, number>; highlight?: string }) {
  const entries = Object.entries(probs);
  return (
    <div className="space-y-2">
      {entries.map(([label, p], i) => {
        const t = TONE[toneForIndex(i)];
        return (
          <div key={label}>
            <div className="mb-1 flex justify-between text-xs">
              <span className={cx("font-medium", label === highlight ? "text-ink" : "text-ink-muted")}>{label}</span>
              <span className="font-mono font-semibold text-ink-soft">{pct(p, 1)}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-100">
              <div className={cx("h-full rounded-full transition-all duration-700", t.bar, label !== highlight && "opacity-40")} style={{ width: `${Math.max(p * 100, 1)}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function ConfidenceRing({ value, tone, size = 76 }: { value: number; tone: Tone; size?: number }) {
  const r = (size - 10) / 2;
  const c = 2 * Math.PI * r;
  const color = tone === "success" ? "#10b981" : tone === "warning" ? "#f59e0b" : "#f43f5e";
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="#e2e8f0" strokeWidth="7" fill="none" />
        <circle cx={size / 2} cy={size / 2} r={r} stroke={color} strokeWidth="7" fill="none" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c * (1 - value)} style={{ transition: "stroke-dashoffset .8s ease" }} />
      </svg>
      <div className="absolute inset-0 grid place-items-center">
        <div className="text-center leading-none">
          <div className="text-lg font-extrabold text-ink">{Math.round(value * 100)}%</div>
          {size >= 84 && <div className="mt-0.5 text-[9px] font-semibold uppercase tracking-wider text-ink-muted">confidence</div>}
        </div>
      </div>
    </div>
  );
}

export function Markdown({ children }: { children: string }) {
  return (
    <div className="md">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  );
}

export function PageHeader({ title, subtitle, icon, actions }: { title: string; subtitle?: string; icon?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="flex items-start gap-3">
        {icon && <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-brand-50 text-xl text-brand-600">{icon}</div>}
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-ink">{title}</h1>
          {subtitle && <p className="mt-1 max-w-3xl text-sm text-ink-muted">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-sm text-ink-muted">
      <LuLoader className="animate-spin text-brand-600" /> {label ?? "Loading…"}
    </div>
  );
}

export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
      <LuCircleAlert className="mt-0.5 shrink-0 text-lg" />
      <div className="flex-1">
        <div className="font-semibold">Something went wrong</div>
        <div className="mt-0.5 break-words text-rose-700">{message}</div>
      </div>
      {onRetry && <button onClick={onRetry} className="btn-secondary !py-1.5">Retry</button>}
    </div>
  );
}

export function StatCard({ label, value, hint, icon }: { label: string; value: ReactNode; hint?: string; icon?: ReactNode }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-ink-muted">{label}</span>
        {icon && <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-50 text-brand-600">{icon}</span>}
      </div>
      <div className="mt-2 text-3xl font-extrabold tracking-tight text-ink">{value}</div>
      {hint && <div className="mt-1 text-xs text-ink-muted">{hint}</div>}
    </div>
  );
}

export function EmptyState({ icon, title, text, action }: { icon: ReactNode; title: string; text: string; action?: ReactNode }) {
  return (
    <div className="card flex flex-col items-center px-6 py-14 text-center">
      <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-50 text-2xl text-brand-600">{icon}</div>
      <h3 className="mt-4 text-lg font-bold text-ink">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-ink-muted">{text}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
