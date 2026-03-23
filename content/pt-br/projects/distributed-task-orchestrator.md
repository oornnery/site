---
title: "Orquestrador de Tarefas Distribuidas"
slug: "distributed-task-orchestrator"
description: >-
  Um orquestrador baseado em filas para jobs de longa duracao com retentativas,
  idempotencia e dashboards operacionais.
thumbnail: "/static/images/projects/distributed-task-orchestrator.svg"
tags: ["python", "distributed-systems", "queues"]
tech_stack: ["Python", "FastAPI", "Redis", "PostgreSQL"]
github_url: "https://github.com/oornnery/distributed-task-orchestrator"
live_url: ""
date: "2025-02-14"
featured: false
---

## Visao geral

Este projeto coordena cargas de trabalho assincronas entre workers, preservando
garantias de ordenacao e tolerancia a falhas.

## Capacidades principais

- Deduplicacao de jobs com chaves de idempotencia
- Backoff exponencial e politicas de dead-letter
- Metricas de execucao em tempo real e visibilidade sobre a saude das filas
- Etapas de workflow declarativas com fronteiras claras de falha

## Resultado

O orquestrador melhorou a confiabilidade de tarefas em segundo plano e reduziu
incidentes de recuperacao manual em producao.

## Modelo de execucao

O sistema trata um job em segundo plano como uma maquina de estados em vez de
uma simples chamada de funcao do tipo dispara e esquece.
Isso tornou retentativas, timeouts e acompanhamento de progresso explicitos.

### Recepcao

Jobs recebidos sao normalizados em um envelope estavel com metadados de tenant,
workflow, chave de idempotencia e prioridade.
Esse envelope se torna o contrato compartilhado entre produtores da API e
consumidores workers.

### Agendamento

O agendamento prioriza equidade previsivel em vez de throughput bruto.
As filas sao particionadas por tipo de carga de trabalho para que uma rajada de
jobs de baixo valor nao prejudique trabalhos operacionalmente criticos.

### Execucao

Os workers processam etapas declarativas e reportam transicoes apos cada
fronteira. Isso cria uma linha do tempo que operadores podem inspecionar sem
ler o codigo da aplicacao.

## Tratamento de falhas

Retentativas so sao uteis quando sao seletivas.

### Politica de retentativa

Falhas transitorias de dependencias usam backoff exponencial com tentativas
limitadas. Erros de validacao ou regras de negocio vao direto para estados
terminais, pois repeti-los adiciona carga sem melhorar os resultados.

### Fluxo de dead-letter

Filas de dead-letter sao tratadas como uma superficie de depuracao, nao como um
deposito de lixo. Cada job enviado para dead-letter mantem metadados de falha,
contagem de retentativas e a ultima etapa conhecida, para que a investigacao
comece com contexto.

## Visibilidade operacional

O projeto inclui dashboards para os sinais que os operadores realmente precisam
durante incidentes.

- idade do item mais antigo na fila
- throughput por workflow
- taxa de falha por etapa
- rotatividade de retentativas por dependencia

Essas visualizacoes facilitaram a identificacao de se um problema era de
capacidade, comportamento de mensagem envenenada ou uma queda de servico
externo.

## Tradeoffs de consistencia

O orquestrador nao tenta simular transacoes distribuidas perfeitas.
Em vez disso, ele se apoia em idempotencia e transicoes de estado explicitas.

### Por que a idempotencia importa

Workers podem reiniciar, mensagens podem ser re-entregues e operadores podem
reprocessar eventos durante a recuperacao. Handlers idempotentes tornam essas
realidades sobreviviveis.

### Onde a ordenacao estrita se aplica

A ordenacao e aplicada apenas dentro de segmentos de workflow que realmente a
exigem. Tentar preservar a ordenacao global em todas as filas reduziria o
paralelismo sem melhorar os resultados de negocio.

## O que eu ajustaria em seguida

O proximo passo seria concorrencia adaptativa baseada na saude das filas e na
saturacao de dependencias. Isso permitiria ao orquestrador processar mais
rapido em periodos tranquilos enquanto recua antes que os servicos externos
comecem a apresentar problemas.
