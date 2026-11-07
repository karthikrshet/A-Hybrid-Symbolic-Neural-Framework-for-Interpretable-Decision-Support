"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { LuSlidersHorizontal, LuSparkles } from "react-icons/lu";
import DecisionView from "@/components/DecisionView";
import DomainForm from "@/components/DomainForm";
import { EmptyState, ErrorBox, PageHeader, Spinner } from "@/components/primitives";
import { api, ApiError } from "@/lib/api";
import { cx, domainIcon } from "@/lib/ui";
import type { DecisionResult, DomainDetail, DomainSummary, Inputs } from "@/lib/types";

function Analyzer() {
  const params = useSearchParams();
  const router = useRouter();
  const [domains, setDomains] = useState<DomainSummary[]>([]);
  const [active, setActive] = useState<string>(params.get("domain") ?? "healthcare");
  const [detail, setDetail] = useState<DomainDetail | null>(null);
  const [values, setValues] = useState<Inputs>({});
  const [result, setResult] = useState<DecisionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.domains().then(setDomains).catch((e: ApiError) => setError(e.message));
  }, []);

  useEffect(() => {
    setDetail(null);
    setResult(null);
    api.domain(active)
      .then((d) => {
        setDetail(d);
        setValues(d.presets[1]?.inputs ?? Object.fromEntries(d.features.map((f) => [f.name, f.default])));
      })
      .catch((e: ApiError) => setError(e.message));
  }, [active]);

  const select = (id: string) => {
    setActive(id);
    router.replace(`/analyze?domain=${id}`);
  };

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.decide(active, values));
      setTimeout(() => document.getElementById("result")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader icon={<LuSlidersHorizontal />} title="Domain Analyzer" subtitle="Select a domain, enter the case parameters and run the full multi-agent pipeline. The same common engine loads a different dataset, model and knowledge base for each domain." />

      <div className="mb-6 grid gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {domains.map((d) => {
          const Icon = domainIcon(d.id);
          const on = d.id === active;
          return (
            <button key={d.id} onClick={() => select(d.id)} className={cx("card flex items-center gap-3 p-3.5 text-left transition", on ? "border-brand-500 ring-4 ring-brand-100" : "hover:border-brand-300")}>
              <span className={cx("grid h-10 w-10 shrink-0 place-items-center rounded-xl text-lg", on ? "bg-brand-600 text-white" : "bg-brand-50 text-brand-600")}><Icon /></span>
              <span className="min-w-0">
                <span className="block truncate text-sm font-bold text-ink">{d.name}</span>
                <span className="block truncate text-[11px] text-ink-muted">{d.tagline}</span>
              </span>
            </button>
          );
        })}
      </div>

      {error && <div className="mb-4"><ErrorBox message={error} /></div>}

      <div className="grid gap-6 xl:grid-cols-[400px_minmax(0,1fr)]">
        <div className="card h-fit p-5 xl:sticky xl:top-4">
          {!detail ? <Spinner /> : (
            <>
              <h2 className="text-base font-bold text-ink">{detail.title}</h2>
              <p className="mt-1 text-xs text-ink-muted">{detail.description}</p>
              <div className="mt-4">
                <div className="label">Scenario presets</div>
                <div className="flex flex-wrap gap-2">
                  {detail.presets.map((p) => (
                    <button key={p.id} onClick={() => setValues(p.inputs)} title={p.description} className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-ink-soft transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700">
                      {p.name}
                    </button>
                  ))}
                </div>
              </div>
              <div className="mt-5"><DomainForm features={detail.features} values={values} onChange={setValues} onSubmit={run} loading={loading} /></div>
            </>
          )}
        </div>

        <div id="result" className="min-w-0 scroll-mt-4">
          {loading && !result && <Spinner label="Agents are collaborating…" />}
          {result ? <DecisionView r={result} /> : !loading && (
            <EmptyState icon={<LuSparkles />} title="Ready to analyse" text="Choose a preset or enter values, then run the analysis. You'll see the neural prediction, rule evaluation, fusion, validation, explanation and the full agent trace." />
          )}
        </div>
      </div>
    </>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<Spinner />}>
      <Analyzer />
    </Suspense>
  );
}
