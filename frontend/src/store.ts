import { create } from 'zustand'

export type Answers = Record<string, string | number | boolean>

type WizardState = {
  templateId?: number
  step: number
  answers: Answers
  start: (templateId: number) => void
  setAnswer: (key: string, value: string | number | boolean) => void
  next: () => void
  previous: () => void
  reset: () => void
}

const initial = { templateId: undefined, step: 0, answers: {} }

export const useWizard = create<WizardState>((set) => ({
  ...initial,
  start: (templateId) => set({ templateId, step: 0, answers: {} }),
  setAnswer: (key, value) => set((state) => ({ answers: { ...state.answers, [key]: value } })),
  next: () => set((state) => ({ step: state.step + 1 })),
  previous: () => set((state) => ({ step: Math.max(0, state.step - 1) })),
  reset: () => set(initial),
}))

export function questionIsVisible(
  question: { key?: string; display_condition?: { key?: string; equals?: unknown } },
  answers: Answers,
) {
  const condition = question.display_condition
  if (!condition?.key) return true
  return 'equals' in condition ? answers[condition.key] === condition.equals : Boolean(answers[condition.key])
}

export const formatCurrency = (value: string | number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value || 0))
