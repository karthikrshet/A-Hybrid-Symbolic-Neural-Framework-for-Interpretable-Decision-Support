"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import type { IconType } from "react-icons";
import {
  LuBookOpen,
  LuChartBar,
  LuHistory,
  LuLayers,
  LuLayoutDashboard,
  LuMenu,
  LuMessagesSquare,
  LuSlidersHorizontal,
  LuX,
} from "react-icons/lu";
import { Logo } from "@/components/primitives";
import { API_BASE } from "@/lib/api";
import { cx } from "@/lib/ui";

const NAV: { href: string; label: string; icon: IconType; hint: string }[] = [
  { href: "/chat", label: "AI Assistant", icon: LuMessagesSquare, hint: "Chat with the agent team" },
  { href: "/dashboard", label: "Dashboard", icon: LuLayoutDashboard, hint: "Overview & domains" },
  { href: "/analyze", label: "Domain Analyzer", icon: LuSlidersHorizontal, hint: "Structured decision form" },
  { href: "/history", label: "Decision History", icon: LuHistory, hint: "Past decisions & compare" },
  { href: "/evaluation", label: "Evaluation", icon: LuChartBar, hint: "Hybrid vs neural benchmark" },
  { href: "/knowledge-base", label: "Knowledge Base", icon: LuBookOpen, hint: "Rules & models" },
  { href: "/architecture", label: "Architecture", icon: LuLayers, hint: "How the framework works" },
];

function useBackendStatus() {
  const [ok, setOk] = useState<boolean | null>(null);
  useEffect(() => {
    let alive = true;
    const ping = () =>
      fetch(`${API_BASE}/health`, { cache: "no-store" })
        .then((r) => alive && setOk(r.ok))
        .catch(() => alive && setOk(false));
    ping();
    const t = setInterval(ping, 15000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);
  return ok;
}

export default function PlatformShell({ children }: { children: ReactNode }) {
  const path = usePathname();
  const compact = path.startsWith("/chat");
  const [open, setOpen] = useState(false);
  const online = useBackendStatus();
  useEffect(() => setOpen(false), [path]);

  const nav = (isCompact: boolean) => (
    <nav className="flex flex-1 flex-col gap-1">
      {NAV.map(({ href, label, icon: Icon, hint }) => {
        const active = path === href || path.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            title={isCompact ? `${label} — ${hint}` : undefined}
            className={cx(
              "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
              active ? "bg-brand-600 text-white shadow-lift" : "text-ink-soft hover:bg-brand-50 hover:text-brand-700",
              isCompact && "justify-center px-0",
            )}
          >
            <Icon className="shrink-0 text-lg" />
            {!isCompact && <span className="truncate">{label}</span>}
          </Link>
        );
      })}
    </nav>
  );

  const status = (isCompact: boolean) => (
    <div className={cx("flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-ink-muted", isCompact && "justify-center px-0")} title={`Backend ${online ? "online" : "offline"}: ${API_BASE}`}>
      <span className={cx("h-2 w-2 rounded-full", online === null ? "bg-slate-300" : online ? "bg-emerald-500" : "bg-rose-500")} />
      {!isCompact && <span>{online === null ? "Connecting…" : online ? "Agents online" : "Backend offline"}</span>}
    </div>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50/60">
      {/* desktop sidebar */}
      <aside className={cx("hidden shrink-0 flex-col gap-4 border-r border-slate-200 bg-white p-3 md:flex", compact ? "w-[68px]" : "w-64")}>
        <div className={cx("px-1 py-2", compact && "flex justify-center")}><Logo compact={compact} /></div>
        {nav(compact)}
        {status(compact)}
      </aside>

      {/* mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-ink/30" onClick={() => setOpen(false)} />
          <aside className="absolute left-0 top-0 flex h-full w-72 flex-col gap-4 bg-white p-4 shadow-xl">
            <div className="flex items-center justify-between"><Logo /><button onClick={() => setOpen(false)} className="btn-ghost !p-2"><LuX /></button></div>
            {nav(false)}
            {status(false)}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 md:hidden">
          <button onClick={() => setOpen(true)} className="btn-ghost !p-2 text-lg"><LuMenu /></button>
          <Logo />
        </header>
        <main className={cx("min-h-0 flex-1", compact ? "overflow-hidden" : "overflow-y-auto")}>
          {compact ? children : <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</div>}
        </main>
      </div>
    </div>
  );
}
