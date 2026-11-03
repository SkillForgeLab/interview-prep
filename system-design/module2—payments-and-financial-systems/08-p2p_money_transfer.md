# Design 9 — P2P Money Transfer System

**10-minute system design interview answer · American Express Solution Architect
preparation**

**Core focus:** Financial correctness, atomic money movement, double-entry
ledger, idempotency, concurrency control, distributed transactions, and
recovery.

> **Scope:** An illustrative system design—not a description of American
> Express's internal architecture. Specific payment-rail rules and compliance
> obligations depend on institution, product, jurisdiction, and rail.

## 1. Problem & Requirements

Design a system that lets a user send money from one account to another.

| Transfer type | Example                                              | Main challenge                                       |
|---------------|------------------------------------------------------|------------------------------------------------------|
| **Internal**  | Account A → Account B within our ledger              | Debit and credit atomically                          |
| **External**  | Account A → Another bank through ACH, FedNow, or RTP | Coordinate money movement across independent systems |

**Functional requirements:** Validate the sender and recipient; check available
balance; enforce transfer limits; evaluate fraud, sanctions, and applicable
compliance rules; initiate transfers; track status; and notify users.

**Non-functional requirements:**

- **Strong consistency** for ledger postings, holds, and funds availability.
- **Idempotency** so retries cannot create another transfer.
- **High availability and durability** with safe recovery from failures.
- **Security and compliance** including authentication, authorization, KYC/AML,
  and sanctions controls as applicable.
- **Scalability** for concurrent transfers and traffic spikes.

**Key assumption:** Internal accounts share an authoritative ledger that
supports one ACID transaction. External institutions cannot participate in that
local database transaction.

## 2. High-Level Architecture

```text
               Mobile / Web App
                      |
                      v
                 API Gateway
                      |
                      v
                Transfer Service
                      |
       +--------------+----------------+
       |              |                |
       v              v                v
 Account Service  Risk / Fraud     Workflow Engine
 - Ownership      - AML / KYC      - Transfer State
 - Status         - Limits         - Retries
 - Recipient      - Sanctions      - Recovery
       |              |                |
       +--------------+----------------+
                      |
                      v
               Financial Ledger
                      |
                      v
              Transactional DB
              - Transfers
              - Balances / Holds
              - Journal Entries
              - Idempotency
              - Outbox
                      |
             +--------+--------+
             |                 |
             v                 v
       Event Broker     Payment Rail Adapter
             |                 |
       Notifications      ACH / FedNow / RTP
       Reconciliation          |
                         External Bank
```

**Responsibilities:**

- **Transfer Service:** Validates requests and coordinates initiation.
- **Account Service:** Verifies ownership, status, and recipient eligibility.
- **Financial Ledger:** Owns authoritative balances and atomic postings.
- **Risk/Fraud Service:** Enforces fraud, limits, and relevant compliance
  decisions.
- **Workflow Engine:** Coordinates long-running external transfers and recovery.
- **Payment Rail Adapter:** Maps internal requests to rail-specific messages,
  status, and error semantics.
- **Event Broker:** Distributes notifications, reporting, and downstream events.

**Key principle:** The Transfer Service orchestrates the business operation; the
Financial Ledger owns financial state changes.

## 3. Key Design Decisions — With Reasons

| Decision             | Choice                                          | Why and main trade-off                                                                                |
|----------------------|-------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| SQL vs. NoSQL        | **Transactional SQL**                           | ACID, uniqueness, and concurrency. NoSQL is possible with equivalent guarantees.                      |
| Internal transfer    | **Single ACID transaction**                     | Debit and credit commit together; requires one transactional boundary.                                |
| External transfer    | **Durable Saga/workflow**                       | An external bank cannot join our local ACID transaction; adds intermediate states and recovery logic. |
| Double-entry ledger  | **Balanced journal entries**                    | Traceable money movement; requires strict accounting rules.                                           |
| Balance consistency  | **Strong**                                      | Prevents double spending; adds write coordination.                                                    |
| Notifications        | **Eventual consistency**                        | Keeps core transfers independent; notifications may be delayed.                                       |
| Idempotency          | **Unique key + durable result**                 | Prevents duplicate postings; requires stable identity and request matching.                           |
| Concurrency          | **Atomic conditional update or short row lock** | Prevents overspending; can create contention.                                                         |
| Messaging            | **Transactional outbox + durable broker**       | Reliable asynchronous events; consumers must handle duplicates.                                       |
| External integration | **Rail adapter + reconciliation**               | Isolates rail-specific behavior; increases workflow complexity.                                       |

### Decision A — ACID vs. Saga

**Internal transfer: one ACID transaction**

```text
BEGIN
  Validate and reserve sender funds
  Debit sender ledger account
  Credit recipient ledger account
  Update authoritative balances
  Save transfer + outbox
COMMIT
```

If any step fails, everything rolls back. For example,
moving $100 between customer deposit accounts can debit the sender's deposit liability and credit the recipient's deposit liability by $
100 (from the institution's accounting perspective).

**External transfer: durable Saga/workflow**

```text
Reserve Funds
     |
     v
Submit to External Rail
     |
     v
Await / Recover Outcome
     |
     +--> Success: Finalize accounting
     |
     +--> Failure: Release or correct funds
     |
     +--> Unknown: Reconcile before acting
```

**Saga:** A sequence of local transactions coordinated through forward steps and
compensating actions. It does **not** provide one ACID transaction across
organizations. Compensation may require a *new* financial transaction; a final
settled payment may not be reversible through the original workflow.

### Decision B — Strong vs. Eventual Consistency

Use **strong consistency** for authoritative balances, holds, transfer identity,
and journal posting. Use **eventual consistency** for notifications,
customer-history projections, and analytics. The notification can be late; a
second withdrawal must not spend the same funds.

### Decision C — Optimistic vs. Pessimistic Concurrency

Suppose a sender has $100 and initiates two $80 transfers simultaneously. Both
must not succeed.

| Strategy                  | How                                                          | Best fit                                         |
|---------------------------|--------------------------------------------------------------|--------------------------------------------------|
| Optimistic locking        | Update only if the expected version matches; retry conflicts | Low contention                                   |
| Pessimistic locking       | Lock the account row (`SELECT FOR UPDATE`)                   | High contention or coordinated multi-row changes |
| Atomic conditional update | Deduct/reserve only when enough funds remain                 | Simple balance invariant                         |

**Choice:** Atomic conditional balance update inside the ledger transaction. For
multiple account locks, acquire locks in a consistent order to reduce deadlocks.

### Decision D — Limits, Fraud, and Compliance

Before executing money movement, check account status, recipient eligibility,
authentication, fraud risk, sanctions, and applicable compliance requirements.

**Hard cumulative transfer limits** must use atomic or otherwise coordinated
enforcement—not a stale cache counter. The precise KYC/AML and sanctions
obligations depend on the institution, payment product, and jurisdiction.

### Decision E — External Payment Rail Selection

| Rail       | Processing characteristics                                              | Architectural impact                                    |
|------------|-------------------------------------------------------------------------|---------------------------------------------------------|
| **ACH**    | Clearing and settlement follow banking-day schedules; returns may occur | Pending states, returns, reconciliation                 |
| **FedNow** | Instant payments between participating institutions, around the clock   | Fast response handling and final settlement semantics   |
| **RTP**    | Real-time payments with final, irrevocable settlement                   | Validate before sending; returns are separate processes |

An adapter isolates rail-specific protocols, operating calendars, cutoff rules,
confirmations, and return behavior.

**Official references:
** [Nacha — How ACH Payments Work](https://www.nacha.org/content/how-ach-payments-work), [Federal Reserve — About FedNow](https://www.frbservices.org/financial-services/fednow-service/about-fednow-service/),
and [The Clearing House — RTP](https://www.theclearinghouse.org/payment-systems/rtp/institution).

## 4. End-to-End Request Flow

### A. Internal Transfer — Atomic

```text
1. Sender initiates transfer
              |
2. Authenticate and authorize
              |
3. Validate recipient and limits
              |
4. Perform risk/compliance checks
              |
5. Begin database transaction
              |
6. Check idempotency + available funds
              |
7. Atomic debit + credit
              |
8. Save balanced journal,
   transfer status, and outbox
              |
9. Commit -> COMPLETED
              |
10. Notify asynchronously
```

**Critical guarantee:** The sender debit and recipient credit are one atomic
financial posting. No committed state may contain only one side.

### B. External Transfer — Distributed Workflow

```text
1. Validate sender, recipient,
   limits, and risk
              |
2. Atomically reserve funds
   and create transfer record
              |
3. Status = PENDING
              |
4. Submit via payment rail adapter
              |
5. Status = SUBMITTED
              |
6. Receive or recover rail outcome
              |
       +------+-------+
       |      |       |
    Success Failure  Unknown
       |      |       |
       v      v       v
   Finalize Release  Reconcile
   posting   funds    with rail
       |      |       |
       v      v       v
   COMPLETED FAILED  PENDING
```

The actual accounting transition depends on the rail and product. Funds may move
into an outbound clearing or settlement account before final confirmation.

**Important:** `SUBMITTED` does not necessarily mean `SETTLED`. ACH may have
subsequent returns; a confirmed final instant payment cannot simply be undone by
releasing a local hold.

## 5. Data Model & Correctness

| Entity           | Important fields                                           | Purpose                   |
|------------------|------------------------------------------------------------|---------------------------|
| Transfer         | `transfer_id`, sender, recipient, amount, currency, status | Transfer lifecycle        |
| Account balance  | `account_id`, posted balance, reserved balance, version    | Funds availability        |
| Journal entry    | `journal_id`, account, debit/credit, amount, currency      | Immutable accounting      |
| Idempotency      | Scoped key, request fingerprint, stored result             | Duplicate prevention      |
| Rail instruction | External reference, rail, submission status                | Tracking and recovery     |
| Outbox           | Event ID, transfer ID, event type                          | Reliable event publishing |

### Simplified Transfer States

```text
CREATED
   |
   v
VALIDATING
   |
   v
RESERVED
   |
   +---- Internal ----> COMPLETED
   |
   +---- External ----> SUBMITTED
                           |
                      +----+----+
                      |         |
                      v         v
                  COMPLETED   FAILED
```

External transfers additionally need `PENDING`/`UNKNOWN` and a separate
return/correction lifecycle when applicable.

### Financial Correctness Invariants

1. **Balance:** Available funds cannot become negative unless an explicit
   overdraft policy permits it.
2. **Journal:** Debits equal credits for each posted transaction, separately by
   currency.
3. **Idempotency:** One logical transfer causes no more than one intended
   posting.
4. **State:** Mark `COMPLETED` only after required postings and confirmation.
5. **Immutability:** Correct posted entries through new correcting/reversal
   entries, not silent edits.

**Sharding trade-off:** Account-based partitioning is attractive, but sender and
recipient may be on separate shards. Preserve an atomic accounting boundary with
a capable database or carefully designed clearing/escrow workflow. Two unrelated
database commits are **not** atomic money movement.

## 6. Failure Handling, Scalability & Security

| Scenario                            | Design response                                           | Why                                   |
|-------------------------------------|-----------------------------------------------------------|---------------------------------------|
| Insufficient funds                  | Reject before posting                                     | Prevent unauthorized overdraft        |
| Simultaneous transfers              | Atomic conditional balance updates                        | Prevent double spending               |
| Duplicate requests                  | Durable idempotency                                       | Avoid duplicate debits                |
| Response lost after commit          | Return/recover stored result                              | Do not transfer twice                 |
| DB fails before commit              | Rollback                                                  | No partial internal transfer          |
| External rail timeout               | Check status and reconcile before retrying                | A timeout may hide successful payment |
| External payment rejected           | Release reserved funds transactionally                    | Restore available balance             |
| Rail success but local update fails | Recover by external reference; reconcile                  | Do not lose financial outcome         |
| Broker unavailable                  | Retain event in transactional outbox                      | Publish after recovery                |
| Regional failure                    | Durable replication, fenced failover, recovery validation | Avoid two conflicting writers         |

**Scalability:** Horizontally scale stateless APIs and workflow workers.
Optimize database access and partition only when needed, without compromising
cross-account financial correctness.

**High availability:** Use redundant instances, resilient storage, and tested
failover. Recover all acknowledged financial state before resuming writes.

**Security:** Authenticate users, verify sender ownership and authorization,
protect sensitive bank/payment credentials, use least-privilege service
identities, and keep auditable fraud, AML/KYC, sanctions, and exception
decisions.

**Recovery rule:** When an external outcome is unknown, do **not** automatically
retry the money movement or release funds. First establish whether the
instruction was accepted, settled, rejected, or returned. Use stable external
references, rail-supported status queries, callbacks, settlement reports, and
reconciliation.

## 7. Five Key Points to Remember

1. **Internal = ACID; external = Saga.** Keep local journal postings atomic;
   coordinate external rails through durable workflows.
2. **Double-entry + atomic balance enforcement.** Balanced journals provide
   accounting integrity; atomic funds checks prevent double spending.
3. **Idempotency prevents duplicate transfers.** A retry must resolve to the
   same logical operation.
4. **Strong consistency for money; eventual for notifications.** Never decide
   spendable funds from a delayed projection.
5. **Unknown external outcome requires reconciliation.** A timeout does not
   prove a payment failed.

## 8. Interview Closing Summary

> I would design the P2P transfer system around an authoritative double-entry
> financial ledger. For internal transfers, I would use one ACID transaction to
> atomically debit the sender, credit the recipient, update balances, and record
> the transfer. Atomic concurrency control and durable idempotency would prevent
> double spending and duplicate transfers. For external transfers, I would use a
> Saga orchestrated by a durable workflow engine, with funds reservation,
> rail-specific integration, pending states, and reconciliation. Mandatory
> fraud,
> limits, and compliance checks would run before execution. I would use a
> transactional outbox for asynchronous notifications, scale stateless services
> independently, and preserve strong consistency for financial data.
