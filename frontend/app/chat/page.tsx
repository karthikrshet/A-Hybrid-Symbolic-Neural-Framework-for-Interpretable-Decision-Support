'use client';
import React, { useState, useEffect, useRef } from 'react';
import {
  FiEdit3,
  FiImage,
  FiClock,
  FiBook,
  FiCpu,
  FiCode,
  FiCompass,
  FiPlus,
  FiMic,
  FiSend,
  FiSettings,
  FiUser,
  FiChevronDown,
  FiChevronUp,
  FiShield,
  FiActivity,
  FiBarChart2,
  FiX,
  FiAlertTriangle,
  FiCheckCircle,
  FiInfo,
  FiKey
} from 'react-icons/fi';

interface AgentTrace {
  agent_id: string;
  agent_type: string;
  step: string;
  status: string;
  execution_time_ms: number;
  timestamp: string;
  details: Record<string, any>;
}

interface MessageItem {
  id: string;
  sender: 'USER' | 'ASSISTANT';
  text: string;
  decision?: any;
  traces?: AgentTrace[];
  timestamp: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [thinkMode, setThinkMode] = useState(true);
  const [selectedModel, setSelectedModel] = useState('neurosymbolic-multiagent');
  const [apiKey, setApiKey] = useState('');
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [expandedTraceId, setExpandedTraceId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || loading) return;

    const userMsg: MessageItem = {
      id: String(Date.now()),
      sender: 'USER',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setShowAttachMenu(false);
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          model: selectedModel,
          api_key: apiKey || undefined
        })
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMsg: MessageItem = {
          id: String(Date.now() + 1),
          sender: 'ASSISTANT',
          text: data.reply,
          decision: data.decision,
          traces: data.agent_traces || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, assistantMsg]);
      } else {
        throw new Error('Backend HTTP error');
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'ASSISTANT',
          text: 'Unable to connect to the Multi-Agent Coordinator backend at http://127.0.0.1:8000. Please ensure the backend server is active.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setInput('');
  };

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'COORDINATOR':
        return <FiCpu className="w-4 h-4 text-blue-600" />;
      case 'NEURAL':
        return <FiActivity className="w-4 h-4 text-purple-600" />;
      case 'SYMBOLIC':
        return <FiShield className="w-4 h-4 text-indigo-600" />;
      case 'VALIDATION':
        return <FiCheckCircle className="w-4 h-4 text-emerald-600" />;
      case 'EXPLANATION':
        return <FiBarChart2 className="w-4 h-4 text-amber-600" />;
      default:
        return <FiInfo className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-white text-slate-800 font-sans">
      {/* =========================================================================
          LEFT SIDEBAR (EXACT MATCH TO USER SCREENSHOT - NO EMOJIS, REACT ICONS)
      ========================================================================= */}
      <aside className="w-64 bg-[#f9f9f9] border-r border-gray-200/70 flex flex-col justify-between shrink-0 select-none">
        <div className="p-3 space-y-4">
          {/* New Chat Top Button */}
          <button
            onClick={startNewChat}
            className="w-full flex items-center justify-between px-3 py-2 bg-white hover:bg-gray-100/80 border border-gray-200/80 rounded-xl text-sm font-medium text-slate-800 transition shadow-sm group"
          >
            <div className="flex items-center space-x-2.5">
              <FiEdit3 className="w-4 h-4 text-slate-600 group-hover:text-slate-900" />
              <span>New chat</span>
            </div>
            <span className="text-[11px] text-gray-400 font-mono">Ctrl+K</span>
          </button>

          {/* Navigation Items (Exact from Screenshot) */}
          <nav className="space-y-0.5 text-[13px] font-medium text-slate-700">
            <button
              onClick={() => setActiveModal('images')}
              className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-200/60 transition text-left"
            >
              <FiImage className="w-4 h-4 text-slate-500" />
              <span>Images</span>
            </button>

            <button
              onClick={() => setActiveModal('scheduled')}
              className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-200/60 transition text-left"
            >
              <FiClock className="w-4 h-4 text-slate-500" />
              <span>Scheduled</span>
            </button>

            <button
              onClick={() => setActiveModal('library')}
              className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-200/60 transition text-left"
            >
              <FiBook className="w-4 h-4 text-slate-500" />
              <span>Library</span>
            </button>

            <button
              onClick={() => setActiveModal('plugins')}
              className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-200/60 transition text-left"
            >
              <FiCpu className="w-4 h-4 text-slate-500" />
              <span>Plugins</span>
            </button>

            <button
              onClick={() => setActiveModal('codex')}
              className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-200/60 transition text-left"
            >
              <FiCode className="w-4 h-4 text-slate-500" />
              <span>Codex</span>
            </button>

            <button
              onClick={() => setActiveModal('explore')}
              className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-200/60 transition text-left"
            >
              <FiCompass className="w-4 h-4 text-slate-500" />
              <span>... Explore</span>
            </button>
          </nav>

          {/* Pinned Section (Exact Match to Screenshot) */}
          <div className="pt-3">
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">
              Pinned
            </div>
            <div className="space-y-0.5 text-xs text-slate-700">
              <button
                onClick={() => handleSend('Tell me innovative product ideas for CodeMyFYP based on AI and Multi-Agent Systems')}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-200/60 transition truncate block font-medium"
                title="Product Ideas for CodeMyFYP"
              >
                Product Ideas for CodeMyFYP
              </button>
              <button
                onClick={() => handleSend('Evaluate a $25,000 international transfer to a sanctioned country without KYC')}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-200/60 transition truncate block text-slate-600"
                title="Financial Risk Audit #1042"
              >
                Financial Risk Audit #1042
              </button>
              <button
                onClick={() => handleSend('How does the Neural Model collaborate with the Symbolic Rule Engine?')}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-200/60 transition truncate block text-slate-600"
                title="Neuro-Symbolic Framework"
              >
                Neuro-Symbolic Framework
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Profile (Clean User Profile - No personal names) */}
        <div className="p-3 border-t border-gray-200/70">
          <div className="flex items-center space-x-3 px-2 py-1.5 rounded-xl hover:bg-gray-200/60 transition cursor-pointer">
            <div className="w-8 h-8 rounded-full bg-slate-800 text-white font-bold flex items-center justify-center text-xs shadow-inner">
              <FiUser className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-slate-800 truncate">Account</div>
              <div className="text-[10px] text-gray-400 truncate">Enterprise Platform</div>
            </div>
            <button
              onClick={() => setActiveModal('settings')}
              title="API & System Settings"
              className="text-gray-400 hover:text-slate-700 p-1"
            >
              <FiSettings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* =========================================================================
          MAIN CHAT WORKSPACE CANVAS
      ========================================================================= */}
      <main className="flex-1 flex flex-col h-screen relative bg-white overflow-hidden">
        {/* Top Minimal Bar */}
        <header className="h-12 border-b border-gray-100 flex items-center justify-between px-6 shrink-0 z-10">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-sm text-slate-800">NeuroSymbolic AI</span>
            <span className="text-xs text-gray-400">&bull;</span>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-transparent text-xs text-slate-600 font-medium outline-none cursor-pointer border border-transparent hover:border-gray-200 rounded px-1.5 py-0.5"
            >
              <option value="neurosymbolic-multiagent">Multi-Agent Team (Default)</option>
              <option value="gpt-4o-mini">GPT-4o Mini (OpenAI)</option>
              <option value="gemini-1.5-flash">Gemini 1.5 Flash (Google)</option>
            </select>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <button
              onClick={() => setActiveModal('settings')}
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition flex items-center space-x-1.5"
            >
              <FiKey className="w-3.5 h-3.5 text-slate-500" />
              <span>Configure API Keys</span>
            </button>
            <a
              href="/decision"
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition flex items-center space-x-1"
            >
              <span>Decision Studio</span>
            </a>
            <a
              href="/evaluations"
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition flex items-center space-x-1"
            >
              <span>Benchmarks</span>
            </a>
          </div>
        </header>

        {/* Message Stream or Empty Greeting Canvas */}
        <div className="flex-1 overflow-y-auto px-4 md:px-0 py-6 space-y-6">
          {messages.length === 0 ? (
            /* ===================================================================
               EMPTY STATE CANVAS (EXACT MATCH TO SCREENSHOT - CLEAN & SPACIOUS)
            =================================================================== */
            <div className="h-full flex flex-col items-center justify-center text-center px-4 -mt-20">
              <h1 className="text-3xl md:text-4xl font-normal text-slate-800 tracking-tight">
                What can I help with today?
              </h1>
            </div>
          ) : (
            /* Active Chat Stream */
            <div className="max-w-3xl mx-auto w-full space-y-6 pb-36">
              {messages.map((m) => (
                <div key={m.id} className="space-y-3">
                  {/* Message Bubble */}
                  <div className={`flex ${m.sender === 'USER' ? 'justify-end' : 'justify-start'}`}>
                    {m.sender === 'ASSISTANT' && (
                      <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold mr-3 shrink-0 mt-0.5 shadow-sm">
                        NS
                      </div>
                    )}

                    <div
                      className={`max-w-2xl text-[14px] leading-relaxed ${
                        m.sender === 'USER'
                          ? 'bg-[#f4f4f4] text-slate-900 rounded-3xl px-5 py-3'
                          : 'text-slate-800 w-full'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{m.text}</div>

                      {/* If Decision Attached: Show Verdict Card */}
                      {m.decision && (
                        <div className="mt-4 p-4 rounded-xl border border-gray-200 bg-slate-50/60 shadow-sm space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                              Collaborative Decision
                            </span>
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-bold ${
                                m.decision.final_decision === 'REJECT'
                                  ? 'bg-rose-100 text-rose-800 border border-rose-200'
                                  : m.decision.final_decision === 'REQUIRES_HUMAN_REVIEW'
                                  ? 'bg-amber-100 text-amber-800 border border-amber-200'
                                  : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              }`}
                            >
                              {m.decision.final_decision} ({(m.decision.confidence_score * 100).toFixed(1)}% Confidence)
                            </span>
                          </div>

                          {m.decision.neural_analysis && (
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs pt-1 border-t border-gray-200/60">
                              <div>
                                <span className="text-gray-400 block text-[10px]">Neural Risk</span>
                                <span className="font-semibold text-slate-800">
                                  {(m.decision.neural_analysis.risk_probability * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-400 block text-[10px]">Symbolic Override</span>
                                <span className="font-semibold text-slate-800">
                                  {m.decision.symbolic_analysis?.has_hard_override ? 'YES (Hard Policy)' : 'NO'}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-400 block text-[10px]">Validation Status</span>
                                <span className="font-semibold text-emerald-700">
                                  {m.decision.validation_status || 'VERIFIED'}
                                </span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Specialized Agent Collaboration Card (Expandable Thoughts) */}
                      {m.traces && m.traces.length > 0 && (
                        <div className="mt-3 pt-2">
                          <button
                            onClick={() => setExpandedTraceId(expandedTraceId === m.id ? null : m.id)}
                            className="flex items-center space-x-1.5 text-xs font-medium text-slate-500 hover:text-slate-800 py-1 transition"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse"></span>
                            <span>
                              {expandedTraceId === m.id
                                ? 'Hide Agent Collaboration Process'
                                : `View Agent Collaboration Process (${m.traces.length} Specialized Agents)`}
                            </span>
                            {expandedTraceId === m.id ? (
                              <FiChevronUp className="w-3 h-3 text-gray-400" />
                            ) : (
                              <FiChevronDown className="w-3 h-3 text-gray-400" />
                            )}
                          </button>

                          {expandedTraceId === m.id && (
                            <div className="mt-2.5 p-3.5 bg-gray-50 border border-gray-200/80 rounded-xl space-y-2 text-xs">
                              {m.traces.map((trace, idx) => (
                                <div key={idx} className="flex items-start space-x-2.5 py-1.5 border-b border-gray-200/40 last:border-0">
                                  <div className="mt-0.5">{getAgentIcon(trace.agent_type)}</div>
                                  <div className="flex-1">
                                    <div className="flex items-center justify-between">
                                      <span className="font-semibold text-slate-800">
                                        {trace.details?.role || trace.agent_id}
                                      </span>
                                      <span className="text-[10px] font-mono text-gray-400">
                                        {trace.execution_time_ms.toFixed(1)} ms
                                      </span>
                                    </div>
                                    <p className="text-slate-600 text-[11px] mt-0.5">
                                      {trace.details?.action ||
                                        (trace.details?.triggered_rules
                                          ? `Triggered ${trace.details.triggered_rules.length} rules`
                                          : `Evaluated step ${trace.step}`)}
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                    NS
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-slate-500 py-2">
                    <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce"></div>
                    <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.2s]"></div>
                    <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.4s]"></div>
                    <span className="font-medium text-slate-600 pl-1">
                      Coordinating specialized agents and executing model inference...
                    </span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* =========================================================================
            BOTTOM FLOATING INPUT PILL BAR (EXACT MATCH TO USER SCREENSHOT)
        ========================================================================= */}
        <div className="absolute bottom-6 left-0 right-0 flex justify-center px-4 pointer-events-none z-20">
          <div className="w-full max-w-3xl pointer-events-auto relative">
            {/* Attachment Menu Popup */}
            {showAttachMenu && (
              <div className="absolute bottom-16 left-2 w-72 bg-white rounded-2xl border border-gray-200 shadow-xl p-2 space-y-1 text-xs text-slate-700 z-30">
                <div className="px-3 py-1.5 font-semibold text-gray-400 uppercase text-[10px] tracking-wider">
                  Select Context
                </div>
                <button
                  onClick={() => {
                    setInput('Evaluate a $25,000 transfer to a sanctioned country without KYC');
                    setShowAttachMenu(false);
                  }}
                  className="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100 transition flex items-center space-x-2"
                >
                  <FiAlertTriangle className="w-4 h-4 text-rose-500" />
                  <span>Sanctioned Jurisdiction Scenario</span>
                </button>
                <button
                  onClick={() => {
                    setInput('Assess rapid withdrawal burst of $4,500 at 3am with 4 failed attempts');
                    setShowAttachMenu(false);
                  }}
                  className="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100 transition flex items-center space-x-2"
                >
                  <FiActivity className="w-4 h-4 text-amber-500" />
                  <span>High Velocity Burst Scenario</span>
                </button>
                <button
                  onClick={() => {
                    setInput('Check $180 legitimate domestic verified groceries transaction');
                    setShowAttachMenu(false);
                  }}
                  className="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100 transition flex items-center space-x-2"
                >
                  <FiCheckCircle className="w-4 h-4 text-emerald-500" />
                  <span>Standard Domestic Payment</span>
                </button>
              </div>
            )}

            {/* Pill Container (Exact Match from Screenshot) */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="bg-white border border-gray-200/90 rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.08)] py-2.5 px-4 flex items-center space-x-3 transition-all focus-within:border-gray-300 focus-within:shadow-[0_8px_32px_rgb(0,0,0,0.12)]"
            >
              {/* Plus Button (+) */}
              <button
                type="button"
                onClick={() => setShowAttachMenu(!showAttachMenu)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-gray-500 hover:bg-gray-100 hover:text-slate-800 transition cursor-pointer shrink-0"
                title="Add attachment / scenario"
              >
                <FiPlus className="w-5 h-5" />
              </button>

              {/* Text Input */}
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask ChatGPT"
                className="flex-1 bg-transparent border-0 outline-none text-[15px] text-slate-800 placeholder:text-gray-400 py-1"
              />

              {/* Think Toggle Button */}
              <button
                type="button"
                onClick={() => setThinkMode(!thinkMode)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition cursor-pointer shrink-0 ${
                  thinkMode
                    ? 'border-blue-200 bg-blue-50/70 text-blue-700'
                    : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
                title="Toggle Deep Multi-Agent Thinking"
              >
                <FiCpu className="w-3.5 h-3.5" />
                <span>Think</span>
              </button>

              {/* Microphone Button */}
              <button
                type="button"
                onClick={() => handleSend('Assess $15,000 transfer with incomplete KYC documentation')}
                className="w-8 h-8 rounded-full flex items-center justify-center text-gray-500 hover:text-slate-800 hover:bg-gray-100 transition cursor-pointer shrink-0"
                title="Voice input simulation"
              >
                <FiMic className="w-4 h-4" />
              </button>

              {/* Blue Circular Waveform / Send Button (Exact Match to Screenshot) */}
              <button
                type="submit"
                disabled={loading}
                className="w-9 h-9 rounded-full bg-blue-600 hover:bg-blue-700 active:scale-95 flex items-center justify-center text-white shadow-sm transition cursor-pointer shrink-0 disabled:opacity-50"
                title={input.trim() ? 'Send message' : 'Voice interaction'}
              >
                {input.trim() ? (
                  <FiSend className="w-4 h-4" />
                ) : (
                  /* Audio Waveform Bars (ılı) from Screenshot */
                  <div className="flex items-center space-x-0.5 h-3.5">
                    <div className="w-0.5 h-2 bg-white rounded-full"></div>
                    <div className="w-0.5 h-3.5 bg-white rounded-full"></div>
                    <div className="w-0.5 h-2 bg-white rounded-full"></div>
                  </div>
                )}
              </button>
            </form>
          </div>
        </div>
      </main>

      {/* =========================================================================
          MODALS FOR SIDEBAR ITEMS (No emojis, clean React Icons)
      ========================================================================= */}
      {activeModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-lg font-bold text-slate-900 capitalize">
                {activeModal === 'images' && 'System Architecture & Visualizations'}
                {activeModal === 'scheduled' && 'Scheduled Risk & AML Batch Jobs'}
                {activeModal === 'library' && 'Knowledge Base & Decision Rules'}
                {activeModal === 'plugins' && 'The 5 Specialized AI Agents'}
                {activeModal === 'codex' && 'Codex ML & Rule Engine Execution'}
                {activeModal === 'explore' && 'Project Navigation & Capabilities'}
                {activeModal === 'settings' && 'Configure API Keys & LLM Engine'}
              </h3>
              <button
                onClick={() => setActiveModal(null)}
                className="text-gray-400 hover:text-slate-700 p-1 rounded-lg"
              >
                <FiX className="w-5 h-5" />
              </button>
            </div>

            {/* Settings / API Key Modal */}
            {activeModal === 'settings' && (
              <div className="space-y-4 text-xs text-slate-600">
                <p>Configure external LLM providers or use the default local multi-agent pipeline:</p>
                <div className="space-y-3">
                  <div>
                    <label className="block font-semibold text-slate-800 mb-1">Active LLM Model</label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg text-sm bg-white"
                    >
                      <option value="neurosymbolic-multiagent">NeuroSymbolic Multi-Agent Team (Default)</option>
                      <option value="gpt-4o-mini">OpenAI GPT-4o-mini</option>
                      <option value="gemini-1.5-flash">Google Gemini 1.5 Flash</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-semibold text-slate-800 mb-1">API Key (OpenAI or Gemini)</label>
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="sk-... or AIza..."
                      className="w-full px-3 py-2 border rounded-lg text-sm font-mono"
                    />
                    <span className="text-[11px] text-gray-400 mt-1 block">
                      Optional: If left blank, the system automatically uses the internal neuro-symbolic multi-agent model.
                    </span>
                  </div>
                </div>
              </div>
            )}

            {activeModal === 'images' && (
              <div className="space-y-4 text-xs text-slate-600">
                <p>Visual architecture and explainability components:</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-4 rounded-xl border border-gray-200 bg-slate-50 text-center">
                    <FiBarChart2 className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                    <div className="font-semibold text-slate-800">TreeSHAP Waterfall Plots</div>
                    <p className="text-[11px] text-gray-500 mt-1">Mathematical feature attributions</p>
                  </div>
                  <div className="p-4 rounded-xl border border-gray-200 bg-slate-50 text-center">
                    <FiActivity className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                    <div className="font-semibold text-slate-800">Calibration Curves</div>
                    <p className="text-[11px] text-gray-500 mt-1">Platt Sigmoid probability bounds</p>
                  </div>
                  <div className="p-4 rounded-xl border border-gray-200 bg-slate-50 text-center">
                    <FiCpu className="w-6 h-6 text-indigo-600 mx-auto mb-2" />
                    <div className="font-semibold text-slate-800">Coordinator FSM Workflow</div>
                    <p className="text-[11px] text-gray-500 mt-1">7 explicit state transitions</p>
                  </div>
                  <div className="p-4 rounded-xl border border-gray-200 bg-slate-50 text-center">
                    <FiShield className="w-6 h-6 text-emerald-600 mx-auto mb-2" />
                    <div className="font-semibold text-slate-800">Decision Fusion Matrix</div>
                    <p className="text-[11px] text-gray-500 mt-1">Symbolic override hierarchy</p>
                  </div>
                </div>
              </div>
            )}

            {activeModal === 'scheduled' && (
              <div className="space-y-3 text-xs text-slate-600">
                <p>Automated monitoring and velocity compliance schedules:</p>
                <div className="p-3 bg-slate-50 border rounded-xl space-y-2">
                  <div className="flex justify-between font-semibold text-slate-800">
                    <span>Cron: */5 * * * *</span>
                    <span className="text-emerald-600">Active</span>
                  </div>
                  <p>Real-time transaction frequency & velocity burst detection.</p>
                </div>
                <div className="p-3 bg-slate-50 border rounded-xl space-y-2">
                  <div className="flex justify-between font-semibold text-slate-800">
                    <span>Cron: 0 0 * * *</span>
                    <span className="text-emerald-600">Active</span>
                  </div>
                  <p>Daily compliance batch report generation & sanctions sync.</p>
                </div>
              </div>
            )}

            {activeModal === 'library' && (
              <div className="space-y-3 text-xs text-slate-600">
                <p>Knowledge Base and verified compliance rule specifications:</p>
                <div className="space-y-2">
                  <div className="p-2.5 bg-slate-50 border rounded-lg">
                    <div className="font-bold text-slate-800">RULE-001: Sanctioned Jurisdiction Destination</div>
                    <div className="text-gray-500 text-[11px]">Action: Hard Override REJECT (Priority: 100)</div>
                  </div>
                  <div className="p-2.5 bg-slate-50 border rounded-lg">
                    <div className="font-bold text-slate-800">RULE-002: Excessive Velocity Ratio Spike</div>
                    <div className="text-gray-500 text-[11px]">Action: Flag Review / High Risk (Priority: 80)</div>
                  </div>
                  <div className="p-2.5 bg-slate-50 border rounded-lg">
                    <div className="font-bold text-slate-800">RULE-003: Large Off-Hours Transfer Lacking KYC</div>
                    <div className="text-gray-500 text-[11px]">Action: Escalation to Officer (Priority: 75)</div>
                  </div>
                </div>
                <div className="pt-2">
                  <a href="/rules" className="text-blue-600 font-semibold hover:underline">
                    View all 8 Rules in Rule Engine &rarr;
                  </a>
                </div>
              </div>
            )}

            {activeModal === 'plugins' && (
              <div className="space-y-3 text-xs text-slate-600">
                <p>The 5 Specialized AI Agents in this platform:</p>
                <div className="space-y-2">
                  <div className="p-2.5 bg-slate-50 border rounded-lg flex items-center space-x-2.5">
                    <FiCpu className="w-5 h-5 text-blue-600" />
                    <div>
                      <div className="font-bold text-slate-800">Coordinator Agent</div>
                      <p className="text-gray-500 text-[11px]">Manages communication between all agents and combines results.</p>
                    </div>
                  </div>
                  <div className="p-2.5 bg-slate-50 border rounded-lg flex items-center space-x-2.5">
                    <FiActivity className="w-5 h-5 text-purple-600" />
                    <div>
                      <div className="font-bold text-slate-800">Neural AI Agent</div>
                      <p className="text-gray-500 text-[11px]">Identifies patterns using statistical machine learning models.</p>
                    </div>
                  </div>
                  <div className="p-2.5 bg-slate-50 border rounded-lg flex items-center space-x-2.5">
                    <FiShield className="w-5 h-5 text-indigo-600" />
                    <div>
                      <div className="font-bold text-slate-800">Reasoning Agent</div>
                      <p className="text-gray-500 text-[11px]">Applies logical rules and domain-specific knowledge.</p>
                    </div>
                  </div>
                  <div className="p-2.5 bg-slate-50 border rounded-lg flex items-center space-x-2.5">
                    <FiCheckCircle className="w-5 h-5 text-emerald-600" />
                    <div>
                      <div className="font-bold text-slate-800">Validation Agent</div>
                      <p className="text-gray-500 text-[11px]">Checks whether generated results are correct and consistent.</p>
                    </div>
                  </div>
                  <div className="p-2.5 bg-slate-50 border rounded-lg flex items-center space-x-2.5">
                    <FiBarChart2 className="w-5 h-5 text-amber-600" />
                    <div>
                      <div className="font-bold text-slate-800">Explanation Agent</div>
                      <p className="text-gray-500 text-[11px]">Explains how the system reached its conclusion via TreeSHAP.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeModal === 'codex' && (
              <div className="space-y-3 text-xs text-slate-600 font-mono">
                <p className="font-sans">Active ML Model Artifact & Rule Engine Pipeline:</p>
                <div className="p-3 bg-slate-900 text-emerald-400 rounded-xl text-[11px] leading-relaxed">
                  <div># Artifact: ml/artifacts/fraud_risk_model.joblib</div>
                  <div># CalibratedClassifierCV (Platt Scaling)</div>
                  <div># Accuracy: 82.7% | Precision: 61.9% | ROC-AUC: 83.8%</div>
                  <div># Test Samples: 1,500 held-out transactions</div>
                  <div>&gt;&gt;&gt; coordinator.execute_decision_pipeline(data)</div>
                  <div>&gt;&gt;&gt; [FSM: RECEIVED -&gt; EXECUTING -&gt; FUSING -&gt; VALIDATING -&gt; EXPLAINING -&gt; COMPLETED]</div>
                </div>
              </div>
            )}

            {activeModal === 'explore' && (
              <div className="space-y-3 text-xs text-slate-600">
                <p>Platform navigation:</p>
                <div className="grid grid-cols-2 gap-2">
                  <a href="/decision" className="p-3 bg-slate-50 hover:bg-slate-100 border rounded-xl block font-semibold text-slate-800">
                    Decision Studio
                  </a>
                  <a href="/evaluations" className="p-3 bg-slate-50 hover:bg-slate-100 border rounded-xl block font-semibold text-slate-800">
                    Performance Benchmarks
                  </a>
                  <a href="/agents" className="p-3 bg-slate-50 hover:bg-slate-100 border rounded-xl block font-semibold text-slate-800">
                    Live Agent Monitor
                  </a>
                  <a href="/models" className="p-3 bg-slate-50 hover:bg-slate-100 border rounded-xl block font-semibold text-slate-800">
                    ML Models & Retraining
                  </a>
                  <a href="/rules" className="p-3 bg-slate-50 hover:bg-slate-100 border rounded-xl block font-semibold text-slate-800">
                    Symbolic Rule Base
                  </a>
                  <a href="/audit" className="p-3 bg-slate-50 hover:bg-slate-100 border rounded-xl block font-semibold text-slate-800">
                    Audit Log
                  </a>
                </div>
              </div>
            )}

            <div className="pt-2 text-right">
              <button
                onClick={() => setActiveModal(null)}
                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
