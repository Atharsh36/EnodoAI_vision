import React, { useEffect, useState } from 'react';
import { Stethoscope, Cpu, Database } from 'lucide-react';
import { fetchHealth } from '../../services/api';
import { SystemHealth } from '../../types';

export const Navbar: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => null);
  }, []);

  const isHealthy = health?.status === 'healthy';

  return (
    <header className="h-14 border-b border-slate-200 bg-white/95 backdrop-blur-sm px-6 flex items-center justify-between sticky top-0 z-40 shadow-xs">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-emerald-600 shadow-md shadow-emerald-600/20 flex items-center justify-center">
          <Stethoscope className="w-4.5 h-4.5 text-white" />
        </div>
        <div className="flex items-center gap-2.5">
          <span className="font-bold text-slate-900 text-base tracking-tight">EndoAI Vision</span>
          <span className="badge badge-warn">Demo</span>
        </div>
      </div>

      {/* Status row */}
      <div className="flex items-center gap-5 text-xs font-mono text-slate-500">
        <div className="hidden md:flex items-center gap-1.5 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200/80 text-emerald-800">
          <Cpu className="w-3.5 h-3.5 text-emerald-600" />
          <span className="font-medium">YOLOv8 + ResNet50</span>
        </div>

        <div className="hidden sm:flex items-center gap-1.5">
          <Database className={`w-3.5 h-3.5 ${health?.database_connected ? 'text-emerald-600' : 'text-rose-500'}`} />
          <span className={health?.database_connected ? 'text-emerald-700 font-medium' : 'text-rose-600 font-medium'}>
            {health?.database_connected ? 'DB Connected' : 'DB Offline'}
          </span>
        </div>

        <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200">
          <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
          <span className="text-slate-700 font-medium capitalize">{health?.status ?? 'Connecting'}</span>
        </div>
      </div>
    </header>
  );
};
