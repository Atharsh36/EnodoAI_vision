import React, { useState } from 'react';
import { Eye } from 'lucide-react';
import { Detection } from '../../types';

interface Props {
  detection: Detection;
}

export const GradCamViewer: React.FC<Props> = ({ detection }) => {
  const [activeTab, setActiveTab] = useState<'OVERLAY' | 'HEATMAP' | 'SPLIT'>('OVERLAY');
  const exp = detection.explanation;

  if (!exp || (!exp.heatmap_url && !exp.overlay_url)) {
    return (
      <div className="glass-panel p-6 text-center text-slate-500 text-xs">
        Grad-CAM activation heatmap not available for this region.
      </div>
    );
  }

  return (
    <div className="glass-panel p-5 space-y-4 border-l-4 border-l-emerald-600">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
            <Eye className="w-4 h-4 text-emerald-600" />
            <span>Grad-CAM Visual Explainability</span>
          </h3>
          <p className="text-[11px] text-slate-500 mt-0.5 font-mono">
            Layer: {exp.target_layer} • Target: {detection.prediction?.predicted_class || detection.class_name}
          </p>
        </div>

        {/* View mode toggle */}
        <div className="flex items-center space-x-1 p-1 rounded-lg bg-slate-100 border border-slate-200 text-xs font-mono">
          <button
            onClick={() => setActiveTab('OVERLAY')}
            className={`px-3 py-1 rounded-md transition ${
              activeTab === 'OVERLAY' ? 'bg-emerald-600 text-white font-semibold shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Blended Overlay
          </button>
          <button
            onClick={() => setActiveTab('HEATMAP')}
            className={`px-3 py-1 rounded-md transition ${
              activeTab === 'HEATMAP' ? 'bg-emerald-600 text-white font-semibold shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Activation Heatmap
          </button>
          <button
            onClick={() => setActiveTab('SPLIT')}
            className={`px-3 py-1 rounded-md transition ${
              activeTab === 'SPLIT' ? 'bg-emerald-600 text-white font-semibold shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Side-by-Side
          </button>
        </div>
      </div>

      {/* Visual Heatmap Display */}
      {activeTab === 'SPLIT' ? (
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5 text-center">
            <span className="text-[11px] text-slate-600 font-mono block font-medium">Feature Activation Heatmap</span>
            <img src={exp.heatmap_url} alt="Grad-CAM Heatmap" className="w-full h-48 object-cover rounded-xl border border-slate-200" />
          </div>
          <div className="space-y-1.5 text-center">
            <span className="text-[11px] text-slate-600 font-mono block font-medium">Endoscopic Overlay</span>
            <img src={exp.overlay_url} alt="Blended Overlay" className="w-full h-48 object-cover rounded-xl border border-slate-200" />
          </div>
        </div>
      ) : (
        <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-900 flex justify-center">
          <img
            src={activeTab === 'HEATMAP' ? exp.heatmap_url : exp.overlay_url}
            alt="Grad-CAM Visual"
            className="max-h-72 object-contain"
          />
        </div>
      )}
    </div>
  );
};
