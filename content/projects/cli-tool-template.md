---
title: "CLI Tool Template"
slug: "cli-tool-template"
description: "A production-ready Python CLI skeleton with Typer, rich output, structured logging, and testable command handlers."
tags: ["python", "cli", "tooling"]
tech_stack: ["Python", "Typer", "Rich", "pytest"]
github_url: "https://github.com/oornnery/cli-tool-template"
date: 2025-12-01
featured: false
---

## Overview

A reusable starting point for Python command-line tools that need more than
a simple script.

## Features

- Typer-based command structure with subcommands
- Rich-formatted output with progress bars and tables
- Structured JSON logging for machine-readable output
- Isolated command handlers for easy unit testing
- Configuration via environment variables and `.env` files

## Usage

```bash
myapp --help
myapp init --name my-project
myapp run --config config.yaml
```
