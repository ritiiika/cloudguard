import React from 'react';
import { X, ShieldAlert, CheckCircle2, Terminal, ExternalLink } from 'lucide-react';

export default function RemediationModal({ finding, onClose }) {
  if (!finding) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <span
            className={`px-2.5 py-1 rounded-full text-xs font-bold ${
              finding.severity === 'CRITICAL'
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                : finding.severity === 'HIGH'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'bg-yellow-400/20 text-yellow-300 border border-yellow-400/30'
            }`}
          >
            {finding.severity}
          </span>
          <span className="text-xs font-mono text-slate-400">{finding.rule_id}</span>
        </div>

        <h2 className="text-lg font-bold text-white mt-3">{finding.title}</h2>

        <div className="mt-4 space-y-4 text-xs">
          <div>
            <h4 className="text-slate-400 font-semibold uppercase tracking-wider mb-1">Affected Resource</h4>
            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 font-mono text-emerald-400 select-all">
              {finding.resource_id}
            </div>
          </div>

          <div>
            <h4 className="text-slate-400 font-semibold uppercase tracking-wider mb-1">Description & Threat</h4>
            <p className="text-slate-300 bg-slate-950/50 p-3 rounded-lg border border-slate-800 leading-relaxed">
              {finding.description}
            </p>
          </div>

          <div>
            <h4 className="text-emerald-400 font-semibold uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <Terminal className="w-4 h-4" /> Recommended Remediation
            </h4>
            <div className="bg-slate-950 p-3 rounded-lg border border-emerald-500/30 text-slate-200 leading-relaxed font-mono">
              {finding.remediation}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
