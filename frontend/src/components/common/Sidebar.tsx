import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Radio, Image as ImageIcon, Video,
  Target, Eye, FileSpreadsheet, History, Cpu, Settings,
} from 'lucide-react';

const groups = [
  {
    label: 'Analysis',
    items: [
      { name: 'Dashboard',       path: '/',               icon: LayoutDashboard },
      { name: 'Image Analysis',  path: '/image-analysis', icon: ImageIcon },
      { name: 'Video Analysis',  path: '/video-analysis', icon: Video },
      { name: 'Live Stream',     path: '/live',           icon: Radio },
    ],
  },
  {
    label: 'Results',
    items: [
      { name: 'Detections',      path: '/detections',     icon: Target },
      { name: 'Explainability',  path: '/explainability', icon: Eye },
      { name: 'Reports',         path: '/reports',        icon: FileSpreadsheet },
      { name: 'History',         path: '/history',        icon: History },
    ],
  },
  {
    label: 'System',
    items: [
      { name: 'Model Info',      path: '/model-info',     icon: Cpu },
      { name: 'Settings',        path: '/settings',       icon: Settings },
    ],
  },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-56 border-r border-slate-200 bg-white hidden md:flex flex-col min-h-[calc(100vh-3.5rem)]">
      <nav className="flex-1 py-4 px-3 space-y-5 overflow-y-auto">
        {groups.map((group) => (
          <div key={group.label}>
            <p className="section-label">{group.label}</p>
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/'}
                    className={({ isActive }) => isActive ? 'nav-link-active' : 'nav-link'}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="p-3 border-t border-slate-200">
        <div className="px-3 py-2.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80">
          <p className="text-2xs font-bold text-emerald-900 mb-0.5">Research Prototype</p>
          <p className="text-2xs text-emerald-700 leading-relaxed">
            Not for clinical use. Human review required for all outputs.
          </p>
        </div>
      </div>
    </aside>
  );
};
