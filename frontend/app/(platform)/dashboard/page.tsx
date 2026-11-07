"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LuActivity, LuArrowRight, LuGitMerge, LuLayoutDashboard, LuMessagesSquare, LuShieldCheck, LuStar, LuTarget } from "react-icons/lu";
import { ErrorBox, PageHeader, Spinner, StatCard, ToneBadge } from "@/components/primitives";
import { api, ApiError } from "@/lib/api";
import { domainIcon, pct, timeAgo } from "@/lib/ui";
import type { DomainSummary, EvaluationRun, Stats } from "@/lib/types";

export default function DashboardPage() {
  const [domains, setDomains] = useState<DomainSummary[] | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [evals, setEvals] = useState<EvaluationRun[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    Promise.all([api.domains(), api.stats(), api.evaluation()])
      .then(([d, s, e]) => { setDomains(d); setStats(s); setEvals(e); })
      .catch((e: ApiError) => setError(e.message));
  };
  useEffect(load, []);

  if (error) return <ErrorBox message={error} onRetry={load} />;
  if (!domains || !stats) return <Spinner />;

  const evalBy = Object.fromEntries(evals.map((e) => [e.domain, e]));
  const total = Object.values(stats.by_tone).reduce((a, b) => a + b, 0) || 1;

  return (
    <>
      <PageHeader icon={<LuLayoutDashboard />} title="Dashboard" subtitle="One common neuro-symbolic engine, five domain configurations. Monitor decisions, agent behaviour and model quality."
        actions={<Link href="/chat" className="btn-primary"><LuMessagesSquare /> Ask the assistant</Link>} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Decisions made" value={stats.total_decisions} hint="Across all domains" icon={<LuActivity />} />
        <StatCard label="Avg. confidence" value={pct(stats.avg_confidence)} hint="Final fused confidence" icon={<LuTarget />} />
        <StatCard label="Rule overrides" value={pct(stats.override_rate, 1)} hint={`Conflicts detected: ${pct(stats.conflict_rate, 1)}`} icon={<LuGitMerge />} />
        <StatCard label="Explanation rating" value={stats.avg_feedback ? `${stats.avg_feedback.toFixed(1)}/5` : "—"} hint={`${stats.feedback_count} user ratings`} icon={<LuStar />} />
      </div>

      <h2 className="mb-3 mt-8 section-title">Domains</h2>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {domains.map((d) => {
          const Icon = domainIcon(d.id);
          const ev = evalBy[d.id];
          return (
            <div key={d.id} className="card flex flex-col p-5 transition hover:shadow-lift">
              <div className="flex items-start gap-3">
                <span className="grid h-11 w-11 place-items-center rounded-xl bg-brand-50 text-xl text-brand-600"><Icon /></span>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold text-brand-700">{d.name}</div>
                  <div className="font-bold text-ink">{d.title}</div>
                </div>
                <span className="chip bg-slate-100 text-ink-muted">{stats.by_domain[d.id] ?? 0} runs</span>
              </div>
              <p className="mt-3 line-clamp-3 text-sm text-ink-muted">{d.description}</p>
              <div className="mt-4 grid grid-cols-3 gap-2 rounded-xl bg-slate-50 p-3 text-center">
                <div><div className="text-sm font-bold text-ink">{d.feature_count}</div><div className="text-[10.5px] text-ink-muted">inputs</div></div>
                <div><div className="text-sm font-bold text-ink">{d.rule_count}</div><div className="text-[10.5px] text-ink-muted">rules</div></div>
                <div><div className="text-sm font-bold text-ink">{ev ? pct(ev.systems.hybrid.accuracy, 1) : "—"}</div><div className="text-[10.5px] text-ink-muted">hybrid acc.</div></div>
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5">{d.classes.map((c) => <ToneBadge key={c.key} tone={c.tone}>{c.label}</ToneBadge>)}</div>
              <div className="mt-auto flex gap-2 pt-4">
                <Link href={`/analyze?domain=${d.id}`} className="btn-primary flex-1 !py-2">Analyse <LuArrowRight /></Link>
                <Link href={`/knowledge-base?domain=${d.id}`} className="btn-secondary !py-2">Rules</Link>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 grid gap-4 lg:grid-cols-3">
        <div className="card p-5 lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="section-title">Recent decisions</h2>
            <Link href="/history" className="text-xs font-semibold text-brand-700 hover:underline">View all</Link>
          </div>
          {stats.recent.length === 0 ? (
            <p className="py-8 text-center text-sm text-ink-muted">No decisions yet — try the <Link className="font-semibold text-brand-700" href="/chat">AI assistant</Link> or the <Link className="font-semibold text-brand-700" href="/analyze">analyzer</Link>.</p>
          ) : (
            <div className="divide-y divide-slate-100">
              {stats.recent.map((r) => {
                const Icon = domainIcon(r.domain);
                return (
                  <Link key={r.id} href={`/history/${r.id}`} className="flex items-center gap-3 py-2.5 hover:bg-slate-50">
                    <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-50 text-brand-600"><Icon /></span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-sm font-medium text-ink">{r.domain_name}</span>
                      <span className="text-[11px] text-ink-muted">{timeAgo(r.timestamp)} · {r.triggered_rules} rules triggered{r.override_applied ? " · override" : ""}</span>
                    </span>
                    <ToneBadge tone={r.final_tone}>{r.final_label}</ToneBadge>
                    <span className="w-12 text-right font-mono text-xs text-ink-muted">{pct(r.confidence)}</span>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
        <div className="card p-5">
          <h2 className="mb-4 section-title">Outcome distribution</h2>
          {(["success", "warning", "danger"] as const).map((t) => (
            <div key={t} className="mb-3">
              <div className="mb-1 flex justify-between text-xs"><span className="capitalize text-ink-soft">{t === "success" ? "Favourable" : t === "warning" ? "Caution" : "Critical"}</span><span className="font-mono text-ink-muted">{stats.by_tone[t]}</span></div>
              <div className="h-2 rounded-full bg-slate-100"><div className={`h-full rounded-full ${t === "success" ? "bg-emerald-500" : t === "warning" ? "bg-amber-500" : "bg-rose-500"}`} style={{ width: `${(stats.by_tone[t] / total) * 100}%` }} /></div>
            </div>
          ))}
          <div className="mt-5 flex items-start gap-2 rounded-xl bg-brand-50 p-3 text-xs text-brand-900">
            <LuShieldCheck className="mt-0.5 shrink-0 text-brand-600" />
            <span>{pct(stats.review_rate, 1)} of decisions were flagged by the Validation Agent for human review.</span>
          </div>
        </div>
      </div>
    </>
  );
}
