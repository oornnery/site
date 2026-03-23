---
title: "pg-schema-diff"
slug: "postgres-schema-diff"
description: "Uma ferramenta CLI que compara dois schemas PostgreSQL e gera SQL de migracao seguro, destacando alteracoes destrutivas antes da execucao."
tags: ["python", "postgres", "tooling"]
tech_stack: ["Python", "psycopg", "Typer", "Rich"]
github_url: "https://github.com/oornnery/pg-schema-diff"
date: "2025-10-20"
featured: false
---

## Visao geral

Pare de rodar diffs de `pg_dump` manualmente. O `pg-schema-diff` conecta-se a
dois bancos de dados (ou le arquivos de dump SQL) e produz um diff legivel alem
de SQL de migracao pronto para execucao.

## Funcionalidades

- Diff lado a lado de tabelas, colunas, indices e constraints
- Sinaliza alteracoes destrutivas (DROP, ALTER TYPE) em vermelho antes da execucao
- Gera SQL puro — sem formato proprietario de migracao
- Funciona com arquivos de dump para comparacao offline

## Uso

```bash
pgsd compare --source $SOURCE_DSN --target $TARGET_DSN
pgsd compare --source schema_v1.sql --target schema_v2.sql --output migration.sql
```
