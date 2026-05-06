import { useState, useEffect } from 'react'
import TransliteratorPanel from './components/TransliteratorPanel.jsx'
import StatusIndicator from './components/StatusIndicator.jsx'
import { checkHealth } from './services/transliterator.js'

export default function App() {
  const [serverStatus, setServerStatus] = useState('loading')

  useEffect(() => {
    const ping = async () => {
      const alive = await checkHealth()
      setServerStatus(alive ? 'online' : 'offline')
    }
    ping()
    const interval = setInterval(ping, 30_000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="d-flex flex-column min-vh-100">

      {/* Header */}
      <header className="py-3 px-4 d-flex justify-content-between align-items-center"
        style={{ borderBottom: '1px solid var(--border-ornate)' }}
      >
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.05rem',
            color: 'var(--gold)',
            letterSpacing: '0.05em',
          }}
        >
          ✦ نقحرة
        </div>
        <StatusIndicator status={serverStatus} />
      </header>

      {/* Main */}
      <main className="flex-grow-1 d-flex align-items-start justify-content-center py-5 px-3">
        <div className="w-100" style={{ maxWidth: 680 }}>

          {/* Title block */}
          <div className="text-center mb-5">
            <h1
              className="display-title mb-2"
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '3rem',
                fontWeight: 700,
                color: 'var(--ink)',
                lineHeight: 1.3,
              }}
            >
              محوّل النقحرة
              <br />
              <span style={{ color: 'var(--gold)', fontSize: '2rem', fontWeight: 400 }}>
                إلى الحروف العربية
              </span>
            </h1>
            <p
              className="text-muted mt-3"
              style={{ fontFamily: 'var(--font-body)', fontSize: '0.9rem', maxWidth: 420, margin: '0 auto' }}
            >
              حوّل النصوص الإسبانية والصينية واليابانية والكورية والفيتنامية
              إلى ما يقابلها في الحروف العربية
            </p>
          </div>

          {/* Panel */}
          <TransliteratorPanel />

          {/* Supported languages info */}
          <div className="mt-4 text-center">
            <small
              className="text-muted"
              style={{ fontFamily: 'var(--font-body)', fontSize: '0.78rem', letterSpacing: '0.02em' }}
            >
              اللغات المدعومة:&nbsp;
              {['الإسبانية', 'الصينية', 'اليابانية', 'الكورية', 'الفيتنامية'].map((l, i, arr) => (
                <span key={l}>
                  <span style={{ color: 'var(--gold-muted)' }}>{l}</span>
                  {i < arr.length - 1 && ' · '}
                </span>
              ))}
            </small>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="py-3 text-center">
        <small
          className="text-muted"
          style={{ fontFamily: 'var(--font-body)', fontSize: '0.75rem' }}
        >
          <span style={{ color: 'var(--gold-muted)' }}>✦</span>
          &nbsp; محوّل النقحرة — يعمل مع خادم Python &nbsp;
          <span style={{ color: 'var(--gold-muted)' }}>✦</span>
        </small>
      </footer>

    </div>
  )
}