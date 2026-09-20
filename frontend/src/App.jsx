import React, { useState, useEffect } from 'react';
import { Shield, Play, RefreshCw, Plus, Cloud, Layers, CheckCircle, AlertTriangle } from 'lucide-react';
import { authAPI, accountsAPI, scansAPI, dashboardAPI } from './services/api';
import ScoreGauge from './components/ScoreGauge';
import SeverityCards from './components/SeverityCards';
import FindingsTable from './components/FindingsTable';
import RemediationModal from './components/RemediationModal';
import AccountModal from './components/AccountModal';

export default function App() {
  const [user, setUser] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccountId, setSelectedAccountId] = useState(null);
  const [overview, setOverview] = useState({
    average_security_score: 100,
    severity_breakdown: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
    scanned_resources_count: 0,
  });
  const [findings, setFindings] = useState([]);
  const [selectedSeverity, setSelectedSeverity] = useState(null);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isAccountModalOpen, setIsAccountModalOpen] = useState(false);
  const [notification, setNotification] = useState(null);

  // Initialize Auth & Data
  useEffect(() => {
    const initApp = async () => {
      try {
        let token = localStorage.getItem('cloudguard_token');
        if (!token) {
          // Auto-login / register default auditor account for seamless local evaluation
          try {
            const loginRes = await authAPI.login('auditor@cloudguard.io', 'Password123!');
            token = loginRes.access_token;
          } catch {
            await authAPI.register('auditor@cloudguard.io', 'Password123!', 'Security Lead');
            const loginRes = await authAPI.login('auditor@cloudguard.io', 'Password123!');
            token = loginRes.access_token;
          }
        }

        const me = await authAPI.getMe();
        setUser(me);
        await loadAccountsAndData();
      } catch (err) {
        console.error('App init error:', err);
      }
    };

    initApp();
  }, []);

  const loadAccountsAndData = async () => {
    try {
      const accs = await accountsAPI.list();
      setAccounts(accs);

      let currentAccId = selectedAccountId;
      if (accs.length > 0 && !currentAccId) {
        currentAccId = accs[0].id;
        setSelectedAccountId(currentAccId);
      }

      await refreshDashboard(currentAccId);
    } catch (err) {
      console.error('Failed to load accounts/data:', err);
    }
  };

  const refreshDashboard = async (accountId) => {
    try {
      const over = await dashboardAPI.getOverview();
      setOverview(over);

      // Fetch findings
      const fList = await dashboardAPI.getAllFindings({
        severity: selectedSeverity || undefined,
      });
      setFindings(fList);
    } catch (err) {
      console.error('Failed to refresh dashboard:', err);
    }
  };

  useEffect(() => {
    if (user) {
      dashboardAPI.getAllFindings({ severity: selectedSeverity || undefined }).then(setFindings);
    }
  }, [selectedSeverity, user]);

  const handleTriggerScan = async () => {
    if (!selectedAccountId) {
      showNotification('Please connect an AWS Cloud Account first.', 'error');
      setIsAccountModalOpen(true);
      return;
    }

    setIsScanning(true);
    try {
      const scanRes = await scansAPI.trigger(selectedAccountId);
      showNotification(`Scan completed! Posture score: ${scanRes.security_score}/100`, 'success');
      await refreshDashboard(selectedAccountId);
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Scan execution failed.', 'error');
    } finally {
      setIsScanning(false);
    }
  };

  const handleAccountCreated = async (newAccountData) => {
    const acc = await accountsAPI.create(newAccountData);
    setAccounts((prev) => [...prev, acc]);
    setSelectedAccountId(acc.id);
    showNotification(`Account ${acc.account_alias} connected successfully.`, 'success');
  };

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-30 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
            <Shield className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              CloudGuard <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono">CSPM</span>
            </h1>
            <p className="text-[11px] text-slate-400">AWS Security Posture & Compliance</p>
          </div>
        </div>

        {/* Account Selector & Actions */}
        <div className="flex items-center gap-3">
          {accounts.length > 0 ? (
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
              <Cloud className="w-3.5 h-3.5 text-sky-400 mr-2" />
              <select
                value={selectedAccountId || ''}
                onChange={(e) => setSelectedAccountId(Number(e.target.value))}
                className="bg-transparent border-none focus:outline-none text-xs text-white cursor-pointer pr-2"
              >
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id} className="bg-slate-900 text-white">
                    {acc.email || acc.account_alias} ({acc.default_region})
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <button
              onClick={() => setIsAccountModalOpen(true)}
              className="text-xs text-slate-400 hover:text-white px-2 py-1"
            >
              No accounts connected
            </button>
          )}

          <button
            onClick={() => setIsAccountModalOpen(true)}
            className="p-1.5 text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-lg text-xs transition-all"
            title="Connect Account"
          >
            <Plus className="w-4 h-4" />
          </button>

          <button
            onClick={handleTriggerScan}
            disabled={isScanning}
            className="flex items-center gap-2 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-md shadow-emerald-950 transition-all cursor-pointer"
          >
            {isScanning ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Scanning AWS...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                Run Security Scan
              </>
            )}
          </button>
        </div>
      </header>

      {/* Notifications banner */}
      {notification && (
        <div
          className={`px-6 py-2 text-xs font-medium flex items-center gap-2 ${
            notification.type === 'error'
              ? 'bg-rose-500/20 text-rose-300 border-b border-rose-500/30'
              : 'bg-emerald-500/20 text-emerald-300 border-b border-emerald-500/30'
          }`}
        >
          {notification.type === 'error' ? (
            <AlertTriangle className="w-4 h-4" />
          ) : (
            <CheckCircle className="w-4 h-4" />
          )}
          <span>{notification.msg}</span>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Top Metric Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ScoreGauge
            score={overview.average_security_score}
            scannedResources={overview.scanned_resources_count}
          />

          <div className="md:col-span-2 flex flex-col justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-3">
                Security Posture by Severity
              </h2>
              <SeverityCards
                counts={overview.severity_breakdown}
                selectedSeverity={selectedSeverity}
                onSelectSeverity={setSelectedSeverity}
              />
            </div>

            <div className="mt-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-400" />
                <span>Active Monitoring Engine: <strong className="text-white">10 Security Rules (S3, IAM, EC2, RDS)</strong></span>
              </div>
              <span className="text-[11px] text-slate-500">Scan status: Ready</span>
            </div>
          </div>
        </div>

        {/* Findings Section */}
        <FindingsTable
          findings={findings}
          onSelectFinding={setSelectedFinding}
        />
      </main>

      {/* Modals */}
      <RemediationModal
        finding={selectedFinding}
        onClose={() => setSelectedFinding(null)}
      />

      <AccountModal
        isOpen={isAccountModalOpen}
        onClose={() => setIsAccountModalOpen(false)}
        onAccountCreated={handleAccountCreated}
      />
    </div>
  );
}
