---
title: "ASGI Rate Limiter"
slug: "rate-limiter-middleware"
description: "A pure ASGI rate limiting middleware with sliding window and token bucket algorithms, Redis-backed for multi-process deployments."
tags: ["python", "backend", "infra"]
tech_stack: ["Python", "Redis", "asyncio"]
github_url: "https://github.com/oornnery/rate-limiter-middleware"
date: 2025-05-08
featured: false
---

## Overview

Drop-in rate limiting for any ASGI app (FastAPI, Starlette, etc.) without
external dependencies beyond Redis for distributed state.

## Features

- Sliding window and token bucket algorithms
- Per-IP, per-user, and per-route limit scopes
- Redis backend with Lua scripts for atomic operations
- In-memory fallback for development
- `X-RateLimit-*` headers on all responses

## Usage

```python
from rate_limiter import RateLimiter

app.add_middleware(
    RateLimiter,
    default_limit="100/minute",
    redis_url=settings.redis_url,
)
```
