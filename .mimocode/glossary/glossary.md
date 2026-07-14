# EVOID Glossary

| Term | Definition |
|------|-----------|
| **Intent** | A declaration on a Pydantic field that drives infrastructure behavior (storage, caching, encryption, etc.) |
| **IOP** | Intent-Oriented Programming — the paradigm where data models declare infrastructure policy |
| **EPHEMERAL** | Intent for temporary data: aggressive caching, short TTL, no persistence |
| **STANDARD** | Intent for normal data: balanced caching, normal priority |
| **CRITICAL** | Intent for vital data: strong consistency, encryption, replication, audit |
| **DataIO** | Provider-agnostic, intent-aware data operations layer |
| **CircuitBreaker** | Pattern preventing cascading failures by tracking provider health |
| **EmergencySafetyBuffer** | In-memory SQLite buffer for CRITICAL data during provider failures |
| **IntentRouter** | Routes DB operations to appropriate services based on data intents |
| **PersistenceGateway** | Unified entry point for all database operations |
| **HealthAwareInject** | DI system that checks provider health on every resolution |
| **HealthProxy** | Wrapper for unhealthy dependencies enabling degraded mode |
| **PriorityQueue** | Intent-aware request scheduling with load shedding |
| **EnvironmentalIntelligence** | System monitoring providing GREEN/YELLOW/RED status |
| **ServiceProxy** | Smart proxy for inter-service communication |
| **MessageBus** | Async pub/sub messaging with intent-aware priority |
| **CacheLayer** | 3-tier caching: Memory → Redis → Disk |
| **BaseProvider** | Interface for all storage providers |
| **ServiceRegistry** | Auto-discovers pluggable services from config.toml |
| **CoreModelMapper** | Bidirectional API ↔ Core model mapping |
| **FuryCodec** | Optional binary serialization using PyFury |
| **DBExceptionInterceptor** | Converts DB-specific errors to unified EVOX errors |
| **BaseError** | Root exception class for all framework errors |
| **ServiceBuilder** | Fluent API for creating EVOID services |
| **Load Shedding** | Rejecting low-priority requests under system stress |
| **Degraded Mode** | Operating with unhealthy dependencies via HealthProxy |
| **Write-Through** | Writing to all cache tiers simultaneously (for CRITICAL data) |
| **Context-Aware Routing** | Proxy detecting internal vs external calls for optimal routing |
