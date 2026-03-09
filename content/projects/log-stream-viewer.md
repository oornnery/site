---
title: "Log Stream Viewer"
slug: "log-stream-viewer"
description: "A terminal UI for tailing and filtering structured JSON logs in real time, with regex search and collapsible nested fields."
tags: ["python", "cli", "devx"]
tech_stack: ["Python", "Textual", "Rich"]
github_url: "https://github.com/oornnery/log-stream-viewer"
date: 2025-06-12
featured: false
---

## Overview

`lsv` is a Textual-based TUI that makes structured logs readable. Pipe any
JSON log stream into it and get instant filtering, search, and pretty-printing
without leaving the terminal.

## Features

- Real-time tail of stdin or a file
- Filter by log level, service name, or arbitrary field value
- Regex search across the full JSON payload
- Collapsible nested objects and arrays
- Copy log line as JSON or formatted text

## Usage

```bash
tail -f app.log | lsv
kubectl logs -f pod/api-server | lsv --level error
lsv --file app.log --filter 'service=api'
```
