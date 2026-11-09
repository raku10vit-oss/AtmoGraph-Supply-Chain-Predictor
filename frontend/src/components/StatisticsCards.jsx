import { Network, Building2, Globe, Factory, Anchor, Share2 } from 'lucide-react'

const STAT_CONFIG = [
  { key: 'total_nodes',         label: 'Total Nodes',    icon: Network,   color: '#2563EB', bg: '#EFF6FF' },
  { key: 'total_relationships', label: 'Relationships',  icon: Share2,    color: '#7C3AED', bg: '#F5F3FF' },
  { key: 'companies',           label: 'Companies',      icon: Building2, color: '#0369A1', bg: '#E0F2FE' },
  { key: 'countries',           label: 'Countries',      icon: Globe,     color: '#059669', bg: '#ECFDF5' },
  { key: 'industries',          label: 'Industries',     icon: Factory,   color: '#D97706', bg: '#FFFBEB' },
  { key: 'ports',               label: 'Ports',          icon: Anchor,    color: '#7C3AED', bg: '#F5F3FF' },
]

function StatCard({ label, value, icon: Icon, color, bg, loading }) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      padding: '14px 18px',
      display: 'flex', alignItems: 'center', gap: 14,
      boxShadow: 'var(--shadow-sm)',
      transition: 'transform .15s, box-shadow .15s',
      cursor: 'default',
      flex: 1, minWidth: 140,
    }}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = 'var(--shadow)'; }}
      onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; }}
    >
      {/* Icon */}
      <div style={{
        width: 42, height: 42, borderRadius: 10,
        background: bg, flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={20} color={color} />
      </div>
      {/* Text */}
      <div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 500, marginBottom: 2 }}>
          {label}
        </div>
        {loading ? (
          <div style={{ height: 22, width: 60, borderRadius: 4,
                        background: 'var(--border)', animation: 'pulse 1.4s ease infinite' }} />
        ) : (
          <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1 }}>
            {value != null ? Number(value).toLocaleString() : '—'}
          </div>
        )}
      </div>
    </div>
  )
}

export default function StatisticsCards({ stats, loading }) {
  return (
    <div style={{
      display: 'flex', flexWrap: 'wrap', gap: 12,
      padding: '16px 20px',
      background: 'var(--bg)',
    }}>
      {STAT_CONFIG.map(({ key, label, icon, color, bg }) => (
        <StatCard
          key={key}
          label={label}
          value={stats?.[key]}
          icon={icon}
          color={color}
          bg={bg}
          loading={loading}
        />
      ))}
    </div>
  )
}
