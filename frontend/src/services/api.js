import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Response interceptor — normalise errors ──────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Unknown error'
    return Promise.reject(new Error(message))
  }
)

// ── API functions ────────────────────────────────────────────────

export const fetchHealth = () =>
  api.get('/api/health').then((r) => r.data)

export const fetchStatistics = () =>
  api.get('/api/graph/statistics').then((r) => r.data)

export const fetchGraph = (limit = 150, label = null) => {
  const params = { limit }
  if (label) params.label = label
  return api.get('/api/graph', { params }).then((r) => r.data)
}

export const fetchNode = (nodeId) =>
  api.get(`/api/graph/node/${nodeId}`).then((r) => r.data)

export const fetchNodeConnections = (nodeId) =>
  api.get(`/api/graph/node/${nodeId}/connections`).then((r) => r.data)

export const searchNodes = (q, limit = 20) =>
  api.get('/api/graph/search', { params: { q, limit } }).then((r) => r.data)

export default api
