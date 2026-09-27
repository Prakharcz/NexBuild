import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, Download, ArrowRight } from 'lucide-react';
import { ingestionService } from '../services/api';
import { Link } from 'react-router-dom';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (dropped.name.endsWith('.csv')) {
        setFile(dropped);
        setError(null);
      } else {
        setError('Please upload a standard .csv file.');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const res = await ingestionService.uploadCSV(file);
      setResult(res.data);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse and upload CSV statement.');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadSample = () => {
    // Generate sample CSV content and trigger browser download
    const sampleCSV = `Date,Description,Amount,Category
2026-04-01,Acme Corp Payroll Direct Deposit,3200.00,Income
2026-04-01,Oakwood Property Management Rent,-1500.00,Housing
2026-04-02,Trader Joe's Groceries,-84.50,Groceries
2026-04-03,Starbucks Coffee,-6.75,Food & Dining
2026-04-04,Netflix Subscription,-15.99,Entertainment
2026-04-05,Spotify Premium,-10.99,Entertainment
2026-04-08,Metropolitan Electric Utility,-112.40,Utilities
2026-04-10,Whole Foods Market,-95.30,Groceries
2026-04-15,Acme Corp Payroll Direct Deposit,3200.00,Income
2026-04-15,Planet Fitness Gym Membership,-45.00,Health & Fitness
2026-05-27,Apex Plumbing Emergency Leak Repair,-1250.00,Housing
2026-06-04,Netflix Subscription,-19.99,Entertainment
2026-07-23,Best Buy Electronics Tech Purchase,-899.00,Shopping`;

    const blob = new Blob([sampleCSV], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_bank_statement.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Upload Bank Statements</h1>
        <p className="text-xs text-slate-400 mt-1">
          Import your CSV transactions. Automatic normalization, categorization, and anomaly detection are applied instantly.
        </p>
      </div>

      {/* Result Alert */}
      {result && (
        <div className="glass-panel p-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 space-y-3">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-sm">Batch Ingestion Completed</h3>
          </div>
          <p className="text-xs text-slate-300">{result.message}</p>
          <div className="flex items-center gap-4 text-xs font-mono pt-2">
            <span>Parsed: <strong>{result.total_parsed}</strong></span>
            <span>Saved: <strong>{result.total_saved}</strong></span>
            <span>Anomalies Flagged: <strong>{result.anomalies_detected}</strong></span>
          </div>
          <div className="pt-2">
            <Link
              to="/transactions"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 hover:text-emerald-300"
            >
              <span>Explore Imported Transactions</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Zone */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-3xl p-10 flex flex-col items-center justify-center text-center transition-all ${
            dragOver
              ? 'border-emerald-500 bg-emerald-500/5'
              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40'
          }`}
        >
          <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-4 text-emerald-400">
            <UploadCloud className="w-7 h-7" />
          </div>

          <h2 className="text-base font-semibold text-white mb-1">
            Drag & Drop bank statement CSV here
          </h2>
          <p className="text-xs text-slate-400 max-w-sm mb-4">
            Supports exports from Chase, Bank of America, Wells Fargo, Citi, and standard custom spreadsheets.
          </p>

          <label className="cursor-pointer">
            <span className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium px-4 py-2.5 rounded-xl border border-slate-700 transition-colors inline-block">
              Browse Files
            </span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>

          {file && (
            <div className="mt-4 flex items-center gap-2 bg-slate-800/80 px-4 py-2 rounded-xl border border-emerald-500/30 text-xs text-emerald-400">
              <FileText className="w-4 h-4" />
              <span className="font-mono">{file.name}</span>
              <span className="text-slate-400">({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={handleDownloadSample}
            className="flex items-center gap-2 text-xs text-slate-400 hover:text-emerald-400 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download Sample Banking CSV</span>
          </button>

          <button
            type="submit"
            disabled={!file || uploading}
            className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20"
          >
            {uploading ? (
              <>
                <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Processing Statement...</span>
              </>
            ) : (
              <span>Start Ingestion & Analysis</span>
            )}
          </button>
        </div>
      </form>

      {/* Format Helper Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-white">Supported Bank Column Formats</h3>
        <p className="text-xs text-slate-400">
          The ingestion engine recognizes standard column headers flexibly:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="font-semibold text-emerald-400">Date Columns</span>
            <p className="text-slate-400 mt-1">Date, Posting Date, Trans Date, Transaction Date (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)</p>
          </div>
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="font-semibold text-blue-400">Description Columns</span>
            <p className="text-slate-400 mt-1">Description, Merchant, Payee, Details, Memo, Narrative</p>
          </div>
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="font-semibold text-purple-400">Amount Formats</span>
            <p className="text-slate-400 mt-1">Single Amount column, or separate Debit/Credit columns with currency symbols</p>
          </div>
        </div>
      </div>
    </div>
  );
}
