# American Express solution architect interview prep: cross-platform projects

## 1. The whiteboard method: 10 steps in 25 minutes

1. **Clarify the journey:** Who is the user? What action do they take? What does success look like to them?
2. **Name the business invariant:** For money movement, define what must never happen, such as an unintended duplicate
   submission.
3. **Bound the system:** Draw channels, domain services, systems of record, external rails or partners, and operations.
4. **State assumptions:** Traffic, peak load, geographic scope, availability target, latency budget, retention, and data
   classification. Ask for missing numbers rather than inventing them.
5. **Choose ownership:** Identify the single owner of each state transition and the source of truth for each data field.
6. **Define contracts:** Request/response schema, versioning, idempotency key, authentication and authorization,
   timeouts, error codes, and events.
7. **Walk the happy path:** Trace one request from channel to final confirmed outcome.
8. **Walk failure paths:** Duplicate request, timeout after submission, delayed partner response, downstream outage,
   stale read, and partial rollout.
9. **Prove operability:** Correlation IDs, metrics, tracing, alerts, reconciliation, runbooks, recovery objectives, and
   audit trail.
10. **Deliver incrementally:** Contract tests, test environment, controlled launch, rollback, and success measures.

**Say your tradeoff aloud.** For example: “I would keep payment orchestration server-side so channels share the same
state machine; I would still allow channel-specific presentation and accessibility behavior.”
