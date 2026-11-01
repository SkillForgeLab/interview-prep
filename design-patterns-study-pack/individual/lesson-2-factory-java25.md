[Skip to guide](#main)

DP / ENGINEERING LAB

Lesson 2
Factory

[01Begin with working code](#start)[02Create the pressure before the pattern](#pressure)[03Give creation one owner](#extract)[04Make the boundary explicit in Java](#types)[05Separate construction from use](#use)[06When constructors become architectural decisions](#construction)[07Test each responsibility separately](#tests)[08Add drone shipping and inspect the change](#drone)[09Derive Factory Method from a new pressure](#factory-method)[10Choose the smallest creation boundary](#distinctions)[11Use a registry when configuration is the pressure](#registry)[12Run the complete system](#run)[13Exercise: move creation out of payment use](#exercise)[14The thought process to carry forward](#review)[AShipping: complete source](#source-shipping)[BFactory Method: complete source](#source-workflow)[CPayment: reference solution](#source-payment)[Official references](#references)

Print / Save as PDFExpand answers & source

One HTML file. Works offline.
All source is embedded.

Lesson 02 / Design from first principles

# FactoryControlling object creation

Working code first. A real change next. Then a boundary that gives construction knowledge one owner.

Java 25 compatible3 complete labsNo dependencies

Problem → pressure → diagnosis → refactor → test → name → trade-offs

## How to use this guide

Read sections 1–8 in order and keep a Java editor open. Predict the effect of each change before you run it. Then derive Factory Method from its own pressure, examine the registry alternative, and complete the payment exercise.

You need basic Java methods, classes and interfaces. Records, enums, lambdas and switch expressions are explained where they appear. You do not need the previous lesson: the shipping model and Strategy foundation are rebuilt here.

For PDF: use **Print / Save as PDF**, portrait orientation, A4 or Letter, and disable the browser's own headers and footers. All answers and full source expand for printing. Reading needs no network; Java programs run locally with a JDK.

JavaScript is disabled. All lesson text and source remain readable. Copy source manually and use your browser’s print command.

### Contents

1. [01. Begin with working code](#start)
2. [02. Create the pressure before the pattern](#pressure)
3. [03. Give creation one owner](#extract)
4. [04. Make the boundary explicit in Java](#types)
5. [05. Separate construction from use](#use)
6. [06. When constructors become architectural decisions](#construction)
7. [07. Test each responsibility separately](#tests)
8. [08. Add drone shipping and inspect the change](#drone)
9. [09. Derive Factory Method from a new pressure](#factory-method)
10. [10. Choose the smallest creation boundary](#distinctions)
11. [11. Use a registry when configuration is the pressure](#registry)
12. [12. Run the complete system](#run)
13. [13. Exercise: move creation out of payment use](#exercise)
14. [14. The thought process to carry forward](#review)
15. [A. Shipping: complete source](#source-shipping)
16. [B. Factory Method: complete source](#source-workflow)
17. [C. Payment: reference solution](#source-payment)
18. [Official references](#references)

01 / Working baseline

## Begin with working code

Strategy gave checkout one capability: *calculate shipping for an order*. Standard, express and overnight policies implement that capability. Checkout can use any of them without knowing their formulas.

That leaves a concrete question: **who creates the policy for this request?** Imagine the request contains `shippingMethod: "express"`. The simplest controller selects the object and gives it to checkout.

Java · excerpt

```
static BigDecimal checkoutBefore(String method, Order order) {
    Objects.requireNonNull(method, "method");
    ShippingPolicy policy = switch (method) {
        case "standard" -> new StandardShipping();
        case "express" -> new ExpressShipping();
        case "overnight" -> new OvernightShipping();
        default -> throw new IllegalArgumentException(
                "Unknown shipping method: " + method);
    };
    return new CheckoutService(policy).total(order);
}
```

This works. One caller with three simple constructors does not automatically need another abstraction. A `switch` is a reasonable way to make a finite choice.

### Rebuild the foundation

Our order contains weight in kilograms and a subtotal. The shared contract returns the shipping charge. All examples use one fictional currency with two decimal places. The rates below are teaching data, not carrier prices.

| Policy | Teaching rule | Shipping for 5 kg |
| --- | --- | --- |
| Standard | weight × 2 | 10.00 |
| Express | weight × 4 + 10 | 30.00 |
| Overnight | weight × 7 + 25 | 60.00 |

Java · excerpt

```
record Order(BigDecimal weightKg, BigDecimal subtotal) {
    Order {
        Objects.requireNonNull(weightKg, "weightKg");
        Objects.requireNonNull(subtotal, "subtotal");
        if (weightKg.signum() <= 0 || subtotal.signum() < 0) {
            throw new IllegalArgumentException("Invalid order");
        }
        subtotal = subtotal.setScale(2, RoundingMode.UNNECESSARY);
    }
}

@FunctionalInterface
interface ShippingPolicy {
    BigDecimal calculate(Order order);
}

static BigDecimal decimal(String value) {
    return new BigDecimal(value);
}

static BigDecimal money(BigDecimal value) {
    return value.setScale(2, RoundingMode.HALF_UP);
}
```

The record supplies accessors such as `order.weightKg()`. Its compact constructor rejects nonpositive weight and negative subtotals, then requires the subtotal to be representable in cents. Records provide component-based data carriers; their component references are final, but arbitrary referenced objects need not be deeply immutable. Here the components are immutable `BigDecimal` values. [[2]](#ref-2)

Construct decimal constants from strings. The lab rounds the completed shipping charge to two places using `HALF_UP`; that is an explicit teaching rule. `UNNECESSARY` rejects a subtotal such as `100.001` instead of silently changing it. [[3]](#ref-3)

Java · excerpt

```
static final class StandardShipping implements ShippingPolicy {
    public BigDecimal calculate(Order order) {
        return money(order.weightKg().multiply(decimal("2.00")));
    }
}

static final class ExpressShipping implements ShippingPolicy {
    public BigDecimal calculate(Order order) {
        return money(order.weightKg().multiply(decimal("4.00"))
                .add(decimal("10.00")));
    }
}

static final class OvernightShipping implements ShippingPolicy {
    public BigDecimal calculate(Order order) {
        return money(order.weightKg().multiply(decimal("7.00"))
                .add(decimal("25.00")));
    }
}
```

`ShippingPolicy` promises a nonnegative charge in the same currency and at two decimal places for a valid order. These implementations meet that contract. Currency conversion, taxes and real carrier rules are outside this lab.

02 / Change and diagnosis

## Create the pressure before the pattern

Now an admin quote screen, an order service, an estimator and a scheduled job all need shipping policies. Each copies the selection code.

| Caller | Knowledge it now carries |
| --- | --- |
| Checkout controller | All concrete policy names and constructors |
| Admin quote controller | The same names and constructors |
| Order service | The same names and constructors |
| Shipping estimator | The same names and constructors |
| Scheduled job | The same names and constructors |

The next request is “add drone shipping.” One selection rule now needs edits in five places. A missed edit could make one entry point reject a method that another accepts.

**Diagnosis: duplicated construction knowledge**

The problem is the spread of knowledge about which class to create and how to build it. The number of `switch` statements is only a symptom.

Call this **change amplification**: one concept changes, but unrelated modules must be edited together. Count the places that own the decision, not merely the lines of code.

### Ask the design questions

1. What varies? The available shipping implementations and how they are constructed.
2. What is stable? Checkout adds a shipping charge to a subtotal.
3. What does stable code need? A `ShippingPolicy`.
4. What knowledge should have one owner? The method-to-object mapping and the construction recipe.

Pause: would extracting each shipping formula fix this new problem?

No. Strategy already extracted those formulas. Callers still duplicate selection and construction. We need a boundary around a different responsibility.

03 / First refactoring

## Give creation one owner

First move the existing string-based selection into a class with one method. Return the capability the caller needs.

Java · intermediate refactoring

```
static final class StringShippingFactory {
    ShippingPolicy create(String method) {
        Objects.requireNonNull(method, "method");
        return switch (method) {
            case "standard" -> new StandardShipping();
            case "express" -> new ExpressShipping();
            case "overnight" -> new OvernightShipping();
            default -> throw new IllegalArgumentException(
                    "Unknown shipping method: " + method);
        };
    }
}
```

Now callers ask for a policy. They no longer repeat concrete constructors. We have derived a **Simple Factory**: one place encapsulates object creation. Microsoft distinguishes this from Factory Method and Abstract Factory. [[1]](#ref-1)

The benefit is ownership. If a construction recipe changes, there is one deliberate place to update it. A static function could provide the same boundary; the extra class is not the essence of the design.

| Responsibility | Owner |
| --- | --- |
| Decode and validate a request value | Request boundary |
| Select and construct a shipping policy | Factory |
| Calculate a shipping charge | Shipping policy |
| Add the charge to the subtotal | Checkout service |

Pause: did we remove the selection decision?

No. We gave it one owner. Every caller delegates to that owner. Removing all conditionals was never a requirement.

04 / Typed input

## Make the boundary explicit in Java

A factory accepting any string still permits typos in internal code. Introduce an enum for the methods supported by this application, and translate external text at the edge.

Java · excerpt

```
enum ShippingMethod {
    STANDARD, EXPRESS, OVERNIGHT;

    static ShippingMethod fromRequest(String raw) {
        if (raw == null) {
            throw new IllegalArgumentException("Missing shipping method");
        }
        return switch (raw.strip().toLowerCase(Locale.ROOT)) {
            case "standard" -> STANDARD;
            case "express" -> EXPRESS;
            case "overnight" -> OVERNIGHT;
            default -> throw new IllegalArgumentException(
                    "Unknown shipping method: " + raw);
        };
    }
}
```

The parser deliberately accepts surrounding whitespace and mixed case. `Locale.ROOT` makes case conversion independent of the user's locale. Unknown, blank and missing values fail explicitly. [[7]](#ref-7)

The factory now accepts only the domain type:

Java · excerpt

```
static final class ShippingPolicyFactory {
    ShippingPolicy create(ShippingMethod method) {
        Objects.requireNonNull(method, "method");
        return switch (method) {
            case STANDARD -> new StandardShipping();
            case EXPRESS -> new ExpressShipping();
            case OVERNIGHT -> new OvernightShipping();
        };
    }
}
```

This enum `switch` expression covers every constant, so it needs no `default`. Add an enum constant and recompile the source: the incomplete factory switch becomes a compiler error. We reject `null` explicitly because an enum reference can still be null. [[4]](#ref-4)

Java · excerpt

```
factory.create(ShippingMethod.EXPRESS); // Valid
// factory.create("banana");           // Does not compile
// factory.create(null);               // Compiles, then throws
```

**Types do not validate an HTTP request**

JSON text is external data. Parse it before constructing the domain object. In a real HTTP adapter, translate an invalid method into the application’s client-error response. An enum alone does not do that work.

The parser and factory contain different mappings. One maps public request vocabulary to a domain value; the other maps that value to an implementation. A new method may require both to change. Localized change does not mean exactly one edited file.

05 / Object composition

## Separate construction from use

Checkout's job is to combine a subtotal and a shipping charge. It receives the policy it will use:

Java · excerpt

```
static final class CheckoutService {
    private final ShippingPolicy shipping;

    CheckoutService(ShippingPolicy shipping) {
        this.shipping = Objects.requireNonNull(shipping, "shipping");
    }

    BigDecimal total(Order order) {
        Objects.requireNonNull(order, "order");
        return order.subtotal().add(shipping.calculate(order));
    }
}
```

The field is final, so this checkout object keeps the policy chosen at construction. This is constructor injection using plain Java. A dependency-injection framework is not required.

Wire the objects at the application boundary. This small method stands in for a controller; the demo creates ordinary objects and does not run an HTTP server.

Java · excerpt

```
static BigDecimal checkout(String rawMethod, Order order) {
    ShippingMethod method = ShippingMethod.fromRequest(rawMethod);
    var factory = new ShippingPolicyFactory();
    ShippingPolicy policy = factory.create(method);
    var service = new CheckoutService(policy);
    return service.total(order);
}
```

| At runtime | What happens |
| --- | --- |
| 1. Parse | `"express"` becomes `ShippingMethod.EXPRESS`. |
| 2. Construct | The factory returns an `ExpressShipping` through the `ShippingPolicy` interface. |
| 3. Compose | The boundary supplies that policy to `CheckoutService`. |
| 4. Use | Checkout calls `calculate(order)`; the express implementation runs. |

The boundary knows the factory and the interface. The factory knows concrete classes. Checkout only needs the policy contract. A different boundary can select a different policy without rewriting checkout.

Pause: should CheckoutService ask a global factory for its policy?

For this design, that would hide its dependency and mix selection with use again. Passing the policy makes the service’s requirement visible and makes substitution straightforward.

06 / Growing construction pressure

## When constructors become architectural decisions

A zero-argument constructor is cheap to repeat. Real construction may involve a maps client, a pricing repository, a surcharge provider and a logger. Now a caller would need to know which implementations to use, which configuration to supply and which dependencies are shared.

Java · conceptual sketch, not a runnable lab fragment

```
// Construction sketch only: these collaborator types are not in the lab.
var policy = new ExpressShipping(
        new DistanceCalculator(mapsClient),
        pricingRepository,
        fuelSurchargeProvider,
        logger);
```

Put that recipe in the creation boundary. Supply already configured long-lived collaborators to the factory from the application's startup code. The factory can then build policies using those collaborators.

**Creation also raises a lifetime question**

The lab returns a fresh, stateless policy on each call. A factory can instead return a shared instance, but sharing introduces state and concurrency questions. The name “factory” does not promise either fresh or cached objects.

Keep resource ownership explicit. If startup creates a database pool or network client, startup should arrange its shutdown. Moving a constructor into a factory does not by itself solve configuration, lifecycle or error handling.

The practical test is whether the caller should carry this construction knowledge. If it obscures the caller's own job or is repeated across entry points, isolate it.

07 / Verification

## Test each responsibility separately

Use a different question for each boundary. A factory-selection test is allowed to name a concrete type because choosing that type is the behavior under test. Checkout tests should not depend on which production policy is chosen.

| Test | Question | Example expectation |
| --- | --- | --- |
| Request parser | Which external values are accepted? | `" Express "` becomes `EXPRESS`; `"banana"` is rejected. |
| Factory | Was the intended implementation selected? | `EXPRESS` produces `ExpressShipping`. |
| Strategy | Is the price calculation correct? | 5 kg express shipping costs 30.00. |
| Checkout | Does orchestration use its dependency? | A fake charge of 10.00 makes a 100.00 subtotal total 110.00. |
| Composition | Do the pieces cooperate? | External `"express"` produces total 130.00. |

Java · excerpt

```
var order = new Order(decimal("5"), decimal("100.00"));
var factory = new ShippingPolicyFactory();

check(factory.create(ShippingMethod.EXPRESS)
        instanceof ExpressShipping, "Express selection");
amount("30.00", new ExpressShipping().calculate(order));

ShippingPolicy fake = ignored -> decimal("10.00");
amount("110.00", new CheckoutService(fake).total(order));
amount("130.00", checkout("express", order));
```

The lambda works because `ShippingPolicy` has one abstract method. It supplies a predictable test implementation. The full file defines `check`, `amount` and `rejects`; these checks throw on failure and do not require `-ea` or a test-library download. [[8]](#ref-8)

`amount` uses `BigDecimal.compareTo` for numeric equality, so `30.0` and `30.00` compare as the same amount. `equals` also compares scale. [[3]](#ref-3)

### Trace one request

Change a method and weight. The subtotal stays at 100.00. This browser calculation illustrates the Java lab; it does not execute Java.

Shipping methodStandardExpressOvernight
Weight in kilograms1 kg5 kg10 kg20 kg

**EXPRESS → ExpressShipping**Shipping: 5 × 4 + 10 = 30.00Checkout: 100.00 + 30.00 = **130.00**

Worked example: EXPRESS selects ExpressShipping. At 5 kg, shipping is 5 × 4 + 10 = 30.00. Checkout is 100.00 + 30.00 = 130.00.

08 / Locality of change

## Add drone shipping and inspect the change

Keep this extension separate from the baseline lab. Implement the new calculation first:

Java · excerpt

```
static final class DroneShipping implements ShippingPolicy {
    public BigDecimal calculate(Order order) {
        return money(order.weightKg().multiply(decimal("5.00"))
                .add(decimal("20.00")));
    }
}
```

Then add the domain value and update the boundaries that own its meaning:

| Location | Edit |
| --- | --- |
| `ShippingMethod` | Add `DRONE`. |
| `fromRequest` | Add `case "drone" -> DRONE;` |
| `ShippingPolicyFactory` | Add `case DRONE -> new DroneShipping();` |
| Tests | Test parsing, selection, 45.00 shipping at 5 kg, and total 145.00. |
| Optional registry | If you retain the registry example, register `DroneShipping::new` too. |

`CheckoutService` needs no edit. Existing policy algorithms also stay intact. The illustrative `checkoutBefore` method intentionally remains the old version: it demonstrates why the original design needed repeated edits.

Try it: what should happen after adding DRONE to the enum but before updating the factory?

Recompilation should fail because the enum switch expression is incomplete. Once the factory is updated, the optional registry still needs its new entry: its constructor checks completeness at runtime.

### What about the Open/Closed Principle?

In this design, checkout is insulated from new shipping implementations by its interface. The factory is deliberately responsible for the supported implementation set. Editing its mapping is an intentional trade-off.

“Never modify existing code” is too blunt a rule to guide this decision. Ask whether the change stays with the owner of the knowledge and whether stable clients remain insulated. User interfaces, API schemas or configuration may still need deliberate updates to expose a new option.

09 / A different variation point

## Derive Factory Method from a new pressure

Now consider a shipping-document workflow: validate an order, create a carrier-specific label, then save the label. Validation and saving are shared. The concrete label product varies with the workflow subclass.

Define the product capability first. These carrier names label local teaching objects; there are no carrier API calls or real shipping labels.

Java · excerpt

```
record Order(String id) {}

interface ShippingLabel {
    String render();
}

// Local teaching objects; these do not call carrier APIs.
record FedExLabel(String orderId) implements ShippingLabel {
    public String render() { return "FedEx label: " + orderId; }
}

record UpsLabel(String orderId) implements ShippingLabel {
    public String render() { return "UPS label: " + orderId; }
}
```

Keep the shared process in a base class. Give subclasses one creation hook:

Java · excerpt

```
abstract static class ShippingWorkflow {
    private final Consumer<ShippingLabel> save;

    ShippingWorkflow(Consumer<ShippingLabel> save) {
        this.save = Objects.requireNonNull(save, "save");
    }

    final ShippingLabel process(Order order) {
        Objects.requireNonNull(order, "order");
        if (order.id() == null || order.id().isBlank()) {
            throw new IllegalArgumentException("Missing order id");
        }
        ShippingLabel label = Objects.requireNonNull(
                createLabel(order), "label");
        save.accept(label);
        return label;
    }

    protected abstract ShippingLabel createLabel(Order order);
}
```

The `final` process method preserves the operation order. `createLabel` is the **Factory Method**: a subclass supplies the concrete product. The injected `Consumer` is a saving callback; the runnable lab uses an in-memory list.

Java · excerpt

```
static final class FedExWorkflow extends ShippingWorkflow {
    FedExWorkflow(Consumer<ShippingLabel> save) { super(save); }

    @Override
    protected ShippingLabel createLabel(Order order) {
        return new FedExLabel(order.id());
    }
}

static final class UpsWorkflow extends ShippingWorkflow {
    UpsWorkflow(Consumer<ShippingLabel> save) { super(save); }

    @Override
    protected ShippingLabel createLabel(Order order) {
        return new UpsLabel(order.id());
    }
}
```

At the boundary, `new FedExWorkflow(saved::add)` chooses a workflow. Inside `process`, the virtual call to `createLabel` reaches that subclass. The base workflow then uses the returned `ShippingLabel`.

**Two related ideas appear in the same example**

`process` has the shape of Template Method: a stable algorithm with an overridable step. That step is specifically about creating a product, so `createLabel` serves as Factory Method. The names describe different roles.

This is useful when a workflow hierarchy already provides a meaningful extension point. If label creation is the only variation, injecting a `Function<Order, ShippingLabel>` may be simpler than introducing subclasses. The pressure should justify the inheritance.

10 / Terminology and trade-offs

## Choose the smallest creation boundary

| Design | Who chooses the product? | Use when | Cost |
| --- | --- | --- | --- |
| Direct construction | The caller | One obvious recipe in one suitable location | Caller knows the concrete class |
| Simple Factory | A centralized function or object | Several callers need the same selection or wiring | A mapping and an extra hop |
| GoF Factory Method | An overridden creator method in a subclass | A base workflow needs subclasses to determine a product | Inheritance and more types |
| Supplier registry | A registered creation function | Wiring varies with configuration | Registration and completeness checks |

Simple Factory and GoF Factory Method are different concepts. A method called `create`, or a static method returning an object, is not automatically the GoF pattern. Abstract Factory addresses families of related products; it is outside this lesson's implementation. [[1]](#ref-1)

### When not to add a factory

* There is one simple implementation and one suitable construction site.
* The factory would only wrap `new` without hiding useful knowledge.
* It introduces a hierarchy merely to avoid one controlled selection.
* The caller actually needs to choose and configure a concrete object directly.

Prefer the simplest design that contains the change you can explain. An extra abstraction has to earn its navigation, wiring and debugging cost.

11 / Alternative implementation

## Use a registry when configuration is the pressure

Suppose startup configuration supplies the available construction recipes. Replace the hard-coded factory switch with a map from the enum to a `Supplier<ShippingPolicy>`. A supplier provides a value through `get()`. Constructor references such as `ExpressShipping::new` act as creation functions. [[5]](#ref-5)

Java · excerpt

```
static final class RegistryShippingFactory {
    private final Map<ShippingMethod, Supplier<ShippingPolicy>> creators;

    RegistryShippingFactory(
            Map<ShippingMethod, Supplier<ShippingPolicy>> creators) {
        this.creators = Map.copyOf(creators);
        if (!this.creators.keySet().equals(
                EnumSet.allOf(ShippingMethod.class))) {
            throw new IllegalArgumentException("Incomplete registry");
        }
    }

    ShippingPolicy create(ShippingMethod method) {
        Objects.requireNonNull(method, "method");
        return Objects.requireNonNull(
                creators.get(method).get(), "Supplier returned null");
    }
}

static RegistryShippingFactory configuredRegistry() {
    var creators = new EnumMap<ShippingMethod,
            Supplier<ShippingPolicy>>(ShippingMethod.class);
    creators.put(ShippingMethod.STANDARD, StandardShipping::new);
    creators.put(ShippingMethod.EXPRESS, ExpressShipping::new);
    creators.put(ShippingMethod.OVERNIGHT, OvernightShipping::new);
    return new RegistryShippingFactory(creators);
}
```

`EnumMap` is a map specialized for enum keys. The registry copies its input so later map edits do not change its configuration. This copy is shallow: objects captured by suppliers can still have state. [[6]](#ref-6)[[10]](#ref-10)

Unlike an exhaustive switch, a Java map literal does not make the compiler require every enum key. The constructor checks completeness at startup and rejects missing entries. It also rejects a supplier that returns null when invoked.

The registry shown here still has a *closed* enum vocabulary. It is not an open-ended plugin system: adding a new method still needs source edits to the enum and request parser. A dynamically extensible identifier scheme would be a separate design decision.

**Supplier does not mean “fresh instance”**

These constructor references create fresh objects. A supplier could return a cached object instead. The Supplier contract does not require a distinct result on each invocation. [[5]](#ref-5)

The boundary is the same: request a capability and let one owner handle construction. Switching from a conditional to a map changes the implementation technique, not the underlying responsibility.

12 / Complete runnable labs

## Run the complete system

The full files are embedded below. Use the download buttons in a browser or copy the complete source from the appendices. Save each under its displayed filename in one folder.

Download shipping labDownload workflow lab

Use a JDK, which includes `javac`. Check that both commands report version 25, then compile and run. These files use standard Java syntax and APIs with no preview flags or external dependencies. `--release 25` selects Java 25's language and API target. [[9]](#ref-9)

Terminal · run from the folder containing the source files

```
java -version
javac -version
javac --release 25 -Xlint:all FactoryLesson.java FactoryMethodLesson.java
java FactoryLesson
java FactoryMethodLesson
```

### Expected output

```
Checkout total: 130.00
All shipping checks passed.
FedEx label: ORD-42
UPS label: ORD-42
All workflow checks passed.
```

The main shipping path is the original 5 kg order with a 100.00 subtotal. The full file also runs the baseline version, the registry alternative and checks for invalid input, invalid orders and rounding.

**Verification note.** All three embedded Java files were compiled with `-Xlint:all` and run successfully on OpenJDK 17.0.20. They use features and APIs available in Java 25, verified against the official Java 25 references below. A Java 25 runtime was unavailable for execution in the authoring environment.

### What the source layout means

To keep each download independent, related classes are nested in one public lab class. `static` nested classes need no enclosing lab instance. This packaging is for a runnable lesson; a larger application can place the types in separate files. Snippets are excerpts and omit the imports or enclosing class unless shown.

13 / Hands-on practice

## Exercise: move creation out of payment use

Your payment entry point currently selects a concrete processor and calls it. These are local processor stubs; the exercise does not integrate payment providers or move money.

Java · starting method; processor stubs are in Appendix C

```
static String pay(String method, BigDecimal amount) {
    Objects.requireNonNull(method, "method");
    return switch (method) {
        case "card" -> new StripeCardProcessor().pay(amount);
        case "paypal" -> new PayPalProcessor().pay(amount);
        case "bank" -> new BankTransferProcessor().pay(amount);
        default -> throw new IllegalArgumentException(
                "Unknown payment method: " + method);
    };
}
```

### Work through the decisions

1. Identify the changing knowledge: processor selection and construction.
2. Define `PaymentProcessor` as the capability to execute `pay(amount)`.
3. Make `PaymentService` receive that capability in its constructor.
4. Create `PaymentMethod` and a request parser.
5. Give `PaymentProcessorFactory` the mapping from method to processor.
6. Compose the parser, factory and service at the entry point.
7. Test parsing, selection, each stub's behavior, and service delegation separately.

### Acceptance checklist

[ ]  PaymentService never names StripeCardProcessor.
[ ]  PaymentService contains no selection switch.
[ ]  Each processor can be tested independently.
[ ]  Factory selection can be tested independently.
[ ]  Adding crypto needs no PaymentService edit.
[ ]  Unknown methods and invalid amounts fail explicitly.

Checklist ticks are for this open page only; they are not saved.

Hint: what should PaymentService depend on?

Only `PaymentProcessor`. Its payment method validates the amount and delegates to the supplied processor. Request strings and concrete processor classes belong elsewhere.

Review: how would you add crypto?

Add a `CryptoProcessor`, a `CRYPTO` enum value, the external text mapping, and the factory branch. Add selection and processor tests. The service remains unchanged because the payment capability is unchanged.

Try the refactoring before opening [Appendix C](#source-payment). The reference solution uses strings as fake receipts to keep attention on dependencies.

Download payment solution

Terminal

```
javac --release 25 -Xlint:all PaymentSolution.java
java PaymentSolution
```

```
card:25.00
All payment checks passed.
```

14 / Design review

## The thought process to carry forward

| Ask while coding | What the answer tells you |
| --- | --- |
| Who knows the concrete classes? | Where construction decisions currently live. |
| Should those callers know? | Whether use and construction have become mixed. |
| Is the same recipe copied? | Whether one change will spread across unrelated modules. |
| What does the consumer actually need? | The capability to place at the dependency boundary. |
| Who should own creation? | A suitable factory or composition boundary. |
| What extra cost did I introduce? | Whether the abstraction earns its complexity. |

**Strategy** isolates interchangeable behavior. **Factory** isolates selection and construction. They often cooperate, but solve different change problems.

### Next pressure: an incompatible provider API

A third-party client returns a quote using a postal code and a weight in grams, while checkout expects `ShippingPolicy.calculate(order)`. Our current order model would also need a destination at the appropriate boundary.

Once the required data is present, an Adapter can translate our request and the provider's response. That is the next lesson: derive a boundary from incompatible interfaces, then implement it.

A / Source appendix

## Shipping: complete source

Includes the baseline, typed factory, strategies, checkout, optional registry and executable checks. Copy all consecutive blocks into `FactoryLesson.java`; they form one complete file.

Complete source: FactoryLesson.java

Download FactoryLesson.javaCopy complete file

FactoryLesson.java · lines 1–40

```
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.function.Supplier;

public final class FactoryLesson {
    record Order(BigDecimal weightKg, BigDecimal subtotal) {
        Order {
            Objects.requireNonNull(weightKg, "weightKg");
            Objects.requireNonNull(subtotal, "subtotal");
            if (weightKg.signum() <= 0 || subtotal.signum() < 0) {
                throw new IllegalArgumentException("Invalid order");
            }
            subtotal = subtotal.setScale(2, RoundingMode.UNNECESSARY);
        }
    }

    @FunctionalInterface
    interface ShippingPolicy {
        BigDecimal calculate(Order order);
    }

    static BigDecimal decimal(String value) {
        return new BigDecimal(value);
    }

    static BigDecimal money(BigDecimal value) {
        return value.setScale(2, RoundingMode.HALF_UP);
    }

    static final class StandardShipping implements ShippingPolicy {
        public BigDecimal calculate(Order order) {
            return money(order.weightKg().multiply(decimal("2.00")));
        }
    }
```

FactoryLesson.java · lines 41–82

```
    static final class ExpressShipping implements ShippingPolicy {
        public BigDecimal calculate(Order order) {
            return money(order.weightKg().multiply(decimal("4.00"))
                    .add(decimal("10.00")));
        }
    }

    static final class OvernightShipping implements ShippingPolicy {
        public BigDecimal calculate(Order order) {
            return money(order.weightKg().multiply(decimal("7.00"))
                    .add(decimal("25.00")));
        }
    }

    static final class CheckoutService {
        private final ShippingPolicy shipping;

        CheckoutService(ShippingPolicy shipping) {
            this.shipping = Objects.requireNonNull(shipping, "shipping");
        }

        BigDecimal total(Order order) {
            Objects.requireNonNull(order, "order");
            return order.subtotal().add(shipping.calculate(order));
        }
    }

    static BigDecimal checkoutBefore(String method, Order order) {
        Objects.requireNonNull(method, "method");
        ShippingPolicy policy = switch (method) {
            case "standard" -> new StandardShipping();
            case "express" -> new ExpressShipping();
            case "overnight" -> new OvernightShipping();
            default -> throw new IllegalArgumentException(
                    "Unknown shipping method: " + method);
        };
        return new CheckoutService(policy).total(order);
    }

    enum ShippingMethod {
        STANDARD, EXPRESS, OVERNIGHT;
```

FactoryLesson.java · lines 83–118

```
        static ShippingMethod fromRequest(String raw) {
            if (raw == null) {
                throw new IllegalArgumentException("Missing shipping method");
            }
            return switch (raw.strip().toLowerCase(Locale.ROOT)) {
                case "standard" -> STANDARD;
                case "express" -> EXPRESS;
                case "overnight" -> OVERNIGHT;
                default -> throw new IllegalArgumentException(
                        "Unknown shipping method: " + raw);
            };
        }
    }

    static final class ShippingPolicyFactory {
        ShippingPolicy create(ShippingMethod method) {
            Objects.requireNonNull(method, "method");
            return switch (method) {
                case STANDARD -> new StandardShipping();
                case EXPRESS -> new ExpressShipping();
                case OVERNIGHT -> new OvernightShipping();
            };
        }
    }

    static BigDecimal checkout(String rawMethod, Order order) {
        ShippingMethod method = ShippingMethod.fromRequest(rawMethod);
        var factory = new ShippingPolicyFactory();
        ShippingPolicy policy = factory.create(method);
        var service = new CheckoutService(policy);
        return service.total(order);
    }

    static final class RegistryShippingFactory {
        private final Map<ShippingMethod, Supplier<ShippingPolicy>> creators;
```

FactoryLesson.java · lines 119–152

```
        RegistryShippingFactory(
                Map<ShippingMethod, Supplier<ShippingPolicy>> creators) {
            this.creators = Map.copyOf(creators);
            if (!this.creators.keySet().equals(
                    EnumSet.allOf(ShippingMethod.class))) {
                throw new IllegalArgumentException("Incomplete registry");
            }
        }

        ShippingPolicy create(ShippingMethod method) {
            Objects.requireNonNull(method, "method");
            return Objects.requireNonNull(
                    creators.get(method).get(), "Supplier returned null");
        }
    }

    static RegistryShippingFactory configuredRegistry() {
        var creators = new EnumMap<ShippingMethod,
                Supplier<ShippingPolicy>>(ShippingMethod.class);
        creators.put(ShippingMethod.STANDARD, StandardShipping::new);
        creators.put(ShippingMethod.EXPRESS, ExpressShipping::new);
        creators.put(ShippingMethod.OVERNIGHT, OvernightShipping::new);
        return new RegistryShippingFactory(creators);
    }

    static void check(boolean condition, String name) {
        if (!condition) throw new AssertionError(name);
    }

    static void amount(String expected, BigDecimal actual) {
        check(decimal(expected).compareTo(actual) == 0,
                "Expected " + expected + ", got " + actual);
    }
```

FactoryLesson.java · lines 153–196

```
    static void rejects(Class<? extends RuntimeException> expected,
                        Runnable action) {
        try {
            action.run();
        } catch (RuntimeException error) {
            check(expected.isInstance(error), "Unexpected exception");
            return;
        }
        throw new AssertionError("Expected " + expected.getSimpleName());
    }

    static void runChecks() {
        var order = new Order(decimal("5"), decimal("100.00"));
        var factory = new ShippingPolicyFactory();
        check(factory.create(ShippingMethod.STANDARD)
                instanceof StandardShipping, "Standard selection");
        check(factory.create(ShippingMethod.EXPRESS)
                instanceof ExpressShipping, "Express selection");
        check(factory.create(ShippingMethod.OVERNIGHT)
                instanceof OvernightShipping, "Overnight selection");
        amount("10.00", new StandardShipping().calculate(order));
        amount("30.00", new ExpressShipping().calculate(order));
        amount("60.00", new OvernightShipping().calculate(order));
        amount("110.00", new CheckoutService(o -> decimal("10.00"))
                .total(order));
        amount("130.00", checkout(" Express ", order));
        amount("130.00", checkoutBefore("express", order));
        var registry = configuredRegistry();
        for (var method : ShippingMethod.values()) {
            check(registry.create(method).getClass()
                    == factory.create(method).getClass(), "Registry selection");
        }
        amount("30.00", registry.create(ShippingMethod.EXPRESS)
                .calculate(order));
        amount("2.47", new StandardShipping().calculate(
                new Order(decimal("1.235"), decimal("0"))));
        amount("2.48", new StandardShipping().calculate(
                new Order(decimal("1.2375"), decimal("0"))));
        rejects(IllegalArgumentException.class,
                () -> ShippingMethod.fromRequest("banana"));
        rejects(IllegalArgumentException.class,
                () -> ShippingMethod.fromRequest(" "));
        rejects(IllegalArgumentException.class,
                () -> ShippingMethod.fromRequest(null));
```

FactoryLesson.java · lines 197–214

```
        rejects(NullPointerException.class, () -> factory.create(null));
        rejects(IllegalArgumentException.class,
                () -> new Order(decimal("0"), decimal("100")));
        rejects(IllegalArgumentException.class,
                () -> new Order(decimal("5"), decimal("-1")));
        rejects(ArithmeticException.class,
                () -> new Order(decimal("5"), decimal("100.001")));
        rejects(IllegalArgumentException.class,
                () -> new RegistryShippingFactory(Map.of()));
    }

    public static void main(String[] args) {
        var order = new Order(decimal("5"), decimal("100.00"));
        System.out.println("Checkout total: " + checkout("express", order));
        runChecks();
        System.out.println("All shipping checks passed.");
    }
}
```

B / Source appendix

## Factory Method: complete source

A standalone workflow with local carrier labels, an in-memory saving callback and checks. Copy all consecutive blocks into `FactoryMethodLesson.java`; they form one complete file.

Complete source: FactoryMethodLesson.java

Download FactoryMethodLesson.javaCopy complete file

FactoryMethodLesson.java · lines 1–42

```
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;

public final class FactoryMethodLesson {
    record Order(String id) {}

    interface ShippingLabel {
        String render();
    }

    // Local teaching objects; these do not call carrier APIs.
    record FedExLabel(String orderId) implements ShippingLabel {
        public String render() { return "FedEx label: " + orderId; }
    }

    record UpsLabel(String orderId) implements ShippingLabel {
        public String render() { return "UPS label: " + orderId; }
    }

    abstract static class ShippingWorkflow {
        private final Consumer<ShippingLabel> save;

        ShippingWorkflow(Consumer<ShippingLabel> save) {
            this.save = Objects.requireNonNull(save, "save");
        }

        final ShippingLabel process(Order order) {
            Objects.requireNonNull(order, "order");
            if (order.id() == null || order.id().isBlank()) {
                throw new IllegalArgumentException("Missing order id");
            }
            ShippingLabel label = Objects.requireNonNull(
                    createLabel(order), "label");
            save.accept(label);
            return label;
        }

        protected abstract ShippingLabel createLabel(Order order);
    }
```

FactoryMethodLesson.java · lines 43–86

```
    static final class FedExWorkflow extends ShippingWorkflow {
        FedExWorkflow(Consumer<ShippingLabel> save) { super(save); }

        @Override
        protected ShippingLabel createLabel(Order order) {
            return new FedExLabel(order.id());
        }
    }

    static final class UpsWorkflow extends ShippingWorkflow {
        UpsWorkflow(Consumer<ShippingLabel> save) { super(save); }

        @Override
        protected ShippingLabel createLabel(Order order) {
            return new UpsLabel(order.id());
        }
    }

    static void check(boolean condition, String name) {
        if (!condition) throw new AssertionError(name);
    }

    public static void main(String[] args) {
        List<ShippingLabel> saved = new ArrayList<>();
        var order = new Order("ORD-42");
        ShippingWorkflow fedEx = new FedExWorkflow(saved::add);
        ShippingWorkflow ups = new UpsWorkflow(saved::add);
        ShippingLabel first = fedEx.process(order);
        ShippingLabel second = ups.process(order);
        check(first instanceof FedExLabel, "FedEx product");
        check(second instanceof UpsLabel, "UPS product");
        check(first.render().equals("FedEx label: ORD-42"), "Order forwarded");
        check(saved.size() == 2 && saved.get(0) == first
                && saved.get(1) == second, "Products saved once in order");
        boolean rejected = false;
        try {
            fedEx.process(new Order(" "));
        } catch (IllegalArgumentException expected) {
            rejected = true;
        }
        check(rejected && saved.size() == 2, "Reject before saving");
        System.out.println(first.render());
        System.out.println(second.render());
        System.out.println("All workflow checks passed.");
```

FactoryMethodLesson.java · lines 87–88

```
    }
}
```

C / Source appendix

## Payment: reference solution

Open after trying the exercise. All processors are local stubs. Copy all consecutive blocks into `PaymentSolution.java`; they form one complete file.

Complete source: PaymentSolution.java

Download PaymentSolution.javaCopy complete file

PaymentSolution.java · lines 1–41

```
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Locale;
import java.util.Objects;

public final class PaymentSolution {
    enum PaymentMethod {
        CARD, PAYPAL, BANK;

        static PaymentMethod fromRequest(String raw) {
            if (raw == null) {
                throw new IllegalArgumentException("Missing payment method");
            }
            return switch (raw.strip().toLowerCase(Locale.ROOT)) {
                case "card" -> CARD;
                case "paypal" -> PAYPAL;
                case "bank" -> BANK;
                default -> throw new IllegalArgumentException(
                        "Unknown payment method: " + raw);
            };
        }
    }

    @FunctionalInterface
    interface PaymentProcessor {
        String pay(BigDecimal amount);
    }

    // Local stubs only: no SDKs, network calls or real payments.
    static final class StripeCardProcessor implements PaymentProcessor {
        public String pay(BigDecimal amount) { return "card:" + amount; }
    }

    static final class PayPalProcessor implements PaymentProcessor {
        public String pay(BigDecimal amount) { return "paypal:" + amount; }
    }

    static final class BankTransferProcessor implements PaymentProcessor {
        public String pay(BigDecimal amount) { return "bank:" + amount; }
    }
```

PaymentSolution.java · lines 42–85

```
    static final class PaymentProcessorFactory {
        PaymentProcessor create(PaymentMethod method) {
            Objects.requireNonNull(method, "method");
            return switch (method) {
                case CARD -> new StripeCardProcessor();
                case PAYPAL -> new PayPalProcessor();
                case BANK -> new BankTransferProcessor();
            };
        }
    }

    static final class PaymentService {
        private final PaymentProcessor processor;

        PaymentService(PaymentProcessor processor) {
            this.processor = Objects.requireNonNull(processor, "processor");
        }

        String pay(BigDecimal amount) {
            Objects.requireNonNull(amount, "amount");
            if (amount.signum() <= 0) {
                throw new IllegalArgumentException("Amount must be positive");
            }
            return processor.pay(amount.setScale(2, RoundingMode.UNNECESSARY));
        }
    }

    static void check(boolean condition, String name) {
        if (!condition) throw new AssertionError(name);
    }

    public static void main(String[] args) {
        var factory = new PaymentProcessorFactory();
        var value = new BigDecimal("25.00");
        check(factory.create(PaymentMethod.CARD)
                instanceof StripeCardProcessor, "Card selection");
        check(factory.create(PaymentMethod.PAYPAL)
                instanceof PayPalProcessor, "PayPal selection");
        check(factory.create(PaymentMethod.BANK)
                instanceof BankTransferProcessor, "Bank selection");
        check(new StripeCardProcessor().pay(value).equals("card:25.00"),
                "Card behavior");
        check(new PayPalProcessor().pay(value).equals("paypal:25.00"),
                "PayPal behavior");
```

PaymentSolution.java · lines 86–104

```
        check(new BankTransferProcessor().pay(value).equals("bank:25.00"),
                "Bank behavior");
        var fake = new PaymentService(amount -> "fake:" + amount);
        check(fake.pay(value).equals("fake:25.00"), "Delegation");
        check(PaymentMethod.fromRequest(" CARD ") == PaymentMethod.CARD,
                "Input normalization");
        boolean rejected = false;
        try { fake.pay(BigDecimal.ZERO); }
        catch (IllegalArgumentException expected) { rejected = true; }
        check(rejected, "Invalid amount");
        rejected = false;
        try { PaymentMethod.fromRequest("banana"); }
        catch (IllegalArgumentException expected) { rejected = true; }
        check(rejected, "Invalid method");
        var processor = factory.create(PaymentMethod.fromRequest("card"));
        System.out.println(new PaymentService(processor).pay(value));
        System.out.println("All payment checks passed.");
    }
}
```

References / official documentation

## Sources and verification

The lesson’s problem sequence is adapted from the supplied Lesson 2. Java language and API statements were checked against these official references on 1 September 2026. The examples, fictional rates and design trade-offs are teaching material.

1. [Microsoft Learn · Design Patterns: Factories](https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-factories)

   Terminology: Simple Factory, Factory Method and Abstract Factory.

   https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-factories
2. [Java Language Specification 25 · Classes](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html)

   Enums (§8.9), records and compact constructors (§8.10), and nested classes.

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html
3. [Java SE 25 API · BigDecimal](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigDecimal.html)

   Decimal construction, immutability, scale, rounding and equality.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigDecimal.html
4. [Java Language Specification 25 · Exhaustive switch blocks](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.11.1.1)

   Exhaustiveness for enum switches; see also switch expressions in Chapter 15.

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.11.1.1
5. [Java SE 25 API · Supplier](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/function/Supplier.html)

   The get() contract and lack of a freshness guarantee.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/function/Supplier.html
6. [Java SE 25 API · EnumMap](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/EnumMap.html)

   Maps with enum keys.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/EnumMap.html
7. [Java SE 25 API · String](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html)

   strip(), isBlank() and locale-aware case conversion.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html
8. [Java Language Specification 25 · Expressions](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html)

   Lambdas (§15.27), method references (§15.13) and switch expressions (§15.28).

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html
9. [JDK 25 · javac command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

   Compilation, --release and -Xlint.

   https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html
10. [Java SE 25 API · Map](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.html)

    copyOf() creates an unmodifiable map and rejects null keys and values.

    https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.html

Lab execution: OpenJDK 17.0.20, compiler warnings enabled, three successful main programs. Java 25 compatibility was checked against the references; execution on Java 25 was not available.

DP / Lesson 2 · First-principles design practice · Java 25-compatible edition