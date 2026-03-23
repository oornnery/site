---
title: "Python Assíncrono: Erros Comuns"
slug: "async-python-common-mistakes"
description: "Erros que transformam código assíncrono em algo mais lento que seu equivalente síncrono."
date: "2026-01-10"
author: "Fabio Souza"
tags:
  - "python"
  - "async"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Python assíncrono é genuinamente útil para cargas de trabalho
intensivas em I/O. Também é fácil de usar incorretamente de
formas difíceis de diagnosticar.

## Chamadas bloqueantes dentro de coroutines

O erro mais comum é chamar uma função bloqueante dentro de um `async def`.

```python
async def get_user(user_id: int) -> User:
    # Isso bloqueia todo o event loop
    return db.query(User).filter_by(id=user_id).one()
```

Use `asyncio.to_thread` para delegar trabalho bloqueante ou
migre para um driver assíncrono.

## Esquecer de usar await

Uma coroutine que não recebe await retorna silenciosamente um
objeto coroutine. Ferramentas de análise estática como `mypy`
com plugins de `asyncio` detectam isso, mas é fácil passar
despercebido em code review.

## Criar tarefas demais de uma vez

`asyncio.gather` sem um semáforo vai abrir tantas conexões
quantas forem as tarefas. Adicione um `asyncio.Semaphore` para
limitar a concorrência ao acessar serviços externos.

## Estado mutável compartilhado

Código assíncrono em Python ainda é single-threaded, mas
concorrente na execução. Mutar listas ou dicts compartilhados
entre awaits é seguro, mas misturar asyncio com threading
introduz condições de corrida reais.
