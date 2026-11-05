# Design 8 — Chargebacks & Dispute Management System

**10-minute system design interview answer**  
**Role:** American Express Solution Architect  
**Core focus:** Durable workflows, deadline enforcement, financial correctness,
evidence management, and network integration.

> This is an illustrative enterprise architecture, not a description of American
> Express's internal implementation. Network stages, deadlines, and dispute
> outcomes must follow the relevant network, jurisdiction, program, and case
> rules.

## 1. Problem & Requirements

Design a system where cardholders can dispute transactions, merchants can submit
evidence, and the financial institution can investigate, decide, and apply the
correct financial adjustments.

### Functional requirements

- Create disputes for eligible transactions.
- Support reasons such as fraud, duplicate billing, incorrect amount, and goods
  not received.
- Handle merchant inquiries and chargebacks.
- Collect and review supporting evidence.
- Track dispute deadlines and notify merchants.
- Support decisions, reversals, and possible case reopening.
- Update financial records and maintain an audit trail.

### Refund vs. chargeback

| Refund                                           | Chargeback                                                              |
|--------------------------------------------------|-------------------------------------------------------------------------|
| Merchant-initiated or merchant-authorized credit | Dispute-related financial adjustment through the issuer/network process |
| Usually part of ordinary purchase resolution     | Governed by dispute rules and evidence                                  |
| Does not require a formal dispute                | May follow investigation or occur upfront                               |
| Merchant voluntarily returns funds               | May debit the merchant under applicable rules                           |

American Express distinguishes a merchant inquiry from an upfront chargeback. An
inquiry requests supporting information before a chargeback; an upfront
chargeback may debit the merchant before its response is reviewed.

**Important:** A dispute does not always result in a chargeback.

### Non-functional requirements

- **Workflow reliability:** Cases may remain open for days or longer.
- **Deadline enforcement:** Responses must meet case-specific rules.
- **Financial correctness:** No duplicate refunds, chargebacks, or reversals.
- **Auditability:** Preserve evidence, decisions, and state history.
- **Security:** Protect customer and merchant information.
- **Scalability:** Support many concurrent cases and document uploads.

**Key assumption:** We are designing an enterprise dispute platform that
integrates with existing payment, network, and ledger systems.

## 2. High-Level Architecture

```text
        Cardholder / Merchant Portal
                     |
                     v
                API Gateway
                     |
                     v
               Dispute Service
                     |
          +----------+-----------+
          |          |           |
          v          v           v
       Payment    Case         Workflow
       Service    Management   Engine
          |          |           |
          |          v           +--> Deadline
          |       Case DB             Scheduler
          |          |
          |          v
          |       Evidence
          |       Store
          |       (Object Storage)
          |
          +----------+-----------+
                     |
                     v
              Network Integration
                     |
                     v
              Financial Ledger
                     |
                     v
               Event Broker
                     |
               Notifications
                / Reporting
```

This is a **logical diagram**. Network Integration and Financial Ledger are
separate integration boundaries, not necessarily a sequential path for every
operation.

### Component responsibilities

| Component               | Responsibility                                      |
|-------------------------|-----------------------------------------------------|
| **Dispute Service**     | APIs, eligibility, duplicate detection              |
| **Case Management**     | Stores cases, states, reasons, decisions            |
| **Workflow Engine**     | Controls long-running dispute steps                 |
| **Deadline Scheduler**  | Reminders, escalation, expiry handling              |
| **Evidence Store**      | Secure storage for receipts and documents           |
| **Payment Service**     | Verifies original transaction and related refunds   |
| **Network Integration** | Exchanges inquiries, evidence, and decisions        |
| **Financial Ledger**    | Records provisional/final adjustments and reversals |
| **Event Broker**        | Notifications, reporting, downstream integration    |

**Main architectural principle:** The case-management system owns the dispute
workflow; the financial ledger remains authoritative for money movements.

## 3. Key Design Decisions — With Reasons

| Decision            | Choice                                            | Why / Trade-off                                                                                              |
|---------------------|---------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Workflow management | **Orchestration** using a durable workflow engine | Central control of deadlines, retries, and states. More centralized coordination.                            |
| Communication       | Synchronous APIs + asynchronous workflows         | Immediate case acknowledgement; long-running investigation happens independently. Adds eventual consistency. |
| Database            | Relational DB                                     | Transactions, constraints, case relationships, audit metadata. Requires scaling planning.                    |
| Case lifecycle      | Durable state machine                             | Enforces valid transitions and resumes after crashes. Adds transition-management complexity.                 |
| Evidence            | Object storage + metadata DB                      | Scalable and cost-effective for documents. Requires separate access controls and consistency checks.         |
| Deadline management | Persistent timers + periodic deadline scans       | Survives restarts and detects missed jobs. Requires reliable scheduler operations.                           |
| Idempotency         | Unique operation IDs + database constraints       | Prevents duplicate cases and financial effects. Identity rules need careful design.                          |
| Messaging           | Event broker + transactional outbox               | Reliable integration with downstream services. Requires duplicate-safe consumers.                            |
| Network integration | Dedicated adapter                                 | Isolates protocol, reason codes, acknowledgements, and retries. Adds mapping and maintenance.                |

### Decision 1 — Why orchestration over choreography?

A dispute can involve:

```text
Open Case
    |
    v
Notify Merchant
    |
    v
Wait for Evidence
    |
    v
Review Evidence
    |
    v
Decide Outcome
    |
    v
Apply Adjustment
    |
    v
Close Case
```

**Choose orchestration:** A workflow engine tracks progress and coordinates
steps.

**Why?** Disputes involve human interaction, external systems, timers,
deadlines, and potentially multiple rounds of review.

**Alternative — Choreography:** Services independently react to events. It
reduces central coordination but makes end-to-end state, timeouts, and exception
handling harder to follow.

**Concept — Durable workflow:** A long-running process whose current state is
persisted so execution can resume after a service restart.

### Decision 2 — Why a durable state machine?

```text
OPEN
  |
  v
VALIDATED
  |
  +----> INQUIRY_PENDING
  |            |
  |            v
  |      EVIDENCE_RECEIVED
  |            |
  |            v
  |          REVIEW
  |
  +----> CHARGEBACK_APPLIED
               |
               v
         EVIDENCE / REVIEW
               |
               v
            DECISION
               |
               v
      FINANCIAL_RECONCILIATION
               |
               v
             CLOSED
```

The exact stages depend on case type and applicable dispute rules. Some cases
resolve without merchant contact; others can be reopened or reconsidered.

**Why persist state transitions?** To prevent contradictory decisions and resume
work safely after failure.

Use an atomic state/version check when updating a case so that two reviewers
cannot both apply incompatible transitions.

### Decision 3 — How do we enforce deadlines?

American Express merchant guidance refers to the case-specific **reply-by date
**. Missing the deadline can result in a chargeback.

```text
Case Created / Updated
          |
          v
Store Authoritative Deadline
          |
          v
Durable Scheduler
          |
          +--> Reminder
          +--> Escalation
          +--> Deadline Action
          |
          v
Periodic Deadline Reconciliation
```

**Why not rely only on a scheduled job?** A scheduler outage or missed execution
could cause a financial loss.

Persist deadlines in the database, use durable timers, and run a separate scan
for overdue cases.

The deadline action must be idempotent and recheck the current case state before
acting.

**Important:** Do not hardcode a universal 30-day response limit. Different
programs, regions, reasons, and case stages can have different rules. Use the
authoritative deadline for that case.

### Decision 4 — Why object storage for evidence?

Documents such as receipts, delivery confirmations, invoices, and customer
correspondence may be large.

Store files in object storage and their metadata in the relational database.

**Why?** Object storage supports document volume efficiently without bloating
the transactional case database.

Store a checksum, immutable version reference, uploader, timestamp, and access
classification.

**Trade-off:** Document uploads and case updates are not naturally one database
transaction. A document must be verified as successfully stored and accessible
before the case marks it as formally submitted.

## 4. End-to-End Request Flow

1. **Cardholder submits dispute.** Receive original transaction reference,
   reason, disputed amount, and supporting information.
2. **Validate eligibility.** Verify transaction, ownership, applicable rules,
   previous refunds, and related disputes.
3. **Create case.** Generate case ID, record reason and deadlines, and start
   durable workflow.
4. **Initiate the appropriate path.** Resolve directly, send merchant inquiry,
   or handle upfront chargeback under applicable rules. An upfront chargeback
   requires a financial adjustment at this stage.
5. **Notify merchant and collect evidence.** Send required network messages and
   securely store the submitted evidence.
6. **Review and decide.** Authorized reviewers or rules evaluate evidence and
   determine the permitted outcome.
7. **Apply financial adjustment.** Send an idempotent command to the ledger for
   any credit, debit, or reversal. Avoid duplicating existing refunds or
   adjustments.
8. **Close the case.** Confirm needed acknowledgements and financial postings;
   record outcome, notify parties, and preserve the audit trail.

### Possible outcomes

| Outcome                                     | Financial implication                                     |
|---------------------------------------------|-----------------------------------------------------------|
| Inquiry resolved in merchant's favor        | No chargeback required                                    |
| Chargeback upheld                           | Merchant debit/related cardholder credit remains          |
| Chargeback reversed                         | Appropriate compensating financial adjustment             |
| Partial resolution                          | Adjustment for the applicable amount                      |
| Case withdrawn or closed without adjustment | No new posting unless needed to reconcile earlier actions |

## 5. Data Model & Correctness

| Entity                  | Important fields                                                                                  |
|-------------------------|---------------------------------------------------------------------------------------------------|
| **Dispute**             | `case_id`, `payment_id`, `network_case_id`, `reason_code`, `disputed_amount`, `status`, `version` |
| **Deadline**            | `case_id`, `stage`, `reply_by_at`, `rule_version`, `action_status`                                |
| **Evidence**            | `evidence_id`, `case_id`, `object_key`, `checksum`, `version`, `submitted_at`                     |
| **DecisionHistory**     | `decision_id`, `case_id`, `previous_state`, `new_state`, `actor`, `timestamp`                     |
| **FinancialAdjustment** | `adjustment_id`, `case_id`, `operation_type`, `ledger_reference`, `status`                        |

### Critical correctness rules

1. **No duplicate dispute operation.** Use network case IDs and scoped operation
   identifiers. Do not impose blanket uniqueness on `payment_id`; a payment can
   have multiple legitimate dispute-related cases or stages.
2. **No duplicate financial adjustment.** Every chargeback, credit, and reversal
   has a unique operation ID enforced by the ledger.
3. **Controlled state transitions.** Use optimistic locking with a `version`
   field or equivalent transaction control.
4. **Immutable history.** Append decision events and preserve evidence versions
   rather than overwriting history.
5. **Financial closure requires confirmation.** A case decision alone is not
   proof the ledger posting succeeded.

**Concept — Optimistic locking:** Update a record only when its version matches
the version previously read. If another process updated it, reload and resolve
the conflict.

## 6. Failure Handling, Scalability & Security

| Scenario                  | Design response                                                | Why                                              |
|---------------------------|----------------------------------------------------------------|--------------------------------------------------|
| Missed deadline job       | Durable timer + overdue-case scan + escalation                 | Recover without silently missing required action |
| Duplicate events          | Idempotent consumers and unique operation IDs                  | Prevent repeated actions                         |
| Network timeout           | Persist pending state, reconcile, safely retry                 | Timeout does not prove rejection                 |
| Evidence upload fails     | Do not mark evidence submitted; retry safely                   | Avoid missing or incomplete evidence             |
| Two reviewers update case | Version-controlled state transitions                           | Prevent conflicting outcomes                     |
| Ledger posting times out  | Query/reconcile by operation ID before retrying                | Prevent duplicate financial adjustment           |
| High case volume          | Stateless API scaling, indexed queries, partitioned workers    | Handle more cases independently                  |
| Sensitive data exposure   | Encryption, least privilege, audit logging, retention controls | Protect customer/merchant information            |

### Important security choices

Use role-based or attribute-based access controls so cardholders, merchants,
investigators, and administrators see only permitted cases and evidence.

Encrypt files, use short-lived upload/download permissions, scan documents for
malware, and protect PII in logs and events.

Apply PCI DSS requirements to payment account data within scope, and define
evidence retention/disposal under applicable legal and business obligations.

### Operational metrics

- Cases approaching or exceeding deadlines.
- Evidence submission failures.
- Workflow failures and backlog.
- Network acknowledgement/reconciliation failures.
- Ledger posting mismatches.
- Duplicate financial operation attempts.

## 7. Five Key Points to Remember

1. **Disputes are long-running workflows.** Use durable orchestration, not one
   synchronous transaction.
2. **Deadlines are business-critical.** Persist authoritative deadlines and use
   redundant enforcement.
3. **Financial correctness is separate from case state.** Every
   chargeback/reversal must be idempotent and confirmed by the ledger.
4. **Evidence and decisions must be auditable.** Preserve immutable history,
   documents, and reviewer actions.
5. **Isolate external network complexity.** Use adapters and reliable messaging
   for retries, acknowledgements, and reconciliation.

## 8. Interview Closing Summary

> I would design the dispute management system around a durable workflow engine
> and a relational case database. Since disputes are long-running and
> deadline-sensitive, orchestration provides controlled state transitions,
> persistent timers, and reliable recovery. I would store evidence in secure
> object storage, integrate with payment networks through dedicated adapters,
> and
> use events for notifications and downstream processing. Financial adjustments
> would be executed through an authoritative ledger with durable idempotency to
> prevent duplicate chargebacks or reversals. Finally, I would implement
> deadline
> reconciliation, immutable audit history, role-based access control, and
> operational monitoring to ensure financial correctness, compliance, and
> reliable
> case resolution.

---

### Official reference sites

- [American Express — Merchant resources](https://www.americanexpress.com/us/merchant/)
- [PCI Security Standards Council — Document Library](https://www.pcisecuritystandards.org/document_library/)

Always use the applicable American Express network/program rulebook and the
actual case reply-by date for operational decisions.
