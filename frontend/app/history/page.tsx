'use client';
import React, { useEffect, useState } from 'react';

export default function DecisionHistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/decisions/history")
      .then(res => res.json())
      .then(d => {
        setHistory(d || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-navy-900">Decision History & Adjudication Logs</h2>
        <p className="text-sm text-slate-500">Immutable chronological record of transactions evaluated by the multi-agent decision core</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase">
            <tr>
              <th className="p-3">Timestamp</th>
              <th className="p-3">Correlation ID</th>
              <th className="p-3">Decision</th>
              <th className="p-3">Confidence</th>
              <th className="p-3">Neural Score</th>
              <th className="p-3">Hard Override</th>
              <th className="p-3">Human Review</th>
              <th className="p-3">Latency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono">
            {history.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-50">
                <td className="p-3 text-slate-500 font-sans">{new Date(row.created_at).toLocaleTimeString()}</td>
                <td className="p-3 font-semibold text-slate-800">{row.correlation_id.substring(0, 12)}...</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded font-bold uppercase ${
                    row.decision === 'REJECT' ? 'bg-rose-100 text-rose-800' : row.decision === 'APPROVE' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {row.decision}
                  </span>
                </td>
                <td className="p-3 font-bold text-slate-900">{(row.confidence * 100).toFixed(0)}%</td>
                <td className="p-3 text-slate-600">{(row.neural_score * 100).toFixed(1)}%</td>
                <td className="p-3">{row.rule_override ? <span className="text-rose-600 font-bold">YES</span> : 'NO'}</td>
                <td className="p-3">{row.human_review_required ? <span className="text-amber-600 font-bold">YES</span> : 'NO'}</td>
                <td className="p-3 text-slate-500">{row.latency_ms?.toFixed(1)} ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
