import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

export default function ScoreGauge({ score = 100, scannedResources = 0 }) {
  const getScoreColor = (val) => {
    if (val >= 85) return 'text-emerald-400 stroke-emerald-500';
    if (val >= 60) return 'text-amber-400 stroke-amber-500';
    return 'text-rose-500 stroke-rose-500';
  };

  const getScoreBg = (val) => {
    if (val >= 85) return 'bg-emerald-500/10 border-emerald-500/30';
    if (val >= 60) return 'bg-amber-500/10 border-amber-500/30';
    return 'bg-rose-500/10 border-rose-500/30';
  };

  const getGrade = (val) => {
    if (val >= 90) return 'Grade A (Excellent)';
    if (val >= 75) return 'Grade B (Good)';
    if (val >= 60) return 'Grade C (Moderate Risk)';
    if (val >= 40) return 'Grade D (High Risk)';
    return 'Grade F (Critical Risk)';
  };

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`rounded-2xl p-6 border ${getScoreBg(score)} backdrop-blur-sm flex flex-col items-center justify-center text-center shadow-lg transition-all`}>
      <div className="relative flex items-center justify-center w-36 h-36">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            className="stroke-slate-800"
            strokeWidth="8"
            fill="transparent"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            className={`${getScoreColor(score)} transition-all duration-1000 ease-out`}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-3xl font-bold tracking-tight text-white">{score}</span>
          <span className="text-xs uppercase tracking-wider text-slate-400">out of 100</span>
        </div>
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-semibold tracking-wide text-slate-200">Security Posture</h3>
        <p className={`text-xs font-medium mt-0.5 ${getScoreColor(score)}`}>
          {getGrade(score)}
        </p>
        <p className="text-[11px] text-slate-400 mt-2">
          Scanned <span className="font-semibold text-slate-200">{scannedResources}</span> cloud resources
        </p>
      </div>
    </div>
  );
}
