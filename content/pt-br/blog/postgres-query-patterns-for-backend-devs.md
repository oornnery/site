---
title: "Padrões de Queries PostgreSQL Para Devs Backend"
slug: "postgres-query-patterns-for-backend-devs"
description: "Técnicas práticas de query que melhoram o throughput sem over-engineering no schema."
date: "2026-02-05"
author: "Fabio Souza"
tags:
  - "postgres"
  - "backend"
  - "python"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

As queries que deixam um sistema lento raramente são as óbvias.
Elas se escondem atrás de loops N+1, índices ausentes em
foreign keys e `SELECT *` em caminhos críticos.

## Sempre indexe o que você filtra

Colunas de foreign key não são automaticamente indexadas no
PostgreSQL. Se você faz join ou filtra por `user_id`
regularmente, adicione o índice explicitamente.

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

## Use EXPLAIN ANALYZE antes de otimizar

Intuição não é confiável. Execute
`EXPLAIN (ANALYZE, BUFFERS)` e observe sequential scans e
estimativas de linhas antes de mexer no schema.

## Prefira CTEs para legibilidade, nem sempre para performance

O PostgreSQL materializa CTEs de forma diferente dependendo da
versão e das dicas do query planner. Na maioria dos casos, uma
subquery dentro de uma cláusula `WHERE` dá ao planner mais
liberdade para otimizar.

## Evite SELECT * no código da aplicação

Buscar colunas desnecessárias aumenta o overhead de rede e
quebra suposições de cache. Nomeie suas colunas explicitamente
e adicione apenas o que o chamador precisa.
