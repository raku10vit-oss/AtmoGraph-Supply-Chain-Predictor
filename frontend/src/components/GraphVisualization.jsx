import { useCallback, useEffect, useState } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from 'reactflow'
import 'reactflow/dist/style.css'
import dagre from '@dagrejs/dagre'
import { Building2, Globe, Factory, Anchor, Network, AlertTriangle } from 'lucide-react'

// ── Node colour/icon map ─────────────────────────────────────────
const LABEL_CONFIG = {
  Company:        { color: '#2563EB', bg: '#EFF6FF', icon: Building2,  abbr: 'CO' },
  Country:        { color: '#059669', bg: '#ECFDF5', icon: Globe,      abbr: 'CN' },
  Industry:       { color: '#D97706', bg: '#FFFBEB', icon: Factory,    abbr: 'IN' },
  Port:           { color: '#7C3AED', bg: '#F5F3FF', icon: Anchor,     abbr: 'PT' },
  AnonNode:       { color: '#64748B', bg: '#F1F5F9', icon: Network,    abbr: 'AN' },
  DisruptionEvent:{ color: '#DC2626', bg: '#FEF2F2', icon: AlertTriangle, abbr: 'DE' },
}
const DEFAULT_CONFIG = { color: '#64748B', bg: '#F1F5F9', abbr: '??' }

// ── Custom Node component ────────────────────────────────────────
function SupplyChainNode({ data, selected }) {
  const cfg = LABEL_CONFIG[data.label] || DEFAULT_CONFIG
  const Icon = cfg.icon
  const name = data.properties?.name || data.properties?.node_id || `Node ${data.id}`

  return (
    <div style={{
      minWidth: 160, maxWidth: 200,
      background: '#fff',
      border: `2px solid ${selected ? cfg.color : '#E2E8F0'}`,
      borderLeft: `4px solid ${cfg.color}`,
      borderRadius: 8,
      boxShadow: selected
        ? `0 0 0 3px ${cfg.color}30, 0 4px 12px rgba(0,0,0,.1)`
        : '0 2px 6px rgba(0,0,0,.07)',
      cursor: 'pointer',
      transition: 'border-color .15s, box-shadow .15s',
      overflow: 'hidden',
    }}>
      <Handle type="target" position={Position.Top} style={{ background: cfg.color, width: 7, height: 7 }} />

      {/* Header */}
      <div style={{
        background: cfg.bg, padding: '6px 10px',
        display: 'flex', alignItems: 'center', gap: 6,
        borderBottom: `1px solid ${cfg.color}22`,
      }}>
        {Icon && <Icon size={12} color={cfg.color} />}
        <span style={{ fontSize: 10, fontWeight: 600, color: cfg.color, letterSpacing: '.04em' }}>
          {data.label}
        </span>
      </div>

      {/* Body */}
      <div style={{ padding: '7px 10px' }}>
        <div style={{
          fontSize: 12, fontWeight: 600, color: '#0F172A',
          overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis',
          maxWidth: 170,
        }} title={name}>
          {name}
        </div>
        {data.properties?.country && (
          <div style={{ fontSize: 10, color: '#64748B', marginTop: 2 }}>
            📍 {data.properties.country}
          </div>
        )}
        {data.properties?.industry && (
          <div style={{ fontSize: 10, color: '#64748B' }}>
            🏭 {data.properties.industry}
          </div>
        )}
        {data.properties?.type && (
          <span style={{
            display: 'inline-block', marginTop: 4,
            fontSize: 9, fontWeight: 600, letterSpacing: '.06em',
            padding: '1px 5px', borderRadius: 3,
            background: cfg.bg, color: cfg.color,
          }}>
            {data.properties.type?.toUpperCase()}
          </span>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: cfg.color, width: 7, height: 7 }} />
    </div>
  )
}

const nodeTypes = { supplyChain: SupplyChainNode }

// ── Layout with dagre ────────────────────────────────────────────
function applyDagreLayout(nodes, edges) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'LR', nodesep: 60, ranksep: 120, marginx: 60, marginy: 60 })

  nodes.forEach((n) => g.setNode(n.id, { width: 190, height: 70 }))
  edges.forEach((e) => {
    if (g.hasNode(String(e.source)) && g.hasNode(String(e.target))) {
      g.setEdge(String(e.source), String(e.target))
    }
  })

  dagre.layout(g)

  return nodes.map((n) => {
    const pos = g.node(n.id)
    return pos
      ? { ...n, position: { x: pos.x - 95, y: pos.y - 35 } }
      : { ...n, position: { x: Math.random() * 800, y: Math.random() * 600 } }
  })
}

// ── Transform backend data → React Flow format ───────────────────
function transformGraph(graphData) {
  if (!graphData?.nodes) return { nodes: [], edges: [] }

  const rfNodes = graphData.nodes.map((n) => ({
    id: String(n.id),
    type: 'supplyChain',
    position: { x: 0, y: 0 }, // will be overwritten by dagre
    data: { id: n.id, label: n.label, properties: n.properties },
  }))

  const rfEdges = graphData.relationships.map((r) => {
    const cfg = LABEL_CONFIG[r.type === 'SUPPLIES_TO' ? 'Company'
              : r.type === 'LOCATED_IN' ? 'Country'
              : r.type === 'BELONGS_TO' ? 'Industry'
              : r.type === 'PORT_IN' ? 'Port'
              : r.type === 'AFFECTED_BY' ? 'DisruptionEvent'
              : 'AnonNode'] || DEFAULT_CONFIG
    return {
      id: String(r.id),
      source: String(r.source_id),
      target: String(r.target_id),
      label: r.type,
      type: 'default',
      animated: r.type === 'SUPPLIES_TO',
      style: { stroke: cfg.color, strokeWidth: 1.5, opacity: .7 },
      labelStyle: { fontSize: 9, fill: '#94A3B8' },
      labelBgStyle: { fill: 'white', fillOpacity: .85 },
      markerEnd: { type: MarkerType.ArrowClosed, color: cfg.color, width: 14, height: 14 },
    }
  })

  const layoutedNodes = applyDagreLayout(rfNodes, rfEdges)
  return { nodes: layoutedNodes, edges: rfEdges }
}

// ── Main component ───────────────────────────────────────────────
export default function GraphVisualization({ graphData, loading, error, onNodeSelect }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    if (!graphData) return
    const { nodes: n, edges: e } = transformGraph(graphData)
    setNodes(n)
    setEdges(e)
  }, [graphData])

  const onNodeClick = useCallback((_, node) => {
    onNodeSelect(node.data)
  }, [onNodeSelect])

  // Loading overlay
  if (loading) {
    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column',
                    alignItems: 'center', justifyContent: 'center', gap: 16,
                    color: 'var(--text-muted)' }}>
        <div className="spinner" />
        <div style={{ fontSize: 14, fontWeight: 500 }}>Loading supply chain graph…</div>
        <div style={{ fontSize: 12 }}>Fetching top nodes from Neo4j</div>
      </div>
    )
  }

  // Error overlay
  if (error) {
    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column',
                    alignItems: 'center', justifyContent: 'center', gap: 12,
                    padding: 32, textAlign: 'center' }}>
        <div style={{ width: 56, height: 56, borderRadius: 14,
                      background: 'var(--danger-bg)', display: 'flex',
                      alignItems: 'center', justifyContent: 'center' }}>
          <AlertTriangle size={28} color="var(--danger)" />
        </div>
        <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>
          Cannot load graph
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 380 }}>
          {error}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4,
                      background: 'var(--surface-2)', padding: '8px 14px',
                      borderRadius: 8, border: '1px solid var(--border)', textAlign: 'left' }}>
          <strong>Checklist:</strong><br />
          1. Is Neo4j running? (Desktop / Aura)<br />
          2. Did you fill in <code>backend/.env</code>?<br />
          3. Run <code>uvicorn app.main:app --reload</code> in <code>backend/</code><br />
          4. Run <code>python scripts/import_supply_chain.py</code>
        </div>
      </div>
    )
  }

  // Empty state
  if (!nodes.length) {
    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column',
                    alignItems: 'center', justifyContent: 'center', gap: 12,
                    color: 'var(--text-muted)' }}>
        <Network size={48} style={{ opacity: .3 }} />
        <div style={{ fontSize: 15, fontWeight: 500 }}>No graph data</div>
        <div style={{ fontSize: 13 }}>Import datasets then refresh.</div>
      </div>
    )
  }

  return (
    <div style={{ flex: 1, position: 'relative' }}>
      {/* Node count badge */}
      <div style={{
        position: 'absolute', top: 12, right: 12, zIndex: 10,
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 999, padding: '4px 12px', fontSize: 12,
        color: 'var(--text-secondary)', boxShadow: 'var(--shadow-sm)',
        display: 'flex', gap: 6,
      }}>
        <span style={{ color: 'var(--accent)', fontWeight: 600 }}>{nodes.length}</span> nodes ·
        <span style={{ color: 'var(--accent)', fontWeight: 600 }}>{edges.length}</span> edges
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.1}
        maxZoom={2}
        attributionPosition="bottom-right"
        style={{ background: '#F8FAFC' }}
      >
        <Controls style={{ boxShadow: 'var(--shadow)', borderRadius: 10,
                           overflow: 'hidden', border: '1px solid var(--border)' }} />
        <MiniMap
          style={{ border: '1px solid var(--border)', borderRadius: 10, boxShadow: 'var(--shadow)' }}
          nodeColor={(n) => {
            const cfg = LABEL_CONFIG[n.data?.label]
            return cfg?.color || '#94A3B8'
          }}
          nodeStrokeWidth={2}
        />
        <Background color="#E2E8F0" gap={20} size={1} />
      </ReactFlow>
    </div>
  )
}
