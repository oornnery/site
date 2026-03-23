---
title: "Rate Limiter ASGI"
slug: "rate-limiter-middleware"
description: "Um middleware ASGI puro de rate limiting com algoritmos de janela deslizante e token bucket, com Redis para deploys multi-processo."
tags: ["python", "backend", "infra"]
tech_stack: ["Python", "Redis", "asyncio"]
github_url: "https://github.com/oornnery/rate-limiter-middleware"
date: "2025-05-08"
featured: false
---

## Visao geral

Rate limiting pronto para uso em qualquer aplicacao ASGI (FastAPI, Starlette,
etc.) sem dependencias externas alem do Redis para estado distribuido.

## Funcionalidades

- Algoritmos de janela deslizante e token bucket
- Escopos de limite por IP, por usuario e por rota
- Backend Redis com scripts Lua para operacoes atomicas
- Fallback em memoria para desenvolvimento
- Headers `X-RateLimit-*` em todas as respostas

## Uso

```python
from rate_limiter import RateLimiter

app.add_middleware(
    RateLimiter,
    default_limit="100/minute",
    redis_url=settings.redis_url,
)
```
