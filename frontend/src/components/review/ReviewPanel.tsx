import React, { useState } from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Save, UserCheck } from 'lucide-react';
import { submitReview } from '../../services/api';

interface Props {
  examinationId: string;
  frameId: string;
  detectionId?: string;
  onReviewSubmitted?: () => void;
}

export const ReviewPanel: React.FC<Props> = ({
  examinationId,
  frameId,
  detectionId,
  onReviewSubmitted,
}) => {
  const [status, setStatus] = useState<'ACCEPTED' | 'REJECTED' | 'NEEDS_REVIEW'>('ACCEPTED');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [submittedStatus, setSubmittedStatus] = useState<string | null>(null);

  const handleSaveReview = async () => {
    setSaving(true);
    try {
      await submitReview({
        examination_id: examinationId,
        frame_id: frameId,
        detection_id: detectionId,
        review_status: status,
        reviewer_notes: notes,
        reviewer_id: 'DR-CLINICIAN-01',
      });
      setSubmittedStatus(status);
      if (onReviewSubmitted) onReviewSubmitted();
    } catch (err) {
      console.error('Save review failed:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="glass-panel p-5 space-y-4 border-l-4 border-l-emerald-600">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <UserCheck className="w-4 h-4 text-emerald-600" />
          <span>Clinician Review & Acceptance Workflow</span>
        </h3>
        {submittedStatus && (
          <span className="px-2.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono text-xs font-semibold">
            SAVED: {submittedStatus}
          </span>
        )}
      </div>

      <div className="space-y-3">
        <label className="text-xs text-slate-600 font-medium block">Select Decision Status:</label>
        <div className="grid grid-cols-3 gap-2 text-xs font-semibold font-mono">
          <button
            type="button"
            onClick={() => setStatus('ACCEPTED')}
            className={`p-2.5 rounded-xl border flex items-center justify-center space-x-1.5 transition ${
              status === 'ACCEPTED'
                ? 'bg-emerald-50 border-emerald-500 text-emerald-800 shadow-xs'
                : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Accept AI</span>
          </button>

          <button
            type="button"
            onClick={() => setStatus('REJECTED')}
            className={`p-2.5 rounded-xl border flex items-center justify-center space-x-1.5 transition ${
              status === 'REJECTED'
                ? 'bg-rose-50 border-rose-500 text-rose-800 shadow-xs'
                : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>Reject AI</span>
          </button>

          <button
            type="button"
            onClick={() => setStatus('NEEDS_REVIEW')}
            className={`p-2.5 rounded-xl border flex items-center justify-center space-x-1.5 transition ${
              status === 'NEEDS_REVIEW'
                ? 'bg-amber-50 border-amber-500 text-amber-800 shadow-xs'
                : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>Further Review</span>
          </button>
        </div>

        <div>
          <label className="text-xs text-slate-600 font-medium block mb-1">Clinician Notes & Observations:</label>
          <textarea
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Enter clinical notes, mucosal observations, or diagnostic recommendations..."
            className="w-full bg-white border border-slate-200 rounded-xl p-3 text-xs text-slate-900 focus:outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-500/30 font-sans"
          ></textarea>
        </div>

        <button
          type="button"
          onClick={handleSaveReview}
          disabled={saving}
          className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs transition flex items-center justify-center space-x-2 shadow-emerald"
        >
          <Save className="w-3.5 h-3.5" />
          <span>{saving ? 'Persisting Decision...' : 'Save Review Decision'}</span>
        </button>
      </div>
    </div>
  );
};
