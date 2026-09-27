import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import StatCard from '../components/StatCard';
import RiskGauge from '../components/RiskGauge';
import {
  analyticsService,
  forecastService,
  riskService,
  transactionService,
} from '../services/api';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [risk, setRisk] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [sumRes, riskRes, foreRes, monthlyRes, anomRes] = await Promise.all([
          analyticsService.getSummary(),
          riskService.getRiskScore(),
          forecastService.getForecast(30),
          analyticsService.getMonthlyTrends(),
          transactionService.getTransactions({ anomaly_only: true, limit: 5 }),
        ]);

        setSummary(sumRes.data);
        setRisk(riskRes.data);
        setForecast(foreRes.data);
        setMonthlyTrends(monthlyRes.data);
        setAnomalies(anomRes.data);
      } catch (err) {
        console.error('Failed to load dashboard metrics', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner / Heading */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Executive Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time financial telemetry, cash flow forecasting, and automated risk scoring.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/upload"
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium px-4 py-2 rounded-xl border border-slate-700 transition-colors"
          >
            Import Statement
          </Link>
          <Link
            to="/recommendations"
            className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 text-xs font-semibold px-4 py-2 rounded-xl flex items-center gap-1.5 transition-colors shadow-lg shadow-emerald-500/20"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Risk Advice</span>
          </Link>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Inflows"
          value={`$${(summary?.total_income || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
          subtitle="Direct deposits & earnings"
          icon={TrendingUp}
          color="emerald"
        />
        <StatCard
          title="Total Outflows"
          value={`$${(summary?.total_expenses || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
          subtitle="Living expenses & subscriptions"
          icon={TrendingDown}
          color="rose"
        />
        <StatCard
          title="Net Cash Flow"
          value={`$${(summary?.net_cash_flow || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
          subtitle={summary?.net_cash_flow >= 0 ? 'Surplus retained' : 'Deficit burn'}
          icon={DollarSign}
          color={summary?.net_cash_flow >= 0 ? 'blue' : 'amber'}
        />
        <StatCard
          title="Savings Rate"
          value={`${summary?.savings_rate || 0}%`}
          subtitle="Of total incoming cash"
          icon={ShieldCheck}
          color="purple"
        />
      </div>

      {/* Main Visuals Row: Risk Gauge & 30-Day Cash Flow Forecast */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <RiskGauge
            score={risk?.score || 50}
            riskLevel={risk?.risk_level || 'Moderate Risk'}
            factors={risk?.factors || []}
          />
        </div>

        {/* 30-Day Cash Flow Forecast Area Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">30-Day Cash Flow & Balance Forecast</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Moving average projection anchored with upcoming recurring bills.
              </p>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400">Projected Ending Balance</span>
              <p className="text-base font-bold text-emerald-400">
                ${(forecast?.projected_end_balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecast?.daily_projections || []}>
                <defs>
                  <linearGradient id="forecastFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: '#64748b', fontSize: 10 }}
                  tickFormatter={(val) => val.slice(5)}
                />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                  formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Balance']}
                />
                <Area
                  type="monotone"
                  dataKey="predicted_balance"
                  stroke="#10b981"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#forecastFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Month-over-Month Cash Flow & Outlier Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* MoM Bar Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">Month-Over-Month Performance</h2>
              <p className="text-xs text-slate-400 mt-0.5">Historical comparison of monthly income and expenses.</p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                  formatter={(val) => `$${Number(val).toFixed(2)}`}
                />
                <Bar dataKey="income" name="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expenses" name="Expenses" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Flagged Anomalies Card */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-white flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Detected Anomalies</span>
              </h2>
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">
                IQR / Z-Score
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Statistical outliers detected in recent expenditure streams.
            </p>

            <div className="space-y-3">
              {anomalies.length === 0 ? (
                <p className="text-xs text-slate-400 py-6 text-center">No abnormal expense spikes detected.</p>
              ) : (
                anomalies.slice(0, 3).map((anom) => (
                  <div
                    key={anom.id}
                    className="p-3 bg-slate-800/40 rounded-xl border border-slate-700/60 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200 truncate max-w-[160px]">
                        {anom.merchant || anom.description}
                      </span>
                      <span className="font-bold text-rose-400">
                        ${Math.abs(anom.amount).toFixed(2)}
                      </span>
                    </div>
                    <p className="text-[11px] text-amber-400/90 leading-tight">
                      {anom.anomaly_reason || 'Statistical outlier'}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          <Link
            to="/transactions?anomalies=true"
            className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-emerald-400 hover:text-emerald-300 font-medium"
          >
            <span>View All Anomalies</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
