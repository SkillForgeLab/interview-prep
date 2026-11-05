# Design 5 — Real-Time Fraud Detection System

**Format:** 10-minute interview answer  
**Context:** American Express — Solution Architect preparation  
**Purpose:** Explain the important architecture decisions, why they fit,
alternatives, failure handling, and key points to remember.

## 1. Problem & Requirements

Design a system that identifies potentially fraudulent credit-card transactions*
*before authorization is approved**.

**Functional requirements**

- Evaluate transactions in real time.
- Detect suspicious behavior using rules and machine-learning models.
- Track transaction velocity, amounts, location, merchant, and device signals.
- Return a risk recommendation with reason codes.
- Continuously update fraud features from transaction events.

**Non-functional requirements**

- **Low latency:** Fraud scoring must fit within the issuer's authorization
  deadline.
- **High availability:** Dependency failures must follow a controlled risk
  policy.
- **Scalability:** Support high peak transaction volume.
- **Feature freshness:** Use recent activity without assuming all streaming data
  is current.
- **Auditability:** Preserve model/policy versions and reasons for decisions.

**Example assumptions:** 10,000 peak TPS, 100 ms p99 fraud-decision budget.
These are illustrative design targets, not American Express's production
figures.

## 2. High-Level Architecture

```text
                   Card Network
                        |
                        v
              Authorization Service
                        |
                        v
                  Fraud Engine
                        |
                +-------+-------+
                |       |       |
                v       v       v
              Rules   ML Model  Online
              Engine  Serving   Feature Store
                |       |           ^
                +-------+           |
                    |               |
                    v               |
               Risk Decision        |
                    |               |
                    v               |
              Authorization         |
                 Service            |
                                    |
     Transaction Events             |
              |                     |
              v                     |
         Kafka / Stream             |
              |                     |
              v                     |
         Stream Processor ----------+
              |
              v
       Historical Data Lake
              |
              v
         Model Training
```

**Two paths:**

1. **Synchronous decision path:** Get recent features, evaluate rules and ML,
   return a risk recommendation immediately.
2. **Asynchronous learning/update path:** Consume transaction events, maintain
   features, store history, and retrain models.

The synchronous path **must not wait** for streaming feature updates to
complete.

## 3. Key Design Decisions — With Reasons

| Decision             | Choice                                     | Why                                                      | Alternative / Trade-off                                                  |
|----------------------|--------------------------------------------|----------------------------------------------------------|--------------------------------------------------------------------------|
| Decisioning          | Synchronous API                            | Issuer needs fraud recommendation before approval        | Async-only detection is too late to block the current transaction        |
| Detection            | Rules + ML                                 | Rules enforce explicit policy; ML finds complex patterns | Rules-only is simpler, but less adaptive                                 |
| Recent features      | Low-latency online key-value/feature store | Avoid warehouse queries on critical path                 | Direct DB queries may be slower; feature store may lag                   |
| Feature updates      | Kafka + stream processor (or equivalent)   | Durable ingestion, windowed aggregations, replay         | Traditional queues can work if replay/windowing requirements are modest  |
| Historical data      | Lake/warehouse                             | Training, backtesting, analytics, investigations         | Not suitable for per-request online scoring                              |
| Hard velocity limits | Atomic/coordinated state                   | Concurrent attempts must not bypass a strict limit       | Eventually updated counters may miss current attempts                    |
| Dependency failure   | Risk-approved fallback policy              | Prevent accidental fail-open approval                    | Fail-closed increases false declines; fail-open increases fraud exposure |
| Model release        | Versioned models, canary/shadow rollout    | Detect accuracy regressions safely                       | Uncontrolled rollout can cause widespread false declines                 |
| Scaling              | Stateless scoring + partitioned streams    | Scale hot components independently                       | More operational complexity                                              |

### A. Why rules and ML together?

**Rules** handle clear policy decisions, such as a stolen card or a hard
transaction restriction. **ML** identifies patterns across amount, merchant,
device, geography, and recent behavior. The final policy combines both; a model
score does not override mandatory controls automatically.

### B. Why stream processing?

To detect unusual transaction velocity, the system maintains features such as
transaction count over five minutes and decline count over ten minutes.

```text
Transaction events -> Durable stream -> Windowed processor -> Online feature store
```

**Windowing** means aggregating events over a period. Processing must account
for **event time** (when the transaction occurred), late arrivals, and duplicate
messages.

### C. Why an online feature store?

Scoring needs recent values quickly, such as:

| Feature                                 | Example value |
|-----------------------------------------|--------------:|
| Transactions in last 5 minutes          |             8 |
| Amount in last hour                     |        $2,500 |
| Declines in last 10 minutes             |             4 |
| Merchant risk score                     |          0.82 |
| Average transaction amount over 30 days |           $75 |

An online store provides low-latency reads. **But streamed features can be
stale.** Rules requiring an exact cap must be enforced with atomic or otherwise
coordinated state.

### D. Why not ML scoring asynchronously?

Fraud evaluation affects whether the current transaction should be approved.
Scoring **must happen before** the issuer's final authorization decision. Event
pipelines are suitable for updating future risk signals, investigations, and
training.

### E. What if the ML service fails?

Use a documented, risk-approved policy. Possible strategies include fail closed,
fail open only for narrowly permitted scenarios, or degraded deterministic
rules. Do **not** bypass mandatory authentication or risk controls. Apply
bounded timeouts, circuit breakers, and redundant scoring instances.

## 4. End-to-End Request Flow

```text
1. Authorization service sends transaction context
                  |
2. Fraud engine validates request
                  |
3. Fetch online behavioral features
                  |
4. Evaluate mandatory rules
                  |
5. Run ML inference
                  |
6. Combine results using decision policy
                  |
7. Return risk score, recommendation, reason codes
                  |
8. Issuer makes final authorization decision
                  |
9. Persist outcome and publish durable event
                  |
10. Stream processors update features and history
```

**Example response:**

```json
{
  "transactionId": "txn_123",
  "riskScore": 0.91,
  "riskLevel": "HIGH",
  "recommendation": "DECLINE",
  "reasonCodes": [
    "HIGH_VELOCITY"
  ],
  "modelVersion": "v12",
  "policyVersion": "p4"
}
```

The fraud response is **a recommendation/input**, not necessarily the issuer's
complete authorization decision.

## 5. Data Model & Correctness

| Entity             | Purpose                                             |
|--------------------|-----------------------------------------------------|
| `TransactionEvent` | Attempt, outcome, event ID, event timestamp         |
| `FraudFeature`     | Recent aggregates and behavioral statistics         |
| `RiskDecision`     | Score, reasons, policy/model version, decision time |
| `ModelVersion`     | Reproducible model metadata                         |
| `FraudCase`        | Investigation, confirmed fraud, analyst outcome     |

**Key invariants:**

- Duplicate events must not inflate velocity counts.
- Strict velocity caps need coordinated atomic enforcement.
- The decision records the actual model and policy versions used.
- Late/out-of-order events must be handled using an explicit event-time policy.
- Sensitive payment information must not leak into logs, features, or training
  datasets unnecessarily.

## 6. Failure Handling, Scalability & Security

| Scenario                         | Response                                                 | Why                                        |
|----------------------------------|----------------------------------------------------------|--------------------------------------------|
| ML model unavailable             | Execute risk-approved fallback                           | Controlled fraud exposure and availability |
| Online feature store unavailable | Use permitted trusted signals/degraded rules             | Avoid arbitrary approval decisions         |
| Event broker unavailable         | Durable outbox/replay after recovery                     | Preserve feature/history updates           |
| Duplicate events                 | Dedupe by event ID                                       | Prevent inflated counters                  |
| Late/out-of-order events         | Event-time windows and correction policy                 | Preserve aggregate meaning                 |
| Traffic spike                    | Horizontally scale scoring workers and model servers     | Improve throughput                         |
| Model drift                      | Monitor accuracy and false-decline signals; rollback     | Prevent silent decline in decision quality |
| Security threat                  | Least privilege, tokenization, encryption, redacted logs | Protect cardholder and financial data      |

**Scaling:** Stateless fraud API and model-serving instances can scale
horizontally. Partition event streams by stable account/card grouping where
per-key ordering is needed. Monitor online store hotspots and feature-update
lag.

**Operational metrics:** Scoring p95/p99 latency, availability, model timeouts,
feature age, stream lag, fraud detection rate, false-decline rate, fraud losses,
policy overrides, and model drift.

## 7. Key Points to Remember

1. **Synchronous scoring, asynchronous updates.** The risk recommendation must
   influence authorization before approval.
2. **Rules + ML.** Rules enforce explicit policies; ML identifies complex
   patterns.
3. **Online feature store = low latency.** Do not query the historical warehouse
   in the authorization critical path.
4. **Feature freshness matters.** Streamed counters may lag; strict velocity
   limits need coordinated state.
5. **Fail safely.** Use risk-approved fallbacks, versioned models, monitoring,
   and auditable decisions.

## 8. Interview Closing Summary

> I would use a synchronous fraud engine with deterministic rules, ML inference,
> and a low-latency online feature store. Kafka and stream processing would
> maintain recent behavior features and feed historical data for training, while
> the current authorization decision remains synchronous. I would use
> coordinated
> state for hard velocity constraints because asynchronous features can lag. I
> would scale scoring services independently, implement risk-approved fallback
> policies, and monitor latency, feature freshness, model drift, and false
> declines. This balances fraud prevention, customer experience, and
> reliability.

---

**Next design:** Payment Gateway & Orchestration — processor routing, retries,
circuit breakers, payment state machines, and preventing duplicate charges
across providers.

**Reference areas for further verification:** Apache Kafka Streams
documentation (event-time/windowing); AWS SageMaker Feature Store
documentation (online/offline stores); NIST AI Risk Management Framework (model
monitoring and governance).
