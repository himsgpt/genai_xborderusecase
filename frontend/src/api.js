const BASE_URL = 'http://localhost:8000'

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('xborder_token')
  }

  setToken(token) {
    this.token = token
    if (token) {
      localStorage.setItem('xborder_token', token)
    } else {
      localStorage.removeItem('xborder_token')
    }
  }

  getToken() {
    return this.token
  }

  isAuthenticated() {
    return !!this.token
  }

  async request(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers,
    })

    if (res.status === 401) {
      this.setToken(null)
      window.location.href = '/login'
      throw new Error('Unauthorized')
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Request failed')
    }

    return res.json()
  }

  // Auth
  async register(data) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async login(email, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    this.setToken(data.access_token)
    return data
  }

  logout() {
    this.setToken(null)
  }

  // Payments
  async getPayments() {
    return this.request('/api/payments')
  }

  async createPayment(data) {
    return this.request('/api/payments', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async loadDemoPayments() {
    return this.request('/api/payments/demo', { method: 'POST' })
  }

  // Analysis
  async runAnalysis() {
    return this.request('/api/analysis/run', { method: 'POST' })
  }

  async getAnalysisSummary() {
    return this.request('/api/analysis/summary')
  }

  async getAnalyses() {
    return this.request('/api/analysis')
  }

  async getAnalysisDetail(id) {
    return this.request(`/api/analysis/${id}`)
  }

  // Recommendations
  async getRecommendations() {
    return this.request('/api/recommendations')
  }

  async updateRecommendationStatus(id, status) {
    return this.request(`/api/recommendations/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })
  }

  // Demo
  async runFullDemo() {
    return this.request('/api/demo/full-pipeline', { method: 'POST' })
  }

  // Health
  async health() {
    return this.request('/health')
  }
}

export const api = new ApiClient()
export default api
