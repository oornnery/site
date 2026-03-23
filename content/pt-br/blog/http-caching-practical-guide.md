---
title: "Cache HTTP: Um Guia Prático"
slug: "http-caching-practical-guide"
description: "Cache-Control, ETags e stale-while-revalidate explicados com exemplos reais de backend."
date: "2025-12-15"
author: "Fabio Souza"
tags:
  - "http"
  - "caching"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Cache HTTP é uma das ferramentas de performance com maior
alavancagem disponíveis. A maioria dos times de backend a
subutiliza porque a semântica dos headers é confusa.

## Diretivas Cache-Control que importam

- `max-age=N` — o navegador faz cache por N segundos
- `s-maxage=N` — a CDN faz cache por N segundos, sobrescreve
  `max-age` para caches compartilhados
- `no-cache` — sempre revalide antes de usar a cópia em cache
- `no-store` — nunca faça cache (use para dados sensíveis)
- `stale-while-revalidate=N` — sirva conteúdo stale enquanto
  busca o conteúdo fresco em background

## ETags para requests condicionais

Um ETag é um token de versão para um recurso. Clientes enviam
`If-None-Match` com o ETag armazenado; servidores respondem com
`304 Not Modified` se nada mudou.

```python
from hashlib import md5

def etag_for(content: str) -> str:
    return f'"{md5(content.encode()).hexdigest()}"'
```

## O que cachear agressivamente

Assets estáticos com nomes de arquivo baseados em hash de
conteúdo: `max-age=31536000, immutable`. Respostas de API que
mudam raramente: `max-age=60, stale-while-revalidate=300`.

## O que não cachear

Dados específicos do usuário, tokens CSRF e qualquer coisa com
acesso controlado por `Authorization` devem usar
`Cache-Control: private, no-store`.
