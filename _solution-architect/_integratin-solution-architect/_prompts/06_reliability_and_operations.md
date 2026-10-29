# Handoff brief 06 — Reliability and operations

Create a **standalone study guide** titled *Operating Reliable Enterprise Integrations*. The audience is a
senior/principal Enterprise or Integration Solution Architect in vendor-neutral interviews. Aim for roughly 2,500–3,500
words. Label assumed SLOs and workloads rather than presenting them as facts; use current primary sources for changing
claims.

**Focus:** Timeouts; bounded retries with exponential backoff and jitter; circuit breakers; bulkheads; throttling;
buffering and backlog capacity; backpressure; DLQs and poison messages; partial success; stale work; recovery and
controlled replay; reconciliation; monitoring, tracing, correlation IDs, audit trails, incident ownership, and business
status visibility.

**Include:**

1. A six-hour ERP outage drill: what can continue, what must pause, backlog sizing method, retry posture,
   customer/business impact, recovery sequence, and reconciliation.
2. An end-to-end order status model that lets support staff follow an order across systems and identify stuck or
   inconsistent states.
3. An operational runbook outline: alert, triage, quarantine, replay, reconcile, escalate, and close.
4. Metrics and alerts for queue depth, lag, age of oldest work, failure rate, latency, throughput, and business
   discrepancies; explain why each matters.
5. Five interviewer challenges with strong answers, anti-patterns, and a failure tabletop exercise with answer key.

Make clear that adding a queue does not itself solve recovery. Keep deep Outbox/Saga mechanics in the distributed
transactions guide.
