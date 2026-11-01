[Skip to guide](#main)

DP / DESIGN PATTERNS

Lesson 8
Builder

[01–05Find the pressure](#step-1)[06–10Derive the pattern](#step-6)[11–13Working implementation](#step-11)[14–17Strengthen the API](#step-14)[18–22Compare the options](#step-18)[23–27Stages and tests](#step-23)[Standard libraryJava 25 in practice](#jdk)[ExerciseDatabase configuration](#exercise)[ConnectionsPattern map](#map)[ReferencesOfficial sources](#sources)

First principles, then code.
Read offline. Print on A4 or Letter.

Lesson 08 · Creational pattern

# Builder

Control complex object construction.

Separate **collecting construction decisions** from **creating the final valid object**.

Java 25 compatibleNo preview featuresSelf-contained guide

Print / Save as PDFDownload Java examples

For PDF: use portrait, 100% scale, and turn browser headers/footers off. Background graphics are optional. All lesson content prints.

**How to use this guide.** Read the numbered steps in order to preserve the derivation. Earlier excerpts illustrate one idea; files marked “complete” form the runnable examples. Only Java basics—classes, methods, constructors, and collections—are assumed.

Part I · Find the pressure

## Start with the construction problem

A pattern earns its place by removing a concrete source of mistakes. Begin with the simplest API and watch where it stops helping.

## 01Start without Builder

Suppose we need a value describing an HTTP request. With just two required inputs, a constructor is readable. There is no construction problem to solve yet.

Java · focused excerptCopy

```
import java.net.URI;

record SimpleRequest(String method, URI uri) {}

// Inside a method:
var request = new SimpleRequest(
    "GET", URI.create("https://example.com/users")
);
```

The example is deliberately minimal; a real constructor would still validate its inputs. **Builder is not a prerequisite for validation or immutability.**

## 02Requirements grow

Now add headers, query parameters, a body, a timeout, authentication, compression, retry count, and redirects. A constructor begins to look like this:

Design sketch · the constructor API we are moving away fromCopy

```
new RequestSpec(
    "POST", uri, headers, queryParams, body,
    Duration.ofSeconds(10), token, true, 3, false
);
```

The arguments contain information, but the call hides their meaning. A reviewer must look up the parameter list to interpret `true, 3, false`. A new optional field adds more friction to every call site.

## 03First problem: positional ambiguity

Named construction steps make the decisions visible where the object is created. This is the API we will work toward:

Java · focused excerptCopy

```
var request = RequestSpec.builder(
        "POST", URI.create("https://example.com/orders"))
    .header("Content-Type", "application/json")
    .body("""
        {"productId":"P123"}
        """)
    .timeout(Duration.ofSeconds(5))
    .retryCount(3)
    .followRedirects(false)
    .build();
```

Each optional value now has a label. Our teaching type is called `RequestSpec` to distinguish it from `java.net.http.HttpRequest`. It stores configuration; creating it does not execute a request.

## 04Second problem: optional parameters

Constructor overloads can help briefly. As more combinations appear, they form a telescoping family that is hard to maintain and use.

Signatures only · telescoping constructor problemCopy

```
RequestSpec(String method, URI uri)
RequestSpec(String method, URI uri, String body)
RequestSpec(String method, URI uri, String body, Duration timeout)
// Which overload handles timeout with no body?
```

A builder lets the caller name just the optional decisions they want to change. Defaults stay inside the construction API.

## 05Third problem: invalid combinations

Construction is more than assigning fields. First, define what counts as a valid result. These are the rules for *our example application*:

| Input or combination | Rule |
| --- | --- |
| Method and URI | Both required. Support the seven uppercase methods listed in the code. Use an absolute HTTP(S) URI with a host, without user info or a fragment. |
| Timeout / retry count | Timeout is non-null and positive. Retry count is zero or greater. |
| GET or HEAD plus a body | Reject this combination. |
| POST plus a body | Require a nonblank Content-Type header. |
| Headers | One value per normalized name. Reject nulls, blank values, invalid names, and control characters other than tab. |

**Separate application policy from HTTP semantics**

The original lesson phrased “GET cannot have a body” as a general rule. RFC 9110 gives GET content no generally defined semantics and advises clients against it without prior server agreement. Our stricter rejection is an application policy. The POST/Content-Type requirement is also our policy. [[1]](#source-http)

We now have three jobs: **collect choices, validate them, and produce a valid value.** Separating these jobs gives us the pressure for Builder.

Part II · Derive the pattern

## A workspace for construction

The builder can be unfinished. The product should be usable as soon as it is returned.

## 06Build the immutable object first

Give the finished value private final fields, no setters, and a private constructor. The constructor snapshots the builder’s state. This excerpt comes from the complete class in step 11.

Java · focused excerptCopy

```
private RequestSpec(Builder builder) {
    method = builder.method;
    uri = builder.uri;
    headers = Map.copyOf(builder.headers);
    body = builder.body;
    timeout = builder.timeout;
    retryCount = builder.retryCount;
    followRedirects = builder.followRedirects;
}
```

A private constructor controls entry into this class’s normal public construction path. That only protects validity if every path that calls it validates correctly. The modifier alone does not establish the invariants.

## 07Create the Builder and give defaults one owner

Inside RequestSpec.BuilderCopy

```
private final String method;
private final URI uri;
private final Map<String, String> headers = new HashMap<>();
private String body;
private Duration timeout = Duration.ofSeconds(30);
private int retryCount = 0;
private boolean followRedirects = true;
```

The builder owns mutable optional configuration. Here the required fields are fixed when the builder is created; steps 14–15 explain that refinement. These defaults belong to `RequestSpec`, not to the JDK HTTP client.

## 08Add fluent methods

Java · focused excerptCopy

```
public Builder retryCount(int retryCount) {
    if (retryCount < 0) {
        throw new IllegalArgumentException("retryCount must be >= 0");
    }
    this.retryCount = retryCount;
    return this;
}
```

`return this` lets the next method operate on the same builder. It does not construct a new product. Validate an independently invalid argument before assigning it, so a rejected call leaves the existing configuration intact.

## 09Add a clear endpoint: build()

Java · focused excerptCopy

```
public RequestSpec build() {
    validateCombinations();
    return new RequestSpec(this);
}
```

The return type changes from `Builder` to `RequestSpec`. That is the boundary between preparing a configuration and using a finished value. If validation fails, no product is returned.

## 10Put each rule at the right boundary

| When | What to check | Failure in this guide |
| --- | --- | --- |
| Builder creation | Required inputs, supported method, URI shape | `NullPointerException` for null; otherwise `IllegalArgumentException` |
| Each fluent call | Nulls and constraints on that one argument | Same distinction |
| build() | Relationships between fields | `IllegalStateException` |

For example, a zero timeout is already invalid when supplied. A POST body without Content-Type may simply be unfinished configuration. Delaying that combination check permits either `body(...).header(...)` or `header(...).body(...)`.

This split is a design choice, not a universal Builder contract. The Java 25 `ModuleDescriptor.Builder` documentation explicitly describes checking components and invariants as components are added. [[2]](#source-module)

**Keep the scope deliberate**

The working implementation below omits query-parameter assembly, authentication, and compression. They motivated the problem, but they are not needed to demonstrate the pattern. Its header map is a simplified single-value model, and its retry count is configuration, not retry logic.

Part III · Make it concrete

## One complete, consistent implementation

All parts below form RequestSpec.java. Copy them in order, or use the bundled source download at the top of the guide.

## 11Complete implementation

Save this as `RequestSpec.java`. It uses standard Java APIs and no preview features or third-party dependencies. Header names are normalized with `Locale.ROOT`; repeated names replace their previous value in this example.

RequestSpec.java · 1 of 4 · immutable product and accessorsCopy

```
import java.net.URI;
import java.time.Duration;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Teaching configuration value; building it sends no network request. */
public final class RequestSpec {
    private final String method;
    private final URI uri;
    private final Map<String, String> headers;
    private final String body;
    private final Duration timeout;
    private final int retryCount;
    private final boolean followRedirects;

    private RequestSpec(Builder builder) {
        method = builder.method;
        uri = builder.uri;
        headers = Map.copyOf(builder.headers);
        body = builder.body;
        timeout = builder.timeout;
        retryCount = builder.retryCount;
        followRedirects = builder.followRedirects;
    }

    public static Builder builder(String method, URI uri) {
        return new Builder(method, uri);
    }

    public String method() { return method; }
    public URI uri() { return uri; }
    public Map<String, String> headers() { return headers; }
    // null means no body; an empty string still means a body was supplied.
    public String body() { return body; }
    public Duration timeout() { return timeout; }
    public int retryCount() { return retryCount; }
    public boolean followRedirects() { return followRedirects; }
```

RequestSpec.java · 2 of 4 · required values and defaultsCopy

```
    public static final class Builder {
        private static final Set<String> METHODS = Set.of(
            "GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"
        );

        private final String method;
        private final URI uri;
        private final Map<String, String> headers = new HashMap<>();
        private String body;
        private Duration timeout = Duration.ofSeconds(30);
        private int retryCount = 0;
        private boolean followRedirects = true;

        private Builder(String method, URI uri) {
            Objects.requireNonNull(method, "method");
            Objects.requireNonNull(uri, "uri");
            if (!METHODS.contains(method)) {
                throw new IllegalArgumentException("Unsupported method");
            }
            boolean http = "http".equalsIgnoreCase(uri.getScheme());
            boolean https = "https".equalsIgnoreCase(uri.getScheme());
            if ((!http && !https) || uri.getHost() == null
                    || uri.getUserInfo() != null || uri.getFragment() != null) {
                throw new IllegalArgumentException(
                    "Use an absolute HTTP(S) URI without user info or fragment"
                );
            }
            this.method = method;
            this.uri = uri;
        }
```

RequestSpec.java · 3 of 4 · fluent optionsCopy

```
        // One value per name; a repeated name replaces its previous value.
        public Builder header(String name, String value) {
            Objects.requireNonNull(name, "header name");
            Objects.requireNonNull(value, "header value");
            if (!name.matches("[!#$%&'*+.^_`|~0-9A-Za-z-]+")) {
                throw new IllegalArgumentException("Invalid header name");
            }
            if (value.isBlank() || value.chars().anyMatch(
                    c -> c == 127 || (c < 32 && c != '\t'))) {
                throw new IllegalArgumentException("Invalid header value");
            }
            headers.put(name.toLowerCase(Locale.ROOT), value);
            return this;
        }

        public Builder body(String body) {
            this.body = Objects.requireNonNull(body, "body");
            return this;
        }

        public Builder timeout(Duration timeout) {
            Objects.requireNonNull(timeout, "timeout");
            if (timeout.isZero() || timeout.isNegative()) {
                throw new IllegalArgumentException("timeout must be positive");
            }
            this.timeout = timeout;
            return this;
        }

        public Builder retryCount(int retryCount) {
            if (retryCount < 0) {
                throw new IllegalArgumentException("retryCount must be >= 0");
            }
            this.retryCount = retryCount;
            return this;
        }

        public Builder followRedirects(boolean value) {
            followRedirects = value;
            return this;
        }
```

RequestSpec.java · 4 of 4 · final combination checksCopy

```
        public RequestSpec build() {
            validateCombinations();
            return new RequestSpec(this);
        }

        private void validateCombinations() {
            if ((method.equals("GET") || method.equals("HEAD"))
                    && body != null) {
                throw new IllegalStateException(
                    "This application forbids a body on GET or HEAD"
                );
            }
            if (method.equals("POST") && body != null
                    && !headers.containsKey("content-type")) {
                throw new IllegalStateException(
                    "POST with a body requires Content-Type in this application"
                );
            }
        }
    }
}
```

Notice the explicit accessors. A normal class does not generate record-style methods such as `timeout()` for you. They are included so the usage and checks later in this guide compile.

**Construction does not promise execution safety**

Accepting `retryCount(3)` does not make retrying a POST safe. The executor still needs an operation-specific retry policy and, when appropriate, idempotency protection. Builder controls configuration validity, not network outcomes.

## 12Why make the final object immutable?

Once a request configuration is valid, another caller should not be able to silently change it. This implementation combines final fields with immutable component types and an isolated header map.

`Map.copyOf` returns an unmodifiable map whose entries do not track later changes to the source map. It rejects null keys and values. It is *not a deep copy*: mutable keys or values would still need their own copying policy. Here both are strings. [[3]](#source-map)

**Final references are not deep immutability**

A `final Map` field alone only prevents reassignment of the field. If the referenced map were mutable and exposed, the product’s contents could still change.

## 13The Builder is a temporary workspace

Java · focused excerptCopy

```
var builder = RequestSpec.builder(
        "GET", URI.create("https://example.com/users"))
    .header("X-Mode", "first");

var first = builder.build();
var second = builder.header("x-mode", "second").build();

System.out.println(first.headers().get("x-mode"));  // first
System.out.println(second.headers().get("x-mode")); // second
```

Our builder is reusable. Each successful build creates a new snapshot, so editing the workspace does not change an earlier product. A POST builder may temporarily have a body without Content-Type; `build()` is where that unfinished state is rejected.

Keep each mutable builder confined to one thread. This implementation has no synchronization. Do not infer builder safety from product immutability; the JDK request builder similarly documents that its methods are not synchronized. [[4]](#source-jdk-request)

Part IV · Strengthen the construction API

## Make the important choices hard to miss

Improve the API without making every possible mistake a type-system problem.

## 14Required parameters

An all-setter API lets a caller forget required fields and discover the mistake only at `build()`:

Design sketch · omitted required fieldsCopy

```
// Earlier API design, not the final RequestSpec API:
RequestSpec.builder().retryCount(3).build();
```

The final API requires both values at the entry point:

Java · focused excerptCopy

```
public static Builder builder(String method, URI uri) {
    return new Builder(method, uri);
}
```

The compiler enforces the number and types of arguments. It does not prove that a string is valid or a URI is non-null. The builder constructor still validates the supplied values.

## 15Constructor + Builder can work together

| Kind of decision | API location | Example |
| --- | --- | --- |
| Required | Builder factory / private builder constructor | `builder("POST", uri)` |
| Optional | Named fluent method | `.timeout(Duration.ofSeconds(5))` |
| Omitted optional value | Builder field initializer | `30 seconds` |
| Final consistency | `build()` | POST body has Content-Type |

Keep the required set small and meaningful. If two required arguments have the same type and are easy to swap, a builder alone does not remove that ambiguity. Better names, a value type, or a different entry point may help.

## 16Validate contradictory combinations

Suppose a future version supports API key, bearer token, and basic credentials, with an application rule allowing only one mode. Separate setters could accidentally configure several.

Extension sketch · these fields are not in RequestSpecCopy

```
// Excerpt from a hypothetical authentication-enabled builder.
private void validateAuthentication() {
    int configured = 0;
    if (apiKey != null) configured++;
    if (bearerToken != null) configured++;
    if (basicCredentials != null) configured++;
    if (configured > 1) {
        throw new IllegalStateException("Choose one authentication mode");
    }
}
```

Rejecting contradictions is one option. Another is a single `authentication(Auth choice)` field with distinct types for each supported choice. Model mutually exclusive states directly when that makes the API simpler.

## 17Builder is more than fluent syntax

Builder can own defaults, normalization, derived values, and cross-field rules. But each operation should have clear semantics. In this guide, header normalization occurs when a header is added, and `build()` validates and snapshots without changing the builder.

From header(...) · explicit normalizationCopy

```
headers.put(name.toLowerCase(Locale.ROOT), value);
```

If you add a default User-Agent later, choose one authoritative place to apply it. A surprising `build()` method that silently edits the workspace can make repeated builds harder to reason about. Avoid network calls and other execution side effects during simple value construction.

Part V · Compare the responsibilities

## Choose the smallest useful abstraction

Builder is one construction tool. It does not replace constructors, records, or factories.

## 18Builder vs Factory

| Tool | Question it helps answer | Typical shape |
| --- | --- | --- |
| Factory | What object should the caller receive, and how can creation be hidden? | `factory.create(kind)` |
| Builder | How can several construction decisions be collected and checked? | `builder.option(...).build()` |

A factory often selects an implementation, as in the earlier lesson, but factories are broader than type selection. A factory may also create a single concrete type or return a configured builder.

## 19Factory + Builder

Consider database clients. A factory could select a Postgres implementation. Its builder could collect host, port, timeout, pool size, and SSL options. The first responsibility is choosing or hiding creation; the second is assembling configuration.

| Stage | Responsibility |
| --- | --- |
| Database factory | Select an appropriate client or builder. |
| Concrete client builder | Collect supported configuration and reject invalid combinations. |
| Constructed client/config | Expose the finished API to its caller. |

Use both only if both responsibilities exist. Returning a builder from a factory is a possible design, not a required pattern arrangement.

## 20Builder vs setters

Design sketch · partially initialized productCopy

```
// An API that exposes a half-configured product:
var request = new MutableRequest();
request.setMethod("POST");
send(request); // What URI would this use?
```

The issue is that the object can escape before it is ready. A separate builder gives unfinished state a separate type. Code that requires a `RequestSpec` cannot receive a `RequestSpec.Builder` by accident.

Setters are not always wrong. They suit objects whose valid behavior includes mutation. The goal here is a stable configuration value, so a construction boundary is useful.

## 21Builder vs Java records

Java · small values with direct constructionCopy

```
record Point(int x, int y) {}

record Money(long cents, String currency) {
    Money {
        if (currency == null || currency.isBlank()) {
            throw new IllegalArgumentException("currency is required");
        }
    }
}
```

A compact value with a clear constructor often needs no builder. A record can also validate in its canonical or compact constructor. Java records are shallowly immutable: a record component can still refer to a mutable collection. [[5]](#source-record)

Records and builders are compatible. A complex record can have a builder, but its public canonical constructor remains an entry point, so put essential validity checks where that path enforces them too.

## 22Builder can become overengineering

For `record Person(String name) {}`, `new Person("Alice")` is usually already clear. Adding a mutable workspace and several methods should solve a real problem, not satisfy a field-count rule.

| Construction pressure | Start here |
| --- | --- |
| A few clear, required values | A constructor or record. |
| A named creation operation or implementation selection | A factory. |
| Many optional choices, defaults, or cross-field rules | Consider a builder. |
| A consequential required sequence | Consider a staged builder after simpler APIs. |

**Several meaningful pressures are stronger evidence than “this class has five fields.”**

Part VI · Add guarantees carefully

## Stages, validity, and executable checks

Stronger APIs have a cost. Add complexity only where it prevents a problem that matters.

## 23Staged Builder

A staged API can expose only the next valid construction step. The following complete optional wrapper uses our existing builder for validation, instead of duplicating its rules. Save it as `StagedRequest.java`.

StagedRequest.java · complete optional wrapperCopy

```
import java.net.URI;
import java.time.Duration;

public final class StagedRequest {
    private StagedRequest() {}

    public interface MethodStep {
        UriStep method(String method);
    }

    public interface UriStep {
        OptionsStep uri(URI uri);
    }

    public interface OptionsStep {
        OptionsStep header(String name, String value);
        OptionsStep body(String body);
        OptionsStep timeout(Duration timeout);
        RequestSpec build();
    }

    public static MethodStep builder() { return new Steps(); }

    private static final class Steps
            implements MethodStep, UriStep, OptionsStep {
        private String method;
        private RequestSpec.Builder delegate;

        @Override
        public UriStep method(String method) {
            this.method = method;
            return this;
        }

        @Override
        public OptionsStep uri(URI uri) {
            delegate = RequestSpec.builder(method, uri);
            return this;
        }

        @Override
        public OptionsStep header(String name, String value) {
            delegate.header(name, value);
            return this;
        }

        @Override
        public OptionsStep body(String body) {
            delegate.body(body);
            return this;
        }

        @Override
        public OptionsStep timeout(Duration timeout) {
            delegate.timeout(timeout);
            return this;
        }

        @Override
        public RequestSpec build() { return delegate.build(); }
    }
}
```

Java · focused excerptCopy

```
var request = StagedRequest.builder()
    .method("POST")
    .uri(URI.create("https://example.com/orders"))
    .header("Content-Type", "application/json")
    .body("{}")
    .build();

// StagedRequest.builder().build(); // does not compile
```

The normal typed chain requires a method step, then a URI step, before `build()` appears. It still permits bad values such as `null`, which runtime validation must reject. The extra interfaces do not guarantee semantic correctness or make this mutable wrapper safe to share.

For two required values, `RequestSpec.builder(method, uri)` is usually simpler. A staged API is justified when the construction sequence itself deserves enforcement.

## 24Builder and object validity

The broader principle is to create a valid object and then use it. Constructors, factories, parsers, and builders can all enforce that boundary.

| Before build() | After a successful build() |
| --- | --- |
| The workspace may be incomplete. | All documented construction rules hold. |
| Optional choices can change. | The returned value is stable. |
| No execution has happened. | Execution has still not happened. |

A valid request configuration does not prove that a server exists, the credentials work, or a future request will succeed. Those are execution concerns. Keep the guarantee precise.

## 25Test the construction contract

Test defaults, configured options, invalid input, cross-field rules, and snapshot isolation. The following file has no test-framework dependency and uses explicit failures rather than Java’s optional `assert` mechanism. Save it as `BuilderChecks.java`.

BuilderChecks.java · 25 executable checksCopy

```
import java.net.URI;
import java.time.Duration;

public final class BuilderChecks {
    private static final URI USERS = URI.create("https://example.com/users");
    private static final URI ORDERS = URI.create("https://example.com/orders");
    private static int checks;

    public static void main(String[] args) {
        var defaults = RequestSpec.builder("GET", USERS).build();
        check(defaults.timeout().equals(Duration.ofSeconds(30)), "timeout default");
        check(defaults.retryCount() == 0, "retry default");
        check(defaults.followRedirects(), "redirect default");
        check(defaults.headers().isEmpty() && defaults.body() == null, "empty defaults");

        var configured = RequestSpec.builder("POST", ORDERS)
            .body("{}") // cross-field rules wait until build()
            .header("CONTENT-TYPE", "application/json")
            .timeout(Duration.ofSeconds(5))
            .retryCount(3)
            .followRedirects(false)
            .build();
        check(configured.method().equals("POST") && configured.uri().equals(ORDERS),
            "required values");
        check(configured.timeout().equals(Duration.ofSeconds(5))
            && configured.retryCount() == 3 && !configured.followRedirects(),
            "configured options");
        check("application/json".equals(configured.headers().get("content-type")),
            "header normalization");

        expect(NullPointerException.class,
            () -> RequestSpec.builder(null, USERS));
        expect(NullPointerException.class,
            () -> RequestSpec.builder("GET", null));
        expect(IllegalArgumentException.class,
            () -> RequestSpec.builder("get", USERS));
        expect(IllegalArgumentException.class,
            () -> RequestSpec.builder("GET", URI.create("/users")));
        expect(IllegalArgumentException.class,
            () -> RequestSpec.builder("GET", USERS).retryCount(-1));
        expect(NullPointerException.class,
            () -> RequestSpec.builder("GET", USERS).timeout(null));
        expect(IllegalArgumentException.class,
            () -> RequestSpec.builder("GET", USERS).timeout(Duration.ZERO));
        expect(IllegalArgumentException.class,
            () -> RequestSpec.builder("GET", USERS).timeout(Duration.ofSeconds(-1)));
        expect(IllegalStateException.class,
            () -> RequestSpec.builder("GET", USERS).body("{}").build());
        expect(IllegalStateException.class,
            () -> RequestSpec.builder("HEAD", USERS).body("").build());
        expect(IllegalStateException.class,
            () -> RequestSpec.builder("POST", ORDERS).body("{}").build());
        expect(NullPointerException.class,
            () -> RequestSpec.builder("POST", ORDERS).body(null));
        expect(NullPointerException.class,
            () -> RequestSpec.builder("GET", USERS).header("X-Test", null));
        expect(IllegalArgumentException.class,
            () -> RequestSpec.builder("GET", USERS).header("Bad Name", "value"));
        expect(IllegalArgumentException.class,
            () -> RequestSpec.builder("GET", USERS).header("X-Test", "a\r\nb"));

        var builder = RequestSpec.builder("GET", USERS).header("X-Mode", "first");
        var first = builder.build();
        var second = builder.header("x-mode", "second").build();
        check("first".equals(first.headers().get("x-mode")), "snapshot isolated");
        check("second".equals(second.headers().get("x-mode")), "builder reused");
        expect(UnsupportedOperationException.class,
            () -> first.headers().put("x-mode", "changed"));

        System.out.println("Passed " + checks + " builder checks.");
    }

    private static void check(boolean condition, String label) {
        if (!condition) throw new AssertionError(label);
        checks++;
    }

    private static void expect(Class<? extends Throwable> type, Runnable action) {
        try {
            action.run();
        } catch (Throwable error) {
            if (!type.isInstance(error)) {
                throw new AssertionError("Expected " + type.getSimpleName(), error);
            }
            checks++;
            return;
        }
        throw new AssertionError("Expected " + type.getSimpleName());
    }
}
```

With a JDK 25 toolchain, put all four supplied Java files in one directory and run:

Terminal · POSIX shell; use one line for javac on other shellsCopy

```
javac --release 25 -Xlint:all RequestSpec.java BuilderChecks.java \
    StagedRequest.java JdkBuilderExample.java
java BuilderChecks
java JdkBuilderExample
```

Expected outputCopy

```
Passed 25 builder checks.
POST https://example.com/orders
NEVER
```

`--release 25` checks the specified Java language level and documented target APIs. [[6]](#source-javac) The checks observe public behavior; they do not require a specific private helper layout.

**Verification for this edition**

The four complete source files compiled with `--release 17 -Xlint:all` on the available OpenJDK 17.0.20 runtime; all 25 checks passed, and the JDK example ran. Their APIs were checked against Java SE 25 documentation. ⚠️ A Java 25 runtime execution was not available for this edition. No preview features are used.

## 26Builder’s core structure

| Role | In this guide | Responsibility |
| --- | --- | --- |
| Client | The calling method | Choose required values and optional settings. |
| Builder | `RequestSpec.Builder` | Hold construction state, defaults, and checks. |
| Completion boundary | `build()` | Validate combinations and produce the product. |
| Product | `RequestSpec` | Expose a valid immutable configuration. |

This lesson uses the common fluent Java builder form. In the classic form, a separate director can coordinate a recipe of build steps, sometimes through a shared builder interface to create different representations. A director is unnecessary for the configuration problem we solved.

## 27The first-principles decision process

1. **Find a concrete construction mistake.** Are arguments confusing or easy to swap?
2. **Identify optional choices.** Are overloads multiplying? Who owns defaults?
3. **Write down validity rules.** Which inputs are independently invalid? Which combinations are invalid?
4. **Define the product boundary.** Must the result be immutable and ready to use immediately?
5. **Choose the simplest API that satisfies those needs.** A constructor, factory, or ordinary builder may be enough.
6. **Add staged types only for a real remaining risk.** Do not encode complexity just because you can.

**The idea to retain**

Separate collecting construction decisions from creating the final valid object. Fluent syntax makes the decisions readable; validation and ownership make the design reliable.

In the standard library

## Recognize the pattern in Java 25

Java’s real `HttpRequest.Builder` collects request settings and builds an immutable `HttpRequest`. Its setter methods return the builder; each `build()` returns a new request. [[4]](#source-jdk-request)

JdkBuilderExample.java · complete; no HTTP request is sentCopy

```
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.time.Duration;

public final class JdkBuilderExample {
    public static void main(String[] args) {
        var client = HttpClient.newBuilder()
            .followRedirects(HttpClient.Redirect.NEVER)
            .build();

        var request = HttpRequest.newBuilder(
                URI.create("https://example.com/orders"))
            .header("Content-Type", "application/json")
            .timeout(Duration.ofSeconds(5))
            .POST(HttpRequest.BodyPublishers.ofString("{\"productId\":\"P123\"}"))
            .build();

        // No send() call: this example only constructs objects.
        System.out.println(request.method() + " " + request.uri());
        System.out.println(client.followRedirects());
    }
}
```

| Our teaching API | Java 25 API |
| --- | --- |
| `RequestSpec.builder(method, uri)` | `HttpRequest.newBuilder(uri)` plus a method call such as `POST(...)` |
| `body(String)` | `BodyPublishers.ofString(...)` supplies a body publisher. |
| One header value per name; replacement | `header(...)` adds a value; `setHeader(...)` replaces values. |
| `followRedirects(boolean)` | Redirect policy is configured on `HttpClient.Builder`. [[7]](#source-client) |
| `retryCount(int)` | There is no matching `retryCount` method on the request builder. |

The example creates a client and a request but never calls `send`. Our 30-second timeout default and application-specific validation rules should not be read as JDK defaults.

Hands-on exercise

## Build DatabaseConnectionConfig

Apply the same reasoning to a database configuration value. Start from these fields, then design the construction boundary.

Starting point · fields only; make the final design immutableCopy

```
class DatabaseConnectionConfig {
    String host;
    int port;
    String username;
    String password;
    boolean ssl;
    int poolSize;
    Duration connectTimeout;
    Duration readTimeout;
}
```

| Field | Required / default | Rule |
| --- | --- | --- |
| host | Required | Non-null and nonblank. |
| port | Required | 1 through 65,535 inclusive. |
| username | Optional; absent by default | If provided, nonblank. |
| password | Optional; absent by default | Cannot be configured without a username. |
| ssl | `true` | A construction default; connection behavior is separate. |
| poolSize | `10` | Greater than zero. |
| connectTimeout | `Duration.ofSeconds(5)` | Non-null and positive. |
| readTimeout | `Duration.ofSeconds(30)` | Non-null and positive. |

Target API · use placeholder credentials for the exerciseCopy

```
var config = DatabaseConnectionConfig
    .builder("db.example.com", 5432)
    .username("app")
    .password("exercise-only-placeholder")
    .ssl(true)
    .poolSize(20)
    .connectTimeout(Duration.ofSeconds(3))
    .build();
```

### Acceptance criteria

1. The final config is immutable and exposes no mutators.
2. The entry point requires host and port; invalid supplied values are still checked.
3. Defaults have one authoritative location.
4. Invalid individual values and combinations fail during construction.
5. A finished config cannot be obtained half-configured through the public API.
6. Use one clear construction path rather than five overloads.

### Tests that reveal design mistakes

| Scenario | Expected behavior |
| --- | --- |
| Only host and port provided | All documented defaults appear. |
| Port 1 or 65,535 | Accepted. |
| Port 0 or 65,536; pool size 0 | Rejected. |
| Null, zero, or negative timeout | Rejected. |
| Password supplied without username | Rejected at the combination boundary. |
| Password followed by username before build() | Allowed if the final combination is valid. |
| Builder changed after first build() | The first config remains unchanged. |

**Implementation hints**

Use private final product fields, a private constructor, and `builder(host, port)`. Keep optional defaults in the builder. Validate independent arguments early and the username/password relationship at `build()`. Document how optional fields represent absence. Never include the password in diagnostic output.

The exercise remains intentionally unsolved. The goal is to decide who owns defaults, validity checks, and the boundary between mutable preparation and immutable use.

Connect the lessons

## Pattern map so far

| Pattern | Primary responsibility |
| --- | --- |
| Strategy | Make an algorithm interchangeable. |
| Factory | Encapsulate creation; often select an implementation. |
| Adapter | Translate between incompatible interfaces. |
| Decorator | Layer additional behavior. |
| Observer | Notify interested parties about changes or events. |
| State | Vary behavior with lifecycle state. |
| Command | Represent an action or request explicitly. |
| Builder | Control complex object construction. |

### Next: Facade

Suppose every caller has to coordinate inventory, payment, tax, fraud, shipping, and email services. The next question is: **why must every client understand that subsystem’s internal choreography?** Facade introduces a simpler entry point over a complex subsystem.

Official references

## Sources and scope

Technical references were checked against Java SE 25 documentation and RFC 9110 on 1 September 2026. The lesson’s design decisions are explained as choices for this example.

1. [RFC 9110 · GET content and HTTP field names](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.1)

   GET content semantics; see also §5.1 for case-insensitive field names.

   https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.1
2. [Java 25 · ModuleDescriptor.Builder](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/module/ModuleDescriptor.Builder.html)

   An official example of validating components during construction.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/module/ModuleDescriptor.Builder.html
3. [Java 25 · Map.copyOf and unmodifiable maps](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.html#copyOf(java.util.Map))

   Snapshot behavior, null restrictions, and the shallow-copy limitation.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.html#copyOf(java.util.Map)
4. [Java 25 · HttpRequest.Builder](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html)

   Fluent methods, build(), headers, timeouts, and builder synchronization.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html
5. [Java 25 · Record](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html)

   Record components, canonical constructors, and shallow immutability.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html
6. [JDK 25 · javac command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

   Meaning of --release and compiler options.

   https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html
7. [Java 25 · HttpClient.Builder](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.Builder.html#followRedirects(java.net.http.HttpClient.Redirect))

   Redirect policy belongs to the client builder.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.Builder.html#followRedirects(java.net.http.HttpClient.Redirect)
8. [Java 25 · Duration](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Duration.html)

   Duration factories, isZero(), isNegative(), and immutable duration values.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Duration.html
9. [Java 25 · URI](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/URI.html)

   URI creation and component access used in the example.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/URI.html

DP · Lesson 8 · Builder · Java 25-compatible edition