# System Design 1 — Credit Card Transaction History Service

*10-minute interview answer · Solution Architect*

## 1. Problem & Requirements

**Problem:** Design a system where customers can view credit card transactions,
including pending and posted transactions.

**Functional requirements:**

- View recent and historical transactions.
- Filter by date, status, and merchant.
- Support pagination and transaction details.
- Ensure customers can only access their own accounts.

**Non-functional requirements:**

| Requirement  | Expectation                                                    |
|--------------|----------------------------------------------------------------|
| Latency      | Fast reads, with an agreed p95 target                          |
| Scale        | Read-heavy, with growing historical data                       |
| Consistency  | Eventual for history; strong for authoritative financial state |
| Availability | Highly available reads with controlled recovery                |

**Key assumption:** The history service is not responsible for processing
payments or maintaining the authoritative financial ledger.

## 2. High-Level Architecture

```text
       Customer App
            |
            v
      API Gateway
            |
            v
      History Service
            |
            v
       History DB
            ^
            |
      Event Consumer
            ^
            |
       Event Broker
            ^
            |
     Outbox Publisher
            ^
            |
   Financial Processing
   System + Source DB
```

| Component        | Why we need it                                      |
|------------------|-----------------------------------------------------|
| API Gateway      | Authentication, routing, rate limiting              |
| History Service  | Authorization, filters, pagination                  |
| History DB       | Read-optimized transaction storage                  |
| Event Broker     | Decouples financial processing from history updates |
| Event Consumer   | Builds and updates the history read model           |
| Financial System | Authoritative source of financial transactions      |

**Key decision:** Separate financial processing from transaction-history reads.
This protects critical financial workloads from heavy customer query traffic.

## 3. Key Design Decisions

| Decision      | Choice and why                                                           | Alternative / Trade-off                                                      |
|---------------|--------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Communication | REST for client reads; events for updates                                | Synchronous integration couples history availability to the financial system |
| Database      | SQL with account/date indexes                                            | NoSQL can help at extreme scale but adds modeling trade-offs                 |
| Consistency   | Eventual consistency for history                                         | Strongly consistent reads from the financial source increase coupling        |
| Caching       | Optional Redis cache for frequently accessed, staleness-tolerant queries | Adds invalidation complexity                                                 |
| Messaging     | Durable broker with an outbox where source integration allows it         | Direct publishing risks losing events                                        |
| Scaling       | Stateless API instances, indexing, partitioning as needed                | Sharding adds operational complexity                                         |

### Important concepts

- **CQRS:** Separate read models from write models to optimize them
  independently.
- **Eventual consistency:** The history database can temporarily lag behind
  financial processing.
- **Transactional outbox:** Store a business update and its event atomically
  before publishing it.
- **Idempotency:** Reprocessing an event must not create duplicate transactions.

## 4. End-to-End Request Flow

### A. Updating transaction history

1. Financial processing creates or updates an authoritative transaction.
2. A change event is recorded reliably, using an outbox or an appropriate CDC
   integration.
3. The publisher sends the event to the broker.
4. The history consumer processes the event.
5. The consumer inserts or updates the history record using transaction ID and
   version.
6. The updated history becomes available for customer reads.

### B. Customer reading transactions

1. The customer calls `GET /accounts/{id}/transactions`.
2. API Gateway authenticates the request.
3. History Service checks account-level authorization.
4. The service queries the database using account ID, filters, and cursor.
5. The API returns the transaction page.

**Why cursor pagination?** It avoids increasingly expensive large-offset queries
and supports efficient navigation through indexed history.

## 5. Data Model & Correctness

**Core entities:**

```text
Transaction
-----------
transaction_id
account_id
amount_minor
currency
merchant
status
transaction_date
posted_at
source_version
```

**Source of truth:** The authoritative financial processing system, not the
history database.

**Critical invariant:** One logical source transaction must not become multiple
history transactions, and a stale event must not overwrite a newer version.

**Concurrency handling:**

- Unique constraint on transaction ID.
- Idempotent upsert for replayed events.
- Version checks for out-of-order events.
- Explicit pending-to-posted lifecycle handling.

The history database must not be used independently to decide whether a customer
has sufficient available credit.

## 6. Failure Handling, Scalability & Security

| Scenario                    | Design response                                       | Why                                  |
|-----------------------------|-------------------------------------------------------|--------------------------------------|
| API instance fails          | Load balancing across stateless instances             | Another instance can serve requests  |
| Duplicate event             | Idempotent consumer                                   | Prevent duplicate history records    |
| Broker unavailable          | Durable outbox and retry                              | Prevent lost updates                 |
| Database unavailable        | Failover; bounded retries                             | Restore service without retry storms |
| Traffic spike               | Horizontal scaling, optimized queries, optional cache | Control database load                |
| Unauthorized account access | Object-level authorization                            | Prevent cross-account data exposure  |

**Other important controls:** Encrypt data in transit and at rest, use
least-privilege service identities, audit sensitive access, and monitor event
lag and reconciliation mismatches.

## 7. Key Points to Remember

1. **Separate writes from reads** — Financial processing requires correctness;
   transaction history needs efficient queries.
2. **Use eventual consistency selectively** — History may lag, but authoritative
   financial state must remain correct.
3. **Optimize access patterns first** — Composite indexes and cursor pagination
   before sharding.
4. **Make event processing reliable** — Outbox, retries, idempotency, and
   version checks.
5. **Keep complexity justified** — Caching, sharding, and multi-region designs
   must solve explicit requirements.

## 8. Interview Closing Summary

> I would design the transaction-history system using a separate read-optimized
> service backed by a relational database. Financial transactions remain in the
> authoritative financial system, and reliable events update the history
> projection asynchronously. This reduces coupling and protects critical
> financial
> processing from customer read traffic. I would use indexing and cursor
> pagination for efficient queries, idempotent event processing for correctness,
> and horizontal scaling for availability. The main trade-off is that
> transaction
> history may briefly lag behind authoritative financial state, which we would
> make explicit and monitor.

**Next design:** Credit Card Authorization — a contrasting design where low
latency, concurrency control, and authoritative financial decisions become the
primary concerns.
