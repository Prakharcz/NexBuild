import React from 'react';
import { ShieldAlert, ShieldCheck, Shield, AlertTriangle } from 'lucide-react';

export default function RiskGauge({ score = 50, riskLevel = 'Moderate Risk', factors = [] }) {
  // Score interpretation
  let color = 'text-amber-400';
  let strokeColor = '#f59e0b';
  let bgColor = 'bg-amber-500/10 border-amber-500/20';
  let Icon = Shield;

  if (score >= 80) {
    color = 'text-emerald-400';
    strokeColor = '#10b981';
    bgColor = 'bg-emerald-500/10 border-emerald-500/20';
    Icon = ShieldCheck;
  } else if (score >= 60) {
    color = 'text-blue-400';
    strokeColor = '#3b82f6';
    bgColor = 'bg-blue-500/10 border-blue-500/20';
    Icon = ShieldCheck;
  } else if (score >= 40) {
    color = 'text-amber-400';
    strokeColor = '#f59e0b';
    bgColor = 'bg-amber-500/10 border-amber-500/20';
    Icon = AlertTriangle;
  } else {
    color = 'text-rose-400';
    strokeColor = '#f43f5e';
    bgColor = 'bg-rose-500/10 border-rose-500/20';
    Icon = ShieldAlert;
  }

  // Calculate svg arc
  const radius = 58;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col items-center text-center">
      <div className="flex items-center justify-between w-full mb-3">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Financial Risk Score</span>
        <span className={`text-xs px-2.5 py-1 rounded-full font-medium border ${bgColor} ${color}`}>
          {riskLevel}
        </span>
      </div>

      <div className="relative my-2 w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 140 140">
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke="#1e293b"
            strokeWidth="10"
            fill="transparent"
          />
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke={strokeColor}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Icon className={`w-6 h-6 mb-1 ${color}`} />
          <span className="text-3xl font-extrabold text-white">{score}</span>
          <span className="text-[10px] text-slate-400 font-medium">/ 100</span>
        </div>
      </div>

      <div className="w-full space-y-2.5 mt-3 pt-3 border-t border-slate-800">
        {factors.map((f, i) => (
          <div key={i} className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{f.name}</span>
            <span className="font-medium text-slate-200">{f.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
