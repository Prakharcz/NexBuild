import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  UploadCloud,
  PieChart,
  Target,
  Sparkles,
  History,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/transactions', label: 'Transactions', icon: Receipt },
  { to: '/upload', label: 'Upload CSV', icon: UploadCloud },
  { to: '/analytics', label: 'Analytics & Forecast', icon: PieChart },
  { to: '/goals', label: 'Savings Goals', icon: Target },
  { to: '/recommendations', label: 'AI Risk Advisory', icon: Sparkles },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900/60 border-r border-slate-800 flex flex-col justify-between p-4 hidden md:flex shrink-0">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm'
                    : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800/80 text-xs text-slate-400 space-y-1">
        <p className="font-medium text-slate-300">Open-Source Engine</p>
        <p className="text-[11px]">100% Free & Self-Hosted. Zero telemetry or external API keys.</p>
      </div>
    </aside>
  );
}
