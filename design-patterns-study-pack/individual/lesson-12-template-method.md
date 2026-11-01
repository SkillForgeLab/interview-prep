[Skip to lesson](#main)

DP / DESIGN PATTERNS

Lesson 12

1. [I · Duplicated workflows](#pressure)
2. [II · The template](#mechanism)
3. [III · Extension points](#extension)
4. [IV · Strategy comparison](#tradeoffs)
5. [V · Control ownership](#ownership)
6. [VI · Failure semantics](#failure)
7. [VII · Decision process](#decision)
8. [Report exercise](#exercise)
9. [A · Runnable importer](#demo)
10. [B · Cleanup experiment](#cleanup-demo)
11. [Pattern map](#pattern-map)
12. [Official references](#sources)

Print / Save PDF

A4 or Letter · portrait
100% scale · headers off
All content prints.

DP · Design patterns from first principles

# Lesson 12Template Method

Fixed workflow.
Deliberately variable steps.

Java 25 compatibleSelf-contained guidePrint styles included

The process stays stable.
A few steps legitimately vary.

Start with duplicated importers. Find the invariant. Give the workflow one owner. Then decide what subclasses may specialize, what failure means, and when composition is the better fit.

**Learn in order**28 numbered sections preserve the lesson’s progression.

**Try it locally**Complete Java source, expected output, and failure checks.

**Practice the decision**Report-generation exercise with explicit acceptance criteria.

**Keep it offline**No external fonts, scripts, styles, or required assets.

Prerequisites: Java classes, inheritance, interfaces, collections, and exceptions. Focused snippets are labeled; the appendices contain complete runnable programs.

Print edition · Source links and Java code are included in full.

Part I · Notice the pressure

## One process, two copies

Begin with the concrete change. Name the pattern only after the problem is clear.

### 01Start with duplicated workflows

You import customers from CSV. Later, JSON arrives. Both importers validate the request, read a file, parse customers, save them, and announce completion.

Java · comparison excerpt; helper bodies omitted

```
// Bodies inside two separate importer classes.
public void importCsv(Path path) throws IOException {
    validate(path);
    String raw = read(path);
    List<Customer> customers = parseCsv(raw);
    save(customers);
    notifyCompletion();
}

public void importJson(Path path) throws IOException {
    validate(path);
    String raw = read(path);
    List<Customer> customers = parseJson(raw);
    save(customers);
    notifyCompletion();
}
```

| Stage | CSV importer | JSON importer |
| --- | --- | --- |
| 1 | Validate request | Validate request |
| 2 | Read file | Read file |
| 3 · varies | Parse CSV | Parse JSON |
| 4 | Save customers | Save customers |
| 5 | Notify completion | Notify completion |

### 02Diagnose the design problem

The pressure is **change amplification**: the stable sequence is copied alongside the format-specific behavior. If a shared audit step must run after saving, every importer needs the same edit.

Repeated lines alone do not prove that a shared base class is right. First ask whether these workflows must evolve together. Similar-looking processes with different rules should remain separate.

### 03Identify the invariant algorithm

For this example, the stable order is:

1. **Validate**Check request
2. **Read**Load input
3. **Parse**Format varies
4. **Save**Persist batch
5. **Notify**Report success

**The design move**

Give one owner the sequence. Let each importer supply the parsing step.

This leads to **Template Method**: a base-class method defines an algorithm and calls steps that subclasses can specialize. [[1]](#ref-1)

Part II · Encode the invariant

## The base owns when; subclasses own how

Use one template method and a deliberately small extension surface.

### 04Create the template

Java · focused excerpt

```
public abstract class CustomerImporter {
    public final void importData(Path path) throws IOException {
        validate(path);
        String raw = read(path);
        List<Customer> customers = parse(raw);
        save(customers);
        notifyCompletion();
    }

    protected abstract List<Customer> parse(String raw);

    // validate, read, save, and notifyCompletion are private,
    // shared helpers. Full runnable code is in Appendix A.
}
```

`importData` is the template method. `parse` is the intentional point of variation. The focused examples show design changes; [Appendix A](#demo) contains complete imports, types, behavior, and checks.

### 05Why final?

`final` prevents a subclass from overriding `importData`. An attempted override is a compile-time error. Private helpers are not override points either. [[2]](#ref-2)

**Protect the sequence, document the contract**

`final` protects this method body. It does not make hooks harmless, prevent reentrant calls, add rollback, or make the object thread-safe. A hook can still throw or perform side effects.

### 06Implement the variations

Java · subclass excerpt; decoders are supplied collaborators

```
final class CsvCustomerImporter extends CustomerImporter {
    @Override
    protected List<Customer> parse(String raw) {
        return csvDecoder.decode(raw);
    }
}

final class JsonCustomerImporter extends CustomerImporter {
    @Override
    protected List<Customer> parse(String raw) {
        return jsonDecoder.decode(raw);
    }
}
```

The decoders represent actual format parsers, not empty success stubs. Their constructors and parser implementations are outside this excerpt. Use the complete dependency-free CSV/TSV fixture in Appendix A to run the pattern without an external parser.

Java · usage sketch; wire constructor dependencies first

```
CustomerImporter importer = new CsvCustomerImporter(/* dependencies */);
importer.importData(Path.of("customers.csv"));
```

### 07Follow the execution

| Call | Owner | What happens |
| --- | --- | --- |
| `importData(path)` | Base class | Starts the fixed workflow |
| `validate`, `read` | Base class | Checks the request and loads data |
| `parse(raw)` | Concrete subclass | Dynamic dispatch selects the implementation |
| `save`, `notifyCompletion` | Base class | Continues if earlier steps completed normally |

The call to `parse` runs on the same importer object. There is no separate CSV or JSON branch in the template.

### 08Name the primitive operation

A required customizable step such as `parse` is commonly called a **primitive operation**. Here, “primitive” means a building block of the algorithm; it does not refer to Java primitive types.

An abstract method declares the operation without a body; a concrete subclass must provide an implementation, directly or through inheritance. [[2]](#ref-2)

Part III · Choose the extension points

## Required steps and optional hooks

Expose variation because the domain needs it, not because subclasses might want unlimited freedom.

### 09More than one step can vary

Suppose formats differ in both validation and parsing. Keep common request checks private, and add a separate format-specific operation.

Java · focused excerpt

```
public final void importData(Path path) throws IOException {
    Objects.requireNonNull(path, "path"); // common request rule
    validateFormat(path);                // required variation
    String raw = read(path);
    List<Customer> customers = parse(raw);
    save(customers);
}

protected abstract void validateFormat(Path path);
protected abstract List<Customer> parse(String raw);
```

A filename extension can select a format; it does not prove that the file contents obey that format. Content rules belong in an appropriate validation or parsing step.

### 10Add an optional hook

If post-import behavior is optional, give it a meaningful default: do nothing. Call the hook only after the save step returns normally.

Java · focused excerpt

```
protected void afterImport(List<Customer> customers) {
    // Default: no additional work.
}

// Last steps of the template:
save(customers);
afterImport(customers);
```

A subclass may override `afterImport` to notify a user. If notification is mandatory for every import, keep it as a shared step or a required operation; do not quietly turn a business requirement into an optional hook.

### 11Abstract operation versus hook

| Operation | Default behavior | Subclass responsibility |
| --- | --- | --- |
| `protected abstract parse(...)` | None | Supply required behavior |
| `protected afterImport(...)` | No-op or documented default | Override only when needed |
| `private save(...)` | Shared implementation | No override |
| `public final importData(...)` | Fixed orchestration | Use the inherited workflow |

### 12Try a second domain: payment processing

Assume a fictional payment system whose providers all obey one lifecycle: validate, fraud check, authorize, capture, record. Only authorization and capture differ.

Java · hypothetical domain excerpt

```
public final PaymentResult process(Payment payment) {
    validate(payment);
    checkFraud(payment);
    String authorization = authorize(payment);
    String transactionId = capture(payment, authorization);
    recordTransaction(transactionId);
    return new PaymentResult(transactionId);
}

protected abstract String authorize(Payment payment);
protected abstract String capture(Payment payment, String authorization);
```

This is a design illustration, not an implementation of a named payment provider. A provider requiring redirection, asynchronous confirmation, or a different step order would challenge the assumed common lifecycle.

### 13What the pattern buys us

The shared sequence lives once. A legitimate lifecycle change has one implementation point, while each subclass remains focused on its variation.

**The cost travels with the benefit**

Every subclass now depends on the base lifecycle. A change in shared ordering needs validation across the supported variants. Code reuse is useful only while those variants share the same contract.

Part IV · Compare the mechanisms

## Template Method and Strategy

The key distinction is how variation is supplied. The size of the varying algorithm is not an absolute rule.

### 14Template Method versus Strategy

| Question | Template Method | Strategy |
| --- | --- | --- |
| How is variation supplied? | Override a step in a subclass | Delegate to a collaborator |
| Who runs the workflow? | Base-class method | The object that uses the strategy |
| Can a single parse step vary? | Yes: overridden `parse` | Yes: injected `CustomerParser` |
| How is a variation chosen? | Construct an appropriate subtype | Provide a strategy object |
| Can it change at runtime? | Usually replace the importer instance | Possible if the owner deliberately supports replacement |

“Replace an algorithm” versus “specialize steps” is a useful introduction. It is not a strict scope boundary: a parser strategy can implement only one step inside a larger stable workflow. The inheritance/delegation distinction is the more reliable guide. This applies Microsoft’s comparison at the parser level. [[3]](#ref-3)

### 15Composition versus inheritance

Java · structural comparison

```
// Template Method: inherit the workflow.
final class CsvImporter extends CustomerImporter { /* parse override */ }

// Strategy: own a collaborator.
final class ImportService {
    private final CustomerParser parser;
    // The service invokes parser.parse(raw) at the chosen step.
}
```

With inheritance, the subclass and base share a lifecycle contract. With composition, the importer depends on a parser contract. Neither mechanism decides the right transaction, retry, or notification policy for you.

### 16The fragile base-class problem

Suppose the base inserts normalization before parsing. A subclass that expected untouched input now receives modified text. The subclass still compiles, yet its assumptions may be wrong.

Document what each extension point receives, what it must return, its allowed failures, whether it can be called repeatedly, and any resource ownership. Avoid calling overridable steps from a constructor, before the object is fully initialized.

### 17Do not expose too many hooks

Adding `beforeValidate`, `afterValidate`, `beforeRead`, `afterRead`, and hooks around every other step creates many places for hidden side effects and ordering dependencies.

The calls may still occur in a fixed order, but understanding the behavior now requires reading many overrides. Start with a few extension points that have concrete reasons to vary.

Part V · Understand control ownership

## Who calls whom?

A pattern is a relationship between responsibilities, not merely a familiar-looking method name.

### 18The Hollywood Principle

The client calls `importData`. The base then calls subclass code at the designated point. The subclass does not run the overall workflow.

**Control is inverted**

Instead of your specialization deciding when each shared step runs, the reusable workflow calls your specialization. This is one form of inversion of control.

### 19Recognize the idea in libraries

Java 25’s `InputStream.read(byte[], int, int)` default implementation repeatedly calls the single-byte `read()` operation that subclasses supply. That is a concrete example of a reusable operation built on a primitive operation. The bulk method itself is overridable, so `final` is our enforcement choice, not a mandatory element of every example of the pattern. [[4]](#ref-4)

Framework callbacks and annotation-driven lifecycles may also invert control. Without the base/subclass relationship, call them related lifecycle or callback designs rather than automatically classifying them as classic Template Method.

### 20Express the same variation without inheritance

Java · Strategy alternative; reuse Customer and standard imports

```
@FunctionalInterface
interface CustomerParser {
    List<Customer> parse(String raw);
}

final class ImportService {
    private final CustomerParser parser;
    private final Consumer<List<Customer>> store;

    ImportService(CustomerParser parser,
                  Consumer<List<Customer>> store) {
        this.parser = Objects.requireNonNull(parser);
        this.store = Objects.requireNonNull(store);
    }

    public int importData(Path path) throws IOException {
        Objects.requireNonNull(path, "path");
        String raw = Files.readString(path);
        List<Customer> customers = List.copyOf(parser.parse(raw));
        store.accept(customers);
        return customers.size();
    }
}
```

The importer still owns a stable sequence. Parsing is now delegated, so choosing a parser does not require subclassing the importer. Notification is omitted in this comparison to keep the delegation visible.

### 21When to prefer Strategy

Consider composition when parsers, validators, and formatters vary independently; when you want to mix them in different combinations; or when a class already has another superclass. Injecting one cohesive parser is often simpler than creating an importer subtype for each format.

Runtime replacement is optional. A `final` parser field deliberately fixes the collaborator for that service instance.

### 22When Template Method is a strong fit

Consider Template Method when a real family of implementations specializes several related steps under one stable lifecycle: initialize a provider, authenticate, transform provider-specific data, then release provider resources.

The subtype should represent a coherent specialization. If each override is unrelated to the others, independent collaborators may communicate the design more clearly.

### 23Combine it with Factory Method

Java · report-domain excerpt

```
public final Report generate() {
    ReportWriter writer = createWriter();
    ReportData data = transform(loadData());
    writer.write(data);
    return writer.result();
}

protected abstract ReportWriter createWriter();
```

`generate` owns the workflow: Template Method. `createWriter` lets subclasses choose which writer to create: Factory Method. If a writer owns resources, define its lifetime explicitly, for example with `AutoCloseable`.

Part VI · Make the semantics explicit

## Success order is only half the workflow

Failures reveal who truly owns the lifecycle.

### 24Test observable behavior and essential sequencing

Test customers saved, errors reported, and steps that must not run after a failure. Do not make private helpers overridable merely to test them. Use real boundaries such as a storage collaborator or a purpose-built fixture trace.

| Case | Required observation |
| --- | --- |
| Successful import | Expected customers are saved once per invocation |
| Invalid request or read failure | Parsing and saving do not run |
| Parsing fails | Storage and the completion hook are skipped |
| Storage fails | The completion hook is skipped |
| Completion hook fails | Previously saved data remains saved in this fixture |
| Render fails with an acquired resource | Resource close is attempted |
| Body and close both fail | Body exception remains primary; close failure is suppressed |

Appendix A checks the importer’s success path, format variation, empty-input policy, parse failure, storage failure, and completion-hook failure. Appendix B demonstrates the resource failure case.

### 25Decide how cleanup works

A normal statement after `parse` will be skipped if parsing throws. A `finally` block runs when control exits the associated `try` through Java’s normal completion or exception mechanisms.

Java · lifecycle sketch

```
try {
    validate(path);
    String raw = read(path);
    save(parse(raw));
} finally {
    cleanup();
}
```

If `cleanup()` itself throws, that failure can replace the original one. For resources implementing `AutoCloseable`, prefer try-with-resources: it closes successfully acquired resources and preserves a body failure while recording a close failure as suppressed. [[5]](#ref-5) [[6]](#ref-6)

Java · resource ownership sketch

```
try (ImportSession session = openSession(path)) {
    List<Customer> customers = parse(session.read());
    save(customers);
} // session.close() is attempted on success or failure.
```

Opening can fail before a resource exists. Closing can also fail. “Cleanup runs” therefore means the cleanup attempt is placed correctly, not that cleanup must succeed under every condition.

**No invented resource to close**

`Files.readString` closes the file internally, including on relevant failures. The runnable importer does not need an empty cleanup hook for reading. Use an explicit resource scope only when your workflow actually owns a resource. [[7]](#ref-7)

### 26Separate saved work from notification

Suppose saving succeeds and notification throws. The method can report failure even though its main side effect already happened. That is the behavior deliberately tested in Appendix A.

| Policy | Meaning | Design consequence |
| --- | --- | --- |
| Propagate notification failure | Caller receives an error after save | Do not assume the save was undone; retries need a policy |
| Best-effort notification | Import is successful; delivery problem is recorded | Catch the expected notification exception at that boundary |
| Durable delivery requirement | Save and delivery intent must be coordinated | Design transaction and delivery semantics explicitly |

Choose and document a policy. Template Method does not provide atomicity, rollback, idempotency, or reliable delivery by itself. Retrying the entire importer may repeat persistence unless storage handles duplicates deliberately.

Part VII · Make the design decision

## Use the relationship that matches the domain

Keep the first-principles question ahead of the pattern name.

### 27Recognize a poor fit

* Subclasses must skip or reorder mandatory stages.
* Most steps need overriding, and the common behavior is small.
* The base accumulates many protected hooks and subtype checks.
* Independent variation produces a growing set of combination subclasses.

These signs challenge the “one stable process” assumption. Consider separate workflows, a composed set of collaborators, or an explicit pipeline when stages themselves need to vary.

### 28Ask the questions in order

1. **Same process?** Are these workflows conceptually one lifecycle, rather than coincidentally similar code?
2. **Stable sequence?** Must the order stay the same for every supported variant?
3. **Few varying steps?** Can you name the specific extension points?
4. **One owner?** Should the base decide when those steps execute?
5. **Honest inheritance?** Does a subtype represent a coherent specialization?

**Choose based on the answers**

Template Method fits a stable inherited lifecycle. Strategy fits variation supplied by collaborators, whether that variation is one step or a larger algorithm. If the sequence itself varies substantially, revisit the shared workflow assumption.

Practice · Report generation

## Build the workflow before the variants

Use the failure cases as part of the design, not as an afterthought.

Build a report generator with one owner for this lifecycle:

| Order | Stage | Owner |
| --- | --- | --- |
| 1 | Validate request | Shared |
| 2 | Load data | Shared |
| 3 | Transform data | PDF or CSV subclass |
| 4 | Render report | PDF or CSV subclass |
| 5 | Store report | Shared |
| 6 | Notify | Shared policy or intentional hook |

Java · exercise scaffold, intentionally incomplete

```
abstract class ReportGenerator {
    public final Report generate(ReportRequest request) {
        // Implement the shared lifecycle here.
        // Define resource and notification failure semantics.
        throw new UnsupportedOperationException("Exercise: implement me");
    }

    protected abstract ReportData transform(RawData data);
    protected abstract Report render(ReportData data);
}
```

Define `ReportRequest`, `RawData`, `ReportData`, and `Report` as domain types. For a unit-test exercise, a report can carry a format tag and text or bytes. A simulated PDF renderer is a test double; producing actual PDF bytes is a separate implementation task.

### Acceptance criteria

1. The workflow order has exactly one implementation owner.
2. Subclasses cannot override `generate`.
3. Shared validation, loading, and storage behavior is not duplicated.
4. Only the genuinely variable steps are protected or abstract.
5. If the workflow owns a resource, its close is attempted when rendering fails.
6. A rendering failure prevents storage and notification.
7. The primary rendering failure is preserved if closing also fails.
8. The notification policy is explicit, including what happens after a successful store.
9. You can explain why subclass overrides make this Template Method.

### Questions to answer before coding

Who acquires the resource? Who closes it? What counts as success? Can this operation be retried without storing a duplicate? Must transformation really differ by output format, or could only rendering vary?

**A useful challenge to the exercise**

The exercise assumes both transform and render vary. Real systems may share transformation across PDF and CSV. Keep that assumption only if the domain supports it.

Appendix A · Runnable Java

## Run the invariant, then break it

The complete program and checks live inside this HTML file.

Save the embedded source as `TemplateMethodDemo.java`. It uses standard Java APIs, one public class, and nested supporting types. No build tool, external library, network call, or preview flag is required.

**What this fixture models**

CSV and TSV are used for a complete dependency-free run. Both accept two unquoted fields per nonblank line: name and email, with no header. Quotes are rejected; field values cannot contain the delimiter or a newline. This is not a general CSV or JSON parser. Persistence is an in-memory list, and empty input is an accepted zero-row batch.

Terminal · run with JDK 25

```
javac --release 25 -Xlint:all -Werror TemplateMethodDemo.java
java TemplateMethodDemo
```

`--release 25` checks language and platform APIs for Java 25. [[8]](#ref-8) The source uses stable features available in Java 25; it does not need Java 25-specific syntax.

**Verification:** source compiled with warnings treated as errors and all embedded checks passed on OpenJDK 17.0.20. Java 25 compatibility was reviewed against official language and API documentation; a Java 25 execution was not performed here.

Download Java sourceCopy complete source

TemplateMethodDemo.java · complete runnable program

```
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.regex.Pattern;

public final class TemplateMethodDemo {
    record Customer(String name, String email) {
        Customer {
            Objects.requireNonNull(name, "name");
            Objects.requireNonNull(email, "email");
            if (name.isBlank() || email.isBlank()) {
                throw new IllegalArgumentException("Blank customer field");
            }
        }
    }

    abstract static class CustomerImporter {
        private final Consumer<List<Customer>> store;
        private final Consumer<String> trace;

        protected CustomerImporter(Consumer<List<Customer>> store,
                                   Consumer<String> trace) {
            this.store = Objects.requireNonNull(store);
            this.trace = Objects.requireNonNull(trace);
        }

        public final int importData(Path path) throws IOException {
            trace.accept("validate");
            Objects.requireNonNull(path, "path");
            trace.accept("read");
            String raw = Files.readString(path);
            trace.accept("parse");
            List<Customer> customers = List.copyOf(parse(raw));
            trace.accept("save");
            store.accept(customers);
            trace.accept("afterImport");
            afterImport(customers);
            return customers.size();
        }

        protected abstract List<Customer> parse(String raw);

        protected void afterImport(List<Customer> customers) {
            // Optional hook. Default behavior is intentionally empty.
        }
    }

    static final class CsvCustomerImporter extends CustomerImporter {
        CsvCustomerImporter(Consumer<List<Customer>> store,
                            Consumer<String> trace) {
            super(store, trace);
        }

        @Override
        protected List<Customer> parse(String raw) {
            return parseRows(raw, ",");
        }
    }

    static final class TsvCustomerImporter extends CustomerImporter {
        TsvCustomerImporter(Consumer<List<Customer>> store,
                            Consumer<String> trace) {
            super(store, trace);
        }

        @Override
        protected List<Customer> parse(String raw) {
            return parseRows(raw, "\t");
        }
    }

    // A deliberately limited fixture format: no header or quoting.
    private static List<Customer> parseRows(String raw, String separator) {
        var customers = new ArrayList<Customer>();
        for (String line : raw.lines().toList()) {
            if (line.isBlank()) {
                continue;
            }
            if (line.indexOf('"') >= 0) {
                throw new IllegalArgumentException("Quoting is unsupported");
            }
            String[] fields = line.split(Pattern.quote(separator), -1);
            if (fields.length != 2) {
                throw new IllegalArgumentException("Expected name and email");
            }
            customers.add(new Customer(fields[0].strip(), fields[1].strip()));
        }
        return customers;
    }

    public static void main(String[] args) throws Exception {
        Path input = Files.createTempFile("template-method-", ".txt");
        try {
            runChecks(input);
        } finally {
            Files.deleteIfExists(input);
        }
    }

    private static void runChecks(Path input) throws Exception {
        var saved = new ArrayList<Customer>();
        var calls = new ArrayList<String>();
        CustomerImporter csv = new CsvCustomerImporter(saved::addAll,
                                                       calls::add);
        Files.writeString(input,
                "Alice,alice@example.com\nBob,bob@example.com\n");
        check(csv.importData(input) == 2, "CSV count");
        check(saved.equals(List.of(new Customer("Alice", "alice@example.com"),
                new Customer("Bob", "bob@example.com"))), "saved customers");
        check(calls.equals(List.of("validate", "read", "parse", "save",
                "afterImport")), "workflow order");
        System.out.println("Imported " + saved.size() + " customers");
        System.out.println("Steps: " + String.join(" -> ", calls));

        saved.clear();
        calls.clear();
        Files.writeString(input, "Carol\tcarol@example.com\n");
        CustomerImporter tsv = new TsvCustomerImporter(saved::addAll,
                                                       calls::add);
        check(tsv.importData(input) == 1, "TSV count");
        check(saved.get(0).name().equals("Carol"), "TSV variation");

        saved.clear();
        calls.clear();
        Files.writeString(input, "invalid-row\n");
        expect(IllegalArgumentException.class, () -> csv.importData(input));
        check(saved.isEmpty(), "parse failure must not save");
        check(calls.equals(List.of("validate", "read", "parse")),
                "parse failure must skip later steps");

        calls.clear();
        Files.writeString(input, "\n");
        check(csv.importData(input) == 0, "empty input policy");
        check(saved.isEmpty(), "empty batch");

        calls.clear();
        Files.writeString(input, "Dana,dana@example.com\n");
        CustomerImporter failingStore = new CsvCustomerImporter(batch -> {
            throw new IllegalStateException("store failed");
        }, calls::add);
        expect(IllegalStateException.class,
                () -> failingStore.importData(input));
        check(!calls.contains("afterImport"), "save failure must skip hook");

        calls.clear();
        CustomerImporter failingHook = new CustomerImporter(saved::addAll,
                                                            calls::add) {
            @Override
            protected List<Customer> parse(String raw) {
                return parseRows(raw, ",");
            }

            @Override
            protected void afterImport(List<Customer> customers) {
                throw new IllegalStateException("notification failed");
            }
        };
        expect(IllegalStateException.class,
                () -> failingHook.importData(input));
        check(saved.size() == 1, "hook failure does not undo save");
        System.out.println("All checks passed");
    }

    private static void check(boolean condition, String description) {
        if (!condition) {
            throw new AssertionError(description);
        }
    }

    @FunctionalInterface
    interface CheckedAction {
        void run() throws Exception;
    }

    private static void expect(Class<? extends Exception> type,
                               CheckedAction action) throws Exception {
        try {
            action.run();
        } catch (Exception exception) {
            if (type.isInstance(exception)) {
                return;
            }
            throw exception;
        }
        throw new AssertionError("Expected " + type.getSimpleName());
    }
}
```

### Expected output

Console

```
Imported 2 customers
Steps: validate -> read -> parse -> save -> afterImport
All checks passed
```

The trace records the shared sequence at the call sites. The saved list confirms actual side effects. These checks use explicit `AssertionError`, so `-ea` is not needed.

`List.copyOf` gives downstream steps an unmodifiable list and rejects null elements. It does not deeply freeze arbitrary element objects. Here, each `Customer` holds immutable strings. [[9]](#ref-9)

The fixture has no transaction or concurrency support. Its trace callback is test instrumentation; it is not a reason to add hooks around every operation in production code.

Appendix B · Failure semantics

## Preserve the original failure

A small executable experiment makes the resource rule concrete.

This experiment intentionally throws during rendering and closing. It isolates Java’s resource semantics before you use them inside a larger template.

Download CleanupDemo.java

CleanupDemo.java · complete runnable program

```
public final class CleanupDemo {
    static final class Session implements AutoCloseable {
        @Override
        public void close() {
            System.out.println("close attempted");
            throw new IllegalStateException("close failed");
        }

        void render() {
            throw new IllegalArgumentException("render failed");
        }
    }

    public static void main(String[] args) {
        try (Session session = new Session()) {
            session.render();
        } catch (RuntimeException failure) {
            System.out.println("primary: " + failure.getMessage());
            for (Throwable suppressed : failure.getSuppressed()) {
                System.out.println("suppressed: " + suppressed.getMessage());
            }
            if (!"render failed".equals(failure.getMessage())
                    || failure.getSuppressed().length != 1
                    || !"close failed".equals(
                            failure.getSuppressed()[0].getMessage())) {
                throw new AssertionError("Incorrect failure semantics");
            }
        }
    }
}
```

Terminal · JDK 25

```
javac --release 25 -Xlint:all -Werror CleanupDemo.java
java CleanupDemo
```

Expected console output

```
close attempted
primary: render failed
suppressed: close failed
```

For a real generator, put the resource acquisition and scope in the lifecycle owner. Do not use a plain `finally` that can mask the original rendering exception. The language rules, not Template Method, provide suppressed-exception behavior. [[5]](#ref-5)

Review · Connect the lessons

## Place Template Method in the map

Use these as orientation cues; the concrete responsibilities determine the pattern.

| Pattern | Design intent |
| --- | --- |
| Strategy | Supply an interchangeable algorithm or step through a collaborator |
| Template Method | Specialize steps of an inherited workflow |
| State | Vary behavior with an object’s current state |
| Command | Represent a requested action as an object |
| Observer | Notify interested parties about changes or events |
| Factory / Factory Method | Encapsulate creation; Factory Method lets subclasses choose a product |
| Builder | Assemble a complex object step by step |
| Adapter | Translate one interface into another |
| Decorator | Add behavior around an object through the same abstraction |
| Facade | Offer a simpler entry point to a subsystem |
| Proxy | Stand in for an object to control access or interaction |
| Composite | Represent a part-whole hierarchy through a shared abstraction |

### Next: Chain of Responsibility

Consider a request passing through authentication, validation, rate limiting, fraud checks, and a business handler. Individual handlers may reject it, handle it, or pass it onward. The next lesson asks how to separate those handling decisions and compose the path through them.

References · Official sources

## Verify the details

Keep the source of a language rule separate from the design judgment built on it.

The lesson progression and exercises are adapted from the supplied Lesson 12. Java semantics and the pattern definition were checked against these official sources. Domain examples, decision questions, and failure policies are teaching designs, not claims about a specific product.

1. [Microsoft Learn · Template Method](https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-template-method)

   Pattern definition: a base operation defines an algorithm and defers selected steps to subclasses.

   https://learn.microsoft.com/en-us/shows/visual-studio-toolbox/design-patterns-template-method
2. [Java Language Specification 25 · Classes, §8.4.3 and §8.4.8](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.3)

   Abstract methods, final methods, and overriding.

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.3
3. [Microsoft Learn · Design patterns already in .NET](https://learn.microsoft.com/en-us/archive/msdn-magazine/2005/july/discovering-the-design-patterns-you-re-already-using-in-net)

   Strategy and Template Method: delegation and inheritance. The parser-level comparison in this guide is an application of that distinction.

   https://learn.microsoft.com/en-us/archive/msdn-magazine/2005/july/discovering-the-design-patterns-you-re-already-using-in-net
4. [Java 25 API · InputStream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/InputStream.html#read(byte[],int,int))

   The default bulk-read implementation calls the single-byte read operation.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/InputStream.html#read(byte[],int,int)
5. [Java Language Specification 25 · §14.20](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20)

   Finally behavior, try-with-resources, and suppressed exceptions.

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20
6. [Java 25 API · AutoCloseable](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/AutoCloseable.html)

   The resource-close contract.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/AutoCloseable.html
7. [Java 25 API · Files.readString](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Files.html#readString(java.nio.file.Path))

   UTF-8 file reading and internal file closure. It reads the contents into memory; use a different I/O design for large inputs.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Files.html#readString(java.nio.file.Path)
8. [Java 25 tools · javac](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

   The --release option selects language rules and the target platform API.

   https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html
9. [Java 25 API · List.copyOf](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection))

   Unmodifiable lists, null handling, and the distinction between the list and its elements.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection)

Reference review: 1 September 2026. This HTML contains all lesson content, styles, and Java source. An internet connection is needed only to open external references.

DP · Lesson 12 · Template Method