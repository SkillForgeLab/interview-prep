# Design 10 — Recurring Billing System

**10-minute system design interview answer | American Express Solution Architect
preparation**

**Core challenges:** Billing correctness, durable scheduling, idempotency,
failed-payment recovery, distributed state management, and financial
reconciliation.

> **Scope:** Illustrative architecture, not American Express's internal
> implementation. Payment and financial requirements depend on provider,
> network,
> jurisdiction, and product rules.

## 1. Problem & Requirements

Design a system that automatically bills customers for subscriptions and
collects payments on recurring schedules.

**Functional requirements**

- Create, update, pause, and cancel subscriptions.
- Manage plans, prices, billing cycles, and payment methods.
- Generate one intended recurring invoice per billable period.
- Collect payments and track payment status.
- Retry eligible failed payments and notify customers.
- Maintain financial records and perform reconciliation.

| Fixed recurring billing    | Usage-based billing                             |
|----------------------------|-------------------------------------------------|
| Example: $20/month         | Example: $0.10/API call                         |
| Amount known from the plan | Amount calculated from recorded and rated usage |
| Invoice uses plan price    | Invoice uses finalized usage for the period     |

A subscription may combine fixed fees and usage-based charges.

**Non-functional requirements:** Strong correctness for invoices and payment
obligations; durable scheduling; high availability; eventual consistency for
notifications and reporting; protection of payment credentials and customer
data.

**Assumption:** The system owns subscriptions and invoices but integrates with a
payment provider/network to collect card payments.

## 2. High-Level Architecture

```text
               Customer / Admin
                      |
                 API Gateway
                      |
              Subscription Service
                |           |
                v           v
             SQL DB    Billing Scheduler
                ^           |
                |           v
                |     Billing Service
                |           |
                |           v
                |     Invoice Service
                |           |
                |           v
                |     Payment Service
                |           |
                |           v
                |     Payment Provider
                |           |
                |       Result / Webhook
                |           |
                +-----------+
                |
                v
           Financial Ledger
                |
                v
        Transactional Outbox
                |
                v
            Event Broker
                |
                v
        Notification Service
```

This diagram shows logical responsibilities, not necessarily separately deployed
microservices. The payment and ledger workflows should use persisted state
rather than depend on one in-memory chain of calls.

| Component            | Responsibility                                                |
|----------------------|---------------------------------------------------------------|
| Subscription Service | Plan selection, lifecycle, consent, billing rules             |
| Billing Scheduler    | Finds billing periods that are due                            |
| Billing Service      | Coordinates invoicing and collection workflow                 |
| Invoice Service      | Calculates prices, usage, tax, and finalized invoices         |
| Payment Service      | Creates payment intents; handles provider results and retries |
| Financial Ledger     | Immutable, balanced accounting postings                       |
| SQL Database         | Durable subscription, invoice, billing-period, payment states |
| Event Broker         | Asynchronous downstream event distribution                    |
| Notification Service | Invoice notices, receipts, reminders, payment failures        |

**Key design principle:** The scheduler triggers a workflow; it does **not**
directly charge the card. Every worker rechecks authoritative subscription and
invoice state before proceeding.

## 3. Key Design Decisions — With Reasons

| Decision                       | Choice                                                                  | Why / Main trade-off                                                                                 |
|--------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| SQL vs. NoSQL                  | **SQL for core billing**                                                | Transactions and uniqueness support correctness. NoSQL may suit some high-scale auxiliary workloads. |
| Cron vs. distributed scheduler | **Distributed, DB-backed scheduler**                                    | Durable due dates, failover, missed-job recovery; more complex than cron.                            |
| Exactly-once billing effect    | **Idempotency + uniqueness constraints**                                | Duplicate delivery must not create duplicate invoices or charges.                                    |
| Lifecycle states               | **Separate subscription, invoice, payment**                             | A failed payment is not the same as a canceled subscription.                                         |
| ACID vs. Saga                  | **Local ACID; cross-service Saga**                                      | Cannot atomically commit the provider charge and our databases.                                      |
| Financial recording            | **Double-entry ledger**                                                 | Balanced, traceable postings; needs explicit accounting rules.                                       |
| Consistency                    | **Strong for money-affecting decisions; eventual for downstream views** | Protect correctness without blocking on notifications/reporting.                                     |
| Synchronous vs. asynchronous   | **Sync customer commands; async recurring work**                        | No customer session is needed when the scheduled cycle runs.                                         |
| Payment retries                | **Bounded retries, backoff, dunning**                                   | Recover eligible failures while avoiding uncontrolled recharges.                                     |
| Events                         | **Broker + transactional outbox**                                       | Durable publishing without unsafe database/broker dual writes.                                       |
| Time zones                     | **Business-local recurrence; UTC execution instant**                    | Define month-end and daylight-saving behavior explicitly.                                            |
| Plan changes                   | **Versioned pricing, effective dates, explicit proration**              | Historical invoices remain explainable.                                                              |

### Decision A. Why a distributed scheduler?

A single-process cron job can miss work during downtime, while multiple
uncoordinated cron instances can execute the same job.

```text
Subscription DB (next_billing_at)
             |
             v
     Distributed Scheduler
             |
             v
       Due Billing Periods
             |
             v
         Worker Pool
             |
             v
       Generate Invoice
```

Store `next_billing_at` and billing-period state durably. Workers claim due work
with transactional leases/locks. A recovery scanner finds overdue cycles after
an outage. **Assume at-least-once job execution**, even with managed scheduling.

### Decision B. How do we prevent duplicate invoices and charges?

For standard recurring invoices, use a stable identity such as:

```text
(subscription_id, billing_period_id, invoice_type)
```

Enforce it using a database `UNIQUE` constraint. Create/update the
billing-period record and invoice atomically.

Separately create **one logical payment intent per invoice**, with stable
provider idempotency references. Each *legitimate* collection attempt also has
its own identity.

- Duplicate scheduler execution: find the existing invoice; do not create
  another.
- Duplicate payment initiation: reuse the existing payment-intent/result as
  appropriate.
- Provider timeout: reconcile the original attempt; **do not blindly launch a
  new charge**.

Exactly-once **business effects** come from durable identity and idempotency,
not an assumption of exactly-once network delivery.

### Decision C. Why three separate lifecycle states?

| Entity          | Example states                         | Meaning                                     |
|-----------------|----------------------------------------|---------------------------------------------|
| Subscription    | ACTIVE, PAST_DUE, PAUSED, CANCELED     | Customer's service and billing relationship |
| Invoice         | DRAFT, OPEN, PAID, VOID, UNCOLLECTIBLE | Amount owed and collection status           |
| Payment attempt | PENDING, SUCCEEDED, FAILED, UNKNOWN    | Outcome of one collection attempt           |

Example: `Subscription = PAST_DUE`, `Invoice = OPEN`, `Payment = FAILED`. A
grace period may preserve access. One status field cannot represent all three
lifecycles safely.

### Decision D. Why ACID locally but a Saga across services?

- **ACID transaction:** Atomically claim a billing period and create its invoice
  or commit related local state.
- **Saga:** Persist and coordinate steps across invoice, payment provider, and
  ledger services, each with retries and recovery.

```text
Create Invoice -> Initiate Payment -> Verify Outcome
        -> Record Ledger Posting -> Update Status
```

The external provider cannot join our local database transaction. If a payment
succeeds but ledger posting fails, **preserve the successful payment and recover
ledger posting**; never charge again simply to compensate for a bookkeeping
failure. Some true business reversals may require an explicit refund, not a
database rollback.

### Decision E. Why bounded retries and dunning?

**Exponential backoff** increases delay between retries; add jitter to avoid
synchronized spikes. **Dunning** is recovery of unpaid invoices through
permitted retries, notices, payment-method updates, and service policy.

| Outcome                                 | Action                                                    |
|-----------------------------------------|-----------------------------------------------------------|
| Transient technical error               | Bounded safe retry with backoff                           |
| Provider timeout or unknown result      | Query/reconcile the original payment before retrying      |
| Hard decline or authentication required | Follow provider/network rules and request customer action |
| Repeated eligible failures              | Dunning/grace period, then policy-based service change    |
| Customer revokes consent                | Stop new unauthorized recurring charges                   |

### Decision F. Why versioned plans and explicit billing-time rules?

Store billing timezone, billing anchor, recurrence rule, and UTC
`next_billing_at`. Explicitly decide how the 29th–31st map to shorter months,
and how daylight-saving changes are handled.

For mid-cycle upgrades/downgrades, create policy-based prorations (credit unused
old-plan service; charge remaining new-plan service) or defer the change to the
next cycle. Keep historical plan/price versions attached to invoices. Treat
immediate cancellation, end-of-period cancellation, and payment-consent
withdrawal as distinct concepts.

## 4. End-to-End Request Flow

### Successful recurring cycle

```text
1. Customer creates subscription; consent recorded
                       |
2. Store plan version, timezone, billing anchor
                       |
3. Scheduler finds due billing period
                       |
4. Claim period; check status/cancellation/consent
                       |
5. Finalize usage if applicable; create unique invoice
                       |
6. Create/reuse payment intent; initiate payment
                       |
7. Verify provider result / signed webhook
                       |
8. Persist payment result; update invoice state
                       |
9. Post idempotent, balanced ledger entries
                       |
10. Update subscription state and next due date
                       |
11. Publish events; send notification
```

These are logical steps, not one long distributed transaction. After payment,
the workflow can continue asynchronously using persisted states and outbox
events.

**Usage-based addition:** Deduplicate meter events, aggregate usage, apply the
cutoff/rating policy, then finalize the invoice. Late data needs a defined
adjustment policy.

### Failed-payment recovery

```text
Payment Attempt
      |
      v
FAILED or UNKNOWN
      |
      +-- UNKNOWN --> Query provider / reconcile
      |
      v
Classify actual outcome
      |
      +-- Eligible retry --> Backoff --> Retry safely
      |
      +-- Needs action ----> Notify customer
      |
      v
Dunning / Grace Period
      |
      +-- Recovered -------> Invoice PAID
      |
      +-- Unresolved ------> Apply subscription policy
```

A request timeout is **not proof of payment failure**. Before another charge,
resolve whether the previous attempt succeeded, failed, or remains unknown.

## 5. Data Model & Correctness

| Entity                             | Essential fields                                                                                                                 |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `BillingPlan`                      | `plan_id`, `version`, `price`, `currency`, `interval`, `billing_type`                                                            |
| `Subscription`                     | `subscription_id`, `customer_id`, `plan_version`, `status`, `timezone`, `billing_anchor`, `next_billing_at`, `consent_reference` |
| `BillingPeriod`                    | `period_id`, `subscription_id`, `start_at`, `end_at`, `status`, `version`                                                        |
| `Invoice`                          | `invoice_id`, `period_id`, `amount`, `currency`, `status`, `finalized_at`                                                        |
| `PaymentIntent` / `PaymentAttempt` | `invoice_id`, `intent_id`, `attempt_id`, `provider_reference`, `idempotency_key`, `status`                                       |
| `JournalEntry`                     | `journal_id`, `posting_reference`, `account_id`, `debit`, `credit`, `currency`                                                   |
| `Outbox`                           | `event_id`, `aggregate_id`, `event_type`, `payload`, `published_at`                                                              |

**Core invariants**

1. One intended standard recurring invoice per
   `(subscription, period, invoice type)`; adjustments have separately
   identified documents.
2. Retries never create an extra successful charge for the same payment
   obligation.
3. Every posted journal transaction balances, with unique financial posting
   identity.
4. Finalized invoices are not silently rewritten; use credit notes or
   adjustments.
5. Cancellations and payment-consent constraints are enforced at initiation,
   including races with due jobs.

**Consistency across services:** Local ACID updates + transactional outbox +
persisted idempotent Saga/workflow + reconciliation against provider outcomes
and ledger postings.

**Illustrative financial posting** when a previously recognized customer
receivable is collected:

```text
Debit   Processor Clearing Receivable    $20
Credit  Customer Receivable              $20
```

Later, confirmed settlement moves the amount from clearing to cash, with
applicable fees/adjustments. Actual accounting depends on the product and
processing model. Maintain a unique posting reference and do not equate payment
authorization with settled cash.

## 6. Failure Handling, Scalability & Security

| Failure/scenario               | Handling                                              | Why                                   |
|--------------------------------|-------------------------------------------------------|---------------------------------------|
| Scheduler crashes              | Durable due dates; another worker resumes             | Do not lose billing cycles            |
| Duplicate job                  | Uniqueness + idempotent workflow                      | Prevent duplicate invoices            |
| Missed period                  | Recovery scan for overdue periods                     | No silent gaps                        |
| Provider timeout               | UNKNOWN state; query and reconcile before retry       | Avoid double charging                 |
| Payment succeeds, ledger fails | Record success; retry/reconcile ledger posting        | Do not charge again                   |
| Database failure               | Rollback, durable replication, tested recovery        | Preserve correctness                  |
| Broker outage                  | Persist event in transactional outbox                 | No missing downstream events          |
| Poison message                 | Bounded retries, dead-letter queue, controlled replay | Isolate repeated failures             |
| Traffic spike                  | Partition worker queues by subscription; backpressure | Scale without double execution        |
| Provider throttles             | Rate limits and bounded concurrency                   | Avoid overload and cascading failures |
| Reconciliation mismatch        | Alert, investigate, repair with auditable corrections | Detect inconsistent systems           |

**Scaling:** Stateless services and distributed workers scale horizontally.
Partition scheduling and job queues by subscription. Keep invoice uniqueness and
account/payment ownership coordinated. Stagger due times where business rules
permit; do not move contractual billing dates merely for convenience.

**Security:** Authenticate APIs, enforce customer-level authorization, protect
consent evidence, encrypt sensitive data, tokenize stored payment methods, and
verify provider webhook signatures. Keep raw payment card credentials out of the
general billing store. Determine PCI DSS scope from actual data flows and system
connections, and follow restrictions on storing sensitive authentication data.

**Operational metrics:** Missed/late periods, billing lag, duplicate-prevention
conflicts, payment unknown-state age, retry recovery, outbox backlog,
reconciliation mismatches, and DLQ depth.

## 7. Five Key Points to Remember

1. **Durable scheduling:** Database owns due dates; jobs may execute more than
   once and must be replay-safe.
2. **Idempotency:** Unique invoice identities and stable payment references
   prevent duplicate financial effects.
3. **Separate states:** Subscription, invoice, payment, and ledger lifecycles
   are distinct.
4. **ACID + Saga:** Use local transactions for correctness; durable
   orchestration for cross-service recovery.
5. **Reconciliation:** Match invoices, provider payments, and ledger postings;
   never infer failure from a timeout.

## 8. Interview Closing Summary

> I would design recurring billing around a durable subscription database,
> distributed scheduler, invoice service, and idempotent payment orchestration.
> Scheduler jobs may execute more than once, but each billing period must
> produce
> only its intended invoice and payment obligations. SQL transactions and unique
> constraints provide local correctness, while a durable Saga coordinates
> payment
> and ledger services. A transactional outbox publishes reliable downstream
> events. Payment failures require bounded retries, dunning, and explicit
> handling
> of unknown outcomes. I would maintain separate lifecycle states, enforce
> cancellation and consent rules, and reconcile invoices, provider charges, and
> ledger postings to ensure financial accuracy.

## Official Reference Material

- **American Express Merchant Regulations** — recurring transaction consent,
  disclosure, and cancellation obligations (network- and market-specific rules
  apply).
- **AWS EventBridge Scheduler documentation** — delivery/retry behavior and
  durable scheduling
  patterns: https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html
- **AWS Transactional Outbox pattern** — atomic local state and event
  publication: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- **Stripe Billing: Smart Retries** — provider-specific retry/dunning
  examples: https://docs.stripe.com/billing/revenue-recovery/smart-retries
- **Stripe Billing: Prorations** — provider-specific plan-change
  examples: https://docs.stripe.com/billing/subscriptions/prorations
- **PCI Security Standards Council Document Library** — PCI DSS and related
  guidance: https://www.pcisecuritystandards.org/document_library/

*These references describe published standards and product patterns; they do not
establish American Express's internal design.*
