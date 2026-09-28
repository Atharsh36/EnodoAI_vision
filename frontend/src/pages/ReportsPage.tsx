import React, { useEffect, useState } from 'react';
import { FileSpreadsheet, Download, FileText, ArrowRight, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchExaminations, fetchExaminationReport } from '../services/api';
import { ExaminationSummary, ExaminationReport } from '../types';

export const ReportsPage: React.FC = () => {
  const [exams, setExams]         = useState<ExaminationSummary[]>([]);
  const [loading, setLoading]     = useState(true);
  const [selectedExamId, setSelectedExamId] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<ExaminationReport | null>(null);

  useEffect(() => {
    async function loadExams() {
      setLoading(true);
      try {
        const data = await fetchExaminations();
        setExams(data);
        if (data.length > 0) {
          setSelectedExamId(data[0].id);
          const rep = await fetchExaminationReport(data[0].id);
          setSelectedReport(rep);
        }
      } catch (err) {
        console.error('Failed fetching reports list:', err);
      } finally {
        setLoading(false);
      }
    }
    loadExams();
  }, []);

  const handleSelectExam = async (id: string) => {
    setSelectedExamId(id);
    try {
      const rep = await fetchExaminationReport(id);
      setSelectedReport(rep);
    } catch (err) {
      console.error('Failed loading report preview:', err);
    }
  };

  if (loading) {
    return (
      <div className="panel p-12 text-center text-slate-500 flex flex-col items-center justify-center space-y-3 bg-white border-slate-200">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
        <p className="text-sm font-medium">Loading clinical examination reports…</p>
      </div>
    );
  }

  if (exams.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Structured Examination Reports</h1>
          <p className="text-sm text-slate-500 mt-1">
            Export clinical decision support reports in JSON and formatted PDF formats
          </p>
        </div>

        <div className="glass-panel p-10 text-center bg-white border-slate-200 space-y-4">
          <FileSpreadsheet className="w-12 h-12 text-emerald-600/60 mx-auto" />
          <div>
            <h3 className="font-bold text-slate-900 text-base">No Reports Generated Yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              Complete an image or video analysis session to generate exportable PDF and JSON reports.
            </p>
          </div>
          <Link to="/image-analysis" className="btn-primary inline-flex">
            Start Image Analysis
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
          <h1 className="text-2xl font-bold text-slate-900">Structured Examination Reports</h1>
          <p className="text-sm text-slate-500 mt-1">
            Export clinical decision support reports in JSON and formatted PDF formats
          </p>
        </div>
        {selectedExamId && (
          <a
            href={`/api/reports/${selectedExamId}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
          >
            <Download className="w-4 h-4" />
            Export Selected PDF
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports Registry Sidebar */}
        <div className="panel bg-white border-slate-200 overflow-hidden">
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center space-x-2">
              <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
              <span>Report Registry ({exams.length})</span>
            </h3>
          </div>
          <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
            {exams.map((exam) => (
              <button
                key={exam.id}
                onClick={() => handleSelectExam(exam.id)}
                className={`w-full p-4 text-left transition-colors flex items-center justify-between ${
                  selectedExamId === exam.id ? 'bg-emerald-50/80 border-l-4 border-l-emerald-600' : 'hover:bg-slate-50'
                }`}
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-xs text-slate-900">{exam.id.substring(0, 8)}&hellip;</span>
                    <span className="badge badge-muted text-[10px]">{exam.input_type}</span>
                  </div>
                  <p className="text-2xs text-slate-500 mt-1">
                    {new Date(exam.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-emerald-700 block">
                    {exam.total_detections} region(s)
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {exam.frame_count} frame(s)
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Selected Report Interactive Preview */}
        <div className="lg:col-span-2 space-y-5">
          {selectedReport ? (
            <div className="panel p-6 bg-white border-slate-200 space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-lg text-slate-900">Clinical Report Preview</h3>
                    <span className="badge badge-emerald">{selectedReport.input_type}</span>
                  </div>
                  <p className="text-xs font-mono text-slate-500 mt-1">
                    Exam ID: <span className="text-emerald-700 font-bold">{selectedReport.id}</span> · Patient: <span className="text-slate-800 font-bold">{selectedReport.patient_anon_id}</span>
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href={`/api/reports/${selectedReport.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-ghost text-xs"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    JSON Payload
                  </a>
                  <a
                    href={`/api/reports/${selectedReport.id}/pdf`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-xs"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download PDF Report
                  </a>
                </div>
              </div>

              {/* Overview Cards */}
              <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">Total Detections</span>
                  <strong className="text-emerald-700 text-lg">{selectedReport.detections.length} region(s)</strong>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">Optical Quality Score</span>
                  <strong className="text-slate-900 text-lg">{selectedReport.quality?.overall_quality || 'GOOD'}</strong>
                </div>
              </div>

              {/* Detected Regions Table */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Detected Abnormal Regions</h4>
                <div className="overflow-x-auto border border-slate-200 rounded-xl">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase text-[10px]">
                        <th className="px-4 py-2.5 text-left">Region</th>
                        <th className="px-4 py-2.5 text-left">Predicted Category</th>
                        <th className="px-4 py-2.5 text-right">Confidence</th>
                        <th className="px-4 py-2.5 text-left">Confidence Rating</th>
                        <th className="px-4 py-2.5 text-right">Review Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {selectedReport.detections.map((det) => (
                        <tr key={det.id || det.region_index} className="hover:bg-slate-50/70">
                          <td className="px-4 py-2.5 font-mono font-bold text-slate-900">Region #{det.region_index}</td>
                          <td className="px-4 py-2.5 font-semibold text-emerald-800">{det.prediction?.predicted_class || det.class_name}</td>
                          <td className="px-4 py-2.5 text-right font-mono font-bold text-emerald-700">
                            {Math.round((det.prediction?.class_confidence || det.confidence) * 100)}%
                          </td>
                          <td className="px-4 py-2.5 font-mono">
                            <span className="badge badge-emerald">{det.prediction?.confidence_level || 'HIGH'}</span>
                          </td>
                          <td className="px-4 py-2.5 text-right">
                            <span className="badge badge-muted">{det.review?.status || 'PENDING'}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* View details CTA */}
              <div className="pt-2 flex justify-end">
                <Link to={`/detections?exam=${selectedReport.id}`} className="text-emerald-700 hover:text-emerald-900 font-bold text-xs flex items-center gap-1">
                  Inspect in Region Inspector <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ) : (
            <div className="panel p-8 text-center text-slate-500 bg-white border-slate-200">
              Select a report from the registry to view clinical details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
