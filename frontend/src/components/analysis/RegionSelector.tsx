import React from 'react';
import { Detection } from '../../types';

interface Props {
  detections: Detection[];
  selectedIndex: number | null;
  onSelect: (index: number) => void;
}

export const RegionSelector: React.FC<Props> = ({ detections, selectedIndex, onSelect }) => {
  if (detections.length === 0) {
    return (
      <div className="p-4 rounded-xl bg-white border border-slate-200 text-slate-500 text-xs text-center shadow-xs">
        No abnormal regions detected in frame.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500 flex items-center justify-between">
        <span>Detected Regions ({detections.length})</span>
        <span className="text-[10px] text-emerald-700 font-mono font-medium">Select region to inspect</span>
      </h3>

      <div className="space-y-2">
        {detections.map((det) => {
          const isSelected = selectedIndex === det.region_index;
          const pred = det.prediction;
          const confLevel = pred?.confidence_level || 'HIGH';

          return (
            <button
              key={det.region_id}
              onClick={() => onSelect(det.region_index)}
              className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                isSelected
                  ? 'bg-emerald-50/90 border-emerald-500 text-slate-900 shadow-md shadow-emerald-600/10 ring-1 ring-emerald-500/40'
                  : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50/60'
              }`}
            >
              <div className="flex items-center justify-between font-semibold text-xs mb-1">
                <span className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-mono font-bold text-[10px]">
                    Region #{det.region_index}
                  </span>
                  <span className="text-slate-900 font-semibold">{pred?.predicted_class || det.class_name}</span>
                </span>
                <span className="font-mono text-emerald-700 font-bold">
                  {Math.round((pred?.class_confidence || det.confidence) * 100)}%
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mt-2">
                <span>Confidence Level:</span>
                <span
                  className={`font-semibold px-2 py-0.5 rounded text-[10px] ${
                    confLevel === 'HIGH'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : confLevel === 'MEDIUM'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}
                >
                  {confLevel} CONFIDENCE
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
