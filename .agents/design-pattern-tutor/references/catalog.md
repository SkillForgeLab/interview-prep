# Design Pattern Learning Catalog

Read for curriculum planning, “start from the beginning,” or selecting a next
topic. Priorities are learning suggestions for this workspace, not universal
rankings or prerequisites. Teach a requested topic directly after only its
essential prerequisites. Do not display this whole catalog in an ordinary
interactive lesson.

## Suggested main path

1. Foundations: responsibilities, composition, coupling, and dependencies.
2. Strategy → State → Command → Observer.
3. Factory Method → Builder.
4. Adapter → Facade → Decorator → Proxy → Chain of Responsibility.
5. Dependency Injection → Layered Architecture → Service Layer → Repository.
6. Hexagonal / Ports & Adapters → Clean Architecture concepts.
7. Producer/Consumer → Message Queue → Publish/Subscribe → Delivery Semantics
   → Idempotent Consumer → Message Ordering.
8. Timeout → Retry → Circuit Breaker → Cache-Aside.
9. Transactional Outbox → Saga → CQRS; Event Sourcing is an optional extension.

Arrows suggest an instructional order, not a technical dependency. Builder does
not require Factory Method, Facade does not require Adapter, and CQRS does not
require Saga or Event Sourcing. Introduce only prerequisites needed for the
selected example. In particular, cover transactions before Outbox, delivery
semantics before broker recovery patterns, and shared-state races before locks.

## Priority guide

The priorities below are suggestions for this workspace, not universal
rankings. Implement a topic when the problem warrants it.

### Behavioral

**Practice deeply:** Strategy, State, Command, Observer, Chain of
Responsibility.

**Learn next when relevant:** Template Method, Iterator.

**Recognize; implement when needed:** Mediator, Memento, Visitor, Interpreter.

### Creational

**Practice deeply:** Factory Method, Builder.

**Learn next when relevant:** Abstract Factory.

**Recognize; implement when needed:** Prototype, Singleton, and Singleton
alternatives.

### Structural

**Practice deeply:** Adapter, Facade, Decorator, Proxy, Composite.

**Learn next when relevant:** Bridge.

**Recognize; implement when needed:** Flyweight.

### Application architecture

**Practice deeply:** DI, Layered Architecture, Service Layer, Hexagonal and
Clean Architecture concepts, MVC.

**Learn next when relevant:** MVVM for UI work.

**Recognize; implement when needed:** MVP.

### Data

**Practice deeply:** Repository, Cache-Aside.

**Learn next when relevant:** Unit of Work, Data Mapper, Active Record, Read
Replicas.

**Recognize; implement when needed:** Identity Map, Sharding, Shared Database
trade-offs.

### Messaging

**Practice deeply:** Producer/Consumer, Message Queue, Pub/Sub, Delivery
Semantics, Idempotent Consumer, Message Ordering.

**Learn next when relevant:** Dead Letter Queue, Competing Consumers.

**Recognize; implement when needed:** Broker-specific mechanisms only when
needed.

### Distributed systems

**Practice deeply:** Timeout, Retry, Circuit Breaker, Transactional Outbox,
Saga, CQRS concepts.

**Learn next when relevant:** Bulkhead, Rate Limiting, API Gateway, BFF,
Anti-Corruption Layer, Strangler Fig, Database per Service, Event Sourcing.

**Recognize; implement when needed:** Production adoption depends on the actual
problem.

### Concurrency

**Practice deeply:** Future/Promise, bounded Producer-Consumer, Thread/Worker
Pool, Lock/Mutex, Semaphore.

**Learn next when relevant:** Read-Write Lock, Reactor, Actor Model.

**Recognize; implement when needed:** Leader Election.

Priorities live here; topic references provide pressures, labs, and comparisons.
The collection includes object-oriented patterns, architectural approaches,
operational techniques, and concurrency primitives. Explain their scope instead
of presenting them all as the same kind of pattern.
