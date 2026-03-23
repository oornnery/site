---
title: "Pipeline Seguro de Contato"
slug: "secure-contact-pipeline"
description: >-
  Um fluxo de contato com protecao CSRF, validacao rigorosa, limites anti-spam e
  notificacoes desacopladas.
thumbnail: "/static/images/projects/secure-contact-pipeline.svg"
tags: ["security", "fastapi", "webhooks"]
tech_stack: ["FastAPI", "Pydantic", "SlowAPI", "HTTPX"]
github_url: "https://github.com/oornnery/secure-contact-pipeline"
live_url: "https://example.dev/secure-contact-pipeline"
date: "2025-08-03"
featured: true
---

## Visao geral

Este projeto demonstra um fluxo seguro de envio de formulario com
responsabilidades claras no backend.
O roteador e intencionalmente enxuto, enquanto os servicos de caso de uso
realizam a validacao e a orquestracao.

## Controles de seguranca

- Token CSRF assinado com HMAC e com expiracao
- Validacao em nivel de campo usando modelos Pydantic
- Rate limiting por IP do cliente
- Middleware rigoroso de headers de seguranca

### Validacao de requisicao

Cada envio e normalizado antes das regras de negocio serem executadas.
Isso inclui verificacoes de content-type, aparamento de campos, guardas de
tamanho do corpo e um schema estavel para o payload que transita pelo pipeline.

### Resistencia a abuso

O endpoint e tratado como uma borda publica, nao como um formulario interno
confiavel. Rate limits, resistencia a replay e logging com identificacao de
origem existem para reduzir o custo de trafego ruidoso antes mesmo de tentativas
de notificacao.

## Arquitetura

A entrega de notificacoes e isolada em canais.
O mesmo envio pode ser entregue via webhook e email sem acoplar a camada HTTP.

## Ciclo de vida da requisicao

O caminho feliz e intencionalmente simples:

1. receber uma requisicao HTTP validada
2. verificar CSRF e controles de abuso
3. mapear a entrada bruta em um comando da aplicacao
4. persistir ou encaminhar por um canal de notificacao
5. emitir uma resposta de sucesso previsivel

Manter essas etapas explicitas facilitou testar caminhos de falha sem misturar
preocupacoes de transporte na camada de caso de uso.

## Estrategia de notificacao

O projeto suporta multiplos destinos de entrega sem transformar o roteador em
um script de orquestracao.

### Entrega via webhook

A entrega via webhook e tratada por um wrapper de cliente dedicado com timeout e
fronteiras de falha. Isso mantem retentativas e mapeamento de respostas fora do
handler de requisicao.

### Fallback por email

O email e modelado como um canal de saida separado.
Se um canal estiver desabilitado ou degradado, a configuracao pode manter o
restante do fluxo ativo sem alteracoes nos templates.

## Notas operacionais

Este projeto so se torna confiavel quando os padroes operacionais sao visiveis.

- identificadores de requisicao sao incluidos nos logs
- falhas de validacao sao agrupadas por tipo, nao por strings de texto livre
- latencia de notificacao e medida separadamente da latencia HTTP
- clientes ruidosos podem ser identificados sem registrar corpos de mensagens sensiveis

## O que eu estenderia em seguida

A proxima camada seria uma fila interna de moderacao para envios de alto risco.
Isso permitiria que mensagens suspeitas fossem aceitas na borda enquanto sao
revisadas ou limitadas antes da entrega downstream.
