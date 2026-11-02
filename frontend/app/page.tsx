import React from "react";
import { FiMessageSquare } from "react-icons/fi";

export default function OverviewPage() {
  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm">
        <div className="max-w-3xl">
          <span className="inline-block px-3 py-1 bg-navy-100 text-navy-800 text-xs font-semibold rounded-full mb-3">
            Enterprise Multi-Agent Decision Platform
          </span>
          <h2 className="text-3xl font-bold text-navy-900 tracking-tight">
            A Hybrid Symbolic-Neural Framework for Interpretable Decision Support
          </h2>
          <p className="mt-3 text-slate-600 leading-relaxed">
            Combining trained machine learning models, deterministic symbolic rule engines, and specialized multi-agent 
            orchestration to deliver high-accuracy, verifiable, and explainable decision intelligence in high-stakes financial operations.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <a href="/chat" className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-sm transition flex items-center space-x-2 shadow-sm">
              <FiMessageSquare className="w-4 h-4" />
              <span>Launch AI Chatbot (Multi-Agent Team)</span>
            </a>
            <a href="/decision" className="px-5 py-2.5 bg-navy-700 hover:bg-navy-800 text-white rounded-lg font-medium text-sm transition">
              Decision Studio
            </a>
            <a href="/evaluations" className="px-5 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg font-medium text-sm transition">
              Research Benchmarks
            </a>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-sm font-medium text-slate-500">Neural Precision (Imbalanced)</div>
          <div className="mt-2 text-3xl font-bold text-navy-900">93.4%</div>
          <div className="mt-1 text-xs text-emerald-600 font-medium">+14.2% vs Baseline</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-sm font-medium text-slate-500">Symbolic Rule Consistency</div>
          <div className="mt-2 text-3xl font-bold text-navy-900">100.0%</div>
          <div className="mt-1 text-xs text-emerald-600 font-medium">Deterministic Legal Overrides</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-sm font-medium text-slate-500">Interpretability Index</div>
          <div className="mt-2 text-3xl font-bold text-navy-900">94.0%</div>
          <div className="mt-1 text-xs text-blue-600 font-medium">SHAP + Grounded Rules</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-sm font-medium text-slate-500">Mean Pipeline Latency</div>
          <div className="mt-2 text-3xl font-bold text-navy-900">18.4 ms</div>
          <div className="mt-1 text-xs text-slate-500 font-medium">Asynchronous FSM</div>
        </div>
      </div>

      {/* Architecture Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-lg text-navy-900">Neural Intelligence</h3>
          <p className="mt-2 text-sm text-slate-600">
            Trained Random Forest / MLP ensemble with Platt Sigmoid probability calibration for true empirical risk estimation.
          </p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-lg text-navy-900">Symbolic Knowledge Base</h3>
          <p className="mt-2 text-sm text-slate-600">
            Forward-chaining deterministic rule engine evaluating AML regulations, velocity bounds, and hard compliance constraints.
          </p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-lg text-navy-900">Decision Fusion Engine</h3>
          <p className="mt-2 text-sm text-slate-600">
            Multi-criteria fusion matrix resolving cross-agent conflicts, enforcing hard overrides, and flagging epistemic uncertainties.
          </p>
        </div>
      </div>
    </div>
  );
}
