---
title: "Distributed Task Orchestrator"
slug: "distributed-task-orchestrator"
description: >-
  A queue-driven orchestrator for long-running jobs with retries, idempotency,
  and operational dashboards.
thumbnail: "/static/images/projects/distributed-task-orchestrator.svg"
tags: ["python", "distributed-systems", "queues"]
tech_stack: ["Python", "FastAPI", "Redis", "PostgreSQL"]
github_url: "https://github.com/oornnery/distributed-task-orchestrator"
live_url: ""
date: 2025-02-14
featured: false
---

## Overview

This project coordinates async workloads across workers while preserving
ordering guarantees and fault tolerance.

## Core capabilities

- Job deduplication with idempotency keys
- Exponential backoff and dead-letter policies
- Real-time execution metrics and queue health insights
- Declarative workflow steps with clear failure boundaries

## Result

The orchestrator improved reliability for background tasks and reduced manual
recovery incidents in production.

## Execution model

The system treats a background job as a state machine instead of a single fire
and forget function call.
That made retries, timeouts, and progress tracking explicit.

### Intake

Incoming jobs are normalized into a stable envelope with tenant, workflow,
idempotency key, and priority metadata.
That envelope becomes the contract shared by API producers and worker
consumers.

### Scheduling

Scheduling prefers predictable fairness over raw throughput.
Queues are partitioned by workload type so a burst of low-value jobs does not
starve operationally critical work.

### Execution

Workers process declarative steps and report transitions after each boundary.
That creates a timeline operators can inspect without reading application code.

## Failure handling

Retries are useful only when they are selective.

### Retry policy

Transient dependency failures use exponential backoff with capped attempts.
Validation or business rule errors go straight to terminal states because
repeating them adds load without improving outcomes.

### Dead-letter flow

Dead-letter queues are treated as a debugging surface, not a dumping ground.
Each dead-lettered job keeps failure metadata, retry count, and the last known
step so investigation starts with context.

## Operator visibility

The project includes dashboards for the signals operators actually need during
incidents.

- oldest queued age
- throughput by workflow
- failure ratio by step
- retry churn by dependency

Those views made it easier to identify whether a problem was capacity,
poison-message behavior, or a downstream outage.

## Consistency tradeoffs

The orchestrator does not try to simulate perfect distributed transactions.
Instead, it leans on idempotency and explicit state transitions.

### Why idempotency matters

Workers can restart, messages can be redelivered, and operators can replay
events during recovery.
Idempotent handlers make those realities survivable.

### Where strict ordering applies

Ordering is enforced only inside workflow segments that truly require it.
Trying to preserve global ordering across all queues would have reduced
parallelism without improving business outcomes.

## What I would tune next

The next step would be adaptive concurrency based on queue health and
dependency saturation.
That would let the orchestrator push faster during calm periods while backing
off before downstream services start thrashing.
