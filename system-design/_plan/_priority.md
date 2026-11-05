I recommend 24 focused designs across 8 modules, with three per module. We
should not give all 24 equal attention.

The ranking below is based on architectural coverage and relevance to a
financial-services Solution Architect role. It is not a prediction of American
Express interview questions.

## 1. Module priorities and selected designs

P1 = highest priority. Within each module, study the three examples in the order
shown.

| Module priority | Module                                 | Three selected examples, in priority order                                                                                                                                                   |
|-----------------|----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| P1              | Architecture fundamentals              | 1. Transaction API — requirements, NFRs, sizing, interfaces  2. Transaction history database — SQL vs. NoSQL, indexes, consistency  3. Async processing API — sync vs. async, queues, events |
| P2              | Payments and financial systems         | 1. Card payment authorization — latency, idempotency, failures  2. Double-entry ledger — ACID, correctness, concurrency  3. Real-time fraud detection — streaming, rules, scoring            |
| P3              | Distributed transactions and workflows | 1. E-commerce checkout — Saga, distributed transactions  2. Transactional outbox — reliable event publishing  3. Ticket booking — locking, race conditions                                   |
| P4              | Security and enterprise architecture   | 1. Legacy/mainframe modernization — Strangler pattern, integration  2. B2B partner API — contracts, security, resiliency  3. Enterprise SSO — OAuth/OIDC, IAM                                |
| P5              | Scalability, cloud and reliability     | 1. Multi-region transactional system — consistency, replication, failover  2. Disaster recovery — RPO, RTO, backup strategies  3. Circuit breaker and fallback — cascading failures          |
| P6              | General distributed systems            | 1. Distributed rate limiter — Redis, atomicity, algorithms  2. Notification platform — queues, retries, delivery guarantees  3. Chat system — WebSockets, ordering, presence                 |
| P7              | Data architecture and streaming        | 1. CDC pipeline — database changes, event streaming  2. Real-time analytics — Kafka, stream processing, OLAP  3. Audit trail — immutability, retention, traceability                         |
| P8              | Advanced architectures                 | 1. Online ML inference — model serving, latency, feature freshness  2. Enterprise RAG — retrieval, access control  3. Collaborative editing — OT vs. CRDT                                    |

Module 1 can be covered as three shorter foundational examples. Modules 2–7
deserve more architectural depth.

## 2. Overall priority — what to cover first

If your available time becomes limited, use this global top 12 ranking,
regardless of module order.

| Global rank | Design                            | Why it deserves priority                                |
|-------------|-----------------------------------|---------------------------------------------------------|
| 1           | Card payment authorization        | Combines correctness, latency, resilience, and security |
| 2           | Double-entry ledger               | Financial correctness and database transactions         |
| 3           | E-commerce checkout               | Saga, distributed consistency, failure recovery         |
| 4           | Multi-region transactional system | Reliability, replication, failover trade-offs           |
| 5           | Legacy/mainframe modernization    | Enterprise-level architecture decisions                 |
| 6           | Real-time fraud detection         | Low-latency streaming and scoring                       |
| 7           | Transactional outbox              | Reliable communication between DB and events            |
| 8           | Distributed rate limiter          | Concurrency and distributed coordination                |
| 9           | B2B partner API                   | External integration, API design, security              |
| 10          | CDC pipeline                      | Data architecture and eventual consistency              |
| 11          | Disaster recovery                 | RPO/RTO and operational resilience                      |
| 12          | Ticket booking                    | Race conditions and locking strategies                  |

If you can cover only six full designs, do ranks 1–6. If you can cover twelve,
complete the table. The remaining twelve broaden coverage after that.

## 3. How deep to study each

**Global ranks 1–6** [Deep]

Complete design, data model, ASCII diagram, component choices, rejected
alternatives, consistency, failures, scaling, security, and operations.

**Global ranks 7–12** [Focused]

Requirements, architecture, core decisions, trade-offs, and important failure
cases.

**Remaining 12** [Pattern coverage]

Understand the unique architectural problem, why the solution works, and how it
differs from designs already covered.

## 4. Two important adjustments

**First, don't skip architecture fundamentals**, even though the global ranking
starts with payments. We need working knowledge of requirements, SQL/NoSQL,
consistency, caching, API contracts, messaging, and failure handling. We will
introduce these briefly inside the first designs instead of spending a whole
section on theory.

**Second, security must be present in every relevant design**, not isolated in
the security module. For payments, that means tokenization, encryption,
auditability, access control, and PCI boundaries. For cloud architecture, it
means identity, networking, secrets, and least privilege.

## Recommended execution sequence

1. Architecture fundamentals (short primer)
2. Payment authorization and financial ledger
3. Distributed transactions and event reliability
4. Fraud detection and streaming
5. Enterprise integration and modernization
6. Multi-region reliability and disaster recovery
7. Remaining general-purpose distributed patterns
8. Advanced architecture, only if time permits

This gives you both breadth and sufficient depth without spending effort on
repetitive designs.

I recommend beginning with Card Payment Authorization, covering the essential
fundamentals as they appear. It offers the best starting point for the
highest-priority concepts.

01-card-payment-authorization
02-double-entry-ledger
03-e-commerce-checkout
04-multi-region-transactional-system
05-legacy_mainframe-modernization
06-real-time-fraud-detection
07-transactional-outbox
08-distributed-rate-limiter
09-b2b-partner-API
10-cdc-pipeline
11-disaster-recovery
12-ticket booking