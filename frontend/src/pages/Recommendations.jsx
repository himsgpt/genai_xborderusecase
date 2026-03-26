import { useEffect, useState } from 'react'
import {
  Lightbulb,
  DollarSign,
  Clock,
  AlertCircle,
  Check,
  X,
  ChevronDown,
  ChevronUp,
  ArrowUpRight,
} from 'lucide-react'
import api from '../api'

const STATUS_COLORS = {
  pending: 'badge-yellow',
  accepted: 'badge-green',
  rejected: 'badge-red',
  implemented: 'badge-blue',
}

const EFFORT_ICONS = {
  low: { color: 'text-emerald-500', label: 'Low effort' },
  medium: { color: 'text-amber-500', label: 'Medium effort' },
  high: { color: 'text-red-500', label: 'High effort' },
}

function RecCard({ rec, onStatusChange }) {
  const [expanded, setExpanded] = useState(false)
  const [updating, setUpdating] = useState(false)

  const handleStatus = async (status) => {
    setUpdating(true)
    try {
      await api.updateRecommendationStatus(rec.id, status)
      onStatusChange(rec.id, status)
    } catch (err) {
      console.error(err)
    } finally {
      setUpdating(false)
    }
  }

  const effort = EFFORT_ICONS[rec.effort] || EFFORT_ICONS.medium

  return (
    <div className="card overflow-hidden">
      <div
        className="px-5 py-4 flex items-start gap-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
          <Lightbulb className="w-5 h-5 text-amber-500" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-medium text-sm">{rec.title}</h4>
            <span className={`badge ${STATUS_COLORS[rec.status] || 'badge-yellow'}`}>
              {rec.status}
            </span>
          </div>
          {rec.description && (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{rec.description}</p>
          )}
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <DollarSign className="w-3 h-3" />
              ${rec.estimated_savings_annual?.toLocaleString()}/yr
            </span>
            <span className={`flex items-center gap-1 ${effort.color}`}>
              <Clock className="w-3 h-3" />
              {effort.label}
            </span>
            <span className="flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {rec.risk} risk
            </span>
            {rec.category && (
              <span className="badge-blue">{rec.category}</span>
            )}
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-lg font-bold text-emerald-600 flex items-center gap-1">
            <ArrowUpRight className="w-4 h-4" />
            ${rec.estimated_savings_annual?.toLocaleString()}
          </div>
          <div className="text-xs text-gray-400">annual savings</div>
        </div>
        {expanded ? <ChevronUp className="w-5 h-5 text-gray-400 mt-1" /> : <ChevronDown className="w-5 h-5 text-gray-400 mt-1" />}
      </div>

      {expanded && (
        <div className="px-5 py-4 border-t border-gray-100 bg-gray-50/50 space-y-4">
          {/* Savings detail */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="bg-white rounded-lg p-3 border">
              <div className="text-xs text-gray-500">Per-Transaction</div>
              <div className="font-bold text-emerald-600">${rec.estimated_savings?.toFixed(2)}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border">
              <div className="text-xs text-gray-500">Annual Projection</div>
              <div className="font-bold text-emerald-600">${rec.estimated_savings_annual?.toLocaleString()}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border">
              <div className="text-xs text-gray-500">Implementation</div>
              <div className="font-bold capitalize">{rec.effort} effort / {rec.risk} risk</div>
            </div>
          </div>

          {/* Implementation steps */}
          {rec.implementation_steps && rec.implementation_steps.length > 0 && (
            <div>
              <h5 className="text-sm font-semibold text-gray-700 mb-2">Implementation Steps</h5>
              <ol className="space-y-2">
                {rec.implementation_steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm">
                    <span className="w-6 h-6 bg-brand-100 text-brand-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    <span className="text-gray-600">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Actions */}
          {rec.status === 'pending' && (
            <div className="flex gap-2 pt-2">
              <button
                onClick={(e) => { e.stopPropagation(); handleStatus('accepted') }}
                disabled={updating}
                className="flex items-center gap-1 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded-lg transition-colors"
              >
                <Check className="w-4 h-4" />
                Accept
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); handleStatus('rejected') }}
                disabled={updating}
                className="flex items-center gap-1 px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
                Reject
              </button>
            </div>
          )}
          {rec.status === 'accepted' && (
            <button
              onClick={(e) => { e.stopPropagation(); handleStatus('implemented') }}
              disabled={updating}
              className="flex items-center gap-1 px-3 py-1.5 bg-brand-600 hover:bg-brand-700 text-white text-sm rounded-lg transition-colors"
            >
              <Check className="w-4 h-4" />
              Mark as Implemented
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default function Recommendations() {
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await api.getRecommendations()
        setRecs(data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  const handleStatusChange = (id, status) => {
    setRecs(recs.map(r => r.id === id ? { ...r, status } : r))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  const totalSavings = recs.reduce((s, r) => s + (r.estimated_savings_annual || 0), 0)
  const accepted = recs.filter(r => r.status === 'accepted' || r.status === 'implemented').length

  return (
    <div className="space-y-6">
      {recs.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="card p-5">
            <p className="text-sm text-gray-500">Total Recommendations</p>
            <p className="text-2xl font-bold mt-1">{recs.length}</p>
          </div>
          <div className="card p-5">
            <p className="text-sm text-gray-500">Annual Savings Potential</p>
            <p className="text-2xl font-bold text-emerald-600 mt-1">${totalSavings.toLocaleString()}</p>
          </div>
          <div className="card p-5">
            <p className="text-sm text-gray-500">Accepted / Implemented</p>
            <p className="text-2xl font-bold text-brand-600 mt-1">{accepted} / {recs.length}</p>
          </div>
        </div>
      )}

      {recs.length === 0 ? (
        <div className="max-w-lg mx-auto mt-12 text-center space-y-6">
          <Lightbulb className="w-16 h-16 text-gray-300 mx-auto" />
          <h2 className="text-xl font-bold">No Recommendations Yet</h2>
          <p className="text-gray-500">Run analysis on your payments to generate actionable cost-saving recommendations.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {recs.map(r => (
            <RecCard key={r.id} rec={r} onStatusChange={handleStatusChange} />
          ))}
        </div>
      )}
    </div>
  )
}
