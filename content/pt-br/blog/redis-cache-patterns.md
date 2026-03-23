---
title: "Padrões de Cache Redis Que Realmente Funcionam"
slug: "redis-cache-patterns"
description: "Cache-aside, write-through e estratégias de TTL para serviços backend usando Redis."
date: "2025-10-20"
author: "Fabio Souza"
tags:
  - "redis"
  - "caching"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Redis é simples de adicionar e fácil de usar incorretamente.
Os padrões abaixo cobrem os casos de uso comuns e os modos de
falha que vale conhecer desde o início.

## Cache-aside (lazy loading)

A aplicação verifica o cache antes de consultar o banco de
dados. Em caso de miss, ela busca no banco, armazena o
resultado e o retorna.

Este é o padrão default mais seguro. Ele só cacheia dados que são realmente
lidos.

## Write-through

A cada escrita no banco de dados, também atualize o cache.
Mantém o cache aquecido e consistente, mas adiciona latência
às escritas.

Use isso quando as leituras são muito frequentes e cache misses são caros.

## Estratégia de TTL

Toda chave deve ter um TTL. Caches sem limite crescem até o
Redis despejar entradas sob pressão de memória, o que é
imprevisível. Defina TTLs com base em quão stale os dados podem
ficar, não em defaults arbitrários.

## Thundering herd na expiração de cache

Quando uma chave popular expira, muitas requests concorrentes
atingem o banco de dados simultaneamente. Mitigue com expiração
antecipada probabilística ou um lock distribuído que permite
que uma request regenere o cache enquanto as outras esperam.

## Convenção de nomenclatura de chaves

Use um esquema de prefixo consistente:
`{service}:{entity}:{id}` (ex: `api:user:1234`). Deleção
baseada em prefixo com `SCAN` é mais fácil de operar.
