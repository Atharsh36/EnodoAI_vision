import React, { useEffect, useState } from 'react';
import { History, Search, Download, ArrowRight, RefreshCw, FileText, Layers, Target } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchExaminations } from '../services/api';
import { ExaminationSummary } from '../types';

export const HistoryPage: React.FC = () => {
  const [exams, setExams]       = useState<ExaminationSummary[]>([]);
  const [loading, setLoading]   = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('ALL');

  useEffect(() => {
    async function loadHistory() {
      setLoading(true);
      try {
        const data = await fetchExaminations();
        setExams(data);
      } catch (err) {
        console.error('Failed loading examination history:', err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  const filteredExams = exams.filter((e) => {
    const matchSearch = e.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        (e.patient_anon_id && e.patient_anon_id.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchType = filterType === 'ALL' || e.input_type === filterType;
    return matchSearch && matchType;
  });

  const totalFrames = exams.reduce((acc, curr) => acc + curr.frame_count, 0);
  const totalDets = exams.reduce((acc, curr) => acc + curr.total_detections, 0);

  if (loading) {
    return (
      <div className="panel p-12 text-center text-slate-500 flex flex-col items-center justify-center space-y-3 bg-white border-slate-200">
        <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
        <p className="text-sm font-medium">Loading examination audit trail…</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Examination History & Audit Trail</h1>
        <p className="text-sm text-slate-500 mt-1">
          Historical record of endoscopic examinations, detections, and clinician review logs
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="stat-tile">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Total Sessions</span>
            <FileText className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold font-mono text-slate-900">{exams.length}</p>
          <span className="text-2xs text-slate-400">Completed examinations</span>
        </div>

        <div className="stat-tile">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Total Scanned Frames</span>
            <Layers className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold font-mono text-slate-900">{totalFrames}</p>
          <span className="text-2xs text-slate-400">Optical frames analyzed</span>
        </div>

        <div className="stat-tile">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Total Abnormality Detections</span>
            <Target className="w-4 h-4 text-rose-600" />
          </div>
          <p className="text-2xl font-bold font-mono text-slate-900">{totalDets}</p>
          <span className="text-2xs text-slate-400">Extracted ROI regions</span>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="panel p-4 bg-white border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by Patient ID or Exam ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-600"
          />
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="text-slate-500 font-medium">Type Filter:</span>
          {['ALL', 'IMAGE', 'VIDEO', 'LIVE'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-2.5 py-1 rounded-md transition font-semibold ${
                filterType === type ? 'bg-emerald-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:text-slate-900'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* History Table */}
      <div className="panel bg-white border-slate-200 overflow-hidden">
        {filteredExams.length === 0 ? (
          <div className="p-10 text-center text-slate-500">
            <History className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-bold text-slate-800">No matching examination records found.</p>
            <p className="text-xs text-slate-400 mt-1">Try adjusting your search query or type filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-2xs">
                  <th className="px-5 py-3 text-left">Examination ID</th>
                  <th className="px-5 py-3 text-left">Patient ID</th>
                  <th className="px-5 py-3 text-left">Input Type</th>
                  <th className="px-5 py-3 text-right">Frames</th>
                  <th className="px-5 py-3 text-right">Detections</th>
                  <th className="px-5 py-3 text-left">Created Timestamp</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredExams.map((exam) => (
                  <tr key={exam.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-5 py-3.5 font-mono font-bold text-emerald-700">{exam.id}</td>
                    <td className="px-5 py-3.5 text-slate-800 font-semibold">{exam.patient_anon_id || 'ANON-PATIENT'}</td>
                    <td className="px-5 py-3.5">
                      <span className="badge badge-emerald">{exam.input_type}</span>
                    </td>
                    <td className="px-5 py-3.5 text-right font-mono text-slate-700 font-bold">{exam.frame_count}</td>
                    <td className="px-5 py-3.5 text-right font-mono text-emerald-700 font-bold">{exam.total_detections}</td>
                    <td className="px-5 py-3.5 text-slate-500">{new Date(exam.created_at).toLocaleString()}</td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-3 font-medium">
                        <Link to={`/detections?exam=${exam.id}`} className="text-emerald-700 hover:text-emerald-900 font-bold flex items-center gap-1 transition">
                          Inspect <ArrowRight className="w-3 h-3" />
                        </Link>
                        <a
                          href={`/api/reports/${exam.id}/pdf`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-slate-600 hover:text-slate-900 flex items-center gap-1 transition"
                        >
                          <Download className="w-3 h-3 text-emerald-600" /> PDF
                        </a>
                      </div>
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
