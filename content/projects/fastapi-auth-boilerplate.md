---
title: "FastAPI Auth Boilerplate"
slug: "fastapi-auth-boilerplate"
description: "Production-ready FastAPI starter with JWT authentication, refresh tokens, role-based access control, and full test coverage."
tags: ["python", "fastapi", "auth"]
tech_stack: ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "pytest"]
github_url: "https://github.com/oornnery/fastapi-auth-boilerplate"
date: 2025-11-15
featured: false
---

## Overview

A battle-tested starting point for FastAPI projects that require authentication
from day one.

## Features

- JWT access + refresh token flow
- Role-based access control (RBAC) with permission guards
- Password hashing with bcrypt
- Async SQLAlchemy sessions with Alembic migrations
- 100% test coverage on auth routes

## Usage

```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```
