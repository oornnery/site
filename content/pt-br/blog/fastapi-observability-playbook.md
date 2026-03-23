---
title: "Playbook de Observabilidade com FastAPI"
slug: "fastapi-observability-playbook"
description: "Um checklist prático para traces, métricas, logs e sinais de alerta em serviços FastAPI."
date: "2026-02-18"
author: "Fabio Souza"
tags:
  - "fastapi"
  - "observability"
  - "opentelemetry"
featured: true
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Boa observabilidade começa com **nomenclatura consistente** e **ownership
claro**.

Em aplicações FastAPI, eu mantenho três camadas instrumentadas:

1. Ciclo de vida da request (latência, status code, rota)
2. Fronteiras de use-case (resultados de negócio)
3. Integrações (e-mail, webhooks, bancos de dados, APIs externas)

Uma regra simples funciona bem: se um endpoint falha em
produção, você deve conseguir responder _o que falhou, onde e
para quem_ em menos de cinco minutos.

## O que instrumentar primeiro

- Duração da request e status code por rota
- Frequência de classes de erro
- Sinais de abuso em contato/API (rate limits, violações de tamanho de body)
- Latência e taxa de falha de dependências externas

Com essa linha de base, criar dashboards e alertas se torna direto.

## A hierarquia de sinais que eu uso

Eu trato traces, métricas e logs como ferramentas diferentes, não
intercambiáveis.

Métricas me dizem se o sistema está desviando. Traces me dizem
onde o tempo está sendo gasto. Logs explicam os fatos locais em
torno de um evento. O erro é esperar que um deles carregue o
incidente inteiro sozinho.

Para um serviço FastAPI, a divisão básica é:

- métricas para latência de rota, throughput, taxas de erro e saúde de
  dependências
- traces para fluxo de request e chamadas downstream caras
- logs para falhas de validação, transições de estado e contexto operacional

Isso mantém cada tipo de sinal pequeno o suficiente para permanecer útil.

## Como é a forma de um trace saudável

Eu quero que traces contem uma história curta.

Um span de request deve identificar o template da rota e o
status code. Spans aninhados devem representar trabalho de
use-case e dependências externas, não cada chamada de função
interna. Se um trace vira um stack dump, ele perde valor
diagnóstico.

Por exemplo, uma request de submissão de contato pode parecer assim:

1. Span HTTP para `POST /contact`
2. Span de validação/use-case
3. Span de entrega de webhook
4. Span de entrega de e-mail

Isso é suficiente para identificar caminhos lentos, problemas
de retry e falhas externas.

## Logs que sobrevivem a um incidente real

Logs ainda são a forma mais rápida de responder "o que exatamente aconteceu?"

O principal que eu evito é ruído de debug não estruturado. Se
cada linha é texto livre, a revisão de incidentes fica cara. Eu
prefiro logs que preservem alguns campos estáveis:

- request id
- rota
- resultado
- resource id ou slug relevante
- tipo de exceção quando algo falhou

A mensagem pode permanecer legível para humanos. Os campos precisam permanecer
previsíveis.

## Alertas que eu realmente mantenho

A maioria dos alertas ruins começa por monitorar tudo com a mesma severidade.

Eu prefiro uma lista curta de alertas que implicam ação:

- taxa de erro de rota sustentada acima de um threshold
- latência p95 ou p99 de dependência desviando além da linha de base
- controles de abuso de contato ou analytics disparando com frequência incomum
- filas ou backlogs de entrega crescendo sem recuperação

Se um alerta não muda o comportamento, provavelmente deveria ser um dashboard.

## O que eu atraso de propósito

Nem todo serviço precisa de observabilidade profunda desde o primeiro dia.

Eu geralmente atraso:

- métricas de negócio customizadas sem uso operacional atual
- atributos detalhados de span que ninguém consulta
- logs que duplicam informação de traces
- dashboards para fluxos que raramente mudam

O primeiro objetivo é diagnóstico rápido, não um museu de gráficos.

## Uma ordem prática de implantação

Se eu estou instrumentando um serviço FastAPI existente, essa geralmente é a
ordem:

1. request ids e correlação de trace nos logs
2. métricas de latência e erro de rota
3. spans de dependência e contadores de falha
4. métricas relacionadas a abuso/segurança
5. alertas focados ligados a decisões operacionais

Essa sequência dá feedback utilizável rapidamente sem arrastar
todo o time para trabalho de observabilidade por semanas.
