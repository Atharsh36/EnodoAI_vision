import React from 'react';
import { Sliders } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">System Settings & Thresholds</h1>
        <p className="text-sm text-slate-500 mt-1">
          Configure detection confidence cutoffs, IoU thresholds, quality score boundaries, and WebSocket latency settings
        </p>
      </div>

      <div className="glass-panel p-6 space-y-6 max-w-2xl bg-white border-slate-200">
        <div className="space-y-4">
          <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2 border-b border-slate-200 pb-2">
            <Sliders className="w-4 h-4 text-emerald-600" />
            <span>Confidence Assessment Thresholds</span>
          </h3>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <div className="flex justify-between text-slate-700 font-medium mb-1.5">
                <span>High Confidence Cutoff</span>
                <span className="font-mono text-emerald-700 font-bold">≥ 0.80</span>
              </div>
              <input type="range" min="0.5" max="0.95" step="0.05" defaultValue="0.80" className="w-full accent-emerald-600" />
            </div>

            <div>
              <div className="flex justify-between text-slate-700 font-medium mb-1.5">
                <span>Medium Confidence Cutoff</span>
                <span className="font-mono text-amber-700 font-bold">0.50 – 0.79</span>
              </div>
              <input type="range" min="0.3" max="0.7" step="0.05" defaultValue="0.50" className="w-full accent-amber-600" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
