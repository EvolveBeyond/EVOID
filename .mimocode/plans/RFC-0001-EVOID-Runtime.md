# RFC-0001: EVOID Runtime

## The Reference Runtime for Intent-Oriented Programming

**Status:** Draft
**Version:** 2.0
**Date:** 2026-07-14

---

## Vision

EVOID is **not** a Python framework.
EVOID is **not** a web framework.
EVOID is **not** an HTTP framework.

EVOID is the **reference runtime and specification** for Intent-Oriented Programming (IOP).

Its purpose is to define how Intent-Oriented applications are executed, regardless of:
- Programming language
- Network protocol
- Transport
- Serialization format
- Dependency Injection implementation
- Validation library

Python is only the first reference implementation (using uv as package manager).

Future implementations may exist in: Rust, Go, C#, Java, Kotlin, Zig, JavaScript, C++

Each language implementation uses its native package manager:
- Python: uv
- Rust: cargo
- Go: go mod
- JavaScript: npm/bun
- etc.

The specification must remain language independent.

---

## Core Philosophy

Traditional frameworks organize applications around infrastructure:
```
HTTP → Router → Controller → Service → Model
```

IOP inverts this relationship:
```
Infrastructure exists only to execute Intents.
Everything else is replaceable.
Intent is permanent.
Infrastructure is temporary.
```

---

## What is EVOID?

EVOID is an execution runtime. Its responsibility is to execute Intent graphs.

It does NOT own:
- HTTP
- WebSocket
- Database
- Validation
- Serialization
- Dependency Injection

Those are infrastructure plugins.

---

## Runtime Architecture

```
        Intent
           │
           ▼
    Intent Resolver
           │
           ▼
   Pipeline Composer
           │
           ▼
 Processor Scheduler
           │
           ▼
  Execution Context
           │
           ▼
        Result
```

Everything else is external.

---

## Infrastructure Layer

Infrastructure is connected through adapters:

```
       Runtime
           │
           ▼
  Runtime Adapter
           │
           ▼
     EVOID Runtime
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
Schema  Storage  Serializer
 Engine   Engine   Engine
    ▼      ▼      ▼
Plugin  Plugin  Plugin
```

The Runtime never depends on concrete implementations.

---

## Runtime Adapters

Runtime adapters convert external events into Intents.

Examples:
- ASGI (FastAPI, Starlette)
- CLI (Typer, Click)
- Telegram Bot
- Discord Bot
- MQTT (IoT)
- Kafka (Event Streaming)
- RabbitMQ (Message Queue)
- Cron (Scheduled Tasks)
- gRPC
- IPC (Inter-Process Communication)

Every runtime produces the same internal execution model.

---

## Language Independence

The Runtime Specification must never depend on Python.

Python Runtime → Intent → Pipeline → Result
must behave exactly like
Rust Runtime → Intent → Pipeline → Result

The language changes. The execution model does not.

---

## Schema System

Schemas are implementation details.

Possible schema engines:
- Native (dataclasses, TypedDict)
- Pydantic
- msgspec
- attrs
- dataclass
- TypedDict

Future runtimes may use completely different schema systems.
This does not affect Intent execution.

---

## Dependency Injection

DI is not part of the Runtime. It is an engine.

Possible implementations:
- Native
- Spring-style
- Container-based
- Compile-time
- Reflection-based

The Runtime consumes dependencies. It never creates architectural assumptions around them.

---

## Transport Independence

HTTP is only one transport.
WebSocket is only one transport.
CLI is only one transport.

The Runtime must execute the same Intent regardless of where it originated.

---

## Execution Context

Every Intent executes inside an isolated execution context.

The context owns:
- State
- Dependencies
- Metadata
- Lifecycle
- Observability
- Security
- Transactions

The runtime owns the context.
Processors never own infrastructure.

---

## Plugin System

Every infrastructure component is a plugin.

Examples:
- Runtime Engine
- Schema Engine
- Serializer Engine
- DI Engine
- Storage Engine
- Cache Engine
- Logger Engine
- Configuration Engine
- Metrics Engine
- Tracing Engine
- Authorization Engine

Plugins communicate through contracts. Never through concrete implementations.

---

## Configuration

Configuration becomes the Composition Root.

```toml
[service]
name = "payment"

[runtime]
type = "asgi"
engine = "granian"

[schema]
engine = "native"

[serializer]
engine = "msgspec"

[di]
engine = "native"

[storage]
engine = "sqlalchemy"

[cache]
engine = "redis"

[metrics]
engine = "prometheus"

[logging]
engine = "structlog"
```

Changing infrastructure requires changing configuration.
Business logic remains untouched.

---

## Service Boot Lifecycle

```
Read Configuration
    ↓
Resolve Plugins
    ↓
Build Dependency Graph
    ↓
Create Execution Context
    ↓
Load Intents
    ↓
Compile Pipelines
    ↓
Initialize Runtime Adapter
    ↓
Start Runtime
    ↓
Serve Intents
```

The lifecycle is identical across all languages.

---

## Rewrite Instead of Migration

EVOID v1 inherited the assumptions of existing Python frameworks.
Those assumptions no longer match the long-term vision.

Attempting to migrate would preserve architectural constraints.
A rewrite allows IOP to become the foundation rather than an abstraction layered on top of HTTP frameworks.

---

## Long-Term Vision

The long-term objective is not to compete with FastAPI, Django, or Flask.

The objective is to define a new execution model.

Just as:
- JVM defines Java execution
- CLR defines .NET execution
- BEAM defines Erlang and Elixir execution

EVOID Runtime aims to define the execution model for Intent-Oriented Programming.

Python is only the beginning.
The Runtime is the product.
The language is an implementation detail.

**Intent is the platform.**
