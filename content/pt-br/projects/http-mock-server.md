---
title: "Servidor HTTP Mock"
slug: "http-mock-server"
description: "Um servidor HTTP mock local sem dependencias para testes de integracao. Defina respostas em YAML e reproduza-as de forma deterministica."
tags: ["python", "testing", "tooling"]
tech_stack: ["Python", "asyncio", "PyYAML"]
github_url: "https://github.com/oornnery/http-mock-server"
date: "2025-09-10"
featured: false
---

## Visao geral

Cansado de subir servicos reais para rodar testes de integracao? Defina as
interacoes HTTP esperadas em um arquivo de fixtures YAML e deixe o servidor
mock cuidar do resto.

## Funcionalidades

- Fixtures de requisicao/resposta definidas em YAML com
  correspondencia por caminho e metodo
- Simulacao de latencia por rota
- Modo de gravacao de requisicoes — faz proxy do trafego real
  e captura fixtures automaticamente
- Modo de asseracao — falha nos testes se requisicoes inesperadas chegarem

## Uso

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
