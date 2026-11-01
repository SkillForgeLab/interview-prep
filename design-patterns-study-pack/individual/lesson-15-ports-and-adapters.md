[Skip to the guide](#main)

DP / Design patterns
Lesson 15

### A · Derive the boundary

[01Start with a realistic bad design](#section-1)[02What happens when inputs change?](#section-2)[03What happens when outputs change?](#section-3)[04The architecture we are aiming for](#section-4)

### B · Build the core

[05First, model the use case](#section-5)[06Implement the application service](#section-6)[07Those dependencies are output ports](#section-7)[08Keep domain rules independent](#section-8)

### C · Add adapters

[09Build the first driving adapter: REST](#section-9)[10Why the controller is an adapter](#section-10)[11Add a CLI adapter](#section-11)[12Add a message consumer](#section-12)[13Implement the persistence adapter](#section-13)[14Implement the payment-provider boundary](#section-14)[15Implement the Kafka output adapter](#section-15)[16See the complete architecture](#section-16)

### D · Wire and verify

[17Give responsibilities a place in the codebase](#section-17)[18Separate compile-time dependencies from calls](#section-18)[19Runtime flow can go outward](#section-19)[20Assemble the object graph at the composition root](#section-20)[21Use lightweight adapters in tests](#section-21)[22Test the use case without the framework](#section-22)[23Test each adapter at its own boundary](#section-23)

### E · Sharpen the boundaries

[24Driving and driven are roles](#section-24)[25Time is an external dependency too](#section-25)[26Do not create a port for everything](#section-26)[27Make ports speak application language](#section-27)[28Keep vendor models outside the port](#section-28)[29Folders do not enforce architecture](#section-29)[30Choose framework separation deliberately](#section-30)[31Relate this to layered architecture](#section-31)[32Relate Hexagonal, Clean, and Onion](#section-32)

### F · Apply the reasoning

[33Connect the patterns already learned](#section-33)[34Use the first-principles design process](#section-34)

### Practice & reference

[RegisterCustomer exercise](#exercise)[Next: the Outbox problem](#next)[A · Runnable Java + tests](#appendix-a)[B · JDBC adapter + schema](#appendix-b)[Sources & validation](#sources)

Java 25-compatible code
Light theme · Offline document
[Back to top](#top)

Lesson 15 · Architecture from first principles

# Ports & AdaptersHexagonal Architecture

Derive an application boundary from one practical problem: paying an order should not tie your business rules to HTTP, SQL, a payment provider, or a message broker.

34 sections + exerciseJava 25-compatibleComplete offline demoPrint-ready A4

Start with coupled checkout code. Identify what must stay stable, give those interactions contracts, translate technology at the edges, then wire and test the result.

Download runnable JavaDownload JDBC adapter

To make a PDF: use your browser’s Print / Save as PDF, choose A4 and 100% scale, and turn off the browser’s default headers and footers. Navigation and copy controls are hidden in print; all lesson content and complete source remain.

**The idea to carry through the lesson**

Let the application express its operation and the capabilities it needs. Let adapters translate between those contracts and external technologies.

Cockburn’s original pattern emphasizes running and testing the application independently of its usual UI and database. [[1]](#source-1) This guide preserves the supplied lesson’s sequence and makes its runnable and conceptual examples explicit.

Contents · jump to a section

### A · Derive the boundary

[01Start with a realistic bad design](#section-1)[02What happens when inputs change?](#section-2)[03What happens when outputs change?](#section-3)[04The architecture we are aiming for](#section-4)

### B · Build the core

[05First, model the use case](#section-5)[06Implement the application service](#section-6)[07Those dependencies are output ports](#section-7)[08Keep domain rules independent](#section-8)

### C · Add adapters

[09Build the first driving adapter: REST](#section-9)[10Why the controller is an adapter](#section-10)[11Add a CLI adapter](#section-11)[12Add a message consumer](#section-12)[13Implement the persistence adapter](#section-13)[14Implement the payment-provider boundary](#section-14)[15Implement the Kafka output adapter](#section-15)[16See the complete architecture](#section-16)

### D · Wire and verify

[17Give responsibilities a place in the codebase](#section-17)[18Separate compile-time dependencies from calls](#section-18)[19Runtime flow can go outward](#section-19)[20Assemble the object graph at the composition root](#section-20)[21Use lightweight adapters in tests](#section-21)[22Test the use case without the framework](#section-22)[23Test each adapter at its own boundary](#section-23)

### E · Sharpen the boundaries

[24Driving and driven are roles](#section-24)[25Time is an external dependency too](#section-25)[26Do not create a port for everything](#section-26)[27Make ports speak application language](#section-27)[28Keep vendor models outside the port](#section-28)[29Folders do not enforce architecture](#section-29)[30Choose framework separation deliberately](#section-30)[31Relate this to layered architecture](#section-31)[32Relate Hexagonal, Clean, and Onion](#section-32)

### F · Apply the reasoning

[33Connect the patterns already learned](#section-33)[34Use the first-principles design process](#section-34)

### Practice & reference

[RegisterCustomer exercise](#exercise)[Next: the Outbox problem](#next)[A · Runnable Java + tests](#appendix-a)[B · JDBC adapter + schema](#appendix-b)[Sources & validation](#sources)

A · Derive the boundary

## 01Start with a realistic bad design

You need checkout. An HTTP endpoint loads a database row, charges a payment provider, changes the order, and publishes a message. One method now owns both the business operation and the details of every external system.

The starting problem · deliberately coupled design

```
// Design sketch, not vendor SDK code.
// All of these responsibilities live in one controller:
// 1. Parse an HTTP request.
// 2. Read an order with SQL.
// 3. Charge a payment provider.
// 4. Set the database status to PAID.
// 5. Publish a Kafka message.
// 6. Construct an HTTP response.
```

| What it knows | Why that creates pressure |
| --- | --- |
| HTTP and JSON | The workflow is tied to one entry mechanism. |
| SQL and table columns | Schema changes can reach the business operation. |
| Payment SDK and broker API | Vendor behavior and transport failures mix with policy. |
| Order rules and workflow | Rules become hard to test without the surrounding infrastructure. |

**First question**

Which parts describe paying an order, and which parts only describe the technology used to do it?

## 02What happens when inputs change?

Today a REST request starts checkout. Tomorrow a CLI, scheduled job, message consumer, or test must start the same operation. If the workflow lives in a controller, each caller must duplicate it or go through HTTP.

Name the operation independently: **PayOrder**. REST is one way to request it. Move the operation into a callable application boundary so each entry mechanism can translate into the same request.

| Incoming mechanism | Translation it should own |
| --- | --- |
| REST | Path, body, authentication context → application command |
| CLI | Arguments → application command |
| Message consumer | Message schema → application command |
| Test | Test inputs → application command |

## 03What happens when outputs change?

The use case needs to load an order, take payment, and announce success. PostgreSQL, a payment provider, and Kafka are possible implementations of those needs.

Ask what the application needs before asking which SDK method to call. A stable contract limits how far an infrastructure change spreads. It cannot make vendors with different business capabilities interchangeable for free.

| Side of the boundary | Who starts the interaction? | Example |
| --- | --- | --- |
| Driving / primary | An external caller starts an application operation. | HTTP endpoint calls PayOrder. |
| Driven / secondary | The application asks for an external capability. | PayOrder asks a gateway to charge. |

This vocabulary follows Cockburn’s original description. [[1]](#source-1)

## 04The architecture we are aiming for

Inside and outside · runtime collaboration

RESTCLIMessage consumerTest

↓ driving adapters translate

Application boundary**PayOrderUseCase**

PayOrderService ↓ Order rules

↓ application calls output contracts

OrderRepositoryPaymentGatewayEventPublisher

↓ driven adapters supply implementations

JDBC / PostgreSQLPayment providerKafka

**Source dependency rule:** adapters refer to core contracts; core code does not name concrete adapters. The arrows above describe calls at runtime. Sections 18–19 separate that flow from source-code dependencies.

The useful distinction is *inside versus outside*. Six sides have no special architectural meaning.

B · Build the core

## 05First, model the use case

The application exposes a capability: pay an order. A command carries the requested input; the input port describes the callable operation.

Java · teaching excerpt

```
record PayOrderCommand(String orderId) {
    PayOrderCommand {
        if (orderId == null || orderId.isBlank()) {
            throw new IllegalArgumentException("orderId must not be blank");
        }
    }
}

record PaymentResult(String paymentId) {}

interface PayOrderUseCase {
    PaymentResult handle(PayOrderCommand command);
}
```

Nothing here mentions HTTP, JSON, Spring, or Kafka. A port is the contract of a meaningful interaction. In Java, an interface is a convenient way to express it; a separate interface for every input method is not a requirement of the pattern.

The runnable version uses package-private types in one file. In a package-separated application, expose the types that adapters must access as public types in their own files.

## 06Implement the application service

The application service coordinates the use case. It loads the order, asks the domain whether payment is allowed, calls a payment capability, saves the new state, and publishes a fact.

Java · exact service from the runnable demo

```
final class PayOrderService implements PayOrderUseCase {
    private final OrderRepository orders;
    private final PaymentGateway payments;
    private final EventPublisher events;
    private final Clock clock;

    PayOrderService(OrderRepository orders, PaymentGateway payments,
                    EventPublisher events, Clock clock) {
        this.orders = Objects.requireNonNull(orders);
        this.payments = Objects.requireNonNull(payments);
        this.events = Objects.requireNonNull(events);
        this.clock = Objects.requireNonNull(clock);
    }

    @Override
    public PaymentResult handle(PayOrderCommand command) {
        Objects.requireNonNull(command);
        Order order = orders.findById(command.orderId())
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));
        order.requirePayable(); // Check BEFORE any external charge.
        PaymentReceipt receipt = payments.charge(new PaymentRequest(
                "pay-order:" + order.id(), order.customerId(), order.total()));
        Order paid = order.markPaid(receipt.paymentId());
        orders.save(paid);
        events.publish(new OrderPaid(paid.id(), receipt.paymentId(),
                Instant.now(clock)));
        return new PaymentResult(receipt.paymentId());
    }
}
```

**Why this order matters**

`requirePayable()` runs before the external charge. The original lesson checked state only while marking the order paid; that could charge an already-paid order before throwing.

Here, an order supports one payment and its amount does not change. That lets the demo derive a stable logical payment key from the order ID. Production retry and concurrency rules need a persisted payment-attempt model and reconciliation.

The four constructor dependencies are explicit. The three custom ports describe capabilities; `java.time.Clock` supplies the timestamp. We return to time in section 25.

**Scope of this implementation**

This is a synchronous teaching workflow. A stored paid order is rejected on a repeat call; the whole use case is **not** idempotent. A gateway key does not make saving state and publishing an event atomic.

## 07Those dependencies are output ports

Define the operations in application language. The repository says what is persisted, the gateway says what payment result is required, and the event port says what fact leaves the application.

Java · teaching excerpt

```
interface OrderRepository {
    Optional<Order> findById(String orderId);
    void save(Order order);
}

interface PaymentGateway {
    // Same key + same request must reuse a successful logical charge.
    // Decline or uncertain outcome: throw; never return a success receipt.
    PaymentReceipt charge(PaymentRequest request);
}

interface EventPublisher {
    // Narrow event contract for this lesson; not tied to a broker model.
    void publish(OrderPaid event);
}
```

Java · teaching excerpt

```
record PaymentRequest(
        String idempotencyKey, String customerId, Money amount) {}

record PaymentReceipt(String paymentId) {
    PaymentReceipt {
        if (paymentId == null || paymentId.isBlank()) {
            throw new IllegalArgumentException("paymentId must not be blank");
        }
    }
}

record OrderPaid(
        String orderId, String paymentId, Instant occurredAt) {}
```

| Contract | Meaning in this lesson |
| --- | --- |
| findById | Return an order or Optional.empty(); absence is explicit. |
| save | Store the supplied immutable order by ID; insert or replace in the demo. |
| charge | Return a confirmed success receipt; failures must not masquerade as success. |
| publish | Hand off an OrderPaid fact; this alone promises no cross-system transaction. |

The contracts belong near the application that needs them. This guide narrows `EventPublisher` to `OrderPaid`; a larger system can introduce a shared event abstraction when several event types require it.

## 08Keep domain rules independent

An order owns the rule that only a created order can be paid. The application invokes the rule; it does not reproduce it in every controller or consumer.

Java · teaching excerpt

```
enum OrderStatus { CREATED, PAID }

// Methods inside the complete Order record in Appendix A:
void requirePayable() {
    if (status != OrderStatus.CREATED) {
        throw new IllegalStateException("Only created orders can be paid");
    }
}

Order markPaid(String paymentId) {
    requirePayable();
    return new Order(id, customerId, total, OrderStatus.PAID, paymentId);
}
```

The demo uses an immutable `Order` record. `markPaid` returns a new value, so the repository changes only when `save` is called. A mutable entity is also valid; then test repositories must avoid accidentally persisting changes by sharing mutable references.

Java · teaching excerpt

```
record Money(long minorUnits, Currency currency) {
    Money {
        if (minorUnits <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        Objects.requireNonNull(currency, "currency");
    }
}
```

Use minor units with a currency, rather than a bare number named “cents” for every currency. This teaching domain accepts only positive payments. Java records provide data carriers; they do not make arbitrary referenced objects deeply immutable. [[3]](#source-3)

All components of this small order model are immutable. Domain code uses Java types and business concepts, with no framework or vendor imports.

C · Add adapters

## 09Build the first driving adapter: REST

The HTTP adapter translates a request into the input port and translates the result back to the protocol.

Spring MVC integration excerpt · separate CheckoutController.java

```
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public final class CheckoutController {
    private final PayOrderUseCase payOrder;

    public CheckoutController(PayOrderUseCase payOrder) {
        this.payOrder = payOrder;
    }

    @PostMapping("/orders/{orderId}/payment")
    public PaymentResponse pay(@PathVariable("orderId") String orderId) {
        var result = payOrder.handle(new PayOrderCommand(orderId));
        return new PaymentResponse(result.paymentId());
    }

    public record PaymentResponse(String paymentId) {}
}
```

`@PostMapping` maps the HTTP operation; the explicit path-variable name avoids depending on compiler parameter-name metadata. [[7]](#source-7) Authentication, authorization, transport validation, and HTTP error mapping also belong at an appropriate inbound boundary.

This excerpt requires Spring MVC and the application types. The embedded offline demo does not start a web server. Use a Java 25-compatible framework line; the verified Spring Boot system requirements include Java 25. [[8]](#source-8)

## 10Why the controller is an adapter

`PayOrderUseCase` expresses the application’s operation. `CheckoutController` connects HTTP to that operation.

| Concept | Question it answers | In this service |
| --- | --- | --- |
| Port | What interaction does the application support? | PayOrderUseCase |
| Adapter | How does this technology participate? | CheckoutController |
| Application service | How is the use case coordinated? | PayOrderService |
| Domain | Which business states and transitions are valid? | Order |

The controller can change its route, response DTO, or HTTP error format without changing the payment workflow. Keeping these roles distinct makes the boundary visible in code.

## 11Add a CLI adapter

A second entry point should reuse the same application operation. Only its translation changes.

Java · teaching excerpt

```
final class PayOrderCli {
    private final PayOrderUseCase payOrder;

    PayOrderCli(PayOrderUseCase payOrder) {
        this.payOrder = Objects.requireNonNull(payOrder);
    }

    void execute(String orderId) {
        var result = payOrder.handle(new PayOrderCommand(orderId));
        System.out.println("Payment: " + result.paymentId());
    }
}
```

The CLI owns argument handling and console output. The service does not know whether its caller is a terminal, controller, or test. The main method in section 20 invokes this adapter.

## 12Add a message consumer

A message-driven request can reach the same input port. This class shows the translation after a transport listener has deserialized a message.

Java · transport-neutral consumer translation

```
record PayOrderMessage(String orderId) {}

final class PayOrderConsumer {
    private final PayOrderUseCase payOrder;

    PayOrderConsumer(PayOrderUseCase payOrder) {
        this.payOrder = Objects.requireNonNull(payOrder);
    }

    void onMessage(PayOrderMessage message) {
        payOrder.handle(new PayOrderCommand(message.orderId()));
    }
}
```

A real Kafka listener wraps this translation with deserialization, acknowledgments, retry policy, and failed-message handling. Those policies must agree with the use case’s duplicate-request behavior. This demo rejects a repeated payment after the order is paid; a consumer cannot blindly retry every failure forever.

Kafka is driving in this role. The same technology is driven when the application publishes to it.

## 13Implement the persistence adapter

The core owns `OrderRepository`. A JDBC class implements it and maps database rows into domain values. SQL, connection handling, and mapping stay in that class.

Java · findById from complete JDBC adapter

```
@Override
    public Optional<Order> findById(String orderId) {
        String sql = """
                SELECT id, customer_id, total_minor, currency, status, payment_id
                FROM orders WHERE id = ?
                """;
        try (var connection = dataSource.getConnection()) {
            requireAutoCommit(connection.getAutoCommit());
            try (var statement = connection.prepareStatement(sql)) {
                statement.setString(1, orderId);
                try (var rows = statement.executeQuery()) {
                    if (!rows.next()) { return Optional.empty(); }
                    return Optional.of(new Order(
                            rows.getString("id"), rows.getString("customer_id"),
                            new Money(rows.getLong("total_minor"),
                                    Currency.getInstance(rows.getString("currency"))),
                            OrderStatus.valueOf(rows.getString("status")),
                            rows.getString("payment_id")));
                }
            }
        } catch (SQLException failure) {
            throw new IllegalStateException("Could not load order", failure);
        }
    }
```

The complete class, imports, save implementation, and schema are in [Appendix B](#appendix-b). It uses `DataSource`, prepared statements, and try-with-resources. [[5]](#source-5) [[6]](#source-6)

The repository returns `Optional.empty()` for a missing order and translates SQL failures into an application-visible runtime failure. A production design should define more precise failure types where callers need distinct recovery decisions.

**Transaction boundary is still missing**

This example explicitly requires an auto-commit connection for each operation. A read and a later write are separate transactions; there is no version check or protection against lost updates. Replacing the adapter does not solve concurrency.

## 14Implement the payment-provider boundary

The adapter converts the application’s `PaymentRequest` into the provider’s request and converts the provider’s result into `PaymentReceipt`. Provider models stay outside the port.

| Application concept | Stripe integration responsibility |
| --- | --- |
| Money | Map minor units and currency into the supported payment amount. |
| Application customer ID | Resolve the provider customer and payment-method references. |
| Logical payment key | Apply the provider request-idempotency mechanism. |
| Confirmed successful payment | Return PaymentReceipt only when the payment has succeeded. |
| Decline, pending state, required customer action | Represent these outcomes explicitly; do not mark the order paid. |

Stripe’s PaymentIntent has a lifecycle; initiating a request is not always equivalent to completing payment. A production design that allows pending payments or customer authentication needs richer outcomes and a completion flow, often driven by webhooks. [[9]](#source-9)

The original lesson’s `stripe.createCharge(...)` was a conceptual placeholder, not a complete SDK integration. This guide keeps that boundary explanation without inventing a vendor API. The runnable version uses a fully implemented fake.

Stripe documents request idempotency, including checks for changed parameters. Provider-specific retention and error behavior must be part of the real adapter’s contract. [[10]](#source-10)

## 15Implement the Kafka output adapter

Publishing is a different role from consuming. Here the application calls an output port, and a Kafka adapter creates the broker record.

Kafka integration excerpt · client library and encoder required

```
import java.util.concurrent.ExecutionException;
import java.util.function.Function;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

public final class KafkaEventPublisher implements EventPublisher {
    private final Producer<String, String> producer;
    private final Function<OrderPaid, String> encode;

    public KafkaEventPublisher(Producer<String, String> producer,
                               Function<OrderPaid, String> encode) {
        this.producer = producer;
        this.encode = encode;
    }

    @Override
    public void publish(OrderPaid event) {
        var record = new ProducerRecord<>(
                "order-paid", event.orderId(), encode.apply(event));
        try {
            producer.send(record).get();
        } catch (InterruptedException failure) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Publish interrupted", failure);
        } catch (ExecutionException failure) {
            throw new IllegalStateException("Publish failed", failure.getCause());
        }
    }
}
```

`send` returns a future; ignoring it can hide asynchronous delivery failure. This teaching adapter waits for completion according to producer configuration. [[11]](#source-11) It does not prove a consumer processed the message, and an interrupted wait does not prove the message was never sent.

The injected encoder owns the message schema and serialization. The composition root owns producer configuration and shutdown. A production publisher also needs bounded waiting and a deliberate failure policy. Waiting for Kafka still cannot atomically commit the database and the broker.

## 16See the complete architecture

Read the architecture by responsibility and ownership. Every concrete technology is attached at a boundary.

| Role | Core contract or policy | Outside implementation |
| --- | --- | --- |
| Incoming payment request | PayOrderUseCase | REST controller, CLI, message consumer |
| Use-case orchestration | PayOrderService | No transport required |
| Valid state transitions | Order | No storage required |
| Order persistence | OrderRepository | JDBC or in-memory repository |
| Taking payment | PaymentGateway | Provider adapter or fake |
| Announcing payment | EventPublisher | Kafka or recording publisher |
| Current time | java.time.Clock | System clock or fixed clock |

The domain is the set of business concepts and rules. The application coordinates those rules with external capabilities. Both sit inside the boundary; ports describe how that boundary can be crossed.

D · Wire and verify

## 17Give responsibilities a place in the codebase

A practical package layout follows those responsibilities. These paths describe the package-separated version; the downloadable teaching file deliberately keeps the types together.

| Package below com.example.orders | Representative types |
| --- | --- |
| `domain` | Order, OrderStatus, Money, OrderPaid |
| `application` | PayOrderCommand, PaymentResult, PayOrderUseCase, PayOrderService |
| `application.port.out` | OrderRepository, PaymentGateway, EventPublisher, payment request/receipt |
| `adapter.in.web` | CheckoutController |
| `adapter.in.cli` | PayOrderCli |
| `adapter.in.messaging` | PayOrderConsumer and wire-message DTO |
| `adapter.out.persistence` | JdbcOrderRepository |
| `adapter.out.payment` | Payment provider adapter |
| `adapter.out.messaging` | KafkaEventPublisher and encoder |
| `config` | ApplicationConfiguration or main composition root |

Package names help people navigate. Separate build modules or dependency checks can enforce boundaries more strongly. A folder name by itself cannot prevent an import in the wrong direction.

## 18Separate compile-time dependencies from calls

When compiling the core, the compiler should need the domain, application contracts, and permitted standard-library types. It should not need a controller, JDBC repository, or payment SDK.

| Source code | May name / depend on | Must not require in this design |
| --- | --- | --- |
| Domain | Domain types and Java standard types | Spring, SQL, Kafka, payment SDK |
| Application | Domain and output contracts | Concrete driven adapters |
| Driving adapters | Application input contract and transport types | Duplicated workflow or business rules |
| Driven adapters | Core output contract and external technology | Core code depending back on the adapter |
| Composition root | Core contracts and concrete implementations | Business rules hidden in wiring |

Microsoft’s architecture guidance distinguishes core dependencies from concrete implementations assembled at runtime. [[2]](#source-2)

## 19Runtime flow can go outward

At runtime, a service must eventually call an actual repository. That does not require its source code to name the JDBC class.

| View | Relationship | Meaning |
| --- | --- | --- |
| Runtime call | `PayOrderService → JdbcOrderRepository` | The injected object receives the call. |
| Service source | `PayOrderService → OrderRepository` | The service names the interface. |
| Adapter source | `JdbcOrderRepository → OrderRepository` | The adapter implements that interface. |

**Dependency inversion** makes the implementation depend on the core contract. **Dependency injection** supplies the chosen implementation to an object. Constructor injection alone does not invert a dependency: a constructor that asks for `JdbcOrderRepository` still depends directly on JDBC infrastructure.

## 20Assemble the object graph at the composition root

Some code must choose concrete implementations. Put that choice in the startup wiring, where the full object graph is assembled.

Plain Java · inside Lesson15.main

```
var orders = new InMemoryOrderRepository();
orders.save(Order.created("O-1", "C-1",
        new Money(5000, Currency.getInstance("USD"))));
var payments = new FakePaymentGateway();
var events = new RecordingEventPublisher();

PayOrderUseCase payOrder = new PayOrderService(
        orders, payments, events, Clock.systemUTC());
new PayOrderCli(payOrder).execute("O-1");
```

Production startup can substitute JDBC, a provider adapter, and Kafka at the same constructor. Their configuration, clients, credentials, and lifecycle stay in infrastructure and wiring.

Spring wiring excerpt · output-adapter beans configured separately

```
import java.time.Clock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration(proxyBeanMethods = false)
public class ApplicationConfiguration {
    @Bean
    Clock clock() { return Clock.systemUTC(); }

    @Bean
    PayOrderUseCase payOrderUseCase(OrderRepository orders,
                                  PaymentGateway payments,
                                  EventPublisher events,
                                  Clock clock) {
        return new PayOrderService(orders, payments, events, clock);
    }
}
```

Spring can construct and supply the beans. The service itself needs no annotation. `@Bean` is container configuration, not the architecture. [[12]](#source-12)

## 21Use lightweight adapters in tests

Keep real domain values and replace external boundaries. The in-memory repository stores immutable order values; the recording publisher captures emitted facts.

Java · teaching excerpt

```
final class InMemoryOrderRepository implements OrderRepository {
    private final Map<String, Order> data = new HashMap<>();
    private int writes;

    public Optional<Order> findById(String orderId) {
        return Optional.ofNullable(data.get(orderId));
    }

    public void save(Order order) {
        data.put(order.id(), order); // Immutable Order: no aliasing mutation.
        writes++;
    }

    int writes() { return writes; }
}
```

Java · teaching excerpt

```
final class RecordingEventPublisher implements EventPublisher {
    private final List<OrderPaid> recorded = new ArrayList<>();

    public void publish(OrderPaid event) { recorded.add(event); }
    List<OrderPaid> events() { return List.copyOf(recorded); }
}
```

The complete `FakePaymentGateway` in Appendix A records successful requests by logical key. Repeating the same request returns the same receipt; changing the request under the same key fails. This models the contract we want to test, not every behavior of a payment provider.

These fakes are intentionally single-threaded. They do not stand in for database isolation, broker delivery, or a provider sandbox.

## 22Test the use case without the framework

The core test provides an order, a gateway, an event recorder, and a fixed clock. It asserts the result, persisted state, charge count, and complete event payload.

Java · complete test method; helpers appear in Appendix A

```
private static void paysOrder() {
        var orders = seeded();
        var payments = new FakePaymentGateway();
        var events = new RecordingEventPublisher();
        var app = new PayOrderService(orders, payments, events, CLOCK);
        var result = app.handle(new PayOrderCommand("O-1"));
        check(result.paymentId().equals("PAY-1"), "receipt");
        check(orders.findById("O-1").orElseThrow().status()
                == OrderStatus.PAID, "saved state");
        check(orders.writes() == 2, "seed plus explicit save");
        check(payments.charges() == 1, "one charge");
        check(events.events().equals(List.of(
                new OrderPaid("O-1", "PAY-1", NOW))), "event payload and time");
    }
```

| Check included in the demo | What it protects or reveals |
| --- | --- |
| Successful payment | One charge, explicit save, expected event and timestamp. |
| Second payment request | A paid order is rejected before another charge. |
| Missing order | No payment, write, or event occurs. |
| Payment failure | No save or event follows a failed payment call. |
| Unsaved immutable result | An in-memory repository cannot hide a missing save. |
| Gateway key reuse | Same request reuses the receipt; changed parameters fail. |
| Publisher failure | The order stays paid, exposing the unresolved dual write. |

The demo uses small checks that throw `AssertionError`; it needs no JUnit library and no `-ea` option. This keeps the architectural test runnable with only a JDK.

## 23Test each adapter at its own boundary

Passing a use-case test does not verify SQL, HTTP mapping, serialization, or external API semantics. Those belong in separate tests.

| Test boundary | Evidence to collect |
| --- | --- |
| REST adapter | Request mapping, command construction, validation, authorization and error responses. |
| JDBC adapter | Round-trip mapping, missing rows, constraints, upserts, connection cleanup and real transaction behavior. |
| Payment adapter | Request translation, successful and pending outcomes, declines, timeouts and idempotency behavior. |
| Kafka adapter | Topic, key, schema, producer failures and acknowledgement policy. |
| Composition | The real object graph starts with the intended implementations. |

Use a real test database where database semantics are the subject of the test, and provider test facilities or a protocol stub for external integrations. Keep this evidence separate from the fast application tests.

E · Sharpen the boundaries

## 24Driving and driven are roles

Ask who starts the application interaction. The technology name alone does not answer that question.

| Adapter | Role | Why |
| --- | --- | --- |
| REST controller | Driving | It requests PayOrder. |
| CLI / scheduled trigger | Driving | It initiates an application operation. |
| Kafka consumer | Driving | An incoming message requests work. |
| JDBC repository | Driven | The use case asks it to load or save. |
| Payment adapter | Driven | The use case asks it to take payment. |
| Kafka publisher | Driven | The use case asks it to publish a fact. |
| Test calling the input port | Driving | It initiates a scenario. |
| Recording fake | Driven | It responds to the application. |

## 25Time is an external dependency too

A direct call to `Instant.now()` uses the system clock. Injecting the source of time lets a test choose an exact instant.

Java · statements inside a method

```
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

Clock production = Clock.systemUTC();
Clock test = Clock.fixed(
        Instant.parse("2026-08-28T12:00:00Z"), ZoneOffset.UTC);

Instant observed = Instant.now(test);
```

Java already provides the `Clock` abstraction and system/fixed implementations. Its documentation explicitly supports substituting clocks for testing. [[4]](#source-4)

You can treat it as the boundary to time without defining a custom `Clock` interface with the same name. A custom port becomes useful if the application needs a different business concept, such as a trading calendar or a business-day cutoff.

## 26Do not create a port for everything

A port should isolate a meaningful interaction or a source of variation. Adding an interface around every class or standard collection increases indirection without necessarily creating a useful boundary.

| Candidate | Decision question |
| --- | --- |
| PaymentGateway / OrderRepository | Is this an external capability the application must control? Usually yes. |
| Clock or randomness | Does nondeterminism affect a rule or test? Then make it controllable. |
| String formatting / basic arithmetic | Is there actual policy or external variation? Often a plain function is enough. |
| UUID generator | Does identity assignment require deterministic tests or a specific policy? Decide from that need. |
| JSON / logging | Keep transport encoding outside; add a core abstraction only for a meaningful application need. |

“Interface for every class” and “never abstract this utility” are both poor defaults. Start with the dependency that needs a boundary.

## 27Make ports speak application language

A technology-shaped interface can preserve the very coupling it was meant to remove.

| Leaky contract | Application-shaped contract | What changes |
| --- | --- | --- |
| `ResultSet executeSql(String query)` | `Optional<Order> findById(String id)` | The core asks for an order rather than building SQL. |
| `HttpResponse post(String path, JsonNode body)` | `PaymentReceipt charge(PaymentRequest request)` | The core asks for a payment rather than describing HTTP. |
| `send(ProducerRecord record)` | `publish(OrderPaid event)` | The core announces a fact rather than constructing broker records. |

A port should also define the semantics that matter: absence, failures, ordering, duplicate handling, and what successful return means. A domain-sounding method name is only the beginning of a useful contract.

## 28Keep vendor models outside the port

If `PaymentGateway` accepts a provider request class and returns a provider charge class, the application still needs the provider SDK to compile.

Contract comparison · vendor names are conceptual examples

```
// Vendor-shaped: still couples the core to the SDK.
// StripeCharge charge(StripeChargeRequest request);

// Application-shaped: adapter owns the conversion.
interface PaymentGateway {
    PaymentReceipt charge(PaymentRequest request);
}
```

Translation is work, but it is localized work. Put SDK objects, provider error codes, broker envelopes, ORM proxies, and transport serialization inside adapters. Expose only the business meaning that the application actually needs.

## 29Folders do not enforce architecture

A `domain` directory can still import a payment SDK. An `application` directory can still construct `JdbcOrderRepository`. Naming does not change the dependency graph.

* Inspect imports across the boundary.
* Look for service locators, globals, and concrete adapter construction in core classes.
* Compile a separated core module without infrastructure libraries.
* Run its use-case tests with in-memory or recording adapters.

Our single-file demo demonstrates responsibilities and substitutions. It does not demonstrate build-module enforcement; split it using section 17 when that enforcement is needed.

## 30Choose framework separation deliberately

A framework-free core is a design choice with benefits and costs. It helps when rules are substantial, several entry points share behavior, or external integrations change independently. Mapping separate persistence and domain models also takes effort.

A small CRUD application may reasonably keep persistence annotations on an entity. That choice accepts a framework dependency; it does not make the code automatically bad. Evaluate the cost of mapping against the isolation your application needs.

**Keep the goal concrete**

Ask whether the separation improves testability, rule clarity, independent change, or replacement of external systems. Architectural purity is not a substitute for those outcomes.

## 31Relate this to layered architecture

Controller, service, repository, and database can remain useful layers. The key question is what the service depends on.

| Organization | Dependency question |
| --- | --- |
| Service directly names a JDBC implementation | Business orchestration is coupled to that persistence mechanism. |
| Service names a core-owned repository contract | Infrastructure supplies an implementation at runtime. |
| Several driving and driven adapters surround a core | Different protocols can share the same operation and capabilities. |

A layered implementation can also follow ports and adapters. These descriptions emphasize different aspects: layering groups responsibilities; ports and adapters emphasizes the application boundary and the direction of dependencies across it.

## 32Relate Hexagonal, Clean, and Onion

These names describe related architectural approaches, not one identical specification. Their common ground is protecting business/application policy from direct dependencies on infrastructure mechanisms.

| Name | Useful emphasis |
| --- | --- |
| Ports & Adapters / Hexagonal | Purposeful boundary interactions and replaceable adapters. |
| Clean Architecture | A dependency rule that points toward inner policy. |
| Onion Architecture | An inner model surrounded by services and outer infrastructure. |

Microsoft discusses these approaches together around an application core and inward dependencies. [[2]](#source-2) For this lesson, evaluate the concrete boundary rather than arguing about which folder layout earns a label.

F · Apply the reasoning

## 33Connect the patterns already learned

Patterns now work together inside a service. Each has a specific job; none replaces the others.

| Pattern or technique | Role here |
| --- | --- |
| Command | PayOrderCommand represents the requested operation. |
| Application service / handler | PayOrderService coordinates the workflow. |
| Repository | OrderRepository expresses persistence needs. |
| Adapter | Translate between the core contract and an external technology. |
| Dependency inversion | Make implementation code depend on core-owned contracts. |
| Dependency injection | Supply collaborators through construction. |
| Factory | Choose or create concrete implementations during composition. |
| Decorator / Proxy | Wrap a port for suitable concerns such as observation or caching. |
| Strategy | Substitute a meaningful policy or algorithm. |
| State | Model lifecycle behavior; an enum alone is not the full State pattern. |
| Observer / events | Notify interested code; broker delivery adds distributed failure semantics. |

Decorators must preserve the contract. For example, retrying a payment call or caching a mutable order is not a harmless wrapper unless duplicate handling and consistency are defined.

## 34Use the first-principles design process

1. **Name the operation.** What does the application let a caller do?
2. **Put rules in the domain.** Which conditions make that operation valid?
3. **Identify external capabilities.** What must the application ask the outside world to provide?
4. **Define meaningful contracts.** Use application language, including success, absence, and failure semantics.
5. **Translate at the edges.** Let each input or output adapter own its technology.
6. **Compose from the outside.** Choose implementations at startup and inject them.
7. **Verify each boundary.** Test the use case in isolation; test actual integrations separately.

**The central question**

**Which layer should own this dependency?** If the application must import an SDK just to express its business operation, revisit the boundary.

Exercise · build the whole service

## RegisterCustomer

Create one application operation that can be requested from REST or a CLI. It creates a customer, saves the customer, sends a welcome email, and publishes `CustomerRegistered`.

Exercise contract · define the command and ID types

```
public interface RegisterCustomerUseCase {
    CustomerId register(RegisterCustomerCommand command);
}
```

| Dependency | Purpose | Test substitute |
| --- | --- | --- |
| CustomerRepository | Persist and retrieve customers. | In-memory repository |
| WelcomeEmailSender | Send the application’s welcome message. | Recording email sender |
| EventPublisher | Publish CustomerRegistered in application language. | Recording publisher |
| java.time.Clock | Provide the registration timestamp. | Clock.fixed(...) |

First define the business rules: required fields, identity assignment, duplicate registration behavior, and what “registered” means if email delivery fails. State those decisions before choosing SMTP or a broker.

### Acceptance criteria

[ ] Domain/application code imports no JDBC, HTTP, SMTP, Kafka, or vendor SDK classes.[ ] REST and CLI call the same RegisterCustomerUseCase.[ ] An in-memory repository replaces PostgreSQL for application tests.[ ] A recording fake replaces the welcome-email adapter.[ ] Broker envelope and schema classes do not leak into the application.[ ] Adapters translate external representations into core representations.[ ] The composition root chooses and wires concrete implementations.[ ] The main use-case test runs without Spring or external services.[ ] Explain which adapters are driving and which are driven.[ ] Explain why CustomerRepository is a port and JdbcCustomerRepository is an adapter.

0 of 10 criteria checked. This checklist resets when the page reloads.

### Test beyond the successful path

Use a fixed clock and assert the event timestamp. Verify that a persistence failure prevents later calls. Then make email or publishing fail *after* saving and describe the resulting inconsistent state. Do not hide that behavior with a catch block that reports success.

Next · transactions and the Outbox problem

## The boundary is clean. The workflow can still fail.

Failure scenario · conceptual excerpt

```
customers.save(customer);
welcomeEmailSender.send(customer);
events.publish(new CustomerRegistered(/* application data */));
```

| Failure window | Possible result |
| --- | --- |
| Database commits; process stops before publishing. | Customer exists, but no event reaches downstream systems. |
| Event is published; database transaction later rolls back. | Consumers see a fact that was never committed. |
| Payment succeeds; saving the order fails. | The provider has a payment, but local state does not reflect it. |
| Message is delivered again after an uncertain acknowledgement. | A consumer may repeat an effect unless it detects duplicates. |

A transactional outbox writes the business change and an outgoing event record in the **same local database transaction**. A relay later publishes committed records. A relay can publish more than once, so consumers must tolerate duplicates. [[13]](#source-13)

The outbox does not make a remote payment or email call part of that database transaction. Those effects need their own durable workflow, idempotency, and recovery decisions.

**Next derivation:** transaction boundary → transactional outbox → relay → delivery retries → idempotent consumers. The final demo test deliberately exposes the problem that this next lesson must solve.

Appendix A · complete offline program

## Run it with only a JDK

Save the source as `Lesson15.java`. All domain, application, adapter, and test types are included. Only `Lesson15` is public, which permits this single-file layout. No preview features or external dependencies are used.

Download Lesson15.java

Commands · use a JDK 25 javac and java

```
javac --release 25 -d out Lesson15.java
java -cp out Lesson15
java -cp out Lesson15 test
```

Output · first the demo, then the test command

```
Payment: PAY-1
Status: PAID
Events: 1

7 checks passed
```

**Validation record**

**Java 25 compatibility:** uses standard features and APIs documented in Java 25, with no preview feature. **Executed here:** compiled with `--release 17` on OpenJDK 17.0.20; the demo and all seven checks passed. **⚠️ Limit:** a Java 25 runtime was unavailable, so execution on Java 25 was not directly verified. The commands above are the intended Java 25 check.

Compiler options and Java 25 API references: [[14]](#source-14) [[3]](#source-3) [[4]](#source-4)

Lesson15.java · complete source

```
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Currency;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

// Lesson 15: single-file teaching version. No preview features or libraries.
// Domain, application, and adapters share a file only to simplify running it.
public final class Lesson15 {
    public static void main(String[] args) {
        if (args.length == 1 && args[0].equals("test")) {
            Lesson15Tests.run();
            return;
        }
        var orders = new InMemoryOrderRepository();
        orders.save(Order.created("O-1", "C-1",
                new Money(5000, Currency.getInstance("USD"))));
        var payments = new FakePaymentGateway();
        var events = new RecordingEventPublisher();
        PayOrderUseCase payOrder = new PayOrderService(
                orders, payments, events, Clock.systemUTC());
        new PayOrderCli(payOrder).execute("O-1");
        System.out.println("Status: "
                + orders.findById("O-1").orElseThrow().status());
        System.out.println("Events: " + events.events().size());
    }
}

// DOMAIN: data and invariants, with no persistence or protocol code.
record Money(long minorUnits, Currency currency) {
    Money {
        if (minorUnits <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        Objects.requireNonNull(currency, "currency");
    }
}

enum OrderStatus { CREATED, PAID }

record Order(String id, String customerId, Money total,
             OrderStatus status, String paymentId) {
    Order {
        requireText(id, "id");
        requireText(customerId, "customerId");
        Objects.requireNonNull(total, "total");
        Objects.requireNonNull(status, "status");
        if (status == OrderStatus.CREATED && paymentId != null) {
            throw new IllegalArgumentException("Created order has no payment");
        }
        if (status == OrderStatus.PAID) {
            requireText(paymentId, "paymentId");
        }
    }

    static Order created(String id, String customerId, Money total) {
        return new Order(id, customerId, total, OrderStatus.CREATED, null);
    }

    void requirePayable() {
        if (status != OrderStatus.CREATED) {
            throw new IllegalStateException("Only created orders can be paid");
        }
    }

    Order markPaid(String paymentId) {
        requirePayable();
        return new Order(id, customerId, total, OrderStatus.PAID, paymentId);
    }

    private static void requireText(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank");
        }
    }
}

record OrderPaid(String orderId, String paymentId, Instant occurredAt) {}

// APPLICATION: the input contract and the output contracts it needs.
record PayOrderCommand(String orderId) {
    PayOrderCommand {
        if (orderId == null || orderId.isBlank()) {
            throw new IllegalArgumentException("orderId must not be blank");
        }
    }
}

record PaymentResult(String paymentId) {}
record PaymentRequest(String idempotencyKey, String customerId, Money amount) {}
record PaymentReceipt(String paymentId) {
    PaymentReceipt {
        if (paymentId == null || paymentId.isBlank()) {
            throw new IllegalArgumentException("paymentId must not be blank");
        }
    }
}

interface PayOrderUseCase {
    PaymentResult handle(PayOrderCommand command);
}

interface OrderRepository {
    Optional<Order> findById(String orderId);
    void save(Order order);
}

interface PaymentGateway {
    // Same key + same request must reuse a successful logical charge.
    // Decline or uncertain outcome: throw; never return a success receipt.
    PaymentReceipt charge(PaymentRequest request);
}

interface EventPublisher {
    // Narrow event contract for this lesson; not tied to a broker model.
    void publish(OrderPaid event);
}

final class PayOrderService implements PayOrderUseCase {
    private final OrderRepository orders;
    private final PaymentGateway payments;
    private final EventPublisher events;
    private final Clock clock;

    PayOrderService(OrderRepository orders, PaymentGateway payments,
                    EventPublisher events, Clock clock) {
        this.orders = Objects.requireNonNull(orders);
        this.payments = Objects.requireNonNull(payments);
        this.events = Objects.requireNonNull(events);
        this.clock = Objects.requireNonNull(clock);
    }

    @Override
    public PaymentResult handle(PayOrderCommand command) {
        Objects.requireNonNull(command);
        Order order = orders.findById(command.orderId())
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));
        order.requirePayable(); // Check BEFORE any external charge.
        PaymentReceipt receipt = payments.charge(new PaymentRequest(
                "pay-order:" + order.id(), order.customerId(), order.total()));
        Order paid = order.markPaid(receipt.paymentId());
        orders.save(paid);
        events.publish(new OrderPaid(paid.id(), receipt.paymentId(),
                Instant.now(clock)));
        return new PaymentResult(receipt.paymentId());
    }
}

// DRIVING ADAPTERS: initiate a use case.
final class PayOrderCli {
    private final PayOrderUseCase payOrder;

    PayOrderCli(PayOrderUseCase payOrder) {
        this.payOrder = Objects.requireNonNull(payOrder);
    }

    void execute(String orderId) {
        var result = payOrder.handle(new PayOrderCommand(orderId));
        System.out.println("Payment: " + result.paymentId());
    }
}

record PayOrderMessage(String orderId) {}

final class PayOrderConsumer {
    private final PayOrderUseCase payOrder;

    PayOrderConsumer(PayOrderUseCase payOrder) {
        this.payOrder = Objects.requireNonNull(payOrder);
    }

    void onMessage(PayOrderMessage message) {
        payOrder.handle(new PayOrderCommand(message.orderId()));
    }
}

// DRIVEN TEST ADAPTERS: single-threaded, in-memory teaching substitutes.
final class InMemoryOrderRepository implements OrderRepository {
    private final Map<String, Order> data = new HashMap<>();
    private int writes;

    public Optional<Order> findById(String orderId) {
        return Optional.ofNullable(data.get(orderId));
    }

    public void save(Order order) {
        data.put(order.id(), order); // Immutable Order: no aliasing mutation.
        writes++;
    }

    int writes() { return writes; }
}

final class FakePaymentGateway implements PaymentGateway {
    private final Map<String, PaymentRequest> requests = new HashMap<>();
    private final Map<String, PaymentReceipt> receipts = new HashMap<>();
    private int charges;

    public PaymentReceipt charge(PaymentRequest request) {
        String key = request.idempotencyKey();
        if (receipts.containsKey(key)) {
            if (!requests.get(key).equals(request)) {
                throw new IllegalArgumentException("Key reused for changed request");
            }
            return receipts.get(key);
        }
        var receipt = new PaymentReceipt("PAY-" + ++charges);
        requests.put(key, request);
        receipts.put(key, receipt);
        return receipt;
    }

    int charges() { return charges; }
}

final class RecordingEventPublisher implements EventPublisher {
    private final List<OrderPaid> recorded = new ArrayList<>();

    public void publish(OrderPaid event) { recorded.add(event); }
    List<OrderPaid> events() { return List.copyOf(recorded); }
}

// TESTS: use real domain values; replace only boundary dependencies.
final class Lesson15Tests {
    private static final Instant NOW = Instant.parse("2026-08-28T12:00:00Z");
    private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);

    static void run() {
        paysOrder();
        refusesSecondCharge();
        missingOrderHasNoEffects();
        paymentFailureDoesNotSaveOrPublish();
        immutableOrderRequiresSave();
        gatewayReusesReceipt();
        publishFailureLeavesPaidOrder();
        System.out.println("7 checks passed");
    }

    private static InMemoryOrderRepository seeded() {
        var orders = new InMemoryOrderRepository();
        orders.save(Order.created("O-1", "C-1",
                new Money(5000, Currency.getInstance("USD"))));
        return orders;
    }

    private static void paysOrder() {
        var orders = seeded();
        var payments = new FakePaymentGateway();
        var events = new RecordingEventPublisher();
        var app = new PayOrderService(orders, payments, events, CLOCK);
        var result = app.handle(new PayOrderCommand("O-1"));
        check(result.paymentId().equals("PAY-1"), "receipt");
        check(orders.findById("O-1").orElseThrow().status()
                == OrderStatus.PAID, "saved state");
        check(orders.writes() == 2, "seed plus explicit save");
        check(payments.charges() == 1, "one charge");
        check(events.events().equals(List.of(
                new OrderPaid("O-1", "PAY-1", NOW))), "event payload and time");
    }

    private static void refusesSecondCharge() {
        var orders = seeded();
        var payments = new FakePaymentGateway();
        var events = new RecordingEventPublisher();
        var app = new PayOrderService(orders, payments, events, CLOCK);
        app.handle(new PayOrderCommand("O-1"));
        expect(IllegalStateException.class,
                () -> app.handle(new PayOrderCommand("O-1")));
        check(payments.charges() == 1 && events.events().size() == 1,
                "paid order rejected before charge or event");
    }

    private static void missingOrderHasNoEffects() {
        var orders = new InMemoryOrderRepository();
        var payments = new FakePaymentGateway();
        var events = new RecordingEventPublisher();
        var app = new PayOrderService(orders, payments, events, CLOCK);
        expect(IllegalArgumentException.class,
                () -> app.handle(new PayOrderCommand("missing")));
        check(payments.charges() == 0 && orders.writes() == 0
                && events.events().isEmpty(), "missing order has no effects");
    }

    private static void paymentFailureDoesNotSaveOrPublish() {
        var orders = seeded();
        PaymentGateway failing = request -> {
            throw new IllegalStateException("Payment failed");
        };
        var events = new RecordingEventPublisher();
        var app = new PayOrderService(orders, failing, events, CLOCK);
        expect(IllegalStateException.class,
                () -> app.handle(new PayOrderCommand("O-1")));
        check(orders.writes() == 1 && events.events().isEmpty(),
                "no save or event after payment failure");
    }

    private static void immutableOrderRequiresSave() {
        var orders = seeded();
        Order loaded = orders.findById("O-1").orElseThrow();
        loaded.markPaid("PAY-unsaved");
        check(orders.findById("O-1").orElseThrow().status()
                == OrderStatus.CREATED, "unsaved value must not change repository");
    }

    private static void gatewayReusesReceipt() {
        var gateway = new FakePaymentGateway();
        var amount = new Money(5000, Currency.getInstance("USD"));
        var request = new PaymentRequest("key-1", "C-1", amount);
        check(gateway.charge(request).equals(gateway.charge(request)),
                "same logical charge returns same receipt");
        check(gateway.charges() == 1, "one logical charge");
        expect(IllegalArgumentException.class, () -> gateway.charge(
                new PaymentRequest("key-1", "C-2", amount)));
    }

    private static void publishFailureLeavesPaidOrder() {
        var orders = seeded();
        EventPublisher failing = event -> {
            throw new IllegalStateException("Broker unavailable");
        };
        var app = new PayOrderService(orders, new FakePaymentGateway(),
                failing, CLOCK);
        expect(IllegalStateException.class,
                () -> app.handle(new PayOrderCommand("O-1")));
        check(orders.findById("O-1").orElseThrow().status()
                == OrderStatus.PAID, "demonstrates the unresolved dual write");
    }

    private static void check(boolean condition, String message) {
        if (!condition) { throw new AssertionError(message); }
    }

    private static void expect(Class<? extends RuntimeException> type,
                               Runnable action) {
        try {
            action.run();
        } catch (RuntimeException failure) {
            if (type.isInstance(failure)) { return; }
            throw new AssertionError("Unexpected exception", failure);
        }
        throw new AssertionError("Expected " + type.getSimpleName());
    }
}
```

Appendix B · complete persistence adapter

## JDBC with PostgreSQL mapping

Save this class beside `Lesson15.java`. It uses the same domain types and port. Compilation needs only the JDK’s JDBC API; running it needs a PostgreSQL JDBC driver, a configured `DataSource`, and the schema below.

Download JdbcOrderRepository.java

Compile · this does not start PostgreSQL

```
javac --release 25 -d out Lesson15.java JdbcOrderRepository.java
```

SQL · create the demo table

```
CREATE TABLE orders (
    id          text PRIMARY KEY,
    customer_id text NOT NULL,
    total_minor bigint NOT NULL CHECK (total_minor > 0),
    currency    char(3) NOT NULL,
    status      text NOT NULL CHECK (status IN ('CREATED', 'PAID')),
    payment_id  text,
    CHECK (
        (status = 'CREATED' AND payment_id IS NULL) OR
        (status = 'PAID' AND payment_id IS NOT NULL
                       AND length(btrim(payment_id)) > 0)
    )
);
```

The save method uses PostgreSQL’s `ON CONFLICT` upsert syntax. [[15]](#source-15) The adapter is not a transaction manager and its upsert does not enforce the order lifecycle under concurrent writers.

**Validation limit**

The class was compiled with the demo. **⚠️** No PostgreSQL instance was available for integration tests. Test row mapping, constraints, failure translation, and the chosen concurrency policy against a real test database before using it.

JdbcOrderRepository.java · complete source

```
import java.sql.SQLException;
import java.util.Currency;
import java.util.Objects;
import java.util.Optional;
import javax.sql.DataSource;

// Compile alongside Lesson15.java. Runtime requires a configured DataSource
// and a JDBC driver. Each operation uses its own auto-commit connection.
public final class JdbcOrderRepository implements OrderRepository {
    private final DataSource dataSource;

    public JdbcOrderRepository(DataSource dataSource) {
        this.dataSource = Objects.requireNonNull(dataSource);
    }

    @Override
    public Optional<Order> findById(String orderId) {
        String sql = """
                SELECT id, customer_id, total_minor, currency, status, payment_id
                FROM orders WHERE id = ?
                """;
        try (var connection = dataSource.getConnection()) {
            requireAutoCommit(connection.getAutoCommit());
            try (var statement = connection.prepareStatement(sql)) {
                statement.setString(1, orderId);
                try (var rows = statement.executeQuery()) {
                    if (!rows.next()) { return Optional.empty(); }
                    return Optional.of(new Order(
                            rows.getString("id"), rows.getString("customer_id"),
                            new Money(rows.getLong("total_minor"),
                                    Currency.getInstance(rows.getString("currency"))),
                            OrderStatus.valueOf(rows.getString("status")),
                            rows.getString("payment_id")));
                }
            }
        } catch (SQLException failure) {
            throw new IllegalStateException("Could not load order", failure);
        }
    }

    @Override
    public void save(Order order) {
        String sql = """
                INSERT INTO orders
                    (id, customer_id, total_minor, currency, status, payment_id)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                    customer_id = EXCLUDED.customer_id,
                    total_minor = EXCLUDED.total_minor,
                    currency = EXCLUDED.currency,
                    status = EXCLUDED.status,
                    payment_id = EXCLUDED.payment_id
                """;
        try (var connection = dataSource.getConnection()) {
            requireAutoCommit(connection.getAutoCommit());
            try (var statement = connection.prepareStatement(sql)) {
                statement.setString(1, order.id());
                statement.setString(2, order.customerId());
                statement.setLong(3, order.total().minorUnits());
                statement.setString(4, order.total().currency().getCurrencyCode());
                statement.setString(5, order.status().name());
                statement.setString(6, order.paymentId());
                if (statement.executeUpdate() != 1) {
                    throw new IllegalStateException("Expected one saved order");
                }
            }
        } catch (SQLException failure) {
            throw new IllegalStateException("Could not save order", failure);
        }
    }

    private static void requireAutoCommit(boolean autoCommit) {
        if (!autoCommit) {
            throw new IllegalStateException("Demo requires auto-commit connections");
        }
    }
}
```

References · verified 2 September 2026

## Primary sources and validation notes

This guide adapts the supplied Lesson 15. Its examples and design commentary are teaching choices; framework and API claims are grounded in the sources below. Reading, navigation, printing, and the code downloads work offline. Opening a source link requires an internet connection.

1. [Alistair Cockburn · Hexagonal Architecture, original article](https://alistair.cockburn.us/hexagonal-architecture)

   Original pattern, ports and adapters, primary/secondary roles, inside/outside distinction.

   https://alistair.cockburn.us/hexagonal-architecture
2. [Microsoft Learn · Common web application architectures](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)

   Application core, inward source dependencies, runtime composition, related architecture families.

   https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures
3. [Oracle · Java 25 record classes](https://docs.oracle.com/en/java/javase/25/language/records.html)

   Records and their generated data-carrier members.

   https://docs.oracle.com/en/java/javase/25/language/records.html
4. [Oracle · Java 25 Clock API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html)

   Injectable clocks, systemUTC, fixed, and deterministic time in tests.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html
5. [Oracle · Java 25 DataSource API](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/javax/sql/DataSource.html)

   JDBC connection source.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/javax/sql/DataSource.html
6. [Oracle · Java 25 PreparedStatement and Connection APIs](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/PreparedStatement.html)

   Bound parameters and statement execution. See also the linked Connection reference.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/PreparedStatement.html
7. [Spring Framework · Mapping requests](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-requestmapping.html)

   HTTP mappings and path variables.

   https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-requestmapping.html
8. [Spring Boot · System requirements](https://docs.spring.io/spring-boot/system-requirements.html)

   Verified page: Boot 4.1.1 supports Java 17 through 26; Java 25 is in that range.

   https://docs.spring.io/spring-boot/system-requirements.html
9. [Stripe · Payment Intents](https://docs.stripe.com/payments/payment-intents)

   Payment lifecycle and integration flow.

   https://docs.stripe.com/payments/payment-intents
10. [Stripe · Idempotent requests](https://docs.stripe.com/api/idempotent_requests)

    Provider request-idempotency semantics.

    https://docs.stripe.com/api/idempotent\_requests
11. [Apache Kafka · KafkaProducer API, 4.1.2](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)

    Asynchronous send, returned future, delivery configuration and lifecycle.

    https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html
12. [Spring Framework · Using @Bean](https://docs.spring.io/spring-framework/reference/core/beans/java/bean-annotation.html)

    Bean declarations and dependency injection through configuration.

    https://docs.spring.io/spring-framework/reference/core/beans/java/bean-annotation.html
13. [AWS Prescriptive Guidance · Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

    Dual writes, local transaction with outbox, relay and duplicate handling.

    https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
14. [Oracle · Java 25 javac command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

    Compilation and --release option.

    https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html
15. [PostgreSQL · INSERT](https://www.postgresql.org/docs/current/sql-insert.html)

    ON CONFLICT and upsert semantics.

    https://www.postgresql.org/docs/current/sql-insert.html

Additional JDBC transaction reference: [Java 25 Connection API](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html).

**Integration status:** Spring MVC and Kafka excerpts were checked against official documentation but were not compiled against those libraries. The Stripe section is a mapping explanation, not a runnable SDK example. The JDBC class was compiled but not integration-tested.

DP · Lesson 15 · Adapted from the supplied lesson. Reference verification: 2 September 2026.