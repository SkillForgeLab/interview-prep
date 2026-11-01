[Skip to guide](#guide)

DP / Lesson 23

[Steps 1–5First, bound the waiting](#waiting)[Steps 6–9Then, make repetition safe](#repetition)[Steps 10–17Reduce pressure, then break synchronization](#spacing)[Steps 18–23Turn the mechanism into a policy](#policy)[Steps 24–30Give retry a clear owner](#ownership)[Steps 31–35Reconnect retry to the workflow](#workflow)[Steps 36–44Test the semantics, not the waiting](#testing)[Steps 45–48Operate the policy and know when it stops helping](#operation)

---

[Appendix A · Java implementation](#implementation)[Appendix B · Tests](#tests)[Official sources](#sources)Print / Save as PDF

One file. Works offline.
Light theme. A4 & Letter friendly.

23 / Distributed interaction patterns

# Timeout → Retry → Exponential Backoff → Jitter

Recover from a temporary failure without repeating a business effect or turning a small outage into a larger one.

First principlesJava 25 compatible48-step progressionComplete runnable examples

How long should we wait, when is another attempt safe, and how do we keep many callers from retrying together?

Print / Save as PDF[Jump to Java code](#implementation)

We left the Saga lesson with Checkout calling Payment. Now we follow one unreliable call from the first timeout through safe repetition, controlled waiting and randomized timing. Each mechanism appears only after the previous one leaves a problem unsolved.

Read in order for the derivation. Use the navigation for review. Small code blocks are labeled fragments; the appendices contain complete source files. This document needs no external scripts, fonts or services. Source links open official documentation.

[Steps 1–5: First, bound the waiting](#waiting)[Steps 6–9: Then, make repetition safe](#repetition)[Steps 10–17: Reduce pressure, then break synchronization](#spacing)[Steps 18–23: Turn the mechanism into a policy](#policy)[Steps 24–30: Give retry a clear owner](#ownership)[Steps 31–35: Reconnect retry to the workflow](#workflow)[Steps 36–44: Test the semantics, not the waiting](#testing)[Steps 45–48: Operate the policy and know when it stops helping](#operation)

For PDF: use Print / Save as PDF, portrait, A4 or Letter, and disable the browser’s extra headers and footers. The print stylesheet hides controls and includes the complete code and source references.

Steps 1–5

## First, bound the waiting

Pressure: one slow remote call can occupy resources long after it is useful.

### 01The simplest working implementation

Our Checkout Saga calls Payment to authorize a purchase. In this *illustrative scenario*, Payment usually responds in 100–300 ms. Today it is slow. Before deciding how often to retry, ask: **how long can one attempt wait?**

Java · fragment

```
HttpRequest request = HttpRequest.newBuilder(paymentUri)
        .POST(HttpRequest.BodyPublishers.ofString(paymentJson))
        .build();
HttpResponse<String> response = client.send(
        request, HttpResponse.BodyHandlers.ofString());
```

This code sends one request. It does not define a useful waiting limit. While the caller waits, memory, connections and worker capacity may remain occupied. Enough slow calls can exhaust a bounded pool.

### 02Derive a timeout

A timeout is a local boundary: after this duration, the caller stops waiting for this attempt. Set a connection timeout on the client and a request timeout on each request. An unset Java request timeout is effectively infinite. [[1]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html#timeout(java.time.Duration) "Oracle · HttpRequest.Builder")[[2]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.Builder.html#connectTimeout(java.time.Duration) "Oracle · HttpClient.Builder")

Java · fragment

```
HttpClient client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(2))
        .build();

HttpRequest request = HttpRequest.newBuilder(paymentUri)
        .timeout(Duration.ofSeconds(3))
        .POST(HttpRequest.BodyPublishers.ofString(paymentJson))
        .build();
```

**Example values, not production defaults**

The durations in this guide illustrate behavior. Choose actual limits from measured latency and the caller’s deadline.

### 03Connection timeout, request timeout, total budget

| Limit | Question it answers | Scope |
| --- | --- | --- |
| Connection timeout | How long can establishing a new connection take? | Applies when a new connection is needed; has no effect on a reused connection. [[2]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.Builder.html#connectTimeout(java.time.Duration) "Oracle · HttpClient.Builder") |
| Request timeout | How long will this request wait for a response? | Configured on each HttpRequest. It is not a budget for the entire retry sequence. [[1]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html#timeout(java.time.Duration) "Oracle · HttpRequest.Builder") |
| Overall deadline | How long is the logical call useful? | Includes attempts, backoff and local overhead; supplied by the caller. |

Do not model these as three durations that must simply be added. Connection establishment is part of an attempt, and attempts must fit inside the overall budget. For a full response-body wait, the adapter in Appendix A also bounds the asynchronous future. [[11]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Future.html#get(long,java.util.concurrent.TimeUnit) "Oracle · Future")[[12]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpResponse.BodySubscribers.html#ofString(java.nio.charset.Charset) "Oracle · HttpResponse.BodySubscribers")

### 04A timeout is a client decision

Payment might complete just before the connection fails. Or it might still be processing after the caller times out. The observation is **“I did not receive a result in time.”** It does not establish whether the business operation happened.

**Stopping the wait does not undo the effect**

Java HTTP cancellation is best effort. The request may still reach the server, and resource release may happen later. A timeout or cancellation cannot provide a remote rollback. [[3]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html "Oracle · HttpClient")

### 05The outcome is ambiguous

| What happened remotely? | What the caller sees |
| --- | --- |
| Request never arrived. | Timeout. |
| Request arrived and is still running. | Timeout. |
| Authorization committed, but its response was lost. | Timeout. |

All three histories can produce the same local observation. The correct business state may be **outcome unknown**. That state must survive into retry, reconciliation and Saga decisions.

Steps 6–9

## Then, make repetition safe

Pressure: the next attempt may succeed, but the previous attempt may already have succeeded.

### 06First response: retry

A temporary connection failure, brief restart or short overload may disappear. A retry repeats the operation in the hope that the transient condition has changed. It is a response to a classified failure, not a default response to every exception. [[4]](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry "Microsoft · Retry pattern")

Java · fragment

```
// Teaching fragment: adds a limit, but still retries immediately.
for (int attempt = 1; attempt <= 3; attempt++) {
    try {
        return payment.authorizeOnce(command, attemptTimeout);
    } catch (RetryGuide.RetryableFailure failure) {
        if (attempt == 3) {
            throw failure;
        }
    }
}
```

**Three maximum attempts means one initial call and at most two retries.** The first attempt does not need a retry delay.

### 07Problem one: is the operation safe to repeat?

If attempt 1 charges the customer and only its response disappears, attempt 2 can charge the customer again. A retry has improved the chance of receiving a response while breaking business correctness. [[4]](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry "Microsoft · Retry pattern")

Before retrying, establish whether repetition is safe: the operation is inherently idempotent, the service deduplicates a stable operation identity, or you have reliable evidence that no effect occurred. A timeout alone supplies no such evidence.

### 08Idempotency changes retry semantics

Create the operation identity once, when the logical authorization is created. Persist it with the command or Saga state, and reuse it across transport retries and restarts. Keep the payload unchanged.

Java · fragment

```
var command = new RetryGuide.PaymentCommand(
        persistedPaymentAttemptId,
        serializedAuthorization);

String result = retrier.execute(remainingBudget,
        timeout -> payment.authorizeOnce(command, timeout));
```

A header is only an identifier. The server must atomically coordinate deduplication with the effect, detect incompatible payload reuse, and define behavior for concurrent attempts and retention expiry. Provider contracts differ; Stripe’s API is one documented example. [[8]](https://docs.stripe.com/api/idempotent_requests "Stripe · Idempotent requests")

**Identity belongs to the operation**

An order can have several legitimate payment operations. Give each one its own identity. Generating a new UUID inside the retry loop makes every attempt look like a new operation.

### 09Problem two: immediate retry increases load

An overloaded Payment service times out. Callers retry immediately. Payment receives the original work plus the retries while capacity is already scarce. The feedback loop is overload → timeouts → retries → more overload. [[5]](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/retry-storm/ "Microsoft · Retry storm antipattern")

If 100 logical calls each make three attempts, they can produce up to 300 application-level invocations. Idempotency protects effects, but duplicate requests can still consume CPU, network, locks and deduplication capacity.

Steps 10–17

## Reduce pressure, then break synchronization

Pressure: a delayed retry can still arrive in a synchronized crowd.

### 10Wait before retrying

Add a delay between a failed attempt and the next one. That gives a transient condition time to recover and lowers the rate at which one caller repeats work.

Java · fragment

```
// Modern Java supports Duration-based sleep.
Thread.sleep(Duration.ofMillis(500));
```

The reusable engine delegates waiting to an injected Sleeper. Its production implementation uses TimeUnit so the complete example also compiles on the available Java 17 validation runtime. [[10]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html "Oracle · Thread")

### 11Fixed delays synchronize clients

Imagine many clients fail at approximately the same time. Each waits 500 ms. They retry together 500 ms later. Fixed waiting has shifted the burst in time, while preserving its shape.

| Client | Failure time | Fixed wait | Next attempt |
| --- | --- | --- | --- |
| A | 0 ms | 500 ms | 500 ms |
| B | 0 ms | 500 ms | 500 ms |
| C | 0 ms | 500 ms | 500 ms |

### 12Increase the delay after each failure

Repeated failure is evidence that immediate recovery is less likely. A widening waiting window lets the caller back away progressively. A common choice doubles the window after each failure. [[6]](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html "AWS · Retry behavior")

**Exponential backoff**

With failed-attempt number `a` starting at 1: `window(a) = min(cap, base × 2^(a − 1))`. The first retry uses the base window.

### 13Make backoff arithmetic safe

The convenient expression `base * (1L << retryNumber)` is a trap for unconstrained inputs: a shift or multiplication can produce the wrong value before the cap is applied. Saturate while doubling instead.

Java · excerpt from Retrier.windowNanos

```
long window = config.baseDelay().toNanos();
long cap = config.maxDelay().toNanos();
for (int i = 1; i < failedAttempt && window < cap; i++) {
    window = window > cap / 2 ? cap : window * 2;
}
return window;
```

| Failed attempt | 1 | 2 | 3 | 4 | 5 | 6+ |
| --- | --- | --- | --- | --- | --- | --- |
| Window, base 200 ms / cap 5 s | 200 ms | 400 ms | 800 ms | 1,600 ms | 3,200 ms | 5,000 ms |

### 14Cap delay, attempts and total time

A delay can grow beyond the remaining useful lifetime of a checkout. A cap prevents an individual backoff window from growing indefinitely. It does not bound the number of attempts or the total call duration.

| Boundary | What it limits |
| --- | --- |
| maxDelay | One locally generated backoff window. |
| maxAttempts | Total application-level invocations, including the first. |
| totalBudget | Elapsed time available for attempts and waiting. |
| minAttemptBudget | The minimum remaining time this use case considers useful for starting an attempt. |

The minimum is an admission rule, not a promise that the next attempt will finish.

### 15Exponential backoff can still synchronize clients

If every caller uses exactly 200, 400, 800 and 1,600 ms, callers that fail together can keep retrying together. Exponential backoff reduces frequency. It does not, by itself, remove coordinated timing.

### 16Add randomness: jitter

At a window of 800 ms, one caller might wait 117 ms, another 683 ms, and a third 401 ms. These are illustrative draws. Random delays spread retry arrivals across time instead of scheduling a common instant. [[6]](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html "AWS · Retry behavior")

Jitter reduces synchronization statistically. It does not guarantee that two clients will never collide, nor does it guarantee that the next sampled delay is larger than the last.

### 17Full jitter

**The algorithm**

First compute the capped exponential window. Then sample uniformly between zero and that window. The window increases; each actual delay is a fresh draw.

Java · fragment

```
long window = windowNanos(failedAttempt);
long delayNanos = ThreadLocalRandom.current()
        .nextLong(window + 1);
return Duration.ofNanos(delayNanos);
```

The inclusive endpoint comes from passing `window + 1` to an API with an exclusive upper bound. Appendix A validates duration ranges so this addition is safe. [[13]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ThreadLocalRandom.html#nextLong(long) "Oracle · ThreadLocalRandom")

Full jitter permits a zero-length wait. For a continuous uniform window W, the expected delay is W/2. This means jitter also changes average waiting time compared with always waiting the full window.

#### Explore the retry timing

12 callers fail together at t = 0. Marks show subsequent attempt start times. Attempt durations are omitted to isolate the effect of waiting. This is an illustrative simulation, not measured traffic.

Delay policyFixed delayExponential backoffFull jitterBase delay (ms)Delay cap (ms)Total attempts

Full jitter · 4 total attempts · base 200 ms · cap 2,000 ms.

C1

C2

C3

C4

C5

C6

C7

C8

C9

C10

C11

C12

0 ms700 ms1,400 ms

Each dot is one retry. A common scale compares all policies. The reproducible sample is held fixed when you change policies.

Retry start times after the initial failure (ms)

| Caller | Attempt 2 | Attempt 3 | Attempt 4 |
| --- | --- | --- | --- |
| C1 | 61 | 286 | 305 |
| C2 | 179 | 530 | 1200 |
| C3 | 96 | 172 | 692 |
| C4 | 13 | 215 | 585 |
| C5 | 132 | 460 | 680 |
| C6 | 49 | 103 | 173 |
| C7 | 167 | 347 | 1068 |
| C8 | 84 | 390 | 961 |
| C9 | 1 | 32 | 452 |
| C10 | 119 | 276 | 546 |
| C11 | 37 | 320 | 440 |
| C12 | 155 | 164 | 935 |

The explorer requires JavaScript; all explanations, code and the static worked examples remain available without it.

Steps 18–23

## Turn the mechanism into a policy

Pressure: safe repetition still needs failure classification, server guidance and a caller-owned budget.

### 18Put the decisions in the right order

* Start with one persisted operation identity and the caller’s remaining budget.
* Before each attempt, check cancellation and remaining time.
* Clip the attempt timeout to the time still available.
* Classify failure using the dependency contract.
* Stop on a permanent failure or the final allowed attempt.
* Compute capped exponential backoff with jitter; apply any server delay floor.
* Wait only if a useful attempt can still fit, then recheck the budget.

Appendix A contains the complete engine. It retries only `RetryableFailure`. Other I/O failures, runtime failures and interruption escape instead of accidentally entering the retry path.

### 19Do not retry every failure

| Failure | Default decision for this example | Reason |
| --- | --- | --- |
| Payment declined | Do not retry unchanged. | Business rejection. |
| Invalid card or request | Do not retry unchanged. | Waiting does not repair the input. |
| Authentication/configuration failure | Stop; correct credentials or configuration. | Blind repetition cannot fix configuration. |
| Temporary unavailable | Potentially retry. | Only if the contract and budget permit it. |
| Rate limited | Potentially retry after delay. | Honor the dependency’s backpressure. |
| Timeout / lost response | Reconcile or retry with a stable identity. | Completion is uncertain. |

Status codes and exception classes are evidence, not a universal policy. Some APIs put important error classifications inside the response body. [[4]](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry "Microsoft · Retry pattern")

### 20Retryability belongs to the dependency contract

A dependency adapter should translate transport details into outcomes the use case understands. Avoid a catch-all rule such as “retry every 4xx” or “retry every IOException.”

Java · alternative domain model, independent of Appendix A

```
public sealed interface PaymentFailure {
    record Declined(String reason) implements PaymentFailure {}
    record InvalidRequest(String reason) implements PaymentFailure {}
    record TemporaryUnavailable() implements PaymentFailure {}
    record RateLimited(Duration retryAfter) implements PaymentFailure {}
    record UnknownOutcome() implements PaymentFailure {}
}
```

An `UnknownOutcome` needs the additional question: is repetition safe? The sample adapter explicitly assumes a server that deduplicates the supplied payment identity. Without that contract, its timeout retry path is inappropriate.

### 21Honor server backpressure

HTTP `Retry-After` can contain an integer delay in seconds or an HTTP date. It can accompany responses such as 503; throttling APIs can also supply retry guidance. [[7]](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after "RFC 9110 · HTTP Semantics")[[5]](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/retry-storm/ "Microsoft · Retry storm antipattern")

Java · fragment

```
Duration delay = localFullJitter;
if (serverRetryAfter.compareTo(delay) > 0) {
    delay = serverRetryAfter;
}
```

This guide treats a valid hint as a lower bound. Never randomize below that floor. If it cannot fit the caller’s deadline, stop synchronous retry or durably defer; do not shorten it to the local cap. A shared floor can still align callers, so extra positive jitter may be appropriate when the service contract permits it.

The example parser accepts seconds and the modern HTTP-date form. Invalid hints fall back to local backoff; enormous numeric delays end the synchronous retry. A fully general HTTP parser also needs the legacy date forms described by the RFC.

### 22One overall deadline

Suppose Checkout has 5 seconds remaining. Three attempts with 3-second timeouts could consume 9 seconds before any waits. A per-attempt timeout alone cannot implement the caller’s budget.

**Budget accounting**

`remaining = totalBudget − elapsed`
`attemptTimeout = min(configuredTimeout, remaining)`
`delay + minAttemptBudget ≤ remaining`

Use a monotonic clock for elapsed time within a process. `System.nanoTime()` supports duration measurement; its value is not a timestamp to send to another machine. Use wall-clock time only when interpreting an absolute HTTP date, then convert it to a duration. [[9]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime() "Oracle · System.nanoTime")

The engine starts its stopwatch when execute begins. Pass the budget *remaining at that point*, not a new full checkout allowance. This is cooperative deadline enforcement: the adapter must honor the supplied allowance, and scheduling or cancellation can complete late. It is not a hard real-time guarantee.

### 23Timeout selection is a trade-off

| If the timeout is… | Likely pressure |
| --- | --- |
| Too long | Resources remain occupied; queues and upstream latency can grow. |
| Too short | Slow-but-successful work is mistaken for failure; false timeouts can add retries. |

Use measured latency distributions, cold connection behavior, the caller’s remaining budget and the cost of false timeouts. Include realistic failure tests. The tutorial’s 700 ms attempt timeout and 3-second example budget are chosen to demonstrate the mechanics, not to prescribe checkout settings.

Steps 24–30

## Give retry a clear owner

Pressure: resilience scattered across layers compounds traffic and makes changes hard to reason about.

### 24Nested retries multiply work

Assume three layers each make up to three attempts for the same failing call. A worst-case path can reach **3 × 3 × 3 = 27** leaf invocations. That arithmetic assumes every layer exhausts its attempts; it is not an observed benchmark.

Choose an owner that understands safe repetition and the useful lifetime of the call. Inventory retry behavior in SDKs, HTTP clients, proxies and queues; configure the combined behavior deliberately. Uncoordinated nested policies compound work and latency. [[4]](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry "Microsoft · Retry pattern")

**A per-call limit is not a fleet-wide limit**

Even one well-bounded loop per request can flood a dependency during a broad outage. A shared retry budget, rate limiter or concurrency limit may also be needed. AWS documents retry quotas as one implementation. [[6]](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html "AWS · Retry behavior")

### 25The lowest layer lacks business context

An HTTP client may know that it saw 503. It may not know whether this is a charge, whether the command expired, or whether the Saga has already begun compensation. The layer that decides to retry must receive enough context to answer those questions.

Keep low-level transport recovery consistent with application retry ownership. The engine’s attempt counter counts adapter invocations; it does not promise an exact count of packets or internal transport attempts.

### 26Separate the source of change

Copying a slightly different retry loop into Payment, Inventory, Shipping and Tax makes one policy fix spread across many clients. Separate **how retry executes** from **which failures and limits a dependency permits**.

| Responsibility | Natural owner |
| --- | --- |
| Serialize, send, decode, classify | Dependency adapter. |
| Count attempts, track elapsed time, wait | Reusable execution mechanism. |
| Choose limits and repeat-safety rules | Dependency/use-case policy. |
| Persist delayed recovery and operation identity | Workflow owner. |

### 27A reusable retry mechanism

Java · fragment

```
var config = new RetryGuide.Config(
        3,                          // total attempts
        Duration.ofMillis(700),      // maximum per attempt
        Duration.ofMillis(50),       // minimum useful allowance
        Duration.ofMillis(200),      // first backoff window
        Duration.ofSeconds(2));      // local backoff cap

var retrier = RetryGuide.Retrier.production(config);
String result = retrier.execute(remainingBudget,
        timeout -> payment.authorizeOnce(command, timeout));
```

The mechanism accepts an operation and passes it the allowed attempt time. The adapter marks only known retryable failures. Clocks, waiting and randomness are injected so tests can control time without sleeping.

### 28Different dependencies need different policies

| Dependency | Questions its policy must answer |
| --- | --- |
| Payment | What does an unknown outcome mean? What identity deduplicates it? |
| Search | How much does a retry cost? Is a degraded result preferable? |
| Inventory | Is this still the same reservation command? Has it expired? |

Share the retry engine. Keep error classification, timing and fallback decisions specific to the dependency and use case. Read-only calls can still be expensive enough that retries are harmful.

### 29Proxy and Decorator provide a natural shape

An application can depend on a PaymentGateway port while a RetryingPaymentGateway wraps the HTTP adapter. The wrapper implements the same capability and adds an interaction policy.

| Layer, outside to inside | Job |
| --- | --- |
| Application / Saga | Supplies command identity and remaining budget. |
| RetryingPaymentGateway | Applies policy and delegates each attempt. |
| HttpPaymentGateway | Sends the request and maps its outcome. |
| Remote Payment service | Owns the authorization and deduplication. |

The wrapper must preserve observable semantics: business rejection, technical failure and unknown outcome remain distinguishable.

### 30Wrapper ordering is behavior

| Composition | Meaning |
| --- | --- |
| Retry around per-attempt timeout | Each invocation has its own bounded wait. |
| Overall deadline around retry | The sequence shares one budget across calls and delays. |
| Circuit breaker inside retry | The breaker can observe individual attempts, depending on its configuration. |
| Circuit breaker outside retry | The breaker can observe the final logical-call result instead. |

Often you need both attempt and overall limits. Metrics need the same distinction: per-attempt latency is different from total logical-call latency. Be explicit about what each wrapper observes.

Steps 31–35

## Reconnect retry to the workflow

Pressure: a local retry outcome influences durable business recovery.

### 31Saga interaction

| Payment outcome | Saga response to design |
| --- | --- |
| Declined | A business rejection may trigger compensation. |
| Temporarily unavailable | Retry forward within business and operational limits. |
| Outcome unknown | Query status or retry with the same identity; reconcile before assuming failure. |

A timeout does not justify pretending no authorization exists. If the Saga moves on while Payment completes late, it needs a rule for that late result: accept it, void it, compensate it or reconcile it. Persist the decision and keep recovery idempotent.

### 32Retry and Outbox solve different boundaries

An outbox relay repeats delivery when publication is uncertain. A remote-call retrier repeats invocation when a response is unavailable. Both need stable identities, but successful delivery and successful business execution are different facts.

| Boundary | Stable identity |
| --- | --- |
| Outbox delivery | Message ID. |
| Saga participant command | Command / operation ID. |
| HTTP authorization | Payment idempotency key. |

Do not replace a command identity just because the delivery mechanism retries. The same logical action may cross several at-least-once boundaries.

### 33Do not keep a database transaction open during backoff

Loading an order, calling Payment, sleeping and retrying before commit can retain a database connection and possibly locks throughout the remote wait. That enlarges the failure boundary.

For a durable workflow, commit the local state and outbox decision first. Perform remote processing separately, then persist the outcome in another local transaction. A remote timeout cannot roll back an already committed authorization.

### 34Short retry versus durable retry

| Short in-process retry | Durable workflow retry |
| --- | --- |
| Milliseconds or a few seconds inside a useful call budget. | Work resumed later, potentially after a process restart. |
| A short blocking wait can be acceptable. | Persist next\_attempt\_at and workflow state. |
| Process failure loses in-memory progress. | A scheduler or queue resumes the durable command. |

Persist the attempt count, next eligible time, operation identity, business expiry and ownership of the retry. Avoid letting both the in-process layer and a workflow worker independently exhaust large retry budgets.

Virtual threads can reduce the cost of blocking, but they do not make a sleeping workflow durable or create downstream capacity. Choose a scheduling model based on ownership and recovery, not only thread cost.

### 35Define failure semantics before the loop

| Outcome | Meaning | Typical action |
| --- | --- | --- |
| Success | Confirmed completion. | Continue. |
| Business rejection | Processed but refused. | Apply business policy; do not repeat unchanged. |
| Permanent technical failure | Configuration or protocol needs attention. | Fail / repair / escalate. |
| Transient failure | May recover soon. | Retry if safe and budgeted. |
| Throttled | Traffic is being limited. | Honor delay and reduce pressure. |
| Unknown outcome | Effect may have happened. | Reconcile or retry with safe identity. |
| Budget exhausted / cancelled | Caller stops spending time. | Stop local attempts; preserve any unresolved outcome. |

These outcomes determine the behavior of the workflow. A generic “failed” result is too weak for a side-effecting operation.

Steps 36–44

## Test the semantics, not the waiting

Pressure: real sleeps hide edge cases and make failure tests slow and flaky.

### 36Inject time, waiting and randomness

Java · fragment

```
@FunctionalInterface
public interface Sleeper {
    void sleep(Duration delay) throws InterruptedException;
}

@FunctionalInterface
public interface NanoClock {
    long now();
}

@FunctionalInterface
public interface Jitter {
    long nextLong(long upperExclusive);
}
```

A recording sleeper should also advance the fake clock. Otherwise a test can record delays while incorrectly believing the total deadline never moves. Appendix B uses this approach and requires no test framework.

### 37Transient failure recovers

Have the fake fail once with a retryable outcome, then succeed. Assert the returned result, two calls and one delay. Check that the first retry uses the base window; off-by-one errors commonly double it accidentally.

### 38Permanent failures stop immediately

Return a business rejection or unclassified permanent exception. Assert one call, no sleeps and the original failure. This catches an overbroad catch-and-retry loop even if its maximum-attempt test passes.

### 39The attempt limit includes the initial call

Make every attempt fail transiently. With maxAttempts = 3, assert exactly three calls and two waits. The final failure propagates immediately; there is no reason to sleep after the last allowed attempt.

### 40The identity stays stable

Record the operation identity and payload on every outgoing attempt. Assert they remain identical. Repeat this test across workflow recovery after a restart if the identity is meant to survive that boundary.

### 41Lose the response after the effect commits

The fake server stores the authorization result, then throws a timeout before returning it. The next call uses the same key and receives the stored result. Assert one effect and two invocations.

**Test the server contract too**

An in-memory fake only proves the client uses the contract correctly. Integration tests must exercise atomic deduplication, concurrent duplicates, payload mismatch and retention behavior in the real participant.

### 42Test windows and samples separately

Assert that the backoff *window* grows and saturates. Inject samples at zero and at the upper endpoint. Do not assert that actual random waits always increase. Include a huge attempt index to prove the arithmetic cannot wrap.

Appendix B checks first-window indexing and saturation. The full-jitter API uses nanoseconds; the timing explorer uses integer milliseconds for readable values.

### 43The deadline prevents useless work

* The initial budget is below the minimum: no attempt starts.
* The next delay leaves too little time: no sleep or retry starts.
* The server hint exceeds the budget: it is not shortened.
* Remaining time is below the configured attempt timeout: pass the smaller allowance.
* A sleeper overshoots: recheck the clock before sending again.

Also test a slow response body at the transport boundary. A fake that immediately returns cannot prove the real HTTP adapter’s waiting behavior.

### 44Interruption is cancellation information

If a method can declare InterruptedException, propagate it. If you must translate it to an unchecked or domain exception, restore the interrupt status first. Do not turn it into a transient dependency error. [[10]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html "Oracle · Thread")

Java · boundary translation example; the engine propagates directly

```
try {
    sleeper.sleep(delay);
} catch (InterruptedException interrupted) {
    Thread.currentThread().interrupt();
    throw new IllegalStateException("Retry cancelled", interrupted);
}
```

The test suite covers interruption during an attempt, during waiting and before the first attempt. The HTTP adapter requests cancellation of its in-flight future when interrupted.

Steps 45–48

## Operate the policy and know when it stops helping

Pressure: retries can hide deterioration until the system runs out of capacity.

### 45Observe both attempts and logical calls

| Measure | What it exposes |
| --- | --- |
| First-attempt success rate | Dependency health before retries hide failures. |
| Attempts per logical call | Load amplification. |
| Attempt and total latency | Remote waiting versus total user cost. |
| Retry reason and status category | Which failures consume the retry budget. |
| Delay / server hint / budget stop | Why work waits or stops. |
| Unknown outcomes and reconciliation age | Business operations still unresolved. |

Use correlation, command and Saga identifiers in structured logs and traces. Keep metric labels low in cardinality; do not make order IDs or payment keys metric dimensions. Avoid logging sensitive payment payloads.

**A useful operational question**

If final success is steady but attempts per call and total latency keep rising, is resilience concealing a dependency outage?

### 46When not to retry

* The failure is a business rejection or unchanged invalid input.
* The operation can duplicate effects and has no repeat-safety contract.
* The caller has no useful time remaining or has cancelled.
* Another layer already owns the same retry policy.
* The expected cost or additional load outweighs likely recovery.
* The dependency is persistently failing and attempts are not helping.

A lower retry count can improve overall availability during overload. Backoff and jitter shape retry traffic; they do not substitute for capacity limits or admission control.

### 47The architecture we derived

| Boundary | Decision |
| --- | --- |
| Caller budget | Is the whole interaction still useful? |
| Repeat-safety contract | May the same operation be attempted again? |
| Retry policy | Is this failure worth another attempt, and how many remain? |
| Backoff and jitter | When should that attempt begin? |
| Per-attempt adapter | How long can it wait, and how does it cancel? |
| Workflow recovery | What happens if the result remains unresolved? |

The strongest part of this design is the contract between boundaries. A polished sleep loop cannot supply missing idempotency, durable state or business failure semantics.

### 48Derive the next pattern

| Observed pressure | Design response |
| --- | --- |
| Remote waiting can exceed usefulness. | Timeout. |
| Some failures disappear. | Retry. |
| A previous attempt may already have committed. | Stable identity and idempotency. |
| Immediate retries add load during failure. | Backoff. |
| Callers retry together. | Jitter. |
| The sequence can consume unlimited resources. | Attempt limits, deadlines and retry budgets. |
| Recent attempts show persistent failure. | Consider temporarily rejecting new calls. |

That final pressure leads to **Circuit Breaker**. Retry spends a limited amount of additional effort because another attempt might succeed. A circuit breaker uses recent failure evidence to temporarily suppress calls. The two policies must agree on what an attempt means and where failure is counted.

Appendix A · complete source

## A bounded retry engine and HTTP adapter

One file, standard JDK APIs, no dependencies and no preview features. The `main` method runs an offline demonstration. The HTTP adapter is an illustrative integration for an explicitly defined server contract.

**Sample contract and practical boundaries**

This example assumes HTTP 200 means a completed authorization, 429/503 can be retried with the same key, and the server atomically deduplicates that key. Other I/O failures stop conservatively. Add the actual API’s business-error decoding, authentication, response-size limits and observability before integration. The example buffers a small response body; streaming needs its own consumption and cancellation policy.

Reuse an application-owned HttpClient across calls. Close it at application shutdown according to the application lifecycle. Do not put a fresh client in a per-attempt try-with-resources block: its close can wait for outstanding work. [[3]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html "Oracle · HttpClient")

Java · integration fragment; example domain, no live endpoint

```
// At application wiring time:
HttpClient client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofMillis(300))
        .build();
var payment = new RetryGuide.PaymentHttp(
        client, URI.create("https://payment.example/authorize"),
        Clock.systemUTC());

// During the logical call: command is loaded with its persisted identity.
String responseJson = retrier.execute(remainingBudget,
        timeout -> payment.authorizeOnce(command, timeout));
```

The future wait covers completion of the String response body. On timeout or interruption, cancellation is requested. That bounds the local wait as scheduling permits; it does not prove the remote operation stopped. [[11]](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Future.html#get(long,java.util.concurrent.TimeUnit) "Oracle · Future")[[12]](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpResponse.BodySubscribers.html#ofString(java.nio.charset.Charset) "Oracle · HttpResponse.BodySubscribers")

Download RetryGuide.java

RetryGuide.java · complete, copyable source

```
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Duration;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public final class RetryGuide {
    private RetryGuide() {}

    // A short, in-process retry policy; longer work belongs in a scheduler.
    public record Config(
            int maxAttempts,
            Duration attemptTimeout,
            Duration minAttemptBudget,
            Duration baseDelay,
            Duration maxDelay) {
        public Config {
            if (maxAttempts < 1) {
                throw new IllegalArgumentException("maxAttempts < 1");
            }
            checkDuration(attemptTimeout);
            checkDuration(minAttemptBudget);
            checkDuration(baseDelay);
            checkDuration(maxDelay);
            if (minAttemptBudget.compareTo(attemptTimeout) > 0
                    || baseDelay.compareTo(maxDelay) > 0) {
                throw new IllegalArgumentException("inconsistent limits");
            }
        }
    }

    // Keep durations <= 1 day so nanosecond arithmetic stays far from overflow.
    private static void checkDuration(Duration value) {
        Objects.requireNonNull(value);
        if (value.isNegative() || value.isZero()
                || value.compareTo(Duration.ofDays(1)) > 0) {
            throw new IllegalArgumentException("duration outside (0, 1 day]");
        }
    }

    @FunctionalInterface
    public interface NanoClock {
        long now(); // monotonic elapsed-time source, e.g. System.nanoTime
    }

    @FunctionalInterface
    public interface Sleeper {
        void sleep(Duration delay) throws InterruptedException;
    }

    @FunctionalInterface
    public interface Jitter {
        long nextLong(long upperExclusive);
    }

    @FunctionalInterface
    public interface Attempt<T> {
        // The adapter must honor this budget and propagate cancellation.
        T call(Duration timeout) throws IOException, InterruptedException;
    }

    // Only the dependency adapter may label a failure as retryable.
    public static final class RetryableFailure extends IOException {
        private static final long serialVersionUID = 1L;
        private final Optional<Duration> retryAfter;

        public RetryableFailure(String reason, Throwable cause,
                                Optional<Duration> retryAfter) {
            super(reason, cause);
            this.retryAfter = Objects.requireNonNull(retryAfter);
            retryAfter.ifPresent(delay -> {
                if (delay.isNegative()) {
                    throw new IllegalArgumentException("negative retryAfter");
                }
            });
        }

        public Optional<Duration> retryAfter() {
            return retryAfter;
        }
    }

    public static final class BudgetExceeded extends IOException {
        private static final long serialVersionUID = 1L;

        public BudgetExceeded(String message, Throwable cause) {
            super(message, cause);
        }
    }

    public static final class Retrier {
        private final Config config;
        private final NanoClock clock;
        private final Sleeper sleeper;
        private final Jitter random;

        public Retrier(Config config, NanoClock clock,
                       Sleeper sleeper, Jitter random) {
            this.config = Objects.requireNonNull(config);
            this.clock = Objects.requireNonNull(clock);
            this.sleeper = Objects.requireNonNull(sleeper);
            this.random = Objects.requireNonNull(random);
        }

        public static Retrier production(Config config) {
            return new Retrier(config, System::nanoTime,
                    delay -> TimeUnit.NANOSECONDS.sleep(delay.toNanos()),
                    bound -> ThreadLocalRandom.current().nextLong(bound));
        }

        // failedAttempt=1 is the first failure; the first window is baseDelay.
        public long windowNanos(int failedAttempt) {
            if (failedAttempt < 1) {
                throw new IllegalArgumentException("failedAttempt < 1");
            }
            long window = config.baseDelay().toNanos();
            long cap = config.maxDelay().toNanos();
            for (int i = 1; i < failedAttempt && window < cap; i++) {
                window = window > cap / 2 ? cap : window * 2;
            }
            return window;
        }

        public <T> T execute(Duration totalBudget, Attempt<T> operation)
                throws IOException, InterruptedException {
            checkDuration(totalBudget);
            Objects.requireNonNull(operation);
            long started = clock.now();
            long total = totalBudget.toNanos();
            RetryableFailure last = null;

            for (int attempt = 1; ; attempt++) {
                // Preserve an existing interrupt flag while stopping work.
                if (Thread.currentThread().isInterrupted()) {
                    throw new InterruptedException("caller cancelled");
                }
                long remaining = total - (clock.now() - started);
                if (remaining < config.minAttemptBudget().toNanos()) {
                    throw new BudgetExceeded("no useful attempt budget", last);
                }
                Duration timeout = Duration.ofNanos(Math.min(
                        config.attemptTimeout().toNanos(), remaining));
                try {
                    return operation.call(timeout);
                } catch (RetryableFailure failure) {
                    last = failure;
                    if (attempt == config.maxAttempts()) {
                        throw failure;
                    }
                    long window = windowNanos(attempt);
                    long sample = random.nextLong(window + 1);
                    if (sample < 0 || sample > window) {
                        throw new IllegalArgumentException("invalid jitter");
                    }
                    Duration delay = Duration.ofNanos(sample);
                    // Treat the server hint as a floor, never jitter below it.
                    if (failure.retryAfter().isPresent()
                            && failure.retryAfter().get().compareTo(delay) > 0) {
                        delay = failure.retryAfter().get();
                    }
                    remaining = total - (clock.now() - started);
                    long reserve = config.minAttemptBudget().toNanos();
                    if (remaining < reserve || delay.compareTo(
                            Duration.ofNanos(remaining - reserve)) > 0) {
                        throw new BudgetExceeded(
                                "retry delay leaves no useful attempt budget",
                                failure);
                    }
                    if (!delay.isZero()) {
                        sleeper.sleep(delay);
                    }
                    // Recheck after sleeping: scheduling may overshoot.
                }
                // Other IOException, RuntimeException and interruption escape.
            }
        }
    }

    // Illustration: an already-serialized, immutable, repeatable request body.
    public record PaymentCommand(String idempotencyKey, String json) {
        public PaymentCommand {
            Objects.requireNonNull(idempotencyKey);
            Objects.requireNonNull(json);
            if (idempotencyKey.isBlank()) {
                throw new IllegalArgumentException("empty idempotency key");
            }
        }
    }

    // Example contract, NOT a universal mapping for arbitrary payment APIs:
    // 200 = final authorization response; 429/503 = retryable with same key.
    // The server must implement atomic deduplication for this command identity.
    public static final class PaymentHttp {
        private final HttpClient client;
        private final URI endpoint;
        private final Clock wallClock;

        public PaymentHttp(HttpClient client, URI endpoint, Clock wallClock) {
            this.client = Objects.requireNonNull(client);
            this.endpoint = Objects.requireNonNull(endpoint);
            this.wallClock = Objects.requireNonNull(wallClock);
        }

        public String authorizeOnce(PaymentCommand command, Duration timeout)
                throws IOException, InterruptedException {
            long started = System.nanoTime();
            long allowance = timeout.toNanos();
            var request = HttpRequest.newBuilder(endpoint)
                    .timeout(timeout)
                    .header("Content-Type", "application/json")
                    .header("Idempotency-Key", command.idempotencyKey())
                    .POST(HttpRequest.BodyPublishers.ofString(
                            command.json(), StandardCharsets.UTF_8))
                    .build();
            var future = client.sendAsync(request,
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            HttpResponse<String> response;
            try {
                long left = allowance - (System.nanoTime() - started);
                if (left <= 0) {
                    throw new TimeoutException("attempt budget elapsed");
                }
                // ofString completes after the whole body is read.
                response = future.get(left, TimeUnit.NANOSECONDS);
            } catch (TimeoutException failure) {
                future.cancel(true); // best effort; never a server rollback
                throw retryable("payment outcome unknown", failure);
            } catch (InterruptedException failure) {
                future.cancel(true);
                throw failure; // do not turn cancellation into retry
            } catch (ExecutionException failure) {
                Throwable cause = failure.getCause();
                if (cause instanceof HttpTimeoutException timeoutFailure) {
                    throw retryable("payment outcome unknown", timeoutFailure);
                }
                // Conservative: unclassified transport failures are not retried.
                if (cause instanceof IOException io) {
                    throw io;
                }
                if (cause instanceof RuntimeException runtime) {
                    throw runtime;
                }
                if (cause instanceof Error error) {
                    throw error;
                }
                throw new IOException("unexpected transport failure", cause);
            }
            int status = response.statusCode();
            if (status == 200) {
                return response.body(); // decode using the actual API contract
            }
            if (status == 429 || status == 503) {
                Optional<Duration> hint = response.headers()
                        .firstValue("Retry-After")
                        .flatMap(value -> retryAfter(value, wallClock));
                throw new RetryableFailure("HTTP " + status, null, hint);
            }
            throw new IOException("non-retryable HTTP status " + status);
        }
    }

    public static RetryableFailure retryable(String reason, Throwable cause) {
        return new RetryableFailure(reason, cause, Optional.empty());
    }

    // Supports delay-seconds and the modern IMF-fixdate HTTP-date form.
    // Legacy HTTP-date formats require a fuller parser at an HTTP boundary.
    public static Optional<Duration> retryAfter(String raw, Clock clock) {
        String value = raw.trim();
        if (value.matches("[0-9]+")) {
            try {
                return Optional.of(Duration.ofSeconds(Long.parseLong(value)));
            } catch (NumberFormatException tooLarge) {
                // Valid, enormous delay: stop this short synchronous retry.
                return Optional.of(Duration.ofSeconds(Long.MAX_VALUE));
            }
        }
        try {
            var instant = ZonedDateTime.parse(value,
                    DateTimeFormatter.RFC_1123_DATE_TIME).toInstant();
            Duration delay = Duration.between(clock.instant(), instant);
            return Optional.of(delay.isNegative() ? Duration.ZERO : delay);
        } catch (DateTimeParseException invalid) {
            return Optional.empty(); // fall back to local backoff
        }
    }

    public static void main(String[] args) throws Exception {
        var config = new Config(3, Duration.ofMillis(700),
                Duration.ofMillis(50), Duration.ofMillis(200),
                Duration.ofSeconds(2));
        int[] calls = {0};
        // Deterministic demonstration: no network and no real sleeping.
        long[] now = {0};
        var retrier = new Retrier(config, () -> now[0],
                delay -> now[0] += delay.toNanos(), bound -> bound / 2);
        String result = retrier.execute(Duration.ofSeconds(3), timeout -> {
            calls[0]++;
            if (calls[0] == 1) {
                throw retryable("temporary failure", null);
            }
            return "authorized";
        });
        System.out.println(result + "; attempts=" + calls[0]);
    }
}
```

Run with JDK 25

```
javac --release 25 RetryGuide.java
java RetryGuide
# Expected: authorized; attempts=2
```

Appendix B · deterministic checks

## Executable checks without real sleeping

Save both Java files in the same directory. The tests exercise the retry mechanism and a simulated idempotency contract. They do not call a payment service.

Download RetryGuideTest.java

RetryGuideTest.java · complete, copyable source

```
import java.io.IOException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public final class RetryGuideTest {
    static int checks;
    static final Duration TOTAL = Duration.ofSeconds(3);
    static RetryGuide.Config config() {
        return new RetryGuide.Config(3, Duration.ofMillis(700),
                Duration.ofMillis(50), Duration.ofMillis(200),
                Duration.ofSeconds(2));
    }
    static final class Rig {
        long now;
        final List<Duration> sleeps = new ArrayList<>();
        final RetryGuide.Retrier retry = new RetryGuide.Retrier(config(),
                () -> now, d -> { sleeps.add(d); now += d.toNanos(); },
                bound -> bound - 1);
    }
    static void check(boolean condition) {
        if (!condition) throw new AssertionError("check " + (checks + 1));
        checks++;
    }
    @FunctionalInterface interface Checked { void run() throws Exception; }
    static <T extends Throwable> T expect(Class<T> type, Checked action)
            throws Exception {
        try { action.run(); }
        catch (Throwable failure) {
            if (!type.isInstance(failure)) throw new AssertionError(failure);
            checks++;
            return type.cast(failure);
        }
        throw new AssertionError("expected " + type.getSimpleName());
    }
    public static void main(String[] args) throws Exception {
        // Transient failure, one delay, then success.
        var recover = new Rig();
        int[] calls = {0};
        String value = recover.retry.execute(TOTAL, timeout -> {
            if (++calls[0] == 1) throw RetryGuide.retryable("temporary", null);
            return "ok";
        });
        check(value.equals("ok") && calls[0] == 2);
        check(recover.sleeps.equals(List.of(Duration.ofMillis(200))));

        // Permanent failures escape unchanged and do not sleep.
        var permanent = new Rig();
        var rejected = new IOException("declined");
        check(expect(IOException.class, () -> permanent.retry.execute(TOTAL,
                t -> { throw rejected; })) == rejected);
        check(permanent.sleeps.isEmpty());

        // Three total attempts, only two waits, final cause retained.
        var exhausted = new Rig();
        calls[0] = 0;
        var unavailable = RetryGuide.retryable("unavailable", null);
        check(expect(RetryGuide.RetryableFailure.class,
                () -> exhausted.retry.execute(TOTAL, timeout -> {
                    calls[0]++;
                    throw unavailable;
                })) == unavailable);
        check(calls[0] == 3 && exhausted.sleeps.size() == 2);

        // A response is lost AFTER the simulated server commits.
        var ambiguous = new Rig();
        var command = new RetryGuide.PaymentCommand("payment-123", "{}");
        List<String> keys = new ArrayList<>();
        Map<String, String> storedResults = new HashMap<>();
        int[] effects = {0};
        String authorization = ambiguous.retry.execute(TOTAL, timeout -> {
            keys.add(command.idempotencyKey());
            String cached = storedResults.get(command.idempotencyKey());
            if (cached != null) return cached;
            effects[0]++;
            storedResults.put(command.idempotencyKey(), "auth-7");
            throw RetryGuide.retryable("lost response", null);
        });
        check(authorization.equals("auth-7") && effects[0] == 1);
        check(keys.equals(List.of("payment-123", "payment-123")));

        // Window grows, caps and cannot wrap around for a huge attempt index.
        var backoff = new Rig();
        check(backoff.retry.windowNanos(1) == Duration.ofMillis(200).toNanos());
        check(backoff.retry.windowNanos(2) == Duration.ofMillis(400).toNanos());
        check(backoff.retry.windowNanos(Integer.MAX_VALUE)
                == Duration.ofSeconds(2).toNanos());

        // A server floor that cannot fit must not be shortened.
        var floor = new Rig();
        expect(RetryGuide.BudgetExceeded.class, () -> floor.retry.execute(
                Duration.ofSeconds(1), timeout -> {
                    throw new RetryGuide.RetryableFailure("throttled", null,
                            Optional.of(Duration.ofSeconds(2)));
                }));
        check(floor.sleeps.isEmpty());
        var honored = new Rig();
        calls[0] = 0;
        honored.retry.execute(TOTAL, timeout -> {
            if (++calls[0] == 1) {
                throw new RetryGuide.RetryableFailure("throttled", null,
                        Optional.of(Duration.ofSeconds(1)));
            }
            return "ok";
        });
        check(honored.sleeps.equals(List.of(Duration.ofSeconds(1))));

        // Per-attempt allowance shrinks to the remaining overall budget.
        var clipped = new Rig();
        clipped.retry.execute(Duration.ofMillis(500), timeout -> {
            check(timeout.equals(Duration.ofMillis(500)));
            return "ok";
        });
        calls[0] = 0;
        expect(RetryGuide.BudgetExceeded.class, () -> clipped.retry.execute(
                Duration.ofMillis(49), timeout -> { calls[0]++; return "bad"; }));
        check(calls[0] == 0);

        // A sleeper can overshoot; recheck before sending another request.
        long[] now = {0};
        var overshoot = new RetryGuide.Retrier(config(), () -> now[0],
                delay -> now[0] += TOTAL.toNanos(), bound -> bound - 1);
        calls[0] = 0;
        expect(RetryGuide.BudgetExceeded.class, () -> overshoot.execute(
                TOTAL, timeout -> { calls[0]++;
                    throw RetryGuide.retryable("temporary", null); }));
        check(calls[0] == 1);

        // Interruption during an attempt or a wait ends the sequence.
        var interrupted = new Rig();
        expect(InterruptedException.class, () -> interrupted.retry.execute(
                TOTAL, timeout -> { throw new InterruptedException(); }));
        check(interrupted.sleeps.isEmpty());
        var interruptedSleep = new RetryGuide.Retrier(config(), () -> 0,
                delay -> { throw new InterruptedException(); }, b -> b - 1);
        expect(InterruptedException.class, () -> interruptedSleep.execute(
                TOTAL, t -> { throw RetryGuide.retryable("temporary", null); }));
        Thread.currentThread().interrupt();
        try {
            expect(InterruptedException.class, () -> new Rig().retry.execute(
                    TOTAL, timeout -> { throw new AssertionError("called"); }));
            check(Thread.currentThread().isInterrupted());
        } finally { Thread.interrupted(); }

        // Retry-After seconds, date, past date, invalid value and huge integer.
        Clock clock = Clock.fixed(Instant.parse("2026-09-02T12:00:00Z"),
                ZoneOffset.UTC);
        check(RetryGuide.retryAfter("2", clock).orElseThrow()
                .equals(Duration.ofSeconds(2)));
        check(RetryGuide.retryAfter("Wed, 02 Sep 2026 12:00:03 GMT", clock)
                .orElseThrow().equals(Duration.ofSeconds(3)));
        check(RetryGuide.retryAfter("Wed, 02 Sep 2026 11:59:00 GMT", clock)
                .orElseThrow().isZero());
        check(RetryGuide.retryAfter("garbage", clock).isEmpty());
        var huge = RetryGuide.retryAfter("99999999999999999999999", clock);
        expect(RetryGuide.BudgetExceeded.class, () -> new Rig().retry.execute(
                TOTAL, t -> { throw new RetryGuide.RetryableFailure(
                        "long server delay", null, huge); }));
        System.out.println("Passed " + checks + " deterministic checks");
    }
}
```

Run with JDK 25

```
javac --release 25 RetryGuide.java RetryGuideTest.java
java RetryGuideTest
# Expected: Passed 31 deterministic checks
```

**Validation scope**

Both complete source files compiled with `--release 17 -Xlint:all` on the available OpenJDK 17 runtime. The demo ran, and all 31 deterministic checks passed. The used APIs were checked against Oracle’s Java 25 documentation. ⚠️ A Java 25 runtime was not available here, so execution on Java 25 has not been directly verified.

These checks validate the tutorial engine. They do not establish real payment-provider semantics, production timing guarantees or server-side idempotency.

Reference notes

## Official sources

Verified 2 September 2026. The first-principles progression follows the supplied lesson. The code and worked scenarios are original teaching examples; numerical settings are illustrative.

1. [Oracle · HttpRequest.Builder](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html#timeout(java.time.Duration))Request timeout and its unset behavior.https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html#timeout(java.time.Duration)
2. [Oracle · HttpClient.Builder](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.Builder.html#connectTimeout(java.time.Duration))Connection timeout and connection reuse.https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.Builder.html#connectTimeout(java.time.Duration)
3. [Oracle · HttpClient](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html)Asynchronous responses, best-effort cancellation and lifecycle.https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html
4. [Microsoft · Retry pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry)Transient faults, idempotency, nested retries and policy ownership.https://learn.microsoft.com/en-us/azure/architecture/patterns/retry
5. [Microsoft · Retry storm antipattern](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/retry-storm/)Load amplification, backoff and server retry guidance.https://learn.microsoft.com/en-us/azure/architecture/antipatterns/retry-storm/
6. [AWS · Retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)Bounded exponential backoff, full jitter, attempt counts and retry quotas.https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
7. [RFC 9110 · HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after)Retry-After syntax and HTTP idempotency semantics.https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after
8. [Stripe · Idempotent requests](https://docs.stripe.com/api/idempotent_requests)A concrete provider example of idempotency keys; verify your own provider contract.https://docs.stripe.com/api/idempotent\_requests
9. [Oracle · System.nanoTime](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime())Elapsed-time measurement and subtraction-based comparisons.https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime()
10. [Oracle · Thread](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html)Sleep and interruption semantics.https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html
11. [Oracle · Future](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Future.html#get(long,java.util.concurrent.TimeUnit))Timed waits and interruption.https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Future.html#get(long,java.util.concurrent.TimeUnit)
12. [Oracle · HttpResponse.BodySubscribers](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpResponse.BodySubscribers.html#ofString(java.nio.charset.Charset))String body completion after the whole response has been read.https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpResponse.BodySubscribers.html#ofString(java.nio.charset.Charset)
13. [Oracle · ThreadLocalRandom](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ThreadLocalRandom.html#nextLong(long))Exclusive upper bound for random long values.https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ThreadLocalRandom.html#nextLong(long)

DP · Lesson 23 · Timeout → Retry → Exponential Backoff → Jitter
Next pressure: persistent failure → Circuit Breaker.