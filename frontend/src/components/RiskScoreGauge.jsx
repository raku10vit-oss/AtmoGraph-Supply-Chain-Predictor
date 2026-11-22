/**
 * RiskScoreGauge — animated SVG arc gauge for a 0–1 risk score.
 * No external chart libraries; pure SVG + CSS animations.
 */
export default function RiskScoreGauge({ score = 0, size = 160 }) {
  const pct = Math.max(0, Math.min(1, score))
  const level = pct >= 0.65 ? 'High' : pct >= 0.35 ? 'Medium' : 'Low'

  const COLOR = { High: '#DC2626', Medium: '#D97706', Low: '#059669' }
  const BG    = { High: '#FEF2F2', Medium: '#FFFBEB', Low: '#ECFDF5' }
  const color = COLOR[level]
  const bg    = BG[level]

  // SVG arc params
  const cx = size / 2
  const cy = size / 2
  const r  = (size / 2) - 14
  const strokeW = 10

  // Arc from 210° to 330° (bottom-left to bottom-right, going clockwise through top)
  const startAngle = 210  // degrees
  const endAngle   = 330
  const totalArc   = 360 - (endAngle - startAngle) + (endAngle > startAngle ? endAngle - startAngle : 0)
  // Simpler: draw 240° arc (from 210 to 210+240=450 = 90°)
  const arcDeg = 240
  const circumference = 2 * Math.PI * r
  const arcLen = (arcDeg / 360) * circumference
  const fillLen = arcLen * pct

  const toXY = (angleDeg) => {
    const rad = (angleDeg - 90) * (Math.PI / 180)
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    }
  }

  const describeArc = (startDeg, sweepDeg) => {
    const s = toXY(startDeg)
    const e = toXY(startDeg + sweepDeg)
    const largeArc = sweepDeg > 180 ? 1 : 0
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${largeArc} 1 ${e.x} ${e.y}`
  }

  const bgPath   = describeArc(210, arcDeg)
  const fillPath = describeArc(210, arcDeg * pct)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ overflow: 'visible' }}>
          {/* Background track */}
          <path
            d={bgPath}
            fill="none"
            stroke="var(--border)"
            strokeWidth={strokeW}
            strokeLinecap="round"
          />
          {/* Filled arc */}
          <path
            d={fillPath}
            fill="none"
            stroke={color}
            strokeWidth={strokeW}
            strokeLinecap="round"
            style={{ transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
          />
        </svg>

        {/* Centre text */}
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          gap: 2,
        }}>
          <div style={{
            fontSize: size * 0.22,
            fontWeight: 800,
            color,
            lineHeight: 1,
            fontVariantNumeric: 'tabular-nums',
          }}>
            {Math.round(pct * 100)}
          </div>
          <div style={{ fontSize: size * 0.09, color: 'var(--text-muted)', fontWeight: 500 }}>
            / 100
          </div>
          <div style={{
            fontSize: size * 0.1, fontWeight: 700, letterSpacing: '.04em',
            padding: '2px 8px', borderRadius: 999,
            background: bg, color,
            marginTop: 2,
          }}>
            {level.toUpperCase()}
          </div>
        </div>
      </div>
    </div>
  )
}
