[Skip to guide](#main)

Print-width preview · Return to reading

DP / SYSTEM DESIGN

22. Saga +
Compensating
Transactions

[01Start with one business operation](#pressure)[02Derive compensating transactions](#compensation)[03Give the workflow durable memory](#durability)[04Choose the correct recovery](#recovery)[05Make retries and compensation durable](#uncertainty)[06Choose who owns the sequence](#coordination)[07Preserve correctness at every boundary](#local)[08Test the failure paths](#tests)[09Make the workflow operable](#operations)[10Know when the pattern is wrong](#boundaries)[11Connect the patterns without conflating them](#connections)[12State the guarantee honestly](#contract)[AComplete Java source](#java)[BPersistence contract](#adapter)[↗Official sources](#sources)

72 steps · 12 chapters
Java 25-compatible · No dependencies
Sources checked 02 Sep 2026

Guide contents[01Start with one business operation](#pressure)[02Derive compensating transactions](#compensation)[03Give the workflow durable memory](#durability)[04Choose the correct recovery](#recovery)[05Make retries and compensation durable](#uncertainty)[06Choose who owns the sequence](#coordination)[07Preserve correctness at every boundary](#local)[08Test the failure paths](#tests)[09Make the workflow operable](#operations)[10Know when the pattern is wrong](#boundaries)[11Connect the patterns without conflating them](#connections)[12State the guarantee honestly](#contract)[AComplete Java source](#java)[BPersistence contract](#adapter)[↗Official sources](#sources)

22 / DISTRIBUTED BUSINESS CONSISTENCY

# Saga + Compensating Transactions

Place an order, reserve inventory,
and authorize payment.

One business operation. Several local commits. What should happen when the next step fails?

First principlesJava 25-compatibleSelf-contained HTMLLight theme · Print ready

Print / Save as PDFPreview print width[Jump to Java source](#java)

Read from the beginning to derive the pattern. Use the contents for reference. Print includes every lesson and the complete Java source; use A4 or Letter, 100% scale, and turn browser headers/footers off. Background graphics are optional.

**01 / THE PRESSURE**Independent commits create partial outcomes.

**02 / THE RESPONSE**Compensation is a new business operation.

**03 / THE MECHANISM**Durable state, messages, identity, and recovery.

**04 / THE CONTRACT**Known outcomes and visible unresolved work.

### Contents

1. [Start with one business operation](#pressure)
2. [Derive compensating transactions](#compensation)
3. [Give the workflow durable memory](#durability)
4. [Choose the correct recovery](#recovery)
5. [Make retries and compensation durable](#uncertainty)
6. [Choose who owns the sequence](#coordination)
7. [Preserve correctness at every boundary](#local)
8. [Test the failure paths](#tests)
9. [Make the workflow operable](#operations)
10. [Know when the pattern is wrong](#boundaries)
11. [Connect the patterns without conflating them](#connections)
12. [State the guarantee honestly](#contract)
13. [Appendix A · Complete Java source](#java)
14. [Appendix B · Persistence contract](#adapter)
15. [Official sources](#sources)

### Trace a failure decision

A reading aid for the decision table. This does not execute Java or simulate network delivery.

Observed resultPayment definitively declinedPayment response timed outInventory release timed outOrder confirmation timed outLate success after cancellation

**Known: payment was rejected.**

Release inventory, wait for its result, then cancel the order. There is no successful authorization to void.

01 / FIRST PRINCIPLES

## Start with one business operation

Before naming the pattern, locate the transaction boundary that breaks.

### 01Place an order, reserve inventory, authorize payment

A customer clicks **Place order**. The business wants an order recorded, stock held for that order, and payment authorized. Only then should the order become confirmed.

1. **Create a pending order**Keep a durable record of the request.
2. **Reserve inventory**Prevent the same units being promised twice.
3. **Authorize payment**Establish a payment hold under the provider’s rules.
4. **Confirm the order**Record that checkout’s required steps succeeded.

For this guide, shipping and payment capture happen later. A completed checkout means *confirmed order + valid reservation + authorization*; it does not mean money settled or goods shipped.

### 02If everything fits inside one transaction

Imagine all required changes really participate in the same database transaction. The application can commit the group or roll it back before commit. Other transactions’ visibility depends on the database’s isolation rules.

The crucial condition is participation in that transaction. Calling a remote payment API from inside a database transaction does not enlist the provider in it. Your database cannot roll back the provider’s authorization. [[1]](#ref1)

### 03Now split ownership across services

| Owner | Local responsibility | Commit boundary |
| --- | --- | --- |
| Orders | Create, confirm, or cancel an order | Orders database |
| Inventory | Enforce stock and reservation rules | Inventory database |
| Payments | Track payment operations and provider outcomes | Payments database; provider is a further boundary |

Assume no shared atomic transaction covers these participants. Each can commit successfully even if a later participant fails. A distributed transaction protocol is a separate architectural option where supported; this guide deliberately works without one.

### 04Watch the first partial failure

| Time | Observed fact | What is now true |
| --- | --- | --- |
| 10:00:00 | Pending order committed | The order exists. |
| 10:00:01 | Inventory reservation committed | Stock is held. |
| 10:00:02 | Payment definitively declined | Checkout cannot complete as requested. |

Throwing a Java exception does not travel backward through the Inventory service’s committed transaction. Rolling back the current Orders transaction does not erase the reservation either.

**The problem:** some parts of one business operation have already happened, and a later part cannot happen.

### 05Why the previous tools do not solve this

| Tool | What it protects | What it does not decide |
| --- | --- | --- |
| Local database transaction | Atomic changes inside its participating boundary | Recovery of another service’s committed work |
| Optimistic concurrency | A write based on the expected version | How to release an already committed reservation |
| Transactional Outbox | A durable publication obligation alongside a database change | What the business should do after payment fails |

An outbox prevents the commit-to-publication gap from losing the intent to communicate. Eventual publication still depends on a functioning relay, reachable infrastructure, retention, and recovery. It is not an unconditional promise of progress. [[4]](#ref4)

02 / FIRST PRINCIPLES

## Derive compensating transactions

Committed history remains true. Recovery must be another valid business action.

### 06What would rollback mean now?

We cannot roll back the old inventory transaction, but we can ask Inventory to perform a new operation: `ReleaseInventory`. Likewise, a payment authorization may be voided and a pending order may be cancelled.

| Completed action | Possible compensation | Domain condition |
| --- | --- | --- |
| `CreatePendingOrder` | `CancelOrder` | Keep the record and mark the failed outcome. |
| `ReserveInventory` | `ReleaseInventory` | Release this reservation, subject to fulfillment rules. |
| `AuthorizePayment` | `VoidAuthorization` | Authorization is still voidable; capture requires a different recovery. |

For a definitive payment decline, compensate the reservation and then cancel the order. There is no successful authorization to void.

### 07Compensation is not database rollback

A rollback before commit aborts that transaction’s database changes. Compensation happens **after an earlier transaction committed**, through a second transaction.

| At 10:00 | At 10:01 | At 10:02 |
| --- | --- | --- |
| Inventory reserved | Payment declined | Inventory released |

During that interval the inventory really was reserved. Other checkouts may have seen less stock available. An audit record or a notification may already exist. Compensation does not erase these observations.

**Recovery target:** an acceptable business state, not necessarily the identical state that existed before checkout.

### 08Compensation belongs to the domain

`undoLastTransaction()` cannot express the rules. `releaseReservation(reservationId)` can.

Inventory must decide whether fulfillment has started, whether this reservation was already released, and whether the command refers to the right reservation. Payments must distinguish an authorization from a capture. Orders must decide whether cancellation remains legal.

Never restore an old stock snapshot blindly: another customer may have legitimately reserved stock since then. Apply the compensating operation against the current protected state. [[3]](#ref3)

### 09Model intermediate states explicitly

| Entity | Illustrative states | Meaning |
| --- | --- | --- |
| Order | `PENDING, CONFIRMED, CANCELLING, CANCELLED` | Customer-facing business lifecycle |
| Reservation | `RESERVED, RELEASED, EXPIRED` | Whether this hold is still effective |
| Payment operation | `REQUESTED, AUTHORIZED, DECLINED, VOIDED` | Durably known provider outcome |
| Saga | Waiting, compensating, completed, cancelled, manual intervention | Progress and outstanding recovery obligations |

`UNKNOWN` is also useful as the coordinator’s knowledge of an outcome. It does not prove that the provider has a payment whose state is literally “unknown.”

If the UI says `CANCELLING`, decide whether that is stored on the Order or derived from a workflow projection. A Saga state change alone does not magically update a different service’s order row.

### 10The persistent workflow is the Saga

| Fact received | Next business action |
| --- | --- |
| Pending order created | Reserve inventory |
| Inventory reserved | Authorize payment |
| Inventory rejected | Cancel order |
| Payment authorized | Confirm order |
| Payment declined | Release inventory; after release succeeds, cancel order |
| Order confirmation definitively rejected | Void authorization; after void succeeds, release inventory; then cancel order |

Someone must remember what succeeded, what remains uncertain, what happens next, and which compensations are owed. A Saga coordinates a sequence of local transactions and their recovery. Forward recovery continues the workflow; backward recovery compensates completed work. [[2]](#ref2)

03 / FIRST PRINCIPLES

## Give the workflow durable memory

A call stack shows the idea. Durable state and transactional messaging make it recoverable.

### 11Begin with an explicit orchestrator

First imagine a single method: create the order, reserve inventory, authorize payment, confirm the order. A catch block for a definitive payment rejection calls release and cancel.

This makes the sequencing obvious. It does not yet make the process reliable. The method can lose its place, compensation can throw another exception, and a transport error may hide a successful remote action. A broad `catch (Exception)` cannot choose the correct business recovery.

Keep this implementation as a teaching sketch. Do not present it as a production Saga engine.

### 12Crash after inventory reservation

The order commits. Inventory reserves stock. The orchestrator crashes before requesting payment.

If progress lived only in local variables, restart does not tell us what to do. If Inventory committed but its reply was lost, the coordinator may not even know the reservation succeeded.

Recovery requires durable workflow state *and* a way to recover uncertain participant outcomes. Persisted state records what the coordinator knows, not every fact that may have happened elsewhere.

### 13Persist the Saga and its pending operation

Illustrative PostgreSQL schema; adapt constraints and indexesSQL

```
CREATE TABLE checkout_saga (
    saga_id UUID PRIMARY KEY,
    order_id UUID NOT NULL UNIQUE,
    state VARCHAR(64) NOT NULL,
    pending_command_id UUID,
    pending_step VARCHAR(64),
    pending_payload JSONB,
    deadline TIMESTAMPTZ,
    attempts INTEGER NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 0,
    definition_version INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
```

Persist the identifiers, immutable checkout input, pending command, deadline, delivery-attempt metadata, and concurrency version. Store resource IDs needed for compensation, such as the actual reservation and authorization IDs, in a production model.

The schema assumes one Saga per order. If an order may have multiple checkout attempts, model that identity explicitly. The workflow-definition version supports resuming old instances after code changes.

### 14The dual-write problem returns

“Save Saga state, then send ReserveInventory” is two writes. A crash after the first leaves a waiting Saga with no command. Reversing the order risks a command whose corresponding state never committed.

Saving state and calling the broker separately cannot make those two effects atomic. Put the outgoing message into the same local transaction as the Saga update.

### 15Saga state + outgoing intent + one commit

Transaction protocol; named placeholders and omitted columns are illustrativeSQL

```
BEGIN;
-- Load and validate the current workflow state/version.
-- Claim the incoming event in the inbox, if this is a reply.

UPDATE checkout_saga
SET state = 'WAITING_FOR_INVENTORY',
    pending_command_id = :command_id,
    version = version + 1
WHERE saga_id = :saga_id AND version = :expected_version;
-- Require exactly one updated row, or roll back the whole transaction.

INSERT INTO outbox_message (message_id, operation_id, payload)
VALUES (:delivery_id, :command_id, :payload);
COMMIT;
```

The relay publishes only committed outbox records. If publication succeeds but marking the row delivered fails, it may publish again. Consumers must tolerate duplicates.

Apply the same rule at startup. In this guide’s implementation, Orders owns the Saga, so pending order + initial Saga + first outbox command share one transaction. A separate coordinator would need a durable start command/event and its own creation states. [[4]](#ref4)

### 16Commands request; events report facts

Types from the complete Java exampleJAVA

```
record Command(UUID commandId, UUID sagaId, Step step,
               Checkout checkout) {}

record Reply(UUID eventId, UUID sagaId, UUID orderId,
             UUID causationId, Fact fact) {}
```

`RESERVE_INVENTORY` is a request to perform work. `INVENTORY_RESERVED` states that the work committed. `INVENTORY_REJECTED` is a definitive business result, not an HTTP timeout.

Replies identify the operation they answer through `causationId`. Production contracts also need schema versions, validated payloads, authenticated producers, and resource identifiers. The compact Java example uses a step enum to keep attention on the state machine.

### 17Turn coordination into a state machine

Excerpt from on(Saga, Reply, Instant) in the appendixJAVA

```
case WAITING_FOR_INVENTORY -> switch (reply.fact()) {
    case INVENTORY_RESERVED -> issue(saga,
            State.WAITING_FOR_PAYMENT,
            Step.AUTHORIZE_PAYMENT, now);
    case INVENTORY_REJECTED -> issue(saga,
            State.CANCELLING_ORDER, Step.CANCEL_ORDER, now);
    default -> reconcile(saga);
};
```

The decision is **current state + correlated fact → next state + outgoing commands**. It performs no remote I/O. The application layer persists the decision atomically with the outbox.

An unexpected reply is not silently discarded. The sample returns `RECONCILE`, requiring the caller to durably preserve it for investigation or a repair workflow. Exact duplicate event IDs should already be recognized by the inbox.

04 / FIRST PRINCIPLES

## Choose the correct recovery

Business rejection, temporary unavailability, and an unknown result are different inputs.

### 18Payment decline starts inventory compensation

Excerpt from the WAITING\_FOR\_PAYMENT branchJAVA

```
case PAYMENT_DECLINED -> issue(saga,
        State.RELEASING_INVENTORY,
        Step.RELEASE_INVENTORY, now);
```

The state remains `RELEASING_INVENTORY` until the corresponding success is known. `INVENTORY_RELEASED` requests `CANCEL_ORDER`. Only `ORDER_CANCELLED` completes this cancellation path.

Emitting a release command is not evidence that the inventory has been released.

### 19Why compensation often goes backward

If payment was authorized and confirmation is definitively rejected, this guide voids the authorization, releases inventory, and cancels the order. The order reflects the dependency structure chosen for this checkout.

Reverse order is a useful starting point, not a universal algorithm. Independent compensations may run concurrently; a business may prioritize releasing a scarce resource first. Document the dependencies and the facts required before each action. [[3]](#ref3)

### 20Not every action needs to be erased

Creating a pending order need not be compensated by deletion. Transitioning that record to `CANCELLED` can preserve the audit trail, customer-support context, and the reason checkout failed.

The contract is that the failed checkout no longer promises fulfillment, holds no unintended stock, and leaves no unintended active authorization. Keeping a cancelled order is compatible with that contract.

### 21Some actions cannot be reversed

A sent email cannot reliably be unsent. A collected parcel may need a return rather than an “unship.” A completed transfer may require a separate recovery process rather than a rollback method.

These are domain examples, not claims that a particular provider offers a reversal API. Before designing the Saga, identify which actions are reservable, compensable, irreversible, or dependent on human decisions.

### 22Delay irreversible promises when the business allows it

Send the confirmation email after the order has been confirmed. Use an outbox event from the confirmation transaction so a failed email delivery does not require cancelling an otherwise valid order.

For supported payment methods, authorization and capture can be separate operations. Stripe documents this distinction and cancellation of an uncaptured authorization; eligibility and expiration depend on the payment method and provider rules. [[7]](#ref7)

Our checkout ends at authorization. If fulfillment must occur later, a further workflow must handle capture, expiry, and failures. Do not call this example an end-to-end payment settlement workflow.

### 23Forward recovery versus backward recovery

| Choice | Question | Example |
| --- | --- | --- |
| Forward recovery | Can the intended operation still succeed safely? | Retry a reservation request with the same operation identity. |
| Backward recovery | Should already completed work be compensated? | Release stock after a definitive payment decline. |

A retry continues toward the original business outcome. Compensation moves toward a different acceptable outcome. The decision depends on the failure semantics and the business deadline. [[2]](#ref2)

### 24Failure does not always mean compensate

| Signal | What you know | Next decision |
| --- | --- | --- |
| Payment declined | This authorization operation was definitively rejected. | Begin the specified compensation path. |
| Service unavailable / 503 | The call failed technically; its side effects may still need checking. | Retry or reconcile according to the API contract. |
| Timeout / connection lost | The caller did not obtain a conclusive result. | Preserve uncertainty. Reuse the operation identity or query status. |
| Confirmation timed out | The order may already be confirmed. | Do not void payment and release stock until that outcome is resolved. |

**Never infer “nothing happened” from “I did not receive success.”** A status query that says “not found” is also insufficient if the original request can still arrive later.

05 / FIRST PRINCIPLES

## Make retries and compensation durable

Identity, timing, and late messages determine whether recovery is actually safe.

### 25The dangerous unknown payment result

| Sequence | Coordinator observes | Payment side may have done |
| --- | --- | --- |
| 1. Send AuthorizePayment | Request sent | Receive request |
| 2. Authorization succeeds | No result yet | Create authorization |
| 3. Response is lost | Timeout | Keep the successful authorization |

A fresh operation identity can create a second authorization. Reuse the same key and payload under the provider’s documented contract, or query/reconcile the existing operation.

Provider guarantees have boundaries. Stripe, for example, persists the first executed result for an idempotency key and compares parameters; retries are not an unlimited, permanent global deduplication promise. [[6]](#ref6)

### 26Idempotent participant commands

Use a stable operation ID for “authorize this checkout attempt.” A transport delivery can have its own message ID; a retry must preserve the business operation ID and the immutable payload.

Deterministic ID for one occurrence of each demo stepJAVA

```
static UUID commandId(UUID sagaId, Step step) {
    String key = sagaId + ":" + step + ":1";
    return UUID.nameUUIDFromBytes(
            key.getBytes(StandardCharsets.UTF_8));
}
```

The suffix `:1` is the step occurrence. This sample permits one occurrence per step. Loops, partial shipments, or multiple authorizations need explicit iteration identities. This UUID is an identifier, not an authentication token.

Participants store the operation ID, canonical input or input hash, and terminal result. A duplicate should return or re-emit that stored result without repeating the effect. Conflicting payloads under the same key must be rejected.

### 27Compensation must also be idempotent

If a release succeeds and the response disappears, the retry must not add inventory a second time. Treat release as a guarded transition on a specific reservation.

Minimal domain transition; persistence and stock adjustment are separateJAVA

```
enum ReservationStatus { RESERVED, RELEASED }

record Reservation(ReservationStatus status) {
    Reservation release() {
        return status == ReservationStatus.RELEASED
                ? this : new Reservation(ReservationStatus.RELEASED);
    }
}
```

Inside one protected local transaction, change `RESERVED` to `RELEASED`, adjust held stock only if that change occurred, record the processed operation, and enqueue the result. An in-memory check followed by unprotected writes is not enough.

### 28Compensation can fail too

Payment declined, but Inventory is unavailable when the Saga requests a release. The reservation is still active. The correct status is “compensation in progress,” not “rolled back.”

Keep the obligation durable: which reservation needs release, which command identifies it, what result is still unknown, and when another attempt is due.

### 29Compensating is itself a workflow

1. Persist `RELEASING_INVENTORY` and the release command.
2. Retry delivery or reconcile the same operation until its result is known.
3. On `INVENTORY_RELEASED`, persist `CANCELLING_ORDER` and its command.
4. On `ORDER_CANCELLED`, mark the Saga `CANCELLED`.

`COMPLETED` and `CANCELLED` are resolved business outcomes. `MANUAL_INTERVENTION_REQUIRED` means automated execution has stopped with unresolved work; it is an operational handoff, not proof of consistency. [[3]](#ref3)

### 30What if compensation never succeeds?

Retry transient failures within a defined policy. If the operation is permanently rejected or cannot be resolved within the automated recovery budget, alert an owner and create a durable repair case. Preserve the pending command and resource identities.

A dead-letter queue is storage, not resolution. A repair process must reconcile participant state, choose a valid business action, record the operator’s decision, and safely resume or close the workflow. Monitor the age of unresolved obligations.

### 31Deadlines, late success, and cancellation races

A response deadline belongs in durable state. A worker reconstructs due work after restart. Inject a `Clock` at the application boundary and pass `clock.instant()` to the decision function; tests pass fixed instants.

**Deadline passed does not mean operation failed.** The demo retries the same pending operation, then hands off to reconciliation after an illustrative attempt budget. It never invents a payment decline from a timeout.

If the business requires cancellation while an operation is uncertain, the participant needs a protocol that closes the operation against future success. A reservation participant can retain a cancellation tombstone or generation fence, so a delayed reserve command cannot recreate a released reservation. Payments additionally require provider-aware reconciliation of any in-flight authorization.

Unexpected late success must be correlated and investigated. It may require voiding an authorization or releasing stock. Silently ignoring it because the Saga is already “cancelled” can leave real effects behind.

**No global isolation:** protect local invariants, use explicit pending/reservation states, and guard fulfillment from proceeding on unresolved checkout state. Optimistic locking on the Saga alone cannot isolate all participant actions. [[5]](#ref5)

06 / FIRST PRINCIPLES

## Choose who owns the sequence

Orchestration makes control flow explicit. Choreography distributes it across event reactions.

### 32Orchestration

A Checkout Saga coordinator chooses the next operation, tracks replies, manages deadlines, and decides compensation. It sends commands to Orders, Inventory, and Payments; each participant replies after making its local decision.

Logical centralization does not require one server process. Multiple workers can coordinate through durable state and concurrency control. The coordinator’s storage and dispatch path still need recovery and availability planning. [[5]](#ref5)

### 33Keep the orchestrator cohesive

The coordinator asks Inventory to reserve units. Inventory determines whether that is legal. The coordinator must not fetch stock rows, calculate availability, and write the participant’s tables directly.

Workflow policy answers “what happens next?” Participant domain rules answer “can this local action happen?” Respecting that split prevents the Saga from becoming a second implementation of every service.

### 34Keep dependencies pointed at contracts

| Coordinator should depend on | Coordinator should not depend on |
| --- | --- |
| Reserve/release command and result contracts | Inventory’s database schema |
| Authorize/void operation contracts | Provider implementation details duplicated in checkout |
| Confirm/cancel order contracts | Cross-service SQL updates |

Contracts still couple the participants semantically. Make that coupling explicit, versioned, and testable instead of hiding it in shared persistence access.

### 35Choreography

Instead of one coordinator issuing the sequence, services subscribe to facts and react. OrderPlaced causes Inventory to reserve; InventoryReserved causes Payments to authorize; PaymentAuthorized causes Orders to confirm.

The business workflow still exists. Its control flow lives in event contracts and subscriptions rather than one coordinator. [[8]](#ref8)

### 36The choreographed happy path

| Service observes | Service acts | Service publishes |
| --- | --- | --- |
| Orders receives checkout | Create pending order | OrderPlaced |
| Inventory receives OrderPlaced | Reserve stock | InventoryReserved |
| Payments receives InventoryReserved | Authorize payment | PaymentAuthorized |
| Orders receives PaymentAuthorized | Confirm order | OrderConfirmed |

Each row still needs local atomicity and reliable publication. Event-driven composition does not remove the outbox or duplicate handling.

### 37The choreographed failure path

PaymentDeclined might trigger Inventory to release and Orders to cancel. If those reactions are independent, they can happen in either order.

If the business contract requires “cancelled means stock is released,” Orders must wait for the release result or use an intermediate state. Two services subscribing to the same failure event do not automatically establish a completion barrier.

### 38The hidden coupling problem

Add fraud, shipping preparation, promotions, and loyalty. Each new event and failure path introduces more workflow dependencies. Finding the whole checkout process may require reading several services and deployment configurations.

That distribution can make global timeout, retry, and recovery policies harder to coordinate. It is a complexity trade-off, not a guarantee that choreography is simpler. [[8]](#ref8)

### 39Coupling moved; it did not disappear

Inventory must understand what OrderPlaced promises. Payments must know whether InventoryReserved is enough to authorize. Orders must interpret PaymentDeclined and delayed or repeated outcomes.

Direct call coupling may decrease while semantic and temporal coupling remain. Evaluate the total behavior of the workflow, not merely whether one service imports another service’s client library.

### 40Orchestration versus choreography

| Concern | Orchestration | Choreography |
| --- | --- | --- |
| Workflow ownership | Explicit coordinator | Distributed participant reactions |
| Visibility | One state model can expose progress | Requires cross-service correlation and projections |
| Coordination policy | Central place for deadlines and recovery | Distributed rules must remain compatible |
| Adding a dependent step | Change workflow and contracts | Change subscriptions and event semantics |
| Availability | Coordinator and state store are dependencies | No single coordinator; brokers and participants still matter |
| Common failure mode | Coordinator duplicates participant domain rules | Nobody owns the complete business process |

This comparison is a design assessment grounded in the two coordination models, not a universal performance ranking.

### 41Choose from the business process

When checkout has one sequence with explicit compensation dependencies, orchestration often makes ownership easier to inspect. When independent consumers respond to a fact for unrelated purposes, ordinary event-driven integration may be enough.

Choose choreography when the overall process stays understandable and the participants’ recovery obligations are explicit. Choose orchestration when coordinating those obligations is itself cohesive business policy.

### 42Not every event chain is a Saga

OrderConfirmed may feed analytics, a search index, and an email service. If the analytics consumer fails, should the order be cancelled? Usually that is not the required business response.

A Saga is useful when the steps cooperate toward a shared consistency outcome. Independent downstream reactions can recover on their own without reversing the originating business transaction.

07 / FIRST PRINCIPLES

## Preserve correctness at every boundary

The Saga composes local guarantees. It does not replace them.

### 43Each participant still needs a local transaction

1. Claim the command in an inbox or operation table with a unique identity.
2. Load the relevant aggregate with concurrency protection.
3. Validate and apply the business transition.
4. Persist its result and append an outgoing event to the local outbox.
5. Commit all those writes together; acknowledge delivery after commit.

If the claim commits but the business update does not, a retry may be incorrectly discarded. If the business update commits without its outgoing result, the Saga may wait forever. The shared local transaction prevents those gaps.

**Payment adapter exception:** an external provider call is outside this local transaction. Payments needs a durable operation record, a stable provider key, and status/webhook reconciliation to close its own uncertainty gap. An inbox row alone cannot make the provider exactly-once.

### 44Layer the guarantees

| Layer | Mechanism | Responsibility |
| --- | --- | --- |
| Local business correctness | Aggregate + transaction + concurrency control | Keep each local change valid and atomic. |
| Reliable communication | Outbox + relay + inbox / idempotency | Retain outgoing intent and tolerate repeated delivery. |
| Cross-service recovery | Durable Saga + participant recovery contracts | Continue, compensate, or escalate the business workflow. |
| Operational completion | Reconciliation + alerts + repair ownership | Find and resolve cases automation cannot finish. |

### 45Saga state has concurrent writers too

Two workers load Saga version 4 in WAITING\_FOR\_INVENTORY. Each sees a reservation success and wants to authorize payment. Guard the state update with the version that was read.

Optimistic compare-and-setSQL

```
UPDATE checkout_saga
SET state = 'WAITING_FOR_PAYMENT', version = 5
WHERE saga_id = :saga_id AND version = 4;
```

Exactly one matching update wins. The loser must roll back *the whole transaction*, including its inbox claim and outbox insert, reload, and evaluate again. Never publish the losing worker’s uncommitted decision.

### 46Duplicates remain expected

Optimistic locking prevents a stale simultaneous transition. It does not prevent relay redelivery after publication, participant retries, or duplicate provider notifications.

Use an inbox for exact incoming message IDs and domain idempotency for the business operation. Keep deduplication records long enough for the accepted replay and recovery window; define behavior when that window expires.

When a response is missing, retrying a known command should be able to recover its stored result. “Duplicate: do nothing” is insufficient if the only original response was lost or expired.

### 47Write the failure matrix before implementation

| Failure | Required behavior in this guide |
| --- | --- |
| Order creation rejected | No initial Saga command is committed. |
| Inventory definitively unavailable | Cancel the pending order; do not authorize payment. |
| Inventory outcome unknown | Retry/reconcile the same operation; do not assume no reservation. |
| Payment declined after reservation | Release inventory, then cancel order. |
| Payment outcome unknown | Recover the existing authorization result; preserve identity. |
| Confirmation definitively rejected | Void known authorization, release stock, cancel order. |
| Confirmation result unknown | Resolve confirmation before compensating resources. |
| Orchestrator crashes | Resume from durable state, inbox, outbox, and deadlines. |
| Duplicate command or event | One logical business effect and transition. |
| Late or contradictory success | Durably reconcile; do not silently discard. |
| Compensation temporarily fails | Keep the obligation; retry safely. |
| Compensation cannot be resolved automatically | Alert and hand off with evidence and pending work. |
| Concurrent Saga update | Roll back losing transaction and re-evaluate. |
| Publication fails | Retain outbox work for relay recovery. |
| Reservation or authorization expires | Revalidate the workflow’s success conditions and recover according to policy. |

08 / FIRST PRINCIPLES

## Test the failure paths

Prove what the workflow does when effects and acknowledgements separate.

### 48Happy path: confirm the actual success contract

Drive inventory success, payment authorization, and order confirmation. Assert Saga = COMPLETED, Order = CONFIRMED, Inventory = RESERVED, and Payment = AUTHORIZED.

Verify that confirmation is a known committed result, not simply a command that was sent. At system level, check the resources are still valid under the reservation and authorization expiry policy.

### 49Inventory rejected

Deliver a definitive inventory rejection. Assert no payment authorization is requested, cancellation is requested, and the Saga becomes CANCELLED only after the cancellation result arrives.

### 50Payment rejected

Deliver InventoryReserved and then PaymentDeclined. Assert ReleaseInventory is emitted first. Assert CancelOrder appears only after InventoryReleased. Verify stock is released once and no authorization exists for the declined operation.

### 51Compensation fails

Make a release request time out. Assert the Saga does not claim CANCELLED and retains the pending release operation. Retry safely; when the release result is known, cancellation can continue.

Also test a permanent rejection or exhausted automated recovery budget. Manual intervention must preserve the unresolved obligation instead of disguising it as successful compensation.

### 52Duplicate and late events

Deliver the same InventoryReserved event twice. The durable inbox should make one logical transition. Then deliver a second event ID for the same operation and a late success after handoff.

Assert no second authorization is created. The core’s unexpected-reply result must create a durable reconciliation record, not an acknowledgement followed by silent loss.

### 53Crash after Saga commit, before publication

Commit the Saga transition and outbox insert, stop the process before relay publication, then restart it. Verify the durable outbox work is published.

Inject failure before commit as a separate case: neither the advanced Saga nor its outgoing message may survive. This is an integration test of the actual database transaction.

### 54Crash after publication, before relay acknowledgement

Publish a command, then crash before marking its outbox record delivered. On restart, allow redelivery. Verify the participant applies the business operation once and can recover the same result.

### 55Payment succeeds but the response is lost

Simulate the provider creating an authorization while the response disappears. Replay the same authorization identity and payload through the payment adapter.

Assert one effective authorization and a resolved participant operation. Also test provider-key retention expiry and a response that remains unknown; neither permits blindly starting a second operation.

### 56Concurrent orchestrator workers

Let two real database transactions load the same Saga version. Assert one state transition commits, the other gets a conflict, and the losing transaction contributes no inbox claim or outgoing command.

On retry, verify the second worker observes the new state or inbox entry. A single-threaded state-machine test cannot prove these database guarantees.

### 57Deadline and stale timer

Pass a fixed Instant before, at, and after the deadline. Assert no early retry and a retry using the identical operation ID and payload when due. Deliver the old step’s timer after the Saga advances; it must not affect the new pending operation.

Race timeout processing against a successful reply using real version checks. Include a delayed success after automatic execution has handed off to reconciliation. [[10]](#ref10)

### 58Separate unit, integration, and system evidence

| Level | Exercise | Evidence |
| --- | --- | --- |
| Unit | State + correlated fact + fixed time | Correct branch, command identity, deadline behavior, handoff. |
| Integration | Real database and transaction boundaries | Atomic inbox/state/outbox, rollback, constraints, version conflicts. |
| System | Services, broker, provider adapter, fault injection | Recovery from outages, lost replies, duplicates, restarts, late work. |

The downloadable example tests the unit-level decision core only. It includes success, inventory rejection, payment decline, authorization voiding, duplicate/stale replies, early/stale timers, identical retries, and unresolved-compensation handoff. It does not claim to test a database or broker.

09 / FIRST PRINCIPLES

## Make the workflow operable

A workflow that can wait for minutes or days needs visible obligations and clear ownership.

### 59Carry enough identity to reconstruct the story

| Field | Purpose |
| --- | --- |
| `sagaId` | Identify this workflow instance. |
| `orderId` | Connect the workflow to the business record. |
| `messageId / eventId` | Deduplicate a transport message or result. |
| `operationId / commandId` | Identify the logical side effect across deliveries. |
| `causationId` | Connect a reply or command to what caused it. |
| `correlationId / trace context` | Connect traces and conversations across services. |
| `resourceId + definitionVersion` | Find actual holds and apply the correct workflow rules. |

Expose state, age, pending command, attempts, deadline, last known participant outcome, next retry, and compensation status. Useful measures include oldest pending Saga, oldest compensation, outbox lag, and unresolved repair cases.

### 60Log business progress, not just HTTP failures

Illustrative operational recordTEXT

```
sagaId=S456 orderId=O123
state=WAITING_FOR_PAYMENT
commandId=AUTH-123 attempt=3
lastObservation=response_timeout
outcome=UNKNOWN
nextAction=reconcile_existing_authorization
nextCheckAt=2026-01-01T10:02:00Z
```

A support view should answer “what happened, what is still unknown, and who must act next?” Avoid logging payment credentials or sensitive payloads merely to make correlation easier.

Monitor the participant operation as well as the orchestrator. A clean coordinator log cannot prove that an external authorization was never created.

10 / FIRST PRINCIPLES

## Know when the pattern is wrong

A Saga cannot invent an acceptable partial outcome or replace a missing business decision.

### 61When not to use a Saga

| Situation | Better starting point |
| --- | --- |
| All required effects fit one real transaction | Use the local transaction. |
| Consumers react independently to a fact | Use ordinary event processing and independent retries. |
| No externally visible intermediate state is allowed | Revisit service boundaries or supported transactional infrastructure. |
| Irreversible partial completion is unacceptable | Redesign the operation before choosing infrastructure. |

Saga explicitly permits independently committed intermediate states. Calling a workflow “eventually consistent” does not satisfy a requirement for immediate global atomicity.

### 62Avoid the giant orchestrator

If checkout duplicates stock allocation rules, payment routing rules, tax calculation, and shipping eligibility, every participant change now has another home.

Move those rules back to their owners. The orchestrator should coordinate outcomes and policy, not implement each participant’s internals.

### 63Avoid an ownerless event web

The opposite failure is spreading one business process across enough subscriptions that nobody can explain the complete recovery path. Circular reactions and incompatible timeout decisions can become hard to spot.

Assign ownership for the full consistency contract even when execution is choreographed. If sequencing is cohesive policy, an explicit orchestrator may make the system easier to change and operate.

11 / FIRST PRINCIPLES

## Connect the patterns without conflating them

Each mechanism answers a different question.

### 64Aggregate

An aggregate defines a local consistency boundary: what must remain valid together when one local action commits? A Saga coordinates several such boundaries over time.

Do not treat Order, Inventory, and Payment as a single imaginary distributed aggregate. Their independent commits are the reason the Saga is needed.

### 65Optimistic concurrency

Order v7, Inventory v12, Payment v3, and Saga v9 can each have concurrent writers. Protect each local update according to its invariants. A Saga does not remove concurrent modification or provide global isolation.

### 66Transactional Outbox

The Saga decides what should happen next. The outbox retains that outgoing intent alongside the committed state change. Relay recovery turns the retained intent into a publication attempt.

State plus message must share a transaction at both the orchestrator and the participants. Never treat a successful database commit as proof the remote operation already happened.

### 67Inbox and business idempotency

The inbox recognizes a message that was already processed. Business idempotency recognizes the same logical operation even if it arrives under another delivery envelope.

Both forward actions and compensations need this protection. The participant also retains enough result information to let a recovering coordinator learn what happened.

### 68State

A state machine maps state and input to allowed behavior. A Saga commonly uses one, but also needs durable progress, participant contracts, recovery, time, and messaging.

The State pattern alone is not a distributed workflow implementation.

### 69Command and event

AuthorizePayment requests work; PaymentAuthorized reports its result. The Saga interprets that fact and chooses a next command.

Keep request identity distinct from event identity, and correlate them. A generic “payment failed” event that mixes rejection with transport uncertainty prevents correct recovery decisions.

### 70The complete message cycle

| Stage | Atomic local work | After commit |
| --- | --- | --- |
| Coordinator receives result | Inbox claim + Saga transition + outgoing outbox record | Acknowledge incoming delivery. |
| Coordinator relay | Read committed outgoing command; record delivery progress | Publish or safely retry publication. |
| Participant receives command | Operation/inbox claim + aggregate change + result outbox | Acknowledge command; relay publishes result. |
| Coordinator receives next result | Correlate operation; repeat guarded transition | Continue, compensate, or create a repair obligation. |

The relay cannot atomically commit its database marker with a normal broker publication. That is precisely why repeat publication remains possible. The payment provider boundary adds its own durable operation and reconciliation cycle.

12 / FIRST PRINCIPLES

## State the guarantee honestly

Success is a known business outcome. Unresolved work stays visible.

### 71What are we actually promising?

**Contract:** each participant protects its own local changes. The Saga durably tracks known progress and unresolved operations, then continues, compensates, or hands off for repair. Repeated delivery must not create repeated business effects.

This is not global ACID, global isolation, or unconditional exactly-once execution. Automatic completion depends on recoverable infrastructure, correct participant behavior, retained records, valid resource lifetimes, and a recovery path that can actually succeed.

Define success and cancellation as predicates over real participant outcomes. Do not label an order fully cancelled while an unknown authorization or reservation obligation is still unresolved.

### 72Rebuild the reasoning from first principles

1. One business operation spans independently committed boundaries.
2. A later failure cannot roll back earlier committed work.
3. Recovery therefore requires new business operations.
4. Some failures should retry forward; others require compensation.
5. Timeouts leave uncertainty that must be resolved.
6. Workflow progress and outgoing intent must survive crashes.
7. Repeated delivery requires stable identity and idempotency.
8. Compensation can fail, so recovery also needs durable state.
9. Late results and concurrent work require explicit rules.
10. Someone must own the full business consistency contract.

That pressure derives the Saga. The next pressure is how to retry remote dependencies without multiplying their load during an outage: **timeout, retry, exponential backoff, jitter**, followed by circuit breakers.

APPENDIX A / EXECUTABLE MODEL

## A complete Java decision core

Save the source as CheckoutSagaDemo.java. It needs no framework or external library.

The implementation makes one deliberate boundary choice: a pending order, the initial Saga, and its first outgoing command are created in the Orders database transaction. The sample below implements the decisions, not that transaction.

The checkout contains one SKU, one authorization, and one occurrence of each step. Money uses a positive integer in minor units plus a currency code. Real checkout input also needs price validation, currency-specific precision, reservation and provider references, and authorization validity checks.

**Implementation boundary.** No broker, database adapter, inbox, provider, scheduler, or repair queue is implemented here. `RECONCILE` is an obligation for the caller to persist. The fixed 30-second window and three attempts are illustrative, not operational recommendations.

Compile and run with JDK 25SHELL

```
javac --release 25 -Xlint:all CheckoutSagaDemo.java
java CheckoutSagaDemo
```

Expected output: `PASS: checkout decisions and failure-path checks`.

Compatibility: the code uses stable records, enums, switch expressions, UUID, and java.time APIs documented for Java 25, with no preview flags. Validation here compiled and ran this exact source with JDK 17; a JDK 25 runtime was not available. The command above is the JDK 25 reproduction command. [[9]](#ref9) [[11]](#ref11) [[12]](#ref12)

Download Java sourceCopy Java source

CheckoutSagaDemo.java — complete source, including executable checksJAVA

```
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/** Decision model only: no database, broker, or payment provider. */
public final class CheckoutSagaDemo {
    enum State {
        WAITING_FOR_INVENTORY, WAITING_FOR_PAYMENT, CONFIRMING_ORDER,
        VOIDING_PAYMENT, RELEASING_INVENTORY, CANCELLING_ORDER,
        COMPLETED, CANCELLED, MANUAL_INTERVENTION_REQUIRED
    }

    enum Step {
        RESERVE_INVENTORY, AUTHORIZE_PAYMENT, CONFIRM_ORDER,
        VOID_AUTHORIZATION, RELEASE_INVENTORY, CANCEL_ORDER
    }

    enum Fact {
        INVENTORY_RESERVED, INVENTORY_REJECTED,
        PAYMENT_AUTHORIZED, PAYMENT_DECLINED,
        ORDER_CONFIRMED, ORDER_CONFIRMATION_REJECTED,
        AUTHORIZATION_VOIDED, INVENTORY_RELEASED, ORDER_CANCELLED
    }

    enum Handling { APPLIED, NO_CHANGE, RECONCILE }

    // One SKU, one authorization, one occurrence of each step in this demo.
    record Checkout(UUID orderId, String sku, int quantity,
                    long amountMinor, String currency) {
        Checkout {
            Objects.requireNonNull(orderId);
            Objects.requireNonNull(sku);
            Objects.requireNonNull(currency);
            if (sku.isBlank() || quantity <= 0 || amountMinor <= 0
                    || !currency.matches("[A-Z]{3}")) {
                throw new IllegalArgumentException("Invalid checkout");
            }
        }
    }

    record Command(UUID commandId, UUID sagaId, Step step,
                   Checkout checkout) {}

    record Reply(UUID eventId, UUID sagaId, UUID orderId,
                 UUID causationId, Fact fact) {}

    // Persist these fields; pending is retained during manual intervention.
    record Saga(UUID sagaId, Checkout checkout, State state,
                Command pending, Instant deadline, int attempts) {}

    record Decision(Saga saga, List<Command> outgoing,
                    Handling handling) {
        Decision { outgoing = List.copyOf(outgoing); }
    }

    // Illustrative policy, not a recommended production timeout.
    static final Duration RESPONSE_WINDOW = Duration.ofSeconds(30);
    static final int MAX_ATTEMPTS = 3;

    static UUID commandId(UUID sagaId, Step step) {
        String key = sagaId + ":" + step + ":1";
        return UUID.nameUUIDFromBytes(
                key.getBytes(StandardCharsets.UTF_8));
    }

    static Decision issue(Saga old, State state, Step step, Instant now) {
        Command command = new Command(commandId(old.sagaId(), step),
                old.sagaId(), step, old.checkout());
        Saga next = new Saga(old.sagaId(), old.checkout(), state,
                command, now.plus(RESPONSE_WINDOW), 1);
        return new Decision(next, List.of(command), Handling.APPLIED);
    }

    // Precondition: PENDING order + initial saga/outbox are committed together
    // in the Order service's database. This method makes only the decision.
    static Decision start(UUID sagaId, Checkout checkout, Instant now) {
        Saga seed = new Saga(sagaId, checkout,
                State.WAITING_FOR_INVENTORY, null, null, 0);
        return issue(seed, State.WAITING_FOR_INVENTORY,
                Step.RESERVE_INVENTORY, now);
    }

    static Decision finish(Saga old, State state) {
        Saga next = new Saga(old.sagaId(), old.checkout(), state,
                null, null, old.attempts());
        return new Decision(next, List.of(), Handling.APPLIED);
    }

    static Decision reconcile(Saga saga) {
        // Caller durably records this reply for investigation/reconciliation.
        // Do not acknowledge it as successfully applied and discard it.
        return new Decision(saga, List.of(), Handling.RECONCILE);
    }

    static Decision on(Saga saga, Reply reply, Instant now) {
        Objects.requireNonNull(reply.fact());
        if (!saga.sagaId().equals(reply.sagaId())
                || !saga.checkout().orderId().equals(reply.orderId())
                || saga.pending() == null
                || !saga.pending().commandId().equals(reply.causationId())) {
            return reconcile(saga);
        }

        return switch (saga.state()) {
            case WAITING_FOR_INVENTORY -> switch (reply.fact()) {
                case INVENTORY_RESERVED -> issue(saga,
                        State.WAITING_FOR_PAYMENT,
                        Step.AUTHORIZE_PAYMENT, now);
                case INVENTORY_REJECTED -> issue(saga,
                        State.CANCELLING_ORDER, Step.CANCEL_ORDER, now);
                default -> reconcile(saga);
            };
            case WAITING_FOR_PAYMENT -> switch (reply.fact()) {
                case PAYMENT_AUTHORIZED -> issue(saga,
                        State.CONFIRMING_ORDER, Step.CONFIRM_ORDER, now);
                case PAYMENT_DECLINED -> issue(saga,
                        State.RELEASING_INVENTORY,
                        Step.RELEASE_INVENTORY, now);
                default -> reconcile(saga);
            };
            case CONFIRMING_ORDER -> switch (reply.fact()) {
                case ORDER_CONFIRMED -> finish(saga, State.COMPLETED);
                // Definitive rejection: Orders guarantees this confirmation
                // operation cannot later succeed. A timeout is not rejection.
                case ORDER_CONFIRMATION_REJECTED -> issue(saga,
                        State.VOIDING_PAYMENT, Step.VOID_AUTHORIZATION, now);
                default -> reconcile(saga);
            };
            case VOIDING_PAYMENT -> reply.fact() == Fact.AUTHORIZATION_VOIDED
                    ? issue(saga, State.RELEASING_INVENTORY,
                            Step.RELEASE_INVENTORY, now)
                    : reconcile(saga);
            case RELEASING_INVENTORY -> reply.fact() == Fact.INVENTORY_RELEASED
                    ? issue(saga, State.CANCELLING_ORDER,
                            Step.CANCEL_ORDER, now)
                    : reconcile(saga);
            case CANCELLING_ORDER -> reply.fact() == Fact.ORDER_CANCELLED
                    ? finish(saga, State.CANCELLED) : reconcile(saga);
            default -> reconcile(saga);
        };
    }

    static Decision onDeadline(Saga saga, UUID expectedCommand,
                               Instant now) {
        // Timer carries command identity; an old timer cannot retry a new step.
        if (saga.pending() == null
                || saga.state() == State.MANUAL_INTERVENTION_REQUIRED
                || !saga.pending().commandId().equals(expectedCommand)
                || now.isBefore(saga.deadline())) {
            return new Decision(saga, List.of(), Handling.NO_CHANGE);
        }
        if (saga.attempts() >= MAX_ATTEMPTS) {
            Saga next = new Saga(saga.sagaId(), saga.checkout(),
                    State.MANUAL_INTERVENTION_REQUIRED,
                    saga.pending(), saga.deadline(), saga.attempts());
            return new Decision(next, List.of(), Handling.APPLIED);
        }
        Saga next = new Saga(saga.sagaId(), saga.checkout(), saga.state(),
                saga.pending(), now.plus(RESPONSE_WINDOW),
                saga.attempts() + 1);
        // Same commandId AND same payload. New delivery is not a new operation.
        return new Decision(next, List.of(saga.pending()), Handling.APPLIED);
    }

    // Small executable checks. They use fixed time, not Thread.sleep().
    static Reply reply(Saga saga, Fact fact) {
        return new Reply(UUID.randomUUID(), saga.sagaId(),
                saga.checkout().orderId(), saga.pending().commandId(), fact);
    }

    static Saga advance(Saga saga, Fact fact, Instant now) {
        Decision decision = on(saga, reply(saga, fact), now);
        check(decision.handling() == Handling.APPLIED, "Reply must apply");
        return decision.saga();
    }

    static void check(boolean condition, String label) {
        if (!condition) throw new AssertionError(label);
    }

    public static void main(String[] args) {
        Instant now = Instant.parse("2026-01-01T10:00:00Z");
        Checkout checkout = new Checkout(UUID.randomUUID(), "BOOK-1",
                1, 2500, "USD");
        Saga initial = start(UUID.randomUUID(), checkout, now).saga();
        Reply reserved = reply(initial, Fact.INVENTORY_RESERVED);
        Saga payment = on(initial, reserved, now).saga();
        Saga confirming = advance(payment, Fact.PAYMENT_AUTHORIZED, now);
        check(advance(confirming, Fact.ORDER_CONFIRMED, now).state()
                == State.COMPLETED, "Happy path");

        Saga cancelling = advance(initial, Fact.INVENTORY_REJECTED, now);
        check(cancelling.pending().step() == Step.CANCEL_ORDER,
                "Inventory rejection must not authorize payment");
        check(advance(cancelling, Fact.ORDER_CANCELLED, now).state()
                == State.CANCELLED, "Inventory rejection path");

        Saga releasing = advance(payment, Fact.PAYMENT_DECLINED, now);
        check(releasing.state() == State.RELEASING_INVENTORY,
                "Payment decline must release inventory");
        Saga cancelAfterRelease = advance(releasing, Fact.INVENTORY_RELEASED, now);
        check(advance(cancelAfterRelease, Fact.ORDER_CANCELLED, now).state()
                == State.CANCELLED, "Payment rejection path");

        Saga voiding = advance(confirming, Fact.ORDER_CONFIRMATION_REJECTED, now);
        Saga afterVoid = advance(voiding, Fact.AUTHORIZATION_VOIDED, now);
        check(afterVoid.state() == State.RELEASING_INVENTORY,
                "Void authorization before releasing inventory");

        Decision duplicate = on(payment, reserved, now);
        check(duplicate.outgoing().isEmpty()
                && duplicate.handling() == Handling.RECONCILE,
                "Core must not emit a second authorization");
        // The durable inbox short-circuits exact eventId duplicates before on().

        Decision early = onDeadline(payment, payment.pending().commandId(), now);
        check(early.handling() == Handling.NO_CHANGE, "Early timer");
        Decision stale = onDeadline(payment, initial.pending().commandId(),
                payment.deadline());
        check(stale.handling() == Handling.NO_CHANGE, "Stale timer");
        Decision retry = onDeadline(payment, payment.pending().commandId(),
                payment.deadline());
        check(retry.saga().state() == State.WAITING_FOR_PAYMENT
                && retry.outgoing().get(0).equals(payment.pending()),
                "Unknown payment result retries identical operation");

        Saga stuck = releasing;
        for (int i = 0; i < MAX_ATTEMPTS; i++) {
            stuck = onDeadline(stuck, stuck.pending().commandId(),
                    stuck.deadline()).saga();
        }
        check(stuck.state() == State.MANUAL_INTERVENTION_REQUIRED
                && stuck.pending().step() == Step.RELEASE_INVENTORY,
                "Failed compensation must retain unresolved obligation");
        Decision late = on(stuck, reply(stuck, Fact.INVENTORY_RELEASED), now);
        check(late.handling() == Handling.RECONCILE,
                "Late success after handoff must be reconciled");
        System.out.println("PASS: checkout decisions and failure-path checks");
    }
}
```

APPENDIX B / PERSISTENCE CONTRACT

## What the application adapter must implement

The state machine decides. One real local transaction records the consequences.

1. **Begin a transaction.** Use one connection/transaction context for inbox, Saga, outbox, and repair writes.
2. **Claim event identity.** Insert a unique inbox record. If an already committed identical event exists, recover its prior handling result and acknowledge it. A payload conflict is an error.
3. **Load the versioned Saga.** Validate sagaId, orderId, producer, message schema, and causationId. Do not trust arbitrary messages to drive the workflow.
4. **Run the pure decision.** Pass the stored Saga and the current Instant. No remote calls occur while deciding.
5. **Apply or reconcile.** On APPLIED, compare-and-set the expected Saga version. On RECONCILE, durably record the unexpected reply and create an actionable reconciliation obligation. Unknown Saga IDs need a bounded parking/repair policy.
6. **Append outgoing commands.** Preserve commandId and payload for the logical operation. If the outbox has a unique delivery-row ID, an explicit retry can use a new delivery ID carrying the same commandId; alternatively re-arm the retained outbox row. Do not silently lose retries by colliding with an already-delivered unique outbox ID.
7. **Commit all writes.** A compare-and-set conflict or any write failure rolls back the inbox claim and all other writes. Retry from a fresh load.
8. **Acknowledge after commit.** Then let the relay publish committed outgoing work. Do not acknowledge a message whose decision or reconciliation obligation was lost.

Timer handling follows the same versioned transaction discipline. Persist/reconstruct deadlines and compare the expected command identity so a stale timer cannot affect a later step. An attempt counter records scheduled logical attempts; relay redeliveries may produce more actual deliveries.

For an explicit retry, participant idempotency must replay the saved terminal result or restore a durable response publication obligation. For a provider call, the participant must also recover its external operation’s state.

Confirmation and cancellation need mutually valid, versioned Order transitions. The sample’s ORDER\_CONFIRMATION\_REJECTED means the particular confirmation operation is definitively rejected and cannot later commit. If that contract is unavailable, route the situation to reconciliation instead of executing that branch.

REFERENCE NOTES

## Official sources and scope

Prepared from the supplied lesson, preserving its 72-step progression. Official sources were checked on 2 September 2026. The checkout policies, state names, schema, and code are teaching designs; they are not quoted provider implementations.

The guide tightens four points: durable state records known progress; timeouts do not imply rejection; late results need reconciliation; manual intervention is an unresolved handoff. Source links remain available offline as text, while opening them requires internet access.

1. [PostgreSQL — Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)

   Local commit/rollback and visibility.

   https://www.postgresql.org/docs/current/tutorial-transactions.html
2. [AWS — Saga patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-patterns.html)

   Sequence of local transactions; continuation and compensation.

   https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-patterns.html
3. [Microsoft — Compensating Transaction pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)

   Business-specific compensation, ordering, idempotency, recovery, and human intervention.

   https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
4. [AWS — Transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

   Local state and publication intent; duplicates and consumer idempotency.

   https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
5. [AWS — Saga orchestration](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html)

   Coordinator responsibilities, isolation limits, and operational concerns.

   https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html
6. [Stripe — Idempotent requests](https://docs.stripe.com/api/idempotent_requests)

   Provider-specific key, payload, and stored-result contract.

   https://docs.stripe.com/api/idempotent\_requests
7. [Stripe — Place a hold on a payment method](https://docs.stripe.com/payments/place-a-hold-on-a-payment-method)

   Authorization, later capture, cancellation, and expiry.

   https://docs.stripe.com/payments/place-a-hold-on-a-payment-method
8. [AWS — Saga choreography](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-choreography.html)

   Event subscriptions, distributed coordination, and complexity.

   https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-choreography.html
9. [Oracle Java 25 — Record classes](https://docs.oracle.com/en/java/javase/25/language/records.html)

   Record syntax and generated members.

   https://docs.oracle.com/en/java/javase/25/language/records.html
10. [Oracle Java 25 — Clock](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html)

    Injectable time sources and fixed clocks for tests.

    https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html
11. [Oracle Java 25 — UUID](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/UUID.html)

    Name-based UUID and random UUID APIs.

    https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/UUID.html
12. [Oracle Java 25 — javac](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html)

    Compiler release targeting and lint options.

    https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html

DP · 22. Saga + Compensating TransactionsFirst principles → recoverable business workflow