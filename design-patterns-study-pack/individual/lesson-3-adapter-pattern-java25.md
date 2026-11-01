Design Patterns
Java 25

# Adapter Pattern from First Principles

A hands-on design and implementation guide derived from Lesson 3. The goal is to understand the engineering pressure that creates an Adapter, not to memorize a class diagram.

**Compatibility note.** The sample is written for Java 25 and intentionally uses no preview features. It uses records for small domain/value types; Oracle documents records as standard Java language constructs. The source was also compiled and executed successfully with the available JDK 21, which is a conservative compatibility check for Java 25.

**Contents**

1. [What problem are we solving?](#goal)
2. [Baseline application boundary](#baseline)
3. [The incompatible SDK](#mismatch)
4. [Deriving the Adapter](#derive)
5. [Java 25 implementation](#implementation)
6. [Testing the translation boundary](#testing)
7. [Error translation](#errors)
8. [Second vendor: deeper translation](#second)
9. [Adapter vs related patterns](#comparisons)
10. [Engineering thought process](#thought-process)
11. [Compile and run](#run)
12. [Exercise](#exercise)
13. [Official Java 25 references](#sources)

## 1. What problem are we solving?

An Adapter becomes useful when **our application needs one contract** but an existing or third-party component exposes a different contract. We do not want the mismatch to leak through the rest of the system.

```
CheckoutService
      |
      v
ShippingPolicy
      ^
      |
LegacyCarrierAdapter
      |
      v
LegacyCarrierClient
```

The design target is simple: `CheckoutService` knows only the capability it needs—`ShippingPolicy`. Vendor-specific method names, units, request objects, responses, and exceptions stay behind the adapter.

## 2. Baseline application boundary

### Domain model

```
package com.example.shipping.domain;

import java.math.BigDecimal;
import java.util.Objects;

public record Order(
        double weightKg,
        BigDecimal subtotal,
        String destinationZip) {

    public Order {
        if (!Double.isFinite(weightKg) || weightKg <= 0) {
            throw new IllegalArgumentException("weightKg must be finite and > 0");
        }
        Objects.requireNonNull(subtotal, "subtotal");
        if (subtotal.signum() < 0) {
            throw new IllegalArgumentException("subtotal must be >= 0");
        }
        if (destinationZip == null || destinationZip.isBlank()) {
            throw new IllegalArgumentException("destinationZip must not be blank");
        }
    }
}
```

The record is a small immutable data carrier. Validation belongs at construction because an invalid order should not circulate through the application.

### Capability required by checkout

```
package com.example.shipping.domain;

import java.math.BigDecimal;

@FunctionalInterface
public interface ShippingPolicy {
    BigDecimal calculate(Order order);
}
```

### Stable application code

```
package com.example.shipping.application;

import com.example.shipping.domain.Order;
import com.example.shipping.domain.ShippingPolicy;

import java.math.BigDecimal;
import java.util.Objects;

public final class CheckoutService {
    private final ShippingPolicy shippingPolicy;

    public CheckoutService(ShippingPolicy shippingPolicy) {
        this.shippingPolicy = Objects.requireNonNull(shippingPolicy);
    }

    public BigDecimal total(Order order) {
        return order.subtotal().add(shippingPolicy.calculate(order));
    }
}
```

**First-principles rule:** the consumer should depend on the capability it needs, not on details of a particular vendor.

## 3. The incompatible SDK

Assume the third-party SDK is outside our control:

```
package com.example.shipping.vendor.legacy;

import java.math.BigDecimal;

public class LegacyCarrierClient {

    // Simulates a third-party SDK that our application does not control.
    public BigDecimal getQuote(String destinationZip, long weightInGrams) {
        if ("00000".equals(destinationZip)) {
            throw new LegacyCarrierUnavailableException("Legacy carrier is unavailable");
        }

        // Example vendor pricing only.
        return BigDecimal.valueOf(12)
                .add(BigDecimal.valueOf(weightInGrams)
                        .multiply(BigDecimal.valueOf(0.002)));
    }
}
```

Our code wants `calculate(Order)`. The SDK gives us `getQuote(zip, grams)`. It also uses grams while our domain uses kilograms.

```
OUR APPLICATION                         THIRD-PARTY SDK

Order                                  getQuote(zip, grams)
  |                                            ^
  |                                            |
  +--> ShippingPolicy.calculate(order)         |
                 ^                              |
                 |                              |
                 +---- LegacyCarrierAdapter ----+
                       - extracts zip
                       - kg -> grams
                       - translates errors
```

**Weak solution:** inject `LegacyCarrierClient` directly into `CheckoutService` and perform conversions there. It works initially, but checkout then owns vendor knowledge and becomes coupled to the external API.

## 4. Deriving the Adapter

Ask four questions:

1. What contract does the application want? `ShippingPolicy`.
2. What contract does the external component provide? `getQuote(String, long)`.
3. What translation is necessary? Extract ZIP, convert kilograms to grams, translate vendor failures.
4. Where should this knowledge live? In one boundary object.

That boundary object is the Adapter.

## 5. Java 25 implementation

### The Adapter

```
package com.example.shipping.adapter;

import com.example.shipping.domain.Order;
import com.example.shipping.domain.ShippingPolicy;
import com.example.shipping.domain.ShippingUnavailableException;
import com.example.shipping.vendor.legacy.LegacyCarrierClient;
import com.example.shipping.vendor.legacy.LegacyCarrierUnavailableException;

import java.math.BigDecimal;
import java.util.Objects;

public final class LegacyCarrierAdapter implements ShippingPolicy {
    private final LegacyCarrierClient client;

    public LegacyCarrierAdapter(LegacyCarrierClient client) {
        this.client = Objects.requireNonNull(client);
    }

    @Override
    public BigDecimal calculate(Order order) {
        long weightInGrams = Math.round(order.weightKg() * 1_000.0);

        try {
            return client.getQuote(order.destinationZip(), weightInGrams);
        } catch (LegacyCarrierUnavailableException ex) {
            throw new ShippingUnavailableException(
                    "Shipping quote is temporarily unavailable", ex);
        }
    }
}
```

The adapter has two simultaneous views:

**Facing inward**
It is a normal `ShippingPolicy`. The application sees no vendor-specific API.

**Facing outward**
It knows how to call the legacy SDK and how to translate our domain representation into vendor representation.

### Composition

```
package com.example.shipping;

import com.example.shipping.adapter.LegacyCarrierAdapter;
import com.example.shipping.application.CheckoutService;
import com.example.shipping.domain.Order;
import com.example.shipping.vendor.legacy.LegacyCarrierClient;

import java.math.BigDecimal;

public final class Main {
    public static void main(String[] args) {
        var order = new Order(
                2.0,
                new BigDecimal("100.00"),
                "85001");

        var shipping = new LegacyCarrierAdapter(
                new LegacyCarrierClient());

        var checkout = new CheckoutService(shipping);

        System.out.println("Checkout total = $" + checkout.total(order));
    }
}
```

At runtime, dependency flow is:

```
Request
  |
  v
Factory (optional)
  |
  v
ShippingPolicy
  |
  +--> native Strategy
  |
  +--> LegacyCarrierAdapter --> Legacy SDK
  |
  +--> NewCarrierAdapter ----> New SDK
```

## 6. Test the translation boundary

The adapter's responsibility is translation, so tests should verify translation rather than merely checking that a method returned a value.

```
package com.example.shipping.adapter;

import com.example.shipping.domain.Order;
import com.example.shipping.domain.ShippingUnavailableException;
import com.example.shipping.vendor.legacy.LegacyCarrierClient;
import com.example.shipping.vendor.legacy.LegacyCarrierUnavailableException;
import com.example.shipping.vendor.newcarrier.NewCarrierApi;

import java.math.BigDecimal;

public final class AdapterTests {

    public static void main(String[] args) {
        shouldTranslateKilogramsToGrams();
        shouldTranslateVendorException();
        shouldTranslateNewCarrierRequestAndResponse();
        System.out.println("All adapter tests passed.");
    }

    private static void shouldTranslateKilogramsToGrams() {
        var client = new RecordingLegacyCarrierClient();
        var adapter = new LegacyCarrierAdapter(client);

        var order = new Order(
                2.0,
                new BigDecimal("100.00"),
                "85001");

        var result = adapter.calculate(order);

        assertEquals("85001", client.lastZip, "zip");
        assertEquals(2_000L, client.lastWeightInGrams, "grams");
        assertBigDecimalEquals("25.00", result, "quote");
    }

    private static void shouldTranslateVendorException() {
        var client = new LegacyCarrierClient() {
            @Override
            public BigDecimal getQuote(String zip, long grams) {
                throw new LegacyCarrierUnavailableException("vendor down");
            }
        };

        var adapter = new LegacyCarrierAdapter(client);
        var order = new Order(
                1.0,
                BigDecimal.ZERO,
                "85001");

        try {
            adapter.calculate(order);
            throw new AssertionError("Expected ShippingUnavailableException");
        } catch (ShippingUnavailableException expected) {
            // pass
        }
    }

    private static void shouldTranslateNewCarrierRequestAndResponse() {
        var api = new RecordingNewCarrierApi();
        var adapter = new NewCarrierAdapter(api);

        var order = new Order(
                1.0,
                BigDecimal.ZERO,
                "90210");

        var result = adapter.calculate(order);

        assertEquals("90210", api.lastRequest.postalCode(), "postal code");
        assertNear(2.2046226218, api.lastRequest.weightPounds(), 0.0000001, "pounds");
        assertBigDecimalEquals("35.00", result, "cents-to-dollars");
    }

    private static final class RecordingLegacyCarrierClient
            extends LegacyCarrierClient {

        private String lastZip;
        private long lastWeightInGrams;

        @Override
        public BigDecimal getQuote(String zip, long grams) {
            this.lastZip = zip;
            this.lastWeightInGrams = grams;
            return new BigDecimal("25.00");
        }
    }

    private static final class RecordingNewCarrierApi
            extends NewCarrierApi {

        private PriceRequest lastRequest;

        @Override
        public PriceResponse price(PriceRequest request) {
            this.lastRequest = request;
            return new PriceResponse(3_500);
        }
    }

    private static void assertEquals(Object expected, Object actual, String label) {
        if (!expected.equals(actual)) {
            throw new AssertionError(
                    label + ": expected=" + expected + ", actual=" + actual);
        }
    }

    private static void assertBigDecimalEquals(
            String expected,
            BigDecimal actual,
            String label) {

        var expectedValue = new BigDecimal(expected);
        if (expectedValue.compareTo(actual) != 0) {
            throw new AssertionError(
                    label + ": expected=" + expectedValue + ", actual=" + actual);
        }
    }

    private static void assertNear(
            double expected,
            double actual,
            double tolerance,
            String label) {

        if (Math.abs(expected - actual) > tolerance) {
            throw new AssertionError(
                    label + ": expected=" + expected + ", actual=" + actual);
        }
    }
}
```

The important assertions are:

* **2.0 kg becomes 2,000 grams** before the legacy API is called.
* The ZIP code is passed to the correct vendor parameter.
* A vendor exception becomes an application-level exception.
* The second vendor's cents response becomes the application's decimal money representation.

A test double that records vendor parameters is often more useful than a test that only stubs the return value. It tells you whether the adapter translated the request correctly.

## 7. Error translation

External exception types are also part of the vendor's model. Letting them escape means application services and controllers eventually need vendor-specific knowledge.

```
package com.example.shipping.domain;

public final class ShippingUnavailableException extends RuntimeException {
    public ShippingUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

```
package com.example.shipping.vendor.legacy;

public final class LegacyCarrierUnavailableException extends RuntimeException {
    public LegacyCarrierUnavailableException(String message) {
        super(message);
    }
}
```

`LegacyCarrierAdapter` catches the vendor exception and throws `ShippingUnavailableException`. This keeps the dependency direction clean:

```
Vendor model                        Application model

LegacyCarrierUnavailableException
              |
              v
       LegacyCarrierAdapter
              |
              v
ShippingUnavailableException
```

## 8. Second vendor: deeper translation

A second vendor makes the benefit clearer because its interface differs in multiple dimensions: request object, pounds rather than kilograms, and integer cents rather than decimal currency.

```
package com.example.shipping.vendor.newcarrier;

public class NewCarrierApi {

    public record PriceRequest(String postalCode, double weightPounds) {}

    public record PriceResponse(long amountInCents) {}

    public PriceResponse price(PriceRequest request) {
        long cents = Math.round(900 + (request.weightPounds() * 175));
        return new PriceResponse(cents);
    }
}
```

```
package com.example.shipping.adapter;

import com.example.shipping.domain.Order;
import com.example.shipping.domain.ShippingPolicy;
import com.example.shipping.vendor.newcarrier.NewCarrierApi;

import java.math.BigDecimal;
import java.util.Objects;

public final class NewCarrierAdapter implements ShippingPolicy {
    private static final double POUNDS_PER_KILOGRAM = 2.2046226218;

    private final NewCarrierApi api;

    public NewCarrierAdapter(NewCarrierApi api) {
        this.api = Objects.requireNonNull(api);
    }

    @Override
    public BigDecimal calculate(Order order) {
        double pounds = order.weightKg() * POUNDS_PER_KILOGRAM;

        var request = new NewCarrierApi.PriceRequest(
                order.destinationZip(),
                pounds);

        var response = api.price(request);

        return BigDecimal.valueOf(response.amountInCents())
                .movePointLeft(2);
    }
}
```

Notice that `CheckoutService` still does not change. Both vendor adapters satisfy the same application-owned boundary.

## 9. Adapter vs related patterns

| Pattern | Core question | Interface relationship |
| --- | --- | --- |
| **Adapter** | How can I use an incompatible existing component? | Converts one interface/model into another. |
| **Strategy** | How can I interchange algorithms? | Implementations already satisfy the same conceptual contract. |
| **Factory** | Who decides which concrete object gets created? | Centralizes or delegates construction. |
| **Decorator** | How can I add behavior without changing the wrapped implementation? | Wrapper normally preserves the same interface. |
| **Facade** | How can I offer a simpler entry point to a complex subsystem? | Simplifies a subsystem rather than primarily translating incompatibility. |

## 10. Engineering thought process

```
1. Identify the stable application capability.
         |
         v
2. Identify the external component's actual interface.
         |
         v
3. List every mismatch:
   - method name
   - parameter shape
   - units
   - response representation
   - exception model
         |
         v
4. Put those translations in one boundary object.
         |
         v
5. Make application code depend only on its own abstraction.
         |
         v
6. Test the translation boundary independently.
```

Do not start by saying “I need an Adapter.” Start with the dependency mismatch. If the mismatch is real and localized translation solves it, the Adapter pattern has emerged naturally.

### When not to use Adapter

If you own both sides and can safely change them to the same clean contract, an adapter may be unnecessary. Likewise, wrapping an already-compatible class just to match a textbook diagram creates indirection without reducing coupling.

## 11. Compile and run with JDK 25

The project contains no external dependencies. From the project root:

```
mkdir -p build/classes build/test-classes

javac --release 25 \
  -d build/classes \
  $(find src/main/java -name "*.java")

javac --release 25 \
  -cp build/classes \
  -d build/test-classes \
  $(find src/test/java -name "*.java")

java -cp build/classes com.example.shipping.Main

java -cp build/classes:build/test-classes \
  com.example.shipping.adapter.AdapterTests
```

Expected output:

```
Checkout total = $116.000
All adapter tests passed.
```

On Windows, replace the classpath separator `:` with `;`. Oracle recommends `--release` for compiling against a specific Java release.

## 12. Hands-on exercise: Old Bank SDK

Build an `OldBankAdapter` around this incompatible SDK:

```
public final class OldBankSdk {
    public BankResult chargeCents(String accountNumber, long amountInCents) {
        // third-party behavior
        return new BankResult("TX-123");
    }

    public record BankResult(String transactionCode) {}
}
```

Your application should own this contract:

```
public interface PaymentProcessor {
    PaymentResult pay(Payment payment);
}

public record Payment(String accountId, BigDecimal amount) {}
public record PaymentResult(String transactionId) {}
```

Acceptance criteria:

1. `PaymentService` never imports `OldBankSdk`.
2. `OldBankSdk` remains unchanged.
3. The adapter converts decimal currency to cents at the boundary.
4. The vendor's `transactionCode` becomes the application's `transactionId`.
5. Vendor result types do not escape the adapter.
6. A unit test records the arguments passed to `chargeCents`.

## 13. Official Java 25 references

* [Oracle Java SE 25 & JDK 25 API Specification](https://docs.oracle.com/en/java/javase/25/docs/).
* [Oracle: Record Classes](https://docs.oracle.com/en/java/javase/25/language/records.html) — records are concise data carriers with generated accessors and value-oriented methods.
* [Oracle: Java Language Changes Summary](https://docs.oracle.com/en/java/javase/25/language/java-language-changes-summary.html) — distinguishes permanent Java 25 features from preview features.
* [Oracle: Preparing for Migration](https://docs.oracle.com/en/java/javase/25/migrate/preparing-migration.html) — recommends `javac --release` for targeting a specific Java release.
* [Oracle: Java SE 25 & JDK 25 Specifications](https://docs.oracle.com/en/java/javase/25/docs/specs/index.html).

The Adapter design discussion is derived from the preceding Lesson 3 in this conversation. The Java language/tooling claims above are linked only to Oracle's official Java 25 documentation.

Adapter Pattern from First Principles — Java 25. Generated as a self-contained, print/PDF-friendly HTML study guide.