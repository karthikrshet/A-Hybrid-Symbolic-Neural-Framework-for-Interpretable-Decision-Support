'use client';
import React, { useEffect, useState } from 'react';

export default function DatasetsPage() {
  const [info, setInfo] = useState<any>(null);
  const [sample, setSample] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/api/v1/datasets/info").then(r => r.json()),
      fetch("http://localhost:8000/api/v1/datasets/sample?limit=15").then(r => r.json())
    ]).then(([infoData, sampleData]) => {
      setInfo(infoData);
      setSample(sampleData);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-navy-900">Financial Datasets & Preprocessing Pipeline</h2>
        <p className="text-sm text-slate-500">Benchmark datasets, exploratory data profiles, and tabular training distributions</p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400">Loading dataset distribution...</div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase">Total Records</span>
              <div className="text-2xl font-bold text-navy-900 mt-1">{info?.total_records?.toLocaleString()}</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase">Fraud Imbalance Rate</span>
              <div className="text-2xl font-bold text-rose-600 mt-1">{(info?.fraud_rate * 100)?.toFixed(1)}%</div>
              <span className="text-[11px] text-slate-500">{info?.fraud_cases} positive cases</span>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase">Mean Transaction</span>
              <div className="text-2xl font-bold text-navy-900 mt-1">${info?.summary_statistics?.mean_amount?.toFixed(2)}</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase">Engineered Features</span>
              <div className="text-2xl font-bold text-navy-900 mt-1">{info?.features_count} Dimensions</div>
            </div>
          </div>

          {/* Sample Table */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
              <h3 className="font-bold text-sm text-navy-900">Preprocessed Training Distribution (Sample Records)</h3>
              <span className="text-xs text-slate-500">Displaying first 15 records</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100 text-slate-600 font-bold uppercase">
                  <tr>
                    <th className="p-3">Amount</th>
                    <th className="p-3">Freq (24h)</th>
                    <th className="p-3">Velocity Ratio</th>
                    <th className="p-3">Distance (km)</th>
                    <th className="p-3">Hour</th>
                    <th className="p-3">Sanctioned</th>
                    <th className="p-3">IP Rep</th>
                    <th className="p-3">Device Trust</th>
                    <th className="p-3">Target (Is Fraud)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {sample.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="p-3 font-semibold text-slate-900 font-sans">${row.transaction_amount}</td>
                      <td className="p-3 text-slate-600">{row.transaction_frequency_24h}</td>
                      <td className="p-3 text-slate-600">{row.velocity_change_ratio}</td>
                      <td className="p-3 text-slate-600">{row.location_distance_km}</td>
                      <td className="p-3 text-slate-600">{row.hour_of_day}:00</td>
                      <td className="p-3">{row.is_sanctioned_destination ? <span className="text-rose-600 font-bold">YES</span> : 'NO'}</td>
                      <td className="p-3 text-slate-600">{row.ip_reputation_score}</td>
                      <td className="p-3 text-slate-600">{row.device_trust_score}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded font-bold uppercase ${row.is_fraud ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'}`}>
                          {row.is_fraud ? 'FRAUD (1)' : 'CLEAN (0)'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
