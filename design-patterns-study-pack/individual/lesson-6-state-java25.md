[Skip to the lesson](#part-1)

DP / Design patterns / Lesson 06

# State

Behavior follows the lifecycle.

The same object receives the same operation. What it may do depends on its current state.

Java 25-compatibleNo external dependenciesSelf-contained / light theme

Start with an invalid transition. Discover the rules. Introduce state objects only when the behavior needs them.

Print / Save as PDF

Read in order, or use the section links below. For PDF: print in portrait at 100% scale; turn off browser headers and footers. All lesson text and Java listings are included in this file.

## Inside the guide

1. [1. Find the modeling problemSections 01–05 · status, rules, pressure](#part-1)
2. [2. Build State in JavaSections 06–10 · context and six states](#part-2)
3. [3. Understand the alternativesSections 11–15 · intent, matrix, enum switch](#part-3)
4. [4. Model data and verify behaviorSections 16–20 · sealed records, tests, persistence](#part-4)
5. [5. Cross the production boundarySections 21–27 · conflicts, effects, events](#part-5)
6. [6. Practice with a ticket lifecycleWorksheet, acceptance criteria, answer table](#exercise)
7. [Appendix A · runnable JavaComplete source and transition tests](#appendix)
8. [Official referencesLanguage rules and architecture sources](#references)

Part 1

## Find the modeling problem

### 01Start with the simplest implementation

An order has a status. The first version treats operations as assignments:

Java • deliberately unsafe starting point

```
enum Status {
    CREATED, PAID, PACKED, SHIPPED, DELIVERED, CANCELLED
}

final class NaiveOrder {
    Status status = Status.CREATED;

    void pay() { status = Status.PAID; }
    void ship() { status = Status.SHIPPED; }
    void cancel() { status = Status.CANCELLED; }
}
```

Java • excerpt

```
NaiveOrder order = new NaiveOrder();
order.ship(); // CREATED becomes SHIPPED without payment or packing.
```

The code compiles, but the business rule is broken. A status label tells us where the object is. It does not say how the object may get there.

### 02Ask what defines the lifecycle

A lifecycle needs **states and legal transitions**. For this lesson, the order follows the rules below. They are teaching rules, not universal commerce rules.

The lifecycle contract

| Current state | Operation | Next state |
| --- | --- | --- |
| Created | `pay()` | Paid |
| Paid | `pack()` | Packed |
| Packed | `ship()` | Shipped |
| Shipped | `deliver()` | Delivered |
| Created, Paid, or Packed | `cancel()` | Cancelled |

Delivered and Cancelled are terminal states in this model. All unlisted operations, including repeated operations, fail explicitly. Cancellation after shipment is prohibited; a returns process would be a separate model.

**First principle**

The important object is the state machine: a set of states plus the rules that connect them.

### 03Protect the rules with simple checks

Java • partial lifecycle, using the Status enum above

```
final class GuardedOrder {
    private Status status = Status.CREATED;

    Status status() { return status; }

    void pay() {
        require(Status.CREATED, "pay");
        status = Status.PAID;
    }

    void pack() {
        require(Status.PAID, "pack");
        status = Status.PACKED;
    }

    void ship() {
        require(Status.PACKED, "ship");
        status = Status.SHIPPED;
    }

    private void require(Status expected, String operation) {
        if (status != expected) {
            throw new IllegalStateException(
                "Cannot " + operation + " order in " + status);
        }
    }
}
```

Now an unpaid order cannot ship, and callers cannot directly assign its status. This is already a useful design.

**Do not introduce State objects yet**

A few explicit checks can be clearer than a class hierarchy. Keep the smallest representation that makes the rules easy to see.

### 04Wait for real pressure

Cancellation starts to vary by state. Created orders need no refund. Paid orders need a refund. Packed orders need inventory released before the refund. We assume packing reserves inventory in this teaching model.

Java • method sketch; effects is a collaborator

```
void cancel() {
    switch (status) {
        case CREATED -> status = Status.CANCELLED;
        case PAID -> {
            effects.refund();
            status = Status.CANCELLED;
        }
        case PACKED -> {
            effects.release();
            effects.refund();
            status = Status.CANCELLED;
        }
        case SHIPPED, DELIVERED, CANCELLED ->
            throw new IllegalStateException(
                "Cannot cancel order in " + status);
    }
}
```

One switch is not a problem by itself. Pressure appears when `pay()`, `pack()`, `ship()`, `cancel()`, and future refund or return operations each carry their own state logic.

### 05Diagnose the axis of change

Suppose the rules for Packed change. If you must inspect many operations to find every Packed branch, related behavior is spread across the class.

| Organization | Where a Packed rule lives | What a change touches |
| --- | --- | --- |
| By operation | A branch in each relevant method | Several methods |
| By state | The Packed state object | Primarily one state implementation |

This is the pressure behind the State pattern: **group behavior that changes together**. The order keeps its identity while its current state object determines the legal response to an operation. Microsoft’s pattern explanation describes this delegation and localization. [[1]](#ref-state)

Part 2

## Build State in Java

Use the current state to decide behavior, and keep state replacement inside the model.

### 06Define the state capability and context

The context is `Order`. Its state interface describes the same operations. Rejection is the default, so each concrete state only overrides the operations it permits.

Java • nested inside StateDemo

```
private interface OrderState {
    Status status();

    default void pay(Order order) { throw invalid("pay"); }
    default void pack(Order order) { throw invalid("pack"); }
    default void ship(Order order) { throw invalid("ship"); }
    default void deliver(Order order) { throw invalid("deliver"); }
    default void cancel(Order order) { throw invalid("cancel"); }

    private IllegalStateException invalid(String operation) {
        return new IllegalStateException(
            "Cannot " + operation + " order in " + status());
    }
}
```

Java • context, nested inside StateDemo

```
public static final class Order {
    private OrderState state = new CreatedState();
    private final Effects effects;

    public Order(Effects effects) {
        this.effects = Objects.requireNonNull(effects);
    }

    public Status status() { return state.status(); }
    public void pay() { state.pay(this); }
    public void pack() { state.pack(this); }
    public void ship() { state.ship(this); }
    public void deliver() { state.deliver(this); }
    public void cancel() { state.cancel(this); }

    private void transitionTo(OrderState next) {
        state = Objects.requireNonNull(next);
    }
}
```

The complete source in [Appendix A](#appendix) places the context and private state types in one enclosing class. This lets the nested state implementations use private transition machinery while ordinary callers only see business operations. There is no public state setter or public `transitionTo()`. Java access control permits this enclosing-class arrangement. [[2]](#ref-access)

`Effects` is a small interface for `charge()`, `refund()`, `reserve()`, and `release()`. The runnable example supplies a recording fake, so no payment or inventory system is needed.

### 07Created owns the Created rules

Java • excerpt

```
private static final class CreatedState implements OrderState {
    public Status status() { return Status.CREATED; }

    public void pay(Order order) {
        order.effects.charge();
        order.transitionTo(new PaidState());
    }

    public void cancel(Order order) {
        order.transitionTo(new CancelledState());
    }
}
```

`pay()` charges first, then advances. `cancel()` needs no refund. Packing, shipping, and delivery inherit explicit rejection. If `charge()` throws, the next-state assignment is not reached.

### 08Paid owns the Paid rules

Java • excerpt

```
private static final class PaidState implements OrderState {
    public Status status() { return Status.PAID; }

    public void pack(Order order) {
        order.effects.reserve();
        order.transitionTo(new PackedState());
    }

    public void cancel(Order order) {
        order.effects.refund();
        order.transitionTo(new CancelledState());
    }
}
```

A Paid order may be packed or cancelled. It cannot be paid again or shipped before packing. Inventory reservation belongs to `pack()` in this example; that rule should be explicit rather than silently assumed.

### 09Packed owns the Packed rules

Java • excerpt

```
private static final class PackedState implements OrderState {
    public Status status() { return Status.PACKED; }

    public void ship(Order order) {
        order.transitionTo(new ShippedState());
    }

    public void cancel(Order order) {
        order.effects.release();
        order.effects.refund();
        order.transitionTo(new CancelledState());
    }
}
```

All Packed behavior is now together. A change to cancellation from Packed has a clear home.

**A state assignment is not a transaction**

If release succeeds and refund throws, the object remains Packed, but inventory was already released. The sample deliberately tests this case. A stable status does not mean earlier external effects were undone. See [section 21](#s21) for the boundary.

### 10Complete the structure, including delivery

Java • excerpt

```
private static final class ShippedState implements OrderState {
    public Status status() { return Status.SHIPPED; }

    public void deliver(Order order) {
        order.transitionTo(new DeliveredState());
    }
}

private static final class DeliveredState implements OrderState {
    public Status status() { return Status.DELIVERED; }
}

private static final class CancelledState implements OrderState {
    public Status status() { return Status.CANCELLED; }
}
```

| Participant | Responsibility |
| --- | --- |
| Client | Requests an operation such as `order.ship()`. |
| Order | Delegates to its current state and owns the state reference. |
| OrderState | Defines the protocol and explicit default rejection. |
| Concrete state | Performs allowed behavior and chooses a legal next state. |

The state objects do not store mutable per-order fields here. Two orders hold independent state references. The example is single-threaded; sharing a context across threads requires additional coordination.

Part 3

## Understand the alternatives

### 11Separate State from Strategy

Both patterns can hold an interface and delegate through it. The difference is the reason for variation.

| Question | Strategy | State |
| --- | --- | --- |
| What varies? | The algorithm used for a task. | The legal behavior at a lifecycle stage. |
| Typical selection | Caller or configuration chooses a policy. | An accepted operation changes the current state. |
| Example | Express versus standard shipping calculation. | Paid versus Packed behavior. |

A shipping strategy answers “How should I calculate shipping?” A state answers “May this order ship now, and what must happen if it does?” External selection is common for Strategy, but it is not a universal rule; intent is the useful distinction.

### 12Treat transitions as the actual model

For each pair of **current state and operation**, define the behavior and the next state, or define rejection. A transition table exposes gaps before you write classes.

Complete order transition matrix • 6 states × 5 operations

| Current | pay | pack | ship | deliver | cancel |
| --- | --- | --- | --- | --- | --- |
| Created | Paid | Reject | Reject | Reject | Cancelled |
| Paid | Reject | Packed | Reject | Reject | Cancelled |
| Packed | Reject | Reject | Shipped | Reject | Cancelled |
| Shipped | Reject | Reject | Reject | Delivered | Reject |
| Delivered | Reject | Reject | Reject | Reject | Reject |
| Cancelled | Reject | Reject | Reject | Reject | Reject |

Every cell is intentional: 7 accepted transitions and 23 rejections. Successful payment charges; successful packing reserves inventory; cancellation refunds from Paid and releases then refunds from Packed. Shipping and delivery only change local status in the runnable teaching example.

#### Try the lifecycle

Attempt any operation. Rejection leaves the state unchanged.

Current state: **Created**

PayPackShipDeliverCancelReset order

Start with Ship to see an invalid transition.

This browser illustration mirrors the transition table. It does not execute Java or call external systems.

### 13Protect invariants, not just fields

The invariant is “an order can ship only after it is packed.” A private field helps only if the public API protects that rule.

Java • excerpt

```
order.ship(); // The current state decides whether this is legal.

// These are unavailable to an ordinary caller:
// order.status = Status.DELIVERED;
// order.transitionTo(new DeliveredState());
```

Exposing a general state-changing method would let clients bypass the machine. Construction starts at Created. Rehydration, discussed later, is a separate trusted persistence operation.

**Encapsulation**

Expose intentions as operations. Keep arbitrary state replacement inside the model.

### 14An enum and a switch can be enough

A state machine is a model. The classic object-oriented State pattern is one way to implement it. For small machines, an enum plus a transition function can be the clearest representation.

Java • members of a class, using the six-value Status enum

```
enum Action { PAY, PACK, SHIP, DELIVER, CANCEL }

static Status next(Status state, Action action) {
    java.util.Objects.requireNonNull(state);
    java.util.Objects.requireNonNull(action);
    return switch (state) {
        case CREATED -> switch (action) {
            case PAY -> Status.PAID;
            case CANCEL -> Status.CANCELLED;
            default -> throw invalid(state, action);
        };
        case PAID -> switch (action) {
            case PACK -> Status.PACKED;
            case CANCEL -> Status.CANCELLED;
            default -> throw invalid(state, action);
        };
        case PACKED -> switch (action) {
            case SHIP -> Status.SHIPPED;
            case CANCEL -> Status.CANCELLED;
            default -> throw invalid(state, action);
        };
        case SHIPPED -> switch (action) {
            case DELIVER -> Status.DELIVERED;
            default -> throw invalid(state, action);
        };
        case DELIVERED, CANCELLED -> throw invalid(state, action);
    };
}

static IllegalStateException invalid(Status state, Action action) {
    return new IllegalStateException(action + " is invalid in " + state);
}
```

This pure function determines the next status. It does not charge, refund, reserve, or release anything. If effects are required, represent the decision separately or orchestrate those effects explicitly.

Java 25 supports enum switch expressions. A switch expression must cover its possible inputs. The outer switch lists every status; its exhaustiveness helps surface a newly added enum constant when this code is recompiled. Explicit null checks keep null outside the model. [[3]](#ref-switch)

### 15Graduate only when behavior justifies it

| Pressure | A useful starting point |
| --- | --- |
| Few rules, little behavior | Private enum and small guarded methods. |
| Many transitions, mostly data | Transition table or a pure transition function. |
| Substantial behavior differs by state | State objects with rules localized by state. |
| Long-running, retrying, distributed work | A workflow design; State may be one part of it. |

There is no threshold such as “six states means six classes.” Ask how often the rules change, how much behavior belongs to each state, and whether the new organization makes those changes more local. A table can remain the best choice.

Part 4

## Model data and verify behavior

### 16Notice when the data also changes

Java • weak data model, for diagnosis

```
final class WeakOrderData {
    Status status;
    String paymentId;
    String trackingNumber;
    java.time.Instant shippedAt;
    java.time.Instant deliveredAt;
    String cancellationReason;
}
```

This shape allows a Created order with a tracking number and a delivery timestamp. Many optional fields make the intended combinations hard to see. Behavior and data are two related modeling problems: State objects organize behavior; different data variants can express what exists at each stage.

### 17Use sealed types and records for data variants

Java’s counterpart to the lesson’s discriminated union is a sealed interface with record implementations. This deliberately reduced *snapshot* example shows only three variants to isolate the data idea; it does not redefine the six-state transition contract or permit skipping Packed.

Java • nested members of SnapshotDemo; data illustration

```
sealed interface OrderSnapshot permits Created, Paid, Shipped {
    String orderId();
}

record Created(String orderId) implements OrderSnapshot {
    Created { orderId = required(orderId); }
}

record Paid(String orderId, String paymentId) implements OrderSnapshot {
    Paid {
        orderId = required(orderId);
        paymentId = required(paymentId);
    }
}

record Shipped(String orderId, String paymentId, String trackingNumber)
        implements OrderSnapshot {
    Shipped {
        orderId = required(orderId);
        paymentId = required(paymentId);
        trackingNumber = required(trackingNumber);
    }
}

static String required(String value) {
    if (value == null || value.isBlank()) {
        throw new IllegalArgumentException("Required value is blank");
    }
    return value;
}
```

A `Created` value has no `trackingNumber()` method. A `Shipped` value requires a nonblank tracking number. A sealed interface restricts its permitted implementations, and records supply component accessors and value-based equality. [[4]](#ref-sealed) [[5]](#ref-records)

Java 25 • exhaustive pattern switch; no preview required

```
static String shippingLabel(OrderSnapshot snapshot) {
    java.util.Objects.requireNonNull(snapshot);
    return switch (snapshot) {
        case Created c -> "Not shipped: " + c.orderId();
        case Paid p -> "Awaiting fulfilment: " + p.orderId();
        case Shipped s -> "Tracking: " + s.trackingNumber();
    };
}
```

The pattern switch can handle every permitted variant without a catch-all default. Recompile after changing a sealed hierarchy so missing cases are checked. These reference-type patterns are permanent Java language features supported in Java 25. [[6]](#ref-patterns)

**What the types do and do not prove**

They constrain the shape of each value. They do not prove that payment happened or that every earlier transition occurred. Constructors or factories still need validation and trusted inputs. Record component fields are final, but referenced mutable objects are not made deeply immutable. [[7]](#ref-record-api)

### 18Choose between behavior objects and data variants

| Approach | Best fit | Main tradeoff |
| --- | --- | --- |
| Classic OO State | Rich behavior and collaborators vary by state. | More types; changes to the operation protocol affect many states. |
| Sealed records and functions | Data differs strongly by stage; closed variants are useful. | Functions must account for variants; transitions remain explicit. |
| Enum and transition table | The graph is the main complexity; behavior is small. | State-specific data and effects need a separate design. |

These approaches can coexist. An application may use a mutable context internally and immutable records for persistence or events. The goal is a clear lifecycle contract, not a particular class diagram.

### 19Test the matrix, failures, and effects

Test legal transitions and prohibited transitions separately. On rejection, also verify that the original state remains intact and no effect was invoked.

Java • test excerpt from the same enclosing test context

```
RecordingEffects effects = new RecordingEffects();
Order order = new Order(effects);

mustFail(order::ship);
equal(order.status(), Status.CREATED);
equal(effects.calls, List.of());

order.pay();
equal(order.status(), Status.PAID);
equal(effects.calls, List.of("charge"));
```

Appendix A exercises all 30 cells of the section 12 matrix with a fresh order per cell. Additional tests check cancellation effects, failed charge and reserve calls, a partial cancellation failure, and independence of two orders.

**Test the contract**

An exception is only part of the assertion. Check the status and effects after the attempt. The test helpers throw `AssertionError` directly, so no `-ea` flag or external test library is required.

For a production system, add tests for input guards, persisted data validation, conflicting updates, retried commands, and emitted events. The right coverage follows the actual business contract.

### 20Rehydrate state at a trusted boundary

Persistence should store stable domain values, not Java state-class names. A factory can translate a validated stored status into its runtime representation:

Java • persistence extension inside the enclosing model

```
private static OrderState stateFrom(Status status) {
    java.util.Objects.requireNonNull(status);
    return switch (status) {
        case CREATED -> new CreatedState();
        case PAID -> new PaidState();
        case PACKED -> new PackedState();
        case SHIPPED -> new ShippedState();
        case DELIVERED -> new DeliveredState();
        case CANCELLED -> new CancelledState();
    };
}
```

This factory restores a snapshot; it must not replay `pay()` or other effects. A repository should validate the stored status and all required accompanying fields before calling a restricted restoration path. Unknown values should be rejected or deliberately migrated, not silently mapped to Created.

The Factory idea returns here: creation and reconstruction have a clear home. A public “set any state” endpoint is still inappropriate.

Part 5

## Cross the production boundary

### 21Handle concurrency and transaction boundaries separately

Two requests can both read Packed. One cancels; the other ships. Each transition is legal against its own snapshot, but both must not independently take effect as though nothing else changed.

| Step | Cancel request | Ship request |
| --- | --- | --- |
| Read | Packed, version 7 | Packed, version 7 |
| Decide | Cancel is legal. | Ship is legal. |
| Persist with version check | One request updates version 7 to 8. | The other must detect a stale version. |

SQL • optimistic update sketch

```
UPDATE orders
SET status = 'shipped', version = version + 1
WHERE id = ? AND status = 'packed' AND version = ?;
```

With a unique order ID, expect one affected row. Zero rows means the expected record did not match: it may have changed or been deleted. Treat that as a conflict or missing record, then reload and re-evaluate the command; do not blindly repeat external effects. Version-based updates are a standard optimistic concurrency technique. [[8]](#ref-concurrency)

**Two different problems**

The version check protects a persisted update. It does not roll back a payment, an inventory call, or a shipment already sent to a carrier. Choose transaction boundaries, idempotency, and recovery steps explicitly. The State pattern supplies none of those mechanisms by itself.

Moving `transitionTo()` after an effect only avoids advancing when the call throws. A timeout can occur after the remote system succeeds. Multi-step cancellation can also partially succeed. A real workflow may need intermediate states, durable work records, retries with stable idempotency keys, and compensation. The exact design depends on the business process.

### 22Let accepted transitions produce events

After a transition into Shipped, other components may need to notify the customer or update tracking. A dedicated event can carry the fact they need.

Java • illustrative event payload; validate at creation

```
record OrderShipped(
    java.util.UUID eventId,
    String orderId,
    String trackingNumber,
    java.time.Instant occurredAt
) { }
```

Record the event only after the transition’s guards and required work succeed. If the order is persisted, a change in memory is not yet proof of a committed database fact.

For reliable external publication, one option is to save the order update and an outbox record in the same database transaction. A relay publishes committed outbox records later. Delivery may still be repeated, so consumers need duplicate-safe handling. This addresses the dual-write gap; it does not make remote effects atomic. [[9]](#ref-outbox)

### 23Keep commands and events distinct

| Message | Meaning | Can it be rejected? |
| --- | --- | --- |
| `ShipOrder` | Please attempt shipping. | Yes: the current state or another guard may prohibit it. |
| `OrderShipped` | Shipping has happened under the defined business contract. | It is a reported fact; consumers may still fail to process it. |

A command enters the model, the model validates the current state and other guards, required work is performed, and an accepted transition can yield an event. An illegal command must not produce a success event.

Define what “shipped” actually means in your domain: a label printed, a carrier handoff, or something else. Naming an event does not settle that business definition. The runnable example only demonstrates local lifecycle rules.

### 24Combine State and Observer deliberately

| Concern | State | Observer |
| --- | --- | --- |
| Core question | What may this object do now? | Who reacts to a fact that happened? |
| Scope | The object’s lifecycle and invariants. | Independent reactions to a notification. |
| Example | Only Packed may accept ship. | Email and analytics react to OrderShipped. |

State decides whether a transition is legal. Observer distributes its consequences. Do not put mandatory ordered steps into independent observers merely to reduce direct references; an explicit workflow is clearer when one step must succeed before another.

### 25Recognize the pressure, not the diagram

The same delegation structure can solve very different problems. Use intent to identify the pattern:

| Situation | Pattern or design pressure |
| --- | --- |
| Choose standard or express pricing. | Strategy: interchangeable algorithms. |
| Rebuild the current state from stored data. | Factory: controlled creation. |
| Translate a legacy carrier interface. | Adapter: interface mismatch. |
| Layer logging around one service call. | Decorator: added behavior along a call path. |
| Several independent parties react to OrderShipped. | Observer: notification. |
| An order’s legal operations depend on Paid versus Packed. | State: lifecycle-dependent behavior. |

State may be implemented with polymorphism, but polymorphism alone does not tell you that a design is State.

### 26Avoid a forest of empty state classes

Separate classes become a poor bargain when most methods only reject and very little behavior varies. Default rejection reduces repetition, but it does not justify an unnecessary hierarchy.

If you keep adding states such as RefundRequested, RefundApproved, RefundProcessing, and RefundCompleted, ask whether you are modeling an order, a payment workflow, or several lifecycles forced into one enum. Independent dimensions may deserve separate models; splitting them still requires explicit cross-model invariants.

**The cost to watch**

State objects localize behavior, but spread the transition graph across types. Keep the transition table beside the code so reviewers can still see the whole lifecycle.

### 27Use the first-principles checklist

1. Does the same operation behave differently because of the object’s lifecycle?
2. Have you defined every legal transition and explicit rejection?
3. Which invariants must the public API protect?
4. Is logic for one state scattered across many operations?
5. Would grouping by state make changes easier to review?
6. Would a small switch or transition table remain clearer?
7. Where do side effects, persistence, conflicts, and retries belong?

Introduce State objects when that organization helps the behavior stay coherent. A guarded enum is a sound answer when it makes the same rules easier to understand.

Practice

## Build a support ticket lifecycle

Write the transition table first. Then choose the representation.

The normal path is Open, Assigned, Resolved, then Closed. Additional rules allow unassignment, reopening, and cancellation before assignment.

| Current | Operation | Next |
| --- | --- | --- |
| Open | assign | Assigned |
| Assigned | unassign | Open |
| Assigned | resolve | Resolved |
| Resolved | reopen | Assigned |
| Resolved | close | Closed |
| Open | close (cancel) | Closed |

**Resolve the command name**

This exercise uses `close()` for both cancellation from Open and normal closure from Resolved. There is no separate `cancel()` method. Closed is terminal; all unlisted operations reject.

Java • design sketch; implement Ticket as the context

```
enum TicketStatus { OPEN, ASSIGNED, RESOLVED, CLOSED }

interface TicketState {
    TicketStatus status();
    void assign(Ticket ticket);
    void unassign(Ticket ticket);
    void resolve(Ticket ticket);
    void reopen(Ticket ticket);
    void close(Ticket ticket);
}
```

First fill this table. Write the target state or “Reject” in every cell:

Worksheet • 20 decisions

| Current | assign | unassign | resolve | reopen | close |
| --- | --- | --- | --- | --- | --- |
| Open | ? | ? | ? | ? | ? |
| Assigned | ? | ? | ? | ? | ? |
| Resolved | ? | ? | ? | ? | ? |
| Closed | ? | ? | ? | ? | ? |

### Acceptance criteria

1. Illegal transitions fail explicitly and leave the current state intact.
2. The Ticket context delegates instead of accumulating status branches.
3. Rules for each state are localized.
4. Tests cover all 20 state/action pairs, including all illegal paths.
5. External callers cannot directly assign the status or replace the state.
6. The meaning of close from Open is documented as cancellation.

Check the transition table

Answer • 6 legal transitions, 14 rejections

| Current | assign | unassign | resolve | reopen | close |
| --- | --- | --- | --- | --- | --- |
| Open | Assigned | Reject | Reject | Reject | Closed |
| Assigned | Reject | Open | Resolved | Reject | Reject |
| Resolved | Reject | Reject | Reject | Assigned | Closed |
| Closed | Reject | Reject | Reject | Reject | Reject |

A useful path test is assign, resolve, reopen, unassign, close. Also verify that Closed rejects every operation, Assigned cannot close directly, and Open cannot resolve.

If tickets carry an assignee, reopening needs another explicit rule: restore the previous assignee, require a new assignee, or reopen into Open. The exercise above tests only the status lifecycle; do not silently invent that data rule.

Next • Lesson 7

## Command: represent an action as a value

State answered “What is legal now?” The next pressure is different: you need to queue, log, authorize, retry, schedule, or sometimes undo an action.

The next design question is whether a request such as ShipOrder can become an object or value that is stored, passed around, and executed later. Making a command retryable or undoable still requires explicit business semantics.

Appendix A

## Complete runnable Java example

Save the following complete listing as StateDemo.java. The nested types keep the example in one file while protecting state replacement from ordinary callers.

Terminal • use a JDK 25 installation

```
javac --release 25 -Xlint:all StateDemo.java
java StateDemo
```

No external libraries and no preview flags are required. The file includes the model, recording effects, and test harness. The Java 25 `javac` manual documents `--release`. [[10]](#ref-javac)

Download StateDemo.java

StateDemo.java • part 1 of 6

```
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public final class StateDemo {
    public enum Status {
        CREATED, PAID, PACKED, SHIPPED, DELIVERED, CANCELLED
    }

    public interface Effects {
        void charge();
        void refund();
        void reserve();
        void release();
    }

    public static final class Order {
        private OrderState state = new CreatedState();
        private final Effects effects;

        public Order(Effects effects) {
            this.effects = Objects.requireNonNull(effects);
        }

        public Status status() { return state.status(); }
        public void pay() { state.pay(this); }
        public void pack() { state.pack(this); }
        public void ship() { state.ship(this); }
        public void deliver() { state.deliver(this); }
        public void cancel() { state.cancel(this); }

        private void transitionTo(OrderState next) {
            state = Objects.requireNonNull(next);
        }
    }

    private interface OrderState {
        Status status();

        default void pay(Order order) { throw invalid("pay"); }
        default void pack(Order order) { throw invalid("pack"); }
        default void ship(Order order) { throw invalid("ship"); }
        default void deliver(Order order) { throw invalid("deliver"); }
        default void cancel(Order order) { throw invalid("cancel"); }
```

StateDemo.java • part 2 of 6

```
        private IllegalStateException invalid(String operation) {
            return new IllegalStateException(
                "Cannot " + operation + " order in " + status());
        }
    }

    private static final class CreatedState implements OrderState {
        public Status status() { return Status.CREATED; }

        public void pay(Order order) {
            order.effects.charge();
            order.transitionTo(new PaidState());
        }

        public void cancel(Order order) {
            order.transitionTo(new CancelledState());
        }
    }

    private static final class PaidState implements OrderState {
        public Status status() { return Status.PAID; }

        public void pack(Order order) {
            order.effects.reserve();
            order.transitionTo(new PackedState());
        }

        public void cancel(Order order) {
            order.effects.refund();
            order.transitionTo(new CancelledState());
        }
    }

    private static final class PackedState implements OrderState {
        public Status status() { return Status.PACKED; }

        public void ship(Order order) {
            order.transitionTo(new ShippedState());
        }

        public void cancel(Order order) {
            order.effects.release();
            order.effects.refund();
            order.transitionTo(new CancelledState());
        }
    }
```

StateDemo.java • part 3 of 6

```
    private static final class ShippedState implements OrderState {
        public Status status() { return Status.SHIPPED; }

        public void deliver(Order order) {
            order.transitionTo(new DeliveredState());
        }
    }

    private static final class DeliveredState implements OrderState {
        public Status status() { return Status.DELIVERED; }
    }

    private static final class CancelledState implements OrderState {
        public Status status() { return Status.CANCELLED; }
    }

    // Everything below is a dependency-free test harness.
    private enum Action {
        PAY, PACK, SHIP, DELIVER, CANCEL;

        void apply(Order order) {
            switch (this) {
                case PAY -> order.pay();
                case PACK -> order.pack();
                case SHIP -> order.ship();
                case DELIVER -> order.deliver();
                case CANCEL -> order.cancel();
            }
        }
    }

    private static final class RecordingEffects implements Effects {
        final List<String> calls = new ArrayList<>();
        String failOn;

        private void record(String effect) {
            if (effect.equals(failOn)) {
                throw new IllegalStateException("Failed: " + effect);
            }
            calls.add(effect);
        }

        public void charge() { record("charge"); }
        public void refund() { record("refund"); }
        public void reserve() { record("reserve"); }
        public void release() { record("release"); }
    }
```

StateDemo.java • part 4 of 6

```
    private static Order orderAt(Status target, RecordingEffects effects) {
        Order order = new Order(effects);
        switch (target) {
            case CREATED -> { }
            case PAID -> order.pay();
            case PACKED -> { order.pay(); order.pack(); }
            case SHIPPED -> {
                order.pay(); order.pack(); order.ship();
            }
            case DELIVERED -> {
                order.pay(); order.pack(); order.ship(); order.deliver();
            }
            case CANCELLED -> order.cancel();
        }
        effects.calls.clear();
        return order;
    }

    private static void equal(Object actual, Object expected) {
        if (!Objects.equals(actual, expected)) {
            throw new AssertionError(
                "Expected " + expected + ", got " + actual);
        }
    }

    private static void mustFail(Runnable operation) {
        try {
            operation.run();
        } catch (IllegalStateException expected) {
            return;
        }
        throw new AssertionError("Expected IllegalStateException");
    }
```

StateDemo.java • part 5 of 6

```
    private static void testTransitionMatrix() {
        // Columns: PAY, PACK, SHIP, DELIVER, CANCEL.
        // Rows: CREATED, PAID, PACKED, SHIPPED, DELIVERED, CANCELLED.
        // null means rejection with the original state unchanged.
        Status[][] expected = {
            {Status.PAID, null, null, null, Status.CANCELLED},
            {null, Status.PACKED, null, null, Status.CANCELLED},
            {null, null, Status.SHIPPED, null, Status.CANCELLED},
            {null, null, null, Status.DELIVERED, null},
            {null, null, null, null, null},
            {null, null, null, null, null}
        };
        for (Status from : Status.values()) {
            for (Action action : Action.values()) {
                RecordingEffects effects = new RecordingEffects();
                Order order = orderAt(from, effects);
                Status next = expected[from.ordinal()][action.ordinal()];
                if (next == null) {
                    mustFail(() -> action.apply(order));
                    equal(order.status(), from);
                    equal(effects.calls, List.of());
                } else {
                    action.apply(order);
                    equal(order.status(), next);
                }
            }
        }
    }

    private static void testEffects() {
        RecordingEffects effects = new RecordingEffects();
        Order order = new Order(effects);
        order.pay();
        order.pack();
        order.cancel();
        equal(effects.calls,
            List.of("charge", "reserve", "release", "refund"));
        equal(order.status(), Status.CANCELLED);

        effects = new RecordingEffects();
        order = orderAt(Status.PAID, effects);
        order.cancel();
        equal(effects.calls, List.of("refund"));
```

StateDemo.java • part 6 of 6

```
        effects = new RecordingEffects();
        order = new Order(effects);
        order.cancel();
        equal(effects.calls, List.of());
    }

    private static void testFailures() {
        RecordingEffects effects = new RecordingEffects();
        Order order = new Order(effects);
        effects.failOn = "charge";
        mustFail(order::pay);
        equal(order.status(), Status.CREATED);
        equal(effects.calls, List.of());

        effects = new RecordingEffects();
        order = orderAt(Status.PAID, effects);
        effects.failOn = "reserve";
        mustFail(order::pack);
        equal(order.status(), Status.PAID);

        effects = new RecordingEffects();
        order = orderAt(Status.PACKED, effects);
        effects.failOn = "refund";
        mustFail(order::cancel);
        equal(order.status(), Status.PACKED);
        equal(effects.calls, List.of("release"));
        // State unchanged does NOT mean earlier effects rolled back.
    }

    private static void testIndependentOrders() {
        Order first = new Order(new RecordingEffects());
        Order second = new Order(new RecordingEffects());
        first.pay();
        equal(first.status(), Status.PAID);
        equal(second.status(), Status.CREATED);
    }

    public static void main(String[] args) {
        testTransitionMatrix();
        testEffects();
        testFailures();
        testIndependentOrders();
        System.out.println("PASS: all 30 state/action combinations");
        System.out.println("PASS: effects, failures, independent orders");
    }
}
```

Expected output

```
PASS: all 30 state/action combinations
PASS: effects, failures, independent orders
```

References

## Official sources and scope

Sources checked on 1 September 2026. The lesson’s order and ticket rules are illustrative design contracts; the sources verify language behavior and architectural mechanisms.

**Verification record**

The complete StateDemo.java listing was compiled with `-Xlint:all` and executed on OpenJDK 17.0.20. It passed the included checks. Its language features and APIs are supported by Java 25. A Java 25 runtime was not available for direct execution. The section 17 pattern-switch excerpt is checked against the official Java 25 language documentation; it is not part of StateDemo.java.

1. [State pattern: delegation and localized behavior](https://learn.microsoft.com/en-us/archive/msdn-magazine/2001/july/design-patterns-solidify-your-csharp-application-architecture-with-design-patterns#state)

   Microsoft, MSDN Magazine archive, “Design Patterns,” State section. Used for the pattern’s structure, not as a claim that classes always beat tables.

   https://learn.microsoft.com/en-us/archive/msdn-magazine/2001/july/design-patterns-solidify-your-csharp-application-architecture-with-design-patterns#state
2. [Java SE 25 access control](https://docs.oracle.com/javase/specs/jls/se25/html/jls-6.html#jls-6.6.1)

   Java Language Specification §6.6.1: private access within the enclosing top-level class or interface.

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-6.html#jls-6.6.1
3. [Java SE 25 switch expressions and exhaustiveness](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.11)

   Java Language Specification §14.11 and §15.28.

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.11
4. [Sealed classes and interfaces](https://docs.oracle.com/en/java/javase/25/language/sealed-classes-interfaces.html)

   Oracle Java 25 Language Updates: permitted subtypes and record implementations.

   https://docs.oracle.com/en/java/javase/25/language/sealed-classes-interfaces.html
5. [Record classes](https://docs.oracle.com/en/java/javase/25/language/records.html)

   Oracle Java 25 Language Updates: components, accessors, canonical constructors, and validation.

   https://docs.oracle.com/en/java/javase/25/language/records.html
6. [Pattern matching with switch](https://docs.oracle.com/en/java/javase/25/language/pattern-matching-switch.html)

   Oracle Java 25 Language Updates: reference-type patterns and sealed-hierarchy coverage.

   https://docs.oracle.com/en/java/javase/25/language/pattern-matching-switch.html
7. [Record API and shallow immutability](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html)

   Oracle Java SE 25 API: record components and the limits of immutability.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html
8. [Version checks and optimistic concurrency](https://learn.microsoft.com/en-us/ef/core/saving/concurrency)

   Microsoft EF Core documentation. The version-predicate principle is illustrated here in SQL, without depending on EF Core.

   https://learn.microsoft.com/en-us/ef/core/saving/concurrency
9. [Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

   AWS Prescriptive Guidance: dual writes, committed publication, and duplicate delivery.

   https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
10. [Java 25 compiler command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

    Oracle JDK 25 tool specification for javac and the --release option.

    https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html

DP · Lesson 6 · State · Java 25 guide
Offline HTML with print styling. No fonts, scripts, stylesheets, or images are loaded from the network.