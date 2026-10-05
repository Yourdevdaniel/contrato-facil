import { beforeEach, describe, expect, it } from 'vitest'
import { formatCurrency, questionIsVisible, useWizard } from './store'

describe('wizard', () => {
  beforeEach(() => useWizard.getState().reset())

  it('stores answers and navigates without going below zero', () => {
    useWizard.getState().setAnswer('client_name', 'Loja Aurora')
    useWizard.getState().next()
    useWizard.getState().previous()
    useWizard.getState().previous()
    expect(useWizard.getState().answers.client_name).toBe('Loja Aurora')
    expect(useWizard.getState().step).toBe(0)
  })

  it('evaluates dependent questions and formats Brazilian currency', () => {
    expect(questionIsVisible({ key: 'percent', display_condition: { key: 'has_signal', equals: true } }, { has_signal: false })).toBe(false)
    expect(questionIsVisible({ key: 'percent', display_condition: { key: 'has_signal', equals: true } }, { has_signal: true })).toBe(true)
    expect(formatCurrency(1500)).toBe('R$ 1.500,00')
  })
})
