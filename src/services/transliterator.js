const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Transliterate text via the FastAPI backend.
 * @param {string} text - Input text
 * @param {string} language - One of the supported language keys
 * @returns {Promise<{ result: string }>}
 */
export async function transliterate(text, language) {
  const response = await fetch(`${API_BASE}/api/transliterate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language }),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || `Server error: ${response.status}`)
  }

  return response.json()
}

/**
 * Ping the backend to check if it's alive.
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(3000) })
    return response.ok
  } catch {
    return false
  }
}