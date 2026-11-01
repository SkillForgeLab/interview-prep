[Skip to guide](#content)[DP / JAVA ARCHITECTURE](#top)

Lesson 14

From patterns to application architecture

1. [ADerive the boundary](#pressure)
2. [BSupply dependencies](#injection)
3. [CImplement persistence](#persistence)
4. [DShape the contract](#contract)
5. [ECompose the graph](#composition)
6. [FExpose dependencies](#dependencies)
7. [GConnect the patterns](#patterns)
8. [HTest and simplify](#testing)
9. [→CancelOrder exercise](#exercise)
10. [A1Runnable Java source](#runnable)
11. [B1Database checks](#jdbc)
12. [•Four decisions](#recap)
13. [↗Official sources](#sources)

38 topics · Complete source
Offline HTML · Print-ready
Verified sources: 01 Sep 2026

DP / Architecture series

Java 25 compatibleFirst principles

14

# Dependency Inversion, Dependency Injection & Repository

Start with a shipping use case. Let testing and persistence pressures reveal the boundary. Then supply the implementation and assemble the application.

Print / Save as PDF[Run the complete Java example →](#runnable)

Print in portrait at 100%. A4 is the default; Letter also works. Disable browser headers and footers if they duplicate the guide’s page labels.

## 01 / Dependency Inversion

Which direction should source-code dependencies point?

## 02 / Dependency Injection

Who supplies the collaborators an object needs?

## 03 / Repository

How does application code access persistent domain objects?

## 04 / Composition root

Where are implementations chosen and wired together?

**How to use this guide.** Read Parts A–H in order: they preserve the original lesson’s 38-step progression. Short snippets explain one idea at a time; Appendix A is the complete source of truth. The exercise comes before its reference solution. All content, styling, and controls are contained in this file.

PART A

## Derive the boundary

Original sections 1–4 · Let a concrete problem earn the abstraction.

### 01Start with working code

A command asks us to ship an order. The use case must load it, apply the shipping rule, and persist the result. Start with those three actions; architecture comes from the pressures around them.

Java • excerpt

```
public void handle(ShipOrderCommand command) {
    Order order = repository.findById(command.orderId());
    order.ship();
    repository.save(order);
}
```

The simplest handler might create its own `PostgresOrderRepository`. For a tiny program, that may be sufficient. The question is whether the coupling becomes costly.

Java • initial design sketch; not part of the runnable file

```
// Initial design sketch: concrete construction inside the handler.
private final PostgresOrderRepository repository =
    new PostgresOrderRepository();
```

### 02Introduce the first pressure: testing

We want to test the shipping rule without starting a database, preparing tables, or cleaning up rows. But a handler that constructs the concrete repository also chooses the storage implementation. The test has no ordinary constructor seam for substituting a fake.

**Separate two decisions**

The handler can know *what capability it requires* without deciding *which implementation supplies it*.

### 03Add pressure from implementation changes

A test may need in-memory storage while deployment uses PostgreSQL. A later adapter could use another database. If the handler branches on the environment to select storage, persistence configuration has entered the shipping use case.

Move that choice outside the handler. An interface does not make a database migration free: adapters must still agree on behavior, errors, and consistency.

### 04Ask what the handler actually needs

It needs to load an `Order` and save its changed state. Name that capability without naming the database.

Java • excerpt

```
public interface OrderRepository {
    Order findById(String id);
    void save(Order order);
}
```

For this guide, `findById` returns a detached order or throws `OrderNotFoundException`. `save` updates an existing order and throws the same exception if it is absent. The fake and JDBC adapter follow this contract.

| Source-code dependency | Why it exists |
| --- | --- |
| ShipOrderHandler → OrderRepository | The application requires a persistence capability. |
| JdbcOrderRepository → OrderRepository | Infrastructure implements that capability. |
| Both → Order | The contract speaks in domain objects. |

The abstraction is controlled by the application/domain side. High-level policy no longer names the database implementation. That is the dependency inversion in this design. [[1]](#ref-1)

PART B

## Supply the dependency

Original sections 5–9 · Make construction explicit, then test the use case.

### 05Distinguish inversion from injection

**Dependency inversion** is about source dependencies and ownership of the abstraction. **Dependency injection** is about supplying a collaborator from outside.

Java • excerpt

```
public ShipOrderHandler(OrderRepository repository) {
    this.repository = Objects.requireNonNull(repository, "repository");
}
```

The constructor is an injection point. This call supplies the dependency:

Java • excerpt

```
OrderRepository repository = new JdbcOrderRepository(dataSource);
ShipOrderHandler handler = new ShipOrderHandler(repository);
```

**Precision matters**

A field whose type is an interface is not, by itself, proof of dependency inversion. Check which layer owns the contract and whether its methods still expose infrastructure types.

### 06Dependency injection is plain Java

The `new ShipOrderHandler(repository)` call already performs constructor injection. A container can automate assembly, but annotations and a framework are not prerequisites. The collaborator is received instead of constructed or looked up inside the handler. [[2]](#ref-2)

### 07Make mandatory dependencies constructor arguments

Java • excerpt

```
public final class ShipOrderHandler {
    private final OrderRepository repository;

    public ShipOrderHandler(OrderRepository repository) {
        this.repository = Objects.requireNonNull(
            repository, "repository");
    }

    public void handle(ShipOrderCommand command) {
        Objects.requireNonNull(command, "command");
        Order order = repository.findById(command.orderId());
        order.ship();
        repository.save(order);
    }
}
```

Ordinary construction either supplies a non-null repository or fails immediately. `final` prevents reassignment of the reference; it does not make the repository object immutable or thread-safe. Oracle documents `requireNonNull` specifically for checks such as constructor parameter validation. [[3]](#ref-3)

### 08Compare setter and field injection

Java • excerpt

```
// Illustrative alternative: a mandatory dependency can be missing.
private OrderRepository repository;

public void setRepository(OrderRepository repository) {
    this.repository = repository;
}
```

Now construction and configuration happen separately. A caller can invoke the handler before assigning the repository. Field injection similarly hides required collaborators from ordinary constructor calls. Use constructor injection for mandatory collaborators; setters can be useful for genuinely optional, safely defaulted or reconfigurable dependencies. [[2]](#ref-2)

### 09Use a fake that can catch a missing save

An in-memory adapter lets us test orchestration and real domain behavior together. But storing and returning the same mutable `Order` reference is misleading: `order.ship()` could change the stored object even if the handler forgets `save()`.

The complete example stores immutable snapshots and restores a new `Order` on each read. Changing that order does not change storage until an explicit save.

Java • executable-check excerpt; helpers in Appendix A

```
var repository = new InMemoryOrderRepository();
repository.seed(Order.packed("O-123"));
var handler = new ShipOrderHandler(repository);

handler.handle(new ShipOrderCommand("O-123"));

equal(OrderStatus.SHIPPED,
      repository.findById("O-123").status());
equal(1, repository.saveCalls());
```

**What this test establishes**

The handler applies the shipping rule and asks the repository to persist it. It does not establish that SQL, a JDBC driver, or a real transaction works.

PART C

## Implement the persistence boundary

Original sections 10–15 · Keep the contract stable while the adapter handles SQL.

### 10Understand what Repository represents

A repository offers an application-facing view of persisted domain objects. The use case asks for an order; it does not navigate a result set. The adapter handles retrieval and mapping at the persistence boundary. [[4]](#ref-4)

| Application vocabulary | Infrastructure vocabulary |
| --- | --- |
| Find an Order | SELECT, parameters, ResultSet |
| Save changed Order state | UPDATE, row counts, driver errors |
| OrderStatus.SHIPPED | A stored status value |

For a rich domain model, a repository usually centers on an aggregate root: the object through which a related set of business invariants is enforced. It need not mirror one database table. [[4]](#ref-4)

### 11Place SQL in infrastructure

| Package | Contents | Allowed direction in this example |
| --- | --- | --- |
| domain | Order, OrderStatus, OrderRepository, OrderNotFoundException, RepositoryException | JDK and domain types |
| application | ShipOrderCommand, ShipOrderHandler | Domain and its repository contract |
| infrastructure | JdbcOrderRepository | Domain contract plus JDBC |
| web | OrderController | Application entry point plus HTTP framework |
| bootstrap | Application or OrdersConfiguration | Concrete implementations needed for assembly |

This is one deliberate package layout. If a persistence port is specific to an application use case, an `application.port` package can own it instead. Preserve inward dependency direction; do not turn a folder convention into a universal law.

**About the downloadable example**

All declarations are nested in one class so one source file is easy to run. That packaging is for the lesson. Split the declarations into the packages above when practicing compile-time boundaries.

### 12Implement the JDBC boundary

Inject `javax.sql.DataSource` into the JDBC adapter. Despite the `javax` name, it is a Java 25 API. It is a factory for database connections; a concrete driver or pool supplies the implementation. [[5]](#ref-5)

Java • excerpt

```
private final DataSource dataSource;

public JdbcOrderRepository(DataSource dataSource) {
    this.dataSource = Objects.requireNonNull(dataSource, "dataSource");
}
```

The load path prepares SQL, binds an ID, executes the query, handles absence, and maps the row. The full implementation in Appendix A closes the connection, statement, and result set with try-with-resources.

Java • excerpt

```
String sql = """
    SELECT id, status FROM orders WHERE id = ?
    """;
// Inside the resource scopes shown in Appendix A:
statement.setString(1, id);
try (ResultSet result = statement.executeQuery()) {
    if (!result.next()) {
        throw new OrderNotFoundException(id);
    }
    return mapOrder(result);
}
```

SQL exceptions are translated to `RepositoryException` with the original cause retained. Application signatures contain no `Connection`, `ResultSet`, or checked `SQLException`. Parameter binding and result access follow the Java 25 JDBC APIs. [[6]](#ref-6)[[7]](#ref-7)

### 13Map representations at the boundary

Java • excerpt

```
private Order mapOrder(ResultSet result) throws SQLException {
    String id = result.getString("id");
    String status = result.getString("status");
    try {
        return Order.restore(id, OrderStatus.valueOf(status));
    } catch (IllegalArgumentException | NullPointerException ex) {
        throw new RepositoryException("Invalid stored order", ex);
    }
}
```

`restore` reconstructs an existing state; it does not replay a shipping operation. Persisted status strings must match the enum mapping. If that representation changes, update the adapter and migration deliberately.

### 14Keep business rules in the domain object

Java • simplified Order method; full version in Appendix A

```
public void ship() {
    if (status != OrderStatus.PACKED) {
        throw new IllegalStateException("Only packed orders can ship");
    }
    status = OrderStatus.SHIPPED;
}
```

For this lesson, only a packed order may ship. The entity enforces that rule; the handler sequences load, ship, and save; the repository persists. Keeping those responsibilities separate lets the shipping rule run without a database.

**A scoped design choice**

An entity with persistence methods is a different style, often called Active Record. This guide deliberately uses a persistence-independent domain model; it is not claiming that every CRUD application needs the same structure.

### 15Save explicitly—and notice what it does not guarantee

Java • excerpt

```
String sql = """
    UPDATE orders SET status = ? WHERE id = ?
    """;
statement.setString(1, order.status().name());
statement.setString(2, order.id());
int updated = statement.executeUpdate();
if (updated == 0) {
    throw new OrderNotFoundException(order.id());
}
if (updated != 1) {
    throw new RepositoryException("Expected exactly one updated row");
}
```

This is an **update-only contract**, not an insert or upsert. Fixtures use `seed`; order creation would require a separate, explicitly designed operation.

**Transaction and concurrency boundary**

The teaching adapter opens a connection per method and requires auto-commit. Loading and saving therefore do not form one transaction. JDBC connections default to auto-commit, but a configured data source can change that setting. [[8]](#ref-8)

A second request can change an order between the read and write. An unconditional update can overwrite that change. A production design must choose a consistency strategy, such as a version column with a conditional update, or appropriate locking within a use-case transaction. Merely adding the word “Repository” provides neither.

If multiple writes must succeed together, define the transaction around the use case and make every participating adapter use that transaction. A transaction alone at the default isolation level is not automatically protection against every lost update.

PART D

## Keep the abstraction useful

Original sections 16–19 · A good boundary expresses a need, not a checklist of methods.

### 16Let repository methods express actual needs

Do not start by giving every entity a generic API with `findAll`, `query`, `delete`, `update`, and `save`. First ask which operations this use case needs. Here, load and save are enough.

Generics are useful when they capture repeated semantics. They add little when they merely rename a database API or force unrelated aggregates into one contract.

### 17Avoid leaking a query engine upward

| Leaky contract | Application-facing contract |
| --- | --- |
| `ResultSet executeQuery(String sql)` | `Order findById(String id)` |
| `EntityManager entityManager()` | `List<Order> findReadyToShip()` |
| `JdbcTemplate jdbcTemplate()` | A named operation with defined results and errors |

The latter query is an example of how to name a capability, not part of this guide’s minimal interface. If absence is ordinary, an `Optional<Order>` return can be appropriate. Choose and document one absence contract; this guide consistently throws for a missing order.

### 18Treat DAO versus Repository as an intent distinction

| Term | Typical emphasis | Illustrative operation |
| --- | --- | --- |
| DAO | Persistence and data access operations | `updateStatus(id, statusText)` |
| Repository | Domain objects and aggregate-oriented access | `save(order)` |

These names overlap in real frameworks. Spring even describes `@Repository` in terms that include DAO. Use this distinction to discuss the boundary, not to infer behavior from a class name. [[9]](#ref-9)

### 19Know when another layer is unnecessary

If an existing persistence abstraction already meets a small CRUD application’s needs, adding a repository interface, implementation, adapter, and mapper may create maintenance work without isolating a meaningful concern.

Add a boundary when it protects business rules, separates a volatile technology, gives useful substitution, or expresses domain-oriented operations. Do not add it just to complete a diagram.

PART E

## Assemble the object graph

Original sections 20–24 · Plain Java first; framework automation second.

### 20Find the place that chooses implementations

The concrete repository still has to be created. Put assembly near the entry point: the **composition root**. It chooses implementations, supplies configuration, and constructs the object graph.

Java • excerpt

```
OrderRepository repository = new JdbcOrderRepository(dataSource);
ShipOrderHandler handler = new ShipOrderHandler(repository);
```

The composition root is allowed to know the concrete classes. The shipping handler is not responsible for that choice.

### 21Write a plain Java composition root

Java • runnable composition excerpt from Lesson14

```
public static void main(String[] args) {
    var repository = new InMemoryOrderRepository();
    repository.seed(Order.packed("O-123"));

    var handler = new ShipOrderHandler(repository);
    handler.handle(new ShipOrderCommand("O-123"));

    System.out.println(repository.findById("O-123").status());
}
```

This graph is complete without a server. For a database deployment, the root supplies a configured `DataSource`, constructs `JdbcOrderRepository`, and passes it to the same handler. Driver settings, pool lifetime, and server startup belong to deployment wiring.

### 22Separate runtime calls from source dependencies

| View | Relationship | Meaning |
| --- | --- | --- |
| Runtime call | Handler → JDBC repository object | The selected implementation executes the call. |
| Source dependency | Handler → OrderRepository | The handler compiles against the contract. |
| Implementation dependency | JdbcOrderRepository → OrderRepository | The adapter implements that contract. |
| Assembly | Composition root → both concrete classes | The entry point chooses and connects the objects. |

Runtime control still reaches the database. What changed is which source types the high-level code needs to name. [[1]](#ref-1)

### 23Introduce Spring after the design works

Spring can perform the assembly we just wrote by hand. Explicit `@Bean` methods keep the relationship visible and let the domain and handler stay free of Spring annotations. [[10]](#ref-10)

Java • optional Spring configuration; assumes split top-level lesson classes

```
import javax.sql.DataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration(proxyBeanMethods = false)
public class OrdersConfiguration {
    @Bean
    OrderRepository orderRepository(DataSource dataSource) {
        return new JdbcOrderRepository(dataSource);
    }

    @Bean
    ShipOrderHandler shipOrderHandler(OrderRepository repository) {
        return new ShipOrderHandler(repository);
    }
}
```

This configuration assumes a `DataSource` bean and the application classes already exist. It is not a standalone Spring project. Component scanning with `@Repository`, `@Service`, and controller annotations is another registration style. Neither style changes what dependency inversion means. [[9]](#ref-9)

**Keep the two examples separate**

The complete downloadable Java file uses only JDK APIs. This optional snippet requires Spring dependencies. If you later add transaction or other AOP advice, review proxy requirements: class-based proxies cannot subclass final classes. The plain Java handler needs no proxy. [[11]](#ref-11)

### 24Distinguish the annotation from the pattern

| Name | What it is |
| --- | --- |
| `OrderRepository` | Our application/domain contract for persistence. |
| `@Repository` | A Spring stereotype for a persistence component; it also participates in exception-translation infrastructure when that support is configured. |

The pattern can exist with no Spring annotation. The annotation alone does not prove that a class presents a useful domain boundary. [[9]](#ref-9)

PART F

## Make dependencies honest

Original sections 25–29 · Visibility and ownership matter more than annotation count.

### 25Prefer visible dependencies to Service Locator

| Constructor injection | Service Locator |
| --- | --- |
| `new ShipOrderHandler(repository)` | The handler calls `ServiceLocator.get(...)` internally. |
| Requirements are visible at construction. | Requirements are discovered by reading implementation or running code. |
| Each test supplies its collaborator directly. | Tests may need locator configuration and cleanup. |

A service locator can be an intentional framework mechanism. Reaching into it from business code hides that code’s needs and couples it to the locating environment. Prefer the explicit constructor boundary here. [[2]](#ref-2)

### 26Recognize the same issue in static globals

A call such as `Database.getInstance()` inside the handler hides a collaborator just as a locator does. Replacing that global access with a constructor argument makes the requirement visible and individually substitutable.

The issue is hidden access to external state. A pure static helper for deterministic string validation is not the same architectural problem.

### 27Read a large constructor as design feedback

A constructor with many collaborators may expose an overloaded responsibility. Review whether the class is mixing several use cases or concerns. Hiding them through field injection removes the signal while keeping the coupling. Spring’s DI guidance also identifies excessive constructor arguments as a possible responsibility problem. [[2]](#ref-2)

There is no magic maximum. Group collaborators only when they form a coherent capability; an arbitrary “Dependencies” bag just hides the original list.

### 28Keep inversion and injection separate in your vocabulary

| Example | Injection? | Inversion at the persistence boundary? |
| --- | --- | --- |
| `ShipOrderHandler(JdbcOrderRepository r)` | Yes: receives a collaborator. | No: names the infrastructure class. |
| `ShipOrderHandler(OrderRepository r)` with an inward-owned, persistence-neutral port | Yes. | Yes, for this boundary. |
| Interface-typed field initialized with `new JdbcOrderRepository(...)` inside the handler | No external supply for that dependency. | The handler still names infrastructure. |

DI is a construction technique. DIP is a dependency-direction principle. They work together, but neither term is a synonym for the other.

### 29Let the consumer’s need shape the interface

The application says, “I need to retrieve and persist Orders.” Infrastructure answers, “I can provide that using JDBC.” If the database layer dictates a contract full of its own types, the high-level code remains shaped by the detail.

Place the interface where its meaning belongs: in the domain for a domain-level repository, or with an application port for a use-case-specific need. The adapter depends on that owned contract.

PART G

## Connect patterns into architecture

Original sections 30–34 · Each pattern solves a different part of the same use case.

### 30Connect Repository to Adapter

`JdbcOrderRepository` adapts JDBC’s connection/row vocabulary to the `OrderRepository` vocabulary the use case wants. That relationship extends naturally to payment, email, and storage adapters in Ports and Adapters architecture.

### 31Connect assembly to Factory

Java • composition sketch; factory and config are illustrative

```
OrderRepository repository = repositoryFactory.create(config);
ShipOrderHandler handler = new ShipOrderHandler(repository);
```

The factory chooses or creates an implementation. Dependency injection supplies that implementation to its consumer. A small composition root may need no factory at all.

### 32Connect the port to Proxy and Decorator

Java • wrapper composition sketch; wrapper classes are not implemented here

```
OrderRepository repository = new AuditingOrderRepository(
    new CachingOrderRepository(
        new JdbcOrderRepository(dataSource)));
```

A wrapper can preserve the repository interface while adding behavior. Decide what a cache returns, how saves invalidate it, and whether auditing runs before or after delegation. Sharing cached mutable Orders can recreate the same aliasing bug as a weak fake.

The interface makes composition possible; it does not guarantee that a wrapper preserves persistence semantics.

### 33Connect the use case to Command

| Element | Owns this responsibility |
| --- | --- |
| Controller / incoming adapter | Translate the transport request into an application call. |
| ShipOrderCommand | Carry the requested order ID. |
| ShipOrderHandler | Load, invoke the domain behavior, then save. |
| Order | Enforce the packed-to-shipped rule. |
| OrderRepository | Declare the persistence capability. |
| JdbcOrderRepository | Execute SQL and map persisted data. |

A Java record is suitable for the command’s small data payload. Its generated constructor, accessors, and value methods avoid routine boilerplate. Records are supported in Java 25; they do not require preview features. [[12]](#ref-12)

### 34See the minimal architecture as boundaries

| Boundary | Incoming knowledge | Outgoing knowledge |
| --- | --- | --- |
| Domain | Business inputs and existing state | Its own invariants and owned contracts |
| Application | Commands from any entry point | Domain objects and required ports |
| Infrastructure | Calls through the port | JDBC, schemas, driver behavior |
| Web / CLI | HTTP or command-line input | Application handler |
| Composition root | Deployment choices | All pieces needed for assembly |

In this example, `Order` never calls the repository itself. The handler coordinates both. This avoids a misleading graph in which the entity appears to depend on SQL or perform persistence.

PART H

## Test the design and keep it small

Original sections 35–38 · Prove behavior at the boundary where it lives.

### 35Test each boundary at the right level

| Test level | Use real objects for | What the test proves |
| --- | --- | --- |
| Domain unit | Order | Packed can ship; cancelled or shipped cannot ship again. |
| Application unit | Handler + Order + detached-state fake | Correct orchestration, explicit save, and no save after rejection. |
| Infrastructure integration | JDBC repository + actual database/driver | SQL syntax, mapping, absent rows, constraints, and chosen transaction/concurrency behavior. |

Run integration tests against isolated test data. A fake is useful for application logic; it cannot prove database behavior. [[4]](#ref-4)

Java • failure-path check; helpers in Appendix A

```
var repository = new InMemoryOrderRepository();
repository.seed(Order.restore("R1", OrderStatus.CANCELLED));
var handler = new ShipOrderHandler(repository);

expectThrows(IllegalStateException.class,
    () -> handler.handle(new ShipOrderCommand("R1")));
equal(0, repository.saveCalls());
```

### 36Do not mock everything

Use the real domain object when its logic is fast and deterministic. Substitute the persistence boundary when that removes infrastructure from the test. Use a mock or spy when a particular interaction is the behavior you need to observe.

The in-memory adapter here deliberately stores snapshots. That extra care makes it a useful fake for this contract, but it still does not model database concurrency.

### 37Do not create an interface for every class

An interface earns its place when it separates policy from detail, isolates an external system, represents real variation, or establishes a valuable test boundary. `ShipOrderHandlerInterface` would add little here. The handler can stay a concrete application class.

Start with the pressure. Count meaningful boundaries, not interface files.

### 38Repeat the first-principles process

1. **Name the job.** What must this class accomplish?
2. **Identify the capability.** What does it need from another object?
3. **Question concrete knowledge.** Would naming the implementation couple policy to a volatile detail?
4. **Define the boundary.** If useful, express a small, consumer-shaped contract.
5. **Supply the implementation.** Make required collaborators constructor arguments.
6. **Assemble at the entry point.** Choose implementations in the composition root.
7. **Test the contracts.** Separate domain, orchestration, and infrastructure evidence.

**The question to carry forward**

Which layer should own each dependency? Framework configuration cannot repair an abstraction that points in the wrong direction.

PART PRACTICE

## Build CancelOrder

Apply the boundary, injection, and ownership decisions yourself.

Build a `CancelOrder` use case by applying the same reasoning. Start with a handler that creates a concrete JDBC repository or reaches into a global database object. Refactor it so the application expresses its need and receives an implementation.

**Rules for this exercise**

Only a `PACKED` order may be cancelled. A `SHIPPED` or already `CANCELLED` order is rejected with `IllegalStateException`. Missing orders raise `OrderNotFoundException`. These are lesson rules, not universal commerce policy.

1. `CancelOrderHandler` contains no `new Jdbc…` and no global database lookup.
2. The handler contains no JDBC imports or types.
3. `Order` owns the cancellation rule and contains no persistence code.
4. `OrderRepository` expresses the operations and errors the application needs.
5. Unit checks use an in-memory repository and prove that a successful cancellation was saved.
6. JDBC behavior has separate integration tests against a database.
7. Constructor parameters expose all mandatory handler collaborators.
8. One composition location chooses and wires the concrete implementation.
9. Rejected cancellation never calls `save` and leaves stored state unchanged.

**Explain your design:** who owns the repository interface, where does the real implementation get selected, and which test would fail if `save()` were deleted?

The runnable source includes a cancellation reference in Appendix A5. Try the design first, then compare responsibilities—not just class names.

PART APPENDIX A

## Run the complete example

One source file · Stable Java syntax · No preview features.

Save the complete source as `Lesson14.java`. The button downloads exactly the source blocks in this appendix, in order. They include every required type, the JDBC adapter, a cancellation reference, and a small check harness. No build tool or third-party library is needed to compile the core file.

Download Lesson14.javaCopy complete Java source

Terminal • run with a JDK 25 installation

```
javac --release 25 Lesson14.java
java Lesson14
```

`--release 25` checks language rules and APIs for Java 25. [[13]](#ref-13)

Expected output

```
All 9 checks passed.
O-123: SHIPPED
```

**Validation record**

The full source compiled with `-Xlint:all` and all nine checks passed on the available JDK 17.0.20. It uses stable Java features and APIs checked against the Java 25 documentation. ⚠️ A JDK 25 runtime was not available for a direct execution check. The JDBC adapter was compiled; no PostgreSQL integration test was run.

The explicit check helpers throw `AssertionError` on failure, so these checks do not depend on enabling JVM `assert` statements. The main method runs the checks and then assembles the small demonstration graph.

### A1 · Imports and domain model

Lesson14.java • continuous source, part 1 of 6

```
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import javax.sql.DataSource;

public final class Lesson14 {
    private Lesson14() {}

    // A1: DOMAIN. No SQL or framework types in these declarations.
    public enum OrderStatus { PACKED, SHIPPED, CANCELLED }

    public static final class Order {
        private final String id;
        private OrderStatus status;

        private Order(String id, OrderStatus status) {
            this.id = requireId(id);
            this.status = Objects.requireNonNull(status, "status");
        }

        public static Order packed(String id) {
            return new Order(id, OrderStatus.PACKED);
        }

        public static Order restore(String id, OrderStatus status) {
            return new Order(id, status);
        }

        public String id() { return id; }
        public OrderStatus status() { return status; }

        public void ship() {
            requirePacked("ship");
            status = OrderStatus.SHIPPED;
        }

        public void cancel() {
            requirePacked("cancel");
            status = OrderStatus.CANCELLED;
        }

        private void requirePacked(String action) {
            if (status != OrderStatus.PACKED) {
                throw new IllegalStateException(
                    "Cannot " + action + " order in state " + status);
            }
        }
    }

    private static String requireId(String id) {
        Objects.requireNonNull(id, "orderId");
        if (id.isBlank() || id.length() > 64) {
            throw new IllegalArgumentException(
                "orderId must contain 1 to 64 characters, not all blank");
        }
        return id;
    }
```

### A2 · Repository port, command, handler, and errors

Lesson14.java • continuous source, part 2 of 6

```
    // A2: PORT AND APPLICATION. Save updates an existing order only.
    public interface OrderRepository {
        // Returns a detached order; throws OrderNotFoundException if absent.
        Order findById(String id);
        // Throws OrderNotFoundException if the order is absent.
        void save(Order order);
    }

    public record ShipOrderCommand(String orderId) {
        public ShipOrderCommand { requireId(orderId); }
    }

    public static final class ShipOrderHandler {
        private final OrderRepository repository;

        public ShipOrderHandler(OrderRepository repository) {
            this.repository = Objects.requireNonNull(
                repository, "repository");
        }

        public void handle(ShipOrderCommand command) {
            Objects.requireNonNull(command, "command");
            Order order = repository.findById(command.orderId());
            order.ship();
            repository.save(order);
        }
    }

    public static final class OrderNotFoundException
            extends RuntimeException {
        private static final long serialVersionUID = 1L;
        public OrderNotFoundException(String id) {
            super("Order not found: " + id);
        }
    }

    public static final class RepositoryException
            extends RuntimeException {
        private static final long serialVersionUID = 1L;
        public RepositoryException(String message) { super(message); }
        public RepositoryException(String message, Throwable cause) {
            super(message, cause);
        }
    }
```

### A3 · In-memory repository with detached reads

Lesson14.java • continuous source, part 3 of 6

```
    // A3: TEST ADAPTER. Snapshots prevent shared-mutation false positives.
    public static final class InMemoryOrderRepository
            implements OrderRepository {
        private record Snapshot(String id, OrderStatus status) {}
        private final Map<String, Snapshot> orders = new HashMap<>();
        private int saveCalls;

        public void seed(Order order) {
            Objects.requireNonNull(order, "order");
            Snapshot snapshot = new Snapshot(order.id(), order.status());
            if (orders.putIfAbsent(order.id(), snapshot) != null) {
                throw new IllegalArgumentException("Duplicate fixture id");
            }
        }

        @Override
        public Order findById(String id) {
            Snapshot snapshot = orders.get(requireId(id));
            if (snapshot == null) {
                throw new OrderNotFoundException(id);
            }
            return Order.restore(snapshot.id(), snapshot.status());
        }

        @Override
        public void save(Order order) {
            Objects.requireNonNull(order, "order");
            saveCalls++;
            if (!orders.containsKey(order.id())) {
                throw new OrderNotFoundException(order.id());
            }
            orders.put(order.id(), new Snapshot(order.id(), order.status()));
        }

        public int saveCalls() { return saveCalls; }
    }
```

### A4 · Complete JDBC repository

This adapter intentionally requires auto-commit and opens one connection per operation. It demonstrates mapping and dependency boundaries; it does not implement a transaction spanning the use case or concurrent-update protection.

Lesson14.java • continuous source, part 4 of 6

```
    // A4: JDBC ADAPTER. Requires auto-commit connections, by design.
    // Each operation is independent; this is NOT a use-case transaction.
    public static final class JdbcOrderRepository
            implements OrderRepository {
        private final DataSource dataSource;

        public JdbcOrderRepository(DataSource dataSource) {
            this.dataSource = Objects.requireNonNull(
                dataSource, "dataSource");
        }

        @Override
        public Order findById(String id) {
            requireId(id);
            String sql = """
                SELECT id, status FROM orders WHERE id = ?
                """;
            try (Connection connection = dataSource.getConnection()) {
                requireAutoCommit(connection);
                try (PreparedStatement statement =
                        connection.prepareStatement(sql)) {
                    statement.setString(1, id);
                    try (ResultSet result = statement.executeQuery()) {
                        if (!result.next()) {
                            throw new OrderNotFoundException(id);
                        }
                        return mapOrder(result);
                    }
                }
            } catch (SQLException exception) {
                throw new RepositoryException("Load failed", exception);
            }
        }

        private Order mapOrder(ResultSet result) throws SQLException {
            String id = result.getString("id");
            String status = result.getString("status");
            try {
                return Order.restore(id, OrderStatus.valueOf(status));
            } catch (IllegalArgumentException | NullPointerException ex) {
                throw new RepositoryException("Invalid stored order", ex);
            }
        }

        @Override
        public void save(Order order) {
            Objects.requireNonNull(order, "order");
            String sql = """
                UPDATE orders SET status = ? WHERE id = ?
                """;
            try (Connection connection = dataSource.getConnection()) {
                requireAutoCommit(connection);
                try (PreparedStatement statement =
                        connection.prepareStatement(sql)) {
                    statement.setString(1, order.status().name());
                    statement.setString(2, order.id());
                    int updated = statement.executeUpdate();
                    if (updated == 0) {
                        throw new OrderNotFoundException(order.id());
                    }
                    if (updated != 1) {
                        throw new RepositoryException(
                            "Expected exactly one updated row");
                    }
                }
            } catch (SQLException exception) {
                throw new RepositoryException("Save failed", exception);
            }
        }

        private void requireAutoCommit(Connection connection)
                throws SQLException {
            if (!connection.getAutoCommit()) {
                throw new RepositoryException(
                    "This teaching adapter requires auto-commit");
            }
        }
    }
```

### A5 · CancelOrder reference solution

Lesson14.java • continuous source, part 5 of 6

```
    // A5: EXERCISE REFERENCE. Try the exercise before reading this part.
    public record CancelOrderCommand(String orderId) {
        public CancelOrderCommand { requireId(orderId); }
    }

    public static final class CancelOrderHandler {
        private final OrderRepository repository;

        public CancelOrderHandler(OrderRepository repository) {
            this.repository = Objects.requireNonNull(
                repository, "repository");
        }

        public void handle(CancelOrderCommand command) {
            Objects.requireNonNull(command, "command");
            Order order = repository.findById(command.orderId());
            order.cancel();
            repository.save(order);
        }
    }
```

### A6 · Composition root and executable checks

Lesson14.java • continuous source, part 6 of 6

```
    // A6: COMPOSITION ROOT AND EXECUTABLE CHECKS. No testing library needed.
    public static void main(String[] args) {
        domainRule();
        savesShippedOrder();
        mutationNeedsSave();
        rejectedShipDoesNotSave();
        missingOrderDoesNotSave();
        dependencyIsRequired();
        cancelsPackedOrder();
        shippedOrderCannotBeCancelled();
        saveIsUpdateOnly();
        System.out.println("All 9 checks passed.");

        var repository = new InMemoryOrderRepository();
        repository.seed(Order.packed("O-123"));
        var handler = new ShipOrderHandler(repository);
        handler.handle(new ShipOrderCommand("O-123"));
        System.out.println("O-123: " + repository.findById("O-123").status());
    }

    private static void domainRule() {
        Order order = Order.packed("D1");
        order.ship();
        equal(OrderStatus.SHIPPED, order.status());
        expectThrows(IllegalStateException.class, order::ship);
    }

    private static void savesShippedOrder() {
        var repository = new InMemoryOrderRepository();
        repository.seed(Order.packed("S1"));
        new ShipOrderHandler(repository).handle(new ShipOrderCommand("S1"));
        equal(OrderStatus.SHIPPED, repository.findById("S1").status());
        equal(1, repository.saveCalls());
    }

    private static void mutationNeedsSave() {
        var repository = new InMemoryOrderRepository();
        repository.seed(Order.packed("M1"));
        Order loaded = repository.findById("M1");
        loaded.ship();
        equal(OrderStatus.PACKED, repository.findById("M1").status());
        repository.save(loaded);
        equal(OrderStatus.SHIPPED, repository.findById("M1").status());
        loaded = repository.findById("M1");
        equal(OrderStatus.SHIPPED, loaded.status());
    }

    private static void rejectedShipDoesNotSave() {
        var repository = new InMemoryOrderRepository();
        repository.seed(Order.restore("R1", OrderStatus.CANCELLED));
        var handler = new ShipOrderHandler(repository);
        expectThrows(IllegalStateException.class,
            () -> handler.handle(new ShipOrderCommand("R1")));
        equal(0, repository.saveCalls());
        equal(OrderStatus.CANCELLED, repository.findById("R1").status());
    }

    private static void missingOrderDoesNotSave() {
        var repository = new InMemoryOrderRepository();
        var handler = new ShipOrderHandler(repository);
        expectThrows(OrderNotFoundException.class,
            () -> handler.handle(new ShipOrderCommand("missing")));
        equal(0, repository.saveCalls());
    }

    private static void dependencyIsRequired() {
        expectThrows(NullPointerException.class,
            () -> new ShipOrderHandler(null));
    }

    private static void cancelsPackedOrder() {
        var repository = new InMemoryOrderRepository();
        repository.seed(Order.packed("C1"));
        new CancelOrderHandler(repository)
            .handle(new CancelOrderCommand("C1"));
        equal(OrderStatus.CANCELLED, repository.findById("C1").status());
        equal(1, repository.saveCalls());
    }

    private static void shippedOrderCannotBeCancelled() {
        var repository = new InMemoryOrderRepository();
        repository.seed(Order.restore("C2", OrderStatus.SHIPPED));
        var handler = new CancelOrderHandler(repository);
        expectThrows(IllegalStateException.class,
            () -> handler.handle(new CancelOrderCommand("C2")));
        equal(0, repository.saveCalls());
        equal(OrderStatus.SHIPPED, repository.findById("C2").status());
    }

    private static void saveIsUpdateOnly() {
        var repository = new InMemoryOrderRepository();
        expectThrows(OrderNotFoundException.class,
            () -> repository.save(Order.packed("absent")));
    }

    private static void equal(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError(
                "Expected " + expected + ", got " + actual);
        }
    }

    private static <T extends Throwable> void expectThrows(
            Class<T> expected, Runnable action) {
        try {
            action.run();
        } catch (Throwable actual) {
            if (expected.isInstance(actual)) {
                return;
            }
            throw new AssertionError("Unexpected exception", actual);
        }
        throw new AssertionError("Expected " + expected.getSimpleName());
    }
}
```

PART APPENDIX B

## Verify the database adapter

Make the persistence contract observable against the real technology.

The JDBC adapter compiles using JDK APIs. Running it also needs a PostgreSQL JDBC driver, a configured `DataSource`, and a database. Those external services are not embedded in the HTML. The in-memory path above is the complete standalone execution path.

SQL • minimal PostgreSQL schema and fixture

```
CREATE TABLE orders (
    id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(16) NOT NULL
        CHECK (status IN ('PACKED', 'SHIPPED', 'CANCELLED'))
);

INSERT INTO orders (id, status) VALUES ('O-123', 'PACKED');
```

The primary key makes the ID unique and non-null; the status constraint limits stored values. [[14]](#ref-14) The application validates IDs before it calls persistence. The schema is intentionally minimal; it does not model all of the Java ID-validation rules.

| Integration case | Required observation |
| --- | --- |
| Load seeded order | Correct ID and PACKED state are restored. |
| Save shipped order | A new connection reads SHIPPED from the database. |
| Load missing order | OrderNotFoundException is thrown. |
| Save absent order | No row is inserted; OrderNotFoundException is thrown. |
| Driver / SQL failure | RepositoryException retains the SQLException cause. |
| Concurrent commands | The intended lost-update strategy is verified once implemented. |
| Multi-write use case | Rollback is verified once a use-case transaction is implemented. |

**When adding Spring transactions**

Do not assume `@Transactional` makes this raw adapter participate in a managed transaction. Its direct per-method connection acquisition and auto-commit requirement are deliberate teaching constraints. Refactor to transaction-aware access, such as Spring’s documented `DataSourceUtils`/`JdbcTemplate` approach, with a transaction manager and a defined use-case boundary. [[15]](#ref-15)

PART REFERENCE

## Keep the four decisions separate

Return to these questions when the implementation starts to feel complicated.

| Idea | Question it answers | In this guide |
| --- | --- | --- |
| Dependency Inversion | Which direction should source dependencies point? | The handler and JDBC adapter depend on an inward-owned repository contract. |
| Dependency Injection | Who supplies the collaborator? | The composition root passes a repository to the handler constructor. |
| Repository | How does the use case access persistent domain objects? | Load and save Orders through an explicit contract. |
| Composition root | Where are implementations chosen and connected? | main, or optional Spring configuration at startup. |

**Next: Ports & Adapters / Hexagonal Architecture.** Extend the same reasoning from persistence to payment providers, email, clocks, and messaging—and from HTTP to CLI commands, scheduled jobs, and message consumers. Keep each external boundary explicit while the domain retains its rules.

PART SOURCES

## Documentation and verification

Java references are pinned to Java 25; framework guidance is linked to official documentation.

Official sources checked on 1 September 2026. Architecture guidance is adapted to this Java example; the business rules and design choices are defined explicitly in the guide.

1. [Microsoft Learn — Architectural principles](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles)

   Dependency inversion and the distinction between compile-time dependencies and runtime flow.

   https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles
2. [Spring Framework — Dependency Injection](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)

   Constructor and setter injection, explicit dependencies, and constructor-size guidance.

   https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html
3. [Oracle Java SE 25 — Objects](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Objects.html)

   requireNonNull constructor and method-argument validation.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Objects.html
4. [Microsoft Learn — Infrastructure persistence layer](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)

   Repositories, aggregates, adapters, and separation of application tests from persistence tests.

   https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design
5. [Oracle Java SE 25 — DataSource](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/javax/sql/DataSource.html)

   The standard connection-factory interface in javax.sql.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/javax/sql/DataSource.html
6. [Oracle Java SE 25 — PreparedStatement](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/PreparedStatement.html)

   Parameter binding, query execution, and update counts.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/PreparedStatement.html
7. [Oracle Java SE 25 — ResultSet](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/ResultSet.html)

   Row navigation, typed access, and closeable result resources.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/ResultSet.html
8. [Oracle Java SE 25 — Connection](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html)

   Auto-commit, commit/rollback, isolation, and connection semantics.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html
9. [Spring Framework — Classpath scanning and components](https://docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html)

   Repository, service, and controller stereotypes and component registration.

   https://docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html
10. [Spring Framework — @Bean and @Configuration](https://docs.spring.io/spring-framework/reference/core/beans/java/basic-concepts.html)

    Explicit Java-based container configuration.

    https://docs.spring.io/spring-framework/reference/core/beans/java/basic-concepts.html
11. [Spring Framework — Proxying mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)

    JDK proxies and the limitations of class-based proxying.

    https://docs.spring.io/spring-framework/reference/core/aop/proxying.html
12. [Oracle Java SE 25 — Record classes](https://docs.oracle.com/en/java/javase/25/language/records.html)

    Records, generated members, and compact constructors.

    https://docs.oracle.com/en/java/javase/25/language/records.html
13. [Oracle JDK 25 — javac command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

    The --release compiler option and target-platform checks.

    https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html
14. [PostgreSQL — Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

    Primary keys, not-null constraints, and check constraints.

    https://www.postgresql.org/docs/current/ddl-constraints.html
15. [Spring Framework — Controlling database connections](https://docs.spring.io/spring-framework/reference/data-access/jdbc/connections.html)

    Transaction-aware connection access and JDBC transaction integration.

    https://docs.spring.io/spring-framework/reference/data-access/jdbc/connections.html

DP · Lesson 14 · Java architectureProblem → capability → boundary → construction