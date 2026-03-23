---
title: "Kit de Event Sourcing"
slug: "event-sourcing-kit"
description: "Biblioteca Python leve para event sourcing e CQRS — aggregate roots, event stores com PostgreSQL e construtores de projections."
tags: ["python", "architecture", "postgres"]
tech_stack: ["Python", "PostgreSQL", "pydantic", "asyncpg"]
github_url: "https://github.com/oornnery/event-sourcing-kit"
date: "2025-08-05"
featured: false
---

## Visao geral

Uma biblioteca minima de event sourcing que nao atrapalha seu caminho. Sem
magica, sem dependencia de framework — apenas os blocos fundamentais para
aggregates, eventos e projections.

## Funcionalidades

- Classe base `Aggregate` com o padrao `apply()` + `raise_event()`
- Event store em PostgreSQL com concorrencia otimista via verificacao de versao
- Reconstrucao sincrona de projections a partir do fluxo de eventos
- Suporte a snapshots para aggregates grandes

## Exemplo

```python
class OrderAggregate(Aggregate):
    def place(self, items: list[Item]) -> None:
        self.raise_event(OrderPlaced(order_id=self.id, items=items))

    def apply_order_placed(self, event: OrderPlaced) -> None:
        self.items = event.items
        self.status = "placed"
```
