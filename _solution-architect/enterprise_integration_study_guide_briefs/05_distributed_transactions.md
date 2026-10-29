# Handoff brief 05 — Distributed transactions

Create a **standalone study guide** titled *Distributed Transactions and Business Consistency*. The audience is a senior/principal Enterprise or Integration Solution Architect in a vendor-neutral interview. Aim for roughly 3,000–4,000 words because this is a P0 topic. Be exact about guarantees and failure windows. Label assumptions and link current primary sources where needed.

**Focus:** Local transaction boundaries; the dual-write problem; Transactional Outbox and publisher recovery; consumer idempotency; deduplication key scope and retention; Saga orchestration versus choreography; compensating actions; timeouts; partial success; eventual consistency; reconciliation; manual intervention; and the limits of “exactly once.”

**Include:**

1. A timeline showing database commit succeeds while event publication fails, then a step-by-step Outbox design and its remaining failure cases.
2. A five-system business process with local transactions, process state, compensations, irreversible side effects, and a human escalation path.
3. A comparison of Saga orchestration and choreography, with criteria for choosing each.
4. A safe billing or order example showing idempotent handling despite message redelivery. Define where keys and outcomes are persisted.
5. Failure-injection questions, model interview answers, a consistency decision table, and a practice exercise with answer key.

Avoid implying compensation perfectly reverses real-world effects. Explain when a business process must pause rather than accept eventual consistency.
