# Backend

Spring Boot application. Implementation begins in Phase 8.

The backend is one deployable modular monolith. Code is organized by business
feature, and a module is created only when an active phase needs it.

Planned shape:

```text
src/main/java/.../
├── incident/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── camera/
├── zone/
└── shared/
```

The first backend implementation starts with the smallest incident/Kafka
consumer slice. Empty future modules are not scaffolded.

Module rules:

- Do not access another module's repository or JPA entity.
- Store cross-module references as stable IDs.
- Call another module through its application-facing interface.
- Keep database table and Flyway migration ownership explicit.
- Keep `shared` free of module-owned business logic.
- Prefer synchronous application-interface calls between in-process modules;
  use internal events only for genuinely asynchronous or one-to-many behavior.
- Apply SRP, DIP, and ISP pragmatically without creating an interface for every
  class.

The Kafka incident consumer belongs to `incident.infrastructure.messaging`.
When a module is later extracted as a service, it receives its own database or
schema credential and communicates through API/event contracts instead of
another service's tables.

See `docs/architecture.md` and ADR 005 for the complete decision.
