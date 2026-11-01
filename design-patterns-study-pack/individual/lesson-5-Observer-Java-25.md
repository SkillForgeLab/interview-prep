[Skip to guide](#guide)

**DP** Design patterns · Lesson 5

First principles / Java 25Print / Save PDF

IN THIS GUIDE

1. [ADerive the need](#derive)
2. [BBuild the smallest useful Observer](#build)
3. [CTest responsibilities separately](#testing)
4. [DMake execution semantics explicit](#semantics)
5. [ECompare the neighboring patterns](#compare)
6. [FUnderstand the production boundary](#production)
7. [GDecide when the trade is worthwhile](#decide)
8. [HPractice, then change the question](#practice)
9. [IRunnable Java files](#runnable)
10. [ROfficial references](#references)

33 steps + exercise
2 complete Java programs
Works offline

Lesson 05 / Behavioral patternsJava 25 edition

05

# Observer

Decouple an event
from its consequences.

The component that detects a meaningful fact should not have to know every action that follows from it. Derive that boundary from a growing checkout flow, then make its execution contract explicit.

First-principles progressionStandard JavaLight themePrint ready

## The path through this lesson

**01 · Find the pressure**

Working checkout code accumulates knowledge of unrelated reactions.

**02 · Derive the mechanism**

A fact, an observer contract, and a publisher replace concrete recipient calls.

**03 · Examine the cost**

Failure, ordering, latency, and delivery remain design decisions.

Read in order to preserve the derivation. Prerequisites: Java interfaces, constructors, lambdas, collections, and exceptions. Records are introduced as they appear.

**PDF:** use Print / Save PDF, choose A4 or Letter, and disable the browser’s own headers and footers if you prefer the guide’s page footer. All lesson text and both source files are included in print; controls are hidden. No internet connection is needed to read or use the guide.

PART A

## Derive the need

Begin with working code. Let a changing requirement reveal the boundary.

01

## Start with the simplest checkout

A checkout first needs to charge for an order and save it. Keeping those two calls explicit is a reasonable starting point.

Java · excerptCopy

```
void checkout(Order order) {
    payment.charge(order);
    repository.save(order);
}
```

Then the requirements grow: send a confirmation, reserve inventory, award loyalty points, record analytics, and notify shipping. The obvious next step is to call each service:

Java · naive implementation, dependency fields omittedCopy

```
void checkout(Order order) {
    payment.charge(order);
    repository.save(order);
    email.sendConfirmation(order);
    inventory.reserve(order);
    loyalty.awardPoints(order);
    analytics.trackPurchase(order);
    shipping.createShipment(order);
}
```

This version is easy to follow. It also makes checkout responsible for knowing every downstream system.

**A business rule we must resolve**

Inventory and shipping appear here because they appeared in the original requirements. They are only candidates for independent notification. If stock must be secured before accepting an order, inventory belongs in the checkout workflow. We revisit this in steps 17–18.

02

## Name the real problem: knowledge coupling

The method’s length is a symptom. The design pressure is that checkout knows both **what happened** and **every consequence of what happened**.

Imagine marketing adds a recommendation engine. The payment and persistence steps are unchanged, yet checkout must be edited again. A reaction changed; the checkout algorithm did not.

**First-principles question**

Why should the component that completes an order have to name every component interested in that fact?

03

## Separate the stable fact from variable reactions

| Stable fact | Reactions that can vary |
| --- | --- |
| An order was placed. | Confirmation email, purchase analytics, loyalty updates, and future independent reactions. |

Instead of issuing every downstream instruction, checkout can announce **“An order was placed.”** Interested components register their own reactions.

This is the Observer idea: a subject maintains interested observers and notifies them when an event occurs. The subscriber count can be zero, one, or many. [[1]](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern "Microsoft Learn: Observer design pattern")

**What we have derived**

Keep the originating operation focused on producing a meaningful fact. Move knowledge of the interested parties into registration and notification.

PART B

## Build the smallest useful Observer

One event, one observer contract, and a publisher. Keep the mechanism visible.

04

## Model the event explicitly

Java · excerptCopy

```
import java.math.BigDecimal;

record Order(String id, String customerId, BigDecimal total) {}

record OrderPlaced(String orderId, String customerId,
                   BigDecimal total) {}
```

The order is input to checkout; `OrderPlaced` is a snapshot of a completed fact. The similar fields do not make the two types interchangeable in meaning.

| Event: a fact | Command: a requested action |
| --- | --- |
| `OrderPlaced` | `SendConfirmation` |
| `PaymentSucceeded` | `ChargePayment` |
| `UserRegistered` | `CreateContact` |

A Java record supplies a constructor, accessors such as `event.orderId()`, and value-based equality. Records are *shallowly* immutable: a record containing a mutable list would still need defensive copying. These examples use immutable value components. [[4]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html "Oracle Java 25: Record")

All core-example totals are USD. Use `new BigDecimal("125.00")` so the decimal value comes from text rather than a binary floating-point approximation. Add a currency to any multi-currency contract. [[5]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigDecimal.html "Oracle Java 25: BigDecimal")

05

## Define an observer

Java · excerptCopy

```
@FunctionalInterface
interface OrderPlacedObserver {
    void onOrderPlaced(OrderPlaced event);
}
```

An observer receives the fact and decides what to do. A named class makes a substantial reaction easy to find and test:

Java · excerptCopy

```
final class PurchaseAnalyticsHandler implements OrderPlacedObserver {
    @Override
    public void onOrderPlaced(OrderPlaced event) {
        System.out.println("Purchase USD " + event.total());
    }
}
```

Email, loyalty, and warehouse handlers can implement the same interface. A small handler can also be a lambda. The print statement above is a stand-in for an analytics client, not an integration.

**Java API choice**

We use our own small interface. Java’s `java.util.Observer` and `Observable` have been deprecated since Java 9; their event model is limited. The design pattern remains useful. [[3]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Observable.html "Oracle Java 25: Observable deprecation")

06

## Build the subject/provider

First separate the ability to publish from the ability to manage subscriptions. Checkout will only need the publishing side:

Java · excerptCopy

```
@FunctionalInterface
interface OrderEvents {
    void publish(OrderPlaced event);
}

@FunctionalInterface
interface Subscription extends AutoCloseable {
    @Override
    void close();
}
```

The publisher stores registrations, takes a snapshot, and calls each observer. This first version propagates a failure immediately.

Java · initial publisher; imports in the runnable appendixCopy

```
final class OrderPlacedPublisher implements OrderEvents {
    private static final class Registration {
        final OrderPlacedObserver observer;
        Registration(OrderPlacedObserver observer) {
            this.observer = observer;
        }
    }

    private final List<Registration> observers = new ArrayList<>();

    Subscription subscribe(OrderPlacedObserver observer) {
        var registration = new Registration(
                Objects.requireNonNull(observer));
        observers.add(registration);
        return () -> observers.remove(registration);
    }

    @Override
    public void publish(OrderPlaced event) {
        Objects.requireNonNull(event);
        for (var registration : List.copyOf(observers)) {
            registration.observer.onOrderPlaced(event);
        }
    }
}
```

`List.copyOf` makes a snapshot unaffected by later changes to the backing list. [[6]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection) "Oracle Java 25: List.copyOf") The registration object gives every call to `subscribe` its own identity, even if the same observer is registered twice.

| Contract in this guide | Meaning |
| --- | --- |
| Synchronous, single thread | The publishing thread runs each callback. Concurrent use is unsupported. |
| Snapshot per publish | A subscription change during a callback affects later dispatches. A removed observer may still run in the current snapshot. |
| Independent registrations | Subscribing twice means two notifications. Closing one handle removes only that registration. |
| Idempotent close | Closing the same handle twice has no additional effect. |
| Strong references | A long-lived publisher retains its observers until the subscriptions are closed. |

**A deliberate scope limit**

A snapshot protects this loop from same-thread subscription changes; it does not make the publisher thread-safe. Reentrant publication also runs immediately and can recurse. Add concurrency or queuing only when the required contract calls for it.

07

## Let checkout publish the fact

Java · excerptCopy

```
final class CheckoutService {
    private final PaymentGateway payment;
    private final OrderRepository repository;
    private final OrderEvents events;

    CheckoutService(PaymentGateway payment,
                    OrderRepository repository, OrderEvents events) {
        this.payment = payment;
        this.repository = repository;
        this.events = events;
    }

    void checkout(Order order) {
        payment.charge(order);
        repository.save(order);
        events.publish(new OrderPlaced(
                order.id(), order.customerId(), order.total()));
    }
}
```

Checkout names neither email nor analytics. It still depends on its payment and persistence contracts, the `OrderEvents` publishing contract, and the event’s meaning.

**Teaching contract**

For now, `save` returns after the order has been saved. A real repository may participate in an outer transaction whose commit happens later. Publishing after a method call is not automatically publishing after a commit. Step 26 addresses that boundary.

08

## Add a new reaction without editing checkout

Java · excerptCopy

```
final class WarehouseHandler implements OrderPlacedObserver {
    @Override
    public void onOrderPlaced(OrderPlaced event) {
        System.out.println("Warehouse received " + event.orderId());
    }
}

// At application assembly:
Subscription warehouse = publisher.subscribe(new WarehouseHandler());
```

The change is a new handler and a new registration. Checkout’s source code stays the same. The warehouse reaction must still fit the event contract and the business rules for independent work.

09

## Recognize the design principle

| Before | After |
| --- | --- |
| Checkout knows which services to call. | Checkout knows which fact to publish. |
| Adding a consequence edits checkout. | Adding a consequence edits composition and adds a handler. |
| The method shows all downstream actions. | Registration shows the set of downstream reactions. |

The publisher still knows observer *objects*, but through one small interface. The application’s composition code knows the concrete implementations. Knowledge has moved to a more appropriate place.

10

## Observer changes coupling; it does not erase it

Every handler now depends on the event’s fields and meaning. If `OrderPlaced` changes from “accepted order” to “unconfirmed attempt,” consumers can become wrong even if their code still compiles.

The synchronous implementation also couples checkout to observer latency and, with fail-fast dispatch, observer exceptions. Observer reduces direct knowledge of concrete recipients. It does not promise isolation in time, transactions, or failure.

**The contract is more than the record**

Document when an event becomes true, what each field means, and what delivery behavior callers can expect. A stable name is not enough.

11

## Register at the composition root

Assemble the object graph in application startup or another outer composition boundary. Do not construct and subscribe concrete observers inside `CheckoutService`.

Java · composition using the initial publisherCopy

```
var publisher = new OrderPlacedPublisher();
EmailClient email = (customer, order) ->
        System.out.println("Email " + customer + " for " + order);

try (var emailSubscription = publisher.subscribe(
            new EmailOrderConfirmation(email));
     var analyticsSubscription = publisher.subscribe(
            new PurchaseAnalyticsHandler())) {
    var checkout = new CheckoutService(payment, repository, publisher);
    checkout.checkout(order);
} // Subscriptions are closed when this scope ends.
```

Here the scope is one short demo. A server would keep registrations alive for its intended lifetime and close them at shutdown or when a subscriber is removed. Do not end the subscription scope before the events you need to observe.

The runnable appendix evolves the constructor to make failure policy explicit; the business service still accepts only `OrderEvents`.

PART C

## Test responsibilities separately

Checkout produces the event. Each observer translates it into one reaction.

12

## Test checkout through a recording publisher

A publishing interface lets the test record events without subclassing the concrete dispatcher or creating downstream services.

Java · dependency-free test excerptCopy

```
final class RecordingOrderEvents implements OrderEvents {
    final List<OrderPlaced> published = new ArrayList<>();

    @Override
    public void publish(OrderPlaced event) {
        published.add(event);
    }
}

var events = new RecordingOrderEvents();
var checkout = new CheckoutService(order -> {}, order -> {}, events);
var order = new Order("O123", "C42", new BigDecimal("125.00"));
checkout.checkout(order);

check(events.published.equals(List.of(new OrderPlaced(
        "O123", "C42", new BigDecimal("125.00")))), "Event payload");
```

`check` is a small helper that throws `AssertionError` on failure. Its definition and executable checks are in Appendix A; no test library or `-ea` flag is required.

Also verify the negative paths: a failed charge must prevent saving and publishing; a failed save must prevent publishing. These tests establish ordering inside checkout, not between independent observers.

13

## Test an observer in isolation

Java · excerptCopy

```
@FunctionalInterface
interface EmailClient {
    void sendConfirmation(String customerId, String orderId);
}

final class EmailOrderConfirmation implements OrderPlacedObserver {
    private final EmailClient email;

    EmailOrderConfirmation(EmailClient email) {
        this.email = Objects.requireNonNull(email);
    }

    @Override
    public void onOrderPlaced(OrderPlaced event) {
        email.sendConfirmation(event.customerId(), event.orderId());
    }
}
```

Java · observer testCopy

```
var sent = new ArrayList<String>();
EmailClient fake = (customer, order) -> sent.add(customer + ":" + order);
new EmailOrderConfirmation(fake).onOrderPlaced(
        new OrderPlaced("O123", "C42", new BigDecimal("125.00")));
check(sent.equals(List.of("C42:O123")), "Confirmation identifiers");
```

The observer depends on the `EmailClient` interface. The test supplies a fake; production composition supplies a real client. A test double should not become the production dependency type.

PART D

## Make execution semantics explicit

A notification loop is easy to write. Failure, ordering, and completion define what it actually means.

14

## What if an observer throws?

With the initial loop, email succeeds, loyalty throws, and later callbacks never run. The exception travels through `publish` into checkout.

| Observer | Result when loyalty throws |
| --- | --- |
| Email | Completed |
| Loyalty | Failed |
| Analytics | Not invoked |
| Shipping, if independent | Not invoked |

The important question is a business question: should one reaction prevent other reactions, and what should the originating caller be told?

15

## Option A: fail fast

Java · excerptCopy

```
for (var registration : List.copyOf(observers)) {
    registration.observer.onOrderPlaced(event);
}
```

This is the original implementation. A thrown exception stops dispatch and reaches the caller. Use it only when that is the intended contract.

**Fail fast is not rollback**

If payment was charged, the order was saved, and email then fails, throwing an exception does not undo the charge or the saved order. Reporting “checkout failed” may prompt a retry after the order already succeeded. Critical operations that define success need an explicit workflow and transaction or compensation design.

16

## Option B: isolate subscriber failures

Catch an expected application exception around each callback, record it, and continue. Make the policy visible rather than leaving it as an accidental consequence of a loop.

Java · evolved publisher; full definition in Appendix ACopy

```
enum FailurePolicy { FAIL_FAST, ISOLATE }

@Override
public void publish(OrderPlaced event) {
    Objects.requireNonNull(event);
    for (var registration : List.copyOf(observers)) {
        try {
            registration.observer.onOrderPlaced(event);
        } catch (RuntimeException failure) {
            if (policy == FailurePolicy.FAIL_FAST) {
                throw failure;
            }
            failures.record(new DeliveryFailure(
                    event, registration.observer, failure));
        }
    }
}
```

This example handles `RuntimeException`; it does not catch JVM `Error`s. The injected `FailureSink` must return normally. If that sink throws, this implementation stops too. The demo records failures in memory, which is useful for tests but provides no recovery after a crash.

**Continuing is not recovering.** The loyalty update remains undone. A real design must decide who retries it, how failure is surfaced, and whether durable storage is required.

TRY THE EXECUTION CONTRACT

### Where does dispatch stop?

These callbacks are deliberately registered as email, loyalty, then analytics to expose this implementation’s loop behavior.

Failure policyFail fastIsolate failuresObserver that throwsNoneEmailLoyaltyAnalytics

| Observer | Result |
| --- | --- |
| Email | Completed |
| Loyalty | Failed |
| Analytics | Not invoked |

Fail fast + loyalty failure: publish throws; analytics is not invoked.

Teaching simulation only. Isolation assumes the failure sink succeeds. Payment and persistence already completed in both cases.

| Policy, with loyalty failing | Email | Loyalty | Analytics | What publish does |
| --- | --- | --- | --- | --- |
| Fail fast | Completes | Throws | Not invoked | Throws |
| Isolate | Completes | Failure recorded | Completes | Returns if recording succeeds |

17

## Do not turn registration order into a business rule

Our list dispatches in registration order. That is an implementation fact, not a good basis for dependencies between independent observers. Microsoft’s Observer guidance likewise cautions against consumers relying on notification order. [[2]](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern-best-practices "Microsoft Learn: Observer best practices")

If shipping must wait for inventory reservation, two registrations are insufficient to express that rule. Someone can reorder, remove, or later parallelize the callbacks. Failure isolation could even run shipping after inventory failed.

**Ask the dependency question**

Does B merely care about the same event as A, or does B require A to have succeeded? The second case is a workflow.

18

## Distinguish consequences from prerequisites

| Business situation | Clearer design |
| --- | --- |
| Email and analytics independently react to an accepted order. | Independent observers. |
| Inventory must be reserved before accepting the order. | An explicit checkout step; do not announce acceptance before it succeeds. |
| Shipping requires confirmed reservation. | Orchestrate the dependency or react to a distinct `InventoryReserved` fact with an explicit workflow contract. |
| Payment authorization result determines whether checkout continues. | A direct call with a result, or an explicitly modeled asynchronous workflow. |

The original list of “after checkout” actions was not enough to prove independence. The business rules decide the boundary. Moving everything into observers would hide sequencing rather than solve it.

19

## Keep notification data separate and deliberate

Publishing the entire mutable order lets consumers depend on internal state and possibly change it. A dedicated snapshot limits that surface. Microsoft recommends a separate notification-data type for the same separation of responsibilities. [[2]](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern-best-practices "Microsoft Learn: Observer best practices")

Include what a legitimate consumer needs, and define whether it is a historical value or a reference to current data. A customer identifier may let an email adapter resolve a destination. It does not make the event sufficient for inventory quantities or a shipping address.

**Avoid an event that contains everything**

If a new consumer needs more data, decide deliberately whether to add a field, fetch related data through a contract, or use a different event. Be cautious with secrets and unnecessary personal data. Records do not validate or minimize payloads automatically.

PART E

## Compare the neighboring patterns

The shape of the code is less useful than the question the pattern answers.

20

## Observer versus a direct method call

A direct call makes the required behavior and result explicit. A notification announces a completed fact without requesting a result from each recipient.

Java · contrasting call sites; domain types are illustrativeCopy

```
// This result controls checkout: keep the dependency explicit.
Authorization authorization = payment.authorize(order);

// This announces a fact: interested observers may react.
events.publish(orderPlaced);
```

An event-driven request/reply workflow is possible, but it adds correlation and lifecycle rules. Do not introduce that machinery merely to hide a dependency you actually need.

21

## Observer versus Strategy

| Question | Strategy | Observer |
| --- | --- | --- |
| What varies? | The algorithm behind a capability. | The set of interested reactions. |
| Typical relationship | One selected implementation per call. | Zero or more registered observers per event. |
| Does the caller need a result? | Often yes. | No per-observer result in this design. |
| Example | Choose standard or express shipping. | Notify email, loyalty, and analytics of an order. |

22

## Observer versus Decorator

| Decorator | Observer |
| --- | --- |
| Each wrapper delegates along a composed path. | A publisher invokes multiple interested recipients. |
| Adds behavior around an existing capability while retaining its interface. | Adds reactions to a fact through a notification contract. |
| Logging wraps metrics, which wraps payment. | Email and analytics separately receive `OrderPlaced`. |

The two can coexist. An observer can itself be decorated with logging or metrics. Keep failure and timing behavior explicit at both boundaries.

23

## Observer versus Publish/Subscribe

The terminology overlaps. A useful distinction is where knowledge of subscribers lives and how delivery occurs.

| Mechanism | Where subscribers are tracked | What it guarantees by itself |
| --- | --- | --- |
| Classic object Observer | A subject holds observer references. | Only its documented callback contract. |
| In-process event bus | A shared dispatcher maps event types to handlers. | Only its documented routing and execution contract. |
| Broker-based pub/sub | Messaging infrastructure maintains subscriptions. | Delivery and durability depend on the broker and configuration. |

A broker-mediated pub/sub architecture lets the originating publisher send a message without knowing the consumers. That architecture often supports asynchronous delivery. An intermediary alone does not make our Java code asynchronous or durable. [[8]](https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber "Microsoft Azure Architecture Center: Publisher-Subscriber")

24

## Generalize only when multiple event types justify it

A dedicated publisher is enough for one event. If several event types genuinely need common routing, use a typed registration boundary rather than string names paired with unchecked handler casts.

Java · generic-bus variant; separate from the core demoCopy

```
interface DomainEvent {}
record OrderPlaced(String orderId, String customerId,
                   BigDecimal total) implements DomainEvent {}
record OrderCancelled(String orderId) implements DomainEvent {}
```

Java · EventBus nested in TypedEventBusDemoCopy

```
// Single-threaded. Exact runtime-class routing. Fail fast.
static final class EventBus {
    private static final class Registration {
        final Consumer<DomainEvent> invoke;

        Registration(Consumer<DomainEvent> invoke) {
            this.invoke = invoke;
        }
    }

    private final Map<Class<?>, List<Registration>> handlers =
            new HashMap<>();

    <E extends DomainEvent> Subscription subscribe(
            Class<E> type, Consumer<? super E> handler) {
        Objects.requireNonNull(type);
        Objects.requireNonNull(handler);
        var registration = new Registration(
                event -> handler.accept(type.cast(event)));
        handlers.computeIfAbsent(type, key -> new ArrayList<>())
                .add(registration);
        return () -> {
            var registrations = handlers.get(type);
            if (registrations != null) {
                registrations.remove(registration);
                if (registrations.isEmpty()) handlers.remove(type);
            }
        };
    }

    void publish(DomainEvent event) {
        Objects.requireNonNull(event);
        var registrations = handlers.get(event.getClass());
        if (registrations == null) return;
        for (var registration : List.copyOf(registrations)) {
            registration.invoke.accept(event);
        }
    }
}
```

Java · excerptCopy

```
var bus = new EventBus();
bus.subscribe(OrderPlaced.class,
        event -> System.out.println(event.orderId()));
bus.publish(new OrderPlaced("O123", "C42", new BigDecimal("125.00")));
```

`Class<E>` ties the registration key to the handler’s accepted type. `Class.cast` performs a checked cast at dispatch; there is no raw handler map or suppressed unchecked warning. [[7]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html#cast(java.lang.Object) "Oracle Java 25: Class.cast")

**Read the routing contract**

This bus matches the exact runtime class. A handler registered for `DomainEvent.class` does not receive every subtype. It is synchronous, single-threaded, snapshot-based, and fail fast. A network event schema needs a stable wire name and version; a Java class key is only a local routing choice.

PART F

## Understand the production boundary

Follow the same reasoning into latency, durability, and duplicate delivery.

25

## Synchronous notification versus asynchronous messaging

Our callbacks execute one after another before `publish` returns. If email takes 800 ms, analytics 300 ms, and loyalty 400 ms, successful notification adds about **1,500 ms**, plus dispatch overhead. These are illustrative timings, not measurements.

An asynchronous handoff separates acceptance of an event from completion of its reactions. The caller must understand what the handoff acknowledges. A thread pool can move work off the request thread, but an in-memory task can still disappear when the process dies.

For durable fan-out, each logical subscriber needs a way to receive its own copy or independently consume the event stream. A single competing-consumer queue does not automatically broadcast one message to every worker. [[8]](https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber "Microsoft Azure Architecture Center: Publisher-Subscriber")

| Move | New question |
| --- | --- |
| Callbacks on the request thread | How much latency and which exceptions reach checkout? |
| Background work in the same process | What happens on shutdown, overload, or a crash? |
| Durable messaging | What are the acceptance, retry, duplicate, ordering, and recovery contracts? |

Java’s `Flow` API is a separate reactive-streams abstraction with demand-based flow control. It is not a durable broker and is not required to derive Observer. [[11]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Flow.html "Oracle Java 25: Flow")

26

## Transaction boundaries create the dual-write problem

| Failure window | Consequence |
| --- | --- |
| Save commits; process crashes before publishing. | The order exists, but observers may never hear about it. |
| Publish occurs inside a transaction; commit later fails. | Observers may act on an order that was never committed. |

Writing state and notifying another system are separate operations. The **transactional outbox** addresses this boundary by storing the business change and the pending event in one database transaction. A relay later delivers committed outbox entries. [[9]](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html "AWS Prescriptive Guidance: Transactional outbox")

1. Within one database transaction, save the order and its outbox event.
2. Commit both records together.
3. Let a relay publish the stored event and track delivery progress.
4. Allow retry; design consumers to tolerate duplicates.

**The boundary matters**

An outbox does not put an external payment charge inside that database transaction. If a charge succeeds and saving fails, you still need a payment-specific recovery or compensation design. Observer alone solves neither atomicity problem.

Publishing after commit avoids announcing a rolled-back change, but without a durable handoff it still leaves a crash window. The lesson stops at deriving the need; neither Java demo implements a database, outbox, or broker.

27

## Duplicate delivery requires idempotent effects

If the same purchase event awards points twice, one order can produce two rewards. Retry must not mean an unintended additional business effect. At-least-once messaging can redeliver a message. [[8]](https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber "Microsoft Azure Architecture Center: Publisher-Subscriber")

The tempting “check, apply, mark” sequence has two gaps: simultaneous deliveries may both pass the check, and a crash after applying the effect may occur before marking it.

**For a database-local effect**

Use a unique key such as `(consumerName, eventId)`, and commit the deduplication record and the effect in the same transaction. A crash must not leave only one of them committed. For an external effect such as sending an email, use an appropriate downstream idempotency contract or another coordinated delivery design. [[12]](https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer "Microsoft Azure Architecture Center: Idempotent Consumer")

Preserve the same event ID when redelivering the same event. A new ID on every retry defeats event-ID deduplication. Different consumers need independent processing records; email having processed the event does not imply loyalty has processed it.

An in-memory `Set` can demonstrate the idea, but it does not survive restart and does not make an external side effect atomic.

28

## Evolve the event with deliberate metadata

Java · evolved event; Clock and Supplier are injectedCopy

```
record OrderPlacedV1(UUID eventId, Instant occurredAt,
                     String orderId, String customerId,
                     BigDecimal total, String currency)
        implements DomainEvent {
    String eventType() { return "order.placed.v1"; }
}

OrderPlacedV1 event = new OrderPlacedV1(
        ids.get(), clock.instant(), order.id(), order.customerId(),
        order.total(), "USD");
```

| Field | Purpose and limit |
| --- | --- |
| `eventId` | Identifies this event for tracing and deduplication; reuse it on redelivery. |
| `occurredAt` | Records the occurrence time. Timestamps alone do not guarantee a total order across producers. |
| `orderId` | Connects the event to its business entity; it is not the same as event identity. |
| `eventType` / version | Names the published contract. Schema evolution still requires compatibility rules. |
| `total` and `currency` | Make the monetary meaning explicit. |

Injecting `Clock` lets a test use `Clock.fixed`; injecting `Supplier<UUID>` makes IDs deterministic too. [[10]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html "Oracle Java 25: Clock") Appendix B includes a check for both.

This Java record is a data model, not a complete serialization specification. Choose an encoding and define field formats before sending it between services.

PART G

## Decide when the trade is worthwhile

Return to the design pressure before choosing the pattern.

29

## Account for hidden control flow

A direct sequence of calls shows its consequences in one place. `events.publish(orderPlaced)` requires the reader to find registrations and handlers.

| Benefit | Cost to manage |
| --- | --- |
| New reactions do not require editing checkout. | The complete behavior is spread across composition and handlers. |
| Observers can be tested independently. | Integration tests still need to verify actual wiring. |
| Concrete recipients are removed from the originating service. | Event meaning, delivery behavior, and failure policy remain shared contracts. |

Keep registrations easy to find, use meaningful handler names, and attach event IDs to diagnostics when the event model has them. More indirection is justified only when it helps manage real variation.

30

## Recognize a good fit

Observer is a strong candidate when one meaningful fact has several independent reactions and the originator should not know them individually.

| Fact | Potential independent reactions |
| --- | --- |
| `UserRegistered` | Welcome email, signup analytics, CRM synchronization. |
| `OrderPlaced` | Confirmation email, purchase analytics, loyalty update. |
| `DocumentUploaded` | Indexing and thumbnail generation, if each is allowed to proceed independently. |

“Potential” matters. If documents must pass a virus scan before indexing or becoming available, scanning is a gate in a workflow. Similar names and a shared trigger do not prove independence.

31

## Recognize a poor fit

* The caller immediately needs a result to decide its next step.
* A must succeed before B, and that sequence is a business rule.
* The operation requires one atomic result across the proposed reactions.
* There is one stable direct dependency and no real pressure to vary the recipients.

Use explicit orchestration when the workflow itself is the important rule. Events may still report progress or trigger later work, but they should not conceal required sequencing.

32

## Use the first-principles checklist

| Question | Answer that favors Observer |
| --- | --- |
| Did something meaningful happen that several parties care about? | Yes. |
| Can the reactions proceed independently? | Yes. |
| Does the originator need every reaction’s result immediately? | No. |
| Must the originator name each recipient? | No. |
| Can the event be represented as a stable, explicit fact? | Yes. |

Then specify the contract: sync or async, failure policy, subscription lifetime, concurrent access, and what successful publication means. The pattern name does not decide these for you.

**Keep this mental model**

A fact has occurred. Several independent components care. Announce the fact through a stable contract, and let registration determine who reacts.

33

## Connect the patterns learned so far

| Pattern | Question it answers | Checkout example |
| --- | --- | --- |
| Strategy | Which algorithm should execute? | Select standard or express shipping. |
| Factory | Who creates or selects an implementation? | Build a configured shipping policy. |
| Adapter | How do incompatible interfaces cooperate? | Expose a legacy carrier through `ShippingPolicy`. |
| Decorator | How do we layer optional behavior? | Wrap shipping with logging or metrics. |
| Observer | How do independent components react to a fact? | Publish `OrderPlaced` to interested observers. |

Each pattern responds to a different reason for change. Combining them is useful only when those distinct pressures exist.

PART H

## Practice, then change the question

Refactor registration. Then look ahead to behavior that depends on state.

## Exercise · refactor user registration

Start with this direct implementation:

Java · starting point; dependency fields omittedCopy

```
void register(User user) {
    repository.save(user);
    email.sendWelcome(user);
    analytics.trackSignup(user);
    crm.createContact(user);
}
```

Derive an event, a publishing interface, a dispatcher, and independent observers. You may use this small event as a starting hypothesis:

Java · excerptCopy

```
record UserRegistered(String userId) {}

@FunctionalInterface
interface RegistrationEvents {
    void publish(UserRegistered event);
}

@FunctionalInterface
interface UserRegisteredObserver {
    void onUserRegistered(UserRegistered event);
}
```

Decide whether `userId` is sufficient. If an observer must fetch more data, define how. Do not silently add the entire user object to the event.

### Acceptance criteria

1. `UserRegistrationService` refers to neither email, analytics, nor CRM.
2. Adding an independent reaction changes the handler and composition, not registration.
3. Each observer is testable with a fake dependency.
4. The event contains only justified data and has a documented meaning.
5. The failure policy is explicit and tested with a throwing observer.
6. No observer depends on another observer’s execution order.
7. A failed save produces no `UserRegistered` event.
8. Subscriptions have a defined owner and lifetime.

### Tests worth writing

* Successful save produces exactly the expected event.
* Failed save produces no event.
* Welcome email receives the correct identifier.
* A throwing observer has the documented effect on later callbacks.
* Closing a subscription stops later notifications.

Review notes · compare after attempting the exercise

Registration should save the user and publish `UserRegistered` through `RegistrationEvents`. Startup code wires the dispatcher to welcome email, analytics, and CRM handlers.

If the account remains valid when CRM is unavailable, fail-fast notification must not be presented as a rollback of registration. If CRM creation is a prerequisite for a usable account, model a registration workflow and its status explicitly.

There is no universal answer to “catch or propagate?” A good answer states what success means, what failures leave behind, and who performs recovery.

NEXT · LESSON 6

## State: legal behavior depends on current state

An order can be created, paid, packed, shipped, delivered, or cancelled. Conditions begin to appear everywhere:

Java · illustrative state checksCopy

```
if (order.status() == OrderStatus.PAID) { /* ... */ }
if (order.status() == OrderStatus.SHIPPED) { /* ... */ }
if (order.status() != OrderStatus.CANCELLED) { /* ... */ }
```

The new pressure is that **the object’s legal behavior changes with its current state**. We will derive the State pattern, explicit transitions, and invalid-state prevention from that problem.

APPENDICES

## Run the complete examples

Two independent files. Standard Java only. No framework, dependency manager, or preview features.

Save each source block using its indicated filename, or use the download buttons. The narrative snippets are successive design stages; the complete files are coherent programs you can compile and run.

Terminal · use a JDK 25 installationCopy

```
javac --release 25 -Xlint:unchecked -Werror Lesson5Demo.java TypedEventBusDemo.java
java Lesson5Demo
java TypedEventBusDemo
```

Alternatively, run either file directly with `java Lesson5Demo.java` or `java TypedEventBusDemo.java`. Each program runs its own checks. All console clients are demonstration fakes; they make no real payments or network calls.

Expected output · both programs, in the order aboveCopy

```
All Lesson 5 checks passed.
Charged O123
Saved O123
Email C42 for O123
Analytics USD 125.00
All typed event bus checks passed.
```

**Validation record**

Both complete programs passed their executable checks on OpenJDK 17.0.20. Their language constructs and referenced APIs are compatible with Java 25 and were checked against official Java 25 documentation. A Java 25 runtime was unavailable, and the browser security policy blocked previewing this local HTML file. Java 25 execution and browser print rendering were not directly tested.

## Appendix A · Observer and failure policies

Lesson5Demo.java · Complete source

Download Lesson5Demo.javaHide source

Java · Lesson5Demo.javaCopy

```
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class Lesson5Demo {
    // All totals in this teaching example are USD.
    record Order(String id, String customerId, BigDecimal total) {}
    record OrderPlaced(String orderId, String customerId,
                       BigDecimal total) {}

    @FunctionalInterface
    interface OrderPlacedObserver {
        void onOrderPlaced(OrderPlaced event);
    }

    @FunctionalInterface
    interface OrderEvents {
        void publish(OrderPlaced event);
    }

    @FunctionalInterface
    interface Subscription extends AutoCloseable {
        @Override
        void close();
    }

    enum FailurePolicy { FAIL_FAST, ISOLATE }

    record DeliveryFailure(OrderPlaced event,
                           OrderPlacedObserver observer,
                           RuntimeException cause) {}

    @FunctionalInterface
    interface FailureSink {
        // Contract: records the failure and returns normally.
        void record(DeliveryFailure failure);
    }

    // Single-threaded, synchronous, in-memory teaching publisher.
    static final class OrderPlacedPublisher implements OrderEvents {
        private static final class Registration {
            final OrderPlacedObserver observer;

            Registration(OrderPlacedObserver observer) {
                this.observer = observer;
            }
        }

        private final List<Registration> observers = new ArrayList<>();
        private final FailurePolicy policy;
        private final FailureSink failures;

        OrderPlacedPublisher(FailurePolicy policy, FailureSink failures) {
            this.policy = Objects.requireNonNull(policy);
            this.failures = Objects.requireNonNull(failures);
        }

        Subscription subscribe(OrderPlacedObserver observer) {
            var registration = new Registration(
                    Objects.requireNonNull(observer));
            observers.add(registration);
            return () -> observers.remove(registration);
        }

        @Override
        public void publish(OrderPlaced event) {
            Objects.requireNonNull(event);
            for (var registration : List.copyOf(observers)) {
                try {
                    registration.observer.onOrderPlaced(event);
                } catch (RuntimeException failure) {
                    if (policy == FailurePolicy.FAIL_FAST) {
                        throw failure;
                    }
                    failures.record(new DeliveryFailure(
                            event, registration.observer, failure));
                }
            }
        }
    }

    @FunctionalInterface
    interface PaymentGateway {
        void charge(Order order);
    }

    @FunctionalInterface
    interface OrderRepository {
        // Demo contract: returns after the order has been saved.
        void save(Order order);
    }

    static final class CheckoutService {
        private final PaymentGateway payment;
        private final OrderRepository repository;
        private final OrderEvents events;

        CheckoutService(PaymentGateway payment,
                        OrderRepository repository, OrderEvents events) {
            this.payment = Objects.requireNonNull(payment);
            this.repository = Objects.requireNonNull(repository);
            this.events = Objects.requireNonNull(events);
        }

        void checkout(Order order) {
            payment.charge(order);
            repository.save(order);
            events.publish(new OrderPlaced(
                    order.id(), order.customerId(), order.total()));
        }
    }

    @FunctionalInterface
    interface EmailClient {
        void sendConfirmation(String customerId, String orderId);
    }

    static final class EmailOrderConfirmation
            implements OrderPlacedObserver {
        private final EmailClient email;

        EmailOrderConfirmation(EmailClient email) {
            this.email = Objects.requireNonNull(email);
        }

        @Override
        public void onOrderPlaced(OrderPlaced event) {
            email.sendConfirmation(event.customerId(), event.orderId());
        }
    }

    static final class RecordingOrderEvents implements OrderEvents {
        final List<OrderPlaced> published = new ArrayList<>();

        @Override
        public void publish(OrderPlaced event) {
            published.add(event);
        }
    }

    static final class FakeEmailClient implements EmailClient {
        final List<String> confirmations = new ArrayList<>();

        @Override
        public void sendConfirmation(String customerId, String orderId) {
            confirmations.add(customerId + ":" + orderId);
        }
    }

    static final Order ORDER =
            new Order("O123", "C42", new BigDecimal("125.00"));
    static final OrderPlaced EVENT =
            new OrderPlaced(ORDER.id(), ORDER.customerId(), ORDER.total());

    static void check(boolean condition, String description) {
        if (!condition) throw new AssertionError(description);
    }

    static void expectFailure(Runnable action) {
        try {
            action.run();
        } catch (IllegalStateException expected) {
            return;
        }
        throw new AssertionError("Expected IllegalStateException");
    }

    static void testCheckout() {
        var events = new RecordingOrderEvents();
        var trace = new ArrayList<String>();
        var checkout = new CheckoutService(
                order -> trace.add("charged"),
                order -> trace.add("saved"),
                event -> {
                    trace.add("published");
                    events.publish(event);
                });
        checkout.checkout(ORDER);
        check(trace.equals(List.of("charged", "saved", "published")),
                "Checkout must charge and save before publishing");
        check(events.published.equals(List.of(EVENT)), "Event payload");

        events.published.clear();
        var failedSave = new CheckoutService(order -> {}, order -> {
            throw new IllegalStateException("Database unavailable");
        }, events);
        expectFailure(() -> failedSave.checkout(ORDER));
        check(events.published.isEmpty(), "No event after failed save");

        var saved = new ArrayList<Order>();
        var failedPayment = new CheckoutService(order -> {
            throw new IllegalStateException("Payment declined");
        }, saved::add, events);
        expectFailure(() -> failedPayment.checkout(ORDER));
        check(saved.isEmpty() && events.published.isEmpty(),
                "No save or event after failed charge");
    }

    static void testEmail() {
        var email = new FakeEmailClient();
        new EmailOrderConfirmation(email).onOrderPlaced(EVENT);
        check(email.confirmations.equals(List.of("C42:O123")),
                "Email observer receives the correct identifiers");
    }

    static void testFailurePolicies() {
        for (var policy : FailurePolicy.values()) {
            var failures = new ArrayList<DeliveryFailure>();
            var publisher = new OrderPlacedPublisher(policy, failures::add);
            var calls = new ArrayList<String>();
            publisher.subscribe(event -> calls.add("email"));
            publisher.subscribe(event -> {
                calls.add("loyalty");
                throw new IllegalStateException("Loyalty unavailable");
            });
            publisher.subscribe(event -> calls.add("analytics"));
            if (policy == FailurePolicy.FAIL_FAST) {
                expectFailure(() -> publisher.publish(EVENT));
                check(calls.equals(List.of("email", "loyalty")),
                        "Fail fast stops dispatch");
                check(failures.isEmpty(), "Failure propagates to caller");
            } else {
                publisher.publish(EVENT);
                check(calls.equals(List.of("email", "loyalty", "analytics")),
                        "Isolation continues dispatch");
                check(failures.size() == 1, "Failure is recorded");
                check(failures.get(0).event().equals(EVENT),
                        "Failure retains the event for diagnosis");
            }
        }
    }

    static void testSubscriptions() {
        var publisher = new OrderPlacedPublisher(
                FailurePolicy.FAIL_FAST, failure -> {});
        var calls = new ArrayList<String>();
        publisher.publish(EVENT); // Zero subscribers is valid.
        OrderPlacedObserver listener = event -> calls.add("called");
        var first = publisher.subscribe(listener);
        var second = publisher.subscribe(listener);
        first.close();
        first.close(); // Repeated close is harmless.
        publisher.publish(EVENT);
        check(calls.size() == 1, "Each registration has its own lifetime");
        second.close();
        publisher.publish(EVENT);
        check(calls.size() == 1, "Closed subscription receives no new events");

        var snapshotPublisher = new OrderPlacedPublisher(
                FailurePolicy.FAIL_FAST, failure -> {});
        Subscription[] later = new Subscription[1];
        snapshotPublisher.subscribe(event -> later[0].close());
        later[0] = snapshotPublisher.subscribe(event -> calls.add("snapshot"));
        snapshotPublisher.publish(EVENT);
        snapshotPublisher.publish(EVENT);
        check(calls.equals(List.of("called", "snapshot")),
                "Removal changes the next dispatch, not the current snapshot");
    }

    public static void main(String[] args) {
        testCheckout();
        testEmail();
        testFailurePolicies();
        testSubscriptions();
        System.out.println("All Lesson 5 checks passed.");

        var failures = new ArrayList<DeliveryFailure>();
        var publisher = new OrderPlacedPublisher(
                FailurePolicy.ISOLATE, failures::add);
        EmailClient email = (customer, order) ->
                System.out.println("Email " + customer + " for " + order);
        try (var emailSubscription = publisher.subscribe(
                    new EmailOrderConfirmation(email));
             var analyticsSubscription = publisher.subscribe(event ->
                    System.out.println("Analytics USD " + event.total()))) {
            var checkout = new CheckoutService(
                    order -> System.out.println("Charged " + order.id()),
                    order -> System.out.println("Saved " + order.id()),
                    publisher);
            checkout.checkout(ORDER);
        }
        check(failures.isEmpty(), "Demo observers should succeed");
    }
}
```

## Appendix B · Typed event bus and event metadata

TypedEventBusDemo.java · Complete source

Download TypedEventBusDemo.javaHide source

Java · TypedEventBusDemo.javaCopy

```
import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Supplier;

public class TypedEventBusDemo {
    interface DomainEvent {}

    record OrderPlaced(String orderId, String customerId,
                       BigDecimal total) implements DomainEvent {}
    record OrderCancelled(String orderId) implements DomainEvent {}

    @FunctionalInterface
    interface Subscription extends AutoCloseable {
        @Override
        void close();
    }

    // Single-threaded. Exact runtime-class routing. Fail fast.
    static final class EventBus {
        private static final class Registration {
            final Consumer<DomainEvent> invoke;

            Registration(Consumer<DomainEvent> invoke) {
                this.invoke = invoke;
            }
        }

        private final Map<Class<?>, List<Registration>> handlers =
                new HashMap<>();

        <E extends DomainEvent> Subscription subscribe(
                Class<E> type, Consumer<? super E> handler) {
            Objects.requireNonNull(type);
            Objects.requireNonNull(handler);
            var registration = new Registration(
                    event -> handler.accept(type.cast(event)));
            handlers.computeIfAbsent(type, key -> new ArrayList<>())
                    .add(registration);
            return () -> {
                var registrations = handlers.get(type);
                if (registrations != null) {
                    registrations.remove(registration);
                    if (registrations.isEmpty()) handlers.remove(type);
                }
            };
        }

        void publish(DomainEvent event) {
            Objects.requireNonNull(event);
            var registrations = handlers.get(event.getClass());
            if (registrations == null) return;
            for (var registration : List.copyOf(registrations)) {
                registration.invoke.accept(event);
            }
        }
    }

    // A separate evolution of the event, corresponding to section 28.
    record OrderPlacedV1(UUID eventId, Instant occurredAt,
                         String orderId, String customerId,
                         BigDecimal total, String currency)
            implements DomainEvent {
        String eventType() { return "order.placed.v1"; }
    }

    static OrderPlacedV1 newEvent(Clock clock, Supplier<UUID> ids) {
        return new OrderPlacedV1(ids.get(), clock.instant(),
                "O123", "C42", new BigDecimal("125.00"), "USD");
    }

    static void check(boolean condition, String description) {
        if (!condition) throw new AssertionError(description);
    }

    public static void main(String[] args) {
        var bus = new EventBus();
        var placed = new ArrayList<String>();
        var cancelled = new ArrayList<String>();
        var catchAll = new ArrayList<DomainEvent>();
        bus.subscribe(DomainEvent.class, catchAll::add);
        var placedSubscription = bus.subscribe(OrderPlaced.class,
                event -> placed.add(event.orderId()));
        bus.subscribe(OrderCancelled.class,
                event -> cancelled.add(event.orderId()));
        var event = new OrderPlaced("O123", "C42",
                new BigDecimal("125.00"));
        bus.publish(event);
        check(placed.equals(List.of("O123")), "Correct typed payload");
        check(cancelled.isEmpty(), "No unrelated handler invocation");
        check(catchAll.isEmpty(), "Routing is exact-class only");
        placedSubscription.close();
        placedSubscription.close();
        bus.publish(event);
        check(placed.size() == 1, "Unsubscribe is effective");
        bus.publish(new OrderCancelled("O124"));
        check(cancelled.equals(List.of("O124")), "Second event type");

        var instant = Instant.parse("2026-01-01T00:00:00Z");
        var id = UUID.fromString("00000000-0000-0000-0000-000000000001");
        var enriched = newEvent(Clock.fixed(instant, ZoneOffset.UTC), () -> id);
        check(enriched.eventId().equals(id), "Deterministic event identity");
        check(enriched.occurredAt().equals(instant), "Deterministic time");
        var enrichedEvents = new ArrayList<OrderPlacedV1>();
        bus.subscribe(OrderPlacedV1.class, enrichedEvents::add);
        bus.publish(enriched);
        check(enrichedEvents.equals(List.of(enriched)), "Enriched event");
        System.out.println("All typed event bus checks passed.");
    }
}
```

SOURCES

## Official references

Java details were checked against Oracle’s Java 25 API documentation. Pattern and messaging references below are official Microsoft and AWS documentation. The .NET references establish general Observer ideas; this guide defines its own Java callback contract rather than implementing .NET’s interfaces.

1. [Microsoft Learn: Observer design pattern](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern)https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern
2. [Microsoft Learn: Observer best practices](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern-best-practices)https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern-best-practices
3. [Oracle Java 25: Observable deprecation](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Observable.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Observable.html
4. [Oracle Java 25: Record](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html
5. [Oracle Java 25: BigDecimal](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigDecimal.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigDecimal.html
6. [Oracle Java 25: List.copyOf](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection))https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection)
7. [Oracle Java 25: Class.cast](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html#cast(java.lang.Object))https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html#cast(java.lang.Object)
8. [Microsoft Azure Architecture Center: Publisher-Subscriber](https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber)https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber
9. [AWS Prescriptive Guidance: Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
10. [Oracle Java 25: Clock](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html
11. [Oracle Java 25: Flow](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Flow.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Flow.html
12. [Microsoft Azure Architecture Center: Idempotent Consumer](https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer)https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer

Prepared 1 September 2026 from the supplied Lesson 5. The reasoning sequence, 33 steps, registration exercise, and transition to State are preserved. The Java edition adds typed publishing, explicit subscription ownership, deterministic checks, and clearer failure and transaction boundaries.

DP · Lesson 5 · ObserverJava 25-compatible edition · 1 September 2026