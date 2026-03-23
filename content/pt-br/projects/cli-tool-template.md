---
title: "Template de Ferramenta CLI"
slug: "cli-tool-template"
description: "Um esqueleto de CLI Python pronto para producao com Typer, saida rica, logging estruturado e handlers de comandos testaveis."
tags: ["python", "cli", "tooling"]
tech_stack: ["Python", "Typer", "Rich", "pytest"]
github_url: "https://github.com/oornnery/cli-tool-template"
date: "2025-12-01"
featured: false
---

## Visao geral

Um ponto de partida reutilizavel para ferramentas de linha de comando em Python
que precisam de mais do que um simples script.

## Funcionalidades

- Estrutura de comandos baseada em Typer com subcomandos
- Saida formatada com Rich, incluindo barras de progresso e tabelas
- Logging estruturado em JSON para saida legivel por maquinas
- Handlers de comandos isolados para facilitar testes unitarios
- Configuracao via variaveis de ambiente e arquivos `.env`

## Uso

```bash
myapp --help
myapp init --name my-project
myapp run --config config.yaml
```
