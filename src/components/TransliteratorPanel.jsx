import { useState, useCallback } from 'react'
import LanguageSelector from './LanguageSelector.jsx'
import { transliterate } from '../services/transliterator.js'

export default function TransliteratorPanel() {
  const [inputText, setInputText]   = useState('')
  const [outputText, setOutputText] = useState('')
  const [language, setLanguage]     = useState('aljamiado')
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)
  const [copied, setCopied]         = useState(false)

  const handleTransliterate = useCallback(async () => {
    if (!inputText.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await transliterate(inputText.trim(), language)
      setOutputText(data.result)
    } catch (err) {
      setError(err.message)
      setOutputText('')
    } finally {
      setLoading(false)
    }
  }, [inputText, language])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleTransliterate()
  }

  const handleCopy = () => {
    if (!outputText) return
    navigator.clipboard.writeText(outputText)
    setCopied(true)
    setTimeout(() => setCopied(false), 1800)
  }

  const handleClear = () => {
    setInputText('')
    setOutputText('')
    setError(null)
  }

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText()
      setInputText(prev => prev + text)
    } catch {
      // clipboard permission denied — silent
    }
  }

  return (
    <div className="card-arabic p-4 p-md-5">

      {/* Language selector */}
      <div className="mb-4">
        <LanguageSelector value={language} onChange={setLanguage} />
      </div>

      <div className="ornament mb-4" aria-hidden="true">❧ ✦ ❧</div>

      {/* Input */}
      <div className="mb-3">
        <label
          htmlFor="input-text"
          className="form-label mb-2"
          style={{ fontFamily: 'var(--font-body)', color: 'var(--ink-soft)', fontSize: '0.88rem' }}
        >
          أدخل النص
        </label>
        <textarea
          id="input-text"
          className="form-control text-area-arabic"
          rows={5}
          placeholder="اكتب النص هنا…"
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          dir="auto"
          spellCheck={false}
        />
        <div className="d-flex justify-content-between align-items-center mt-2">
          <small className="text-muted" style={{ fontSize: '0.75rem' }}>
            Ctrl+Enter للتحويل
          </small>
          <small className="text-muted" style={{ fontSize: '0.75rem' }}>
            {inputText.length} حرف
          </small>
        </div>
      </div>

      {/* Action buttons */}
      <div className="d-flex gap-2 flex-wrap mb-4">
        <button
          className="btn btn-gold d-flex align-items-center gap-2"
          onClick={handleTransliterate}
          disabled={loading || !inputText.trim()}
          style={{ minWidth: 150 }}
        >
          {loading
            ? <><span className="spinner-gold" />&nbsp;جارٍ التحويل</>
            : <><i className="bi bi-translate" aria-hidden="true" /> تحويل إلى العربية</>
          }
        </button>
        <button
          className="btn btn-outline-arabic d-flex align-items-center gap-2"
          onClick={handlePaste}
          title="لصق من الحافظة"
        >
          <i className="bi bi-clipboard" aria-hidden="true" /> لصق
        </button>
        <button
          className="btn btn-outline-arabic d-flex align-items-center gap-2"
          onClick={handleClear}
          title="مسح الكل"
        >
          <i className="bi bi-eraser" aria-hidden="true" /> مسح
        </button>
      </div>

      {/* Error alert */}
      {error && (
        <div className="alert mb-4 p-3 d-flex align-items-start gap-2"
          style={{
            background: 'rgba(139,58,42,0.07)',
            border: '1px solid rgba(139,58,42,0.25)',
            borderRadius: 2,
            color: 'var(--terracotta)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.9rem',
          }}
          role="alert"
        >
          <i className="bi bi-exclamation-triangle-fill mt-1" aria-hidden="true" />
          <div>
            <strong>حدث خطأ: </strong>{error}
          </div>
        </div>
      )}

      {/* Output */}
      <div className="mb-3">
        <div className="d-flex justify-content-between align-items-center mb-2">
          <label
            htmlFor="output-text"
            className="form-label mb-0"
            style={{ fontFamily: 'var(--font-body)', color: 'var(--ink-soft)', fontSize: '0.88rem' }}
          >
            النتيجة بالحروف العربية
          </label>
          {outputText && (
            <button
              className={`btn btn-sm btn-outline-arabic d-flex align-items-center gap-1 ${copied ? 'copy-flash' : ''}`}
              onClick={handleCopy}
              style={{ fontSize: '0.8rem', padding: '2px 10px' }}
            >
              <i className={`bi ${copied ? 'bi-check2' : 'bi-copy'}`} aria-hidden="true" />
              {copied ? 'تم النسخ' : 'نسخ'}
            </button>
          )}
        </div>
        <textarea
          id="output-text"
          className="form-control text-area-arabic output-area"
          rows={4}
          value={outputText}
          readOnly
          placeholder="ستظهر النتيجة هنا…"
          dir="rtl"
          style={{ fontFamily: 'var(--font-display)', fontSize: '1.35rem', lineHeight: 2 }}
          aria-live="polite"
        />
      </div>

    </div>
  )
}