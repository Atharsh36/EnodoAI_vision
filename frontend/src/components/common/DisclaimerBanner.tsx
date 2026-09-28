import React, { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';

export const DisclaimerBanner: React.FC = () => {
  const [dismissed, setDismissed] = useState(false);
  if (dismissed) return null;

  return (
    <div className="bg-amber-50/90 border-b border-amber-200 px-6 py-2 flex items-center justify-between gap-4 shadow-2xs">
      <div className="flex items-center gap-2.5 text-xs text-amber-800">
        <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-600" />
        <span>
          <strong className="font-semibold text-amber-950">Research prototype only.</strong>{' '}
          AI outputs are not a substitute for professional medical judgment. Not validated for clinical use.
        </span>
      </div>
      <button onClick={() => setDismissed(true)} className="text-amber-600 hover:text-amber-900 transition shrink-0">
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
