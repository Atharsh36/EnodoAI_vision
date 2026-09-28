import React, { useEffect, useState } from 'react';
import { Cpu } from 'lucide-react';
import { fetchModels } from '../services/api';
import { ModelInfo } from '../types';

export const ModelInfoPage: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);

  useEffect(() => {
    fetchModels().then(setModels).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Model Registry & Architecture Info</h1>
        <p className="text-sm text-slate-500 mt-1">
          Loaded neural network models, versioning, class distribution, and training configuration
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {models.map((model, idx) => (
          <div key={idx} className="glass-panel p-6 space-y-4 bg-white border-slate-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900">{model.name}</h3>
                  <p className="text-xs text-slate-500">Type: {model.type}</p>
                </div>
              </div>
              <span className="badge badge-warn">
                {model.status}
              </span>
            </div>

            <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-200">
              {model.description}
            </p>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between text-slate-500">
                <span>Version:</span>
                <span className="text-slate-900 font-bold">{model.version}</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Input Dimensions:</span>
                <span className="text-slate-900 font-bold">{model.input_size.join(' × ')} px</span>
              </div>
            </div>

            <div className="border-t border-slate-200 pt-3">
              <h4 className="text-xs font-bold text-slate-700 mb-2">Supported Classification Classes:</h4>
              <div className="flex flex-wrap gap-1.5">
                {model.classes.map((cls, cIdx) => (
                  <span
                    key={cIdx}
                    className="px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 font-mono text-[11px] font-semibold"
                  >
                    {cls}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
