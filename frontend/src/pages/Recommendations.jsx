import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  CheckCircle,
  XCircle,
  History,
  ShieldAlert,
  ArrowRight,
  TrendingDown,
  RefreshCw,
  FileCheck,
} from 'lucide-react';
import { recommendationService } from '../services/api';
import Modal from '../components/Modal';

export default function Recommendations() {
  const [activeTab, setActiveTab] = useState('recommendations'); // 'recommendations' | 'audit'
  const [recommendations, setRecommendations] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  // Human approval modal state
  const [selectedRec, setSelectedRec] = useState(null);
  const [pendingAction, setPendingAction] = useState(null); // 'ACTED_ON' | 'APPROVED' | 'DISMISSED'
  const [actionNotes, setActionNotes] = useState('');
  const [submittingAction, setSubmittingAction] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const [recRes, auditRes] = await Promise.all([
        recommendationService.getRecommendations('PENDING'),
        recommendationService.getAuditLogs(),
      ]);
      setRecommendations(recRes.data);
      setAuditLogs(auditRes.data);
    } catch (err) {
      console.error('Failed to load recommendations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleScanNow = async () => {
    setScanning(true);
    try {
      const res = await recommendationService.generateRecommendations();
      setRecommendations(res.data.filter((r) => r.status === 'PENDING'));
      const auditRes = await recommendationService.getAuditLogs();
      setAuditLogs(auditRes.data);
    } catch (err) {
      console.error('Scan error', err);
    } finally {
      setScanning(false);
    }
  };

  const openActionModal = (rec, action) => {
    setSelectedRec(rec);
    setPendingAction(action);
    setActionNotes('');
  };

  const handleConfirmAction = async (e) => {
    e.preventDefault();
    if (!selectedRec || !pendingAction) return;

    setSubmittingAction(true);
    try {
      await recommendationService.actOnRecommendation(
        selectedRec.id,
        pendingAction,
        actionNotes
      );
      setSelectedRec(null);
      setPendingAction(null);
      setActionNotes('');
      // Refresh list and audit log
      fetchRecommendations();
    } catch (err) {
      console.error('Failed to register human approval decision', err);
    } finally {
      setSubmittingAction(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>AI Risk Advisory & Human Approval</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              Human-in-the-Loop
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Algorithmic insights require explicit user confirmation before execution. Decisions are permanently logged.
          </p>
        </div>

        <button
          onClick={handleScanNow}
          disabled={scanning}
          className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
          <span>{scanning ? 'Analyzing History...' : 'Scan For Risks'}</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 gap-6">
        <button
          onClick={() => setActiveTab('recommendations')}
          className={`pb-3 text-xs font-semibold flex items-center gap-2 transition-colors relative ${
            activeTab === 'recommendations'
              ? 'text-emerald-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Pending Recommendations</span>
          <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[10px] text-slate-300">
            {recommendations.length}
          </span>
          {activeTab === 'recommendations' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-400" />
          )}
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`pb-3 text-xs font-semibold flex items-center gap-2 transition-colors relative ${
            activeTab === 'audit' ? 'text-emerald-400' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <History className="w-4 h-4" />
          <span>Decision Audit Trail</span>
          <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[10px] text-slate-300">
            {auditLogs.length}
          </span>
          {activeTab === 'audit' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-400" />
          )}
        </button>
      </div>

      {/* Tab 1: Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="space-y-4">
          {loading ? (
            <div className="flex justify-center py-16">
              <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : recommendations.length === 0 ? (
            <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-3">
              <FileCheck className="w-10 h-10 text-emerald-400 mx-auto" />
              <h3 className="text-sm font-semibold text-white">All Clear! No Pending Risk Actions</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                No subscription spikes, liquidity warnings, or unapproved optimizations detected.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 hover:border-slate-700/80 transition-all"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-semibold uppercase tracking-wider text-[10px]">
                        {rec.severity} priority
                      </span>
                      <span className="text-xs text-slate-400">
                        Category: <strong className="text-slate-300 capitalize">{rec.category.replace('_', ' ')}</strong>
                      </span>
                    </div>

                    {rec.estimated_monthly_savings > 0 && (
                      <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                        <TrendingDown className="w-3.5 h-3.5" />
                        <span>Est. Monthly Savings: +${rec.estimated_monthly_savings.toFixed(2)}/mo</span>
                      </div>
                    )}
                  </div>

                  <div>
                    <h3 className="font-bold text-white text-base">{rec.title}</h3>
                    <p className="text-xs text-slate-300 mt-1">{rec.description}</p>
                  </div>

                  {/* AI Explanation Box */}
                  {rec.ai_explanation && (
                    <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 text-xs text-slate-200 space-y-1">
                      <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-[11px] mb-1">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>AI Advisory Rationale</span>
                      </div>
                      <p className="leading-relaxed text-slate-300">{rec.ai_explanation}</p>
                    </div>
                  )}

                  {/* Human-in-the-Loop Action Buttons */}
                  <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
                    <span className="text-[11px] text-slate-400 italic">
                      Requires explicit human confirmation
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openActionModal(rec, 'DISMISSED')}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white px-3 py-1.5 rounded-xl text-xs font-medium border border-slate-700 transition-colors"
                      >
                        Dismiss
                      </button>
                      <button
                        onClick={() => openActionModal(rec, 'APPROVED')}
                        className="bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/40 px-3 py-1.5 rounded-xl text-xs font-medium transition-colors"
                      >
                        Approve Plan
                      </button>
                      <button
                        onClick={() => openActionModal(rec, 'ACTED_ON')}
                        className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold px-4 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-md shadow-emerald-500/20"
                      >
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Confirm Acted On</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Immutable Audit Log */}
      {activeTab === 'audit' && (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          {auditLogs.length === 0 ? (
            <p className="py-12 text-center text-xs text-slate-400">
              No audit log entries yet. Confirm or dismiss recommendations above to record decisions.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/60 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Action Taken</th>
                    <th className="py-3 px-4">Recommendation Target</th>
                    <th className="py-3 px-4">User Notes / Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/20">
                      <td className="py-3.5 px-4 font-mono text-slate-400 whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                            log.action === 'ACTED_ON'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              : log.action === 'APPROVED'
                              ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                              : 'bg-slate-800 text-slate-400 border-slate-700'
                          }`}
                        >
                          {log.action}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-medium text-white max-w-xs truncate">
                        {log.recommendation_title || `Recommendation #${log.recommendation_id}`}
                      </td>
                      <td className="py-3.5 px-4 text-slate-300">
                        {log.decision_reason || 'Confirmed via UI modal'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Human Approval Confirmation Modal */}
      <Modal
        isOpen={Boolean(selectedRec)}
        onClose={() => setSelectedRec(null)}
        title="Confirm Human-in-the-Loop Action"
      >
        <form onSubmit={handleConfirmAction} className="space-y-4">
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60 text-xs">
            <span className="text-slate-400">Target Recommendation:</span>
            <p className="font-semibold text-white mt-0.5">{selectedRec?.title}</p>
          </div>

          <div>
            <span className="text-xs text-slate-300">
              Action to execute:{' '}
              <strong className="text-emerald-400 font-mono">{pendingAction}</strong>
            </span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Decision Reason / Audit Notes (Optional)
            </label>
            <textarea
              rows={3}
              placeholder="e.g., Canceled Netflix plan online; downgraded to standard with ads."
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setSelectedRec(null)}
              className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingAction}
              className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-2"
            >
              {submittingAction && (
                <span className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              )}
              <span>Record & Log Decision</span>
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
