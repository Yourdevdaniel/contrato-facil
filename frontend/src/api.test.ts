import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from './api'


describe('api authentication', () => {
  beforeEach(() => {
    localStorage.setItem('access_token', 'expired-access')
    localStorage.setItem('refresh_token', 'valid-refresh')
    localStorage.setItem('user', JSON.stringify({ name: 'Ana', email: 'ana@example.com' }))
  })

  afterEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('renews an expired access token and retries the original request', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Token inválido.' }), { status: 401, headers: { 'Content-Type': 'application/json' } }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ access: 'renewed-access' }), { status: 200, headers: { 'Content-Type': 'application/json' } }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ contracts: 2 }), { status: 200, headers: { 'Content-Type': 'application/json' } }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(api<{ contracts: number }>('/api/contracts/')).resolves.toEqual({ contracts: 2 })
    expect(localStorage.getItem('access_token')).toBe('renewed-access')
    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(fetchMock.mock.calls[1][0]).toContain('/api/auth/refresh/')
    expect((fetchMock.mock.calls[2][1].headers as Headers).get('Authorization')).toBe('Bearer renewed-access')
  })
})
