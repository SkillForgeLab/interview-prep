Print / Save as PDF
Light theme · Self-contained HTML · A4 print layout

SENIOR / PRINCIPAL LEVEL

# Enterprise Solution Architect Design Patterns Competency Roadmap

For an architect with 20 years of experience · Four-phase
learning plan

The goal is to select, combine, defend, and reject patterns
based on business outcomes, integration complexity, reliability,
security, cost, and maintainability—not to memorize names.

**Success criteria:** Demonstrate
enterprise-wide architecture decisions, explicit trade-offs, realistic
failure handling, and clear communication to both delivery teams and
executives.

## 1. Competency levels

| Level | Capability |
| --- | --- |
| L1 — Awareness | Explain purpose and basic structure. |
| L2 — Application | Apply in a straightforward system. |
| L3 — Design | Select and compare alternatives. |
| L4 — Enterprise | Apply across systems, teams, and platforms. |
| L5 — Principal | Define standards, challenge assumptions, and govern adoption. |

**Target:** L4–L5 for must-know patterns; L2–L3 for optional
patterns.

## 2. Pattern inventory by category

These are the same must-know and optional topics detailed in section 3. Section 2 groups them by category; section 3 places them in study phases.

### A. Architecture foundations and domain boundaries

| Must know (target) | Optional / situational |
| --- | --- |
| Layered Architecture (L5) · Critical; Modular Monolith (L5) · Critical; Microservices (L5) · Critical; SOA (L5) · Critical; Hexagonal Architecture (L4) · Critical; DDD (L5) · Critical; Bounded Context (L5) · Critical; Anti-Corruption Layer (L5) · Critical; API-First (L4); Onion Architecture (L4) · Critical; Clean Architecture (L4) · Critical; Event-Driven Architecture (L5) · Critical; Aggregates (L5) · Critical; Domain Events (L4) · Critical; Ports and Adapters (L4) · Critical; Team Topologies (L4) · Critical | Microkernel; Plugin Architecture; Space-Based Architecture |

**Example:** Connect an old ERP, a CRM SaaS platform, and a
new e-commerce service. Decide where domain boundaries belong and when
direct integration is acceptable. **Trade-off:**
Microservices improve independent ownership but increase distributed
operations and consistency costs.

### B. Distributed systems and resilience

| Must know (target) | Optional / situational |
| --- | --- |
| Circuit Breaker (L5) · Critical; Retry with Backoff and Jitter (L5) · Critical; Timeout (L5) · Critical; Bulkhead (L5) · Critical; Idempotency (L5) · Critical; Saga (L5) · Critical; Transactional Outbox (L5) · Critical; Dead Letter Queue (L4) · Critical; Backpressure (L4) · Critical; Rate Limiting (L5) · Critical; Graceful Degradation (L5) · Critical; Leader Election (L4) · Critical; Load Shedding (L5) · Critical; Connection Pooling (L4) · Critical; Failover (L5) · Critical; Throttling (L4) · Critical | Distributed Locking; Hedged Requests; Quorum Reads/Writes; Consistent Hashing |

**Example:** Payment succeeds while inventory reservation
fails. Design retries, compensation, status reconciliation, and
duplicate prevention. **Trade-off:** Retrying improves
recovery but can overload failing dependencies; Saga compensation is not
a database rollback.

### C. Enterprise integration and messaging

| Must know (target) | Optional / situational |
| --- | --- |
| Request-Reply (L5) · Critical; API Gateway (L5) · Critical; Backend for Frontend (BFF) (L4) · Critical; Consumer-Driven Contracts (L4); Publish-Subscribe (L5) · Critical; Competing Consumers (L4) · Critical; CDC (L5) · Critical; Message Router (L4) · Critical; Message Translator (L4) · Critical; Strangler Fig (L5) · Critical; Canonical Data Model (L4); Service Mesh (L4) · Critical; Sidecar (L4) · Critical; Service Discovery (L5) · Critical | Aggregator; Claim Check; Scatter-Gather; Content-Based Router; Pipes and Filters |

**Example:** Synchronize customer changes across core
banking, CRM, fraud, and analytics. **Trade-off:** One
canonical enterprise model reduces some translations but can create a
central governance bottleneck.

### D. Data architecture and consistency

| Must know (target) | Optional / situational |
| --- | --- |
| Database per Service (L5) · Critical; CQRS (L4) · Critical; Cache-Aside (L5) · Critical; Materialized View (L4) · Critical; Replication (L5) · Critical; Sharding (L4) · Critical; Eventual Consistency (L5); Outbox + CDC (L5); Event Sourcing (L4) · Critical; Lakehouse Architecture (L4); Data Mesh Principles (L4); Caching (L5) · Critical; Polyglot Persistence (L4) · Critical | Event-Carried State Transfer; Specialized Consistency Models; Lambda/Kappa Architecture; Data Vault |

**Example:** Create a unified customer view across 25
applications. Address system-of-record ownership, identity matching,
master data, and conflicts. **Trade-off:** CQRS adds models
and synchronization complexity; Event Sourcing is separate and not
required.

### E. Cloud, security, and modernization

| Must know (target) | Optional / situational |
| --- | --- |
| Queue-Based Load Leveling (L5) · Critical; Multi-AZ (L5) · Critical; Active-Passive (L5) · Critical; Active-Active (L4) · Critical; Autoscaling (L4) · Critical; Zero Trust (L5) · Critical; Least Privilege (L5) · Critical; Defense in Depth (L5) · Critical; Strangler Fig (L5) · Critical; Branch by Abstraction (L4) · High; Expand-Contract (L4) · High; Multi-Region Active-Active (L4) · Critical; Service Mesh (L4) · Critical; Serverless (L4) · Critical; Multi-Region Architecture (L5) · Critical; OAuth 2.0 / OpenID Connect (L5) · Critical; Token Exchange (L4) · Critical; Secrets Management (L5) · Critical; Parallel Run (L4) · High; Blue-Green Deployment (L4) · High; Canary Deployment (L4) · High | Cell-Based Architecture; Sidecar Security Enforcement; Advanced Chaos Engineering |

**Example:** Migrate a regulated on-premises workload to
cloud. Cover identity, encryption, data residency, disaster recovery,
rollback, and cost. **Trade-off:** Multi-region
active-active adds consistency and operational complexity and should be
justified by measurable business needs.

### F. Object-oriented / GoF

| Must know (target) | Optional / situational |
| --- | --- |
| Factory Method (L4) · High; Abstract Factory (L4) · High; Builder (L4) · High; Singleton (L4) · High; Adapter (L4) · High; Facade (L4) · High; Strategy (L4) · High; Observer (L4) · High; Decorator (L4) · High; Proxy (L4) · High; Command (L4) · High; Template Method (L4) · High; Chain of Responsibility (L4) · High | — |

**Example:** Compose a legacy integration client with clear creation, behavior and access boundaries. **Trade-off:** Object-level patterns help local design but do not replace enterprise architecture decisions.

### G. Enterprise application

| Must know (target) | Optional / situational |
| --- | --- |
| Repository (L4) · High; Unit of Work (L4) · High; Dependency Injection (L4) · High; Service Layer (L4) · High; Data Mapper (L4) · High; Specification (L4) · High; Domain Model (L4) · High | — |

**Example:** Model an order application with explicit domain behavior, persistence and transaction boundaries. **Trade-off:** Extra layers help when they enforce real boundaries, but add ceremony when the domain is simple.

## 3. Learning, delivery and interview mastery plan

For each topic, prepare a 60-second explanation, a whiteboard design, when to use or avoid it, two alternatives, failure modes, security and operational implications, and a production example with measurable trade-offs. Categories retain the A–G grouping from the pattern inventory in section 2. Critical and High checklist topics are must-know assignments. The numbered assignments group work by theme; the mastery tables contain the complete pattern inventory for each phase. After each topic, draft the architecture card described in section 4.

### Phase 1 — Architecture foundations

#### Learning assignments and deliverables

1. **Architecture style selection**
   Required deliverable: Compare three architectures for one business system.
2. **Domain modeling and ownership boundaries**
   Required deliverable: Domain map and integration boundaries.
3. **Application and API boundaries**
   Required deliverable: API boundary and dependency diagrams.
4. **Quality attributes and architecture decisions**
   Required deliverable: Three ADRs with rejected alternatives.

#### Must-know interview mastery

| Pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| **Layered Architecture (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Dependency direction, layer responsibilities, bypass risks, testing boundaries; compare with hexagonal and modular monolith. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Modular Monolith (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Module ownership, enforceable boundaries, shared deployment, extraction triggers; defend against premature microservices. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Microservices (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Service decomposition, independent deployment, data ownership, network failure, observability, organizational prerequisites. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **SOA (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Service contracts, enterprise integration, orchestration, shared infrastructure and governance; contrast microservices. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #11 **Hexagonal Architecture (L4)** Must know · Critical | A — Architecture foundations and domain boundaries | Ports/adapters, dependency inversion, test seams, framework independence; sketch inbound and outbound adapters. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #1 **DDD (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Ubiquitous language, subdomains, context mapping, aggregates, invariants, domain events and strategic vs tactical ddd. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #1 **Bounded Context (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Context boundaries, ownership, translation, context maps and avoiding a universal enterprise data model. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #14 **Anti-Corruption Layer (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Legacy translation, domain isolation, ownership, latency and migration lifecycle. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **API-First (L4)** Must know | A — Architecture foundations and domain boundaries | Contract design, versioning, compatibility, auth, pagination, errors, lifecycle and governance. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Request-Reply (L5)** Must know · Critical | C — Enterprise integration and messaging | Sync coupling, timeout, error contracts, retries, latency and when async is better. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #9 **API Gateway (L5)** Must know · Critical | C — Enterprise integration and messaging | Routing, auth, throttling, observability, api lifecycle, bottlenecks and gateway vs service responsibilities. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #9 **Backend for Frontend (BFF) (L4)** Must know · Critical | C — Enterprise integration and messaging | Client-specific composition, team ownership, api duplication, cache and mobile/web trade-offs. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Consumer-Driven Contracts (L4)** Must know | C — Enterprise integration and messaging | Provider/consumer compatibility, contract tests, deployment sequencing and breaking changes. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Onion Architecture (L4)** Must know · Critical | A — Architecture foundations and domain boundaries | Explain dependency rule and overlap with hexagonal/clean architecture; name one situation where it is preferable and one where it is not. |
| **Clean Architecture (L4)** Must know · Critical | A — Architecture foundations and domain boundaries | Explain use cases, boundaries and dependency inversion; name one situation where it is preferable and one where it is not. |
| **Factory Method (L4)** Must know · High | F — Object-oriented / GoF | Creation behind an interface, subclass choice and test seams; compare with Abstract Factory and direct construction. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Abstract Factory (L4)** Must know · High | F — Object-oriented / GoF | Consistent families of related objects, product compatibility and extensibility; compare with Factory Method. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Builder (L4)** Must know · High | F — Object-oriented / GoF | Stepwise construction, validation and immutable results; avoid unnecessary builders for simple objects. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Singleton (L4)** Must know · High | F — Object-oriented / GoF | Single-instance lifecycle, concurrency, hidden global state and testing costs; compare with managed dependency scope. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Adapter (L4)** Must know · High | F — Object-oriented / GoF | Translate an incompatible object interface while preserving client contracts; distinguish from architecture-level ports and adapters. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Facade (L4)** Must know · High | F — Object-oriented / GoF | Provide a simpler boundary over a complex subsystem; avoid hiding important failures or ownership. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Strategy (L4)** Must know · High | F — Object-oriented / GoF | Select interchangeable algorithms by context; explain composition, configuration and testing. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Observer (L4)** Must know · High | F — Object-oriented / GoF | Notify subscribers of state changes; address lifecycle, ordering and failure; distinguish from distributed publish-subscribe. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Decorator (L4)** Must know · High | F — Object-oriented / GoF | Add behavior by composition; explain ordering, transparency and tracing through wrapper chains. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Proxy (L4)** Must know · High | F — Object-oriented / GoF | Control access through a representative object; compare local proxy, remote proxy and gateway boundaries. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Command (L4)** Must know · High | F — Object-oriented / GoF | Encapsulate an action as an object for queuing, audit or undo; distinguish from a distributed command message. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Template Method (L4)** Must know · High | F — Object-oriented / GoF | Fix an algorithm skeleton while varying steps; compare with Strategy and composition. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Chain of Responsibility (L4)** Must know · High | F — Object-oriented / GoF | Pass a request through ordered handlers; define termination, error behavior and observability. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Repository (L4)** Must know · High | G — Enterprise application | Separate domain-facing persistence contracts from storage details; avoid leaking query and transaction behavior. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Unit of Work (L4)** Must know · High | G — Enterprise application | Coordinate one transactional change set, identity tracking and commit boundaries; explain limits across services. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Dependency Injection (L4)** Must know · High | G — Enterprise application | Provide dependencies explicitly, control object lifetimes and composition roots; avoid service locator behavior. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Service Layer (L4)** Must know · High | G — Enterprise application | Place application orchestration and transaction boundaries outside domain entities; distinguish from domain services. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Data Mapper (L4)** Must know · High | G — Enterprise application | Map domain objects to persistence models without coupling domain logic to storage schemas. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Specification (L4)** Must know · High | G — Enterprise application | Express reusable business predicates and composition; distinguish in-memory evaluation from database translation. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Domain Model (L4)** Must know · High | G — Enterprise application | Model entities, value objects, invariants and behavior; compare with anemic data models. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Aggregates (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Define consistency boundaries, invariants, roots and transaction scope; avoid oversized aggregates. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Domain Events (L4)** Must know · Critical | A — Architecture foundations and domain boundaries | Capture meaningful domain facts, publication boundaries and evolution; distinguish internal events from integration events. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Ports and Adapters (L4)** Must know · Critical | A — Architecture foundations and domain boundaries | Define inward-facing ports and replaceable adapters; distinguish this architecture concept from the GoF Adapter pattern. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Service Discovery (L5)** Must know · Critical | C — Enterprise integration and messaging | Resolve healthy service instances, handle registration and stale endpoints, and compare client-side with platform discovery. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |

#### Optional / situational topics (L2–L3)

| Pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| Microkernel | A — Architecture foundations and domain boundaries | Explain plugin lifecycle, extensibility and core stability; name one situation where it is preferable and one where it is not. |
| Plugin Architecture | A — Architecture foundations and domain boundaries | Explain contracts, versioning and sandboxing; name one situation where it is preferable and one where it is not. |

### Phase 2 — Distributed systems

#### Learning assignments and deliverables

1. **Dependency resilience and failure handling**
   Required deliverable: Resilience design for a failing dependency.
2. **Distributed workflow and recovery**
   Required deliverable: Distributed order and payment workflow.
3. **Event integration and contracts**
   Required deliverable: Five-application event integration design.
4. **Read models, scale and consistency**
   Required deliverable: Read-scaling and consistency decision matrix.

#### Must-know interview mastery

| Pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| #13 **Event-Driven Architecture (L5)** Must know · Critical | A — Architecture foundations and domain boundaries | Commands vs events, broker semantics, ordering, schema evolution, replay, eventual consistency and observability. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #5 **Circuit Breaker (L5)** Must know · Critical | B — Distributed systems and resilience | Closed/open/half-open states, thresholds, failure signals, fallback, observability and when not to trip. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #7 **Retry with Backoff and Jitter (L5)** Must know · Critical | B — Distributed systems and resilience | Transient vs permanent faults, retry budgets, jitter, idempotency, deadlines and retry storms. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #7 **Timeout (L5)** Must know · Critical | B — Distributed systems and resilience | Connection vs request timeouts, end-to-end deadlines, latency budgets and cancellation propagation. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #6 **Bulkhead (L5)** Must know · Critical | B — Distributed systems and resilience | Thread/connection pool isolation, concurrency limits, blast radius and capacity trade-offs. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #8 **Idempotency (L5)** Must know · Critical | B — Distributed systems and resilience | Keys, deduplication storage, response replay, atomicity, ttl, side-effect boundaries and payments. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #2 **Saga (L5)** Must know · Critical | B — Distributed systems and resilience | Orchestration vs choreography, compensation, irreversible steps, timeouts, state tracking and reconciliation. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #3 **Transactional Outbox (L5)** Must know · Critical | B — Distributed systems and resilience | Atomic database write + outbox, relay, ordering, duplicates, cleanup and consumer idempotency. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Dead Letter Queue (L4)** Must know · Critical | B — Distributed systems and resilience | Poison messages, retry policy, alerting, replay, privacy and operational ownership. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Backpressure (L4)** Must know · Critical | B — Distributed systems and resilience | Producer/consumer mismatch, bounded queues, admission control, shedding and throughput/latency trade-offs. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Rate Limiting (L5)** Must know · Critical | B — Distributed systems and resilience | Token/leaky bucket, quotas, fairness, distributed counters, http 429 and burst behavior. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Graceful Degradation (L5)** Must know · Critical | B — Distributed systems and resilience | Critical vs optional features, fallbacks, stale reads, feature flags and user-facing behavior. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #12 **Publish-Subscribe (L5)** Must know · Critical | C — Enterprise integration and messaging | Topic design, fan-out, subscriptions, delivery guarantees, ordering and schema evolution. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Competing Consumers (L4)** Must know · Critical | C — Enterprise integration and messaging | Consumer groups, parallelism, partitions, ordering, duplicate processing and scaling bottlenecks. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **CDC (L5)** Must know · Critical | C — Enterprise integration and messaging | Log-based capture, snapshot + stream, ordering, schema changes, lag, deletes and system-of-record semantics. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #15 **Database per Service (L5)** Must know · Critical | D — Data architecture and consistency | Ownership, no cross-service joins, consistency, query composition and reporting alternatives. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #4 **CQRS (L4)** Must know · Critical | D — Data architecture and consistency | Separate models, projection lag, query needs, complexity and why event sourcing is optional. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Cache-Aside (L5)** Must know · Critical | D — Data architecture and consistency | Miss/hit flow, invalidation, ttl, stampede, consistency and eviction. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Materialized View (L4)** Must know · Critical | D — Data architecture and consistency | Refresh strategy, projection rebuild, lag, source of truth and query acceleration. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Replication (L5)** Must know · Critical | D — Data architecture and consistency | Sync vs async, lag, failover, read-your-writes, split-brain and recovery. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Sharding (L4)** Must know · Critical | D — Data architecture and consistency | Shard key, skew, resharding, hotspots, cross-shard queries and tenant isolation. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Eventual Consistency (L5)** Must know | D — Data architecture and consistency | Staleness bounds, user expectations, invariants, reconciliation and consistency choices. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Outbox + CDC (L5)** Must know | D — Data architecture and consistency | Transaction log capture, outbox delivery, ordering, duplicates and operations. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Queue-Based Load Leveling (L5)** Must know · Critical | E — Cloud, security, and modernization | Buffer sizing, consumer scaling, queue age, overload, dlq and backpressure. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Leader Election (L4)** Must know · Critical | B — Distributed systems and resilience | Explain leases, fencing tokens and split-brain; name one situation where it is preferable and one where it is not. |
| **Event Sourcing (L4)** Must know · Critical | D — Data architecture and consistency | Explain append-only events, replay, projections, event versioning and GDPR concerns; name one situation where it is preferable and one where it is not. |
| **Load Shedding (L5)** Must know · Critical | B — Distributed systems and resilience | Reject excess work deliberately under overload; define admission signals, user impact and recovery thresholds. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Connection Pooling (L4)** Must know · Critical | B — Distributed systems and resilience | Bound connection reuse and concurrency; tune pool size, timeouts, queueing and failure behavior. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Failover (L5)** Must know · Critical | B — Distributed systems and resilience | Detect unhealthy components, move traffic or leadership safely and prevent split-brain during recovery. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Throttling (L4)** Must know · Critical | B — Distributed systems and resilience | Shape request or work rate, return clear signals and coordinate per-client limits with downstream capacity. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Caching (L5)** Must know · Critical | D — Data architecture and consistency | Select cache ownership, invalidation, TTL, consistency and stampede controls; compare with Cache-Aside. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Polyglot Persistence (L4)** Must know · Critical | D — Data architecture and consistency | Choose stores by access pattern and data ownership; address operations, skills, integration and consistency costs. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |

#### Optional / situational topics (L2–L3)

| Pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| Space-Based Architecture | A — Architecture foundations and domain boundaries | Explain in-memory grids, partitioning and operational complexity; name one situation where it is preferable and one where it is not. |
| Distributed Locking | B — Distributed systems and resilience | Explain lease expiry, fencing and correctness; name one situation where it is preferable and one where it is not. |
| Hedged Requests | B — Distributed systems and resilience | Explain tail latency vs extra load; name one situation where it is preferable and one where it is not. |
| Quorum Reads/Writes | B — Distributed systems and resilience | Explain replica agreement, availability and consistency; name one situation where it is preferable and one where it is not. |
| Consistent Hashing | B — Distributed systems and resilience | Explain key distribution and node churn; name one situation where it is preferable and one where it is not. |
| Event-Carried State Transfer | D — Data architecture and consistency | Explain event payload completeness, duplication and staleness; name one situation where it is preferable and one where it is not. |
| Specialized Consistency Models | D — Data architecture and consistency | Explain linearizability, causal consistency, quorums and business invariants; name one situation where it is preferable and one where it is not. |

### Phase 3 — Enterprise integration and modernization

#### Learning assignments and deliverables

1. **Enterprise application integration**
   Required deliverable: Enterprise integration reference architecture.
2. **Incremental legacy modernization**
   Required deliverable: Phased legacy modernization plan.
3. **Identity and security boundaries**
   Required deliverable: Cross-platform identity and access design.
4. **Cloud resilience and disaster recovery**
   Required deliverable: Business-critical hybrid deployment review.

#### Must-know interview mastery

| Pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| **Message Router (L4)** Must know · Critical | C — Enterprise integration and messaging | Routing rules, content vs metadata, versioning, traceability and operational ownership. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Message Translator (L4)** Must know · Critical | C — Enterprise integration and messaging | Schema mapping, semantic mismatch, validation, canonical vs domain contracts and error handling. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #10 **Strangler Fig (L5)** Must know · Critical | C — Enterprise integration and messaging | Incremental routing, coexistence, cutover, rollback, data migration and legacy dependency risks. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Canonical Data Model (L4)** Must know | C — Enterprise integration and messaging | Shared semantics, versioning, governance, translation costs and over-centralization risks. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Lakehouse Architecture (L4)** Must know | D — Data architecture and consistency | Batch/stream ingestion, table formats, governance, quality, cost and bi/ml access patterns. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Data Mesh Principles (L4)** Must know | D — Data architecture and consistency | Domain ownership, data products, federated governance, interoperability and adoption prerequisites. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Multi-AZ (L5)** Must know · Critical | E — Cloud, security, and modernization | Failure domains, health checks, regional dependencies, failover tests and cost. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Active-Passive (L5)** Must know · Critical | E — Cloud, security, and modernization | Standby modes, failover triggers, rto/rpo, replication and dr exercises. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Active-Active (L4)** Must know · Critical | E — Cloud, security, and modernization | Traffic steering, data conflicts, state replication, consistency and operational complexity. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Autoscaling (L4)** Must know · Critical | E — Cloud, security, and modernization | Metrics, warm-up, limits, stateful constraints, scale-in safety and cost. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Zero Trust (L5)** Must know · Critical | E — Cloud, security, and modernization | Identity-centric access, continuous verification, device/workload posture, segmentation and policy enforcement. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Least Privilege (L5)** Must know · Critical | E — Cloud, security, and modernization | Role vs attribute policies, jit access, service identities, privilege reviews and exceptions. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Defense in Depth (L5)** Must know · Critical | E — Cloud, security, and modernization | Identity, network, application, data, monitoring, layered controls and threat modeling. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| #10 **Strangler Fig (L5)** Must know · Critical | E — Cloud, security, and modernization | Incremental routing, coexistence, cutover, rollback, data migration and legacy dependency risks. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Branch by Abstraction (L4)** Must know · High | E — Cloud, security, and modernization | Replace dependency behind interface, feature toggles, parallel implementations and safe removal. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Expand-Contract (L4)** Must know · High | E — Cloud, security, and modernization | Additive schema change, dual reads/writes, rollout ordering, backfill and cleanup. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Service Mesh (L4)** Must know · Critical | C — Enterprise integration and messaging | Explain mTLS, traffic policy, overhead and team readiness; name one situation where it is preferable and one where it is not. |
| **Sidecar (L4)** Must know · Critical | C — Enterprise integration and messaging | Explain deployment coupling, resource cost and policy enforcement; name one situation where it is preferable and one where it is not. |
| **Multi-Region Active-Active (L4)** Must know · Critical | E — Cloud, security, and modernization | Explain conflict resolution, residency, RPO/RTO and cost; name one situation where it is preferable and one where it is not. |
| **Service Mesh (L4)** Must know · Critical | E — Cloud, security, and modernization | Explain mTLS, traffic policy, overhead and team readiness; name one situation where it is preferable and one where it is not. |
| **Serverless (L4)** Must know · Critical | E — Cloud, security, and modernization | Assess event-driven execution, scaling, cold starts, limits, observability and lock-in against long-running services. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Multi-Region Architecture (L5)** Must know · Critical | E — Cloud, security, and modernization | Choose regional topology using latency, residency, RTO/RPO, failover and consistency requirements. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **OAuth 2.0 / OpenID Connect (L5)** Must know · Critical | E — Cloud, security, and modernization | Explain authorization versus authentication, flows, scopes, token validation and trust boundaries. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Token Exchange (L4)** Must know · Critical | E — Cloud, security, and modernization | Delegate identity across services with audience restriction, short lifetimes and auditable trust boundaries. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Secrets Management (L5)** Must know · Critical | E — Cloud, security, and modernization | Control storage, access, rotation, distribution and audit of credentials and keys. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Parallel Run (L4)** Must know · High | E — Cloud, security, and modernization | Run legacy and replacement paths side by side; compare outputs, resolve divergence and define cutover criteria. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Blue-Green Deployment (L4)** Must know · High | E — Cloud, security, and modernization | Switch between complete environments with health gates and rollback; plan database compatibility. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |
| **Canary Deployment (L4)** Must know · High | E — Cloud, security, and modernization | Release to a small cohort, measure guardrails and expand or roll back safely. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |

#### Optional / situational topics (L2–L3)

| Pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| Aggregator | C — Enterprise integration and messaging | Explain fan-in, partial failures and latency; name one situation where it is preferable and one where it is not. |
| Claim Check | C — Enterprise integration and messaging | Explain large payload storage, retention and security; name one situation where it is preferable and one where it is not. |
| Scatter-Gather | C — Enterprise integration and messaging | Explain parallel calls, time budgets and partial results; name one situation where it is preferable and one where it is not. |
| Content-Based Router | C — Enterprise integration and messaging | Explain routing rules and testability; name one situation where it is preferable and one where it is not. |
| Pipes and Filters | C — Enterprise integration and messaging | Explain composable transformations and observability; name one situation where it is preferable and one where it is not. |
| Lambda/Kappa Architecture | D — Data architecture and consistency | Explain batch/stream complexity and operational choices; name one situation where it is preferable and one where it is not. |
| Data Vault | D — Data architecture and consistency | Explain historical modeling, lineage and warehouse trade-offs; name one situation where it is preferable and one where it is not. |
| Cell-Based Architecture | E — Cloud, security, and modernization | Explain failure isolation, routing and tenancy; name one situation where it is preferable and one where it is not. |
| Sidecar Security Enforcement | E — Cloud, security, and modernization | Explain policy deployment and blast radius; name one situation where it is preferable and one where it is not. |
| Advanced Chaos Engineering | E — Cloud, security, and modernization | Explain hypotheses, guardrails, blast radius and rollback; name one situation where it is preferable and one where it is not. |

### Phase 4 — Principal architect practice

#### Learning assignments and deliverables

1. **Business capabilities, target state and roadmaps**
   Required deliverable: Three-year target-state roadmap.
2. **Governance, standards, exceptions and technical debt**
   Required deliverable: Architecture review checklist.
3. **Trade-off analysis and executive communication**
   Required deliverable: Two-option architecture board presentation.
4. **Full enterprise architecture case study**
   Required deliverable: Complete proposal with defense and review.

#### Must-know interview mastery

| Pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| **Team Topologies (L4)** Must know · Critical | A — Architecture foundations and domain boundaries | Align team ownership, interaction modes and cognitive load with architecture boundaries and platform responsibilities. *Interview drill:* explain a real enterprise scenario, defend this choice against an alternative, and identify one failure case. |

**Interview synthesis:** Apply the patterns from phases 1–3 to the four deliverables above. Defend choices against alternatives, explain failures and recovery, and translate decisions into standards, roadmaps and executive recommendations.

## 4. Top 15 patterns to prioritize

This interview shortlist follows the phase plan above. A shared rank groups closely related patterns; the same badges appear beside their detailed mastery rows in section 3. Event Sourcing and Cache-Aside remain in the full guide for deeper, workload-specific study.

| Priority & pattern / level | Category | What to master to pass a senior interview |
| --- | --- | --- |
| #1 **DDD (L5) / Bounded Context (L5)** | A — Architecture foundations | Identify subdomains, define context boundaries and ownership, map interactions, and defend the split against alternative service boundaries. |
| #2 **Saga (L5)** | B — Distributed systems | Design local transactions, orchestration or choreography, compensation, reconciliation, and recovery when compensation itself fails. |
| #3 **Transactional Outbox (L5)** | B — Distributed systems | Prevent dual-write loss; explain the local transaction, relay, at-least-once delivery, ordering, and idempotent consumers. |
| #4 **CQRS (L4)** | D — Data architecture | Separate write and read models only when warranted; address projections, stale reads, synchronization, and simpler alternatives. |
| #5 **Circuit Breaker (L5)** | B — Distributed systems | Set failure thresholds and reset behavior; show how callers fail fast, recover, and avoid cascading outages. |
| #6 **Bulkhead (L5)** | B — Distributed systems | Isolate resource pools and workloads; choose concurrency limits and explain what happens when a partition fills. |
| #7 **Retry with Backoff and Jitter (L5) / Timeout (L5)** | B — Distributed systems | Budget end-to-end time, retry only safe failures, add backoff and jitter, and prevent retry storms or duplicate effects. |
| #8 **Idempotency (L5)** | B — Distributed systems | Define keys, deduplication scope and retention; make repeated commands safe across retries and at-least-once delivery. |
| #9 **API Gateway (L5) / Backend for Frontend (BFF) (L4)** | C — Enterprise integration | Define client-facing boundaries, auth, routing and composition; distinguish a shared gateway from client-specific backends. |
| #10 **Strangler Fig (L5)** | C / E — Integration and modernization | Plan coexistence, incremental routing, data ownership, cutover and rollback while the legacy system remains live. |
| #11 **Hexagonal Architecture (L4)** | A — Architecture foundations | Draw ports and adapters, dependency direction and test seams; explain when the added boundaries pay off. |
| #12 **Publish-Subscribe (L5)** | C — Enterprise integration | Explain producer-consumer decoupling, contracts, delivery semantics, ordering, replay and operational failure handling. |
| #13 **Event-Driven Architecture (L5)** | A — Architecture foundations | Distinguish commands from events; defend event flow, schema evolution, consistency, observability and recovery. |
| #14 **Anti-Corruption Layer (L5)** | A — Architecture foundations | Protect a domain model from legacy semantics; address translation ownership, latency and migration lifecycle. |
| #15 **Database per Service (L5)** | D — Data architecture | Define data ownership and cross-service queries; defend consistency, migration and operational costs against shared storage. |

### Architecture card — create after each topic

Draft this card from memory after the interview drill, then check and correct it. Keep it concise; give the Top 15 fuller treatment and use shorter cards for the other topics.

1. **Problem:** What specific problem does the pattern solve?
2. **Context:** When is it appropriate, and when should it be avoided?
3. **Trade-offs:** What complexity, cost and risks does it introduce?
4. **Alternatives:** What simpler approach could work, and why might it be sufficient?
5. **Implementation:** How would it work in the target stack? State the stack and the main components, data flows and operational controls.
6. **Failure scenarios:** What happens during outages, duplicates or traffic spikes? Adapt this field to the pattern; for object-oriented patterns, consider misuse, object lifetime, concurrency and testing.

**Top 15 only — Real-world project example:** The AI assistant must find, verify, and provide one named production project that used the pattern. Include the organization and system, the problem, how the pattern was applied, any reported outcome, and a direct link to the organization’s engineering write-up or another primary source. The assistant must do this research itself, without asking you to name a project. If it cannot verify a suitable case, it must say so and must not invent one.

## 5. Worked example — Enterprise order platform

```
        Web / Mobile / Partners
                  |
             API Gateway
                  |
             Order Service
                  |
             Order Database
                  |
         Transactional Outbox
                  |
             Event Broker
                  |
         Workflow Orchestrator
           /       |       \
      Payment   Inventory  Shipping
         |         |         |
      Provider   ERP Adapter  Logistics API
                    |
                 Legacy ERP
```

| Pattern | Why use it | Trade-off |
| --- | --- | --- |
| API Gateway | Routing and entry-point policies | Shared dependency and potential bottleneck |
| Saga | Coordinate multi-system transactions | Complex compensation and recovery |
| Transactional Outbox | Publish events reliably after database commits | Relay operations and duplicate handling |
| Idempotency | Avoid duplicate payment actions | Durable request-state tracking |
| Anti-Corruption Layer | Isolate legacy ERP models | Mapping maintenance |
| Circuit Breaker | Limit pressure on failing services | Threshold tuning and recovery handling |
| Event-Driven | Decouple systems | Eventual consistency and tracing complexity |

**Interview challenge:** A payment
provider times out after charging the customer. Explain status
reconciliation, idempotency, correlation IDs, retry rules, and
operational recovery. Do not blindly retry the charge.

## 6. AI study assistant — copy-and-use instructions

Give the entire HTML file to your AI assistant, then paste this
prompt. It is designed for structured interview practice rather than
passive reading.

```
You are my Principal Enterprise Solution Architect interview coach. Use the attached roadmap as the complete study syllabus. Treat all MUST-KNOW patterns as target L4–L5 and OPTIONAL patterns as L2–L3.

For EACH topic in the roadmap:
1. Explain the problem, pattern mechanics and context in plain English.
2. Draw a small ASCII architecture diagram.
3. Give a realistic enterprise example involving legacy, SaaS, cloud or regulated systems.
4. Compare at least two alternatives; explain when NOT to use this pattern.
5. Explain failure modes, consistency, security, observability, operations and cost implications.
6. Ask five interview questions: fundamentals, design, failure scenario, trade-off challenge, and executive communication.
7. Ask ONE question at a time. Wait for my response. Do not reveal the model answer first.
8. Score my answer 0–5 for correctness, depth, trade-offs, communication and enterprise applicability. Identify missing points and give a stronger model answer.
9. Make me redo weak answers. Track my topic scores, gaps and revisit dates.
10. After I answer, ask me to draft an architecture card from memory before you fill gaps. Review and correct it. Use six fields: Problem, Context, Trade-offs, Alternatives (including a simpler option), Implementation in my target stack, and Failure scenarios. Ask for my target stack if unknown; adapt failure scenarios to the pattern. Keep the card concise, with fuller treatment for Top 15 topics.
11. For each Top 15 topic, YOU must research and provide one real-world production project that used the pattern. Browse the web and verify it with a primary source, preferably the organization’s engineering write-up. Give the organization and system, the problem, how the pattern was implemented, any reported outcome, and a direct source link. Do not ask me to name a project or supply an example. Do not invent a case or present an inferred use as documented fact. If no suitable case can be verified, say so explicitly.
12. End each topic with three follow-up drills and revisit weak cards later.

Start by assessing my current knowledge in the first must-know topic. Challenge vague claims and unsupported assumptions. If the roadmap uses a concept that is not formally a design pattern, distinguish it from an architectural style, principle, or technique. Do not invent vendor-specific facts; verify current product claims using official documentation.
```

## 7. Interview-ready answer framework

**Context → Constraints → Options → Decision → Trade-offs →
Failure/Recovery → Evidence.** In every system design answer,
quantify expected scale, SLO, RTO/RPO, consistency needs, team
capacity and cost before choosing technology. Use ADRs to document
decisions.

## 8. Official reference material

* [Microsoft
  Learn — Cloud Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
* [AWS
  Prescriptive Guidance — Cloud Design Patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/)
* [The Open Group — TOGAF
  Standard](https://www.opengroup.org/togaf)

Enterprise Solution Architect Design Patterns Competency Roadmap ·
Print using the button above or your browser's Print → Save as PDF.
Background graphics are optional; the document is designed to remain
readable without them.