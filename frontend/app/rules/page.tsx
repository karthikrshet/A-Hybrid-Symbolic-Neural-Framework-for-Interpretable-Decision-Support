'use client';
import React, { useEffect, useState } from 'react';

export default function RulesPage() {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/rules/list")
      .then(res => res.json())
      .then(data => {
        setRules(data.rules || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-navy-900">Symbolic Knowledge Base & Compliance Rules</h2>
        <p className="text-sm text-slate-500">Deterministic IF-THEN rules governing financial regulations, KYC bounds, and velocity limits</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {rules.map((r, idx) => (
          <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono text-xs font-bold text-navy-600 bg-navy-50 px-2 py-0.5 rounded">{r.rule_id}</span>
                <h3 className="font-bold text-slate-900 text-base mt-1.5">{r.name}</h3>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                r.is_hard_override ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {r.is_hard_override ? 'Hard Override' : 'Soft Heuristic'}
              </span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">{r.description}</p>
            <div className="pt-2 border-t border-slate-100 text-xs text-slate-500 flex justify-between">
              <span>Category: <strong className="text-slate-700">{r.category}</strong></span>
              <span>Regulatory Ref: <strong className="text-slate-700">{r.regulatory_reference || 'Internal'}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
