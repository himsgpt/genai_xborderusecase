import { useEffect, useState } from 'react'
import {
  BarChart3,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  AlertTriangle,
  TrendingDown,
  Shield,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import api from '../api'

function FeeBreakdown({ analysis }) {
  const fees = [
    { label: 'Platform Fee', value: analysis.platform_fee, color: 'bg-blue-500' },
    { label: 'Intermediary Fee', value: analysis.intermediary_fee, color: 'bg-amber-500' },
    { label: 'FX Spread Cost', value: analysis.fx_spread_cost, color: 'bg-red-500' },
  ]
  const total = analysis.total_fees || 0

  return (
    <div className="space-y-3">
      {fees.map(f => (
        <div key={f.label}>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">{f.label}</span>
            <span className="font-medium">${f.value?.toFixed(2)}</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${f.color}`}
              style={{ width: `${total > 0 ? (f.value / total) * 100 : 0}%` }}
            />
          </div>
        </div>
      ))}
      <div className="flex justify-between text-sm font-bold pt-2 border-t">
        <span>Total Fees</span>
        <span>${total.toFixed(2)}</span>
      </div>
    </div>
  )
}

function PaymentFlow({ flow }) {
  if (!flow || flow.length === 0) return null

  return (
    <div className="flex items-center gap-1 flex-wrap">
      {flow.map((hop, i) => (
        <div key={i} className="flex items-center gap-1">
          <div className={`px-3 py-1.5 rounded-lg text-xs font-medium ${
            hop.type === 'PSP' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
            hop.type === 'intermediary' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
            hop.type === 'network' ? 'bg-gray-100 text-gray-600 border border-gray-200' :
            'bg-purple-50 text-purple-700 border border-purple-200'
          }`}>
            <div>{hop.entity}</div>
            {hop.fee_usd > 0.01 && (
              <div className="text-[10px] opacity-75">${hop.fee_usd.toFixed(2)}</div>
            )}
          </div>
          {i < flow.length - 1 && <ArrowRight className="w-3 h-3 text-gray-300 flex-shrink-0" />}
        </div>
      ))}
    </div>
  )
}

function AnalysisCard({ analysis }) {
  const [expanded, setExpanded] = useState(false)

  const leakageLevel = analysis.leakage_pct > 2 ? 'high' : analysis.leakage_pct > 1 ? 'medium' : 'low'

  return (
    <div className="card overflow-hidden">
      <div
        className="px-5 py-4 flex items-center gap-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
          leakageLevel === 'high' ? 'bg-red-50 text-red-600' :
          leakageLevel === 'medium' ? 'bg-amber-50 text-amber-600' :
          'bg-emerald-50 text-emerald-600'
        }`}>
          {leakageLevel === 'high' ? <AlertTriangle className="w-5 h-5" /> :
           leakageLevel === 'medium' ? <TrendingDown className="w-5 h-5" /> :
           <Shield className="w-5 h-5" />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="font-medium text-sm">Payment {analysis.payment_id?.slice(0, 8)}...</span>
            <span className={`badge ${
              leakageLevel === 'high' ? 'badge-red' : leakageLevel === 'medium' ? 'badge-yellow' : 'badge-green'
            }`}>
              {analysis.leakage_pct?.toFixed(2)}% leakage
            </span>
            <span className="badge-blue">
              {(analysis.confidence_score * 100)?.toFixed(0)}% confidence
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-0.5 truncate">{analysis.explanation}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-lg font-bold text-red-600">-${analysis.total_leakage?.toFixed(2)}</div>
          <div className="text-xs text-gray-400">${analysis.total_fees?.toFixed(2)} total fees</div>
        </div>
        {expanded ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
      </div>

      {expanded && (
        <div className="px-5 py-4 border-t border-gray-100 bg-gray-50/50 space-y-5">
          {/* Fee breakdown */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Fee Attribution</h4>
            <FeeBreakdown analysis={analysis} />
          </div>

          {/* Rates */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-white rounded-lg p-3 border">
              <div className="text-xs text-gray-500">Mid-Market Rate</div>
              <div className="font-bold">{analysis.mid_market_rate?.toFixed(4)}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border">
              <div className="text-xs text-gray-500">Actual Rate</div>
              <div className="font-bold">{analysis.actual_rate?.toFixed(4)}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border">
              <div className="text-xs text-gray-500">Expected Amount</div>
              <div className="font-bold">{analysis.expected_amount?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border">
              <div className="text-xs text-gray-500">Analysis Time</div>
              <div className="font-bold">{analysis.analysis_duration_ms}ms</div>
            </div>
          </div>

          {/* Payment flow */}
          {analysis.reconstructed_flow && analysis.reconstructed_flow.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Reconstructed Payment Route</h4>
              <PaymentFlow flow={analysis.reconstructed_flow} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Analysis() {
  const [analyses, setAnalyses] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const [a, s] = await Promise.all([api.getAnalyses(), api.getAnalysisSummary()])
        setAnalyses(a)
        setSummary(s)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (analyses.length === 0) {
    return (
      <div className="max-w-lg mx-auto mt-12 text-center space-y-6">
        <BarChart3 className="w-16 h-16 text-gray-300 mx-auto" />
        <h2 className="text-xl font-bold">No Analyses Yet</h2>
        <p className="text-gray-500">Go to Payments, load data, and click "Run Analysis" to see results here.</p>
      </div>
    )
  }

  // Fee comparison chart data
  const chartData = analyses.slice(0, 10).map((a, i) => ({
    name: `#${i + 1}`,
    'Platform': a.platform_fee,
    'Intermediary': a.intermediary_fee,
    'FX Spread': a.fx_spread_cost,
  }))

  return (
    <div className="space-y-6">
      {/* Summary headline */}
      {summary && (
        <div className="card p-5 bg-gradient-to-r from-red-600 to-red-800 text-white">
          <p className="text-red-200 text-sm font-medium">Analysis Results</p>
          <p className="text-lg font-semibold mt-1">{summary.headline}</p>
        </div>
      )}

      {/* Fee stacked chart */}
      <div className="card p-5">
        <h3 className="font-semibold text-gray-900 mb-4">Fee Attribution Across Payments</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={v => `$${v}`} />
              <Tooltip
                formatter={(v) => `$${v?.toFixed(2)}`}
                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
              />
              <Bar dataKey="Platform" stackId="a" fill="#6366f1" radius={[0, 0, 0, 0]} />
              <Bar dataKey="Intermediary" stackId="a" fill="#f59e0b" />
              <Bar dataKey="FX Spread" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Individual analyses */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">
          Payment Analyses
          <span className="text-sm font-normal text-gray-400 ml-2">({analyses.length})</span>
        </h3>
        <div className="space-y-3">
          {analyses.map(a => (
            <AnalysisCard key={a.id} analysis={a} />
          ))}
        </div>
      </div>
    </div>
  )
}
