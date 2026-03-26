import { useEffect, useState } from 'react'
import {
  Upload,
  Play,
  CreditCard,
  Clock,
  Plus,
  ArrowRight,
  X,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function Payments() {
  const [payments, setPayments] = useState([])
  const [loading, setLoading] = useState(true)
  const [demoLoading, setDemoLoading] = useState(false)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [showAdd, setShowAdd] = useState(false)
  const [message, setMessage] = useState(null)
  const navigate = useNavigate()

  const [form, setForm] = useState({
    corridor: 'USD_EUR',
    amount_sent: '',
    currency_sent: 'USD',
    amount_received: '',
    currency_received: 'EUR',
    initiated_at: new Date().toISOString().slice(0, 16),
    psp: 'wise',
  })

  const corridors = [
    { value: 'USD_EUR', send: 'USD', recv: 'EUR' },
    { value: 'USD_INR', send: 'USD', recv: 'INR' },
    { value: 'USD_GBP', send: 'USD', recv: 'GBP' },
  ]

  const fetchPayments = async () => {
    setLoading(true)
    try {
      const data = await api.getPayments()
      setPayments(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchPayments() }, [])

  const handleLoadDemo = async () => {
    setDemoLoading(true)
    setMessage(null)
    try {
      const data = await api.loadDemoPayments()
      setMessage({ type: 'success', text: `Loaded ${data.loaded} demo payments` })
      await fetchPayments()
    } catch (err) {
      setMessage({ type: 'error', text: err.message })
    } finally {
      setDemoLoading(false)
    }
  }

  const handleRunAnalysis = async () => {
    setAnalysisLoading(true)
    setMessage(null)
    try {
      const data = await api.runAnalysis()
      setMessage({
        type: 'success',
        text: `Analyzed ${data.analyzed} payments. Total leakage: $${data.summary?.total_leakage?.toFixed(2) || '0'}`,
      })
      setTimeout(() => navigate('/analysis'), 1500)
    } catch (err) {
      setMessage({ type: 'error', text: err.message })
    } finally {
      setAnalysisLoading(false)
    }
  }

  const handleAddPayment = async (e) => {
    e.preventDefault()
    setMessage(null)
    try {
      await api.createPayment({
        ...form,
        amount_sent: parseFloat(form.amount_sent),
        amount_received: parseFloat(form.amount_received),
        initiated_at: new Date(form.initiated_at).toISOString(),
      })
      setMessage({ type: 'success', text: 'Payment added successfully' })
      setShowAdd(false)
      await fetchPayments()
    } catch (err) {
      setMessage({ type: 'error', text: err.message })
    }
  }

  const handleCorridorChange = (val) => {
    const c = corridors.find(c => c.value === val)
    setForm({
      ...form,
      corridor: val,
      currency_sent: c?.send || 'USD',
      currency_received: c?.recv || 'EUR',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Message banner */}
      {message && (
        <div className={`rounded-lg px-4 py-3 text-sm flex items-center justify-between ${
          message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.text}
          <button onClick={() => setMessage(null)}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Action bar */}
      <div className="flex flex-wrap gap-3">
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Payment
        </button>
        <button
          onClick={handleLoadDemo}
          disabled={demoLoading}
          className="btn-secondary flex items-center gap-2"
        >
          {demoLoading ? (
            <span className="animate-spin w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full" />
          ) : (
            <Upload className="w-4 h-4" />
          )}
          Load Demo Data
        </button>
        {payments.length > 0 && (
          <button
            onClick={handleRunAnalysis}
            disabled={analysisLoading}
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          >
            {analysisLoading ? (
              <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Run Analysis
          </button>
        )}
      </div>

      {/* Add Payment Modal */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between px-5 py-4 border-b">
              <h3 className="font-semibold">Add Payment</h3>
              <button onClick={() => setShowAdd(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleAddPayment} className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Corridor</label>
                <select
                  value={form.corridor}
                  onChange={(e) => handleCorridorChange(e.target.value)}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg"
                >
                  {corridors.map(c => (
                    <option key={c.value} value={c.value}>
                      {c.value.replace('_', ' -> ')}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Amount Sent ({form.currency_sent})
                  </label>
                  <input
                    type="number"
                    required
                    step="0.01"
                    value={form.amount_sent}
                    onChange={(e) => setForm({ ...form, amount_sent: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg"
                    placeholder="10000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Amount Received ({form.currency_received})
                  </label>
                  <input
                    type="number"
                    required
                    step="0.01"
                    value={form.amount_received}
                    onChange={(e) => setForm({ ...form, amount_received: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg"
                    placeholder="9200"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">PSP</label>
                  <select
                    value={form.psp}
                    onChange={(e) => setForm({ ...form, psp: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg"
                  >
                    <option value="wise">Wise</option>
                    <option value="stripe">Stripe</option>
                    <option value="paypal">PayPal</option>
                    <option value="ofx">OFX</option>
                    <option value="bank_direct">Bank Direct</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                  <input
                    type="datetime-local"
                    value={form.initiated_at}
                    onChange={(e) => setForm({ ...form, initiated_at: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" className="btn-primary flex-1">Add Payment</button>
                <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Payments list */}
      {payments.length === 0 ? (
        <div className="card p-12 text-center">
          <CreditCard className="w-12 h-12 text-gray-300 mx-auto" />
          <h3 className="text-lg font-semibold mt-4">No payments yet</h3>
          <p className="text-gray-500 mt-1">Add your first payment or load demo data to get started.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">
              Your Payments
              <span className="ml-2 text-sm font-normal text-gray-400">({payments.length})</span>
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left px-5 py-3 font-medium text-gray-500">Corridor</th>
                  <th className="text-right px-5 py-3 font-medium text-gray-500">Sent</th>
                  <th className="text-right px-5 py-3 font-medium text-gray-500">Received</th>
                  <th className="text-left px-5 py-3 font-medium text-gray-500">PSP</th>
                  <th className="text-left px-5 py-3 font-medium text-gray-500">Date</th>
                  <th className="text-left px-5 py-3 font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {payments.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{p.currency_sent}</span>
                        <ArrowRight className="w-3 h-3 text-gray-400" />
                        <span className="font-medium">{p.currency_received}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-right font-medium">
                      ${p.amount_sent?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="px-5 py-3 text-right">
                      {p.currency_received === 'INR' ? '\u20B9' : p.currency_received === 'EUR' ? '\u20AC' : p.currency_received === 'GBP' ? '\u00A3' : '$'}
                      {p.amount_received?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="px-5 py-3">
                      <span className="badge-blue">{p.psp || 'N/A'}</span>
                    </td>
                    <td className="px-5 py-3 text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(p.initiated_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`badge ${p.status === 'completed' ? 'badge-green' : 'badge-yellow'}`}>
                        {p.status || 'pending'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
