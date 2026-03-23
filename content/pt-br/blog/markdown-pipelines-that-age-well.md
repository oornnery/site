---
title: "Pipelines de Markdown Que Envelhecem Bem"
slug: "markdown-pipelines-that-age-well"
description: "Uma abordagem de pipeline de conteúdo que se mantém sustentável após o primeiro lote de posts."
date: "2026-01-15"
author: "Fabio Souza"
tags:
  - "markdown"
  - "content"
  - "python"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Sites baseados em Markdown permanecem agradáveis apenas quando
o pipeline de conteúdo permanece previsível.

A tentação é tratar Markdown como texto não estruturado e
resolver casos especiais nos templates depois. Isso funciona
até o conteúdo precisar de sanitização, regras de metadados,
comportamento de fallback e previews em múltiplas páginas.

## Frontmatter é um contrato

Eu trato o frontmatter como um contrato de API entre conteúdo e renderização.

Cada post deve resolver corretamente para:

- title
- slug
- description
- date
- tags
- author
- estado de publicação

Se o contrato é vago, a camada de renderização começa a
adivinhar. Adivinhar geralmente cria bugs sutis em SEO,
ordenação e navegação.

## Parsing e sanitização devem ficar centralizados

Os piores pipelines de Markdown são aqueles que fazem parsing em vários lugares.

Se um caminho renderiza Markdown bruto, outro caminho sanitiza
HTML e um terceiro caminho injeta comportamento de fallback
customizado, a saída se torna inconsistente rapidamente.

Eu prefiro um único pipeline de conteúdo que seja dono de:

1. descoberta de arquivos
2. validação de frontmatter
3. renderização de Markdown
4. sanitização de HTML
5. ordenação e cache

Assim, cada página consome o mesmo modelo estável de post.

## Fallbacks devem ser explícitos

Sistemas de conteúdo sempre encontram entradas imperfeitas eventualmente.

Talvez uma description esteja faltando. Talvez um body esteja
vazio. Talvez um gist remoto esteja indisponível. O importante
é que o comportamento de fallback seja intencional.

Exemplos que funcionam bem:

- derivar uma description do primeiro parágrafo quando ausente
- pular drafts inválidos com um log claro
- usar um body placeholder quando não existe conteúdo
- normalizar URLs de discussão uma vez, em um lugar só

São detalhes pequenos, mas eles decidem se o conteúdo parece confiável.

## Modelos de conteúdo melhoram a renderização

Uma vez que Markdown se torna um modelo de domínio tipado, as
funcionalidades das páginas ficam mais fáceis.

Coisas como:

- páginas de tags
- navegação de post anterior e próximo
- geração de feed
- seleção de posts em destaque
- cálculo de tempo de leitura

deixam de ser gambiarras em templates e se tornam lógica direta de service.

Esse é o verdadeiro retorno. Um pipeline de Markdown limpo não
é sobre o parser. É sobre tornar cada página downstream mais
simples.

## Mantenha o atrito de autoria baixo

O sistema ainda precisa ser agradável para escrever.

Para sites pequenos, eu quero que autores possam:

- colocar um arquivo em uma pasta
- preencher o frontmatter óbvio
- escrever Markdown sem sintaxe especial em todo lugar
- confiar que a saída será renderizada de forma consistente

Se autores de conteúdo precisam entender o renderizador para
publicar um post, o sistema já é esperto demais.
