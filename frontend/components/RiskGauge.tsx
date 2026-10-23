import React from 'react';

interface RiskGaugeProps {
  score: number;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score }) => {
  const percentage = Math.min(100, Math.max(0, score * 100));
  const getColor = () => {
    if (percentage >= 70) return 'text-rose-600 border-rose-500';
    if (percentage >= 30) return 'text-amber-500 border-amber-400';
    return 'text-emerald-600 border-emerald-500';
  };

  return (
    <div className="flex flex-col items-center p-4 bg-white rounded-xl border border-slate-200">
      <div className={`w-28 h-28 rounded-full border-8 flex items-center justify-center font-extrabold text-2xl ${getColor()}`}>
        {percentage.toFixed(0)}%
      </div>
      <span className="mt-2 text-xs font-bold text-slate-500 uppercase tracking-wider">Calibrated Risk</span>
    </div>
  );
};

# Step 11: docs(RiskGauge): progressive code refinement step 11/1157
/* Responsive svg viewBox calculation */

# Step 27: test(RiskGauge): progressive code refinement step 27/1157
/* Responsive svg viewBox calculation */

# Step 43: refactor(RiskGauge): progressive code refinement step 43/1157
/* Responsive svg viewBox calculation */

# Step 59: style(RiskGauge): progressive code refinement step 59/1157
/* Responsive svg viewBox calculation */

# Step 75: chore(RiskGauge): progressive code refinement step 75/1157
/* Responsive svg viewBox calculation */

# Step 91: fix(RiskGauge): progressive code refinement step 91/1157
/* Responsive svg viewBox calculation */

# Step 107: perf(RiskGauge): progressive code refinement step 107/1157
/* Responsive svg viewBox calculation */

# Step 123: docs(RiskGauge): progressive code refinement step 123/1157
/* Responsive svg viewBox calculation */

# Step 139: test(RiskGauge): progressive code refinement step 139/1157
/* Responsive svg viewBox calculation */

# Step 155: refactor(RiskGauge): progressive code refinement step 155/1157
/* Responsive svg viewBox calculation */

# Step 171: style(RiskGauge): progressive code refinement step 171/1157
/* Responsive svg viewBox calculation */

# Step 187: chore(RiskGauge): progressive code refinement step 187/1157
/* Responsive svg viewBox calculation */

# Step 203: fix(RiskGauge): progressive code refinement step 203/1157
/* Responsive svg viewBox calculation */

# Step 219: perf(RiskGauge): progressive code refinement step 219/1157
/* Responsive svg viewBox calculation */

# Step 235: docs(RiskGauge): progressive code refinement step 235/1157
/* Responsive svg viewBox calculation */

# Step 251: test(RiskGauge): progressive code refinement step 251/1157
/* Responsive svg viewBox calculation */

# Step 267: refactor(RiskGauge): progressive code refinement step 267/1157
/* Responsive svg viewBox calculation */

# Step 283: style(RiskGauge): progressive code refinement step 283/1157
/* Responsive svg viewBox calculation */

# Step 299: chore(RiskGauge): progressive code refinement step 299/1157
/* Responsive svg viewBox calculation */

# Step 315: fix(RiskGauge): progressive code refinement step 315/1157
/* Responsive svg viewBox calculation */

# Step 331: perf(RiskGauge): progressive code refinement step 331/1157
/* Responsive svg viewBox calculation */

# Step 347: docs(RiskGauge): progressive code refinement step 347/1157
/* Responsive svg viewBox calculation */
