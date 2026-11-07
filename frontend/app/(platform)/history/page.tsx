"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { LuArrowLeftRight, LuDownload, LuHistory, LuSearch, LuTrash2 } from "react-icons/lu";
import { EmptyState, ErrorBox, PageHeader, Spinner, ToneBadge } from "@/components/primitives";
import { api, ApiError } from "@/lib/api";
import { cx, domainIcon, pct } from "@/lib/ui";
import type { DecisionSummary, DomainSummary } from "@/lib/types";

export default function HistoryPage() {
  const [items, setItems] = useState<DecisionSummary[] | null>(null);
  const [domains, setDomains] = useState<DomainSummary[]>([]);
  const [domain, setDomain] = useState("");
  const [query, setQuery] = useState("");
  const [onlyFlags, setOnlyFlags] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    api.decisions(domain || undefined).then(setItems).catch((e: ApiError) => setError(e.message));
  };
  useEffect(() => { api.domains().then(setDomains).catch(() => undefined); }, []);
  useEffect(load, [domain]);

  const rows = useMemo(() => (items ?? []).filter((r) =>
    (!onlyFlags || r.override_applied || r.conflict || r.requires_review) &&
    `${r.domain_name} ${r.final_label} ${r.neural_label} ${r.id}`.toLowerCase().includes(query.toLowerCase())), [items, query, onlyFlags]);

  const toggle = (id: string) => setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id].slice(-2)));

  const remove = async (id: string) => {
    await api.deleteDecision(id).catch(() => undefined);
    setSelected((s) => s.filter((x) => x !== id));
    load();
  };

  const clearAll = async () => {
    if (!confirm("Delete the entire decision history? This cannot be undone.")) return;
    await api.clearDecisions().catch(() => undefined);
    load();
  };

  const exportCsv = () => {
    const head = "id,timestamp,domain,neural,final,confidence,rules_triggered,override,conflict,review,rating";
    const body = rows.map((r) => [r.id, r.timestamp, r.domain, r.neural_label, r.final_label, r.confidence, r.triggered_rules, r.override_applied, r.conflict, r.requires_review, r.feedback_rating ?? ""].join(","));
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([[head, ...body].join("\n")], { type: "text/csv" }));
    a.download = "decision_history.csv";
    a.click();
  };

  return (
    <>
      <PageHeader icon={<LuHistory />} title="Decision History" subtitle="Every decision is stored with its full evidence trail. Select two decisions to compare them side by side."
        actions={<>
          {selected.length === 2 && <Link href={`/history/compare?a=${selected[0]}&b=${selected[1]}`} className="btn-primary"><LuArrowLeftRight /> Compare selected</Link>}
          <button onClick={exportCsv} className="btn-secondary" disabled={!rows.length}><LuDownload /> CSV</button>
          <button onClick={clearAll} className="btn-secondary hover:!text-rose-600" disabled={!items?.length}><LuTrash2 /> Clear</button>
        </>} />

      <div className="card mb-4 flex flex-wrap items-center gap-3 p-3">
        <div className="relative min-w-[220px] flex-1">
          <LuSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
          <input className="input !pl-9" placeholder="Search by outcome, domain or ID" value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <select className="input !w-auto" value={domain} onChange={(e) => setDomain(e.target.value)}>
          <option value="">All domains</option>
          {domains.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <label className="flex items-center gap-2 text-sm text-ink-soft"><input type="checkbox" checked={onlyFlags} onChange={(e) => setOnlyFlags(e.target.checked)} className="accent-brand-600" /> Overrides / conflicts / reviews only</label>
      </div>

      {error && <ErrorBox message={error} onRetry={load} />}
      {!items && !error && <Spinner />}
      {items && rows.length === 0 && <EmptyState icon={<LuHistory />} title="No decisions found" text="Decisions made in the chat assistant or the domain analyzer appear here." action={<Link href="/chat" className="btn-primary">Open the assistant</Link>} />}
      {rows.length > 0 && (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wider text-ink-muted">
              <tr>
                <th className="w-10 px-4 py-3" />
                <th className="px-4 py-3">Domain</th>
                <th className="px-4 py-3">Neural</th>
                <th className="px-4 py-3">Final decision</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Rules</th>
                <th className="px-4 py-3">Flags</th>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((r) => {
                const Icon = domainIcon(r.domain);
                return (
                  <tr key={r.id} className={cx("hover:bg-brand-50/40", selected.includes(r.id) && "bg-brand-50/60")}>
                    <td className="px-4 py-3"><input type="checkbox" checked={selected.includes(r.id)} onChange={() => toggle(r.id)} className="accent-brand-600" /></td>
                    <td className="px-4 py-3"><Link href={`/history/${r.id}`} className="flex items-center gap-2 font-medium text-ink hover:text-brand-700"><Icon className="text-brand-600" />{r.domain_name}</Link></td>
                    <td className="px-4 py-3 text-ink-muted">{r.neural_label}</td>
                    <td className="px-4 py-3"><ToneBadge tone={r.final_tone}>{r.final_label}</ToneBadge></td>
                    <td className="px-4 py-3 font-mono text-xs">{pct(r.confidence, 1)}</td>
                    <td className="px-4 py-3 font-mono text-xs">{r.triggered_rules}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {r.override_applied && <span className="chip bg-rose-50 text-[10px] text-rose-700">override</span>}
                        {r.conflict && <span className="chip bg-amber-50 text-[10px] text-amber-700">conflict</span>}
                        {r.requires_review && <span className="chip bg-violet-50 text-[10px] text-violet-700">review</span>}
                        {r.feedback_rating && <span className="chip bg-slate-100 text-[10px] text-ink-muted">★ {r.feedback_rating}</span>}
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-xs text-ink-muted">{new Date(r.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3"><button onClick={() => remove(r.id)} className="rounded p-1.5 text-ink-muted hover:bg-rose-50 hover:text-rose-600" title="Delete"><LuTrash2 /></button></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
