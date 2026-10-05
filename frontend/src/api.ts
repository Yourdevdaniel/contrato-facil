const origin = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const auth = {
  token: () => localStorage.getItem('access_token'),
  refresh: () => localStorage.getItem('refresh_token'),
  user: () => JSON.parse(localStorage.getItem('user') || 'null') as { name: string; email: string } | null,
  save: (payload: { access: string; refresh: string; user: unknown }) => {
    localStorage.setItem('access_token', payload.access)
    localStorage.setItem('refresh_token', payload.refresh)
    localStorage.setItem('user', JSON.stringify(payload.user))
  },
  clear: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  },
}

export async function api<T>(path: string, options: RequestInit = {}, authenticated = true): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body) headers.set('Content-Type', 'application/json')
  if (authenticated && auth.token()) headers.set('Authorization', `Bearer ${auth.token()}`)
  let response = await fetch(`${origin}${path}`, { ...options, headers })
  if (response.status === 401 && authenticated && auth.refresh()) {
    const renewed = await fetch(`${origin}/api/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: auth.refresh() }),
    })
    if (renewed.ok) {
      const { access } = await renewed.json() as { access: string }
      localStorage.setItem('access_token', access)
      headers.set('Authorization', `Bearer ${access}`)
      response = await fetch(`${origin}${path}`, { ...options, headers })
    } else {
      auth.clear()
    }
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Não foi possível concluir. Tente novamente.' }))
    throw new Error(error.detail || Object.values(error).flat().join(' ') || 'Não foi possível concluir.')
  }
  return response.json() as Promise<T>
}

export const pdfUrl = (contractId: number) => `${origin}/api/contracts/${contractId}/pdf/`
