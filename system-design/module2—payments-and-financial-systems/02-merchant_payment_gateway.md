# Design 02 — Merchant Payment Gateway System

**Interview format:** 10-minute system design answer  
**Role:** American Express Solution Architect  
**Core focus:** Merchant API security, payment orchestration, idempotency, retry
contracts, provider failures, webhooks, and financial reconciliation.

> **Scope:** Illustrative multi-provider merchant payment gateway. This does not
> describe American Express's internal architecture. Capacity assumptions are
> examples, not production figures.

## 1. Problem & Requirements

Design a **multi-merchant payment gateway** that securely accepts card payments
through APIs, routes them to external payment processors/acquirers, tracks
payment status, and recovers safely when a provider fails or its outcome is
uncertain.

**Functional requirements**

- Register merchants, issue and rotate scoped API credentials, and enforce
  merchant permissions.
- Initiate and authorize payments.
- Capture, cancel/void, and refund payments, including partial operations where
  supported.
- Route transactions to multiple processors or acquirers.
- Track payment and attempt status; expose retrieval APIs.
- Notify merchants using signed webhooks.
- Prevent duplicate charges, captures, and refunds.
- Recover from provider timeouts and failures.
- Reconcile gateway records with processor/acquirer records; retain an audit
  trail.

**Non-functional requirements**

| Requirement           | Design implication                                                                       |
|-----------------------|------------------------------------------------------------------------------------------|
| Low latency           | Keep initial authorization path synchronous and bounded.                                 |
| High availability     | Redundant stateless APIs; controlled state-store failover; safe provider-routing policy. |
| Financial correctness | Durable idempotency, persisted attempts, guarded state transitions, reconciliation.      |
| Security              | TLS, scoped credentials, tokenization, card-data isolation, PCI controls.                |
| Scalability           | Horizontal API scaling, merchant isolation, careful database partitioning.               |
| Auditability          | Immutable or tamper-evident state transition and operation history.                      |

**Assumption:** Two or more providers and an illustrative peak of 10,000
requests/second. Real provider timeouts, idempotency retention, and processing
limits come from provider contracts.

### Responsibility boundaries

| Actor                       | Responsibility                                                                                         |
|-----------------------------|--------------------------------------------------------------------------------------------------------|
| Merchant gateway            | Merchant integration, authentication, payment orchestration, routing, state, webhooks, reconciliation. |
| Processor/acquirer          | Acquiring-side processing and connections to card networks.                                            |
| Issuer                      | Decides whether a card transaction is authorized.                                                      |
| Clearing/settlement systems | Handle clearing and final settlement obligations.                                                      |

The gateway is **not automatically the issuer or the authoritative settlement
ledger**.

## 2. High-Level Architecture

```text
                  Merchant Application
                          |
                          v
                     API Gateway
                          |
              +-----------+-----------+
              |                       |
              v                       v
         Auth / RBAC             Rate Limiter
              |                       |
              +-----------+-----------+
                          |
                          v
                   Payment Service
                     /         \
                    v           v
              Payment DB   Idempotency Store
                    |
                    v
             Orchestration / Router
                    |
            +-------+-------+
            |               |
            v               v
       Adapter A         Adapter B
            |               |
            v               v
       Processor A       Processor B
            |               |
            +-------+-------+
                    |
                    v
           Networks / Issuer Systems

       Payment DB -- Transactional Outbox
                           |
                           v
                       Event Broker
                    /      |        \
                   v       v         v
              Webhooks  Reconcile  Audit /
               Service   Service  Monitoring
                          |
                          v
                   Provider Reports
```

**Why these components?**

| Component                    | Responsibility and reason                                                                                                         |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| API Gateway                  | TLS termination, routing, input validation, request correlation.                                                                  |
| Authentication/authorization | Verify merchant identity and permitted payment operations.                                                                        |
| Rate limiter                 | Throttle abuse and protect tenants from each other's traffic.                                                                     |
| Payment Service              | Own intents, operation lifecycles, and payment-state transitions.                                                                 |
| Payment DB and idempotency   | Authoritative, transactionally consistent gateway state. A cache may accelerate lookups but cannot be the only correctness guard. |
| Orchestrator/router          | Select eligible providers, coordinate attempts and recovery.                                                                      |
| Provider adapters            | Convert canonical requests and responses to provider-specific APIs/protocols.                                                     |
| Event broker                 | Decouple noncritical downstream work.                                                                                             |
| Webhook worker               | Signed, retryable merchant notifications.                                                                                         |
| Reconciliation               | Compare gateway outcomes with provider records and settlement evidence.                                                           |
| Audit/monitoring             | Investigations, tracing, operational alerts, security history.                                                                    |

**Key design principle:** Maintain a canonical internal payment model; keep
provider-specific message formats, statuses, and retry semantics inside
adapters.

## 3. Key Design Decisions — Choice, Why, Trade-off

| Decision                 | Choice                                                                      | Why / trade-off                                                                                                             |
|--------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| Merchant API             | REST/HTTPS                                                                  | Easy merchant integration; network-specific protocols remain behind provider adapters.                                      |
| Merchant authentication  | Scoped API keys; OAuth 2.0 client credentials or mTLS when needed           | API keys are simple; OAuth adds token/scoping infrastructure; mTLS increases identity assurance and certificate operations. |
| Request integrity        | HMAC signature with timestamp and nonce when needed                         | Mitigates tampering and replay; requires key management and canonicalization rules.                                         |
| Database                 | SQL/ACID as baseline                                                        | State transitions, unique constraints, and local atomic writes; partition only when justified.                              |
| Idempotency              | Unique `(merchant_id, operation, idempotency_key)` plus request fingerprint | Prevents duplicate logical financial operations.                                                                            |
| Payment initiation       | Synchronous attempt + asynchronous updates                                  | Fast initial result without falsely claiming unknown outcomes are final.                                                    |
| Provider integration     | Adapter pattern                                                             | Isolates provider differences and supports future providers.                                                                |
| Provider routing         | Eligibility/rule-based first; dynamic health/cost/performance later         | Simpler initial behavior; dynamic routing needs reliable metrics and safeguards.                                            |
| Retries                  | Bounded exponential backoff + jitter only when safe                         | Reduces transient failure impact; an unsafe retry can create a duplicate charge.                                            |
| Circuit breaker          | Stop sending new attempts to failing provider                               | Limits cascading failures; does not resolve in-flight attempts.                                                             |
| Distributed transactions | ACID locally; Saga-style coordination externally                            | Cannot hold an ACID transaction across independent payment providers.                                                       |
| Events                   | Transactional outbox + durable broker                                       | Avoids database/broker dual-write gaps; consumers still deduplicate.                                                        |
| Webhooks                 | Signed, at-least-once                                                       | Merchants must deduplicate and tolerate delays/out-of-order delivery.                                                       |
| Security                 | Tokenization, scoped access, PCI boundary                                   | Reduces exposure; tokenization does not automatically remove all PCI obligations.                                           |
| Consistency              | Strong for payment state; eventual for webhooks and analytics               | Money-affecting transitions must be correct, while downstream views may lag.                                                |
| Multi-region             | Multi-region stateless APIs, controlled single-writer ownership per payment | Availability without concurrent conflicting attempts; failover is more complex.                                             |
| Tenant isolation         | Per-merchant rate limits, quotas, capacity protection                       | Stops one merchant from overwhelming others.                                                                                |
| Reconciliation           | Match provider transactions and reports to gateway records                  | API responses/webhooks alone do not prove eventual settlement.                                                              |

### Merchant onboarding and API security

Onboard the merchant, verify the allowed capabilities, and issue scoped
credentials. Store credential identifiers, permission scopes, status,
rotation/expiry metadata, and secret or public-key references. Keep sensitive
secrets in a dedicated secrets system.

- **API key:** Simple server-to-server use, but often long-lived unless rotated.
- **OAuth 2.0 client credentials:** Scoped, short-lived access tokens; more
  moving parts.
- **mTLS:** Certificate-based peer authentication; stronger B2B control with
  certificate lifecycle cost.
- **Request signing:** Canonicalize method, path, timestamp, nonce, and body
  hash, then verify an HMAC/signature. Reject old timestamps and replayed nonces
  within the accepted window.

### Idempotency and retry contract

Example:

```http
POST /v1/payments
Authorization: Bearer <credential>
Idempotency-Key: order-784-payment-1
```

- Same key **and same payload**: return the existing payment ID/current recorded
  result.
- Same key but **different payload**: return an idempotency conflict.
- Existing request still processing: return a defined pending/retry response.
- New key: allow a new logical operation after normal business validation.

There are **two idempotency boundaries**: merchant → gateway and gateway →
provider. Persist a stable provider-attempt reference and use provider-supported
idempotency keys. Each capture, refund, and void also requires its own operation
identity. Provider key retention and exact semantics are provider-specific.

### Provider routing and fallback

Route using merchant eligibility, geography, currency, payment-method support,
processor health, capabilities, cost, and latency. Prefer simple rule-based
routing initially. Add dynamic routing when measurement justifies it.

**Never reroute an in-flight or timed-out attempt solely because it was slow.**
First confirm whether the original attempt had a financial effect, or use a
documented recovery protocol that makes rerouting safe.

### ACID vs. Saga

Use one local ACID transaction for payment-intent state, attempt metadata,
idempotency, and outbox records. Treat external authorization, capture, and
refund as independently committed operations coordinated by an
orchestration/Saga workflow. A compensation is a new financial operation, not an
instant global rollback.

## 4. End-to-End Request Flow

```text
1. Merchant sends POST /payments
             |
2. Authenticate and authorize merchant
             |
3. Validate input and rate limits
             |
4. Check scoped idempotency key + fingerprint
             |
5. Persist PaymentIntent and PaymentAttempt
             |
6. Select eligible processor/acquirer
             |
7. Adapter sends provider-specific request
             |
8. Receive provider result or timeout
             |
9. Persist resulting state transition
             |
10. Return APPROVED / DECLINED / PENDING
             |
11. Handle later capture, void, refund, status
             |
12. Commit outbox, publish event, send webhooks
             |
13. Reconcile provider records and reports
```

**Important:** Persist attempt ID, provider selection, provider idempotency
key/reference, and `PROCESSING` state *before* invoking the external provider. A
recovery worker must know which provider operation may already have executed.

### Simplified payment state machine

```text
CREATED
   |
   v
PROCESSING ----------------> DECLINED / FAILED
   |
   +-----------------------> OUTCOME_UNKNOWN
   |                                |
   |                         Resolve original
   |                         provider attempt
   v
AUTHORIZED
   +------> VOID_PENDING --> VOIDED
   |
   v
CAPTURE_PENDING
   +------> CAPTURE_FAILED (reconcile first)
   |
   v
PARTIALLY_CAPTURED / CAPTURED
   |
   v
SETTLEMENT_PENDING --> SETTLED

Refunds are separate operations:
REFUND_PENDING --> REFUNDED / REFUND_FAILED / REFUND_UNKNOWN
```

Provider state transitions differ. The gateway should maintain canonical
statuses without erasing critical provider-specific information.

### Failure scenarios

| Scenario                                                     | Handling                                                                                           | Reason                                              |
|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| Duplicate merchant requests                                  | Reuse recorded intent/result by idempotency key                                                    | Prevent duplicate charges.                          |
| Provider timeout after successful authorization              | Keep `OUTCOME_UNKNOWN`; query provider, wait for callbacks, reconcile                              | Timeout is not proof of failure.                    |
| Provider outage before any attempt was sent                  | Route a new safe attempt to an eligible healthy provider                                           | No original financial effect.                       |
| Gateway crashes after provider success, before saving result | Recover from persisted attempt and query provider via stable reference                             | Avoid another charge.                               |
| Delayed/duplicate webhook                                    | Deduplicate by event ID; use versioned state transitions; offer status lookup                      | Prevent duplicate/stale merchant updates.           |
| Partial refund                                               | Track cumulative succeeded **and pending/reserved** refund amounts; enforce eligibility atomically | Prevent over-refunding.                             |
| Capture failure or timeout                                   | Record pending/unknown, query provider, retry only under provider contract                         | Capture may have succeeded despite a lost response. |

### The crucial timeout example

```text
Gateway                       Provider A
   |                              |
   |------ Authorize $100 ------->|
   |                              |
   |                         APPROVED
   |                              |
   |<------ Response lost --------X
   |
   v
Mark OUTCOME_UNKNOWN
   |
   v
Query Provider A / await callback / reconcile
   |
   +--> Approved: persist success
   |
   +--> Confirmed no effect: safe retry/reroute
   |
   +--> Unresolved: remain pending and investigate
```

Do **not** immediately switch to Provider B: both processors might create a hold
or charge. The merchant API contract must say which states are final, when to
reuse idempotency keys, how to poll status, and how retry/rate-limit responses
work.

## 5. Data Model & Correctness

| Entity                 | Important fields                                                                        |
|------------------------|-----------------------------------------------------------------------------------------|
| `Merchant`             | merchant_id, status, allowed_methods, configuration                                     |
| `MerchantCredential`   | credential_id, merchant_id, scopes, secret/public-key reference, expiry, rotation state |
| `PaymentIntent`        | payment_id, merchant_id, amount, currency, status, version                              |
| `PaymentAttempt`       | attempt_id, payment_id, provider_id, provider_key, status, timestamps                   |
| `ProviderRoutingRule`  | rule_id, eligibility, priority, cost, enabled                                           |
| `ProviderTransaction`  | provider_reference, attempt_id, operation_type, amount, outcome                         |
| `IdempotencyRecord`    | merchant_id, operation, key, request_hash, result_reference                             |
| `Capture`              | capture_id, payment_id, amount, state, provider_reference                               |
| `Refund`               | refund_id, payment_id, amount, state, provider_reference                                |
| `WebhookEvent`         | event_id, merchant_id, payment_id, event_type, version, delivery_status                 |
| `ReconciliationRecord` | provider_id, reference, amount, currency, match_status, exception                       |

**Correctness invariants**

1. One logical merchant payment request must not accidentally create multiple
   effective charges.
2. Each external attempt has a durable and stable reference.
3. Total captures must comply with authorized amount and provider/payment-method
   rules.
4. Completed plus in-flight reserved refunds cannot exceed the refundable
   captured amount.
5. Duplicate provider responses must not apply the same state change twice.
6. Stale events must not overwrite newer final/payment states.
7. Payment state and associated idempotency/outbox updates commit atomically
   where they share a local database.

Use database unique constraints, optimistic versioning or row locks, and
append-only operation/event history as appropriate.

## 6. Failure Handling, Scalability, Security & Reconciliation

### Webhooks

```text
Payment state commit
        |
        v
Transactional Outbox
        |
        v
Durable Event Broker
        |
        v
Webhook Delivery Worker
        |
        v
Merchant HTTPS Endpoint
        |
        v
   2xx acknowledgement
```

Choose **signed, at-least-once** webhook delivery. Include event ID, timestamp,
payment ID, event version, and status. Retry transient failures with exponential
backoff and jitter; track delivery attempts and use a **dead-letter queue (DLQ)
** for repeated failures. Merchants should deduplicate events and fetch current
payment state when necessary. Event delivery can be delayed or out of order.

### Reconciliation

```text
Gateway Records           Provider API / Files
       |                          |
       +------------+-------------+
                    |
                    v
             Reconciliation
                    |
        Match reference, operation,
        amount, currency, status
                    |
           +--------+--------+
           |                 |
         MATCH           MISMATCH
           |                 |
           v                 v
        Confirm          Exception Queue
                             |
                             v
                     Investigate / correct
```

Reconcile at two levels:

- **Operational:** Authorization, capture, void, and refund outcomes.
- **Financial:** Clearing, settlement, fees, FX, payouts, and adjustments.

Provider callbacks and API responses are not necessarily final settlement
evidence. Maintain explicit unmatched/exception workflows and auditable
corrections.

### Security

- Prefer hosted payment fields/tokenization to keep raw PAN out of general
  orchestration services.
- Isolate systems that handle sensitive card data; follow applicable **PCI DSS**
  requirements.
- Use TLS, scoped merchant credentials, credential rotation, least privilege,
  and strong service identities.
- Sign webhook payloads and protect against replay.
- Protect/redact logs; use tamper-evident audit records.
- Tokenization can reduce PCI scope, **not automatically eliminate it**.

### Scalability and regional availability

| Concern            | Design                                                                                                                         |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Gateway throughput | Horizontally scale stateless API and orchestration workers.                                                                    |
| Noisy merchant     | Per-merchant rate limits, quotas, and bounded queues.                                                                          |
| Provider overload  | Backpressure, concurrency budgets, circuit breakers.                                                                           |
| Database capacity  | Index around merchant/payment access; partition only when justified.                                                           |
| Region failure     | Tested failover with payment-level ownership and durable state; prevent dual active attempts.                                  |
| Observability      | Track p95/p99 latency, technical failures, processor timeouts, unresolved payment age, webhook lag, reconciliation exceptions. |

**Active-passive vs. active-active:** Active-active stateless APIs are
relatively straightforward; active-active independent writes to the same payment
are unsafe without coordination. Prefer controlled payment ownership or a
suitably strong distributed consistency mechanism.

## 7. Key Points to Remember

1. **Idempotency at both boundaries:** Merchant → gateway and gateway →
   provider. Retries must not create multiple financial effects.
2. **Unknown is not failed:** After a timeout, resolve the original attempt
   before retrying or rerouting.
3. **Orchestration isolates providers:** Canonical model + adapters + routing
   policies reduce integration coupling.
4. **Strong local state, asynchronous external updates:** ACID for gateway
   state; Saga for external operations; outbox + signed at-least-once webhooks
   for notifications.
5. **Reconciliation closes the financial loop:** Match gateway operations
   against provider and settlement evidence; investigate exceptions.

## 8. Interview Closing Summary

> I would design the merchant payment gateway as a secure, API-first,
> multi-provider orchestration platform. Merchants use scoped credentials, and
> every financial operation has durable idempotency. The gateway persists the
> payment intent and provider attempt before calling an external processor, then
> stores the result using guarded state transitions. The most important design
> choice is handling uncertain provider outcomes: I would never blindly retry
> through a second provider after a timeout. Instead, I would resolve the
> original
> attempt and reconcile it. ACID transactions protect local state, a
> transactional
> outbox and durable broker support asynchronous processing, and signed
> at-least-once webhooks notify merchants. Stateless services scale
> horizontally,
> while controlled payment ownership prevents conflicting multi-region attempts.
> Tokenization, audit controls, and provider reconciliation protect security and
> financial correctness.

**Interview takeaway:** A payment gateway is not just an API router. It is a *
*durable payment-state and recovery orchestration system**, designed to remain
financially correct even when external systems return uncertain outcomes.
