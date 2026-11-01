[Skip to guide](#main)

DESIGN PATTERNS

10 / Proxy

A first-principles guide · Java 25

[01Start with the pressure](#pressure)[02Protect, cache, and defer](#protection)[03Respect the remote boundary](#remote)[04Distinguish intent from shape](#distinctions)[05Generate the wrapper at runtime](#dynamic)[06Make policy semantics explicit](#policies)[07Test the behavior the proxy owns](#tests)[08Decide whether Proxy fits](#judgment)[↗Practice exercise](#exercise)[{ }Complete source](#source)[↗Official references](#references)

Print / Save as PDF

A4 print layout. All examples and source are embedded. Use your browser’s print command if scripts are disabled.

LESSON 10 / STRUCTURAL PATTERNSJAVA 25

# Proxy

Control access.
Keep the caller’s abstraction.

Derive the pattern from a document repository that acquires authorization, caching, auditing, rate limits, and expensive initialization—one pressure at a time.

THE FIRST-PRINCIPLES QUESTION

Should an object stand between the caller and the real implementation to control how access happens?

31 steps + exerciseComplete Java sourceOffline · light theme · print ready

Pressure→ Contract→ Wrapper→ Semantics→ Tests

**Read in order.** The pattern name follows the problem. Later sections revisit early simplifications and make the runtime policies explicit.

**Prerequisites:** Java interfaces, constructors, composition, exceptions, and basic collections. Lambdas and reflection are explained where they enter the design.

**Print:** choose A4 or Letter, use 100% scale, and disable browser-generated headers and footers if they duplicate the page labels. The guide prints all essential text, review notes, and complete source.

PART 01

## Start with the pressure

Steps 1–4 · Derive the need before naming the pattern

### 01Start with a remote document repository

A client needs a document. A repository delegates retrieval to a storage client. At this point, the design has one job and needs no extra wrapper.

Contract · declarations inside ProxyLesson

```
public record Document(String id, String body) {}

public interface DocumentRepository {
    Document findById(String id);
}

public interface StorageClient {
    Document download(String id);
}
```

Real subject · ProxyLesson.RemoteDocumentRepository

```
public static final class RemoteDocumentRepository
        implements DocumentRepository {
    private final StorageClient storage;

    public RemoteDocumentRepository(StorageClient storage) {
        this.storage = Objects.requireNonNull(storage);
    }

    @Override
    public Document findById(String id) {
        return Objects.requireNonNull(storage.download(id));
    }
}
```

Client · wiring excerpt

```
DocumentRepository repository =
        new RemoteDocumentRepository(storageClient);
Document document = repository.findById("DOC-123");
```

Throughout this guide, a read returns a **non-null document** or throws an unchecked exception. A missing document is not represented by `null`. The complete source adds null checks and defines every supporting type.

### 02New requirement: authorization

Security adds a rule: a user must have permission before reading a document. The obvious implementation puts the check directly in the remote repository:

Naive version · method body; assumes injected dependencies

```
@Override
public Document findById(String id) {
    authorization.checkCanRead(currentUser.get(), id);
    return storage.download(id);
}
```

This can be reasonable for a small system. But retrieval now changes for two separate reasons: storage behavior and access policy. More pressure will tell us whether separation is useful.

### 03More pressure arrives

| Requirement | What it changes |
| --- | --- |
| Authorization | Whether a caller may read a document. |
| Caching | Whether this read needs to reach storage. |
| Auditing | What must be recorded for attempted, successful, and failed access. |
| Rate limiting | Whether another remote operation is allowed now. |
| Lazy creation | When an expensive dependency is constructed. |

Putting every rule in `RemoteDocumentRepository` ties together policies with different lifecycles. The design pressure is to give access decisions a separate place while keeping retrieval focused.

### 04What does the caller actually need?

The caller already depends on `DocumentRepository`. It does not need a new API for each policy. Place another object in front of the real repository, and have it implement that same interface.

| Role | Responsibility in this lesson |
| --- | --- |
| Client | Calls `DocumentRepository.findById(id)`. |
| Subject | `DocumentRepository`, the shared contract. |
| Proxy | Implements the contract and decides how access proceeds. |
| Real subject | `RemoteDocumentRepository`, which performs retrieval. |

**The Proxy idea**

Stand in for another object and control whether, when, or how it is accessed, while preserving the caller’s abstraction.

PART 02

## Protect, cache, and defer

Steps 5–10 · Learn from the path a call takes

### 05Build a protection proxy

Protection proxy · complete nested class

```
public static final class AuthorizedDocumentRepository
        implements DocumentRepository {
    private final DocumentRepository target;
    private final AuthorizationService authorization;
    private final Supplier<String> currentUser;

    public AuthorizedDocumentRepository(
            DocumentRepository target,
            AuthorizationService authorization,
            Supplier<String> currentUser) {
        this.target = Objects.requireNonNull(target);
        this.authorization = Objects.requireNonNull(authorization);
        this.currentUser = Objects.requireNonNull(currentUser);
    }

    @Override
    public Document findById(String id) {
        authorization.checkCanRead(currentUser.get(), id);
        return target.findById(id);
    }
}
```

The proxy checks permission *before* delegation. If the check throws, the real repository is never reached. `currentUser` is an injected supplier of trusted request identity; the caller must not be able to choose another user’s identity.

Composition · dependencies supplied by application startup

```
DocumentRepository repository =
        new AuthorizedDocumentRepository(
                new RemoteDocumentRepository(storageClient),
                authorizationService,
                currentUser);
```

### 06Trace the execution

| Step | Allowed request | Denied request |
| --- | --- | --- |
| 1 · Client | Calls `findById("DOC-123")`. | Same call. |
| 2 · Proxy | Permission check succeeds. | Permission check throws. |
| 3 · Target | Storage retrieval runs. | **Not reached.** |
| 4 · Result | Document or retrieval failure propagates. | Access denial propagates. |

The responsibility is precise: **may this call reach the target?** The proxy enforces this only for calls routed through it. Do not expose a bypassing target reference to untrusted callers.

### 07Add a simple caching proxy

First cache · intentionally single-threaded and unbounded

```
public static final class SimpleCachedRepository
        implements DocumentRepository {
    private final DocumentRepository target;
    private final Map<String, Document> cache = new HashMap<>();

    public SimpleCachedRepository(DocumentRepository target) {
        this.target = Objects.requireNonNull(target);
    }

    @Override
    public Document findById(String id) {
        Document cached = cache.get(id);
        if (cached != null) return cached;
        Document loaded = Objects.requireNonNull(target.findById(id));
        cache.put(id, loaded);
        return loaded;
    }
}
```

Call order · Authorization, Cache, Remote

```
DocumentRepository repository =
        new AuthorizedDocumentRepository(
                new SimpleCachedRepository(
                        new RemoteDocumentRepository(storageClient)),
                authorizationService,
                currentUser);
```

A hit returns early. A miss delegates, then stores a successful result. This first version teaches the structure; section 22 adds a size bound, expiration, and synchronization.

### 08Order changes runtime semantics

| Outer → inner | Warm-cache behavior |
| --- | --- |
| **Authorization → Cache → Remote** | Authorization runs even when the cache has the document. |
| Cache → Authorization → Remote | A hit can return before authorization runs. A denied caller may receive cached data. |

This comparison assumes a cache shared across callers and keyed only by document ID. Even a per-user cache needs a deliberate permission-revocation policy. If document content varies by tenant, user, locale, or version, the cache key must represent those dimensions too.

TRY THE CALL PATH

#### Can a cached read bypass permission?

A single-request model with a shared cache. This illustrates control flow; it does not run Java.

Wrapper orderAuthorization → Cache → RemoteCache → Authorization → Remote
[ ] User has permission[x] Document is cached

**Ordering rule**

Put authorization outside every cache that can return protected data. Wrapping the wrong object can preserve the interface and break the security requirement.

### 09Defer construction with a lazy proxy

If creating a client or repository is expensive, defer that work until a call actually needs it. Inject a factory so the proxy does not also decide how storage is configured.

Virtual proxy · synchronized initialization

```
public static final class LazyDocumentRepository
        implements DocumentRepository {
    private final Supplier<DocumentRepository> factory;
    private DocumentRepository target;

    public LazyDocumentRepository(Supplier<DocumentRepository> factory) {
        this.factory = Objects.requireNonNull(factory);
    }

    private synchronized DocumentRepository target() {
        if (target == null) {
            target = Objects.requireNonNull(factory.get());
        }
        return target;
    }

    @Override
    public Document findById(String id) {
        return target().findById(id);
    }
}
```

Constructing this proxy does not call the factory. The first read creates the target; later reads reuse it. The synchronized helper guards construction and publication. Delegation happens after the helper releases the monitor. [JLS 25: synchronization](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html)

If the factory throws, `target` stays unset, so a later request retries construction. This is an explicit policy. It does not make the target itself thread-safe, and the factory must not re-enter the same lazy proxy. Defer the expensive work *inside* the supplier; creating it before the supplier defeats laziness.

### 10Why is this different from Factory?

| Question | Factory | Proxy |
| --- | --- | --- |
| Primary job | Create and return an object. | Stand between caller and subject. |
| Lifetime in the call path | The caller uses the created object afterward. | Every call through the proxy reference enters it. |
| Can they cooperate? | Supplies the real repository. | A lazy proxy invokes the factory on demand. |

Factory answers *how do I obtain it?* Proxy answers *how should access to it proceed?*

PART 03

## Respect the remote boundary

Steps 11–13 · Preserve the interface without concealing cost

### 11Use a remote proxy

A remote implementation lets client code express `repository.findById(id)` while the implementation handles a protocol. With the JDK API, build an `HttpRequest` and call `HttpClient.send`. There is no JDK `client.get(path, Document.class)` convenience method. [Java 25 HttpClient](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html)

The complete `HttpDocumentRepository.java` is in the appendix. It implements the same lesson contract and expects an HTTPS endpoint returning a bounded UTF-8 plain-text document. Its IDs are restricted to letters, digits, underscores, and hyphens.

HTTP request and response · excerpt from findById

```
HttpRequest request = HttpRequest.newBuilder(base.resolve(id))
        .timeout(Duration.ofSeconds(3))
        .header("Accept", "text/plain")
        .GET()
        .build();
try {
    HttpResponse<String> response = client.send(request,
            HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
    int status = response.statusCode();
    if (status == 404) throw new NoSuchElementException("Document not found");
    if (status == 401 || status == 403) {
        throw new ProxyLesson.AccessDeniedException();
    }
    if (status != 200) throw new RepositoryException("HTTP " + status);
    // Teaching endpoint contract: bounded, UTF-8 plain-text body.
    return new ProxyLesson.Document(id, response.body());
```

Failure translation · same method

```
} catch (InterruptedException interrupted) {
    Thread.currentThread().interrupt();
    throw new RepositoryException("Document read interrupted", interrupted);
} catch (IOException failure) {
    throw new RepositoryException("Document transport failed", failure);
}
```

The proxy retains the original cause and restores interrupt status when translating interruption. It explicitly maps status codes instead of treating every response as a successful document.

### 12Remote calls are not local calls

| Concern | Decision that belongs in the contract or application |
| --- | --- |
| Latency and blocking | Set time budgets and avoid accidental serial work. |
| Timeouts and failures | Define how callers distinguish transport failure, denial, and missing data. |
| Retries | Choose retryability, idempotency, backoff, and an overall deadline. |
| Payload and identity | Define schema, response-size limits, credentials, and data sensitivity. |
| Resource ownership | Share the configured client and decide who closes it at shutdown. |

The example sets a per-request timeout. A real composition root should also configure the client’s connection timeout. These settings address different parts of the operation; they are not a complete application deadline. [Request timeout](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html) · [Client lifecycle](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html)

**Scope of the HTTP example**

The endpoint and plain-text protocol are teaching assumptions. Authentication headers, JSON mapping, retry policy, response-size enforcement, and live service integration are outside this example. The code has no endpoint to contact until you supply one.

### 13Avoid the fallacy of transparent remoting

Same source code · potentially different operational cost

```
for (String id : ids) {
    repository.findById(id);
}
```

For 100 uncached IDs, an implementation that sends one request per call makes 100 remote requests. A local implementation can execute the same loop without those network exchanges. Identical method syntax does not imply identical cost.

If the use case is bulk retrieval, a deliberate batch operation such as `findAllByIds(ids)` may express it better. Define batch size, partial failures, result ordering, and limits instead of promising that remote access is transparent.

PART 04

## Distinguish intent from shape

Steps 14–17 · Similar class structures can solve different problems

### 14Proxy vs Decorator

| Pattern | Primary intent | Example |
| --- | --- | --- |
| Proxy | Stand in for a subject or control access to it. | `AuthorizedDocumentRepository` gates access. |
| Decorator | Add composable behavior to a component. | A metrics wrapper adds measurement. |

Both often implement the same interface and delegate to another instance. Caching, auditing, and logging can be described through either lens depending on why the wrapper exists. Pattern names describe intent; they are not mutually exclusive runtime types.

### 15Structural similarity is not enough

Structural sketch · uses the lesson’s document types

```
final class Wrapper implements DocumentRepository {
    private final DocumentRepository target;

    Wrapper(DocumentRepository target) {
        this.target = target;
    }

    @Override
    public Document findById(String id) {
        // Policy or additional behavior can live here.
        return target.findById(id);
    }
}
```

Reading this shape cannot tell you whether the design is Proxy or Decorator. Ask: **why does this wrapper exist?** Also ask whether callers can rely on the original contract after wrapping.

### 16Proxy vs Adapter

| Pattern | Relationship to the interface |
| --- | --- |
| Adapter | Translates an incompatible API into the API a client expects. |
| Proxy | Preserves the subject’s conceptual API while mediating access. |

A remote repository can have both aspects: it stands in for a document service and translates HTTP into an application interface. The useful question is which problem you are explaining.

### 17Proxy vs Facade

A Facade offers a simpler entry point over subsystem operations. It need not share an interface with those components. A Proxy stands in for a subject behind the same conceptual contract.

| Pattern | Question it answers |
| --- | --- |
| Adapter | How do incompatible interfaces communicate? |
| Decorator | How do I add composable behavior? |
| Facade | How do I simplify a subsystem? |
| Proxy | How do I control access to a subject? |

PART 05

## Generate the wrapper at runtime

Steps 18–21 · Java dynamic proxies and their tradeoffs

### 18Java can generate interface-based proxies

`java.lang.reflect.Proxy` creates runtime objects implementing specified interfaces. Interface calls are dispatched to an associated `InvocationHandler`. These JDK proxies do not subclass your concrete service class. [Java 25 Proxy](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html)

Contract and real service · nested in DynamicProxyDemo

```
public interface PaymentService {
    void charge(long cents);
}

public static final class DemoPaymentService implements PaymentService {
    @Override
    public void charge(long cents) {
        if (cents <= 0) throw new IllegalArgumentException("Positive cents required");
        System.out.println("Charging " + cents);
    }
}
```

This service only prints a message. It is a local demonstration and does not invoke a payment provider.

### 19Route calls through an InvocationHandler

LoggingHandler.invoke · full method

```
@Override
    public Object invoke(Object proxy, Method method, Object[] args)
            throws Throwable {
        // Explicit identity semantics for this teaching proxy.
        if (method.getDeclaringClass() == Object.class) {
            return switch (method.getName()) {
                case "equals" -> proxy == args[0];
                case "hashCode" -> System.identityHashCode(proxy);
                case "toString" -> "LoggingProxy["
                        + target.getClass().getSimpleName() + "]";
                default -> throw new AssertionError(method);
            };
        }
        System.out.println("Calling " + method.getName());
        try {
            return method.invoke(target, args);
        } catch (InvocationTargetException failure) {
            throw failure.getCause();
        }
```

Create and invoke · complete program in appendix

```
PaymentService proxy = (PaymentService) Proxy.newProxyInstance(
        PaymentService.class.getClassLoader(),
        new Class<?>[] { PaymentService.class },
        new LoggingHandler(new DemoPaymentService()));

proxy.charge(5000);
```

`Method.invoke` wraps a target-thrown exception in `InvocationTargetException`. Unwrapping its cause preserves the target’s failure at the proxy boundary. Otherwise an undeclared checked wrapper can emerge as `UndeclaredThrowableException`. [Method.invoke](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Method.html#invoke(java.lang.Object,java.lang.Object...)) · [InvocationHandler exception contract](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/InvocationHandler.html)

The handler also gives `equals`, `hashCode`, and `toString` an explicit identity-based policy. Blindly forwarding `equals` to the target can make `proxy.equals(proxy)` false. [Object-method dispatch](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html)

### 20Why dynamic proxies matter

If payment, order, and user services need the same interception logic, generating wrappers can avoid repeating one forwarding class per interface. A handler can centralize logging or another cross-cutting policy.

Dynamic generation is a mechanism. A generic logging handler may have Decorator intent, while a permission handler may have Proxy intent. Generating a proxy does not supply transaction, authorization, or audit correctness automatically.

### 21The costs and edge cases

| Question | What to remember |
| --- | --- |
| Can this target be proxied? | JDK dynamic proxies require interfaces; Java 25 disallows sealed or hidden proxy interfaces. Visibility and module rules also apply. |
| What reaches the handler? | Calls made through the proxy reference. A target’s internal calls on `this` bypass this wrapper. |
| What about arguments? | `args` may be `null` for a no-argument method. |
| What about default methods? | Choose target delegation or an explicit `InvocationHandler.invokeDefault` policy. |
| What can be thrown? | Unchecked exceptions, errors, and checked exceptions allowed by the interface contract. |
| Is it worth it? | Use generic interception when it offsets less explicit control flow and more difficult debugging. |

In this example, default methods use normal reflective delegation to the target. No special default-method dispatch is required by `PaymentService`. [Proxy restrictions](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html) · [Handler and default-method rules](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/InvocationHandler.html)

PART 06

## Make policy semantics explicit

Steps 22–26 · Caching, quotas, auditing, and composition

### 22A better teaching cache still needs a policy

The initial map grows without limit. Adding an `expiresAt` field does not remove expired entries that are never read again, so TTL alone does not bound memory. A concurrent map also does not make a multi-step check/load/store sequence one atomic operation. [ConcurrentHashMap contract](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)

The second cache uses a capacity-limited, access-order `LinkedHashMap`, elapsed-time TTL, and one monitor. It removes the least recently used entry when capacity is exceeded. [LinkedHashMap ordering](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/LinkedHashMap.html)

Bounded cache · read and invalidation methods

```
@Override
    public synchronized Document findById(String id) {
        Entry entry = cache.get(id);
        long now = ticker.getAsLong();
        if (entry != null && now - entry.loadedAt() < ttlNanos) {
            return entry.document();
        }
        cache.remove(id);
        Document loaded = Objects.requireNonNull(target.findById(id));
        cache.put(id, new Entry(loaded, ticker.getAsLong()));
        if (cache.size() > maxEntries) {
            var eldest = cache.entrySet().iterator();
            eldest.next();
            eldest.remove();
        }
        return loaded;
    }

    public synchronized void invalidate(String id) {
        cache.remove(id);
```

| Policy | Choice in the complete example |
| --- | --- |
| Clock | `System.nanoTime()` for elapsed time; injectable ticker for tests. |
| TTL start | After a successful load finishes; equality at the TTL boundary counts as expired. |
| Capacity | A positive maximum number of entries, with least-recently-used eviction. |
| Failures and missing values | Do not cache exceptions or `null`. |
| Concurrency | Serialize lookup and load under one monitor, including remote work. |
| Invalidation | Explicit per-ID invalidation; no background cleanup or distributed coherence. |

Elapsed-time subtraction follows the JDK’s guidance; do not treat the ticker as wall-clock time. [System.nanoTime](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime())

**Deliberate tradeoff**

The monitor makes this example easy to reason about, but one slow load blocks all reads through this cache, even for other keys. A high-throughput system needs a separately designed loading and concurrency policy. The pattern supplies a location for caching, not cache correctness.

### 23Control capacity with a rate-limiting proxy

Rate-limiting proxy · complete nested class

```
public static final class RateLimitedRepository
        implements DocumentRepository {
    private final DocumentRepository target;
    private final RateLimiter limiter;

    public RateLimitedRepository(DocumentRepository target, RateLimiter limiter) {
        this.target = Objects.requireNonNull(target);
        this.limiter = Objects.requireNonNull(limiter);
    }

    @Override
    public Document findById(String id) {
        if (!limiter.tryAcquire()) throw new RateLimitExceededException();
        return target.findById(id);
    }
}
```

`RateLimiter` is a lesson-defined interface, not a JDK class. The complete source supplies a synchronized fixed-window implementation. Each permit counts an attempted target call, including a call that later fails.

| Outer → inner | What consumes a permit? |
| --- | --- |
| Cache → RateLimit → Remote | Cache misses that attempt remote access. |
| RateLimit → Cache → Remote | Every allowed call reaching the limiter, including cache hits. |

The original requirement was to limit **remote storage calls**, so our composition places the cache outside the limiter. The supplied limiter is local to one instance, shares one quota, and allows bursts around a window boundary. It is not a distributed or per-user limit.

### 24Audit attempts and outcomes

An audit wrapper records an attempt, then either success or failure. It must also decide what happens when recording itself fails. The full implementation preserves a target failure and adds a failure-log error as a suppressed exception.

Audit method · constructor and AuditEvent are in the appendix

```
@Override
    public Document findById(String id) {
        String user = currentUser.get();
        audit.record(new AuditEvent(user, id, "ATTEMPT", ""));
        Document result;
        try {
            result = target.findById(id);
        } catch (RuntimeException failure) {
            try {
                audit.record(new AuditEvent(user, id, "FAILURE",
                        failure.getClass().getSimpleName()));
            } catch (RuntimeException auditFailure) {
                if (auditFailure != failure) failure.addSuppressed(auditFailure);
            }
            throw failure;
        }
        audit.record(new AuditEvent(user, id, "SUCCESS", ""));
        return result;
```

This example propagates an attempt-log failure before delegation and a success-log failure before returning the result. It catches target `RuntimeException`s; it is not an exhaustive recorder of JVM errors or process crashes. Audit durability, sensitive-field redaction, correlation IDs, and sink failure policy need explicit production decisions.

### 25Combine wrappers around a stated policy

For this lesson, the decisions are: record attempts including denials; authorize every read; count only remote attempts against the quota; create storage only when needed.

| Call enters in this order | Purpose |
| --- | --- |
| 1 · Audit | See attempts, denied reads, successful cache hits, and retrieval failures. |
| 2 · Authorization | Check permission before any protected value can be returned. |
| 3 · Cache | Return a valid cached document without consuming a remote permit. |
| 4 · Rate limit | Gate calls that need the remote target. |
| 5 · Lazy repository | Create the target on the first permitted remote read. |
| 6 · Remote repository | Download the document. |

**An inconsistency to resolve**

Authorization → Audit cannot record authorization denials in that audit wrapper, because the call never reaches it. If “audit every failed access” includes denied requests, Audit must be outside Authorization, or denials must be recorded separately.

The innermost successful result returns outward through the chain. A wrapper can return early or throw, so later wrappers may never run. Runtime semantics come from the whole chain.

### 26Keep wiring at the composition root

Composition root · complete factory method

```
public static DocumentRepository buildDocumentRepository(
        Supplier<StorageClient> storageFactory,
        AuthorizationService authorization,
        Supplier<String> currentUser, AuditLog audit,
        RateLimiter limiter) {
    DocumentRepository repository = new LazyDocumentRepository(
            () -> new RemoteDocumentRepository(storageFactory.get()));
    repository = new RateLimitedRepository(repository, limiter);
    repository = new CachedDocumentRepository(repository,
            Duration.ofMinutes(5), 100, System::nanoTime);
    repository = new AuthorizedDocumentRepository(
            repository, authorization, currentUser);
    return new AuditedRepository(repository, audit, currentUser);
}
```

Build from the target outward, then hand the outer reference to business code. This keeps policy wiring in one reviewable place. The factory assembles the chain once; the proxy objects remain in the path of subsequent calls.

In a concurrent application, use a trusted request context that remains consistent throughout the call. The audit sink, authorization service, and target must each support the intended concurrency. A synchronized cache does not make the entire application thread-safe.

PART 07

## Test the behavior the proxy owns

Steps 27–28 · Verify both isolation and the assembled chain

### 27Prove denied access never reaches the target

Self-check pattern · helpers defined in ProxyLesson.java

```
AtomicInteger calls = new AtomicInteger();
DocumentRepository target = id -> {
    calls.incrementAndGet();
    return new Document(id, "body");
};
AuthorizationService deny = (user, id) -> {
    throw new AccessDeniedException();
};
var proxy = new AuthorizedDocumentRepository(
        target, deny, () -> "learner");

expect(AccessDeniedException.class,
        () -> proxy.findById("DOC-1"));
check(calls.get() == 0, "Denied request reached target");
```

The important assertion is not only that an exception occurred. It is that the target was never called. Repeat this test with a warmed cache inside authorization; a cache hit must not bypass the check.

### 28Test cache and composition semantics

| Scenario | Required observation |
| --- | --- |
| Read one ID twice before expiry | Only one target load. |
| Reach the TTL boundary | A new load occurs without sleeping in the test. |
| Exceed capacity and revisit an evicted key | The evicted key is loaded again. |
| Invalidate a key | The next read loads it again. |
| Concurrent first use of the lazy proxy | One target construction. |
| Cache hit with the remote quota exhausted | The cached read succeeds; a miss is rejected. |
| Authorization denial inside outer audit | Attempt and failure are recorded. |
| Target failure plus audit-sink failure | The original failure survives; audit failure is suppressed. |
| Full chain: repeated public read, then denied read | One load, two audited successes, one audited denial. |

The complete source runs these checks with explicit `AssertionError`s. No test framework, extra dependency, sleeps, or `-ea` flag is required. The dynamic-proxy demo separately verifies target exception propagation and its Object-method policy.

PART 08

## Decide whether Proxy fits

Steps 29–31 · Keep the abstraction honest

### 29When Proxy is useful

Strong signals include expensive initialization, remote access, permission checks, cache access, resource quotas, and audit policy. In each case, ask whether an intervening object can preserve the caller’s contract while controlling access.

A wrapper is useful when it separates a meaningful policy. A forwarding class with no policy, no substituted location, and no expected variation may add little value.

### 30When Proxy hides too much

A method that looks like a simple lookup may perform authorization, cache loading, remote calls, and retry attempts. Hiding the plumbing can help clients; hiding latency and failure behavior can mislead them.

Make timeouts, consistency, authorization, and failure semantics part of the documented contract. Track the actual path in diagnostics. Choose explicit bulk or asynchronous APIs when the use case needs them.

**The boundary to preserve**

Interface compatibility is not a promise of identical performance, failure modes, or consistency. A good abstraction still tells callers what they need to plan around.

### 31Reason from first principles

1. Does the caller already depend on the right abstraction?
2. Do I need an object to stand between the caller and the implementation?
3. Should it control whether, when, or how the target is accessed?
4. Should callers keep seeing the same interface?
5. Can I state and test the semantics of the resulting call path?

If these answers fit the problem, Proxy is a strong candidate. Choose the abstraction and policy first; use the pattern name to communicate the resulting design.

PRACTICE

## Exercise · protect user profiles

Transfer the reasoning to a new subject.

Start with this contract. Implement a fake remote repository that returns a real value and counts calls, then add independent authorization, cache, rate-limit, and audit wrappers.

Exercise contract · use separate files for public top-level types

```
public record UserProfile(String userId, String displayName) {}

public interface UserProfileRepository {
    UserProfile find(String userId);
}
```

Use this call order when auditing includes denied access and rate limiting counts remote attempts:

Audit → Authorization → Cache → RateLimit → Remote

1. The client depends only on `UserProfileRepository`.
2. Unauthorized requests return no protected profile and never reach the remote repository.
3. Cache hits avoid network work and still undergo authorization.
4. Cached reads do not consume the remote-call quota; explain how to change that policy.
5. Audit attempted, successful, and failed access, including authorization denial.
6. Test each wrapper and at least one complete composition.
7. Explain one concrete behavior change caused by reversing two wrappers.

#### Questions to answer before coding

Is a profile’s content identical for all authorized callers? Which dimensions belong in the cache key? What happens when permission is revoked or the profile changes? Should an unavailable audit sink block the read?

Review notes

For the stated policy, outer audit sees denial; authorization outside cache checks every read; cache outside limiter avoids charging for hits. A per-user read quota would move the limiter outside cache. None of those choices alone solves cache invalidation or a changing authorization decision during an in-flight request.

NEXT · LESSON 11

### Composite

The next pressure is a part-whole hierarchy. When a file and a directory can support a meaningful common operation such as `size()`, a shared component abstraction lets callers operate on one item or an entire tree. Proxy’s question is access; Composite’s question is recursive structure.

RUNNABLE SOURCE

## Complete Java examples

Three source files are embedded below. No external assets or dependencies.

Save all three files in the same directory. On JDK 25, use:

Terminal · JDK 25

```
javac --release 25 ProxyLesson.java DynamicProxyDemo.java HttpDocumentRepository.java
java ProxyLesson
java DynamicProxyDemo
```

`ProxyLesson` uses a fake storage client, so its checks run offline. `DynamicProxyDemo` also runs locally. `HttpDocumentRepository` is a reusable implementation with no `main`; compile it with `ProxyLesson` and supply a real client and endpoint when integrating it.

The main checks print `ProxyLesson: all checks passed`. The dynamic demo prints its call trace, then `DynamicProxyDemo: all checks passed`.

**Compatibility and validation**

Uses stable Java features and APIs available in Java 25; no preview flags. All three files compiled, and both executable check suites passed, on the available OpenJDK 17.0.20 runtime. Java 25 APIs were checked against Oracle’s versioned documentation. A JDK 25 execution and live HTTP integration were not available in this validation environment.

Lesson excerpts omit imports and surrounding containers where indicated. In `ProxyLesson.java` and `DynamicProxyDemo.java`, helper types are nested so each program fits in one file. The complete files below are the authoritative runnable versions.

### ProxyLesson.java

Show sourceCopyDownload .java

ProxyLesson.java

```
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Executors;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.LongSupplier;
import java.util.function.Supplier;

public final class ProxyLesson {
    // Contract: return a non-null document, or throw a RuntimeException.
    public record Document(String id, String body) {
        public Document {
            Objects.requireNonNull(id);
            Objects.requireNonNull(body);
        }
    }

    public interface DocumentRepository {
        Document findById(String id);
    }

    @FunctionalInterface
    public interface StorageClient {
        Document download(String id);
    }

    public static final class RemoteDocumentRepository
            implements DocumentRepository {
        private final StorageClient storage;

        public RemoteDocumentRepository(StorageClient storage) {
            this.storage = Objects.requireNonNull(storage);
        }

        @Override
        public Document findById(String id) {
            return Objects.requireNonNull(storage.download(id));
        }
    }

    @FunctionalInterface
    public interface AuthorizationService {
        void checkCanRead(String userId, String documentId);
    }

    public static final class AccessDeniedException
            extends RuntimeException {
        public AccessDeniedException() { super("Access denied"); }
    }

    public static final class AuthorizedDocumentRepository
            implements DocumentRepository {
        private final DocumentRepository target;
        private final AuthorizationService authorization;
        private final Supplier<String> currentUser;

        public AuthorizedDocumentRepository(
                DocumentRepository target,
                AuthorizationService authorization,
                Supplier<String> currentUser) {
            this.target = Objects.requireNonNull(target);
            this.authorization = Objects.requireNonNull(authorization);
            this.currentUser = Objects.requireNonNull(currentUser);
        }

        @Override
        public Document findById(String id) {
            authorization.checkCanRead(currentUser.get(), id);
            return target.findById(id);
        }
    }

    // Stage 1: single-threaded, unbounded, no expiration.
    public static final class SimpleCachedRepository
            implements DocumentRepository {
        private final DocumentRepository target;
        private final Map<String, Document> cache = new HashMap<>();

        public SimpleCachedRepository(DocumentRepository target) {
            this.target = Objects.requireNonNull(target);
        }

        @Override
        public Document findById(String id) {
            Document cached = cache.get(id);
            if (cached != null) return cached;
            Document loaded = Objects.requireNonNull(target.findById(id));
            cache.put(id, loaded);
            return loaded;
        }
    }

    public static final class LazyDocumentRepository
            implements DocumentRepository {
        private final Supplier<DocumentRepository> factory;
        private DocumentRepository target;

        public LazyDocumentRepository(Supplier<DocumentRepository> factory) {
            this.factory = Objects.requireNonNull(factory);
        }

        private synchronized DocumentRepository target() {
            if (target == null) {
                target = Objects.requireNonNull(factory.get());
            }
            return target;
        }

        @Override
        public Document findById(String id) {
            return target().findById(id);
        }
    }

    // Stage 2: bounded LRU + TTL; serializes all reads and loads.
    public static final class CachedDocumentRepository
            implements DocumentRepository {
        private record Entry(Document document, long loadedAt) {}
        private final DocumentRepository target;
        private final long ttlNanos;
        private final int maxEntries;
        private final LongSupplier ticker;
        private final Map<String, Entry> cache =
                new LinkedHashMap<>(16, 0.75f, true);

        public CachedDocumentRepository(DocumentRepository target,
                Duration ttl, int maxEntries, LongSupplier ticker) {
            this.target = Objects.requireNonNull(target);
            this.ticker = Objects.requireNonNull(ticker);
            this.ttlNanos = Objects.requireNonNull(ttl).toNanos();
            if (ttlNanos <= 0 || maxEntries <= 0) {
                throw new IllegalArgumentException("Positive TTL and capacity required");
            }
            this.maxEntries = maxEntries;
        }

        @Override
        public synchronized Document findById(String id) {
            Entry entry = cache.get(id);
            long now = ticker.getAsLong();
            if (entry != null && now - entry.loadedAt() < ttlNanos) {
                return entry.document();
            }
            cache.remove(id);
            Document loaded = Objects.requireNonNull(target.findById(id));
            cache.put(id, new Entry(loaded, ticker.getAsLong()));
            if (cache.size() > maxEntries) {
                var eldest = cache.entrySet().iterator();
                eldest.next();
                eldest.remove();
            }
            return loaded;
        }

        public synchronized void invalidate(String id) {
            cache.remove(id);
        }
    }

    @FunctionalInterface
    public interface RateLimiter {
        boolean tryAcquire();
    }

    // One limiter instance, one fixed window; not a distributed quota.
    public static final class FixedWindowRateLimiter implements RateLimiter {
        private final int limit;
        private final long windowNanos;
        private final LongSupplier ticker;
        private long started;
        private int used;

        public FixedWindowRateLimiter(int limit, Duration window,
                LongSupplier ticker) {
            this.windowNanos = Objects.requireNonNull(window).toNanos();
            if (limit <= 0 || windowNanos <= 0) {
                throw new IllegalArgumentException("Positive limit and window required");
            }
            this.limit = limit;
            this.ticker = Objects.requireNonNull(ticker);
            this.started = ticker.getAsLong();
        }

        @Override
        public synchronized boolean tryAcquire() {
            long now = ticker.getAsLong();
            if (now - started >= windowNanos) {
                started = now;
                used = 0;
            }
            if (used >= limit) return false;
            used++;
            return true;
        }
    }

    public static final class RateLimitExceededException
            extends RuntimeException {
        public RateLimitExceededException() { super("Rate limit exceeded"); }
    }

    public static final class RateLimitedRepository
            implements DocumentRepository {
        private final DocumentRepository target;
        private final RateLimiter limiter;

        public RateLimitedRepository(DocumentRepository target, RateLimiter limiter) {
            this.target = Objects.requireNonNull(target);
            this.limiter = Objects.requireNonNull(limiter);
        }

        @Override
        public Document findById(String id) {
            if (!limiter.tryAcquire()) throw new RateLimitExceededException();
            return target.findById(id);
        }
    }

    public record AuditEvent(String user, String documentId,
            String outcome, String detail) {}

    @FunctionalInterface
    public interface AuditLog {
        void record(AuditEvent event);
    }

    public static final class AuditedRepository implements DocumentRepository {
        private final DocumentRepository target;
        private final AuditLog audit;
        private final Supplier<String> currentUser;

        public AuditedRepository(DocumentRepository target, AuditLog audit,
                Supplier<String> currentUser) {
            this.target = Objects.requireNonNull(target);
            this.audit = Objects.requireNonNull(audit);
            this.currentUser = Objects.requireNonNull(currentUser);
        }

        @Override
        public Document findById(String id) {
            String user = currentUser.get();
            audit.record(new AuditEvent(user, id, "ATTEMPT", ""));
            Document result;
            try {
                result = target.findById(id);
            } catch (RuntimeException failure) {
                try {
                    audit.record(new AuditEvent(user, id, "FAILURE",
                            failure.getClass().getSimpleName()));
                } catch (RuntimeException auditFailure) {
                    if (auditFailure != failure) failure.addSuppressed(auditFailure);
                }
                throw failure;
            }
            audit.record(new AuditEvent(user, id, "SUCCESS", ""));
            return result;
        }
    }

    // Request flow: Audit -> Authorization -> Cache -> RateLimit -> Lazy -> Remote.
    public static DocumentRepository buildDocumentRepository(
            Supplier<StorageClient> storageFactory,
            AuthorizationService authorization,
            Supplier<String> currentUser, AuditLog audit,
            RateLimiter limiter) {
        DocumentRepository repository = new LazyDocumentRepository(
                () -> new RemoteDocumentRepository(storageFactory.get()));
        repository = new RateLimitedRepository(repository, limiter);
        repository = new CachedDocumentRepository(repository,
                Duration.ofMinutes(5), 100, System::nanoTime);
        repository = new AuthorizedDocumentRepository(
                repository, authorization, currentUser);
        return new AuditedRepository(repository, audit, currentUser);
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static <T extends RuntimeException> T expect(
            Class<T> type, Runnable action) {
        try {
            action.run();
        } catch (RuntimeException failure) {
            if (type.isInstance(failure)) return type.cast(failure);
            throw new AssertionError("Unexpected failure", failure);
        }
        throw new AssertionError("Expected " + type.getSimpleName());
    }

    public static void main(String[] args) throws Exception {
        AtomicInteger remoteCalls = new AtomicInteger();
        DocumentRepository remote = id -> {
            remoteCalls.incrementAndGet();
            return new Document(id, "body");
        };
        AuthorizationService deny = (user, id) -> {
            throw new AccessDeniedException();
        };
        Supplier<String> user = () -> "learner";

        // A denied request never reaches the target.
        var protectedRemote = new AuthorizedDocumentRepository(remote, deny, user);
        expect(AccessDeniedException.class, () -> protectedRemote.findById("DOC-1"));
        check(remoteCalls.get() == 0, "Denied request reached remote");

        // Authorization stays outside a warm cache.
        var cache = new SimpleCachedRepository(remote);
        cache.findById("DOC-1");
        cache.findById("DOC-1");
        check(remoteCalls.get() == 1, "Cache did not reuse the value");
        var protectedCache = new AuthorizedDocumentRepository(cache, deny, user);
        expect(AccessDeniedException.class, () -> protectedCache.findById("DOC-1"));
        check(remoteCalls.get() == 1, "Denied cached read reached remote");

        // Bounded cache: deterministic TTL and eviction checks, without sleeps.
        AtomicLong time = new AtomicLong();
        AtomicInteger loads = new AtomicInteger();
        var bounded = new CachedDocumentRepository(id -> {
            loads.incrementAndGet();
            return new Document(id, "body");
        }, Duration.ofNanos(10), 2, time::get);
        bounded.findById("A");
        time.set(9);
        bounded.findById("A");
        check(loads.get() == 1, "Entry expired too early");
        time.set(10);
        bounded.findById("A");
        check(loads.get() == 2, "Entry must expire at the TTL boundary");
        bounded.findById("B");
        bounded.findById("A"); // A becomes the most recently used.
        bounded.findById("C"); // B is evicted.
        bounded.findById("B");
        check(loads.get() == 5, "LRU capacity rule failed");
        bounded.invalidate("B");
        bounded.findById("B");
        check(loads.get() == 6, "Invalidation failed");

        // Concurrent callers construct a lazy target only once.
        AtomicInteger builds = new AtomicInteger();
        var lazy = new LazyDocumentRepository(() -> {
            builds.incrementAndGet();
            return remote;
        });
        check(builds.get() == 0, "Lazy proxy constructed eagerly");
        var pool = Executors.newFixedThreadPool(4);
        try {
            List<Callable<Document>> tasks = new ArrayList<>();
            for (int i = 0; i < 8; i++) tasks.add(() -> lazy.findById("A"));
            for (var result : pool.invokeAll(tasks)) result.get();
        } finally {
            pool.shutdown();
        }
        check(builds.get() == 1, "Lazy target was constructed more than once");

        // Cache hits do not consume this remote-call quota.
        time.set(0);
        var limiter = new FixedWindowRateLimiter(1,
                Duration.ofNanos(10), time::get);
        var limitedCache = new SimpleCachedRepository(
                new RateLimitedRepository(remote, limiter));
        limitedCache.findById("X");
        limitedCache.findById("X");
        expect(RateLimitExceededException.class, () -> limitedCache.findById("Y"));
        time.set(10);
        limitedCache.findById("Y");

        // Outer audit sees authorization failures.
        List<AuditEvent> events = new ArrayList<>();
        var audited = new AuditedRepository(protectedRemote, events::add, user);
        expect(AccessDeniedException.class, () -> audited.findById("SECRET"));
        check(events.size() == 2
                && events.get(0).outcome().equals("ATTEMPT")
                && events.get(1).outcome().equals("FAILURE"), "Denied read was not audited");

        // A failed failure-log write must not hide the original error.
        RuntimeException original = new IllegalStateException("storage down");
        var auditFailureProxy = new AuditedRepository(id -> { throw original; }, event -> {
            if (event.outcome().equals("FAILURE")) throw new IllegalArgumentException("log down");
        }, user);
        RuntimeException caught = expect(IllegalStateException.class,
                () -> auditFailureProxy.findById("A"));
        check(caught == original && caught.getSuppressed().length == 1,
                "Original failure was lost");

        // Full composition: one remote read, two audited successes, one denial.
        AtomicInteger fullLoads = new AtomicInteger();
        List<AuditEvent> fullAudit = new ArrayList<>();
        DocumentRepository repository = buildDocumentRepository(
                () -> id -> {
                    fullLoads.incrementAndGet();
                    return new Document(id, "body");
                }, (who, id) -> {
                    if (id.equals("SECRET")) throw new AccessDeniedException();
                }, user, fullAudit::add, () -> true);
        repository.findById("PUBLIC");
        repository.findById("PUBLIC");
        expect(AccessDeniedException.class, () -> repository.findById("SECRET"));
        check(fullLoads.get() == 1 && fullAudit.size() == 6,
                "Composition semantics changed");
        System.out.println("ProxyLesson: all checks passed");
    }
}
```

### DynamicProxyDemo.java

Show sourceCopyDownload .java

DynamicProxyDemo.java

```
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.Objects;

public final class DynamicProxyDemo {
    public interface PaymentService {
        void charge(long cents);
    }

    public static final class DemoPaymentService implements PaymentService {
        @Override
        public void charge(long cents) {
            if (cents <= 0) throw new IllegalArgumentException("Positive cents required");
            System.out.println("Charging " + cents);
        }
    }

    public static final class LoggingHandler implements InvocationHandler {
        private final Object target;

        public LoggingHandler(Object target) {
            this.target = Objects.requireNonNull(target);
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args)
                throws Throwable {
            // Explicit identity semantics for this teaching proxy.
            if (method.getDeclaringClass() == Object.class) {
                return switch (method.getName()) {
                    case "equals" -> proxy == args[0];
                    case "hashCode" -> System.identityHashCode(proxy);
                    case "toString" -> "LoggingProxy["
                            + target.getClass().getSimpleName() + "]";
                    default -> throw new AssertionError(method);
                };
            }
            System.out.println("Calling " + method.getName());
            try {
                return method.invoke(target, args);
            } catch (InvocationTargetException failure) {
                throw failure.getCause();
            }
        }
    }

    public static void main(String[] args) {
        PaymentService target = new DemoPaymentService();
        PaymentService proxy = (PaymentService) Proxy.newProxyInstance(
                PaymentService.class.getClassLoader(),
                new Class<?>[] { PaymentService.class },
                new LoggingHandler(target));
        proxy.charge(5000);
        try {
            proxy.charge(-1);
            throw new AssertionError("Expected IllegalArgumentException");
        } catch (IllegalArgumentException expected) {
            // Original unchecked exception survives the reflective call.
        }
        if (!proxy.equals(proxy) || proxy.equals(target)
                || proxy.hashCode() != System.identityHashCode(proxy)
                || !proxy.toString().equals("LoggingProxy[DemoPaymentService]")) {
            throw new AssertionError("Object method policy failed");
        }
        System.out.println("DynamicProxyDemo: all checks passed");
    }
}
```

### HttpDocumentRepository.java

Show sourceCopyDownload .java

HttpDocumentRepository.java

```
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.regex.Pattern;

// Compile together with ProxyLesson.java. This class has no main method.
public final class HttpDocumentRepository
        implements ProxyLesson.DocumentRepository {
    private static final Pattern ID = Pattern.compile("[A-Za-z0-9_-]+");
    private final HttpClient client;
    private final URI base;

    public HttpDocumentRepository(HttpClient client, URI base) {
        this.client = Objects.requireNonNull(client);
        this.base = Objects.requireNonNull(base);
        if (!"https".equalsIgnoreCase(base.getScheme())
                || base.getHost() == null || base.getRawUserInfo() != null
                || base.getRawQuery() != null || base.getRawFragment() != null
                || !base.getPath().endsWith("/")) {
            throw new IllegalArgumentException("Expected HTTPS directory URI");
        }
    }

    @Override
    public ProxyLesson.Document findById(String id) {
        // Deliberately narrow ID contract: no arbitrary path input.
        if (id == null || !ID.matcher(id).matches()) {
            throw new IllegalArgumentException("Invalid document id");
        }
        HttpRequest request = HttpRequest.newBuilder(base.resolve(id))
                .timeout(Duration.ofSeconds(3))
                .header("Accept", "text/plain")
                .GET()
                .build();
        try {
            HttpResponse<String> response = client.send(request,
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            int status = response.statusCode();
            if (status == 404) throw new NoSuchElementException("Document not found");
            if (status == 401 || status == 403) {
                throw new ProxyLesson.AccessDeniedException();
            }
            if (status != 200) throw new RepositoryException("HTTP " + status);
            // Teaching endpoint contract: bounded, UTF-8 plain-text body.
            return new ProxyLesson.Document(id, response.body());
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            throw new RepositoryException("Document read interrupted", interrupted);
        } catch (IOException failure) {
            throw new RepositoryException("Document transport failed", failure);
        }
    }

    public static final class RepositoryException extends RuntimeException {
        public RepositoryException(String message) { super(message); }
        public RepositoryException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
```

Source controls work offline when JavaScript is enabled. Without JavaScript, all source is visible. Printing always includes the complete source and review notes.

REFERENCE

## Official Java 25 sources

The supplied Lesson 10 provides the design progression; these sources ground the JDK-specific behavior.

1. [Proxy · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html
2. [InvocationHandler · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/InvocationHandler.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/InvocationHandler.html
3. [Method.invoke · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Method.html#invoke(java.lang.Object,java.lang.Object...))https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Method.html#invoke(java.lang.Object,java.lang.Object...)
4. [HttpClient · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html
5. [HttpRequest.Builder · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.Builder.html
6. [LinkedHashMap · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/LinkedHashMap.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/LinkedHashMap.html
7. [ConcurrentHashMap · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html
8. [System.nanoTime · Java SE 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime())https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html#nanoTime()
9. [JLS 25 §17 · Threads and Locks](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html)https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html

Edition prepared 1 September 2026. The guide deliberately targets Java 25, including the versioned reflection and HTTP documentation.

DESIGN PATTERNS / LESSON 10Proxy · Java 25 edition