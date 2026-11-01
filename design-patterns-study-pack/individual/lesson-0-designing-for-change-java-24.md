# Lesson 0 — Designing for Change

> A first-principles introduction to cohesion, coupling, dependencies, abstraction, and composition using Java 24.

## Why this lesson exists

Design patterns are not class diagrams to memorize. They are recurring responses to recurring design pressure.

```text
Requirements change
      ↓
Some code changes frequently
      ↓
That change starts affecting unrelated code
      ↓
We identify what varies independently
      ↓
We create an appropriate boundary
      ↓
A recognizable pattern emerges
```

In this course, every pattern will be approached in the same way:

1. Build the simplest thing that works.
2. Change the requirements.
3. Observe where the design becomes painful.
4. Diagnose the cause rather than treating only the symptom.
5. Refactor in small steps.
6. Test the resulting behavior.
7. Name the pattern only after understanding why it exists.
8. Evaluate its benefits, costs, and appropriate use.

## Learning objectives

By the end of Lesson 0, you should be able to:

- resist adding abstractions before there is evidence that they help;
- distinguish a symptom, such as a long method, from its design cause;
- identify an **axis of change**—something that varies independently;
- explain cohesion, coupling, and dependencies in practical terms;
- separate policy-selection code from business-calculation code;
- recognize where a future abstraction may be useful without implementing it prematurely.

---

# Part 1 — Set up Java 24 and IntelliJ IDEA

## 1. Understand the version choice

JDK 24 reached general availability on March 18, 2025. It is a non-LTS release and has since been superseded. Oracle's Java 24 archive warns that archived JDKs no longer receive the latest security fixes and are not recommended for production. Java 24 is suitable here because this is a local learning project; use a currently supported LTS JDK for a new production application.

Use **IntelliJ IDEA 2025.1 or newer**. JetBrains documents full Java 24 support beginning with IntelliJ IDEA 2025.1. A current IntelliJ IDEA release also supports Java 24.

Official references:

- [OpenJDK project: JDK 24](https://openjdk.org/projects/jdk/24/)
- [JetBrains: IntelliJ IDEA 2025.1 and Java 24 support](https://www.jetbrains.com/idea/whatsnew/2025-1/)
- [Oracle: Java SE 24 archive downloads](https://www.oracle.com/java/technologies/javase/jdk24-archive-downloads.html)

## 2. Install IntelliJ IDEA

1. Download IntelliJ IDEA from [JetBrains](https://www.jetbrains.com/idea/download/).
2. Install and launch it.
3. On the Welcome screen, confirm the displayed version is 2025.1 or newer. You can also check **Help → About** after opening the IDE.

The free edition is sufficient for this lesson.

## 3. Obtain JDK 24

The JDK contains the Java compiler, runtime, debugger support, standard libraries, and development tools. IntelliJ IDEA's bundled runtime runs the IDE itself; it is not a replacement for the project JDK.

### Preferred route: download through IntelliJ IDEA

1. From the Welcome screen, select **New Project**.
2. Select **Java**.
3. Open the **JDK** list and select **Download JDK**.
4. Select version **24**.
5. Select **Oracle OpenJDK** if it is available. JetBrains recommends Oracle OpenJDK when you do not have a vendor-specific requirement.
6. Keep the suggested installation location and select **Download**.

JetBrains documents this workflow in [SDKs — Configure and download a JDK](https://www.jetbrains.com/help/idea/sdk.html).

### Fallback: install JDK 24 manually

If version 24 is no longer offered by IntelliJ's downloader:

1. Open the [OpenJDK archive](https://jdk.java.net/archive/) or [Oracle Java SE 24 archive](https://www.oracle.com/java/technologies/javase/jdk24-archive-downloads.html).
2. Choose the JDK 24.0.2 package matching your operating system and CPU:
   - Windows: x64 installer or ZIP;
   - macOS on Apple Silicon: Arm 64 DMG;
   - macOS on an Intel processor: x64 DMG;
   - Linux: the package or compressed archive appropriate for your distribution and CPU.
3. Install or extract the JDK.
4. In IntelliJ, open the JDK list and select **Add JDK from Disk**.
5. Select the JDK home directory. On macOS, an Oracle installation is typically under `/Library/Java/JavaVirtualMachines/jdk-24.jdk/Contents/Home`.

Oracle provides platform-specific instructions in the [JDK 24 Installation Guide](https://docs.oracle.com/en/java/javase/24/install/).

## 4. Create the project

In IntelliJ IDEA:

1. Select **New Project** from the Welcome screen, or **File → New → Project**.
2. Select **Java**.
3. Set **Name** to `design-patterns-from-first-principles`.
4. Choose a location you can find easily.
5. For **Build system**, select **IntelliJ**. This lesson uses no external dependencies, so a Maven or Gradle build is unnecessary.
6. For **JDK**, select the JDK 24 installation from the previous step.
7. Clear **Add sample code** so that we build from an empty project.
8. Select **Create**.

These steps follow JetBrains' official [Create your first Java application](https://www.jetbrains.com/help/idea/creating-and-running-your-first-java-application.html) workflow.

## 5. Verify the project configuration

1. Open **File → Project Structure → Project**.
2. Confirm **SDK** is JDK 24.
3. Set **Language level** to **24** without preview features.
4. Open **Project Structure → Modules → Dependencies**.
5. Confirm **Module SDK** is **Project SDK** or the same JDK 24 installation.
6. Select **Apply**, then **OK**.

This lesson does not use Java 24 preview features, so `--enable-preview` is not required.

## 6. Verify from IntelliJ's terminal

Open **View → Tool Windows → Terminal** and run:

```shell
java -version
javac -version
```

Both commands should report version 24, for example:

```text
openjdk version "24.0.2" ...
javac 24.0.2
```

If they do not, first recheck the Project SDK. Current IntelliJ IDEA versions expose the project JDK to the built-in terminal. If an already-open terminal still shows an older version, close that terminal session, reopen it, and run the commands again.

## 7. Create the package and first class

1. In the **Project** tool window, right-click `src`.
2. Select **New → Package**.
3. Name it `com.example.designpatterns.lesson0`.
4. Right-click the new package and select **New → Java Class**.
5. Name the class `Application`.
6. Replace its contents with:

```java
package com.example.designpatterns.lesson0;

public final class Application {
    private Application() {
        // This class is not meant to be instantiated.
    }

    public static void main(String[] args) {
        System.out.println("Lesson 0 is ready.");
    }
}
```

Select the green run icon beside `main`, then choose **Run 'Application.main()'**. The Run window should show:

```text
Lesson 0 is ready.
```

At this point, the Java 24 project is correctly configured.

---

# Part 2 — Start with the simplest design

The business gives us one requirement:

> Calculate the standard shipping price at $2 per kilogram.

Create `ShippingCalculator.java` in the lesson package:

```java
package com.example.designpatterns.lesson0;

public final class ShippingCalculator {
    public double calculate(double weightKg) {
        return weightKg * 2.0;
    }
}
```

Use it from `Application.main`:

```java
var calculator = new ShippingCalculator();
var shippingCost = calculator.calculate(10.0);

System.out.printf("Shipping cost: $%.2f%n", shippingCost);
```

Expected output:

```text
Shipping cost: $20.00
```

This is good code for the current requirement. There is:

- one operation;
- one algorithm;
- no meaningful variation;
- no demonstrated need for an interface, hierarchy, factory, or framework.

**First principle:** start with the simplest design that correctly expresses what the system currently does.

An abstraction has a cost: more concepts, files, indirection, object wiring, and navigation while debugging. Do not pay that cost before it buys something useful.

---

# Part 3 — Let the requirement change

The business now supports standard and express shipping:

- standard: `$2 × weight`;
- express: `$4 × weight + $10`.

Create `ShippingMethod.java`:

```java
package com.example.designpatterns.lesson0;

public enum ShippingMethod {
    STANDARD,
    EXPRESS
}
```

Change `ShippingCalculator`:

```java
package com.example.designpatterns.lesson0;

public final class ShippingCalculator {
    public double calculate(double weightKg, ShippingMethod method) {
        if (method == ShippingMethod.STANDARD) {
            return weightKg * 2.0;
        }

        if (method == ShippingMethod.EXPRESS) {
            return weightKg * 4.0 + 10.0;
        }

        throw new IllegalArgumentException("Unsupported shipping method: " + method);
    }
}
```

This is still reasonable.

A common mistake is to conclude:

> There is an `if`, so I need a design pattern.

Conditionals are not inherently bad. This method has two small branches that are easy to read, test, and change. Replacing them with several types would not yet make the design clearly better.

We used an enum instead of a raw string because the compiler can now help prevent misspellings and invalid method names. That is a type-safety improvement, not a design pattern.

---

# Part 4 — Add enough pressure to expose the problem

A few months later, shipping has independently evolving rules:

```text
standard
express
overnight
international
same-day
store pickup
partner delivery
```

The input is now an order, not just a weight. Create `Order.java`:

```java
package com.example.designpatterns.lesson0;

public record Order(
        double weightKg,
        double merchandiseTotal,
        boolean remoteDestination
) {
    public Order {
        if (weightKg < 0) {
            throw new IllegalArgumentException("Weight cannot be negative");
        }

        if (merchandiseTotal < 0) {
            throw new IllegalArgumentException("Merchandise total cannot be negative");
        }
    }
}
```

Add `OVERNIGHT` to `ShippingMethod`, then imagine the calculator growing into this:

```java
package com.example.designpatterns.lesson0;

public final class ShippingCalculator {
    public double calculate(Order order, ShippingMethod method) {
        if (method == ShippingMethod.STANDARD) {
            var price = order.weightKg() * 2.0;

            if (order.merchandiseTotal() > 100.0) {
                price -= 5.0;
            }

            return price;
        }

        if (method == ShippingMethod.EXPRESS) {
            var price = order.weightKg() * 4.0 + 10.0;

            if (order.remoteDestination()) {
                price += 15.0;
            }

            return price;
        }

        if (method == ShippingMethod.OVERNIGHT) {
            var price = order.weightKg() * 7.0 + 25.0;

            if (order.remoteDestination()) {
                price += 30.0;
            }

            return price;
        }

        throw new IllegalArgumentException("Unsupported shipping method: " + method);
    }
}
```

The important observation is not merely that the method is long. Length is a symptom. The deeper problem is that several business policies that can change independently live in one module.

```text
Standard rules change ─────┐
Express rules change ──────┤
Overnight rules change ────┼──> ShippingCalculator
International rules change┤
Pickup rules change ───────┘
```

Changing overnight shipping requires opening a class that also contains standard and express shipping. A mistake in one edit can affect unrelated behavior, and the class must be retested as a broad unit.

---

# Part 5 — Diagnose from first principles

## Axis of change

Ask:

> What can vary independently?

In this example:

```text
Checkout workflow     mostly stable
Shipping algorithms  vary independently and increasingly often
```

The shipping algorithm is an **axis of change**. Finding such axes is more valuable than searching a pattern catalog for a class diagram that looks familiar.

## Cohesion

**Cohesion** describes how strongly the responsibilities inside a unit belong together.

- A class containing only standard-shipping rules has high policy cohesion.
- A class containing every unrelated shipping policy has weaker cohesion, even though all the code is broadly about “shipping.”

A useful question is:

> Do these lines usually change for the same business reason?

If the answer is no, they may not belong in the same unit.

## Coupling

**Coupling** is the degree to which one part of the system knows about or depends on another.

The growing calculator couples one module to every shipping policy. Checkout code may also become coupled to the list of supported methods if it contains both method selection and pricing rules.

Coupling is not automatically bad; software must have dependencies to do useful work. The goal is to keep coupling deliberate and prevent independently changing details from becoming unnecessarily entangled.

## Dependencies

If class A names, creates, calls, inherits from, or reads details from class B, A depends on B in some way.

Dependencies determine the direction in which change can travel. When stable checkout code directly knows every concrete shipping rule, a new shipping option can force changes through stable code.

## Abstraction

An abstraction describes what a caller needs without exposing every implementation detail.

Later, checkout will need something that can answer:

> What is the shipping cost for this order?

That capability can become a stable boundary. However, Lesson 0 stops before introducing that interface. First we want evidence that the boundary corresponds to real, independently changing behavior.

## Composition

Composition means building behavior by giving an object its collaborators rather than making it contain or choose every possible behavior itself.

This will eventually let checkout use a selected shipping policy without knowing all policies. For now, simply notice the design opportunity:

```text
STABLE CODE

Checkout
   |
   | needs a shipping price
   v
????????????????????   ← a boundary may belong here
   ^
   |
VARIABLE CODE

Standard / Express / Overnight / ...
```

---

# Part 6 — Make one small refactor, not the final leap

Before introducing a new abstraction, improve local cohesion by extracting each calculation into a named method:

```java
package com.example.designpatterns.lesson0;

public final class ShippingCalculator {
    public double calculate(Order order, ShippingMethod method) {
        return switch (method) {
            case STANDARD -> standardCost(order);
            case EXPRESS -> expressCost(order);
            case OVERNIGHT -> overnightCost(order);
        };
    }

    private double standardCost(Order order) {
        var price = order.weightKg() * 2.0;
        return order.merchandiseTotal() > 100.0 ? price - 5.0 : price;
    }

    private double expressCost(Order order) {
        var price = order.weightKg() * 4.0 + 10.0;
        return order.remoteDestination() ? price + 15.0 : price;
    }

    private double overnightCost(Order order) {
        var price = order.weightKg() * 7.0 + 25.0;
        return order.remoteDestination() ? price + 30.0 : price;
    }
}
```

This refactor improves readability and local cohesion. It does **not** solve the deeper coupling problem: every policy still lives in one class, and adding a method still requires modifying the switch and that class.

That distinction matters. A refactor can improve one design property without solving every problem.

The switch is not the enemy. Its current job mixes policy selection with a class that owns all policy implementations. In the next lesson, selection will remain somewhere in the system, but the algorithms will move behind a capability-oriented boundary.

---

# Part 7 — Check the behavior without a testing library

Create `Lesson0Checks.java`:

```java
package com.example.designpatterns.lesson0;

public final class Lesson0Checks {
    private static final double TOLERANCE = 0.000_001;

    private Lesson0Checks() {
    }

    public static void main(String[] args) {
        var calculator = new ShippingCalculator();

        var localOrder = new Order(10.0, 80.0, false);
        check(20.0, calculator.calculate(localOrder, ShippingMethod.STANDARD));
        check(50.0, calculator.calculate(localOrder, ShippingMethod.EXPRESS));
        check(95.0, calculator.calculate(localOrder, ShippingMethod.OVERNIGHT));

        var remoteOrder = new Order(10.0, 150.0, true);
        check(15.0, calculator.calculate(remoteOrder, ShippingMethod.STANDARD));
        check(65.0, calculator.calculate(remoteOrder, ShippingMethod.EXPRESS));
        check(125.0, calculator.calculate(remoteOrder, ShippingMethod.OVERNIGHT));

        System.out.println("All Lesson 0 checks passed.");
    }

    private static void check(double expected, double actual) {
        if (Math.abs(expected - actual) > TOLERANCE) {
            throw new AssertionError(
                    "Expected " + expected + " but received " + actual
            );
        }
    }
}
```

Run `Lesson0Checks.main`. Expected output:

```text
All Lesson 0 checks passed.
```

This deliberately uses a tiny executable check instead of introducing Maven/Gradle and JUnit before they are needed. A later lesson can add a real unit-testing framework.

> Production note: money should normally use `BigDecimal` or a dedicated money type rather than `double`. We use `double` here to keep the lesson focused on design forces.

---

# Part 8 — Hands-on exercise

Add an `INTERNATIONAL` shipping method with these rules:

```text
base price       = $30
weight charge    = $8 per kilogram
remote surcharge = $20 when the destination is remote
```

Work in this order:

1. Add the enum value.
2. Add the new switch branch.
3. Add a focused `internationalCost` method.
4. Add at least two checks: local and remote.
5. Run all existing checks.
6. Record every existing file you had to modify.

Then answer:

1. What varied?
2. What remained stable?
3. Which class knows every shipping method?
4. Which code performs selection?
5. Which code implements business calculations?
6. Can the international calculation be tested without exercising the switch?
7. If ten teams owned ten shipping policies, would one shared class remain comfortable to change?
8. What capability does checkout actually need?

Do not introduce an interface yet. The exercise is diagnostic: experience the change pressure before applying a pattern.

---

# Lesson 0 summary

The central design principle is:

> Separate things that change independently—but only when the separation earns its cost.

You observed the progression:

```text
One algorithm
   ↓
Simple conditional
   ↓
Several independently changing policies
   ↓
Weak cohesion and unnecessary coupling become visible
   ↓
An axis of change suggests a future boundary
```

You have not implemented a named design pattern yet. That is intentional. The next lesson will introduce the smallest stable contract checkout needs and separate the shipping algorithms behind it. Once derived from the problem, that structure will have a name: **Strategy**.

## Definition of done

Before moving to Lesson 1, confirm that:

- IntelliJ IDEA uses Project SDK 24 and language level 24;
- `java -version` and `javac -version` report 24 in IntelliJ's terminal;
- `Application.main` runs;
- `Lesson0Checks.main` prints `All Lesson 0 checks passed.`;
- you can explain why the growing calculator has a design problem without saying only “it is long”;
- you can identify the shipping algorithm as the axis of change;
- you understand why we did not start with an interface.

## Troubleshooting

### `invalid source release: 24`

The compiler or build process is using an older JDK. Recheck **File → Project Structure → Project → SDK**, then the module SDK under **Modules → Dependencies**.

### `release version 24 not supported`

The configured compiler is older than JDK 24. Select the JDK 24 installation as the Project SDK; changing only the language level is not enough.

### `java -version` shows a different version

Confirm the Project SDK, close the current built-in terminal session, and open a new one. If you are using an external terminal, its `PATH` and `JAVA_HOME` configuration is separate from the IntelliJ project SDK.

### No run icon appears next to `main`

Confirm the file is below a source root (normally `src`, shown in blue), the package declaration matches its folder, and the Project SDK is configured.

### `Unsupported shipping method` or a non-exhaustive switch after the exercise

After adding an enum constant, update the switch expression. Java's exhaustiveness check is useful feedback: the compiler is showing you where the code depends on the complete set of shipping methods.

---

# Verified official sources

Setup details were checked on August 31, 2026 against:

- [JetBrains — Create your first Java application](https://www.jetbrains.com/help/idea/creating-and-running-your-first-java-application.html)
- [JetBrains — SDKs: configure a project JDK](https://www.jetbrains.com/help/idea/sdk.html)
- [JetBrains — Supported Java versions and features](https://www.jetbrains.com/help/idea/supported-java-versions.html)
- [JetBrains — IntelliJ IDEA 2025.1: full Java 24 support](https://www.jetbrains.com/idea/whatsnew/2025-1/)
- [Oracle — JDK Installation Guide, Release 24](https://docs.oracle.com/en/java/javase/24/install/)
- [Oracle — Java SE 24 archive downloads and security warning](https://www.oracle.com/java/technologies/javase/jdk24-archive-downloads.html)
- [OpenJDK — JDK 24 project](https://openjdk.org/projects/jdk/24/)
