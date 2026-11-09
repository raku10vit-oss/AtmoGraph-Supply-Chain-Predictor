import { Building2, Globe, Factory, Anchor, Boxes, Network } from 'lucide-react'

const NODE_TYPES = [
  { label: 'Company',        color: 'var(--node-company)',  icon: Building2, badge: 'badge-blue' },
  { label: 'Country',        color: 'var(--node-country)',  icon: Globe,     badge: 'badge-green' },
  { label: 'Industry',       color: 'var(--node-industry)', icon: Factory,   badge: 'badge-orange' },
  { label: 'Port',           color: 'var(--node-port)',     icon: Anchor,    badge: 'badge-purple' },
  { label: 'AnonNode',       color: 'var(--node-anon)',     icon: Network,   badge: 'badge-grey' },
  { label: 'DisruptionEvent',color: 'var(--node-event)',    icon: Boxes,     badge: 'badge-red' },
]

export default function Sidebar({ activeLabelFilter, onLabelFilter, stats }) {
  return (
    <aside style={{
      position: 'fixed', top: 'var(--navbar-h)', left: 0, bottom: 0,
      width: 'var(--sidebar-w)',
      background: 'var(--surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column',
      overflowY: 'auto', zIndex: 50,
    }}>

      {/* Section: Graph View */}
      <div style={{ padding: '16px 16px 8px' }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)',
                      letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 8 }}>
          Graph View
        </div>

        {/* Show all */}
        <button
          onClick={() => onLabelFilter(null)}
          style={{
            width: '100%', textAlign: 'left', padding: '8px 10px',
            border: 'none', borderRadius: 7, cursor: 'pointer', fontSize: 13,
            fontWeight: 500,
            background: !activeLabelFilter ? 'var(--accent-light)' : 'transparent',
            color: !activeLabelFilter ? 'var(--accent)' : 'var(--text-secondary)',
            transition: 'all .15s',
            display: 'flex', alignItems: 'center', gap: 8,
          }}
        >
          <span style={{ fontSize: 16 }}>⬡</span>
          All Node Types
          {stats?.total_nodes != null && (
            <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>
              {stats.total_nodes.toLocaleString()}
            </span>
          )}
        </button>
      </div>

      {/* Divider */}
      <div style={{ height: 1, background: 'var(--border)', margin: '4px 16px' }} />

      {/* Node type filters */}
      <div style={{ padding: '8px 16px' }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)',
                      letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 8 }}>
          Filter by Type
        </div>
        {NODE_TYPES.map(({ label, color, icon: Icon }) => {
          const count = stats?.[label.toLowerCase() === 'company' ? 'companies'
                              : label.toLowerCase() === 'country' ? 'countries'
                              : label.toLowerCase() === 'industry' ? 'industries'
                              : label.toLowerCase() === 'port' ? 'ports'
                              : label.toLowerCase() === 'anonnode' ? 'anon_nodes'
                              : 'disruption_events'] ?? 0

          const isActive = activeLabelFilter === label
          return (
            <button
              key={label}
              onClick={() => onLabelFilter(isActive ? null : label)}
              style={{
                width: '100%', textAlign: 'left', padding: '7px 10px',
                border: 'none', borderRadius: 7, cursor: 'pointer', fontSize: 13,
                background: isActive ? `${color}18` : 'transparent',
                color: isActive ? color : 'var(--text-secondary)',
                transition: 'all .15s',
                display: 'flex', alignItems: 'center', gap: 8,
                marginBottom: 2,
                borderLeft: isActive ? `3px solid ${color}` : '3px solid transparent',
              }}
            >
              <span style={{
                width: 8, height: 8, borderRadius: '50%',
                background: color, flexShrink: 0,
              }} />
              <Icon size={13} />
              <span style={{ flex: 1 }}>{label}</span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {count > 0 ? count.toLocaleString() : '—'}
              </span>
            </button>
          )
        })}
      </div>

      {/* Divider */}
      <div style={{ height: 1, background: 'var(--border)', margin: '8px 16px' }} />

      {/* Legend */}
      <div style={{ padding: '8px 16px' }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)',
                      letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 10 }}>
          Relationship Types
        </div>
        {[
          { label: 'SUPPLIES_TO',  color: 'var(--node-company)' },
          { label: 'LOCATED_IN',   color: 'var(--node-country)' },
          { label: 'BELONGS_TO',   color: 'var(--node-industry)' },
          { label: 'CONNECTS_TO',  color: 'var(--node-anon)' },
          { label: 'AFFECTED_BY',  color: 'var(--node-event)' },
          { label: 'PORT_IN',      color: 'var(--node-port)' },
        ].map(({ label, color }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8,
                                    marginBottom: 6, fontSize: 12 }}>
            <div style={{ width: 20, height: 2, background: color, borderRadius: 1, flexShrink: 0 }} />
            <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div style={{ marginTop: 'auto', padding: '12px 16px',
                    borderTop: '1px solid var(--border)',
                    fontSize: 11, color: 'var(--text-muted)' }}>
        <div style={{ fontWeight: 600, marginBottom: 2 }}>AtmoGraph v1.0</div>
        <div>Week 1 · Graph Foundation</div>
        <div style={{ marginTop: 4, fontSize: 10 }}>
          Data: CC BY-NC 4.0 / Academic use
        </div>
      </div>
    </aside>
  )
}
