---
title: "Hub de Observabilidade para APIs"
slug: "api-observability-hub"
description: >-
  Um template de servico FastAPI com logs estruturados, rastreamento de
  requisicoes e padroes de confiabilidade desde o inicio.
thumbnail: "/static/images/projects/api-observability-hub.svg"
tags: ["python", "fastapi", "observability"]
tech_stack: ["Python", "FastAPI", "Pydantic", "Uvicorn"]
github_url: "https://github.com/oornnery/api-observability-hub"
live_url: "https://example.dev/api-observability-hub"
date: "2025-11-10"
featured: true
---

## Visao geral

Este projeto surgiu como uma base reutilizavel de backend para servicos em
producao. Ele oferece rastreamento do ciclo de vida das requisicoes, middleware
de seguranca e limites claros de dependencias.

## Destaques

- Propagacao de ID de requisicao em todos os logs
- Respostas de erro unificadas
- Inicializacao orientada por configuracao com validacao de ambiente
- Casos de uso por rota com injecao de dependencias

## Por que isso importa

A maioria dos projetos de API falha em operacoes, nao no desenvolvimento local.
Este template reduz esse risco ao tornar observabilidade e seguranca
preocupacoes de primeira classe.

## Modelo de telemetria

O objetivo nao e registrar tudo.
O objetivo e responder o que aconteceu, onde falhou e qual foi o raio de
impacto em poucos minutos.

### Logs

Os logs sao estruturados em torno de campos estaveis como ID de requisicao,
template de rota, codigo de status e classe de falha.
Isso mantem a busca e os alertas uteis apos o primeiro mes de crescimento.

### Traces

O rastreamento foca nas fronteiras que realmente importam:

- spans de requisicoes recebidas
- spans de execucao de casos de uso
- spans de dependencias externas
- caminhos de excecao com atributos de erro estaveis

### Metricas

As metricas sao intencionalmente enxutas.
O template acompanha latencia por rota, taxa de erros e alguns sinais de
dependencias em vez de criar um dashboard para cada detalhe de implementacao.

## Padroes de confiabilidade

O template vem com configuracoes que direcionam os times para um comportamento
pronto para producao em vez de atalhos voltados para depuracao.

### Validacao na inicializacao

A configuracao e validada na inicializacao para que ambientes mal configurados
falhem rapidamente. Isso evita rodar servicos parcialmente configurados que so
falham sob trafego real.

### Formatacao de erros

Os erros sao traduzidos em um contrato de resposta estavel.
Operadores recebem detalhes de diagnostico nos logs e traces, enquanto os
clientes recebem uma superficie de resposta HTTP previsivel.

## Fronteiras de servico

A arquitetura mantem os roteadores enxutos e trata os modulos de servico como o
lugar onde as decisoes acontecem.

### Camada de roteamento

Os roteadores recebem a entrada, chamam as dependencias e retornam respostas
HTTP. Eles nao sao responsaveis por retentativas, regras de negocio ou
politicas de mapeamento de respostas.

### Camada de casos de uso

Os casos de uso sao responsaveis pela orquestracao.
Isso inclui chamar repositorios, aplicar regras de dominio e decidir quais
eventos ou notificacoes devem ser emitidos.

## Licoes de implantacao

O maior efeito deste projeto nao foram dashboards mais bonitos.
Foi a reducao do tempo gasto discutindo o que instrumentar, porque a base ja
existia.

Quando um novo servico comeca com IDs de requisicao, traces e middleware
adequado, o time gasta menos esforco reconstruindo habitos de plataforma do
zero.
