[Skip to guide](#content)[DPFirst principles / 21](#top)

[Java reference](#reference)Print / Save PDF

IN THIS GUIDE

[IThe pressure1–4](#pressure)[IICompare and advance5–11](#mechanism)[IIIConsistency boundary12–15](#boundary)[IVRecovery and retries16–21](#recovery)[VOutbox and events22–26](#events)[VIPersistence and ORM27–32](#persistence)[VIIAPI and user workflows33–36](#api)[VIIIAlternatives and limits37–44](#alternatives)[IXDatabase testing45–50](#tests)[XGuarantee and connections51–58](#synthesis)[AComplete Java / JDBC](#reference)[BDatabase race test](#race-test)[↗Official sources](#sources)

Read → decide → verify
Then commit or reconsider.

DP · Design patterns from first principles

# 21. Optimistic Concurrency Control

We ended with an `Order` aggregate protecting this invariant:

> An order may contain at most **100 total units.**

The next question is what happens when two requests each load a valid order, each make a valid decision, and then try to persist both decisions.

Java 25-compatible code · PostgreSQL 18 examples · 58 reasoning steps

**How to use this guide**

Read the numbered steps in order: each introduces the pressure that motivates the next mechanism. The short code blocks explain one idea at a time. Appendix A contains the complete JDBC reference implementation and schema; Appendix B contains a real two-connection race test.

All content, styles, and controls are embedded. The guide works offline. Use **Print / Save PDF** for a single-column print layout; the entire guide prints even with JavaScript disabled. Official-source links require a connection.

## I. The pressure: two correct decisions can conflict

### 01Re-establish the aggregate

An aggregate is a group of domain objects whose consistency rules are protected through a root. Here, callers ask `Order` to add a line; they do not mutate its internal list directly. A repository loads and saves the whole order as one consistency boundary.

Start with a draft order containing Product A, quantity 90. Its remaining capacity is 10. The local rule is straightforward:

JAVACopy

```
void addLine(UUID productId, int quantity) {
    requireDraft();
    Objects.requireNonNull(productId);
    if (quantity <= 0) throw new IllegalArgumentException("Quantity");
    if (quantity > 100 - totalUnits()) {
        throw new OrderCapacityExceeded();
    }
    lines.add(new Line(UUID.randomUUID(), productId, quantity));
}
```

The subtraction avoids overflowing an `int` when checking a large requested quantity. Positive quantities and a previously valid total make this check safe. Immutable `Line` values and defensive list copies prevent callers from bypassing the root.

### 02Introduce two concurrent requests

Request A adds 10 units of Product B. Request B adds 10 units of Product C. Both load the same committed order before either saves.

| Step | Transaction A | Transaction B |
| --- | --- | --- |
| 1 | Load total = 90 |  |
| 2 |  | Load total = 90 |
| 3 | Check 90 + 10 ≤ 100: valid |  |
| 4 |  | Check 90 + 10 ≤ 100: valid |
| 5 | Insert Product B, quantity 10; commit |  |
| 6 |  | Insert Product C, quantity 10; commit |

If persistence applies independent child inserts without coordinating the root, the final total can be **110**. A different naive save strategy, such as replacing a stale snapshot of all lines, might instead lose one request's update. The exact failure depends on the writes; neither result is a valid concurrency policy.

### 03Diagnose the missing question

Each Java object correctly checked its own copy. Neither knew the other copy existed. We have **two independently loaded instances of the same consistency boundary**.

The missing question is: **Has the relevant state changed since I loaded it?** Local validation answers whether a decision fits the examined state. Concurrency control must establish whether that examined state is still suitable for committing the decision.

### 04Why a transaction alone is not enough

Atomicity makes a transaction's changes commit or roll back together. Isolation determines what concurrent transactions can observe and how their operations interact. These are separate guarantees.

PostgreSQL's default `READ COMMITTED` gives an ordinary query a snapshot at the start of that statement. Separate queries in one transaction can therefore see different committed states. Two transactions can both read 90 before either writes. [PostgreSQL: transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-READ-COMMITTED)

Putting both handlers in transactions preserves each handler's atomicity. It does not, by itself, implement the cross-line 100-unit rule under every interleaving. We need an explicit concurrency decision.

## II. Derive the mechanism: remember, compare, advance

### 05Remember which revision was loaded

Add a version to the root row:

SQLCopy

```
ALTER TABLE orders
ADD COLUMN version BIGINT NOT NULL DEFAULT 0;
```

| Order | Status | Version | Total units |
| --- | --- | --- | --- |
| #123 | DRAFT | 7 | 90 |

When we load version 7, our decisions are based on revision 7. The version is a token for the aggregate's relevant state, not a count of child rows.

In the reference implementation, `Order.loadedVersion` is immutable metadata: it records the revision read. The repository returns a candidate next version, and the transaction wrapper returns it to the caller only after commit. An alternative design can keep the token in a `LoadedOrder` wrapper outside the domain object.

### 06Make the update conditional

A blind update only identifies the order:

SQLCopy

```
UPDATE orders SET version = 8 WHERE id = :order_id;
```

Both writers could execute it. Instead, require the original revision:

SQLCopy

```
UPDATE orders
SET version = 8
WHERE id = :order_id AND version = 7;
```

The named parameter here is explanatory SQL notation; JDBC uses `?` placeholders. The comparison and update must be **one atomic database operation**. A separate `SELECT version`, followed by an unconditional `UPDATE`, leaves another race between those statements.

### 07Recognize compare-and-swap

We have derived a compare-and-swap operation: compare the stored version with the expected version; advance it only when they match.

| Expected revision | Current revision | Conditional update result |
| --- | --- | --- |
| 7 | 7 | One row updated; candidate revision becomes 8 |
| 7 | 8 | Zero rows updated; stale write rejected |

A primary key limits the update to at most one root. Zero rows can also mean the root was deleted. The repository can report this as “the expected revision no longer exists” without pretending it knows which change occurred.

### 08Run the race again

Both A and B load total 90 at version 7. Both locally add 10. A's conditional root update affects one row; A writes its children and commits version 8, total 100. B's update expecting 7 affects zero rows; B rolls back.

If B reaches the root update before A finishes, it can wait. At `READ COMMITTED`, PostgreSQL rechecks the update condition after a conflicting updater commits. If A commits version 8, B no longer matches; if A rolls back, B can still succeed. [PostgreSQL: concurrent updates](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-READ-COMMITTED)

**One committed winner**100 unitsversion 8stale writer rejected

### 09Let the repository detect the conflict

The save method computes the candidate revision and checks the affected-row count:

JAVACopy

```
long next = Math.incrementExact(order.loadedVersion());
String sql = """
    UPDATE orders SET status = ?, version = ?
    WHERE id = ? AND version = ?
    """;
try (var p = c.prepareStatement(sql)) {
    p.setString(1, order.status().name());
    p.setLong(2, next);
    p.setObject(3, order.id());
    p.setLong(4, order.loadedVersion());
    if (p.executeUpdate() != 1) {
        throw new ConcurrentOrderModification(
                order.id(), order.loadedVersion());
    }
    replaceLines(order);
    return next; // Provisional until the surrounding commit.
}
```

This is an excerpt from the complete adapter. JDBC's update API supplies the row count used for the check. [Java 25: Statement](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Statement.html#executeUpdate(java.lang.String))

### 10Keep child writes in the same transaction

Suppose B inserted a child before detecting the conflict. That insert must roll back with the failed save. The same rule applies if a child write fails after the root version update: the root update must roll back too.

Use **one connection, one transaction, one commit decision** for root, children, and any outbox rows. Throwing a Java exception alone does not undo SQL. The transaction owner must roll back; JDBC advises explicitly committing or rolling back before closing an active connection. [Java 25: Connection](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html#close())

### 11Explain “optimistic” precisely

We first read and decide without acquiring an exclusive root lock for the whole decision period. At write time, we verify the assumption that our revision is still valid.

This does **not** mean “no locks.” The conditional `UPDATE` still participates in database locking and can wait for another writer. Pessimistic locking moves coordination earlier, commonly with `SELECT ... FOR UPDATE`. PostgreSQL holds that row lock until the transaction ends and blocks conflicting writers and lockers. [PostgreSQL: row-level locks](https://www.postgresql.org/docs/18/explicit-locking.html#LOCKING-ROWS)

## III. Put the token on the consistency boundary

### 12Version the aggregate, not just each child

If A creates Line B while B creates Line C, they touch different child rows. Individual line versions have nothing to compare with one another. Yet the invariant depends on their **combined quantities**.

The order root supplies a shared concurrency token. Every writer whose change can affect the order's rule must contend on that token. The token covers the decision's dependency set: all state whose change could invalidate the decision.

### 13Make every relevant mutation participate

Changing only an `OrderLine` still changes the aggregate. The root version must advance even when no other root column needs updating. Apply the same discipline to line removal, quantity changes, confirmation, and version-aware deletion.

Background jobs, administrative tools, batch SQL, and other services cannot bypass this protocol without weakening its guarantee. A bulk update that skips the version is a bypass. A read-only operation need not advance a revision merely because it loaded the order.

### 14Keep ownership clear

| Owner | Question it answers |
| --- | --- |
| `Order` | Does this operation satisfy the business rules for the state I hold? |
| Repository / Unit of Work | Does the database still match the revision on which this work depends? |
| Application | Should a conflict be rejected, reloaded, or retried? |

Keep `addLine(productId, quantity)` focused on business behavior. It should not accept a JDBC connection or an expected database version. Passive revision metadata is a design choice; SQL coordination inside domain behavior is a dependency leak.

### 15Preserve Ports & Adapters

The application depends on domain objects and ports. The JDBC adapter implements the ports. The domain does not call the repository to save itself.

JAVACopy

```
interface OrderRepository {
    Order get(UUID id);
    long save(Order order);
}

interface Transactions {
    <T> T execute(Work<T> work);
}
```

The adapter binds both the repository and outbox to the same connection. No `Connection` appears in these application-facing signatures. Keeping a connection parameter in an explicitly infrastructure-only helper is fine; putting it in a domain port would change the dependency contract.

## IV. Recover by redoing the decision

### 16Separate stale state from invalid behavior

`OrderCapacityExceeded` means the request did not fit the state examined. `ConcurrentOrderModification` means the examined revision no longer matched at save time.

These are different outcomes. A domain rejection does not prove the state remains current forever; a concurrency rejection does not prove the command is intrinsically invalid. Reloading may change the answer.

### 17Classify failures before deciding to retry

| Failure | Meaning | Appropriate next step |
| --- | --- | --- |
| Domain failure | Business rule rejects the operation on the examined state | Explain the rejection; retry only if inputs or relevant state change |
| Optimistic conflict | Expected revision no longer matches | Roll back; reject or reconsider on fresh state |
| Infrastructure failure | A database operation or communication failed | Classify the cause and determine whether the outcome is known |

Do not catch every exception and blindly retry. In particular, a lost connection during commit can leave the caller uncertain about whether the operation committed. An idempotency key or reconciliation may be needed before replaying an additive command. This is an outcome-uncertainty problem, separate from a known failed version check.

### 18See what a correct retry does

In our example, A commits 100 units. B receives a version conflict. B then reloads and tries its original intent—add 10—against total 100. The aggregate now throws `OrderCapacityExceeded`.

The retry did its job even though the command did not succeed. Its purpose was to obtain a valid decision on fresh state. It must never turn a stale approval into permission to exceed capacity.

### 19Retry the whole transaction

Discard the stale order and the failed transaction. Begin a new transaction, reload, rerun the business operation, attempt the save, and commit. Retrying only the failed `UPDATE`, or replacing its expected version with the latest version without revalidating, defeats the protection.

PostgreSQL similarly requires complete transaction retries for serialization failures, including the logic that chose the SQL and its values. Those failures use SQLSTATE `40001`; they need an explicit policy alongside application version conflicts. [PostgreSQL: serialization failure handling](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html)

### 20Use a bounded, specific retry wrapper

JAVACopy

```
static <T> T retryConflict(int maxAttempts, Supplier<T> entireAttempt) {
    if (maxAttempts < 1) throw new IllegalArgumentException("maxAttempts");
    for (int attempt = 1; ; attempt++) {
        try {
            return entireAttempt.get();
        } catch (ConcurrentOrderModification conflict) {
            if (attempt == maxAttempts || conflict.getSuppressed().length != 0) {
                throw conflict;
            }
        }
    }
}
```

Call it around the transaction-owning use case, so each invocation opens fresh work:

JAVACopy

```
long committedVersion = retryConflict(3,
        () -> addLine(tx, orderId, productId, 10));
```

This sample retries only its own `ConcurrentOrderModification`. Java's `java.util.ConcurrentModificationException` is a different type and is not a database conflict contract. The sample omits backoff for clarity; under contention, use a bounded delay with jitter, a deadline, and cancellation appropriate to the service. Never retry a domain rejection or an arbitrary SQL error through this wrapper.

### 21Keep external effects outside retryable work

Charging a card before the conditional save is dangerous. If the save conflicts, a retry might charge again even though the first local database transaction rolled back. An HTTP call is not undone by JDBC rollback.

A retryable unit should usually load state, run domain behavior, write the aggregate, write any durable outgoing message, then commit. Delivery happens afterward. If an external call must occur synchronously, it needs its own idempotency and recovery design.

## V. Combine the version check with an outbox

### 22Commit state and the event together

An outbox is a table of outgoing messages written in the same transaction as the state change. A separate relay delivers committed rows later. Here is the application flow for confirming an order:

JAVACopy

```
static long confirm(Transactions tx, UUID id) {
    return tx.execute(s -> {
        Order order = s.orders().get(id);
        order.confirm();
        long next = s.orders().save(order);
        s.outbox().append(UUID.randomUUID(), id, next, "OrderConfirmed");
        return next;
    });
}
```

If save or outbox insertion fails, the wrapper rolls back both. The relay must publish only committed rows. Outbox delivery can still duplicate messages, so consumers need idempotency. [AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

### 23Do not let the outbox survive a failed transition

An outbox insert in its own transaction could survive while order confirmation fails. That would advertise an event which never happened. The version check, child writes, root state, and outbox insert must share the **same local commit or rollback**.

The event ID is durable message identity. It helps a consumer deduplicate repeated delivery of one committed message. It does not automatically deduplicate two separately accepted client requests.

### 24Attach the committed aggregate revision to events

| State transition | Event metadata |
| --- | --- |
| Order v7 → v8: confirm | `OrderConfirmed`, `aggregateVersion = 8` |
| Order v8 → v9: pack | `OrderPacked`, `aggregateVersion = 9` |
| Order v9 → v10: ship | `OrderShipped`, `aggregateVersion = 10` |

Packing and shipping illustrate later behavior; the reference domain implements draft and confirmed states only. Version metadata lets a consumer relate an event to a revision of that order.

**A gap is meaningful only under an explicit event contract.** Receiving v10 after v8 suggests a missing or out-of-order event only if the consumer was entitled to an event for v9. Some mutations may emit no event, or the subscription may filter event types. An aggregate version alone does not prove that a message was lost.

### 25Do not treat it as a global sequence

Order A v10 and Order B v10 have no shared ordering meaning. Even when v8 precedes v9 for one order, version metadata does not itself force transport delivery order. The relay, partitioning, consumer, and reconciliation policy must implement whatever ordering the workflow requires.

Use the pair `(aggregateId, aggregateVersion)` to identify a revision. Do not compare unrelated aggregates' numeric versions to infer which business event happened first.

### 26Handle multiple events from one revision deliberately

One confirmation might produce `OrderConfirmed`, `CustomerNotificationRequested`, and `InventoryReservationRequested`, all at version 8. The revision identifies their shared state transition, not their order within it.

If consumers require that order, add an event index such as `(aggregateId, version, eventIndex)`, and retain a unique event ID for deduplication. If no consumer needs the ordering, avoid introducing a sequencing protocol merely because it is possible.

## VI. Make persistence implement the model

### 27Build a concrete JDBC repository

Use a root table with `id`, `status`, and `version`, a child table with `order_id` and positive `quantity`, and an outbox table. Appendix A supplies the complete schema, including a draft order seeded at version 7 with 90 units.

The reference loader deliberately uses a single joined query:

SQLCopy

```
SELECT o.status, o.version, l.id AS line_id, l.product_id, l.quantity
FROM orders o
LEFT JOIN order_line l ON l.order_id = o.id
WHERE o.id = ?
ORDER BY l.id;
```

This reconstructs the root and children from one statement snapshot. With separate reads at `READ COMMITTED`, the root and children can come from different revisions. The later version check might reject such work, but a mixed read can already produce confusing validation or read responses. A coherent load avoids that problem. [PostgreSQL: statement snapshots](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-READ-COMMITTED)

### 28Check the root before writing children

The implementation order is: conditionally advance the root; persist the lines; append required outbox messages; commit. Stale work fails before doing unnecessary child writes.

For this small example, line persistence deletes and reinserts the order's lines while preserving their IDs. Positive quantities and the 100-unit cap bound the line count. This is a teaching choice: use a diff when row churn, audit triggers, or external references make replacement inappropriate. The concurrency contract remains the same.

### 29Distinguish “saved” from “committed”

An `UPDATE` returning one row means that statement succeeded inside the transaction. A later child failure, outbox failure, or commit failure can still prevent a successful unit of work.

The reference design therefore keeps `loadedVersion` unchanged, returns a provisional number from `save`, and exposes that number from the transaction wrapper only after `commit` returns. It saves each order once per transaction and discards its mutable instance afterward. It never calls `markPersistedAt` before commit.

If a design reuses objects after rollback, it needs an explicit restoration strategy. Request-scoped disposal is simpler. A commit communication failure still needs outcome reconciliation; changing the in-memory number cannot resolve that uncertainty.

### 30Map the idea to Jakarta Persistence / Hibernate

JAVACopy

```
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Version;
import java.util.UUID;

@Entity
public class OrderEntity {
    @Id
    private UUID id;
    @Version
    private long version;

    protected OrderEntity() {}
}
```

This separate mapping example requires the Jakarta Persistence API and a provider; they are not part of the JDK. A versioned entity gives the provider a concurrency token. A mismatch causes an optimistic-lock failure. Detection may occur at flush or commit, so handle the outcome around the transaction boundary, not only around `save` or `merge`. [Jakarta Persistence 3.2: entity versions](https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2#entity-versions-and-optimistic-locking)

### 31Verify the ORM's aggregate behavior

An ORM manages entities and relationships according to their mappings. A business aggregate may span several such entities. `@Version` on the root does not automatically prove that every change to a child's scalar fields participates in that root's version check.

Audit each mutation path. Where needed, request a root version increment with `LockModeType.OPTIMISTIC_FORCE_INCREMENT` within the transaction, and verify the generated behavior with a race test. The standard distinguishes owned relationships from unowned ones; it does not promise whole-graph consistency merely because one entity is versioned. [Jakarta Persistence 3.2: locking](https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2#locking-and-concurrency)

### 32Prefer a dedicated version to a timestamp

A numeric revision gives a clear comparison: 7, then 8, then 9. Timestamp tokens require care about precision, generation, and equality across writes. Hibernate documents timestamp locking as less reliable than dedicated version numbers. [Hibernate ORM 7.1: optimistic locking](https://docs.hibernate.org/orm/7.1/userguide/html_single/#locking-optimistic)

A numeric token still needs a policy: never reset or reuse revisions for an existing identity, and do not silently wrap on overflow. `Math.incrementExact` makes the example fail explicitly at the numeric limit.

## VII. Extend the idea across a user workflow

### 33Carry the revision across an edit

The server may finish a GET long before a person submits their edit. A fresh transaction at submission time cannot, by itself, identify the revision the person originally saw.

HTTPCopy

```
HTTP/1.1 200 OK
ETag: "order-123-v7"
Content-Type: application/json

{"id":"123","version":7,"status":"DRAFT"}
```

HTTPCopy

```
PUT /orders/123 HTTP/1.1
If-Match: "order-123-v7"
Content-Type: application/json

{"shippingAddress":"New address"}
```

`If-Match` uses strong entity-tag comparison. On a failed precondition, the usual response is **412 Precondition Failed**. A strong ETag derived from a version is valid only when it identifies the selected representation correctly; include representation variants or another validator scheme when needed. [RFC 9110: If-Match](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1)

### 34Do not require a client version mechanically

| Workflow | Where the relevant revision comes from |
| --- | --- |
| Short server command: load, add, save | Repository remembers the loaded revision |
| Human edits a previously displayed order | Client returns a validator or expected revision |
| Offline edit or detached form | Client revision is part of the conflict contract |

For a conditional edit, check the client's expectation and still use the repository's atomic version check. A separate precheck followed by a blind save creates another race. Do not automatically retry a stale client edit against a newer revision: that would discard the very condition the client supplied.

### 35Define the response policy

A version mismatch says something relevant changed. It does not explain whether two human intentions can safely merge. An address edit and a quantity change might be compatible, depending on the business rules.

For an application conflict without an HTTP precondition, **409 Conflict** can express that the request conflicts with current resource state. Explain the conflict and return enough current information for the caller to recover under the API's access rules. [RFC 9110: 409 Conflict](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.10)

Semantic merging requires renewed validation of the combined result. It cannot be implemented safely by ignoring a failed token check.

### 36Weigh coarse and fine-grained checks

| Strategy | Benefit | Cost |
| --- | --- | --- |
| One aggregate token | Simple dependency boundary; catches changes anywhere within it | Can reject compatible edits |
| Field or child tokens | More independent changes can proceed | Cross-field rules become harder to protect |

Begin with the boundary required by the invariant. Narrow it only when measured contention justifies a more complex proof. A “false conflict” may be a tolerable cost; a missed cross-child invariant is a correctness failure.

## VIII. Compare alternatives and expose the limits

### 37Compare optimistic and pessimistic concurrency

| Dimension | Optimistic root version | Pessimistic root lock |
| --- | --- | --- |
| Coordination point | Conditional save | Lock before reading decision state |
| Another writer | May do work and later conflict | Waits when it requests a conflicting lock |
| Main cost | Discarded work, retries, rejections | Waiting, lock duration, connection occupancy |
| Required discipline | Every relevant writer checks the token | Every relevant writer coordinates on the root |

To protect this aggregate pessimistically, lock its root first, then read its children and decide. Merely locking whatever child row happens to be updated still misses the shared invariant. PostgreSQL row locks block conflicting writers and lockers, not ordinary nonlocking reads; deadlocks remain possible. [PostgreSQL: explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html)

### 38Decide using contention and work cost

Suppose, hypothetically, 60% of attempts collide and each attempt is expensive. Repeatedly discarding that work may cost more than early serialization. A scarce resource with sustained competition may benefit from a shared lock or a queue.

Measure conflict rate, time spent before conflict, lock wait, retry count, latency, and exhausted attempts. Keep transactions short whichever strategy you choose. Do not hold a database transaction open while a human edits a form or while avoidable external work runs.

### 39Consider serializable isolation

PostgreSQL `SERIALIZABLE` ensures that committed transactions have effects consistent with some serial execution. It can abort transactions with serialization failures, so callers must be prepared to retry. [PostgreSQL: transaction modes](https://www.postgresql.org/docs/18/sql-set-transaction.html)

This is another way to protect an invariant when the full relevant read and write set participates correctly. It is not a promise that every attempted transaction succeeds. Do not substitute the name of an isolation level for testing the actual workload and its failure handling.

### 40Keep versions when they serve an application contract

Even with stronger isolation, a version can still express stale browser edits, offline edits, aggregate revision metadata, and explicit expected-state commands. A database transaction cannot cover the minutes a user spent looking at an earlier representation.

Choose mechanisms by responsibility. Database isolation governs overlapping transactions. A client revision can govern a longer decision interval. They may both be needed.

### 41Understand write skew

Two doctors are on call. The rule says at least one must remain on call. Each doctor has an independent version.

| Transaction A | Transaction B |
| --- | --- |
| Reads A = on and B = on | Reads A = on and B = on |
| Turns A off, checking A's version | Turns B off, checking B's version |
| Its own version check succeeds | Its own version check succeeds |

Under isolation that allows this interleaving, both can commit because they update different tokens. Nobody remains on call. The invariant spans more state than either token covers.

Possible designs include a shared roster aggregate/token, a shared coordination lock, or appropriately used serializable transactions. Reservations can make coordination explicit. Eventual consistency is an option only if the business accepts temporarily relaxing the rule; it cannot preserve a strict “always at least one” invariant.

### 42Revisit the aggregate boundary

Ask both questions: **What must remain consistent together? What state must participate in the same concurrency decision?** Their answers often point to the same aggregate boundary.

An aggregate is useful operationally because it aligns invariant scope, load/save scope, and coordination. This does not require every application transaction to contain exactly one aggregate, or all emitted messages to form a gapless stream. The boundary must fit the actual correctness requirement.

### 43Make temporal coupling visible

The two requests were already related through shared mutable state. Versioning makes that relationship explicit: both expect revision 7, and at most one competing transaction may successfully commit the transition from that revision under the protocol.

The pattern exposes an existing dependency. It does not make independent operations dependent by accident; an overly broad aggregate can, however, introduce avoidable contention and deserves examination when measurements show it matters.

### 44Centralize the concurrency mechanism

If add-line, change-quantity, and confirm handlers each implement their own SQL version checks, a change to the protocol touches every handler. Missing one path creates a bypass.

Centralize expected-version persistence in the repository or Unit of Work. Let application code choose retry policy and express any client precondition. Let domain behavior remain responsible for invariants. These distinct responsibilities keep the change surface small without hiding the policy.

## IX. Test the contract against the database

### 45Test a normal save and a stale writer

Start from version 7. Load and mutate, commit, and assert version 8 plus the expected children. Then load two copies at version 7 in separate transactions; commit one and attempt to save the other. Assert a conflict and verify that only the winning change is durable.

Use a real PostgreSQL instance with the intended isolation and schema. A mock can test that an exception is handled; it cannot establish the database's concurrency behavior.

### 46Test rollback of child writes

Inject a failure after the conditional root update and at least one child write. After rollback, use a separate connection to assert the original root version and original lines. This tests the actual ordering in the reference repository.

If another implementation writes children before checking the root, deliberately create a stale version, write a child, fail the check, and verify the child is absent after rollback. Testing only the thrown exception misses the atomicity requirement.

### 47Test the invariant after retry

Coordinate two attempts so both load 90 at v7 before either saves. Each adds 10. One commits; the other receives a conflict. Run the losing command in a fresh transaction and expect `OrderCapacityExceeded`.

Assert final total 100 and final version 8. If policy rejects without retry, the losing result is the original concurrency error. “Eventually a capacity error” is only expected when a fresh retry actually happens and no intervening operation changes capacity.

### 48Test outbox rollback

Inject a failure after inserting an outbox row but before commit. Assert neither the aggregate transition nor that event ID is durable. Also verify that a stale save never leaves an event behind.

The first test proves rollback after an actual insert; the second proves the stale path. With a root-first implementation, the stale path may never reach outbox insertion, so testing only that path would be incomplete.

### 49Test the event revision contract

After successful confirmation, assert that the outbox's `aggregate_version` equals the resulting committed root version. If a later transition emits another event, assert its corresponding revision.

Where required, separately test event indexes, deduplication by event ID, and out-of-order processing. Do not assert gapless versions for a subscription unless the publisher's contract guarantees them.

### 50Run genuinely overlapping transactions

A sequential stale-copy test is useful, but it does not exercise contention during simultaneous save attempts. Appendix B uses two threads, separate transactions, and a timed barrier after loading. That ensures both decisions begin from the same revision before the writes race.

The test expects one committed result, one optimistic conflict, total 100, version 8, and a capacity rejection on a fresh retry. It also gives the root updates a database lock timeout so a locking regression fails rather than hanging indefinitely. ORM implementations should repeat this test for every child-only mutation path.

## X. State the guarantee and connect the patterns

### 51Know when a version adds little value

| Situation | Why a token may be unnecessary or unsuitable |
| --- | --- |
| Immutable historical rows | No update race exists for that data |
| Independent append-only records | There may be no shared decision to invalidate |
| A correctly enforced database constraint or atomic SQL rule | The required invariant may already be protected |
| Very high contention | Early serialization or a different model may cost less |

“Append-only” is not sufficient by itself: our failing example appended independent lines while violating a shared sum. Look for the shared invariant before concluding that independent row inserts are independent business operations.

### 52Keep database constraints

Positive quantities, foreign keys, primary keys, and appropriate uniqueness rules are still valuable. If the business permits only one line per product, for example, add `UNIQUE (order_id, product_id)` and make the domain behavior match. The reference model permits repeated products as separate lines, so it does not add that constraint.

A PostgreSQL `CHECK` on one row is not a general way to enforce a sum across all child rows. PostgreSQL explicitly cautions against checks that depend on other rows. [PostgreSQL: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS)

The database protects the constraints declared in its schema. Domain behavior expresses richer business operations. The version protocol prevents stale decisions from committing through participating writers. None makes the other two redundant.

### 53Use an ownership map

| Layer | Responsibility in this example |
| --- | --- |
| Domain: `Order` | At most 100 units; positive additions; confirmed order cannot change; empty order cannot confirm |
| Application | Load, invoke behavior, request save; choose conflict policy; coordinate a transaction through a port |
| Persistence adapter | Reconstruct one revision; execute conditional root update; persist children; insert outbox |
| Database | Atomic statements, transaction commit/rollback, isolation, locks, declared constraints |
| Delivery / consumer | Publish committed outbox records; handle duplicate delivery and required ordering |

### 54Trace the complete use case

| Stage | Success path | Failure path |
| --- | --- | --- |
| Begin and load | Reconstruct order v7 and its lines | Missing order or load failure ends work |
| Domain operation | `addLine` validates and changes local state | Domain rejection; roll back |
| Conditional save | One root row updated to candidate v8 | Zero rows; throw conflict and roll back |
| Persist children and required outbox | All local writes succeed | Any failure rolls the unit back |
| Commit | Expose the committed result | Classify failure; reconcile an uncertain outcome |
| Optional conflict recovery | Start a fresh transaction and reconsider | Stop at retry bound or return a new domain rejection |

### 55State exactly what the pattern guarantees

**A stale aggregate decision cannot silently commit through this save protocol if every consistency-relevant mutation participates in the same token check and all dependent writes share the transaction.**

That guarantee assumes a coherent load, correct local rules, and tokens that are not reused. It does not prevent all concurrency, prove that every rejected edit is semantically incompatible, solve cross-token invariants, deliver messages exactly once, or resolve an uncertain commit outcome.

The proof for our example is simple: a valid revision is read; only one competing writer can commit its advancement; that writer's rules limit its new total to 100; stale dependent writes roll back. Each next successful command must validate against a revision it can still claim.

### 56Connect the patterns already learned

| Pattern | Its question | Connection to optimistic concurrency |
| --- | --- | --- |
| Aggregate | What must stay consistent together? | Defines the state covered by the token |
| Repository | How is that state loaded and persisted? | Applies expected-version persistence centrally |
| Unit of Work | What commits or rolls back together? | Makes a conflict undo root, child, and outbox writes |
| Transactional Outbox | How does a committed change create a durable outgoing message? | Event survives only with its successful transition |
| Inbox / idempotency | Has this message or command already been handled? | Handles duplicates, a different problem from competing writers |
| State | Which behavior is allowed in a logical state? | Domain behavior uses state; the token checks its revision |

### 57Re-derive it instead of memorizing an annotation

1. I read mutable business state.
2. I make a decision based on that revision.
3. Another writer may change the state that matters.
4. My earlier decision may no longer be valid.
5. My save must atomically verify the revision it depends on.
6. If verification fails, all dependent local writes must roll back.
7. Recovery means reloading and reconsidering, or explicitly rejecting the operation.

These steps derive the version, conditional update, conflict, rollback, and retry policy. `@Version` is one implementation mechanism, not the reasoning itself.

### 58Reach the next design pressure

An aggregate is a statement about correctness under transactions and concurrency. Its boundary should cover the state whose changes can invalidate its decisions.

Now extend the workflow across Order, Payment, Inventory, and Shipping, each with separately committed state. The local order token cannot atomically control all of those commits. Some steps may succeed before a later step fails, and their effects may need business compensation.

That is the next pressure from which **Saga and compensating transactions** emerge. Carry forward the same habit: identify the required guarantee, find the boundary that can actually enforce it, and make failure semantics explicit.

## Appendix A. Complete Java / JDBC reference

This is a small teaching implementation, not a production framework. All nested types are in one file so the example is copyable and self-contained. It implements loading, adding a line, confirmation, root-first saves, child replacement, atomic outbox insertion, and bounded optimistic retries. It updates existing orders; creation is represented by the SQL seed.

**Implementation contract:** use one fresh connection per transaction; do not let a mutable `Order`, repository, or session escape its transaction; save each order once; let failures propagate to the transaction owner. The outbox stores a minimal event envelope. A real integration event may need an immutable payload describing the committed transition; loading “whatever the order looks like later” is not an equivalent event snapshot. The relay is outside this example.

**Compatibility and validation:** source uses standard Java features and JDBC APIs supported by Java 25, with no preview features. The reference and race-test sources were compiled with the available Java 17 compiler; the domain smoke test passed. A Java 25 runtime and PostgreSQL server were not available for execution here, so the database race test is supplied for verification in your environment. The ORM mapping example is separate and requires its own dependencies.

**Print validation:** the HTML includes A4 print styles, wrapping code, repeated table headers, and page-break rules. ⚠ Browser print preview could not be verified in this environment; check the preview before exporting your final PDF.

#### Compile and run the domain-only smoke test on JDK 25

SHCopy

```
javac --release 25 OrderOccExample.java
java OrderOccExample
```

#### Run against PostgreSQL

Execute the schema below once in a disposable database. Obtain a PostgreSQL JDBC driver from the [official pgJDBC download page](https://jdbc.postgresql.org/download/) and add the JAR to the runtime classpath. Set `OCC_JDBC_URL`, `OCC_DB_USER`, and `OCC_DB_PASSWORD` to your database values. The URL has the form `jdbc:postgresql://localhost:5432/occ_example`. [pgJDBC: connecting](https://jdbc.postgresql.org/documentation/use/)

Then add 10 units to the seed order (Unix-style classpath separator shown; Windows uses `;`):

SHCopy

```
java -cp ".:postgresql.jar" OrderOccExample \
  00000000-0000-0000-0000-000000000123 \
  00000000-0000-0000-0000-00000000000b 10
```

Here `postgresql.jar` stands for your downloaded driver filename. The first successful run prints `Committed version: 8`. An unchanged second run rejects the additional 10 because the order is already full. This command has no idempotency key; rerunning a successful additive command is a new command.

#### schema.sql

Download schema.sql

SQLCopy

```
-- PostgreSQL 18. Run once in a disposable example database.
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    status VARCHAR(20) NOT NULL CHECK (status IN ('DRAFT', 'CONFIRMED')),
    version BIGINT NOT NULL DEFAULT 0 CHECK (version >= 0)
);

CREATE TABLE order_line (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id),
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);
CREATE INDEX order_line_order_id_idx ON order_line(order_id);

CREATE TABLE outbox_message (
    id UUID PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    aggregate_version BIGINT NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO orders (id, status, version)
VALUES ('00000000-0000-0000-0000-000000000123', 'DRAFT', 7);

INSERT INTO order_line (id, order_id, product_id, quantity)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000123',
    '00000000-0000-0000-0000-00000000000a', 90
);
```

#### OrderOccExample.java

Download OrderOccExample.java

JAVACopy

```
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

public final class OrderOccExample {
    private OrderOccExample() {}

    enum Status { DRAFT, CONFIRMED }

    record Line(UUID id, UUID productId, int quantity) {
        Line {
            Objects.requireNonNull(id);
            Objects.requireNonNull(productId);
            if (quantity <= 0) {
                throw new IllegalArgumentException("Quantity must be positive");
            }
        }
    }

    static final class OrderCapacityExceeded extends RuntimeException {
        OrderCapacityExceeded() { super("An order may contain at most 100 units"); }
    }

    static final class ConcurrentOrderModification extends RuntimeException {
        ConcurrentOrderModification(UUID id, long expectedVersion) {
            super("Order " + id + " no longer matches v" + expectedVersion);
        }
    }

    static final class PersistenceFailure extends RuntimeException {
        PersistenceFailure(Throwable cause) { super(cause); }
    }

    static final class Order {
        private final UUID id;
        private final long loadedVersion;
        private Status status;
        private final List<Line> lines;

        Order(UUID id, long loadedVersion, Status status, List<Line> lines) {
            this.id = Objects.requireNonNull(id);
            if (loadedVersion < 0) throw new IllegalArgumentException("Version");
            this.loadedVersion = loadedVersion;
            this.status = Objects.requireNonNull(status);
            this.lines = new ArrayList<>(List.copyOf(lines));
            if (this.lines.stream().mapToLong(Line::quantity).sum() > 100) {
                throw new OrderCapacityExceeded();
            }
            if (status == Status.CONFIRMED && this.lines.isEmpty()) {
                throw new IllegalArgumentException("Confirmed order is empty");
            }
        }

        UUID id() { return id; }
        long loadedVersion() { return loadedVersion; }
        Status status() { return status; }
        List<Line> lines() { return List.copyOf(lines); }
        int totalUnits() { return lines.stream().mapToInt(Line::quantity).sum(); }

        void addLine(UUID productId, int quantity) {
            requireDraft();
            Objects.requireNonNull(productId);
            if (quantity <= 0) throw new IllegalArgumentException("Quantity");
            if (quantity > 100 - totalUnits()) {
                throw new OrderCapacityExceeded();
            }
            lines.add(new Line(UUID.randomUUID(), productId, quantity));
        }

        void confirm() {
            requireDraft();
            if (lines.isEmpty()) throw new IllegalStateException("Empty order");
            status = Status.CONFIRMED;
        }

        private void requireDraft() {
            if (status != Status.DRAFT) {
                throw new IllegalStateException("Order is already confirmed");
            }
        }
    }

    interface OrderRepository {
        Order get(UUID id);
        long save(Order order); // New version is provisional until commit.
    }

    interface Outbox {
        void append(UUID eventId, UUID orderId, long version, String type);
    }

    record Session(OrderRepository orders, Outbox outbox) {}

    @FunctionalInterface
    interface Work<T> { T run(Session session); }

    interface Transactions {
        <T> T execute(Work<T> work);
    }

    @FunctionalInterface
    interface ConnectionFactory { Connection open() throws SQLException; }

    static final class JdbcTransactions implements Transactions {
        private final ConnectionFactory connections;

        JdbcTransactions(ConnectionFactory connections) {
            this.connections = Objects.requireNonNull(connections);
        }

        public <T> T execute(Work<T> work) {
            try (Connection c = connections.open()) {
                c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
                c.setAutoCommit(false);
                try {
                    var session = new Session(
                            new JdbcOrders(c), new JdbcOutbox(c));
                    T result = work.run(session);
                    c.commit();
                    return result;
                } catch (SQLException | RuntimeException | Error failure) {
                    try {
                        c.rollback();
                    } catch (SQLException rollbackFailure) {
                        failure.addSuppressed(rollbackFailure);
                        // Do not treat an uncertain rollback as retryable OCC.
                        throw new PersistenceFailure(failure);
                    }
                    throw failure;
                }
            } catch (SQLException failure) {
                throw new PersistenceFailure(failure);
            }
        }
    }

    static final class JdbcOrders implements OrderRepository {
        private final Connection c;
        private final Set<UUID> saved = new HashSet<>();

        JdbcOrders(Connection c) { this.c = c; }

        public Order get(UUID id) {
            // One statement gives the root and children one read snapshot.
            String sql = """
                SELECT o.status, o.version, l.id AS line_id,
                       l.product_id, l.quantity
                FROM orders o
                LEFT JOIN order_line l ON l.order_id = o.id
                WHERE o.id = ?
                ORDER BY l.id
                """;
            try (var p = c.prepareStatement(sql)) {
                p.setObject(1, id);
                try (var r = p.executeQuery()) {
                    if (!r.next()) {
                        throw new IllegalArgumentException("Order not found: " + id);
                    }
                    Status status = Status.valueOf(r.getString("status"));
                    long version = r.getLong("version");
                    var lines = new ArrayList<Line>();
                    do {
                        UUID lineId = r.getObject("line_id", UUID.class);
                        if (lineId != null) {
                            lines.add(new Line(lineId,
                                    r.getObject("product_id", UUID.class),
                                    r.getInt("quantity")));
                        }
                    } while (r.next());
                    return new Order(id, version, status, lines);
                }
            } catch (SQLException failure) {
                throw new PersistenceFailure(failure);
            }
        }

        public long save(Order order) {
            if (!saved.add(order.id())) {
                throw new IllegalStateException("Save once per order per transaction");
            }
            long next = Math.incrementExact(order.loadedVersion());
            String sql = """
                UPDATE orders SET status = ?, version = ?
                WHERE id = ? AND version = ?
                """;
            try (var p = c.prepareStatement(sql)) {
                p.setString(1, order.status().name());
                p.setLong(2, next);
                p.setObject(3, order.id());
                p.setLong(4, order.loadedVersion());
                if (p.executeUpdate() != 1) {
                    throw new ConcurrentOrderModification(
                            order.id(), order.loadedVersion());
                }
                replaceLines(order);
                return next;
            } catch (SQLException failure) {
                throw new PersistenceFailure(failure);
            }
        }

        private void replaceLines(Order order) throws SQLException {
            try (var p = c.prepareStatement(
                    "DELETE FROM order_line WHERE order_id = ?")) {
                p.setObject(1, order.id());
                p.executeUpdate();
            }
            String sql = """
                INSERT INTO order_line(id, order_id, product_id, quantity)
                VALUES (?, ?, ?, ?)
                """;
            try (var p = c.prepareStatement(sql)) {
                for (Line line : order.lines()) {
                    p.setObject(1, line.id());
                    p.setObject(2, order.id());
                    p.setObject(3, line.productId());
                    p.setInt(4, line.quantity());
                    p.addBatch();
                }
                p.executeBatch();
            }
        }
    }

    static final class JdbcOutbox implements Outbox {
        private final Connection c;
        JdbcOutbox(Connection c) { this.c = c; }

        public void append(UUID eventId, UUID orderId, long version, String type) {
            String sql = """
                INSERT INTO outbox_message
                    (id, aggregate_id, aggregate_version, event_type)
                VALUES (?, ?, ?, ?)
                """;
            try (var p = c.prepareStatement(sql)) {
                p.setObject(1, eventId);
                p.setObject(2, orderId);
                p.setLong(3, version);
                p.setString(4, type);
                p.executeUpdate();
            } catch (SQLException failure) {
                throw new PersistenceFailure(failure);
            }
        }
    }

    static long addLine(Transactions tx, UUID id, UUID productId, int quantity) {
        return tx.execute(s -> {
            Order order = s.orders().get(id);
            order.addLine(productId, quantity);
            return s.orders().save(order);
        });
    }

    static long confirm(Transactions tx, UUID id) {
        return tx.execute(s -> {
            Order order = s.orders().get(id);
            order.confirm();
            long next = s.orders().save(order);
            s.outbox().append(UUID.randomUUID(), id, next, "OrderConfirmed");
            return next;
        });
    }

    static <T> T retryConflict(int maxAttempts, Supplier<T> entireAttempt) {
        if (maxAttempts < 1) throw new IllegalArgumentException("maxAttempts");
        for (int attempt = 1; ; attempt++) {
            try {
                return entireAttempt.get();
            } catch (ConcurrentOrderModification conflict) {
                // A resource-close failure can be attached by try-with-resources.
                if (attempt == maxAttempts || conflict.getSuppressed().length != 0) {
                    throw conflict;
                }
            }
        }
    }

    static void domainSmokeTest() {
        var order = new Order(UUID.randomUUID(), 7, Status.DRAFT,
                List.of(new Line(UUID.randomUUID(), UUID.randomUUID(), 90)));
        order.addLine(UUID.randomUUID(), 10);
        if (order.totalUnits() != 100) throw new AssertionError("Expected 100");
        try {
            order.addLine(UUID.randomUUID(), 1);
            throw new AssertionError("Expected capacity rejection");
        } catch (OrderCapacityExceeded expected) {
            if (order.totalUnits() != 100) throw new AssertionError("Mutated");
        }
        order.confirm();
        if (order.status() != Status.CONFIRMED) throw new AssertionError("Status");
        System.out.println("Domain smoke test passed; no database was used.");
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            domainSmokeTest();
            return;
        }
        if (args.length != 3) {
            throw new IllegalArgumentException("Usage: order-id product-id quantity");
        }
        String url = Objects.requireNonNull(System.getenv("OCC_JDBC_URL"));
        String user = Objects.requireNonNull(System.getenv("OCC_DB_USER"));
        String password = Objects.requireNonNull(System.getenv("OCC_DB_PASSWORD"));
        Transactions tx = new JdbcTransactions(
                () -> DriverManager.getConnection(url, user, password));
        UUID id = UUID.fromString(args[0]);
        UUID productId = UUID.fromString(args[1]);
        int quantity = Integer.parseInt(args[2]);
        long committedVersion = retryConflict(3,
                () -> addLine(tx, id, productId, quantity));
        System.out.println("Committed version: " + committedVersion);
    }
}
```

## Appendix B. Real database race test

Run this against the freshly seeded 90-unit, v7 order, before the add-line command above. It changes that order. To repeat, use another fresh disposable database and rerun the schema. No destructive reset command is embedded.

SHCopy

```
javac --release 25 OrderOccExample.java OccRaceTest.java
java -cp ".:postgresql.jar" OccRaceTest
```

Use the same three database environment variables as Appendix A. This test proves a specific race outcome; it does not replace the rollback, outbox, ORM, and event-contract tests described in steps 45–50.

#### OccRaceTest.java

Download OccRaceTest.java

JAVACopy

```
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public final class OccRaceTest {
    private static final UUID ORDER = UUID.fromString(
            "00000000-0000-0000-0000-000000000123");
    record Outcome(UUID product, boolean committed) {}

    private static Connection open() throws SQLException {
        Connection c = DriverManager.getConnection(
                Objects.requireNonNull(System.getenv("OCC_JDBC_URL")),
                Objects.requireNonNull(System.getenv("OCC_DB_USER")),
                Objects.requireNonNull(System.getenv("OCC_DB_PASSWORD")));
        try (var p = c.createStatement()) {
            p.execute("SET lock_timeout = '5s'");
            p.execute("SET statement_timeout = '10s'");
            return c;
        } catch (SQLException failure) {
            try { c.close(); }
            catch (SQLException closing) { failure.addSuppressed(closing); }
            throw failure;
        }
    }

    private static Outcome attempt(
            OrderOccExample.Transactions tx,
            CyclicBarrier bothLoaded, UUID product) {
        try {
            long version = tx.execute(s -> {
                var order = s.orders().get(ORDER);
                check(order.loadedVersion() == 7, "Use a fresh v7 seed");
                check(order.totalUnits() == 90, "Use a fresh 90-unit seed");
                order.addLine(product, 10);
                try {
                    bothLoaded.await(5, TimeUnit.SECONDS);
                } catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException(interrupted);
                } catch (Exception failure) {
                    throw new IllegalStateException("Load barrier failed", failure);
                }
                return s.orders().save(order);
            });
            check(version == 8, "Winner must commit v8");
            return new Outcome(product, true);
        } catch (OrderOccExample.ConcurrentOrderModification expected) {
            check(expected.getSuppressed().length == 0, "Resource cleanup failed");
            return new Outcome(product, false);
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    public static void main(String[] args) throws Exception {
        var tx = new OrderOccExample.JdbcTransactions(OccRaceTest::open);
        var gate = new CyclicBarrier(2);
        var workers = Executors.newFixedThreadPool(2);
        try {
            var a = workers.submit(() -> attempt(tx, gate, UUID.randomUUID()));
            var b = workers.submit(() -> attempt(tx, gate, UUID.randomUUID()));
            Outcome first = a.get(20, TimeUnit.SECONDS);
            Outcome second = b.get(20, TimeUnit.SECONDS);
            check(first.committed() != second.committed(), "Need one winner");
            Outcome loser = first.committed() ? second : first;
            try {
                OrderOccExample.addLine(tx, ORDER, loser.product(), 10);
                throw new AssertionError("Fresh retry must exceed capacity");
            } catch (OrderOccExample.OrderCapacityExceeded expected) {
                // New state is full; the business rule rejects the intent.
            }
            tx.execute(s -> {
                var current = s.orders().get(ORDER);
                check(current.totalUnits() == 100, "Invariant violated");
                check(current.loadedVersion() == 8, "Unexpected revision");
                check(current.lines().stream()
                        .noneMatch(line -> line.productId().equals(loser.product())),
                        "Losing line persisted");
                return null;
            });
            System.out.println("Race passed: one commit, one conflict, total 100.");
        } finally {
            workers.shutdownNow();
        }
    }
}
```

## Official sources and scope

Technical behavior was checked against the following official documentation on 2 September 2026. The order, doctors, API payloads, and code are teaching examples derived from the supplied lesson. Recommendations about boundaries and recovery follow from those examples and the stated guarantees; they are design reasoning, not product SLAs.

| Source | Behavior checked |
| --- | --- |
| [PostgreSQL 18 — transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html) | Statement snapshots, concurrent updates, stronger isolation |
| [PostgreSQL 18 — explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html) | Row locks, waiting, deadlocks |
| [PostgreSQL 18 — serialization failure handling](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html) | SQLSTATE 40001 and complete retries |
| [PostgreSQL 18 — constraints](https://www.postgresql.org/docs/18/ddl-constraints.html) | Check constraints and cross-row limitations |
| [Java 25 — Connection](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html) | Explicit transactions, commit, rollback, close |
| [Java 25 — Statement](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Statement.html) | Update counts |
| [Jakarta Persistence 3.2 specification](https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2) | Version checks, entity scope, optimistic lock modes |
| [Hibernate ORM 7.1 user guide](https://docs.hibernate.org/orm/7.1/userguide/html_single/#locking-optimistic) | Version and timestamp locking |
| [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) | ETag / If-Match, 412 and 409 |
| [AWS — transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Atomic state/message writes, duplicate delivery |
| [pgJDBC — using the driver](https://jdbc.postgresql.org/documentation/use/) | Driver loading and connection URL |

End of lesson 21 · Next design pressure: Saga and compensating transactions