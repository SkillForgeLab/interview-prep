# Messaging and Event-Driven Architecture

**Core learning guide for Solution Architect interviews**

This guide helps decide when to use a queue, publish-subscribe, or event stream, and what must be designed around
delivery and recovery. It builds
on [Distributed Application Design](01_Distributed_Application_Design_for_Solution_Architect_Interviews.md)
and [Data Architecture](03_Data_Architecture_and_Database_Selection.md).

## Learning outcomes

- Choose messaging based on the business interaction and delivery needs.
- Explain queues, publish-subscribe, and retained streams without treating them as interchangeable.
- Design for duplicate delivery, ordering, backpressure, failure recovery, and message evolution.
- Describe a reliable handoff from a database change to published work.

## 1. Choose the interaction before the broker

Use synchronous requests when the caller needs an immediate result. Use asynchronous messaging when work can finish
later, the producer and consumer should progress independently, or a buffer helps absorb uneven load.

```text
Request/response: caller waits for a decision
Queue:            one work item is generally processed by one competing consumer
Publish/subscribe: multiple subscribers can receive an event
Stream:           ordered records are retained for independent consumption or replay
```

Products can provide more than one of these models. Compare delivery, retention, ordering, replay, throughput,
operational effort, and failure behavior rather than choosing by product name alone.

**Queue or event stream?**

> A managed work queue is often a fit when consumers need to claim tasks, acknowledge completion, and retry failed
> work. A retained stream is useful when independent consumer groups need to process an ordered log and may need to
> replay retained records from a position. A publish-subscribe broker fits distributing notifications to multiple
> subscribers. Products overlap, so verify their actual retention, delivery, ordering, and replay guarantees.

For example, compare Kafka with a managed queue such as Amazon SQS only after deciding whether the system needs a
retained multi-consumer event log or a managed work-queue lifecycle. Compare operational ownership, throughput,
retention, ordering scope, replay, and cost; neither product is a universal replacement for the other.

## 2. Design delivery as an end-to-end property

Most practical messaging systems can redeliver when a consumer fails before acknowledging work. Design consumers so
reprocessing is safe, commonly by recording a stable message or business-operation identifier with the result.
Idempotency avoids repeating the business effect; deduplication alone is safe only when its state is reliable and
correctly scoped.

“Exactly once” needs a boundary. A broker's delivery guarantee does not automatically make a database update, external
API call, and customer-visible side effect happen exactly once together. State which effects are atomic and how the
rest are made safe or reconciled.

**Ordering:**

> Global ordering can limit throughput and is often unnecessary. Define the scope that must be ordered—such as events
> for one account or order—and select a partitioning key and consumer behavior that preserve that scope.

Add bounded retries with backoff for transient failures. Route repeatedly failing work to a dead-letter or quarantine
path with an owner, alert, diagnosis process, and safe replay procedure. A dead-letter queue without operations and
recovery ownership is only deferred data loss.

## 3. Protect the database-to-message handoff

If an application commits a database update and then separately publishes an event, a crash between those actions can
leave state changed but no message published. The transactional outbox pattern records the business change and an
outgoing event in the same local transaction; a relay publishes the event and marks progress.

```text
Business update + outbox row (one DB transaction)
                  -> relay -> broker -> idempotent consumer
```

The outbox makes the local handoff durable, but does not remove duplicate publication, consumer idempotency, schema
compatibility, or monitoring requirements. Polling, log-based capture, and other relays have different operational
tradeoffs.

When coordinating a multi-step workflow, **orchestration** uses a coordinator to direct steps and track state.
**Choreography** lets participants react to events without one central coordinator. Orchestration makes workflow
progress visible in one place but can concentrate logic; choreography reduces central coordination but can make
causality and recovery harder to understand. Choose based on workflow complexity, ownership, and operational
visibility.

## 4. Manage pressure and change

Watch queue depth, oldest-message age, processing rate, redelivery, and failure rate. If producers outrun consumers,
decide whether to add capacity, reduce work, shed optional load, or slow producers. Unbounded backlog can move the
failure from request time to storage exhaustion or stale business state.

Version message contracts intentionally. Prefer compatible additions when possible; consumers should handle unknown
optional fields safely. Coordinate breaking changes with consumers, and define retention and replay implications
before removing old fields.

**Say it professionally:**

> “I would introduce a broker only where asynchronous processing or decoupling solves a stated need. I would define
> delivery and ordering scope, make side effects safe under redelivery, monitor backlog age, and assign an owner for
> replay and failed-message recovery.”

## 5. Practice and self-check

Design order acceptance and fulfillment. Mark which step requires an immediate answer, where a queue helps, how a
duplicate event is handled, what is ordered, how a database update is reliably published, and who resolves poison
messages. Explain when direct API calls would be simpler.

Check your answer: Does every message have a purpose, owner, contract, retention rule, and failure path? Can work be
replayed without causing a harmful second effect?

## References

- [Azure Architecture Center: asynchronous messaging](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/)
- [Azure Architecture Center: design patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
- [AWS Well-Architected Framework: reliability pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
