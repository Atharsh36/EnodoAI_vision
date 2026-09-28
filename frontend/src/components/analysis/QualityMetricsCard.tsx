import React from 'react';
import { ShieldCheck, AlertTriangle, AlertCircle, Eye, Sun } from 'lucide-react';
import { QualityMetrics } from '../../types';

interface Props {
  metrics: QualityMetrics;
}

export const QualityMetricsCard: React.FC<Props> = ({ metrics }) => {
  const getQualityBadge = (status: string) => {
    switch (status) {
      case 'GOOD':
        return (
          <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold flex items-center space-x-1.5 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>GOOD OPTICAL QUALITY</span>
          </span>
        );
      case 'WARNING':
        return (
          <span className="px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold flex items-center space-x-1.5 font-mono">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>QUALITY WARNING</span>
          </span>
        );
      case 'POOR':
      default:
        return (
          <span className="px-3 py-1 rounded-full bg-rose-50 text-rose-700 border border-rose-200 text-xs font-semibold flex items-center space-x-1.5 font-mono">
            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>POOR OPTICAL QUALITY</span>
          </span>
        );
    }
  };

  // Normalize scores for progress bar rendering
  const blurPct = Math.min(100, (metrics.blur_score / 200.0) * 100);
  const brightnessPct = Math.min(100, (metrics.brightness_score / 255.0) * 100);

  return (
    <div className="glass-panel p-5 space-y-4 border-l-4 border-l-emerald-600">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <Eye className="w-4 h-4 text-emerald-600" />
          <span>Optical Image Quality Metrics</span>
        </h3>
        {getQualityBadge(metrics.overall_quality)}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
        {/* Blur Metric */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
          <div className="flex justify-between text-slate-700">
            <span className="text-slate-500 flex items-center space-x-1">
              <span>Laplacian Blur Variance</span>
            </span>
            <strong className="text-emerald-700">{metrics.blur_score.toFixed(1)}</strong>
          </div>
          <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                metrics.blur_score >= 100
                  ? 'bg-emerald-500'
                  : metrics.blur_score >= 40
                  ? 'bg-amber-500'
                  : 'bg-rose-500'
              }`}
              style={{ width: `${blurPct}%` }}
            ></div>
          </div>
          <span className="text-[10px] text-slate-500 block">Cutoffs: &lt;40 Poor | 40-99 Warning | &ge;100 Good</span>
        </div>

        {/* Brightness Metric */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
          <div className="flex justify-between text-slate-700">
            <span className="text-slate-500 flex items-center space-x-1">
              <Sun className="w-3 h-3 text-amber-500" />
              <span>Mean Illumination</span>
            </span>
            <strong className="text-amber-700">{metrics.brightness_score.toFixed(1)} / 255</strong>
          </div>
          <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                metrics.brightness_score >= 40 && metrics.brightness_score <= 215
                  ? 'bg-emerald-500'
                  : 'bg-amber-500'
              }`}
              style={{ width: `${brightnessPct}%` }}
            ></div>
          </div>
          <span className="text-[10px] text-slate-500 block">Cutoffs: 40 - 215 optimal range</span>
        </div>
      </div>

      {/* Warnings List */}
      {metrics.warnings.length > 0 && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs space-y-1">
          <div className="font-semibold text-amber-900 flex items-center space-x-1">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>Quality Considerations:</span>
          </div>
          <ul className="list-disc list-inside text-amber-800 text-[11px] space-y-0.5 pl-1">
            {metrics.warnings.map((warn, idx) => (
              <li key={idx}>{warn}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
