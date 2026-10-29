# Runnable Java 17+ drills

These examples are **self-contained classroom demos**. They are not production payment implementations. No Spring or
JUnit dependency is needed.

Run from this directory:

```sh
javac FeeStrategyDemo.java PaymentStateDemo.java IdempotencyToyDemo.java
java FeeStrategyDemo
java PaymentStateDemo
java IdempotencyToyDemo
```

Expected output: three lines starting with `PASS:`. Change one rule or operation to make each assertion fail; then
explain why.

1. **FeeStrategyDemo:** Strategy, composition, SRP, and dependency inversion. Add a `TieredFee` without editing
   `Processor`.
2. **PaymentStateDemo:** Encapsulation and State/transition validation. Try to authorize or settle twice.
3. **IdempotencyToyDemo:** Tenant-scoped deduplication and payload conflict rules. **Deliberate limitation:** This
   stores deduplication state only in one process and loses it on restart. A real payment API needs durable database
   uniqueness, transactional storage, and downstream safety/reconciliation. Do not copy this in-memory approach to
   production.
