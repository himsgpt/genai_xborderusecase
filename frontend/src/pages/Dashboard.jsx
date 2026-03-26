import { useEffect, useState } from 'react'
import {
  DollarSign,
  TrendingDown,
  AlertTriangle,
  Lightbulb,
  RefreshCw,
  Zap,
  ArrowUpRight,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import { Link } from 'react-router-dom'
import api from '../api'

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

function StatCard({ title, value, subtitle, icon: Icon, color, trend }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    green: 'bg-emerald-50 text-emerald-600',
    yellow: 'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600',
  }

  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorMap[color] || colorMap.blue}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center gap-1 text-xs">
          <ArrowUpRight className="w-3 h-3 text-emerald-500" />
          <span className="text-emerald-600 font-medium">{trend}</span>
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getAnalysisSummary()
      setSummary(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error || !summary || summary.payments_analyzed === 0) {
    return (
      <div className="max-w-lg mx-auto mt-12 text-center space-y-6">
        <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mx-auto">
          <Zap className="w-8 h-8 text-brand-500" />
        </div>
        <h2 className="text-xl font-bold">No Analysis Data Yet</h2>
        <p className="text-gray-500">
          Load demo payments and run analysis to see your dashboard come alive.
        </p>
        <div className="flex gap-3 justify-center">
          <Link to="/payments" className="btn-primary">
            Go to Payments
          </Link>
        </div>
      </div>
    )
  }

  const corridorBarData = (summary.corridors || []).map(c => ({
    name: c.corridor,
    'Total Sent': Math.round(c.total_sent),
    'Total Fees': Math.round(c.total_fees),
    'Leakage': Math.round(c.total_leakage),
  }))

  const costPieData = (summary.corridors || []).map(c => ({
    name: c.corridor,
    value: Math.round(c.total_leakage),
  }))

  return (
    <div className="space-y-6">
      {/* Headline */}
      <div className="card p-5 bg-gradient-to-r from-brand-600 to-brand-800 text-white">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <p className="text-brand-200 text-sm font-medium">Intelligence Summary</p>
            <p className="text-lg font-semibold mt-1">{summary.headline}</p>
          </div>
          <button onClick={fetchData} className="bg-white/20 hover:bg-white/30 text-white px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          title="Payments Analyzed"
          value={summary.payments_analyzed}
          subtitle={`Across ${summary.corridors?.length || 0} corridors`}
          icon={DollarSign}
          color="blue"
        />
        <StatCard
          title="Total Fees Detected"
          value={`$${summary.total_fees?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }) || 0}`}
          subtitle={`${summary.avg_cost_pct?.toFixed(2) || 0}% average cost`}
          icon={TrendingDown}
          color="yellow"
        />
        <StatCard
          title="Money Leakage"
          value={`$${summary.total_leakage?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }) || 0}`}
          subtitle="Above-market costs"
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title="Annual Savings"
          value={`$${summary.potential_annual_savings?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }) || 0}`}
          subtitle="Projected if optimized"
          icon={Lightbulb}
          color="green"
          trend="Actionable"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Bar chart */}
        <div className="card p-5 lg:col-span-2">
          <h3 className="font-semibold text-gray-900 mb-4">Costs by Corridor</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={corridorBarData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={v => `$${v.toLocaleString()}`} />
                <Tooltip
                  formatter={(v) => `$${v.toLocaleString()}`}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Bar dataKey="Total Sent" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Total Fees" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Leakage" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie chart */}
        <div className="card p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Leakage Distribution</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={costPieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  innerRadius={50}
                  paddingAngle={3}
                  label={({ name, value }) => `${name}: $${value}`}
                >
                  {costPieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={v => `$${v.toLocaleString()}`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Corridor table */}
      <div className="card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Corridor Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left px-5 py-3 font-medium text-gray-500">Corridor</th>
                <th className="text-right px-5 py-3 font-medium text-gray-500">Payments</th>
                <th className="text-right px-5 py-3 font-medium text-gray-500">Total Sent</th>
                <th className="text-right px-5 py-3 font-medium text-gray-500">Total Fees</th>
                <th className="text-right px-5 py-3 font-medium text-gray-500">Leakage</th>
                <th className="text-right px-5 py-3 font-medium text-gray-500">Avg Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {(summary.corridors || []).map(c => (
                <tr key={c.corridor} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3 font-medium">{c.corridor}</td>
                  <td className="px-5 py-3 text-right">{c.payments}</td>
                  <td className="px-5 py-3 text-right">${c.total_sent?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="px-5 py-3 text-right text-amber-600">${c.total_fees?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="px-5 py-3 text-right text-red-600">${c.total_leakage?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="px-5 py-3 text-right">
                    <span className={`badge ${c.avg_cost_pct > 3 ? 'badge-red' : c.avg_cost_pct > 2 ? 'badge-yellow' : 'badge-green'}`}>
                      {c.avg_cost_pct?.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
