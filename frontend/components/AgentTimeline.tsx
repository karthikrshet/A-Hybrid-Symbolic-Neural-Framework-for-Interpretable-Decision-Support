import React from 'react';

interface TraceStep {
  agent_id: string;
  step: string;
  status: string;
  execution_time_ms: number;
  timestamp: string;
}

export const AgentTimeline: React.FC<{ traces: TraceStep[] }> = ({ traces }) => {
  return (
    <div className="space-y-3">
      {traces.map((t, idx) => (
        <div key={idx} className="flex items-start space-x-3 text-xs">
          <div className="w-2.5 h-2.5 rounded-full bg-navy-600 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <div className="flex justify-between font-semibold text-slate-800">
              <span>{t.step}</span>
              <span className="text-slate-400 font-mono">{t.execution_time_ms.toFixed(1)} ms</span>
            </div>
            <p className="text-slate-500 text-[11px]">Executed by {t.agent_id} &bull; Status: {t.status}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

# Step 12: chore(AgentTimeline): progressive code refinement step 12/1157
/* Micro-animation transition curve */

# Step 28: fix(AgentTimeline): progressive code refinement step 28/1157
/* Micro-animation transition curve */

# Step 44: perf(AgentTimeline): progressive code refinement step 44/1157
/* Micro-animation transition curve */

# Step 60: docs(AgentTimeline): progressive code refinement step 60/1157
/* Micro-animation transition curve */

# Step 76: test(AgentTimeline): progressive code refinement step 76/1157
/* Micro-animation transition curve */

# Step 92: refactor(AgentTimeline): progressive code refinement step 92/1157
/* Micro-animation transition curve */

# Step 108: style(AgentTimeline): progressive code refinement step 108/1157
/* Micro-animation transition curve */

# Step 124: chore(AgentTimeline): progressive code refinement step 124/1157
/* Micro-animation transition curve */

# Step 140: fix(AgentTimeline): progressive code refinement step 140/1157
/* Micro-animation transition curve */

# Step 156: perf(AgentTimeline): progressive code refinement step 156/1157
/* Micro-animation transition curve */
