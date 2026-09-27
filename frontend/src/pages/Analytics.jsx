import React, { useState, useEffect } from 'react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import { RefreshCw, Calendar, TrendingUp, AlertTriangle } from 'lucide-react';
import { analyticsService, forecastService } from '../services/api';

const COLORS = [
  '#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6',
  '#14b8a6', '#f97316', '#6366f1', '#84cc16', '#06b6d4', '#64748b'
];

export default function Analytics() {
  const [categories, setCategories] = useState([]);
  const [recurring, setRecurring] = useState([]);
  const [forecastDays, setForecastDays] = useState(30);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [catRes, recRes, foreRes] = await Promise.all([
        analyticsService.getCategories(),
        analyticsService.getRecurring(),
        forecastService.getForecast(forecastDays),
      ]);
      setCategories(catRes.data);
      setRecurring(recRes.data);
      setForecast(foreRes.data);
    } catch (err) {
      console.error('Failed to load analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [forecastDays]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Spending Analytics & Forecasting</h1>
        <p className="text-xs text-slate-400 mt-1">
          Detailed category allocation, recurring cadence detection, and forward cash flow modeling.
        </p>
      </div>

      {/* Category Breakdown Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pie Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col items-center">
          <h2 className="text-sm font-semibold text-white mb-2 self-start">Expense Distribution</h2>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={categories}
                  dataKey="total_amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={50}
                  paddingAngle={3}
                >
                  {categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                  formatter={(val) => `$${Number(val).toFixed(2)}`}
                />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Categories Table */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800">
          <h2 className="text-sm font-semibold text-white mb-4">Category Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3 text-right">Total Spent</th>
                  <th className="py-2.5 px-3 text-right">Share</th>
                  <th className="py-2.5 px-3 text-center">Transactions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {categories.map((c, i) => (
                  <tr key={c.category} className="hover:bg-slate-800/20">
                    <td className="py-3 px-3 flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: COLORS[i % COLORS.length] }}
                      />
                      <span className="font-medium text-slate-200">{c.category}</span>
                    </td>
                    <td className="py-3 px-3 text-right font-semibold text-white">
                      ${c.total_amount.toFixed(2)}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${c.percentage}%`,
                              backgroundColor: COLORS[i % COLORS.length],
                            }}
                          />
                        </div>
                        <span className="text-slate-400 font-mono w-10 text-right">{c.percentage}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-center text-slate-400 font-mono">
                      {c.transaction_count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Recurring Transactions Section */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-emerald-400" />
              <span>Detected Recurring Subscriptions & Inflows</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Algorithmically grouped by merchant frequency and interval cadence.
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
            {recurring.length} Patterns Active
          </span>
        </div>

        {recurring.length === 0 ? (
          <p className="text-xs text-slate-400 py-8 text-center">
            No recurring charges detected yet. Import at least 2 billing cycles of data.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                  <th className="py-2.5 px-3">Merchant / Stream</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3 text-center">Cadence</th>
                  <th className="py-2.5 px-3 text-right">Avg Amount</th>
                  <th className="py-2.5 px-3 text-center">Next Expected</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recurring.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/20">
                    <td className="py-3 px-3 font-medium text-white">{r.merchant}</td>
                    <td className="py-3 px-3 text-slate-400">{r.category}</td>
                    <td className="py-3 px-3 text-center">
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-emerald-400 border border-emerald-500/20 text-[11px] capitalize">
                        {r.cadence}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right font-semibold text-white">
                      ${Math.abs(r.average_amount).toFixed(2)}
                    </td>
                    <td className="py-3 px-3 text-center font-mono text-slate-400">
                      {r.next_expected_date || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Forecast Configuration & Simulation */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span>Forward Cash Flow Projection</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Simulate cash trajectory based on recent burn rate and scheduled charges.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-800/80 p-1 rounded-xl border border-slate-700">
            {[30, 45, 60].map((days) => (
              <button
                key={days}
                onClick={() => setForecastDays(days)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                  forecastDays === days
                    ? 'bg-emerald-500 text-slate-950 font-semibold shadow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {days} Days
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="text-[11px] text-slate-400">Current Balance</span>
            <p className="text-lg font-bold text-white mt-1">
              ${(forecast?.current_balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
          </div>
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="text-[11px] text-slate-400">Projected Balance ({forecastDays}d)</span>
            <p className="text-lg font-bold text-emerald-400 mt-1">
              ${(forecast?.projected_end_balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
          </div>
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="text-[11px] text-slate-400">Model Confidence</span>
            <p className="text-lg font-bold text-blue-400 mt-1">
              {((forecast?.confidence_level || 0.85) * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecast?.daily_projections || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                formatter={(val, name) => [`$${Number(val).toFixed(2)}`, name]}
              />
              <Area type="monotone" dataKey="upper_bound" stroke="none" fill="#3b82f6" fillOpacity={0.08} />
              <Area type="monotone" dataKey="predicted_balance" stroke="#10b981" strokeWidth={2} fill="#10b981" fillOpacity={0.2} name="Forecast" />
              <Area type="monotone" dataKey="lower_bound" stroke="none" fill="#3b82f6" fillOpacity={0.08} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
