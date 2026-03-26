import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Payments from './pages/Payments'
import Analysis from './pages/Analysis'
import Recommendations from './pages/Recommendations'
import Login from './pages/Login'
import api from './api'

export default function App() {
  const [isAuth, setIsAuth] = useState(api.isAuthenticated())

  useEffect(() => {
    const check = () => setIsAuth(api.isAuthenticated())
    window.addEventListener('storage', check)
    return () => window.removeEventListener('storage', check)
  }, [])

  const handleLogin = () => setIsAuth(true)
  const handleLogout = () => {
    api.logout()
    setIsAuth(false)
  }

  if (!isAuth) {
    return (
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/payments" element={<Payments />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
