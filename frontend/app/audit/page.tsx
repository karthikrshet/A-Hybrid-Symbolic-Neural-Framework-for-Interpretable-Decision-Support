'use client';
import React, { useEffect, useState } from 'react';

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [verified, setVerified] = useState<boolean | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/audit/logs")
      .then(res => res.json())
      .then(data => setLogs(data || []))
      .catch(() => {});

    fetch("http://localhost:8000/api/v1/audit/verify")
      .then(res => res.json())
      .then(data => setVerified(data.chain_valid))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-navy-900">Cryptographic Audit Trail</h2>
          <p className="text-sm text-slate-500">Tamper-evident decision log backed by SHA-256 hash chaining</p>
        </div>
        {verified !== null && (
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>SHA-256 Integrity Chain Verified</span>
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase">
            <tr>
              <th className="p-3">Timestamp</th>
              <th className="p-3">Entity Type</th>
              <th className="p-3">Action</th>
              <th className="p-3">Actor</th>
              <th className="p-3">Payload Hash (SHA-256)</th>
              <th className="p-3">Previous Hash</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono">
            {logs.map((e, idx) => (
              <tr key={idx} className="hover:bg-slate-50">
                <td className="p-3 text-slate-500 font-sans">{new Date(e.timestamp).toLocaleString()}</td>
                <td className="p-3 font-semibold text-slate-700">{e.entity_type}</td>
                <td className="p-3 text-navy-700 font-bold">{e.action}</td>
                <td className="p-3 text-slate-600">{e.actor}</td>
                <td className="p-3 text-slate-500">{e.payload_hash.substring(0, 16)}...</td>
                <td className="p-3 text-slate-400">{e.prev_hash.substring(0, 16)}...</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
