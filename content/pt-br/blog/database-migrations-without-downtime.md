---
title: "Migrações de Banco de Dados Sem Downtime"
slug: "database-migrations-without-downtime"
description: "Padrões seguros de migração para adicionar colunas, renomear campos e alterar constraints em bancos de dados em produção."
date: "2025-09-12"
author: "Fabio Souza"
tags:
  - "postgres"
  - "backend"
  - "infra"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Migrações sem downtime exigem pensar em mudanças de schema em
duas fases: o que o banco de dados pode fazer com segurança
enquanto o código antigo está rodando, e o que o novo código
assume após o deploy.

## Adicionar uma coluna nullable

Seguro de fazer com o código antigo rodando. O novo código lê
a coluna; o código antigo a ignora. Torne a coluna non-nullable
em uma migração separada após o backfill.

## Renomear uma coluna

Perigoso com uma única migração. A sequência segura:

1. Adicionar a nova coluna.
2. Escrever em ambas as colunas na aplicação.
3. Fazer o backfill da nova coluna.
4. Mudar as leituras para a nova coluna.
5. Parar de escrever na coluna antiga.
6. Remover a coluna antiga.

## Adicionar índices de forma concorrente

`CREATE INDEX` bloqueia a tabela por padrão. Use
`CREATE INDEX CONCURRENTLY` para construir o índice sem
bloquear leituras ou escritas.

## Alterar o tipo de uma coluna

A maioria das mudanças de tipo exige uma reescrita completa da
tabela. Use uma nova coluna, faça o backfill e troque em
etapas. Nunca altere o tipo de uma coluna em uma única migração
em uma tabela grande em produção.

## Mantenha as migrações reversíveis

Toda migração deve ter um caminho de `downgrade`. Não porque
você vai usá-lo com frequência, mas porque isso obriga você a
raciocinar sobre a mudança de schema completamente.
