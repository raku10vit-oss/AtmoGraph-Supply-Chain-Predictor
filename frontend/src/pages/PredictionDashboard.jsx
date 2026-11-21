import { useCallback, useEffect, useState } from 'react'
import { RefreshCw, AlertTriangle, Info, X, Globe, Factory,
         TrendingUp, Shield, Zap } from 'lucide-react'
import Navbar from '../components/Navbar'
import RiskScoreGauge from '../components/RiskScoreGauge'
import DisruptionList from '../components/DisruptionList'
import AffectedCompanies from '../components/AffectedCompanies'
import RiskChart from '../components/RiskChart'
import {
  fetchHealth,
  fetchPredictionOverview,
  fetchDisruptions,
  fetchAffectedCompanies,
  fetchCompanyRiskProfile,
  fetchScenarios,
} from '../services/api'

// ── Helpers ──────────────────────────────────────────────────────

function SectionHeader({ icon: Icon, title, subtitle, color = 'var(--accent)' }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{
          width: 30, height: 30, borderRadius: 8,
          background: `${color}18`, display: 'flex',
          alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <Icon size={15} color={color} />
        </div>
        <div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
            {title}
          </h2>
          {subtitle && (
            <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
              {subtitle}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function StatChip({ label, value, color }) {
  return (
    <div style={{
      flex: 1, minWidth: 100,
      background: 'var(--surface)', border: '1px solid var(--border)',
      borderRadius: 10, padding: '12px 14px',
      display: 'flex', flexDirection: 'column', gap: 4,
    }}>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: color || 'var(--text-primary)', lineHeight: 1 }}>
        {value ?? '—'}
      </div>
    </div>
  )
}

function TopCountryRow({ item, rank }) {
  const color = item.risk_level === 'High' ? '#DC2626' : item.risk_level === 'Medium' ? '#D97706' : '#059669'
  const pct = Math.round((item.risk_score || 0) * 100)
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10,
      padding: '8px 0', borderBottom: '1px solid var(--border)',
    }}>
      <span style={{ fontSize: 11, color: 'var(--text-muted)', width: 18, textAlign: 'right' }}>
        {rank}
      </span>
      <span style={{ flex: 1, fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
        {item.country}
      </span>
      <span style={{ fontSize: 11, color: 'var(--text-muted)', marginRight: 4 }}>
        {item.event_count} events
      </span>
      <div style={{ width: 70, height: 5, background: 'var(--border)', borderRadius: 999, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 999 }} />
      </div>
      <span style={{ fontSize: 11, fontWeight: 700, color, minWidth: 24, textAlign: 'right' }}>{pct}</span>
    </div>
  )
}

function CompanyDetailPanel({ profile, onClose }) {
  if (!profile) return null
  return (
    <div style={{
      position: 'fixed', top: 0, right: 0, bottom: 0,
      width: 380, background: 'var(--surface)',
      borderLeft: '1px solid var(--border)',
      boxShadow: 'var(--shadow-lg)',
      zIndex: 200, overflowY: 'auto',
      animation: 'slideIn .2s ease both',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 18px', borderBottom: '1px solid var(--border)',
        display: 'flex', alignItems: 'flex-start', gap: 10,
      }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
            {profile.name}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
            {profile.industry} · {profile.country}
          </div>
        </div>
        <button onClick={onClose} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: 'var(--text-muted)', display: 'flex', padding: 4,
        }}>
          <X size={16} />
        </button>
      </div>

      <div style={{ padding: '16px 18px' }}>
        {/* Score */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 20 }}>
          <RiskScoreGauge score={profile.overall_score} size={140} />
        </div>

        {/* Summary */}
        <div style={{
          background: 'var(--surface-2)', borderRadius: 8, padding: '10px 12px',
          fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 16,
        }}>
          {profile.explanation}
        </div>

        {/* Signal breakdown */}
        <div style={{ marginBottom: 16 }}>
          <RiskChart signals={profile.signals} title="Signal Breakdown" />
        </div>

        {/* Supply info */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          <div style={{
            flex: 1, background: 'var(--surface-2)', borderRadius: 8, padding: '10px 12px',
          }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>As Customer</div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>{profile.supplier_count}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>supply links in</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {profile.supplier_countries?.slice(0, 3).join(', ')}
              {profile.supplier_countries?.length > 3 ? ` +${profile.supplier_countries.length - 3}` : ''}
            </div>
          </div>
          <div style={{
            flex: 1, background: 'var(--surface-2)', borderRadius: 8, padding: '10px 12px',
          }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>As Supplier</div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>{profile.customer_count}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>customer links in</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {profile.customer_countries?.slice(0, 3).join(', ')}
              {profile.customer_countries?.length > 3 ? ` +${profile.customer_countries.length - 3}` : ''}
            </div>
          </div>
        </div>

        {/* Matching scenarios */}
        {profile.matching_scenarios?.length > 0 && (
          <div>
            <div style={{
              fontSize: 11, fontWeight: 600, color: 'var(--text-muted)',
              letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: 8,
            }}>
              Matching Disruption Scenarios ({profile.matching_scenarios.length})
            </div>
            {profile.matching_scenarios.map(s => (
              <div key={s.scenario_id} style={{
                background: 'var(--surface-2)', borderRadius: 8, padding: '10px 12px',
                marginBottom: 6, fontSize: 12,
              }}>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
                  {s.name}
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                  {s.disruption_type} · Tier {s.target_tier}
                  {s.is_true_positive ? ' · ✓ True Positive' : ''}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ══════════════════════════════════════════════════════════════════
//  MAIN PAGE
// ══════════════════════════════════════════════════════════════════

export default function PredictionDashboard({ onNavigate }) {
  const [neo4jStatus, setNeo4jStatus]         = useState('loading')
  const [overview, setOverview]               = useState(null)
  const [disruptions, setDisruptions]         = useState([])
  const [companies, setCompanies]             = useState([])
  const [activeTab, setActiveTab]             = useState('overview')   // 'overview' | 'disruptions' | 'companies' | 'scenarios'
  const [scenarios, setScenarios]             = useState([])
  const [loading, setLoading]                 = useState(true)
  const [error, setError]                     = useState(null)
  const [companyProfile, setCompanyProfile]   = useState(null)
  const [profileLoading, setProfileLoading]   = useState(false)

  // ── Loaders ───────────────────────────────────────────────────
  const checkHealth = useCallback(async () => {
    try {
      const h = await fetchHealth()
      setNeo4jStatus(h.neo4j_connected ? 'ok' : 'error')
    } catch {
      setNeo4jStatus('error')
    }
  }, [])

  const loadAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [ov, dis, cos, sc] = await Promise.all([
        fetchPredictionOverview(),
        fetchDisruptions(20),
        fetchAffectedCompanies(50),
        fetchScenarios(30),
      ])
      setOverview(ov)
      setDisruptions(dis)
      setCompanies(cos)
      setScenarios(sc)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleCompanyClick = useCallback(async (co) => {
    setProfileLoading(true)
    setCompanyProfile(null)
    try {
      const profile = await fetchCompanyRiskProfile(co.name)
      setCompanyProfile(profile)
    } catch (err) {
      // If not found in KG, build a minimal profile from table data
      setCompanyProfile({
        name: co.name,
        country: co.country,
        industry: co.industry,
        overall_score: co.risk_score,
        risk_level: co.risk_level,
        signals: [
          { signal_name: 'Port Exposure', score: co.country_risk_score, weight: 0.30, weighted_score: co.country_risk_score * 0.30, explanation: 'Based on historical port disruption data for this country.' },
          { signal_name: 'Supplier Concentration', score: co.concentration_score, weight: 0.25, weighted_score: co.concentration_score * 0.25, explanation: 'HHI concentration score of supplier countries.' },
          { signal_name: 'Industry Vulnerability', score: co.industry_risk_score, weight: 0.15, weighted_score: co.industry_risk_score * 0.15, explanation: 'Industry exposure to historically disrupted regions.' },
        ],
        supplier_countries: [],
        customer_countries: [],
        supplier_count: co.supplier_count,
        customer_count: co.customer_count,
        matching_scenarios: [],
        explanation: `${co.name} in ${co.industry || 'unknown sector'}, ${co.country}. Risk score: ${Math.round(co.risk_score * 100)}/100 (${co.risk_level}).`,
      })
    } finally {
      setProfileLoading(false)
    }
  }, [])

  useEffect(() => {
    checkHealth()
    loadAll()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  // ── Tab nav ────────────────────────────────────────────────────
  const TABS = [
    { id: 'overview',    label: 'Overview',    icon: Shield },
    { id: 'disruptions', label: 'Disruptions', icon: AlertTriangle },
    { id: 'companies',   label: 'Companies',   icon: TrendingUp },
    { id: 'scenarios',   label: 'Scenarios',   icon: Zap },
  ]

  const hasDetail = !!companyProfile

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Navbar
        neo4jStatus={neo4jStatus}
        activePage="predictions"
        onNavigate={onNavigate}
        onSearch={null}
      />

      {/* Page body */}
      <div style={{
        flex: 1, overflowY: 'auto',
        marginTop: 'var(--navbar-h)',
        marginRight: hasDetail ? 380 : 0,
        transition: 'margin-right .2s ease',
        background: 'var(--bg)',
      }}>

        {/* Page header bar */}
        <div style={{
          background: 'var(--surface)', borderBottom: '1px solid var(--border)',
          padding: '0 24px', display: 'flex', alignItems: 'center',
          gap: 20, flexShrink: 0,
        }}>
          {/* Tabs */}
          <div style={{ display: 'flex', gap: 2 }}>
            {TABS.map(({ id, label, icon: Icon }) => {
              const active = activeTab === id
              return (
                <button
                  key={id}
                  id={`tab-${id}`}
                  onClick={() => setActiveTab(id)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    padding: '14px 16px', border: 'none', background: 'transparent',
                    fontSize: 13, fontWeight: active ? 600 : 500, cursor: 'pointer',
                    color: active ? 'var(--accent)' : 'var(--text-secondary)',
                    borderBottom: active ? '2px solid var(--accent)' : '2px solid transparent',
                    transition: 'all .15s',
                  }}
                >
                  <Icon size={13} />
                  {label}
                </button>
              )
            })}
          </div>

          <div style={{ flex: 1 }} />

          {/* Refresh + methodology note */}
          <button
            id="btn-refresh-predictions"
            className="btn btn-ghost btn-sm"
            onClick={loadAll}
            style={{ display: 'flex', alignItems: 'center', gap: 5 }}
          >
            <RefreshCw size={12} />
            Refresh
          </button>

          <div style={{
            display: 'flex', alignItems: 'center', gap: 5,
            fontSize: 11, color: 'var(--text-muted)',
            background: 'var(--accent-light)', borderRadius: 6,
            padding: '4px 8px',
          }}>
            <Info size={11} color="var(--accent)" />
            5 interpretable signals · no black-box ML
          </div>
        </div>

        {/* Error state */}
        {error && (
          <div style={{
            margin: 24, padding: '14px 18px', borderRadius: 10,
            background: 'var(--danger-bg)', border: '1px solid #FCA5A5',
            color: '#B91C1C', fontSize: 13, display: 'flex', gap: 10,
          }}>
            <AlertTriangle size={16} style={{ flexShrink: 0 }} />
            <div>
              <strong>Prediction engine error:</strong> {error}
              <div style={{ marginTop: 4, opacity: 0.8 }}>
                Ensure the backend is running: <code>uvicorn app.main:app --reload</code>
              </div>
            </div>
          </div>
        )}

        {/* ── OVERVIEW TAB ───────────────────────────────────────── */}
        {activeTab === 'overview' && (
          <div style={{ padding: 24 }}>
            {loading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
                <div className="spinner" />
              </div>
            ) : overview ? (
              <>
                {/* Top row: gauge + stats */}
                <div style={{ display: 'flex', gap: 20, marginBottom: 24, flexWrap: 'wrap' }}>
                  {/* Gauge card */}
                  <div className="card fade-in" style={{ padding: 24, flexShrink: 0 }}>
                    <SectionHeader icon={Shield} title="Overall Supply Chain Risk"
                      subtitle="Weighted average across all 5 signals" color="#2563EB" />
                    <div style={{ display: 'flex', justifyContent: 'center', margin: '8px 0 16px' }}>
                      <RiskScoreGauge score={overview.overall_risk_score} size={180} />
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.5 }}>
                      Based on {overview.top_risk_countries?.length} countries with historical disruption data
                    </div>
                  </div>

                  {/* Stats grid */}
                  <div style={{ flex: 1, minWidth: 200 }}>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
                      <StatChip label="Companies at Risk"   value={overview.total_companies_at_risk?.toLocaleString()} color="var(--accent)" />
                      <StatChip label="High Risk"           value={overview.high_risk_count?.toLocaleString()}          color="#DC2626" />
                      <StatChip label="Medium Risk"         value={overview.medium_risk_count?.toLocaleString()}        color="#D97706" />
                      <StatChip label="Lower Risk"          value={overview.low_risk_count?.toLocaleString()}           color="#059669" />
                    </div>

                    {/* Signal weights info */}
                    <div className="card fade-in" style={{ padding: 16 }}>
                      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)',
                                    letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: 10 }}>
                        Signal Weights
                      </div>
                      {overview.signal_weights && Object.entries(overview.signal_weights).map(([k, w]) => (
                        <div key={k} style={{
                          display: 'flex', justifyContent: 'space-between',
                          fontSize: 12, padding: '4px 0', borderBottom: '1px solid var(--border)',
                          color: 'var(--text-secondary)',
                        }}>
                          <span style={{ textTransform: 'capitalize' }}>
                            {k.replace(/_/g, ' ')}
                          </span>
                          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                            {(w * 100).toFixed(0)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Two-column: countries + industries */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
                  {/* Top risk countries */}
                  <div className="card fade-in" style={{ padding: 20 }}>
                    <SectionHeader icon={Globe} title="Top Risk Countries"
                      subtitle="Ranked by historical port disruption severity" color="#7C3AED" />
                    {overview.top_risk_countries?.map((item, i) => (
                      <TopCountryRow key={item.country} item={item} rank={i + 1} />
                    ))}
                  </div>

                  {/* Top risk industries */}
                  <div className="card fade-in" style={{ padding: 20 }}>
                    <SectionHeader icon={Factory} title="Top Risk Industries"
                      subtitle="Ranked by supplier exposure in disrupted countries" color="#D97706" />
                    {overview.top_risk_industries?.map((item, i) => {
                      const pct = Math.round((item.risk_score || 0) * 100)
                      const color = item.risk_level === 'High' ? '#DC2626'
                                  : item.risk_level === 'Medium' ? '#D97706' : '#059669'
                      return (
                        <div key={item.industry} style={{
                          display: 'flex', alignItems: 'center', gap: 10,
                          padding: '8px 0', borderBottom: '1px solid var(--border)',
                        }}>
                          <span style={{ fontSize: 11, color: 'var(--text-muted)', width: 18, textAlign: 'right' }}>
                            {i + 1}
                          </span>
                          <span style={{ flex: 1, fontSize: 12, fontWeight: 500, color: 'var(--text-primary)',
                                         overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {item.industry}
                          </span>
                          <div style={{ width: 60, height: 5, background: 'var(--border)', borderRadius: 999, overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 999 }} />
                          </div>
                          <span style={{ fontSize: 11, fontWeight: 700, color, minWidth: 24, textAlign: 'right' }}>{pct}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Methodology note */}
                <div style={{
                  background: 'var(--accent-light)', border: '1px solid #BFDBFE',
                  borderRadius: 10, padding: '12px 16px',
                  fontSize: 12, color: '#1D4ED8', lineHeight: 1.6,
                  display: 'flex', gap: 10,
                }}>
                  <Info size={15} style={{ flexShrink: 0, marginTop: 1 }} />
                  <span>{overview.methodology_note}</span>
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>
                No data loaded yet. Click Refresh or start the backend.
              </div>
            )}
          </div>
        )}

        {/* ── DISRUPTIONS TAB ────────────────────────────────────── */}
        {activeTab === 'disruptions' && (
          <div style={{ padding: 24 }}>
            <SectionHeader icon={AlertTriangle} title="Historical Disruption Events"
              subtitle={`${disruptions.length} events from Port-disruption-database.xlsx (2011–2019), ranked by risk score`}
              color="#DC2626" />
            <DisruptionList disruptions={disruptions} loading={loading} />
          </div>
        )}

        {/* ── COMPANIES TAB ──────────────────────────────────────── */}
        {activeTab === 'companies' && (
          <div style={{ padding: 24 }}>
            <SectionHeader icon={TrendingUp} title="At-Risk Companies"
              subtitle={`${companies.length} companies identified via port exposure + supplier concentration + industry vulnerability`}
              color="#D97706" />
            <AffectedCompanies
              companies={companies}
              loading={loading || profileLoading}
              onCompanyClick={handleCompanyClick}
            />
          </div>
        )}

        {/* ── SCENARIOS TAB ──────────────────────────────────────── */}
        {activeTab === 'scenarios' && (
          <div style={{ padding: 24 }}>
            <SectionHeader icon={Zap} title="Disruption Scenarios"
              subtitle={`${scenarios.length} structured scenarios from evaluation dataset, with risk scores computed from real data`}
              color="#7C3AED" />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 14 }}>
              {scenarios.map(s => {
                const color = s.risk_level === 'High' ? '#DC2626' : s.risk_level === 'Medium' ? '#D97706' : '#059669'
                const bg = s.risk_level === 'High' ? '#FEF2F2' : s.risk_level === 'Medium' ? '#FFFBEB' : '#ECFDF5'
                const pct = Math.round((s.risk_score || 0) * 100)
                return (
                  <div key={s.scenario_id} className="card fade-in" style={{
                    padding: 16, borderLeft: `4px solid ${color}`,
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)',
                                       marginBottom: 3, lineHeight: 1.3 }}>
                          {s.name}
                        </div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>
                          {s.scenario_id} · {s.disruption_type}
                          {s.target_tier != null ? ` · Tier ${s.target_tier}` : ''}
                        </div>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0 }}>
                        <span style={{
                          fontSize: 10, fontWeight: 700, padding: '2px 7px',
                          borderRadius: 999, background: bg, color,
                        }}>{s.risk_level?.toUpperCase()}</span>
                        <span style={{ fontSize: 16, fontWeight: 800, color }}>{pct}</span>
                      </div>
                    </div>

                    {/* Score bar */}
                    <div style={{ height: 4, background: 'var(--border)', borderRadius: 999, overflow: 'hidden', marginBottom: 10 }}>
                      <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 999 }} />
                    </div>

                    <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 8 }}>
                      {s.description?.slice(0, 140)}{s.description?.length > 140 ? '…' : ''}
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                      {s.affected_countries?.slice(0, 3).map(c => (
                        <span key={c} style={{
                          fontSize: 10, padding: '2px 7px', borderRadius: 999,
                          background: 'var(--surface-2)', border: '1px solid var(--border)',
                          color: 'var(--text-secondary)',
                        }}>🌍 {c}</span>
                      ))}
                      {s.affected_industries?.slice(0, 2).map(ind => (
                        <span key={ind} style={{
                          fontSize: 10, padding: '2px 7px', borderRadius: 999,
                          background: '#FFFBEB', border: '1px solid #FCD34D',
                          color: '#92400E',
                        }}>🏭 {ind}</span>
                      ))}
                      {s.is_true_positive && (
                        <span style={{
                          fontSize: 10, padding: '2px 7px', borderRadius: 999,
                          background: '#ECFDF5', border: '1px solid #6EE7B7',
                          color: '#065F46', fontWeight: 600,
                        }}>✓ True Positive</span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Company detail panel */}
      {(companyProfile || profileLoading) && (
        companyProfile
          ? <CompanyDetailPanel profile={companyProfile} onClose={() => setCompanyProfile(null)} />
          : (
            <div style={{
              position: 'fixed', top: 0, right: 0, bottom: 0, width: 380,
              background: 'var(--surface)', borderLeft: '1px solid var(--border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200,
            }}>
              <div className="spinner" />
            </div>
          )
      )}
    </div>
  )
}
