# Data Architecture and Database Selection

**Core learning guide for Solution Architect interviews**

This guide explains how to reason from business facts and data access patterns to a data design. It builds on
[Requirements, Quality Attributes, and Capacity](02_Requirements_Quality_Attributes_and_Capacity.md) and
[Distributed Application Design](01_Distributed_Application_Design_for_Solution_Architect_Interviews.md).

## Learning outcomes

- Identify authoritative data ownership, invariants, and lifecycle requirements.
- Compare relational, document, key-value, and analytical storage by workload rather than popularity.
- Explain transaction boundaries, consistency choices, and scaling tradeoffs.
- Describe migration and recovery as part of the architecture, not as later cleanup.

## 1. Start with business facts and access patterns

Ask which facts the business must preserve, who is allowed to change them, and how the system reads and writes them.
Then characterize volume, query shape, consistency, retention, recovery, and sensitivity.

```text
Business fact -> owner -> write rules -> read patterns -> lifecycle -> storage choice
```

For an order, possible facts include order state, line items, payment status, and shipment status. They may have
different owners and change at different times. Putting all related facts in one database does not make one component
the legitimate owner of all of them.

**Invariant:**

> A condition that must remain true, such as “an order cannot be charged twice” or “a transfer must debit and credit
> the same amount.”

An invariant helps decide whether an operation needs an atomic transaction, a workflow with explicit intermediate
states, or eventual reconciliation.

## 2. Choose storage by workload and failure needs

| Storage shape         | Often fits                                                       | Important questions                                                     |
|-----------------------|------------------------------------------------------------------|-------------------------------------------------------------------------|
| Relational            | Related entities, constraints, joins, and multi-row transactions | Do the schema and transaction boundaries match the business invariants? |
| Document              | Data commonly read and changed as a cohesive aggregate           | Which fields are duplicated, and how are cross-document rules enforced? |
| Key-value             | Lookup by a known key with predictable low-latency access        | How are secondary queries, expiration, and hot keys handled?            |
| Analytical / columnar | Large scans and aggregation over historical or event data        | How fresh must results be, and how is analytical data governed?         |

These are workload tendencies, not rigid product categories. Compare the actual query and write patterns, consistency
needs, operational skills, backup and restore behavior, and total cost. A familiar database with suitable guarantees
can be a better choice than a fashionable new service.

**PostgreSQL or a document database?**

> PostgreSQL is a strong candidate when relationships, joins, constraints, and transactional updates are central to
> the workload. A document database can fit when an aggregate is commonly read and changed as a cohesive document and
> its access patterns are understood. Modern products can support overlapping features; compare the specific
> transaction, query, indexing, scaling, and operational requirements instead of assuming one option cannot do
> something.

**ACID transactions:**

> Atomicity, consistency, isolation, and durability describe properties of database transactions. Confirm the
> guarantees and isolation behavior of the selected product and transaction; do not assume every multi-step workflow
> can be made atomic across independent systems.

Isolation level determines how concurrent transactions can observe one another's changes. Stronger isolation may
reduce anomalies but increase contention or retries. Explain the business invariant first, then select and test the
transaction behavior that preserves it.

**CAP theorem:**

> During a network partition, a distributed data system must make a tradeoff between remaining available for requests
> and preserving strong consistency for those requests. This is not a permanent choice of “consistency or
> availability” for an entire product: guarantees can differ by operation, configuration, and failure condition.
> Describe the required behavior during a partition rather than using CAP as a product-selection slogan.

## 3. Scale reads and writes deliberately

Indexes can reduce lookup work but add storage and write cost. Partitioning divides data into manageable portions;
sharding distributes portions across nodes, which introduces routing and rebalancing concerns. Replicas may improve
read capacity or availability, but replication lag can mean a recent write is not immediately visible everywhere.

Caching can lower latency and load, but introduces freshness, invalidation, stampede, and failure questions. State
which data may be stale, for how long, and what happens when the cache is unavailable. Do not add a cache before
identifying a measured bottleneck or a clear latency need.

**Read and write model:**

> Command Query Responsibility Segregation (CQRS) separates operations that change state from those that read it. It
> can help when read and write needs differ, but creates synchronization and operational complexity. It is not a
> default requirement for every application.

## 4. Plan the data lifecycle

For each important dataset, define creation, ownership, retention, deletion, archival, recovery, and access. Include
data classification, lineage, quality, legal or contractual constraints, and migration. A backup is useful only if it
can be restored within the required RTO and RPO; test the restore path.

For migrations, identify the source of truth at each stage. If old and new systems coexist, specify how writes are
handled, how differences are detected, what cutover evidence is required, and how to roll back safely. See
[Enterprise Modernization and Roadmaps](10_Enterprise_Modernization_and_Roadmaps.md).

**Say it professionally:**

> “I would choose the data platform from the invariants, access patterns, recovery targets, and operating constraints.
> I would name the authoritative owner, then validate the expected query and growth profile before committing to a
> scaling strategy.”

## 5. Practice and self-check

For a banking transfer or order scenario, list the facts, owners, reads, writes, and invariants. Choose a primary
storage model and describe one credible alternative. Explain transaction scope, backup and restore, growth pressure,
and what would trigger partitioning or a separate read model.

Check your answer: Did you choose a database because of the workload rather than a label? Are stale reads acceptable?
Can the critical invariant survive retries, failover, and migration?

## References

- [PostgreSQL documentation: transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [AWS Well-Architected Framework: reliability pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Azure Well-Architected Framework: data-related design guidance](https://learn.microsoft.com/en-us/azure/well-architected/)
