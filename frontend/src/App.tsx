import { FormEvent, PointerEvent, ReactNode, useEffect, useRef, useState } from 'react'
import { Link, NavLink, Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { api, auth, pdfUrl } from './api'
import { formatCurrency, questionIsVisible, useWizard } from './store'
import type { AuditEvent, Contract, Question, Template } from './types'

const statusLabel: Record<string, string> = {
  draft: 'Rascunho', sent: 'Enviado', partial: 'Parcialmente assinado', signed: 'Assinado', cancelled: 'Cancelado',
  pending: 'Pendente', viewed: 'Visualizado', verified: 'Verificado', paid: 'Pago', overdue: 'Vencido',
}

function Button({ children, secondary = false, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { secondary?: boolean }) {
  return <button className={secondary ? 'button secondary' : 'button'} {...props}>{children}</button>
}

function ErrorMessage({ message }: { message?: string }) {
  return message ? <div className="error" role="alert">{message}</div> : null
}

const LEGAL_NOTICE = 'Modelo gerado automaticamente. Não é aconselhamento jurídico: revise com um advogado antes de usar. O uso é por sua conta e risco; os autores não se responsabilizam por danos ou disputas.'

function LegalNotice() {
  return <div className="legal-notice" role="note">{LEGAL_NOTICE}</div>
}

type ContractSection = { title: string; text: string }

function parseContract(body: string): ContractSection[] {
  const document = new DOMParser().parseFromString(body, 'text/html')
  const sections = [...document.querySelectorAll('section')].map(section => ({
    title: section.querySelector('h2')?.textContent || '',
    text: section.querySelector('p')?.textContent || '',
  }))
  return sections.length ? sections : [{ title: '', text: document.body.textContent || '' }]
}

function contractHtml(sections: ContractSection[]) {
  const escape = (value: string) => value.replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]!)
  return sections.map(section => `<section><h2>${escape(section.title)}</h2><p>${escape(section.text)}</p></section>`).join('\n')
}

function ContractBody({ body }: { body: string }) {
  return <>{parseContract(body).map((section, index) => <section key={index}>{section.title && <h2>{section.title}</h2>}<p>{section.text}</p></section>)}</>
}

function Shell({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const user = auth.user()
  return <>
    <header className="topbar">
      <Link className="brand" to="/" aria-label="ContratoFácil — início"><span>Contrato</span>Fácil</Link>
      <nav aria-label="Navegação principal">
        <NavLink to="/modelos">Modelos</NavLink>
        {user && <NavLink to="/cofre">Meus contratos</NavLink>}
        {!user ? <Link className="nav-action" to="/entrar">Entrar</Link> : <button className="link-button" onClick={() => { auth.clear(); navigate('/') }}>Sair</button>}
      </nav>
    </header>
    <main>{children}</main>
    <footer><div><Link className="brand footer-brand" to="/">ContratoFácil</Link><p>Contratos claros. Acordos protegidos.</p></div><div><Link to="/modelos">Modelos</Link><a href="mailto:contato@example.com">Ajuda</a></div><p>© 2026 ContratoFácil. Modelos gerados automaticamente, sem aconselhamento jurídico. Uso por sua conta e risco.</p></footer>
  </>
}

function Home() {
  return <Shell>
    <section className="hero container">
      <div className="hero-copy">
        <p className="context">Do combinado à assinatura, sem juridiquês.</p>
        <h1>Seu trabalho merece mais que um print.</h1>
        <p className="lead">Responda perguntas simples, receba uma minuta de contrato para revisar e assine pelo celular. Em cerca de sete minutos.</p>
        <div className="actions"><Link className="button" to="/modelos">Criar meu contrato grátis</Link><a className="text-link" href="#como-funciona">Ver como funciona →</a></div>
        <p className="fine-print">1 contrato grátis por mês · sem cartão</p>
      </div>
      <div className="hero-document" aria-label="Prévia de um contrato">
        <div className="document-top"><span>Contrato de prestação de serviços</span><span className="status success">Pronto para assinar</span></div>
        <div className="document-body"><p>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</p><h2>1. DO OBJETO</h2><span>O contratado realizará o desenvolvimento da identidade visual, conforme escopo acordado entre as partes.</span><h2>2. DO PAGAMENTO</h2><span>O valor total é de R$ 5.000,00, com sinal de 30% para reserva da agenda.</span></div>
        <div className="signature-row"><div><small>CONTRATANTE</small><strong>Marina Oliveira</strong></div><div><small>CONTRATADO</small><strong>Rafael Mendes</strong></div></div>
      </div>
    </section>

    <section id="como-funciona" className="process-section"><div className="container narrow"><h2>Um contrato completo, sem começar pela cláusula primeira.</h2><div className="steps"><article><span>1</span><div><h3>Escolha o acordo</h3><p>Serviço, freela, locação ou dívida. Cada modelo faz apenas as perguntas relevantes.</p></div></article><article><span>2</span><div><h3>Conte o combinado</h3><p>Valores, prazos e responsabilidades em linguagem comum. O contrato cresce ao seu lado.</p></div></article><article><span>3</span><div><h3>Envie e acompanhe</h3><p>Cada parte recebe um link. Você vê quem abriu, verificou e assinou.</p></div></article></div></div></section>

    <section className="trust container"><div><h2>Clareza na tela. Evidência no documento.</h2><p>Hash SHA-256, horário, IP, dispositivo e histórico de cada assinatura compõem a trilha de auditoria.</p></div><dl><div><dt>6</dt><dd>modelos jurídicos guiados</dd></div><div><dt>100%</dt><dd>do fluxo pelo celular</dd></div><div><dt>24h</dt><dd>alertas e acompanhamento</dd></div></dl></section>

    <section className="pricing container"><div><h2>Comece com o próximo acordo.</h2><p>Sem taxa por assinatura no plano profissional.</p></div><div className="price-list"><article><h3>Grátis</h3><strong>R$ 0</strong><p>1 contrato por mês, com marca d'água.</p><Link className="button secondary" to="/modelos">Experimentar</Link></article><article className="featured"><span className="tag">Mais escolhido</span><h3>Profissional</h3><strong>R$ 39 <small>/mês</small></strong><p>Contratos ilimitados, assinaturas e cofre.</p><Link className="button" to="/cadastro">Começar agora</Link></article><article><h3>Empresa</h3><strong>R$ 99 <small>/mês</small></strong><p>5 usuários, parcelas Pix e modelos próprios.</p><Link className="button secondary" to="/cadastro">Escolher Empresa</Link></article></div></section>
  </Shell>
}

function AuthPage({ register = false }: { register?: boolean }) {
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setLoading(true)
    const data = Object.fromEntries(new FormData(event.currentTarget))
    try {
      const result = await api<{ access: string; refresh: string; user: unknown }>(register ? '/api/auth/register/' : '/api/auth/login/', { method: 'POST', body: JSON.stringify(data) }, false)
      auth.save(result); navigate('/modelos')
    } catch (err) { setError((err as Error).message) } finally { setLoading(false) }
  }
  return <Shell><section className="auth-layout container"><div><p className="context">{register ? 'Sua primeira proteção' : 'Bem-vindo de volta'}</p><h1>{register ? 'Crie sua conta grátis.' : 'Entre no seu cofre.'}</h1><p>Seus contratos, assinaturas e pagamentos ficam organizados em um só lugar.</p></div><form className="form-panel" onSubmit={submit}><h2>{register ? 'Cadastro' : 'Entrar'}</h2>{register && <><label>Seu nome<input name="name" required autoComplete="name" /></label><label>CPF ou CNPJ<input name="cpf_cnpj" autoComplete="off" /></label><label>WhatsApp<input name="phone" type="tel" autoComplete="tel" /></label></>}<label>E-mail<input name="email" type="email" required autoComplete="email" /></label><label>Senha<input name="password" type="password" minLength={8} required autoComplete={register ? 'new-password' : 'current-password'} /></label><ErrorMessage message={error} /><Button disabled={loading}>{loading ? 'Aguarde…' : register ? 'Criar conta' : 'Entrar'}</Button><p>{register ? <>Já tem conta? <Link to="/entrar">Entre</Link></> : <>Ainda não tem conta? <Link to="/cadastro">Crie grátis</Link></>}</p></form></section></Shell>
}

function Templates() {
  const [items, setItems] = useState<Template[]>([])
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')
  useEffect(() => { api<Template[]>('/api/templates/', {}, false).then(setItems).catch(err => setError(err.message)) }, [])
  const filtered = items.filter(item => `${item.name} ${item.category} ${item.description}`.toLowerCase().includes(query.toLowerCase()))
  return <Shell><section className="page-head container"><p className="context">Biblioteca jurídica</p><h1>Que acordo você quer colocar no papel?</h1><p>Escolha o caso mais próximo. As próximas perguntas adaptam as cláusulas ao seu combinado.</p><label className="search"><span>Buscar modelo</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Ex.: serviço, dívida, equipamento" /></label></section><section className="template-list container"><ErrorMessage message={error} />{!error && items.length === 0 && <div className="empty"><h2>Preparando os modelos…</h2><p>Se esta tela continuar vazia, execute o seed de demonstração descrito no README.</p></div>}{filtered.map((item, index) => <article className={index === 0 ? 'template-featured' : ''} key={item.id}><div><span className="tag">{item.category}</span><h2>{item.name}</h2><p>{item.description}</p></div><div className="template-meta"><span>~7 min</span><span>{item.question_count} perguntas</span>{auth.user() ? <Link className="button" to={`/criar/${item.id}`}>Usar este modelo</Link> : <Link className="button" to="/cadastro">Criar conta para usar</Link>}</div></article>)}</section></Shell>
}

function InputForQuestion({ question, value, onChange }: { question: Question; value: string | number | boolean | undefined; onChange: (value: string | number | boolean) => void }) {
  if (question.type === 'bool') return <div className="choice-row"><button type="button" className={value === true ? 'choice selected' : 'choice'} onClick={() => onChange(true)}>Sim</button><button type="button" className={value === false ? 'choice selected' : 'choice'} onClick={() => onChange(false)}>Não</button></div>
  if (question.type === 'option') return <select id="answer" value={String(value ?? '')} onChange={event => onChange(event.target.value)} required={question.required}><option value="">Selecione</option>{question.options.map(option => <option key={option}>{option}</option>)}</select>
  if (question.type === 'textarea') return <textarea id="answer" value={String(value ?? '')} onChange={event => onChange(event.target.value)} rows={5} required={question.required} />
  return <input id="answer" type={question.type === 'value' || question.type === 'number' ? 'number' : question.type} step={question.type === 'value' ? '0.01' : undefined} value={String(value ?? '')} onChange={event => onChange(question.type === 'number' || question.type === 'value' ? Number(event.target.value) : event.target.value)} required={question.required} autoFocus />
}

function Wizard() {
  const { templateId } = useParams(); const navigate = useNavigate()
  const wizard = useWizard(); const [questions, setQuestions] = useState<Question[]>([]); const [template, setTemplate] = useState<Template>(); const [error, setError] = useState(''); const [loading, setLoading] = useState(false)
  useEffect(() => {
    if (!auth.user()) return
    const id = Number(templateId); wizard.start(id)
    Promise.all([api<Question[]>(`/api/templates/${id}/questions/`), api<Template[]>('/api/templates/')]).then(([qs, templates]) => { setQuestions(qs); setTemplate(templates.find(item => item.id === id)) }).catch(err => setError(err.message))
  // start must run only when a different template opens.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [templateId])
  if (!auth.user()) return <Navigate to="/entrar" />
  const visible = questions.filter(question => questionIsVisible(question, wizard.answers)); const question = visible[wizard.step]; const progress = visible.length ? ((wizard.step + 1) / visible.length) * 100 : 0
  async function advance(event: FormEvent) {
    event.preventDefault(); setError('')
    if (wizard.step < visible.length - 1) return wizard.next()
    setLoading(true)
    try { const contract = await api<Contract>('/api/contracts/', { method: 'POST', body: JSON.stringify({ template: Number(templateId), responses: wizard.answers }) }); navigate(`/contratos/${contract.id}/revisar`) } catch (err) { setError((err as Error).message); setLoading(false) }
  }
  return <Shell><section className="wizard-shell"><div className="wizard-form"><div className="wizard-heading"><Link to="/modelos">← Voltar aos modelos</Link><span>{template?.name}</span></div><div className="progress" aria-label={`${Math.round(progress)}% concluído`}><span style={{ transform: `scaleX(${progress / 100})` }} /></div>{question ? <form onSubmit={advance} className="question"><p>Passo {wizard.step + 1} de {visible.length}</p><label htmlFor="answer"><h1>{question.text}</h1></label><InputForQuestion question={question} value={wizard.answers[question.key]} onChange={value => wizard.setAnswer(question.key, value)} /><small>{question.help_text}</small><ErrorMessage message={error} /><div className="actions"><Button type="button" secondary disabled={wizard.step === 0} onClick={wizard.previous}>Voltar</Button><Button disabled={loading || wizard.answers[question.key] === undefined || wizard.answers[question.key] === ''}>{loading ? 'Criando…' : wizard.step === visible.length - 1 ? 'Gerar contrato' : 'Continuar'}</Button></div></form> : <div className="skeleton"><span /><span /><span /></div>}<LegalNotice /></div><aside className="preview"><div className="preview-head"><span>Prévia do contrato</span><span>Atualiza a cada resposta</span></div><div className="paper"><h2>{template?.name || 'Seu contrato'}</h2>{Object.entries(wizard.answers).map(([key, value]) => <p key={key}><strong>{questions.find(item => item.key === key)?.text}</strong><br />{typeof value === 'boolean' ? value ? 'Sim' : 'Não' : key === 'value' ? formatCurrency(value as number) : String(value)}</p>)}</div></aside></section></Shell>
}

function Review() {
  const { id } = useParams(); const navigate = useNavigate(); const [contract, setContract] = useState<Contract>(); const [editing, setEditing] = useState(false); const [title, setTitle] = useState(''); const [sections, setSections] = useState<ContractSection[]>([]); const [error, setError] = useState('')
  useEffect(() => { api<Contract>(`/api/contracts/${id}/`).then(value => { setContract(value); setTitle(value.title); setSections(parseContract(value.final_body)) }).catch(err => setError(err.message)) }, [id])
  const updateSection = (index: number, field: keyof ContractSection, value: string) => setSections(current => current.map((section, position) => position === index ? { ...section, [field]: value } : section))
  function toggleEditing() { if (editing && contract) { setTitle(contract.title); setSections(parseContract(contract.final_body)) } setEditing(!editing) }
  async function save() { try { const value = await api<Contract>(`/api/contracts/${id}/`, { method: 'PATCH', body: JSON.stringify({ title, final_body: contractHtml(sections) }) }); setContract(value); setTitle(value.title); setSections(parseContract(value.final_body)); setEditing(false) } catch (err) { setError((err as Error).message) } }
  return <Shell><section className="review-head container"><div><p className="context">Revise antes de enviar</p><h1>{contract?.title || 'Seu contrato'}</h1><p>Confira nomes, valores e prazos. Cada explicação traduz o efeito da cláusula.</p><LegalNotice /></div><div className="actions"><Button secondary onClick={toggleEditing}>{editing ? 'Cancelar edição' : 'Editar texto'}</Button><Button disabled={!contract} onClick={() => navigate(`/contratos/${id}/enviar`)}>Enviar para assinatura</Button></div></section><ErrorMessage message={error} />{editing ? <section className="editor container"><div className="warning"><strong>Edite em linguagem comum</strong><span>Todos os campos podem ser alterados. Em caso de dúvida jurídica, consulte um profissional.</span></div><label>Título do contrato<input value={title} onChange={event => setTitle(event.target.value)} /></label>{sections.map((section, index) => <fieldset key={index}><legend>Cláusula {index + 1}</legend><label>Título da cláusula {index + 1}<input value={section.title} onChange={event => updateSection(index, 'title', event.target.value)} /></label><label>Texto da cláusula {index + 1}<textarea value={section.text} onChange={event => updateSection(index, 'text', event.target.value)} rows={6} /></label></fieldset>)}<Button onClick={save}>Salvar alterações</Button></section> : <section className="review-layout container"><article className="contract-paper"><ContractBody body={contract?.final_body || ''} /></article><aside className="clause-guide"><h2>Entenda as cláusulas</h2>{contract?.clauses.map(clause => <details key={clause.key}><summary>{clause.title}</summary><p>{clause.explanation}</p></details>)}</aside></section>}</Shell>
}

type SendParty = { name: string; cpf_cnpj: string; contact: string; signing_order: number }
function SendContract() {
  const { id } = useParams(); const navigate = useNavigate(); const [parties, setParties] = useState<SendParty[]>([{ name: '', cpf_cnpj: '', contact: '', signing_order: 1 }]); const [message, setMessage] = useState('Olá! Preparei nosso contrato. Leia com atenção e assine pelo link.'); const [error, setError] = useState(''); const [loading, setLoading] = useState(false); const [addPayment, setAddPayment] = useState(false); const [amount, setAmount] = useState(''); const [dueDate, setDueDate] = useState(''); const [result, setResult] = useState<{ signing_links: { name: string; url: string; verification_code?: string }[] }>()
  const user = auth.user(); const userIncluded = !!user && parties.some(party => party.contact === user.email)
  const update = (index: number, key: keyof SendParty, value: string) => setParties(current => current.map((party, position) => position === index ? { ...party, [key]: key === 'signing_order' ? Number(value) : value } : party))
  function includeUser() {
    if (!user) return
    setParties(current => {
      const empty = current.findIndex(party => !party.name && !party.cpf_cnpj && !party.contact)
      return empty >= 0
        ? current.map((party, index) => index === empty ? { ...party, name: user.name, contact: user.email } : party)
        : [...current, { name: user.name, cpf_cnpj: '', contact: user.email, signing_order: current.length + 1 }]
    })
  }
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setLoading(true); setError(''); try { const sent = await api<{ signing_links: { name: string; url: string; verification_code?: string }[] }>(`/api/contracts/${id}/send/`, { method: 'POST', body: JSON.stringify({ parties, message, installments: addPayment ? [{ amount, due_date: dueDate }] : [] }) }); setResult(sent) } catch (err) { setError((err as Error).message) } finally { setLoading(false) } }
  if (result) return <Shell><section className="page-head container"><p className="context">Envio concluído</p><h1>Links prontos para assinatura.</h1><p>Os contatos foram notificados. No modo local, copie os links e use os códigos abaixo para testar o fluxo.</p></section><section className="send-result container">{result.signing_links.map(link => <article key={link.url}><div><strong>{link.name}</strong><a href={link.url}>{link.url}</a>{link.verification_code && <code>Código: {link.verification_code}</code>}</div><Button secondary onClick={() => navigator.clipboard.writeText(link.url)}>Copiar link</Button></article>)}<Button onClick={() => navigate(`/contratos/${id}`)}>Acompanhar contrato</Button></section></Shell>
  return <Shell><section className="page-head container"><Link to={`/contratos/${id}/revisar`}>← Voltar à revisão</Link><p className="context">Assinatura eletrônica</p><h1>Quem precisa assinar?</h1><p>Adicione as partes na ordem certa. Cada uma recebe um link e um código temporário.</p></section><form className="send-form container" onSubmit={submit}><div className="self-sign"><div><strong>Você também participa do contrato?</strong><span>Inclua seus dados para receber um link e assinar como as demais partes.</span></div><Button type="button" secondary disabled={userIncluded} onClick={includeUser}>{userIncluded ? 'Você foi incluído' : 'Eu também vou assinar'}</Button></div>{parties.map((party, index) => <fieldset key={index}><legend>Parte {index + 1}</legend><div className="field-grid"><label>Nome completo<input required value={party.name} onChange={event => update(index, 'name', event.target.value)} /></label><label>CPF ou CNPJ<input required value={party.cpf_cnpj} onChange={event => update(index, 'cpf_cnpj', event.target.value)} /></label><label>E-mail ou WhatsApp<input required value={party.contact} onChange={event => update(index, 'contact', event.target.value)} /></label><label>Ordem de assinatura<input type="number" min="1" required value={party.signing_order} onChange={event => update(index, 'signing_order', event.target.value)} /></label></div>{parties.length > 1 && <button type="button" className="danger-link" onClick={() => setParties(current => current.filter((_, position) => position !== index))}>Remover parte</button>}</fieldset>)}<Button type="button" secondary onClick={() => setParties(current => [...current, { name: '', cpf_cnpj: '', contact: '', signing_order: current.length + 1 }])}>+ Adicionar outra parte</Button><label>Mensagem<textarea rows={4} value={message} onChange={event => setMessage(event.target.value)} /></label><label className="check"><input type="checkbox" checked={addPayment} onChange={event => setAddPayment(event.target.checked)} /> Gerar uma cobrança Pix vinculada</label>{addPayment && <div className="field-grid"><label>Valor da parcela<input type="number" step="0.01" min="0.01" required value={amount} onChange={event => setAmount(event.target.value)} /></label><label>Vencimento<input type="date" required value={dueDate} onChange={event => setDueDate(event.target.value)} /></label></div>}<ErrorMessage message={error} /><Button disabled={loading}>{loading ? 'Enviando…' : 'Gerar links e enviar'}</Button></form></Shell>
}

function Dashboard() {
  const [contracts, setContracts] = useState<Contract[]>([]); const [filter, setFilter] = useState('all'); const [error, setError] = useState('')
  useEffect(() => { api<Contract[]>('/api/contracts/').then(setContracts).catch(err => setError(err.message)) }, [])
  if (!auth.user()) return <Navigate to="/entrar" />
  const filtered = filter === 'all' ? contracts : contracts.filter(contract => contract.status === filter)
  return <Shell><section className="dashboard-head container"><div><p className="context">Seu cofre</p><h1>Contratos</h1><p>{contracts.length ? `${contracts.length} acordo${contracts.length > 1 ? 's' : ''} sob controle.` : 'Seu primeiro acordo começa por um modelo.'}</p></div><Link className="button" to="/modelos">Novo contrato</Link></section><section className="filters container" aria-label="Filtrar contratos">{['all', 'draft', 'sent', 'partial', 'signed'].map(value => <button className={filter === value ? 'active' : ''} key={value} onClick={() => setFilter(value)}>{value === 'all' ? 'Todos' : statusLabel[value]}</button>)}</section><section className="vault container"><ErrorMessage message={error} />{!error && filtered.length === 0 ? <div className="empty"><h2>{contracts.length ? 'Nenhum contrato neste status.' : 'Seu cofre está pronto.'}</h2><p>{contracts.length ? 'Troque o filtro para encontrar outros acordos.' : 'Escolha um modelo e responda às perguntas para criar seu primeiro rascunho.'}</p><Link className="button" to="/modelos">Explorar modelos</Link></div> : <div className="table-wrap"><table><thead><tr><th>Contrato</th><th>Status</th><th>Atualizado</th><th>Partes</th><th></th></tr></thead><tbody>{filtered.map(contract => <tr key={contract.id}><td><strong>{contract.title}</strong><span>{contract.template_name}</span></td><td><span className={`status ${contract.status}`}>{statusLabel[contract.status]}</span></td><td>{new Date(contract.updated_at).toLocaleDateString('pt-BR')}</td><td>{contract.parties.length || '—'}</td><td><Link to={contract.status === 'draft' ? `/contratos/${contract.id}/revisar` : `/contratos/${contract.id}`}>Abrir →</Link></td></tr>)}</tbody></table></div>}</section></Shell>
}

function ContractDetail() {
  const { id } = useParams(); const [contract, setContract] = useState<Contract>(); const [events, setEvents] = useState<AuditEvent[]>([]); const [error, setError] = useState('')
  useEffect(() => { Promise.all([api<Contract>(`/api/contracts/${id}/`), api<AuditEvent[]>(`/api/contracts/${id}/audit/`)]).then(([value, audit]) => { setContract(value); setEvents(audit) }).catch(err => setError(err.message)) }, [id])
  async function downloadPdf() { try { const response = await fetch(pdfUrl(Number(id)), { headers: { Authorization: `Bearer ${auth.token()}` } }); if (!response.ok) throw new Error('Não foi possível baixar o PDF.'); const url = URL.createObjectURL(await response.blob()); const anchor = document.createElement('a'); anchor.href = url; anchor.download = `contrato-${id}.pdf`; anchor.click(); URL.revokeObjectURL(url) } catch (err) { setError((err as Error).message) } }
  return <Shell><section className="detail-head container"><div><Link to="/cofre">← Voltar ao cofre</Link><h1>{contract?.title}</h1><div className="detail-meta"><span className={`status ${contract?.status}`}>{contract && statusLabel[contract.status]}</span><span>Criado em {contract && new Date(contract.created_at).toLocaleDateString('pt-BR')}</span></div></div><Button onClick={downloadPdf}>Baixar PDF assinado</Button></section><ErrorMessage message={error} /><section className="detail-grid container"><div><section className="panel"><h2>Partes</h2>{contract?.parties.map(party => <div className="party-row" key={party.id}><div><strong>{party.name}</strong><span>{party.contact}</span></div><span className={`status ${party.status}`}>{statusLabel[party.status] || party.status}</span></div>)}</section><section className="panel"><h2>Parcelas</h2>{contract?.installments.length ? contract.installments.map(item => <div className="party-row" key={item.id}><div><strong>{formatCurrency(item.amount)}</strong><span>Vence em {new Date(`${item.due_date}T12:00:00`).toLocaleDateString('pt-BR')}</span></div><span className={`status ${item.status}`}>{statusLabel[item.status]}</span></div>) : <p>Nenhuma parcela vinculada.</p>}</section></div><aside className="timeline"><h2>Trilha de auditoria</h2>{events.length ? events.map(event => <div className="event" key={event.id}><span /><div><strong>{statusLabel[event.type] || event.type} por {event.party_name}</strong><time>{new Date(event.timestamp).toLocaleString('pt-BR')}</time><small>{event.ip || 'IP não informado'}</small></div></div>) : <p>A atividade de assinatura aparecerá aqui.</p>}{contract?.hash_sha256 && <div className="hash"><strong>Hash SHA-256</strong><code>{contract.hash_sha256}</code></div>}</aside></section></Shell>
}

function SignatureCanvas({ onChange }: { onChange: (value: string) => void }) {
  const ref = useRef<HTMLCanvasElement>(null); const drawing = useRef(false)
  const point = (event: PointerEvent<HTMLCanvasElement>) => { const canvas = event.currentTarget; const rect = canvas.getBoundingClientRect(); return [(event.clientX - rect.left) * canvas.width / rect.width, (event.clientY - rect.top) * canvas.height / rect.height] as const }
  const start = (event: PointerEvent<HTMLCanvasElement>) => { drawing.current = true; event.currentTarget.setPointerCapture(event.pointerId); const context = ref.current?.getContext('2d'); const [x, y] = point(event); context?.beginPath(); context?.moveTo(x, y) }
  const move = (event: PointerEvent<HTMLCanvasElement>) => { if (!drawing.current) return; const context = ref.current?.getContext('2d'); const [x, y] = point(event); if (context) { context.lineWidth = 2; context.lineCap = 'round'; context.strokeStyle = '#1E3A5F'; context.lineTo(x, y); context.stroke() } }
  const stop = () => { drawing.current = false; if (ref.current) onChange(ref.current.toDataURL()) }
  return <div className="canvas-wrap"><canvas ref={ref} width="560" height="180" onPointerDown={start} onPointerMove={move} onPointerUp={stop} onPointerCancel={stop} aria-label="Área para desenhar assinatura" /><button type="button" onClick={() => { ref.current?.getContext('2d')?.clearRect(0, 0, 560, 180); onChange('') }}>Limpar</button></div>
}

function PublicSign() {
  const { token } = useParams(); const [data, setData] = useState<{ contract: { title: string; final_body: string; status: string }; party: { name: string; status: string } }>(); const [code, setCode] = useState(''); const [verified, setVerified] = useState(false); const [signature, setSignature] = useState(''); const [drawn, setDrawn] = useState(''); const [accepted, setAccepted] = useState(false); const [done, setDone] = useState(false); const [error, setError] = useState('')
  useEffect(() => { api(`/public/sign/${token}/`, {}, false).then(value => setData(value as typeof data)).catch(err => setError(err.message)) }, [token])
  async function verify() { setError(''); try { await api(`/public/sign/${token}/verify/`, { method: 'POST', body: JSON.stringify({ code }) }, false); setVerified(true) } catch (err) { setError((err as Error).message) } }
  async function sign() { setError(''); try { await api(`/public/sign/${token}/sign/`, { method: 'POST', body: JSON.stringify({ code, signature: signature || drawn }) }, false); setDone(true) } catch (err) { setError((err as Error).message) } }
  if (done) return <main className="public-page"><section className="signed-success"><span>✓</span><h1>Assinatura registrada.</h1><p>O responsável pelo contrato já pode acompanhar a atualização no cofre.</p></section></main>
  return <main className="public-page"><header><Link className="brand" to="/">ContratoFácil</Link><span>Ambiente seguro de assinatura</span></header><section className="sign-layout"><article className="contract-paper"><p className="context">Documento para assinatura</p><h1>{data?.contract.title}</h1><ContractBody body={data?.contract.final_body || ''} /></article><aside className="sign-panel"><h2>Olá, {data?.party.name || 'signatário'}.</h2><p>Leia o contrato completo. Depois confirme o código enviado ao seu contato.</p><label>Código de 6 dígitos<input inputMode="numeric" maxLength={6} value={code} onChange={event => setCode(event.target.value.replace(/\D/g, ''))} /></label>{!verified ? <Button disabled={code.length !== 6} onClick={verify}>Verificar código</Button> : <><div className="verified">Identidade verificada</div><label>Assinatura digitada<input value={signature} onChange={event => setSignature(event.target.value)} placeholder="Digite seu nome completo" /></label><span className="or">ou desenhe abaixo</span><SignatureCanvas onChange={setDrawn} /><label className="check"><input type="checkbox" checked={accepted} onChange={event => setAccepted(event.target.checked)} /> Li e concordo com o documento acima.</label><Button disabled={!accepted || (!signature && !drawn)} onClick={sign}>Assinar contrato</Button></>}<ErrorMessage message={error} /><LegalNotice /><small>Ao assinar, data, horário, IP e dispositivo serão registrados na trilha de auditoria.</small></aside></section></main>
}

export default function App() {
  return <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/entrar" element={<AuthPage />} />
    <Route path="/cadastro" element={<AuthPage register />} />
    <Route path="/modelos" element={<Templates />} />
    <Route path="/criar/:templateId" element={<Wizard />} />
    <Route path="/contratos/:id/revisar" element={<Review />} />
    <Route path="/contratos/:id/enviar" element={<SendContract />} />
    <Route path="/contratos/:id" element={<ContractDetail />} />
    <Route path="/cofre" element={<Dashboard />} />
    <Route path="/assinar/:token" element={<PublicSign />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
}
