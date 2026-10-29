## Java 8

- Default and Static Interface Methods (allowed interface evolution without breaking APIs)
- New Date & Time API (java.time package replacing mutable java.util.Date)
- Lambdas/Streams/Optional

## Java 9

- Module System (strong encapsulation of JDK internals)
- JShell (official interactive command-line REPL)
- Collection Factory Methods (List.of(), Set.of(), Map.of())

## Java 11 (LTS)

- Standard HTTP Client API (built-in modern async HTTP/2 support)
- Local-Variable Syntax for Lambda Parameters (var allowed inside lambdas)
- Single-File Source Code Execution (running .java files directly without explicit compilation)

## Java 17 (LTS)

- Records/sealed classes
- Pattern Matching for instanceof (automatic variable binding, removing explicit casts)
- Text Blocks (multi-line string literals)
- Switch Expressions (arrow syntax and value-returning switch blocks)

## Java 21 (LTS)

- Record Patterns & Pattern Matching for Switch (destructuring records and matching switch by types)
- Sequenced Collections (unified interfaces for collections with defined encounter order)
- Generational ZGC (massive reduction in garbage collection pause times)

## Java 25 (LTS)

- Virtual threads
- Scoped Values & Structured Concurrency (standardized lightweight thread-data sharing and task grouping)
- Flexible Constructor Bodies (statements allowed before calling super())
- Compact Object Headers (Project Lilliput memory footprint reduction)
- Module Import Declarations (import module java.base;)

## Java 26

- Primitive Types in Patterns (pattern matching for int, double, etc. in switch/instanceof)
- HTTP/3 Support (native QUIC/UDP capabilities added to HttpClient)
- AOT Object Caching (Project Leyden startup acceleration extended to all GCs)
