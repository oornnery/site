---
title: "Hábitos de Docker Compose Para Dev Próximo de Produção"
slug: "docker-compose-habits-for-production-like-dev"
description: "Pequenos hábitos que tornam ambientes locais com containers mais próximos de deploys reais."
date: "2025-11-20"
author: "Fabio Souza"
tags:
  - "docker"
  - "infra"
  - "devx"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Ambientes Docker locais se tornam úteis quando expõem restrições reais cedo.

Eu não preciso de paridade com produção para cada side project,
mas quero que o dev local revele drift de configuração,
suposições de inicialização e dependências ausentes.

## Separe dev e produção intencionalmente

Tentar fazer um único arquivo Compose lidar com todos os
ambientes geralmente cria condicionais ocultas e defaults pouco
claros.

Eu prefiro:

- um setup orientado a dev otimizado para iteração rápida
- um setup orientado a produção otimizado para previsibilidade
- conceitos compartilhados, mas sem simetria forçada em nível de arquivo

Isso mantém a intenção de cada ambiente fácil de entender.

## Trate o comportamento do reverse proxy como parte da aplicação

Para aplicações web, ambientes locais são mais realistas quando o proxy está
presente.

Isso ajuda a revelar:

- problemas de trusted host
- suposições sobre headers de forwarding
- tratamento de path e scheme
- comportamento de headers de segurança e tamanho de body

Se a aplicação só roda diretamente no localhost durante o
desenvolvimento, problemas de deploy aparecem mais tarde do que
deveriam.

## Registre suposições de inicialização em log

Containers falham de formas frustrantes quando as expectativas
de inicialização são implícitas.

Eu quero que os logs de inicialização deixem óbvio:

- qual arquivo de configuração está ativo
- qual porta está vinculada
- se os assets estáticos estão montados
- se os exportadores de telemetria estão habilitados
- se os serviços dependentes estão acessíveis

Esses fatos eliminam muito tempo desperdiçado quando uma stack
"inicia" mas não se comporta de verdade.

## Mantenha o ciclo de dev pequeno

Próximo de produção não significa lento.

Eu ainda quero:

- bind mounts onde a iteração importa
- health checks claros
- grafo mínimo de serviços para trabalho local
- rebuilds fáceis quando dependências mudam

Uma boa stack local deve parecer realista o suficiente para
detectar problemas, mas pequena o suficiente para que as
pessoas realmente a usem todos os dias.

## Revise os limites dos containers ocasionalmente

A cada poucas semanas, vale conferir se a stack local ainda
reflete os limites importantes de produção.

Perguntas que eu gosto de fazer:

1. A aplicação ainda depende de algo disponível apenas fora dos containers?
2. As suposições de proxy e segurança ainda são exercitadas localmente?
3. As variáveis de ambiente e arquivos montados ainda estão explícitos?
4. A stack é pequena o suficiente para que os desenvolvedores a mantenham
   rodando?

Esse equilíbrio importa mais do que perseguir paridade perfeita.
