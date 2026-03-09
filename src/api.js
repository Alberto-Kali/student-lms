const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export async function postVisitLead(payload) {
  const response = await fetch(`${API_BASE}/visit/lead`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error('Failed to submit visit lead')
  }

  return response.json()
}

export async function fetchVisitContent() {
  const response = await fetch(`${API_BASE}/visit/content`)

  if (!response.ok) {
    throw new Error('Failed to load visit content')
  }

  return response.json()
}
