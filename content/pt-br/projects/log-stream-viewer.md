---
title: "Visualizador de Fluxo de Logs"
slug: "log-stream-viewer"
description: "Uma interface de terminal para acompanhar e filtrar logs JSON estruturados em tempo real, com busca por regex e campos aninhados retratieis."
tags: ["python", "cli", "devx"]
tech_stack: ["Python", "Textual", "Rich"]
github_url: "https://github.com/oornnery/log-stream-viewer"
date: "2025-06-12"
featured: false
---

## Visao geral

`lsv` e uma TUI baseada em Textual que torna logs estruturados legiveis.
Redirecione qualquer fluxo de logs JSON para ela e obtenha filtragem
instantanea, busca e formatacao sem sair do terminal.

## Funcionalidades

- Acompanhamento em tempo real via stdin ou arquivo
- Filtragem por nivel de log, nome do servico ou valor arbitrario de campo
- Busca por regex em todo o payload JSON
- Objetos e arrays aninhados retratieis
- Copia de linha de log como JSON ou texto formatado

## Uso

```bash
tail -f app.log | lsv
kubectl logs -f pod/api-server | lsv --level error
lsv --file app.log --filter 'service=api'
```
