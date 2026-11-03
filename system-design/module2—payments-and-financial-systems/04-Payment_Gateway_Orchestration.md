# Design 6 — Payment Gateway & Orchestration System

*10-minute interview answer · American Express Solution Architect Preparation*

## 1. Problem & Requirements

Design a payment gateway that allows merchants to accept payments through
multiple payment processors, such as Stripe, Adyen, or other supported
providers.

**Functional requirements:**

- Accept payment requests from merchants.
- Select the best eligible payment processor.
- Process authorizations and captures.
- Handle processor failures and retries.
- Prevent duplicate charges.
- Track payment status across providers.
- Support refunds and payment reconciliation.

**Non-functional requirements:**

- **High availability:** Handle processor outages.
- **Low latency:** Fast payment initiation and response.
- **Idempotency:** Prevent duplicate financial effects.
- **Consistency:** Maintain reliable payment state.
- **Security:** Protect sensitive payment data.

**Key assumption:** We are designing a merchant-side payment orchestration
platform, not an issuer authorization system.

---

## 2. High-Level Architecture

```text
                Merchant / Checkout
                       |
                       v
                   API Gateway
                       |
                       v
                Payment Service
                       |
              +--------+--------+
              |                 |
              v                 v
         Payment DB        Routing Engine
              |                 |
              |          +------+------+
              |          |             |
              |          v             v
              |       PSP A          PSP B
              |      Adapter        Adapter
              |          |             |
              |          v             v
              |      Processor A   Processor B
              |          |             |
              +----------+-------------+
                         |
                         v
                 Payment State DB
                         |
                         v
                    Event Broker
                         |
                 +-------+-------+
                 |               |
                 v               v
            Notifications   Reconciliation
```

**Why these components?**

- **Payment Service:** Owns the payment lifecycle.
- **Routing Engine:** Chooses an eligible processor.
- **PSP Adapters:** Hide differences in provider APIs and response codes.
- **Payment DB:** Stores payment state and idempotency records.
- **Event Broker:** Supports asynchronous notifications and reconciliation.

**Concept — Adapter pattern:** Wrap each external processor behind a common
interface so the business logic does not depend on its specific API.

---

## 3. Key Design Decisions — With Reasons

| Decision         | Choice                            | Why / Trade-off                                           |
|------------------|-----------------------------------|-----------------------------------------------------------|
| Communication    | REST API + provider adapters      | Simple merchant integration and independent PSP APIs      |
| Database         | Relational transactional DB       | Reliable payment state and unique constraints             |
| Routing          | Rules-based, health-aware routing | Choose an eligible, available processor                   |
| Orchestration    | Central Payment Service           | One owner of payment lifecycle and retries                |
| Retry            | Idempotent retry with backoff     | Recover transient failures without double charging        |
| Circuit breaker  | Per-processor circuit breaker     | Prevent cascading failures                                |
| Failover         | Route only when safe              | Avoid charging through two providers                      |
| State management | Payment state machine             | Track pending, successful, failed, and uncertain outcomes |
| Events           | Webhooks + durable broker         | Handle asynchronous provider updates                      |

### Decision 1 — How do we select a payment processor?

Suppose we have two processors:

- Processor A: Lower transaction cost.
- Processor B: Better availability for some payment methods or regions.

The Routing Engine evaluates:

1. Supported payment method and currency.
2. Merchant configuration and contractual restrictions.
3. Processor health and rate limits.
4. Historical success rates and latency.
5. Processing cost.

**Choice:** Start with deterministic, configurable rules. Introduce intelligent
routing only when data justifies it.

**Why?** A machine-learning router adds complexity, while rules can provide
predictable behavior and easier investigation.

### Decision 2 — Why a centralized orchestrator?

Without orchestration, each merchant integration must independently implement
provider selection, retries, and payment tracking.

With orchestration:

```text
Merchant
   |
   v
Payment Orchestrator
   |
   +--> Choose Provider
   +--> Execute Payment
   +--> Track State
   +--> Handle Failure
   +--> Reconcile Result
```

**Why?** One service owns the logical payment and maintains a consistent
lifecycle even when different processors are used.

**Trade-off:** It becomes an important dependency, so we run redundant stateless
instances and store workflow state durably.

### Decision 3 — How do we prevent duplicate charges?

This is the **most important architectural decision**.

Suppose a merchant sends a $100 payment request.

```text
Merchant             Gateway            PSP A
   |                    |                 |
   |--- Pay $100 ------>|                 |
   |                    |--- Pay $100 --->|
   |                    |                 |
   |                    |<-- SUCCESS -----|
   |                    X  Response lost
   |
   |--- Retry $100 ---->|
```

A naive implementation could create a second charge.

**Solution: Two levels of idempotency.**

| Level     | Protection                                                    |
|-----------|---------------------------------------------------------------|
| Gateway   | Unique merchant-scoped payment idempotency key                |
| Processor | Stable provider-specific idempotency key for the same attempt |

The gateway stores the logical payment ID and individual processor attempt IDs.

Stripe and Adyen document payment API idempotency mechanisms for safely
repeating supported requests. Their exact behavior and retention rules differ.

**Critical distinction:** The same key sent to two different processors does not
prevent duplicate charges across them. That requires gateway-level coordination
and reconciliation.

### Decision 4 — What happens if Processor A times out?

**Wrong approach:**

```text
PSP A timeout
     |
     v
Immediately charge via PSP B
```

Processor A may have charged the customer even though the gateway never received
its response. Using Processor B could create a duplicate charge.

**Correct approach:**

```text
PSP A timeout
     |
     v
Mark Attempt UNKNOWN
     |
     v
Query PSP A using payment reference
     |
     +--> Succeeded --> Record success
     |
     +--> Failed, confirmed no charge
     |                  |
     |                  v
     |           Consider PSP B
     |
     +--> Still unknown
                        |
                        v
               Keep payment pending
               and reconcile later
```

We must have reliable evidence that the original attempt cannot succeed before
starting a new provider attempt.

If the provider cannot establish the outcome, the system may need to keep the
payment pending and investigate. Cross-provider duplicate prevention cannot be
guaranteed merely through local idempotency keys.

### Decision 5 — Why use circuit breakers?

Suppose Processor A is repeatedly timing out. Without a circuit breaker,
thousands of requests continue hitting the failing provider.

**Concept — Circuit breaker:** Stops requests to an unhealthy dependency
temporarily, then permits limited recovery checks.

```text
CLOSED
  |
  | Failure threshold exceeded
  v
 OPEN
  |
  | Recovery delay
  v
HALF-OPEN
  |
  +--> Healthy --> CLOSED
  |
  +--> Failure --> OPEN
```

**Choice:** Use independent circuit breakers per processor.

**Why?** A failure at Processor A should not exhaust the gateway's resources.

A circuit breaker can direct **new, unattempted payments** to healthy providers.
It does not authorize rerouting a payment with an unknown previous outcome.

### Decision 6 — How should retries work?

Not every failure should trigger a retry.

| Failure                                                          | Action                                            |
|------------------------------------------------------------------|---------------------------------------------------|
| Transient connection failure with a safe provider retry contract | Retry with the same attempt identity/key          |
| Processor rate limiting                                          | Retry with bounded exponential backoff            |
| Card declined                                                    | Do not automatically retry as a technical failure |
| Provider timeout with uncertain outcome                          | Query/reconcile before failover                   |
| Invalid payment request                                          | Reject without retry                              |

**Concept — Exponential backoff:** Increase the delay between retries, typically
with randomness (jitter), to avoid overwhelming a struggling service.

Retries must follow the particular provider's documented rules.

---

## 4. End-to-End Payment Flow

```text
1. Merchant submits payment
              |
              v
2. Validate request + idempotency
              |
              v
3. Create durable Payment Intent
              |
              v
4. Routing Engine selects PSP
              |
              v
5. Create durable Provider Attempt
              |
              v
6. Call PSP through adapter
              |
              v
7. Process response / required action
              |
              v
8. Update payment state
              |
              v
9. Return result or pending status
              |
              v
10. Process webhooks and reconcile
    uncertain or delayed outcomes
```

**Important:** Persist the provider attempt identity before making the external
call. If the gateway crashes immediately afterward, it must be able to recover
that same attempt instead of creating an unrelated charge.

---

## 5. Payment State Machine & Data Model

A payment can pass through multiple states.

```text
            CREATED
               |
               v
            ROUTING
               |
               v
         PROCESSING
          /    |     \
         v     v      v
   REQUIRES  UNKNOWN  FAILED
    ACTION      |
         \      v
          \  RECONCILING
           \    |
            v   v
         AUTHORIZED
              |
              v
           CAPTURED
```

This is a simplified state model. The actual transitions depend on the payment
method and whether capture is immediate or delayed. Payment providers may also
require customer actions, asynchronous confirmation, or additional terminal
states.

### Core entities

| Entity              | Purpose                                    |
|---------------------|--------------------------------------------|
| `PaymentIntent`     | Logical merchant payment                   |
| `PaymentAttempt`    | Each attempt against a specific PSP        |
| `ProcessorConfig`   | Routing rules and supported capabilities   |
| `IdempotencyRecord` | Prevent duplicate logical payment creation |
| `PaymentEvent`      | Auditable lifecycle events                 |

**Key invariant:** One merchant payment must not create multiple successful
charges unintentionally.

Each provider attempt has a separate stable reference. A payment remains
unresolved while any prior attempt could still succeed.

Webhooks should be authenticated, deduplicated, and applied through valid state
transitions. A delayed webhook must not incorrectly overwrite a newer confirmed
payment state.

---

## 6. Failure Handling, Scalability & Security

| Scenario                           | Design response                           | Why                                |
|------------------------------------|-------------------------------------------|------------------------------------|
| PSP unavailable before new attempt | Route to another eligible PSP             | Maintain availability              |
| PSP timeout after submission       | Mark UNKNOWN, query and reconcile         | Avoid double charge                |
| Duplicate merchant request         | Gateway idempotency                       | Prevent duplicate payment creation |
| PSP repeatedly failing             | Circuit breaker                           | Reduce cascading failures          |
| Gateway crashes mid-payment        | Resume from durable payment/attempt state | Safe recovery                      |
| Webhook duplicated or delayed      | Deduplication + state validation          | Correct lifecycle                  |
| Traffic spike                      | Horizontally scale stateless instances    | Increase capacity                  |
| Broker unavailable                 | Transactional outbox                      | Preserve events                    |
| Payment credentials exposed        | Tokenization, PCI-aligned controls        | Reduce sensitive-data exposure     |

**Scalability:** Keep orchestration workers stateless, store payment state in a
transactional database, and scale adapters independently where provider limits
allow.

**Security:** Use tokenized payment methods, protected provider credentials,
encryption, least-privilege access, signed webhook verification, and controlled
PCI DSS scope.

**Observability:** Monitor success rate by PSP, technical error rate, p99
latency, retry rate, circuit-breaker state, unknown-outcome age, and
reconciliation mismatches.

---

## 7. Key Points to Remember

1. **Centralize orchestration.** One logical payment owner manages provider
   routing, attempts, state, and recovery.
2. **Idempotency at two levels.** Gateway-level and processor-level
   deduplication protect different boundaries.
3. **Never blindly fail over after a timeout.** The original provider may
   already have charged the customer.
4. **Circuit breakers protect availability.** Stop sending new payments to
   unhealthy processors, while recovering uncertain existing attempts
   separately.
5. **Durable state and reconciliation are essential.** External payment outcomes
   can be delayed, ambiguous, or delivered through webhooks.

---

## 8. Interview Closing Summary

> I would design a centralized payment orchestration service with a configurable
> routing engine and separate adapters for each payment processor. A
> transactional
> database stores payment intents, provider attempts, and idempotency records. I
> would use health-aware routing and circuit breakers for new transactions, plus
> bounded retries with provider-specific idempotency. The most important design
> choice is handling uncertain outcomes: if a processor times out, I would
> reconcile the existing attempt before rerouting to avoid duplicate charges.
> Finally, durable events, webhook handling, and reconciliation provide
> resilience, scalability, and financial correctness.

---

## Official References for Further Reading

- [Stripe — Idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [Adyen — API idempotency](https://docs.adyen.com/development-resources/api-idempotency)
- [Microsoft Azure Architecture Center — Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [AWS — Transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

*Illustrative interview design; not a description of American Express's
proprietary payment architecture.*
