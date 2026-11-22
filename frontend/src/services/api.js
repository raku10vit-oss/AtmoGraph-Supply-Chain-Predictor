import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
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

// ════════════════════════════════════════════════════════════════
//  WEEK 1 — Graph API functions (unchanged)
// ════════════════════════════════════════════════════════════════

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

// ════════════════════════════════════════════════════════════════
//  WEEK 2 — Prediction API functions
// ════════════════════════════════════════════════════════════════

/** Overall supply chain risk overview */
export const fetchPredictionOverview = () =>
  api.get('/api/predictions/overview').then((r) => r.data)

/** Ranked list of disruption events */
export const fetchDisruptions = (limit = 20) =>
  api.get('/api/predictions/disruptions', { params: { limit } }).then((r) => r.data)

/** Companies at risk */
export const fetchAffectedCompanies = (limit = 50) =>
  api.get('/api/predictions/affected-companies', { params: { limit } }).then((r) => r.data)

/** Full risk profile for a named company */
export const fetchCompanyRiskProfile = (companyName) =>
  api.get(`/api/predictions/company/${encodeURIComponent(companyName)}`).then((r) => r.data)

/** Country disruption impact */
export const fetchCountryImpact = (country) =>
  api.get(`/api/predictions/impact/${encodeURIComponent(country)}`).then((r) => r.data)

/** BFS propagation from a node */
export const fetchPropagation = (nodeId, maxHops = 3) =>
  api.get(`/api/predictions/propagation/${nodeId}`, { params: { max_hops: maxHops } }).then((r) => r.data)

/** Disruption scenarios */
export const fetchScenarios = (limit = 30) =>
  api.get('/api/predictions/scenarios', { params: { limit } }).then((r) => r.data)

export default api
