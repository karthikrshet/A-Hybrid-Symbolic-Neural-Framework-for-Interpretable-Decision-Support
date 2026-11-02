'use client';
import React, { useEffect, useState } from 'react';

export default function AgentsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/agents")
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-navy-900">Specialized AI Agents Ecosystem</h2>
        <p className="text-sm text-slate-500">Live operational status, paradigms, and capabilities of all participating autonomous agents</p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400">Loading agent telemetry...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data?.agents?.map((agent: any, idx: number) => (
            <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[11px] font-mono font-bold text-navy-600 bg-navy-50 px-2 py-0.5 rounded">{agent.agent_id}</span>
                  <h3 className="font-bold text-lg text-slate-900 mt-1">{agent.name}</h3>
                </div>
                <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span>{agent.status}</span>
                </span>
              </div>

              <div className="text-xs text-slate-600 space-y-1">
                <div><strong>Paradigm:</strong> <span className="text-slate-800">{agent.paradigm}</span></div>
                {agent.model_version && <div><strong>Model Version:</strong> <span className="font-mono text-navy-700">{agent.model_version}</span></div>}
                {agent.active_rules_count && <div><strong>Active Rules:</strong> <span className="text-navy-700 font-bold">{agent.active_rules_count} Rules</span></div>}
              </div>

              {agent.features_utilized && (
                <div>
                  <span className="text-[11px] font-bold text-slate-400 uppercase">Input Features ({agent.features_utilized.length})</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {agent.features_utilized.slice(0, 7).map((f: string, i: number) => (
                      <span key={i} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-mono">{f}</span>
                    ))}
                    {agent.features_utilized.length > 7 && (
                      <span className="px-2 py-0.5 bg-slate-100 text-slate-400 rounded text-[10px]">+{agent.features_utilized.length - 7} more</span>
                    )}
                  </div>
                </div>
              )}

              {agent.checks_enforced && (
                <div>
                  <span className="text-[11px] font-bold text-slate-400 uppercase">Invariants Enforced</span>
                  <ul className="mt-1 list-disc list-inside text-xs text-slate-600 space-y-0.5">
                    {agent.checks_enforced.map((c: string, i: number) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
