import { useCallback, useEffect, useRef, useState } from 'react'
import { RefreshCw, Search as SearchIcon, X as XIcon } from 'lucide-react'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import StatisticsCards from '../components/StatisticsCards'
import GraphVisualization from '../components/GraphVisualization'
import NodeDetails from '../components/NodeDetails'
import {
  fetchHealth,
  fetchStatistics,
  fetchGraph,
  searchNodes,
} from '../services/api'

const GRAPH_LIMIT = 150

export default function Dashboard() {
  // ── Status ─────────────────────────────────────────────────────
  const [neo4jStatus, setNeo4jStatus] = useState('loading')

  // ── Stats ──────────────────────────────────────────────────────
  const [stats, setStats] = useState(null)
  const [statsLoading, setStatsLoading] = useState(true)

  // ── Graph ──────────────────────────────────────────────────────
  const [graphData, setGraphData] = useState(null)
  const [graphLoading, setGraphLoading] = useState(true)
  const [graphError, setGraphError] = useState(null)
  const [labelFilter, setLabelFilter] = useState(null)

  // ── Selected node ──────────────────────────────────────────────
  const [selectedNode, setSelectedNode] = useState(null)

  // ── Search ─────────────────────────────────────────────────────
  const [searchResults, setSearchResults] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchLoading, setSearchLoading] = useState(false)

  // ── Load health ────────────────────────────────────────────────
  const checkHealth = useCallback(async () => {
    try {
      const h = await fetchHealth()
      setNeo4jStatus(h.neo4j_connected ? 'ok' : 'error')
    } catch {
      setNeo4jStatus('error')
    }
  }, [])

  // ── Load statistics ────────────────────────────────────────────
  const loadStats = useCallback(async () => {
    setStatsLoading(true)
    try {
      const s = await fetchStatistics()
      setStats(s)
    } catch {
      /* stats are optional — don't block the page */
    } finally {
      setStatsLoading(false)
    }
  }, [])

  // ── Load graph ─────────────────────────────────────────────────
  const loadGraph = useCallback(async (label = null) => {
    setGraphLoading(true)
    setGraphError(null)
    setSearchResults(null)
    setSearchQuery('')
    try {
      const data = await fetchGraph(GRAPH_LIMIT, label)
      setGraphData(data)
    } catch (err) {
      setGraphError(err.message)
    } finally {
      setGraphLoading(false)
    }
  }, [])

  // ── Search ─────────────────────────────────────────────────────
  const handleSearch = useCallback(async (q) => {
    if (!q) {
      setSearchResults(null)
      setSearchQuery('')
      return
    }
    setSearchQuery(q)
    setSearchLoading(true)
    try {
      const results = await searchNodes(q)
      setSearchResults(results)
    } catch {
      setSearchResults([])
    } finally {
      setSearchLoading(false)
    }
  }, [])

  // ── Label filter ───────────────────────────────────────────────
  const handleLabelFilter = useCallback((label) => {
    setLabelFilter(label)
    setSelectedNode(null)
    loadGraph(label)
  }, [loadGraph])

  // ── Node navigation (from NodeDetails) ────────────────────────
  const handleNavigate = useCallback((node) => {
    setSelectedNode(node)
  }, [])

  // ── Init ───────────────────────────────────────────────────────
  useEffect(() => {
    checkHealth()
    loadStats()
    loadGraph(null)
    // Poll health every 30s
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const hasDetails = !!selectedNode

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Navbar onSearch={handleSearch} neo4jStatus={neo4jStatus} />

      <div style={{
        display: 'flex', flex: 1, overflow: 'hidden',
        marginTop: 'var(--navbar-h)',
      }}>
        {/* Sidebar */}
        <Sidebar
          activeLabelFilter={labelFilter}
          onLabelFilter={handleLabelFilter}
          stats={stats}
        />

        {/* Main area */}
        <main style={{
          marginLeft: 'var(--sidebar-w)',
          marginRight: hasDetails ? 'var(--details-w)' : 0,
          flex: 1, display: 'flex', flexDirection: 'column',
          overflow: 'hidden', transition: 'margin-right .2s ease',
        }}>
          {/* Stats row */}
          <StatisticsCards stats={stats} loading={statsLoading} />

          {/* Search results overlay */}
          {searchQuery && (
            <div style={{
              padding: '0 20px 12px',
              borderBottom: '1px solid var(--border)',
              background: 'var(--surface)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <SearchIcon size={14} color="var(--accent)" />
                <span style={{ fontSize: 13, fontWeight: 600 }}>
                  Search results for "{searchQuery}"
                </span>
                {searchResults && (
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    — {searchResults.length} found
                  </span>
                )}
                <button
                  onClick={() => { setSearchResults(null); setSearchQuery('') }}
                  style={{ marginLeft: 'auto', background: 'none', border: 'none',
                           cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}
                >
                  <XIcon size={14} />
                </button>
              </div>

              {searchLoading && <div className="spinner" style={{ width: 24, height: 24, borderWidth: 2 }} />}

              {searchResults && !searchLoading && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {searchResults.length === 0
                    ? <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>No results found.</span>
                    : searchResults.map((r) => (
                        <button
                          key={r.id}
                          onClick={() => setSelectedNode({ id: r.id, label: r.label, properties: r.properties })}
                          style={{
                            padding: '6px 12px', borderRadius: 999,
                            border: '1px solid var(--border)',
                            background: 'var(--surface-2)', cursor: 'pointer',
                            fontSize: 12, color: 'var(--text-primary)', fontWeight: 500,
                            transition: 'all .12s',
                          }}
                          onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.background = 'var(--accent-light)' }}
                          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--surface-2)' }}
                        >
                          <span style={{ marginRight: 5, opacity: .5 }}>{r.label}</span>
                          {r.name}
                        </button>
                      ))
                  }
                </div>
              )}
            </div>
          )}

          {/* Toolbar */}
          <div style={{
            padding: '8px 20px', display: 'flex', alignItems: 'center', gap: 10,
            borderBottom: '1px solid var(--border)', background: 'var(--surface)',
            flexShrink: 0,
          }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Showing top <strong>{GRAPH_LIMIT}</strong>
              {labelFilter ? ` ${labelFilter}` : ' Company'} nodes by out-degree
            </span>
            <div style={{ marginLeft: 'auto' }}>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => loadGraph(labelFilter)}
                style={{ display: 'flex', alignItems: 'center', gap: 5 }}
              >
                <RefreshCw size={12} />
                Refresh
              </button>
            </div>
          </div>

          {/* Graph canvas */}
          <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
            <GraphVisualization
              graphData={graphData}
              loading={graphLoading}
              error={graphError}
              onNodeSelect={setSelectedNode}
            />
          </div>
        </main>
      </div>

      {/* Node Details panel */}
      {selectedNode && (
        <NodeDetails
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          onNavigate={handleNavigate}
        />
      )}
    </div>
  )
}
