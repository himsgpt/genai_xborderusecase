import { useState } from 'react'
import { Globe, ArrowRight, Zap } from 'lucide-react'
import api from '../api'

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false)
  const [loading, setLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    email: '',
    password: '',
    name: '',
    company: '',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegister) {
        await api.register(form)
      }
      await api.login(form.email, form.password)
      onLogin()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDemo = async () => {
    setError('')
    setDemoLoading(true)
    try {
      const data = await api.runFullDemo()
      api.setToken(data.auth.token)
      onLogin()
    } catch (err) {
      setError(err.message)
    } finally {
      setDemoLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel - branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gray-900 text-white flex-col justify-between p-12">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-brand-500 rounded-lg flex items-center justify-center">
            <Globe className="w-6 h-6" />
          </div>
          <span className="font-bold text-xl">XBorder</span>
        </div>

        <div className="space-y-6">
          <h1 className="text-4xl font-bold leading-tight">
            Stop losing money on <br />
            <span className="text-brand-400">cross-border payments</span>
          </h1>
          <p className="text-lg text-gray-400 max-w-md">
            Our AI engine analyzes your payment flows, exposes hidden fees, and tells you
            exactly where your money leaks -- with actionable fixes.
          </p>
          <div className="grid grid-cols-3 gap-4 pt-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl font-bold text-brand-400">2.8%</div>
              <div className="text-xs text-gray-400 mt-1">Avg. hidden cost</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl font-bold text-emerald-400">$11K+</div>
              <div className="text-xs text-gray-400 mt-1">Annual savings</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl font-bold text-amber-400">3</div>
              <div className="text-xs text-gray-400 mt-1">Corridors tracked</div>
            </div>
          </div>
        </div>

        <p className="text-sm text-gray-500">
          Cross-Border Payment Intelligence Platform v0.1
        </p>
      </div>

      {/* Right panel - form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-8">
          <div className="lg:hidden flex items-center gap-3 justify-center">
            <div className="w-10 h-10 bg-brand-500 rounded-lg flex items-center justify-center">
              <Globe className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl">XBorder Intelligence</span>
          </div>

          <div className="text-center">
            <h2 className="text-2xl font-bold">
              {isRegister ? 'Create your account' : 'Welcome back'}
            </h2>
            <p className="text-gray-500 mt-1">
              {isRegister ? 'Start optimizing payments in minutes' : 'Sign in to your dashboard'}
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
                  <input
                    type="text"
                    value={form.company}
                    onChange={(e) => setForm({ ...form, company: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
                    placeholder="Company name"
                  />
                </div>
              </>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
                placeholder="you@company.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
                placeholder="Min 6 characters"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3"
            >
              {loading ? (
                <span className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <>
                  {isRegister ? 'Create Account' : 'Sign In'}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center">
              <span className="px-4 bg-gray-50 text-sm text-gray-500">or</span>
            </div>
          </div>

          <button
            onClick={handleDemo}
            disabled={demoLoading}
            className="btn-secondary w-full flex items-center justify-center gap-2 py-3"
          >
            {demoLoading ? (
              <span className="animate-spin w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full" />
            ) : (
              <>
                <Zap className="w-4 h-4 text-amber-500" />
                Try Demo (No signup needed)
              </>
            )}
          </button>

          <p className="text-center text-sm text-gray-500">
            {isRegister ? 'Already have an account? ' : "Don't have an account? "}
            <button
              onClick={() => { setIsRegister(!isRegister); setError('') }}
              className="text-brand-600 font-medium hover:text-brand-700"
            >
              {isRegister ? 'Sign in' : 'Register'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
