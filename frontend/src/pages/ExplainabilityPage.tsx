import React, { useEffect, useState } from 'react';
import { Eye, RefreshCw, Activity, Layers } from 'lucide-react';
import { useSearchParams, Link } from 'react-router-dom';
import { fetchExaminations, fetchExaminationReport } from '../services/api';
import { ExaminationReport, Detection } from '../types';
import { GradCamViewer } from '../components/analysis/GradCamViewer';

export const ExplainabilityPage: React.FC = () => {
  const [searchParams]          = useSearchParams();
  const examIdParam             = searchParams.get('exam');
  const [report, setReport]     = useState<ExaminationReport | null>(null);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        let targetId = examIdParam;
        if (!targetId) {
          const exams = await fetchExaminations();
          if (exams.length > 0) targetId = exams[0].id;
        }
        if (targetId) {
          const rep = await fetchExaminationReport(targetId);
          setReport(rep);
        }
      } catch (err) {
        console.error('Failed loading explainability heatmaps:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [examIdParam]);

  if (loading) {
    return (
      <div className="panel p-12 text-center text-slate-500 flex flex-col items-center justify-center space-y-3 bg-white border-slate-200">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
        <p className="text-sm font-medium">Generating Grad-CAM activation heatmaps…</p>
      </div>
    );
  }

  if (!report || report.detections.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Grad-CAM Visual Explainability Engine</h1>
          <p className="text-sm text-slate-500 mt-1">
            Feature map gradient activation heatmaps & endoscopic layer overlays
          </p>
        </div>

        <div className="glass-panel p-10 text-center bg-white border-slate-200 space-y-4">
          <Eye className="w-12 h-12 text-emerald-600/60 mx-auto" />
          <div>
            <h3 className="font-bold text-slate-900 text-base">No Heatmaps Active</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              Upload an endoscopic image or video to generate deep neural feature activation heatmaps.
            </p>
          </div>
          <Link to="/image-analysis" className="btn-primary inline-flex">
            <Activity className="w-4 h-4" />
            Analyze Image for Heatmaps
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Grad-CAM Visual Explainability Engine</h1>
        <p className="text-sm text-slate-500 mt-1">
          Exam ID: <span className="font-mono text-emerald-700 font-bold">{report.id}</span> · Target Layer: <span className="font-mono font-bold text-slate-800">ResNet50 Conv4 (layer4)</span>
        </p>
      </div>

      {/* Info Notice */}
      <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-center space-x-3">
        <Layers className="w-5 h-5 text-emerald-600 shrink-0" />
        <span>
          <strong className="font-bold">Neural Explainability Interpretation:</strong> Grad-CAM computes gradients of the target Softmax class score with respect to feature activation maps in the final convolutional layer. High-intensity warm regions (red/yellow) indicate key mucosal microvascular and pit pattern features driving the AI prediction.
        </span>
      </div>

      {/* Heatmap Cards Grid */}
      <div className="space-y-6">
        {report.detections.map((det: Detection) => (
          <div key={det.id || det.region_id} className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="font-bold text-slate-900">Region #{det.region_index} — {det.prediction?.predicted_class || det.class_name}</span>
              <span className="text-emerald-700 font-bold">Confidence: {Math.round((det.prediction?.class_confidence || det.confidence) * 100)}%</span>
            </div>
            <GradCamViewer detection={det} />
          </div>
        ))}
      </div>
    </div>
  );
};
