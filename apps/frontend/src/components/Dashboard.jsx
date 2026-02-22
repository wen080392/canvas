import React, { useState, useEffect } from 'react'
import './Dashboard.css'

const API_URL = window.API_BASE || 'http://localhost:8000'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_URL}/dashboard/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.status === 401) {
        window.location.href = '/login.html'
        return
      }

      if (!response.ok) throw new Error('Failed to fetch stats')

      const data = await response.json()
      setStats(data)
      setError(null)
    } catch (err) {
      console.error('Error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="dashboard-loading">⏳ Carregando...</div>
  if (error) return <div className="dashboard-error">❌ {error}</div>
  if (!stats) return <div className="dashboard-empty">Sem dados</div>

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {/* Critical Issues */}
        <div className="dashboard-card critical">
          <div className="card-icon">🚨</div>
          <div className="card-content">
            <div className="card-label">Critical Issues</div>
            <div className="card-value">{stats.critical_count || 0}</div>
            <div className="card-desc">Requerem ação imediata</div>
          </div>
        </div>

        {/* High Issues */}
        <div className="dashboard-card high">
          <div className="card-icon">⚠️</div>
          <div className="card-content">
            <div className="card-label">High Issues</div>
            <div className="card-value">{stats.high_count || 0}</div>
            <div className="card-desc">Prioridade alta</div>
          </div>
        </div>

        {/* Medium Issues */}
        <div className="dashboard-card medium">
          <div className="card-icon">⚡</div>
          <div className="card-content">
            <div className="card-label">Medium Issues</div>
            <div className="card-value">{stats.medium_count || 0}</div>
            <div className="card-desc">Atenção recomendada</div>
          </div>
        </div>

        {/* Low Issues */}
        <div className="dashboard-card low">
          <div className="card-icon">ℹ️</div>
          <div className="card-content">
            <div className="card-label">Low Issues</div>
            <div className="card-value">{stats.low_count || 0}</div>
            <div className="card-desc">Informativo</div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="dashboard-summary">
        <h3>📊 Resumo da Segurança</h3>
        <div className="summary-stats">
          <div className="stat">
            <span className="stat-label">Total de Issues:</span>
            <span className="stat-value">{stats.total_issues || 0}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Scans Completados:</span>
            <span className="stat-value">{stats.scans_completed || 0}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Compliance Score:</span>
            <span className="stat-value">{stats.compliance_score || 0}%</span>
          </div>
          <div className="stat">
            <span className="stat-label">Projetos Ativos:</span>
            <span className="stat-value">{stats.active_projects || 0}</span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="dashboard-activity">
        <h3>📝 Atividade Recente</h3>
        {stats.recent_scans && stats.recent_scans.length > 0 ? (
          <ul className="activity-list">
            {stats.recent_scans.map((scan, idx) => (
              <li key={idx} className="activity-item">
                <span className="activity-time">{scan.created_at}</span>
                <span className="activity-text">{scan.filename}</span>
                <span className={`activity-status ${scan.status.toLowerCase()}`}>
                  {scan.status}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">Nenhuma atividade recente</p>
        )}
      </div>
    </div>
  )
}
