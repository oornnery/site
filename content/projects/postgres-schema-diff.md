---
title: "pg-schema-diff"
slug: "postgres-schema-diff"
description: "A CLI tool that compares two PostgreSQL schemas and generates safe migration SQL, highlighting destructive changes before you run them."
tags: ["python", "postgres", "tooling"]
tech_stack: ["Python", "psycopg", "Typer", "Rich"]
github_url: "https://github.com/oornnery/pg-schema-diff"
date: 2025-10-20
featured: false
---

## Overview

Stop running `pg_dump` diffs by hand. `pg-schema-diff` connects to two
databases (or reads SQL dump files) and produces a human-readable diff plus
ready-to-run migration SQL.

## Features

- Side-by-side table, column, index, and constraint diff
- Flags destructive changes (DROP, ALTER TYPE) in red before execution
- Outputs pure SQL — no proprietary migration format
- Works with dump files for offline comparison

## Usage

```bash
pgsd compare --source $SOURCE_DSN --target $TARGET_DSN
pgsd compare --source schema_v1.sql --target schema_v2.sql --output migration.sql
```
