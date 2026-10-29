# Handoff brief 04 — Enterprise messaging

Create a **standalone study guide** titled *Enterprise Messaging: Queues, Topics, and Event Streams*. The audience is a senior/principal Enterprise or Integration Solution Architect preparing for vendor-neutral interviews. Aim for roughly 2,500–3,500 words. Use precise semantics, concrete diagrams, labeled assumptions, and current primary sources for platform-dependent claims.

**Focus:** Durable queues, topics and subscriptions, brokers, retained event logs, consumer groups, partitions, throughput, ordering boundaries, retention, replay, acknowledgements, delivery semantics, duplicates, poison messages, DLQs, backpressure, and consumer concurrency. Explain the operational and cost consequences of each choice.

**Include:**

1. A decision matrix for a traditional queue versus a Kafka-like event stream, including command/work distribution, multiple independent consumers, replay, scale, ordering, retention, expertise, and total cost.
2. A message lifecycle diagram from publish to acknowledgement, retry, DLQ, inspection, and controlled replay.
3. Worked scenarios: distribute fulfillment work; notify CRM and analytics of an order event; recover from a consumer outage; handle a poison message without blocking healthy work.
4. A precise explanation of at-most-once, at-least-once, and any exactly-once scope. State why broker guarantees alone do not ensure a single external billing action.
5. Interview questions, model answers, diagnostic metrics, common mistakes, and an exercise with answer key.

Do not turn this into a vendor configuration manual or a full Saga guide. Keep the focus on messaging architecture and operation.
