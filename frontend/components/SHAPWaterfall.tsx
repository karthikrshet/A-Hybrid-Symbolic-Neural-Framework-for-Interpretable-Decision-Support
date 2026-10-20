import React from 'react';

interface FeatureAttribution {
  feature_name: string;
  feature_value: any;
  attribution_score: number;
  direction: string;
}

export const SHAPWaterfall: React.FC<{ attributions: FeatureAttribution[] }> = ({ attributions }) => {
  const maxScore = Math.max(...attributions.map(a => Math.abs(a.attribution_score)), 0.01);

  return (
    <div className="space-y-2">
      {attributions.slice(0, 6).map((attr, idx) => {
        const width = `${Math.min(100, (Math.abs(attr.attribution_score) / maxScore) * 100)}%`;
        const isPositive = attr.attribution_score >= 0;

        return (
          <div key={idx} className="text-xs">
            <div className="flex justify-between text-slate-700 font-medium mb-0.5">
              <span>{attr.feature_name}</span>
              <span className={`font-mono font-bold ${isPositive ? 'text-rose-600' : 'text-emerald-600'}`}>
                {isPositive ? '+' : ''}{attr.attribution_score.toFixed(4)}
              </span>
            </div>
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${isPositive ? 'bg-rose-500' : 'bg-emerald-500'}`}
                style={{ width }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

# Step 13: test(SHAPWaterfall): progressive code refinement step 13/1157
/* Accessible color contrast ratio compliance */

# Step 29: refactor(SHAPWaterfall): progressive code refinement step 29/1157
/* Accessible color contrast ratio compliance */
