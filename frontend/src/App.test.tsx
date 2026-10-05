import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

describe('assinatura desenhada', () => {
  afterEach(() => vi.restoreAllMocks())

  it('converte coordenadas CSS para a resolução interna do canvas', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({
        contract: { title: 'Contrato', final_body: '<p>Documento</p>', status: 'sent' },
        party: { name: 'Ana', status: 'viewed' },
      }), { status: 200, headers: { 'Content-Type': 'application/json' } }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ verified: true }), { status: 200, headers: { 'Content-Type': 'application/json' } })))

    const context = { beginPath: vi.fn(), moveTo: vi.fn(), lineTo: vi.fn(), stroke: vi.fn() }
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(context as unknown as CanvasRenderingContext2D)
    HTMLCanvasElement.prototype.setPointerCapture = vi.fn()

    render(<MemoryRouter initialEntries={['/assinar/token']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><App /></MemoryRouter>)
    await screen.findByText('Olá, Ana.')
    fireEvent.change(screen.getByLabelText('Código de 6 dígitos'), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verificar código' }))
    await screen.findByText('Identidade verificada')

    const canvas = screen.getByLabelText('Área para desenhar assinatura') as HTMLCanvasElement
    vi.spyOn(canvas, 'getBoundingClientRect').mockReturnValue({
      left: 10, top: 20, width: 280, height: 90, right: 290, bottom: 110, x: 10, y: 20, toJSON: () => ({}),
    })
    fireEvent(canvas, new MouseEvent('pointerdown', { bubbles: true, clientX: 150, clientY: 65 }))

    await waitFor(() => expect(context.moveTo).toHaveBeenCalledWith(280, 90))
  })
})

describe('edição do contrato', () => {
  afterEach(() => vi.restoreAllMocks())

  it('permite editar todo o conteúdo sem escrever HTML', async () => {
    const contract = {
      id: 1,
      title: 'Contrato original',
      final_body: '<section><h2>DO OBJETO</h2><p>Texto original.</p></section>',
      clauses: [],
      parties: [],
      installments: [],
    }
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(contract), { status: 200, headers: { 'Content-Type': 'application/json' } }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ...contract, title: 'Novo contrato' }), { status: 200, headers: { 'Content-Type': 'application/json' } }))
    vi.stubGlobal('fetch', fetchMock)

    render(<MemoryRouter initialEntries={['/contratos/1/revisar']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><App /></MemoryRouter>)
    await screen.findByText('Contrato original')
    expect(screen.getByRole('note').textContent).toContain('Não é aconselhamento jurídico')
    fireEvent.click(screen.getByRole('button', { name: 'Editar texto' }))
    fireEvent.change(screen.getByLabelText('Título do contrato'), { target: { value: 'Novo contrato' } })
    fireEvent.change(screen.getByLabelText('Título da cláusula 1'), { target: { value: 'OBJETO ALTERADO' } })
    fireEvent.change(screen.getByLabelText('Texto da cláusula 1'), { target: { value: '<script>alert(1)</script>' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    const request = JSON.parse(String(fetchMock.mock.calls[1][1].body))
    expect(request.title).toBe('Novo contrato')
    expect(request.final_body).toContain('<h2>OBJETO ALTERADO</h2>')
    expect(request.final_body).toContain('&lt;script&gt;alert(1)&lt;/script&gt;')
    expect(request.final_body).not.toContain('<script>')
  })
})

describe('inclusão do criador na assinatura', () => {
  afterEach(() => { vi.restoreAllMocks(); localStorage.clear() })

  it('preenche a parte vazia com os dados da conta', () => {
    localStorage.setItem('user', JSON.stringify({ name: 'Ana Souza', email: 'ana@example.com' }))

    render(<MemoryRouter initialEntries={['/contratos/1/enviar']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><App /></MemoryRouter>)
    fireEvent.click(screen.getByRole('button', { name: 'Eu também vou assinar' }))

    expect((screen.getByLabelText('Nome completo') as HTMLInputElement).value).toBe('Ana Souza')
    expect((screen.getByLabelText('E-mail ou WhatsApp') as HTMLInputElement).value).toBe('ana@example.com')
    expect((screen.getByRole('button', { name: 'Você foi incluído' }) as HTMLButtonElement).disabled).toBe(true)
  })
})
