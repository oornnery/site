---
title: "Event Sourcing Kit"
slug: "event-sourcing-kit"
description: "Lightweight Python library for event sourcing and CQRS — aggregate roots, event stores backed by PostgreSQL, and projection builders."
tags: ["python", "architecture", "postgres"]
tech_stack: ["Python", "PostgreSQL", "pydantic", "asyncpg"]
github_url: "https://github.com/oornnery/event-sourcing-kit"
date: 2025-08-05
featured: false
---

## Overview

A minimal event sourcing library that stays out of your way. No magic, no
framework lock-in — just the building blocks for aggregates, events, and
projections.

## Features

- `Aggregate` base class with `apply()` + `raise_event()` pattern
- PostgreSQL event store with optimistic concurrency via version checks
- Synchronous projection rebuilds from event stream
- Snapshot support for large aggregates

## Example

```python
class OrderAggregate(Aggregate):
    def place(self, items: list[Item]) -> None:
        self.raise_event(OrderPlaced(order_id=self.id, items=items))

    def apply_order_placed(self, event: OrderPlaced) -> None:
        self.items = event.items
        self.status = "placed"
```
