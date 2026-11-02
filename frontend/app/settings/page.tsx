'use client';
import React from 'react';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-bold text-navy-900">System Configuration & Threshold Settings</h2>
        <p className="text-sm text-slate-500">Configure decision fusion parameters, epistemic uncertainty bands, and compliance rules</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-navy-900">Decision Fusion Thresholds</h3>
          
          <div className="space-y-3 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">High Risk Threshold (P(Risk) &ge; 0.70)</label>
              <input type="number" defaultValue={0.70} step={0.05} className="w-full px-3 py-2 border rounded-lg" />
              <span className="text-slate-400">Probabilities at or above this value trigger REJECT or FLAG_SUSPICIOUS</span>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Low Risk Clearance Bound (P(Risk) &lt; 0.30)</label>
              <input type="number" defaultValue={0.30} step={0.05} className="w-full px-3 py-2 border rounded-lg" />
              <span className="text-slate-400">Transactions below this threshold are eligible for clear consensus APPROVE</span>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Uncertainty Human Review Band</label>
              <div className="p-3 bg-slate-50 border rounded-lg font-mono text-slate-700">
                [0.30, 0.70] &rarr; Escalate to Compliance Officer
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-navy-900">System & Platform Architecture</h3>
          <div className="text-xs text-slate-600 space-y-2 leading-relaxed">
            <div><strong>Platform:</strong> NeuroSymbolic Multi-Agent Decision Support</div>
            <div><strong>Deployment Target:</strong> Production Financial Compliance & AML Risk</div>
            <div><strong>Orchestrator:</strong> 7-State Deterministic Coordinator FSM</div>
            <div><strong>Inference Engines:</strong> Calibrated Machine Learning + Forward-Chaining Rules</div>
            <div className="pt-2 border-t border-slate-100 text-slate-500">
              Built as an enterprise-grade multi-agent neuro-symbolic framework merging empirical models, deterministic IF-THEN expert systems, and verifiable TreeSHAP explainability.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
