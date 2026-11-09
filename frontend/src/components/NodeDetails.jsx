import { useEffect, useState } from 'react'
import { X, ExternalLink, ChevronRight, Loader } from 'lucide-react'
import { fetchNodeConnections } from '../services/api'

const LABEL_COLORS = {
  Company: '#2563EB', Country: '#059669', Industry: '#D97706',
  Port: '#7C3AED', AnonNode: '#64748B', DisruptionEvent: '#DC2626',
}

function PropRow({ label, value }) {
  if (!value && value !== 0) return null
  return (
    <div style={{ display: 'flex', gap: 8, padding: '5px 0',
                  borderBottom: '1px solid var(--border)', fontSize: 12 }}>
      <span style={{ color: 'var(--text-muted)', minWidth: 100, flexShrink: 0 }}>{label}</span>
      <span style={{ color: 'var(--text-primary)', fontWeight: 500, wordBreak: 'break-word' }}>
        {String(value)}
      </span>
    </div>
  )
}

export default function NodeDetails({ node, onClose, onNavigate }) {
  const [connections, setConnections] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!node) return
    setConnections(null)
    setError(null)
    setLoading(true)
    fetchNodeConnections(node.id)
      .then((data) => { setConnections(data); setLoading(false) })
      .catch((err) => { setError(err.message); setLoading(false) })
  }, [node?.id])

  if (!node) return null

  const color = LABEL_COLORS[node.label] || '#64748B'
  const name = node.properties?.name || node.properties?.node_id || `Node ${node.id}`
  const props = node.properties || {}

  // Build connected node list (excluding the focused node)
  const connectedNodes = connections
    ? connections.nodes.filter((n) => n.id !== node.id)
    : []
  const relMap = {}
  connections?.relationships?.forEach((r) => {
    const otherId = r.source_id === node.id ? r.target_id : r.source_id
    relMap[otherId] = r.type
  })

  return (
    <aside
      className="slide-in"
      style={{
        position: 'fixed', top: 'var(--navbar-h)', right: 0, bottom: 0,
        width: 'var(--details-w)',
        background: 'var(--surface)',
        borderLeft: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column',
        zIndex: 60, overflowY: 'auto',
        boxShadow: '-4px 0 20px rgba(0,0,0,.06)',
      }}
    >
      {/* Header */}
      <div style={{
        padding: '14px 16px', borderBottom: '1px solid var(--border)',
        display: 'flex', alignItems: 'flex-start', gap: 10,
        background: `${color}08`,
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: 8, flexShrink: 0,
          background: `${color}20`,
          border: `2px solid ${color}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontWeight: 700, color,
        }}>
          {node.label?.slice(0, 2).toUpperCase()}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 10, fontWeight: 600, color, letterSpacing: '.06em',
                        textTransform: 'uppercase', marginBottom: 2 }}>
            {node.label}
          </div>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)',
                        overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}
               title={name}>
            {name}
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 1 }}>
            ID: {node.id}
          </div>
        </div>
        <button onClick={onClose} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: 'var(--text-muted)', padding: 2, flexShrink: 0,
          borderRadius: 4, display: 'flex',
        }}>
          <X size={16} />
        </button>
      </div>

      {/* Properties */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)',
                      letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 8 }}>
          Properties
        </div>
        {Object.entries(props).map(([k, v]) => (
          <PropRow key={k} label={k} value={v} />
        ))}
        {Object.keys(props).length === 0 && (
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>No properties</div>
        )}
      </div>

      {/* Connections */}
      <div style={{ padding: '12px 16px', flex: 1 }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)',
                      letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 8 }}>
          Connected Nodes
          {connections && (
            <span style={{ marginLeft: 6, fontWeight: 400, fontSize: 10 }}>
              ({connectedNodes.length})
            </span>
          )}
        </div>

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8,
                        color: 'var(--text-muted)', fontSize: 12, padding: '8px 0' }}>
            <Loader size={13} style={{ animation: 'spin .7s linear infinite' }} />
            Loading connections…
          </div>
        )}

        {error && (
          <div style={{ fontSize: 12, color: 'var(--danger)', padding: '6px 0' }}>{error}</div>
        )}

        {connectedNodes.map((cn) => {
          const cnColor = LABEL_COLORS[cn.label] || '#64748B'
          const cnName = cn.properties?.name || cn.properties?.node_id || `Node ${cn.id}`
          const relType = relMap[cn.id] || ''
          return (
            <button
              key={cn.id}
              onClick={() => onNavigate(cn)}
              style={{
                width: '100%', textAlign: 'left', padding: '8px 10px',
                marginBottom: 4, borderRadius: 7, cursor: 'pointer',
                border: '1px solid var(--border)',
                background: 'var(--surface-2)',
                display: 'flex', alignItems: 'center', gap: 8,
                transition: 'all .12s',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = cnColor; e.currentTarget.style.background = `${cnColor}08` }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--surface-2)' }}
            >
              <div style={{
                width: 8, height: 8, borderRadius: '50%',
                background: cnColor, flexShrink: 0,
              }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-primary)',
                              overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                  {cnName}
                </div>
                {relType && (
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{relType}</div>
                )}
              </div>
              <ChevronRight size={12} color="var(--text-muted)" />
            </button>
          )
        })}

        {!loading && !error && connectedNodes.length === 0 && (
          <div style={{ fontSize: 12, color: 'var(--text-muted)', padding: '6px 0' }}>
            No connections found.
          </div>
        )}
      </div>
    </aside>
  )
}
