---
title: "env-vault"
slug: "env-vault"
description: "Um gerenciador de segredos amigavel para equipes que criptografa arquivos .env com age e os armazena com seguranca no seu repositorio git."
tags: ["python", "tooling", "infra"]
tech_stack: ["Python", "age", "Typer"]
github_url: "https://github.com/oornnery/env-vault"
date: "2025-07-18"
featured: false
---

## Visao geral

Compartilhe segredos com seguranca com sua equipe sem precisar de uma
assinatura de gerenciador de segredos. Criptografe seu `.env` com chaves
publicas `age`, faca commit do texto cifrado e permita que colegas
descriptografem com sua propria chave privada.

## Funcionalidades

- Criptografia age (moderna, auditada, sem as armadilhas do OpenSSL)
- Cofres por ambiente: `.env.production.age`, `.env.staging.age`
- Assistente de rotacao de chaves que re-criptografa todos os
  cofres para um novo membro da equipe
- Integracao com CI: descriptografe no momento do build usando uma chave de
  maquina

## Uso

```bash
ev encrypt .env --recipients team-keys.txt -o .env.production.age
ev decrypt .env.production.age -o .env
ev rotate --remove alice@example.com --add bob@example.com
```
