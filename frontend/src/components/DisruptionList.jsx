import { AlertTriangle, Anchor, Globe, Calendar } from 'lucide-react'

const DTYPE_ICON = {
  Hurricane: '🌀',
  Typhoon: '🌪️',
  'Tropical Cyclone': '🌊',
  Flood: '💧',
  'Weather Event': '⛈️',
}

function LevelBadge({ level }) {
  const styles = {
    High:   { background: '#FEF2F2', color: '#DC2626', border: '1px solid #FCA5A5' },
    Medium: { background: '#FFFBEB', color: '#D97706', border: '1px solid #FCD34D' },
    Low:    { background: '#ECFDF5', color: '#059669', border: '1px solid #6EE7B7' },
  }
  return (
    <span style={{
      fontSize: 11, fontWeight: 700, padding: '2px 9px',
      borderRadius: 999, letterSpacing: '.04em',
      ...(styles[level] || styles.Low),
    }}>
      {level?.toUpperCase()}
    </span>
  )
}

function ScoreBar({ score }) {
  const pct = Math.round((score || 0) * 100)
  const color = score >= 0.65 ? '#DC2626' : score >= 0.35 ? '#D97706' : '#059669'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 6 }}>
      <div style={{
        flex: 1, height: 5, background: 'var(--border)', borderRadius: 999, overflow: 'hidden',
      }}>
        <div style={{
          height: '100%', width: `${pct}%`,
          background: `linear-gradient(90deg, ${color}80, ${color})`,
          borderRadius: 999,
          transition: 'width 0.6s ease',
        }} />
      </div>
      <span style={{ fontSize: 11, fontWeight: 700, color, minWidth: 28, textAlign: 'right' }}>
        {pct}
      </span>
    </div>
  )
}

export default function DisruptionList({ disruptions = [], loading = false, onSelect }) {
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 32 }}>
        <div className="spinner" style={{ width: 28, height: 28, borderWidth: 2 }} />
      </div>
    )
  }

  if (!disruptions.length) {
    return (
      <div style={{
        textAlign: 'center', padding: 32, color: 'var(--text-muted)', fontSize: 13,
      }}>
        <AlertTriangle size={32} style={{ opacity: 0.3, marginBottom: 8, display: 'block', margin: '0 auto 8px' }} />
        No disruption data available.<br />Run the preprocessing script first.
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {disruptions.map((ev, idx) => (
        <div
          key={ev.event_name + idx}
          onClick={() => onSelect?.(ev)}
          style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '12px 14px',
            cursor: onSelect ? 'pointer' : 'default',
            transition: 'all .15s',
            borderLeft: `4px solid ${ev.risk_level === 'High' ? '#DC2626' : ev.risk_level === 'Medium' ? '#D97706' : '#059669'}`,
          }}
          onMouseEnter={e => { if (onSelect) e.currentTarget.style.boxShadow = 'var(--shadow)' }}
          onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none' }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
            {/* Icon */}
            <div style={{ fontSize: 20, flexShrink: 0, lineHeight: 1.2 }}>
              {DTYPE_ICON[ev.disruption_type] || '⛈️'}
            </div>

            {/* Content */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <span style={{
                  fontSize: 13, fontWeight: 600, color: 'var(--text-primary)',
                  flex: 1, minWidth: 0,
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                }}>
                  {ev.event_name}
                </span>
                <LevelBadge level={ev.risk_level} />
              </div>

              {/* Meta row */}
              <div style={{
                display: 'flex', flexWrap: 'wrap', gap: '6px 14px',
                marginTop: 5, fontSize: 11, color: 'var(--text-muted)',
              }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Anchor size={10} />
                  {ev.ports_count} port{ev.ports_count !== 1 ? 's' : ''}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Globe size={10} />
                  {ev.countries_affected?.slice(0, 2).join(', ')}
                  {ev.countries_affected?.length > 2 ? ` +${ev.countries_affected.length - 2}` : ''}
                </span>
                {ev.years?.length > 0 && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Calendar size={10} />
                    {ev.years[0]}{ev.years.length > 1 ? `–${ev.years[ev.years.length - 1]}` : ''}
                  </span>
                )}
                <span>Severity {ev.mean_severity?.toFixed(1)}/3</span>
                <span>{ev.total_days?.toFixed(0)} total days impacted</span>
              </div>

              <ScoreBar score={ev.risk_score} />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
