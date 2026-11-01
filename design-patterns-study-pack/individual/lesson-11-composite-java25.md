[Skip to guide](#content)

[DP Design Patterns](#top)

Lesson 11

[01

Find the pressureSteps 1–4](#pressure)[02

Shared abstractionSteps 5–7](#abstraction)[03

Follow the recursionSteps 8–11](#recursion)[04

Behavior & alternativesSteps 12–14](#behavior)[05

Other domainsSteps 15–16](#domains)[06

API & invariantsSteps 17–21](#invariants)[07

Mutation & costSteps 22–24](#engineering)[08

Compare the conceptsSteps 25–28](#comparisons)[09

Use & test the patternSteps 29–32](#practice)[10

Organization exerciseTry it yourself](#exercise)[11

Pattern map & nextTemplate Method](#pattern-map)[A–D

Complete sourceFour runnable programs](#runnable)[Ref

Official referencesJava 25 documentation](#references)

One HTML file.
No external assets.
Ready to read offline.

Design patterns · Lesson 11

# Composite

11

Treat one object and a tree uniformly.

Start with a file. Add a folder. Add a folder inside a folder. Then derive the abstraction that lets a caller treat a part and a whole through the same meaningful operation.

Java 25 compatibleNo dependenciesFirst principles

Print / Save as PDF[Get runnable code](#runnable)

For PDF: use the browser’s Print command, portrait orientation, and standard A4 or Letter paper. All code and trace steps stay visible; navigation and buttons are omitted.

**Understand**The recursive type relationship.

**Implement**Leaves, containers, and client code.

**Question**Cycles, ownership, cost, and API design.

**How to use this guide**

Read the numbered steps in order. Early snippets show successive designs; they are not one concatenated program. Appendices A–D provide complete, independent files with executable checks.

## Contents

[01

Find the pressureSteps 1–4](#pressure)[02

Shared abstractionSteps 5–7](#abstraction)[03

Follow the recursionSteps 8–11](#recursion)[04

Behavior & alternativesSteps 12–14](#behavior)[05

Other domainsSteps 15–16](#domains)[06

API & invariantsSteps 17–21](#invariants)[07

Mutation & costSteps 22–24](#engineering)[08

Compare the conceptsSteps 25–28](#comparisons)[09

Use & test the patternSteps 29–32](#practice)[10

Organization exerciseTry it yourself](#exercise)[11

Pattern map & nextTemplate Method](#pattern-map)[A–D

Complete sourceFour runnable programs](#runnable)[Ref

Official referencesJava 25 documentation](#references)

Part 01 · Find the pressure

## Start with objects. Let the hierarchy reveal the pattern.

Composite is useful when one object and a group of similar objects should support the same operation. The file-system example makes the pressure concrete: a folder can contain files and more folders. Microsoft’s pattern explanation uses this same setting to motivate a shared interface. [[1]](#ref-1)

If leaves and containers mean the same thing to a caller, give them the same meaningful operations.

### 01Start with a file

A file knows its name and its own size. Nothing recursive is needed yet. In this guide, size means **logical bytes in the model**; it does not measure disk allocation, directory metadata, or a real file system.

JavaCopy

```
public final class FileItem {
    private final String name;
    private final long size;

    public FileItem(String name, long size) {
        this.name = name;
        this.size = size;
    }

    public long size() {
        return size;
    }
}
```

JavaCopy

```
var file = new FileItem("report.pdf", 5_000);
System.out.println(file.size()); // 5000
```

### 02Add directories that contain files

A directory can calculate its size by adding the sizes of its files. This first version needs only one collection.

JavaCopy

```
import java.util.ArrayList;
import java.util.List;

public final class Directory {
    private final String name;
    private final List<FileItem> files = new ArrayList<>();

    public Directory(String name) {
        this.name = name;
    }

    public void add(FileItem file) {
        files.add(file);
    }

    public long size() {
        long total = 0;
        for (FileItem file : files) {
            total += file.size();
        }
        return total;
    }
}
```

The constructor initializes `name`; it is not an omitted dependency. These early versions assume valid inputs. We add explicit invariants after establishing the design.

### 03Change the requirement: directories can contain directories

The model must now represent a hierarchy, not just a flat group of files.

One hierarchy, several levels

* root/
  + README.md *100 bytes*
  + src/
    - Main.java *500 bytes*
    - service/
      * OrderService.java *700 bytes*

The running example totals 1,300 logical bytes.

`List<FileItem>` cannot hold a `Directory`. The problem is a mismatch between the domain and the type of our collection.

### 04Try the obvious solution: two collections

We could add a separate `List<Directory>` and maintain both lists. Inside that version of `Directory`, the calculation becomes:

JavaCopy

```
public long size() {
    long total = 0;
    for (FileItem file : files) {
        total += file.size();
    }
    for (Directory directory : directories) {
        total += directory.size();
    }
    return total;
}
```

This works, but operations that inspect both kinds of child must repeat the distinction. Printing and searching need the same split, and two collections also lose a single insertion order across files and directories.

**The pressure:** we want to ask every child the same question without repeatedly sorting children into “file” and “directory.” A caller also needs a common type if it is to accept either kind of object.

Part 02 · Introduce the shared concept

## A directory is also a file-system node.

### 05Find the common abstraction

Both files and directories have a name and a size. The result has the same unit, even though the way it is calculated differs.

JavaCopy

```
public interface FileSystemNode {
    String name();
    long size();
}
```

The leaf can be concise without losing the idea:

JavaCopy

```
public record FileItem(String name, long size)
        implements FileSystemNode {}
```

A record provides accessors named after its components, so `name()` and `size()` satisfy this interface. Records are permanent language features available in Java 25; no preview flag is needed. [[2]](#ref-2)

The record replaces the earlier `FileItem` class. These are successive versions of one example, not declarations to paste together into one file.

### 06Let the directory implement the same abstraction

JavaCopy

```
import java.util.ArrayList;
import java.util.List;

public final class Directory implements FileSystemNode {
    private final String name;
    private final List<FileSystemNode> children = new ArrayList<>();

    public Directory(String name) {
        this.name = name;
    }

    public void add(FileSystemNode child) {
        children.add(child);
    }

    @Override
    public String name() {
        return name;
    }

    @Override
    public long size() {
        long total = 0;
        for (FileSystemNode child : children) {
            total += child.size();
        }
        return total;
    }
}
```

The decisive line is **`List<FileSystemNode> children`**. A directory stores the abstraction it also implements. It can therefore contain files, directories, and—if the interface stays open—other valid implementations.

**Teaching version.** This short implementation accepts nulls, cycles, duplicate references, and overflowing totals. Use it to understand the pattern. Appendix A contains the runnable version with validation and cycle checks.

### 07Identify the recursive relationship

The recursive type relationship

Component contract**FileSystemNode**`name() · size()`

Implements FileSystemNode**FileItem**

Returns its own size.

Implements FileSystemNode**Directory**

Asks each child for its size.

`List<FileSystemNode>`Each child can be a file or another directory.

The relationship is recursive because a directory’s child may itself be a directory with more children. The client does not need a different API at each depth.

**Container behavior:** delegate the operation to each child, then combine the results according to the domain. Summation is one possible combination; it is not part of the definition of Composite.

Part 03 · Follow one call

## Build the tree, then let each node do its part.

### 08Compose a small tree

JavaCopy

```
var root = new Directory("root");
var readme = new FileItem("README.md", 100);
var src = new Directory("src");
var service = new Directory("service");

service.add(new FileItem("OrderService.java", 700));
src.add(new FileItem("Main.java", 500));
src.add(service);
root.add(readme);
root.add(src);

System.out.println(root.size()); // 1300
```

Construction code knows which objects can contain children. That is appropriate: **assembling the structure and consuming the structure are different responsibilities**. A size-reporting client should only need `FileSystemNode`.

### 09Follow the recursion down and the values back up

`root.size()` calls each immediate child. A file returns its own number; a directory waits for its children and returns their sum. The empty-directory base case is `0`, because the loop performs no additions.

Trace one depth-first evaluation

PreviousNext stepResetStep 1 of 9

1. Call

   **root.size()**

   Start total at 0.
2. Return

   **README.md → 100**

   root total becomes 100.
3. Call

   **src.size()**

   root waits; src starts at 0.
4. Return

   **Main.java → 500**

   src total becomes 500.
5. Call

   **service.size()**

   src waits; service starts at 0.
6. Return

   **OrderService.java → 700**

   service total becomes 700.
7. Return

   **service → 700**

   src total becomes 500 + 700 = 1,200.
8. Return

   **src → 1,200**

   root total becomes 100 + 1,200 = 1,300.
9. Return

   **root → 1,300**

   The caller receives the aggregate.

Read top to bottom. All nine steps are included when printed.

| Returned value | Calculation | Bytes |
| --- | --- | --- |
| `service.size()` | `OrderService.java` | 700 |
| `src.size()` | `Main.java + service` | 1,200 |
| `root.size()` | `README.md + src` | **1,300** |

This is **structural recursion**: the call structure follows the containment structure. In a valid finite tree, every path eventually reaches a leaf or an empty container.

### 10Give the caller one API

JavaCopy

```
static void printSize(FileSystemNode node) {
    System.out.println(node.name() + ": " + node.size());
}

// Inside the method that built the tree:
printSize(readme); // README.md: 100
printSize(root);   // root: 1300
```

The client delegates to `size()` without inspecting the concrete type. The shared contract makes one file and a whole subtree interchangeable **for this operation**.

### 11Name the roles after understanding them

| Composite role | Our type | Responsibility |
| --- | --- | --- |
| Component | `FileSystemNode` | Defines operations meaningful for both leaves and containers |
| Leaf | `FileItem` | Implements an operation directly; has no children |
| Composite | `Directory` | Contains components and combines or forwards their behavior |
| Client | `printSize` | Uses the component contract |

The useful property is not the vocabulary. It is that adding another level of directories requires no change to `printSize`.

Part 04 · Add behavior, then question the design

## Uniform calls do not require identical implementations.

### 12Add printing

Extend the component contract. This is the final operation set used by Appendix A.

JavaCopy

```
public interface FileSystemNode {
    String name();
    long size();
    void print(String indent);
}
```

Add this method to the leaf:

JavaCopy

```
@Override
public void print(String indent) {
    System.out.println(indent + name);
}
```

The directory prints itself and asks each child to print one level deeper:

JavaCopy

```
@Override
public void print(String indent) {
    System.out.println(indent + name + "/");
    for (FileSystemNode child : children) {
        child.print(indent + "  ");
    }
}
```

Calling `root.print("")` produces:

OutputCopy

```
root/
  README.md
  src/
    Main.java
    service/
      OrderService.java
```

The indentation is state passed down the recursion. Printing is a side effect; it does not combine return values. Direct console output keeps the example small. For reusable rendering, consider writing to a supplied output object or returning a representation.

### 13Remove repeated type decisions from clients

If each client performs an `instanceof` check for every node kind, every new node kind creates more places to update. A shared operation centralizes that responsibility inside the node implementations.

JavaCopy

```
node.size();
node.print("");
```

This does not remove traversal. It moves the recursive coordination into the composite, so clients can use a subtree through its contract.

### 14Keep pattern matching when it fits the model

Conditionals are not inherently bad. If node variants are deliberately closed and operations belong outside the data, a sealed hierarchy with a pattern-matching `switch` is a reasonable alternative.

JavaCopy

```
sealed interface Node permits FileNode, DirectoryNode {}
record FileNode(String name, long size) implements Node {}
record DirectoryNode(String name, List<Node> children) implements Node {
    DirectoryNode {
        children = List.copyOf(children);
    }
}

static long size(Node node) {
    return switch (node) {
        case FileNode file -> file.size();
        case DirectoryNode directory -> {
            long total = 0;
            for (Node child : directory.children()) {
                total = Math.addExact(total, size(child));
            }
            yield total;
        }
    };
}
```

This is a declaration excerpt; it needs `import java.util.List` and an enclosing class for the method. Appendix B supplies the complete source, validation, and an iterative alternative. The two record variants cover the permitted implementations. A null input is rejected explicitly in the complete version.

Sealed types and reference-type patterns in `switch` are permanent features supported by Java 25. This example uses no primitive-pattern preview features. [[3]](#ref-3) [[4]](#ref-4)

| Change pressure | OO Composite | Closed data plus external operations |
| --- | --- | --- |
| Add a node kind | With an open interface, add an implementation of existing operations | Update the permitted types and relevant switches |
| Add an operation | Usually update the interface and all implementations | Add a function over the known variants |
| Keep behavior close to domain objects | Natural fit | Behavior is separate from the data |

Choose from the expected changes in the domain. Neither approach makes the other obsolete.

Part 05 · Generalize the idea

## Look for meaningful operations on both parts and wholes.

### 15Let the domain decide the operation

Composite can support `render()`, `evaluate()`, `validate()`, `calculatePrice()`, `print()`, or `execute()` when those operations make sense for leaves and groups.

For a UI model, a button could render itself while a panel renders its children. The name of the operation is shared; the behavior differs. Layout, clipping, ordering, and error handling are additional policies the model must define.

**A useful question:** what should invoking this operation on the whole mean in terms of its parts?

### 16Apply it to pricing bundles

A product has a price. A bundle can contain products or other bundles. Define a common price operation:

JavaCopy

```
interface PricedItem {
    long priceInCents();
}

record Product(String name, long priceInCents) implements PricedItem {}

record Bundle(List<PricedItem> items) implements PricedItem {
    Bundle {
        items = List.copyOf(items);
    }

    @Override
    public long priceInCents() {
        long total = 0;
        for (PricedItem item : items) {
            total = Math.addExact(total, item.priceInCents());
        }
        return total;
    }
}
```

The caller uses `item.priceInCents()` for a single product or a nested bundle. This excerpt assumes one currency and nonnegative input prices; Appendix C validates product inputs and constructs a complete example.

| Example bundle | Contents | Total |
| --- | --- | --- |
| Gaming | Laptop 100,000 + mouse 5,000 + headset 8,000 | 113,000 cents |
| Ultimate | Gaming + warranty bundle 12,000 | **125,000 cents** |

Discounts, taxes, quantities, and currency conversion are separate pricing rules. Composite only supplies a place to combine the parts. `Math.addExact` throws if the result overflows a `long`; ordinary `+` does not provide that check. [[6]](#ref-6)

Part 06 · Design the API and protect the structure

## A common operation does not imply common child management.

### 17Transparent Composite: put child methods everywhere

One API style puts `add` and `remove` on the component interface as well as `size`. Every node then has the same surface, but a leaf must reject or otherwise define child-management calls.

JavaCopy

```
interface Node {
    void add(Node child);
    void remove(Node child);
    long size();
}
```

If `file.add(child)` throws `UnsupportedOperationException`, the invalid operation is detected at runtime. This can be a deliberate tradeoff, but it should be part of the documented contract.

### 18Safer Composite: child methods only on containers

Our preferred API for this example keeps `name`, `size`, and `print` on `FileSystemNode`; only `Directory` exposes `add`. A `FileItem` has no child-management method to call accidentally.

| Decision | Transparent API | Container-only mutation API |
| --- | --- | --- |
| Does a leaf expose `add`? | Yes | No |
| Can a generic component reference add children? | Yes, possibly failing at runtime | No; construction needs a container reference |
| Is reading uniform? | Yes | Yes |
| Where is an invalid leaf mutation caught? | In the implementation | By the type checker |

Uniformity should cover meaningful domain behavior. It need not extend to operations that some node kinds cannot support.

### 19Write down structural invariants

A mutable container needs rules beyond “implements the right interface.” At minimum, decide how it handles:

* Null children and invalid leaf values.
* Direct and indirect containment cycles.
* Duplicate references and a child shared by multiple parents.
* Mutation during traversal, including concurrent mutation.

Without a cycle rule, `root.add(root)` makes naïve `size()` recursion fail to terminate normally. An indirect cycle is just as harmful.

### 20Reject more than direct self-reference

This small guard is useful but incomplete:

JavaCopy

```
public void add(FileSystemNode child) {
    if (child == this) {
        throw new IllegalArgumentException("Self-reference");
    }
    children.add(child);
}
```

It rejects `A` containing itself, but allows `A` to contain `B`, `B` to contain `C`, and `C` to contain `A`.

**A stronger rule:** before adding `child` to `this`, ask whether `this` is already reachable from `child`. If so, the new edge would close a cycle.

JavaCopy

```
// From the complete Directory implementation in Appendix A:
public void add(FileSystemNode child) {
    Objects.requireNonNull(child, "child");
    if (containsIdentity(child, this)) {
        throw new IllegalArgumentException("Cycle");
    }
    if (children.stream().anyMatch(existing -> existing == child)) {
        throw new IllegalArgumentException("Duplicate child");
    }
    children.add(child);
}
```

Appendix A supplies `containsIdentity`, an iterative traversal with an identity-based visited set. Identity matters: two equal-valued records can be different nodes. `IdentityHashMap` compares keys by reference identity, making it suitable for this topology check. [[7]](#ref-7)

**Why the runnable version is sealed.** Its component permits only `FileItem` and `Directory`, so the cycle checker knows every possible container type. The early open interface teaches extensibility; the final closed model gives the validation a clear boundary. Adding a new container type requires updating that boundary and traversal.

### 21Distinguish a tree from a graph

Blocking cycles is not the same as enforcing one parent per node. Appendix A allows a node to appear under different parents, so its general structure can be an acyclic directed graph. It rejects repeated insertion of the same instance into the same parent.

| Structure or policy | Consequence for traversal |
| --- | --- |
| Strict tree: each non-root node has one parent | Each reachable node is visited once |
| Shared node under multiple parents | Decide whether each occurrence contributes or each identity contributes once |
| Cyclic graph | Reject cycles or use an operation-specific graph algorithm |

Our aggregation counts **each containment occurrence**. If the same 100-byte file is attached through two branches, the sum includes 200 bytes. If that is wrong for your domain, enforce exclusive ownership or define a distinct “unique-node total.” Do not quietly insert a visited set into the sum: it changes the meaning of the operation.

The visited set in the cycle check only avoids redundant exploration. It does not change aggregation semantics. A full strict-tree API would also track parent ownership and define moves/removals atomically. The mutable example is for single-threaded use; its check-and-add sequence is not a concurrency protocol.

Part 07 · Account for mutation and cost

## The pattern does not remove algorithmic constraints.

### 22Consider immutable composites

An immutable container can receive its children at construction time. This alternative uses a new name to avoid confusing it with the mutable `Directory`:

JavaCopy

```
public record ImmutableDirectory(
        String name, List<FileSystemNode> children)
        implements FileSystemNode {
    public ImmutableDirectory {
        Objects.requireNonNull(name, "name");
        children = List.copyOf(children);
    }

    @Override
    public long size() {
        long total = 0;
        for (FileSystemNode child : children) {
            total = Math.addExact(total, child.size());
        }
        return total;
    }

    @Override
    public void print(String indent) {
        System.out.println(indent + name + "/");
        for (FileSystemNode child : children) {
            child.print(indent + "  ");
        }
    }
}
```

This standalone variant uses the **open** interface from section 12 and imports `List` and `Objects`. It is not an extra permitted type in Appendix A’s sealed model.

`List.copyOf` protects the list’s membership from later changes and rejects null elements. It does **not** make the child objects immutable. A mutable child can still change the result of `size()`. [[5]](#ref-5)

To obtain an immutable hierarchy, every permitted node kind must have appropriately immutable state. Appendix B and the exercise solution use closed, immutable node types constructed from already-built children. That construction prevents ordinary containment cycles, though shared references remain possible. Read-only sharing is simpler when the whole reachable model is immutable and published safely.

### 23Understand traversal and caching costs

For the recursive implementation on a tree with `n` nodes, one `size()` call visits each node once: **O(n) time**, assuming fixed-cost leaf operations. Repeating it repeats the work.

| Choice | Benefit | Obligation |
| --- | --- | --- |
| Recompute totals | Simple, reflects current children | Pay the traversal cost on each call |
| Cache mutable totals | Faster repeated reads | Invalidate or update every affected ancestor |
| Precompute immutable totals | Constant-time size lookup can be possible | Pay construction cost and keep all reachable state immutable |

With shared subtrees, counting occurrences may revisit the same objects many times. The work is then proportional to the expanded traversal, not necessarily the number of distinct object identities. The cycle check also adds a traversal during insertion.

Use `Math.addExact` if silent overflow would violate the contract. A valid structure does not guarantee that its aggregate fits in a `long`.

### 24Bound or avoid recursive call depth

The recursive `size()` implementation uses **O(h) call-stack space**, where `h` is tree height. Very deep input can cause `StackOverflowError`; there is no universal safe node-depth limit. [[8]](#ref-8)

Appendix B also computes the same total with an explicit worklist:

JavaCopy

```
public static long sizeIterative(Node root) {
    var pending = new ArrayDeque<Node>();
    pending.push(Objects.requireNonNull(root, "root"));
    long total = 0;
    while (!pending.isEmpty()) {
        Node node = pending.pop();
        switch (node) {
            case FileNode file ->
                    total = Math.addExact(total, file.size());
            case DirectoryNode directory ->
                    pending.addAll(directory.children());
        }
    }
    return total;
}
```

The worklist moves traversal state to the heap. This version can hold O(n) pending nodes in a wide tree; it does not make memory use disappear. The addition order is irrelevant for these nonnegative byte sizes, but an order-sensitive operation such as printing must preserve the desired child order deliberately.

For externally supplied structures, also decide limits for depth, node count, total work, and malformed data.

Part 08 · Recognize intent

## Similar shapes can express different relationships.

### 25Composite versus Decorator

Both use a shared abstraction. A typical Decorator wraps one subject to add behavior; a Composite represents a whole containing zero or more parts. “Chain versus tree” is a useful first cue, but intent is more reliable than counting fields. A directory with one child is still a Composite.

### 26Composite versus Facade

A Facade offers a simpler entry point to subsystem services. Those services usually do not implement the facade’s abstraction. Composite depends on the part and the whole sharing a meaningful component contract.

### 27Composite versus Observer

A publisher with many listeners may look like branching structure. Its relationship is notification: something happened, so listeners should react. A Composite relationship is containment: these parts make up this whole. A picture with branches alone does not establish the pattern.

### 28Composite versus recursion

Recursion is an implementation technique. Composite is a design relationship in which a container is a component and contains components. Recursive functions can operate on data without implementing OO Composite; composite structures can also be traversed iteratively.

| Concept | Main question | Typical relationship |
| --- | --- | --- |
| Composite | How can clients operate on a part and a whole uniformly? | Component contains components |
| Decorator | How can I layer behavior around a subject? | Component wraps a component |
| Facade | How can I simplify access to a subsystem? | Entry point coordinates services |
| Observer | How should interested objects react to an event? | Publisher notifies subscribers |
| Recursion | How can a computation solve smaller instances of itself? | Calls follow a base case and recursive cases |

Part 09 · Put the pattern to work

## Test the contract and the structural rules.

### 29Recognize real hierarchical models

The JDK provides a direct example: `java.awt.Container` extends `Component` and can contain other components. [[9]](#ref-9)

The compiler API’s `com.sun.source.tree.Tree` is a shared interface for syntax-tree nodes. It also exposes `accept` for visitors, illustrating that a shared hierarchy and externally organized operations can coexist. It is an API to consume, not a hierarchy that applications should implement themselves. [[10]](#ref-10)

Other candidate domains include menus, document sections, product bundles, organization structures, expression trees, and workflow trees. Treat these as modeling opportunities: the actual operations and containment semantics determine whether Composite fits.

### 30Model a permission expression

Consider this rule: **the user is an employee AND (an admin OR the document owner)**. Every node answers the same Boolean question.

JavaCopy

```
record AuthorizationContext(boolean employee, boolean admin, boolean owner) {}

interface PermissionRule {
    boolean evaluate(AuthorizationContext context);
}

record IsAdmin() implements PermissionRule {
    @Override
    public boolean evaluate(AuthorizationContext context) {
        return context.admin();
    }
}
```

The composite evaluates child rules and combines their answers:

JavaCopy

```
record AndRule(List<PermissionRule> rules) implements PermissionRule {
    AndRule {
        rules = List.copyOf(rules);
        if (rules.isEmpty()) {
            throw new IllegalArgumentException("AND needs a rule");
        }
    }

    @Override
    public boolean evaluate(AuthorizationContext context) {
        return rules.stream().allMatch(rule -> rule.evaluate(context));
    }
}
```

Appendix C adds `OrRule`, constructs the policy, and checks allowed and denied cases. Its leaf predicates read Boolean values supplied in the example context; this is a policy-expression model, not a complete authorization system.

`allMatch` and `anyMatch` short-circuit. For an empty stream, `allMatch` returns `true` and `anyMatch` returns `false`. Our constructors reject empty rule groups so that an accidental empty AND cannot become an allow rule. This is an explicit domain policy, not a requirement of Composite. [[11]](#ref-11)

### 31Test behavior at three levels

First test a leaf. Then test a simple aggregate. Finally test nesting: that is where the recursive contract is exercised.

| Test | Setup | Expected result |
| --- | --- | --- |
| Leaf | One 100-byte file | `100` |
| Empty composite | Directory with no children | `0` |
| Flat aggregate | Files of 100 and 200 bytes | `300` |
| Nested aggregate | Root: 50-byte file + child: 200-byte file | `250` |
| Full example | README 100 + Main 500 + OrderService 700 | `1,300` |
| Direct cycle | Add root to itself | Reject before mutation |
| Indirect cycle | Add root to a descendant | Reject before mutation |
| Same-parent duplicate | Insert the same object twice | Reject under our chosen policy |
| Overflow | `Long.MAX_VALUE` plus one byte | `ArithmeticException` |

Appendix A contains executable checks using small helpers that throw `AssertionError`. There is no JUnit dependency and no reliance on Java assertions being enabled. The key test is the result promised by the contract, not a test that merely checks a private list’s implementation.

Also test output order when printing matters, ownership when strict trees are required, and mutation semantics when totals are cached.

### 32Use the design questions in order

1. Does the domain naturally contain parts and wholes?
2. Can a whole contain other wholes recursively?
3. Do leaves and groups support the same meaningful operation?
4. Would clients benefit from calling that operation without checking the node kind?
5. Can you state the rules for aggregation, ownership, cycles, mutation, and cost?

If the first four answers are yes, Composite is a strong candidate. The fifth question determines whether your implementation has a coherent contract.

A list alone is not the signal. A part and a whole sharing meaningful behavior is.

Part 10 · Exercise

## Build an organization hierarchy.

An `Employee` is a leaf. A `Department` contains employees and other departments. The caller needs only the common operation:

JavaCopy

```
public interface OrgUnit {
    long monthlyCost();
    void print(String indent);
}
```

For this exercise, **`monthlyCost()` returns whole US dollars per month**. The simplified unit preserves the lesson’s expected result of `40_000`. If you choose cents instead, rename or document the contract and expect `4_000_000` cents.

| Department | Member | Monthly cost |
| --- | --- | --- |
| Engineering | Alice | $10,000 |
| Engineering | Bob | $9,000 |
| Engineering / Platform | Carol | $11,000 |
| Engineering / Platform | Dave | $10,000 |
| **Engineering total** | Including Platform | **$40,000** |

### Acceptance criteria

1. `Employee` and `Department` implement `OrgUnit`.
2. `Department` stores `OrgUnit`, with one child collection.
3. Departments can nest to any depth allowed by your resource limits.
4. `monthlyCost()` recursively combines children using the documented unit.
5. Employees expose no child-management methods.
6. The construction or mutation API prevents direct and indirect containment cycles.
7. Caller code calculates cost without `instanceof` or manual traversal.
8. Tests cover a leaf, an empty department, and the nested $40,000 example.

### Make one design decision before coding

Choose mutable construction with guarded `add`, or immutable bottom-up construction. For a mutable strict tree, account for parent ownership and reparenting as well as cycles. For an immutable hierarchy, keep every permitted node type immutable and copy input collections.

Decide whether reusing the same employee instance in two departments represents two billable positions or an error. Immutability does not resolve that ownership rule.

**Reference solution:** Appendix D uses immutable records, a sealed `OrgUnit`, and `List.copyOf`. Since nodes are assembled from completed children and cannot be changed afterward, the ordinary API cannot create containment cycles. It allows shared references and counts each occurrence; the provided organization uses each employee once.

### Quick self-check

Try answering before looking at the answers: Why does an empty department cost zero? Why is `List<FileItem>` the wrong child type? Why does a direct self-check miss a three-node cycle? What changes when a shared employee is counted only once?

**Answers.** Zero is the identity for addition. The child type must include both leaves and groups. Indirect reachability matters, not just equality with the immediate child. Counting once per identity is a different aggregation contract and requires a suitable traversal policy.

Part 11 · Place the lesson

## Keep the intent of each pattern distinct.

| Pattern | Main design pressure |
| --- | --- |
| Strategy | Select or replace an algorithm |
| Factory | Select or create an implementation |
| Builder | Assemble an object through a controlled construction process |
| Adapter | Translate between incompatible interfaces |
| Decorator | Layer composable behavior around a subject |
| Facade | Provide a simpler entry point to a subsystem |
| Proxy | Stand in for a subject and control its access |
| **Composite** | **Represent a part-whole hierarchy through a shared abstraction** |
| Observer | Notify interested objects about events |
| State | Vary behavior as an object’s state changes |
| Command | Represent a requested action as an object |

### Next: Template Method

Now consider several processes that all validate input, load data, transform it, save it, and notify someone. The order is stable, but a few steps vary.

The next question is: **how can a workflow keep its algorithm skeleton stable while selected steps vary?** That is the pressure behind Template Method.

Appendices · Complete source

## Run the examples without dependencies.

Each source listing below is a complete file. Save it with the shown filename. The page’s download buttons work offline; if scripts are disabled, copy the visible listing. All imports and support types are included as nested types, so the examples do not collide.

Use a **JDK 25** installation, with `java` and `javac` on your path:

TerminalCopy

```
javac --release 25 CompositeDemo.java AlternativesDemo.java DomainExamples.java OrgExercise.java
java CompositeDemo
java AlternativesDemo
java DomainExamples
java OrgExercise
```

`--release 25` selects Java 25 language/API compatibility. No preview flag or external library is required. [[12]](#ref-12)

**Validation record.** Java 25 compatibility was checked against Oracle’s Java 25 language and API documentation. All four programs were compiled and executed in the available OpenJDK 17.0.20 environment; only the pattern-switch example needed that older compiler’s preview flag. A JDK 25 execution was not available in the authoring environment. Java 25 uses the reference-type switch patterns here as permanent features. All 32 numbered steps, internal links, offline assets, and embedded source text passed structural checks. Browser policy blocked the local visual preview, so PDF pagination was not visually verified.

### Appendix A · CompositeDemo.java

This is the mutable example with cycle checks, duplicate-reference rejection, validated file sizes, checked addition, and executable checks. Its cycle search uses identity; `size()` counts occurrences. It is intentionally single-threaded. The component is sealed so that the traversal can recognize every container.

CompositeDemo.java · complete file

Download .java Copy

```
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public final class CompositeDemo {
    public sealed interface FileSystemNode
            permits FileItem, Directory {
        String name();
        long size();
        void print(String indent);
    }

    public record FileItem(String name, long size)
            implements FileSystemNode {
        public FileItem {
            Objects.requireNonNull(name, "name");
            if (size < 0) {
                throw new IllegalArgumentException("Negative size");
            }
        }

        @Override
        public void print(String indent) {
            System.out.println(indent + name);
        }
    }

    public static final class Directory implements FileSystemNode {
        private final String name;
        private final List<FileSystemNode> children = new ArrayList<>();

        public Directory(String name) {
            this.name = Objects.requireNonNull(name, "name");
        }

        public void add(FileSystemNode child) {
            Objects.requireNonNull(child, "child");
            if (containsIdentity(child, this)) {
                throw new IllegalArgumentException("Cycle");
            }
            if (children.stream().anyMatch(existing -> existing == child)) {
                throw new IllegalArgumentException("Duplicate child");
            }
            children.add(child);
        }

        @Override
        public String name() {
            return name;
        }

        @Override
        public long size() {
            long total = 0;
            for (FileSystemNode child : children) {
                total = Math.addExact(total, child.size());
            }
            return total;
        }

        @Override
        public void print(String indent) {
            System.out.println(indent + name + "/");
            for (FileSystemNode child : children) {
                child.print(indent + "  ");
            }
        }
    }

    private static boolean containsIdentity(
            FileSystemNode start, FileSystemNode sought) {
        var pending = new ArrayDeque<FileSystemNode>();
        Set<FileSystemNode> seen = Collections.newSetFromMap(
                new IdentityHashMap<FileSystemNode, Boolean>());
        pending.push(start);
        while (!pending.isEmpty()) {
            FileSystemNode node = pending.pop();
            if (node == sought) {
                return true;
            }
            if (!seen.add(node)) {
                continue;
            }
            if (node instanceof Directory directory) {
                pending.addAll(directory.children);
            }
        }
        return false;
    }

    private static void printSize(FileSystemNode node) {
        System.out.println(node.name() + ": " + node.size());
    }

    private static void expect(long expected, long actual) {
        if (expected != actual) {
            throw new AssertionError(expected + " != " + actual);
        }
    }

    private static void expectThrows(
            Class<? extends RuntimeException> type, Runnable action) {
        try {
            action.run();
        } catch (RuntimeException error) {
            if (type.isInstance(error)) {
                return;
            }
            throw new AssertionError("Wrong exception", error);
        }
        throw new AssertionError("Expected " + type.getSimpleName());
    }

    public static void main(String[] args) {
        var root = new Directory("root");
        var readme = new FileItem("README.md", 100);
        var src = new Directory("src");
        var service = new Directory("service");
        service.add(new FileItem("OrderService.java", 700));
        src.add(new FileItem("Main.java", 500));
        src.add(service);
        root.add(readme);
        root.add(src);

        expect(100, readme.size());
        expect(0, new Directory("empty").size());
        expect(700, service.size());
        expect(1200, src.size());
        expect(1300, root.size());
        var flat = new Directory("flat");
        flat.add(new FileItem("a", 100));
        flat.add(new FileItem("b", 200));
        expect(300, flat.size());
        var nested = new Directory("nested");
        var child = new Directory("child");
        child.add(new FileItem("file", 200));
        nested.add(new FileItem("readme", 50));
        nested.add(child);
        expect(250, nested.size());
        expectThrows(IllegalArgumentException.class, () -> root.add(root));
        expectThrows(IllegalArgumentException.class, () -> service.add(root));
        expectThrows(IllegalArgumentException.class, () -> root.add(readme));
        expectThrows(NullPointerException.class, () -> root.add(null));
        expectThrows(IllegalArgumentException.class,
                () -> new FileItem("bad", -1));
        var huge = new Directory("huge");
        huge.add(new FileItem("max", Long.MAX_VALUE));
        huge.add(new FileItem("one", 1));
        expectThrows(ArithmeticException.class, () -> huge.size());

        printSize(readme);
        printSize(root);
        root.print("");
        System.out.println("Composite checks passed.");
    }
}
```

Expected output:

OutputCopy

```
README.md: 100
root: 1300
root/
  README.md
  src/
    Main.java
    service/
      OrderService.java
Composite checks passed.
```

### Appendix B · AlternativesDemo.java

This is a separate immutable data model. One function uses recursion and another uses a worklist. Both count each occurrence and return 1,300 for the sample.

AlternativesDemo.java · complete file

Download .java Copy

```
import java.util.ArrayDeque;
import java.util.List;
import java.util.Objects;

public final class AlternativesDemo {
    public sealed interface Node permits FileNode, DirectoryNode {}

    public record FileNode(String name, long size) implements Node {
        public FileNode {
            Objects.requireNonNull(name, "name");
            if (size < 0) {
                throw new IllegalArgumentException("Negative size");
            }
        }
    }

    public record DirectoryNode(String name, List<Node> children)
            implements Node {
        public DirectoryNode {
            Objects.requireNonNull(name, "name");
            children = List.copyOf(children);
        }
    }

    public static long size(Node node) {
        Objects.requireNonNull(node, "node");
        return switch (node) {
            case FileNode file -> file.size();
            case DirectoryNode directory -> {
                long total = 0;
                for (Node child : directory.children()) {
                    total = Math.addExact(total, size(child));
                }
                yield total;
            }
        };
    }

    public static long sizeIterative(Node root) {
        var pending = new ArrayDeque<Node>();
        pending.push(Objects.requireNonNull(root, "root"));
        long total = 0;
        while (!pending.isEmpty()) {
            Node node = pending.pop();
            switch (node) {
                case FileNode file ->
                        total = Math.addExact(total, file.size());
                case DirectoryNode directory ->
                        pending.addAll(directory.children());
            }
        }
        return total;
    }

    public static void main(String[] args) {
        Node root = new DirectoryNode("root", List.of(
                new FileNode("README.md", 100),
                new DirectoryNode("src", List.of(
                        new FileNode("Main.java", 500),
                        new DirectoryNode("service", List.of(
                                new FileNode("OrderService.java", 700)))))));
        if (size(root) != 1300 || sizeIterative(root) != 1300) {
            throw new AssertionError("Expected 1300 bytes");
        }
        System.out.println("Recursive and iterative sizes: 1300");
    }
}
```

Expected output: `Recursive and iterative sizes: 1300`.

### Appendix C · DomainExamples.java

This file supplies the complete bundle and permission models, including the missing context, constructors, OR composite, and checks. The open interfaces permit additional implementations; their behavior and immutability remain part of the implementer’s contract.

DomainExamples.java · complete file

Download .java Copy

```
import java.util.List;
import java.util.Objects;

public final class DomainExamples {
    public interface PricedItem {
        long priceInCents();
    }

    public record Product(String name, long priceInCents)
            implements PricedItem {
        public Product {
            Objects.requireNonNull(name, "name");
            if (priceInCents < 0) {
                throw new IllegalArgumentException("Negative price");
            }
        }
    }

    public record Bundle(List<PricedItem> items) implements PricedItem {
        public Bundle {
            items = List.copyOf(items);
        }

        @Override
        public long priceInCents() {
            long total = 0;
            for (PricedItem item : items) {
                total = Math.addExact(total, item.priceInCents());
            }
            return total;
        }
    }

    public record AuthorizationContext(
            boolean employee, boolean admin, boolean owner) {}

    public interface PermissionRule {
        boolean evaluate(AuthorizationContext context);
    }

    public record IsAdmin() implements PermissionRule {
        @Override
        public boolean evaluate(AuthorizationContext context) {
            return context.admin();
        }
    }

    public record AndRule(List<PermissionRule> rules)
            implements PermissionRule {
        public AndRule {
            rules = List.copyOf(rules);
            if (rules.isEmpty()) {
                throw new IllegalArgumentException("AND needs a rule");
            }
        }

        @Override
        public boolean evaluate(AuthorizationContext context) {
            return rules.stream().allMatch(rule -> rule.evaluate(context));
        }
    }

    public record OrRule(List<PermissionRule> rules)
            implements PermissionRule {
        public OrRule {
            rules = List.copyOf(rules);
            if (rules.isEmpty()) {
                throw new IllegalArgumentException("OR needs a rule");
            }
        }

        @Override
        public boolean evaluate(AuthorizationContext context) {
            return rules.stream().anyMatch(rule -> rule.evaluate(context));
        }
    }

    public static void main(String[] args) {
        PricedItem gaming = new Bundle(List.of(
                new Product("Laptop", 100_000),
                new Product("Mouse", 5_000),
                new Product("Headset", 8_000)));
        PricedItem ultimate = new Bundle(List.of(gaming,
                new Bundle(List.of(new Product("Warranty", 12_000)))));
        if (ultimate.priceInCents() != 125_000) {
            throw new AssertionError("Wrong bundle price");
        }
        PermissionRule policy = new AndRule(List.of(
                AuthorizationContext::employee,
                new OrRule(List.of(new IsAdmin(),
                        AuthorizationContext::owner))));
        if (!policy.evaluate(new AuthorizationContext(true, false, true))
                || policy.evaluate(new AuthorizationContext(false, true, true))
                || policy.evaluate(new AuthorizationContext(true, false, false))) {
            throw new AssertionError("Wrong policy result");
        }
        System.out.println("Bundle: 125000 cents; policy checks passed.");
    }
}
```

Expected output: `Bundle: 125000 cents; policy checks passed.`

### Appendix D · OrgExercise.java

Read this after attempting the exercise. The immutable solution enforces its cycle rule through construction rather than through a runtime `add` check.

OrgExercise.java · complete file

Download .java Copy

```
import java.util.List;
import java.util.Objects;

public final class OrgExercise {
    // Whole US dollars per month, for this exercise only.
    public sealed interface OrgUnit permits Employee, Department {
        long monthlyCost();
        void print(String indent);
    }

    public record Employee(String name, long monthlyCost) implements OrgUnit {
        public Employee {
            Objects.requireNonNull(name, "name");
            if (monthlyCost < 0) {
                throw new IllegalArgumentException("Negative monthly cost");
            }
        }

        @Override
        public void print(String indent) {
            System.out.println(indent + name + " $" + monthlyCost);
        }
    }

    public record Department(String name, List<OrgUnit> members)
            implements OrgUnit {
        public Department {
            Objects.requireNonNull(name, "name");
            members = List.copyOf(members);
        }

        @Override
        public long monthlyCost() {
            long total = 0;
            for (OrgUnit member : members) {
                total = Math.addExact(total, member.monthlyCost());
            }
            return total;
        }

        @Override
        public void print(String indent) {
            System.out.println(indent + name + "/");
            for (OrgUnit member : members) {
                member.print(indent + "  ");
            }
        }
    }

    public static void main(String[] args) {
        OrgUnit engineering = new Department("Engineering", List.of(
                new Employee("Alice", 10_000),
                new Employee("Bob", 9_000),
                new Department("Platform", List.of(
                        new Employee("Carol", 11_000),
                        new Employee("Dave", 10_000)))));
        if (engineering.monthlyCost() != 40_000
                || new Department("Empty", List.of()).monthlyCost() != 0
                || new Employee("Leaf", 100).monthlyCost() != 100) {
            throw new AssertionError("Wrong organization cost");
        }
        engineering.print("");
        System.out.println("Monthly cost: $" + engineering.monthlyCost());
    }
}
```

Expected output:

OutputCopy

```
Engineering/
  Alice $10000
  Bob $9000
  Platform/
    Carol $11000
    Dave $10000
Monthly cost: $40000
```

Official references

## Verify the contracts behind the examples.

The lesson’s narrative is adapted from the supplied Lesson 11. These official sources support the pattern definition and Java-specific details. API links are pinned to Java 25.

1. [Microsoft Learn · Composite pattern](https://learn.microsoft.com/en-us/archive/msdn-magazine/2001/july/design-patterns-solidify-your-csharp-application-architecture-with-design-patterns#composite)

   Pattern intent and the file/folder example; archived article.

   https://learn.microsoft.com/en-us/archive/msdn-magazine/2001/july/design-patterns-solidify-your-csharp-application-architecture-with-design-patterns#composite
2. [Oracle Java 25 · Record classes](https://docs.oracle.com/en/java/javase/25/language/records.html)

   Generated accessors and compact constructors.

   https://docs.oracle.com/en/java/javase/25/language/records.html
3. [Oracle Java 25 · Language changes summary](https://docs.oracle.com/en/java/javase/25/language/java-language-changes-summary.html)

   Permanent versus preview language features.

   https://docs.oracle.com/en/java/javase/25/language/java-language-changes-summary.html
4. [Oracle Java 25 · Pattern matching with switch](https://docs.oracle.com/en/java/javase/25/language/pattern-matching-switch.html)

   Reference-type patterns, dispatch, and null handling.

   https://docs.oracle.com/en/java/javase/25/language/pattern-matching-switch.html
5. [Oracle Java 25 · List](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html)

   Unmodifiable lists, List.copyOf, and mutable element caveats.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html
6. [Oracle Java 25 · Math.addExact](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Math.html#addExact(long,long))

   Checked addition and overflow.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Math.html#addExact(long,long)
7. [Oracle Java 25 · IdentityHashMap](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/IdentityHashMap.html)

   Reference-identity key comparison.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/IdentityHashMap.html
8. [Oracle Java 25 · StackOverflowError](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/StackOverflowError.html)

   Failure caused by overly deep recursion.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/StackOverflowError.html
9. [Oracle Java 25 · AWT Container](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/java/awt/Container.html)

   A component that contains components.

   https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/java/awt/Container.html
10. [Oracle Java 25 · Compiler Tree interface](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.compiler/com/sun/source/tree/Tree.html)

    Shared syntax-tree abstraction and visitor support.

    https://docs.oracle.com/en/java/javase/25/docs/api/jdk.compiler/com/sun/source/tree/Tree.html
11. [Oracle Java 25 · Stream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html)

    allMatch/anyMatch short-circuiting and empty-stream results.

    https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html
12. [Oracle Java 25 · javac command](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

    Source compilation and --release.

    https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html

Prepared 1 September 2026 · DP / Lesson 11

DP · Lesson 11 · Composite [Back to top](#top)