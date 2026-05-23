const LANGUAGES = [
  { value: 'angloarab',      label: 'الإنجليزية', latin: 'English'    },
  { value: 'aljamiado',      label: 'الإسبانية',  latin: 'Español'    },
  { value: 'xiaoerjing',     label: 'الصينية',   latin: 'Chinese'    },
  { value: 'araboji',        label: 'اليابانية',  latin: 'Japanese'   },
  { value: 'soagyeong',      label: 'الكورية',   latin: 'Korean'     },
  { value: 'tieunhikinh',    label: 'الفيتنامية', latin: 'Vietnamese' },
  { value: 'russoarab',      label: 'الروسية',    latin: 'Russian'    }
]

export default function LanguageSelector({ value, onChange }) {
  return (
    <div className="d-flex align-items-center gap-3 flex-wrap">
      <label
        className="mb-0 text-muted"
        style={{ fontFamily: 'var(--font-body)', fontSize: '0.88rem', whiteSpace: 'nowrap' }}
      >
        اختر اللغة المصدر
      </label>
      <select
        className="lang-select form-select"
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{ minWidth: 180 }}
        aria-label="اختيار اللغة"
      >
        {LANGUAGES.map(lang => (
          <option key={lang.value} value={lang.value}>
            {lang.label} — {lang.latin}
          </option>
        ))}
      </select>
    </div>
  )
}

export { LANGUAGES }