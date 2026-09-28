import React, { useState } from 'react';
import { Video, Upload, Activity, Download, RefreshCw, AlertCircle, X, Film } from 'lucide-react';
import { analyzeVideo } from '../services/api';
import { ExaminationReport, Detection } from '../types';
import { DetectionOverlay } from '../components/analysis/DetectionOverlay';
import { RegionSelector } from '../components/analysis/RegionSelector';
import { QualityMetricsCard } from '../components/analysis/QualityMetricsCard';
import { GradCamViewer } from '../components/analysis/GradCamViewer';
import { ReviewPanel } from '../components/review/ReviewPanel';

export const VideoAnalysisPage: React.FC = () => {
  const [file, setFile]                         = useState<File | null>(null);
  const [analyzing, setAnalyzing]               = useState(false);
  const [result, setResult]                     = useState<ExaminationReport | null>(null);
  const [selectedFrameIdx, setSelectedFrameIdx] = useState<number>(0);
  const [selectedRegionIdx, setSelectedRegionIdx] = useState<number>(1);
  const [error, setError]                       = useState<string | null>(null);
  const [dragOver, setDragOver]                 = useState(false);

  const handleFile = (f: File) => { setFile(f); setError(null); };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f && (f.type.startsWith('video/') || f.name.match(/\.(mp4|avi|mov|mkv|webm)$/i))) handleFile(f);
  };

  const handleRunAnalysis = async () => {
    if (!file) return;
    setAnalyzing(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_anon_id', `PATIENT-${Math.floor(1000 + Math.random() * 9000)}`);
    try {
      const res = await analyzeVideo(formData);
      setResult(res);
      setSelectedFrameIdx(0);
      if (res.frames.length > 0 && res.frames[0].detections.length > 0) {
        setSelectedRegionIdx(res.frames[0].detections[0].region_index);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Video analysis failed. Ensure backend service is running.');
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => { setResult(null); setFile(null); setError(null); };

  const currentFrame = result?.frames[selectedFrameIdx] ?? result?.frames[0];
  const frameDetections = currentFrame?.detections ?? [];
  const selectedDetection: Detection | undefined = frameDetections.find((d) => d.region_index === selectedRegionIdx) ?? frameDetections[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Endoscopic Video Analysis</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Frame-by-frame abnormality extraction · Neural detection · Grad-CAM visual heatmaps
          </p>
        </div>
        {result && (
          <a
            href={`/api/reports/${result.id}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
          >
            <Download className="w-4 h-4" />
            Export Clinical PDF Report
          </a>
        )}
      </div>

      {/* Upload Zone */}
      {!result && (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`panel p-10 flex flex-col items-center gap-5 border-2 border-dashed transition-colors duration-200 bg-white
            ${dragOver ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-300 hover:border-emerald-400'}`}
        >
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors shadow-2xs
            ${dragOver ? 'bg-emerald-100 text-emerald-700' : 'bg-emerald-50 text-emerald-600 border border-emerald-200'}`}>
            <Video className="w-8 h-8" />
          </div>

          <div className="text-center">
            <p className="text-base font-bold text-slate-900">
              {file ? file.name : 'Drop an endoscopic video file here'}
            </p>
            <p className="text-xs text-slate-500 mt-1">MP4, AVI, MOV, MKV, WEBM supported (max 100MB)</p>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="file"
              accept="video/*,.mp4,.avi,.mov,.mkv,.webm"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              id="video-upload"
              className="hidden"
            />
            <label htmlFor="video-upload" className="btn-ghost cursor-pointer">
              {file ? 'Change Video' : 'Browse Video Files'}
            </label>
            {file && (
              <button onClick={handleRunAnalysis} disabled={analyzing} className="btn-primary">
                {analyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
                {analyzing ? 'Extracting Frames & Analyzing…' : 'Run Video Analysis'}
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

      {/* Analysis Results */}
      {result && (
        <div className="space-y-6">
          {/* Metadata bar */}
          <div className="flex items-center justify-between px-5 py-3 rounded-xl bg-white border border-slate-200 text-xs font-mono shadow-2xs">
            <span className="text-slate-600">
              Exam <span className="text-emerald-700 font-bold">{result.id}</span>
              <span className="mx-2 text-slate-300">·</span>
              <span className="text-slate-900 font-bold">{result.frames.length} frame(s) scanned</span>
              <span className="mx-2 text-slate-300">·</span>
              <span className="text-emerald-700 font-bold">{result.detections.length} total region(s) detected</span>
            </span>
            <button onClick={reset} className="flex items-center gap-1.5 text-slate-500 hover:text-slate-900 font-medium transition">
              <X className="w-3.5 h-3.5" /> New video
            </button>
          </div>

          {/* Frame Selector Carousel */}
          {result.frames.length > 0 && (
            <div className="panel p-4 space-y-3 bg-white border-slate-200">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-2">
                <Film className="w-4 h-4 text-emerald-600" />
                <span>Extracted Keyframes ({result.frames.length})</span>
              </h3>
              <div className="flex items-center gap-3 overflow-x-auto pb-2">
                {result.frames.map((frame, idx) => (
                  <button
                    key={frame.frame_id}
                    onClick={() => {
                      setSelectedFrameIdx(idx);
                      if (frame.detections.length > 0) setSelectedRegionIdx(frame.detections[0].region_index);
                    }}
                    className={`relative shrink-0 w-32 rounded-xl overflow-hidden border transition-all text-left ${
                      selectedFrameIdx === idx
                        ? 'border-emerald-500 ring-2 ring-emerald-500/30 shadow-md'
                        : 'border-slate-200 hover:border-slate-300 opacity-80 hover:opacity-100'
                    }`}
                  >
                    <img src={frame.image_url} alt={`Frame ${frame.frame_index}`} className="w-full h-20 object-cover" />
                    <div className="p-1.5 bg-slate-900/90 text-white text-[10px] font-mono flex items-center justify-between">
                      <span>Frame #{frame.frame_index}</span>
                      <span className="text-emerald-400 font-bold">{frame.detections.length} det</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Frame Inspector */}
          {currentFrame && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-5">
                <DetectionOverlay
                  imageUrl={currentFrame.image_url}
                  detections={frameDetections}
                  selectedRegionIndex={selectedRegionIdx}
                  onSelectRegion={setSelectedRegionIdx}
                />
                <RegionSelector
                  detections={frameDetections}
                  selectedIndex={selectedRegionIdx}
                  onSelect={setSelectedRegionIdx}
                />
                {result.quality && <QualityMetricsCard metrics={result.quality} />}
              </div>

              <div className="space-y-5">
                {selectedDetection ? (
                  <>
                    <div className="panel p-5 space-y-4 border-slate-200 bg-white">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-bold text-slate-900">
                          Frame #{currentFrame.frame_index} — Region #{selectedDetection.region_index} Classification
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
                      examinationId={result.id}
                      frameId={currentFrame.frame_id}
                      detectionId={selectedDetection.id}
                    />
                  </>
                ) : (
                  <div className="panel p-8 text-center text-sm text-slate-500 border-slate-200 bg-white">
                    No abnormalities detected on Frame #{currentFrame.frame_index}.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
