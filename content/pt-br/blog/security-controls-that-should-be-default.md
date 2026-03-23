---
title: "Controles de Segurança Que Deveriam Ser Padrão"
slug: "security-controls-that-should-be-default"
description: "Um conjunto baseline de controles que previne padrões comuns de abuso web desde cedo."
date: "2025-12-11"
author: "Fabio Souza"
tags:
  - "security"
  - "owasp"
  - "fastapi"
featured: true
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Hardening de segurança é mais fácil quando controles são
comportamento padrão, não add-ons opcionais.

Para serviços pequenos e médios, este baseline já bloqueia muitos incidentes:

- Geração + validação de token CSRF para formulários
- Verificações rigorosas de content-type
- Limites de tamanho de body por sensibilidade da rota
- Rate limits globais e por rota
- Trusted hosts + allowlist de CORS
- Headers de segurança consistentes e CSP

O objetivo não é perfeição. O objetivo é eliminar caminhos de
ataque de baixo esforço desde cedo.

## Defaults vencem documentos de política

A erosão de segurança geralmente acontece quando a proteção
depende de lembrar de ativá-la. Um controle que exige que cada
autor de funcionalidade faça opt-in eventualmente será esquecido
sob pressão de tempo.

É por isso que eu prefiro defaults seguros integrados ao shell da aplicação:

- middleware para headers e validação de host
- proteção compartilhada de formulários para fluxos sensíveis a CSRF
- limites de body aplicados antes de trabalho pesado começar
- wiring de dependências que centraliza allowlists e rate limits

Isso muda a segurança de "por favor lembre-se" para "você precisa contornar de propósito."

## Controles que bloqueiam abuso comum desde cedo

Para sites pessoais ou de produto, os problemas mais comuns raramente são exóticos.

Geralmente são:

- spam contra fluxos de contato
- bodies de request superdimensionados
- erros de headers de origin e host
- endpoints de analytics abusados como coletores abertos
- sanitização fraca de conteúdo para Markdown ou rich text

Bons defaults reduzem drasticamente esses caminhos antes que se tornem incidentes.

## Separe responsabilidades de edge e aplicação claramente

Eu não quero que a aplicação e o proxy disputem o mesmo trabalho sem intenção.

No edge, eu quero modelagem ampla de tráfego:

- caps de conexão e in-flight
- controles grosseiros de tamanho de body
- rate limiting amplo
- allowlists baseadas em IP quando necessário

Na aplicação, eu quero proteção ciente de contexto:

- limites de body por rota
- validação de CSRF
- trusted hosts
- aplicação de content-type
- headers de resposta e sanitização de conteúdo

Essa divisão mantém a aplicação de controles em camadas, mas compreensível.

## Validação deve falhar explicitamente

Um problema de segurança sutil é comportamento de falha vago.

Se input malformado, tokens CSRF ausentes e content-types não
suportados colapsam no mesmo tratamento genérico, fica mais
difícil debugar abuso e mais difícil raciocinar sobre proteções.

Eu prefiro caminhos de falha estáveis e explícitos com status
codes e logs previsíveis. Isso ajuda tanto defensores quanto
mantenedores sem expor internos sensíveis.

## Revise o baseline como código de produto

Controles de segurança são comportamento de produto. Eles
precisam de revisão da mesma forma que funcionalidades de
negócio.

Minha revisão rápida de baseline é assim:

1. Um host inseguro consegue alcançar a aplicação?
2. Um body grande ou malformado consegue contornar a intenção da rota?
3. Um post de formulário consegue ter sucesso sem um token CSRF válido?
4. Conteúdo Markdown ou HTML consegue renderizar elementos inseguros?
5. Abuso contra rotas de analytics ou contato pode ser throttled?

Se essas respostas são visíveis em testes e na estrutura do
código, o baseline tende a permanecer forte ao longo do tempo.

O ponto não é criar uma fortaleza ao redor de um site simples.
O ponto é tornar caminhos comuns de abuso caros desde o início.
