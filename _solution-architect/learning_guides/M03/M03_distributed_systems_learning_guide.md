# M03 — The essential distributed-systems mental model

**Beginner-first learning and speaking guide · 24 October 2026**  
**Authoritative syllabus:** `__sa_beginner_first_curriculum.md`, mission M03 (L29–L40).  
**Scope:** One complete study resource, **not** one lesson to deliver in a single tutoring turn.  
**Practice context:** A **hypothetical** commercial spending platform; no American Express internal architecture is
assumed or claimed.

> **The mental model:** A program can send a request to another program, but it cannot always tell whether the other
> program completed the work. Different machines can fail or be delayed independently. Safe design starts by
> distinguishing **what happened**, **what we observed**, and **what remains unknown**.

## How to use this guide

1. Start at **L29** only after the M01 request/network/database basics and M02 business journey are familiar. If these
   feel unclear, return to those prerequisites first. **Do not begin with a diagnostic.**
2. Work on **one lesson per conversation/session**. First read *Purpose*, *Example*, and *Trace*. Then answer the **one
   immediate check**. Do not read the answer key before attempting it.
3. After the check, say a **single sentence in your own words**. Then do the *Small change* exercise. Only afterward try
   the 2–4 sentence interview version and its judgment prompt.
4. If you cannot explain a step, use the sentence starter and replay the original example. Progress depends on
   understanding, not speed.
5. Keep a short progress note. Review material already taught after roughly 1, 3, 7, and 21 days if useful; those are
   flexible review intervals, not a scientific prescription.

**M03 exit gate:** Trace a normal request, explain one failure, apply the idea to a nearby case, and explain it clearly
for **30–60 seconds**. A full senior panel answer is **not** expected yet.

**Tutor feedback pattern:** `UNDERSTANDING: ... | SPECIFIC FIX: ... | SPEAKING: ... | TRY AGAIN: ... | NEXT: ...`.
Correct technical meaning first; improve wording second. If the learner misses twice, teach differently before trying
again.

### Five prerequisite facts to remember, not to test cold

A **process** is a running program. A **client** sends a **request** to a **server**, which may send back a
**response**. A **network** carries information between machines and can delay or lose communication. A **database
transaction** groups supported local operations so that they commit together or roll back. An **API contract** states
how programs exchange requests and responses. These ideas are from M01; the business journey and requirement/assumption
distinction come from M02.

### Running case — first learn the normal path

An employee submits a purchase request. The platform checks an organization's spending policy. Some requests also need a
remote risk check. A separate payment provider may later receive an instruction. Finance needs accurate status. All
services, timings, policies, and amounts below are **made-up training assumptions**.

```text
Employee     Purchase application        Policy data       Risk service       Provider
   |                  |                       |                  |              |
   |-- submit ------->|                       |                  |              |
   |                  |-- read -------------->|                  |              |
   |                  |<-- allowed -----------|                  |              |
   |                  |-- check, if needed --------------------->|              |
   |                  |<-- risk result --------------------------|              |
   |                  |-- record request state |                  |              |
   |                  |-- send financial instruction, if authorized ----------->|
   |                  |<-- provider reply, if delivered -----------------------|
   |<-- truthful status + request ID ---------|                  |              |
```

A `request_id` identifies a **logical business request**. A network **attempt** is one effort to send or execute work.
One logical request can have several attempts. Do not assume that a timeout or a response labeled “accepted” proves that
money moved or final settlement occurred. The provider contract and business policy must define these states; M05 treats
them in depth.

---

## L29 — One running program versus two programs communicating

**Purpose.** Inside one running program, a function can call another function directly. With two programs on different
machines, one program sends information across a network. The other program may be slow, unreachable, or fail
independently.

**Tiny example.** Asking a colleague beside you is not the same as mailing a request to another office. You may send the
letter but not know when it arrived. **Limit of the analogy:** Networks deliver digital messages under protocols;
delivery, security, and retry behavior depend on the specific system.

**Trace the normal path.**

1. The purchase program receives `request_id = R-17`.
2. In one process, it calls `check_policy(900, 1000)` as an ordinary function and receives `True`.
3. In a two-program design, it instead sends a message to a policy service.
4. That service evaluates the request and sends a reply over the network.

```text
ONE PROCESS                        TWO PROGRAMS
+----------------------+           +-------------+      network      +-------------+
| Purchase program     |           | Purchase    |------------------>| Policy      |
|  -> check_policy()   |           | program     |<------------------| service     |
+----------------------+           +-------------+                   +-------------+
Direct call inside process          Request and separate response
```

**Immediate check — answer before continuing.** In the two-program picture, what carries the request between programs?

**Speak.** “When two programs run separately, they communicate by ___.” Then add: “This matters because ___.”

**Small change, later.** Suppose the policy service is running but its network link stops working. Can the purchase
program still receive its answer?

**Later interview form (read only after your own attempt).** “A local function call stays inside a running process,
whereas a remote service call crosses a communication boundary. That introduces independent failures, delays, and
uncertain replies. I choose the boundary only when its business and operational benefits justify those costs.”

**Review cue.** Draw a line between *same process* and *remote process*, and describe what crosses the line.

## L30 — Modular monolith versus separate services

**Purpose.** A **modular monolith** is one deployable application with clear internal modules. **Separate services** run
and deploy independently and communicate through explicit interfaces. More services do not automatically make a system
better.

**Tiny example.** One shop can have separate counters inside the same building. Two independent shops need delivery and
coordination between them. **Limit:** Software modules can share one deployment and transaction; shops do not precisely
model code or data ownership.

**Trace the choice.**

1. A purchase module accepts the request.
2. A policy module checks a rule. In a modular monolith, this may be a local function call.
3. A reporting module records a view. It can be internal or a separate service.
4. With separately deployed services, their owners must specify calls, data authority, timeouts, and recovery paths.

```text
OPTION A: one deployable app          OPTION B: separately deployed
+-----------------------------+       +----------+   API   +----------+
| Purchase | Policy | Report  |       | Purchase |-------->| Policy   |
|   modules, clear boundaries |       +----------+         +----------+
+-----------------------------+            |
           |                               +------API------> Reporting
        Database                         (different release/failure boundaries)
```

| Question                             | Modular monolith         | Separate services                   |
|--------------------------------------|--------------------------|-------------------------------------|
| Independent deployment needed?       | Usually no               | Possible                            |
| Remote hops between these modules?   | Not needed               | Usually yes                         |
| Operational coordination             | Often simpler            | More contracts and monitoring       |
| Can it still have distributed risks? | Yes: remote DB/providers | Yes: between services and providers |

**Immediate check.** Can one modular monolith still depend on a remote database or payment provider?

**Speak.** “I would start with ___ when ___, because ___.”

**Small change, later.** Reporting now has its own team and must deploy independently every day. How might that change
the boundary choice?

**Later interview form.** “I would first test whether clear modules in one application meet the team and release needs.
Separate services offer independent deployment and scaling but add network failure modes, data ownership, and
operational cost. I would split when a specific constraint justifies those costs.”

**Review cue.** Explain why “microservices everywhere” is not a design requirement.

## L31 — Network call, latency, and a normal request timeline

**Purpose.** **Latency** is elapsed time between starting an operation and receiving the outcome being measured. A
remote call spends time in the network, queues, and server work, so multiple calls can add delay.

**Tiny example.** Sending a form to another desk takes delivery time, processing time, and return time. **Limit:** Real
networks can vary sharply, and queued requests can overtake each other.

**Trace a normal call.** These milliseconds are **hypothetical teaching values**, not measured service targets.

1. At `t=0 ms`, the purchase service sends a policy request.
2. Request travel takes 20 ms; policy processing takes 40 ms.
3. Reply travel takes 20 ms.
4. The caller receives the response at `t=80 ms`. Observed call latency is **80 ms**.

```text
Time        Purchase program                  Policy program
0 ms        send ----------------------------->
20 ms                                            receive
20–60 ms                                         work (40 ms)
60 ms       <-------------------------------   reply
80 ms       receive result
```

If a risk call of 150 ms starts **after** the policy call, these two calls alone cost about `80 + 150 = 230 ms` on this
hypothetical path. If independent work can safely run in parallel, elapsed time may be closer to the longer branch plus
coordination overhead. Do not parallelize work that depends on a prior decision.

**Immediate check.** In the 80 ms example, how much time did policy processing itself take?

**Speak.** “A remote call's time includes ___, ___, and ___.”

**Small change, later.** The policy service starts queuing requests for 120 ms. What happens to total elapsed time if
all else stays equal?

**Later interview form.** “I would draw the critical request path and measure elapsed time at each hop. Serial
dependencies add to user-visible latency, while queueing and variable remote delays often affect slow requests most. I
would allocate a provisional end-to-end budget and validate it with measurements.”

**Review cue.** Distinguish **one hop’s elapsed time** from **total journey time**. A sum of individual high-percentile
timings is not itself a guaranteed journey percentile.

## L32 — What failure looks like: crash, missing reply, delayed reply

**Purpose.** A **crash** stops a running process. A **missing reply** means the caller did not receive an answer. A
**delayed reply** may arrive too late to be useful. These events look different from the caller’s point of view.

**Tiny example.** A courier might never reach the office, deliver a message but lose the receipt, or return the receipt
tomorrow. **Limit:** The analogy does not provide evidence of exact digital execution or commitment.

**Trace three separate cases.** Teach them separately, then compare.

```text
A. Crash before work:       Caller ---> Service X     (not executed in this case)
B. Reply lost:              Caller ---> Service [work done] --X--> Caller
C. Reply late:              Caller ---> Service [slow work] -----> Caller (too late)
```

1. In case A, **given the stated trace**, the service stopped before the work started. The work did not run.
2. In case B, the work occurred, but the network hid the success reply.
3. In case C, the server eventually answered, but the caller may have given up waiting.
4. Without a trustworthy trace or durable evidence, the caller may not know which case happened.

**Immediate check.** In case B, did the action fail just because the reply was lost?

**Speak.** “The caller observed ___, but the actual work may have ___.”

**Small change, later.** The server crashed *after* writing to its database but before sending the reply. Which part of
the work can survive the crash?

**Later interview form.** “I separate execution failure from communication failure. If a caller receives no answer, I do
not infer that the server did no work. I inspect durable state and trace evidence before choosing a recovery action.”

**Review cue.** Re-create A, B, and C without looking.

## L33 — A timeout is not proof of failure

**Purpose.** A **timeout** means the caller stopped waiting after a configured limit. It does **not** by itself prove
whether the remote action happened.

**Tiny example.** A restaurant does not answer your call within 30 seconds. That does not tell you whether it already
received the order you placed earlier. **Limit:** A phone-call analogy cannot establish the provider’s guarantees.

**Trace the unknown state.**

1. Purchase service sends instruction `R-17` at `t=0`.
2. Provider executes the action at `t=200 ms` in this scenario.
3. The provider’s response never reaches the purchase service.
4. The purchase service’s **500 ms deadline** expires.
5. The purchase service knows **“no timely reply”**, not **“provider did nothing.”**

```text
Caller                 Provider
  |---- R-17 ----------->|
  |                      | action completed
  |<----X reply lost ----|
  |
  +-- timeout (knowledge = UNKNOWN)
```

**Immediate check.** After the timeout, what fact can the caller state with confidence?

**Speak.** “A timeout tells us ___; it does not tell us ___.”

**Small change, later.** A status-query API exists. What question can the caller ask without initiating another action?

**Later interview form.** “A timeout only tells me that the deadline passed without a usable response. The remote side
may have committed the action. For a side-effecting operation I preserve an unknown state, inspect durable evidence, and
avoid blindly resubmitting it.”

**Review cue.** Say the M03 pass phrase using different words: **No reply is not proof of no action.**

## L34 — Safe and unsafe retries; stable request identity

**Purpose.** A **retry** is another attempt after a first attempt has not yielded a usable result. A **stable request
identity** lets the system recognize that the second attempt refers to the same logical operation. Retries are only safe
when the operation and the receiver’s contract make them safe.

**Tiny example.** Refreshing a read-only page is different from pressing “pay” twice. **Limit:** Some “read” operations
can have side effects and some writes offer explicit retry-safe contracts; check the actual contract rather than relying
on labels.

**Trace.**

1. Client sends `request_id=R-17` and amount `900` minor units.
2. Reply is lost. Client retries **the same** `R-17`.
3. The receiving system checks a **durable**, atomically created identity record for this scope and the original input.
4. It returns the known result or a truthful pending state rather than starting a second independent operation.
5. If the same identity arrives with different parameters, the system rejects the mismatch.

```text
First attempt:  R-17 / 900 --> [durable operation R-17] --> external effect?
Retry:          R-17 / 900 --> [look up R-17] ---------> same operation
Different:      R-17 / 950 --> [reject mismatch]
```

A unique ID **by itself** does not guarantee one external effect. It needs atomic deduplication, a defined scope and
retention window, and the downstream provider’s actual guarantees. If the provider has neither reliable idempotency nor
status queries, hold uncertain financial outcomes for reconciliation rather than blindly retrying. M05 develops this
carefully.

**Immediate check.** On retry, should the client generate a new logical request ID for the same intended action?

**Speak.** “I reuse the same request identity because ___.”

**Small change, later.** Two identical requests reach two different application instances at once. Why does checking an
in-memory list on each instance fail?

**Later interview form.** “I classify the operation before retrying it. For mutations, a stable business request ID must
be backed by atomic durable deduplication and compatible provider semantics. On an uncertain financial outcome, I query
or reconcile before sending another independent instruction.”

**Review cue.** Distinguish **a logical operation** from **one network attempt**.

## L35 — Two requests at the same time: lost update

**Purpose.** **Concurrency** means multiple pieces of work overlap in time. A **lost update** happens when one writer
saves an old calculation and overwrites another writer’s change.

**Tiny example.** Two people both read the same notebook balance, calculate separately, and each write a new balance.
**Limit:** A real database has concurrency controls and exact behavior depends on its isolation and query form.

**Trace.** The training balance starts at **100**.

1. Worker A reads `balance=100` and plans to subtract 10.
2. Worker B also reads `balance=100` and plans to subtract 20.
3. Worker A writes `90`.
4. Worker B writes `80` from its stale read, hiding A’s subtraction.
5. Expected total after both valid subtractions is **70**. Actual stored value is **80**.

```text
Time   Worker A                  Stored balance            Worker B
 t0                              100
 t1    read 100
 t2                                                        read 100
 t3    write 90  -------------> 90
 t4                              80 <------------------ write 80
 Final = 80; one update has been lost.
```

One fix is **optimistic concurrency control**: every record has a `version`. A writer updates only if the version is
still the one it read.

```sql
UPDATE balances
SET amount_minor = amount_minor - 10,
    version      = version + 1
WHERE account_id = 'A'
  AND version = 4
  AND amount_minor >= 10;
```

The caller must check the number of affected rows. **One** means this guarded write succeeded; **zero** means a
conflict, missing row, or rejected condition. It must decide whether to reread, report conflict, or safely retry the
full business decision. This example assumes the database executes the statement atomically. A pessimistic alternative
is a transaction with an appropriate row lock and carefully defined scope; locking is not universally better.

**Immediate check.** What number is left in the flawed trace, and what number should be left?

**Speak.** “A lost update occurs when ___.”

**Small change, later.** Worker B uses a version check after worker A succeeds. Does B overwrite A’s value, or does it
detect a conflict?

**Later interview form.** “Concurrent read–modify–write operations can lose changes. I would choose an atomic database
update or version guard, test a conflict under overlapping requests, and define what the caller sees when one update
cannot proceed. I would not assume that a transaction label alone removes every race.”

**Review cue.** Try the included Python interleaving lab **after** you can explain this paper trace.

## L36 — One-database transactions versus actions across systems

**Purpose.** A **transaction** commits a supported set of changes as one unit **inside its transactional boundary**. A
local database commit does not automatically commit or roll back a separate provider’s action.

**Tiny example.** Updating two fields in one ledger can be one local step; sending a separate package needs another
confirmation. **Limit:** Some specialized distributed transaction protocols exist, but they need explicit coordination
and guarantees and are not assumed in this case.

**Trace.**

1. The application inserts `PurchaseRequest(R-17, 'PENDING')` into its database.
2. The database commits that record.
3. The application sends a financial instruction to a separate provider.
4. The provider acts, but the reply is lost. The local database still records the request; external outcome is unknown
   until evidence resolves it.

```text
LOCAL DATABASE TRANSACTION                 REMOTE PROVIDER
BEGIN -> insert R-17 -> COMMIT             <--- send after commit
    |                                          action may happen
Local change is durable (assumed)          local COMMIT cannot undo it
```

A **transactional outbox** later helps atomically save a local change and the *intent to publish a message* in the
**same database**. It does not magically give atomic execution with the provider, and consumers still need duplicate
handling. **Saga** and compensation appear later in M05. A compensation is a new fallible business action, not a
guaranteed database rollback.

**Immediate check.** If the local database commits, does that prove the external provider completed its action?

**Speak.** “A database transaction protects ___, but it does not automatically protect ___.”

**Small change, later.** The process crashes after the database commit but before the remote send. What local evidence
might help a recovery worker know what is still pending?

**Later interview form.** “I mark the transactional boundary explicitly. Local commits do not make a remote payment or
message send atomic. I persist intent durably, model pending/unknown states, and design recovery and reconciliation
around the actual external contract.”

**Review cue.** On a diagram, circle only the steps inside one transaction.

## L37 — Synchronous versus asynchronous communication

**Purpose.** In **synchronous request–reply**, the caller waits for a result before it can finish the dependent step. In
**asynchronous work**, a caller can accept a request and let other work continue later. Neither model automatically
guarantees reliability.

**Tiny example.** Waiting on the phone for an answer is synchronous; leaving a written request with a tracking number is
asynchronous. **Limit:** A queue is not necessarily durable, and “accepted” need not mean “completed.”

**Trace the same user journey two ways.**

```text
SYNCHRONOUS                      ASYNCHRONOUS
Client -> API -> Risk            Client -> API -> store durable intent
Client <- API <- Risk            Client <- API : ACCEPTED / R-17
                                 Worker -> Risk (later)
                                 Client -> status lookup -> pending/done
```

1. Sync: request arrives; API waits on a risk response; it then replies.
2. Async: API validates the input and durably records an accepted work item.
3. API returns a request ID with **pending/accepted** status, not a false final success.
4. Worker performs the task later; the caller checks status or receives a documented notification.
5. If the work queue or worker fails, the design must define retention, retry/replay safety, and monitoring.

**Immediate check.** In the asynchronous example, does the immediate “accepted” response mean risk checking is complete?

**Speak.** “I prefer asynchronous processing when ___, but I must still ___.”

**Small change, later.** The employee must receive a binding risk decision before buying. Can the system simply report
“approved” immediately after queueing?

**Later interview form.** “I use synchronous work for decisions required before responding. Asynchronous processing can
remove long work from the immediate request path, but I still need durable acceptance, observable pending states, replay
behavior, and clear completion semantics.”

**Review cue.** Define **accepted**, **in progress**, and **completed** without making them synonyms.

## L38 — Clock uncertainty: timestamps do not always prove order

**Purpose.** Different computers have **clocks** that can disagree. A timestamp from machine A is not always sufficient
to prove that its event occurred before a timestamp on machine B.

**Tiny example.** Two wall clocks show different minutes even when people act in a clear order. **Limit:**
Well-engineered systems may use clock synchronization and special protocols; this lesson does not deny those specific
guarantees.

**Trace.**

1. Service A completes event `E1` at real elapsed moment `t=10`, but its clock reads `10:00:05`.
2. Service A sends a message to service B. B receives it afterward.
3. Service B records event `E2` at real moment `t=11`, but its clock reads `10:00:03`.
4. Looking only at timestamps falsely suggests `E2` came first.

```text
Real order:      A:E1 --------message--------> B:E2
Recorded time:   10:00:05                     10:00:03
                 (larger)                     (smaller)
```

The known **causal order** is `E1 -> message sent -> message received -> E2`. **Causality** here means one event could
influence a later event. Within one ordered record stream, a **sequence number** or database-generated version can often
express local order more reliably than wall-clock comparison. A global order across unrelated streams needs an explicit
protocol and scope.

**Immediate check.** Which occurred first in this trace: `E1` or `E2`?

**Speak.** “Timestamps on different machines may mislead us because ___.”

**Small change, later.** Both services append to a single authoritative sequence. What additional ordering evidence
would that provide?

**Later interview form.** “I avoid deriving global order from independent wall clocks alone. For correctness, I prefer
causal relationships and a documented version or sequence order within the business entity. Any stronger cross-system
ordering promise must be backed by the actual protocol.”

**Review cue.** Explain why `10:00:03` does not necessarily precede `10:00:05` across computers.

## L39 — Network partition: decide which operation may pause

**Purpose.** A **network partition** occurs when parts of a distributed system cannot reliably communicate. If two sides
cannot coordinate, some operations may need to pause to preserve a hard business rule.

**Tiny example.** Two store branches lose contact with the shared inventory office. Both can continue showing a cached
catalog, but both independently selling the last unique item could cause an oversell. **Limit:** Software can use
authority and reconciliation mechanisms; the analogy does not dictate a universal answer.

**Trace a concrete purchase policy operation.** Assume: one authoritative policy record, a hard organization spending
cap, and two application locations that can no longer reach the authoritative record.

1. Before partition, one designated writer checks and updates the authoritative remaining limit.
2. The network link to that writer fails for the second location.
3. Both locations might have old policy copies. An old copy is not proof of current capacity.
4. **Policy choice in this hypothetical case:** pause **new cap-consuming approvals** at the disconnected location;
   continue read-only history with a clear **possibly stale** label.
5. Resume approvals only after authority and any in-flight requests are resolved. Someone must own this operational
   policy.

```text
Location A ------X------ Location B
  |                            |
  | authorized cap writer      | cached cap (may be old)
  | new approvals possible     | PAUSE cap-consuming approvals
  | read history possible      | read history with freshness label
```

This is a **per-operation** choice. A report read and a cap-consuming approval need not make the same
availability–consistency trade-off. Do **not** describe an entire product as simply “AP” or “CP” without defining
guarantees and failure assumptions.

**Immediate check.** Under the stated hard-cap policy, which operation pauses at location B?

**Speak.** “During a partition, I would allow ___ but pause ___ because ___.”

**Small change, later.** The business explicitly accepts a bounded overspend risk and sets a small offline allowance.
What must be defined before that controlled degradation is safe?

**Later interview form.** “I first identify the invariant for a specific operation. During a partition, I would preserve
authoritative writes for cap-consuming approvals even if some requests become unavailable. Less sensitive reads can
continue with labeled stale data, provided product owners approve the behavior and reconciliation is defined.”

**Review cue.** Explain the partition decision for **one action**, not the entire system.

## L40 — Put it together: one failure timeline and one decision

**Purpose.** A **failure timeline** records the order of requests, durable writes, observations, and unknowns. A
**decision record** compares two credible choices using business requirements, failure behavior, and ownership.

**Tiny example.** A team reviews a lost parcel: when it was sent, whether delivery was confirmed, and which follow-up
would create risk. **Limit:** For software, exact durable records and provider contracts matter more than anecdotes.

**Trace the integrated training case.**

1. Employee submits `R-17`. Purchase service records its validated intent.
2. Purchase service calls a risk service, which evaluates the request.
3. The risk reply is lost. The purchase service times out.
4. The system keeps risk decision **unknown**, not “risk passed”. It does not issue a payment instruction whose policy
   requires prior risk approval.
5. It uses an authorized status query or controlled reconciliation. A responsible owner reviews any unresolved case.

```text
Time    Employee       Purchase service          Risk provider
 t0     R-17 ---------> intent recorded
 t1                     risk R-17 ---------------> receives
 t2                                                evaluates
 t3                     <---------X--------------- reply lost
 t4     pending <------- timeout / UNKNOWN
 t5                     status query ------------> evidence?
 t6     updated <------- confirmed or still pending
```

**Immediate check.** At `t4`, is the risk result *rejected*, *approved*, or *unknown* from the caller’s available
evidence?

**Speak.** “First ___; then the response ___; so we know ___ but still need ___.”

**Small change, later.** The risk provider has **no** status-query API. Who must decide whether requests wait, decline,
or use a narrowly defined alternate process? What evidence is required?

**Later interview form.** “I would first draw the normal request path and ownership of each step. Then I would trace
failure timing, separate local observations from external outcomes, and show which invariants prevent unsafe
continuation. My boundary and recovery choice would be documented with a measurable latency goal, an operating owner,
and a reversal condition.”

**Review cue.** Narrate L40 for 30–60 seconds without reading the professional answer.

---

## M03 capstone workbook — do only after L29–L40

**This workbook is not Day 1 homework.** It matches all five M03 “Do” tasks plus the dependency-failure exercise. Keep
notes open for a first attempt. Work independently only after guided practice. All figures below are **hypothetical**;
verify real requirements with their owners.

### Capstone A — Mark the purchase → policy → payment call chain

Make a diagram including **nodes**, **network hops**, **owner**, **timeout/deadline**, and **possibly unknown result**.
Fill this worksheet:

| Boundary                                      | Owner (role, not assumed team name) | Caller knows | What may still be unknown | Recovery path |
|-----------------------------------------------|-------------------------------------|--------------|---------------------------|---------------|
| Employee → Purchase                           |                                     |              |                           |               |
| Purchase → Policy store/owner                 |                                     |              |                           |               |
| Purchase → External risk, if required         |                                     |              |                           |               |
| Purchase → Provider, only after authorization |                                     |              |                           |               |

**Acceptance check:** Each arrow has a named timeout **and** a statement about what the timeout does *not* prove. Name
the actual business owner who must approve the failure policy in a real system; do not invent one.

### Capstone B — Produce three failure timelines

Draw each trace with columns
`time | caller | receiver | durable fact | what caller observed | unknown | safe next step`.

**B1. Crash before execution.** The remote worker receives the request but crashes before it performs or durably records
the action. In this **known trace**, no action happened. Explain what evidence would be needed before the caller could
rely on that statement.

**B2. Commit then reply lost.** The provider commits the action. The reply is dropped. The caller times out. Explain why
a blind second instruction is unsafe.

**B3. Retry while first call still running.** A second attempt of the same `request_id` arrives while the first attempt
is in progress. Show how **atomic** record creation stops two distinct logical operations. Decide whether the caller
sees pending or a known result.

**For every trace, say aloud:** “I observed ___; the actual state is ___ or unknown; my next safe action is ___.”

### Capstone C — Allocate a hypothetical latency budget

Assume the business proposes a **1,000 ms** end-to-end deadline. This is an exercise, **not** an external service-level
promise. One initial serial budget:

| Step                                                    | Allocated elapsed time |
|---------------------------------------------------------|-----------------------:|
| Ingress/validation                                      |                  60 ms |
| Policy lookup                                           |                 100 ms |
| Remote risk check                                       |                 200 ms |
| Remote provider step (only if in this synchronous path) |                 450 ms |
| Response and network overhead                           |                  90 ms |
| Safety reserve                                          |                 100 ms |
| **Total**                                               |           **1,000 ms** |

Draw a serial chain and mark which steps must finish before later ones. Then answer: if the provider uses **650 ms**,
which budget is exceeded, and what should the caller truthfully return? What could change if the provider is moved out
of the synchronous path? Explain why a budget is **not proof** of actual percentile latency. Do not claim 1,000 ms is an
achievable target without measurements and business approval.

### Capstone D — Reproduce and prevent a lost update

First predict the trace: balance 100, worker A subtracts 10, worker B subtracts 20, both read before either writes. Then
run the optional companion `M03_lost_update_lab.py`. It is a **deterministic teaching simulation** using a local SQLite
database, not a load test or real simultaneous production workload.

Success evidence: the flawed trace ends at **80**, whereas the guarded version preserves **70** after detecting one
version conflict and recomputing safely. Explain why comparing a version and updating it must be **one atomic database
action**. Show a test where the stale write changes **zero rows**. Also describe an alternative transaction/lock-based
design and the cost of holding locks.

### Capstone E — Network partition: choose by operation

Assume a single authoritative organization-spend limit and temporary loss of connectivity at one site. Create a decision
table:

| Operation                          | During partition | Safety / truth condition | Decision owner |
|------------------------------------|------------------|--------------------------|----------------|
| Show purchase history              |                  |                          |                |
| Approve new cap-consuming purchase |                  |                          |                |
| Record a new request as pending    |                  |                          |                |
| Show finalized provider result     |                  |                          |                |

Then change **one** assumption: the business authorizes a bounded offline limit. State the bound, how to prevent two
sites spending the **same** allowance, how to audit it, and who can approve the risk. Do not assume a magic global
partition mode.

### Capstone F — Risk provider unavailable during approval

Compare only these business-policy choices:

| Choice                       | Observable user result                        | Main risk                                 | Required authorization                                 |
|------------------------------|-----------------------------------------------|-------------------------------------------|--------------------------------------------------------|
| **Stop / decline**           | No approval; state accurately why             | Legitimate purchases blocked              | Business risk and user-experience owner                |
| **Wait / pending**           | Decision deferred; status query or follow-up  | Delay, backlog and abandoned cases        | Owners of deadline, queue and customer communication   |
| **Narrowly defined degrade** | Only an explicitly permitted subset continues | Unauthorized acceptance if policy is weak | Risk/control owner, with documented scope and evidence |

**Prompt:** For a purchase requiring risk approval, can the system silently treat the service timeout as “approved”?
Explain using the invariant and authorized business policy. Treat “declined” vs “could not decide” as distinct statuses
unless policy explicitly says otherwise.

### Final artifact — service boundary ADR

**Architecture Decision Record (ADR)** — brief note explaining an architecture choice. Create one page:

- **Decision:** Keep policy logic inside a modular application **or** deploy it as a separate policy service.
- **Context/known facts:** Who changes policy, deployment needs, traffic, ownership, latency and failure tolerance. Mark
  missing items **open**, not facts.
- **Option A and B:** At least one real benefit and cost for each.
- **Normal path:** Show where the policy result comes from.
- **Failure path:** What happens when policy/risk connectivity breaks? Which operation pauses?
- **Data authority:** Who owns the policy record and version?
- **Recommendation:** Conditional on stated assumptions. No default “microservices win.”
- **Validation:** Concurrency/conflict test, timeout test, duplicate request test, observed latency, and an owner for
  repair.
- **Reversal signal:** The measured condition that would justify changing the decision.

**Complete M03 evidence set:** Three failure timelines; concurrency reproduction and fix; estimated or measured latency
diagram; one justified service-boundary ADR. Syllabus coverage tags are **C036–C045 and C118–C123**. The source syllabus
supplies these as coverage IDs, not a separate item-by-item definition in this file; do not invent their wording.

---

## Coach's answer key — reveal only after making an attempt

These are teaching answers to the *immediate checks*. They are not scripts to memorize. A learner can use different
words if the technical meaning is correct.

| Lesson | Short model answer                                                              | Most important correction if missed                                     |
|--------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| L29    | The network carries the request between separate programs.                      | A normal function call inside one process is not a remote network call. |
| L30    | Yes. A modular monolith can depend on remote systems.                           | “Monolith” does not mean “nothing is distributed.”                      |
| L31    | 40 ms was server processing.                                                    | Do not confuse processing time with round-trip latency.                 |
| L32    | No. The reply was lost after the work completed.                                | Missing response does not prove missing execution.                      |
| L33    | The caller knows it did not get a timely usable answer.                         | Timeout does not prove the action failed.                               |
| L34    | No. Reuse the same logical ID for the same intended action.                     | A fresh ID can make a repeated request appear new.                      |
| L35    | Flawed: 80. Correct combined subtraction: 70.                                   | Two workers used stale snapshots of the same original value.            |
| L36    | No. Local commit does not establish remote provider execution.                  | Local atomicity stops at its stated boundary.                           |
| L37    | No. It means work was accepted, if durable acceptance was actually established. | Accepted/pending is not completed/approved.                             |
| L38    | `E1` occurred before `E2`; the message establishes causal order.                | Independent clock values may not be comparable.                         |
| L39    | New cap-consuming approvals pause at disconnected B.                            | Use a concrete operation and invariant, not a product-wide label.       |
| L40    | Unknown, until reliable evidence confirms a result.                             | Do not infer approval or rejection from a missing reply.                |

### Model capstone thinking — compare only after an attempt

**B1 — known crash-before-work:** `receive → crash before execution/durable effect`. The outside caller cannot infer
this from timeout alone; it needs trusted status, logs plus correct durability semantics, or equivalent evidence. A
retry may be safe only under the receiver’s defined retry contract.

**B2 — reply lost:** `receive → commit → reply lost → caller timeout`. The provider action happened, while the caller
still sees unknown. Reconcile/query or use a documented provider idempotency guarantee; do not blindly create another
financial action.

**B3 — concurrent retry:**
`same R-17 → two instances → shared database atomic unique identity claim → exactly one logical operation row; other request sees the same operation and its pending/result state`.
This does **not** alone guarantee one effect at an external provider.

**C — latency:** The planned provider budget is 450 ms. If that step takes 650 ms and other steps consume their full
budgets, total would be 1,200 ms, exceeding 1,000 ms by 200 ms. A configured deadline may fire sooner, so that exact
total is not necessarily observed. The safe user result is a documented timeout/pending/unknown status that reflects
evidence. Async processing changes what the immediate response means; it does not remove eventual work latency.

**D — concurrency:** Both read 100. A writes 90; B writes 80. A guarded `UPDATE ... WHERE version=original` rejects the
stale second write with `rowcount == 0`. B must fetch the new 90, re-check the business condition, and apply its 20
deduction to reach 70. In a real spending system this must be coupled with the actual authorization and transactional
invariants; this lab alone is not a financial safety design.

**E — example per-operation decision:** History can be read with a stale-data label; new cap-consuming approval pauses
at B; a new request may be **durably accepted as pending** only if storage, status, and replay semantics permit it; a
final provider result is shown only with trustworthy evidence. Any offline allowance requires disjoint authority and
explicit reconciliation. The exact policy belongs to the business/control owner.

**F — risk outage:** If risk approval is mandatory, silently treating an unavailable risk service as “approved” violates
the stated requirement. Stop/decline versus pending versus controlled degradation is an authorized business decision.
Never mix a timeout with a genuine negative risk decision without documented policy.

**ADR — credible recommendation under limited facts:** Begin with a modular application containing a clean policy module
if independent release/scale is not yet required. This is a **conditional training choice**, not a universal rule.
Reconsider separate deployment if evidence shows a persistent ownership, release, isolation, or scaling need that
outweighs network failure and transaction costs.

---

## Speaking laboratory — understanding first, polish second

Practice each stage **in order** and only after tracing the example.

| Stage            | Goal                      | M03 example                                                                                                                                            |
|------------------|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Point         | Identify what happened    | “The service sent a request and got no reply.”                                                                                                         |
| 2. One sentence  | Define meaning            | “A timeout means the caller stopped waiting.”                                                                                                          |
| 3. Two sentences | Add the risk              | “The provider might still have acted. So no reply is not proof of failure.”                                                                            |
| 4. Walkthrough   | Narrate order             | “First we sent the instruction. Then the provider may have processed it. We lost the response, so we must check.”                                      |
| 5. Professional  | Answer concisely          | “I treat remote timeouts as uncertain outcomes. I preserve operation identity and use documented status/idempotency guarantees to resolve the result.” |
| 6. Judgment      | Apply business constraint | “For financial effects I do not blindly retry; I keep it pending and reconcile if no reliable answer is available.”                                    |

**If words are hard:** Start with “A ___ is ___,” “This matters because ___,” and “One thing that can go wrong is ___.”
When you struggle, select one: “A timeout means the action failed” **or** “A timeout means there was no answer in time.”
Explain your choice after reviewing L33. The second sentence is technically correct.

### Two guided 30–60-second practice prompts

**Prompt 1 (after L33–L34):** “An external call timed out. How do you interpret that, and what is your next safe step?”
Build the answer from: observation → uncertainty → stable identity → evidence-based recovery.

**Prompt 2 (after L39–L40):** “Your policy service becomes unreachable. Would you allow purchases?” Build from: business
invariant → which operation → two policy choices → owner and trade-off. There is no safe one-word answer without a
defined policy.

### One-minute misconception repair

| Tempting sentence                                             | Better sentence                                                                         |
|---------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| “The request timed out, so the provider rejected it.”         | “The request timed out, so the caller does not have a timely result.”                   |
| “A second request with a unique ID is safe.”                  | “Safe retry needs stable identity **and** atomic deduplication and provider semantics.” |
| “Microservices are always better.”                            | “I compare them with a modular monolith against real requirements.”                     |
| “Database COMMIT covers every system.”                        | “A commit covers the participating transaction boundary.”                               |
| “The earlier timestamp happened first.”                       | “Independent clocks do not prove cross-machine order without guarantees.”               |
| “During partition, the whole system must be either AP or CP.” | “I state availability and consistency needs for a **specific operation**.”              |

---

## Glossary — plain language, in lesson order

| Term                      | Meaning in this guide                                                                                                |
|---------------------------|----------------------------------------------------------------------------------------------------------------------|
| Program / process         | Saved instructions / a running program.                                                                              |
| Module                    | A logical part of an application with one responsibility.                                                            |
| Modular monolith          | One deployable program with clear internal modules.                                                                  |
| Service                   | Software providing a defined capability through an interface; in M03, usually a separately running process.          |
| Remote call / network hop | A request that crosses a communication link to another process or system.                                            |
| Latency                   | Elapsed time for the measured operation.                                                                             |
| Deadline / timeout        | End of an allowed waiting period / the waiting limit being reached.                                                  |
| Partial failure           | One part or request fails while others can still work.                                                               |
| Retry / attempt           | Another try / one execution or network transmission effort.                                                          |
| Logical request identity  | Stable name for the business action, reused across its attempts.                                                     |
| Idempotency               | Contract/behavior that makes repeated equivalent requests safe from duplicate intended effects within defined scope. |
| Atomic                    | A change is treated as one indivisible operation within its guarantee.                                               |
| Concurrency               | Operations overlap in time.                                                                                          |
| Lost update               | One writer overwrites another writer’s change based on an old read.                                                  |
| Version check             | Comparing stored version with the version read before allowing a write.                                              |
| Transaction               | Group of database changes committed or rolled back under stated database guarantees.                                 |
| Synchronous               | Caller waits for the needed result in the current flow.                                                              |
| Asynchronous              | Work continues separately; caller can receive an accepted/pending status first.                                      |
| Causal order              | A documented chain showing one event could influence another.                                                        |
| Network partition         | Network communication between some parts is disrupted.                                                               |
| Invariant                 | A business or data rule that must remain true.                                                                       |
| Authority                 | System or actor permitted to make the decisive change for a fact.                                                    |
| Reconciliation            | Comparing independent records/evidence and safely resolving differences.                                             |
| ADR                       | Architecture Decision Record: choice, context, alternatives, trade-offs, proof, and revisit condition.               |

---

## Progress notebook and completion checklist

Use the following compact record after each session. The guide does not automatically assess technical mastery;
completing a checkbox means **you** confirmed the evidence.

```text
Current lesson (L29–L40):
Normal example I can trace:
My own one-sentence explanation:
Technical idea I understood:
One technical gap:
Speaking stage (point / one sentence / two sentences / walkthrough / professional / judgment):
One corrected sentence I can say aloud:
Next lesson or review date:
```

**M03 completion checklist (not an entry test):**

- [ ] I traced the normal purchase → policy → risk/provider flow and marked communication boundaries.
- [ ] I distinguished a crash, a lost reply, a slow reply, and the caller’s actual knowledge.
- [ ] I explained a timeout without assuming remote failure.
- [ ] I explained stable identity and why retries require an actual contract.
- [ ] I reproduced a lost update and showed a conflict-safe write.
- [ ] I marked a local transaction’s boundary versus a remote effect.
- [ ] I compared synchronous and asynchronous paths truthfully.
- [ ] I explained one misleading cross-machine timestamp trace.
- [ ] I made one per-operation partition decision with an invariant and owner.
- [ ] I produced the **three failure timelines**, **latency diagram**, **concurrency test**, and **boundary ADR**.
- [ ] I can explain one normal path, one failure, and one changed case in **30–60 seconds**.

**What comes next:** M04 covers source of truth, replication, stale reads, and sharding. M05 deepens operation IDs,
durable idempotency, unknown financial outcomes, compensation, and reconciliation. M06 treats API contracts, events,
duplicate delivery, and outbox processing in detail. Do not treat this M03 guide as a replacement for those missions.

---

## Verified primary sources and scope notes

The **lesson order, exit criteria, case framing, and capstone requirements** come from the uploaded syllabus. The
following are **independent official sources** for mechanisms explained here. They do **not** establish employer
internals, actual performance targets, or a provider's payment guarantees.

1. **Microsoft Learn, Microservices architecture style** — benefits and costs of separate services, extra communication,
   and distributed
   consistency: https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices (L29–L30,
   L31).
2. **AWS Builder's Library, Timeouts, retries, and backoff with jitter** — what timeouts do, why retrying mutations can
   be unsafe, and load amplification: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
   (L31–L34).
3. **AWS Builder's Library, Making retries safe with idempotent APIs** — client request IDs, atomic identity handling,
   changed input, and retention: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
   (L34).
4. **PostgreSQL documentation, Transaction isolation** — isolation guarantees and concurrent transaction
   anomalies: https://www.postgresql.org/docs/current/transaction-iso.html (L35). **PostgreSQL documentation, Explicit
   locking:** https://www.postgresql.org/docs/current/explicit-locking.html (L35).
5. **SQLite documentation, Transactions** — `BEGIN`, `COMMIT`, `ROLLBACK` and its specific database
   behavior: https://www.sqlite.org/lang_transaction.html (L35–L36 and the lab). Database guarantees are
   product-specific.
6. **AWS Prescriptive Guidance, Transactional outbox pattern** — dual-write risks and duplicate
   events: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html (L36
   preview, later M06).
7. **Microsoft Learn, Asynchronous request-reply pattern** — accepted/pending semantics, polling, and asynchronous
   costs: https://learn.microsoft.com/en-us/azure/architecture/patterns/asynchronous-request-reply (L37).
8. **Google Cloud Spanner, TrueTime and external consistency** — example of why cross-machine clocks need explicit
   ordering guarantees: https://docs.cloud.google.com/spanner/docs/true-time-external-consistency (L38). This is a
   documented **Spanner-specific** mechanism, not a claim about all databases.
9. **AWS, CAP theorem** — trade-offs under network
   partitions: https://docs.aws.amazon.com/whitepapers/latest/availability-and-beyond-improving-resilience/cap-theorem.html
   (L39). The guide applies the choice to a stated business operation.

**Evidence discipline:** All latency values and failure traces are illustrative. SQL/Python examples are educational and
are **not** sufficient to operate a real payment system. Provider status query, idempotency semantics, retention, risk
fallback, deadline, and business approval requirements remain **open** until verified in the actual project.
