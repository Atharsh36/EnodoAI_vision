import React, { useState } from 'react';
import { Upload, Activity, Download, RefreshCw, AlertCircle, X } from 'lucide-react';
import { api } from '../services/api';
import { FrameAnalysis } from '../types';
import { DetectionOverlay } from '../components/analysis/DetectionOverlay';
import { RegionSelector } from '../components/analysis/RegionSelector';
import { QualityMetricsCard } from '../components/analysis/QualityMetricsCard';
import { GradCamViewer } from '../components/analysis/GradCamViewer';
import { ReviewPanel } from '../components/review/ReviewPanel';

export const ImageAnalysisPage: React.FC = () => {
  const [file, setFile]                         = useState<File | null>(null);
  const [analyzing, setAnalyzing]               = useState(false);
  const [result, setResult]                     = useState<FrameAnalysis | null>(null);
  const [selectedRegionIndex, setSelectedRegionIndex] = useState<number>(1);
  const [error, setError]                       = useState<string | null>(null);
  const [dragOver, setDragOver]                 = useState(false);

  const handleFile = (f: File) => { setFile(f); setError(null); };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f && f.type.startsWith('image/')) handleFile(f);
  };

  const handleRunAnalysis = async () => {
    if (!file) return;
    setAnalyzing(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_anon_id', `PATIENT-${Math.floor(1000 + Math.random() * 9000)}`);
    try {
      const res = await api.post<FrameAnalysis>('/analyze/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
      if (res.data.detections.length > 0) setSelectedRegionIndex(res.data.detections[0].region_index);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Ensure the backend service is running.');
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => { setResult(null); setFile(null); setError(null); };
  const selectedDetection = result?.detections.find((d) => d.region_index === selectedRegionIndex) ?? result?.detections[0];

  return (
    <div className="space-y-5">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Image Analysis</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Abnormality detection · Softmax classification · Grad-CAM explainability
          </p>
        </div>
        {result && (
          <a
            href={`/api/reports/${result.examination_id}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
          >
            <Download className="w-4 h-4" />
            Export PDF Report
          </a>
        )}
      </div>

      {/* ── Upload zone ── */}
      {!result && (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`panel p-10 flex flex-col items-center gap-5 border-2 border-dashed transition-colors duration-200 bg-white
            ${dragOver ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-300 hover:border-emerald-400'}`}
        >
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-colors shadow-xs
            ${dragOver ? 'bg-emerald-100 text-emerald-700' : 'bg-emerald-50 text-emerald-600 border border-emerald-200'}`}>
            <Upload className="w-6 h-6" />
          </div>

          <div className="text-center">
            <p className="text-sm font-bold text-slate-800">
              {file ? file.name : 'Drop an endoscopic image here'}
            </p>
            <p className="text-xs text-slate-500 mt-1">JPG, JPEG, PNG supported</p>
          </div>

          <div className="flex items-center gap-3">
            <input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} id="img-upload" className="hidden" />
            <label htmlFor="img-upload" className="btn-ghost cursor-pointer">
              {file ? 'Change File' : 'Browse Files'}
            </label>
            {file && (
              <button onClick={handleRunAnalysis} disabled={analyzing} className="btn-primary">
                {analyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
                {analyzing ? 'Analyzing…' : 'Run Analysis'}
              </button>
            )}
          </div>

          {error && (
            <div className="w-full max-w-md flex items-center gap-2.5 px-4 py-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}
        </div>
      )}

      {/* ── Results ── */}
      {result && (
        <div className="space-y-5">
          {/* Result meta bar */}
          <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-xs font-mono shadow-2xs">
            <span className="text-slate-600">
              Exam <span className="text-emerald-700 font-bold">{result.examination_id}</span>
              <span className="mx-2 text-slate-300">·</span>
              <span className="text-slate-800 font-semibold">{result.detections.length} detection{result.detections.length !== 1 ? 's' : ''}</span>
            </span>
            <button onClick={reset} className="flex items-center gap-1.5 text-slate-500 hover:text-slate-800 font-medium transition">
              <X className="w-3.5 h-3.5" /> New frame
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Left column */}
            <div className="space-y-5">
              <DetectionOverlay
                imageUrl={result.image_url}
                detections={result.detections}
                selectedRegionIndex={selectedRegionIndex}
                onSelectRegion={setSelectedRegionIndex}
              />
              <RegionSelector
                detections={result.detections}
                selectedIndex={selectedRegionIndex}
                onSelect={setSelectedRegionIndex}
              />
              <QualityMetricsCard metrics={result.quality} />
            </div>

            {/* Right column */}
            <div className="space-y-5">
              {selectedDetection ? (
                <>
                  {/* Softmax scores */}
                  <div className="panel p-5 space-y-4 border-slate-200 bg-white">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-bold text-slate-900">
                        Region #{selectedDetection.region_index} — Classification
                      </h3>
                      <span className="badge badge-emerald">{selectedDetection.prediction?.predicted_class}</span>
                    </div>
                    <div className="space-y-3">
                      {Object.entries(selectedDetection.prediction?.raw_softmax_scores || {}).map(([cls, score]) => (
                        <div key={cls}>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-600 font-mono font-medium">{cls}</span>
                            <span className="text-emerald-700 font-mono font-bold">{(score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="progress-track h-2 bg-slate-100">
                            <div className="progress-fill bg-emerald-600" style={{ width: `${score * 100}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <GradCamViewer detection={selectedDetection} />
                  <ReviewPanel
                    examinationId={result.examination_id}
                    frameId={result.frame_id}
                    detectionId={selectedDetection.id}
                  />
                </>
              ) : (
                <div className="panel p-8 text-center text-sm text-slate-500 border-slate-200 bg-white">
                  Select a region to view classification and Grad-CAM results.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
