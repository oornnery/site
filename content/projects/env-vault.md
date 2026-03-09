---
title: "env-vault"
slug: "env-vault"
description: "A team-friendly secrets manager that encrypts .env files with age encryption and stores them in your git repo safely."
tags: ["python", "tooling", "infra"]
tech_stack: ["Python", "age", "Typer"]
github_url: "https://github.com/oornnery/env-vault"
date: 2025-07-18
featured: false
---

## Overview

Share secrets safely with your team without a secret manager subscription.
Encrypt your `.env` with `age` public keys, commit the ciphertext, and let
teammates decrypt with their own private key.

## Features

- Age encryption (modern, audited, no OpenSSL footguns)
- Per-environment vaults: `.env.production.age`, `.env.staging.age`
- Key rotation wizard that re-encrypts all vaults for a new team member
- CI integration: decrypt at build time using a machine key

## Usage

```bash
ev encrypt .env --recipients team-keys.txt -o .env.production.age
ev decrypt .env.production.age -o .env
ev rotate --remove alice@example.com --add bob@example.com
```
