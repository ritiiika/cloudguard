import React from 'react';
import { AlertOctagon, AlertTriangle, AlertCircle, Info } from 'lucide-react';

export default function SeverityCards({ counts = {}, selectedSeverity, onSelectSeverity }) {
  const cards = [
    {
      id: 'CRITICAL',
      label: 'Critical',
      count: counts.critical || 0,
      icon: AlertOctagon,
      textColor: 'text-rose-500',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/30',
      activeRing: 'ring-2 ring-rose-500',
    },
    {
      id: 'HIGH',
      label: 'High',
      count: counts.high || 0,
      icon: AlertTriangle,
      textColor: 'text-amber-500',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
      activeRing: 'ring-2 ring-amber-500',
    },
    {
      id: 'MEDIUM',
      label: 'Medium',
      count: counts.medium || 0,
      icon: AlertCircle,
      textColor: 'text-yellow-400',
      bgColor: 'bg-yellow-400/10',
      borderColor: 'border-yellow-400/30',
      activeRing: 'ring-2 ring-yellow-400',
    },
    {
      id: 'LOW',
      label: 'Low',
      count: counts.low || 0,
      icon: Info,
      textColor: 'text-blue-400',
      bgColor: 'bg-blue-400/10',
      borderColor: 'border-blue-400/30',
      activeRing: 'ring-2 ring-blue-400',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const isSelected = selectedSeverity === card.id;

        return (
          <button
            key={card.id}
            onClick={() => onSelectSeverity(isSelected ? null : card.id)}
            className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
              card.bgColor
            } ${card.borderColor} ${
              isSelected ? `${card.activeRing} shadow-lg scale-[1.02]` : 'hover:border-slate-600 opacity-90 hover:opacity-100'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                {card.label}
              </span>
              <Icon className={`w-4 h-4 ${card.textColor}`} />
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className={`text-2xl font-bold ${card.textColor}`}>{card.count}</span>
              <span className="text-xs text-slate-400">findings</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
