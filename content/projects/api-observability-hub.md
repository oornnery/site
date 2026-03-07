---
title: "API Observability Hub"
slug: "api-observability-hub"
description: >-
  A FastAPI service template with structured logs, request tracing, and
  reliability-first defaults.
thumbnail: "/static/images/projects/api-observability-hub.svg"
tags: ["python", "fastapi", "observability"]
tech_stack: ["Python", "FastAPI", "Pydantic", "Uvicorn"]
github_url: "https://github.com/oornnery/api-observability-hub"
live_url: "https://example.dev/api-observability-hub"
date: 2025-11-10
featured: true
---

## Overview

This project started as a reusable backend baseline for production services.
It provides request lifecycle tracing, security middleware, and clear
dependency boundaries.

## Highlights

- Request ID propagation across all logs
- Unified error responses
- Config-first initialization with environment validation
- Route-level use cases with dependency injection

## Why it matters

Most API projects fail in operations, not in local development.
This template reduces that risk by making observability and security
first-class concerns.

## Telemetry model

The goal is not to record everything.
The goal is to answer what happened, where it failed, and how wide the blast
radius was within a few minutes.

### Logs

Logs are structured around stable fields such as request ID, route template,
status code, and failure class.
That keeps search and alerting useful after the first month of growth.

### Traces

Tracing focuses on the boundaries that matter:

- inbound request spans
- use-case execution spans
- outbound dependency spans
- exceptional paths with stable error attributes

### Metrics

Metrics stay intentionally small.
The template tracks route latency, error ratio, and a few dependency signals
instead of creating a dashboard for every implementation detail.

## Reliability defaults

The template ships with settings that push teams toward production-ready
behavior instead of debug-friendly shortcuts.

### Startup validation

Configuration is validated on startup so broken environments fail fast.
That avoids running half-configured services that only fail under real traffic.

### Error shaping

Errors are translated into a stable response contract.
Operators get diagnostic detail in logs and traces, while clients get a
predictable HTTP response surface.

## Service boundaries

The architecture keeps routers thin and treats service modules as the place
where decisions happen.

### Router layer

Routers receive input, call dependencies, and return HTTP responses.
They do not own retries, business rules, or response mapping policies.

### Use-case layer

Use cases own orchestration.
That includes calling repositories, applying domain rules, and deciding which
events or notifications should be emitted.

## Rollout lessons

The strongest effect of this project was not prettier dashboards.
It was reducing the time spent debating what to instrument because the baseline
already existed.

When a new service starts with request IDs, traces, and sane middleware, the
team spends less effort rebuilding platform habits from scratch.
