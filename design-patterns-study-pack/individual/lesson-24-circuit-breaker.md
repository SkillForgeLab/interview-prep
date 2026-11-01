DP · Distributed systems · Pattern 24

# 24. Circuit Breaker

When recent failures tell us to stop trying.

First principles → state machine → Java → composition → testing

Retry asks whether another attempt might help. A circuit breaker uses recent evidence to decide whether to admit that attempt at all.

Start with a retrying Payment client. Change the failure from transient to persistent. Derive each mechanism from the problem that the previous design leaves unresolved.

Print / Save as PDF[Complete Java example](#appendix-a)

Offline-ready HTML. Light theme. Use A4 or Letter, 100% scale, and turn browser headers and footers off. All lesson text and code remain visible with JavaScript disabled.

## Reading path

1. [Why retry stops helping](#part-01)Steps 1–7
2. [Derive the state machine](#part-02)Steps 8–12
3. [Evidence and failure semantics](#part-03)Steps 13–20
4. [Recovery, concurrency and scope](#part-04)Steps 21–28
5. [Compose the controls](#part-05)Steps 29–35
6. [Business truth and implementation](#part-06)Steps 36–47
7. [Test observable guarantees](#part-07)Steps 48–57
8. [Operate it and move forward](#part-08)Steps 58–62
9. [Complete teaching implementation](#appendix-a)Appendix A · source and deterministic checks
10. [Resilience4j integration](#appendix-b)Appendix B · source and Maven setup
11. [Official sources and application checklist](#references)Reference notes

Part 01 · Steps 1–7

## Why retry stops helping

### 01.Start with the retrying client

Checkout calls Payment through a gateway. A timeout followed by a successful second attempt is exactly the situation where a bounded retry can help.

java

```
// Conceptual fragment: RetryPolicy is from the previous lesson.
return retryPolicy.execute(() -> delegate.authorize(command));
```

Each retry reuses the same command and idempotency key. The application asks for one authorization; the policy may make several attempts to obtain its result.

**Working assumption:** another attempt has a reasonable chance of succeeding within the caller’s remaining deadline.

### 02.Now Payment stays broken

Change one condition: Payment will be unavailable for the next ten minutes. Suppose 1,000 checkouts arrive and each performs three total attempts.

1,000 logical requests × 3 attempts = 3,000 dependency calls

This is an illustrative upper bound if every request exhausts all three attempts. “Three retries” would mean four attempts and up to 4,000 calls. Count attempts explicitly.

Those repeated calls add traffic, connection pressure and work to an already unhealthy dependency.

### 03.Failure amplification

The damage can spread upstream. Slow Payment attempts keep Checkout work in flight; queues and retained request state grow; Checkout loses capacity for other work. Its callers then experience their own delays and retries.

Timeouts eventually stop individual waits, but many requests may accumulate before their timeouts expire. We need a way to stop admitting predictably unsuccessful work earlier.

### 04.What evidence are we ignoring?

After a sequence of dependency failures, a new checkout should not have to behave as if it knows nothing about recent outcomes.

**Question:** can the caller remember enough evidence to decide that calling Payment right now is probably wasteful?

This knowledge is local and imperfect. It is evidence for an admission decision, not proof of global service health.

### 05.The smallest useful idea

Keep a consecutive-failure counter. Reset it on a measured success. Reject new calls when it reaches a threshold.

java

```
// Intentionally incomplete sketch: single-threaded, no recovery.
if (consecutiveFailures >= 5) {
    throw new CircuitOpenException();
}
```

The key change happens before the remote call: once the policy rejects permission, the dependency is never invoked for that attempt.

The early sketches illustrate one design pressure at a time. They are not independent, production-ready classes. The complete dependency-free listing is in [Appendix A](#appendix-a).

### 06.Why failing immediately helps

A doomed three-second attempt consumes three seconds of latency plus whatever resources remain associated with that work. Rejecting admission avoids the remote wait and most of that resource cost.

Payment receives less unwanted traffic; Checkout preserves capacity. Recovery still depends on the underlying fault being repaired. Opening the breaker does not repair Payment.

[[1: pattern and motivation]](#ref-1)

### 07.Permanent blocking cannot be the policy

If five failures cause permanent rejection, Payment can recover while Checkout continues refusing every call. We have protected the system by making it permanently unavailable.

**New requirement:** pause for a bounded interval, then collect new evidence about recovery.

[Back to contents](#contents)

Part 02 · Steps 8–12

## Derive the state machine

### 08.Derive three states

| State | Admission rule | Purpose |
| --- | --- | --- |
| CLOSED | Ordinary calls pass. | Collect evidence during normal operation. |
| OPEN | New calls are rejected. | Pause attempts while the dependency may be unhealthy. |
| HALF\_OPEN | Only a limited set of probes passes. | Test recovery before restoring ordinary traffic. |

The electrical analogy explains the names: a closed circuit permits flow; an open circuit interrupts it.

[[1: three-state model]](#ref-1)

### 09.Make the transition rules explicit

| Current state | Event | Next state |
| --- | --- | --- |
| CLOSED | Recorded failures reach the chosen threshold. | OPEN |
| OPEN | Recovery delay has elapsed and a caller requests permission. | HALF\_OPEN |
| HALF\_OPEN | Enough measured probes succeed. | CLOSED |
| HALF\_OPEN | A measured probe fails in our strict teaching policy. | OPEN |

This guide’s educational implementation transitions lazily: elapsed time alone does not execute code or send a probe. The next caller discovers that the delay has elapsed. Libraries can offer scheduled transitions too.

#### Try the state machine

Teaching policy: 3 consecutive failures, a 30-second pause, and 2 successful probes. Calls complete sequentially in this simulation.

CLOSEDOPENHALF\_OPEN

CLOSED · 0 consecutive failures · time 0s

Call → successCall → failureCall → ignoredAdvance 30 secondsReset

Send three failing calls to open the circuit.

**Worked trace:** fail → fail → fail → OPEN; calls before 30 seconds are rejected; advance 30 seconds; successful probe → HALF\_OPEN; second successful probe → CLOSED.

### 10.First implementation: state plus evidence

The mechanism needs a state, a failure count, an opening time, and policy parameters. Use an elapsed-time source for the waiting interval.

java

```
enum State { CLOSED, OPEN, HALF_OPEN }

private State state = State.CLOSED;
private int consecutiveFailures;
private long openedAt;
private final long openNanos;
private final LongSupplier ticker; // System::nanoTime in real use
```

The original wall-clock sketch is easy to read, but a wall-clock adjustment should not change a recovery interval. Java’s `System.nanoTime()` is intended for elapsed time. Compare differences, not absolute timestamps.

[[3: Java 25 elapsed-time API]](#ref-3)

### 11.Permission comes before execution

The call lifecycle has three responsibilities: acquire permission, execute the operation, then record the outcome. Keep the remote call outside the lock that protects breaker state.

java

```
Permit permit = acquire();
Outcome outcome = Outcome.IGNORE;
try {
    T result = operation.call();
    outcome = Outcome.SUCCESS;
    return result;
} finally {
    finish(permit, outcome);
}
```

This fragment only shows the success path and cleanup. Appendix A adds exception classification and cancellation. Rejection happens before the `try`, so a rejected attempt does not become another dependency failure.

### 12.Wrap the dependency

The application should keep depending on `PaymentGateway`. The wrapper owns admission and accounting; the adapter owns transport and response interpretation.

java

```
@Override
public Authorization authorize(AuthorizePayment command) throws Exception {
    return breaker.execute(() -> delegate.authorize(command));
}
```

This is a proxy/decorator: callers see the same port while the wrapper adds operational behavior. Full records, interface and wrapper are included in Appendix A.

[Back to contents](#contents)

Part 03 · Steps 13–20

## Evidence and failure semantics

### 13.Closed means observe while allowing

In CLOSED, admitted calls run normally. Under a consecutive-failure policy, a measured success resets the counter; a measured failure increments it; an ignored result changes neither.

With concurrency, “consecutive” means the order in which completions are recorded under the lock. It is not necessarily request-start order. State the meaning in tests and metrics.

### 14.One failure is usually too little evidence

One timeout after a long run of successful calls may be a transient fault. Opening immediately could reject calls that would have succeeded.

A threshold is a tradeoff between rejecting useful work and continuing harmful work. Five failures is a teaching parameter, not a generally correct setting. Some failures can justify immediate opening, but that requires an explicit policy.

### 15.Failure count versus failure rate

Alternating success and failure never reaches five consecutive failures, even though half the calls fail. A rate-based policy can detect this condition.

failure rate = measured failures ÷ measured calls × 100%

For a window with 60 successes and 40 failures, the rate is 40%. A policy might open at 50%, but only after at least 20 measured calls.

A count window describes the last N measured completions. A time window describes a recent interval. The choice changes how quickly old evidence expires.

### 16.Minimum samples prevent premature decisions

The first failed call gives a numerical failure rate of 100%, but one observation is weak evidence for a broad rejection policy. A minimum sample count delays rate-based decisions until the chosen amount of evidence exists.

It does not guarantee statistical confidence. Low traffic, correlated failures and changing conditions still matter. At low volume, waiting for 20 calls can also delay protection.

### 17.Slow success can still be operationally harmful

Suppose authorization normally takes 200 milliseconds but now takes 15 seconds. A technically successful response can still tie up unacceptable amounts of caller capacity.

A slow-call policy records whether completed calls exceeded a duration threshold. It can open on the proportion of slow calls as well as on failures. The same call may be both slow and failed.

**Timing matters:** slow-call measurement is not a timeout. A breaker usually learns the duration when the call completes; it does not make a hung call return.

[[2: rates and measurement]](#ref-2)

### 18.Open rejects new permission

When OPEN, the breaker returns a distinct admission error without invoking the protected operation for that attempt. In the teaching code it is `CircuitOpenException`; Resilience4j uses `CallNotPermittedException`.

Calls admitted before opening can still be running, and can even reach the transport after the transition. Opening does not cancel them. “No calls while open” is only accurate for newly denied admissions.

### 19.Preserve failure semantics

| Observed result | What it establishes | What it does not establish |
| --- | --- | --- |
| Payment declined | Payment returned a business rejection. | Infrastructure is unhealthy. |
| Timeout | The caller did not obtain a result in time. | Payment definitely performed no side effect. |
| Circuit open | This attempt was denied before its delegate ran. | Earlier attempts did not already authorize payment. |

The last distinction matters after retries. An open-circuit rejection on attempt 3 cannot erase an ambiguous timeout on attempt 1. Preserve the logical request’s outcome uncertainty and its idempotency key.

### 20.Saga behavior with an open circuit

A workflow can choose to enter `WAITING_FOR_PAYMENT`, persist a retry time, and return a truthful pending or unavailable state. That is a business policy layered above the breaker.

The breaker itself does not persist, queue or replay commands. Durable resumption needs the workflow’s own storage and scheduling. If an earlier attempt may have succeeded, reconcile using the same operation identity before treating the order as declined or safely compensating.

[Back to contents](#contents)

Part 04 · Steps 21–28

## Recovery, concurrency and scope

### 21.Why half-open exists

After the recovery delay, closing immediately would let ordinary traffic resume all at once. A recovering dependency may only be ready for a small amount of work.

Half-open makes recovery an evidence-gathering phase. Allow a small number of representative operations, observe them, then decide whether to close or pause again. No built-in queue is implied: excess callers can be rejected.

### 22.Choose the probe policy deliberately

The teaching policy requires every measured probe in a small batch to succeed; any measured failure reopens immediately. A successful business decline can count as a healthy response from Payment.

Library semantics can differ. Resilience4j evaluates failure and slow-call rates for the half-open sample, so one failed probe need not reopen immediately at every configuration. Keep tests aligned with the actual implementation.

[[2: half-open semantics]](#ref-2)

### 23.The first implementation has concurrency bugs

If many threads see HALF\_OPEN and all pass, “probe mode” can become an uncontrolled burst. A volatile state field alone cannot make a check-and-decrement operation atomic.

There is another race: call A is admitted in CLOSED; call B fails and opens the circuit; then A completes successfully. A naïve `recordSuccess()` closes the breaker and destroys the new decision.

**Required invariants:** allocate probe permissions atomically, and associate each completion with the state generation that admitted it.

### 24.Use a quota and generation-bearing permits

Appendix A guards state changes and probe accounting with short `synchronized` methods. Each permitted call carries the current generation number. Every state transition increments the generation.

java

```
private record Permit(long generation) {}

// Inside synchronized completion accounting:
if (permit.generation() != generation) {
    return; // Ignore old evidence for this newer generation.
}
```

Half-open admits a total batch of measured probes, not a continuously refilled concurrency pool. Successful completions consume the batch; ignored outcomes release their slot for a replacement. Close only after the required number of measured successes.

The remote operation executes outside the monitor. This avoids serializing all I/O behind one slow call.

### 25.Classify health evidence, not exception ancestry

| Outcome | Teaching treatment | Reason |
| --- | --- | --- |
| Authorization approved or declined | SUCCESS | The dependency completed a valid business operation. |
| Transport timeout, connection failure, mapped unavailable response | FAILURE | Evidence that this dependency call could not complete normally. |
| Local validation or caller cancellation | IGNORE | Insufficient evidence about dependency health. |
| HTTP 429, 401, or 404 | Contract-dependent | Scope and meaning may be tenant-, credential- or operation-specific. |

A Java `RuntimeException` does not automatically imply an unhealthy dependency. Conversely, the HTTP client may return a 503 as a normal response object unless your adapter maps it into the failure model.

### 26.Keep the boundary explicit

The adapter translates transport behavior into a stable contract. The resilience policy decides how that contract updates health evidence.

**Ignored and successful are different.** Ignored outcomes are omitted from the measured sample. A measured success can lower a failure rate and can satisfy a recovery probe. Returning a real decline as a domain value preserves that useful distinction.

In the library example, only mapped `IOException` failures count as infrastructure failures. Other thrown outcomes are ignored and still propagate. That is a declared adapter contract, not a general rule for every Java client.

### 27.One breaker per failure domain

If Payment, Inventory and Shipping use one shared breaker, Payment failures can suppress healthy Inventory and Shipping calls. The health boundary is too broad.

Share a breaker among calls that should share admission knowledge. Separate independent dependencies. Reuse each instance across requests; constructing a new breaker for every call prevents useful history from accumulating.

### 28.One service may need several breakers

Authorize, Refund and Fraud Lookup may fail independently. Regions, hosts, shards or tenant quotas can also define different failure domains.

Too broad a scope blocks healthy capacity. Too narrow a scope fragments traffic into samples that may never become informative, and increases state and metric cardinality. Choose a boundary supported by the dependency’s architecture and observed failure modes.

[Back to contents](#contents)

Part 05 · Steps 29–35

## Compose the controls

### 29.Retry and circuit breaker answer different questions

| Mechanism | Decision |
| --- | --- |
| Retry | Is another attempt safe and useful within the remaining budget? |
| Circuit breaker | Should this call be admitted given recent dependency evidence? |

They can cooperate. A retry policy must recognize an admission rejection and stop immediate retries through the same open breaker. Repeatedly catching “circuit open” and sleeping within a short user request adds latency without testing Payment.

### 30.Retry outside the breaker: measure attempts

`Retry(Breaker(TimedHttp))` means every attempt asks for permission. Three failed attempts can contribute three failures. If the breaker opens after attempt 2, attempt 3 is denied before reaching HTTP.

This observes dependency attempts directly. It also means one logical request can contribute several correlated observations. Configure your window and threshold with that fact in mind.

java

```
// Conceptual composition; RetryPolicy owns safe retry rules.
retry.execute(() -> breaker.execute(() -> timedHttp.authorize(command)));
```

### 31.Breaker outside retry: measure logical calls

`Breaker(Retry(TimedHttp))` makes one admission decision for the whole retry sequence. The breaker records the final logical result, and measured duration includes attempts plus backoff.

If another request opens the breaker while this sequence is running, already-admitted retries can continue unless they consult another admission check. In half-open, five logical probes can create more than five HTTP attempts.

java

```
// Conceptual composition with one breaker observation per sequence.
breaker.execute(() -> retry.execute(() -> timedHttp.authorize(command)));
```

### 32.Write down the scope before wiring wrappers

| Property | Retry outside breaker | Breaker outside retry |
| --- | --- | --- |
| One measured call | One admitted attempt | One retry sequence |
| Half-open permission bounds | Attempts | Logical sequences; attempts can multiply |
| Latency measured by breaker | Attempt duration | Attempts plus retry delays |
| Recheck between retries | Yes | No, unless explicitly implemented |

Both still need one stable idempotency key, a total caller deadline, attempt limits, and bounded attempts. The complete library example wraps one already-timed adapter call; adding retry is a separate composition decision.

### 33.A breaker still needs a timeout

A call that never returns produces no completed failure or slow-call measurement. The breaker cannot use an outcome it has not received.

java

```
// Java 25 API fragment. Also enforce the caller's total deadline.
HttpRequest request = HttpRequest.newBuilder(paymentUri)
        .timeout(Duration.ofSeconds(3))
        .header("Idempotency-Key", command.idempotencyKey())
        .POST(HttpRequest.BodyPublishers.ofString(payload))
        .build();
```

This assumes the provider supports that header and idempotency contract. Request timeout and connection timeout address different concerns. Streaming body consumption can need additional bounds. A timeout does not prove a remote authorization was rolled back.

[[4: Java 25 request timeout]](#ref-4)

### 34.A breaker still needs sensible retry policy

A transient failure may be worth another attempt even while recent health evidence remains good. Bounded retry, backoff and jitter address that case.

A retry remains conditional: repeat-safe operation, retryable failure, available attempt budget, and enough remaining time. Caller interruption is cancellation information. Propagate it or restore interrupt status when translating it; do not turn it into an endless retry loop.

### 35.A breaker does not impose a resource limit

Five hundred calls may enter while CLOSED before enough completed failures arrive to open it. A sliding window of 100 measurements is not a limit of 100 concurrent calls.

Virtual threads do not change that admission fact. Java’s virtual-thread-per-task executor starts a thread per task; it does not provide a fixed dependency concurrency cap. Connections, memory, downstream capacity and queues still need deliberate bounds.

This creates the next requirement: a bulkhead that limits how much capacity one dependency can occupy.

[[5: Java 25 virtual-thread executor]](#ref-5)

[Back to contents](#contents)

Part 06 · Steps 36–47

## Business truth and implementation

### 36.Fallback is a business decision

When Payment is unavailable, returning a fabricated authorization would corrupt business truth. A useful fallback must state what actually happened.

For an optional recommendation read, cached results might meet the product contract. For authorization, pending, unavailable or durable deferral may be appropriate. Decide this with the business workflow, not inside a generic breaker mechanism.

### 37.Valid fallbacks have explicit conditions

| Fallback | Condition to establish |
| --- | --- |
| Cached or stale data | Its age and limitations are acceptable for this operation. |
| Omit an optional feature | The product can still satisfy its essential promise. |
| Alternate provider | Failover is safe, including ambiguous prior effects. |
| Queue for later | The work is durably stored and eventual execution is acceptable. |
| Temporarily unavailable | The caller gets a truthful, actionable outcome. |

For payments, switching providers after a timeout can duplicate a charge: an idempotency key accepted by provider A is not automatically deduplicated by provider B.

### 38.Fallback must remain observable

A page may return 200 OK while its recommendation dependency has been unavailable for hours. Overall HTTP success does not establish primary dependency success.

Separate primary success, fallback success, admission rejection and final business outcome. Put fallback outside the breaker’s measured primary call when the goal is to observe primary health; otherwise a successful fallback can hide the failure from the breaker itself.

### 39.Choose thresholds from the cost of being wrong

Ask how much harmful work can accumulate before detection, and how much useful work a false opening would reject. Consider volume, normal failure rate, latency, correlated retry attempts, and sample freshness.

A low-volume dependency may need different settings from one receiving tens of thousands of calls per second. Load tests and incident traces should challenge the chosen parameters. The numbers in this guide are examples.

### 40.Choose recovery timing from observed behavior

A short pause can cause repeated failed probes and rapid state changes. A long pause can continue rejecting requests after the dependency has recovered.

Also bound probe duration. If a half-open batch never finishes, the policy can remain stuck unless calls time out or a maximum half-open residence time returns it to OPEN. At fleet scale, simultaneous probe schedules can add up; consider timing variation and downstream capacity.

### 41.Shared within a process does not mean global

Checkout instances can independently be OPEN, CLOSED and HALF\_OPEN because they have different local observations. This does not automatically indicate a bug.

With 100 instances and five probes per instance, the fleet could admit 500 probes. A local quota is not a fleet-wide quota. Distributed coordination introduces its own availability and consistency costs; use it only for a concrete requirement.

### 42.Separate operational and domain state

| Owner | State it owns |
| --- | --- |
| Order | Business facts such as placed, cancelled or fulfilled. |
| Checkout saga | Workflow progress, pending payment and durable resumption. |
| Payment breaker | Recent dependency evidence and admission mode. |

A transient `paymentCircuitOpen` field does not belong on the Order aggregate. The workflow may persist a payment-unavailable event because it affects business progress; that does not turn the breaker’s internal state into domain truth.

### 43.The breaker fits the proxy shape

The same `PaymentGateway` port can be implemented by an HTTP adapter, a circuit-breaking wrapper, a retrying wrapper and a metering wrapper. Each adds one policy while delegating the business operation.

Dependency inversion remains intact: application code depends on the port. Infrastructure implements it. The place that assembles the wrappers determines the operational semantics.

### 44.The composition root owns the ordering

The source lesson chose one breaker around the complete retry sequence. Keep that choice visible when assembling dependencies.

java

```
// Wiring sketch; these adapters belong to the surrounding application.
PaymentGateway http = new HttpPaymentGateway(httpClient, paymentConfig);
PaymentGateway timed = new TimeoutPaymentGateway(http, timeoutPolicy);
PaymentGateway retried = new RetryingPaymentGateway(timed, retryPolicy);
PaymentGateway protectedGateway =
        new CircuitBreakingPaymentGateway(retried, paymentBreaker);
```

The application receives `protectedGateway` through its `PaymentGateway` constructor parameter. Appendix B supplies a complete smaller composition with a real library API and a fake delegate; it does not invent an HTTP contract for Payment.

### 45.Separate shared mechanics from specific policy

Copying a custom failure counter into Payment, Inventory and Shipping multiplies the places where a race or classification bug must be fixed.

Share state-machine mechanics, timing and observability infrastructure. Configure identity, thresholds, health classification and fallback according to each dependency’s contract. Reusing implementation code does not require sharing one mutable breaker instance across independent backends.

### 46.What the teaching implementation does and omits

Appendix A handles atomic admission, a bounded measured probe batch, late completions, elapsed time, ignored outcomes and interruption cleanup. It deliberately uses a consecutive-failure policy.

It omits sliding windows, slow-call metrics, events, operational overrides, automatic transitions and a maximum half-open residence time. It is synchronous; returning a `CompletableFuture` would measure future creation rather than its eventual result.

For an application, a maintained resilience library can supply these mechanics. The teaching implementation exists to make their purpose understandable.

### 47.A concrete Resilience4j example

Appendix B pins `resilience4j-circuitbreaker:2.3.0` for reproducibility and includes imports, domain records, the gateway contract and a runnable fake. The release exists in the project’s official history; it is not presented as the latest release.

java

```
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
        .slidingWindowSize(100)
        .minimumNumberOfCalls(20)
        .failureRateThreshold(50.0f)
        .waitDurationInOpenState(Duration.ofSeconds(30))
        .permittedNumberOfCallsInHalfOpenState(5)
        .build();
```

The full example also defines slow-call behavior, ignored exceptions, and a maximum half-open wait. Configuration values require workload validation.

[[2: configuration and decoration]](#ref-2) [[6: official release history]](#ref-6)

[Back to contents](#contents)

Part 07 · Steps 48–57

## Test observable guarantees

### 48.Test 1: CLOSED really calls the dependency

Use a controllable ticker for breaker time and a fake delegate with an invocation counter. Start CLOSED, execute one call, and assert that the delegate was invoked exactly once and its result reached the caller.

Do not sleep for the open duration. Advance the fake ticker. Appendix A uses `AtomicLong` and `Duration.toNanos()` so tests control elapsed time explicitly.

### 49.Test 2: the threshold opens the circuit

Configure three consecutive failures. After two measured failures, assert CLOSED. After the third, assert OPEN. Also verify that a success between failures resets this particular counter.

Then attempt another call and assert the invocation count does not increase. A state assertion alone cannot prove the dependency was protected.

### 50.Test 3: business rejection does not trip it

Return many real declines as `Authorization(false, "DECLINED")`. Assert the caller still receives declines, the dependency is called, and the breaker remains CLOSED.

If your contract represents declines as exceptions, decide whether they are measured successes or ignored outcomes. Add a half-open test: that choice determines whether a decline can establish recovery.

### 51.Test 4: OPEN fails before calling

With the breaker already OPEN, call through the same wrapper the application uses. Assert the admission exception and an unchanged delegate count.

Verify that rejected calls are not added to the dependency-failure sample and do not restart the open interval. Testing “fast” by a tiny wall-clock threshold is fragile; prove the remote work was skipped.

### 52.Test 5: recovery begins at the time boundary

Open at elapsed time T with a 30-second interval. At T + 29 seconds, assert rejection. At T + 30 seconds, the next admitted call should be a probe.

For a lazy implementation, reading `state()` before requesting permission may still return OPEN. Use two required successes and complete one probe, or hold a probe in flight, to observe HALF\_OPEN without immediately closing it.

### 53.Test 6: enough probes close the circuit

Require three measured successful probes. Complete two and assert HALF\_OPEN. Complete the third and assert CLOSED. Verify the next ordinary call passes and the relevant closed-state evidence has reset.

An ignored probe must not count as a success. In the teaching policy it releases a slot for another measured probe.

### 54.Test 7: a failed probe starts a fresh pause

After opening and advancing time, make a probe fail. Assert OPEN, then attempt another call before the new recovery interval expires and assert rejection.

Testing only the state misses a subtle bug: reusing the old opening timestamp could immediately allow another half-open cycle. The failed probe must establish the new opening time.

### 55.Test 8: probe admission under concurrency

Hold the permitted probes inside a fake dependency using latches while additional callers compete for admission. Assert that only the quota reaches the delegate and excess calls are rejected.

Keep probes blocked until competing admission attempts finish. If probes complete and the circuit closes during the test, later ordinary calls are valid and an “at most five calls forever” assertion would be wrong.

Also test a late CLOSED-era success after another call opens the breaker. Appendix A verifies that it cannot close the newer state.

### 56.Test 9: the actual sliding-window policy

For a library breaker, configure a minimum of 10 measured calls and a 50% threshold. Three failures in four calls must not open it because the minimum has not been reached.

Continue to six failures in ten measured calls: it must open. Add an exact-boundary case of five in ten, because the configured comparison is “greater than or equal.” Test window eviction and ignored-outcome exclusion separately.

The consecutive-failure demo does not implement a sliding window; run these checks against the actual library policy.

### 57.Test 10: fallback preserves truth

For an optional read, open the breaker and assert that the primary is untouched, the cache is used, and fallback usage is observable.

For Payment, assert an explicit unavailable or pending workflow result. If deferral is selected, verify durable scheduling and stable operation identity. Assert that no authorization is invented and that an earlier ambiguous attempt remains eligible for reconciliation.

[Back to contents](#contents)

Part 08 · Steps 58–62

## Operate it and move forward

### 58.Make the control loop observable

| Signal | Question it helps answer |
| --- | --- |
| State, transitions and time OPEN | When did the policy begin suppressing calls, and for how long? |
| Allowed and rejected calls | How much work reached or was kept from the dependency? |
| Measured failures, slow calls, sample size | What evidence caused the decision? |
| Half-open admissions and outcomes | Is recovery making progress? |
| Primary, fallback and final business outcomes | Is apparent success hiding degradation? |

Include breaker identity and instance context. Keep metric labels bounded; avoid request IDs or arbitrary customer IDs as metric dimensions. Traces can connect logical requests to individual attempts.

### 59.Breaker state is not a universal health check

OPEN means this caller’s observations triggered this policy. A regional network issue, tenant-specific throttling or bad caller credentials can explain the evidence without the whole service being down.

Do not automatically equate OPEN with “restart this instance” or “the dependency is dead everywhere.” Correlate it with transport errors, dependency telemetry and the affected failure domain.

### 60.When a breaker adds little value

Do not wrap every local method mechanically. Ask whether repeated dependency attempts threaten caller capacity and whether admission suppression is acceptable.

A local in-memory operation usually lacks the remote failure pressure that motivated this pattern. Bounded retry, durable messaging or platform isolation may already meet the requirement. But messaging by itself does not protect a consumer making synchronous downstream calls; inspect the actual boundary.

Avoid duplicated policy layers whose combined behavior you cannot explain or observe.

### 61.The failure-control stack so far

| Mechanism | Question |
| --- | --- |
| Timeout | How long may one attempt consume? |
| Total deadline | How long may the complete logical operation consume? |
| Retry | Should another attempt be made? |
| Backoff | How long should the caller wait before another attempt? |
| Jitter | How do many callers avoid retrying together? |
| Idempotency | How are repeated effects prevented or deduplicated? |
| Circuit breaker | Should this dependency call be admitted now? |
| Bulkhead | How much concurrent capacity may this dependency consume? |

These are different decisions. Wrapper order determines which outcomes and durations each mechanism observes.

### 62.The design pressure that leads to Bulkhead

We began with a remote call that could hang, which required a timeout. Transient failure made bounded retry useful. Repeated side effects required idempotency. Retry load required backoff and jitter. Persistent failure required admission control informed by recent outcomes.

The circuit breaker now learns and temporarily stops calls. But it learns from calls that were already admitted. A large burst can occupy Checkout’s capacity before that evidence exists.

**Next: 25. Bulkhead — failure and resource isolation.**

Payment may be slow, but it should have an explicit limit on the share of Checkout’s capacity it can consume.

[Back to contents](#contents)

Appendix A

## Complete Java teaching implementation

This single source file uses standard APIs available in Java 25, with no preview features and no external libraries. Save it as `CircuitBreakerDemo.java`. The download button embeds the same source in this HTML.

Download Java demo

shell

```
javac --release 25 CircuitBreakerDemo.java
java CircuitBreakerDemo
```

Expected output on a successful run:

expected output

```
All deterministic breaker checks passed.
```

**Policy boundary.** The delegate must complete or have an effective timeout. This breaker does not interrupt it. Ignored probes can be replaced, so total attempts can exceed the measured probe count; concurrent outstanding probes remain bounded. A hanging or permanently unmeasurable probe stream needs an additional half-open residence limit.

The classifier must be quick, deterministic and non-throwing. Unknown exceptions are propagated and ignored for dependency health. Production use can replace the fake ticker with `System::nanoTime`.

Validation status: Java 25 API references were checked. No working Java 25 compiler/runtime is available in this session, so the Java listings and expected output are not represented as locally compiled or executed.

CircuitBreakerDemo.java · lines 1–38

```
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.function.LongSupplier;

/** Educational synchronous breaker. No external dependencies or preview APIs. */
public final class CircuitBreakerDemo {
    enum State { CLOSED, OPEN, HALF_OPEN }
    enum Outcome { SUCCESS, FAILURE, IGNORE }

    static final class CircuitOpenException extends RuntimeException {
        CircuitOpenException() { super("Dependency call not permitted"); }
    }

    static final class DependencyUnavailable extends RuntimeException {}
    static final class LocalValidationException extends RuntimeException {}
    record Authorization(boolean approved, String reason) {}
    record AuthorizePayment(String idempotencyKey) {}

    @FunctionalInterface
    interface PaymentGateway {
        Authorization authorize(AuthorizePayment command) throws Exception;
    }

    static final class Breaker {
        private final int failureThreshold;
        private final int probeLimit;
        private final long openNanos;
        private final LongSupplier ticker;
        private final Function<Exception, Outcome> classifier;
        private State state = State.CLOSED;
        private int consecutiveFailures;
```

CircuitBreakerDemo.java · lines 39–76

```
private int admittedProbes;
        private int successfulProbes;
        private long openedAt;
        private long generation;

        private record Permit(long generation) {}

        Breaker(int failureThreshold, Duration openDuration, int probeLimit,
                LongSupplier ticker, Function<Exception, Outcome> classifier) {
            if (failureThreshold < 1 || probeLimit < 1) {
                throw new IllegalArgumentException("Counts must be positive");
            }
            this.failureThreshold = failureThreshold;
            this.probeLimit = probeLimit;
            this.openNanos = Objects.requireNonNull(openDuration).toNanos();
            if (openNanos <= 0) {
                throw new IllegalArgumentException("Duration must be positive");
            }
            this.ticker = Objects.requireNonNull(ticker);
            this.classifier = Objects.requireNonNull(classifier);
        }

        public <T> T execute(Callable<T> operation) throws Exception {
            Objects.requireNonNull(operation);
            Permit permit = acquire(); // Rejection is outside outcome recording.
            Outcome outcome = Outcome.IGNORE;
            try {
                T result = operation.call(); // Never hold the breaker lock here.
                outcome = Outcome.SUCCESS;
                return result;
            } catch (InterruptedException interrupted) {
                throw interrupted; // Checked cancellation propagates to caller.
            } catch (Exception failure) {
                outcome = Objects.requireNonNull(classifier.apply(failure));
                throw failure; // Classification does not change business truth.
            } finally {
                finish(permit, outcome); // Also releases an ignored probe on Error.
            }
```

CircuitBreakerDemo.java · lines 77–114

```
}

        private synchronized Permit acquire() {
            if (state == State.OPEN) {
                if (ticker.getAsLong() - openedAt < openNanos) {
                    throw new CircuitOpenException();
                }
                moveTo(State.HALF_OPEN); // Lazy: the next call triggers this.
                admittedProbes = 0;
                successfulProbes = 0;
            }
            if (state == State.HALF_OPEN) {
                if (admittedProbes >= probeLimit) {
                    throw new CircuitOpenException();
                }
                admittedProbes++;
            }
            return new Permit(generation);
        }

        private synchronized void finish(Permit permit, Outcome outcome) {
            if (permit.generation() != generation) {
                return; // Old work must not rewrite a newer state generation.
            }
            if (state == State.CLOSED) {
                switch (outcome) {
                    case SUCCESS -> consecutiveFailures = 0;
                    case FAILURE -> {
                        if (++consecutiveFailures >= failureThreshold) open();
                    }
                    case IGNORE -> { }
                }
            } else if (state == State.HALF_OPEN) {
                switch (outcome) {
                    case FAILURE -> open();
                    case SUCCESS -> {
                        if (++successfulProbes == probeLimit) {
                            consecutiveFailures = 0;
```

CircuitBreakerDemo.java · lines 115–152

```
moveTo(State.CLOSED);
                        }
                    }
                    case IGNORE -> admittedProbes--; // Replace unmeasured probe.
                }
            }
        }

        private void open() { // Called only while holding this object's monitor.
            openedAt = ticker.getAsLong();
            moveTo(State.OPEN);
        }

        private void moveTo(State next) {
            state = next;
            generation++;
        }

        synchronized State state() { return state; }
    }

    static final class CircuitBreakingPaymentGateway implements PaymentGateway {
        private final PaymentGateway delegate;
        private final Breaker breaker;

        CircuitBreakingPaymentGateway(PaymentGateway delegate, Breaker breaker) {
            this.delegate = Objects.requireNonNull(delegate);
            this.breaker = Objects.requireNonNull(breaker);
        }

        @Override
        public Authorization authorize(AuthorizePayment command) throws Exception {
            return breaker.execute(() -> delegate.authorize(command));
        }
    }

    static final class FakeTicker implements LongSupplier {
        private final AtomicLong now = new AtomicLong();
```

CircuitBreakerDemo.java · lines 153–190

```
public long getAsLong() { return now.get(); }
        void advance(Duration duration) { now.addAndGet(duration.toNanos()); }
    }

    static Breaker newBreaker(FakeTicker time, int threshold, int probes) {
        return new Breaker(threshold, Duration.ofSeconds(30), probes, time,
                ex -> ex instanceof DependencyUnavailable
                        ? Outcome.FAILURE : Outcome.IGNORE);
    }

    static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    static void expect(Class<? extends Exception> type, Callable<?> action)
            throws Exception {
        try {
            action.call();
        } catch (Exception ex) {
            if (type.isInstance(ex)) return;
            throw ex;
        }
        throw new AssertionError("Expected " + type.getSimpleName());
    }

    static void fail(Breaker breaker) throws Exception {
        expect(DependencyUnavailable.class, () -> breaker.execute(() -> {
            throw new DependencyUnavailable();
        }));
    }

    static void await(CountDownLatch latch) throws InterruptedException {
        if (!latch.await(5, TimeUnit.SECONDS)) {
            throw new AssertionError("Test coordination timed out");
        }
    }

    public static void main(String[] args) throws Exception {
```

CircuitBreakerDemo.java · lines 191–228

```
FakeTicker time = new FakeTicker();
        Breaker breaker = newBreaker(time, 3, 2);
        AtomicInteger calls = new AtomicInteger();
        PaymentGateway payment = new CircuitBreakingPaymentGateway(command -> {
            calls.incrementAndGet();
            return new Authorization(false, "DECLINED");
        }, breaker);
        for (int i = 0; i < 20; i++) {
            check(!payment.authorize(new AuthorizePayment("stable-key")).approved(),
                    "A business decline must remain a decline");
        }
        check(calls.get() == 20 && breaker.state() == State.CLOSED,
                "Closed passes calls; declines do not open");

        fail(breaker);
        breaker.execute(() -> "healthy"); // Resets consecutive failure count.
        fail(breaker);
        fail(breaker);
        check(breaker.state() == State.CLOSED, "Success resets the count");
        fail(breaker);
        check(breaker.state() == State.OPEN, "Threshold opens");
        expect(CircuitOpenException.class,
                () -> payment.authorize(new AuthorizePayment("stable-key")));
        check(calls.get() == 20, "Open must not call the delegate");
        time.advance(Duration.ofSeconds(29));
        expect(CircuitOpenException.class, () -> breaker.execute(() -> "early"));
        time.advance(Duration.ofSeconds(1));
        breaker.execute(() -> "probe one");
        check(breaker.state() == State.HALF_OPEN, "One success is not enough");
        expect(LocalValidationException.class, () -> breaker.execute(() -> {
            throw new LocalValidationException();
        }));
        breaker.execute(() -> "replacement probe");
        check(breaker.state() == State.CLOSED, "Measured successes close");

        Breaker concurrent = newBreaker(time, 1, 2);
        fail(concurrent);
        time.advance(Duration.ofSeconds(30));
```

CircuitBreakerDemo.java · lines 229–266

```
CountDownLatch entered = new CountDownLatch(2);
        CountDownLatch release = new CountDownLatch(1);
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            Callable<String> heldProbe = () -> concurrent.execute(() -> {
                entered.countDown();
                await(release);
                return "healthy";
            });
            var first = executor.submit(heldProbe);
            var second = executor.submit(heldProbe);
            try {
                await(entered);
                for (int i = 0; i < 100; i++) {
                    expect(CircuitOpenException.class,
                            () -> concurrent.execute(() -> "must not run"));
                }
                check(concurrent.state() == State.HALF_OPEN, "Probes still active");
            } finally {
                release.countDown();
            }
            first.get(5, TimeUnit.SECONDS);
            second.get(5, TimeUnit.SECONDS);
        }
        check(concurrent.state() == State.CLOSED, "Both probes completed");

        Breaker stale = newBreaker(time, 1, 1);
        CountDownLatch started = new CountDownLatch(1);
        CountDownLatch finishOld = new CountDownLatch(1);
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            var oldCall = executor.submit(() -> stale.execute(() -> {
                started.countDown();
                await(finishOld);
                return "late success";
            }));
            try {
                await(started);
                fail(stale); // Opens while another CLOSED-era call is active.
            } finally {
```

CircuitBreakerDemo.java · lines 267–283

```
finishOld.countDown();
            }
            oldCall.get(5, TimeUnit.SECONDS);
        }
        check(stale.state() == State.OPEN, "Late success cannot close new state");
        time.advance(Duration.ofSeconds(30));
        fail(stale); // A failed probe starts a new OPEN period.
        expect(CircuitOpenException.class, () -> stale.execute(() -> "too soon"));
        time.advance(Duration.ofSeconds(30));
        expect(InterruptedException.class, () -> stale.execute(() -> {
            throw new InterruptedException("cancelled probe");
        }));
        stale.execute(() -> "replacement after cancellation");
        check(stale.state() == State.CLOSED, "Cancellation releases a probe slot");
        System.out.println("All deterministic breaker checks passed.");
    }
}
```

Appendix B

## Resilience4j integration

Use a JDK 25 installation to build this Maven project. Save the configuration below as `pom.xml` and the Java source as `src/main/java/PaymentPolicies.java`. This example supplies one breaker per protected gateway construction; reuse the resulting gateway.

The timed adapter’s contract is explicit: return business declines normally, translate transport failures and selected unavailable responses into `IOException`, and propagate cancellation. The fake `main` demonstrates wiring only; it does not call a payment service.

Download library exampleDownload pom.xml

pom.xml

```
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>example</groupId>
  <artifactId>circuit-breaker-guide</artifactId>
  <version>1.0.0</version>
  <properties>
    <maven.compiler.release>25</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <dependencies>
    <dependency>
      <groupId>io.github.resilience4j</groupId>
      <artifactId>resilience4j-circuitbreaker</artifactId>
      <version>2.3.0</version>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.14.0</version>
      </plugin>
    </plugins>
  </build>
</project>
```

shell · macOS / Linux

```
mvn package
mvn dependency:copy-dependencies -DoutputDirectory=target/dependency
java -cp "target/classes:target/dependency/*" PaymentPolicies
```

On Windows, replace the classpath colon with a semicolon. The HTML itself has no external assets; building this optional example requires Maven dependencies.

PaymentPolicies.java · lines 1–38

```
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import java.io.IOException;
import java.time.Duration;

public final class PaymentPolicies {
    public record AuthorizePayment(String idempotencyKey) {}
    public record Authorization(boolean approved, String reason) {}

    @FunctionalInterface
    public interface PaymentGateway {
        Authorization authorize(AuthorizePayment command) throws Exception;
    }

    public static PaymentGateway protect(PaymentGateway timedHttpAdapter) {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
                .slidingWindowType(CircuitBreakerConfig.SlidingWindowType.COUNT_BASED)
                .slidingWindowSize(100)
                .minimumNumberOfCalls(20)
                .failureRateThreshold(50.0f)
                .slowCallDurationThreshold(Duration.ofSeconds(2))
                .slowCallRateThreshold(50.0f)
                .waitDurationInOpenState(Duration.ofSeconds(30))
                .permittedNumberOfCallsInHalfOpenState(5)
                .maxWaitDurationInHalfOpenState(Duration.ofSeconds(10))
                .automaticTransitionFromOpenToHalfOpenEnabled(false)
                // Contract: the adapter maps dependency failures to IOException.
                // Business declines are returned as Authorization(false, reason).
                .recordExceptions(IOException.class)
                .ignoreException(ex -> !(ex instanceof IOException))
                .build();

        CircuitBreaker breaker = CircuitBreaker.of("payment-authorize", config);
        // Construct this once per intended failure domain and reuse the result.
        return command -> breaker.executeCallable(
                () -> timedHttpAdapter.authorize(command));
    }
```

PaymentPolicies.java · lines 39–45

```
public static void main(String[] args) throws Exception {
        PaymentGateway fake = command -> new Authorization(false, "DECLINED");
        PaymentGateway protectedGateway = protect(fake);
        System.out.println(protectedGateway.authorize(
                new AuthorizePayment("one-stable-key")));
    }
}
```

At a 50% failure threshold with five measured half-open probes, one failure does not imply immediate reopening. Keep the library’s rate-based recovery semantics separate from Appendix A’s strict any-failure policy. Ignored exceptions count toward neither success nor failure. [[2]](#ref-2)

References and reading notes

## Official sources

This guide adapts the supplied “24. Circuit Breaker” lesson and preserves its 62-step progression. Wording, code and examples were revised to make the artifact self-contained and clarify concurrency, timing and outcome semantics. Numerical settings are teaching examples, not production recommendations.

Reference check: 2 September 2026. Java compatibility here means standard Java 25 language and API usage without preview features; it does not certify every dependency or application integration.

1. [Microsoft Learn — Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breakerFirst-principles motivation, core states, proxy behavior and recovery considerations.
2. [Resilience4j — CircuitBreaker documentation](https://resilience4j.readme.io/docs/circuitbreaker)https://resilience4j.readme.io/docs/circuitbreakerConfiguration, sliding windows, measured and ignored outcomes, half-open rate evaluation, and thread safety. The configuration is explicit to avoid relying on undocumented assumptions.
3. [Oracle Java SE 25 — System.nanoTime()](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime())https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime()Elapsed-time measurement and subtraction-based timeout comparison.
4. [Oracle Java SE 25 — HttpRequest.Builder.timeout(Duration)](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html#timeout(java.time.Duration))https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html#timeout(java.time.Duration)Request timeout configuration and timeout exception semantics.
5. [Oracle Java SE 25 — Executors.newVirtualThreadPerTaskExecutor()](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Executors.html#newVirtualThreadPerTaskExecutor())https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Executors.html#newVirtualThreadPerTaskExecutor()Virtual-thread-per-task executor API used by the concurrency checks.
6. [Resilience4j — official releases](https://github.com/resilience4j/resilience4j/releases)https://github.com/resilience4j/resilience4j/releasesPublished release history supporting the pinned 2.3.0 dependency.
7. [Apache Maven Compiler Plugin — Java release option](https://maven.apache.org/plugins/maven-compiler-plugin/examples/set-compiler-release.html)https://maven.apache.org/plugins/maven-compiler-plugin/examples/set-compiler-release.htmlMaven compiler release configuration.

### Before applying the policy

* Define the protected failure domain and reuse its breaker instance.
* Separate business outcomes, infrastructure failures and ignored outcomes.
* Choose whether the breaker measures attempts or retry sequences.
* Bound attempt duration, total deadline and half-open recovery time.
* Preserve idempotency and ambiguous-outcome reconciliation.
* Observe rejection and fallback separately from primary success.
* Apply a bulkhead when concurrent work needs a hard capacity limit.

24. Circuit Breaker · Adapted from the supplied lesson · Next: 25. Bulkhead