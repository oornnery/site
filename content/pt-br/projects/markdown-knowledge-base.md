---
title: "Base de Conhecimento em Markdown"
slug: "markdown-knowledge-base"
description: >-
  Uma arquitetura de site orientada a conteudo usando frontmatter markdown e
  renderizacao baseada em componentes.
thumbnail: "/static/images/projects/markdown-knowledge-base.svg"
tags: ["markdown", "jinja", "content"]
tech_stack: ["Python", "Jinja2", "Jx", "YAML"]
github_url: "https://github.com/oornnery/markdown-knowledge-base"
live_url: ""
date: "2024-12-21"
featured: false
---

## Visao geral

Este projeto foca em pipelines de conteudo para paginas de estilo estatico
servidas a partir de um backend dinamico.
Arquivos markdown sao parseados, transformados em HTML e injetados em
componentes de pagina reutilizaveis.

## Funcionalidades

- Suporte a frontmatter YAML
- Cache de renderizacao para carregamento de conteudo
- Metadados SEO por pagina e por projeto
- Shells de pagina reutilizaveis com importacao de componentes

## Resultado

O resultado final e simples de manter para desenvolvedores e editores.
Atualizacoes de conteudo nao exigem alteracoes no codigo das rotas.

## Pipeline de conteudo

A ideia central e tornar a autoria flexivel mantendo as regras de renderizacao
previsiveis.
O markdown deve ser a parte facil; a consistencia deve vir do pipeline.

### Contrato de frontmatter

O frontmatter define os metadados tipados exigidos por cada template de pagina.
Isso evita o problema comum onde o conteudo e renderizado silenciosamente com
campos ausentes ou cards quebrados.

### Etapa de renderizacao

O markdown e convertido em HTML, sanitizado e entao inserido em layouts de
pagina reutilizaveis.
Ao manter essas etapas explicitas, o site pode evoluir seus templates sem
alterar o modelo de autoria.

## Ergonomia de autoria

Editores precisam de um sistema facil de estender sem precisar aprender toda a
arquitetura da aplicacao.

### Estrutura de arquivos previsivel

As paginas ficam em pastas bem delimitadas com um arquivo por entrada.
Isso significa que criar um novo artigo ou projeto e principalmente uma
operacao de conteudo, nao uma tarefa de engenharia.

### Shells de pagina reutilizaveis

Layouts e componentes compartilhados definem a estrutura visual uma unica vez.
Arquivos de conteudo focam no significado em vez de repetir convencoes de
marcacao.

## Consideracoes de desempenho

Um site orientado a markdown ainda precisa de disciplina operacional.

### Carregamento com cache

O conteudo parseado e armazenado em cache para evitar reconstruir as mesmas
paginas a cada requisicao. Isso mantem o SSR responsivo mesmo conforme o numero
de entradas cresce.

### Saida HTML segura

A sanitizacao faz parte do pipeline, nao e um complemento opcional.
Isso permite recursos de texto rico sem aceitar HTML arbitrario de autores de
conteudo.

## Por que essa estrutura perdura

A verdadeira vantagem nao e que o conteudo vive em markdown.
E que o modelo de conteudo, o modelo de renderizacao e o modelo de pagina estao
separados.

- autores editam conteudo
- templates controlam a apresentacao
- servicos decidem qual contexto tipado chega a cada pagina

Essa separacao mantem a base de codigo mais calma quando novas secoes, feeds ou
paginas de arquivo sao adicionadas depois.

## Extensoes futuras

As proximas adicoes seriam indexacao de conteudo relacionado e suporte leve a
preview editorial. Elas se encaixam naturalmente porque o pipeline de conteudo
ja possui metadados tipados e fronteiras de renderizacao centralizadas.
