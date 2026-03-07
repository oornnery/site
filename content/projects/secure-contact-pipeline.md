---
title: "Secure Contact Pipeline"
slug: "secure-contact-pipeline"
description: >-
  A contact flow with CSRF protection, strict validation, anti-spam limits, and
  decoupled notifications.
thumbnail: "/static/images/projects/secure-contact-pipeline.svg"
tags: ["security", "fastapi", "webhooks"]
tech_stack: ["FastAPI", "Pydantic", "SlowAPI", "HTTPX"]
github_url: "https://github.com/oornnery/secure-contact-pipeline"
live_url: "https://example.dev/secure-contact-pipeline"
date: 2025-08-03
featured: true
---

## Overview

This project demonstrates a secure form submission workflow with clear backend
responsibilities.
The router is intentionally thin, while use-case services perform validation
and orchestration.

## Security controls

- HMAC-signed CSRF token with expiration
- Field-level validation using Pydantic models
- Rate limiting per client IP
- Strict security headers middleware

### Request validation

Every submission is normalized before business rules run.
That includes content-type checks, field trimming, body-size guards, and a
stable schema for the payload that moves through the pipeline.

### Abuse resistance

The endpoint is treated as a public edge, not a trusted internal form.
Rate limits, replay resistance, and source-aware logging exist to reduce the
cost of noisy traffic before notifications are even attempted.

## Architecture

Notification delivery is isolated in channels.
The same submission can be delivered to webhook and email without coupling the
HTTP layer.

## Request lifecycle

The happy path is intentionally boring:

1. receive a validated HTTP request
2. verify CSRF and abuse controls
3. map raw input into an application command
4. persist or forward through a notification channel
5. emit a predictable success response

Keeping those steps explicit made it easier to test unhappy paths without
mixing transport concerns into the use-case layer.

## Notification strategy

The project supports multiple delivery targets without turning the router into
an orchestration script.

### Webhook delivery

Webhook delivery is handled through a dedicated client wrapper with timeout and
failure boundaries.
That keeps retries and response mapping out of the request handler.

### Email fallback

Email is modeled as a separate outbound channel.
If one channel is disabled or degraded, the configuration can keep the rest of
the flow alive without template changes.

## Operational notes

This project only becomes reliable when the operational defaults are visible.

- request identifiers are included in logs
- validation failures are grouped by type, not by free-form strings
- notification latency is measured separately from HTTP latency
- noisy clients can be identified without logging sensitive message bodies

## What I would extend next

The next layer would be an internal moderation queue for high-risk submissions.
That would allow suspicious messages to be accepted at the edge while being
reviewed or rate-shaped before downstream delivery.
