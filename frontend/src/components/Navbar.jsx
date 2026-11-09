import { useState, useRef, useEffect } from 'react'
import { Search, Activity, AlertCircle } from 'lucide-react'

export default function Navbar({ onSearch, neo4jStatus }) {
  const [query, setQuery] = useState('')
  const [focused, setFocused] = useState(false)
  const inputRef = useRef(null)

  // Keyboard shortcut: Cmd/Ctrl+K to focus search
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) onSearch(query.trim())
  }

  const handleClear = () => {
    setQuery('')
    onSearch('')
  }

  return (
    <header style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      height: 'var(--navbar-h)',
      background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center',
      padding: '0 20px', gap: '20px',
      boxShadow: '0 1px 0 var(--border)',
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: 'linear-gradient(135deg, #2563EB, #7C3AED)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Activity size={16} color="#fff" />
        </div>
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.1 }}>
            AtmoGraph
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '.05em' }}>
            SUPPLY CHAIN PREDICTOR
          </div>
        </div>
      </div>

      {/* Divider */}
      <div style={{ width: 1, height: 28, background: 'var(--border)', flexShrink: 0 }} />

      {/* Search */}
      <form onSubmit={handleSubmit} style={{ flex: 1, maxWidth: 480, position: 'relative' }}>
        <Search
          size={15}
          style={{
            position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)',
            color: focused ? 'var(--accent)' : 'var(--text-muted)',
            transition: 'color .15s',
          }}
        />
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Search companies, countries, industries…"
          style={{
            width: '100%', height: 36,
            padding: '0 60px 0 34px',
            border: `1px solid ${focused ? 'var(--accent)' : 'var(--border)'}`,
            borderRadius: 8,
            background: focused ? '#fff' : 'var(--surface-2)',
            color: 'var(--text-primary)', fontSize: 13,
            outline: 'none',
            transition: 'border-color .15s, background .15s',
            boxShadow: focused ? '0 0 0 3px rgba(37,99,235,.12)' : 'none',
          }}
        />
        <div style={{
          position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
          display: 'flex', gap: 4,
        }}>
          {query && (
            <button type="button" onClick={handleClear}
              style={{ background: 'none', border: 'none', cursor: 'pointer',
                       color: 'var(--text-muted)', fontSize: 16, lineHeight: 1,
                       padding: '0 2px' }}>
              ×
            </button>
          )}
          <kbd style={{
            padding: '2px 5px', borderRadius: 4,
            background: 'var(--surface-2)', border: '1px solid var(--border)',
            fontSize: 10, color: 'var(--text-muted)', fontFamily: 'inherit',
          }}>⌘K</kbd>
        </div>
      </form>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Neo4j status */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 7,
        padding: '5px 12px', borderRadius: 999,
        background: neo4jStatus === 'ok' ? 'var(--success-bg)' : 'var(--danger-bg)',
        border: `1px solid ${neo4jStatus === 'ok' ? '#6EE7B7' : '#FCA5A5'}`,
      }}>
        <span style={{
          width: 7, height: 7, borderRadius: '50%',
          background: neo4jStatus === 'ok' ? 'var(--success)' : 'var(--danger)',
          display: 'inline-block',
          ...(neo4jStatus === 'ok' ? { animation: 'pulse 2s ease infinite' } : {}),
        }} />
        <span style={{
          fontSize: 12, fontWeight: 500,
          color: neo4jStatus === 'ok' ? 'var(--success)' : 'var(--danger)',
        }}>
          {neo4jStatus === 'ok' ? 'Neo4j Connected' : neo4jStatus === 'loading' ? 'Connecting…' : 'Neo4j Offline'}
        </span>
        {neo4jStatus !== 'ok' && neo4jStatus !== 'loading' && (
          <AlertCircle size={12} color="var(--danger)" />
        )}
      </div>
    </header>
  )
}
