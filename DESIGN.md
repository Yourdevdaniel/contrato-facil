---
name: ContratoFácil
description: Contratos jurídicos guiados e assinatura eletrônica em linguagem simples.
colors:
  primary: "#1E3A5F"
  primary-deep: "#142B49"
  accent: "#C9A227"
  background: "#F8F9FB"
  surface: "#FFFFFF"
  ink: "#1A2332"
  muted: "#5A6B7F"
  success: "#2E7D5B"
  danger: "#C0392B"
  border: "#E3E8EF"
  control-border: "#AAB7C7"
  surface-muted: "#EDF1F5"
  success-soft: "#E1F2E9"
  success-ink: "#19523B"
  gold-soft: "#F4EDCF"
  gold-ink: "#654F0B"
  status-ink: "#405168"
  info-soft: "#E5EEF9"
  info-ink: "#294F80"
  warning-soft: "#F8F0D1"
  warning-ink: "#735C0C"
  danger-soft: "#F8E5E2"
  danger-ink: "#8B2D25"
  body-strong: "#344155"
  navy-line: "#506986"
  on-dark: "#D0DAE5"
  on-dark-muted: "#9CABBC"
  placeholder: "#65768A"
  focus: "#9B7910"
  control-hover: "#EEF2F7"
  choice-selected: "#E9EFF6"
  preview: "#E9EDF3"
  skeleton: "#E5EAF0"
  canvas: "#FBFCFD"
typography:
  display:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "clamp(2.5rem, 6vw, 5rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  document:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  sm: "4px"
  control: "8px"
  surface: "12px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "12px 20px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "12px 14px"
---

# Design System: ContratoFácil

## Overview

**Creative North Star: "Cartório claro"**

Rigor documental sem intimidação: superfícies claras, hierarquia firme e linguagem cotidiana. A landing pode usar Fraunces para dar caráter; o produto usa Inter e padrões familiares para desaparecer atrás da tarefa. Movimento comunica avanço, nunca decora.

**Key Characteristics:**

- Confiança por clareza e evidência.
- Densidade moderada e muito espaço respirável.
- Uma ação primária por contexto.
- Responsivo desde telas pequenas.

## Colors

Azul-marinho domina ações e estrutura; dourado aparece com parcimônia em hover e destaques.

**The One Warm Element Rule.** O dourado nunca compete com ações, estados semânticos ou texto.

## Typography

**Display Font:** Fraunces com fallback Georgia  
**Body Font:** Inter com fallback system-ui  
**Document Font:** Source Serif 4 com fallback Georgia

Títulos de marketing evocam documentos bem compostos; toda a UI operacional permanece direta e neutra. Texto corrido limita-se a 70 caracteres por linha.

## Elevation

Superfícies são planas por padrão. A sombra curta `0 1px 3px rgba(16,24,40,.08)` separa somente elementos realmente elevados; borda e sombra larga nunca aparecem juntas.

## Components

Botões, campos, navegação, tabelas e acordeões usam cantos de 8px, foco visível e estados hover, active, disabled, loading e error. Cartões existem apenas para entidades ou escolhas independentes. O documento usa Source Serif 4 e não herda estilos de UI.

## Do's and Don'ts

### Do:

- **Do** usar perguntas como “quem vai pagar?” e explicar termos ao lado do contrato.
- **Do** manter contraste AA, foco visível e alvos de toque de pelo menos 44px.
- **Do** mostrar status, datas, hash e eventos com rótulos explícitos.

### Don't:

- **Don't** parecer um escritório de advocacia antigo, um editor genérico ou uma fintech agressiva.
- **Don't** usar gradientes, glassmorphism, métricas decorativas ou grades de cartões idênticos.
- **Don't** esconder conteúdo atrás de animação ou depender apenas de cor para comunicar estado.
