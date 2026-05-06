export default function StatusIndicator({ status }) {
  const configs = {
    online:  { cls: 'status-online',  icon: 'bi-circle-fill', text: 'الخادم متصل'   },
    offline: { cls: 'status-offline', icon: 'bi-circle-fill', text: 'الخادم غير متاح' },
    loading: { cls: 'status-loading', icon: 'bi-hourglass-split', text: 'جارٍ الاتصال…' },
  }
  const { cls, icon, text } = configs[status] || configs.loading

  return (
    <span className={`status-badge ${cls}`}>
      <i className={`bi ${icon}`} style={{ fontSize: '0.55rem' }} aria-hidden="true" />
      {text}
    </span>
  )
}