[Skip to guide](#main)

DP / DESIGN PATTERNS

A first-principles guide to durable messaging.

[IDerive the problem](#derive)[IIMake the promise durable](#outbox)[IIICross the network with retry](#relay)[IVMake duplicate processing harmless](#inbox)[VRead the failure contract](#failures)[VIAdd concurrency and operational control](#operations)[VIIDerive the ordering you need](#ordering)[VIIIBe precise about exactly once](#guarantees)[IXTest the failure contract](#tests)[XChoose and explain the design](#design)[A · Java reference](#source)[B · SQL schema](#schema)[C · Official references](#references)

Print / Save as PDF[x] Include full Java source in print

Offline HTML · Light theme
Java 25-compatible examples

Print / Save as PDF[Contents](#contents)[Code](#source)

DISTRIBUTED SYSTEMS / FIRST PRINCIPLES

# Transactional Outbox

How local transactions, durable intent, and safe retries turn a fragile dual write into a testable failure contract.

JAVA 25POSTGRESQLOUTBOX + INBOX47 STEPS

Follow the business promise through every crash window. Derive the mechanisms before naming the patterns.

01**Record together**Business change and publication intent share one database transaction.

02**Retry the handoff**Cross the network with a stable event identity. Expect duplicates.

03**Commit the effect**Deduplication and the consumer’s local change share another transaction.

**Read this as a derivation**

The running example records a confirmed payment, then notifies downstream services. Start with parts I-IV. Parts V-X make the failure, ordering, and operational contracts explicit. Appendices provide the complete reference code, SQL, and official documentation.

## Reading path

1. [Derive the problem](#derive)
2. [Make the promise durable](#outbox)
3. [Cross the network with retry](#relay)
4. [Make duplicate processing harmless](#inbox)
5. [Read the failure contract](#failures)
6. [Add concurrency and operational control](#operations)
7. [Derive the ordering you need](#ordering)
8. [Be precise about exactly once](#guarantees)
9. [Test the failure contract](#tests)
10. [Choose and explain the design](#design)
11. [Complete Java reference](#source)
12. [Database schema](#schema)
13. [Official references](#references)

PART I

## Derive the problem

Start with a business promise. Add failure before adding infrastructure.

### 01What must stay true?

A customer pays an order. The order service must record the payment, and Shipping must eventually learn that the order is ready. These are two related facts held by independently failing systems.

| Fact | Owner | Required relationship |
| --- | --- | --- |
| The order is paid | Producer database | Committed only after business validation |
| Shipping can learn the order was paid | Messaging path | Every committed payment transition has a durable path to notification |

For this guide, `PayOrder` records a payment already authorized or confirmed by the surrounding workflow. It does not charge a card. The example permits exactly one transition from `NEW` to `PAID`, and asynchronous downstream work is acceptable.

**The question to keep asking**

If the process dies between these operations, what durable evidence remains?

### 02Separate the request from the fact

A command asks for a change; an event describes a change that committed. A cancelled order cannot become paid. Retrying payment of an already paid order is a no-op in this deliberately small domain.

Java

```
public record PayOrder(UUID orderId) {}

public record OrderPaid(
        UUID eventId, UUID orderId, UUID customerId,
        long orderVersion, Instant occurredAt) {}
```

The model carries `customerId` so the later loyalty consumer can credit the right customer without reaching back into the producer database. `orderVersion` describes domain progression; it is different from the event schema version. The complete model is in [Appendix A](#source).

### 03The obvious implementation has two writes

Pseudocode - failure analysis

```
// Deliberately unsafe pseudocode:
savePaidOrderToDatabase();
publishOrderPaidToBroker();
```

A successful method call is not an atomicity boundary. Saving an order and sending a message involve different resources. A crash can occur after either resource has changed.

| Database change | Broker publication | Meaning |
| --- | --- | --- |
| Committed | Accepted | Desired result |
| Committed | Missing | Paid order with no notification |
| Rolled back | Accepted | Notification for a fact that did not commit |
| Rolled back | Missing | No committed business change |

### 04Database first leaves a missing-message window

Commit the order, then publish. If the process dies after the commit and before the send, the database says `PAID` and the broker has nothing. Retrying inside a catch block cannot recover work that vanished with the process.

| Step | Durable state |
| --- | --- |
| 1. Commit order | Order = PAID |
| 2. Process crashes | No durable record of the unsent notification |
| 3. Application restarts | The unfinished network operation is not automatically known |

A failed HTTP response is not proof that payment failed. Retrying the command must also be safe; we return to this in section 11.

### 05Broker first leaves a false-fact window

Reverse the operations. The broker accepts `OrderPaid`, then the database transaction fails. A consumer can act on an event whose business fact never committed.

**Reordering is insufficient**

Putting the network call inside an ordinary database transaction does not enlist the broker in that transaction. Rolling back SQL cannot recall an already accepted message.

### 06An in-memory callback cannot make intent durable

Publishing after commit, using an observer, or scheduling a background task removes some timing problems, but a process can die after commit and before the callback runs. An in-memory queue has the same lifetime as the process.

A compensating action can be useful for a business workflow, but it is another operation that can fail. It does not turn the original two writes into one atomic write. We need a durable recovery point.

### 07Choose an atomic boundary you actually own

The producer can atomically change multiple rows in one database transaction. PostgreSQL transactions group those changes so a successful commit makes them visible together; rollback cancels the transaction’s changes. [[1]](#ref-1)

The application cannot get that guarantee merely by placing a database call and a broker call next to each other. Ask instead: can the second obligation be represented as data in the database we already control?

### 08Record the obligation to publish

Insert a row that says: this committed business transition needs publication. Save that row in the same transaction as the order change.

| Transaction outcome | Order state | Publication intent |
| --- | --- | --- |
| Commit | PAID | An outbox row exists |
| Rollback | Unchanged | No new outbox row |

**The crucial move**

Make the business change and its publication intent atomic. Let a separate worker cross the network boundary later.

We have now derived the **Transactional Outbox**. The pattern follows from the failure analysis.

PART II

## Make the promise durable

One producer transaction owns the business change and the record of its consequences.

### 09The Transactional Outbox boundary

| Inside the producer transaction | After the transaction commits |
| --- | --- |
| Validate and update the order Insert the outbox row | Relay reads pending rows Broker accepts publications Consumers process events |

The atomic boundary covers the order and outbox. It does not include broker publication or consumer processing. The outbox is a durable handoff mechanism; it need not be an event store, and the orders table can remain the authoritative business state.

### 10Start with a small schema

The reference schema includes identity, schema version, and aggregate version from the start so all examples fit together. The nullable publication timestamp records whether the relay has recorded a successful acknowledgement.

PostgreSQL

```
CREATE TABLE outbox_message (
    id                UUID PRIMARY KEY,
    event_type        VARCHAR(200) NOT NULL,
    event_version     INTEGER NOT NULL CHECK (event_version > 0),
    aggregate_id      UUID NOT NULL,
    aggregate_version BIGINT NOT NULL,
    payload           JSONB NOT NULL,
    occurred_at       TIMESTAMPTZ NOT NULL,
    published_at      TIMESTAMPTZ
);
CREATE INDEX idx_outbox_unpublished
    ON outbox_message (occurred_at, id)
    WHERE published_at IS NULL;
```

**What NULL really means**

`published_at IS NULL` means publication has not been durably recorded as complete. The broker might already have accepted the message if acknowledgement or the subsequent database update failed.

The row ID is the event ID. The payload also contains it. Use the same identity in headers and payload, and reject inconsistent envelopes during decoding. A production serializer should validate payloads before insertion when possible.

### 11Make transaction ownership explicit

Both repositories receive the same `Connection`. They must not open or commit their own independent transactions. A callback that permits `SQLException` avoids pretending JDBC operations fit a plain `Function` without exception handling.

Java

```
public record PayOrderHandler(
        TransactionRunner transactions, OrderRepository orders,
        OutboxRepository outbox, Clock clock) {
    public void handle(PayOrder command) throws SQLException {
        transactions.inTransaction(c -> {
            Order before = orders.findForUpdate(c, command.orderId())
                    .orElseThrow(() ->
                            new IllegalArgumentException("Unknown order"));
            Order paid = before.markPaid();
            if (before.status() == Status.PAID) return null;

            orders.save(c, paid);
            OrderPaid event = new OrderPaid(
                    UUID.randomUUID(), paid.id(), paid.customerId(),
                    paid.version(), clock.instant());
            outbox.add(c, OutboxMessage.from(event));
            return null;
        });
    }
}
```

The adapter loads the order with `SELECT ... FOR UPDATE`. Under PostgreSQL Read Committed, a concurrent locker waits and then sees the updated row. The second payment command therefore sees `PAID` and creates no second event. Other writers must respect the same state and concurrency rules. [[2]](#ref-2)

Java

```
@FunctionalInterface
public interface SqlWork<T> {
    T run(Connection connection) throws SQLException;
}

public interface TransactionRunner {
    <T> T inTransaction(SqlWork<T> work) throws SQLException;
}

public record JdbcTransactions(DataSource dataSource)
        implements TransactionRunner {
    @Override
    public <T> T inTransaction(SqlWork<T> work)
            throws SQLException {
        // Own a fresh connection; no nested/JTA transaction support.
        try (Connection c = dataSource.getConnection()) {
            c.setAutoCommit(false);
            try {
                T result = work.run(c);
                c.commit();
                return result;
            } catch (SQLException | RuntimeException | Error failure) {
                try {
                    c.rollback();
                } catch (SQLException rollbackFailure) {
                    failure.addSuppressed(rollbackFailure);
                }
                // A commit/connection error can have unknown outcome.
                // No automatic retry or claim of successful rollback.
                throw failure;
            }
        }
    }
}
```

JDBC connections use auto-commit by default; disabling it allows the repository calls to share an explicit commit or rollback. The transaction runner owns and closes a fresh connection. It does not implement nested transactions or participate in an existing transaction manager. [[3]](#ref-3)

**Commit response lost does not mean rollback**

⚠️ If a connection fails during commit, the client may not know whether the database committed. Calling rollback afterward cannot undo an already committed transaction. PostgreSQL explicitly recognizes an unknown transaction resolution. Reconcile using durable business state or retry an idempotent command; do not blindly create a new logical operation. [[4]](#ref-4)

Here, one irreversible `NEW → PAID` transition plus the row lock makes a repeated command safe. A real charging workflow usually needs a separate request or payment identity, stored atomically with its result. An event ID deduplicates a message; it is not a universal command-idempotency key.

### 12Separate business ownership from delivery ownership

| Component | Owns | Changes when |
| --- | --- | --- |
| Application handler | Business validation, state change, durable intent | Business rules change |
| Relay | Publication attempts and acknowledgement recording | Broker integration or retry policy changes |
| Consumer | Its local interpretation and effect | Downstream business rules change |

The domain does not know Kafka exists. Broker availability no longer directly gates the order transaction, provided delayed propagation is acceptable. A prolonged outage can still fill the outbox and exhaust storage; operational capacity remains part of the design.

PART III

## Cross the network with retry

The relay exchanges a loss window for a recoverable duplicate window.

### 13Implement the simplest relay with an honest contract

Java

```
public record OutboxRelay(
        TransactionRunner transactions, OutboxRepository outbox,
        MessagePublisher publisher) {
    // Exactly one active worker for this teaching implementation.
    // This sorted poll is not a causal-ordering guarantee.
    public void runOnce() throws Exception {
        List<OutboxMessage> batch = transactions.inTransaction(
                c -> outbox.findPending(c, 100));
        for (OutboxMessage message : batch) {
            publisher.publishAndAwaitAck(message);
            transactions.inTransaction(c -> {
                outbox.markPublished(c, message.id());
                return null;
            });
        }
        // A failure exits the batch; the row remains eligible.
        // Backoff/quarantine are extensions, not implemented here.
    }
}

public static ScheduledFuture<?> schedule(
        ScheduledExecutorService scheduler, OutboxRelay relay) {
    System.Logger log = System.getLogger("outbox-relay");
    return scheduler.scheduleWithFixedDelay(() -> {
        try {
            relay.runOnce();
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Relay interrupted",
                    interrupted);
        } catch (Exception failure) {
            log.log(System.Logger.Level.ERROR,
                    "Relay pass failed; pending rows will retry", failure);
        }
    }, 0, 1, TimeUnit.SECONDS);
}
```

The initial implementation has exactly one active worker, including across deployments. It reads a batch, closes the read transaction, publishes each row, waits for acknowledgement, and then marks that row in a new local transaction. Network I/O is outside the database transaction.

An exception exits the batch. The scheduler logs ordinary failures so later passes can retry. Java suppresses future periodic executions if the scheduled task throws; interruption deliberately stops this task. The application owns the scheduler lifecycle and must monitor the returned future. [[5]](#ref-5)

**Acknowledgement is a real adapter requirement**

Calling an asynchronous send method is not enough. `publishAndAwaitAck` must wait for the configured broker acknowledgement before returning. Kafka `send` returns a future; completion must be observed. [[6]](#ref-6)

One second and 100 rows are illustrative settings. This minimal loop has no backoff, quarantine, or ordering guarantee; later sections derive those additions.

### 14Failure: the broker is unavailable

If publication fails before acceptance, the relay never marks the row. The pending intent survives application restarts. When service is restored, a later pass can publish it.

This protects the handoff only while the outbox is retained, the relay keeps operating, and failures can eventually be resolved. A pending row is a recoverable obligation, not evidence of eventual progress by itself.

### 15Failure: publish succeeds, then the relay crashes

| Sequence | Broker | Outbox |
| --- | --- | --- |
| Send event abc123 | Accepts abc123 | Pending |
| Relay dies before mark | Still has abc123 | Still pending |
| Relay restarts and sends again | May now have two abc123 records | Marked after acknowledgement |

The relay cannot distinguish this row from an unsent one using the outbox state alone. Duplicate publication is an expected recovery outcome.

### 16Why marking first is worse

| Order of operations | Crash window | Consequence |
| --- | --- | --- |
| Publish, then mark | After acceptance, before mark | Duplicate possible on retry |
| Mark, then publish | After mark, before acceptance | Message can be permanently omitted |

A deduplicating consumer can make a repeated delivery harmless. A consumer cannot process an event it never receives. We therefore publish first and keep the row pending until acknowledgement has been recorded.

### 17State the at-least-once guarantee conditionally

An acknowledgement can disappear even when the broker stored the message. Retrying is necessary for recovery and can repeat an accepted message. “At least once” permits duplicate delivery; it does not claim every message is duplicated.

**Safety and progress are different**

Safety: a committed payment retains its publication intent until handled under the retention policy. Progress: valid pending work is eventually delivered if storage survives, retries continue, the systems recover, and the message remains consumable.

If an operator discards a pending row, a permanent error remains unresolved, or retention expires before a consumer reads the event, eventual delivery is not guaranteed. Quarantining a message preserves evidence but suspends its normal delivery path.

### 18Keep identity stable across attempts

Generate the event ID when the business transaction creates the outbox row. Every relay attempt republishes that row’s same ID and immutable event content. A timeout does not create a new business event.

| Action | Identity rule |
| --- | --- |
| Retry publication | Reuse the persisted event ID |
| Redeliver from broker | Preserve the original event ID |
| Create a different business fact | Assign a different event ID |
| Replay for the same consumer | Same ID means the inbox will normally skip it |

A corrected event is usually a new, explicitly related fact. Silently changing the meaning of an existing event ID makes deduplication ambiguous.

PART IV

## Make duplicate processing harmless

The consumer needs its own atomic boundary; producer reliability cannot supply it.

### 19The consumer receives the same event twice

If Shipping creates a shipment for every delivery, two deliveries of `abc123` can create two shipments. The producer outbox solved the durable handoff problem. It did not make downstream effects idempotent.

Correctness must cover the receiver’s database and every external side effect. First ask whether the business operation is already safe to repeat.

### 20Prefer natural idempotency when it fits

If the domain permits exactly one shipment per order, express that invariant with a unique database constraint and an insert that tolerates that conflict.

PostgreSQL - alternative Shipping consumer

```
CREATE TABLE shipment (
    order_id UUID PRIMARY KEY
);

INSERT INTO shipment (order_id) VALUES (?)
ON CONFLICT (order_id) DO NOTHING;
```

The constraint arbitrates concurrent attempts. A separate “does it exist?” check followed by an unguarded insert is insufficient. PostgreSQL `ON CONFLICT` handles the specified uniqueness conflict within the statement. [[7]](#ref-7)

**Let the domain choose the key**

If split shipments are valid, `UNIQUE(order_id)` would enforce the wrong rule. Idempotency keys must represent the effect you intend to allow once.

### 21Some operations accumulate effects

Adding 100 loyalty points twice produces 200 points. A stable event ID helps only if the consumer remembers it. For this event, the required effect is one credit per consumer and logical event, even if the event is delivered repeatedly.

That memory must survive a restart and must be coordinated with the points update. We have encountered the same atomicity question again.

### 22Derive a durable inbox

PostgreSQL

```
CREATE TABLE inbox_message (
    consumer_name VARCHAR(200) NOT NULL,
    message_id    UUID NOT NULL,
    processed_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (consumer_name, message_id)
);
```

The primary key is `(consumer_name, message_id)`. Shipping and Loyalty can both process the same event; one consumer’s completion must not suppress the other’s work. `consumer_name` identifies a logical handler, not a pod or process instance.

Keep this name stable across ordinary deployments. Renaming it makes old messages eligible again. The `processed_at` value is inserted before the effect, but the row becomes committed evidence only when the whole consumer transaction commits.

### 23Insert the inbox row and apply the effect together

Java

```
public record OrderPaidConsumer(
        TransactionRunner transactions, InboxRepository inbox,
        LoyaltyRepository loyalty) {
    public void handle(OrderPaid event) throws SQLException {
        transactions.inTransaction(c -> {
            if (!inbox.tryInsert(c, "loyalty-order-paid-v1",
                    event.eventId())) return null;
            loyalty.addPoints(c, event.customerId(), 100);
            return null;
        });
    }
}
// Broker adapter acknowledges/commits offsets AFTER handle returns.
// JSON decoding, validation and broker offset management are adapters.
```

PostgreSQL

```
INSERT INTO inbox_message
  (consumer_name, message_id, processed_at)
VALUES (?, ?, NOW())
ON CONFLICT (consumer_name, message_id) DO NOTHING;
```

Use the inserted row count: one means this transaction claimed first processing; zero means a committed duplicate already won. The complete adapter uses `executeUpdate() == 1`. Avoid a prior existence check, which races with another delivery. [[7]](#ref-7)[[8]](#ref-8)

At Read Committed, concurrent inserts contend on the unique key. If the winner commits, the other skips; if it rolls back, another attempt can insert and apply the effect. Stricter isolation can require retrying the entire transaction after a serialization failure. [[9]](#ref-9)

### 24An inbox committed separately can lose the effect

| Approach | Crash after inbox commit | Redelivery |
| --- | --- | --- |
| Inbox commits, then points update | Inbox exists; points absent | Skips the missing effect |
| Inbox and points share one transaction | Either both commit or both roll back | Skips completed work or safely retries |

Do not swallow a business update exception inside the transaction and then commit the inbox anyway. A failed local effect must abort its deduplication claim too.

### 25Acknowledge only after the consumer database commits

The consumer first commits the inbox and the business effect. Only then does its broker adapter acknowledge delivery. A crash after the database commit but before acknowledgement causes redelivery; the inbox makes that redelivery harmless.

**Kafka uses offsets**

For Kafka, “ACK” here means advancing the consumer group’s committed offset. Disable automatic offset commits for this workflow. Commit only offsets whose preceding records in that partition have all completed; never skip an unfinished earlier record. [[10]](#ref-10)

A generic per-message `ack()` abstraction can hide this difference. Rebalances and parallel processing need explicit offset tracking. The Java reference intentionally leaves this broker adapter outside the database consumer.

### 26The end-to-end result is a deduplicated local effect

| Boundary | What is atomic? | Recovery |
| --- | --- | --- |
| Producer database | Order transition + outbox insert | Safe command reconciliation/retry |
| Relay and broker | No joint transaction with the outbox mark | Repeat publication with the same ID |
| Consumer database | Inbox insert + local effect | Repeat delivery, skip the duplicate effect |

For a successfully processed event and retained inbox identity, this gives one committed local effect for that logical consumer. The message can still be published, received, decoded, or handled more than once.

PART V

## Read the failure contract

Analyze durable state at each crash point. A pattern name is not a substitute for this table.

### 27Use a failure matrix

| Failure window | Durable state | Recovery or requirement |
| --- | --- | --- |
| Domain validation fails | No new order/outbox commit | Reject the command |
| Order update or outbox insert fails before commit | Transaction must roll back | Retry only when the cause is transient and the command is safe |
| Commit is definitively aborted | Neither change committed | Retry the whole transaction if appropriate |
| Commit response is lost | Both may have committed; caller does not know | Read durable state / use command idempotency |
| Relay dies before send | Outbox pending | Retry publication |
| Broker rejects the send | Outbox pending | Retry with policy |
| Acceptance or ACK is uncertain | Outbox pending; broker may have it | Retry; duplicate possible |
| Send succeeds, mark fails or is uncertain | Broker has event; mark may be absent | Read pending state; duplicate possible |
| Consumer effect fails before commit | Inbox and effect roll back | Redeliver after addressing the cause |
| Consumer commit is uncertain | Inbox and effect may have committed | Do not advance offset; redelivery resolves through inbox |
| Consumer commits, ACK is lost | Inbox and effect committed | Redelivery skips effect, then acknowledges |
| Same event ID arrives again | Inbox identity already exists | Skip local effect |
| Inbox record was deleted before replay | No deduplication memory remains | Effect can repeat; retention must cover replay policy |

### 28An external side effect opens another failure window

Email, payments, or an HTTP call do not become transactional because they run between `BEGIN` and `COMMIT`. If an email send succeeds and the inbox transaction rolls back, redelivery may send a second email.

| Local consumer transaction | Later external action |
| --- | --- |
| Insert inbox Update local state Insert email-outbox intent | Dispatcher retries the provider call Then records acknowledgement |

**A second outbox preserves intent, not uniqueness at the provider**

The dispatcher still has the send-then-mark duplicate window. Duplicate external effects require provider-supported idempotency with a stable key, a naturally idempotent operation, or explicit reconciliation. An email outbox alone does not guarantee one email.

If a provider offers idempotency keys, verify their scope, retention, parameter matching, and failure rules against that provider’s documentation. The same key must survive retries for the same effect. No particular provider guarantee is assumed here.

PART VI

## Add concurrency and operational control

Introduce each mechanism to solve a demonstrated failure or capacity requirement.

### 29Multiple workers need durable claiming

Two workers can read the same pending rows. With the first relay, this produces routine duplicate publication. PostgreSQL `FOR UPDATE SKIP LOCKED` can divide available queue rows among transactions, but its locks last only as long as those transactions. [[11]](#ref-11)

PostgreSQL - lock held until transaction ends

```
SELECT *
FROM outbox_message
WHERE published_at IS NULL
ORDER BY occurred_at, id
LIMIT 100
FOR UPDATE SKIP LOCKED;
```

Keeping that transaction open while waiting on the broker holds connections and locks through slow network I/O. Committing immediately after the SELECT releases the locks and does not leave a durable claim. A lease records ownership in a short transaction instead.

PostgreSQL - commit this claim before publishing

```
-- Optional migration for multiple workers; not used by the basic relay.
ALTER TABLE outbox_message
  ADD COLUMN claim_token UUID,
  ADD COLUMN locked_until TIMESTAMPTZ;

-- Bind ? to a fresh token for this claim attempt.
WITH candidates AS (
  SELECT id FROM outbox_message
  WHERE published_at IS NULL
    AND (locked_until IS NULL OR locked_until < NOW())
  ORDER BY occurred_at, id
  LIMIT 100
  FOR UPDATE SKIP LOCKED
)
UPDATE outbox_message AS o
SET claim_token = ?, locked_until = NOW() + INTERVAL '30 seconds'
FROM candidates AS c
WHERE o.id = c.id
RETURNING o.*;
```

PostgreSQL - conditional completion

```
-- After acknowledged publication, bind row ID and the claim token.
UPDATE outbox_message
SET published_at = NOW(), claim_token = NULL, locked_until = NULL
WHERE id = ? AND claim_token = ? AND published_at IS NULL;
```

An expired lease permits another worker to claim the row. The token prevents an obsolete owner from completing a newer claim in the database. It cannot prevent an obsolete worker’s already running network send: duplicates remain possible. A zero-row completion means ownership or state changed; it is not success.

The 30-second lease is illustrative. Size or renew leases for batch duration, use database time, and test slow sends and pauses. Add retry eligibility to the claim query when adopting section 30. This example does not preserve per-aggregate ordering.

### 30Make the outbox operable

PostgreSQL - operational extension

```
-- Optional extension to the baseline schema:
ALTER TABLE outbox_message
  ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN next_attempt_at TIMESTAMPTZ,
  ADD COLUMN last_error TEXT,
  ADD COLUMN failed_at TIMESTAMPTZ;
```

These columns do nothing unless the relay updates them and its selection query honors them. Define when an attempt increments, which failures are retryable, and how a quarantined row returns to the pending set.

| Question | Useful signal or control |
| --- | --- |
| Are we falling behind? | Pending count, oldest pending age, event-to-publication latency |
| Can the worker still make progress? | Last successful pass, scheduler health, throughput |
| Which records are stuck? | Failure count, attempts, next retry, sanitized last error |
| Can we investigate one event? | Event ID, aggregate ID/version, schema version, trace correlation |
| Can storage survive an outage? | Growth rate, available capacity, cleanup progress |
| Can consumers replay safely? | Inbox age/retention and consumer lag |

Define an owner for alerts, manual replay, schema failures, and cleanup. Retain pending or failed obligations until resolved under an explicit policy. Purging an inbox row makes its event eligible to apply again; keep deduplication history for the allowed retry and replay horizon.

### 31Poison messages require a decision

A malformed or unsupported event can fail indefinitely. In the basic relay, it can stop the batch and repeatedly block later rows. Retry alone cannot repair invalid data.

| Failure type | Useful policy | Consequence |
| --- | --- | --- |
| Temporary outage or throttling | Bounded exponential backoff with jitter | Reduce load while retaining retry intent |
| Permanent payload/schema issue | Quarantine with diagnosis and alert | Normal delivery stops until repaired |
| Unknown failure | Limited investigation-friendly retries, then escalation | Avoid silent infinite loops |
| Ordering-critical event fails | Block that aggregate or reconcile deliberately | Skipping it can violate causal assumptions |

A dead-letter queue or `failed_at` field is an operational state, not proof of successful processing. Replay the same event ID for the same logical fact. If a new fact is required, make that decision visible.

PART VII

## Derive the ordering you need

Identity answers “have I processed this?” Sequence answers “what must precede this?”

### 32Specify the scope first

| Requirement | What must be serialized? |
| --- | --- |
| No required ordering | Independent effects can proceed freely |
| Per order | Events and effects for the same order |
| Per customer | Relevant changes across that customer’s orders |
| Global order | Everything in one logical sequence |

Do not assume `OrderShipped` may precede `OrderPaid` if the consumer relies on that causality. Also do not introduce global serialization because someone said “events should stay ordered.” Derive the scope from the effect.

### 33Timestamps are not a business sequence

One transaction can stamp an event earlier and commit later than another transaction. Clock skew and timestamp ties add more ambiguity. Sorting by `occurred_at, id` makes polling deterministic; it does not establish causal order.

| Field | What it expresses | What it does not prove |
| --- | --- | --- |
| occurred\_at | Application-observed event time | Commit order or causal order |
| aggregate\_version | Domain version tied to the state transition | A complete event stream for every consumer |
| event\_version | Payload contract version | Order between two business events |

Increment the aggregate version under the same concurrency control as the state change. If one transition emits several events, add an event index or stream sequence. If some versions produce no subscribed event, a consumer cannot assume “next aggregate version = last + 1.” Use a sequence specific to the delivered stream or an explicit gap policy.

### 34A broker partition preserves the order it receives

Kafka ordering is scoped to a partition. A stable aggregate key can route related events to one partition, assuming compatible partitioning and partition-count management. This does not fix events submitted out of sequence by independent relays. [[12]](#ref-12)

| Concurrent relay action | Broker arrival order |
| --- | --- |
| Worker A claims Order A v17 but stalls | Nothing yet |
| Worker B claims Order A v18 and sends | v18 |
| Worker A resumes and sends | v18, then v17 |

The broker cannot infer and repair the intended domain order from the message key. Retries, partition-count changes, and producer configuration must be included in your ordering contract.

### 35Ordering must hold through the entire path

| Stage | Necessary decision |
| --- | --- |
| Domain | Assign meaningful versions/sequences with concurrency control |
| Outbox relay | Prevent later same-key work overtaking unresolved earlier work |
| Broker | Use a stable key and a partitioning policy that preserves the intended scope |
| Consumer | Serialize same-key effects and track offsets correctly |
| Gap handling | Wait, retry, reload authoritative state, or reconcile according to the domain |

Possible relay designs include one owner per aggregate shard, sequence-aware claiming, or a log-based relay with a verified ordering contract. A lease per row is insufficient on its own. A poison event may need to block subsequent events for that aggregate.

For full-state snapshots, ignoring older versions may be correct. For deltas such as “add 100 points,” skipping an old event can lose an effect. The payload’s semantics determine whether versions may be skipped.

PART VIII

## Be precise about exactly once

Name the resource and the effect before claiming a guarantee.

### 36“Exactly once” hides several different questions

| Question | Scope |
| --- | --- |
| Was one record appended? | Broker storage |
| Was the message delivered once? | Transport and consumer session |
| Was the handler invoked once? | Process execution |
| Was the local effect committed once? | Consumer database and deduplication |
| Was the card charged or email sent once? | External provider and its idempotency contract |

These guarantees are not interchangeable. An application can tolerate repeated delivery while ensuring one committed database effect. It can also avoid duplicate broker records while still repeating an external call after a crash.

### 37Kafka transactions have a defined scope

Kafka can transactionally coordinate Kafka output records and consumed offsets for supported Kafka-to-Kafka processing. Coordinating an external destination requires that destination to participate in an appropriate scheme. A PostgreSQL update or an email call is not automatically included. [[12]](#ref-12)

A consumer that charges a card and then crashes before recording progress still needs a way to reconcile whether that charge happened. A broker-level guarantee cannot answer a question about an external resource it does not control.

### 38Idempotent producers complement the outbox

Kafka producer idempotence addresses certain protocol-level retries. It does not publish a row when the application crashed before calling Kafka, and it does not make a PostgreSQL transaction part of Kafka’s transaction.

A relay that resends an outbox row after a restart may create another application-level send. Do not treat `enable.idempotence=true` as an inbox keyed by your event UUID. Verify producer settings together, including `acks`, retries, and in-flight request limits. [[13]](#ref-13)

Java - Kafka adapter; requires the Kafka client library

```
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

/** Requires Kafka client library; uses the non-transactional send path. */
public record KafkaPublisher(Producer<String, String> producer, String topic)
        implements OutboxGuide.MessagePublisher {
    @Override
    public void publishAndAwaitAck(OutboxGuide.OutboxMessage message)
            throws Exception {
        var record = new ProducerRecord<String, String>(
                topic, message.aggregateId().toString(), message.payload());
        record.headers().add("event-id", message.id().toString()
                .getBytes(StandardCharsets.UTF_8));
        record.headers().add("event-type", message.eventType()
                .getBytes(StandardCharsets.UTF_8));
        record.headers().add("event-version",
                Integer.toString(message.eventVersion())
                        .getBytes(StandardCharsets.UTF_8));
        producer.send(record).get(30, TimeUnit.SECONDS);
        // A timeout does not prove rejection; the send may still complete.
        // Retrying the same outbox message can therefore duplicate it.
    }
}
```

This adapter uses the non-transactional producer send path. Configure `acks=all` and idempotence intentionally, along with replication and minimum in-sync replicas. A send acknowledgement proves acceptance under that configuration, not consumer completion or immunity to every storage failure. [[13]](#ref-13)

The 30-second future wait is illustrative and should be coordinated with the client delivery timeout. A local timeout does not cancel acceptance; a retry can duplicate the event. If using Kafka transactions instead, recording publication would have to wait for the Kafka transaction commit, not just a send future.

### 39Could distributed transactions solve it?

A coordinator can use two-phase commit only when every resource and adapter supports the required protocol. PostgreSQL supports prepared transactions, but that fact does not make an arbitrary broker part of the same distributed transaction. Prepared transactions can retain locks until resolved and need an external transaction manager. [[14]](#ref-14)

| Approach | What you coordinate | Cost you accept |
| --- | --- | --- |
| Distributed transaction | Participating resources under one commit protocol | Participant support, retained resources, coordinator recovery, operational coupling |
| Outbox and inbox | Local transactions plus asynchronous retry | Lag, duplicates, retention, relay and consumer operations |

Do not choose either approach by slogan. Match the resource support and consistency requirement. The outbox is especially useful when delayed propagation is allowed and durable retries are easier to operate than distributed atomic commit.

PART IX

## Test the failure contract

Prefer tests that can expose a broken atomic boundary or unsafe retry.

### 40Exercise the real failure windows

| Test | Fault or action | Required assertion |
| --- | --- | --- |
| 1. Happy path | Pay a NEW order | PAID and exactly one matching outbox row |
| 2. Outbox insertion fails | Force database failure after order update | Order update is rolled back; no outbox commit |
| 3. Domain rejection | Pay a CANCELLED order | No order or outbox change |
| 4. Broker outage | Fail publication, then recover | Row remains pending, then can be published |
| 5. Send succeeds, mark fails | Fail after acknowledged send; rerun | Same event ID can be published twice |
| 6. Duplicate consumer delivery | Deliver identical event twice, also concurrently | One inbox identity and one points credit |
| 7. Consumer effect fails | Throw after inbox insert | Inbox and effect roll back; later retry works |
| 8. Consumer commits, ACK fails | Redeliver after committed processing | No second points credit |
| 9. Relay concurrency | Run workers against actual claims | Claim/lease rules hold; stale owner cannot mark a new claim |
| 10. Ordering | Delay an earlier same-key event | Promised sequence holds or the specified gap response occurs |
| 11. Command retry | Lose commit response and retry PayOrder | No second transition or logical OrderPaid event |
| 12. Retention/replay | Replay at and beyond the deduplication horizon | Behavior matches the documented retention contract |

Use a real database to test rollback, constraints, and lock behavior. Simulate a lost commit response or process stop at the boundary rather than interpreting any thrown exception as proof that nothing committed.

### 41Place each test where its guarantee lives

| Level | Good subjects | Why |
| --- | --- | --- |
| Unit | Domain transition, event construction, retry decisions | Pure rules do not require a broker |
| Integration | Order/outbox transaction, inbox/effect transaction, constraints, SQL claims | The database supplies the actual semantics |
| System | Crash/restart, ACK ambiguity, broker outage, rebalances, ordering | The guarantee spans processes and protocols |

A mock verifying `outbox.add()` was called does not prove that it shares a transaction with the order update. A mock cannot establish that `SKIP LOCKED`, leases, or offsets behave correctly under concurrency. Test the claimed contract at its real boundary.

PART X

## Choose and explain the design

The pattern is useful when its costs buy the reliability your workflow needs.

### 42When an outbox is unnecessary or insufficient

| Situation | Appropriate conclusion |
| --- | --- |
| All required writes share one database | A normal local transaction may be enough |
| Loss is explicitly acceptable | Best-effort notification may fit |
| Success requires an immediate external reservation | An asynchronous outbox alone does not satisfy the rule; model a synchronous or pending workflow |
| Existing infrastructure already covers the exact resources atomically | Verify the scope before adding another handoff mechanism |

An outbox changes the temporal contract: the command can succeed before downstream services observe the event. UI and business workflows must tolerate that delay, or represent a pending state until the necessary external result arrives.

### 43Account for the cost

The design adds durable rows, a relay, event identity and schemas, retry decisions, cleanup, monitoring, publication latency, and consumer duplicate handling. Ordering and external effects can add further machinery.

In return, a process crash no longer erases the only evidence that publication is owed. The recovery workload becomes explicit, inspectable data. This is a useful trade when durable propagation matters, but it still needs an owner.

### 44Connect it to familiar architectural patterns

| Pattern | What the outbox makes explicit |
| --- | --- |
| Repository | Methods must share the caller’s transaction; hidden commits break atomicity |
| Dependency injection | Handler receives transactions, repositories, and Clock |
| Composition root | Choose PostgreSQL adapters and broker publisher in one wiring location |
| Ports and adapters | Business rules do not depend on a Kafka client |
| Commands and events | PayOrder is a request; OrderPaid describes the committed transition |
| Observer | In-memory notification needs durable intent when process failure matters |

The reference passes JDBC `Connection` through ports to make the physical boundary obvious. That couples those application interfaces to JDBC. A richer architecture can expose an application-owned unit of work instead, while keeping exactly the same transaction guarantee.

### 45The resulting dependency structure

| Component | Depends on | Does not own |
| --- | --- | --- |
| PayOrderHandler | TransactionRunner, OrderRepository, OutboxRepository, Clock | Broker connectivity |
| OutboxRelay | TransactionRunner, OutboxRepository, MessagePublisher | Payment business rules |
| OrderPaidConsumer | TransactionRunner, InboxRepository, LoyaltyRepository | Producer’s transaction |
| Composition root | Concrete DataSource and broker adapters | Domain validation |

Java

```
public static PayOrderHandler newHandler(DataSource producerDb) {
    PostgresStore store = new PostgresStore();
    return new PayOrderHandler(new JdbcTransactions(producerDb),
            store, store, Clock.systemUTC());
}

public static OutboxRelay newRelay(
        DataSource producerDb, MessagePublisher publisher) {
    return new OutboxRelay(new JdbcTransactions(producerDb),
            new PostgresStore(), publisher);
}

public static OrderPaidConsumer newConsumer(DataSource consumerDb) {
    PostgresStore store = new PostgresStore();
    return new OrderPaidConsumer(new JdbcTransactions(consumerDb),
            store, store);
}
```

Producer and consumer data sources are separate service resources. Inside each service, all repositories participating in one effect use that service’s one transaction connection.

### 46Use the reasoning again

For the next distributed workflow, work through these questions in order:

1. Which business facts must agree?
2. Which can share one actual atomic transaction?
3. Which operations cross an independently failing boundary?
4. Can the obligation to cross it be recorded durably?
5. What survives a crash before and after each operation?
6. Can retries create duplicates, and which identity stays stable?
7. Can the receiver make its effect safe to repeat?
8. What ordering is required, and at what scope?
9. What retention, monitoring, and reconciliation make recovery possible?

### 47State a concrete, testable promise

**The failure contract**

If the producer transaction commits, the business transition and its publication intent are stored together. The relay retries retained pending intent and may publish it more than once. The consumer commits its inbox identity with its local effect, so duplicate delivery does not repeat that effect while the identity is retained.

Eventual progress depends on recoverable infrastructure, valid messages, continued retries, and a retention policy that preserves the work. External side effects and required ordering need their own explicit contracts.

| Producer database | Network and broker | Consumer database |
| --- | --- | --- |
| **Atomic** Business state + outbox | **Retryable** Stable ID; duplicates possible | **Atomic** Inbox + local effect |

The design contains failure where durable state makes recovery possible and where repeated work can be made harmless.

APPENDIX A

## Complete Java reference

A coherent teaching implementation with explicit boundaries.

The embedded `OutboxGuide.java` uses standard Java language features and JDK APIs available in Java 25, without preview features. It defines the domain, ports, JDBC transaction runner, handlers, a single-worker relay, and PostgreSQL adapters. It is a reference library, not a server with a `main` method.

**Verification scope**

⚠️ API signatures and SQL behavior were checked against the official references below. This environment has no working Java compiler or running PostgreSQL/Kafka services, so these examples have not been compiled or integration-tested here. Run the commands and boundary tests below in your own Java 25 setup.

Compilation of the core source needs only a JDK. Execution against PostgreSQL additionally needs a compatible pgJDBC driver, a configured `DataSource`, and the schema in Appendix B. The Kafka adapter additionally needs the Kafka client library. Resolve and pin dependency versions appropriate to your environment; they are not bundled into this HTML.

Compile commands

```
javac --release 25 OutboxGuide.java

# Linux/macOS; use ; instead of : as the classpath separator on Windows.
# Replace /path/to/... with the actual Kafka client JAR location.
javac --release 25 -cp ".:/path/to/kafka-clients.jar" KafkaPublisher.java
```

The adapter uses `OffsetDateTime` for PostgreSQL `TIMESTAMPTZ` bindings and converts to/from the domain’s `Instant`. pgJDBC documents this mapping and does not directly support `Instant` for that path. [[15]](#ref-15)

**Implementation boundaries**

The basic relay is single-worker and does not implement ordering, leases, retry backoff, quarantine, cleanup, or broker consumer offsets. Those are explicitly discussed extensions. Records are used to make data and injected dependencies concise; they are not required by the outbox pattern.

Download OutboxGuide.javaDownload KafkaPublisher.javaShow full Java source

OutboxGuide.java - full source

OutboxGuide.java · lines 1-36

```
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;

/** Java 25-compatible teaching example; no preview features. */
public final class OutboxGuide {
    private OutboxGuide() {}

    // BEGIN domain
    public record PayOrder(UUID orderId) {}

    public record OrderPaid(
            UUID eventId, UUID orderId, UUID customerId,
            long orderVersion, Instant occurredAt) {}

    public enum Status { NEW, PAID, CANCELLED }

    public record Order(
            UUID id, UUID customerId, Status status, long version) {
        public Order markPaid() {
            if (status == Status.CANCELLED) {
                throw new IllegalStateException("Cancelled order");
            }
            if (status == Status.PAID) return this;
            return new Order(id, customerId, Status.PAID,
```

OutboxGuide.java · lines 37-72

```
                Math.addExact(version, 1));
    }
}

public record OutboxMessage(
        UUID id, String eventType, int eventVersion,
        UUID aggregateId, long aggregateVersion,
        String payload, Instant occurredAt) {
    public static OutboxMessage from(OrderPaid e) {
        // Safe here: UUIDs, an integer, and Instant's ISO text only.
        // Use a JSON serializer if arbitrary text fields are added.
        String json = """
                {"eventId":"%s","orderId":"%s",
                 "customerId":"%s","orderVersion":%s,
                 "occurredAt":"%s"}
                """.formatted(e.eventId(), e.orderId(),
                e.customerId(), Long.toString(e.orderVersion()),
                e.occurredAt());
        return new OutboxMessage(e.eventId(), "OrderPaid", 1,
                e.orderId(), e.orderVersion(), json, e.occurredAt());
    }
}
// END domain

// BEGIN transaction
@FunctionalInterface
public interface SqlWork<T> {
    T run(Connection connection) throws SQLException;
}

public interface TransactionRunner {
    <T> T inTransaction(SqlWork<T> work) throws SQLException;
}

public record JdbcTransactions(DataSource dataSource)
        implements TransactionRunner {
```

OutboxGuide.java · lines 73-108

```
    @Override
    public <T> T inTransaction(SqlWork<T> work)
            throws SQLException {
        // Own a fresh connection; no nested/JTA transaction support.
        try (Connection c = dataSource.getConnection()) {
            c.setAutoCommit(false);
            try {
                T result = work.run(c);
                c.commit();
                return result;
            } catch (SQLException | RuntimeException | Error failure) {
                try {
                    c.rollback();
                } catch (SQLException rollbackFailure) {
                    failure.addSuppressed(rollbackFailure);
                }
                // A commit/connection error can have unknown outcome.
                // No automatic retry or claim of successful rollback.
                throw failure;
            }
        }
    }
}
// END transaction

// BEGIN ports
public interface OrderRepository {
    Optional<Order> findForUpdate(Connection c, UUID id)
            throws SQLException;
    void save(Connection c, Order order) throws SQLException;
}

public interface OutboxRepository {
    void add(Connection c, OutboxMessage message) throws SQLException;
    List<OutboxMessage> findPending(Connection c, int limit)
            throws SQLException;
```

OutboxGuide.java · lines 109-144

```
    void markPublished(Connection c, UUID id) throws SQLException;
}

public interface InboxRepository {
    boolean tryInsert(Connection c, String consumer, UUID messageId)
            throws SQLException;
}

public interface LoyaltyRepository {
    void addPoints(Connection c, UUID customerId, long points)
            throws SQLException;
}

@FunctionalInterface
public interface MessagePublisher {
    // Return only after acknowledgement under the broker's
    // configured durability policy. Keep the original event ID.
    void publishAndAwaitAck(OutboxMessage message) throws Exception;
}
// END ports

// BEGIN handler
public record PayOrderHandler(
        TransactionRunner transactions, OrderRepository orders,
        OutboxRepository outbox, Clock clock) {
    public void handle(PayOrder command) throws SQLException {
        transactions.inTransaction(c -> {
            Order before = orders.findForUpdate(c, command.orderId())
                    .orElseThrow(() ->
                            new IllegalArgumentException("Unknown order"));
            Order paid = before.markPaid();
            if (before.status() == Status.PAID) return null;

            orders.save(c, paid);
            OrderPaid event = new OrderPaid(
                    UUID.randomUUID(), paid.id(), paid.customerId(),
```

OutboxGuide.java · lines 145-180

```
                    paid.version(), clock.instant());
            outbox.add(c, OutboxMessage.from(event));
            return null;
        });
    }
}
// END handler

// BEGIN relay
public record OutboxRelay(
        TransactionRunner transactions, OutboxRepository outbox,
        MessagePublisher publisher) {
    // Exactly one active worker for this teaching implementation.
    // This sorted poll is not a causal-ordering guarantee.
    public void runOnce() throws Exception {
        List<OutboxMessage> batch = transactions.inTransaction(
                c -> outbox.findPending(c, 100));
        for (OutboxMessage message : batch) {
            publisher.publishAndAwaitAck(message);
            transactions.inTransaction(c -> {
                outbox.markPublished(c, message.id());
                return null;
            });
        }
        // A failure exits the batch; the row remains eligible.
        // Backoff/quarantine are extensions, not implemented here.
    }
}

public static ScheduledFuture<?> schedule(
        ScheduledExecutorService scheduler, OutboxRelay relay) {
    System.Logger log = System.getLogger("outbox-relay");
    return scheduler.scheduleWithFixedDelay(() -> {
        try {
            relay.runOnce();
        } catch (InterruptedException interrupted) {
```

OutboxGuide.java · lines 181-216

```
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Relay interrupted",
                    interrupted);
        } catch (Exception failure) {
            log.log(System.Logger.Level.ERROR,
                    "Relay pass failed; pending rows will retry", failure);
        }
    }, 0, 1, TimeUnit.SECONDS);
}
// END relay

// BEGIN consumer
public record OrderPaidConsumer(
        TransactionRunner transactions, InboxRepository inbox,
        LoyaltyRepository loyalty) {
    public void handle(OrderPaid event) throws SQLException {
        transactions.inTransaction(c -> {
            if (!inbox.tryInsert(c, "loyalty-order-paid-v1",
                    event.eventId())) return null;
            loyalty.addPoints(c, event.customerId(), 100);
            return null;
        });
    }
}
// Broker adapter acknowledges/commits offsets AFTER handle returns.
// JSON decoding, validation and broker offset management are adapters.
// END consumer

// BEGIN postgres-orders
public static final class PostgresStore implements
        OrderRepository, OutboxRepository,
        InboxRepository, LoyaltyRepository {
    @Override
    public Optional<Order> findForUpdate(Connection c, UUID id)
            throws SQLException {
        try (var s = c.prepareStatement("""
```

OutboxGuide.java · lines 217-252

```
            SELECT id, customer_id, status, version
            FROM orders WHERE id = ? FOR UPDATE
            """)) {
        s.setObject(1, id);
        try (var rs = s.executeQuery()) {
            if (!rs.next()) return Optional.empty();
            return Optional.of(new Order(
                    rs.getObject("id", UUID.class),
                    rs.getObject("customer_id", UUID.class),
                    Status.valueOf(rs.getString("status")),
                    rs.getLong("version")));
        }
    }
}

@Override
public void save(Connection c, Order order) throws SQLException {
    try (var s = c.prepareStatement("""
            UPDATE orders SET status = ?, version = ?
            WHERE id = ? AND version = ?
            """)) {
        s.setString(1, order.status().name());
        s.setLong(2, order.version());
        s.setObject(3, order.id());
        s.setLong(4, order.version() - 1);
        if (s.executeUpdate() != 1) {
            throw new SQLException("Order version mismatch");
        }
    }
}
// END postgres-orders

// BEGIN postgres-outbox
@Override
public void add(Connection c, OutboxMessage m) throws SQLException {
    try (var s = c.prepareStatement("""
```

OutboxGuide.java · lines 253-288

```
            INSERT INTO outbox_message
              (id, event_type, event_version, aggregate_id,
               aggregate_version, payload, occurred_at)
            VALUES (?, ?, ?, ?, ?, CAST(? AS jsonb), ?)
            """)) {
        s.setObject(1, m.id());
        s.setString(2, m.eventType());
        s.setInt(3, m.eventVersion());
        s.setObject(4, m.aggregateId());
        s.setLong(5, m.aggregateVersion());
        s.setString(6, m.payload());
        s.setObject(7, m.occurredAt().atOffset(ZoneOffset.UTC));
        s.executeUpdate();
    }
}

@Override
public List<OutboxMessage> findPending(Connection c, int limit)
        throws SQLException {
    try (var s = c.prepareStatement("""
            SELECT id, event_type, event_version, aggregate_id,
                   aggregate_version, payload::text, occurred_at
            FROM outbox_message
            WHERE published_at IS NULL
            ORDER BY occurred_at, id LIMIT ?
            """)) {
        s.setInt(1, limit);
        try (var rs = s.executeQuery()) {
            List<OutboxMessage> result = new ArrayList<>();
            while (rs.next()) {
                result.add(new OutboxMessage(
                        rs.getObject("id", UUID.class),
                        rs.getString("event_type"),
                        rs.getInt("event_version"),
                        rs.getObject("aggregate_id", UUID.class),
                        rs.getLong("aggregate_version"),
```

OutboxGuide.java · lines 289-324

```
                        rs.getString("payload"),
                        rs.getObject("occurred_at", OffsetDateTime.class)
                                .toInstant()));
            }
            return List.copyOf(result);
        }
    }
}

@Override
public void markPublished(Connection c, UUID id) throws SQLException {
    try (var s = c.prepareStatement("""
            UPDATE outbox_message SET published_at = NOW()
            WHERE id = ? AND published_at IS NULL
            """)) {
        s.setObject(1, id);
        if (s.executeUpdate() != 1) {
            throw new SQLException("Pending outbox row not found");
        }
    }
}
// END postgres-outbox

// BEGIN postgres-inbox
@Override
public boolean tryInsert(Connection c, String consumer, UUID id)
        throws SQLException {
    try (var s = c.prepareStatement("""
            INSERT INTO inbox_message
              (consumer_name, message_id, processed_at)
            VALUES (?, ?, NOW())
            ON CONFLICT (consumer_name, message_id) DO NOTHING
            """)) {
        s.setString(1, consumer);
        s.setObject(2, id);
        return s.executeUpdate() == 1;
```

OutboxGuide.java · lines 325-360

```
        }
    }

    @Override
    public void addPoints(Connection c, UUID customerId, long points)
            throws SQLException {
        try (var s = c.prepareStatement("""
                INSERT INTO customer_loyalty (customer_id, points)
                VALUES (?, ?)
                ON CONFLICT (customer_id) DO UPDATE
                SET points = customer_loyalty.points + EXCLUDED.points
                """)) {
            s.setObject(1, customerId);
            s.setLong(2, points);
            s.executeUpdate();
        }
    }
}
// END postgres-inbox

// BEGIN composition
public static PayOrderHandler newHandler(DataSource producerDb) {
    PostgresStore store = new PostgresStore();
    return new PayOrderHandler(new JdbcTransactions(producerDb),
            store, store, Clock.systemUTC());
}

public static OutboxRelay newRelay(
        DataSource producerDb, MessagePublisher publisher) {
    return new OutboxRelay(new JdbcTransactions(producerDb),
            new PostgresStore(), publisher);
}

public static OrderPaidConsumer newConsumer(DataSource consumerDb) {
    PostgresStore store = new PostgresStore();
    return new OrderPaidConsumer(new JdbcTransactions(consumerDb),
```

OutboxGuide.java · lines 361-364

```
                store, store);
    }
    // END composition
}
```

APPENDIX B

## Database schema

The baseline used by the complete reference.

Run the producer tables in the producer database and the consumer tables in the consumer database. The optional lease and operational migrations in sections 29-30 are separate extensions; the baseline relay does not use them.

Download schema.sql

schema.sql

```
-- PostgreSQL 18 syntax. Run each group on its owning service database.
-- Producer database
CREATE TABLE orders (
    id          UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    status      VARCHAR(20) NOT NULL
                CHECK (status IN ('NEW', 'PAID', 'CANCELLED')),
    version     BIGINT NOT NULL DEFAULT 0 CHECK (version >= 0)
);

CREATE TABLE outbox_message (
    id                UUID PRIMARY KEY,
    event_type        VARCHAR(200) NOT NULL,
    event_version     INTEGER NOT NULL CHECK (event_version > 0),
    aggregate_id      UUID NOT NULL,
    aggregate_version BIGINT NOT NULL,
    payload           JSONB NOT NULL,
    occurred_at       TIMESTAMPTZ NOT NULL,
    published_at      TIMESTAMPTZ
);
CREATE INDEX idx_outbox_unpublished
    ON outbox_message (occurred_at, id)
    WHERE published_at IS NULL;

-- Consumer database
CREATE TABLE inbox_message (
    consumer_name VARCHAR(200) NOT NULL,
    message_id    UUID NOT NULL,
    processed_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (consumer_name, message_id)
);

CREATE TABLE customer_loyalty (
    customer_id UUID PRIMARY KEY,
    points      BIGINT NOT NULL DEFAULT 0
);
```

APPENDIX C

## Official references

Checked on 2 September 2026. Java 25, PostgreSQL 18, and versioned Kafka 4.1 documentation.

The failure scenarios and architectural derivation follow the supplied conversation. The official references ground API and product-specific behavior; they are not a claim that these samples form a production-certified stack. The opening derivation makes the supplied excerpt standalone.

1. [PostgreSQL 18: Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)

   Atomic grouping, commit, rollback.

   https://www.postgresql.org/docs/current/tutorial-transactions.html
2. [PostgreSQL 18: Explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html)

   Row locks and concurrent updates.

   https://www.postgresql.org/docs/18/explicit-locking.html
3. [Java SE 25: Connection](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html)

   Auto-commit, commit, rollback, connection lifecycle.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html
4. [PostgreSQL 18: Error codes](https://www.postgresql.org/docs/18/errcodes-appendix.html)

   Includes transaction\_resolution\_unknown (08007).

   https://www.postgresql.org/docs/18/errcodes-appendix.html
5. [Java SE 25: ScheduledExecutorService](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html)

   Periodic tasks stop on unhandled exceptions.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html
6. [Apache Kafka 4.1: KafkaProducer API](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)

   Asynchronous send and acknowledgement futures.

   https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html
7. [PostgreSQL 18: INSERT](https://www.postgresql.org/docs/18/sql-insert.html)

   ON CONFLICT and uniqueness handling.

   https://www.postgresql.org/docs/18/sql-insert.html
8. [Java SE 25: PreparedStatement](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/PreparedStatement.html)

   Bound parameters and update counts.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/PreparedStatement.html
9. [PostgreSQL 18: Transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html)

   Read Committed conflicts and transaction retries.

   https://www.postgresql.org/docs/18/transaction-iso.html
10. [Apache Kafka 4.1: KafkaConsumer API](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)

    Manual offset management and external stores.

    https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html
11. [PostgreSQL 18: SELECT](https://www.postgresql.org/docs/18/sql-select.html)

    FOR UPDATE SKIP LOCKED and queue access.

    https://www.postgresql.org/docs/18/sql-select.html
12. [Apache Kafka 4.1: Design](https://kafka.apache.org/41/design/design/)

    Partition ordering and the scope of delivery semantics.

    https://kafka.apache.org/41/design/design/
13. [Apache Kafka 4.1: Producer configs](https://kafka.apache.org/41/configuration/producer-configs/)

    Idempotence, acknowledgements and retry configuration.

    https://kafka.apache.org/41/configuration/producer-configs/
14. [PostgreSQL 18: PREPARE TRANSACTION](https://www.postgresql.org/docs/18/sql-prepare-transaction.html)

    Two-phase support and retained resources.

    https://www.postgresql.org/docs/18/sql-prepare-transaction.html
15. [pgJDBC: Querying and processing results](https://jdbc.postgresql.org/documentation/query/)

    TIMESTAMPTZ mapping to OffsetDateTime.

    https://jdbc.postgresql.org/documentation/query/

DP · Transactional Outbox · Java 25-compatible reference
Self-contained HTML. All styling and download code are embedded. External links are optional reference reading.