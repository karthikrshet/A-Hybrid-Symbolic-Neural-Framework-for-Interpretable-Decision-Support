'use client';
import React, { useState, useEffect, useRef } from 'react';
import {
  FiEdit3,
  FiPlus,
  FiSend,
  FiSettings,
  FiUser,
  FiChevronDown,
  FiChevronUp,
  FiShield,
  FiActivity,
  FiBarChart2,
  FiX,
  FiCheckCircle,
  FiInfo,
  FiKey,
  FiTrash2,
  FiMessageSquare,
  FiCpu,
  FiCopy,
  FiCheck,
  FiRefreshCw
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

interface ConversationItem {
  id: string;
  title: string;
  created_at?: string;
}

export default function ChatPage() {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [thinkMode, setThinkMode] = useState(true);
  const [selectedModel, setSelectedModel] = useState('neurosymbolic-multiagent');
  const [apiKey, setApiKey] = useState('');
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [expandedTraceId, setExpandedTraceId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load API key from localStorage on mount
  useEffect(() => {
    const savedKey = localStorage.getItem('neurosymbolic_api_key') || '';
    setApiKey(savedKey);
    fetchConversations();
  }, []);

  // Fetch conversations from backend
  const fetchConversations = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/chat/conversations');
      if (res.ok) {
        const list: ConversationItem[] = await res.json();
        setConversations(list);
        if (list.length > 0 && !currentSessionId) {
          loadConversation(list[0].id);
        } else if (list.length === 0) {
          startNewChat(false);
        }
      }
    } catch {
      // Fallback if offline
      if (!currentSessionId) {
        const localId = 'session_' + Date.now();
        setCurrentSessionId(localId);
      }
    }
  };

  // Load messages for a specific conversation session
  const loadConversation = async (convId: string) => {
    setCurrentSessionId(convId);
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/chat/conversations/${convId}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      } else {
        setMessages([]);
      }
    } catch {
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  // Start a fresh chat session
  const startNewChat = async (createOnBackend = true) => {
    setMessages([]);
    setInput('');
    if (createOnBackend) {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/chat/conversations', {
          method: 'POST'
        });
        if (res.ok) {
          const newConv: ConversationItem = await res.json();
          setConversations(prev => [newConv, ...prev]);
          setCurrentSessionId(newConv.id);
          inputRef.current?.focus();
          return;
        }
      } catch {
        // Fallback
      }
    }
    const newId = 'session_' + Date.now();
    setCurrentSessionId(newId);
    inputRef.current?.focus();
  };

  // Delete a conversation session
  const deleteConversation = async (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    try {
      await fetch(`http://127.0.0.1:8000/api/v1/chat/conversations/${convId}`, {
        method: 'DELETE'
      });
      setConversations(prev => prev.filter(c => c.id !== convId));
      if (currentSessionId === convId) {
        const remaining = conversations.filter(c => c.id !== convId);
        if (remaining.length > 0) {
          loadConversation(remaining[0].id);
        } else {
          startNewChat(true);
        }
      }
    } catch {
      setConversations(prev => prev.filter(c => c.id !== convId));
    }
  };

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
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: currentSessionId || undefined,
          message: query,
          model: selectedModel,
          api_key: apiKey || undefined
        })
      });

      if (res.ok) {
        const data = await res.json();
        
        // Update session ID if backend returned one
        if (data.conversation_id && data.conversation_id !== currentSessionId) {
          setCurrentSessionId(data.conversation_id);
        }

        const assistantMsg: MessageItem = {
          id: String(Date.now() + 1),
          sender: 'ASSISTANT',
          text: data.reply,
          decision: data.decision,
          traces: data.agent_traces || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, assistantMsg]);

        // Refresh conversations to show updated title
        fetchConversations();
      } else {
        throw new Error('Backend HTTP error');
      }
    } catch {
      setMessages(prev => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'ASSISTANT',
          text: 'Unable to reach the Neuro-Symbolic Coordinator at http://127.0.0.1:8000. Please verify that the backend server is active.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const saveSettings = () => {
    localStorage.setItem('neurosymbolic_api_key', apiKey);
    setShowSettingsModal(false);
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
          LEFT SIDEBAR: CHAT SESSIONS & HISTORY (ZERO MOCK JUNK)
      ========================================================================= */}
      <aside className="w-64 bg-[#f9f9f9] border-r border-gray-200/80 flex flex-col justify-between shrink-0 select-none">
        <div className="p-3 flex flex-col h-[calc(100vh-65px)]">
          {/* New Chat Button */}
          <button
            onClick={() => startNewChat(true)}
            className="w-full flex items-center justify-between px-3 py-2 bg-white hover:bg-gray-100/80 border border-gray-200/80 rounded-xl text-sm font-medium text-slate-800 transition shadow-sm group shrink-0"
          >
            <div className="flex items-center space-x-2.5">
              <FiEdit3 className="w-4 h-4 text-slate-600 group-hover:text-slate-900" />
              <span>New chat</span>
            </div>
            <span className="text-[11px] text-gray-400 font-mono">
              <FiPlus className="w-3.5 h-3.5 inline" />
            </span>
          </button>

          {/* Chat Sessions Header */}
          <div className="pt-4 pb-2 px-3 flex items-center justify-between shrink-0">
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
              Recent Chats
            </span>
            <span className="text-[10px] text-gray-400 font-mono">
              {conversations.length}
            </span>
          </div>

          {/* Chat Sessions List (Real, Dynamic, Database-Backed) */}
          <div className="flex-1 overflow-y-auto space-y-1 pr-1 text-xs">
            {conversations.length === 0 ? (
              <div className="px-3 py-6 text-center text-slate-400 text-xs italic">
                No past conversations. Click &ldquo;New chat&rdquo; to start.
              </div>
            ) : (
              conversations.map(conv => {
                const isActive = conv.id === currentSessionId;
                return (
                  <div
                    key={conv.id}
                    onClick={() => loadConversation(conv.id)}
                    className={`group flex items-center justify-between px-3 py-2.5 rounded-lg transition cursor-pointer text-left ${
                      isActive
                        ? 'bg-slate-200/70 text-slate-900 font-semibold shadow-sm'
                        : 'text-slate-600 hover:bg-gray-200/50 hover:text-slate-900'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5 min-w-0 flex-1 mr-2">
                      <FiMessageSquare
                        className={`w-3.5 h-3.5 shrink-0 ${
                          isActive ? 'text-blue-600' : 'text-slate-400'
                        }`}
                      />
                      <span className="truncate block">{conv.title || 'Conversation'}</span>
                    </div>

                    <button
                      onClick={e => deleteConversation(e, conv.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-600 text-slate-400 rounded transition"
                      title="Delete chat session"
                    >
                      <FiTrash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Sidebar Footer: Settings & Account */}
        <div className="p-3 border-t border-gray-200/80 bg-white/50">
          <button
            onClick={() => setShowSettingsModal(true)}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-200/60 transition text-left text-xs font-medium text-slate-700"
          >
            <div className="flex items-center space-x-2.5">
              <FiSettings className="w-4 h-4 text-slate-500" />
              <span>Model & API Settings</span>
            </div>
            {apiKey ? (
              <span className="w-2 h-2 rounded-full bg-emerald-500" title="API key configured" />
            ) : (
              <span className="text-[10px] text-slate-400">Default</span>
            )}
          </button>
        </div>
      </aside>

      {/* =========================================================================
          MAIN CHAT WORKSPACE
      ========================================================================= */}
      <main className="flex-1 flex flex-col h-screen relative bg-white overflow-hidden">
        {/* Top Floating Control Bar */}
        <header className="h-14 px-6 border-b border-gray-100 flex items-center justify-between shrink-0 bg-white/90 backdrop-blur z-10">
          <div className="flex items-center space-x-3">
            {/* Model Selector Dropdown */}
            <div className="relative inline-block text-left">
              <select
                value={selectedModel}
                onChange={e => setSelectedModel(e.target.value)}
                className="appearance-none bg-slate-50 hover:bg-slate-100 text-slate-800 font-semibold text-xs px-3 py-1.5 pr-8 rounded-lg border border-slate-200 cursor-pointer focus:outline-none transition shadow-sm"
              >
                <option value="neurosymbolic-multiagent">NeuroSymbolic Multi-Agent Team (Default)</option>
                <option value="gpt-4o-mini">OpenAI GPT-4o Mini</option>
                <option value="gemini-1.5-flash">Google Gemini 1.5 Flash</option>
              </select>
              <FiChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
              {selectedModel === 'neurosymbolic-multiagent'
                ? 'ML Classifier + Deterministic Rules + TreeSHAP'
                : 'External Generative LLM'}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => startNewChat(true)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 transition flex items-center space-x-1.5"
            >
              <FiPlus className="w-3.5 h-3.5" />
              <span>New chat</span>
            </button>

            <button
              onClick={() => setShowSettingsModal(true)}
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
              title="Configure API Keys"
            >
              <FiKey className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Message Feed / Empty State */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6">
          {messages.length === 0 ? (
            /* Empty State: Clean & Functional */
            <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto text-center space-y-6 select-none">
              <div className="w-14 h-14 rounded-2xl bg-slate-900 text-white flex items-center justify-center shadow-lg">
                <FiCpu className="w-7 h-7 text-blue-400" />
              </div>

              <div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  What can I help with today?
                </h1>
                <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
                  Submit financial transactions to the 5-agent neuro-symbolic engine or ask any questions about AML risk and explainability.
                </p>
              </div>

              {/* Functional Quick-Action Chips */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left pt-2">
                <button
                  onClick={() =>
                    handleSend(
                      'Evaluate a $15,000 transaction with incomplete KYC and 4 failed login attempts'
                    )
                  }
                  className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 transition group"
                >
                  <div className="text-xs font-semibold text-slate-800 group-hover:text-blue-700">
                    High Risk & Incomplete KYC
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                    $15,000 wire with KYC incomplete & 4 failed logins
                  </div>
                </button>

                <button
                  onClick={() =>
                    handleSend(
                      'Evaluate transaction of $50,000 destined for a sanctioned embargoed country'
                    )
                  }
                  className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 transition group"
                >
                  <div className="text-xs font-semibold text-slate-800 group-hover:text-blue-700">
                    Sanctioned Jurisdiction Override
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                    Triggers deterministic AML hard statutory rejection
                  </div>
                </button>

                <button
                  onClick={() =>
                    handleSend(
                      'How do deterministic AML rules override neural machine learning probabilities?'
                    )
                  }
                  className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 transition group"
                >
                  <div className="text-xs font-semibold text-slate-800 group-hover:text-blue-700">
                    Neuro-Symbolic Precedence
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                    Explain the multi-criteria fusion decision matrix
                  </div>
                </button>

                <button
                  onClick={() =>
                    handleSend(
                      'Explain how TreeSHAP calculates feature attributions for fraud risk scoring'
                    )
                  }
                  className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 transition group"
                >
                  <div className="text-xs font-semibold text-slate-800 group-hover:text-blue-700">
                    TreeSHAP Explainability
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                    Polynomial Shapley values for transparent decision support
                  </div>
                </button>
              </div>
            </div>
          ) : (
            /* Active Message History */
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${
                    msg.sender === 'USER' ? 'items-end' : 'items-start'
                  } space-y-2`}
                >
                  {/* Sender & Timestamp Header */}
                  <div className="flex items-center space-x-2 text-[11px] text-slate-400 px-1">
                    <span className="font-semibold text-slate-600">
                      {msg.sender === 'USER' ? 'You' : 'NeuroSymbolic AI'}
                    </span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                  </div>

                  {/* Message Bubble */}
                  <div
                    className={`rounded-2xl p-4 text-sm leading-relaxed ${
                      msg.sender === 'USER'
                        ? 'bg-slate-100 text-slate-900 rounded-tr-sm max-w-[85%]'
                        : 'bg-white border border-slate-200/90 shadow-sm text-slate-800 w-full'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.text}</div>

                    {/* Decision Verdict Card (if financial transaction was evaluated) */}
                    {msg.decision && (
                      <div className="mt-4 pt-4 border-t border-slate-100 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                            Formal Multi-Agent Verdict
                          </span>
                          <span
                            className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                              msg.decision.final_decision === 'REJECT'
                                ? 'bg-rose-100 text-rose-800'
                                : msg.decision.final_decision === 'APPROVE'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-amber-100 text-amber-800'
                            }`}
                          >
                            {msg.decision.final_decision}
                          </span>
                        </div>

                        {/* Confidence & Epistemic Uncertainty */}
                        <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100 font-mono">
                          <div>
                            <span className="text-slate-500 font-sans block text-[10px] uppercase">
                              Confidence
                            </span>
                            <span className="font-bold text-slate-800">
                              {(msg.decision.confidence_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-500 font-sans block text-[10px] uppercase">
                              Calibrated Neural Risk
                            </span>
                            <span className="font-bold text-slate-800">
                              {(
                                (msg.decision.neural_analysis?.risk_probability || 0) * 100
                              ).toFixed(1)}
                              %
                            </span>
                          </div>
                        </div>

                        {/* Triggered Rules */}
                        {msg.decision.symbolic_analysis?.triggered_rules?.length > 0 && (
                          <div>
                            <span className="text-[11px] font-bold text-slate-500 uppercase block mb-1.5">
                              Triggered Compliance Rules
                            </span>
                            <div className="space-y-1">
                              {msg.decision.symbolic_analysis.triggered_rules.map(
                                (r: any, idx: number) => (
                                  <div
                                    key={idx}
                                    className="p-2 rounded bg-rose-50/70 border border-rose-200/70 text-xs flex justify-between items-center"
                                  >
                                    <span className="font-medium text-rose-900">{r.rule_name}</span>
                                    <span className="text-[10px] font-bold uppercase text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded">
                                      {r.severity}
                                    </span>
                                  </div>
                                )
                              )}
                            </div>
                          </div>
                        )}

                        {/* Top Driving SHAP Features */}
                        {msg.decision.explanation?.top_driving_features?.length > 0 && (
                          <div>
                            <span className="text-[11px] font-bold text-slate-500 uppercase block mb-1.5">
                              Top TreeSHAP Attribution Factors
                            </span>
                            <div className="space-y-1">
                              {msg.decision.explanation.top_driving_features
                                .slice(0, 3)
                                .map((f: any, idx: number) => (
                                  <div
                                    key={idx}
                                    className="flex items-center justify-between text-xs py-1 px-2 rounded bg-slate-50"
                                  >
                                    <span className="text-slate-700">{f.feature_name}</span>
                                    <span
                                      className={`font-mono font-bold ${
                                        f.attribution_score > 0
                                          ? 'text-rose-600'
                                          : 'text-emerald-600'
                                      }`}
                                    >
                                      {f.attribution_score > 0 ? '+' : ''}
                                      {f.attribution_score.toFixed(3)}
                                    </span>
                                  </div>
                                ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Collaborative Multi-Agent Execution Trace (Think Mode) */}
                    {thinkMode && msg.traces && msg.traces.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-100">
                        <button
                          onClick={() =>
                            setExpandedTraceId(expandedTraceId === msg.id ? null : msg.id)
                          }
                          className="flex items-center space-x-1.5 text-xs text-blue-600 font-semibold hover:text-blue-800 transition"
                        >
                          <FiActivity className="w-3.5 h-3.5" />
                          <span>
                            {expandedTraceId === msg.id ? 'Hide' : 'View'} 5-Agent Collaborative
                            Workflow Trace ({msg.traces.length} steps)
                          </span>
                          {expandedTraceId === msg.id ? (
                            <FiChevronUp className="w-3.5 h-3.5" />
                          ) : (
                            <FiChevronDown className="w-3.5 h-3.5" />
                          )}
                        </button>

                        {expandedTraceId === msg.id && (
                          <div className="mt-2.5 space-y-2 bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs">
                            {msg.traces.map((trace, idx) => (
                              <div
                                key={idx}
                                className="flex items-start space-x-2.5 pb-2 border-b border-slate-200/60 last:border-0 last:pb-0"
                              >
                                <div className="mt-0.5">{getAgentIcon(trace.agent_type)}</div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-slate-800">
                                      {trace.agent_id}
                                    </span>
                                    <span className="text-[10px] text-slate-400 font-mono">
                                      {trace.execution_time_ms.toFixed(1)} ms
                                    </span>
                                  </div>
                                  <div className="text-slate-600 mt-0.5 text-[11px]">
                                    {trace.details?.action ||
                                      trace.details?.role ||
                                      trace.step}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Copy Response Button */}
                    {msg.sender === 'ASSISTANT' && (
                      <div className="mt-2 flex items-center justify-end space-x-2">
                        <button
                          onClick={() => copyToClipboard(msg.text, msg.id)}
                          className="text-slate-400 hover:text-slate-700 text-xs flex items-center space-x-1 p-1 rounded transition"
                          title="Copy response"
                        >
                          {copiedId === msg.id ? (
                            <>
                              <FiCheck className="w-3 h-3 text-emerald-600" />
                              <span className="text-emerald-600 text-[10px]">Copied</span>
                            </>
                          ) : (
                            <>
                              <FiCopy className="w-3 h-3" />
                              <span className="text-[10px]">Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Streaming / Loading Indicator */}
              {loading && (
                <div className="flex flex-col items-start space-y-2">
                  <div className="flex items-center space-x-2 text-[11px] text-slate-400 px-1">
                    <span className="font-semibold text-slate-600">NeuroSymbolic AI</span>
                    <span>•</span>
                    <span>Evaluating...</span>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center space-x-3">
                    <FiRefreshCw className="w-4 h-4 text-blue-600 animate-spin" />
                    <span className="text-xs text-slate-600">
                      Multi-agent pipeline coordinating neural inference & symbolic rule evaluation...
                    </span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* =========================================================================
            BOTTOM FLOATING INPUT BAR
        ========================================================================= */}
        <div className="p-4 bg-gradient-to-t from-white via-white to-transparent shrink-0">
          <div className="max-w-3xl mx-auto">
            <div className="relative bg-white border border-gray-300 rounded-2xl shadow-md focus-within:border-gray-500 focus-within:ring-1 focus-within:ring-gray-500 transition-all p-3">
              {/* Text Input */}
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={1}
                placeholder="Ask anything or describe a transaction to analyze..."
                className="w-full resize-none border-0 bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-0 max-h-36 min-h-[24px]"
              />

              {/* Bottom Row Tools inside Input Capsule */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                {/* Think Mode Pill */}
                <button
                  type="button"
                  onClick={() => setThinkMode(!thinkMode)}
                  className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold transition ${
                    thinkMode
                      ? 'bg-blue-100 text-blue-800 border border-blue-200'
                      : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                  }`}
                  title="Toggle multi-agent collaborative thinking traces"
                >
                  <FiCpu className="w-3.5 h-3.5" />
                  <span>Think</span>
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      thinkMode ? 'bg-blue-600' : 'bg-gray-400'
                    }`}
                  />
                </button>

                {/* Send Button */}
                <button
                  type="button"
                  onClick={() => handleSend()}
                  disabled={!input.trim() || loading}
                  className={`p-2 rounded-xl transition ${
                    input.trim() && !loading
                      ? 'bg-slate-900 text-white hover:bg-slate-800 shadow-sm'
                      : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                  }`}
                  title="Send message (Enter)"
                >
                  <FiSend className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="text-center mt-2 text-[11px] text-slate-400">
              Multi-Agent Decision Support combines machine learning statistical inference with deterministic rule compliance.
            </div>
          </div>
        </div>
      </main>

      {/* =========================================================================
          API KEY & MODEL CONFIGURATION MODAL
      ========================================================================= */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <FiKey className="w-5 h-5 text-blue-600" />
                <h3 className="text-base font-bold text-navy-900">Model & API Key Configuration</h3>
              </div>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="text-slate-400 hover:text-slate-700"
              >
                <FiX className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  OpenAI or Gemini API Key (Optional)
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={e => setApiKey(e.target.value)}
                  placeholder="sk-... or AIzaSy..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs font-mono"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  If omitted, queries automatically execute via our high-precision deterministic Grounded XAI Synthesizer with zero hallucinations.
                </p>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Active Architecture</label>
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 space-y-1">
                  <div>
                    <strong>Paradigm:</strong> Hybrid Neuro-Symbolic Multi-Agent System
                  </div>
                  <div>
                    <strong>Models:</strong> Calibrated Random Forest / MLP + Platt Sigmoid
                  </div>
                  <div>
                    <strong>Knowledge Engine:</strong> Deterministic Forward-Chaining Rules
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2 border-t border-slate-100">
              <button
                onClick={() => setShowSettingsModal(false)}
                className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={saveSettings}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition shadow-sm"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
