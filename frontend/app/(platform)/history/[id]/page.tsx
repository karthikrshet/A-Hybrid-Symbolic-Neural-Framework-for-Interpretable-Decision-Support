"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { LuArrowLeft, LuStar } from "react-icons/lu";
import DecisionView from "@/components/DecisionView";
import { ErrorBox, Spinner } from "@/components/primitives";
import { api, ApiError } from "@/lib/api";
import { cx, fmtValue } from "@/lib/ui";
import type { DecisionResult } from "@/lib/types";

export default function DecisionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [r, setR] = useState<DecisionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rating, setRating] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.decision(id).then((d) => { setR(d); setRating(d.feedback_rating); setComment(d.feedback_comment ?? ""); }).catch((e: ApiError) => setError(e.message));
  }, [id]);

  const save = async () => {
    if (!rating) return;
    await api.feedback(id, rating, comment || undefined);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (error) return <ErrorBox message={error} />;
  if (!r) return <Spinner />;

  return (
    <div className="space-y-5">
      <Link href="/history" className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-700 hover:underline"><LuArrowLeft /> Back to history</Link>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <DecisionView r={r} />
        <div className="space-y-4">
          <div className="card p-5">
            <h3 className="mb-3 text-sm font-bold text-ink">Case inputs</h3>
            <dl className="space-y-1.5 text-xs">
              {Object.entries(r.inputs).map(([k, v]) => (
                <div key={k} className="flex justify-between gap-3"><dt className="text-ink-muted">{k.replace(/_/g, " ")}</dt><dd className="font-mono font-semibold text-ink">{fmtValue(v)}</dd></div>
              ))}
              {Object.entries(r.derived).map(([k, v]) => (
                <div key={k} className="flex justify-between gap-3 border-t border-dashed border-slate-200 pt-1.5"><dt className="text-brand-700">{k.replace(/_/g, " ")} (derived)</dt><dd className="font-mono font-semibold text-brand-800">{fmtValue(v)}</dd></div>
              ))}
            </dl>
          </div>
          <div className="card p-5">
            <h3 className="text-sm font-bold text-ink">Rate this explanation</h3>
            <p className="mt-1 text-xs text-ink-muted">Your rating feeds the interpretability evaluation (clarity & usefulness).</p>
            <div className="mt-3 flex gap-1">
              {[1, 2, 3, 4, 5].map((n) => (
                <button key={n} onClick={() => setRating(n)} className={cx("text-2xl transition", rating && n <= rating ? "text-amber-400" : "text-slate-300 hover:text-amber-300")}><LuStar fill="currentColor" /></button>
              ))}
            </div>
            <textarea className="input mt-3" rows={3} placeholder="Optional comment" value={comment} onChange={(e) => setComment(e.target.value)} />
            <button onClick={save} disabled={!rating} className="btn-primary mt-3 w-full">{saved ? "Saved ✓" : "Submit rating"}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
