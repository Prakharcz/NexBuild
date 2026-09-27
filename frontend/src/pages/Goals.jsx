import React, { useState, useEffect } from 'react';
import { Target, Plus, CheckCircle, Calendar, DollarSign, Trash2, ArrowUpRight } from 'lucide-react';
import { goalService } from '../services/api';
import Modal from '../components/Modal';

export default function Goals() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [targetAmount, setTargetAmount] = useState('');
  const [currentAmount, setCurrentAmount] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [category, setCategory] = useState('Emergency Fund');

  // Contribute state
  const [contributeGoalId, setContributeGoalId] = useState(null);
  const [contributeAmount, setContributeAmount] = useState('');

  const fetchGoals = async () => {
    setLoading(true);
    try {
      const res = await goalService.getGoals();
      setGoals(res.data);
    } catch (err) {
      console.error('Failed to load goals', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const handleCreateGoal = async (e) => {
    e.preventDefault();
    try {
      await goalService.createGoal({
        name,
        target_amount: parseFloat(targetAmount),
        current_amount: currentAmount ? parseFloat(currentAmount) : 0.0,
        target_date: targetDate || null,
        category,
      });
      setIsModalOpen(false);
      setName('');
      setTargetAmount('');
      setCurrentAmount('');
      setTargetDate('');
      fetchGoals();
    } catch (err) {
      console.error('Failed to create goal', err);
    }
  };

  const handleContributeSubmit = async (e) => {
    e.preventDefault();
    if (!contributeGoalId || !contributeAmount) return;

    const goal = goals.find((g) => g.id === contributeGoalId);
    if (!goal) return;

    try {
      const newCurrent = goal.current_amount + parseFloat(contributeAmount);
      await goalService.updateGoal(contributeGoalId, { current_amount: newCurrent });
      setContributeGoalId(null);
      setContributeAmount('');
      fetchGoals();
    } catch (err) {
      console.error('Failed to contribute to goal', err);
    }
  };

  const handleDeleteGoal = async (id) => {
    if (!window.confirm('Are you sure you want to delete this goal?')) return;
    try {
      await goalService.deleteGoal(id);
      setGoals((prev) => prev.filter((g) => g.id !== id));
    } catch (err) {
      console.error('Failed to delete goal', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Savings Goals</h1>
          <p className="text-xs text-slate-400 mt-1">
            Track capital targets, monitor funding pacing, and calculate required monthly contributions.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center gap-2 transition-colors shadow-lg shadow-emerald-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>New Savings Goal</span>
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : goals.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-3">
          <Target className="w-10 h-10 text-slate-500 mx-auto" />
          <h3 className="text-sm font-semibold text-white">No Savings Goals Set Yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Establish financial milestones like a 6-month Emergency Fund, house down payment, or investment target.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="mt-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium px-4 py-2 rounded-xl border border-slate-700"
          >
            Create First Goal
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {goals.map((g) => (
            <div
              key={g.id}
              className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-colors"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                    {g.category}
                  </span>
                  <button
                    onClick={() => handleDeleteGoal(g.id)}
                    className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <h3 className="font-bold text-white text-base">{g.name}</h3>

                <div className="mt-4 flex items-baseline justify-between">
                  <span className="text-2xl font-extrabold text-white">
                    ${g.current_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">
                    / ${g.target_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="mt-3 w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      g.progress_percentage >= 100 ? 'bg-teal-400' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(g.progress_percentage, 100)}%` }}
                  />
                </div>

                <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                  <span>{g.progress_percentage}% achieved</span>
                  <span>${g.remaining_amount.toFixed(2)} remaining</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/80 space-y-2 text-xs">
                {g.target_date && (
                  <div className="flex items-center justify-between text-slate-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      Target Date:
                    </span>
                    <span className="text-slate-200 font-mono">{g.target_date}</span>
                  </div>
                )}

                {g.monthly_savings_needed && (
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Required Monthly:</span>
                    <span className="text-emerald-400 font-semibold font-mono">
                      ${g.monthly_savings_needed.toFixed(2)}/mo
                    </span>
                  </div>
                )}

                <button
                  onClick={() => setContributeGoalId(g.id)}
                  className="w-full mt-2 bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-200 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                >
                  <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Contribute Funds</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Goal Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create Savings Goal">
        <form onSubmit={handleCreateGoal} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Goal Name</label>
            <input
              type="text"
              required
              placeholder="e.g. 6-Month Emergency Buffer"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Target Amount ($)</label>
              <input
                type="number"
                step="1"
                required
                placeholder="10000"
                value={targetAmount}
                onChange={(e) => setTargetAmount(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Initial Saved ($)</label>
              <input
                type="number"
                step="1"
                placeholder="2500"
                value={currentAmount}
                onChange={(e) => setCurrentAmount(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target Completion Date</label>
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            >
              <option value="Emergency Fund">Emergency Fund</option>
              <option value="Housing">Housing Down Payment</option>
              <option value="Travel">Travel & Vacation</option>
              <option value="Vehicles">Vehicle Purchase</option>
              <option value="Investments">Retirement & Brokerage</option>
              <option value="General Savings">General Savings</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold px-4 py-2 rounded-xl text-xs"
            >
              Create Goal
            </button>
          </div>
        </form>
      </Modal>

      {/* Contribute Funds Modal */}
      <Modal
        isOpen={Boolean(contributeGoalId)}
        onClose={() => setContributeGoalId(null)}
        title="Contribute Towards Goal"
      >
        <form onSubmit={handleContributeSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Contribution Amount ($)
            </label>
            <input
              type="number"
              step="0.01"
              required
              placeholder="150.00"
              value={contributeAmount}
              onChange={(e) => setContributeAmount(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>
          <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setContributeGoalId(null)}
              className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold px-4 py-2 rounded-xl text-xs"
            >
              Add Contribution
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
