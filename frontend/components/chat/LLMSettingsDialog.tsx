"use client";

import { useState } from "react";
import { LuCircleCheck, LuCircleAlert, LuExternalLink, LuEye, LuEyeOff, LuLoader, LuPlugZap, LuX } from "react-icons/lu";
import { api, ApiError } from "@/lib/api";
import { LLM_PROVIDERS, llmHeaders, saveLLM, type LLMProvider, type LLMSettings } from "@/lib/llm";
import { cx } from "@/lib/ui";

interface Props {
  initial: LLMSettings;
  onClose: () => void;
  onSaved: (s: LLMSettings) => void;
}

export default function LLMSettingsDialog({ initial, onClose, onSaved }: Props) {
  const [s, setS] = useState<LLMSettings>(initial);
  const [show, setShow] = useState(false);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<{ ok: boolean; text: string } | null>(null);
  const provider = LLM_PROVIDERS.find((p) => p.id === s.provider);

  const pick = (id: LLMProvider) => {
    setResult(null);
    setS((prev) => ({ provider: id, apiKey: id === prev.provider ? prev.apiKey : "", model: "" }));
  };

  const test = async () => {
    setTesting(true);
    setResult(null);
    try {
      const r = await api.llmTest(llmHeaders(s));
      setResult({ ok: true, text: `Connected to ${r.label}` });
    } catch (e) {
      setResult({ ok: false, text: e instanceof ApiError ? e.message : "Connection failed" });
    } finally {
      setTesting(false);
    }
  };

  const save = () => {
    saveLLM(s);
    onSaved(s);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center p-4">
      <div className="absolute inset-0 bg-ink/30 backdrop-blur-[2px]" onClick={onClose} />
      <div className="relative w-full max-w-lg animate-fade-up rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-start gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-brand-50 text-lg text-brand-600"><LuPlugZap /></span>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-ink">LLM integration</h2>
            <p className="text-xs text-ink-muted">Optional. The agents always make the decision; the LLM helps understand free-text questions, writes natural explanations and follow-up questions, and answers general questions.</p>
          </div>
          <button onClick={onClose} className="btn-ghost !p-2"><LuX /></button>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {[{ id: "off" as const, label: "Offline" }, ...LLM_PROVIDERS].map((p) => (
            <button key={p.id} onClick={() => pick(p.id)}
              className={cx("rounded-xl border px-3 py-2.5 text-xs font-semibold transition", s.provider === p.id ? "border-brand-600 bg-brand-600 text-white" : "border-slate-200 text-ink-soft hover:border-brand-300")}>
              {p.label}
            </button>
          ))}
        </div>

        {provider ? (
          <div className="mt-5 space-y-4">
            <label className="block">
              <span className="label">API key</span>
              <div className="relative">
                <input type={show ? "text" : "password"} className="input pr-10 font-mono" placeholder={provider.keyHint} value={s.apiKey} autoComplete="off"
                  onChange={(e) => { setS({ ...s, apiKey: e.target.value }); setResult(null); }} />
                <button type="button" onClick={() => setShow((v) => !v)} className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-ink-muted hover:text-ink">{show ? <LuEyeOff /> : <LuEye />}</button>
              </div>
              <a href={provider.keyUrl} target="_blank" rel="noreferrer" className="mt-1 inline-flex items-center gap-1 text-[11px] font-semibold text-brand-700 hover:underline">Get a {provider.label} key <LuExternalLink /></a>
            </label>
            <label className="block">
              <span className="label">Model <span className="font-normal text-ink-muted">(optional)</span></span>
              <input className="input font-mono" placeholder={provider.defaultModel} value={s.model} onChange={(e) => setS({ ...s, model: e.target.value })} />
            </label>
            <div className="rounded-xl bg-amber-50 p-3 text-[11.5px] text-amber-900">
              The key is stored only in this browser. When enabled, the text of your questions and the agents&apos; evidence are sent to {provider.label}; avoid entering real personal data.
            </div>
            {result && (
              <div className={cx("flex items-start gap-2 rounded-xl p-3 text-xs", result.ok ? "bg-emerald-50 text-emerald-800" : "bg-rose-50 text-rose-800")}>
                {result.ok ? <LuCircleCheck className="mt-0.5 shrink-0" /> : <LuCircleAlert className="mt-0.5 shrink-0" />}
                <span className="break-words">{result.text}</span>
              </div>
            )}
          </div>
        ) : (
          <p className="mt-5 rounded-xl bg-slate-50 p-3 text-xs text-ink-soft">
            Offline mode: the built-in neural intent classifier and rule-based extractors understand your questions. Everything runs locally.
            (A key set on the server via <code className="rounded bg-white px-1">GEMINI_API_KEY</code>, <code className="rounded bg-white px-1">OPENAI_API_KEY</code> or <code className="rounded bg-white px-1">ANTHROPIC_API_KEY</code> is ignored while Offline is selected.)
          </p>
        )}

        <div className="mt-6 flex justify-end gap-2">
          {provider && <button onClick={test} disabled={!s.apiKey.trim() || testing} className="btn-secondary">{testing ? <LuLoader className="animate-spin" /> : <LuPlugZap />} Test connection</button>}
          <button onClick={save} disabled={!!provider && !s.apiKey.trim()} className="btn-primary">Save</button>
        </div>
      </div>
    </div>
  );
}
