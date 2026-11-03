# System Design — Payment Clearing, Settlement & Reconciliation

## 1. Problem & Requirements

**Problem:** Design a system that converts authorized card transactions into
financial postings, calculates settlement obligations, transfers funds, and
identifies and resolves mismatches.

### Understand the three stages

| Stage              | Meaning                                                                           | Example                                            |
|--------------------|-----------------------------------------------------------------------------------|----------------------------------------------------|
| **Clearing**       | Validate and exchange completed transaction details; create financial obligations | Merchant submits a $100 charge                     |
| **Settlement**     | Calculate amounts owed and arrange actual fund transfers                          | Merchant receives $97 after an illustrative $3 fee |
| **Reconciliation** | Compare internal records with external records and actual payments                | Verify $100 charge, $3 fee, and $97 payout         |

An **authorization is not a completed payment**. It approves a proposed
transaction. Clearing and settlement follow the capture/submission of the
transaction.

American Express's merchant documentation distinguishes authorization,
submission, settlement, and reconciliation. Settlement amounts can include
deductions for fees, refunds, chargebacks, and adjustments.

### Functional requirements

- Accept clearing submissions from merchants or processors.
- Validate submissions and match them to authorizations where applicable.
- Create immutable financial ledger entries.
- Calculate settlement obligations, including fees and adjustments.
- Initiate transfers through the configured banking or network channels.
- Reconcile internal records, external settlement reports, and bank
  confirmations.
- Investigate mismatches and support controlled corrections.

### Non-functional requirements

| Attribute    | Requirement                                                               |
|--------------|---------------------------------------------------------------------------|
| Latency      | Meet clearing cutoffs and settlement deadlines; not necessarily real-time |
| Scale        | Handle large transaction batches and parallel merchant processing         |
| Consistency  | Strong for financial postings; eventual between independent systems       |
| Availability | Resumable operations without lost or duplicate financial effects          |
| Auditability | Trace every amount from submission through final settlement               |

**Key assumption:** We are designing a conceptual processing platform for a card
network/payment processor. It is not a claim about American Express's internal
architecture. Actual settlement responsibilities depend on whether the
organization is the issuer, acquirer, network, or a combination.

## 2. High-Level Architecture

```text
Merchant / Payment Processor
             |
             v
   Clearing Ingestion
      (API / File)
             |
             v
   Validation & Matching <--- Authorization Store
             |
             v
       Clearing DB
             |
             v
    Financial Ledger
             |
             v
     Settlement Engine
       |           |
       v           v
  Settlement    Settlement
    Batches      Ledger
       |
       v
   Banking / Network Adapter
       |
       v
 External Settlement Channel
       |
       v
 Confirmations / Statements
       |
       v
   Reconciliation Engine <--- Internal Ledger
             |
             v
     Exception Management
             |
             v
     Corrections / Audit
```

### Why each component exists

| Component               | What and why                                                                                       |
|-------------------------|----------------------------------------------------------------------------------------------------|
| Clearing ingestion      | Receives transaction data through APIs or files. Supports both modern and existing integrations.   |
| Validation & matching   | Checks transaction identifiers, amounts, currency, authorization references, and processing rules. |
| Clearing DB             | Records submissions, validation results, and processing states. Supports replay and audit.         |
| Financial ledger        | Records financial obligations using balanced, immutable accounting entries.                        |
| Settlement engine       | Calculates who owes whom, how much, in which currency, and for which cycle.                        |
| Banking/network adapter | Isolates payment-rail protocols, acknowledgments, retries, and confirmations.                      |
| Reconciliation engine   | Independently compares expected financial outcomes with external evidence.                         |
| Exception management    | Tracks unresolved differences without silently modifying financial records.                        |

**Architectural principle:** Keep transaction processing, financial accounting,
money movement, and reconciliation as separate responsibilities. They have
different correctness and failure-handling requirements.

## 3. Key Design Decisions — Most Important Section

| Decision                   | Choice and why                                                                              | Alternative / trade-off                                                                             |
|----------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| **Communication**          | Asynchronous processing for clearing and settlement; these are often cutoff-based workflows | Synchronous API appropriate for submission acknowledgment, not completion of settlement             |
| **Database**               | Relational database with ACID transactions for financial state                              | NoSQL may scale some workloads, but financial invariants need explicit enforcement                  |
| **Ledger**                 | Append-only double-entry postings                                                           | Updating balances directly is simpler but weakens traceability                                      |
| **Consistency**            | Strong within one financial posting; eventual across external systems                       | A distributed transaction across banks and services is generally not practical                      |
| **Settlement calculation** | Batch by participant, currency, settlement cycle                                            | Per-transaction transfers may be appropriate for other payment products but increase transfer count |
| **Messaging**              | Durable queue or event stream plus transactional outbox                                     | Direct service calls create tighter coupling and harder recovery                                    |
| **Reconciliation**         | Transaction-level and aggregate matching                                                    | Totals-only checks can hide offsetting errors                                                       |
| **Scaling**                | Partition independent work by merchant/participant and cycle                                | Avoid parallel writes that violate account or batch consistency                                     |
| **Caching**                | No cache as the authoritative source for financial amounts                                  | Cache reference data where freshness can be controlled                                              |

### Three concepts that matter

**1. Double-entry ledger:** Each journal entry has balanced debits and credits.
This prevents creating an unbalanced financial posting, although it does not by
itself prove the posting is economically correct.

**2. Net settlement:** Instead of transferring money for every transaction,
eligible obligations and adjustments are combined to calculate net amounts owed.
The exact netting rules depend on the network and agreement.

**3. Transactional outbox:** Save the financial state change and an event record
in one database transaction. A separate publisher sends the event. This avoids
committing a financial posting but losing its downstream notification.

## 4. End-to-End Request Flow

Consider an illustrative $100 credit-card purchase.

### Step 1 — Authorization already exists

The issuer approved $100. The authorization system has a reference ID and may
have reserved credit.

**Why no settlement yet?** Approval does not establish that the merchant has
submitted a final charge.

### Step 2 — Merchant submits the transaction

The merchant sends a capture/clearing record. The system stores the received
file or message and validates its integrity and source.

**Why durable ingestion?** A large file must be replayable after partial
processing failure, without losing or duplicating accepted transactions.

### Step 3 — Validate and clear

The system checks authorization linkage, permitted amount differences, currency,
duplicate submissions, and applicable network rules.

Some valid transactions may clear for an amount different from authorization,
such as eligible adjusted or partial charges. These differences must follow
scheme rules rather than an unconditional equality test.

### Step 4 — Create financial postings

Once accepted for financial posting, the system creates balanced entries.

Example from a simplified *issuer accounting perspective*:

| Account               |    Debit |   Credit |
|-----------------------|---------:|---------:|
| Cardholder receivable |     $100 |        — |
| Settlement payable    |        — |     $100 |
| **Total**             | **$100** | **$100** |

The exact accounts and posting rules depend on the institution's role and
accounting policy.

**Why here?** The clearing event gives the basis for recognizing a financial
obligation; the authorization alone generally does not.

### Step 5 — Calculate settlement

The settlement engine groups eligible obligations for a cycle and calculates net
payable amounts.

**Illustrative merchant settlement:**

| Item                    |     Amount |
|-------------------------|-----------:|
| Gross submitted charge  |    $100.00 |
| Assumed merchant fee    |     −$3.00 |
| **Net merchant payout** | **$97.00** |

Actual calculations also consider credits, deductions, chargebacks, and
settlement arrangements. American Express publishes both net-pay and gross-pay
options in its U.S. merchant reference guide.

### Step 6 — Complete the transfer

The banking adapter sends a settlement instruction, records its external
reference, and waits for the required confirmation.

**Important:** Sending a payment instruction or receiving a technical
acknowledgment does not necessarily mean the money has settled.

Different payment rails have different completion, finality, and return rules; a
settlement adapter must reflect the rules of the selected rail.

### Step 7 — Reconcile

Compare expected and actual amounts at multiple levels:

```text
Merchant Submission
       |
       v
  Cleared Items
       |
       v
Financial Ledger
       |
       v
Settlement Obligation
       |
       v
Network / Bank Record
       |
       v
  MATCH / EXCEPTION
```

Reconciliation evaluates transaction references, amounts, currencies, settlement
cycle, fees, and external confirmation identifiers.

### Step 8 — Resolve exceptions

If the system expects $97 but the confirmed bank record says $95, it creates an
exception.

It checks for valid deductions, missing records, timing differences, and
processing errors.

An unresolved difference is escalated. Any financial correction uses an
authorized adjustment or reversing entry, never a silent rewrite of posted
history.

## 5. Data Model & Correctness

### Core entities

| Entity                  | Important fields                                                    |
|-------------------------|---------------------------------------------------------------------|
| `ClearingRecord`        | clearing_id, capture_id, authorization_id, amount, currency, status |
| `JournalEntry`          | journal_id, source_reference, posting_date, status                  |
| `JournalLine`           | journal_id, account_id, debit, credit, currency                     |
| `SettlementBatch`       | batch_id, participant_id, currency, cycle, net_amount, status       |
| `SettlementInstruction` | instruction_id, batch_id, external_reference, status                |
| `ReconciliationResult`  | match_id, internal_reference, external_reference, difference        |
| `ExceptionCase`         | exception_id, reason, status, owner, resolution_reference           |

**Source of truth:** The financial ledger is authoritative for internal
financial postings. Bank and network records provide independent evidence that
external obligations were fulfilled.

### Critical invariants

1. **Balanced postings:** Debits equal credits for each posted journal, with
   currency handling defined explicitly.
2. **No duplicate financial effect:** A capture, adjustment, or settlement
   instruction must have stable uniqueness controls.
3. **Immutable history:** Corrections use new entries rather than editing posted
   ones.
4. **No false completion:** A settlement cannot be marked financially completed
   based only on instruction submission.
5. **Traceability:** Each journal and payment can be traced to its originating
   transaction, batch, and supporting external records.

**Concurrency handling:** Use database transactions and uniqueness constraints
for posting idempotency. Lock or version a settlement batch while finalizing it
to prevent two workers from settling the same obligation.

## 6. Failure Handling, Scalability & Security

### Failure handling

| Scenario                           | Design response                                     | Why                                       |
|------------------------------------|-----------------------------------------------------|-------------------------------------------|
| Clearing file arrives twice        | File and transaction-level deduplication            | Prevent duplicate postings                |
| Worker crashes midway through file | Checkpoint progress; replay idempotently            | Avoid missing transactions                |
| DB fails during posting            | Roll back incomplete local transaction              | No partial journal                        |
| Event publication fails            | Transactional outbox retries                        | Do not lose downstream work               |
| Settlement request times out       | Query external status before retry; reuse reference | Avoid duplicate transfers                 |
| External totals disagree           | Exception workflow with source-level investigation  | Preserve financial integrity              |
| Late refund or chargeback          | Apply to the appropriate later/adjustment cycle     | Avoid silently changing a finalized cycle |
| Traffic spike                      | Partition workers and batch processing              | Scale independent work                    |

### Reconciliation mismatch types

| Mismatch              | Example                                                    | Resolution approach                                               |
|-----------------------|------------------------------------------------------------|-------------------------------------------------------------------|
| Missing transaction   | Merchant submitted a charge, but no clearing record exists | Check submission acceptance/rejection and replay safely if needed |
| Duplicate transaction | Same capture posted twice                                  | Verify source, reverse incorrect posting under controls           |
| Amount difference     | Authorized $100, cleared $110                              | Validate whether the difference is permitted                      |
| Fee difference        | Expected $3, charged $5                                    | Recalculate contractual fees                                      |
| Timing difference     | Internal posting today, bank settlement next business day  | Track as pending with expected settlement date                    |
| Missing settlement    | Obligation exists but no confirmed payment                 | Investigate rail status and initiate controlled recovery          |
| Currency difference   | Amounts compared across different currencies               | Match by currency and validate applicable FX conversion           |

### Scaling

Start with a relational ledger, batch settlement engine, and horizontally
scalable clearing and reconciliation workers.

Scale independent partitions by participant and processing cycle. Retain
transaction-level identifiers so files and partitions can be retried safely.

Only introduce more complex sharding when transaction volume and database limits
justify it. Global financial accounting becomes harder when balances and
obligations are spread across independently consistent stores.

### Security and operations

- Encrypt financial records and transfer files in transit and at rest.
- Tokenize or avoid sensitive card data where full PAN is not required.
- Use mutual authentication and least-privilege access for external
  integrations.
- Require approval controls for high-risk manual financial adjustments.
- Track unreconciled amounts, oldest exceptions, settlement delays, batch
  failures, and ledger imbalance alerts.
- Preserve audit trails and support disaster recovery with tested restore
  procedures.

## 7. Key Points to Remember

1. **Authorization is not settlement** — Clearing establishes the accepted
   transaction details; settlement fulfills financial obligations.
2. **Use an immutable double-entry ledger** — Financial postings need strong
   consistency, balancing, and traceability.
3. **Separate clearing from settlement** — Clearing is transaction-data
   processing; settlement calculates and completes money movements.
4. **Reconcile independently** — Compare clearing records, ledger entries,
   settlement obligations, and external bank/network evidence.
5. **Never blindly retry money movement** — Use idempotency, external status
   checks, and controlled corrections for unknown or failed outcomes.

## 8. Interview Closing Summary

I would design clearing, settlement, and reconciliation as separate but
connected financial services. Clearing validates merchant submissions and
creates durable, traceable financial postings. A relational, append-only
double-entry ledger ensures internal accounting consistency. The settlement
engine calculates obligations by participant, currency, and processing cycle,
while a banking adapter handles external money movement and confirmations. An
independent reconciliation engine compares transaction-level and aggregate
financial records against external evidence, routing unmatched items into
controlled exception workflows.

The key trade-off is accepting asynchronous, potentially delayed settlement and
reconciliation in exchange for reliable financial correctness, recovery,
auditability, and controlled integration with external systems.
