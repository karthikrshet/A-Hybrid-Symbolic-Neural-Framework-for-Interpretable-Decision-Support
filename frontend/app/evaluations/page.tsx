'use client';
import React, { useEffect, useState } from "react";
import { 
  FiPlay, FiRefreshCw, FiCheckCircle, FiShield, 
  FiActivity, FiTrendingUp, FiTrendingDown, FiClock, FiLayers
} from "react-icons/fi";

export default function EvaluationsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBenchmark = async () => {
    try {
      setError(null);
      const res = await fetch("http://localhost:8000/api/v1/evaluations/benchmark");
      if (res.ok) {
        const json = await res.json();
        setData(json);
      } else {
        setError("Failed to load evaluation benchmark.");
      }
    } catch (err: any) {
      setError(err?.message || "Connection error to evaluation service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBenchmark();
  }, []);

  const handleRunEvaluation = async () => {
    setRunning(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/evaluations/run?n_samples=150", {
        method: "POST"
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
      } else {
        setError("Failed to complete dynamic evaluation.");
      }
    } catch (err: any) {
      setError(err?.message || "Evaluation execution error.");
    } finally {
      setRunning(false);
    }
  };

  const formatPct = (val?: number) => {
    if (val === undefined || val === null || isNaN(val)) return "N/A";
    return (val * 100).toFixed(1) + "%";
  };

  const formatDelta = (val?: number, isInverse: boolean = false) => {
    if (val === undefined || val === null || isNaN(val)) return "0.0%";
    const pct = (val * 100).toFixed(1);
    const isPositive = isInverse ? val < 0 : val > 0;
    const isNeutral = Math.abs(val) < 0.0001;
    const prefix = val > 0 ? "+" : "";
    
    return (
      <span className={`inline-flex items-center space-x-1 font-semibold ${isNeutral ? 'text-slate-500' : isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
        {!isNeutral && (isPositive ? <FiTrendingUp className="w-3.5 h-3.5" /> : <FiTrendingDown className="w-3.5 h-3.5" />)}
        <span>{prefix}{pct}%</span>
      </span>
    );
  };

  const baseline = data?.baseline_neural_only;
  const hybrid = data?.hybrid_symbolic_neural;
  const deltas = data?.delta_improvements;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold bg-blue-50 text-blue-700 border border-blue-200">
              HELD-OUT EMPIRICAL EVALUATION
            </span>
            {data?.sample_size && (
              <span className="text-xs text-slate-500">
                N = {data.sample_size} test transactions
              </span>
            )}
          </div>
          <h2 className="text-2xl font-bold text-navy-900 mt-1">Empirical Benchmark & Evaluation</h2>
          <p className="text-sm text-slate-500">
            Head-to-head comparison: Conventional Neural Baseline vs. Proposed Hybrid Symbolic-Neural Architecture
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchBenchmark}
            disabled={loading || running}
            className="px-3.5 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition flex items-center space-x-1.5"
            title="Refresh benchmark data"
          >
            <FiRefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleRunEvaluation}
            disabled={running}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition flex items-center space-x-2 shadow-sm disabled:opacity-60"
          >
            {running ? (
              <>
                <FiRefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Running Test Split Evaluation...</span>
              </>
            ) : (
              <>
                <FiPlay className="w-3.5 h-3.5" />
                <span>Run Live Benchmark Evaluation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchBenchmark} className="underline text-xs font-semibold">Retry</button>
        </div>
      )}

      {loading && !data ? (
        <div className="p-16 text-center text-slate-400 bg-white rounded-xl border border-slate-200">
          <FiRefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
          <p className="text-sm">Loading dynamic evaluation results...</p>
        </div>
      ) : (
        <>
          {/* Top Key Takeaway Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
                <FiShield className="w-3.5 h-3.5 text-blue-600" />
                <span>Rule Consistency Rate</span>
              </span>
              <div className="text-2xl font-bold text-navy-900">{formatPct(hybrid?.rule_consistency_rate)}</div>
              <div className="text-xs text-emerald-600 font-semibold flex items-center space-x-1">
                <FiCheckCircle className="w-3 h-3" />
                <span>100% Deterministic Override Invariant</span>
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
                <FiActivity className="w-3.5 h-3.5 text-emerald-600" />
                <span>Precision (Imbalance)</span>
              </span>
              <div className="text-2xl font-bold text-navy-900">{formatPct(hybrid?.precision)}</div>
              <div className="text-xs text-slate-500">
                vs {formatPct(baseline?.precision)} baseline ({formatDelta(deltas?.precision_gain)})
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
                <FiLayers className="w-3.5 h-3.5 text-purple-600" />
                <span>Interpretability Coverage</span>
              </span>
              <div className="text-2xl font-bold text-navy-900">{formatPct(hybrid?.interpretability_score)}</div>
              <div className="text-xs text-purple-600 font-semibold">
                Verifiable SHAP + Rule Linkage
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
                <FiClock className="w-3.5 h-3.5 text-slate-500" />
                <span>Mean Pipeline Latency</span>
              </span>
              <div className="text-2xl font-bold text-navy-900">
                {hybrid?.mean_latency_ms ? hybrid.mean_latency_ms.toFixed(1) + " ms" : "N/A"}
              </div>
              <div className="text-xs text-slate-400">
                Multi-Agent Coordination Overhead
              </div>
            </div>
          </div>

          {/* Comparative Metrics Table */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-sm text-navy-900">Empirical Test Results on Held-Out Split</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Calculated dynamically across real statistical models and deterministic forward-chaining rules
                </p>
              </div>
              {data?.timestamp && (
                <span className="text-[11px] font-mono text-slate-400">
                  Last evaluated: {new Date(data.timestamp).toLocaleString()}
                </span>
              )}
            </div>

            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100 text-xs font-bold text-slate-600 uppercase">
                <tr>
                  <th className="p-4">Evaluation Metric</th>
                  <th className="p-4">Conventional Neural Baseline</th>
                  <th className="p-4">Proposed Hybrid Framework</th>
                  <th className="p-4">Delta Improvement</th>
                  <th className="p-4">Mathematical Formulation / Meaning</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">Overall Accuracy</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.accuracy)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.accuracy)}</td>
                  <td className="p-4">{formatDelta(deltas?.accuracy_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">(TP + TN) / Total Samples</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">Precision (Positive Predictive Value)</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.precision)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.precision)}</td>
                  <td className="p-4">{formatDelta(deltas?.precision_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">TP / (TP + FP) — Minimizes false alerts</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">Recall (Sensitivity)</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.recall)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.recall)}</td>
                  <td className="p-4">{formatDelta(deltas?.recall_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">TP / (TP + FN) — Captures genuine fraud</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">F1-Score (Harmonic Mean)</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.f1_score)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.f1_score)}</td>
                  <td className="p-4">{formatDelta(deltas?.f1_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">2 * (P * R) / (P + R) under class imbalance</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">PR-AUC (Precision-Recall Curve)</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.pr_auc)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.pr_auc)}</td>
                  <td className="p-4">{formatDelta(deltas?.pr_auc_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">Area under Precision-Recall curve</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">ROC-AUC</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.roc_auc)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.roc_auc)}</td>
                  <td className="p-4">{formatDelta(deltas?.roc_auc_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">Area under Receiver Operating Characteristic</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">Rule Consistency Rate</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.rule_consistency_rate)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.rule_consistency_rate)}</td>
                  <td className="p-4">
                    <span className="text-emerald-600 font-semibold text-xs">
                      {hybrid?.rule_consistency_rate === 1.0 ? "100.0% Hard Invariant" : formatDelta(deltas?.rule_consistency_gain)}
                    </span>
                  </td>
                  <td className="p-4 text-xs text-slate-500">Adherence to hard statutory AML overrides</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">Decision Stability (Adversarial Perturbation)</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.decision_stability)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.decision_stability)}</td>
                  <td className="p-4">{formatDelta(deltas?.stability_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">Invariance under 2% continuous input jitter</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">Interpretability Coverage</td>
                  <td className="p-4 text-slate-600 font-mono">{formatPct(baseline?.interpretability_score)}</td>
                  <td className="p-4 font-bold text-navy-900 font-mono">{formatPct(hybrid?.interpretability_score)}</td>
                  <td className="p-4">{formatDelta(deltas?.interpretability_gain)}</td>
                  <td className="p-4 text-xs text-slate-500">Ratio of decisions with complete SHAP + rule audit traces</td>
                </tr>

                <tr className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-800">Mean Execution Latency</td>
                  <td className="p-4 text-slate-600 font-mono">
                    {baseline?.mean_latency_ms ? baseline.mean_latency_ms.toFixed(1) + " ms" : "N/A"}
                  </td>
                  <td className="p-4 text-slate-700 font-mono">
                    {hybrid?.mean_latency_ms ? hybrid.mean_latency_ms.toFixed(1) + " ms" : "N/A"}
                  </td>
                  <td className="p-4 text-xs text-slate-500">
                    +{(hybrid?.mean_latency_ms - baseline?.mean_latency_ms)?.toFixed(1)} ms
                  </td>
                  <td className="p-4 text-xs text-slate-500">End-to-end 5-agent coordination pipeline</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Operational Sub-Counts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase">Hard Statutory Overrides</span>
              <div className="text-2xl font-bold text-rose-600 mt-1">
                {hybrid?.rule_override_count ?? 0} Transactions
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Cases where deterministic compliance law strictly superseded statistical model probability.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase">Uncertainty Human Review Escalations</span>
              <div className="text-2xl font-bold text-amber-600 mt-1">
                {hybrid?.human_review_count ?? 0} Transactions
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Cases falling within the epistemic uncertainty band [30%-70%] safely routed to compliance officers.
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
