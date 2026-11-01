[Skip to guide](#main)

**DP / Lesson 09 · Facade**

Print / Save PDFDownload JavaCopy Java

In this lesson

[Overview](#top)[01 · The starting point](#step-1)[02–04 · Find the pressure](#step-2)[05 · Extract the facade](#step-5)[06–09 · Scope and ownership](#step-6)[10–13 · Related patterns](#step-10)[14–15 · Results and errors](#step-14)[16–18 · Sequence and tests](#step-16)[19 · Reliability limits](#step-19)[20 · Complete Java code](#step-20)[21 · Decision guide](#step-21)[Video-processing exercise](#exercise)[Sources](#sources)

DP / Design patterns from first principles

Lesson 09 · Structural pattern

# Facade

Hide subsystem complexity behind
one useful entry point.

A client wants checkout. It should not have to learn how inventory, tax, fraud, payment, shipping, and email work together.

Java 25 compatibleNo external librariesOffline guide

The question that leads to the pattern

Why does every caller need to know the subsystem’s internal choreography?

A Facade offers a simpler interface over a larger subsystem. The complexity remains, but a focused boundary owns the common workflow. [[1]](#source-1)

### What you will derive

1. Notice repeated coordination.
2. Identify the capability callers want.
3. Move workflow knowledge behind that capability.
4. Define results, failure semantics, and tests.

### What you will build

A checkout facade, six small subsystem contracts, a thin controller, and seven executable workflow checks.

Then apply the same reasoning to video processing.

**Reading path**

[1–4: derive the need](#step-1) · [5–13: design the boundary](#step-5) · [14–19: outcomes and reliability](#step-14) · [20: complete Java example](#step-20) · [21: decision guide](#step-21) · [exercise](#exercise)

Everything needed to read this guide and retrieve its Java example is embedded. Use “Print / Save PDF” at the top, or your browser’s print command. Choose A4 or Letter, 100% scale, and disable browser headers and footers.

## 01Start without Facade

Suppose a checkout controller coordinates these components directly. The subsystem is deliberately small enough to inspect.

| Component | Its responsibility in this lesson |
| --- | --- |
| `InventoryService` | Reserve stock for an order. |
| `TaxService` | Calculate tax for a trusted subtotal. |
| `FraudService` | Approve or reject the proposed purchase. |
| `PaymentService` | Charge the customer. |
| `ShippingService` | Create a shipment. |
| `EmailService` | Send a confirmation. |

The controller stores these six dependencies. Its method looks like this:

Java · teaching excerpt

```
CheckoutResult checkout(CheckoutRequest request) {
    inventory.reserve(request.orderId(), request.productId(),
                      request.quantity());
    long taxCents = tax.calculateTax(request.subtotalCents());
    long total = Math.addExact(request.subtotalCents(), taxCents);

    if (!fraud.approve(request.customerId(), total)) {
        throw new IllegalStateException("Fraud check failed");
    }
    String paymentId = payment.charge(request.orderId(),
                                      request.customerId(), total);
    String shipmentId = shipping.createShipment(request.orderId());
    email.sendConfirmation(request.customerId(), request.orderId());
    return new CheckoutSuccess(request.orderId(), paymentId,
                               shipmentId, total);
}
```

The happy path is readable. But the HTTP layer now knows the entire workflow: the participants, their order, and how one step supplies data to the next.

**An intentional first draft**

This version can leave stock reserved after fraud rejection. It is here to expose the design pressure, not to prescribe a safe checkout sequence. Step 20 moves fraud before reservation and handles specific business rejections.

Early snippets are excerpts, not separate programs. Step 20 defines every type and dependency in one complete source file.

## 02Add another client

Now the REST API, mobile API, admin UI, scheduled order processor, and CLI all need checkout. Each starts copying the same coordination code.

Duplication is only the visible symptom. The deeper problem is that every caller must learn and maintain the same subsystem knowledge.

## 03Diagnose the coupling

| Knowledge duplicated in clients | What a change now costs |
| --- | --- |
| Which services participate | Adding a required step can affect every client. |
| Which steps depend on others | A sequencing rule can require several coordinated edits. |
| Which values cross each boundary | Internal contract changes spread into entry points. |
| How failures become checkout outcomes | Clients may disagree about what the same failure means. |

If fraud must happen before reservation, one conceptual workflow change may force five callers to change. That is the design smell.

## 04Ask what callers actually want

A caller wants to complete checkout. The low-level steps are the means, not the capability it should have to assemble itself.

Java · the desired caller experience

```
CheckoutResult result = checkout.checkout(request);
```

Derivation

Repeated workflow knowledge creates pressure for a smaller, use-case-oriented entry point.

### Pause and reason

If you remove five duplicate methods but callers still choose which checkout steps to skip, have you created the intended boundary?

**Reasoning:** You have reduced code duplication, but workflow ownership is still scattered. The useful boundary owns the common operation and its required steps.

## 05Create the Facade

Move the common workflow into `CheckoutFacade`. Supply its collaborators through the constructor. Clients depend on one operation; the facade depends on the subsystem contracts.

Java · extraction sketch; complete method appears in Step 20

```
final class CheckoutFacade {
    private final InventoryService inventory;
    private final TaxService tax;
    private final FraudService fraud;
    private final PaymentService payment;
    private final ShippingService shipping;
    private final EmailService email;

    CheckoutFacade(InventoryService inventory, TaxService tax,
                   FraudService fraud, PaymentService payment,
                   ShippingService shipping, EmailService email) {
        this.inventory = inventory;
        this.tax = tax;
        this.fraud = fraud;
        this.payment = payment;
        this.shipping = shipping;
        this.email = email;
    }

    // Move the checkout(...) method from Step 1 here.
}
```

The controller now delegates. It can still own transport concerns such as parsing input and mapping the result to an HTTP response.

Java · teaching excerpt

```
final class CheckoutController {
    private final CheckoutFacade checkout;

    CheckoutController(CheckoutFacade checkout) {
        this.checkout = checkout;
    }

    public CheckoutResult checkout(CheckoutRequest request) {
        return checkout.checkout(request);
    }
}
```

| Boundary | Knowledge it owns |
| --- | --- |
| Caller | Request data and checkout outcomes. |
| Facade | Common workflow, coordination, sequencing. |
| Subsystem components | Inventory, tax, payment, and other specialized behavior. |

## 06What actually improved?

The amount of knowledge required at the client boundary has decreased. The subsystem may remain complex; its common use is now simpler.

## 07Hide information that changes together

Suppose checkout evolves from reserving stock before charging to authorizing payment, reserving stock, and then capturing payment. Clients should not have to coordinate that transition.

| Before extraction | After extraction |
| --- | --- |
| Each client coordinates the steps. | The facade coordinates the steps. |
| Sequencing edits spread across clients. | Sequencing edits stay behind the boundary. |
| Clients learn internal service details. | Clients learn the checkout contract. |

**Locality of change is conditional:** callers can stay unchanged when the public request and outcome contract remains stable. A new required user input or a new meaning of “completed” may still require caller changes.

## 08Keep the capability coherent

A single `EverythingFacade` with checkout, password reset, reporting, reconciliation, and user creation becomes a god object. Hiding every service behind one class is not a useful goal.

Prefer boundaries such as `CheckoutFacade`, `ReportingFacade`, or `MediaProcessingFacade`, each with a focused reason to change. Method names should describe capabilities, not mirror every low-level method.

## 09Facade and application service can overlap

A `CheckoutService` that exposes an application operation and coordinates its collaborators can also play the Facade role. Service Layer describes an application boundary and coordinated operations; Facade describes simplifying access to a subsystem. The concepts overlap without being identical. [[2]](#source-2)

The facade should coordinate domain behavior. Stock rules belong with inventory, tax rules with the tax component, and payment rules with the payment component. A new wrapper should not absorb every business algorithm.

**Design test**

Can you explain the class’s public capability in one sentence, and can you identify the workflow knowledge clients no longer need?

## 10Facade vs Adapter

Adapter reconciles incompatible interfaces; Facade simplifies access to a larger subsystem. An adapter may sit behind a facade when one participant is a legacy or external service. [[1]](#source-1)

| Pattern | Pressure | Example |
| --- | --- | --- |
| Adapter | A needed interface does not match an existing one. | Translate `shipping.quote(order)` into a legacy call using postal code and weight. |
| Facade | A caller must understand too much internal coordination. | Expose `checkout(request)` over the checkout subsystem. |

## 11Facade vs Factory

Factory deals with object creation, often including which implementation to instantiate. Facade deals with using a subsystem through a simpler capability.

Java · contrasting responsibilities; illustrative API names

```
PaymentProcessor processor = factory.create(method);
CheckoutResult result = checkout.checkout(request);
```

## 12Facade vs Command

A command represents a request to do something. A command handler executes that request. A facade can provide the capability that the handler calls.

If `CheckoutCommandHandler` already owns the entire checkout workflow, adding a pass-through facade may add no value. Choose a clear owner instead of stacking pattern names.

| Concept | Question answered |
| --- | --- |
| Command data | What action was requested, with which inputs? |
| Handler | How is this request executed? |
| Facade role | What simpler capability should subsystem clients use? |

## 13Lower-level access may remain available

Normal checkout callers use the facade. A specialized maintenance tool may still need an inventory operation such as rebuilding reservations.

A Facade does not itself enforce access restrictions. If bypassing the workflow would violate a requirement, enforce that boundary with API design, package or module access, and appropriate authorization.

## 14Define outcomes at the boundary

Callers need a coherent checkout contract. Instead of forcing them to understand every internal business exception, expose explicit outcomes. Records carry data; a sealed interface restricts the permitted result implementations. [[3]](#source-3) [[4]](#source-4)

Java · teaching excerpt

```
sealed interface CheckoutResult
        permits CheckoutSuccess, CheckoutRejected {}

record CheckoutSuccess(String orderId, String paymentId,
                       String shipmentId, long totalCents)
        implements CheckoutResult {}

enum Rejection { FRAUD_REJECTED, OUT_OF_STOCK, PAYMENT_DECLINED }

record CheckoutRejected(Rejection reason)
        implements CheckoutResult {}
```

`CheckoutSuccess` means that all synchronous calls in this example returned successfully. It does not mean a parcel has been delivered or an email has reached the recipient.

## 15Keep meaningful failures distinct

Do not catch every `Exception` and report a business rejection. That would make a programming bug, a database outage, a payment timeout, and an actual payment decline look the same.

Java · teaching excerpt

```
try {
    paymentId = payment.charge(request.orderId(),
                              request.customerId(), total);
} catch (PaymentDeclinedException declined) {
    inventory.release(request.orderId());
    return new CheckoutRejected(Rejection.PAYMENT_DECLINED);
}
```

This translation relies on a precise contract: the decline exception guarantees no charge occurred, and a successful `release` call guarantees the reservation is gone. A release failure propagates as a system failure.

**A timeout is not a decline**

The remote payment might have succeeded even when its response was lost. Report and investigate an unknown outcome; do not silently translate it into a safe-to-retry rejection.

The complete example catches only named business exceptions. Unexpected failures propagate to the application’s error-handling boundary.

## 16Protect required sequencing

If payment must succeed before shipment creation, the facade owns that dependency. Callers request checkout rather than choosing the step order.

The sequence itself is a business decision. The pattern does not tell you whether authorization should precede reservation or whether email belongs in the synchronous path.

## 17Test workflow semantics with fakes

Inject small subsystem interfaces. A recording fake can track calls and simulate a rejection or failure without reaching a payment network or storage service.

| Scenario | Behavior that matters |
| --- | --- |
| Success | Total is correct; payment precedes shipment; confirmation is requested. |
| Fraud rejection | No reservation or charge is attempted. |
| Out of stock | No charge is attempted. |
| Payment decline | Stock is released; no shipment is created. |
| Release failure | The failure propagates rather than becoming a clean rejection. |
| Shipment or email failure | The failure propagates; earlier effects are not undone. |

## 18Assert order only when it matters

Use a shared `List<String>` for meaningful operations. Assert the required relationship instead of freezing every incidental call into one exact sequence.

Java · assertions from the runnable example

```
check(result instanceof CheckoutSuccess, "Expected success");
check(ok.calls.indexOf("payment") < ok.calls.indexOf("shipment"),
      "Payment must precede shipment");

check(!fraud.calls.contains("reserve") &&
      !fraud.calls.contains("payment"), "Fraud caused side effects");
```

Step 20 supplies the `check` helper and fakes. Checks throw `AssertionError` on failure, so they do not require the JVM’s `-ea` flag or a test library.

Test tax arithmetic and payment-provider behavior separately in their own components. A facade test should tell you whether the workflow obeys its contract.

## 19Face the hidden reliability problem

Suppose inventory reservation succeeds, payment succeeds, and shipment creation fails. One Java method has coordinated three effects; it has not made them one atomic transaction.

| Failure point | What may already be true | What the sample does |
| --- | --- | --- |
| Fraud rejection | No stock reserved or money charged. | Returns a rejection. |
| Payment decline | Stock is reserved; the contract says no charge occurred. | Releases stock, then returns a rejection. |
| Payment timeout | Stock is reserved; charge outcome is unknown. | Propagates the failure; does not retry. |
| Shipment failure | Stock is reserved and payment succeeded; shipment outcome may be unknown. | Propagates the failure; earlier effects remain. |
| Email failure | Reservation, payment, and shipment calls succeeded. | Propagates the failure; earlier effects remain. |

**The dangerous shortcut**

Retrying the entire checkout method can charge again. An order ID alone does not create idempotency: the services must implement and durably enforce the intended duplicate-handling contract.

Reliability mechanisms address different gaps. A compensation performs a business action that counters an earlier effect; it can also fail. A saga coordinates local transactions and their recovery. [[6]](#source-6) [[7]](#source-7)

An outbox records a business change and an event in the same local transaction, then publishes the event separately. It does not make inventory, payment, shipping, and email one transaction. Consumers still need duplicate-safe processing. [[8]](#source-8) [[9]](#source-9)

### Decide what the API promises

This guide’s implementation is synchronous. If you move work to a queue, define an “accepted” response with a durable workflow ID and a way to observe completion. Do not return “completed” merely because work was queued.

The facade remains the simple capability. Durable state, recovery policy, idempotency, and delivery guarantees need their own explicit design.

## 20A complete, consistent Java example

Save the five consecutive code panels below as `FacadeDemo.java`, in order. The download button embeds that exact file. Every type, fake, and executable check is included.

Terminal · run with JDK 25

```
javac --release 25 -Xlint:all -d out FacadeDemo.java
java -cp out FacadeDemo
```

Uses standard Java records, sealed interfaces, lambdas, and `Math.addExact`. No preview features or third-party dependencies. `addExact` detects integer overflow. [[3]](#source-3) [[4]](#source-4) [[5]](#source-5) [[10]](#source-10)

FacadeDemo.java · 1 of 5 · data and outcomes

```
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public final class FacadeDemo {
    // Part A: data and outcomes
    record CheckoutRequest(String orderId, String customerId,
                           String productId, int quantity,
                           long subtotalCents) {
        CheckoutRequest {
            requireText(orderId);
            requireText(customerId);
            requireText(productId);
            if (quantity <= 0 || subtotalCents < 0) {
                throw new IllegalArgumentException("Invalid order");
            }
        }
    }

    static void requireText(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("ID is required");
        }
    }

    sealed interface CheckoutResult
            permits CheckoutSuccess, CheckoutRejected {}

    record CheckoutSuccess(String orderId, String paymentId,
                           String shipmentId, long totalCents)
            implements CheckoutResult {}

    enum Rejection { FRAUD_REJECTED, OUT_OF_STOCK, PAYMENT_DECLINED }

    record CheckoutRejected(Rejection reason)
            implements CheckoutResult {}
```

**Model boundary:** this single-item example uses one currency in cents. `subtotalCents` is trusted server-side input; a real public API must derive or verify it against authoritative pricing. The IDs and amounts below are test fixtures.

20 / Complete implementation · continued

## Subsystem contracts and construction

The facade receives collaborators; it does not create service implementations. The two business exceptions have explicit side-effect guarantees.

FacadeDemo.java · 2 of 5 · contracts and facade constructor

```
    // Part B: subsystem contracts
    interface InventoryService {
        // OutOfStockException guarantees no reservation was made.
        void reserve(String orderId, String productId, int quantity);
        // Normal return guarantees this reservation was released.
        void release(String orderId);
    }

    interface TaxService {
        long calculateTax(long subtotalCents);
    }

    interface FraudService {
        boolean approve(String customerId, long totalCents);
    }

    interface PaymentService {
        // PaymentDeclinedException guarantees no charge was made.
        // A timeout is NOT a decline: its outcome may be unknown.
        String charge(String orderId, String customerId, long cents);
    }

    interface ShippingService {
        String createShipment(String orderId);
    }

    interface EmailService {
        void sendConfirmation(String customerId, String orderId);
    }

    static final class OutOfStockException extends RuntimeException {
        private static final long serialVersionUID = 1L;
    }

    static final class PaymentDeclinedException extends RuntimeException {
        private static final long serialVersionUID = 1L;
    }

    // Part C: the facade and its client
    static final class CheckoutFacade {
        private final InventoryService inventory;
        private final TaxService tax;
        private final FraudService fraud;
        private final PaymentService payment;
        private final ShippingService shipping;
        private final EmailService email;

        CheckoutFacade(InventoryService inventory, TaxService tax,
                       FraudService fraud, PaymentService payment,
                       ShippingService shipping, EmailService email) {
            this.inventory = Objects.requireNonNull(inventory);
            this.tax = Objects.requireNonNull(tax);
            this.fraud = Objects.requireNonNull(fraud);
            this.payment = Objects.requireNonNull(payment);
            this.shipping = Objects.requireNonNull(shipping);
            this.email = Objects.requireNonNull(email);
        }
```

20 / Complete implementation · continued

## One owner of the workflow

Tax and fraud run before reservation. A payment decline releases stock; shipping and email failures stay visible. This method continues inside `CheckoutFacade` from the previous panel.

FacadeDemo.java · 3 of 5 · orchestration and client

```
        public CheckoutResult checkout(CheckoutRequest request) {
            Objects.requireNonNull(request);
            long taxCents = tax.calculateTax(request.subtotalCents());
            if (taxCents < 0) {
                throw new IllegalStateException("Negative tax");
            }
            long total = Math.addExact(request.subtotalCents(), taxCents);
            if (!fraud.approve(request.customerId(), total)) {
                return new CheckoutRejected(Rejection.FRAUD_REJECTED);
            }
            try {
                inventory.reserve(request.orderId(), request.productId(),
                                  request.quantity());
            } catch (OutOfStockException declined) {
                return new CheckoutRejected(Rejection.OUT_OF_STOCK);
            }
            String paymentId;
            try {
                paymentId = payment.charge(request.orderId(),
                                          request.customerId(), total);
            } catch (PaymentDeclinedException declined) {
                // If release fails, propagate that system failure.
                inventory.release(request.orderId());
                return new CheckoutRejected(Rejection.PAYMENT_DECLINED);
            }
            // Later failures propagate; earlier effects remain.
            String shipmentId = shipping.createShipment(request.orderId());
            email.sendConfirmation(request.customerId(), request.orderId());
            return new CheckoutSuccess(request.orderId(), paymentId,
                                       shipmentId, total);
        }
    }

    static final class CheckoutController {
        private final CheckoutFacade checkout;
        CheckoutController(CheckoutFacade checkout) {
            this.checkout = Objects.requireNonNull(checkout);
        }
        public CheckoutResult checkout(CheckoutRequest request) {
            return checkout.checkout(request);
        }
    }
```

**What this example intentionally leaves open**

It has no durable workflow store, automatic retries, or deduplication. Passing an order ID gives collaborators useful context, but does not make these fakes idempotent.

20 / Complete implementation · continued

## Fakes make behavior observable

Each scenario gets a fresh `Rig`. Its fixed 100-cent tax is a test fixture, not a tax rule.

FacadeDemo.java · 4 of 5 · recording fakes and test helpers

```
    // Part D: a deterministic fake subsystem
    static final class Rig {
        final List<String> calls = new ArrayList<>();
        boolean fraudApproved = true, inStock = true;
        boolean paymentApproved = true, failShipping, failEmail;
        boolean failRelease;

        CheckoutFacade facade() {
            return new CheckoutFacade(new InventoryService() {
                public void reserve(String order, String product, int qty) {
                    calls.add("reserve");
                    if (!inStock) throw new OutOfStockException();
                }
                public void release(String order) {
                    calls.add("release");
                    if (failRelease) throw new IllegalStateException("release");
                }
            }, subtotal -> {
                calls.add("tax");
                return 100L; // Fixed test fixture, not a tax algorithm.
            }, (customer, total) -> {
                calls.add("fraud");
                return fraudApproved;
            }, (order, customer, total) -> {
                calls.add("payment");
                if (!paymentApproved) throw new PaymentDeclinedException();
                return "PAY-1";
            }, order -> {
                calls.add("shipment");
                if (failShipping) throw new IllegalStateException("shipping");
                return "SHIP-1";
            }, (customer, order) -> {
                calls.add("email");
                if (failEmail) throw new IllegalStateException("email");
            });
        }
    }

    static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    static void expectFailure(Rig rig, CheckoutRequest request,
                              String message) {
        try {
            rig.facade().checkout(request);
            throw new AssertionError("Expected " + message + " failure");
        } catch (IllegalStateException failure) {
            check(message.equals(failure.getMessage()), "Wrong failure");
        }
    }
```

20 / Complete implementation · continued

## Run seven workflow scenarios

FacadeDemo.java · 5 of 5 · executable checks and closing brace

```
    // Part E: execute workflow checks without a test library
    public static void main(String[] args) {
        var request = new CheckoutRequest("ORD-1", "CUS-1", "SKU-1", 2, 2000);
        var ok = new Rig();
        var controller = new CheckoutController(ok.facade());
        var result = controller.checkout(request);
        check(result instanceof CheckoutSuccess, "Expected success");
        check(((CheckoutSuccess) result).totalCents() == 2100, "Wrong total");
        check(ok.calls.indexOf("payment") < ok.calls.indexOf("shipment"),
              "Payment must precede shipment");
        check(ok.calls.contains("email"), "Confirmation is required");

        var fraud = new Rig();
        fraud.fraudApproved = false;
        check(fraud.facade().checkout(request).equals(
              new CheckoutRejected(Rejection.FRAUD_REJECTED)), "Fraud result");
        check(!fraud.calls.contains("reserve") &&
              !fraud.calls.contains("payment"), "Fraud caused side effects");

        var stock = new Rig();
        stock.inStock = false;
        check(stock.facade().checkout(request).equals(
              new CheckoutRejected(Rejection.OUT_OF_STOCK)), "Stock result");
        check(!stock.calls.contains("payment"), "Charged without stock");

        var declined = new Rig();
        declined.paymentApproved = false;
        check(declined.facade().checkout(request).equals(
              new CheckoutRejected(Rejection.PAYMENT_DECLINED)), "Decline result");
        check(declined.calls.contains("release") &&
              !declined.calls.contains("shipment"), "Decline cleanup");

        var release = new Rig();
        release.paymentApproved = false;
        release.failRelease = true;
        expectFailure(release, request, "release");

        var shipment = new Rig();
        shipment.failShipping = true;
        expectFailure(shipment, request, "shipping");
        check(shipment.calls.contains("payment") &&
              !shipment.calls.contains("email"), "Partial failure semantics");

        var email = new Rig();
        email.failEmail = true;
        expectFailure(email, request, "email");
        check(email.calls.contains("payment") &&
              email.calls.contains("shipment"), "Earlier effects remain");

        System.out.println(result);
        System.out.println("PASS: 7 workflow scenarios");
    }
}
```

**Expected result:** the success record contains `ORD-1`, `PAY-1`, `SHIP-1`, and `2100`; the final line is `PASS: 7 workflow scenarios`.

**Verification:** compiled with `--release 17 -Xlint:all` and ran on OpenJDK 17.0.20 with all seven scenarios passing. The language features and APIs were checked against the Java 25 documentation. A JDK 25 runtime was not available for direct execution.

## 21Use the first-principles decision process

Counting services is a weak reason to add a facade. Look for duplicated workflow knowledge and a capability that can own it.

| Ask | What a “yes” suggests |
| --- | --- |
| Do several callers repeat the same coordination? | There may be a missing shared workflow owner. |
| Do callers know internal service names and sequencing rules? | The client boundary may expose too much. |
| Does one workflow change force edits in many callers? | A focused entry point could improve locality of change. |
| Can the operation be named in the client’s language? | You may have a useful public capability. |
| Does an existing handler or service already own the workflow? | It may already play the Facade role. |
| Are failure and completion semantics clear? | The simplified interface is becoming a usable contract. |

### When the extra class earns its place

Use it when it removes meaningful knowledge from clients. A thin facade can be valuable even with few collaborators if those collaborators are difficult to use correctly. A wrapper over many services can still be unhelpful if it simply exposes all their methods.

The transferable idea

A good boundary makes the caller’s intention simple while giving the internal workflow a clear owner.

### Recall prompts

1. Which knowledge moved out of `CheckoutController`?
2. Why can a payment timeout not become `PAYMENT_DECLINED`?
3. Which guarantee does the facade provide, and which transaction guarantee does it not provide?
4. When would a command handler make an additional facade redundant?

Apply the reasoning

## Exercise: a video-processing facade

Every caller currently loads a video, decodes video and audio, parses optional subtitles, encodes an output, generates a thumbnail, and uploads the result.

| Subsystem component | Focused responsibility |
| --- | --- |
| `VideoDecoder` | Decode the video stream. |
| `AudioDecoder` | Decode the audio stream. |
| `SubtitleParser` | Parse supplied subtitles. |
| `VideoEncoder` | Produce the encoded output. |
| `ThumbnailGenerator` | Generate a thumbnail. |
| `StorageClient` | Load input and upload artifacts. |

Java · exercise skeleton; define request and result types

```
final class VideoProcessingFacade {
    // Inject the subsystem collaborators through a constructor.
    ProcessingResult process(ProcessingRequest request) {
        // Own the common workflow here.
        throw new UnsupportedOperationException("Exercise");
    }
}
```

### Acceptance criteria

1. The API/controller knows none of the internal processing sequence.
2. The facade owns the common workflow.
3. A sequencing change with the same public contract does not change callers.
4. Low-level components remain independently testable.
5. The facade stays focused on media processing.
6. You explicitly decide what happens if upload fails after encoding succeeds.

### Write the contract before the method

Define the source reference, output format, optional subtitles, and workflow identity. Decide what success means and whether completion is synchronous.

**Failure-policy choice to justify:** preserve encoded artifacts and retry upload, or clean them up and report failure. Account for a timeout after upload actually succeeded, and for video upload succeeding while thumbnail upload fails. Define stable artifact keys, cleanup ownership, and how a caller observes the outcome.

Extend the workflow checks with: decode failure prevents encoding; encode failure prevents upload; upload retry does not unnecessarily repeat encoding or publish duplicate artifacts under your chosen policy.

Continue the pattern sequence

## Next: Proxy

Facade simplifies a subsystem’s interface. Next, keep the same `DocumentRepository` abstraction and introduce a stand-in that can control access to an expensive, remote, secured, or lazily initialized repository.

The next pressure is: **how can access be controlled while callers keep using the same abstraction?**

## Sources and compatibility

The lesson was adapted from the supplied Lesson 9, preserving its 21-step progression. Supporting references below were checked on 1 September 2026. Design choices and test fixtures are specific to this guide.

1. [Microsoft Learn: Adapter and Façade](https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-adapterfaade)Pattern definition and the distinction from Adapter.https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-adapterfaade
2. [Martin Fowler: Service Layer](https://martinfowler.com/eaaCatalog/serviceLayer.html)Primary pattern-author reference for application boundaries and coordination.https://martinfowler.com/eaaCatalog/serviceLayer.html
3. [Oracle Java 25: Record Classes](https://docs.oracle.com/en/java/javase/25/language/records.html)Data carriers, generated accessors, and compact constructors.https://docs.oracle.com/en/java/javase/25/language/records.html
4. [Oracle Java 25: Sealed Classes](https://docs.oracle.com/en/java/javase/25/language/sealed-classes-interfaces.html)Sealed interfaces and permitted implementations.https://docs.oracle.com/en/java/javase/25/language/sealed-classes-interfaces.html
5. [Oracle Java 25: Math](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Math.html#addExact(long,long))Overflow-detecting integer addition.https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Math.html#addExact(long,long)
6. [Microsoft Learn: Compensating Transaction](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)Business compensation and recovery limits.https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
7. [Microsoft Learn: Saga](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)Coordinating local transactions and recovery.https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
8. [Microsoft Learn: Transactional Outbox](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos)Saving state and events together before separate publication.https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos
9. [Microsoft Learn: Idempotent Consumer](https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer)Processing duplicate deliveries without duplicating effects.https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer
10. [Oracle Java 25: javac](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)Compilation, release targeting, and compiler options.https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html

DP / Lesson 09 · Facade · End of guide