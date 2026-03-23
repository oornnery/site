---
title: "Boilerplate de Autenticacao FastAPI"
slug: "fastapi-auth-boilerplate"
description: "Starter FastAPI pronto para producao com autenticacao JWT, refresh tokens, controle de acesso baseado em papeis e cobertura completa de testes."
tags: ["python", "fastapi", "auth"]
tech_stack: ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "pytest"]
github_url: "https://github.com/oornnery/fastapi-auth-boilerplate"
date: "2025-11-15"
featured: false
---

## Visao geral

Um ponto de partida testado em batalha para projetos FastAPI que precisam de
autenticacao desde o primeiro dia.

## Funcionalidades

- Fluxo de access token + refresh token com JWT
- Controle de acesso baseado em papeis (RBAC) com guards de permissao
- Hashing de senhas com bcrypt
- Sessoes SQLAlchemy assincronas com migracoes Alembic
- 100% de cobertura de testes nas rotas de autenticacao

## Uso

```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```
