"""Plugin Engine — Register custom adapters, engines, and languages.

IOP: Plugin system is just a registry (dict) and registration functions.
Users can register:
- Adapters (Telegram, Discord, MQTT, gRPC, etc.)
- Engines (Storage, Cache, Serializer, etc.)
- Languages (Rust, Go, etc.)
- Processors (custom logic)

The runtime doesn't care what you register — it just resolves by name.
"""
