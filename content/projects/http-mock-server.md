---
title: "HTTP Mock Server"
slug: "http-mock-server"
description: "A zero-dependency local HTTP mock server for integration tests. Define responses in YAML and replay them deterministically."
tags: ["python", "testing", "tooling"]
tech_stack: ["Python", "asyncio", "PyYAML"]
github_url: "https://github.com/oornnery/http-mock-server"
date: 2025-09-10
featured: false
---

## Overview

Tired of spinning up real services to run integration tests? Define your
expected HTTP interactions in a YAML fixture file and let the mock server
handle the rest.

## Features

- YAML-defined request/response fixtures with path and method matching
- Latency simulation per route
- Request recording mode — proxy real traffic and capture fixtures automatically
- Assertion mode — fail tests if unexpected requests arrive

## Usage

```yaml
# fixtures/github.yaml
- method: GET
  path: /repos/owner/repo
  status: 200
  body: { "name": "repo", "stargazers_count": 42 }
```

```bash
http-mock --fixtures fixtures/ --port 8888
```
