'use client';
import React, { useState } from "react";

export default function DecisionAnalysisPage() {
  const [amount, setAmount] = useState(12500);
  const [freq, setFreq] = useState(4);
  const [velocity, setVelocity] = useState(2.8);
  const [sanctioned, setSanctioned] = useState(false);
  const [kyc, setKyc] = useState("VERIFIED");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        transaction_amount: Number(amount),
        transaction_frequency_24h: Number(freq),
        velocity_change_ratio: Number(velocity),
        location_distance_km: 15.0,
        hour_of_day: 14,
        is_weekend: false,
        is_sanctioned_destination: sanctioned,
        kyc_status: kyc,
        foreign_exchange_risk: 0.1,
        ip_reputation_score: 0.90,
        device_trust_score: 0.85,
        user_failed_attempts_1h: 0,
        past_chargeback_count: 0
      };
      const res = await fetch("http://localhost:8000/api/v1/decisions/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setResult(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-navy-900">Structured Decision Analysis</h2>
          <p className="text-sm text-slate-500">Submit financial records to the multi-agent neuro-symbolic pipeline</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Panel */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-semibold text-lg text-navy-900">Transaction Parameters</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Transaction Amount ($)</label>
              <input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">24h Frequency</label>
              <input type="number" value={freq} onChange={(e) => setFreq(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Velocity Change Ratio</label>
              <input type="number" step="0.1" value={velocity} onChange={(e) => setVelocity(Number(e.target.value))} className="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">KYC Status</label>
              <select value={kyc} onChange={(e) => setKyc(e.target.value)} className="w-full px-3 py-2 border rounded-lg text-sm">
                <option value="VERIFIED">VERIFIED</option>
                <option value="INCOMPLETE">INCOMPLETE</option>
              </select>
            </div>
            <div className="flex items-center space-x-2 pt-2">
              <input type="checkbox" id="sanc" checked={sanctioned} onChange={(e) => setSanctioned(e.target.checked)} className="rounded text-navy-600" />
              <label htmlFor="sanc" className="text-xs font-semibold text-rose-700">Sanctioned Country Destination</label>
            </div>
            <button type="submit" disabled={loading} className="w-full py-2.5 bg-navy-700 hover:bg-navy-800 text-white rounded-lg font-medium text-sm transition">
              {loading ? "Evaluating Agents..." : "Analyze Transaction"}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Final Decision Outcome</span>
                  <div className={`text-3xl font-extrabold mt-1 ${result.final_decision === 'REJECT' ? 'text-rose-600' : result.final_decision === 'APPROVE' ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {result.final_decision}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Confidence Score</span>
                  <div className="text-2xl font-bold text-navy-900 mt-1">{(result.confidence_score * 100).toFixed(1)}%</div>
                </div>
              </div>

              {/* Summary */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                <h4 className="text-xs font-bold text-navy-900 uppercase">Explainable Decision Report</h4>
                <p className="mt-1 text-sm text-slate-700 leading-relaxed">{result.explanation.summary}</p>
              </div>

              {/* Triggered Rules */}
              <div>
                <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Triggered Symbolic Rules</h4>
                {result.symbolic_analysis.triggered_rules.length > 0 ? (
                  <div className="space-y-2">
                    {result.symbolic_analysis.triggered_rules.map((r: any, idx: number) => (
                      <div key={idx} className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex justify-between items-center text-xs">
                        <div>
                          <span className="font-bold text-rose-900">{r.rule_name}</span>
                          <p className="text-rose-700 mt-0.5">{r.reason}</p>
                        </div>
                        <span className="px-2 py-1 bg-rose-200 text-rose-800 rounded font-bold uppercase">{r.severity}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-slate-400 italic">No symbolic rules or legal violations triggered.</div>
                )}
              </div>

              {/* SHAP Feature Attributions */}
              <div>
                <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Key Neural Driving Features</h4>
                <div className="space-y-2">
                  {result.explanation.top_driving_features?.map((f: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100">
                      <span className="font-medium text-slate-700">{f.feature_name}</span>
                      <span className={`font-mono font-bold ${f.attribution_score > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                        {f.attribution_score > 0 ? '+' : ''}{f.attribution_score.toFixed(3)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white p-12 rounded-xl border border-dashed border-slate-300 text-center text-slate-400">
              Select transaction parameters and click "Analyze Transaction" to observe real multi-agent collaboration.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
