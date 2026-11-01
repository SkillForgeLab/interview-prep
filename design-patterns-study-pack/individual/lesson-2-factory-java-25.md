# Lesson 2 — Factory in Java 25

> Goal: continue from Strategy, derive Factory from duplicated creation knowledge, implement both Simple Factory and
> Factory Method, test their responsibilities, and know when a plain constructor or conditional is the better design.

## Learning outcomes

By the end, you should be able to:

- explain why Strategy leaves object selection and creation unresolved;
- identify **creation knowledge** and choose where it should live;
- centralize runtime selection with a Simple Factory;
- distinguish Simple Factory from the GoF Factory Method pattern;
- implement Factory Method as an overridable creation step inside a creator workflow;
- test products, factories, and creator workflows at the correct boundaries;
- evaluate the costs of centralized conditionals, inheritance, and indirection; and
- recognize when direct construction is simpler and more honest.

---

## 1. Bridge from Lesson 1: Strategy solved behavior, not creation

Lesson 1 separated shipping algorithms behind one capability:

```java

@FunctionalInterface
interface ShippingPolicy {
    int costInCents(Order order);
}
```

The stable checkout workflow depends on that capability:

```java
import java.util.Objects;

final class CheckoutService {
    private final ShippingPolicy shippingPolicy;

    CheckoutService(ShippingPolicy shippingPolicy) {
        this.shippingPolicy = Objects.requireNonNull(shippingPolicy);
    }

    int totalInCents(Order order) {
        return order.subtotalCents()
                + shippingPolicy.costInCents(order);
    }
}
```

```text
CheckoutService ──uses──> ShippingPolicy <── StandardShipping
                                         <── ExpressShipping
                                         <── OvernightShipping
```

Strategy answered:

> How can checkout use interchangeable shipping algorithms without knowing their details?

But a caller must still obtain the correct strategy:

```java
var policy = new ExpressShipping();
var checkout = new CheckoutService(policy);
```

Or, when the choice comes from input:

```java
ShippingPolicy policy = switch (request.shippingMethod()) {
    case STANDARD -> new StandardShipping();
    case EXPRESS -> new ExpressShipping();
    case OVERNIGHT -> new OvernightShipping();
};
```

That is not a flaw in Strategy. Selection and construction are separate responsibilities that must live somewhere.

---

## 2. Start with the simplest correct creation code

Suppose only one endpoint needs to translate a validated `ShippingMethod` into a policy:

```java
static ShippingPolicy policyFor(ShippingMethod method) {
    return switch (method) {
        case STANDARD -> new StandardShipping();
        case EXPRESS -> new ExpressShipping();
        case OVERNIGHT -> new OvernightShipping();
    };
}
```

This is good code when the decision is local, small, and stable. A `switch` and `new` are not design smells by
themselves.

### First principle

Object creation is ordinary code. Introduce a creation abstraction only when it contains real change pressure or
prevents important knowledge from spreading.

---

## 3. Let duplicated creation create pressure

Now five callers need the same translation:

```text
CheckoutController
AdminQuoteController
OrderService
ShippingEstimator
ScheduledQuoteJob
```

Each begins to repeat this knowledge:

```java
switch(method){
        case STANDARD ->new

StandardShipping();
    case EXPRESS ->new

ExpressShipping();
    case OVERNIGHT ->new

OvernightShipping();
}
```

Then construction grows:

```java
case EXPRESS ->new

ExpressShipping(
        fuelPriceProvider,
        remoteAreaRepository,
        clock
        );
```

The repeated syntax is only the symptom. The deeper problem is:

> Many callers know which concrete class corresponds to each input and how that class must be assembled.

When the mapping or constructor changes, all those callers may need coordinated edits.

```text
                    duplicated creation knowledge

CheckoutController ───────────────┐
AdminQuoteController ─────────────┤
OrderService ─────────────────────┼──> concrete shipping classes
ShippingEstimator ────────────────┤
ScheduledQuoteJob ────────────────┘
```

### First-principles diagnosis

Ask these questions before naming a pattern:

1. **What decision is repeated?** A shipping method is mapped to a concrete policy.
2. **What construction details are repeated?** Callers know constructors and dependencies.
3. **Who needs the product?** Callers need only the `ShippingPolicy` capability.
4. **Where should the volatile knowledge live?** In one cohesive creation boundary.
5. **What remains unavoidable?** Somewhere, code must still make the concrete choice.

Factory does not eliminate the decision. It gives the decision one owner.

---

## 4. Derive a Simple Factory

Move the mapping into one class:

```java
import java.util.Objects;

final class ShippingPolicyFactory {
    private ShippingPolicyFactory() {
    }

    static ShippingPolicy create(ShippingMethod method) {
        Objects.requireNonNull(method, "method");

        return switch (method) {
            case STANDARD -> new StandardShipping();
            case EXPRESS -> new ExpressShipping();
            case OVERNIGHT -> new OvernightShipping();
        };
    }
}
```

Callers now depend on one creation boundary:

```java
var policy = ShippingPolicyFactory.create(request.shippingMethod());
var checkout = new CheckoutService(policy);
```

```text
input ──> ShippingPolicyFactory ──creates──> ShippingPolicy
                                                    │
                                                    v
                                            CheckoutService
```

### Why this helps

- There is one authoritative mapping from `ShippingMethod` to implementation.
- Callers no longer know concrete constructors.
- Constructor dependencies can be assembled in one place.
- Creation behavior can be tested directly.
- A new caller reuses the same decision instead of copying it.

### What it does not do

- The conditional still exists.
- Adding a shipping method usually changes the factory.
- The factory can become a large registry if unrelated products accumulate in it.
- It does not make every caller automatically extensible.

That is a deliberate trade: one cohesive place changes instead of many scattered places.

---

## 5. Name it accurately: Simple Factory

The class above is commonly called a **Simple Factory**:

> A dedicated function or object receives selection information and returns a product through a shared contract.

Simple Factory is a useful design idiom, but it is not the Gang of Four (GoF) Factory Method pattern.

Its essential shape is:

```text
                      chooses with ordinary logic
                                  │
                                  v
Client ──calls──> SimpleFactory.create(key) ──> Product
```

The factory may be:

- a static method, as in this lesson;
- an instance with constructor-injected dependencies;
- a lambda or function;
- a map from keys to suppliers; or
- composition-root code in a dependency-injection setup.

The shape matters less than the responsibility: it owns creation knowledge.

### Three similarly named ideas

| Term                       | Defining idea                                                                            | In this lesson                                                                                                       |
|----------------------------|------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Simple Factory             | Central method/object chooses and creates a product                                      | `ShippingPolicyFactory.create(method)`                                                                               |
| Factory Method pattern     | A creator workflow calls an overridable method; a subtype supplies the product           | `QuoteWorkflow.createShippingPolicy()`                                                                               |
| Java static factory method | A static, named alternative to a constructor; it may or may not choose an implementation | `ShippingPolicyFactory.create(...)` is also static, but “static factory method” alone does not imply the GoF pattern |

Do not identify Factory Method merely because a method returns a new object. The pattern depends on an overridable
creation decision inside a creator abstraction.

---

## 6. Keep selection, construction, and use distinct

These are three different jobs:

```text
selection             construction                 use

EXPRESS      ──>      new ExpressShipping() ──>    costInCents(order)
```

In this design:

| Responsibility                          | Owner                     |
|-----------------------------------------|---------------------------|
| Express shipping algorithm              | `ExpressShipping`         |
| Map `EXPRESS` to a concrete policy      | `ShippingPolicyFactory`   |
| Add subtotal and shipping               | `CheckoutService`         |
| Read and validate external request text | Controller/input boundary |

Keeping input parsing outside the factory is often cleaner. For example, an HTTP controller can reject `"rocket"` as
invalid input, while the factory accepts only the already-valid `ShippingMethod` enum.

The factory should not become a dumping ground for validation, business workflow, persistence, and calculation merely
because it creates something.

---

## 7. Test the Simple Factory at its responsibility boundary

The factory's contract is the mapping. Test that mapping explicitly:

```java
static void simpleFactoryMapsEveryMethod() {
    check(ShippingPolicyFactory.create(ShippingMethod.STANDARD)
                    instanceof StandardShipping,
            "STANDARD maps to StandardShipping");

    check(ShippingPolicyFactory.create(ShippingMethod.EXPRESS)
                    instanceof ExpressShipping,
            "EXPRESS maps to ExpressShipping");

    check(ShippingPolicyFactory.create(ShippingMethod.OVERNIGHT)
                    instanceof OvernightShipping,
            "OVERNIGHT maps to OvernightShipping");
}
```

An `instanceof` assertion is appropriate here because the mapping to a concrete implementation is exactly what the
factory owns. Product tests separately verify each algorithm's behavior.

Then test composition:

```java
var policy = ShippingPolicyFactory.create(ShippingMethod.EXPRESS);
var checkout = new CheckoutService(policy);

check(checkout.totalInCents(new Order(10, 10_000))==15_000,
        "factory product composes with checkout");
```

Do not make every `CheckoutService` test go through the factory. The service accepts a strategy precisely so it can be
tested in isolation:

```java
ShippingPolicy fixedShipping = ignored -> 1_000;
var checkout = new CheckoutService(fixedShipping);

check(checkout.totalInCents(new Order(10, 10_000))==11_000,
        "checkout uses its supplied policy");
```

### Test boundaries

```text
strategy test       → algorithm is correct
factory test        → key maps to the intended product
context test        → checkout uses any supplied product correctly
integration check   → selected product and checkout work together
```

Each test should fail for a narrow reason.

---

## 8. When a Simple Factory should be an object

A static factory is sufficient while construction is pure and dependency-free. Suppose express shipping needs
collaborators:

```java
final class ShippingPolicyFactory {
    private final FuelPriceProvider fuelPrices;
    private final RemoteAreaRepository remoteAreas;
    private final Clock clock;

    ShippingPolicyFactory(
            FuelPriceProvider fuelPrices,
            RemoteAreaRepository remoteAreas,
            Clock clock
    ) {
        this.fuelPrices = fuelPrices;
        this.remoteAreas = remoteAreas;
        this.clock = clock;
    }

    ShippingPolicy create(ShippingMethod method) {
        return switch (method) {
            case STANDARD -> new StandardShipping();
            case EXPRESS -> new ExpressShipping(
                    fuelPrices, remoteAreas, clock
            );
            case OVERNIGHT -> new OvernightShipping();
        };
    }
}
```

This is still a Simple Factory. Making it an object lets the application's composition root supply shared dependencies
once.

Do not add a factory interface automatically. Add one only if clients truly need substitutable creation behavior. Often
a client should receive the finished `ShippingPolicy`, not a factory it never needed to know about.

---

## 9. Introduce different pressure: a workflow needs an extension point

Simple Factory fits runtime key-to-product selection. Factory Method addresses a different pressure.

Imagine a quote framework owns a stable workflow:

1. obtain a shipping policy;
2. construct checkout with it;
3. calculate the quote; and
4. return the total.

Different applications of that workflow need different policies. The workflow should remain fixed, while a subtype
supplies the product.

```java
abstract class QuoteWorkflow {
    final int quoteInCents(Order order) {
        ShippingPolicy policy = createShippingPolicy();
        var checkout = new CheckoutService(policy);
        return checkout.totalInCents(order);
    }

    protected abstract ShippingPolicy createShippingPolicy();
}
```

The creation operation is the **factory method**:

```java
protected abstract ShippingPolicy createShippingPolicy();
```

Concrete creators decide which product is returned:

```java
final class StandardQuoteWorkflow extends QuoteWorkflow {
    @Override
    protected ShippingPolicy createShippingPolicy() {
        return new StandardShipping();
    }
}

final class OvernightQuoteWorkflow extends QuoteWorkflow {
    @Override
    protected ShippingPolicy createShippingPolicy() {
        return new OvernightShipping();
    }
}
```

The client chooses a creator, and the creator workflow uses its product:

```java
QuoteWorkflow workflow = new OvernightQuoteWorkflow();
int quote = workflow.quoteInCents(order);
```

---

## 10. Name the GoF Factory Method pattern

Factory Method means:

> Define a creation operation in a creator abstraction, let subclasses decide which concrete product it returns, and
> have creator code work through the product contract.

```text
                  CREATOR HIERARCHY

                  QuoteWorkflow
                  + quoteInCents()
                  + createShippingPolicy()  <── factory method
                         ^             ^
                         |             |
            StandardQuoteWorkflow   OvernightQuoteWorkflow
                         |             |
                         v             v
                StandardShipping   OvernightShipping

                  PRODUCT HIERARCHY

                  ShippingPolicy
                         ^
                    concrete policies
```

The important collaboration is:

```text
QuoteWorkflow.quoteInCents()
        │
        ├── calls createShippingPolicy()
        │          │
        │          └── resolved by the concrete creator
        │
        └── uses the returned ShippingPolicy
```

### Roles

| Factory Method role                 | This example                                      |
|-------------------------------------|---------------------------------------------------|
| Product                             | `ShippingPolicy`                                  |
| Concrete products                   | `StandardShipping`, `OvernightShipping`           |
| Creator                             | `QuoteWorkflow`                                   |
| Factory method                      | `createShippingPolicy()`                          |
| Concrete creators                   | `StandardQuoteWorkflow`, `OvernightQuoteWorkflow` |
| Creator operation using the product | `quoteInCents(...)`                               |

This is also an example of a controlled extension hook: the base class owns the workflow, while subclasses fill in one
creation decision.

---

## 11. Simple Factory versus Factory Method

| Question                                             | Simple Factory                       | Factory Method                             |
|------------------------------------------------------|--------------------------------------|--------------------------------------------|
| Where is the choice made?                            | Inside one ordinary method/object    | Through overriding in a creator subtype    |
| Typical input                                        | Runtime key, enum, configuration     | Chosen creator subtype                     |
| Primary mechanism                                    | Composition plus conditional/map     | Inheritance plus dynamic dispatch          |
| Does adding a product change central selection code? | Usually yes                          | Often add a new creator subtype            |
| Is a creator workflow required?                      | No                                   | Yes                                        |
| Main strength                                        | Centralizes mapping and construction | Extends a stable framework workflow        |
| Main cost                                            | Central factory can grow             | Creator hierarchy and inheritance coupling |

### Selection flow comparison

Simple Factory:

```text
ShippingMethod ──> one factory switch ──> ShippingPolicy
```

Factory Method:

```text
chosen creator subtype ──> overridden creation method ──> ShippingPolicy
```

Factory Method does not automatically replace every Simple Factory. If a request contains `EXPRESS`, something may still
need to map that runtime value to either a product or a creator. A subtype hierarchy can merely move the selection
problem if the application does not already have a meaningful creator abstraction.

---

## 12. Test Factory Method without losing isolation

Test a concrete creator through its public workflow:

```java
var order = new Order(10, 10_000);
QuoteWorkflow workflow = new OvernightQuoteWorkflow();

check(workflow.quoteInCents(order) ==19_500,
        "overnight creator supplies overnight shipping");
```

Test the base workflow with a deterministic test creator:

```java
QuoteWorkflow fixedWorkflow = new QuoteWorkflow() {
    @Override
    protected ShippingPolicy createShippingPolicy() {
        return ignored -> 123;
    }
};

check(fixedWorkflow.quoteInCents(new Order(10, 10_000))==10_123,
        "base workflow uses the factory method product");
```

The anonymous subclass is useful here because the extension point is the thing under test. It supplies a tiny product
with a known result.

Keep the distinctions clear:

- test each shipping policy's calculation independently;
- test the creator workflow with a controlled product;
- test concrete creators to verify their creation choice; and
- add a small integration check for the assembled path.

---

## 13. Complete runnable lab

Create `src/Main.java` and paste this code:

```java
import java.util.Objects;

public class Main {
    public static void main(String[] args) {
        var order = new Order(10, 10_000);

        // Product behavior checks
        check(new StandardShipping().costInCents(order) == 2_000,
                "standard shipping calculation");
        check(new ExpressShipping().costInCents(order) == 5_000,
                "express shipping calculation");
        check(new OvernightShipping().costInCents(order) == 9_500,
                "overnight shipping calculation");

        // Simple Factory mapping checks
        check(ShippingPolicyFactory.create(ShippingMethod.STANDARD)
                        instanceof StandardShipping,
                "STANDARD maps to StandardShipping");
        check(ShippingPolicyFactory.create(ShippingMethod.EXPRESS)
                        instanceof ExpressShipping,
                "EXPRESS maps to ExpressShipping");
        check(ShippingPolicyFactory.create(ShippingMethod.OVERNIGHT)
                        instanceof OvernightShipping,
                "OVERNIGHT maps to OvernightShipping");
        expectThrows(NullPointerException.class,
                () -> ShippingPolicyFactory.create(null),
                "factory rejects a null method");

        // Factory product composed with the Strategy context
        var selectedPolicy = ShippingPolicyFactory.create(
                ShippingMethod.EXPRESS
        );
        var selectedCheckout = new CheckoutService(selectedPolicy);
        check(selectedCheckout.totalInCents(order) == 15_000,
                "factory product composes with checkout");

        // Context isolated from production products and factory
        ShippingPolicy fixedShipping = ignored -> 1_000;
        var isolatedCheckout = new CheckoutService(fixedShipping);
        check(isolatedCheckout.totalInCents(order) == 11_000,
                "checkout uses a supplied test policy");

        // Factory Method: concrete creator chooses the product
        QuoteWorkflow overnightWorkflow = new OvernightQuoteWorkflow();
        check(overnightWorkflow.quoteInCents(order) == 19_500,
                "overnight workflow creates overnight shipping");

        // Base creator workflow isolated with a test factory method
        QuoteWorkflow fixedWorkflow = new QuoteWorkflow() {
            @Override
            protected ShippingPolicy createShippingPolicy() {
                return ignored -> 123;
            }
        };
        check(fixedWorkflow.quoteInCents(order) == 10_123,
                "base workflow uses its factory method product");

        System.out.println("All Factory checks passed.");
    }

    private static void check(boolean condition, String description) {
        if (!condition) {
            throw new AssertionError("Failed: " + description);
        }
    }

    private static void expectThrows(
            Class<? extends Throwable> expectedType,
            Runnable action,
            String description
    ) {
        try {
            action.run();
        } catch (Throwable actual) {
            if (expectedType.isInstance(actual)) {
                return;
            }
            throw new AssertionError(
                    "Failed: " + description
                            + "; expected " + expectedType.getSimpleName()
                            + " but got " + actual.getClass().getSimpleName(),
                    actual
            );
        }

        throw new AssertionError(
                "Failed: " + description
                        + "; expected " + expectedType.getSimpleName()
        );
    }
}

record Order(int weightKg, int subtotalCents) {
    Order {
        if (weightKg < 0 || subtotalCents < 0) {
            throw new IllegalArgumentException(
                    "Order values cannot be negative"
            );
        }
    }
}

enum ShippingMethod {
    STANDARD,
    EXPRESS,
    OVERNIGHT
}

@FunctionalInterface
interface ShippingPolicy {
    int costInCents(Order order);
}

final class StandardShipping implements ShippingPolicy {
    @Override
    public int costInCents(Order order) {
        return order.weightKg() * 200;
    }
}

final class ExpressShipping implements ShippingPolicy {
    @Override
    public int costInCents(Order order) {
        return order.weightKg() * 400 + 1_000;
    }
}

final class OvernightShipping implements ShippingPolicy {
    @Override
    public int costInCents(Order order) {
        return order.weightKg() * 700 + 2_500;
    }
}

final class CheckoutService {
    private final ShippingPolicy shippingPolicy;

    CheckoutService(ShippingPolicy shippingPolicy) {
        this.shippingPolicy = Objects.requireNonNull(
                shippingPolicy,
                "shippingPolicy"
        );
    }

    int totalInCents(Order order) {
        return order.subtotalCents()
                + shippingPolicy.costInCents(order);
    }
}

// Simple Factory: one ordinary method owns runtime selection.
final class ShippingPolicyFactory {
    private ShippingPolicyFactory() {
    }

    static ShippingPolicy create(ShippingMethod method) {
        Objects.requireNonNull(method, "method");

        return switch (method) {
            case STANDARD -> new StandardShipping();
            case EXPRESS -> new ExpressShipping();
            case OVERNIGHT -> new OvernightShipping();
        };
    }
}

// Creator: owns a stable workflow that uses its factory method.
abstract class QuoteWorkflow {
    final int quoteInCents(Order order) {
        ShippingPolicy policy = Objects.requireNonNull(
                createShippingPolicy(),
                "createShippingPolicy() returned null"
        );
        return new CheckoutService(policy).totalInCents(order);
    }

    protected abstract ShippingPolicy createShippingPolicy();
}

// Concrete creator: decides which concrete product to return.
final class StandardQuoteWorkflow extends QuoteWorkflow {
    @Override
    protected ShippingPolicy createShippingPolicy() {
        return new StandardShipping();
    }
}

// Concrete creator: decides which concrete product to return.
final class OvernightQuoteWorkflow extends QuoteWorkflow {
    @Override
    protected ShippingPolicy createShippingPolicy() {
        return new OvernightShipping();
    }
}
```

Expected output:

```text
All Factory checks passed.
```

The lab uses stable Java features only. It does not require preview flags, a build tool, JUnit, or third-party
libraries.

---

## 14. Run the lab incrementally

Do not paste the final design and merely admire it. Build it in stages so each abstraction has a reason to exist.

### Stage 1 — Re-establish Strategy

Add these types first:

- `Order`
- `ShippingPolicy`
- the three concrete shipping policies
- `CheckoutService`

Construct `ExpressShipping` directly and verify the total. At this stage, direct construction is correct.

### Stage 2 — Expose the selection pressure

Add `ShippingMethod` and write the selection `switch` next to `main`. Duplicate it once in a second method to make the
maintenance problem visible, then remove the duplicate in Stage 3.

### Stage 3 — Extract the Simple Factory

Move the switch into `ShippingPolicyFactory.create`. Make both callers use it. Verify every enum value maps to the
intended concrete policy.

Observe that the conditional did not disappear; its ownership improved.

### Stage 4 — Keep checkout isolated

Test `CheckoutService` with a lambda returning a fixed shipping cost. This confirms that centralizing production
creation did not couple the Strategy context to the factory.

### Stage 5 — Add Factory Method for a creator workflow

Add `QuoteWorkflow`, put the stable quote algorithm in `quoteInCents`, and let `createShippingPolicy` be abstract. Add
`StandardQuoteWorkflow` and `OvernightQuoteWorkflow`.

Notice the changed reason for the abstraction: this is not a runtime enum mapping. It is an extension point in a
reusable workflow.

### Stage 6 — Test the hook

Create the anonymous `fixedWorkflow` from the complete lab. Its 123-cent product proves that the base workflow uses the
result of the factory method without depending on a production product.

---

## 15. Verified Java 25 and IntelliJ IDEA setup

The instructions in this section were checked on **September 1, 2026** using Oracle and JetBrains documentation only.

### Option A — Create and run the project in IntelliJ IDEA

JetBrains documents Java 25 support beginning with IntelliJ IDEA 2025.2. Use IntelliJ IDEA 2025.2 or a later release
with Java 25 support.

1. Open IntelliJ IDEA and select **New Project**, or use **File → New Project**.
2. Select **Java**.
3. Name the project `factory-pattern`.
4. Select **IntelliJ** as the build system. The lab has no external dependencies.
5. In **JDK**, select an installed JDK 25.
6. If JDK 25 is not configured:
    - choose **Download JDK**;
    - select version **25**;
    - select a vendor; and
    - confirm the download.
7. If needed, open **File → Project Structure → Project** and set:
    - **SDK:** JDK 25
    - **Language level:** `25 – Compact source files, module imports`
8. Under the project, create `src/Main.java` and paste the complete lab.
9. Select the green run icon beside `main`, then choose **Run 'Main.main()'**.
10. Confirm that the Run window prints `All Factory checks passed.`

JetBrains' official documentation covers the Java project flow, choosing or downloading JDK 25, and running a `main`
method. Its Java 25 setup article covers the project SDK and language-level settings:

-
JetBrains, [Create your first Java application](https://www.jetbrains.com/help/idea/creating-and-running-your-first-java-application.html)
- JetBrains, [Java 25 LTS and IntelliJ IDEA](https://blog.jetbrains.com/idea/2025/09/java-25-lts-and-intellij-idea/)
- JetBrains, [Supported Java versions and features](https://www.jetbrains.com/help/idea/supported-java-versions.html)

### Option B — Install JDK 25 separately

Oracle publishes JDK 25 installation procedures for Windows, macOS, and Linux in
the [JDK 25 Installation Guide](https://docs.oracle.com/en/java/javase/25/install/).

Follow the page for your operating system, then verify the runtime and compiler:

```shell
java --version
javac --version
```

Both outputs should identify version 25. If IntelliJ does not detect the installation, use **Add JDK from Disk** in its
JDK selector and choose the JDK home directory.

### Option C — Compile and run from a terminal

From the project root:

```shell
javac --release 25 -d out src/Main.java
java -cp out Main
```

Oracle documents that:

- `javac` compiles `.java` source into class files;
- `--release 25` compiles for the Java SE 25 language and documented API;
- `-d out` selects the class-output directory; and
- `java -cp out Main` places that directory on the class path and launches `Main`.

See Oracle's Java 25 command documentation:

- Oracle, [The `javac` command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)
- Oracle, [The `java` command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html)

### Troubleshooting

- **IntelliJ reports that records or switch expressions are unsupported:** verify that both the project SDK and language
  level are set to 25.
- **`javac` is not found:** install a full JDK, not only a runtime, and ensure the terminal can locate its `bin`
  directory. Alternatively, use IntelliJ's **Download JDK** flow.
- **The terminal and IDE report different versions:** IntelliJ's project SDK is configured separately from the terminal'
  s default JDK. Check both.
- **The compiler cannot find `src/Main.java`:** run the command from the project directory containing `src`, or adjust
  the path.
- **Do I need `--enable-preview`?** No. Every language feature used in this lab is stable in Java 25.

---

## 16. Extend the lab: add drone shipping

Add a new product:

```java
final class DroneShipping implements ShippingPolicy {
    @Override
    public int costInCents(Order order) {
        if (order.weightKg() > 5) {
            throw new IllegalArgumentException(
                    "Drone shipping supports at most 5 kg"
            );
        }
        return 2_000 + order.weightKg() * 500;
    }
}
```

Then make the smallest necessary changes:

1. Add `DRONE` to `ShippingMethod`.
2. Add one branch to `ShippingPolicyFactory`.
3. Add a factory mapping test.
4. Add product behavior tests for accepted and rejected weights.
5. Add `DroneQuoteWorkflow` only if a real creator-workflow use case exists.

### What should not change?

- `CheckoutService`
- existing shipping algorithms
- callers already using `ShippingPolicyFactory`
- `QuoteWorkflow`

### What this teaches

The Simple Factory does change when its authoritative mapping grows. That is not automatically a violation or a failure.
The goal is locality of change, not the impossible promise that no existing code ever changes.

Factory Method lets a new concrete creator extend a creator hierarchy without changing the base creator. But adding a
subtype solely to avoid editing one clear switch may cost more than it saves.

---

## 17. Design alternatives before adding a pattern

Factories are not the only way to assemble objects.

### Direct construction

```java
var checkout = new CheckoutService(new StandardShipping());
```

Best when the choice is obvious, local, and stable.

### Constructor injection

```java
final class CheckoutController {
    private final CheckoutService checkout;

    CheckoutController(CheckoutService checkout) {
        this.checkout = checkout;
    }
}
```

Best when an outer composition root already knows what to build. The controller does not need a factory if it always
uses one assembled service.

### Supplier

```java
import java.util.function.Supplier;

Supplier<ShippingPolicy> policySupplier = ExpressShipping::new;
ShippingPolicy policy = policySupplier.get();
```

Best for a small deferred-creation seam without a custom factory type.

### Map of suppliers

```java
import java.util.Map;
import java.util.function.Supplier;

Map<ShippingMethod, Supplier<ShippingPolicy>> creators = Map.of(
        ShippingMethod.STANDARD, StandardShipping::new,
        ShippingMethod.EXPRESS, ExpressShipping::new,
        ShippingMethod.OVERNIGHT, OvernightShipping::new
);
```

Best when registrations are data-like and lookup is the main behavior. It still needs policies for missing keys,
dependencies, and lifecycle.

### Dependency-injection container

Useful at a large application composition boundary when object graphs and lifecycles are already managed there. A
container relocates construction; it does not remove the need to understand ownership and selection.

Choose the smallest mechanism that makes the creation decision clear.

---

## 18. Trade-offs and failure modes

### Simple Factory is a good fit when

- several callers repeat the same key-to-product mapping;
- callers should know only the product contract;
- constructors or their dependencies change together;
- a runtime value selects one of a closed, understood set of products; or
- one testable location should own creation policy.

### Factory Method is a good fit when

- a base class or framework already owns a meaningful stable workflow;
- that workflow must use a product whose concrete type varies by extension;
- subclasses are natural domain or framework concepts, not artificial wrappers; or
- framework authors need a protected creation hook for application authors.

### Keep direct construction or a local conditional when

- there is one caller and one obvious product;
- the selection has only a few tiny, stable branches;
- constructors are simple and unlikely to change independently;
- no useful creator workflow exists;
- the new abstraction would only rename `new`; or
- following the creation path would become harder than reading it inline.

### Common failure modes

#### 1. The god factory

One factory creates shipping policies, repositories, controllers, loggers, reports, and unrelated services. Its cohesion
collapses, and every application change touches it.

Prefer factories with a focused product family or keep wiring in a clear composition root.

#### 2. Hiding dependencies

A static factory reaches into global state or service locators. Constructors look simple, but dependencies become
invisible and tests become order-dependent.

Prefer explicit constructor dependencies in an instance factory when creation needs collaborators.

#### 3. One factory interface per class

`ThingFactory.createThing()` wraps a single stable `new Thing()` call without selection, lifecycle, or complex assembly.
This adds navigation without containing change.

Keep the constructor.

#### 4. Subclass explosion

Every product gets a creator subclass even though there is no reusable creator workflow. The design doubles its class
count to avoid one readable mapping.

Prefer Simple Factory, a supplier, or direct construction.

#### 5. Putting business algorithms in the factory

The factory calculates shipping rather than constructing a `ShippingPolicy`. Creation and product behavior become
coupled again.

Keep algorithms in products; keep assembly in the factory.

#### 6. Assuming “open for extension” forbids all edits

A central enum-to-product mapping is supposed to change when its supported set changes. Editing one authoritative place
is often safer than registrations spread across modules.

Optimize for coherent, predictable change—not slogan compliance.

---

## 19. First-principles decision guide

Use this sequence instead of starting from a pattern name:

```text
Is construction simple, local, and stable?
        │
        ├── yes ──> construct directly
        │
        └── no
             │
             v
Is the same runtime key-to-product mapping duplicated?
        │
        ├── yes ──> consider Simple Factory
        │
        └── no
             │
             v
Does a meaningful creator workflow need a product-creation hook?
        │
        ├── yes ──> consider Factory Method
        │
        └── no
             │
             v
Would constructor injection, a Supplier, or clear composition-root code suffice?
        │
        ├── yes ──> use the smaller mechanism
        └── no  ──> identify the actual creation pressure again
```

### Review checklist

Before introducing a factory, verify:

- [ ] There is concrete creation knowledge worth containing.
- [ ] The product contract represents what clients actually need.
- [ ] Product behavior remains outside the factory.
- [ ] The chosen factory owns a cohesive product family.
- [ ] Dependencies and lifecycle remain explicit.
- [ ] Tests cover product behavior separately from creation mapping.
- [ ] Callers receive a product directly when they do not need deferred creation.
- [ ] Factory Method is backed by a real creator workflow.
- [ ] Inheritance costs less than the extension pressure it solves.
- [ ] Direct construction or a small conditional was considered honestly.

---

## 20. Mental model

Strategy and Factory solve adjacent but different design problems:

```text
external choice
      │
      v
Factory ──creates/selects──> Strategy ──performs algorithm──> result
      │                           │
      │                           └── isolates variable behavior
      └── isolates creation knowledge
```

The progression is:

```text
one algorithm
      ↓
several independently changing algorithms
      ↓
Strategy separates behavior behind a capability
      ↓
selection and construction become duplicated or complex
      ↓
Simple Factory centralizes that creation knowledge
      ↓
a reusable creator workflow needs an overridable creation hook
      ↓
Factory Method lets creator subtypes supply the product
```

The pattern is successful when the design makes change more local and responsibilities more legible—not when it contains
the largest number of interfaces and classes.

## Next lesson

Factory answers:

> Who owns selection and creation of the concrete collaborator?

As object graphs grow, a related question appears:

> How should dependencies be assembled and supplied without hiding them or coupling business code to construction?

That pressure leads naturally toward **Dependency Injection and composition roots**.

---

## Official verification sources

Only first-party Oracle and JetBrains sources were used to verify the Java 25 and IntelliJ IDEA instructions:

- Oracle, [JDK 25 Installation Guide](https://docs.oracle.com/en/java/javase/25/install/)
-
Oracle, [Overview of JDK Installation](https://docs.oracle.com/en/java/javase/25/install/overview-jdk-installation.html)
- Oracle, [The `javac` Command — Java 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)
- Oracle, [The `java` Command — Java 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html)
-
JetBrains, [Create your first Java application](https://www.jetbrains.com/help/idea/creating-and-running-your-first-java-application.html)
- JetBrains, [Supported Java versions and features](https://www.jetbrains.com/help/idea/supported-java-versions.html)
- JetBrains, [Java 25 LTS and IntelliJ IDEA](https://blog.jetbrains.com/idea/2025/09/java-25-lts-and-intellij-idea/)
