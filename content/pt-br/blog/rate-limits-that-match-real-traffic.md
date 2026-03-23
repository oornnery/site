---
title: "Rate Limits Que Combinam Com Tráfego Real"
slug: "rate-limits-that-match-real-traffic"
description: "Como eu escolho rate limits práticos sem punir usuários normais."
date: "2026-02-07"
author: "Fabio Souza"
tags:
  - "security"
  - "api"
  - "fastapi"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Rate limits só ajudam quando refletem o uso real.

Se os limites são frouxos demais, o abuso ainda passa. Se são
restritos demais, usuários normais se tornam dano colateral e o
time para de confiar no controle.

## Comece pela intenção da rota

Eu não escolho limites de posts genéricos de blog. Eu começo pela intenção da
rota.

Um endpoint público de leitura intensa, um formulário de
contato e uma rota de ingestão de analytics não precisam da
mesma política. Seus modelos de ameaça e padrões normais de
burst são diferentes.

A primeira divisão útil é:

- rotas públicas de leitura: limites mais amplos, principalmente
  proteção contra bursts de scraping
- rotas de mutação: limites mais apertados, especialmente
  quando disparam efeitos colaterais
- rotas sensíveis: limites agressivos e melhor visibilidade sobre tráfego
  bloqueado

Isso mantém a política ligada ao comportamento em vez de superstição.

## Tolerância a bursts importa

Pessoas não interagem com sites em intervalos perfeitamente uniformes.

Navegadores fazem retry. Páginas atualizam. Redes móveis
reconectam. Bots sondam em picos curtos. Um limite que ignora
bursts frequentemente cria falsos positivos.

O que eu geralmente quero não é "exatamente N requests a cada
minuto." Eu quero "bursts razoáveis são ok, abuso sustentado
não é."

Na prática isso significa:

- um default amplo para a maioria das rotas
- overrides específicos por rota mais apertados para endpoints
  de contato ou analytics
- logging em torno de requests bloqueadas para confirmar que a
  política condiz com a realidade

## Limites cientes de proxy não são opcionais

Se a aplicação está atrás de Traefik, Nginx ou um proxy de
plataforma, o tratamento de IP de origem precisa ser explícito.

Um rate limiter que confia no header errado é pior do que
nenhum limiter porque cria falsa confiança. Todo ambiente deve
responder:

- quais headers de proxy são confiáveis
- se headers de forwarding estão habilitados
- o que acontece em dev local e testes

É por isso que eu prefiro uma função compartilhada de extração
de IP de origem em vez de código de rota adivinhando a
identidade da request ad hoc.

## Observe o controle, não apenas a aplicação

Uma vez que um limite existe, ele se torna parte do comportamento de produção.

Eu quero saber:

- quais rotas estão atingindo o limiter
- se requests bloqueadas estão agrupadas por IP ou path
- se o volume está crescendo gradualmente ou em picos
- se tráfego legítimo está sendo penalizado

Esses sinais ajudam a decidir se o problema é abuso, mau
comportamento de cliente ou um erro de política do nosso lado.

## Um padrão de implantação que se mantém saudável

Ao adicionar rate limiting a um serviço existente, eu uso uma ordem simples:

1. adicionar um limite default seguro
2. instrumentar respostas bloqueadas
3. apertar rotas sensíveis
4. revisar logs após tráfego real
5. ajustar apenas com evidências

Essa sequência previne o modo de falha comum onde limites
parecem aleatórios e são desabilitados na primeira vez que um
usuário normal os atinge.

Bom rate limiting não é sobre parecer rigoroso. É sobre
aplicar fricção no lugar certo com dano mínimo ao uso normal.
