export type Template = {
  id: number
  name: string
  slug: string
  category: string
  version: number
  description: string
  question_count: number
}

export type Question = {
  id: number
  key: string
  text: string
  type: 'text' | 'value' | 'date' | 'option' | 'bool' | 'number' | 'textarea'
  options: string[]
  order: number
  display_condition: { key?: string; equals?: unknown }
  required: boolean
  help_text: string
}

export type Party = {
  id: number
  name: string
  cpf_cnpj: string
  contact: string
  signing_order: number
  status: string
  signed_at?: string
}

export type Installment = {
  id: number
  amount: string
  due_date: string
  status: string
  pix_txid: string
  paid_at?: string
}

export type Contract = {
  id: number
  template: number
  template_name: string
  title: string
  responses: Record<string, string | number | boolean>
  final_body: string
  status: 'draft' | 'sent' | 'partial' | 'signed' | 'cancelled'
  hash_sha256: string
  expires_at?: string
  created_at: string
  updated_at: string
  clauses: { key: string; title: string; text: string; explanation: string; order: number }[]
  parties: Party[]
  installments: Installment[]
}

export type AuditEvent = {
  id: number
  party_name: string
  type: 'viewed' | 'verified' | 'signed'
  ip?: string
  user_agent: string
  timestamp: string
}
