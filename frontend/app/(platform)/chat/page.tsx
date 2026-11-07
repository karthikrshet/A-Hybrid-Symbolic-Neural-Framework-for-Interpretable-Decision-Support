"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  LuBrain,
  LuDownload,
  LuMessageSquare,
  LuMic,
  LuMicOff,
  LuPanelLeft,
  LuPlugZap,
  LuPencil,
  LuPin,
  LuPinOff,
  LuSearch,
  LuSend,
  LuSparkles,
  LuSquarePen,
  LuTrash2,
  LuX,
} from "react-icons/lu";
import DecisionView from "@/components/DecisionView";
import MessageBubble from "@/components/chat/MessageBubble";
import ThinkingIndicator from "@/components/chat/ThinkingIndicator";
import LLMSettingsDialog from "@/components/chat/LLMSettingsDialog";
import { loadLLM, type LLMSettings } from "@/lib/llm";
import { api, ApiError } from "@/lib/api";
import { cx, domainIcon, timeAgo } from "@/lib/ui";
import type { ChatMessage, ChatSession, ChatSuggestion, DomainSummary, Inputs } from "@/lib/types";

const ACTIVE_KEY = "ns_active_session";
const TRACE_KEY = "ns_show_trace";
const NUDGE_AFTER_MS = 60_000; // idle follow-up after one minute without a reply
const msgKey = (id: string) => `ns_msgs_${id}`;

// Minimal typing for the browser Speech Recognition API (voice input)
interface SpeechResultEvent { results: ArrayLike<ArrayLike<{ transcript: string }>> }
interface SpeechRecognitionLike {
  lang: string;
  interimResults: boolean;
  onresult: ((e: SpeechResultEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
}
type SpeechCtor = new () => SpeechRecognitionLike;

function getSpeech(): SpeechCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as { SpeechRecognition?: SpeechCtor; webkitSpeechRecognition?: SpeechCtor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

function saveLocal(id: string, msgs: ChatMessage[]) {
  try {
    localStorage.setItem(msgKey(id), JSON.stringify(msgs.filter((m) => !m.pending).slice(-60)));
  } catch {
    /* quota — ignore */
  }
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<ChatSuggestion[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  const [panelOpen, setPanelOpen] = useState(true);
  const [search, setSearch] = useState("");
  const [renaming, setRenaming] = useState<string | null>(null);
  const [renameText, setRenameText] = useState("");
  const [drawer, setDrawer] = useState<ChatMessage | null>(null);
  const [listening, setListening] = useState(false);
  const [offline, setOffline] = useState<string | null>(null);
  const [domains, setDomains] = useState<DomainSummary[]>([]);
  const [domainMode, setDomainMode] = useState<string>("auto");
  const [llm, setLlm] = useState<LLMSettings>({ provider: "off", model: "", apiKey: "" });
  const [llmLabel, setLlmLabel] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const nudgedRef = useRef<Set<string>>(new Set());
  const scrollRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const recRef = useRef<SpeechRecognitionLike | null>(null);

  const refreshSessions = useCallback(async () => {
    try {
      setSessions(await api.chatSessions());
      setOffline(null);
    } catch (e) {
      setOffline(e instanceof ApiError ? e.message : "Backend unavailable");
    }
  }, []);

  const openSession = useCallback(async (id: string) => {
    setActiveId(id);
    localStorage.setItem(ACTIVE_KEY, id);
    const cached = localStorage.getItem(msgKey(id));
    if (cached) setMessages(JSON.parse(cached) as ChatMessage[]);
    try {
      const s = await api.chatSession(id);
      setMessages(s.messages);
      saveLocal(id, s.messages);
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) {
        localStorage.removeItem(ACTIVE_KEY);
        localStorage.removeItem(msgKey(id));
        setActiveId(null);
        setMessages([]);
      }
    }
  }, []);

  useEffect(() => {
    setShowTrace(localStorage.getItem(TRACE_KEY) === "1");
    try { localStorage.removeItem("ns_chat_domain"); } catch { /* old persisted picker value */ }
    setLlm(loadLLM());
    api.llmStatus().then((st) => setLlmLabel(st.enabled ? st.label : null)).catch(() => undefined);
    api.domains().then(setDomains).catch(() => undefined);
    if (window.innerWidth < 1024) setPanelOpen(false);
    refreshSessions();
    api.chatSuggestions().then(setSuggestions).catch(() => undefined);
    const last = localStorage.getItem(ACTIVE_KEY);
    if (last) openSession(last);
  }, [refreshSessions, openSession]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`;
  }, [input]);

  const newChat = () => {
    setActiveId(null);
    setMessages([]);
    setDomainMode("auto");
    localStorage.removeItem(ACTIVE_KEY);
    taRef.current?.focus();
  };

  const send = async (text: string, structured?: { domain: string; inputs: Inputs }) => {
    if ((!text.trim() && !structured) || busy) return;
    const tempUser: ChatMessage = {
      id: `tmp-${Date.now()}`, session_id: activeId ?? "", role: "user",
      content: text.trim() || `Analyse this ${structured?.domain.replace("_", " ")} case using the form values.`,
      created_at: new Date().toISOString(), structured: structured ?? null, pending: true,
    };
    setMessages((prev) => [...prev, tempUser]);
    setInput("");
    setBusy(true);
    try {
      const res = await api.sendMessage({ message: text, session_id: activeId, structured, domain: domainMode === "auto" ? null : domainMode });
      setActiveId(res.session_id);
      localStorage.setItem(ACTIVE_KEY, res.session_id);
      if (res.message.picker_overridden) setDomainMode("auto");
      setMessages((prev) => {
        const next = [...prev.filter((m) => m.id !== tempUser.id), res.user_message, res.message];
        saveLocal(res.session_id, next);
        return next;
      });
      refreshSessions();
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Unexpected error";
      setMessages((prev) => [
        ...prev.map((m) => (m.id === tempUser.id ? { ...m, pending: false } : m)),
        { id: `err-${Date.now()}`, session_id: activeId ?? "", role: "assistant", content: msg, created_at: new Date().toISOString(), error: true },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const regenerate = () => {
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    if (lastUser) send(lastUser.structured ? "" : lastUser.content, lastUser.structured ?? undefined);
  };

  const remove = async (id: string) => {
    if (!confirm("Delete this conversation? This cannot be undone.")) return;
    await api.deleteSession(id).catch(() => undefined);
    localStorage.removeItem(msgKey(id));
    if (id === activeId) newChat();
    refreshSessions();
  };

  const commitRename = async (id: string) => {
    const title = renameText.trim();
    setRenaming(null);
    if (!title) return;
    await api.renameSession(id, title).catch(() => undefined);
    refreshSessions();
  };

  const togglePin = async (s: ChatSession) => {
    await api.pinSession(s.id, !s.pinned).catch(() => undefined);
    refreshSessions();
  };

  const exportChat = () => {
    const title = sessions.find((s) => s.id === activeId)?.title ?? "conversation";
    const md = messages.map((m) => `### ${m.role === "user" ? "You" : "NeuroSymbolic AI"}\n\n${m.content}\n`).join("\n");
    const blob = new Blob([`# ${title}\n\n${md}`], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${title.replace(/[^\w-]+/g, "_").slice(0, 40)}.md`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const toggleVoice = () => {
    const Ctor = getSpeech();
    if (!Ctor) {
      alert("Voice input is not supported in this browser. Try Chrome or Edge.");
      return;
    }
    if (listening) {
      recRef.current?.stop();
      return;
    }
    const rec = new Ctor();
    rec.lang = "en-IN";
    rec.interimResults = false;
    rec.onresult = (e) => setInput((v) => `${v}${v ? " " : ""}${e.results[0][0].transcript}`);
    rec.onend = () => setListening(false);
    recRef.current = rec;
    setListening(true);
    rec.start();
  };

  const filtered = useMemo(() => sessions.filter((s) => s.title.toLowerCase().includes(search.toLowerCase())), [sessions, search]);
  const groups = useMemo(() => {
    const today = new Date().toDateString();
    const g: Record<string, ChatSession[]> = { Pinned: [], Today: [], Earlier: [] };
    filtered.forEach((s) => {
      if (s.pinned) g.Pinned.push(s);
      else if (new Date(s.updated_at).toDateString() === today) g.Today.push(s);
      else g.Earlier.push(s);
    });
    return g;
  }, [filtered]);

  // Idle follow-up: if the user doesn't reply to a question or result, the assistant nudges once.
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (!activeId || busy || input.trim() || !last || last.role !== "assistant" || last.error) return;
    if (last.kind === "nudge" || !(last.kind === "clarify" || last.kind === "decision") || nudgedRef.current.has(last.id)) return;
    const t = setTimeout(async () => {
      nudgedRef.current.add(last.id);
      try {
        const res = await api.nudge(activeId);
        setMessages((prev) => {
          const next = [...prev, res.message];
          saveLocal(activeId, next);
          return next;
        });
      } catch {
        /* nothing to follow up on */
      }
    }, NUDGE_AFTER_MS);
    return () => clearTimeout(t);
  }, [messages, activeId, busy, input]);

  const pickDomain = (id: string) => {
    setDomainMode(id);
    taRef.current?.focus();
  };
  const selectedDomain = domains.find((d) => d.id === domainMode);
  const visibleSuggestions = selectedDomain ? suggestions.filter((s) => s.domain === selectedDomain.id) : suggestions;

  const activeTitle = sessions.find((s) => s.id === activeId)?.title ?? "New conversation";
  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant")?.id;

  return (
    <div className="flex h-full">
      {/* ---------------- conversations panel ---------------- */}
      <aside className={cx("flex shrink-0 flex-col border-r border-slate-200 bg-white transition-all duration-300", panelOpen ? "w-72" : "w-0 overflow-hidden border-r-0")}>
        <div className="space-y-3 p-3">
          <button onClick={newChat} className="btn-primary w-full"><LuSquarePen /> New chat</button>
          <div className="relative">
            <LuSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search conversations" className="input !pl-9" />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto px-2 pb-3">
          {sessions.length === 0 && <p className="px-3 py-6 text-center text-xs text-ink-muted">{offline ? "Backend offline — conversations will appear once it is running." : "No conversations yet. Ask your first question!"}</p>}
          {Object.entries(groups).map(([name, list]) =>
            list.length === 0 ? null : (
              <div key={name} className="mb-3">
                <div className="px-3 pb-1 pt-2 text-[10.5px] font-bold uppercase tracking-wider text-ink-muted">{name}</div>
                {list.map((s) => (
                  <div key={s.id} className={cx("group flex items-center gap-2 rounded-xl px-3 py-2 text-sm", s.id === activeId ? "bg-brand-50 text-brand-800" : "text-ink-soft hover:bg-slate-50")}>
                    <LuMessageSquare className="shrink-0 text-ink-muted" />
                    {renaming === s.id ? (
                      <input autoFocus value={renameText} onChange={(e) => setRenameText(e.target.value)} onBlur={() => commitRename(s.id)}
                        onKeyDown={(e) => { if (e.key === "Enter") commitRename(s.id); if (e.key === "Escape") setRenaming(null); }} className="input !px-2 !py-1 text-xs" />
                    ) : (
                      <button onClick={() => openSession(s.id)} className="min-w-0 flex-1 text-left">
                        <span className="block truncate font-medium">{s.title}</span>
                        <span className="text-[10.5px] text-ink-muted">{timeAgo(s.updated_at)} · {s.message_count} msgs</span>
                      </button>
                    )}
                    <div className="hidden shrink-0 items-center gap-0.5 group-hover:flex">
                      <button onClick={() => togglePin(s)} title={s.pinned ? "Unpin" : "Pin"} className="rounded p-1 hover:bg-white hover:text-brand-700">{s.pinned ? <LuPinOff /> : <LuPin />}</button>
                      <button onClick={() => { setRenaming(s.id); setRenameText(s.title); }} title="Rename" className="rounded p-1 hover:bg-white hover:text-brand-700"><LuPencil /></button>
                      <button onClick={() => remove(s.id)} title="Delete" className="rounded p-1 hover:bg-white hover:text-rose-600"><LuTrash2 /></button>
                    </div>
                  </div>
                ))}
              </div>
            ),
          )}
        </div>
      </aside>

      {/* ---------------- conversation ---------------- */}
      <section className="flex min-w-0 flex-1 flex-col bg-white">
        <header className="flex items-center gap-2 border-b border-slate-200 px-4 py-2.5">
          <button onClick={() => setPanelOpen((v) => !v)} className="btn-ghost !p-2 text-lg" title="Toggle conversations"><LuPanelLeft /></button>
          <h1 className="min-w-0 flex-1 truncate text-sm font-semibold text-ink">{activeTitle}</h1>
          <button onClick={() => setSettingsOpen(true)} title="LLM integration settings"
            className={cx("flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium transition", llmLabel ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-slate-200 text-ink-soft hover:border-brand-300")}>
            <LuPlugZap className={llmLabel ? "text-emerald-600" : "text-brand-600"} />
            <span className="hidden max-w-[180px] truncate sm:inline">{llmLabel ? `LLM: ${llmLabel}` : "Connect LLM"}</span>
          </button>
          <label className="flex cursor-pointer select-none items-center gap-2 rounded-xl border border-slate-200 px-3 py-1.5 text-xs font-medium text-ink-soft" title="Show the multi-agent collaboration trace inside answers">
            <LuBrain className="text-brand-600" /> Agent reasoning
            <input type="checkbox" className="peer sr-only" checked={showTrace}
              onChange={(e) => { setShowTrace(e.target.checked); localStorage.setItem(TRACE_KEY, e.target.checked ? "1" : "0"); }} />
            <span className="relative h-4 w-7 rounded-full bg-slate-200 transition after:absolute after:left-0.5 after:top-0.5 after:h-3 after:w-3 after:rounded-full after:bg-white after:transition peer-checked:bg-brand-600 peer-checked:after:translate-x-3" />
          </label>
          {messages.length > 0 && <button onClick={exportChat} className="btn-ghost !p-2" title="Export conversation (Markdown)"><LuDownload /></button>}
        </header>

        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-3xl space-y-6 px-4 py-6">
            {offline && messages.length === 0 && (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">{offline}</div>
            )}
            {messages.length === 0 && (
              <div className="pt-6 text-center sm:pt-12">
                <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-800 text-3xl text-white shadow-lift"><LuBrain /></div>
                <h2 className="mt-5 text-3xl font-extrabold tracking-tight text-ink">How can the agent team help?</h2>
                <p className="mx-auto mt-2 max-w-xl text-sm text-ink-muted">
                  Ask in plain language. The Coordinator routes your question to neural, reasoning, validation and explanation agents,
                  and returns an answer with its <b className="text-ink-soft">reasoning, evidence and confidence</b>.
                </p>
                <div className="mt-8 grid gap-3 text-left sm:grid-cols-2">
                  {visibleSuggestions.map((s) => {
                    const Icon = domainIcon(s.domain);
                    return (
                      <button key={s.domain} onClick={() => send(s.prompt)} className="card group flex gap-3 p-4 text-left transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-lift">
                        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand-50 text-lg text-brand-600 group-hover:bg-brand-600 group-hover:text-white"><Icon /></span>
                        <span>
                          <span className="block text-xs font-bold text-brand-700">{s.domain_name}</span>
                          <span className="mt-0.5 block text-sm text-ink-soft">{s.prompt}</span>
                        </span>
                      </button>
                    );
                  })}
                  <button onClick={() => send("How does this system work?")} className="card flex gap-3 p-4 text-left transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-lift">
                    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand-50 text-lg text-brand-600"><LuBrain /></span>
                    <span><span className="block text-xs font-bold text-brand-700">About the framework</span><span className="mt-0.5 block text-sm text-ink-soft">How do the agents work together to reach a decision?</span></span>
                  </button>
                </div>
              </div>
            )}
            {messages.map((m) => (
              <MessageBubble
                key={m.id}
                m={m}
                showTrace={showTrace}
                busy={busy}
                isLast={m.id === lastAssistant}
                onSuggestion={(s) => send(s)}
                onStructured={(d, v) => send("", { domain: d, inputs: v })}
                onOpenDecision={setDrawer}
                onRegenerate={regenerate}
              />
            ))}
            {busy && <ThinkingIndicator />}
          </div>
        </div>

        <div className="border-t border-slate-100 bg-white px-4 pb-4 pt-3">
          <form onSubmit={(e) => { e.preventDefault(); send(input); }} className="mx-auto max-w-3xl">
            <div className="mb-2 flex items-center gap-1.5 overflow-x-auto pb-0.5" role="radiogroup" aria-label="Domain">
              <span className="shrink-0 pr-1 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">Domain</span>
              {[{ id: "auto", name: "Auto-detect" }, ...domains].map((d) => {
                const on = domainMode === d.id;
                const Icon = d.id === "auto" ? LuSparkles : domainIcon(d.id);
                return (
                  <button key={d.id} type="button" role="radio" aria-checked={on} onClick={() => pickDomain(d.id)}
                    title={d.id === "auto" ? "The Coordinator detects the domain from your message" : `Send every message to the ${d.name} agents`}
                    className={cx("inline-flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition",
                      on ? "border-brand-600 bg-brand-600 text-white shadow-sm" : "border-slate-200 bg-white text-ink-soft hover:border-brand-300 hover:text-brand-700")}>
                    <Icon /> {d.name}
                  </button>
                );
              })}
            </div>
            <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-card transition focus-within:border-brand-400 focus-within:ring-4 focus-within:ring-brand-100">
              <textarea
                ref={taRef}
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
                placeholder={selectedDomain ? `Ask the ${selectedDomain.name} agents — ${selectedDomain.tagline.toLowerCase()}… (Shift+Enter for a new line)` : "Describe a patient, loan, transaction, server or student… (Shift+Enter for a new line)"}
                className="max-h-44 min-h-[40px] flex-1 resize-none border-0 bg-transparent px-2 py-2 text-[15px] text-ink placeholder-slate-400 focus:outline-none"
              />
              <button type="button" onClick={toggleVoice} title="Voice input" className={cx("grid h-10 w-10 place-items-center rounded-xl transition", listening ? "bg-rose-50 text-rose-600" : "text-ink-muted hover:bg-slate-100")}>
                {listening ? <LuMicOff /> : <LuMic />}
              </button>
              <button type="submit" disabled={busy || !input.trim()} className="grid h-10 w-10 place-items-center rounded-xl bg-brand-600 text-white transition hover:bg-brand-700 disabled:bg-slate-200 disabled:text-slate-400" title="Send">
                <LuSend />
              </button>
            </div>
            <p className="mt-2 text-center text-[11px] text-ink-muted">Decision-support output — answers are explained with rules and evidence, but always verify important decisions with an expert.</p>
          </form>
        </div>
      </section>

      {settingsOpen && (
        <LLMSettingsDialog initial={llm} onClose={() => setSettingsOpen(false)}
          onSaved={(st) => { setLlm(st); api.llmStatus().then((r) => setLlmLabel(r.enabled ? r.label : null)).catch(() => setLlmLabel(null)); }} />
      )}

      {/* ---------------- full analysis drawer ---------------- */}
      {drawer?.decision && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-ink/30 backdrop-blur-[2px]" onClick={() => setDrawer(null)} />
          <div className="relative h-full w-full max-w-5xl animate-fade-up overflow-y-auto bg-slate-50 p-5 shadow-2xl sm:p-7">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-extrabold text-ink">Full multi-agent analysis</h2>
              <button onClick={() => setDrawer(null)} className="btn-secondary !p-2"><LuX /></button>
            </div>
            <DecisionView r={drawer.decision} />
          </div>
        </div>
      )}
    </div>
  );
}
