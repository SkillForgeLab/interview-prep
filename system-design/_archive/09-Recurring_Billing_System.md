# Design 10 — Recurring Billing System

**10-minute system design interview | American Express Solution Architect
preparation**

**Core challenges:** Billing correctness, durable scheduling, idempotency,
failed-payment recovery, distributed state management, and financial
reconciliation.

> **Scope:** An illustrative architecture, not American Express's internal
> implementation. Specific card-network and payment-provider rules depend on the
> applicable agreement.

## 1. Problem & Requirements

Design a system that automatically bills customers for subscriptions and
collects payments on recurring schedules.

**Functional requirements**

- Create, update, pause, and cancel subscriptions.
- Manage plans, prices, billing cycles, and payment methods.
- Generate one invoice per billable period.
- Collect payments and track their status.
- Retry eligible failed payments and notify customers.
- Maintain financial records and reconciliation.

**Fixed vs. usage-based billing**

| Fixed recurring             | Usage-based                                 |
|-----------------------------|---------------------------------------------|
| $20 per month               | $0.10 per API call                          |
| Amount known before billing | Requires usage aggregation and rating       |
| Invoice uses plan price     | Invoice uses finalized usage for the period |

Both models can be combined in one subscription.

**Non-functional requirements:** Strong correctness for invoices and payments;
durable scheduling; high availability; eventual consistency for notifications
and reporting; secure payment credentials.

**Key assumption:** The system owns subscriptions and invoices but integrates
with a payment provider or payment-network service for collecting card payments.

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
                |       Result/Webhook
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

*Logical view: Service workflows communicate through durable state and events.
The diagram does not imply all actions are in one database transaction or that
ledger posting must precede every event.*

| Component            | Responsibility                                           |
|----------------------|----------------------------------------------------------|
| Subscription Service | Plan selection, lifecycle, consent, billing rules        |
| Billing Scheduler    | Finds periods due for billing                            |
| Billing Service      | Coordinates invoice creation and payment collection      |
| Invoice Service      | Calculates amounts, taxes, and finalizes invoices        |
| Payment Service      | Initiates payments, handles provider results and retries |
| Financial Ledger     | Immutable, balanced financial postings                   |
| SQL Database         | Durable subscription, period, invoice, and payment state |
| Event Broker         | Delivers downstream events asynchronously                |
| Notification Service | Sends invoices, receipts, failures, and reminders        |

**Critical point:** The scheduler does not directly charge cards. It triggers an
idempotent billing workflow that checks the authoritative subscription and
period state.

## 3. Key Design Decisions — With Reasons

| Decision                       | Choice                                                      | Why / Main trade-off                                                                               |
|--------------------------------|-------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| SQL vs. NoSQL                  | **SQL** for core billing                                    | Transactions, uniqueness, and lifecycle consistency; NoSQL may suit selected high-scale workloads. |
| Cron vs. distributed scheduler | **Distributed, DB-backed scheduler**                        | Multiple workers, failover, and recovery of missed jobs; more complexity than cron.                |
| Exactly-once billing effect    | **Idempotency + unique constraints**                        | Duplicate job delivery must not cause duplicate invoices or charges.                               |
| State management               | **Separate subscription, invoice, payment states**          | A failed payment does not necessarily mean a subscription is canceled.                             |
| ACID vs. Saga                  | **ACID locally; Saga across services**                      | A local database transaction cannot atomically commit an external payment-provider operation.      |
| Ledger                         | **Double-entry accounting**                                 | Traceable, balanced posting; requires defined journal rules.                                       |
| Consistency                    | **Strong for billing decisions; eventual downstream**       | Protect financial effects while decoupling reporting/notifications.                                |
| Sync vs. async                 | **Sync for customer commands; async for scheduled billing** | Billing should continue even when the customer is offline.                                         |
| Payment retries                | **Bounded backoff + dunning**                               | Recover transient failures without repeated unintended charges.                                    |
| Messaging                      | **Event broker + transactional outbox**                     | Publish events reliably after local commits.                                                       |
| Billing time                   | **Business timezone + UTC execution instant**               | Correct cycles across daylight-saving transitions.                                                 |
| Plan changes                   | **Versioned rules + effective dates**                       | Keep historical billing explainable.                                                               |

### A. Why a distributed scheduler?

One cron process can miss jobs during outages; multiple unsynchronized cron
workers can run the same job. Store `next_billing_at` and each billing period in
the database. Workers atomically claim due periods, and a recovery scanner finds
overdue work.

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
       Invoice Workflow
```

Schedule delivery should be assumed **at least once**, not exactly once. AWS
EventBridge Scheduler documents at-least-once invocation and configurable retry
policies.
See [AWS EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html).

### B. How do we prevent duplicate invoices and charges?

Create a unique invoice identity such as:

```text
(subscription_id, billing_period_id, invoice_type)
```

Use a database unique constraint. Generate the invoice and mark its period state
in the same local transaction.

For collection, create one stable **payment intent** per invoice. Each real
payment attempt has its own identity; a retry of an uncertain attempt reuses the
appropriate provider idempotency reference. New legitimate attempts must be
distinguished from duplicate deliveries.

**Remember:** Exactly-once *business effect* comes from durable identity, state
checks, constraints, and reconciliation—not a guarantee that a job or message is
delivered once.

### C. Why three separate lifecycle states?

| Entity          | Example states                         | What it represents                       |
|-----------------|----------------------------------------|------------------------------------------|
| Subscription    | ACTIVE, PAST_DUE, PAUSED, CANCELED     | Service and billing relationship         |
| Invoice         | DRAFT, OPEN, PAID, VOID, UNCOLLECTIBLE | Customer's billed obligation             |
| Payment attempt | PENDING, SUCCEEDED, FAILED, UNKNOWN    | Outcome of a specific collection attempt |

Example: `Subscription = PAST_DUE`, `Invoice = OPEN`, `Payment = FAILED`. The
subscription might still be usable during a grace period. A later successful
payment may settle the existing invoice.

### D. ACID vs. Saga

Use **ACID transactions** within a database for invoice creation, unique-period
enforcement, and consistent state updates.

Use a **Saga** or durable workflow to coordinate external payment collection,
ledger posting, and subscription-state changes:

```text
Create Invoice
      |
      v
Initiate Payment
      |
      v
Confirm Provider Result
      |
      v
Post Ledger Entries
      |
      v
Update Billing Status
```

A Saga is not one giant rollback. If payment succeeds but ledger posting fails,
**do not charge again**. Persist the confirmed payment and retry/reconcile the
missing journal posting. Some business failures require compensation, such as
refunds; others require finishing incomplete work.

### E. Retries, exponential backoff, and dunning

- **Exponential backoff:** Increasing delays between attempts, with jitter to
  avoid retry storms.
- **Dunning:** Collection recovery using permitted retries, reminders,
  payment-method updates, and grace-period/service policies.

| Payment outcome                         | Response                                                              |
|-----------------------------------------|-----------------------------------------------------------------------|
| Transient processor failure             | Bounded retry if permitted and safe                                   |
| Timeout; outcome unknown                | Query and reconcile original attempt before initiating another charge |
| Hard decline or authentication required | Follow provider/network rules; prompt customer action                 |
| Repeated eligible failure               | Dunning and policy-based suspension                                   |
| Consent revoked                         | Stop further unauthorized recurring collections                       |

### F. Time zones, billing cycles, and cancellation

Store the **billing timezone**, **billing anchor**, **recurrence rule**, *
*period boundaries**, and next UTC execution instant. Define what monthly
billing on the 29th/30th/31st means when a month lacks that date. Explicitly
handle daylight-saving transitions.

For plan changes, version prices and calculate proration under a defined policy.
For cancellation, distinguish **service access ending now vs. at period end**
from **payment authorization being withdrawn**. Enforce consent and cancellation
rules before launching a new collection, including races with an already queued
billing job.

American Express's published U.S. merchant regulations discuss recurring billing
and cancellation requirements.
See [American Express Merchant Regulations (U.S.)](https://www.americanexpress.com/content/dam/amex/us/merchant/new-merchant-regulations/Regs_EN_US.pdf).

## 4. End-to-End Request Flow

### Successful recurring billing

```text
1. Create subscription + capture consent
                   |
2. Store plan, timezone, next billing date
                   |
3. Scheduler finds due billing period
                   |
4. Claim period; check cancellation/status
                   |
5. Generate unique invoice
                   |
6. Initiate payment with idempotency reference
                   |
7. Receive/verify provider result
                   |
8. Record success and update invoice
                   |
9. Post financial journal entries
                   |
10. Update subscription/billing state
                   |
11. Schedule next billing period
                   |
12. Publish events and notify customer
```

Individual stages persist state so the workflow can resume after a crash. Steps
after external payment may be asynchronous and eventually converge through
reconciliation.

For **usage-based billing**, finalize deduplicated metered usage according to
the period cutoff before invoicing. Define a policy for late usage and
corrections.

### Failed-payment recovery

```text
Payment Attempt
       |
       v
 Failed / Unknown
       |
       +--> UNKNOWN? --> Query provider
       |                 Reconcile outcome
       v
 Classified Failure
       |
       +--> Retry permitted?
       |       |
       |       +-- Yes --> Scheduled retry
       |       |
       |       +-- No ---> Customer action
       v
 Dunning / Grace Period
       |
       +--> Recovered --> Mark invoice PAID
       |
       +--> Unresolved --> Apply service policy
```

**Never treat an unknown payment outcome as a definite failure solely because
the HTTP/network request timed out.**

## 5. Data Model & Correctness

| Entity                  | Essential fields                                                                                                |
|-------------------------|-----------------------------------------------------------------------------------------------------------------|
| BillingPlan             | `plan_id`, `version`, price, currency, interval, billing_type                                                   |
| Subscription            | `subscription_id`, customer, plan_version, status, timezone, billing_anchor, next_billing_at, consent_reference |
| BillingPeriod           | `period_id`, subscription_id, start, end, status, version                                                       |
| Invoice                 | `invoice_id`, period_id, amount, currency, status, finalized_at                                                 |
| PaymentIntent / Attempt | invoice_id, attempt_id, provider_reference, idempotency_key, status                                             |
| JournalEntry            | journal_id, posting_reference, account_id, debit, credit, currency                                              |
| Outbox                  | event_id, aggregate_id, event_type, payload, published_at                                                       |

**Core invariants**

1. One intended recurring invoice per subscription/period/invoice type.
2. Duplicate deliveries and retries cannot create an unintended second
   successful collection for the same obligation.
3. Each posted ledger transaction balances by currency and has a unique
   financial-event reference.
4. Finalized invoices are not silently rewritten; use credit notes/adjustments.
5. Cancellation and payment consent are checked when starting a new payment, not
   only when generating a schedule.

**Consistency approach:** ACID for local invoice/billing-period changes,
transactional outbox for reliable event publication, durable Saga/workflow for
cross-service processing, and reconciliation for eventual convergence.

**Illustrative double-entry posting:** If an invoice is already recorded as a
receivable and a payment is confirmed/captured:

```text
Debit   Processor Clearing Receivable   $20
Credit  Customer Receivable             $20
```

When settlement arrives, move the clearing receivable to cash, with separate
fee/adjustment entries as required. Actual journal rules depend on the
accounting and provider model.

## 6. Failure Handling, Scalability & Security

| Scenario                         | Handling and reason                                                  |
|----------------------------------|----------------------------------------------------------------------|
| Scheduler failure                | Persist due dates; another worker can resume                         |
| Duplicate job                    | Unique period constraint and idempotent workflow                     |
| Missed billing cycle             | Recovery scanner identifies overdue periods                          |
| Provider timeout                 | Keep outcome UNKNOWN; reconcile before retry                         |
| Payment succeeded, ledger failed | Preserve success; retry missing posting safely                       |
| Database failure                 | Transaction rollback, replicated recovery, replay                    |
| Broker outage                    | Retain outbox events for later publication                           |
| Poison message                   | Bounded retry, dead-letter queue, controlled replay                  |
| Billing spike                    | Partition by subscription, spread due work, limit worker concurrency |
| Provider rate limit              | Backpressure and retry limits                                        |
| State mismatch                   | Reconcile invoice, provider payment, and journal records             |

**Security:** Authenticate APIs, enforce customer-level authorization, encrypt
personal data, preserve consent evidence, minimize access, and use payment
tokens rather than raw card data in billing tables. PCI DSS scope depends on how
payment data is stored, processed, transmitted, and connected. See
the [PCI SSC document library](https://www.pcisecuritystandards.org/document_library/).

**Operational metrics:** Overdue billing-period age, missing invoices,
duplicate-prevention conflicts, payment recovery rate, unknown-attempt age,
outbox backlog, reconciliation mismatches, and DLQ depth.

## 7. Five Key Points to Remember

1. **Durable scheduling:** Due dates and billing periods live in persistent
   state; missed jobs can be recovered.
2. **Idempotent billing:** Unique invoices and stable payment identities prevent
   duplicate financial effects.
3. **Separate lifecycle states:** Subscription, invoice, payment, and ledger
   describe different business facts.
4. **ACID locally, Saga across services:** Recover partial failures without
   blindly charging again.
5. **Reconciliation is mandatory:** Compare invoices, provider outcomes, and
   ledger postings, particularly after timeouts.

## 8. Interview Closing Summary

> I would design recurring billing around a durable subscription database,
> distributed scheduler, invoice service, and idempotent payment orchestration.
> The key principle is that scheduler jobs may run more than once, but each
> billing period must produce only its intended invoice and payment obligations.
> I
> would use SQL transactions and unique constraints for local correctness,
> Saga-based workflows across payment and ledger services, and a transactional
> outbox for reliable events. Payment failures require bounded retries, dunning,
> and explicit handling of unknown outcomes. I would also preserve separate
> lifecycle states, enforce cancellation and consent rules, and reconcile
> invoices, provider charges, and ledger postings to ensure financial accuracy.

---

## Official References

- [American Express Merchant Regulations — United States](https://www.americanexpress.com/content/dam/amex/us/merchant/new-merchant-regulations/Regs_EN_US.pdf) —
  recurring billing rules, consent and cancellation handling.
- [AWS EventBridge Scheduler — Overview](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html) —
  at-least-once scheduled delivery and retry behavior.
- [AWS EventBridge Scheduler — Schedule Types](https://docs.aws.amazon.com/scheduler/latest/UserGuide/schedule-types.html) —
  time-zone and daylight-saving-time considerations.
- [AWS EventBridge Scheduler — Failure and DLQ Handling](https://docs.aws.amazon.com/scheduler/latest/UserGuide/managing-schedule.html) —
  retry and dead-letter-queue handling.
- [PCI Security Standards Council — Document Library](https://www.pcisecuritystandards.org/document_library/) —
  official PCI DSS publications.

*This document is for interview preparation. Examples and accounting records are
illustrative, not a description of American Express internal systems.*
