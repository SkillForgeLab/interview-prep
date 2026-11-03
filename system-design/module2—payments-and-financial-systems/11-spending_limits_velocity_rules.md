# Design 11 — Spending Limits and Transaction Velocity Rules System

*10-minute system design interview answer · American Express Solution Architect Preparation*

> **Scope:** Illustrative architecture, not an assertion about American Express's internal systems. Hard financial limits require strong enforcement; fraud-velocity signals may tolerate delayed aggregation.

## 1. Problem & Requirements

Design a real-time system that checks whether a credit card transaction violates spending or velocity limits **before authorization**.

**Functional requirements**

- **Amount limits:** Per-transaction, daily, weekly, monthly, and rolling-period spending limits.
- **Velocity limits:** Transaction counts, such as a maximum of five purchases in a rolling hour.
- **Scoped limits:** Account, card, merchant, merchant category, geography, and channel.
- **Shared limits:** Multiple cards drawing from a common account allowance.
- **Policy management:** Customer restrictions, mandatory issuer rules, temporary changes, overrides, effective dates, and expiry.
- **Lifecycle:** Reservations, reversals, refunds, hold expiry, resets, and audit history.

**Non-functional requirements**

| Requirement | Design implication |
|---|---|
| Low latency | Evaluate limits in the synchronous authorization path. |
| Strong consistency | Hard limits cannot be exceeded by concurrent approvals. |
| High availability | Redundant services and controlled failover. |
| Financial correctness | No duplicate reservations or accidental releases. |
| Scalability | Partition counters around the owner of each limit. |
| Auditability | Record policy versions, decisions, overrides, and actors. |

**Key distinction:** A **hard spending limit** requires authoritative enforcement. A **fraud-velocity signal** may tolerate a short aggregation delay. Customer-configured limits may tighten but must not silently override mandatory issuer controls. Exceptions require authorized, auditable policy changes.

## 2. High-Level Architecture

```text
                 Card Network
                      |
                      v
             Gateway / Adapter
                      |
                      v
             Authorization Service
                      |
                      v
            Limit Evaluation Service
                 /          \
                v            v
          Rules/Policy    Config Store
             Engine       (SQL)
                |
                v
       Atomic Reservation Operation
                |
                v
      Authoritative Transactional DB
      +-----------------------------+
      | Authorization + Credit      |
      | Limit Counters              |
      | Reservations + Idempotency  |
      | Policy Version + Outbox     |
      +-----------------------------+
             |              |
             v              v
       Allow / Deny     Outbox Publisher
             |              |
             v              v
       Authorization     Event Broker
          Service            |
                       Stream Processor
                             |
                      +------+------+
                      |             |
                      v             v
                 Redis /        Audit &
                 Analytics      Monitoring
                 Counters
```

**Responsibilities and why they exist**

- **Limit Evaluation Service:** Find and evaluate every applicable limit before approval.
- **Rules/Policy Engine:** Apply issuer, customer, scoped, and temporary policies consistently.
- **Configuration Store:** Persist versioned rules, priorities, approvals, and effective dates.
- **Real-Time Counter Store:** Track hard-limit usage in authoritative transactional records. Redis can separately serve non-authoritative signals.
- **Transactional DB:** Atomically commit reservations, authorization decision, and deduplication state.
- **Event Broker + Stream Processor:** Publish committed events for analytics, fraud features, and reporting without delaying checkout.
- **Audit and Monitoring:** Support investigations, exception tracking, and reconciliation.

**Critical choice:** For this baseline, authorization, credit reservations, and **all applicable hard-limit reservations commit in one coordinated transaction**. Logical services need not be separate microservices. Separate independently committing databases would introduce a dual-write consistency risk.

## 3. Key Design Decisions — With Reasons

### A. Storage, consistency, and coordination

| Decision | Choice | Why / main alternative or trade-off |
|---|---|---|
| Limit configurations | Versioned SQL records | Transactional policy changes and auditability. Consistent NoSQL storage could also work. |
| Hard counters | Transactional SQL store | Atomic multi-counter updates and durability. Redis-only counters require much more care around durable commits and failover. |
| Soft fraud signals | Redis / stream-derived counters | Fast reads and high throughput; some staleness is permitted by policy. |
| Consistency | Strong for hard limits | Two approvals must not consume the same remaining allowance. Eventual consistency is adequate only for defined soft signals. |
| Concurrency | Short transactions + atomic conditional updates/row locks | Direct DB coordination is simpler than separate distributed locks. Optimistic version checks are viable under lower contention. |
| Shared cards | Account-level counter ownership | All cards sharing an underlying credit account consume the same limit. |
| Policy precedence | Mandatory issuer rules cannot be weakened by customer settings | Explicit issuer-approved exceptions must be versioned and audited. |

**Why not Redis as the final authority for hard limits?** Redis offers atomic operations, but atomicity inside Redis alone does not atomically update a separate authorization database. Redis failover and persistence choices also require durability analysis. A Redis cache can accelerate non-authoritative lookups, but stale or lost cache entries must not create financial approvals beyond hard limits.

### B. Fixed window vs. sliding window vs. token bucket

| Algorithm | Meaning | Preferred use |
|---|---|---|
| Fixed window | Count within defined calendar intervals | Daily, weekly, monthly limits. |
| Exact sliding window | Check eligible events in the last *N* seconds/minutes | Hard rolling count or amount limits. |
| Bucketed sliding window | Sum discrete time buckets | Scalable approximate velocity signals; bucket boundaries can introduce error. |
| Token bucket | Consume tokens that refill over time | Rate control and bursts, not inherently the same as calendar spending limits. |

**Example:** At 10:30, a strict five-transactions-per-hour policy must count eligible transactions since 9:30. A fixed hour would allow five at 9:59 and five more at 10:01, violating the intended rolling-hour rule.

**Choice:** Exact sliding-window history for strict rolling limits; time buckets or token buckets only when their semantics and accuracy are suitable.

### C. Atomic enforcement across several limits

A single $100 transaction may count against a daily spending cap, monthly spending cap, merchant-category cap, and hourly count cap. **All must pass together**.

```text
BEGIN TRANSACTION

  Lock the relevant account / counter domain
  Read the effective policy version and current usage
  Evaluate every applicable hard limit

  IF any required limit fails:
      Record declined decision (no reservation)
  ELSE:
      Reserve usage across ALL applicable limits
      Reserve available credit
      Save authorization, idempotency, and outbox event

COMMIT
```

If the monthly check fails after the daily check passes, **no partial reservation** may remain.

**Alternatives:** Optimistic concurrency with row versions can reduce locking under low contention but creates retry conflicts; distributed locks add a separate coordination system and cannot substitute for an atomic final database commit.

### D. Scope and ownership

| Limit | Logical key / owner |
|---|---|
| Shared account spending | Account ID |
| Individual card spending | Account ID + Card ID |
| Merchant-specific account spending | Account ID + Merchant ID |
| Category spending | Account ID + Category |
| Geographic spending | Account ID + Region/Country |
| Channel spending | Account ID + Channel |

A single purchase may affect multiple keys. Account-based partitioning keeps most account-scoped keys in the same transactional boundary. **Trade-off:** A truly *global merchant-wide* cap spanning many independent accounts requires separate cross-partition coordination.

### E. Reservations, policies, and events

- **Reservation vs. posted spending:** Approved transactions consume reserved capacity, if the policy is defined to count authorizations. When clearing posts the charge, move eligible reserved usage to posted usage; do not double count it.
- **Reversal/expiry/refund:** Release or adjust usage under explicit policy semantics. An anti-fraud *attempt-count* rule may still count an attempt after reversal.
- **Policy versions:** Apply effective-dated rules and record the version used for every decision; overrides require actor, approval, reason, and expiry.
- **Kafka/event broker:** Use after the authoritative transaction for fraud enrichment, monitoring, and reporting. It should not be the sole hard-limit enforcement mechanism.
- **Transactional outbox:** Write outbox events in the same transaction; publish later. Consumers deduplicate because delivery can repeat.

## 4. End-to-End Request Flow

```text
1. Receive authorization request
          |
2. Resolve card -> underlying credit account
          |
3. Retrieve effective policy version
          |
4. Identify all applicable limit scopes
          |
5. Read authoritative current usage
          |
6. Atomically evaluate and reserve all limits
          |
7. Commit authorization, idempotency, and audit/outbox
          |
8. Return ALLOW / DENY to Authorization Service
          |
9. Publish downstream events asynchronously
          |
10. Reconcile/release on clearing, reversal, expiry, adjustment
```

**Four critical cases**

1. **Concurrent transactions:** Remaining daily limit is $100. Two $80 requests arrive simultaneously. Serialized or atomic enforcement allows one $80 reservation and denies the other, leaving $20.
2. **Duplicate authorization:** A $50 request committed, but its response was lost. The retry uses a stable network-derived identity and returns the previous decision; it cannot increment counters again.
3. **Multiple limits:** $100 fits the daily limit but breaches the monthly limit. Deny the request without reserving any applicable counter.
4. **Reversal:** A $100 hold is validly reversed. In one transaction, release the eligible reservation, update the authorization lifecycle, and record the reversal. Whether count-based limits regain capacity is policy-specific.

## 5. Data Model & Correctness

| Entity | Main fields |
|---|---|
| `SpendingLimit` | limitId, scope, currency, maxAmount/maxCount, windowType |
| `LimitPolicy` | policyId, issuer/customer owner, precedence, status |
| `PolicyVersion` | version, effectiveFrom, effectiveTo, approvedBy |
| `AccountCard` | accountId, cardId, status, association dates |
| `LimitCounter` | scopeKey, policyVersion, windowId, used, reserved |
| `AuthorizationReservation` | authorizationId, limitId, reservedAmount, lifecycleStatus |
| `TransactionEvent` | eventId, authorizationId, eventType, timestamp, sequence |
| `IdempotencyRecord` | requestIdentity, requestFingerprint, decision/result |
| `AuditRecord` | actor, action, old/new policy, reason, timestamp |

**Sources of truth:** Versioned authoritative SQL for policy configuration; transactional counters plus durable reservation/event history for hard-limit usage; authorization store for approval status. Redis/stream projections may serve approximate fraud velocity, not replace the authoritative record.

### Rolling-window correctness

For a strict rolling-hour **transaction-count** policy:

```text
usage(t) = number of eligible events in (t - 3600 seconds, t]
```

Calculate usage while coordinating with concurrent reservations, and atomically add the new eligible event if within the limit. Exact amount windows need timestamped amounts, not just a single total. Event-order/version checks prevent delayed updates from overwriting newer state.

### Time zones and reset

- Store timestamps in UTC and retain each policy's IANA time zone.
- Compute calendar day/week/month boundaries in the policy time zone; DST changes can produce 23- or 25-hour local days.
- A rolling hour always means the preceding 3,600 seconds, not the current wall-clock hour.
- Use versioned window IDs or new buckets instead of relying on a reset job to erase usage at precisely midnight.
- Keep durable history for reconstruction and reconciliation; cache TTL expiry is not proof that a window was correctly reset.

### Changes, overrides, and reconciliation

Define what happens if a temporary or customer-controlled limit drops below already committed usage. A safe default is to preserve existing valid reservations and reject new spending until usage is within the new policy, unless authorized rules explicitly differ.

Periodically reconstruct expected counters from authoritative authorization, clearing, reversal, expiry, refund, and adjustment events. Investigate mismatches and repair them through audited operations. Balanced or internally consistent counters can still be wrong if source events were missing; reconciliation checks that risk.

## 6. Failure Handling, Scalability & Security

| Failure | Design response | Why |
|---|---|---|
| Hard counter SQL DB unavailable | No ordinary hard-limit approval; use separately authorized contingency only | Cannot safely verify and reserve capacity. |
| Redis unavailable | Degrade soft features or use permitted authoritative fallback | Redis must not determine hard-limit correctness. |
| Duplicate limit evaluation | Durable idempotency + unique constraint | No double reservation. |
| Concurrent requests | Atomic checks and reservations | No over-limit approval. |
| Authorization commits while counter update fails | Avoid independent commits by sharing one transaction | Prevent authorization/counter divergence. |
| Partial failure across multiple checks | Roll back the whole transaction | No partial capacity usage. |
| Stale limit configuration | Check authoritative effective version or fail safely | Prevent outdated rules from authorizing transactions. |
| Lost/delayed event | Outbox replay, idempotent consumers, reconciliation | Restore downstream views. |
| Counter reset job fails | Derive current windows from effective time/window ID | Cleanup jobs are not correctness dependencies. |
| Hot account/high contention | Short transactions, suitable indexes, targeted throttling | Preserve p99 latency without weakening consistency. |
| Regional failover | One writer per account, fencing and tested replication | Prevent split-brain approvals. |
| Traffic spikes | Autoscale stateless workers, backpressure, bounded retries | Avoid resource exhaustion and retry storms. |

**Scaling:** Shard account-scoped hard counters and reservations by underlying `account_id` once a single DB is insufficient. For hot accounts, optimize the critical section; do not blindly distribute a single hard counter across independent writers. An account's multiple cards must route to the same authoritative owner. If using Redis Cluster for soft counters, multi-key atomic operations must respect hash-slot constraints.

**Recovery:** Maintain bounded retries with jitter for retryable operations, dead-letter queues for failed asynchronous consumers, and reconciliation to recover counters after missed or out-of-order downstream events. Define RPO/RTO, durable acknowledgement semantics, and tested failover procedures.

**Fail-open vs. fail-closed:** Mandatory issuer hard limits must not silently fail open. Appropriate degraded behavior is set by a risk-approved policy with clear boundaries and auditability. Some *soft* risk features can be omitted or degraded with corresponding risk controls.

**Security:** Authenticate network/service callers, authorize access to the correct card/account and limit scopes, encrypt data in transit and at rest, minimize payment-card data in counters and logs, strictly control limit overrides, and retain tamper-evident decision/audit records. PCI DSS controls apply to systems that store, process, or transmit payment account data, based on their actual scope.

## 7. Key Points to Remember

1. **Atomic enforcement prevents race conditions.** Evaluate and reserve every applicable hard limit in one coordinated transaction with the authorization.
2. **Hard limits need strong consistency.** Derived Redis and event-stream counters are suitable for soft signals, not as stale financial authority.
3. **Idempotency governs the whole lifecycle.** Retries must not reserve twice; clearing, reversals, expiry, and refunds follow explicit counter policies.
4. **Choose the right window algorithm.** Fixed windows for calendar limits; exact sliding windows for strict rolling rules; bucketed approximations/token buckets only when their semantics fit.
5. **Scale and recover without losing correctness.** Partition by account, avoid split-brain writers, monitor contention, and reconcile authoritative events against counters.

## 8. Interview Closing Summary

> I would implement spending limits as a synchronous component of credit card authorization. A versioned policy engine determines applicable issuer and customer rules, while an authoritative transactional store maintains hard-limit usage. Each authorization atomically checks and reserves all applicable limits, using account-level concurrency control and durable idempotency. Exact sliding windows handle strict velocity limits, while Redis and streaming provide fast, eventually consistent fraud signals. I would partition account-scoped counters by credit account, use a transactional outbox for downstream reporting, and support reversals, policy changes, and reconciliation. For resilience, I would use redundant services, controlled single-writer failover, and explicit degradation policies that never silently bypass mandatory limits.

---

*Reference topics for further verification (official primary documentation): PCI Security Standards Council — PCI DSS document library; PostgreSQL documentation — explicit locking and transaction isolation; AWS Prescriptive Guidance — transactional outbox pattern; Redis documentation — persistence, Lua, and Redis Cluster constraints. Network-specific reversal and limit semantics must be checked against the applicable network agreement.*
