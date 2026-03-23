---
title: "Type Hints em Python Além do Básico"
slug: "python-type-hints-beyond-basics"
description: "TypeVar, Protocol, TypedDict e Annotated para times que querem garantias estáticas reais."
date: "2025-11-05"
author: "Fabio Souza"
tags:
  - "python"
  - "types"
  - "architecture"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Type hints básicos (`str`, `int`, `list[str]`) resolvem a
maior parte. Além disso, algumas funcionalidades avançadas
fecham as lacunas restantes.

## Protocol para tipagem estrutural

`Protocol` permite definir interfaces sem herança. Qualquer
classe que implemente os métodos exigidos satisfaz o protocol.

```python
from typing import Protocol

class Notifier(Protocol):
    def send(self, message: str) -> None: ...
```

Isso é mais flexível que ABC e funciona com classes de
terceiros que você não pode modificar.

## TypeVar para funções genéricas

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

## TypedDict para dados em formato de dicionário

Quando você precisa anotar um dict sem convertê-lo para um
dataclass ou modelo Pydantic, `TypedDict` oferece verificação
em nível de campo.

## Annotated para metadados

`Annotated[int, Gt(0)]` permite que bibliotecas como Pydantic
e FastAPI associem metadados de validação a anotações de tipo
sem alterar o tipo subjacente.
