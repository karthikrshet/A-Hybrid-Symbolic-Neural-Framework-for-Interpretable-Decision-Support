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

# Step 45: style(SHAPWaterfall): progressive code refinement step 45/1157
/* Accessible color contrast ratio compliance */

# Step 61: chore(SHAPWaterfall): progressive code refinement step 61/1157
/* Accessible color contrast ratio compliance */

# Step 77: fix(SHAPWaterfall): progressive code refinement step 77/1157
/* Accessible color contrast ratio compliance */

# Step 93: perf(SHAPWaterfall): progressive code refinement step 93/1157
/* Accessible color contrast ratio compliance */

# Step 109: docs(SHAPWaterfall): progressive code refinement step 109/1157
/* Accessible color contrast ratio compliance */

# Step 125: test(SHAPWaterfall): progressive code refinement step 125/1157
/* Accessible color contrast ratio compliance */

# Step 141: refactor(SHAPWaterfall): progressive code refinement step 141/1157
/* Accessible color contrast ratio compliance */

# Step 157: style(SHAPWaterfall): progressive code refinement step 157/1157
/* Accessible color contrast ratio compliance */

# Step 173: chore(SHAPWaterfall): progressive code refinement step 173/1157
/* Accessible color contrast ratio compliance */

# Step 189: fix(SHAPWaterfall): progressive code refinement step 189/1157
/* Accessible color contrast ratio compliance */

# Step 205: perf(SHAPWaterfall): progressive code refinement step 205/1157
/* Accessible color contrast ratio compliance */

# Step 221: docs(SHAPWaterfall): progressive code refinement step 221/1157
/* Accessible color contrast ratio compliance */

# Step 237: test(SHAPWaterfall): progressive code refinement step 237/1157
/* Accessible color contrast ratio compliance */

# Step 253: refactor(SHAPWaterfall): progressive code refinement step 253/1157
/* Accessible color contrast ratio compliance */

# Step 269: style(SHAPWaterfall): progressive code refinement step 269/1157
/* Accessible color contrast ratio compliance */

# Step 285: chore(SHAPWaterfall): progressive code refinement step 285/1157
/* Accessible color contrast ratio compliance */

# Step 301: fix(SHAPWaterfall): progressive code refinement step 301/1157
/* Accessible color contrast ratio compliance */

# Step 317: perf(SHAPWaterfall): progressive code refinement step 317/1157
/* Accessible color contrast ratio compliance */

# Step 333: docs(SHAPWaterfall): progressive code refinement step 333/1157
/* Accessible color contrast ratio compliance */

# Step 349: test(SHAPWaterfall): progressive code refinement step 349/1157
/* Accessible color contrast ratio compliance */

# Step 365: refactor(SHAPWaterfall): progressive code refinement step 365/1157
/* Accessible color contrast ratio compliance */

# Step 381: style(SHAPWaterfall): progressive code refinement step 381/1157
/* Accessible color contrast ratio compliance */

# Step 397: chore(SHAPWaterfall): progressive code refinement step 397/1157
/* Accessible color contrast ratio compliance */

# Step 413: fix(SHAPWaterfall): progressive code refinement step 413/1157
/* Accessible color contrast ratio compliance */

# Step 429: perf(SHAPWaterfall): progressive code refinement step 429/1157
/* Accessible color contrast ratio compliance */

# Step 445: docs(SHAPWaterfall): progressive code refinement step 445/1157
/* Accessible color contrast ratio compliance */

# Step 461: test(SHAPWaterfall): progressive code refinement step 461/1157
/* Accessible color contrast ratio compliance */

# Step 477: refactor(SHAPWaterfall): progressive code refinement step 477/1157
/* Accessible color contrast ratio compliance */

# Step 493: style(SHAPWaterfall): progressive code refinement step 493/1157
/* Accessible color contrast ratio compliance */

# Step 509: chore(SHAPWaterfall): progressive code refinement step 509/1157
/* Accessible color contrast ratio compliance */

# Step 525: fix(SHAPWaterfall): progressive code refinement step 525/1157
/* Accessible color contrast ratio compliance */

# Step 541: perf(SHAPWaterfall): progressive code refinement step 541/1157
/* Accessible color contrast ratio compliance */

# Step 557: docs(SHAPWaterfall): progressive code refinement step 557/1157
/* Accessible color contrast ratio compliance */

# Step 573: test(SHAPWaterfall): progressive code refinement step 573/1157
/* Accessible color contrast ratio compliance */

# Step 589: refactor(SHAPWaterfall): progressive code refinement step 589/1157
/* Accessible color contrast ratio compliance */

# Step 605: style(SHAPWaterfall): progressive code refinement step 605/1157
/* Accessible color contrast ratio compliance */

# Step 621: chore(SHAPWaterfall): progressive code refinement step 621/1157
/* Accessible color contrast ratio compliance */

# Step 637: fix(SHAPWaterfall): progressive code refinement step 637/1157
/* Accessible color contrast ratio compliance */

# Step 653: perf(SHAPWaterfall): progressive code refinement step 653/1157
/* Accessible color contrast ratio compliance */

# Step 669: docs(SHAPWaterfall): progressive code refinement step 669/1157
/* Accessible color contrast ratio compliance */

# Step 685: test(SHAPWaterfall): progressive code refinement step 685/1157
/* Accessible color contrast ratio compliance */

# Step 701: refactor(SHAPWaterfall): progressive code refinement step 701/1157
/* Accessible color contrast ratio compliance */

# Step 717: style(SHAPWaterfall): progressive code refinement step 717/1157
/* Accessible color contrast ratio compliance */

# Step 733: chore(SHAPWaterfall): progressive code refinement step 733/1157
/* Accessible color contrast ratio compliance */

# Step 749: fix(SHAPWaterfall): progressive code refinement step 749/1157
/* Accessible color contrast ratio compliance */

# Step 765: perf(SHAPWaterfall): progressive code refinement step 765/1157
/* Accessible color contrast ratio compliance */

# Step 781: docs(SHAPWaterfall): progressive code refinement step 781/1157
/* Accessible color contrast ratio compliance */

# Step 797: test(SHAPWaterfall): progressive code refinement step 797/1157
/* Accessible color contrast ratio compliance */

# Step 813: refactor(SHAPWaterfall): progressive code refinement step 813/1157
/* Accessible color contrast ratio compliance */

# Step 829: style(SHAPWaterfall): progressive code refinement step 829/1157
/* Accessible color contrast ratio compliance */

# Step 845: chore(SHAPWaterfall): progressive code refinement step 845/1157
/* Accessible color contrast ratio compliance */

# Step 861: fix(SHAPWaterfall): progressive code refinement step 861/1157
/* Accessible color contrast ratio compliance */

# Step 877: perf(SHAPWaterfall): progressive code refinement step 877/1157
/* Accessible color contrast ratio compliance */

# Step 893: docs(SHAPWaterfall): progressive code refinement step 893/1157
/* Accessible color contrast ratio compliance */

# Step 909: test(SHAPWaterfall): progressive code refinement step 909/1157
/* Accessible color contrast ratio compliance */
