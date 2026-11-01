[Skip to the lesson](#start)

DP / Design patterns from first principles / Lesson 04

# DecoratorAdd behavior without modifying the core object

Start with one clean shipping capability. Follow the pressure from duplicated concerns to composable wrappers, then make order and failure behavior explicit.

Java 25-compatibleStandard library onlySelf-containedLight theme

Keep the capability. Add a wrapper. Preserve the interface the caller uses.

Print / Save as PDF[Jump to complete Java source](#run)

Print at 100% scale on A4 or Letter. The stylesheet supplies page breaks and hides controls. Disable browser headers/footers if they duplicate page labels. Background graphics are optional; meaning does not depend on color.

[**01**Starting contract](#start)[**02**Independent concerns](#pressure)[**03**The first decorator](#wrapper)[**04**Metrics and insurance](#layers)[**05**Failure semantics](#failure)[**06**Order and time](#order)[**07**Focused checks](#testing)[**08**Composition root](#composition)[**09**Pattern distinctions](#distinctions)[**10**Design judgment](#judgment)[**11**Payment exercise](#exercise)[**12**Complete Java source](#run)

Read in order to preserve the derivation. Use the contents to revisit a concept or the exercise.

01 / Establish the capability

## Start with a design that already works

### 1. What does checkout need?

One capability: calculate a shipping price for an order. A `ShippingPolicy` supplies it. Checkout adds that price to the merchandise total. The standard and express algorithms can vary independently of checkout.

Java · excerpt

```
record Order(BigDecimal weightKg, BigDecimal total,
             String destinationZip) {}

@FunctionalInterface
interface ShippingPolicy {
    BigDecimal calculate(Order order);
}

static BigDecimal money(BigDecimal value) {
    return value.setScale(2, RoundingMode.HALF_UP);
}

static BigDecimal usd(String value) {
    return money(new BigDecimal(value));
}
```

Java · excerpt

```
static final class StandardShipping implements ShippingPolicy {
    @Override
    public BigDecimal calculate(Order order) {
        return money(order.weightKg()
            .multiply(new BigDecimal("2.00")));
    }
}

record CheckoutService(ShippingPolicy shipping) {
    BigDecimal total(Order order) {
        return money(order.total().add(shipping.calculate(order)));
    }
}
```

**Java reading key.** A `record` declares its components and receives a constructor and accessors; `order.weightKg()` reads a component. A record can implement an interface. We use records for small holders, and ordinary classes for the base algorithms. `@FunctionalInterface` asks the compiler to verify the functional-interface shape. Because `ShippingPolicy` has one abstract method, it can be implemented with a lambda; the annotation itself is optional. [[9]](#source-9)

### 2. Make the example’s contract explicit

These are invented teaching prices: standard is $2 per kg; express is $4 per kg plus $10. All amounts are USD. Inputs are already validated: non-null fields and dependencies, positive weight, non-negative merchandise total, and a usable ZIP. Validation and currency conversion are outside this lesson.

Quotes use `BigDecimal`, with decimal strings and two decimal places. This lesson rounds each pricing layer with `HALF_UP`; that is a chosen rule, not a universal financial rule. `BigDecimal` supports decimal arithmetic and explicit rounding. [[2]](#source-2)

Nothing needs a decorator yet. The pressure appears when unrelated behaviors must follow every algorithm.

02 / Find the pressure

## A small addition spreads

### 3. The first request: log each calculation

Adding logging directly to standard shipping works:

Java · first attempt

```
// Replacement calculate method inside StandardShipping.
public BigDecimal calculate(Order order) {
    System.out.println("shipping.started");
    BigDecimal cost = money(order.weightKg()
        .multiply(new BigDecimal("2.00")));
    System.out.println("shipping.finished=" + cost);
    return cost;
}
```

### 4. The same request reaches every implementation

Express shipping needs the same messages. So does the legacy-carrier adapter from Lesson 3. Copying the logging into each implementation creates several places to update its format or failure behavior.

### 5. More concerns vary independently

| Concern | Reason it changes | What it needs |
| --- | --- | --- |
| Shipping algorithm | Carrier or pricing rules | An order |
| Logging | Message format or destination | The call and its outcome |
| Metrics | Timing or measurement policy | The duration of the call |
| Insurance | Optional pricing policy | The wrapped shipping price |
| Weekend surcharge | Calendar and surcharge rules | The wrapped price and a weekend decision |

The deeper issue is independent reasons to change becoming entangled. Logging and metrics observe the calculation; insurance and weekend pricing change its result. That distinction will matter when we choose the order.

### 6. Derive the missing object

Logging needs *something that calculates shipping*. It can hold a `ShippingPolicy`, delegate the work, and add behavior around the call. If the wrapper also implements `ShippingPolicy`, checkout can use it without learning a new interface.

The wrapper both **is usable as** a ShippingPolicy and **holds** a ShippingPolicy.

03 / Derive Decorator

## Preserve the interface; wrap the call

### 7. Build the first decorator

Java · excerpt

```
record LoggingShipping(ShippingPolicy inner, Consumer<String> log)
        implements ShippingPolicy {
    @Override
    public BigDecimal calculate(Order order) {
        log.accept("shipping.started");
        try {
            BigDecimal result = inner.calculate(order);
            log.accept("shipping.finished=" + result);
            return result;
        } catch (RuntimeException failure) {
            log.accept("shipping.failed="
                + failure.getClass().getSimpleName());
            throw failure;
        }
    }
}
```

The record components become constructor arguments. `inner` is the wrapped capability; `log` is an injected message destination. For the lesson, logging and metric destinations must return normally. We examine this assumption in step 13.

Java · excerpt

```
ShippingPolicy shipping = new LoggingShipping(
    new StandardShipping(), System.out::println);
CheckoutService checkout = new CheckoutService(shipping);
```

### 8. Read the execution, not just the nesting

| When | What happens |
| --- | --- |
| Before delegation | Logging writes `shipping.started`. |
| Inside | Standard shipping calculates the price. |
| Successful return | Logging writes the price, then returns it unchanged. |
| Runtime exception | Logging writes a failure event, then rethrows the same exception. |

### 9. Name the pattern after the reasoning

This is **Decorator**: adding behavior to an individual object through a wrapper. Microsoft’s definition emphasizes that other objects of the original class need not change. [[1]](#source-1)

1. Implement the caller’s interface.
2. Hold another implementation of that interface.
3. Delegate the core work.
4. Add behavior around delegation or transform its result.

Checkout still depends only on `ShippingPolicy`. In this example, each decorator delegates exactly once. A shared interface enables substitution; the behavioral contract still needs to be respected.

04 / Add independent behaviors

## Observe duration; transform the price

### 10. Metrics must also run on failure

Java · excerpt

```
record MetricsShipping(ShippingPolicy inner, LongSupplier nanoTime,
                       LongConsumer durationNanos)
        implements ShippingPolicy {
    @Override
    public BigDecimal calculate(Order order) {
        long start = nanoTime.getAsLong();
        try {
            return inner.calculate(order);
        } finally {
            durationNanos.accept(nanoTime.getAsLong() - start);
        }
    }
}
```

`System::nanoTime` supplies elapsed-time readings in real use. Subtract readings from the same JVM; this API is not a wall clock and does not promise nanosecond resolution. A `LongSupplier` makes timing deterministic in tests. [[3]](#source-3)

`finally` runs as the delegated call returns or throws during normal Java execution. It records failure duration as well as success duration. [[4]](#source-4)

### 11. Insurance changes the wrapped result

Java · excerpt

```
record InsuranceShipping(ShippingPolicy inner)
        implements ShippingPolicy {
    @Override
    public BigDecimal calculate(Order order) {
        BigDecimal base = inner.calculate(order);
        return money(base.multiply(new BigDecimal("1.10")));
    }
}
```

The invented insurance rule adds 10% of the price returned by the inner policy. A $20.00 quote becomes $22.00. Insurance does not run its arithmetic if the inner calculation throws.

### 12. Stack them

Java · excerpt

```
ShippingPolicy shipping = new LoggingShipping(
    new MetricsShipping(
        new InsuranceShipping(new StandardShipping()),
        System::nanoTime,
        nanos -> System.out.println("duration.ns=" + nanos)),
    System.out::println);
```

Calls enter the outer wrapper first. Results return from the inner implementation outward. Here the log sees the insured price, and metrics measures standard shipping plus insurance.

05 / Make execution semantics explicit

## Failure behavior is part of the design

### 13. “After” and “always” are different requirements

| Behavior | Before inner call | After success | After failure |
| --- | --- | --- | --- |
| Logging | Start event | Result event | Failure event, rethrow |
| Metrics | Read start | Record elapsed time | Record elapsed time |
| Insurance | Nothing | Multiply and round | No new price |
| Weekend surcharge | Nothing | Optionally add $20 | No new price |

**The sink contract matters.** Java’s `Consumer` and `LongConsumer` do not guarantee non-throwing implementations. If a metrics sink throws inside `finally`, it can replace the original exception or a successful return. A failing logger can also alter the result. The Java specification defines this replacement behavior. [[4]](#source-4)

Our example requires the injected log, duration sink, and time source to return normally. If a real integration cannot guarantee that, enforce an explicit failure policy at that boundary. For best-effort diagnostics, sink failures should not turn successful shipping into failed shipping; required audit delivery may need a different design.

The logger catches `RuntimeException`, not all `Throwable` values. An `Error` still propagates and the metrics `finally` is attempted, but this logger does not promise a failure event for it. No wrapper guarantees cleanup after abrupt process termination.

### 14. Trace one composed call

| Step | Success | Inner runtime exception |
| --- | --- | --- |
| 1 | Log started | Log started |
| 2 | Start timer | Start timer |
| 3 | Calculate base, then insurance | Base throws; insurance is skipped |
| 4 | Record duration | Record duration |
| 5 | Log finished; return price | Log failed; rethrow |

A correct wrapper preserves the intended result and failure behavior. Its class shape alone does not prove that.

06 / Price in a deliberate order

## The same wrappers can mean different prices

### 15. Add weekend pricing without hiding a clock

Java · excerpt

```
record WeekendSurchargeShipping(ShippingPolicy inner,
                                BooleanSupplier isWeekend)
        implements ShippingPolicy {
    @Override
    public BigDecimal calculate(Order order) {
        BigDecimal cost = inner.calculate(order);
        return isWeekend.getAsBoolean()
            ? money(cost.add(usd("20.00"))) : cost;
    }
}

static boolean isWeekend(Clock clock) {
    DayOfWeek day = LocalDate.now(clock).getDayOfWeek();
    return day == DayOfWeek.SATURDAY || day == DayOfWeek.SUNDAY;
}
```

`BooleanSupplier` supplies a boolean via `getAsBoolean()`. Tests pass `() -> true` or `() -> false`. [[5]](#source-5) In application wiring, choose a business timezone, evaluate an injected `Clock` once for the quote, and capture that decision. Java’s `Clock` also supports fixed clocks for tests. [[6]](#source-6)

### 16. Change the order; change the meaning

A · insurance outermost

```
new InsuranceShipping(
    new WeekendSurchargeShipping(
        fixed, () -> true));
```

**($100 + $20) × 1.10 = $132**
Insurance includes the surcharge.

B · weekend outermost

```
new WeekendSurchargeShipping(
    new InsuranceShipping(fixed),
    () -> true);
```

**$100 × 1.10 + $20 = $130**
The surcharge is added after insurance.

`fixed` returns $100.00. The outer decorator’s *post-processing* happens last. Decide which price insurance covers before choosing the nesting.

**Observation order matters too.** Logging outside insurance sees the final insured price; logging inside sees the earlier price. Metrics outside logging includes logging time; metrics inside excludes the outer log calls. Rounding can introduce further differences between compositions.

07 / Verify responsibilities

## Test the boundary each wrapper owns

### 17. Replace the carrier with a fixed price

Java · excerpt

```
record FixedShipping(BigDecimal price) implements ShippingPolicy {
    @Override
    public BigDecimal calculate(Order order) {
        return money(price);
    }
}
```

Java · excerpt

```
ShippingPolicy fixed = new FixedShipping(usd("100.00"));
checkMoney("110.00", new InsuranceShipping(fixed).calculate(order));
checkMoney("120.00", new WeekendSurchargeShipping(
    fixed, () -> true).calculate(order));
checkMoney("100.00", new WeekendSurchargeShipping(
    fixed, () -> false).calculate(order));
```

The complete program supplies `order` and the check helpers. `checkMoney` uses `compareTo` for numeric equality; `BigDecimal.equals` also considers scale. [[2]](#source-2)

### 18. Verify the semantics beyond arithmetic

| Check | Evidence to assert |
| --- | --- |
| Delegation | One base call, with the same order |
| Logging success | Started, base call, then finished with the result |
| Logging failure | A failure event; no success event; same exception escapes |
| Metrics success / failure | Two supplied ticks yield the expected duration in both cases |
| Pricing order | Insurance last gives $132; weekend last gives $130 |
| Rounding | $0.05 × 1.10 rounds to $0.06 under this lesson’s rule |

The executable checks in the appendix use lists to record events and two-value time sources. They make no network calls and do not sleep. They throw `AssertionError` directly, so the checks do not depend on enabling Java assertions.

Test each independent behavior, then test any composition whose order carries business meaning.

08 / Keep assembly outside checkout

## Compose objects instead of multiplying subclasses

### 19. Why not subclass each combination?

A logging subclass of standard shipping handles one combination. Add express, insurance, metrics, and weekend options, and the combinations spread. With three algorithms and four independently optional behaviors, there are **3 × 2⁴ = 48 selections** before accounting for different orders. This counts configurations; it does not mean every inheritance design must contain 48 classes.

Decorator represents the behaviors separately and assembles objects. The base algorithm is chosen once; wrappers can be reused across standard, express, and an adapted carrier. Ordinary inheritance remains useful when a stable specialization is what you need.

### 20. Put construction at the application’s entry point

Java · excerpt

```
// In main, a factory, or another application assembly point:
ShippingPolicy priced = new InsuranceShipping(
    new WeekendSurchargeShipping(
        new StandardShipping(), () -> weekend));
ShippingPolicy observed = new LoggingShipping(
    new MetricsShipping(priced, System::nanoTime, metrics), log);
CheckoutService checkout = new CheckoutService(observed);
```

This assembly point is commonly called the **composition root**. It creates dependencies and chooses the object graph. Checkout receives the finished capability through its constructor.

Logging ShippingPolicy

Metrics ShippingPolicy

Insurance ShippingPolicy

Weekend surcharge ShippingPolicy

Standard shipping ShippingPolicy

A factory can select standard, express, or an adapter first. Apply wrappers to that returned `ShippingPolicy`. Neither checkout nor the decorators need the concrete carrier type.

09 / Recognize the intent

## Related patterns solve different pressures

### 21. Compare the responsibility, not the wrapper syntax

| Idea | Question it answers | In our example |
| --- | --- | --- |
| Strategy | Which interchangeable algorithm? | Standard versus express |
| Factory | Which object or graph should be created? | Select a carrier and assemble its policy |
| Adapter | How can an incompatible API satisfy this boundary? | Translate `getQuote(zip, grams)` into `calculate(order)` |
| Decorator | Which behavior surrounds an existing capability? | Log, time, insure, or surcharge a policy |
| Middleware / interceptor | Which stages surround or route a request? | A related before/delegate/after structure |

Adapter translates a mismatched interface; Decorator preserves the interface used by the caller and adds behavior. Microsoft defines Adapter in terms of interface conversion. [[7]](#source-7) Middleware is a useful analogy, but not every pipeline is an object-oriented Decorator: stages may short-circuit, route, or use a separate continuation contract.

### 22. See the shape in Java’s own APIs

Java · excerpt

```
// Independent example: input.bin must already exist.
try (java.io.InputStream input = new java.io.BufferedInputStream(
        java.nio.file.Files.newInputStream(
            java.nio.file.Path.of("input.bin")))) {
    int firstByte = input.read();
    System.out.println(firstByte); // -1 means end of stream
}
```

Java documents `FilterInputStream` as wrapping another input stream and delegating to it. `BufferedInputStream` adds buffering and mark/reset support while remaining an `InputStream`. This is a concrete example of the same composition shape. [[8]](#source-8)

Wrapping can affect resource ownership too. With stream wrappers, closing the outer stream closes its underlying stream. Our shipping policies do not own closeable resources, so they do not model that lifecycle. [[8]](#source-8)

10 / Use judgment

## Flexibility has a reasoning cost

### 23. Decide whether the pressure justifies wrappers

1. Identify the capability the caller already needs.
2. Find concerns that change independently.
3. Check whether those concerns are repeated or optional.
4. Ask whether they naturally surround a call or transform its result.
5. Keep the caller’s contract intact.
6. Choose and test the ordering, result, and failure semantics.

A single stable calculation may be clearer as one method. Do not introduce a class for every line of code. Decorator earns its cost when independent behaviors need reuse or composition across implementations.

### 24. Stop when the object graph hides the policy

Eight nested wrappers can be harder to understand than one explicit workflow. Give important compositions names, centralize assembly, and test their outcomes. An explicit pricing policy or orchestration method may be clearer when rules must operate in a tightly controlled sequence.

| Risk | Design response |
| --- | --- |
| Unclear order | Document what each layer observes or transforms |
| Duplicate wrapping | Assemble once; prevent applying insurance twice |
| Hidden failure changes | Specify sink failures and preserve intended exceptions |
| Retry plus payment | Define idempotency before repeating side effects |
| Cache plus pricing | Define which result is cached and what makes it stale |

Configuration, middleware, or a dependency-injection container may organize assembly, but none decides business semantics for you. Same method signatures do not guarantee equivalent behavior.

I have a capability. I need independently composable behavior around it. The caller should still use the same interface.

That is the reason to reach for Decorator.

11 / Apply it

## Exercise: decorate a payment capability

This is a simulation. `StripeProcessor` below is an invented stub, not the Stripe SDK and not a real charge.

Java · place inside an exercise class; import BigDecimal

```
record PaymentResult(String transactionId) {}

interface PaymentProcessor {
    PaymentResult pay(BigDecimal amount);
}

static final class StripeProcessor implements PaymentProcessor {
    @Override
    public PaymentResult pay(BigDecimal amount) {
        return new PaymentResult("TX123");
    }
}

record PaymentCheckout(PaymentProcessor processor) {
    PaymentResult pay(BigDecimal amount) {
        return processor.pay(amount);
    }
}
```

Add `LoggingPayment`, `MetricsPayment`, and `FraudCheckPayment`. Each must implement `PaymentProcessor` and hold an inner processor. Assemble logging outside metrics, with fraud checking immediately before the processor.

| Acceptance criterion | What to prove |
| --- | --- |
| Preserve the boundary | PaymentCheckout still receives only PaymentProcessor |
| Preserve the existing processor | StripeProcessor is unchanged |
| Check fraud before charging | A rejection produces zero inner payment calls |
| Log the correct outcome | Rejections and failures never produce a success event |
| Measure both outcomes | Record duration on success, rejection, and processor failure |
| Keep dependencies testable | Inject the fraud decision, clock ticks, and observation sinks |

**Work through:** Which behavior happens before delegation? Which requires a successful result? Which must be attempted when the inner call throws? Moving metrics inside fraud checking means rejected payments are no longer included in that measurement.

### Next pressure: Observer

After checkout succeeds, email, inventory, loyalty, analytics, and shipping may all need to react. Why should checkout name every consequence? This leads to Observer and publish-subscribe ideas. They are related, but broker-based messaging also raises delivery, ordering, and timing questions that a local listener list does not solve.

12 / Run and inspect

## One file, standard Java, no dependencies

The full listing below is `DecoratorLesson.java`. It contains the model, both base algorithms, four decorators, application wiring, and deterministic checks. Earlier snippets are excerpts from this file; they share its imports and helper methods.

Download DecoratorLesson.javaCopy full Java source

If scripting is disabled, copy the complete listing directly into a file with that name. Reading and printing the guide require no JavaScript or external assets.

Terminal · use a JDK 25 installation

```
javac --release 25 DecoratorLesson.java
java DecoratorLesson
java DecoratorLesson --test
```

`--release 25` selects the Java 25 language and API target. No preview flag or build tool is needed. The launcher accepts the compiled class name and passes following arguments to `main`. [[10]](#source-10)

| Demo condition | Shipping | Checkout total |
| --- | --- | --- |
| Weekday in the example’s UTC timezone | $20 × 1.10 = $22.00 | $122.00 |
| Weekend in the example’s UTC timezone | ($20 + $20) × 1.10 = $44.00 | $144.00 |

The demo uses a 10 kg order with $100.00 of merchandise. The duration varies. The test command is designed to print `All checks passed.` when its checks succeed.

**Verification status.** The API and language usage was reviewed against official Java 25 documentation. **⚠ Compilation and Java execution were not verified here:** the workspace has no working JDK. The commands above are included so the exact source and checks can be run locally.

### Complete source listing

Continue through the listing in order. There are no omitted methods or external libraries.

```
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Clock;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;
import java.util.function.LongConsumer;
import java.util.function.LongSupplier;

public class DecoratorLesson {
    record Order(BigDecimal weightKg, BigDecimal total,
                 String destinationZip) {}

    @FunctionalInterface
    interface ShippingPolicy {
        BigDecimal calculate(Order order);
    }

    static BigDecimal money(BigDecimal value) {
        return value.setScale(2, RoundingMode.HALF_UP);
    }

    static BigDecimal usd(String value) {
        return money(new BigDecimal(value));
    }
    static final class StandardShipping implements ShippingPolicy {
        @Override
        public BigDecimal calculate(Order order) {
            return money(order.weightKg()
                .multiply(new BigDecimal("2.00")));
        }
    }

    static final class ExpressShipping implements ShippingPolicy {
        @Override
        public BigDecimal calculate(Order order) {
            return money(order.weightKg()
                .multiply(new BigDecimal("4.00"))
                .add(usd("10.00")));
        }
    }

    record CheckoutService(ShippingPolicy shipping) {
        BigDecimal total(Order order) {
            return money(order.total().add(shipping.calculate(order)));
        }
    }
    record LoggingShipping(ShippingPolicy inner, Consumer<String> log)
            implements ShippingPolicy {
        @Override
        public BigDecimal calculate(Order order) {
            log.accept("shipping.started");
            try {
                BigDecimal result = inner.calculate(order);
                log.accept("shipping.finished=" + result);
                return result;
            } catch (RuntimeException failure) {
                log.accept("shipping.failed="
                    + failure.getClass().getSimpleName());
                throw failure;
            }
        }
    }
    record MetricsShipping(ShippingPolicy inner, LongSupplier nanoTime,
                           LongConsumer durationNanos)
            implements ShippingPolicy {
        @Override
        public BigDecimal calculate(Order order) {
            long start = nanoTime.getAsLong();
            try {
                return inner.calculate(order);
            } finally {
                durationNanos.accept(nanoTime.getAsLong() - start);
            }
        }
    }
    record InsuranceShipping(ShippingPolicy inner)
            implements ShippingPolicy {
        @Override
        public BigDecimal calculate(Order order) {
            BigDecimal base = inner.calculate(order);
            return money(base.multiply(new BigDecimal("1.10")));
        }
    }
    record WeekendSurchargeShipping(ShippingPolicy inner,
                                    BooleanSupplier isWeekend)
            implements ShippingPolicy {
        @Override
        public BigDecimal calculate(Order order) {
            BigDecimal cost = inner.calculate(order);
            return isWeekend.getAsBoolean()
                ? money(cost.add(usd("20.00"))) : cost;
        }
    }

    static boolean isWeekend(Clock clock) {
        DayOfWeek day = LocalDate.now(clock).getDayOfWeek();
        return day == DayOfWeek.SATURDAY || day == DayOfWeek.SUNDAY;
    }
    record FixedShipping(BigDecimal price) implements ShippingPolicy {
        @Override
        public BigDecimal calculate(Order order) {
            return money(price);
        }
    }
    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("--test")) {
            runChecks();
            return;
        }

        Order order = new Order(new BigDecimal("10"),
                                usd("100.00"), "85001");
        Consumer<String> log = System.out::println;
        LongConsumer metrics = nanos ->
            System.out.println("shipping.duration.ns=" + nanos);

        // Demonstration business timezone; choose yours explicitly.
        Clock clock = Clock.system(ZoneId.of("UTC"));
        // One decision per quote; stable even across midnight.
        boolean weekend = isWeekend(clock);

        ShippingPolicy priced = new InsuranceShipping(
            new WeekendSurchargeShipping(
                new StandardShipping(), () -> weekend));
        ShippingPolicy observed = new LoggingShipping(
            new MetricsShipping(priced, System::nanoTime, metrics), log);

        CheckoutService checkout = new CheckoutService(observed);
        System.out.println("checkout.total=" + checkout.total(order));
    }
    static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    static void checkMoney(String expected, BigDecimal actual) {
        check(usd(expected).compareTo(actual) == 0,
            "Expected " + expected + ", got " + actual);
    }

    static LongSupplier ticks(long start, long end) {
        long[] values = { start, end };
        int[] next = { 0 };
        return () -> values[next[0]++];
    }

    static void expectSameFailure(ShippingPolicy shipping, Order order,
                                  RuntimeException expected) {
        try {
            shipping.calculate(order);
            throw new AssertionError("Expected an exception");
        } catch (RuntimeException actual) {
            check(actual == expected, "The original failure must escape");
        }
    }
    static void runChecks() {
        Order order = new Order(new BigDecimal("10"),
                                usd("100.00"), "85001");
        ShippingPolicy fixed = new FixedShipping(usd("100.00"));

        checkMoney("20.00", new StandardShipping().calculate(order));
        checkMoney("50.00", new ExpressShipping().calculate(order));
        checkMoney("120.00", new CheckoutService(
            new StandardShipping()).total(order));
        checkMoney("110.00", new InsuranceShipping(fixed).calculate(order));
        checkMoney("0.06", new InsuranceShipping(
            new FixedShipping(usd("0.05"))).calculate(order));
        checkMoney("120.00", new WeekendSurchargeShipping(
            fixed, () -> true).calculate(order));
        checkMoney("100.00", new WeekendSurchargeShipping(
            fixed, () -> false).calculate(order));

        ShippingPolicy insuranceLast = new InsuranceShipping(
            new WeekendSurchargeShipping(fixed, () -> true));
        ShippingPolicy weekendLast = new WeekendSurchargeShipping(
            new InsuranceShipping(fixed), () -> true);
        checkMoney("132.00", insuranceLast.calculate(order));
        checkMoney("130.00", weekendLast.calculate(order));
        List<String> events = new ArrayList<>();
        int[] calls = { 0 };
        ShippingPolicy base = value -> {
            calls[0]++;
            check(value == order, "The same order must be delegated");
            events.add("base");
            return usd("100.00");
        };
        ShippingPolicy observed = new LoggingShipping(
            new MetricsShipping(base, ticks(100, 175),
                elapsed -> events.add("duration=" + elapsed)), events::add);
        checkMoney("100.00", observed.calculate(order));
        check(calls[0] == 1, "Exactly one delegation");
        check(events.equals(List.of("shipping.started", "base",
            "duration=75", "shipping.finished=100.00")),
            "Success execution order");

        events.clear();
        RuntimeException failure = new IllegalStateException("carrier");
        ShippingPolicy failing = value -> { throw failure; };
        ShippingPolicy observedFailure = new LoggingShipping(
            new MetricsShipping(failing, ticks(500, 525),
                elapsed -> events.add("duration=" + elapsed)), events::add);
        expectSameFailure(observedFailure, order, failure);
        check(events.equals(List.of("shipping.started", "duration=25",
            "shipping.failed=IllegalStateException")),
            "Failure duration and logging; no success event");

        System.out.println("All checks passed.");
    }
}
```

Reference / Official sources

## Sources and example boundaries

The lesson progression is adapted from the Lesson 4 text supplied in this conversation. The Java examples, invented prices, checks, and design commentary were written for this guide. The sources below verify pattern definitions and language/API behavior; they do not prescribe the example’s business rules.

1. **Decorator definition.** Microsoft Learn.
   <https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-decorator>
2. **Decimal arithmetic, constructors, equality and rounding.** Oracle Java 25 · BigDecimal.
   <https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigDecimal.html>
3. **Elapsed-time measurement.** Oracle Java 25 · System.nanoTime.
   <https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime()>
4. **try-finally completion and exception replacement.** Java Language Specification 25 · §14.20.2.
   <https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20.2>
5. **Boolean supplier interface.** Oracle Java 25 · BooleanSupplier.
   <https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/function/BooleanSupplier.html>
6. **Injectable time and fixed test clocks.** Oracle Java 25 · Clock.
   <https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html>
7. **Adapter interface conversion.** Microsoft Learn.
   <https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-adapterfaade>
8. **Stream wrapping and buffering.** Oracle Java 25 · FilterInputStream.
   <https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/FilterInputStream.html>
9. **Records and functional interfaces.** Java Language Specification 25 · §8.10.
   <https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.10>
10. **Compilation and execution.** Oracle JDK 25 · javac.
    <https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html>

Related official pages: [BufferedInputStream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/BufferedInputStream.html); [functional interfaces (§9.8)](https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html#jls-9.8); [java launcher](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html). Sources checked 1 September 2026.

Lesson 4 · Decorator · Java 25 edition · Official sources checked 1 September 2026