[Skip to guide](#main)

DP / DESIGN PATTERNS

**Lesson 13**[01–03 · Derive the need](#s1)[04–09 · Choose a model](#s4)[10–13 · Middleware](#s10)[14–18 · Compare patterns](#s14)[19–26 · Semantics & tests](#s19)[Exercise](#exercise)[Runnable Java reference](#reference)[Pattern map](#pattern-map)[Official sources](#sources)

Self-contained HTML
Light theme · Print stylesheet
No external assets

Design patterns from first principles · Lesson 13

# Chain of Responsibility

One request. Independent stages.
Explicit control over what happens next.

JAVA 25 COMPATIBLE26 LESSON STEPSRUNNABLE REFERENCE

Print / Save as PDFGo to full Java example

For PDF: select A4, portrait, 100% scale. Disable browser headers and footers if they duplicate the guide’s footer.

**The core idea:** break request processing into independent stages and give continuation a clear contract.

We begin with ordinary service code, find the pressure created by repeated processing rules, try a simple list, and introduce middleware only when stages need to wrap downstream work.

**Read in order:** problem → stage abstraction → stop rules → middleware → ordering → failure → tests.

**Prerequisites:** Java interfaces, exceptions, collections, lambdas, and constructors. Records are used for small data carriers.

The lesson is readable and printable without JavaScript. Print and copy controls are conveniences; all explanations and complete source are included below.

Part I

## Derive the need

Start with ordinary code. Introduce a pattern only when independent stages and different combinations create pressure.

## 01Start without a pattern

A money-transfer service can begin as one explicit method. Authentication, validation, a fraud decision, and execution are easy to follow when there is one use case.

Java · starting design; execution is simulatedCopy

```
record TransferRequest(String userId, long amountInCents) {}
record TransferResult(String transactionId) {}

final class TransferService {
    private final java.util.function.Predicate<TransferRequest> suspicious;

    TransferService(
            java.util.function.Predicate<TransferRequest> suspicious) {
        this.suspicious = java.util.Objects.requireNonNull(suspicious);
    }

    TransferResult transfer(TransferRequest request) {
        if (request.userId() == null || request.userId().isBlank()) {
            throw new SecurityException("Authentication required");
        }
        if (request.amountInCents() <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        if (request.amountInCents() > 1_000_000) {
            throw new IllegalArgumentException("Transfer limit exceeded");
        }
        if (suspicious.test(request)) {
            throw new IllegalArgumentException("Transfer rejected");
        }
        return new TransferResult("DEMO-TX");
    }
}
```

**This is a reasonable starting point.** A few `if` statements do not justify a handler framework.

**Two deliberate simplifications**

Here `userId` is assumed to come from a trusted authentication boundary; checking for a value does not authenticate a caller. The amount cap is a transfer rule. Rate limiting controls request admission, such as requests per time window, and needs a separate policy. The complete example verifies a demo credential before assigning a user ID. [[9]](#source-9)

## 02Requirements grow

Additional concerns arrive: authorization, rate limiting, sanctions checks, audit, and idempotency. Extracting private methods keeps one service readable. The pressure changes when multiple operations need different combinations.

| Operation | Illustrative stages before execution |
| --- | --- |
| Transfer money | Authentication, validation, rate limit, fraud, sanctions, idempotency |
| Update profile | Authentication, validation, rate limit |
| Generate report | Authentication, authorization, rate limit |

Now changing a shared rule may require editing several orchestration methods. The recurring unit is a **processing stage**, not the entire use case.

## 03Diagnose the actual problem

Each independent stage receives a request, inspects it, and chooses an outcome. The caller should depend on one entry point instead of knowing every stage.

| Stage decision | Effect |
| --- | --- |
| Continue | Allow the next stage to run. |
| Stop with a result | Return a rejection or a completed response. |
| Fail | Throw; downstream processing does not continue unless something deliberately recovers. |

That leads to **Chain of Responsibility**: potential handlers receive a request in sequence, with continuation controlled along the chain. The classic form passes until a handler accepts responsibility. [[1]](#source-1)

**Keep two variants distinct**

A *first-handler-wins chain* looks for a receiver, such as escalating a support request. A *processing pipeline* runs multiple stages, any of which may stop the request. This lesson develops the pipeline and middleware variant. They share a continuation idea, but are not identical semantics.

Part II

## Choose the smallest execution model

Start with a list. Add explicit stop results or next-callbacks only when the behavior needs them.

## 04Represent one processing stage

Give checks a common contract. Normal return means this check passed. These excerpts use the `TransferRequest` record from step 1.

Java · teaching excerptCopy

```
@FunctionalInterface
interface Handler {
    void handle(TransferRequest request);
}

final class AuthenticationHandler implements Handler {
    @Override
    public void handle(TransferRequest request) {
        if (request.userId() == null || request.userId().isBlank()) {
            throw new SecurityException("Authentication required");
        }
    }
}

final class ValidationHandler implements Handler {
    @Override
    public void handle(TransferRequest request) {
        if (request.amountInCents() <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
    }
}
```

A fraud handler can use the same interface and receive a fraud service in its constructor. The rule belongs to the stage; sequencing belongs elsewhere.

## 05A list is often enough

The pipeline owns iteration. Handlers do not need a mutable `next` field.

Java · teaching excerptCopy

```
final class TransferPipeline {
    private final java.util.List<Handler> handlers;

    TransferPipeline(java.util.List<Handler> handlers) {
        this.handlers = java.util.List.copyOf(handlers);
    }

    void execute(TransferRequest request) {
        java.util.Objects.requireNonNull(request);
        for (Handler handler : handlers) {
            handler.handle(request);
        }
    }
}
```

Java · caller excerptCopy

```
var pipeline = new TransferPipeline(java.util.List.of(
    new AuthenticationHandler(),
    new ValidationHandler()
));
pipeline.execute(request);
// Call the business operation only after execute returns normally.
```

`List.copyOf` preserves iteration order, rejects null elements, and provides an unmodifiable list. It does not freeze the handler objects inside it. [[4]](#source-4)

## 06Stopping with an exception

If validation throws, the loop exits and later handlers are not invoked. Authentication may already have run; fraud and business execution will not run.

Use this convention when exception handling matches your application boundary. Expected user rejection can also be represented as data. An exception alone does not undo earlier side effects.

| Outcome of handler A | Will handler B run? |
| --- | --- |
| Returns normally | Yes, under this loop contract. |
| Throws an uncaught exception | No. |
| Exception is caught and ignored inside A | Yes. The outer loop sees normal return. |

## 07Make continuation an explicit result

If stopping is an expected decision, return it. Use a different interface name so the two designs are not accidentally mixed.

Java · declarations inside an enclosing classCopy

```
enum Decision { CONTINUE, STOP }

@FunctionalInterface
interface DecidingHandler {
    Decision handle(TransferRequest request);
}

static Decision execute(java.util.List<DecidingHandler> handlers,
                        TransferRequest request) {
    for (DecidingHandler handler : handlers) {
        Decision decision = java.util.Objects.requireNonNull(
            handler.handle(request));
        if (decision == Decision.STOP) return Decision.STOP;
    }
    return Decision.CONTINUE;
}
```

The caller must honor `STOP`. A bare enum says nothing about *why* processing stopped or whether the request succeeded. If that matters, return a result carrying the reason or response. Middleware below makes that response the return value.

## 08Understand the classic linked form

In a linked chain, each handler stores its successor. This version illustrates *first-handler-wins* using a routing topic.

Java · teaching excerptCopy

```
abstract class LinkedHandler {
    private final LinkedHandler next;

    protected LinkedHandler(LinkedHandler next) {
        this.next = next;
    }

    public final String handle(String topic) {
        if (canHandle(topic)) return respond(topic);
        if (next != null) return next.handle(topic);
        return "Unhandled: " + topic;
    }

    protected abstract boolean canHandle(String topic);
    protected abstract String respond(String topic);
}
```

A billing receiver can answer billing topics and forward the rest. Define what happens when nobody handles the request; silence is a poor default. Constructor wiring keeps linkage fixed after construction. Mutable `setNext` designs need protection against accidental cycles and rewiring.

## 09Prefer a list when it expresses the rules

| Execution model | Continuation owner | Useful when |
| --- | --- | --- |
| List of checks | The loop | Every successful check should proceed; failure stops. |
| List of decision handlers | Stage result, interpreted by loop | Expected stops need explicit decisions. |
| Linked receivers | Current receiver | A request seeks a suitable handler. |
| Middleware with `Next` | Current middleware | Stages wrap downstream work or return a response early. |

For the simple pipeline, a list makes configuration and testing straightforward. This is a design recommendation for this problem, not a universal claim that linked handlers are wrong.

Part III

## Add middleware when stages must wrap work

The key change is ownership of continuation: a stage receives a callable representation of everything downstream.

## 10A stage may need before and after behavior

Logging and timing need to surround downstream work. A one-way loop of `void` checks cannot directly express that nesting.

Java · teaching excerptCopy

```
@FunctionalInterface
interface Next {
    Response invoke(Request request);
}

@FunctionalInterface
interface Middleware {
    Response handle(Request request, Next next);
}
```

`Next` represents the remainder of the chain. A middleware can call it, pass an enriched request to it, inspect its response, or return its own response without calling it.

**Contract for this guide**

Processing is synchronous. Call `next` zero or one time during `handle`, return a non-null response, and do not retain `next`. Zero calls means short-circuit. A terminal handler supplies the response when every stage continues.

## 11Authenticate, then forward trusted identity

Authentication establishes identity. A caller-supplied user ID is not evidence. The authenticator returns a verified identity, or an empty result.

Java · exact excerpt from the complete exampleCopy

```
record Authentication(Authenticator auth) implements Middleware {
    @Override
    public Response handle(Request request, Next next) {
        var user = auth.authenticate(request.token());
        if (user.isEmpty()) {
            return new Response(Outcome.UNAUTHENTICATED,
                "Authentication required");
        }
        return next.invoke(request.withUser(user.orElseThrow()));
    }
}
```

The JDK 25 HTTP server has an analogous mechanism: `Filter.doFilter` can call `Filter.Chain.doFilter` or stop and send an appropriate response. [[2]](#source-2)[[3]](#source-3)

This is `com.sun.net.httpserver.Filter.Chain` in the JDK’s `jdk.httpserver` module. Jakarta Servlet’s `jakarta.servlet.FilterChain` is a separate API. [[10]](#source-10)

## 12Logging wraps the downstream call

Java · teaching excerptCopy

```
Middleware logging = (request, next) -> {
    System.out.println("start");
    try {
        return next.invoke(request);
    } finally {
        System.out.println("finish");
    }
};
```

For two wrappers A and B, entry runs A then B; successful return unwinds B then A. Only code that actually exists runs: authentication does not have an “after” action merely because it calls `next`.

| Event | Accepted request | Authentication rejection |
| --- | --- | --- |
| 1 | Logging starts | Logging starts |
| 2 | Authentication calls next | Authentication returns rejection |
| 3 | Remaining stages and business run | Downstream stages are skipped |
| 4 | Response returns through wrappers | Rejection returns to logging |
| 5 | Logging finally runs | Logging finally runs |

A `finally` block runs during normal return and Java exception unwinding. Code placed only after `next.invoke` is skipped when that call throws. A throwing `finally` can replace the original failure. [[6]](#source-6)

## 13Ordering is behavior

Consider two different admission policies. Both can be intentional; choose based on what the limit protects and which identity is available.

| Placement | Admission key | Consequence |
| --- | --- | --- |
| Before authentication | Connection, source, or global capacity policy | Can protect authentication work; must not rely on an unverified user ID. |
| After authentication | Verified user or tenant | Enforces per-identity quotas; authentication rejects do not reach this limiter. |

The reference example uses a **per-user limiter after authentication**. Because it precedes validation, authenticated invalid requests still consume admission attempts. An early coarse limiter and a later per-user limiter can coexist. Actual accounting depends on the limiter’s policy. [[9]](#source-9)

**Assembly must preserve list order**

Build nested middleware from the end of the list toward the beginning. If the list is A, B, C, the result must enter A first and C last. The complete composer in Appendix A implements this and creates a fresh continuation guard for every request.

Part IV

## Distinguish neighboring patterns

Similar class shapes can serve different design goals. Compare intent and control flow.

## 14Chain vs Decorator

| Question | Decorator | Chain / middleware |
| --- | --- | --- |
| Primary intent | Add behavior around an object while preserving its abstraction. | Let a request pass through potential processors or receivers. |
| Typical shape | Wrapper holds the wrapped object. | Handler delegates to a successor or a next callback. |
| Continuation | Delegation commonly supports the enhancement. | Short-circuiting is an explicit part of the contract. |

The distinction is intent, not a rule that decorators must always delegate. Middleware may be implemented with a decorator-like structure and still serve a chain-of-responsibility purpose.

## 15Chain vs Observer

| Observer | Chain |
| --- | --- |
| An event is offered to multiple subscribers. | A request follows a configured sequence. |
| One subscriber usually does not decide whether another receives it. | A stage can prevent downstream stages from running. |
| Useful for independent reactions such as notifications and analytics. | Useful for staged request processing. |

Observer does not inherently mean parallel or unordered execution. The decisive difference here is the continuation relationship between stages.

## 16Chain vs Template Method

Lesson 12 put a stable workflow in a base method and exposed selected subclass operations. Here, the sequence is assembled from collaborators.

| Template Method | Chain |
| --- | --- |
| The template method owns the algorithm skeleton. | A composition location defines the stage sequence. |
| Variation commonly uses inheritance. | Variation commonly uses separately supplied handlers. |
| A good fit for one stable lifecycle. | A good fit for independently composed processing stages. |

A chain can be assembled at startup and remain fixed. Configurable composition does not require live mutation. Conversely, if no stage can stop and the order is essential domain logic, an explicit workflow may communicate more clearly.

## 17Chain vs Command

A command represents **what is requested**. A chain handles concerns around processing it.

Java · teaching excerptCopy

```
record TransferMoneyCommand(
    String commandId,
    String fromAccount,
    String toAccount,
    long amountInCents
) {}
```

The same command can pass through validation, authorization, and idempotency handling before reaching its business handler. The command does not need to know which middleware exists.

## 18Command pipelines connect the patterns

A command pipeline can assemble authorization, validation, logging, transaction handling, and idempotency around execution. This is a useful architecture, but a diagram of stage names does not settle correctness.

| Concern | Decision you still own |
| --- | --- |
| Transaction | Which operations belong to one transaction, and who commits or rolls back? |
| Idempotency | What identifies a repeated request, and how is the outcome stored consistently with the business effect? |
| Retry | Which failures are retryable, and could retrying duplicate side effects? |

The continuation guard in this guide prevents a stage from calling downstream twice in one invocation. It does **not** provide durable idempotency or exactly-once business execution across retries.

Part V

## Make the semantics visible

A useful chain tells you where results come from, where failure is observed, and which dependencies determine order.

## 19Failures and rejections are different outcomes

An audit stage that only records “started” cannot report the final decision. Put it outside the stages it must observe, inspect returned outcomes, and catch failures deliberately.

Java · logging method body excerptCopy

```
try {
    Response response = next.invoke(request);
    log.accept("result:" + response.outcome());
    return response;
} catch (RuntimeException ex) {
    log.accept("failed:" + ex.getClass().getSimpleName());
    throw ex;
} finally {
    log.accept("finish");
}
```

A rejection returned as `Response` never enters `catch`. A logging stage placed after authentication cannot observe authentication rejections. The demo log sink is assumed not to throw; production audit failure policy must be explicit.

**No automatic rollback**

Stopping a chain does not reverse earlier side effects. A transaction boundary, compensation, and external response mapping remain separate responsibilities. This guide’s business handler returns a simulated result and changes no balances.

## 20Enrichment can hide dependencies

If one stage sets a risk score and another reads it, the second depends on the first. Calling the order “configuration” does not remove that dependency.

Java · teaching excerptCopy

```
Request authenticated = request.withUser(verifiedUserId);
return next.invoke(authenticated);
```

The reference example uses a record and creates replacement values for identity and correlation ID. Its components are strings and a primitive. Records provide final component fields; arbitrary referenced objects inside records would not become deeply immutable. [[5]](#source-5)

For a richer dependency such as “risk assessment required before fraud decision,” consider explicit types or orchestration. Do not turn the context into an untyped bag of hidden prerequisites.

## 21Keep required business workflows explicit

“Withdraw, deposit, record ledger” describes the transfer use case itself. Hiding those mandatory operations in a reorderable collection can obscure the invariant you need to protect.

Keep those steps in an explicit application operation with the necessary transaction semantics. Use surrounding middleware for independently composed concerns: authentication, authorization, validation, admission control, logging, metrics, and request normalization.

**The boundary to remember**

A chain organizes processing. It does not make unrelated steps independent, enforce transactionality, or make every reordering valid.

## 22Test a handler in isolation

Supply a small `Next` spy. Check the returned decision and whether delegation happened. The complete example uses plain Java checks, so there is no testing-library dependency.

Java · check body using Appendix A typesCopy

```
int[] calls = {0};
Next spy = request -> {
    calls[0]++;
    return new Response(Outcome.OK, "accepted");
};
Response result = new Validation().handle(
    new Request("demo-token", "U1", -100, "test-id"), spy);

check(result.outcome() == Outcome.INVALID, "negative amount rejected");
check(calls[0] == 0, "validation must not call next");
```

Also test the passing case: `next` receives the intended request and its result returns to the caller.

## 23Prove short-circuiting and unwinding

| Scenario | Assertion that matters |
| --- | --- |
| Bad credential and bad amount | Authentication result wins; rate limiting and business are skipped. |
| Valid identity, invalid amount | Validation rejects and business is not called. |
| Quota denied / permission denied | The corresponding result returns; business is not called. |
| Downstream throws | The same exception propagates and outer finally runs. |
| Middleware calls next twice | The second attempt fails before a second downstream execution. |
| Same pipeline invoked twice | Each request starts at the first stage and reaches business once when accepted. |
| Empty middleware list | The terminal handler supplies the response. |

These checks verify the continuation contract and observable effects. Checking only a returned error is insufficient: the business handler might already have run.

## 24A practical Java composition root

Put the order in one place. The full program supplies every type, a composer, demo policies, a terminal business function, and executable checks.

Java · exact composition from the complete exampleCopy

```
return compose(List.of(
    new CorrelationId(),
    new Logging(log),
    new Authentication(demoAuth),
    new RateLimit(limiter),
    new Validation(),
    new Authorization("U1"::equals)
), business);
```

Correlation ID is assigned before logging. Logging surrounds all policy stages. Authentication establishes identity before per-user admission. Validation and authorization finish before business execution.

**Why there is no shared cursor**

The composer builds nested functions once. Each invocation has its own local “next already called” guard. Immutable wiring can be reused; stateful collaborators still need their own concurrency design. `List.copyOf` does not make a rate limiter or log sink thread-safe.

## 25Recognize when a chain becomes hard to reason about

Warning signs include many undocumented ordering rules, shared request mutation, unclear error ownership, duplicate business execution, mutable successor cycles, and runtime configuration that can bypass required checks.

Write a short contract for each stage: what it requires, what it produces, when it stops, and what it can change. If you cannot explain why a stage exists in that position, make the orchestration explicit or simplify the chain.

| Failure mode | Design response |
| --- | --- |
| “Magic” context fields | Use explicit fields, typed values, or a dedicated workflow. |
| Order changed without review | Centralize assembly and test the invariant. |
| Repeated next calls | Document zero-or-one continuation; guard it if valuable. |
| Async work introduced | Use an asynchronous contract; synchronous finally measures return, not future completion. |

## 26Use the first-principles decision process

1. **Do requests pass through multiple independent processors?** If there is only one simple use case, explicit code may be sufficient.
2. **Can a stage meaningfully stop or complete processing?** State the expected result for every stopping point.
3. **Do different operations need different valid compositions?** Keep required dependencies visible when assembling them.
4. **Should the sender know only the entry point?** Hide stage wiring behind a stable invocation contract.
5. **Do stages need to surround downstream work?** Choose a next-callback model; otherwise start with a list.

Choose Chain of Responsibility because continuation is part of the problem, not because several classes happen to implement the same interface.

Practice

## Build an API request pipeline

Define `Middleware.handle(Request, Next)` and assemble this order in one composition location. Add logging around the stages whose final outcome it must observe.

| Position | Stage | Responsibility |
| --- | --- | --- |
| 1 | Correlation ID | Assign request identity for tracing. |
| 2 | Authentication | Establish a trusted identity or stop. |
| 3 | Rate limiting | Apply the chosen admission policy. |
| 4 | Validation | Reject invalid input. |
| 5 | Authorization | Check permission for the requested action. |
| 6 | Business handler | Execute the use case and return a result. |

### Acceptance criteria

1. Authentication failure stops all downstream execution.
2. Validation happens only after authentication.
3. Logging can run before and after the rest of the chain, including when it throws.
4. Business code knows nothing about middleware or `Next`.
5. Middleware order is defined in one composition location.
6. Checks prove a rejected request never reaches business execution.
7. Explain whether rate limiting belongs before or after authentication, which key it uses, and what consumes quota.

### Before opening the reference

Write the expected trace for an accepted request, an authentication rejection, and a business exception. Decide what an empty chain does and what happens if a stage calls `next` twice. Then implement the smallest model that satisfies those decisions.

**Reference choices**

Appendix A chooses per-user admission after authentication, response values for expected rejection, exception propagation for unexpected failures, outer logging, immutable request enrichment, and a terminal handler. These are explicit choices for the exercise, not universal middleware defaults.

Appendix A · runnable reference

## One file, no external dependencies

Save the complete source as `Lesson13Demo.java`. The following blocks are consecutive parts of that single file; join them in order, or use the download button. The earlier lesson snippets are independent teaching excerpts and should not be pasted together with this class.

Download Lesson13Demo.java

Run with JDK 25 · no preview featuresCopy

```
javac --release 25 -Xlint:all -Werror Lesson13Demo.java
java Lesson13Demo
```

The program uses only standard APIs and stable language features supported by Java 25. The `--release` option selects the language and API target. [[7]](#source-7)

**Verification scope**

The source compiled with `--release 17 -Xlint:all -Werror` and its checks passed on OpenJDK 17.0.20 in this workspace. Java 25 API and language compatibility were checked against official documentation. **A JDK 25 execution was not available here.**

**Demo boundaries:** fixed credential strings and a simple permission predicate are test doubles. The injected rate limiter returns an admission decision; the example does not implement quota storage or time windows. No network service is called, no tokens are parsed, and no money is moved. The log consumer is assumed not to throw.

The checks throw `AssertionError` explicitly, so `-ea` is not required. The local continuation guard uses `AtomicBoolean.compareAndSet`; it does not make the whole pipeline asynchronous or transactional. [[8]](#source-8)

### A1. Data and contracts

Lesson13Demo.java · part 1 of 7Copy

```
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Predicate;

public final class Lesson13Demo {
    // PART 1: Data and contracts
    record Request(String token, String userId,
                   long amountInCents, String correlationId) {
        Request withUser(String id) {
            return new Request(token, id, amountInCents, correlationId);
        }

        Request withCorrelation(String id) {
            return new Request(token, userId, amountInCents, id);
        }
    }

    enum Outcome {
        OK, UNAUTHENTICATED, RATE_LIMITED, INVALID, FORBIDDEN
    }

    record Response(Outcome outcome, String message) {}

    @FunctionalInterface
    interface Next {
        Response invoke(Request request);
    }

    @FunctionalInterface
    interface Middleware {
        Response handle(Request request, Next next);
    }

    @FunctionalInterface
    interface Authenticator {
        Optional<String> authenticate(String token);
    }

    @FunctionalInterface
    interface RateLimiter {
        boolean allow(String userId);
    }
```

### A2. Compose once; invoke many times

Lesson13Demo.java · part 2 of 7Copy

```
    // PART 2: Compose once; invoke many times
    static Next compose(List<Middleware> middleware, Next terminal) {
        var snapshot = List.copyOf(middleware);
        Objects.requireNonNull(terminal);
        Next chain = request -> Objects.requireNonNull(
            terminal.invoke(Objects.requireNonNull(request)));

        for (int i = snapshot.size() - 1; i >= 0; i--) {
            Middleware current = snapshot.get(i);
            Next downstream = chain;
            chain = request -> {
                Objects.requireNonNull(request);
                var called = new AtomicBoolean();
                Next once = forwarded -> {
                    if (!called.compareAndSet(false, true)) {
                        throw new IllegalStateException(
                            "next may be called at most once");
                    }
                    return downstream.invoke(
                        Objects.requireNonNull(forwarded));
                };
                return Objects.requireNonNull(
                    current.handle(request, once));
            };
        }
        return chain;
    }
```

### A3. Enrich, surround, authenticate

Lesson13Demo.java · part 3 of 7Copy

```
    // PART 3: Enrich, surround, authenticate
    static final class CorrelationId implements Middleware {
        @Override
        public Response handle(Request request, Next next) {
            return next.invoke(request.withCorrelation(
                UUID.randomUUID().toString()));
        }
    }

    record Logging(Consumer<String> log) implements Middleware {
        @Override
        public Response handle(Request request, Next next) {
            log.accept("start");
            try {
                Response response = next.invoke(request);
                log.accept("result:" + response.outcome());
                return response;
            } catch (RuntimeException ex) {
                log.accept("failed:" + ex.getClass().getSimpleName());
                throw ex;
            } finally {
                log.accept("finish");
            }
        }
    }

    record Authentication(Authenticator auth) implements Middleware {
        @Override
        public Response handle(Request request, Next next) {
            var user = auth.authenticate(request.token());
            if (user.isEmpty()) {
                return new Response(Outcome.UNAUTHENTICATED,
                    "Authentication required");
            }
            return next.invoke(request.withUser(user.orElseThrow()));
        }
    }
```

### A4. Rate limit, validate, authorize

Lesson13Demo.java · part 4 of 7Copy

```
    // PART 4: Rate limit, validate, authorize
    record RateLimit(RateLimiter limiter) implements Middleware {
        @Override
        public Response handle(Request request, Next next) {
            if (!limiter.allow(request.userId())) {
                return new Response(Outcome.RATE_LIMITED,
                    "Request quota exhausted");
            }
            return next.invoke(request);
        }
    }

    static final class Validation implements Middleware {
        @Override
        public Response handle(Request request, Next next) {
            if (request.amountInCents() <= 0) {
                return new Response(Outcome.INVALID,
                    "Amount must be positive");
            }
            return next.invoke(request);
        }
    }

    record Authorization(Predicate<String> permitted)
            implements Middleware {
        @Override
        public Response handle(Request request, Next next) {
            if (!permitted.test(request.userId())) {
                return new Response(Outcome.FORBIDDEN,
                    "Transfer permission required");
            }
            return next.invoke(request);
        }
    }
```

### A5. One composition root, with explicit demo policies

Lesson13Demo.java · part 5 of 7Copy

```
    // PART 5: One composition root, with explicit demo policies
    static Next demoPipeline(RateLimiter limiter, Next business,
                             Consumer<String> log) {
        Authenticator demoAuth = token -> {
            if ("demo-token".equals(token)) return Optional.of("U1");
            if ("read-only".equals(token)) return Optional.of("U2");
            return Optional.empty();
        };
        return compose(List.of(
            new CorrelationId(),
            new Logging(log),
            new Authentication(demoAuth),
            new RateLimit(limiter),
            new Validation(),
            new Authorization("U1"::equals)
        ), business);
    }

    static Response business(Request request) {
        return new Response(Outcome.OK,
            "Accepted " + request.amountInCents() + " cents");
    }

    public static void main(String[] args) {
        // Always-allow is a test double, not a real rate limiter.
        Next pipeline = demoPipeline(user -> true,
            Lesson13Demo::business, System.out::println);
        System.out.println(pipeline.invoke(
            new Request("demo-token", null, 500, null)));
        runChecks();
        System.out.println("All checks passed.");
    }
```

### A6. Rejections must not reach the business handler

Lesson13Demo.java · part 6 of 7Copy

```
    // PART 6: Rejections must not reach the business handler
    static void runChecks() {
        var events = new ArrayList<String>();
        int[] businessCalls = {0};
        int[] rateCalls = {0};
        Next businessSpy = request -> {
            check("U1".equals(request.userId()), "trusted user");
            check(request.correlationId() != null, "correlation id");
            businessCalls[0]++;
            return business(request);
        };
        Next pipeline = demoPipeline(user -> {
            check(user != null, "authenticate before rate limit");
            rateCalls[0]++;
            return true;
        }, businessSpy, events::add);

        Request accepted = new Request("demo-token", null, 500, null);
        check(pipeline.invoke(accepted).outcome() == Outcome.OK,
            "accepted result");
        check(pipeline.invoke(accepted).outcome() == Outcome.OK,
            "pipeline can be reused");
        check(businessCalls[0] == 2, "business runs once per call");
        check(accepted.userId() == null, "input record unchanged");

        events.clear();
        Response unauthenticated = pipeline.invoke(
            new Request("bad-token", "forged", -1, null));
        check(unauthenticated.outcome() == Outcome.UNAUTHENTICATED,
            "authenticate before validating the negative amount");
        check(rateCalls[0] == 2, "auth rejection skips rate limit");
        check(businessCalls[0] == 2, "auth rejection skips business");
        check(events.equals(List.of("start",
            "result:UNAUTHENTICATED", "finish")), "log rejection");

        check(pipeline.invoke(new Request("demo-token", null, 0, null))
            .outcome() == Outcome.INVALID, "reject zero amount");
        check(pipeline.invoke(new Request("read-only", null, 1, null))
            .outcome() == Outcome.FORBIDDEN, "reject permission");
        Next limited = demoPipeline(user -> false, businessSpy, s -> {});
        check(limited.invoke(accepted).outcome() == Outcome.RATE_LIMITED,
            "reject quota");
        check(businessCalls[0] == 2, "all rejections skip business");

        checkExceptionalExit(events, accepted);
        checkContinuationGuard(accepted);
        checkEmptyChain(accepted);
    }
```

### A7. Failure, double-next and empty-chain behavior

Lesson13Demo.java · part 7 of 7Copy

```
    // PART 7: Failure, double-next and empty-chain behavior
    static void checkExceptionalExit(List<String> events, Request request) {
        events.clear();
        var failure = new IllegalStateException("simulated failure");
        Next broken = demoPipeline(user -> true, r -> {
            throw failure;
        }, events::add);
        try {
            broken.invoke(request);
            throw new AssertionError("exception must propagate");
        } catch (IllegalStateException actual) {
            check(actual == failure, "preserve original exception");
        }
        check(events.equals(List.of("start",
            "failed:IllegalStateException", "finish")), "finally runs");
    }

    static void checkContinuationGuard(Request request) {
        int[] calls = {0};
        Middleware twice = (r, next) -> {
            next.invoke(r);
            return next.invoke(r);
        };
        Next guarded = compose(List.of(twice), r -> {
            calls[0]++;
            return business(r);
        });
        try {
            guarded.invoke(request);
            throw new AssertionError("double next must fail");
        } catch (IllegalStateException expected) {
            check(calls[0] == 1, "never execute downstream twice");
        }
    }

    static void checkEmptyChain(Request request) {
        Next empty = compose(List.of(), Lesson13Demo::business);
        check(empty.invoke(request).outcome() == Outcome.OK,
            "empty chain invokes terminal handler");
    }

    static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
```

### Expected output

ConsoleCopy

```
start
result:OK
finish
Response[outcome=OK, message=Accepted 500 cents]
All checks passed.
```

Appendix B · pattern map

## Place the pattern in the larger picture

| Pattern | Design pressure it addresses |
| --- | --- |
| Strategy | Swap an algorithm behind a shared contract. |
| Template Method | Keep a workflow skeleton; specialize selected steps. |
| Chain of Responsibility | Offer a request to ordered handlers with controlled continuation. |
| Observer | Notify multiple subscribers of an event or change. |
| State | Vary behavior with lifecycle state. |
| Command | Represent a requested action as an object. |
| Factory | Encapsulate implementation selection or object creation. |
| Builder | Assemble a complex object. |
| Adapter | Translate one interface into another. |
| Decorator | Layer behavior around an abstraction. |
| Facade | Offer a simpler entry point to a subsystem. |
| Proxy | Provide a stand-in that controls access. |
| Composite | Model recursive part-whole structures uniformly. |

### Next: Repository + Dependency Injection

Move from isolated patterns into application architecture: dependency inversion defines the direction of dependencies; dependency injection supplies collaborators; repositories abstract persistence needs; the composition root wires concrete implementations together.

The question becomes: how can a use case depend on the capabilities it needs while keeping database clients and other infrastructure choices outside its core logic?

Appendix C · official references

## Sources and editorial notes

This guide adapts the supplied Lesson 13 and preserves its 26-step teaching sequence. Examples and design recommendations are the guide’s own; official sources below verify the pattern definition and Java contracts. References were checked on 1 September 2026. The guide itself works offline; opening a source link requires a connection.

1. [Microsoft Learn · Chain of Responsibility](https://learn.microsoft.com/en-us/archive/msdn-magazine/2001/october/biztalk-implement-design-patterns-for-business-rules-with-orchestration-designer)

   Classic intent: multiple potential receivers, forwarding until handled.

   https://learn.microsoft.com/en-us/archive/msdn-magazine/2001/october/biztalk-implement-design-patterns-for-business-rules-with-orchestration-designer
2. [Oracle · Java 25 Filter](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.httpserver/com/sun/net/httpserver/Filter.html)

   Pre/post-processing and the choice to continue or send a response.

   https://docs.oracle.com/en/java/javase/25/docs/api/jdk.httpserver/com/sun/net/httpserver/Filter.html
3. [Oracle · Java 25 Filter.Chain](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.httpserver/com/sun/net/httpserver/Filter.Chain.html)

   Next-filter invocation and the terminal exchange handler.

   https://docs.oracle.com/en/java/javase/25/docs/api/jdk.httpserver/com/sun/net/httpserver/Filter.Chain.html
4. [Oracle · Java 25 List](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html)

   List.of and List.copyOf contracts, order, null handling, and shallow immutability.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html
5. [Oracle · Java 25 record classes](https://docs.oracle.com/en/java/javase/25/language/records.html)

   Record components, generated accessors, and final fields.

   https://docs.oracle.com/en/java/javase/25/language/records.html
6. [Oracle · JLS 25, §14.20.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20.2)

   Return, exception unwinding, and finally completion rules.

   https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20.2
7. [Oracle · Java 25 javac](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

   The --release compiler option and compilation targets.

   https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html
8. [Oracle · Java 25 AtomicBoolean](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/AtomicBoolean.html)

   compareAndSet semantics used by the continuation guard.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/AtomicBoolean.html
9. [Microsoft Learn · Rate limiting middleware](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit?view=aspnetcore-10.0)

   Admission policies and partitioning; used for concepts, not as a Java API.

   https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit?view=aspnetcore-10.0
10. [Jakarta Servlet 6.1 · FilterChain](https://jakarta.ee/specifications/servlet/6.1/apidocs/jakarta.servlet/jakarta/servlet/filterchain)

    A separate servlet API, distinct from the JDK HTTP server chain.

    https://jakarta.ee/specifications/servlet/6.1/apidocs/jakarta.servlet/jakarta/servlet/filterchain

Editorial corrections: the amount cap is labeled as a business limit; JDK and Jakarta filter APIs are distinguished; middleware assembly, a terminal result, failure behavior, and complete checks are supplied; list pipelines and first-handler-wins chains are separated.

DP · Lesson 13 · Adapted from the supplied lesson · Official references checked 1 September 2026