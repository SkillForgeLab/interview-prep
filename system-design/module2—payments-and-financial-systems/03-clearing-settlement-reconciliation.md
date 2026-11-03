# Design 4 — Payment Clearing, Settlement & Reconciliation

**10-minute system design answer · American Express Solution Architect
Preparation**

## 1. Problem & Requirements

Design a system that processes transactions submitted by merchants, posts
financial obligations, settles payments, and detects financial mismatches.

| Operation          | Purpose                                                                           |
|--------------------|-----------------------------------------------------------------------------------|
| **Authorization**  | Approve a purchase and reserve credit                                             |
| **Clearing**       | Process the merchant's submitted charge and create appropriate financial postings |
| **Settlement**     | Calculate and complete financial obligations between parties                      |
| **Reconciliation** | Verify that independent financial records agree                                   |

### Functional requirements

- Ingest clearing files or messages.
- Validate and match transactions with authorizations where applicable.
- Post transactions to the financial ledger.
- Calculate merchant settlement amounts.
- Create and track settlement instructions.
- Reconcile ledger, network, and bank records.
- Handle duplicates, missing transactions, refunds, and adjustments.

### Non-functional requirements

**Financial correctness, durability, idempotency, auditability, security, and
recoverability** are critical.

Unlike authorization, clearing and settlement can often use asynchronous and
batch processing, subject to contractual cutoffs.

## 2. High-Level Architecture

```text
      Merchant / Payment Network
                 |
                 v
        Clearing Ingestion
                 |
                 v
         Validate + Deduplicate
                 |
                 v
       Authorization Matching
                 |
                 v
        Clearing Processor
                 |
                 v
          Financial Ledger
                 |
                 v
        Settlement Engine
                 |
                 v
         Payout / Bank API
                 |
                 v
        Settlement Confirmation

  Independent Reconciliation Engine
           /       |       \
          v        v        v
       Clearing  Ledger   Bank Records
          \        |        /
           v       v       v
           Exception Queue
```

**Architecture principle:** Separate clearing, ledger posting, settlement
execution, and reconciliation. Each has a different responsibility and failure
model.

## 3. Key Design Decisions — With Reasons

| Decision          | Choice                                                          | Why / Trade-off                                           |
|-------------------|-----------------------------------------------------------------|-----------------------------------------------------------|
| Processing        | Asynchronous, batch-capable                                     | Supports large submission volumes and settlement cutoffs  |
| Database          | Relational transactional DB                                     | Atomic financial state changes                            |
| Financial records | Double-entry ledger                                             | Accurate, auditable accounting                            |
| Idempotency       | Unique clearing/posting reference                               | Prevent duplicate financial postings                      |
| Settlement        | Separate settlement engine                                      | Independent calculation, scheduling, and payout lifecycle |
| Messaging         | Durable queue or event stream                                   | Decouple processing stages                                |
| Reliability       | Transactional outbox                                            | Avoid lost events after commits                           |
| Reconciliation    | Independent matching engine                                     | Detect errors that transaction validation misses          |
| Scaling           | Partition by merchant, settlement batch, or accounting boundary | Parallel processing with controlled financial consistency |

### Decision 1 — Why asynchronous processing?

Authorization requires an immediate response. Clearing usually does not.

Merchants may submit transactions in files or batches. Settlement may depend on
cutoffs, adjustments, and financial schedules.

**Choice:** Durable ingestion followed by asynchronous processing.

**Why:**

- Absorbs traffic spikes.
- Supports retries.
- Allows parallel processing.
- Prevents one slow downstream component from blocking all submissions.

**Trade-off:** Processing is not immediately complete. We need explicit
statuses, monitoring, and reconciliation.

### Decision 2 — How do we prevent duplicate clearing?

The same clearing record may arrive again after a file retry.

**Choice:** Persist a unique, properly scoped clearing-record identity.

```text
Clearing Record
      |
      v
Already processed?
   /       \
 Yes        No
  |          |
  v          v
Return     Validate and
existing   post ledger
result
```

The clearing identity, ledger posting identity, and associated state transition
must be stored transactionally or coordinated with recoverable workflow states.

**Why:** A duplicate message must not charge the cardholder twice.

### Decision 3 — Why separate clearing from settlement?

Clearing determines which financial transactions and obligations should be
recorded.

Settlement determines the applicable amounts to be paid and manages their
execution.

**Example — Illustrative merchant settlement:**

| Item               |   Amount |
|--------------------|---------:|
| Submitted sales    |   $1,000 |
| Refunds/credits    |    -$100 |
| Applicable fees    |     -$30 |
| **Net settlement** | **$870** |

Actual settlement calculations depend on the merchant agreement, fees,
adjustments, and payment arrangements.

**Why separate the services?** A financial posting may succeed even while the
payout bank is unavailable. We must not lose or recreate that posting because
settlement is delayed.

### Decision 4 — Why an independent reconciliation engine?

Even when each service is internally correct, different systems can disagree.

For example:

- Clearing contains $1,000.
- The ledger records $1,000.
- Bank settlement confirms only $970.

That difference may be expected fees or an actual error.

**Choice:** Compare independent records using transaction IDs, settlement
references, amounts, currencies, and business dates.

**Concept — Reconciliation:** Detecting and investigating mismatches between
financial records.

It must support both transaction-level matching and aggregate settlement
balancing.

## 4. End-to-End Request Flow

```text
1. Receive clearing file/message
            |
2. Durably store original input
            |
3. Validate format and records
            |
4. Deduplicate clearing records
            |
5. Match authorizations where applicable
            |
6. Post financial ledger entries
            |
7. Release/adjust authorization holds
            |
8. Calculate merchant settlement
            |
9. Create payout instruction
            |
10. Receive payout confirmation
            |
11. Reconcile financial records
```

**Important:** Steps 6 and 7 must be coordinated so that a transaction is not
counted twice against available credit. If separate databases are involved, use
an idempotent, recoverable workflow rather than assuming one distributed ACID
transaction exists.

Settlement instructions must have their own identity and lifecycle. A bank
accepting an instruction does not necessarily mean funds have settled.

## 5. Data Model & Correctness

| Entity                    | Purpose                                          |
|---------------------------|--------------------------------------------------|
| `ClearingRecord`          | Submitted financial transaction and its identity |
| `LedgerPosting`           | Immutable accounting entries                     |
| `SettlementBatch`         | Group of obligations to settle                   |
| `PayoutInstruction`       | External payment instruction and status          |
| `ReconciliationException` | Missing, duplicate, or mismatched records        |

**Core invariants:**

- One logical clearing record must not create duplicate ledger postings.
- Every posted journal transaction must balance.
- A payout retry must not unintentionally create another payment.
- Financial differences must be accounted for or explicitly tracked as
  unresolved.
- A settlement cannot be marked completed solely because an instruction was
  sent.

### Failure handling

| Failure                 | Response                                                                      |
|-------------------------|-------------------------------------------------------------------------------|
| Duplicate clearing file | File and record-level idempotency                                             |
| Invalid records         | Quarantine with error details; process valid records according to batch rules |
| Missing authorization   | Apply network/business rules; investigate exceptions                          |
| Ledger failure          | Retry safely without duplicate postings                                       |
| Bank timeout            | Query/reconcile status before retrying payment instruction                    |
| Partial settlement      | Track confirmed, pending, and failed obligations                              |
| Reconciliation mismatch | Create exception for investigation and controlled correction                  |
| Event broker failure    | Persist committed events in the outbox                                        |

A bank timeout is an **uncertain outcome**. The payout might have succeeded.
Blindly retrying with a new reference could create a duplicate payment.

For scalability, process independent merchant/batch workloads in parallel while
preserving accounting and payout constraints. For security, use authenticated
partner connections, encrypted data, least-privilege payout permissions,
approval controls, and auditable records.

## 6. Key Points to Remember

1. **Authorization is not settlement.** Approval reserves credit; clearing
   creates financial postings; settlement completes payment obligations.
2. **Asynchronous processing is appropriate.** Clearing and settlement can often
   be processed asynchronously with durable workflows and cutoffs.
3. **Idempotency prevents double charging and payout.** Every clearing posting
   and settlement instruction requires durable identity.
4. **Ledger and settlement are different responsibilities.** Ledger records
   obligations; settlement executes payments against those obligations.
5. **Reconciliation is mandatory.** Compare independent records and resolve
   exceptions. Internal transaction success does not guarantee external
   financial settlement.

## 7. Interview Closing Summary

> I would design clearing and settlement as separate, durable, asynchronous
> financial workflows. Clearing ingestion validates and deduplicates submitted
> transactions, matches applicable authorizations, and posts financial entries
> through an authoritative double-entry ledger. The settlement engine calculates
> obligations and manages payout instructions independently. Durable idempotency
> prevents duplicate postings and payments, while transactional outbox messaging
> protects downstream delivery. Finally, an independent reconciliation engine
> compares clearing, ledger, and bank records and manages exceptions. This gives
> us financial correctness, scalability, auditability, and safe recovery from
> partial failures.

---

**Next design:** Real-Time Fraud Detection System — low-latency decisions using
streaming data, feature stores, rules, and machine learning.
