/**
 * RiskChart — horizontal bar chart for 5 risk signal scores.
 * Pure CSS, no external chart library.
 */

const SIGNAL_COLORS = {
  'Port Exposure':          '#7C3AED',
  'Supplier Concentration': '#D97706',
  'Graph Centrality':       '#2563EB',
  'Industry Vulnerability': '#DC2626',
  'Network Propagation':    '#059669',
}

function Bar({ label, score, weight, weightedScore, explanation, color }) {
  const pct = Math.round(score * 100)
  const level = score >= 0.65 ? 'High' : score >= 0.35 ? 'Medium' : 'Low'
  const levelColor = { High: '#DC2626', Medium: '#D97706', Low: '#059669' }[level]
  const levelBg    = { High: '#FEF2F2', Medium: '#FFFBEB', Low: '#ECFDF5' }[level]

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            width: 10, height: 10, borderRadius: '50%',
            background: color, flexShrink: 0,
          }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
            {label}
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            (w={weight})
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            fontSize: 11, fontWeight: 600, padding: '1px 7px',
            borderRadius: 999, background: levelBg, color: levelColor,
          }}>{level}</span>
          <span style={{ fontSize: 14, fontWeight: 700, color, minWidth: 36, textAlign: 'right' }}>
            {pct}
          </span>
        </div>
      </div>

      {/* Bar track */}
      <div style={{
        height: 8, background: 'var(--border)', borderRadius: 999, overflow: 'hidden',
      }}>
        <div style={{
          height: '100%',
          width: `${pct}%`,
          background: `linear-gradient(90deg, ${color}99, ${color})`,
          borderRadius: 999,
          transition: 'width 0.7s cubic-bezier(0.4,0,0.2,1)',
        }} />
      </div>

      {/* Explanation */}
      {explanation && (
        <div style={{
          fontSize: 11, color: 'var(--text-muted)', marginTop: 4,
          lineHeight: 1.5, paddingLeft: 18,
        }}>
          {explanation}
        </div>
      )}
    </div>
  )
}

export default function RiskChart({ signals = [], title = 'Risk Signal Breakdown' }) {
  if (!signals.length) {
    return (
      <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: 16, textAlign: 'center' }}>
        No signal data available
      </div>
    )
  }

  return (
    <div>
      {title && (
        <div style={{
          fontSize: 12, fontWeight: 600, color: 'var(--text-muted)',
          letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: 16,
        }}>
          {title}
        </div>
      )}
      {signals.map((s) => (
        <Bar
          key={s.signal_name}
          label={s.signal_name}
          score={s.score}
          weight={s.weight}
          weightedScore={s.weighted_score}
          explanation={s.explanation}
          color={SIGNAL_COLORS[s.signal_name] || '#64748B'}
        />
      ))}
    </div>
  )
}
