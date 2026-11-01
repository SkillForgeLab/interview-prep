[Skip to guide](#guide)

**DP** Architecture notes

Lesson 20 · Contents

I · Discover the consistency boundary[01   Start with the simplest model](#s01)[02   The first requirement exposes a hole](#s02)[03   Duplicated checks reveal weak ownership](#s03)[04   Give the order ownership of the decision](#s04)[05   A second rule makes the boundary clearer](#s05)[06   Name the boundary we have discovered](#s06)[07   Why the aggregate needs a root](#s07)[08   Make bypass difficult in Java](#s08)II · Persist the boundary[09   Let the write repository follow the root](#s09)[10   The database representation can use several tables](#s10)[11   Make the transaction boundary explicit](#s11)[12   Recognize an aggregate that is too large](#s12)[13   Test membership using the rule, not the relationship](#s13)[14   Reference other aggregates by identity](#s14)III · Size the aggregate around business semantics[15   A cross-aggregate requirement changes the problem](#s15)[16   Choose an enforcement model with explicit semantics](#s16)[17   Keep the boundary small enough to remain useful](#s17)IV · Make the implementation concrete[18   Turn the discovered rules into an intentional API](#s18)[19   Keep application orchestration explicit and small](#s19)V · Connect commits, events, and concurrent writers[20   Connect the aggregate to Transactional Outbox](#s20)[21   Use versions without overclaiming ordering](#s21)[22   Expose the bug: two correct copies can conflict](#s22)[23   Separate the failure contracts](#s23)VI · Verify each correctness boundary[24   Test the aggregate’s business contract](#s24)[25   Test the repository against a real database](#s25)[26   Test the outbox at the crash points](#s26)VII · Keep the model proportionate[27   Distinguish aggregates from nearby concepts](#s27)[28   Do not force rich modeling onto simple CRUD](#s28)[29   Connect the patterns by responsibility](#s29)[30   Put the whole operation in one picture](#s30)VIII · Carry the model forward[31   Keep the reasoning sequence](#s31)[A · Runnable Java example](#appendix-a)[B · Sources & scope](#sources)

Read from the problem forward.
All lesson content is available offline.

20 · Domain modeling · First principles

# Aggregate /Aggregate Root

We’ll derive this from one question:

> Which objects must remain consistent together when a business operation commits?

Follow one order model as business rules expose its weak points. The consistency boundary emerges first; the pattern name follows.

Java 25-compatibleNo preview featuresStandalone HTMLPrint-ready layout

Print / Save PDFDownload Java example[Start the lesson](#s01)[Jump to runnable code](#appendix-a)

For PDF: choose A4 or Letter, use 100% scale, and turn off browser headers/footers. The page supplies its own margins. A4 is the authored page size.

All lesson content is visible without JavaScript. Use your browser’s Print command; copy the complete Java listing from Appendix A.

**01 · Find the invariant**

Start with lifecycle and quantity rules.

**02 · Give it an owner**

Close child mutation and persistence bypasses.

**03 · Protect the commit**

Connect atomic writes, events, and concurrency.

## Reading route

1. Discover the boundary · 1–8
2. Persist the boundary · 9–14
3. Size the model · 15–17
4. Implement the behavior · 18–19
5. Events and concurrency · 20–23
6. Verify correctness · 24–26
7. Keep the model proportionate · 27–30
8. Reasoning checklist · 31
9. Runnable Java · Appendix A
10. Official sources · Appendix B

I · Discover the consistency boundary

## 01Start with the simplest model

An order has a lifecycle. Its lines identify products and quantities. At first, giving both objects independent mutation methods and repositories seems natural.

Java · deliberately incomplete starting design

```
// Initial design: independently writable objects.
final class Order {
    private OrderStatus status = OrderStatus.DRAFT;
    public void confirm() { status = OrderStatus.CONFIRMED; }
}

final class OrderLine {
    private int quantity;
    public void changeQuantity(int value) { quantity = value; }
}
```

The application can load an `Order` through `OrderRepository` and an `OrderLine` through `OrderLineRepository`. Nothing in this design makes their rules agree.

**Begin with behavior**

We have not chosen an aggregate yet. First, introduce a business rule and observe where the current design breaks.

## 02The first requirement exposes a hole

> Once an order is confirmed, its lines must not change.

Java · teaching excerpt

```
OrderLine line = lines.findById(lineId).orElseThrow();
line.changeQuantity(20);
lines.save(line);
```

That path never checks the order’s status. It can modify a line belonging to a confirmed order. A handler-level check looks like a repair:

Java · teaching excerpt

```
Order order = orders.findById(orderId).orElseThrow();
if (order.status() != OrderStatus.DRAFT) {
    throw new IllegalStateException("Confirmed orders cannot change");
}
OrderLine line = lines.findById(lineId).orElseThrow();
// This design must also verify that the line belongs to this order.
line.changeQuantity(newQuantity);
lines.save(line);
```

This protects one code path under a single-writer assumption. It leaves two questions unanswered: will every caller remember the rule, and can another transaction confirm the order between the check and the write?

## 03Duplicated checks reveal weak ownership

Adding, removing, repricing, discounting, and changing quantities may all affect an order’s contents. If each handler must repeat the lifecycle check, one business rule has many enforcement points.

| Pressure | What it reveals |
| --- | --- |
| A new handler forgets the check | Correctness depends on every caller remembering domain knowledge. |
| The lifecycle rule changes | Several use cases must change together. |
| Different handlers interpret the rule differently | There is no single owner of the invariant. |

The rule joins **order lifecycle** and **order contents**. Put its enforcement where those concepts can be considered together.

## 04Give the order ownership of the decision

Java · teaching excerpt

```
public void changeQuantity(OrderLineId lineId, int quantity) {
    ensureDraft();
    ensurePositive(quantity);
    OrderLine line = findLine(lineId);
    line.quantity = quantity;
}
```

The application now asks the order to perform an operation. It no longer reconstructs the lifecycle rule. Looking up the line inside this order also checks membership: a line from a different order is not a valid target.

| Application handler | Order |
| --- | --- |
| Load the model, invoke an operation, arrange persistence | Decide whether the operation is valid and make the state change. |

**A local improvement**

This centralizes behavior in one object instance. We will close public bypasses and address concurrent copies separately.

## 05A second rule makes the boundary clearer

> An order may contain at most 100 total units.

| Line A | Line B | Total | Decision |
| --- | --- | --- | --- |
| 40 | 50 | 90 | Valid current state |
| 40 | 70 | 110 | Reject the proposed change |
| 40 | 60 | 100 | Accept the proposed change |

A line cannot enforce this rule by examining only its own quantity. The decision needs the quantities of the other lines in the order.

Java · teaching excerpt

```
public void changeQuantity(OrderLineId lineId, int quantity) {
    ensureDraft();
    ensurePositive(quantity);
    OrderLine line = findLine(lineId);
    int otherUnits = totalQuantity() - line.quantity;

    if (quantity > MAX_UNITS - otherUnits) {
        throw new RuleViolation("Order cannot exceed 100 units");
    }
    line.quantity = quantity;
}
```

**Validate before mutating**

The rejected operation leaves the existing state intact. Comparing against remaining capacity also avoids overflow from adding an arbitrary positive `int` to the current total. The existing aggregate is assumed valid.

## 06Name the boundary we have discovered

For add, remove, change, and confirm operations, the order and its relevant lines must satisfy the order rules together when the operation commits. This is the cluster we call an **aggregate**.

Order aggregate · one consistency boundary

**Order**Status, line membership, total-unit rule

Line A · 40 unitsLine B · 50 units

Every accepted operation preserves the rules for this whole boundary.

Microsoft’s aggregate guidance starts from the domain concepts that must be transactionally consistent together. This example applies that principle to the lifecycle and quantity rules. [[1]](#ref-1)

**The name follows the need**

We grouped these objects because of the rules they must preserve together. Being related is insufficient by itself.

## 07Why the aggregate needs a root

The order’s validation is ineffective if callers still have an independent child write path.

| Entry point | Consequence |
| --- | --- |
| `order.changeQuantity(lineId, 70)` | The owner evaluates lifecycle, membership, and total quantity. |
| `line.changeQuantity(500)` followed by child save | The caller can bypass the owner. |

Choose one entity as the controlled entry point for changes: **Order is the aggregate root**. Its public methods expose business operations. It coordinates any internal entities and value objects needed to preserve the rules.

The root can delegate calculations and local rules to its children. It still owns the consistency contract for changes across the boundary. [[1]](#ref-1)

## 08Make bypass difficult in Java

Package-private child mutation restricts access to a package; it does not restrict access to the root alone. For this small model, a private nested child and immutable read snapshots make the boundary more explicit.

Java · teaching excerpt

```
private static final class OrderLine {
    private final OrderLineId id;
    private final ProductId productId;
    private int quantity;
    // Constructor is private; only aggregate internals use this type.
}

public List<LineSnapshot> lines() {
    List<LineSnapshot> snapshots = new ArrayList<>();
    for (OrderLine line : lines.values()) {
        snapshots.add(new LineSnapshot(
                line.id, line.productId, line.quantity));
    }
    return List.copyOf(snapshots);
}
```

The complete implementation is in Appendix A. Its snapshot records contain immutable identifiers and an `int`, so callers cannot change the order through a returned object.

**An unmodifiable list is not a deep freeze**

`List.copyOf(mutableChildren)` blocks list edits but would still expose mutable element references. Records also do not recursively freeze their components. The snapshot’s component types matter. [[3]](#ref-3) [[4]](#ref-4)

This is API encapsulation, not a security boundary against reflection, privileged persistence code, or arbitrary database writes. Those paths also need disciplined ownership.

II · Persist the boundary

## 09Let the write repository follow the root

Java · teaching excerpt

```
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    void save(Order order);
}
```

Use one write repository for the `Order` aggregate instead of independently saving its children through application-facing repositories. The adapter may still have internal helpers that map individual tables.

Queries have a different job. A report may read or join line rows directly and return DTOs without reconstructing a writable aggregate. Microsoft makes this command/query distinction explicit. [[2]](#ref-2)

**A useful convention, not a required framework**

A custom repository interface is optional. An existing persistence abstraction can serve the same role. The necessary property is controlled writes that preserve the aggregate’s rules. [[2]](#ref-2)

## 10The database representation can use several tables

SQL · PostgreSQL-oriented teaching schema

```
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('DRAFT', 'CONFIRMED')),
    version BIGINT NOT NULL DEFAULT 0 CHECK (version >= 0)
);

CREATE TABLE order_line (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id),
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);
```

A repository can reconstruct one order from these rows and save changes across both tables. The aggregate boundary need not match the table boundary.

The row constraints protect basic persisted shape. They do not, by themselves, enforce the sum of all lines or the rule that confirmed contents cannot change. Those rules need a coordinated write protocol.

**Restoring state is different from executing a command**

A real adapter needs a deliberate rehydration path that restores identifiers, status, children, and version without re-emitting historical events. It should reject malformed state or use a documented trusted mapping path. Calling `confirm()` merely to rebuild a confirmed order would generate a new event.

## 11Make the transaction boundary explicit

The application’s transaction scope must include every required aggregate write. A repository method named `save` does not prove that several statements commit atomically.

1. Begin one database transaction.
2. Load a coherent order state and the version it represents.
3. Invoke the domain operation.
4. Persist the root and child changes using the concurrency protocol.
5. Commit everything together, or roll everything back.

With JDBC, new connections normally use auto-commit. Disable it for the unit of work, run the participating statements on the same transaction-bound connection, and explicitly commit or roll back. [[5]](#ref-5)

**Atomicity and isolation solve different problems**

Atomicity prevents a partial commit. Isolation and concurrency control determine how competing operations interact. Simply adding `BEGIN` and `COMMIT` does not make two stale copies safe.

Loading also deserves attention. Under PostgreSQL Read Committed, successive queries can see different committed states. A root query followed by a child query is not automatically one coherent snapshot. Choose an appropriate single-query load, snapshot strategy, or root-lock protocol, then validate the write version. [[6]](#ref-6)

## 12Recognize an aggregate that is too large

Suppose one customer object owns every order, every line, every product, and every supplier. That is a large relationship graph, but we have not established a rule requiring all of it to change atomically.

| Possible cost | Why it appears |
| --- | --- |
| Broad conflicts | Unrelated operations may compete on the same root version or lock. |
| Expensive reads and validation | Operations may require large amounts of state. |
| Longer transactions | More coordinated work extends the time resources are held. |
| Unclear ownership | Catalog, supplier, customer, and order lifecycles become coupled. |

An aggregate does not force an ORM to eagerly load every related row. The real problem is the oversized consistency and concurrency boundary. Lazy loading alone cannot fix that modeling decision.

## 13Test membership using the rule, not the relationship

| Relationship or rule | Boundary reasoning |
| --- | --- |
| Order total units must stay at or below 100 | The relevant line quantities need coordinated enforcement with the order. |
| Order belongs to a customer | An identity reference alone does not require one aggregate. |
| Order line identifies a product | That alone does not bring the live product catalog into the order aggregate. |
| The delivery address is fixed when ordered | An address value copied into the order may belong to the order’s historical state. |

For each candidate object, ask what would become invalid if it changed independently. If you cannot name the invariant, containment may be expressing navigation convenience rather than consistency.

## 14Reference other aggregates by identity

Java · teaching excerpt

```
private final OrderId id;
private final CustomerId customerId;

// A line stores ProductId, not a writable Product aggregate.
public record ProductId(UUID value) {
    public ProductId { Objects.requireNonNull(value); }
}
```

Identity references keep cross-boundary interaction deliberate. They do not prohibit database joins, foreign keys where appropriate, or loading another aggregate in a use case. They prevent a convenient object traversal from silently becoming a broad mutation path. [[1]](#ref-1)

**A reference is not a guarantee**

Storing `CustomerId` does not prove the customer currently exists, remains eligible, or has sufficient credit. Those requirements need their own policy and enforcement mechanism.

III · Size the aggregate around business semantics

## 15A cross-aggregate requirement changes the problem

> A customer’s outstanding order value must never exceed the customer’s credit limit.

First define the terms with the business: which order states consume credit, whether pending reservations count, when a cancellation releases credit, and what reducing a limit is allowed to do. The rule is not implementable until those semantics are clear.

Now imagine two orders both checking the same “available credit” and then committing independently. Each can pass while their combined commitment exceeds the limit. Moving the check into a domain method does not remove this race.

**Do not infer a giant aggregate**

Strict enforcement needs one coordinated authority over the constrained resource. It does not automatically need every historical order object inside a customer aggregate.

## 16Choose an enforcement model with explicit semantics

| Approach | What has to be true |
| --- | --- |
| Small credit/reservation authority | A credit account atomically reserves an amount against its remaining capacity. An order becomes credit-approved only with a valid reservation. |
| One local transaction across separate roots | If the data is colocated, a deliberate transaction and locking/conditional-write protocol may coordinate the updates. This adds coupling without requiring one giant object graph. |
| Pending order plus asynchronous approval | Pending must mean “not yet credit-approved.” A later workflow approves, rejects, or cancels it. If all accepted orders already count as committed credit, this relaxes the original rule. |

The reservation model still needs lifecycle rules: a stable reservation identity, harmless duplicate requests, confirmation, release, expiry, and reconciliation. An approved order must not silently lose its credit backing when an unrelated timer expires.

**Separate physical atomicity from the business promise**

Across independent databases, a workflow cannot turn separate commits into an ordinary local rollback. Reservations and intermediate states can preserve a carefully defined business rule; they are not permission to claim atomicity that does not exist.

## 17Keep the boundary small enough to remain useful

| Larger boundary | Smaller boundaries |
| --- | --- |
| More rules can be coordinated inside one owner | More independent operations can proceed concurrently |
| Potentially larger loads and write sets | Potentially smaller loads and write sets |
| More operations may share a conflict point | Cross-boundary rules need explicit coordination or allowed delay |

These are design pressures, not universal performance measurements. Real cost depends on access patterns and storage design. Choose the **smallest useful boundary that can enforce the immediate invariants**.

“One aggregate per transaction” is a useful default in many DDD designs. It is not a physical database limit, and an aggregate is not a universal maximum on how much state a transaction may touch.

IV · Make the implementation concrete

## 18Turn the discovered rules into an intentional API

| Operation | Checks before mutation |
| --- | --- |
| `addLine(product, quantity)` | Draft; non-null product; positive quantity; remaining capacity |
| `changeQuantity(line, quantity)` | Draft; positive quantity; line belongs to this order; total capacity |
| `removeLine(line)` | Draft; line belongs to this order |
| `confirm()` | Draft; at least one line |

Java · teaching excerpt

```
public void confirm() {
    ensureDraft();
    if (lines.isEmpty()) {
        throw new RuleViolation("An empty order cannot be confirmed");
    }
    OrderConfirmed event = new OrderConfirmed(UUID.randomUUID(), id);
    status = OrderStatus.CONFIRMED;
    pendingEvents.add(event);
}
```

The sample’s confirmed state freezes line membership and quantities. Product metadata outside the aggregate may still evolve. Its event is pending in memory until the application persists it with the state change.

**Keep expected rejection side-effect-free**

For ordinary invalid input or violated rules, check first and leave state unchanged. If persistence later fails, discard the mutated instance and reload for a fresh attempt. A database rollback does not reverse Java field assignments.

## 19Keep application orchestration explicit and small

Java · application sketch; ports supplied by the application

```
public void handle(ChangeOrderQuantity command) {
    transactions.inTransaction(() -> {
        Order order = orders.findById(command.orderId()).orElseThrow();
        order.changeQuantity(command.lineId(), command.quantity());
        orders.save(order);
    });
}
```

Here `transactions` and `orders` must share the same transaction context. The wrapper owns commit and rollback. The repository participates; it must not commit each table independently.

| Responsibility | Owner |
| --- | --- |
| Authentication, authorization, command mapping, transaction scope | Application/infrastructure boundary |
| Order lifecycle, line membership, quantity rules | Aggregate |
| Row mapping, coherent reconstruction, version check, SQL writes | Persistence adapter |
| Conflict response and safe retry policy | Application policy |

The domain operation receives already identified business inputs. Keeping database and broker APIs out of it makes the rule easy to exercise directly.

V · Connect commits, events, and concurrent writers

## 20Connect the aggregate to Transactional Outbox

Confirming an order can record `OrderConfirmed`. A domain event describes the accepted domain transition in this attempt. The application may map it to a versioned integration-event contract before persistence.

One producer database transaction

**Order writes**

Status, children if changed, and root version

**Outbox insert**

Event identity, aggregate identity, payload, sequencing metadata

Both commit, or neither commits.

1. Load and validate the aggregate operation.
2. Claim the expected root version and write its state.
3. Map the pending event and insert the outbox row on the same transaction.
4. Commit, then discard the command-attempt instance.
5. A separate relay publishes committed outbox rows and retries failures.

The relay may publish duplicates. A consumer needs an idempotent business effect, commonly with a processed-event record stored atomically with that effect. The outbox makes publication intent durable; it does not make a database commit and broker publish globally atomic. [[7]](#ref-7)

**Do not publish from the aggregate**

No broker call belongs inside `confirm()`. If the transaction rolls back, discard its pending events. Do not clear them before the durable write succeeds or reuse a rolled-back instance as though it represented committed state.

## 21Use versions without overclaiming ordering

Java · integration envelope shape

```
public record EventEnvelope(
        UUID eventId,
        OrderId orderId,
        long aggregateVersion,
        int eventIndex,
        String eventType,
        String payload
) {}
```

If persistence advances an order from version 6 to version 7, it can stamp the event with committed revision 7. Assign that revision within the successful save protocol. An increment on an arbitrary in-memory copy is not enough.

| Field | Purpose |
| --- | --- |
| `eventId` | Identity for deduplicating redelivery of this logical event |
| `orderId` | Aggregate identity and a possible ordering/partition scope |
| `aggregateVersion` | Revision of aggregate state associated with the event |
| `eventIndex` | Distinguishes several events produced by the same revision |

**Sequence metadata does not enforce delivery order**

A revision can produce zero, one, or several events. Therefore revision gaps need not mean lost events. If every event needs a contiguous sequence, define a separate per-aggregate event sequence. Relay scheduling, broker routing, and consumer behavior must honor whichever ordering contract is required.

A consumer also needs to decide what out-of-order delivery means. Ignoring an older full-state projection may be valid; dropping an older increment event can lose a required effect.

## 22Expose the bug: two correct copies can conflict

An order contains 90 units at version 7. Two transactions each try to add 10.

| Step | Transaction A | Transaction B |
| --- | --- | --- |
| 1 | Reads 90 units, version 7 | Reads 90 units, version 7 |
| 2 | Validates 90 + 10 = 100 | Validates 90 + 10 = 100 |
| 3 | Saves its accepted change | Attempts to save its stale copy |

With independent child inserts, both new lines might survive and yield 110. With overwrite-style persistence, one accepted update might be lost. The exact symptom depends on the adapter; the missing protection is the same.

SQL · optimistic version claim for an existing aggregate

```
UPDATE orders
SET status = ?, version = version + 1
WHERE id = ? AND version = ?;
```

Bind the expected version read with the aggregate. Require exactly one affected row. If zero rows match, treat it as a conflict or disappearance and abort the whole attempt. Only the winner may persist its child changes and outbox rows in that transaction.

**Every mutation participates**

A change to only a child must still claim/increment the root version. If one write path skips that step, the aggregate-wide concurrency guarantee breaks. At some isolation levels the database may instead raise a serialization error; that also aborts the attempt.

After A commits version 8 with 100 units, B can reload and re-run its command. The fresh domain decision now rejects another 10 units. Retry means **reload and re-evaluate**, not blindly save the previously mutated object. [[6]](#ref-6)

## 23Separate the failure contracts

| Failure | Meaning | Response |
| --- | --- | --- |
| Domain rejection | The requested operation violates the current business rule. | Return a useful rejection. Retrying unchanged input against unchanged state cannot help. |
| Optimistic conflict / serialization failure | The attempt did not have an acceptable concurrency outcome. | Abort. Reload and re-evaluate if retry is allowed, or return a conflict. |
| Known rollback after a transient database error | This attempt did not commit. | Retry the full transaction only under a bounded, appropriate policy. |
| Connection lost during commit acknowledgement | The client may not know whether the database committed. | Reconcile by durable command identity or another reliable status check before blindly repeating effects. |

Outbox event deduplication and command idempotency are separate. A regenerated event ID on a repeated command does not prevent a duplicate business operation after an uncertain commit.

**No blanket retry**

`catch (Exception e) { retry(); }` erases the distinctions the application needs to make. A fresh attempt should also have a fresh aggregate instance.

VI · Verify each correctness boundary

## 24Test the aggregate’s business contract

Start with direct domain checks, without a database. Appendix A includes executable checks using only the Java standard library; it does not depend on a test framework.

| Scenario | Expected result |
| --- | --- |
| Confirm an empty order | Reject; remain draft; no event |
| 40 + 50, then change 50 to 70 | Reject; original lines unchanged |
| 40 + 50, then change 50 to 60 | Accept exactly 100 units |
| Zero, negative, or overflow-sized quantity | Reject without mutation |
| Change or remove a foreign line identity | Reject without mutation |
| Change the returned list or an old snapshot | List edits rejected; snapshot unaffected by later root changes |
| Mutate or confirm again after confirmation | Reject; no second confirmation event |

Java · excerpt from the runnable checks

```
List<LineSnapshot> before = order.lines();
expect(RuleViolation.class, () -> order.changeQuantity(b, 70));
check(order.lines().equals(before), "Rejected change mutated lines");
```

These checks target observable behavior and invariant preservation. They do not prove database isolation or transactional persistence.

## 25Test the repository against a real database

| Integration test | Evidence to collect |
| --- | --- |
| Save and reload | Same identifiers, status, children, quantities, and version; no replay-generated pending events |
| Failure partway through child persistence | Root and all child rows remain at their previously committed state |
| Two connections edit the same version | At most one attempt commits; the other conflicts or aborts; total remains valid |
| One confirms while another changes a line | A stale line writer cannot commit after confirmation |
| Coherent reconstruction under concurrent writes | The loader never accepts a mixed root/child state as a valid revision |

Use the actual chosen isolation level and force the concurrency interleaving with barriers or latches. Mocks and an in-memory map cannot establish these database guarantees.

## 26Test the outbox at the crash points

| Injected failure point | Required persisted outcome |
| --- | --- |
| Before producer commit | Neither confirmation nor its outbox event commits |
| Outbox insert fails | Aggregate writes roll back with it |
| After producer commit, before relay publish | Confirmed order and pending outbox row remain durable |
| After publish, before relay marks sent | Redelivery is possible; consumer’s duplicate effect remains harmless |
| After consumer effect, before acknowledgement | Redelivery does not repeat the committed business effect when deduplication and effect share a transaction |

For the producer, inspect both the order state and the outbox row. For the consumer, inspect both its processed-event record and its actual business effect. This validates the boundary each component really owns.

VII · Keep the model proportionate

## 27Distinguish aggregates from nearby concepts

| Concept | Why it does not define the aggregate |
| --- | --- |
| A collection | A `List<OrderLine>` has no business consistency policy by itself. |
| A foreign key | Referential integrity can connect data on either side of an aggregate boundary. |
| ORM navigation | A traversable graph says what can be reached, not what must change atomically. |
| A table | One aggregate may span multiple tables. |
| A service or bounded context | A domain model may contain several aggregate boundaries. [[1]](#ref-1) |
| An entity with children | Containment alone does not establish an invariant or write protocol. |

An aggregate may also contain only its root entity. Multiple child objects are not a requirement.

## 28Do not force rich modeling onto simple CRUD

Java · simple reference-data shape

```
public record Country(String isoCode, String displayName) {}
```

If the application merely maintains reference data, a simple model and straightforward validation may be sufficient. Rich aggregate behavior earns its place when state transitions or cross-object rules create a real ownership problem. [[1]](#ref-1)

The record above is only a data shape. Add whatever input validation and persistence constraints that specific reference-data feature requires; there is no benefit in inventing a hierarchy of domain services and factories without a need.

## 29Connect the patterns by responsibility

| Pattern / concept | Question it answers |
| --- | --- |
| Aggregate / root | Which rules must hold together, and who owns changes? |
| Repository | How does the application retrieve and persist the writable domain boundary? |
| Unit of Work / transaction | Which persistence operations commit or roll back together? |
| Dependency Inversion / Ports & Adapters | How can domain and application policy stay independent of database and broker details? |
| Command | What operation is being requested? A request may be rejected. |
| Domain event | What domain transition was accepted in this attempt? It becomes durable only with persistence. |
| Transactional Outbox | How is publication intent committed atomically with the producer’s state? |
| Optimistic concurrency | How can a stale aggregate writer be detected before it commits? |

The aggregate can say what happened in business terms without knowing how JDBC stores it or how a broker distributes it.

## 30Put the whole operation in one picture

**Command → Application handler**Authenticate / authorize · begin transaction · load coherent state

**Order aggregate**

Order root evaluates lifecycle, membership, and capacity.
Internal lines change only through that API.

Persistence · one database transaction

**Repository adapter**

Claim expected root version
Write root and child rows

**Outbox adapter**

Map pending domain events
Insert durable publication intent

Commit all participating writes, or abort all of them.

**After commit: relay → broker → consumer**Retry delivery · handle duplicates · enforce required ordering scope

The diagram separates domain enforcement, atomic persistence, and eventual delivery. A correct design needs all three contracts to agree.

VIII · Carry the model forward

## 31Keep the reasoning sequence

1. **What invariant must hold?**State it in business language, including when it applies.
2. **Which state is needed to enforce it?**Include membership, lifecycle, and cross-object calculations.
3. **What must commit atomically?**Separate immediate consistency from explicitly allowed intermediate states.
4. **Who owns enforcement?**Expose meaningful operations through one root.
5. **Can callers bypass that owner?**Inspect public APIs, returned references, repositories, and direct writes.
6. **How small can the boundary be?**Challenge relationship-based grouping and unnecessary contention.
7. **What if two copies change concurrently?**Require a coherent load and an explicit persistence concurrency protocol.

**The derived model**

For this lesson’s rules: **Order is the root; Order plus its internal lines is the aggregate.** The root protects each in-memory operation. The persistence protocol protects competing commits.

Next · 21

### Optimistic Concurrency Control

What should happen when another transaction changes the order after we read it?

Appendix A · Complete source

## Run the domain model

Save the complete listing as `AggregateGuideDemo.java`, or use the download button at the top. The numbered parts below concatenate into one source file. No external dependencies or preview flags are required.

Shell · with a JDK 25 installation

```
javac --release 25 AggregateGuideDemo.java
java AggregateGuideDemo
```

Expected output: `All aggregate checks passed.`

**Validation and scope**

The exact listing was compiled and its checks passed on the available Java 17 runtime; it uses a stable subset compatible with Java 25 and was checked against the Java 25 API documentation. A Java 25 runtime was not available for execution here. This is a domain-only executable: repository loading, database transactions, outbox delivery, and multi-transaction tests remain integration responsibilities.

One instance belongs to one command attempt on one thread. The sample has no persistence rehydration path, root version, or event-draining lifecycle. It deliberately keeps those adapter concerns outside the executable domain lesson. Its pending events describe only that attempt; discard the instance after commit or rollback.

AggregateGuideDemo.java · part 1 of 6

```
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

public final class AggregateGuideDemo {
    public record OrderId(UUID value) {
        public OrderId { Objects.requireNonNull(value); }
    }

    public record CustomerId(UUID value) {
        public CustomerId { Objects.requireNonNull(value); }
    }

    public record ProductId(UUID value) {
        public ProductId { Objects.requireNonNull(value); }
    }

    public record OrderLineId(UUID value) {
        public OrderLineId { Objects.requireNonNull(value); }
    }

    public enum OrderStatus { DRAFT, CONFIRMED }

    public record LineSnapshot(
            OrderLineId id, ProductId productId, int quantity) {
        public LineSnapshot {
            Objects.requireNonNull(id);
            Objects.requireNonNull(productId);
            if (quantity <= 0) {
                throw new IllegalArgumentException("Positive quantity required");
            }
        }
    }
```

AggregateGuideDemo.java · part 2 of 6

```
// A pending fact about this attempt; it is not yet durable.
    public record OrderConfirmed(UUID eventId, OrderId orderId) {
        public OrderConfirmed {
            Objects.requireNonNull(eventId);
            Objects.requireNonNull(orderId);
        }
    }

    public static final class RuleViolation extends RuntimeException {
        public RuleViolation(String message) { super(message); }
    }

    // One instance belongs to one command attempt, on one thread.
    public static final class Order {
        public static final int MAX_UNITS = 100;
        private final OrderId id;
        private final CustomerId customerId;
        private OrderStatus status = OrderStatus.DRAFT;
        private final Map<OrderLineId, OrderLine> lines =
                new LinkedHashMap<>();
        private final List<OrderConfirmed> pendingEvents = new ArrayList<>();

        public Order(OrderId id, CustomerId customerId) {
            this.id = Objects.requireNonNull(id);
            this.customerId = Objects.requireNonNull(customerId);
        }

        public OrderId id() { return id; }
        public CustomerId customerId() { return customerId; }
        public OrderStatus status() { return status; }

        public int totalQuantity() {
            return lines.values().stream()
                    .mapToInt(line -> line.quantity).sum();
        }
```

AggregateGuideDemo.java · part 3 of 6

```
public List<LineSnapshot> lines() {
            List<LineSnapshot> snapshots = new ArrayList<>();
            for (OrderLine line : lines.values()) {
                snapshots.add(new LineSnapshot(
                        line.id, line.productId, line.quantity));
            }
            return List.copyOf(snapshots);
        }

        public List<OrderConfirmed> pendingEvents() {
            return List.copyOf(pendingEvents);
        }

        public OrderLineId addLine(ProductId productId, int quantity) {
            ensureDraft();
            Objects.requireNonNull(productId);
            ensurePositive(quantity);
            ensureCapacity(totalQuantity(), quantity);

            OrderLineId lineId;
            do {
                lineId = new OrderLineId(UUID.randomUUID());
            } while (lines.containsKey(lineId));
            lines.put(lineId, new OrderLine(lineId, productId, quantity));
            return lineId;
        }

        public void changeQuantity(OrderLineId lineId, int quantity) {
            ensureDraft();
            ensurePositive(quantity);
            OrderLine line = findLine(lineId);
            int otherUnits = totalQuantity() - line.quantity;
            ensureCapacity(otherUnits, quantity);
            line.quantity = quantity;
        }

        public void removeLine(OrderLineId lineId) {
            ensureDraft();
            findLine(lineId);
            lines.remove(lineId);
        }
```

AggregateGuideDemo.java · part 4 of 6

```
public void confirm() {
            ensureDraft();
            if (lines.isEmpty()) {
                throw new RuleViolation("An empty order cannot be confirmed");
            }
            OrderConfirmed event = new OrderConfirmed(UUID.randomUUID(), id);
            status = OrderStatus.CONFIRMED;
            pendingEvents.add(event);
        }

        private void ensureDraft() {
            if (status != OrderStatus.DRAFT) {
                throw new RuleViolation("Confirmed orders cannot change");
            }
        }

        private static void ensurePositive(int quantity) {
            if (quantity <= 0) {
                throw new RuleViolation("Quantity must be positive");
            }
        }

        private static void ensureCapacity(int otherUnits, int quantity) {
            // Subtraction avoids overflowing otherUnits + quantity.
            if (quantity > MAX_UNITS - otherUnits) {
                throw new RuleViolation("Order cannot exceed 100 units");
            }
        }

        private OrderLine findLine(OrderLineId lineId) {
            Objects.requireNonNull(lineId);
            OrderLine line = lines.get(lineId);
            if (line == null) {
                throw new RuleViolation("Line does not belong to this order");
            }
            return line;
        }

        // Mutable children never cross the root's public API.
        private static final class OrderLine {
            private final OrderLineId id;
            private final ProductId productId;
            private int quantity;
```

AggregateGuideDemo.java · part 5 of 6

```
private OrderLine(OrderLineId id, ProductId productId, int quantity) {
                this.id = id;
                this.productId = productId;
                this.quantity = quantity;
            }
        }
    }

    public static void main(String[] args) {
        Order order = new Order(
                new OrderId(UUID.randomUUID()),
                new CustomerId(UUID.randomUUID()));
        ProductId productA = new ProductId(UUID.randomUUID());
        ProductId productB = new ProductId(UUID.randomUUID());

        expect(RuleViolation.class, order::confirm);
        check(order.status() == OrderStatus.DRAFT, "Empty confirm changed status");
        check(order.pendingEvents().isEmpty(), "Rejected confirm emitted an event");

        OrderLineId a = order.addLine(productA, 40);
        OrderLineId b = order.addLine(productB, 50);
        List<LineSnapshot> before = order.lines();
        expect(RuleViolation.class, () -> order.changeQuantity(b, 70));
        check(order.lines().equals(before), "Rejected change mutated lines");
        check(order.totalQuantity() == 90, "Expected 90 units");

        order.changeQuantity(b, 60);
        check(order.totalQuantity() == 100, "Exactly 100 must be allowed");
        List<LineSnapshot> atCapacity = order.lines();
        expect(RuleViolation.class, () -> order.addLine(productA, 1));
        expect(RuleViolation.class, () -> order.changeQuantity(b, 0));
        expect(RuleViolation.class, () -> order.changeQuantity(b, -1));
        expect(RuleViolation.class,
                () -> order.changeQuantity(b, Integer.MAX_VALUE));
        expect(RuleViolation.class,
                () -> order.addLine(productB, Integer.MAX_VALUE));
        OrderLineId foreign = new OrderLineId(UUID.randomUUID());
        expect(RuleViolation.class, () -> order.changeQuantity(foreign, 1));
        expect(RuleViolation.class, () -> order.removeLine(foreign));
        check(order.lines().equals(atCapacity), "Rejected commands changed state");
```

AggregateGuideDemo.java · part 6 of 6

```
expect(UnsupportedOperationException.class, () -> order.lines().clear());
        check(before.get(1).quantity() == 50, "Snapshot changed after mutation");
        order.removeLine(a);
        check(order.totalQuantity() == 60, "Removal did not reduce total");
        order.changeQuantity(b, 40);
        order.confirm();
        check(order.status() == OrderStatus.CONFIRMED, "Confirmation failed");
        check(order.pendingEvents().size() == 1, "Expected one pending event");
        check(order.pendingEvents().get(0).orderId().equals(order.id()),
                "Event identifies another order");

        List<LineSnapshot> confirmedLines = order.lines();
        expect(RuleViolation.class, () -> order.addLine(productA, 1));
        expect(RuleViolation.class, () -> order.changeQuantity(b, 1));
        expect(RuleViolation.class, () -> order.removeLine(b));
        expect(RuleViolation.class, order::confirm);
        expect(UnsupportedOperationException.class,
                () -> order.pendingEvents().clear());
        check(order.lines().equals(confirmedLines), "Confirmed contents changed");
        check(order.pendingEvents().size() == 1, "Duplicate confirmation event");
        System.out.println("All aggregate checks passed.");
    }

    private static void check(boolean condition, String message) {
        if (!condition) { throw new AssertionError(message); }
    }

    private static void expect(
            Class<? extends Throwable> expected, Runnable action) {
        try {
            action.run();
        } catch (Throwable failure) {
            if (expected.isInstance(failure)) { return; }
            throw new AssertionError("Unexpected failure", failure);
        }
        throw new AssertionError("Expected " + expected.getSimpleName());
    }
}
```

Appendix B · References

## Sources & scope

The first-principles order example and lesson sequence adapt the conversation supplied with this request. The implementation, failure cases, and credit-reservation discussion are worked design reasoning for the stated example, not universal prescriptions. Official sources below verify the referenced platform and pattern claims. Checked 2 September 2026.

* [[1] Microsoft Learn · Design a microservice domain model](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/microservice-domain-model)Aggregate boundaries, roots, identity references, and proportionate use of rich domain models.https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/microservice-domain-model
* [[2] Microsoft Learn · Design the infrastructure persistence layer](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)Root-oriented write repositories, independent read queries, Unit of Work, and the optional nature of custom repositories.https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design
* [[3] Oracle · Java SE 25 List API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html)Unmodifiable collections, mutable elements, and List.copyOf.https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html
* [[4] Oracle · Java 25 Record Classes](https://docs.oracle.com/en/java/javase/25/language/records.html)Record components, generated members, and constructor validation.https://docs.oracle.com/en/java/javase/25/language/records.html
* [[5] Oracle · Java SE 25 Connection API](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html)Auto-commit, explicit commit/rollback, and transaction-bound connection behavior.https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html
* [[6] PostgreSQL · Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html)Read Committed snapshots, concurrent updates, and serialization failure handling.https://www.postgresql.org/docs/18/transaction-iso.html
* [[7] AWS Prescriptive Guidance · Transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)Atomic state/outbox persistence, publication retries, duplicate delivery, and idempotent consumers.https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

DP · Architecture Notes · Lesson 20
Self-contained HTML: inline styles, inline enhancement script, embedded Java source; no external fonts, scripts, images, or runtime fetches.