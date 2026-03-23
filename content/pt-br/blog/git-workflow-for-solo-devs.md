---
title: "Workflow Git Para Devs Solo"
slug: "git-workflow-for-solo-devs"
description: "Um workflow Git leve porém disciplinado que mantém projetos solo limpos e prontos para deploy."
date: "2025-07-01"
author: "Fabio Souza"
tags:
  - "git"
  - "devx"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Trabalhar sozinho remove a pressão de seguir um workflow de
equipe, mas disciplina importa mais quando não há code review
para pegar erros.

## Mantenha a main sempre pronta para deploy

Nunca faça commit de código quebrado ou inacabado na main. Use
branches de curta duração mesmo trabalhando sozinho.

## Faça commits por responsabilidade, não por tempo

Um bom commit encapsula uma mudança lógica. Um commit ruim
agrupa três correções não relacionadas porque "eu já estava
mexendo nesse arquivo." Commits atômicos tornam `git bisect` e
`git log` realmente úteis.

## Escreva mensagens de commit que expliquem o porquê

```text
fix: prevent CSRF token reuse after form submission

Tokens were being accepted twice in high-latency requests. Added a
one-time-use check in the validation layer.
```

O "o quê" está no diff. O "porquê" pertence à mensagem.

## Use tags para releases

Um `git tag v1.2.0` com versão semântica em cada deploy cria
uma referência permanente. Quando um bug é reportado "depois da
última atualização", você sabe exatamente onde procurar.

## Faça rebase antes de mergear na main

`git rebase main` mantém o histórico linear. Merge commits
adicionam ruído quando você é o único contribuidor.
