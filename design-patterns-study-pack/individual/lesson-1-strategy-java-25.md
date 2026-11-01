# Lesson 1 — Strategy Pattern in Java 25

> Goal: derive Strategy from a real design problem, implement it in Java 25, run it, test it, and understand when the
> pattern is—and is not—worth using.

## Learning outcomes

By the end, you should be able to:

- identify an **axis of variation**;
- separate stable workflow code from independently changing algorithms;
- define a capability as a Java interface;
- inject a strategy into a context using composition;
- test strategies and their caller independently;
- explain where strategy selection still belongs; and
- recognize when a conditional is simpler than Strategy.

---

## 1. Start with the simplest correct code

The first requirement is:

> Standard shipping costs 200 cents per kilogram.

```java
static int shippingCost(int weightKg) {
    return weightKg * 200;
}
```

This is good code. There is one rule and no meaningful variation. Adding interfaces and classes now would create
complexity without solving a real problem.

### First principle

Do not begin with a pattern. Begin with the simplest design that satisfies the current requirement.

---

## 2. Let the requirements create pressure

The business adds express and overnight shipping:

```java
enum ShippingMethod {
    STANDARD,
    EXPRESS,
    OVERNIGHT
}

static int shippingCost(Order order, ShippingMethod method) {
    return switch (method) {
        case STANDARD -> order.weightKg() * 200;
        case EXPRESS -> order.weightKg() * 400 + 1_000;
        case OVERNIGHT -> order.weightKg() * 700 + 2_500;
    };
}
```

This is still reasonable. A `switch` is not automatically a design problem.

Now imagine each policy growing independently:

- standard shipping gains a free-shipping rule;
- express shipping gains a remote-area surcharge;
- overnight shipping gains cutoff-time and weekend rules;
- international, same-day, pickup, and partner delivery are added.

One method now has many unrelated reasons to change:

```text
standard rules ─────┐
express rules ──────┤
overnight rules ────┼──> shippingCost(...)
international rules ┤
pickup rules ───────┘
```

The long method is only the symptom. The deeper problem is:

> Independently changing business policies are coupled inside one module.

Changing one branch requires opening, understanding, and retesting the container that holds every branch.

---

## 3. Find the axis of variation

Ask two questions:

1. What remains stable?
2. What varies independently?

For checkout:

| Stable                             | Variable                                       |
|------------------------------------|------------------------------------------------|
| Add the order subtotal to shipping | How shipping is calculated                     |
| Present a total                    | Standard, express, overnight, and future rules |

The stable checkout workflow needs only one capability:

> Given an order, calculate its shipping cost.

That capability is the boundary we need.

```text
STABLE                           VARIABLE

CheckoutService ──uses──> ShippingPolicy <──implemented by── Standard
                                                       ├──── Express
                                                       └──── Overnight
```

This is the key design move: stable code depends on a stable capability, not on every concrete algorithm.

---

## 4. Express the capability as a contract

```java

@FunctionalInterface
interface ShippingPolicy {
    int costInCents(Order order);
}
```

The name describes what the caller needs, not how a particular implementation works.

The order is a small immutable domain value:

```java
record Order(int weightKg, int subtotalCents) {
    Order {
        if (weightKg < 0 || subtotalCents < 0) {
            throw new IllegalArgumentException("Order values cannot be negative");
        }
    }
}
```

This lesson represents money as integer cents so floating-point rounding does not distract from the design problem.

---

## 5. Separate the algorithms

```java
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
```

Each class now owns one business policy and can change or be tested without touching the others.

---

## 6. Compose the behavior into checkout

```java
import java.util.Objects;

final class CheckoutService {
    private final ShippingPolicy shippingPolicy;

    CheckoutService(ShippingPolicy shippingPolicy) {
        this.shippingPolicy = Objects.requireNonNull(shippingPolicy);
    }

    int totalInCents(Order order) {
        return order.subtotalCents() + shippingPolicy.costInCents(order);
    }
}
```

`CheckoutService` is the **context**. It does not inherit a shipping algorithm and does not branch on shipping methods.
A `ShippingPolicy` is supplied through its constructor.

```java
var checkout = new CheckoutService(new ExpressShipping());
int total = checkout.totalInCents(new Order(10, 10_000));
```

This is composition: the object's behavior is assembled by giving it a collaborator.

### Dependency change

Before:

```text
CheckoutService ──> Standard rules
                ├─> Express rules
                └─> Overnight rules
```

After:

```text
CheckoutService ──> ShippingPolicy <── StandardShipping
                                   <── ExpressShipping
                                   <── OvernightShipping
```

The dependency points toward a capability. Concrete algorithms plug into that substitution point.

---

## 7. Name the pattern

We have derived **Strategy**:

> Put interchangeable algorithms behind one contract and let a context use the contract without knowing the algorithm's
> internal details.

The pattern is not merely “an interface plus several classes.” Those are implementation tools. The design intent is to
isolate independently varying behavior behind a stable boundary.

| Role                    | This example                                               |
|-------------------------|------------------------------------------------------------|
| Context                 | `CheckoutService`                                          |
| Strategy contract       | `ShippingPolicy`                                           |
| Concrete strategies     | `StandardShipping`, `ExpressShipping`, `OvernightShipping` |
| Client/composition root | Code that constructs `CheckoutService`                     |

---

## 8. What happens when a requirement changes?

Add drone shipping:

```java
final class DroneShipping implements ShippingPolicy {
    @Override
    public int costInCents(Order order) {
        return 2_000 + order.weightKg() * 500;
    }
}
```

`CheckoutService` does not change. That is **locality of change**: the new algorithm lives in its own implementation.

Strategy does not guarantee that no existing file will ever change. It aims to keep algorithm changes away from stable
workflow code.

---

## 9. Where does selection happen?

Something must still translate an input such as `EXPRESS` into an object such as `new ExpressShipping()`:

```java
static ShippingPolicy select(ShippingMethod method) {
    return switch (method) {
        case STANDARD -> new StandardShipping();
        case EXPRESS -> new ExpressShipping();
        case OVERNIGHT -> new OvernightShipping();
    };
}
```

The conditional did not disappear; its responsibility changed:

- policy classes contain business algorithms;
- the selection boundary chooses an algorithm;
- checkout uses the chosen algorithm.

```text
input ──> selection ──> ShippingPolicy ──> CheckoutService
```

Keeping this small selection method is fine. If construction knowledge becomes duplicated or complicated, that new
pressure leads naturally to Lesson 2: Factory.

---

## 10. Test responsibilities independently

A strategy test asks:

> Does this algorithm calculate the correct result?

```java
var order = new Order(10, 10_000);

check(new StandardShipping().

costInCents(order) ==2_000,
        "standard shipping");

check(new ExpressShipping().

costInCents(order) ==5_000,
        "express shipping");
```

A context test asks:

> Does checkout use a supplied strategy correctly?

Because `ShippingPolicy` has one abstract method, a lambda can act as a deterministic test strategy:

```java
ShippingPolicy fixedShipping = ignored -> 1_000;
var checkout = new CheckoutService(fixedShipping);

check(checkout.totalInCents(new Order(10, 10_000))==11_000,
        "checkout includes shipping");
```

The test does not need any production shipping rule. That is the practical value of a substitution point.

---

## 11. Complete runnable lab

Create `src/Main.java` and paste this code:

```java
import java.util.Objects;

public class Main {
    public static void main(String[] args) {
        var order = new Order(10, 10_000);

        check(new StandardShipping().costInCents(order) == 2_000,
                "standard shipping");
        check(new ExpressShipping().costInCents(order) == 5_000,
                "express shipping");
        check(new OvernightShipping().costInCents(order) == 9_500,
                "overnight shipping");

        var expressCheckout = new CheckoutService(new ExpressShipping());
        check(expressCheckout.totalInCents(order) == 15_000,
                "checkout uses the selected production strategy");

        ShippingPolicy fixedShipping = ignored -> 1_000;
        var isolatedCheckout = new CheckoutService(fixedShipping);
        check(isolatedCheckout.totalInCents(order) == 11_000,
                "checkout can be tested with a test strategy");

        System.out.println("All Strategy checks passed.");
    }

    private static void check(boolean condition, String description) {
        if (!condition) {
            throw new AssertionError("Failed: " + description);
        }
    }
}

record Order(int weightKg, int subtotalCents) {
    Order {
        if (weightKg < 0 || subtotalCents < 0) {
            throw new IllegalArgumentException("Order values cannot be negative");
        }
    }
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
        this.shippingPolicy = Objects.requireNonNull(shippingPolicy);
    }

    int totalInCents(Order order) {
        return order.subtotalCents() + shippingPolicy.costInCents(order);
    }
}
```

Expected output:

```text
All Strategy checks passed.
```

The lab uses stable Java features only; no preview flags or external libraries are required.

---

## 12. Verified Java 25 and IntelliJ IDEA setup

The instructions in this section were checked on **September 1, 2026** against Oracle and JetBrains documentation only.

### Option A — Create and run the project in IntelliJ IDEA

Use IntelliJ IDEA 2025.2 or later, whose official release information includes Java 25 support.

1. Open IntelliJ IDEA and choose **New Project** (or **File → New Project**).
2. Select **Java**.
3. Name the project `strategy-pattern`.
4. Choose **IntelliJ** as the build system; this lab has no external dependencies.
5. In **JDK**, select an installed JDK 25. If none is configured, choose **Download JDK**, select version **25** and a
   vendor, then confirm.
6. If needed, open **File → Project Structure → Project** and set:
    - **SDK:** JDK 25
    - **Language level:** `25 – Compact source files, module imports`
7. Under the project, create `src/Main.java` and paste the complete lab.
8. Click the green run icon next to `main`, then choose **Run 'Main.main()'**.

JetBrains' current Java tutorial documents the New Project flow, selecting or downloading JDK 25, and running `main`
from the editor. Its Java 25 setup article documents the SDK and language-level settings.
See [Create your first Java application](https://www.jetbrains.com/help/idea/creating-and-running-your-first-java-application.html), [Java 25 LTS and IntelliJ IDEA](https://blog.jetbrains.com/idea/2025/09/java-25-lts-and-intellij-idea/),
and [supported Java versions](https://www.jetbrains.com/help/idea/supported-java-versions.html).

### Option B — Install the JDK separately

Oracle publishes JDK 25 installation procedures for Windows, macOS, and Linux in
its [JDK 25 Installation Guide](https://docs.oracle.com/en/java/javase/25/install/). Follow the
operating-system-specific page there, then verify both tools:

```shell
java --version
javac --version
```

Both outputs should identify version 25. On macOS, Oracle also documents `java -version` and
`/usr/libexec/java_home -v 25` for locating the selected JDK
in [Installation of the JDK on macOS](https://docs.oracle.com/en/java/javase/25/install/installation-jdk-macos.html).

### Option C — Compile and run from a terminal

From the project root:

```shell
javac --release 25 -d out src/Main.java
java -cp out Main
```

Oracle documents that `javac` compiles `.java` sources into class files, `--release 25` targets the Java SE 25
language/API release, and `-d out` selects the class-output directory. Oracle's `java` documentation defines `-cp`/
`--class-path` and launching a main class. See [The
`javac` command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html) and [The
`java` command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html).

### Troubleshooting

- **IntelliJ marks records or switch expressions as errors:** confirm the project SDK and language level are both 25.
- **`javac` is not found:** a full JDK is missing from the terminal environment, or its `bin` directory is not available
  to the shell. Use IntelliJ's **Download JDK** path or follow Oracle's OS-specific installation guide.
- **The IDE uses a different Java version than the terminal:** IntelliJ's project SDK is configured independently of the
  terminal's default JDK; check both explicitly.
- **Do I need `--enable-preview`?** No. This lab intentionally avoids preview features.

---

## 13. Hands-on exercise: discount strategies

Start with this code:

```java
static int discountInCents(String customerType, int amountInCents) {
    return switch (customerType) {
        case "regular" -> amountInCents * 5 / 100;
        case "premium" -> amountInCents * 10 / 100;
        case "employee" -> amountInCents * 30 / 100;
        default -> 0;
    };
}
```

Refactor toward:

```text
Checkout ──> DiscountPolicy <── RegularDiscount
                             <── PremiumDiscount
                             <── EmployeeDiscount
```

Work in this order:

1. Write `DiscountPolicy` as a capability, not as a customer-type selector.
2. Move each algorithm into an independent implementation.
3. Inject one `DiscountPolicy` into a checkout class.
4. Test each policy independently.
5. Test checkout with a lambda that always returns 500 cents.
6. Add `StudentDiscount` without modifying checkout.

### Questions to answer before viewing a solution

- What varies?
- What remains stable?
- Which knowledge belongs in each policy?
- Which knowledge belongs at the selection boundary?
- Can checkout be tested without a real discount algorithm?

<details>
<summary>One possible solution</summary>

```java

@FunctionalInterface
interface DiscountPolicy {
    int discountInCents(int amountInCents);
}

final class RegularDiscount implements DiscountPolicy {
    public int discountInCents(int amountInCents) {
        return amountInCents * 5 / 100;
    }
}

final class PremiumDiscount implements DiscountPolicy {
    public int discountInCents(int amountInCents) {
        return amountInCents * 10 / 100;
    }
}

final class EmployeeDiscount implements DiscountPolicy {
    public int discountInCents(int amountInCents) {
        return amountInCents * 30 / 100;
    }
}

final class DiscountingCheckout {
    private final DiscountPolicy discountPolicy;

    DiscountingCheckout(DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }

    int totalInCents(int subtotalInCents) {
        return subtotalInCents
                - discountPolicy.discountInCents(subtotalInCents);
    }
}
```

</details>

---

## 14. Trade-offs and when not to use Strategy

### Strategy is a good fit when

- multiple algorithms implement the same meaningful capability;
- the algorithms evolve or are tested independently;
- a caller should not contain their business details; or
- behavior must be selected or replaced at runtime.

### Keep the conditional when

- there are only one or two tiny, stable branches;
- the branches are unlikely to evolve independently;
- introducing new types makes the behavior harder to follow; or
- the caller legitimately owns the whole decision and its rules.

### Costs introduced by Strategy

- more types and files;
- indirection while navigating and debugging;
- a construction/selection decision elsewhere; and
- a risk of creating interfaces that do not represent stable domain capabilities.

The goal is not maximum abstraction. It is the simplest design that contains the change you realistically expect.

---

## 15. Mental model and review checklist

```text
requirements change
        ↓
algorithms vary independently
        ↓
identify the capability shared by those algorithms
        ↓
put that capability behind a stable contract
        ↓
compose one implementation into the stable workflow
```

Before calling a design “Strategy,” verify:

- [ ] The implementations are genuinely interchangeable from the caller's view.
- [ ] The interface describes a capability the caller needs.
- [ ] Each strategy owns one coherent algorithm.
- [ ] The context depends only on the strategy contract.
- [ ] Selection is separate from algorithm implementation.
- [ ] Strategies and context can be tested independently.
- [ ] The extra abstraction costs less than the change pressure it contains.

## Next lesson

Strategy answers:

> Which interchangeable algorithm should execute?

It leaves a related question:

> Who constructs and selects the correct strategy without duplicating that knowledge?

That pressure leads to **Lesson 2 — Factory**.

---

## Official verification sources

Only first-party documentation was used for Java and IntelliJ setup:

- Oracle, [JDK 25 Installation Guide](https://docs.oracle.com/en/java/javase/25/install/)
- Oracle, [The `javac` Command — Java 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)
- Oracle, [The `java` Command — Java 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html)
-
JetBrains, [Create your first Java application](https://www.jetbrains.com/help/idea/creating-and-running-your-first-java-application.html)
- JetBrains, [Supported Java versions and features](https://www.jetbrains.com/help/idea/supported-java-versions.html)
- JetBrains, [Java 25 LTS and IntelliJ IDEA](https://blog.jetbrains.com/idea/2025/09/java-25-lts-and-intellij-idea/)
