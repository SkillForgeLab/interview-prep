# Design 8 — Chargebacks & Dispute Management System

**Format:** 10-minute system design interview answer  
**Role:** Solution Architect (American Express context)  
**Focus:** Workflow reliability, deadlines, financial correctness, evidence,
network integration  
**Note:** Illustrative design, not a description of American Express internal
architecture.

## 1. Problem & Requirements

Design a system where cardholders dispute card transactions, merchants provide
evidence, and an issuer/network disputes function investigates and reaches an
outcome.

**Functional requirements**

- Open a dispute against an eligible transaction with a reason and amount.
- Support inquiries and chargebacks, merchant notifications, evidence uploads,
  review, decisions, and permitted appeals/reopenings.
- Track case-specific deadlines and outcomes, including chargeback upheld or
  reversed, partial resolution, or closure without a chargeback.
- Apply financial credits, debits, and reversals through the financial ledger.
- Maintain a complete case history.

**Non-functional requirements**

- Durable, long-running workflows; reliable deadline handling.
- No duplicate financial adjustments; recover from uncertain external outcomes.
- Strong auditability, controlled access to PII and evidence.
- Scalable case processing and document storage.

**Refund vs. chargeback:** A refund is generally a merchant-authorized return of
funds through an ordinary credit transaction. A chargeback is a dispute-related
financial adjustment under applicable payment-network rules; it can result in a
debit to the merchant and credit to the cardholder. **A dispute does not
necessarily result in a chargeback.** American Express describes both *inquiry*
and *upfront chargeback*
paths. [Official American Express guide](https://www.americanexpress.com/us/merchant/tpp/manage-disputes.html).

**Key assumption:** Our platform integrates with existing payment,
payment-network, and authoritative accounting systems. Deadlines and available
dispute paths come from the applicable network/product rules, not hardcoded
universal values.

## 2. High-Level Architecture

```text
         Cardholder / Merchant Portal
                      |
                      v
                API Gateway
                      |
                      v
                Dispute Service
                 /          \
                v            v
       Payment/Transaction  Case Management
            Service          |     \
                             |      v
                             |   Case DB
                             v
                       Workflow Engine
                        /     |     \
                       v      v      v
                  Deadline  Evidence  Network
                  Scheduler  Store    Integration
                              |         |
                         Object Store   v
                                     External Network
                             |
                             v
                      Financial Ledger
                             |
                             v
                    Outbox / Event Broker
                             |
                      Notifications / BI
```

**Responsibilities:**

- **Dispute Service:** API, validation, eligibility, request deduplication.
- **Case Management:** case records, state, reason code, decisions, history.
- **Workflow Engine:** durable steps, waits, retries, escalations.
- **Deadline Scheduler:** persistent timers and overdue reconciliation.
- **Evidence Store:** protected documents in object storage; metadata in case
  DB.
- **Payment Service:** authoritative transaction references, refunds and other
  related adjustments.
- **Network Adapter:** protocol mapping, message correlation, acknowledgement
  and retry handling.
- **Ledger:** authoritative financial postings and reversals, each with a
  durable operation ID.

## 3. Key Design Decisions — What, Why, Trade-off

| Decision              | Choice                                           | Why                                                               | Main trade-off                          |
|-----------------------|--------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------|
| Workflow coordination | **Durable orchestration**                        | One coordinated view of multi-step, long-lived case and deadlines | Central workflow ownership/operations   |
| Interactions          | **Synchronous API + asynchronous investigation** | Acknowledge case intake promptly; merchant responses take time    | Eventual consistency across services    |
| Transactional storage | **Relational case DB**                           | Constraints, joins, controlled transitions and deadlines          | Scaling and schema management           |
| Case lifecycle        | **Persisted state machine**                      | Explicit valid transitions; resume after crashes                  | Lifecycle/rule versioning complexity    |
| Evidence              | **Object storage + metadata DB**                 | Large documents without bloating DB                               | Two-system upload/metadata coordination |
| Deadlines             | **Durable timers + periodic scans**              | Recover missed jobs and avoid silent expiry                       | Duplicate-safe execution required       |
| Deduplication         | **Scoped unique operation IDs**                  | Prevent repeated intake/actions/postings                          | Correct identity varies by operation    |
| Events                | **Outbox + event broker**                        | Reliable notification/reporting after case commits                | Consumers need idempotency              |
| Network integration   | **Dedicated adapter**                            | Isolate external fields, acknowledgements and retries             | Additional integration layer            |

**Why orchestration rather than choreography?** Events between autonomous
services are useful, but a dispute needs authoritative knowledge of case stage,
evidence status, reply-by time, and permitted next action. A durable workflow
engine makes this easier to inspect, retry, and recover.

**State-machine concept:** Persist a state and enforce permitted transitions (
for example
`OPEN → VALIDATED → INQUIRY_PENDING → EVIDENCE_RECEIVED → REVIEW → DECIDED → FINANCIAL_RECONCILIATION → CLOSED`).
This is illustrative, not a network-mandated sequence. An upfront chargeback may
post before the evidence review.

**Deadlines:** Store the actual rule-derived **reply-by date** with case stage
and rule version. Execute reminders/escalations with durable timers and recheck
overdue cases using a separate scan. American Express merchant guidance says
merchants must respond by the displayed reply-by date and may incur a chargeback
if they do not support the charge in
time. [Official case guidance](https://www.americanexpress.com/us/merchant/support-center/disputes/managing-a-disputes-case.html).

## 4. End-to-End Request Flow

1. **Open case:** Cardholder submits transaction reference, reason, disputed
   amount, and evidence.
2. **Validate:** Verify ownership, original charge, eligible amount, refunds,
   previous disputes, and relevant rules.
3. **Create durable case:** Assign case ID, capture policy/rule version,
   deadlines, and idempotency identity; start workflow.
4. **Choose allowed path:** Resolve directly, request merchant inquiry, or apply
   an upfront chargeback when rules allow.
5. **Notify merchant / collect evidence:** Use network adapter; verify uploads
   are durable and secure before marking `SUBMITTED`.
6. **Review:** Evaluate evidence, assess deadlines, and persist an auditable
   decision.
7. **Post adjustments:** Request idempotent ledger debit/credit/reversal as
   needed; track pending/confirmed result. Account for existing refunds and
   credits.
8. **Close:** Confirm external acknowledgements and postings, notify parties,
   preserve case/evidence/decision history.

**Possible outcomes:** inquiry resolved without chargeback; chargeback upheld;
chargeback reversed after sufficient evidence; partial resolution;
withdrawn/closed without new adjustment. Financial outcomes depend on what has
already been posted.

## 5. Data Model & Correctness

| Entity                | Key fields                                                                                              |
|-----------------------|---------------------------------------------------------------------------------------------------------|
| `Dispute`             | `case_id`, `payment_id`, `network_case_id`, `reason_code`, `disputed_amount_minor`, `status`, `version` |
| `CaseDeadline`        | `case_id`, `stage`, `reply_by_at`, `rule_version`, `action_status`                                      |
| `Evidence`            | `evidence_id`, `case_id`, `object_key`, `checksum`, `object_version`, `submitted_at`, `classification`  |
| `DecisionHistory`     | `decision_id`, `case_id`, `old_state`, `new_state`, `actor`, `occurred_at`                              |
| `FinancialAdjustment` | `operation_id`, `case_id`, `type`, `amount_minor`, `ledger_id`, `status`                                |
| `Outbox`              | `event_id`, `case_id`, `event_type`, `published_at`                                                     |

**Correctness rules:**

- **No duplicate case operation:** use scoped network/case/step identity; do *
  *not** assume one dispute per payment for all time.
- **No duplicate money movement:** the ledger enforces uniqueness by financial
  operation ID.
- **No conflicting transitions:** optimistic version check / transactional
  compare-and-update.
- **Immutable audit:** append decision events and retain evidence versions, not
  silent overwrites.
- **Do not close prematurely:** an outcome decision and a confirmed financial
  posting are different states.

## 6. Failure Handling, Scalability & Security

| Failure                        | Response                                                                       | Why                                          |
|--------------------------------|--------------------------------------------------------------------------------|----------------------------------------------|
| Missed deadline timer          | Periodic overdue scan, alert, re-evaluate state before action                  | Avoid silently missing business deadline     |
| Duplicate events               | Idempotent handlers, unique operation IDs                                      | No repeated case action or financial posting |
| Network timeout                | Persist `PENDING`; reconcile status before safe retry                          | Timeout ≠ failed external operation          |
| Evidence upload fails          | Do not mark `SUBMITTED`; retry/cleanup orphan files                            | Prevent false proof of submission            |
| Two reviewers act concurrently | Versioned state transition                                                     | Reject incompatible decisions                |
| Ledger response lost           | Requery by operation ID; do not blindly repost                                 | Prevent duplicate debit/credit               |
| Traffic spike                  | Horizontal API workers, indexed case queries, partitioned workflow work        | Scalable without changing correctness        |
| Sensitive evidence leak        | Encryption, least-privilege access, time-limited URLs, audit and malware scans | Protect PII and uploaded content             |

**Operational metrics:** overdue/near-deadline cases, evidence failures, failed
workflow activities, network acknowledgement lag, unconfirmed ledger
adjustments, and reconciliation differences.

**Compliance:** Apply PCI DSS where payment-account data is within scope; follow
relevant legal rules and approved retention
schedules. [PCI SSC official library](https://www.pcisecuritystandards.org/document_library/).

## 7. Five Key Points to Remember

1. **Long-running workflow → durable orchestration**, not one synchronous
   request.
2. **Deadlines are financial controls → persisted timers plus independent
   deadline reconciliation.**
3. **Case decision ≠ ledger posting → independent confirmed, idempotent
   financial operation.**
4. **Evidence and history must be auditable → object versioning + append-only
   decision trail.**
5. **Network integration is unreliable/variable → isolated adapter,
   acknowledgements, retries and reconciliation.**

## 8. Interview Closing Summary

> I would design dispute management as a durable, deadline-driven workflow
> backed by a relational case store. The Dispute Service manages eligibility,
> while a workflow engine coordinates merchant inquiries, evidence, review and
> case-specific deadlines. Evidence lives in protected object storage, and a
> network adapter isolates external protocols and acknowledgements. Any
> chargebacks or reversals go through an authoritative ledger using unique
> operation IDs to avoid duplicate financial effects. Persistent timers with
> independent overdue scans, immutable decision history, reconciliation, and
> role-based security make the system reliable and auditable.

## Official Sources

- [American Express — Managing Disputes as Merchants](https://www.americanexpress.com/us/merchant/tpp/manage-disputes.html)
- [American Express — Managing a Dispute Case](https://www.americanexpress.com/us/merchant/support-center/disputes/managing-a-disputes-case.html)
- [American Express — Disputes Summary Table](https://www.americanexpress.com/us/merchant/support-center/disputes/disputes-summary-table.html)
- [PCI SSC — Document Library](https://www.pcisecuritystandards.org/document_library/)
