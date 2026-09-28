import React, { useEffect, useState } from 'react';
import {
  FileText, Layers, AlertTriangle, Clock,
  CheckCircle2, Cpu, Activity, ArrowRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchStats, fetchExaminations, fetchModels } from '../services/api';
import { ExaminationStats, ExaminationSummary, ModelInfo } from '../types';

export const DashboardPage: React.FC = () => {
  const [stats, setStats]           = useState<ExaminationStats | null>(null);
  const [recentExams, setRecentExams] = useState<ExaminationSummary[]>([]);
  const [models, setModels]         = useState<ModelInfo[]>([]);
  const [loading, setLoading]       = useState(true);

  useEffect(() => {
    Promise.all([fetchStats(), fetchExaminations(), fetchModels()])
      .then(([s, e, m]) => { setStats(s); setRecentExams(e); setModels(m); })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const activeModel = models[0] ?? { name: 'EndoAI Detector (YOLOv8)', version: '0.1.0-demo', status: 'DEMO' };

  return (
    <div className="space-y-6">

      {/* ── Page header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Clinical Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">Endoscopic imaging overview & decision-support summary</p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/image-analysis" className="btn-primary">
            <Activity className="w-4 h-4" />
            New Analysis
          </Link>
          <Link to="/live" className="btn-ghost">
            Live Stream
          </Link>
        </div>
      </div>

      {/* ── Model status bar ── */}
      <div className="panel px-5 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 border-slate-200">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center">
            <Cpu className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-slate-900">{activeModel.name}</span>
              <span className="badge badge-warn">{activeModel.status}</span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 font-medium">
              v{activeModel.version} · Detection (YOLO) + Softmax Classification + Grad-CAM
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6 text-xs font-mono">
          <div>
            <p className="text-slate-400 mb-0.5">System</p>
            <div className="flex items-center gap-1.5 text-emerald-700 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              Operational
            </div>
          </div>
          <div>
            <p className="text-slate-400 mb-0.5">Target Classes</p>
            <p className="text-slate-800 font-bold">6 Lesion Types</p>
          </div>
        </div>
      </div>

      {/* ── Stat tiles ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Examinations',
            value: stats?.total_examinations ?? 0,
            icon: FileText,
            iconColor: 'text-emerald-600',
            sub: 'Image & video sessions',
          },
          {
            label: 'Frames Processed',
            value: stats?.frames_processed ?? 0,
            icon: Layers,
            iconColor: 'text-emerald-600',
            sub: 'Optical frames captured',
          },
          {
            label: 'Abnormal Regions',
            value: stats?.abnormal_regions_detected ?? 0,
            icon: Activity,
            iconColor: 'text-rose-600',
            sub: 'Polyps, ulcers, lesions',
          },
          {
            label: 'Avg Latency',
            value: stats?.avg_processing_time_ms ? `${stats.avg_processing_time_ms} ms` : '—',
            icon: Clock,
            iconColor: 'text-emerald-600',
            sub: 'Per frame end-to-end',
          },
        ].map((tile) => {
          const Icon = tile.icon;
          return (
            <div key={tile.label} className="stat-tile">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500 font-semibold">{tile.label}</span>
                <div className="w-7 h-7 rounded-lg bg-emerald-50 flex items-center justify-center">
                  <Icon className={`w-4 h-4 ${tile.iconColor}`} />
                </div>
              </div>
              <p className="text-2xl font-bold font-mono text-slate-900 leading-none">
                {loading ? <span className="text-slate-300">—</span> : tile.value}
              </p>
              <p className="text-2xs text-slate-500 font-medium">{tile.sub}</p>
            </div>
          );
        })}
      </div>

      {/* ── Alert tiles ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card p-4 border-l-4 border-l-amber-500 bg-amber-50/40 flex items-center justify-between gap-4 border-slate-200">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
            <div>
              <p className="text-sm font-bold text-amber-950">Low Confidence Flags</p>
              <p className="text-xs text-amber-800 mt-0.5">Predictions below threshold — human review required</p>
            </div>
          </div>
          <span className="text-2xl font-bold font-mono text-amber-700 shrink-0">
            {stats?.low_confidence_predictions ?? 0}
          </span>
        </div>

        <div className="card p-4 border-l-4 border-l-emerald-600 bg-emerald-50/40 flex items-center justify-between gap-4 border-slate-200">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <div>
              <p className="text-sm font-bold text-emerald-950">Pending Reviews</p>
              <p className="text-xs text-emerald-800 mt-0.5">Awaiting clinician acceptance or rejection</p>
            </div>
          </div>
          <span className="text-2xl font-bold font-mono text-emerald-700 shrink-0">
            {stats?.pending_reviews ?? 0}
          </span>
        </div>
      </div>

      {/* ── Recent examinations ── */}
      <div className="panel border-slate-200">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <h2 className="text-sm font-bold text-slate-900">Recent Examinations</h2>
          <Link to="/history" className="text-xs text-emerald-700 hover:text-emerald-800 font-semibold flex items-center gap-1 transition">
            View all <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentExams.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <p className="text-sm text-slate-600 font-medium">No examinations yet.</p>
            <p className="text-xs text-slate-400 mt-1">Upload an endoscopic image or connect a live stream to begin.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/80 text-slate-500 font-bold uppercase tracking-wider text-2xs">
                  <th className="px-5 py-3 text-left">Exam ID</th>
                  <th className="px-5 py-3 text-left">Patient</th>
                  <th className="px-5 py-3 text-left">Type</th>
                  <th className="px-5 py-3 text-right">Frames</th>
                  <th className="px-5 py-3 text-right">Detections</th>
                  <th className="px-5 py-3 text-left">Created</th>
                  <th className="px-5 py-3 text-right"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentExams.slice(0, 6).map((exam) => (
                  <tr key={exam.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-5 py-3 font-mono font-bold text-emerald-700">{exam.id.substring(0, 8)}&hellip;</td>
                    <td className="px-5 py-3 text-slate-700 font-medium">{exam.patient_anon_id || 'ANON'}</td>
                    <td className="px-5 py-3">
                      <span className="badge badge-muted">{exam.input_type}</span>
                    </td>
                    <td className="px-5 py-3 text-right font-mono text-slate-700 font-medium">{exam.frame_count}</td>
                    <td className="px-5 py-3 text-right font-mono text-slate-700 font-medium">{exam.total_detections}</td>
                    <td className="px-5 py-3 text-slate-500">{new Date(exam.created_at).toLocaleString()}</td>
                    <td className="px-5 py-3 text-right">
                      <Link to={`/detections?exam=${exam.id}`} className="text-emerald-700 hover:text-emerald-900 font-bold transition">
                        Inspect →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
