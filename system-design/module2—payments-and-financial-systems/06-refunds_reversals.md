# Design 7 — Refunds & Reversals System

**10-minute System Design Interview | American Express | Solution Architect**

## 1. Problem & Requirements

Design a system that processes **full refunds, partial refunds, and
authorization reversals** safely, without duplicate refunds or incorrect
financial balances.

### Refund vs. reversal

| Operation                  | When                                        | Financial effect                                                     |
|----------------------------|---------------------------------------------|----------------------------------------------------------------------|
| **Full refund**            | After payment capture/processing            | Return the entire eligible payment amount                            |
| **Partial refund**         | After payment capture/processing            | Return part of the payment; multiple partial refunds may occur       |
| **Authorization reversal** | Before the charge is submitted for clearing | Cancel or reduce an authorization hold; no refund of a posted charge |

**Example:** A $100 purchase is authorized, but the customer cancels before
submission. Reverse the authorization to release the hold. If the charge has
already been submitted, process a credit/refund instead.

American Express's public U.S. Merchant Reference Guide distinguishes an
authorization reversal from a charge already submitted. Some processors offer a
combined reversal operation that chooses cancellation or refund depending on
capture status. Internally, we should still distinguish the two outcomes.

**Core requirements:**

- Support full refunds and multiple partial refunds.
- Never refund more than the eligible captured amount.
- Prevent duplicate refunds and double release of holds.
- Track asynchronous processor outcomes.
- Maintain correct ledger records.
- Support audit, recovery, and reconciliation.

---

## 2. High-Level Architecture

We design a merchant-facing payment platform integrating with an external
processor.

```text
           Merchant / Customer Service
                       |
                       v
                 API Gateway
                 (Auth / RBAC)
                       |
                       v
                Refund Service
                       |
          +------------+-------------+
          |            |             |
          v            v             v
     Payment DB     Refund DB     State Machine
     (Original      + Limits      (Lifecycle)
      Payment)          |
                       v
                 Outbox / Queue
                       |
                       v
                 Refund Worker
                       |
                       v
                Processor Adapter
                       |
                       v
              External Processor
                       |
                Webhook / Query
                       |
                       v
               Refund Finalizer
                       |
           +-----------+-----------+
           |                       |
           v                       v
      Financial Ledger         Reconciliation
           |
           v
    Confirmation / Notification
```

| Component             | Responsibility                                               |
|-----------------------|--------------------------------------------------------------|
| **Refund Service**    | Validate requests and reserve refundable amount              |
| **Refund DB**         | Store refund records, request identities, and lifecycle      |
| **Refund Worker**     | Execute approved refund requests                             |
| **Processor Adapter** | Isolate processor-specific APIs and responses                |
| **Financial Ledger**  | Record balanced financial journal entries                    |
| **Reconciliation**    | Match internal records with processor and settlement records |

**Key choice:** Separate refund orchestration from the ledger and processor
integration because they have different failure and correctness requirements.

---

## 3. Key Design Decisions — With Reasons

| Decision              | What we choose                                 | Why                                                            | Main trade-off                        |
|-----------------------|------------------------------------------------|----------------------------------------------------------------|---------------------------------------|
| Refund vs. reversal   | Route based on original payment lifecycle      | Refund changes the posted obligation; reversal releases a hold | Requires reliable payment state       |
| Communication         | Synchronous acceptance, asynchronous execution | Processor completion may be delayed                            | More states and monitoring            |
| Database              | Relational DB with ACID transactions           | Atomic limits and refund records                               | Write contention under hot payments   |
| Idempotency           | Durable, scoped unique request key             | Avoid duplicate refunds on retry                               | Key retention/conflict rules          |
| Concurrency           | Atomic conditional reservation                 | Prevent simultaneous over-refunds                              | Some serialization per payment        |
| State management      | Durable state machine                          | Track pending, unknown, failed, and confirmed                  | More transitions                      |
| Processor integration | Adapter plus stable external reference         | Safer retries, status queries, provider changes                | Mapping complexity                    |
| Events                | Transactional outbox                           | Avoid losing dispatch work after DB commit                     | Additional component and replay logic |

### Decision 1 — Why asynchronous execution?

The processor may accept a refund request before the financial outcome is final.
Return an acknowledgment, not premature success:

```http
HTTP/1.1 202 Accepted
```

```json
{
  "refundId": "ref_123",
  "status": "PENDING"
}
```

The client can call `GET /refunds/{refundId}` or receive a signed status
webhook.

**Trade-off:** This protects correctness but requires explicit pending, final,
and exceptional states.

### Decision 2 — Why relational DB?

We must atomically validate the captured amount, calculate completed and pending
refunds, reserve the new amount, create the refund record, store its idempotency
identity, and save an outbox event.

A transactional relational database is a simple baseline. Other databases are
possible if they provide equivalent atomicity and consistency.

### Decision 3 — Why idempotency?

If
a $50 refund succeeds but the HTTP response is lost, a client may retry. A stable key scoped to the merchant and logical request means that retry returns the **same refund**, rather than creating a second $
50 refund.

Store a request fingerprint. If the same key is used for different refund
details, reject the conflict. Preserve a stable processor-side identity where
supported.

### Decision 4 — Why a state machine?

```text
              REQUESTED
                  |
                  v
               PENDING
                  |
                  v
               SUBMITTED
                  |
           +------+------+ 
           |      |      |
           v      v      v
        CONFIRMED FAILED UNKNOWN
```

`UNKNOWN` means the processor's outcome is not yet established. Resolve it by
querying the processor, processing authenticated webhooks, or reconciling
records. Later refund failures or reversals may require explicit corrective
transitions and financial entries.

---

## 4. End-to-End Request Flow

Example: A $30 refund for a $100 captured purchase.

```text
1. POST /payments/{id}/refunds
             |
2. Authenticate and authorize merchant
             |
3. Validate original captured payment
             |
4. Check duplicate request
             |
5. Atomically reserve $30
             |
6. Save refund + outbox event
             |
7. Commit DB transaction
             |
8. Return 202 PENDING
             |
9. Worker sends refund to processor
             |
10. Processor returns reference/status
             |
11. Webhook or reconciliation confirms outcome
             |
12. Post financial ledger adjustment
             |
13. Mark refund confirmed
             |
14. Notify merchant/customer
```

**Critical design rule:** Do **not** call an external processor while holding a
database transaction open. Reserve and commit the refundable amount locally,
then dispatch via a durable worker. Finalize financial state using a reliable,
idempotent posting workflow when the appropriate external outcome is confirmed.

For authorization reversals, use a separate operation referencing the original
authorization; coordinate the network outcome and release the eligible hold
through the authoritative authorization system. A hold release is not
automatically a posted refund journal.

---

## 5. Data Model & Correctness

### Core tables

```text
Payment
-------
payment_id             PK
merchant_id
captured_amount_minor
currency
status
processor_reference

RefundBalance
-------------
payment_id             PK
confirmed_refunds_minor
reserved_refunds_minor
version

Refund
------
refund_id              PK
payment_id             FK
merchant_id
idempotency_key
amount_minor
currency
status
processor_reference
created_at
updated_at

RefundEvent
-----------
event_id               PK
refund_id
event_type
external_event_id
created_at

LedgerJournal
-------------
journal_id             PK
refund_id              UNIQUE
journal_type
posting_status

LedgerEntry
-----------
entry_id               PK
journal_id
account_id
debit_minor
credit_minor
currency
```

Add uniqueness constraints for merchant-scoped idempotency keys, external event
IDs, and processor references where appropriate.

### Prevent over-refunding

**Invariant:**

```text
Confirmed refunds + Reserved (pending) refunds
    <= Eligible captured amount
```

For a $100 captured payment:

- $30 confirmed refunds
- $40 pending/reserved refunds
- $30 still available to refund

Pending refunds must count against the refundable amount, otherwise concurrent
requests can consume the same capacity.

### Concurrent partial refunds

Suppose two $60 refunds are requested simultaneously against $100 of
eligibility. Use an atomic conditional update:

```sql
UPDATE refund_balance
SET reserved_refunds_minor =
    reserved_refunds_minor + :amount
WHERE payment_id = :payment_id
  AND :amount <=
      captured_amount_minor
      - confirmed_refunds_minor
      - reserved_refunds_minor;
```

The eligible captured amount must be in the same authoritative, locked data
boundary or protected by an equivalent transactional constraint. Only
one $60 reservation should succeed; the other sees $40 remaining.

### Ledger adjustments

A confirmed financial refund creates **new, balanced ledger entries**, linked to
the original payment. The exact chart of accounts depends on whether this ledger
belongs to the merchant, issuer, acquirer, or processor.

Illustrative issuer-side entry for a $30 refund:

| Ledger account             |   Debit |  Credit |
|----------------------------|--------:|--------:|
| Refund settlement clearing |     $30 |       — |
| Cardholder receivable      |       — |     $30 |
| **Total**                  | **$30** | **$30** |

Do not overwrite the original posted transaction. Use compensating journal
entries for later corrections, and guarantee the same refund does not post
twice.

---

## 6. Failure Handling, Scalability & Security

### Failure handling

| Failure                                 | Response                                                       |
|-----------------------------------------|----------------------------------------------------------------|
| Client retries refund                   | Return existing refund via idempotency key                     |
| Two partial refunds race                | Atomic reservation enforces the remaining limit                |
| Processor times out                     | Mark `UNKNOWN`; query or reconcile before retrying             |
| Processor unavailable                   | Durable queue, bounded retry/backoff, circuit breaker          |
| Refund definitively fails               | Release reserved amount transactionally                        |
| Duplicate processor webhook             | Deduplicate by external event/operation identity               |
| Refund fails after earlier confirmation | Record exception and any required compensating financial entry |
| Event broker unavailable                | Outbox event remains durable for later delivery                |
| Internal and processor records differ   | Reconcile by stable refund/processor reference                 |

**Most important failure:** The processor executes a refund but its response is
lost. Do **not** start a new refund with a new identity. Query the existing
operation or retry safely only when the processor's contract supports that
behavior. Keep the reservation while the outcome is uncertain.

### Scalability

- Horizontally scale stateless refund APIs and workers.
- Partition work by `payment_id` where ordering is needed.
- Coordinate all reservations for one payment under one transactional owner.
- Independently scale notification/reporting consumers.
- Partition/archive historical data only when volume justifies it.
- Monitor pending refund age, processor failures, reconciliation mismatches, and
  posting lag.

### Security

- Enforce merchant- and account-level access controls; use role-based privileges
  for sensitive actions.
- Apply appropriate refund amount and velocity limits and stronger approvals
  where policy requires.
- Protect processor credentials and verify external webhook authenticity.
- Use payment references or tokens; do not expose full card numbers in standard
  refund APIs/logs.
- Keep an immutable audit trail of the requester, original payment, amount,
  decision, processor reference, and financial outcome.
- Prevent conflicting remedies when a chargeback/dispute is already in progress.

---

## 7. Five Key Points to Remember

1. **Refund is not reversal.** Refunds return charged funds; reversals cancel or
   reduce authorization holds.
2. **Never over-refund.** Enforce
   `confirmed + pending <= eligible captured amount` atomically.
3. **Idempotency is mandatory.** Retries and duplicate webhooks must not produce
   duplicate financial effects.
4. **Processor acceptance is not final success.** Handle `PENDING`, `UNKNOWN`,
   late failures, and reconciliation.
5. **Every financial change must be auditable.** Use balanced ledger postings,
   corrective journal entries, and durable processing.

---

## 8. Interview Closing Summary

> I would design a Refunds and Reversals System using a transactional Refund
> Service that validates the original payment and enforces refund limits
> atomically. Authorization reversals and financial refunds follow separate
> workflows because their financial effects differ. I would use a relational
> database for idempotency, concurrent partial refunds, and state management,
> while executing processor requests asynchronously through a durable outbox and
> worker. Since processor acknowledgments do not always mean final success, I
> would track intermediate states, resolve uncertain outcomes through
> reconciliation, and post balanced ledger adjustments against confirmed
> financial
> events. The system would scale through stateless services and distributed
> workers, with strong authorization, auditability, and financial correctness
> controls.

---

## Reusable Prompt — Design 8: Chargebacks & Dispute Management System

Continue with **Design 8 — Chargebacks & Dispute Management System**.

Use our standard **10-minute system design interview template** for an American
Express Solution Architect position.

Cover:

1. **Problem & Requirements** — Cardholder disputes, chargebacks, merchant
   inquiries, dispute reasons, evidence submission, time limits, and possible
   outcomes. Explain the difference between a refund and a chargeback.
2. **High-Level Architecture** — Simple ASCII diagram showing components and
   responsibilities, including Dispute Service, Case Management, Workflow
   Engine, Evidence Store, Payment/Transaction Service, Network Integration, and
   Financial Ledger.
3. **Key Design Decisions — With Reasons** — Workflow orchestration vs.
   choreography, synchronous vs. asynchronous communication, relational database
   selection, durable state machines, document/object storage, idempotency,
   deadline management, event-driven processing, and external network
   integration.
4. **End-to-End Request Flow** — From cardholder dispute creation through
   transaction validation, case creation, merchant notification, evidence
   collection, review, decision, financial adjustment, and final case closure.
5. **Data Model & Correctness** — Dispute records, original payment references,
   dispute states, deadlines, evidence metadata, decision history, preventing
   duplicate disputes and financial adjustments, and immutable audit trails.
6. **Failure Handling, Scalability & Security** — Missed deadlines, duplicate
   events, external network timeouts, evidence upload failures, concurrent
   updates, retries, reconciliation, PII protection, access control, and
   compliance.
7. **Five Key Points to Remember** — Concise and interview-focused.
8. **Interview Closing Summary** — One strong paragraph suitable for a Solution
   Architect interview.

For every key architectural decision, explain **what we choose, why, and the
main trade-off**. Introduce concepts briefly where used. Focus on financial
correctness, workflow reliability, deadline enforcement, and enterprise
integration.

Use official sources to verify material financial or network-specific claims. Do
not assume American Express's internal architecture. Keep the explanation
concise enough for a 10-minute interview answer. Avoid repeating fundamentals
already covered. No assessments.

**At the end, print the complete reusable prompt for Design 9 — P2P Money
Transfer System**, using the same structure.
