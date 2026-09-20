import React, { useState } from 'react';
import { Search, ShieldAlert, Wrench, Database, HardDrive, KeyRound, Server } from 'lucide-react';

export default function FindingsTable({ findings = [], onSelectFinding }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredFindings = findings.filter((f) => {
    const term = searchTerm.toLowerCase();
    return (
      f.title?.toLowerCase().includes(term) ||
      f.resource_id?.toLowerCase().includes(term) ||
      f.rule_id?.toLowerCase().includes(term) ||
      f.resource_type?.toLowerCase().includes(term)
    );
  });

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-500/10 text-rose-400 border border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border border-amber-500/30';
      case 'MEDIUM':
        return 'bg-yellow-400/10 text-yellow-300 border border-yellow-400/30';
      case 'LOW':
        return 'bg-blue-400/10 text-blue-300 border border-blue-400/30';
      default:
        return 'bg-slate-700 text-slate-300';
    }
  };

  const getResourceIcon = (type) => {
    switch (type) {
      case 's3_bucket':
        return <HardDrive className="w-3.5 h-3.5 text-sky-400 inline mr-1.5" />;
      case 'iam_root':
      case 'iam_user':
      case 'iam_access_key':
        return <KeyRound className="w-3.5 h-3.5 text-purple-400 inline mr-1.5" />;
      case 'security_group':
      case 'ec2_instance':
        return <Server className="w-3.5 h-3.5 text-emerald-400 inline mr-1.5" />;
      case 'rds_instance':
        return <Database className="w-3.5 h-3.5 text-orange-400 inline mr-1.5" />;
      default:
        return <ShieldAlert className="w-3.5 h-3.5 text-slate-400 inline mr-1.5" />;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
        <div>
          <h2 className="text-lg font-semibold text-white">Detected Security Findings</h2>
          <p className="text-xs text-slate-400">
            Showing {filteredFindings.length} of {findings.length} misconfigurations
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search rules, resources, ARNs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Rule & Finding</th>
              <th className="py-3 px-4">Resource Target</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredFindings.length === 0 ? (
              <tr>
                <td colSpan="4" className="py-8 text-center text-slate-500">
                  No security misconfigurations found matching criteria.
                </td>
              </tr>
            ) : (
              filteredFindings.map((f) => (
                <tr key={f.id || f.rule_id + f.resource_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${getSeverityBadge(f.severity)}`}>
                      {f.severity}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <p className="font-semibold text-slate-100">{f.title}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">{f.rule_id}</p>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center text-slate-300 font-mono text-[11px]">
                      {getResourceIcon(f.resource_type)}
                      <span className="truncate max-w-xs">{f.resource_id}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => onSelectFinding(f)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-medium transition-all"
                    >
                      <Wrench className="w-3.5 h-3.5" />
                      Remediate
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
