---
title: "Notas sobre Clean Architecture em Projetos Reais"
slug: "clean-architecture-notes-from-real-projects"
description: "Padrões que mantêm projetos web sustentáveis após o primeiro release."
date: "2026-01-29"
author: "Fabio Souza"
tags:
  - "architecture"
  - "python"
  - "backend"
featured: true
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

A regra de arquitetura mais útil no dia a dia é simples:

> Routers devem traduzir HTTP, services devem conter a lógica de negócio.

Quando os arquivos de rota ficam enxutos, os testes ficam mais
baratos e as refatorações mais seguras.

## Heurísticas que eu uso

- Se a lógica depende de termos de negócio, ela pertence a um service/use-case.
- Se a lógica depende de headers ou status codes, ela pertence à camada de
  router.
- Se muitas páginas usam o mesmo contrato de dados, defina um
  modelo de contexto tipado uma única vez.

Isso mantém os templates previsíveis e evita acoplamento oculto entre pastas.

## Onde as fronteiras se pagam primeiro

O primeiro lugar onde a arquitetura se paga não é em escala. É na mudança.

Quando um fluxo de contato começa simples, é tentador manter
validação, envio de e-mail, analytics e mapeamento de resposta
em uma única função de rota. Isso funciona por uma semana.
Então o segundo canal de notificação aparece, o rate limiting
muda e alguém pede melhor telemetria sobre falhas.

Se a rota é responsável apenas por questões HTTP, o formato dessa mudança fica
claro:

- router valida detalhes de transporte
- service decide o caminho do use-case
- infrastructure lida com efeitos colaterais
- rendering mapeia a saída para um contrato estável de página

Essa separação não remove complexidade. Ela coloca a
complexidade onde pode ser testada com menos atrito.

## Os erros que eu tento evitar

A maioria da erosão arquitetural vem de três erros repetidos.

Primeiro, regras de negócio ficam atreladas a objetos do
framework. Um service que precisa de `Request`, `Response` ou
headers brutos geralmente se torna mais difícil de reutilizar e
mais difícil de entender.

Segundo, templates se tornam contratos implícitos. Se a página
silenciosamente espera dez variáveis com nomes vagos, pequenas
mudanças de UI se tornam arriscadas porque nada indica o que a
página realmente precisa.

Terceiro, módulos "utilitários" viram lixeiras. Helpers
compartilhados são úteis, mas apenas quando permanecem
genéricos. No momento em que codificam um fluxo de trabalho,
não são mais helpers; são services ocultos.

## Contratos de template importam mais do que parecem

Aplicações renderizadas no servidor se mantêm sustentáveis
quando os dados de renderização são tipados e previsíveis.

Eu prefiro um modelo de contexto de página que responda a uma
pergunta simples: o que essa página precisa, e nada mais? Isso
parece óbvio, mas muda a forma como times trabalham.

Em vez de passar dicionários amplos para templates, contextos
de página tipados tornam cada página explícita:

- título, metadados e estado de navegação ficam visíveis em um só lugar
- campos opcionais são intencionais em vez de acidentais
- valores ausentes falham cedo durante o desenvolvimento

Para sites pessoais, documentação e apps administrativos, essa
abordagem remove uma quantidade surpreendente de confusão na
UI.

## Fronteiras de service e telemetria

Outro benefício prático é a observabilidade.

Se uma fronteira de service já existe, a instrumentação fica
mais fácil. Você pode registrar resultados de use-case,
associar nomes de span a operações significativas e gravar
métricas no nível em que as pessoas realmente discutem
incidentes.

Isso é melhor do que ter apenas "POST /contact retornou 500".

Sinais úteis geralmente se parecem com:

- submissão de contato aceita
- entrega de notificação de contato falhou
- parsing de markdown ignorou documento inválido
- renderização de página concluída com fallback de conteúdo vazio

Esses nomes são compreensíveis durante incidentes, code review e trabalho com
dashboards.

## Um checklist leve de revisão

Quando eu reviso uma nova funcionalidade, geralmente pergunto:

1. O router ainda está enxuto?
2. O service é dono da decisão de negócio?
3. Os efeitos colaterais estão isolados?
4. O contrato da página é tipado e explícito?
5. A telemetria consegue descrever o resultado em linguagem de domínio?

Se essas respostas estão claras, o codebase geralmente
permanece flexível sem se transformar em cerimônia.

Clean Architecture só se torna um problema quando é praticada
como teatro. Usada com cuidado, ela simplesmente reduz o custo
da próxima mudança.
