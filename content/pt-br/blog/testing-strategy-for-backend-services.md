---
title: "Estratégia de Testes Para Serviços Backend"
slug: "testing-strategy-for-backend-services"
description: "Uma abordagem prática em camadas para testes backend: o que testar unitariamente, o que integrar e o que pular."
date: "2025-07-30"
author: "Fabio Souza"
tags:
  - "testing"
  - "python"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Boa cobertura de testes não é sobre atingir uma meta de
porcentagem. É sobre ter confiança de que os caminhos
importantes funcionam e que regressões são detectadas rápido.

## Testes unitários pertencem à lógica de negócio

Services, validadores e regras de domínio são o alvo certo
para testes unitários. Eles rodam rápido, são fáceis de isolar
e capturam os bugs de lógica que mais importam.

```python
def test_normalize_tag_strips_whitespace():
    assert normalize_tag("  python  ") == "python"
```

## Testes de integração pertencem à fronteira HTTP

Teste rotas com um banco de dados real (de teste) ou
equivalentes em memória. Foque em status codes corretos,
formatos de resposta e efeitos colaterais.

Use `httpx.AsyncClient` com o transporte ASGI do FastAPI para
testes de integração HTTP limpos e rápidos que não precisam de
um servidor rodando.

## Pule testes para código de terceiros

Não escreva testes que apenas verificam se uma biblioteca
funciona corretamente. Confie na biblioteca, teste o seu uso
dela.

## Testes baseados em propriedades para edge cases

Bibliotecas como `hypothesis` geram inputs que revelam edge
cases que você não pensaria em escrever manualmente. Útil para
parsers, validadores e funções com muita matemática.

## Mantenha a pirâmide de testes saudável

Muitos testes unitários, menos testes de integração, o mínimo
de testes end-to-end. Testes end-to-end são caros de escrever e
instáveis de executar.
