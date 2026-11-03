# Design 8 — Chargebacks & Dispute Management System

**American Express Solution Architect interview | 10-minute system design answer
**

> **Scope:** Illustrative issuer/network-facing dispute case management
> platform. This is **not** a description of American Express's private
> architecture. Network rules and exact response deadlines vary by geography,
> product, case type, and program. The authoritative case-specific **reply-by
> date
** wins.

## 1. Problem & requirements

Design a platform where a cardholder disputes a posted transaction, the business
collects relevant information, contacts the merchant when required, tracks
evidence and deadlines, records decisions, and posts the correct financial
adjustments.

**Refund versus dispute/chargeback:** A **refund** is a merchant-initiated
return of funds on a charge. A **dispute** is a cardholder's challenge to a
charge; a **chargeback** is a formal financial debit/adjustment under the
applicable network process. Not every inquiry becomes a chargeback, and in some
cases an **upfront chargeback** may occur before the merchant submits evidence.
American Express distinguishes inquiries from upfront chargebacks in its public
merchant guidance.[1]

**Functional needs:**

- Open a dispute against a valid original transaction and capture reason code,
  amount, merchant, and cardholder reference.
- Support inquiry, upfront chargeback, evidence submission, merchant response,
  decision, case closure, and any permitted follow-on proceedings.
- Store evidence securely with a complete history of who uploaded/submitted what
  and when.
- Track the *case-specific* reply-by deadline and escalation rules.
- Coordinate financial adjustments, refunds, and dispute outcomes so the same
  amount is not accidentally credited twice.

**Non-functional needs:** Auditability and financial correctness are critical;
workflow must survive crashes; merchant communication may be asynchronous; case
data, documents and cardholder information require tight access control.

## 2. High-level architecture

```text
Cardholder / Service Agent            Merchant Portal
          |                                  |
          v                                  v
     Case Intake API                    Evidence API
          |                                  |
          +---------------+------------------+
                          |
                          v
                 Dispute Case Service
                          |
             +------------+------------+
             |            |            |
             v            v            v
       Case DB      Workflow Engine   Evidence Store
    (state/history) (deadlines/tasks)  (encrypted files)
             |            |
             +------+-----+
                    |
                    v
              Outbox / Broker
                    |
        +-----------+------------+
        |           |            |
        v           v            v
 Network Adapter  Notifications   Finance Adapter
 (inquiry /       (merchant,       (ledger and
  representment)   case owner)      reconciliation)
        |                            |
        v                            v
 Network/External System        Financial Ledger
```

**Responsibilities:** Case Service owns case identity, validated state
transitions, and audit history. Workflow Engine owns durable tasks, deadlines
and retries. Evidence Store keeps large documents outside the database. Network
Adapter isolates external message formats. Finance Adapter translates confirmed
dispute-related adjustments into controlled ledger commands.

## 3. Key design decisions — what, why, trade-off

| Decision             | Choose                                                      | Why                                                                   | Main trade-off                                           |
|----------------------|-------------------------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------|
| Workflow control     | **Durable central orchestration**                           | Disputes are long-running, deadline-driven processes with human steps | A workflow engine is another component to operate        |
| Case storage         | **Relational database**                                     | Transaction linkage, state constraints, case searches, atomic updates | Requires indexing/partitioning as volume grows           |
| Evidence storage     | **Encrypted object storage + DB metadata**                  | Supports large files, versioning, retention and secure access         | Two stores need coordinated lifecycle management         |
| User API             | **Synchronous case acceptance; asynchronous processing**    | Opening a case can return immediately; external review takes longer   | Clients must handle intermediate states                  |
| Idempotency          | **Unique external case/event identifiers and request keys** | Network callbacks and user actions can be delivered more than once    | Identity scoping and event retention need design         |
| State transitions    | **Explicit state machine + optimistic concurrency**         | Prevents duplicate closure or contradictory decisions                 | More code than free-form status updates                  |
| Deadline enforcement | **Persistent `reply_by` + durable scheduled jobs**          | Missing an evidence deadline can cause a financial loss               | Clock/time-zone, cancellation, and escalation complexity |
| External integration | **Adapter + outbox + inbox/deduplication**                  | Handles heterogeneous networks, retries, unknown outcomes             | Eventual consistency and reconciliation needed           |
| Accounting           | **Append-only journal for financial effects**               | Allows traceable adjustments and compensating entries                 | Requires coordination with external settlement events    |

**Orchestration vs. choreography:** A workflow engine is preferable here because
deadlines and legal/business decisions require one clear place to understand
what should happen next. Events are still useful for notifications and
independent consumers; the entire business state should not be inferred from
loose event subscriptions.

**Brief concept — optimistic concurrency:** Store a `version` on the case.
Update only when the expected version matches so two agents cannot both finalize
conflicting decisions.

## 4. End-to-end request flow

```text
1. Cardholder disputes a posted transaction
                |
2. Validate transaction, ownership, eligibility and scope
                |
3. Create case idempotently; store reason, amount, reply-by policy
                |
4. Start durable workflow; assess inquiry vs. chargeback path
                |
5. Notify merchant / send network inquiry if required
                |
6. Collect evidence; scan, encrypt, classify, version
                |
7. Validate merchant response and submit before reply-by date
                |
8. Receive external acknowledgment / decision asynchronously
                |
9. Apply approved financial adjustment using idempotent ledger command
                |
10. Reconcile external financial records; close or escalate case
                |
11. Notify relevant parties and retain full audit trail
```

**Important:** A submitted evidence package is **not** a successful dispute
outcome. Acknowledgment, decision and financial settlement are separate states.
Merchant response windows are not universal: American Express tells merchants to
use the **reply-by date displayed in the specific case**, and notes that a
missed deadline can result in a chargeback.[2] Its optional U.S. Accelerated
Dispute Resolution program may provide up to **8 calendar days**, but that must
not be applied to all disputes.[3]

## 5. Data model & correctness

```text
DisputeCase
  case_id (PK), external_case_id (UNIQUE per network)
  original_payment_id, merchant_id, cardholder_reference
  disputed_amount_minor, currency, reason_code
  case_type, status, reply_by_at, version
  created_at, updated_at

CaseEvent
  case_event_id (PK), case_id, external_event_id (UNIQUE where applicable)
  event_type, actor_id, occurred_at, recorded_at, payload_ref

Evidence
  evidence_id (PK), case_id, object_key, file_hash, version
  uploaded_by, uploaded_at, scan_status, submission_status

FinancialAdjustment
  adjustment_id (PK), case_id, original_payment_id
  external_adjustment_ref (UNIQUE where applicable)
  amount_minor, currency, direction, status, ledger_journal_id

WorkflowTask
  task_id (PK), case_id, action, due_at, status, attempt_count
```

**Correctness rules:**

1. Every dispute links to an authoritative original payment; do not assume each
   payment permits only one case. Enforce **network-defined uniqueness**, reason
   and amount eligibility rules.
2. Record each external event once (inbox/dedup), even when callbacks are
   retried or arrive out of order.
3. State transitions must be valid and version-checked. Keep an immutable
   event/audit history even when current status changes.
4. Never automatically issue a second full credit if a refund was already
   issued. Cross-reference refund, dispute, payment, and adjustments. Resolve
   overlaps according to applicable policy rather than simply rejecting every
   legitimate dispute.
5. Post financial effects only for a valid *financial adjustment instruction or
   confirmed accounting event*, not merely because an agent clicked **Close**.
   Use a unique adjustment identity and **balanced ledger journal**; use a new
   compensating journal for reversals, not edits to old entries.

## 6. Failure handling, scalability & security

| Failure / risk                       | Response                                                                             |
|--------------------------------------|--------------------------------------------------------------------------------------|
| Duplicate dispute message or webhook | Deduplicate by network-scoped external identifiers and event IDs                     |
| Merchant submits evidence twice      | Version evidence; idempotent submission; preserve first confirmed external reference |
| Network call times out               | Mark outcome **UNKNOWN**, query/reconcile before creating another external action    |
| Evidence object upload fails         | Keep case open, reject incomplete submission, alert and allow safe retry             |
| Workflow engine crashes              | Restore durable task state; resume from latest committed checkpoint                  |
| Deadline approaching                 | Persistent reminders and escalation; prioritize tasks by true `reply_by_at`          |
| Deadline passes                      | Enforce policy-defined next state; record breach and resulting financial outcome     |
| Two agents make conflicting updates  | Optimistic concurrency and permissions by role                                       |
| Processor/network financial mismatch | Reconciliation queue and human exception handling                                    |
| Duplicate adjustment notification    | Unique financial event ID prevents duplicate ledger entries                          |

**Scalability:** Scale API workers, evidence uploads and case-processing workers
independently. Index by merchant, case status and reply-by date. Partition large
case-event histories by retention/access needs. Durable schedulers can bucket
tasks by due time, but must be backed by persistent state; a process-local timer
is not sufficient.

**Security:** Enforce cardholder/merchant/agent authorization at the **case and
document level**, not just at login. Use encrypted object storage, scoped/signed
access, malware scanning, retention/deletion controls, access audit logs and
least-privilege integration identities. Keep unnecessary PANs and sensitive card
data out of cases and logs. Follow applicable PCI DSS requirements for systems
in scope.[4]

## 7. Five key points to remember

1. **Dispute is not refund:** An inquiry may resolve without chargeback; an
   upfront chargeback can create a financial adjustment before evidence review.
2. **Durable workflow is central:** Human review, evidence and deadlines make
   this a long-running state machine, not one API transaction.
3. **Use the case-specific deadline:** Persist, monitor and escalate based on
   `reply_by_at`; never hardcode one universal response window.
4. **Idempotency plus reconciliation:** External acknowledgments and timeouts
   are uncertain; prevent duplicate case events and ledger postings.
5. **Audit every decision and financial effect:** Immutable history, protected
   evidence, role-based access and balanced adjustments.

## 8. Interview closing summary

> I would build a Dispute Management System around a relational case store and
> durable workflow orchestration, because chargebacks are long-running,
> deadline-sensitive business processes. The platform would validate the
> original
> transaction, distinguish inquiries from upfront chargebacks, collect secure
> versioned evidence, and track the actual case reply-by deadline. I would
> isolate
> network integrations behind adapters, use an outbox and idempotent consumers
> for
> reliable asynchronous messaging, and apply explicit state transitions with
> concurrency control. Financial adjustments would be posted through a
> separately
> controlled, auditable ledger interface and reconciled against external
> records.
> The design would scale case work independently while protecting cardholder
> information and preventing duplicate refunds or financial postings.

---

## Official sources

1. [American Express — Managing Disputes as Merchants](https://www.americanexpress.com/us/merchant/tpp/manage-disputes.html) —
   inquiry versus upfront chargeback.
2. [American Express — Managing a Dispute Case](https://www.americanexpress.com/us/merchant/support-center/disputes/managing-a-disputes-case.html) —
   case details and reply-by deadline.
3. [American Express — Accelerated Dispute Resolution factsheet](https://www.americanexpress.com/content/dam/amex/us/merchant/pdf/manage-disputes/Amex_ADR_Factsheet.pdf) —
   optional program and up-to-eight-day response window.
4. [PCI Security Standards Council — Document Library](https://www.pcisecuritystandards.org/document_library/) —
   current PCI DSS materials.

> Sources describe public products and merchant processes, not American
> Express's private system architecture. Design components and data models above
> are illustrative.

---

## Reusable prompt — Design 9: P2P Money Transfer System

Continue with **Design 9 — P2P Money Transfer System**.

Use our standard **10-minute system design interview template** for an American
Express Solution Architect position.

Cover:

1. **Problem & Requirements** — P2P transfers, internal vs. external transfers,
   balances, fees, limits and fraud controls.
2. **High-Level Architecture** — Simple ASCII diagram with components and
   responsibilities.
3. **Key Design Decisions — With Reasons** — Synchronous initiation vs.
   asynchronous completion, relational ledger, double-entry posting,
   idempotency, atomic transfers, external rail integration, and orchestration
   vs. choreography.
4. **End-to-End Request Flow** — From authenticated transfer request to balance
   reservation, posting, settlement confirmation and notification.
5. **Data Model & Correctness** — Transfer records, immutable ledger journals,
   concurrency, double spending prevention, limits, reconciliation and
   compensating entries.
6. **Failure Handling, Scalability & Security** — Retries, timeouts, uncertain
   outcomes, duplicate transfers, external settlement failures, fraud/KYC/AML
   controls, encryption and audit.
7. **Five Key Points to Remember** — Concise and interview-focused.
8. **Interview Closing Summary** — One strong paragraph.

For every key architectural decision, explain **what we choose, why, and the
main trade-off**. Introduce concepts briefly where used. Use official sources
for material claims and do not assume American Express internal architecture.
Avoid repeating fundamentals already covered. **No assessments.**

**At the end, print the complete reusable prompt for Design 10 — Recurring
Billing System**, using the same structure.
