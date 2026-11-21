import { useState } from 'react'
import { Building2, ChevronDown, ChevronUp } from 'lucide-react'

function LevelBadge({ level }) {
  const styles = {
    High:   { background: '#FEF2F2', color: '#DC2626', border: '1px solid #FCA5A5' },
    Medium: { background: '#FFFBEB', color: '#D97706', border: '1px solid #FCD34D' },
    Low:    { background: '#ECFDF5', color: '#059669', border: '1px solid #6EE7B7' },
  }
  return (
    <span style={{
      fontSize: 11, fontWeight: 700, padding: '2px 8px',
      borderRadius: 999, flexShrink: 0,
      ...(styles[level] || styles.Low),
    }}>
      {level?.toUpperCase()}
    </span>
  )
}

function ScoreCell({ score }) {
  const pct = Math.round((score || 0) * 100)
  const color = score >= 0.65 ? '#DC2626' : score >= 0.35 ? '#D97706' : '#059669'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ width: 60, height: 5, background: 'var(--border)', borderRadius: 999, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`,
          background: color, borderRadius: 999,
        }} />
      </div>
      <span style={{ fontSize: 12, fontWeight: 700, color, minWidth: 24 }}>{pct}</span>
    </div>
  )
}

export default function AffectedCompanies({ companies = [], loading = false, onCompanyClick }) {
  const [sortKey, setSortKey] = useState('risk_score')
  const [sortDir, setSortDir] = useState('desc')
  const [page, setPage] = useState(0)
  const PAGE_SIZE = 15

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
    setPage(0)
  }

  const sorted = [...companies].sort((a, b) => {
    const av = a[sortKey] ?? ''
    const bv = b[sortKey] ?? ''
    const cmp = typeof av === 'number' ? av - bv : String(av).localeCompare(String(bv))
    return sortDir === 'asc' ? cmp : -cmp
  })

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE)
  const paged = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <ChevronDown size={11} style={{ opacity: 0.3 }} />
    return sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
  }

  const TH = ({ col, label, right }) => (
    <th
      onClick={() => handleSort(col)}
      style={{
        padding: '10px 12px', textAlign: right ? 'right' : 'left',
        fontSize: 11, fontWeight: 600, color: 'var(--text-muted)',
        letterSpacing: '.07em', textTransform: 'uppercase',
        cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap',
        background: 'var(--surface-2)', borderBottom: '1px solid var(--border)',
      }}
    >
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
        {label} <SortIcon col={col} />
      </span>
    </th>
  )

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
        <div className="spinner" style={{ width: 28, height: 28, borderWidth: 2 }} />
      </div>
    )
  }

  if (!companies.length) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)', fontSize: 13 }}>
        <Building2 size={32} style={{ opacity: 0.2, display: 'block', margin: '0 auto 8px' }} />
        No company risk data available. Ensure Neo4j is running and data is imported.
      </div>
    )
  }

  return (
    <div>
      <div style={{ overflowX: 'auto', borderRadius: 10, border: '1px solid var(--border)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr>
              <TH col="name"             label="Company" />
              <TH col="country"          label="Country" />
              <TH col="industry"         label="Industry" />
              <TH col="risk_level"       label="Level" />
              <TH col="risk_score"       label="Risk Score" right />
              <TH col="supplier_count"   label="Customers" right />
            </tr>
          </thead>
          <tbody>
            {paged.map((co, i) => (
              <tr
                key={co.name + i}
                onClick={() => onCompanyClick?.(co)}
                style={{
                  borderBottom: '1px solid var(--border)',
                  cursor: onCompanyClick ? 'pointer' : 'default',
                  transition: 'background .1s',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--surface-2)' }}
                onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
              >
                <td style={{ padding: '10px 12px', fontWeight: 500, maxWidth: 220 }}>
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                       title={co.name}>
                    {co.name}
                  </div>
                  {co.reasons?.[0] && (
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2,
                                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {co.reasons[0]}
                    </div>
                  )}
                </td>
                <td style={{ padding: '10px 12px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                  {co.country || '—'}
                </td>
                <td style={{ padding: '10px 12px', color: 'var(--text-secondary)', maxWidth: 160 }}>
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {co.industry || '—'}
                  </div>
                </td>
                <td style={{ padding: '10px 12px' }}>
                  <LevelBadge level={co.risk_level} />
                </td>
                <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                  <ScoreCell score={co.risk_score} />
                </td>
                <td style={{ padding: '10px 12px', textAlign: 'right',
                             color: 'var(--text-secondary)', fontVariantNumeric: 'tabular-nums' }}>
                  {co.supplier_count?.toLocaleString() ?? '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginTop: 12, fontSize: 12, color: 'var(--text-muted)',
        }}>
          <span>
            Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, sorted.length)} of {sorted.length}
          </span>
          <div style={{ display: 'flex', gap: 6 }}>
            <button
              className="btn btn-ghost btn-sm"
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
              style={{ opacity: page === 0 ? 0.4 : 1 }}
            >← Prev</button>
            <button
              className="btn btn-ghost btn-sm"
              disabled={page >= totalPages - 1}
              onClick={() => setPage(p => p + 1)}
              style={{ opacity: page >= totalPages - 1 ? 0.4 : 1 }}
            >Next →</button>
          </div>
        </div>
      )}
    </div>
  )
}
