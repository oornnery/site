---
title: "UX Renderizada no Servidor Com JavaScript Leve"
slug: "server-rendered-ux-with-lightweight-javascript"
description: "Como eu mantenho páginas interativas sem transformar um site simples em uma aplicação client-side."
date: "2025-10-02"
author: "Fabio Souza"
tags:
  - "frontend"
  - "ssr"
  - "javascript"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Páginas renderizadas no servidor não precisam parecer estáticas.

O truque é adicionar JavaScript apenas onde a interação melhora
significativamente a página, em vez de reconstruir toda a
interface como uma aplicação client-side.

## Comece pelo contrato HTML

Para páginas SSR, o HTML já deve expressar a experiência principal:

- o conteúdo é legível sem hydration
- links e formulários funcionam por padrão
- metadados e estrutura estão completos na primeira renderização

JavaScript então melhora a experiência em vez de resgatá-la.

## Bons progressive enhancements são específicos

Eu gosto de melhorias pequenas com escopo claro:

- barras de progresso de leitura
- ativação de sumário (table of contents)
- carrosséis de posts em destaque
- estados de submissão de formulário
- comportamento leve de disclosure ou filtro

Esses são focados o suficiente para testar e baratos o suficiente para manter.

## Mantenha o comportamento próximo da marcação semântica

Uma regra útil é que JS deve se vincular a data attributes
significativos, não a suposições aleatórias sobre a forma do
DOM.

Isso torna o comportamento mais resiliente quando templates
evoluem. Também mantém a estrutura renderizada pelo servidor
legível durante a revisão.

## Evite construir um segundo sistema de roteamento

Sites pequenos se tornam mais difíceis de manter quando
comportamento client-side começa a substituir decisões do
servidor.

Se navegação, carregamento de conteúdo ou contratos de página
são duplicados em JavaScript, o codebase começa a carregar duas
aplicações em vez de uma.

Para um site pessoal ou de conteúdo, isso geralmente não vale a pena.

## Meça o trade-off honestamente

O teste que eu uso é simples: essa interação melhora a clareza
o suficiente para justificar as partes móveis extras?

Se sim, adicione o menor script que resolve o problema.

Se não, deixe a página renderizada pelo servidor permanecer
simples. Isso não é um compromisso. Para muitos sites, é a
decisão de produto mais limpa.
