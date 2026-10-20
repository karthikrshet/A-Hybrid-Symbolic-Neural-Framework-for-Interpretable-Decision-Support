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
