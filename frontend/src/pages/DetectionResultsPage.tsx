import React, { useEffect, useState } from 'react';
import { Target, Download, Activity, RefreshCw } from 'lucide-react';
import { useSearchParams, Link } from 'react-router-dom';
import { fetchExaminations, fetchExaminationReport } from '../services/api';
import { ExaminationReport, Detection } from '../types';
import { DetectionOverlay } from '../components/analysis/DetectionOverlay';
import { RegionSelector } from '../components/analysis/RegionSelector';
import { ReviewPanel } from '../components/review/ReviewPanel';

export const DetectionResultsPage: React.FC = () => {
  const [searchParams]                          = useSearchParams();
  const examIdParam                             = searchParams.get('exam');
  const [report, setReport]                     = useState<ExaminationReport | null>(null);
  const [loading, setLoading]                   = useState(true);
  const [selectedFrameIdx, setSelectedFrameIdx] = useState<number>(0);
  const [selectedRegionIdx, setSelectedRegionIdx] = useState<number>(1);

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
          if (rep.frames.length > 0 && rep.frames[0].detections.length > 0) {
            setSelectedRegionIdx(rep.frames[0].detections[0].region_index);
          }
        }
      } catch (err) {
        console.error('Failed loading detection results:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [examIdParam]);

  const currentFrame = report?.frames[selectedFrameIdx] ?? report?.frames[0];
  const frameDetections = currentFrame?.detections ?? [];
  const selectedDetection: Detection | undefined = frameDetections.find((d) => d.region_index === selectedRegionIdx) ?? frameDetections[0];

  if (loading) {
    return (
      <div className="panel p-12 text-center text-slate-500 flex flex-col items-center justify-center space-y-3 bg-white border-slate-200">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
        <p className="text-sm font-medium">Loading detection results…</p>
      </div>
    );
  }

  if (!report || report.detections.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Detection Results & Region Inspection</h1>
          <p className="text-sm text-slate-500 mt-1">
            Multi-region bounding box extraction, confidence assessment, and review logs
          </p>
        </div>

        <div className="glass-panel p-10 text-center bg-white border-slate-200 space-y-4">
          <Target className="w-12 h-12 text-emerald-600/60 mx-auto" />
          <div>
            <h3 className="font-bold text-slate-900 text-base">No Detections Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              No examination records found or current examination contains no abnormal detections.
            </p>
          </div>
          <Link to="/image-analysis" className="btn-primary inline-flex">
            <Activity className="w-4 h-4" />
            Run New Analysis
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Detection Results & Region Inspection</h1>
          <p className="text-sm text-slate-500 mt-1">
            Exam ID: <span className="font-mono text-emerald-700 font-bold">{report.id}</span> · Patient ID: <span className="font-mono font-bold text-slate-800">{report.patient_anon_id}</span>
          </p>
        </div>
        <a
          href={`/api/reports/${report.id}/pdf`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary"
        >
          <Download className="w-4 h-4" />
          Export Clinical PDF Report
        </a>
      </div>

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
          </div>

          <div className="space-y-5">
            {selectedDetection ? (
              <>
                <div className="panel p-5 space-y-4 border-slate-200 bg-white">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-900">
                      Region #{selectedDetection.region_index} — Classification Details
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

                <ReviewPanel
                  examinationId={report.id}
                  frameId={currentFrame.frame_id}
                  detectionId={selectedDetection.id}
                />
              </>
            ) : (
              <div className="panel p-8 text-center text-sm text-slate-500 border-slate-200 bg-white">
                Select a region on the frame overlay to view detailed findings.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
