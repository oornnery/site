---
title: "Estratégias de Versionamento de API"
slug: "api-versioning-strategies"
description: "Versionamento por caminho de URL, header e query param comparados — com trade-offs práticos de cada abordagem."
date: "2025-08-28"
author: "Fabio Souza"
tags:
  - "api"
  - "architecture"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Toda API pública eventualmente precisa de versionamento.
Escolher a estratégia certa desde o início evita migrações
dolorosas no futuro.

## Versionamento por caminho de URL

```text
GET /v1/users
GET /v2/users
```

A opção mais visível e amigável para cache. Clientes podem
salvar ou fixar URLs diretamente. A desvantagem é que a versão
polui todas as rotas.

## Versionamento por header

```text
GET /users
API-Version: 2024-01-01
```

Mantém as URLs limpas. Mais difícil de testar no navegador ou
compartilhar como link. Comum nas APIs do Stripe e GitHub.

## Query parameter

```text
GET /users?version=2
```

Fácil de adicionar e testar, mas frequentemente tratado como
algo secundário. O cache fica mais complexo porque a chave de
cache precisa incluir o parâmetro.

## O que importa mais do que a estratégia

Consistência e uma política clara de descontinuação. Escolha
uma abordagem, documente-a e dê aos clientes tempo suficiente
antes de remover versões antigas. A maioria dos times investe
pouco em comunicação de descontinuação e investe demais na
estratégia de versionamento.
