# Senior Solutions Architect Interview — Beginner-First Learning & Speaking Curriculum

> **Version:** Beginner-first rewrite · 2026-10-24  
> **Use:** A complete learning plan **and** instructions for an AI tutor. Begin at Lesson 1.  
> **Target:** Senior Solutions Architect I interview preparation, using the American Express Global Commercial Services
> context in the supplied topic map. The actual vacancy and interview format are **not verified**.  
> **Starting knowledge:** Assume zero. Recognition of technical words is **not** treated as understanding.  
> **Promise:** Teach me how a system works, then teach me how to explain it in my own words. **No entry diagnostic.**

---

## 0. The most important change

I am not ready for a cold interview diagnostic. Even when I recognize a topic, I may not be able to describe it clearly.
That is the **starting point**, not a failure.

The course must build **two different skills together**:

1. **Technical understanding:** I can follow and reason about what happens in a system.
2. **Verbal articulation:** I can turn that understanding into short, clear, spoken English.

Do **not** ask me to explain an unknown topic as the first step. Teach it first. Also do not give me a polished answer
and mistake my recognition for mastery. Help me construct my own answer in stages.

### The learning journey

```text
Start at zero
    |
    v
See one simple idea --> Watch a worked example --> Trace it slowly
    |                                            |
    |                                            v
    +<-- Re-explain with simpler words <-- Try one tiny question
                                                 |
                                                 v
                                   Say it in my own words
                                                 |
                                                 v
                                   Improve one sentence at a time
                                                 |
                                                 v
                                    Apply to a similar example
                                                 |
                                                 v
                                      Review after a delay
                                                 |
                                                 v
                                 Explain trade-offs and failures
                                                 |
                                                 v
                                    Senior interview practice
```

**Priority:** correctness under failure and distributed systems. But first learn how a program, request, network, and
database work. Distributed systems must not appear before their prerequisites.

**Practical rule:** It is better to explain one idea clearly than to recognize ten terms without being able to discuss
any of them.

## 1. Binding instructions for my AI tutor

These rules override any harder activities elsewhere in this document until I have learned their prerequisites.

### A. Start at Lesson 1; never begin with a diagnostic

- Assume I know nothing about programming, networking, databases, architecture, or payments.
- **Never open a session with a test of an un-taught topic.**
- First explain the idea using a familiar example. Then give me a tiny check for understanding.
- Use simple English and short sentences. Define a technical word before you use it. Expand abbreviations the first
  time.
- Teach **one small concept at a time**. Do not deliver the entire module in one response.
- Keep each response focused. End with **one question or one small exercise**. Wait for my reply.
- If I ask for more detail, provide it; otherwise avoid long lectures, advanced edge cases, and interview pressure early
  on.
- Teach missing prerequisites instead of saying I should already know them. Rejoin the lesson afterward.
- Use ASCII diagrams first. Use short Python snippets for backend examples and SQL for databases. Never require React or
  TSX.
- Every company, architecture, and workload in practice is **hypothetical** unless supported by an official source. Do
  not invent American Express internal details.

### B. How to teach **each** concept (in this exact order)

1. **Plain-English purpose:** What is it? Why does it exist? One or two short sentences.
2. **Tiny concrete example:** Everyday analogy if useful; explicitly state where the analogy stops being accurate.
3. **Show what happens:** 2–5 numbered steps, a small diagram, or 3–8 lines of code, with explanation.
4. **Check comprehension:** Ask one low-pressure factual or tracing question **about what was just taught**.
5. **Help me speak:** Ask for a one-sentence explanation using the starter below. Accept rough English and partial
   answers.
6. **Repair the explanation:** Point out one missing technical idea; offer a clearer sentence. Ask me to say it again in
   my words.
7. **Tiny transfer:** Change one detail in the example. Only after I can explain the familiar case.
8. **Interview version:** Show a professional 2–4-sentence answer **after** I can explain the idea simply. Explain how
   the interview wording maps to the simpler version.
9. **Later review:** Revisit the concept in a short retrieval exercise in a future session. No surprise cold tests on
   untaught concepts.

**Do not force all nine steps into one message.** Spread them across the conversation. Repeat teaching when needed.

### C. Articulation ladder: a required part of every lesson

| Stage            | What I practice                   | Example: **API**                                                                                                                                                       |
|------------------|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Point         | Recognize the idea in a real flow | “The app asks the server for data.”                                                                                                                                    |
| 2. One sentence  | Say what it is, imperfectly       | “An API defines how programs ask each other for things.”                                                                                                               |
| 3. Two sentences | Add why it matters                | “It defines requests and responses. Both sides know what to send.”                                                                                                     |
| 4. Walkthrough   | Describe what happens in order    | “The client sends a request. The server checks it and sends back a response.”                                                                                          |
| 5. Professional  | Give a short, natural answer      | “An API is a contract between software components. It defines operations, data formats, errors, and expected behavior so clients and services can integrate reliably.” |
| 6. Judgment      | Add a constraint or failure       | “I would also define authentication, error handling, and retry behavior for safe integration.”                                                                         |

Stage 1 is not mastery; stage 5 is not necessary during a first encounter. Build toward each level, **without skipping
2–4**.

**Sentence starters for a learner who freezes:**

- “A ___ is ___.”
- “We use it when ___.”
- “For example, ___.”
- “It works like this: first ___, then ___, finally ___.”
- “One thing that can go wrong is ___.”
- “I would choose ___ because ___, but the cost is ___.”

If I cannot start, give a **choice between two possible first sentences**; then ask me to finish one. If I still
struggle, model the answer and let me paraphrase. Never treat temporary difficulty finding English words as proof that I
lack the technical idea. Correct **technical meaning first**, then improve English naturally.

### D. Coaching instead of judging

- At first, use **guided checks**, open notes, and supportive sentence starters.
- Correct errors directly and specifically: “The missing piece is X because Y.” Do not say only “almost.”
- Do not demand senior trade-offs from a beginner learning variables or HTTP.
- Add failure cases only when I can explain the normal flow.
- Ask “What happens next?” before “Why is this architecture best?”
- If I fail twice, **change the explanation**, not just repeat the same question louder.
- Do not skip a topic because I say “I've heard of it.” Ask me to explain it *after teaching*.
- Explicitly distinguish: “You understood it but couldn't phrase it yet” versus “The technical reasoning is incorrect.”
- Keep a private-in-session progress note: current lesson, facts understood, speaking stage, confusion, next step. At
  the end, show me a compact progress note I can save for the next chat.

### E. The only progress gates

| Phase                    | Enough to continue                                                                                       | NOT required yet                                          |
|--------------------------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| **Foundation** (M01–M02) | Follow a worked example; answer a small taught question; explain in 1–3 sentences with prompts if needed | Cold system design, complex trade-offs, speed             |
| **Mechanics** (M03–M06)  | Trace normal path; explain one failure; apply to a nearby scenario; speak clearly for 30–60 seconds      | Full senior panel answer                                  |
| **Design** (M07–M11)     | Compare two choices; state why, failure, test and owner; speak for 60–90 seconds                         | Perfection or exhaustive vendor trivia                    |
| **Interview** (M12)      | Solve unfamiliar cases with appropriate time limits, clear speech, and safe decisions                    | Memorized scripts or claims about real employer internals |

Passing a lesson means understanding **and** explaining, not memorizing the answer. Keep the 141 items in the appendix
as coverage checks, **not** a starting quiz or a list of 141 lectures.

## 2. Start using this guide — no setup or test required

### Copy/paste this exact prompt into a new tutoring chat

```text
Use the attached "Beginner-First Learning & Speaking Curriculum".
I am preparing for a Senior Solutions Architect interview, but please assume
I am a complete beginner. I recognize some technical words but struggle to
explain them clearly. Do not diagnose me first. Start at Lesson L01 below.

Teach ONE small concept per turn, with simple English, a small example and an
ASCII diagram when useful. Define every new technical term. After teaching,
ask ONE easy question about what you just explained. Wait for my answer.
Then help me turn the idea into one natural sentence, a short explanation,
and eventually a professional interview answer. If I struggle, simplify,
show me an example, and let me retry. Do not skip prerequisites.

Separate feedback about technical understanding from feedback about wording.
No senior-level challenges until the basics are clear. Don't claim company
internals or current standards without official evidence. At the end of a
session, give me a compact progress note for the next chat.
```

### A small, realistic session

| Order | Tutor action                                               | My action                          |
|-------|------------------------------------------------------------|------------------------------------|
| 1     | Explain one idea in plain English (2–4 minutes of reading) | Read or listen                     |
| 2     | Walk through one example                                   | Follow each step                   |
| 3     | Ask one question based on that example                     | Answer in any English I can manage |
| 4     | Help me repair my answer                                   | Say it again, shorter and clearer  |
| 5     | Ask a nearby variant                                       | Try without copying the model      |
| 6     | Save one-sentence progress note                            | Continue or stop without guilt     |

**Articulation practice is not optional.** If I can select the right multiple-choice answer but cannot say one correct
sentence about it, we continue practicing that concept.

### How we review previous lessons

- Start later sessions with a **two-minute recap of already taught material**, not a cold diagnostic of the full
  syllabus.
- A useful optional review schedule is 1, 3, 7 and 21 days after a lesson. Adapt to my availability and actual memory;
  these are planning intervals, not a proven personal optimum.
- Change the example on review, but keep the underlying idea the same.
- Keep a short **my own words** glossary. Do not fill it with copied definitions.
- If I lose a concept, revisit the original worked example before moving on.

---

## 3. Running practice story (hypothetical)

> **Hypothetical system:** A commercial spending platform. Administrators set spend policies. Employees request
> purchases. A risk capability checks some transactions. A payment provider may perform an external action. Finance
> staff
> need status, statements, audit history, and reconciliation. Suppliers may also receive payments through different
> rails.
> No claim is made about any American Express internal system.

### Starting journey

```text
Employee                 Business platform                External parties
   |                            |                               |
   |--- submit purchase ------->|                               |
   |                            |--- read policy/limit          |
   |                            |--- validate identity          |
   |                            |--- maybe check risk ---------->|
   |                            |--- persist request/state      |
   |                            |--- financial instruction ----->|
   |                            |<-- reply (may be lost) -------|
   |<--- status / request ID ---|                               |
   |                            |--- durable event intent       |
   |                            |--- reporting projection       |
   |                            |--- reconciliation workflow    |
```

Treat every arrow as a potential delay, duplicate, timeout, denial, overload, data exposure, or uncertain state. Always
specify **what the caller knows** versus **what actually occurred**.

### Sample entities to evolve (not a prescribed schema)

- `Organization`, `User`, `Entitlement`, `SpendPolicy`, `PolicyVersion`
- `PurchaseRequest(request_id, organization_id, amount_minor, currency, state)`
- `IdempotencyRecord(scope, key, payload_hash, operation_id, outcome)`
- `PaymentAttempt(attempt_id, operation_id, partner_reference, status)`
- `OutboxEvent(event_id, aggregate_id, event_type, version, payload)`
- `ReconciliationException(exception_id, operation_id, evidence, owner, status)`

Use integer minor units (such as cents) rather than binary floating point for simple monetary examples.
Currency-specific precision and rounding rules must be specified for real systems.

### Business invariants to investigate, not assume automatically true

- Every attempt is attributable to an authenticated and authorized tenant/actor.
- One logical request must not accidentally create multiple externally effective financial actions.
- A recorded state must say no more than the available evidence proves.
- Policy decisions have a documented policy version and audit evidence.
- Reports may lag within an agreed window; core financial correctness must not silently degrade.
- Discrepancies are visible, assigned, reconciled, and repaired through controlled actions.

These are candidate requirements. In an interview, **confirm which ones apply**, who owns them, and what external
provider capabilities are actually available.

### Later variation deck (use after normal flows are clear)

| Card | Inject a surprise                                           | What must change?                                     |
|------|-------------------------------------------------------------|-------------------------------------------------------|
| V1   | The payment succeeded, but the reply never arrived          | State, replay, query and reconciliation               |
| V2   | Two identical requests arrive concurrently                  | Atomic deduplication scope and result                 |
| V3   | Policy is edited while a purchase is being processed        | Decision snapshot, transaction/order control          |
| V4   | Reporting is unavailable for six hours                      | Durable events, lag, catch-up, customer freshness     |
| V5   | The largest tenant produces half of traffic                 | Partitioning, fairness, isolation, cost               |
| V6   | Primary region becomes partitioned, not conclusively dead   | Writer authority, failover, fencing, uncertain writes |
| V7   | A customer retrieves another customer's purchase ID         | Object-level authorization, tenant isolation, tests   |
| V8   | A downstream provider has no status-query API               | Uncertain outcomes, manual escalation, contracts      |
| V9   | The business requests 10× load next month                   | Estimation, bottleneck evidence, migration plan       |
| V10  | The system looks healthy, but purchases are stuck pending   | Journey SLI, traces, lag, state reconciliation        |
| V11  | A partner's webhook is duplicated and reordered             | Event identity, ordering scope, consumer semantics    |
| V12  | A new rail has different settlement and exception semantics | Shared capabilities versus rail-specific states       |

**Tutor rule:** Do not use these until the learner can explain the normal path. Introduce just one failure at a time,
then later rotate unfamiliar variations.

---

## 4. Your first lesson — L01 (begin here, not with a diagnostic)

### L01 — What is a computer program?

**Goal:** Understand three words: **computer**, **program**, **process**. Nothing else is assumed.

**Plain explanation:** A computer is a machine that follows instructions. A **program** is a set of instructions written
for a computer. A **process** is a program while it is running. We will learn more about the operating system later.

**Everyday comparison:** A written cooking recipe is like a program. Cooking the recipe is like running a process. The
comparison helps, but computer processes also use memory and other system resources.

**Tiny flow:**

```text
Instructions saved on disk (program)
                   |
              start / run
                   v
Instructions being executed (process)
                   |
             produces result
                   v
                 output
```

**Worked example:** Here is a tiny Python program. You do not need to know Python yet.

```python
print("Hello")
```

- `print` means “show some output.”
- `"Hello"` is the text to show.
- When a Python interpreter executes the instruction, the result is `Hello`.
- The source code is part of the program. When it runs, an operating-system process executes it.

**Comprehension check (ask only this first):** “What is the difference between a program and a process?”

**If I need help, offer this starter:** “A program is ___; a process is ___.”

**After my attempt, show a simple sample:** “A program is saved instructions. A process is those instructions running.”
Then ask me to say it another way. Do **not** immediately teach servers, memory management, threads, or microservices.

**Speaking ladder, only when ready:**

- First: “A program contains instructions. A process is a running program.”
- Next: “An operating system runs programs as processes and manages the resources they use.”
- Much later, in an architecture interview: “A service runs in one or more processes. Each process can fail
  independently, so I need to understand which work and state survive a restart.”

**One small variation after success:** “If a program is stored on disk but nobody runs it, is it a running process?”
Expected idea: no.

**Completion evidence:** I can explain program vs process in **my own words**. No score, no stopwatch.

### L02 preview — What are input, output, and data?

Teach L02 in the same small-step format **only after** L01 is understood. Start with a calculator example. The input is
`2` and `3`, the operation is addition, and the output is `5`. Then introduce the term **data** as information a program
receives, stores, or produces. Do not teach variables until this is clear.

### L03 preview — What is a variable?

After L02, use `price = 100` and show how a program stores a named value. Ask me what is stored in `price`. Then ask for
a one-sentence explanation of a variable. Do not introduce concurrency or memory layout here.

**The remaining lessons follow the same teach → trace → explain → practice pattern.** The next section specifies their
dependency order.

---

## 5. The path: 12 missions taught as 125 micro-lessons

**Mission order is a prerequisite order, not a time limit.** There are **125 very small lessons** grouped into 12
missions. Some lessons may take several sessions. Start at L01 and continue in sequence. Do not skip ahead because a
title sounds familiar. The 141-topic coverage audit is in Appendix A; it is not the study sequence.

The original **“Do”** exercises in each mission are **end-of-mission capstones**, not Day 1 homework. The tutor must
first teach the micro-lessons above them. The learner may use notes and hints for early attempts. Each capstone becomes
independent only after repeated supported practice.

| Order | Mission                                                     | Primary result                                      |
|-------|-------------------------------------------------------------|-----------------------------------------------------|
| M01   | Computing, Python, web, SQL                                 | Runnable code and a tiny correct database           |
| M02   | Business, commercial payments context, architecture framing | One-page problem brief and clear diagrams           |
| M03   | Service boundaries, uncertainty, time, concurrency          | Failure timeline and justified boundaries           |
| M04   | Data authority, replication, consistency, sharding          | Data/consistency contract and scale choices         |
| M05   | Financial workflows, idempotency, transactions              | Safe state machine and reconciliation design        |
| M06   | APIs, integration, events, replay                           | Consumer-safe contract and replayable pipeline      |
| M07   | Identity, tenant isolation, payment-data security           | Threat model and authorization tests                |
| M08   | Reliability, capacity, overload controls                    | Numeric capacity model and failure budget           |
| M09   | Multi-region recovery, observability, incidents             | Failover runbook and evidence-based incident review |
| M10   | Cloud, Python engineering, test and release                 | Working code and adversarial review                 |
| M11   | Modernization, governance, influence, AI, stories           | Roadmap, decisions and truthful leadership stories  |
| M12   | Unseen end-to-end interview simulations                     | Independent, repeatable readiness evidence          |

### M01 — Make the system real: computer → program → network → database

**Beginner micro-lessons (in order; do not bundle them):**

- **L01:** Computer, program, and running process.
- **L02:** Input, output, and data.
- **L03:** Variables and simple values.
- **L04:** Expressions and comparisons.
- **L05:** `if` decisions.
- **L06:** Functions: input, work, return value.
- **L07:** Lists, dictionaries, and loops.
- **L08:** Errors and why programs stop unexpectedly.
- **L09:** Simple tests and boundary cases.
- **L10:** Client, server, request, and response.
- **L11:** Addresses, ports, Domain Name System (DNS), Transmission Control Protocol (TCP), and Transport Layer Security
  (TLS), one at a time.
- **L12:** Hypertext Transfer Protocol (HTTP): method, status, headers, and response body.
- **L13:** JavaScript Object Notation (JSON) and an application programming interface (API) contract.
- **L14:** Database, table, row, column, and key.
- **L15:** Structured Query Language (SQL): `SELECT`, `WHERE`, `JOIN`, `INSERT`, and `UPDATE`, one operation at a time.
- **L16:** Database transaction and rollback.
- **L17:** Uniqueness, foreign keys, indexes, and basic data correctness.
- **L18:** Guided mini-project: tiny spending rule, API sketch, and purchase table.

**First-pass rule:** For L01–L17 use tiny questions, not the full mission project. Do L18 only after the pieces make
sense.

**Why first:** Later discussions fail if "process", HTTP, transaction, and uniqueness are vague.

**Learn in small steps:** Hardware/OS/process/memory → Python values, control flow, functions, exceptions/tests →
client/server, DNS/TCP/TLS/HTTP, JSON, API contract → relational keys, JOIN, `INSERT/UPDATE`, transactions, indexes,
parameterized SQL.

**Do, don't just read:**

1. Implement `check_spend(amount_minor, remaining_minor)` in Python. Reject invalid and negative amounts; test equality
   at the limit, above limit, zero, wrong types.
2. Draw one browser → service → database request. Mark an error response versus a missing network reply.
3. Create `organizations`, `policies`, `purchases` in SQLite with primary/foreign keys, a uniqueness rule, and a
   transaction. Write one `JOIN` and one rollback test.
4. Explain why an index improves a query but **does not replace** a unique constraint.

**Break it:** Throw an exception between two related writes; show what a transaction protects and what it cannot protect
across two independent systems.

**End-of-mission evidence, after guided lessons:** Working code/tests + diagram + SQL example + a clear 30–60-second
explanation (first with prompts, later without notes). **Coverage:** C001–C013.

**A senior-style question with beginner vocabulary:** "Should the same spending rule be copied into three callers or
owned in one place? What makes it testable and changeable?"

### M02 — Start from the business, not the technology

**Beginner micro-lessons:**

- **L19:** What a business process is, using one employee purchase.
- **L20:** Who the customer, administrator, employee, supplier, and finance user are.
- **L21:** Requirement versus assumption versus constraint.
- **L22:** What “success” means and how to measure it.
- **L23:** What an architecture diagram tries to explain.
- **L24:** One simple journey and one sequence diagram.
- **L25:** Commercial spending policy, approvals, and organizational limits.
- **L26:** Invoice, accounts payable (AP), and enterprise resource planning (ERP).
- **L27:** Virtual card versus bank payment, at business level only.
- **L28:** Trade-off and architecture decision: two plausible choices.

**First-pass rule:** Teach one user journey first. Add stakeholders and payment variants gradually.

**Learn:** Customer/admin/employee/finance/supplier journeys; accounts payable (AP), enterprise resource planning (ERP),
virtual cards versus ACH/check; policy, limits, authorization and approval; requirements, quality attributes, capability
boundaries, stakeholders, architecture views, decision records.

**Do:**

1. Ask 10 clarifying questions of the running case. Label every answer **known**, **assumed**, or **open**.
2. Draw three journeys: **employee purchase**, **supplier invoice → approval → instruction**, **finance
   reconciliation**. Mark differences in financial rails and states.
3. Write a one-page brief with actors, major capabilities, three business outcomes, three quality-attribute scenarios
   (for example, a measured status freshness target), risks, dependencies, and owners.
4. Produce context and sequence diagrams. Compare a modular monolith and separately deployed services at a high level;
   record one ADR.
5. Give the brief aloud in 2 minutes as if speaking to a business sponsor.

**Break it:** Finance says "real time". Risk needs more checks. Engineering suggests a five-minute projection delay.
Turn the disagreement into measurable options and identify who can accept each risk.

**Exit evidence:** Problem brief, capability map, diagrams, ADR, and spoken explanation. **Coverage:** C014–C028,
C032–C034. **Depth:** cross-border details only if relevant.

**Trap to avoid:** Treating "American Express probably does X" as a requirement. Use public business context only as
context; do not invent internal architecture.

### M03 — The essential distributed-systems mental model

**Beginner micro-lessons:**

- **L29:** One running program versus two programs communicating.
- **L30:** Modular monolith versus separate services (no “always use microservices”).
- **L31:** Network call, latency, and a normal request timeline.
- **L32:** What failure looks like: crash, missing reply, or delayed reply.
- **L33:** A timeout tells us we stopped waiting, not necessarily what happened.
- **L34:** Safe and unsafe retries; stable request identity.
- **L35:** Two requests at the same time; lost update.
- **L36:** Transactions inside one database versus actions across systems.
- **L37:** Synchronous versus asynchronous communication.
- **L38:** Clock/timing and why timestamps do not always prove order.
- **L39:** Network partition and choosing which operation may pause.
- **L40:** Small failure timeline and a two-choice decision.

**First-pass rule:** Explain the normal request before introducing failures. Introduce only one failure at a time.

**Learn:** Modular monolith versus services; synchronous versus asynchronous calls; process crash versus network loss;
timeouts and uncertain outcomes; hop latency; deadlines; network partitions and per-operation consistency decisions;
causality, clock uncertainty, lost updates, optimistic/pessimistic locking; idempotency and saga/outbox motivation.

**Do:**

1. Take a purchase → policy → payment call chain. Mark each node, network hop, owner, timeout, and possible unknown
   result.
2. Draw **three timelines**: (a) request fails before execution, (b) result committed then reply lost, (c) client
   retries while the first call is still running. Say what is observed, what is unknown, and the safe next action.
3. Allocate a hypothetical end-to-end latency target across hops; explain why adding serial dependencies hurts the tail.
4. Demonstrate a lost update with two workers. Fix it with a database version check or appropriate transaction/locking;
   show a conflicting write test.
5. Explain a partition using **one concrete operation**: what stays available, what must pause, and why. Avoid labeling
   an entire product "AP" or "CP" without context.

**Break it:** The external risk service becomes unavailable during an approval. Compare stop/decline, wait, and narrowly
defined degrade; specify what business policy authorizes each.

**Exit evidence:** Three failure timelines, concurrency repro, measured/estimated latency diagram, service-boundary ADR.
**Coverage:** C036–C045, C118–C123. **Depth:** leases/fencing only when a stale owner might still act.

**Pass phrase to understand, not memorize:** "A timeout proves I lack a timely answer; it does not prove the action did
not occur."

### M04 — Decide what data is true, and when

**Beginner micro-lessons:**

- **L41:** What a source of truth means.
- **L42:** Why applications keep a second copy of data.
- **L43:** Replica, replication delay, and stale reading.
- **L44:** Stronger versus weaker read/write guarantees; examples.
- **L45:** Leader and follower; what happens when one fails.
- **L46:** Read/write agreement and quorum ideas using a toy model.
- **L47:** Sharding/partitioning by a stable key.
- **L48:** Hot partition, data movement, and cross-partition work.
- **L49:** Data correction and reconciliation versus silent overwrite.

**First-pass rule:** A duplicated record and a delayed copy must be clear before consensus/quorum jargon.

**Learn:** Source of truth and data ownership; transactions versus read projections; leader/follower and
synchronous/asynchronous replication; replica lag; linearizable versus eventual reads/writes; quorum and partitions in a
**specified** datastore model; shard key, hot keys, fan-out, rebalancing; data contracts, lineage, freshness, audits,
retention and reconciliation.

**Do:**

1. Make a table for `policy`, `purchase`, `provider status`, and `finance report`: owner, authoritative writer, readers,
   freshness promise, and repair method.
2. Simulate a stale replica: purchase commits on the leader; a follower still returns old state. Decide which user path
   can tolerate that.
3. Compare one primary datastore versus sharding by organization. Model a tenant so large that the chosen key becomes a
   hotspot; propose two alternatives and their costs.
4. Write a reconciliation query or precisely testable consistency check for missing/duplicated records.

**Break it:** A network partition leaves replicas unable to coordinate. Specify which write operations remain allowed;
discuss split-brain or stale-read risks **under explicit assumptions**, not generic database slogans.

**Exit evidence:** Data-authority matrix, two read/write contracts, partition-key ADR, discrepancy test. **Coverage:**
C058–C065, C124–C130. **Depth:** consensus internals, cache invalidation, and CQRS/event sourcing only on evidence of
need.

**Interview follow-up:** "Your reporting database disagrees with payment status. Which fact is authoritative, and how
would you correct the projection without losing evidence?"

### M05 — Financial correctness: unknown outcomes are a first-class state

**Beginner micro-lessons:**

- **L50:** What a business operation is versus a single attempt.
- **L51:** Authorization, clearing, settlement, and reconciliation are different states.
- **L52:** A simple state machine with only valid transitions.
- **L53:** One logical instruction, repeated request; idempotency in plain words.
- **L54:** Durable identity, unique constraint, and concurrent duplicates.
- **L55:** Unknown payment outcome after a timeout.
- **L56:** Query status, preserve evidence, and controlled reconciliation.
- **L57:** Local database transaction and an external dependency.
- **L58:** What compensation can and cannot undo.
- **L59:** Ledger/audit evidence, exception owner, and a safe spoken answer.

**First-pass rule:** Do not mention 'exactly once' or distributed sagas until the student can trace a normal financial
operation.

**Learn:** Authorization, clearing, settlement, reconciliation **as distinct concepts**; payment rails with different
state machines; declines, reversals/refunds/disputes; request identity versus provider attempt identity; durable
idempotency, unique constraints, concurrent retries; transaction boundaries; outbox and saga with fallible compensation;
audit and exception repair.

**Do:**

1. Design states for a **hypothetical purchase instruction**: `RECEIVED → VALIDATED → SUBMITTED → CONFIRMED` with an
   explicit `UNKNOWN/PENDING_RECONCILIATION` branch. Define which transitions are reversible and which require external
   evidence. Do not force every payment rail into this exact state machine.
2. Design the idempotency key's scope, retention policy, payload mismatch handling, and unique database constraint. Race
   two identical requests and prove only one logical operation is created.
3. Trace: provider succeeds, response times out, retry arrives. Demonstrate **status query or reconciliation first** and
   distinguish a fresh financial action from safe re-observation. If the provider lacks idempotency/query capabilities,
   define escalation and avoid an unsafe blind retry.
4. Propose a durable outbox for committed local state; prove a consumer still needs duplicate handling.
5. Specify how finance detects and assigns unresolved discrepancies. Never present a compensation as guaranteed or as
   "undoing" an irreversible settlement.

**Break it:** The UI says "approved" but final settlement evidence has not arrived. Correct the user-facing semantics,
alert, reconciliation procedure, and audit trail.

**Exit evidence:** State machine, idempotency proof/test, uncertain-result timeline, reconciliation plan, one recovery
runbook. **Coverage:** C029–C031, C035, C131–C132; earlier C041/C043/C044 are tested again here. **Depth:**
network-specific messages only if the interview explicitly needs them.

**A strong answer always distinguishes:** requested action / local accepted request / external action / confirmed
provider outcome / financial completion / reconciled outcome.

### M06 — Make interfaces and events safe for other teams

**Beginner micro-lessons:**

- **L60:** What an API contract promises.
- **L61:** Requests, validation, success response, and error response.
- **L62:** Pagination and backward-compatible changes.
- **L63:** A message or event, producer and consumer.
- **L64:** Queue/broker and delayed consumption.
- **L65:** Acknowledgment, duplicate messages, and safe replay.
- **L66:** Ordering, event versions, and out-of-order examples.
- **L67:** Database update plus event intent: transactional outbox idea.
- **L68:** Dead-letter processing and ownership of repairs.
- **L69:** Choosing API call, event, webhook, or file for a concrete need.

**First-pass rule:** Start with sender → message → receiver, not Kafka terminology or delivery guarantees.

**Learn:** API consumer and owner; HTTP methods/status/errors, pagination, OpenAPI, versions and compatibility; login
versus delegated authorization (OAuth 2.0, OpenID Connect, mTLS by purpose); request/response versus events, webhooks,
batch and adapters; transactional outbox, broker partitions, ack/offset/retention, duplicate and out-of-order delivery,
poison events, dead-letter queue (DLQ), replay, consumer lag and monitoring.

**Do:**

1. Design `POST /purchase-requests` and `GET /purchase-requests/{id}` with explicit request identity, errors, pending
   state, authorization, version and compatibility behavior.
2. Define `PurchaseStatusChanged` with `event_id`, `operation_id`, `aggregate_version`, event time, schema version, and
   safe evolution rules. State **ordering scope**; do not assume a universal total order.
3. Write a consumer that deduplicates event IDs, rejects unsafe out-of-order state regressions, and acknowledges only
   after durable processing.
4. Model reporting offline for six hours. Explain retention, backlog growth, replay, freshness labels, poison-message
   handling, and the on-call owner.
5. Compare API pull, webhook push, and batch file integration for a partner with limited infrastructure.

**Break it:** The same event is replayed three times, with version 6 arriving before version 5. Specify the correct
resulting projection and test it.

**Exit evidence:** API contract sample, event schema, runnable/testable consumer, recovery diagram, compatibility ADR.
**Coverage:** C046–C057, C133–C134; C039/C044/C052/C053 reappear by design.

**Trap:** "The broker guarantees exactly once" is not a substitute for end-to-end side-effect reasoning.

### M07 — Security is an architecture boundary, not a last slide

**Beginner micro-lessons:**

- **L70:** Sensitive data and who should see it.
- **L71:** Authentication (who are you?) versus authorization (what may you do?).
- **L72:** One employee reading only the correct organization's purchase.
- **L73:** Tenant isolation, permissions, and test cases.
- **L74:** Trust boundary, encryption, secrets, and keys, one by one.
- **L75:** Token, scope, claims, and the purpose of OAuth / OpenID Connect / mutual TLS.
- **L76:** Audit trail and data minimization.
- **L77:** Threat scenario and how to verify the control.
- **L78:** Specialist review and residual risk statement.

**First-pass rule:** Never skip object-level permission checks because a request has a valid login.

**Learn:** Identity and service identity, authentication versus authorization; least privilege, role- and
attribute-based checks, tenant isolation; OAuth 2.0/OIDC/mTLS according to actual purpose; object-level access controls,
secrets/keys, encryption, tokenization, data minimization; threat modeling, third-party risk, software supply chain,
audit and privacy. Review current applicable Payment Card Industry (PCI) requirements with official material and
security specialists; **do not claim compliance from this guide**.

**Do:**

1. Mark all trust boundaries and sensitive fields in the design.
2. Attack a `GET /purchase-requests/{id}` endpoint by changing an object ID and tenant claim; write both negative and
   positive tests.
3. Identify five threats, each with control, residual risk, test, decision owner, and required specialist review.
4. Reduce payment-data handling and retention where possible. Show what additional risk remains at provider boundaries.
5. Explain delegated permission, user login, and workload authentication as different problems.

**Break it:** A disaster mode bypasses the usual permission service. Specify which operation fails closed and whether
any controlled degradation is permitted.

**Exit evidence:** Annotated trust-boundary diagram, authorization tests, threat/control table, residual-risk statement.
**Coverage:** C066–C074; C049/C055/C056/C063 reinforced.

### M08 — Capacity and reliability with numbers and ownership

**Beginner micro-lessons:**

- **L79:** Latency versus throughput; use easy numbers.
- **L80:** Capacity estimate from people × requests.
- **L81:** Peak traffic, concurrent work, and bottlenecks.
- **L82:** What a service level indicator (SLI) measures.
- **L83:** What a service level objective (SLO) sets as a target.
- **L84:** Why retries can create more load.
- **L85:** Timeouts and retry limits.
- **L86:** Queue, backpressure, and load shedding.
- **L87:** Circuit breaker and bulkhead ideas.
- **L88:** Simple cost-versus-reliability decision.

**First-pass rule:** Always teach one operation's latency before multi-hop budgets and performance math.

**Learn:** Service-level indicator (SLI), service-level objective (SLO), error budget; throughput versus concurrency;
percentiles and latency budgets; queueing, retry amplification, jitter, propagated deadlines, circuit breakers,
backpressure, bulkheads and load shedding; peak demand, hot partitions, capacity/cost trade-offs; graceful versus
fail-safe degradation; backup, RTO/RPO basics.

**Do:**

1. Given **hypothetical** 600 requests/second and a 0.4-second average in-flight time, estimate average concurrency.
   Then discuss why bursts and high-percentile latency still require headroom. State assumptions.
2. Allocate a response-time budget among API, policy, database and external dependencies; identify which remote call can
   exceed the deadline.
3. Design bounded retries with jitter and budgets **only for safe operations**. Compare this to a circuit breaker, then
   show the caller's observable result.
4. Decide which actions to pause under overload (financial instructions may need stricter behavior than an eventually
   consistent report).
5. Produce SLO/alert signals tied to end-to-end purchase success and an owner who can act on the signal.

**Break it:** 5,000 clients retry simultaneously after a 30-second upstream outage. Show how the load can amplify and
how limits prevent a retry storm.

**Exit evidence:** Estimate with assumptions, numeric budget, overload flowchart, SLO/alert definition, capacity ADR.
**Coverage:** C075–C082, C135–C136; C040/C081 re-tested here.

### M09 — Failover, diagnosis, and real operations

**Beginner micro-lessons:**

- **L89:** Logs, metrics, and traces: three ways to see what happened.
- **L90:** Customer success versus “server is up.”
- **L91:** Alert, on-call engineer, incident, and runbook.
- **L92:** Backup and restoring saved data.
- **L93:** Recovery time and recovery point objectives (RTO/RPO).
- **L94:** Two regions: primary and backup.
- **L95:** Why two simultaneous writers can conflict.
- **L96:** Safe failover, verifying data, and failback.
- **L97:** Simple incident investigation and fault-test plan.

**First-pass rule:** Understand restart and restore before regional failover or split brain.

**Learn:** Multi-region active/passive and active/active trade-offs; data-lag and writer authority; RTO/RPO, split
brain, fencing and failback; backups and restore tests; correlation IDs and traces; business-level observability,
consumer lag, incident process, runbooks, safe fault injection and postmortems.

**Do:**

1. Draw a two-region architecture with a **single stated authority** for critical writes. Show exactly what happens if
   the primary loses connectivity but may still be running.
2. Write a failover decision tree: declare, fence, assess data gap, switch, prove invariants, reconcile, return traffic,
   later fail back. Attach accountable owners.
3. Investigate "all containers healthy, but purchases pending." Use traces, state transitions, event lag, external
   partner status, and customer cohort as evidence.
4. Plan controlled tests: delayed reply, duplicated event, stalled consumer, and region outage. Name rollback/stop
   conditions.
5. Separate measured recovery time/data loss in a test from an aspirational target.

**Break it:** During a partition both regions think they are primary. Choose read-only/deferred writes versus writable
failover; define who decides and which data is authoritative.

**Exit evidence:** Runbook, incident timeline, dashboard/alert spec, drill table, measured-vs-target notes.
**Coverage:** C083–C085, C137–C140; C077/C078 reiterated.

### M10 — Prove that architecture survives code, test, and release

**Beginner micro-lessons:**

- **L98:** Where software runs and what deployment means.
- **L99:** Server, container, and managed runtime at an introductory level.
- **L100:** Code change, tests, and a safe release.
- **L101:** Configuration, secrets, and environments.
- **L102:** Read a small Python handler line by line.
- **L103:** Input validation and a simple authorization check.
- **L104:** Database write and a deliberately failing dependency.
- **L105:** Unit test versus integration test.
- **L106:** Rollout, feature flags, and rollback.
- **L107:** Simple code review: find and explain one defect.

**First-pass rule:** Never ask me to review production-style concurrent code before I can explain ordinary Python
functions.

**Learn:** Infrastructure and deployment zones; hybrid/on-premises dependencies; managed service versus containers;
infrastructure as code; configuration/secrets; service ownership; Python concurrency and production-style API review;
unit, integration, contract, load, security and resilience tests; continuous integration/continuous delivery (CI/CD),
rollout, rollback and safe operations.

**Do:**

1. Implement a minimal Python handler around a local transactional store with validation, tenant authorization stub,
   durable request identity, state transition, and a mocked external dependency. Keep the simulation **non-financial**;
   never connect to a live payment rail.
2. Add tests: same key with same/different payload, two concurrent requests, unknown external result, duplicate event,
   cross-tenant object read, rollback after database failure.
3. Review deliberately flawed code. Find unsafe retry, missing transaction/unique key, leaked token, unbounded
   memory/queue, and missing observability.
4. Make a small release plan: compatibility check, canary or feature flag, monitoring, rollback condition, and
   post-release invariant checks.
5. Compare managed runtime, containerized runtime, and a simpler deployment against team skill and reliability, not
   fashion.

**Break it:** A deployment changes event schema; an old consumer is still running. Demonstrate compatible evolution or a
safe rollout sequence.

**Exit evidence:** Code and tests, review comments ranked by risk, deployment diagram, rollback checklist. **Coverage:**
C086–C097.

### M11 — Act like an architect across an organization

**Beginner micro-lessons:**

- **L108:** Why systems need modernization.
- **L109:** Moving one feature gradually without breaking users.
- **L110:** Legacy adapter, coexistence, and transition ownership.
- **L111:** Roadmap: goal, milestone, owner, evidence.
- **L112:** Architecture standard versus exception.
- **L113:** Comparing cost, risk, and business benefit.
- **L114:** Explaining a decision to a nontechnical stakeholder.
- **L115:** Disagreement and mentoring, using only real experiences.
- **L116:** Answering behavioral questions with situation, action, result.
- **L117:** Using AI as a reviewer, verifying sources, and keeping information safe.

**First-pass rule:** Help me form truthful short stories; do not invent professional experience or performance metrics.

**Learn:** Inventory legacy systems and owners; adapter and strangler migration; coexistence, shadow/parallel operation,
reconciliation and decommission; enterprise roadmaps, standards, exceptions, build/buy, technical-debt economics;
stakeholder disagreement and mentoring; executive communication; truthful STAR/CAR personal stories; AI-assisted review
with confidentiality, source verification, prompt-injection awareness, and human accountability.

**Do:**

1. Create a phased migration of the purchase/reporting workflow. Show old/new writers, state ownership, reconciliation
   and rollback at **each** phase.
2. Write a one-page architecture decision and a one-page roadmap with measurable milestones, dependencies, owner,
   costs/risks and exit triggers.
3. Rehearse six **real** stories: hard trade-off, production issue, disagreement, migration, mentoring, reversed
   decision. Use personal actions and observed outcomes. If evidence is missing, say so.
4. Deliver one executive brief in 90 seconds: decision, business impact, primary risk, evidence, next step.
5. Ask an AI assistant to critique a design and identify which claims were accepted, rejected or require verified
   primary evidence. Do not upload confidential material without authorization.

**Break it:** Two teams disagree about service ownership while leadership wants an immediate launch. Propose decision
rights, a reversible experiment, escalation and a clear owner.

**Exit evidence:** Migration decision tree, roadmap, six honest story outlines, executive brief, AI verification log.
**Coverage:** C098–C114, C117.

### M12 — Earn the interview: no more familiar examples

**Gradual interview-speaking lessons before cold mocks:**

- **L118:** Give a 20-second plain-English explanation of a known topic.
- **L119:** Expand the same explanation to 60 seconds with a real example.
- **L120:** Draw and narrate one known request path.
- **L121:** Explain one familiar failure and recovery.
- **L122:** Compare two designs using one business requirement.
- **L123:** Explain a known design to a manager in plain English.
- **L124:** Only now attempt a new design prompt with hints; remove hints gradually.
- **L125:** Complete the timed cold design and senior panel rounds described below.

**First-pass rule:** If I freeze, return to a familiar problem and use sentence starters. Timed mocks are the *end* of
training, not the beginning.

**Prerequisite:** M01–M11 have been taught, practiced, and explained aloud. Start with guided known examples in
L118–L123; only then remove hints and try unfamiliar timed scenarios.

**Round A: 50-minute cold design.** Randomly choose an unfamiliar prompt. Require a business model, 2–3 measurable
nonfunctionals, invariants, two viable architectures, API/data contract, normal and failing state transitions, security,
observability, capacity reasoning, phased rollout and decision owner.

**Round B: 50-minute different cold design.** Midway through, inject one of: uncertain provider response, network
partition, 10× demand, outdated replica, tenant breach, six-hour consumer outage, or stricter recovery target. Defend
your change without papering over existing state.

**Round C: 40-minute senior panel.** Include one code-review problem, one incident diagnostic, one executive trade-off,
and two real leadership stories. Follow up aggressively on weak claims and evidence.

**Cold prompt deck (rotate; never use only the running case):**

- Enterprise invoice approval and multi-rail supplier payout.
- Per-tenant API rate-limit and entitlement platform.
- Audit-ready event ingestion from unreliable partners.
- Multi-region reservation/inventory allocation with a hard no-oversell rule.
- Near-real-time expense reporting fed by delayed batches and events.
- Safe migration from a shared database to service-owned data.

**Late-stage readiness gate (not used during beginner lessons):** Two different cold design mocks **and** two
consecutive senior panel/deep-dive mocks. Score at least **3/4 in every applicable category**, with **4/4 on
safety-critical correctness and recovery**, no blocking mistakes, and an articulate 60–90-second summary. This is a
self-imposed preparation standard, not an employer passing score. Retest weak areas after a spaced interval; do not
declare readiness from the best single attempt.

**Exit evidence:** Time-stamped scoring sheets, recordings/notes if available, diagrams, decisions, follow-up gaps, and
corrected re-tests. **Coverage:** C115–C116, C141 (and integration of all earlier core skills).

---

## 6. The senior interview design script (use for every cold prompt)

**Use only after M01–M11 prerequisites.** This is an eventual interview outline, not a script for a beginner to
memorize. First learn to narrate one request from input to output.

| Interview phase      | What I must produce                                                | Warning sign                         |
|----------------------|--------------------------------------------------------------------|--------------------------------------|
| 1. Frame             | Users, journey, decision, missing facts                            | Jumping to Kafka or microservices    |
| 2. Prioritize        | Measurable correctness, latency, availability, freshness, security | "Highly scalable" with no target     |
| 3. Invariants        | What must never happen; evidence of truth                          | Ignoring duplicate/uncertain actions |
| 4. Choose boundaries | System context, owners, key stores, trust lines                    | No source of truth                   |
| 5. Walk normal path  | Sequence, state changes, contracts                                 | Boxes with no execution story        |
| 6. Walk failure path | Timeouts, concurrency, replay, partition, recovery                 | "Retry solves it"                    |
| 7. Size & operate    | Capacity estimate, hotspots, SLO, alert, failover                  | No numeric assumptions or owner      |
| 8. Compare           | Two credible options, costs, reversal condition                    | One fashionable answer               |
| 9. Deliver           | Security, migration, tests, milestones, rollback                   | No feasible adoption path            |
| 10. Summarize        | Recommendation, consequence, evidence and next step                | Endless details without a decision   |

**Suggested 50-minute allocation:** 5 framing, 5 requirements/invariants, 12 core design, 10 correctness/failure, 6
scalability/security, 6 alternatives/operations/rollout, 6 questions and summary. This is a training allocation, not a
known interview format. Change it according to the interviewer.

### Reusable ASCII views

Context:

```text
Actors --> Product/API boundary --> External systems
                 |                      |
              Data owner             Trust boundary
```

Request/failure timeline:

```text
Time     Caller           Our system             External provider
 t0       submit ---------> store intent
 t1                       send instruction -------> executes?
 t2       timeout <-------- no response <---------- X reply lost
 t3       retry same ID --> inspect durable state
 t4                       query/reconcile --------> evidence
 t5       known/pending <-- outcome based on evidence
```

State trace:

```text
received -> validated -> instruction_sent -> confirmed
                              |
                              v
                   outcome_unknown -> reconcile -> final_state
```

These are teaching sketches, **not** universal production state machines.

### The seven questions that expose shallow designs

1. What must never become inconsistent, and who defines that rule?
2. What is the unique identity of a business operation versus an attempt?
3. What if the result is **unknown**, not merely success or failure?
4. Which system is authoritative for each state, and for how long can reads be stale?
5. What happens if this dependency, region, or consumer disappears while others remain healthy?
6. How does an operator prove that a repair worked without erasing audit evidence?
7. Why is this architecture better than a simpler alternative **for these constraints**?

If one answer is missing, the design is incomplete; ask for the missing fact or name the assumption.

---

## 7. Later worked examples (read after the underlying lessons, not on Day 1)

### Drill A — Unknown payment outcome

**Question (only after learning idempotency and uncertain outcomes):** A purchase request has a stable ID. The platform
sends an external instruction. The provider may have executed it, but the reply times out. The client resubmits the same
ID. Can the platform safely send a new instruction?

**Worked reasoning:**

1. A timeout is **no timely confirmation**; it is not evidence of nonexecution.
2. Look up a durable local record using an idempotency scope that includes the tenant/caller as appropriate. A unique
   constraint and atomic creation protect concurrent requests.
3. Compare the stored payload fingerprint. The same key with a different request should be rejected rather than silently
   reused.
4. If the provider supports idempotency, reuse its documented key/contract within its actual guarantees. Otherwise query
   the provider's status or reconcile against authoritative external evidence.
5. While the result is unresolved, return a truthful **pending/unknown** status and queue controlled reconciliation. Do
   not issue a second independent money-moving instruction blindly.
6. Close only after durable evidence and invariant checks; escalate unresolved cases with trace IDs, owners, and an
   audit trail.

**Change the problem:** Two requests reach two API instances simultaneously. Which **atomic storage guarantee** prevents
duplicate creation? What if the provider has no reliable query endpoint?

**Senior spoken version:** "I treat a timeout as an unknown result. I persist the logical request identity, deduplicate
atomically, and use the provider's documented idempotency or status contract to resolve it. If that evidence is
unavailable, I keep the operation pending and reconcile rather than risking a second financial action."

### Drill B — A broken reporting pipeline

**Question (only after learning APIs, events, and database transactions):** Purchases must continue even if reporting is
unavailable for six hours; finance accepts delayed visibility. What must be true for this to be safe?

**Worked reasoning:**

1. Record the authoritative purchase state in a local transaction with a **durable event intent** (such as an outbox);
   do not assume database and broker writes are atomic together.
2. Relay the event eventually. A crash/restart can cause duplicates; the consumer must tolerate them.
3. Give each event an identity, aggregate/order scope, and schema evolution rule.
4. Track consumer lag, last processed position, oldest event age, dead-letter cases, and visible report freshness.
5. Define retention sufficient for the agreed outage and recovery; do not assume infinite backlog capacity.
6. On recovery, replay safely, compare reporting completeness with the authoritative store, and assign exceptions for
   repair.
7. Finance sees a data freshness indicator, not a false "live" badge.

**Change the problem:** The reporting projection falls 12 hours behind and retention expires after eight. What can be
rebuilt from the source of truth? Which escalation is immediate?

**Senior spoken version:** "Because reporting has a defined freshness allowance, I would keep purchase correctness
independent of reporting availability. A durable event-intent and idempotent projection allow replay. I would monitor
backlog and completeness, publish actual freshness, and reconcile after recovery."

---

## 8. Later review: the misconception bank (do not memorize before lessons)

| Tempting claim                         | Better mental model                                                                                 |
|----------------------------------------|-----------------------------------------------------------------------------------------------------|
| "Timeout = operation failed"           | Timeout = no answer within a deadline; outcome may be unknown                                       |
| "Microservices = distributed systems"  | A single modular application may interact with remote databases/providers; boundaries matter        |
| "A unique ID guarantees exactly once"  | Identity must combine with atomic storage, provider contract, deduplication and recovery semantics  |
| "Events are ordered"                   | Ordering is limited to a documented scope and broker/model; consumers still need defensive handling |
| "Sagas roll back transactions"         | Local steps commit; compensations are business actions that may fail or be irreversible             |
| "A replica is a fresh source"          | Freshness depends on replication semantics and observed lag                                         |
| "A quorum fixes every partition"       | The guarantee depends on the actual protocol, configuration, failure model and operation            |
| "Active/active means resilient writes" | Conflicting write authority may break invariants without strong coordination/conflict design        |
| "API gateway means secure API"         | Enforce per-object, per-tenant and function permissions at appropriate boundaries                   |
| "Up servers = healthy product"         | Measure completed business journeys and repairability, not only infrastructure health               |
| "Authorized = settled"                 | Authorization and later clearing/settlement/reconciliation are distinct evidence stages             |
| "A good diagram = an architecture"     | Senior architecture includes ownership, invariants, operation, risk, and adoption                   |
| "I can answer it after reading"        | Mastery requires cold recall, application, changed constraints and delayed retest                   |

---

## 9. Checklists for actual interview day

### Before technical design

- [ ] I can state **known / assumed / unknown** without pretending.
- [ ] I ask about core workflow, correctness, peak traffic, security, and failure tolerance.
- [ ] I state a minimum viable design before adding components.
- [ ] I anchor technology claims to mechanisms and constraints.

### Before calling a financial path "safe"

- [ ] Business operation and external attempt IDs are distinct where necessary.
- [ ] Concurrent duplicates have an atomic prevention mechanism.
- [ ] Uncertain outcomes remain visible until reconciled.
- [ ] The provider's retry and status guarantees are not assumed.
- [ ] Audit and finance reconciliation preserve evidence and ownership.
- [ ] Payment rail semantics are not accidentally mixed.

### Before recommending production rollout

- [ ] The source of truth and writer authority are explicit.
- [ ] Object- and tenant-level access checks are testable.
- [ ] Latency/reliability/freshness targets are measurable.
- [ ] SLO, alerts, capacity, failure drills, and on-call ownership exist.
- [ ] Migrations have coexistence, reconciliation and rollback criteria.
- [ ] A simpler alternative was seriously compared.

### Before closing a behavioral answer

- [ ] It is a real event and accurately describes **my** actions.
- [ ] The initial disagreement/constraint is clear.
- [ ] I explain a real option I rejected and why.
- [ ] Outcome is evidence-based; uncertainties are acknowledged.
- [ ] I explain what I learned or would do differently.

---

## 10. Official, primary references (use only when relevant)

Official technical references were cross-checked for Python basics, SQLite transaction behavior, and AWS transactional
outbox on 2026-10-24. Check the current version again when learning a specification. The sources below explain standards
or documented technical patterns. They do **not** verify employer-specific interview scope, internal systems, or
implementation choices.

| Learn this                               | Primary source                                                                                                                                                                  |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Python language                          | [Python tutorial](https://docs.python.org/3/tutorial/) (the tutorial expects some programming background; use M01 first if completely new)                                      |
| Relational transaction behavior          | [SQLite transactions](https://www.sqlite.org/lang_transaction.html)                                                                                                             |
| HTTP behavior                            | [IETF RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)                                                                                                   |
| API descriptions                         | [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)                                                                                                              |
| OAuth security                           | [IETF RFC 9700 — OAuth 2.0 Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html)                                                                                           |
| Authn vs authz implementation risks      | [OWASP API Security Top 10](https://owasp.org/API-Security/) (primary project guidance; tailor controls to the threat)                                                          |
| Distributed compensating workflows       | [Microsoft Learn — Saga](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)                                                                                    |
| Local database + event dual-write safety | [AWS — Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)                                          |
| Circuit breakers                         | [Microsoft Learn — Circuit breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)                                                              |
| PCI standard documents                   | [PCI Security Standards Council document library](https://www.pcisecuritystandards.org/document_library/) (verify applicability and current version before citing requirements) |

**Reference discipline:** Start from a scenario, identify the claim to verify, read the appropriate official primary
source, and record what the source **does and does not** prove. Vendor documents describe their named systems or
patterns, not universal guarantees.

---

## Appendix A. Full coverage audit: original C001–C141 preserved

This is a **coverage inventory**, not the teaching order. Each legacy item is assigned to a new mission. The
descriptions are taken from the supplied study map and deduplicated where original cards repeated an item. Use the right
depth for the current phase: **simple explanation first**, then a tiny application, then failure/trade-off practice when
its prerequisite lessons have been taught, and eventually a later retest. `Depth` means optional unless scope or a
demonstrated gap requires it.

| ID   | Focus (original requirement)                                                                                                                                                                            | Mission | Tier  | Check |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------|-------|
| C001 | Explain hardware, operating systems, programs, processes, memory, files, and how an application executes.                                                                                               | M01     | Core  | ☐    |
| C002 | Use Python variables, basic types, operators, conditions, loops, functions, and simple collections.                                                                                                     | M01     | Core  | ☐    |
| C003 | Read code, trace inputs and outputs, catch errors, and distinguish a defect from an expected result.                                                                                                    | M01     | Core  | ☐    |
| C004 | Write, run, and test a small Python function with normal, invalid, and boundary inputs.                                                                                                                 | M01     | Core  | ☐    |
| C005 | Explain client, server, browser, backend, process, network address, port, and request/response.                                                                                                         | M01     | Core  | ☐    |
| C006 | Trace Domain Name System (DNS), Transmission Control Protocol (TCP), Transport Layer Security (TLS), and Hypertext Transfer Protocol (HTTP) at a beginner level.                                        | M01     | Core  | ☐    |
| C007 | Understand HTTP verbs, response status, headers, JSON bodies, and network failure versus application error.                                                                                             | M01     | Core  | ☐    |
| C008 | Explain what an application programming interface (API) contract specifies.                                                                                                                             | M01     | Core  | ☐    |
| C009 | Distinguish relational databases, tables, records, columns, relationships, and data ownership.                                                                                                          | M01     | Core  | ☐    |
| C010 | Design primary keys, foreign keys, and basic one-to-many relationships for a tiny business case.                                                                                                        | M01     | Core  | ☐    |
| C011 | Write Structured Query Language (SQL) SELECT, WHERE, JOIN, INSERT, and UPDATE examples.                                                                                                                 | M01     | Core  | ☐    |
| C012 | Explain database transactions, atomicity, constraints, and what a partial update would break.                                                                                                           | M01     | Core  | ☐    |
| C013 | Explain beginner-level indexes, safe queries, and basic data correctness checks.                                                                                                                        | M01     | Core  | ☐    |
| C014 | Identify customer types, user roles, business capabilities, and end-to-end journeys.                                                                                                                    | M02     | Core  | ☐    |
| C015 | Map stakeholders, decision owners, affected teams, and conflicting objectives.                                                                                                                          | M02     | Core  | ☐    |
| C016 | Elicit functional requirements, constraints, assumptions, and open questions.                                                                                                                           | M02     | Core  | ☐    |
| C017 | Write measurable quality-attribute scenarios for availability, latency, security, data freshness, and changeability; rank them by business impact.                                                      | M02     | Core  | ☐    |
| C018 | Define business key performance indicators (KPIs) and technical measures that show whether the solution worked.                                                                                         | M02     | Core  | ☐    |
| C019 | Produce context, component, data-flow, sequence, and deployment views for different audiences.                                                                                                          | M02     | Core  | ☐    |
| C020 | Compare options using explicit criteria; write architecture decision records with consequences and revisit triggers.                                                                                    | M02     | Core  | ☐    |
| C021 | Trace requirements to design decisions, tests, risks, dependencies, and owners.                                                                                                                         | M02     | Core  | ☐    |
| C022 | Practice a formal architecture review and evaluate whether a design is ready to implement.                                                                                                              | M02     | Depth | ☐    |
| C023 | Explain corporate and small-business spending needs, including travel and expense, employee purchasing, and administrative controls.                                                                    | M02     | Core  | ☐    |
| C024 | Model customer, administrator, employee, finance, supplier, and servicing journeys.                                                                                                                     | M02     | Core  | ☐    |
| C025 | Understand organization hierarchies, spend policies, limits, entitlements, approval flows, and exception handling.                                                                                      | M02     | Core  | ☐    |
| C026 | Understand supplier payments, B2B payables, virtual-card use cases, cash-flow needs, and working-capital concepts at a business level.                                                                  | M02     | Core  | ☐    |
| C027 | Identify onboarding, billing, statements, transaction visibility, and customer-service touchpoints.                                                                                                     | M02     | Core  | ☐    |
| C028 | Identify where credit, fraud, risk, and finance teams affect a commercial payment journey.                                                                                                              | M02     | Core  | ☐    |
| C029 | Explain authorization, clearing, settlement, and reconciliation as distinct stages.                                                                                                                     | M05     | Core  | ☐    |
| C030 | Handle declines, timeouts, reversals, refunds, disputes, and chargeback-style exception workflows at a conceptual level.                                                                                | M05     | Core  | ☐    |
| C031 | Model payment state transitions, financial integrity, ledger/audit concepts, duplicate prevention, and discrepancy repair.                                                                              | M05     | Core  | ☐    |
| C032 | Map accounts payable (AP) from supplier invoice through validation, approval, payment instruction, and reconciliation; connect it to enterprise resource planning (ERP) at a conceptual level.          | M02     | Core  | ☐    |
| C033 | Distinguish virtual-card payments from non-card bank payment rails such as Automated Clearing House (ACH) and check, and identify differences in state, settlement, exceptions, and control boundaries. | M02     | Core  | ☐    |
| C034 | Discuss cross-border payments, currency conversion, cutoffs, and regional variation when relevant to a prompt.                                                                                          | M02     | Depth | ☐    |
| C035 | Study detailed network messages or product rules only if the actual interview scope calls for them.                                                                                                     | M05     | Depth | ☐    |
| C036 | Compare layered/multi-tier systems, service-oriented architecture (SOA), modular monoliths, microservices, and event-driven designs.                                                                    | M03     | Core  | ☐    |
| C037 | Derive service boundaries from capabilities, ownership, change patterns, and data boundaries.                                                                                                           | M03     | Core  | ☐    |
| C038 | Account for tenant isolation, organizational hierarchy, shared platform capabilities, and product-specific behavior.                                                                                    | M03     | Core  | ☐    |
| C039 | Explain sync versus async communication and where each belongs in a user journey.                                                                                                                       | M03     | Core  | ☐    |
| C040 | Explain partial failure, timeouts, bounded retries, retry storms, circuit breaking, and backpressure.                                                                                                   | M03     | Core  | ☐    |
| C041 | Design idempotency keys, deduplication, safe retry behavior, and concurrency control.                                                                                                                   | M03     | Core  | ☐    |
| C042 | Explain ordering guarantees, replay, eventual consistency, and the limits of “exactly once” claims.                                                                                                     | M03     | Core  | ☐    |
| C043 | Choose transaction boundaries and use compensation or saga-style workflows where appropriate.                                                                                                           | M03     | Core  | ☐    |
| C044 | Explain transactional outbox and change-data-capture concepts when a database change must produce an event.                                                                                             | M03     | Core  | ☐    |
| C045 | Evaluate Command Query Responsibility Segregation (CQRS) or event sourcing when a concrete requirement justifies the extra complexity.                                                                  | M03     | Depth | ☐    |
| C046 | Identify API consumers, ownership, developer experience, onboarding, documentation, and support model.                                                                                                  | M06     | Core  | ☐    |
| C047 | Design resources/operations, Hypertext Transfer Protocol (HTTP) behavior, pagination, filtering, errors, and idempotent requests.                                                                       | M06     | Core  | ☐    |
| C048 | Define contracts with OpenAPI and manage schemas, backward compatibility, versioning, deprecation, and consumer communication.                                                                          | M06     | Core  | ☐    |
| C049 | Select authentication and authorization mechanisms, scopes/claims, gateway policies, quotas, and rate limits.                                                                                           | M06     | Core  | ☐    |
| C050 | Use contract testing and consumer-driven feedback to prevent breaking changes.                                                                                                                          | M06     | Core  | ☐    |
| C051 | Compare request/response APIs, events, webhooks, file/batch exchange, and adapters for legacy or partner systems.                                                                                       | M06     | Core  | ☐    |
| C052 | Design event names, schemas, ownership, ordering assumptions, evolution rules, and retention/replay policy.                                                                                             | M06     | Core  | ☐    |
| C053 | Handle dead-letter queues, poison messages, duplicate delivery, delayed consumers, and recovery.                                                                                                        | M06     | Core  | ☐    |
| C054 | Define integration-level monitoring, partner dependencies, service expectations, and escalation paths.                                                                                                  | M06     | Core  | ☐    |
| C055 | Distinguish authentication (who/what you are) from authorization (what you may do); explain delegated access versus login and object-level access checks.                                               | M06     | Core  | ☐    |
| C056 | Introduce OAuth 2.0, OpenID Connect (OIDC), and mutual Transport Layer Security (mTLS); describe their purpose and appropriate use without assuming a required company implementation.                  | M06     | Core  | ☐    |
| C057 | Compare gRPC or GraphQL with REST only if the scenario makes the choice relevant.                                                                                                                       | M06     | Depth | ☐    |
| C058 | Define logical and physical data models for core entities and their relationships.                                                                                                                      | M04     | Core  | ☐    |
| C059 | Name the authoritative source, owner, update path, and consumer for each critical data item.                                                                                                            | M04     | Core  | ☐    |
| C060 | Distinguish operational data, events, caches, analytical stores, and reporting projections.                                                                                                             | M04     | Core  | ☐    |
| C061 | Plan schema evolution, reference/master data, and data contracts across teams.                                                                                                                          | M04     | Core  | ☐    |
| C062 | Define correctness, freshness, completeness, and reconciliation checks; detect and repair discrepancies.                                                                                                | M04     | Core  | ☐    |
| C063 | Design auditability, lineage, retention, deletion, privacy classification, and access controls.                                                                                                         | M04     | Core  | ☐    |
| C064 | Explain batch versus streaming trade-offs and the effect of delayed or missing events on reports.                                                                                                       | M04     | Core  | ☐    |
| C065 | Use partitioning, replication, indexing, or CDC details to resolve a demonstrated scale or integration need.                                                                                            | M04     | Depth | ☐    |
| C066 | Draw trust boundaries and trace sensitive data through each component and third party.                                                                                                                  | M07     | Core  | ☐    |
| C067 | Explain identity federation, authentication, service identity, least privilege, and role-based access control (RBAC) and attribute-based access control (ABAC).                                         | M07     | Core  | ☐    |
| C068 | Test object-level and function-level authorization, tenant isolation, and administrative entitlements.                                                                                                  | M07     | Core  | ☐    |
| C069 | Design secrets/key handling, encryption in transit and at rest, tokenization, and data minimization.                                                                                                    | M07     | Core  | ☐    |
| C070 | Threat-model API abuse, fraud-related misuse, sensitive business flows, and unsafe dependencies.                                                                                                        | M07     | Core  | ☐    |
| C071 | Understand payment-data environment boundaries and the need to verify current Payment Card Industry (PCI) requirements with official sources.                                                           | M07     | Core  | ☐    |
| C072 | Address privacy, audit evidence, third-party and software-supply-chain risk in the delivery process.                                                                                                    | M07     | Core  | ☐    |
| C073 | State residual risk, control owner, review evidence, and when to seek security or compliance specialists.                                                                                               | M07     | Core  | ☐    |
| C074 | Study jurisdiction-specific rules or deep cryptographic implementation only if the role or interview identifies them.                                                                                   | M07     | Depth | ☐    |
| C075 | Define user-journey service level indicators (SLIs), service level objectives (SLOs), error budgets, and alert thresholds.                                                                              | M08     | Core  | ☐    |
| C076 | Conduct failure-mode analysis and choose graceful degradation or safe failure behavior.                                                                                                                 | M08     | Core  | ☐    |
| C077 | Compare high-availability and failover options, including active/passive and active/active trade-offs.                                                                                                  | M08     | Core  | ☐    |
| C078 | Set recovery time objectives (RTO) and recovery point objectives (RPO), backup/restore strategy, disaster-recovery drills, and recovery evidence.                                                       | M08     | Core  | ☐    |
| C079 | Estimate peak demand, throughput, concurrency, storage growth, and latency budgets.                                                                                                                     | M08     | Core  | ☐    |
| C080 | Diagnose tail latency, network/database bottlenecks, hot partitions, cache behavior, and resource saturation.                                                                                           | M08     | Core  | ☐    |
| C081 | Apply load shedding, queueing/backpressure, scaling, and capacity tests when justified.                                                                                                                 | M08     | Core  | ☐    |
| C082 | Connect performance choices to cost drivers and operational complexity.                                                                                                                                 | M08     | Core  | ☐    |
| C083 | Instrument logs, metrics, traces, and business-journey telemetry; detect failures that infrastructure metrics miss.                                                                                     | M09     | Core  | ☐    |
| C084 | Design actionable alerts, runbooks, on-call ownership, incident communication, and post-incident learning.                                                                                              | M09     | Core  | ☐    |
| C085 | Analyze multi-region consistency or fault-injection testing when the design requires it.                                                                                                                | M09     | Depth | ☐    |
| C086 | Explain deployment topology, network zones, service-to-service communication, hybrid/on-premises dependencies, and blast radius.                                                                        | M10     | Core  | ☐    |
| C087 | Compare managed services, containers, and other runtime choices against team skill, control, cost, and reliability.                                                                                     | M10     | Core  | ☐    |
| C088 | Use infrastructure as code, configuration management, secrets, and environment promotion responsibly.                                                                                                   | M10     | Core  | ☐    |
| C089 | Define platform ownership, shared capabilities, support model, and operational boundaries.                                                                                                              | M10     | Core  | ☐    |
| C090 | Build hands-on depth in Python. Start with simple code, then add concurrency and failure handling.                                                                                                      | M10     | Core  | ☐    |
| C091 | Review code for correctness, concurrency, failure handling, security, readability, and observability.                                                                                                   | M10     | Core  | ☐    |
| C092 | Select unit, integration, contract, performance, security, and resilience tests for a change.                                                                                                           | M10     | Core  | ☐    |
| C093 | Explain continuous integration and continuous delivery (CI/CD) controls, dependency checks, release strategies, feature flags, rollback, and post-release verification.                                 | M10     | Core  | ☐    |
| C094 | Debug a production-style fault from symptoms through evidence, hypothesis, fix, and regression test.                                                                                                    | M10     | Core  | ☐    |
| C095 | Read and modify a production-style Python API handler, explain its input/output and dependency calls, and defend its error handling.                                                                    | M10     | Core  | ☐    |
| C096 | Demonstrate an evidence-based code review with tests for concurrency, timeout uncertainty, retry duplicates, authorization, and safe rollback.                                                          | M10     | Core  | ☐    |
| C097 | Prepare vendor-specific cloud services or algorithm drills only after the interview process or chosen technology discipline justifies them.                                                             | M10     | Depth | ☐    |
| C098 | Inventory legacy dependencies, consumers, data flows, and business risk before migration.                                                                                                               | M11     | Core  | ☐    |
| C099 | Use adapters, strangler-style migration, coexistence, and contract compatibility to reduce cutover risk.                                                                                                | M11     | Core  | ☐    |
| C100 | Plan data migration, parallel run, reconciliation, feature flags, rollback, decommissioning, and exit criteria.                                                                                         | M11     | Core  | ☐    |
| C101 | Align business, data, application, and technology architecture to platform blueprints and company roadmaps.                                                                                             | M11     | Core  | ☐    |
| C102 | Define architecture standards, review criteria, decision rights, exceptions/waivers, and evidence of adoption.                                                                                          | M11     | Core  | ☐    |
| C103 | Compare build/buy, technical-debt reduction, cost, business benefit, and delivery sequencing.                                                                                                           | M11     | Core  | ☐    |
| C104 | Produce an incremental roadmap with dependencies, milestones, owners, risks, and measurable outcomes.                                                                                                   | M11     | Core  | ☐    |
| C105 | Discuss portfolio-level economics or vendor negotiation after the core roadmap concepts are understood.                                                                                                 | M11     | Depth | ☐    |
| C106 | Influence product, business, security, data, operations, and engineering stakeholders without relying on title alone.                                                                                   | M11     | Core  | ☐    |
| C107 | Resolve disagreements using constraints, evidence, decision owners, and documented follow-through.                                                                                                      | M11     | Core  | ☐    |
| C108 | Run design/code reviews that improve quality without becoming a bottleneck.                                                                                                                             | M11     | Core  | ☐    |
| C109 | Mentor junior architects by developing their judgment and independence.                                                                                                                                 | M11     | Core  | ☐    |
| C110 | Explain architecture decisions to executives through customer impact, options, cost, risk, and a clear recommendation.                                                                                  | M11     | Core  | ☐    |
| C111 | Prepare truthful examples of decisions, incidents, modernization, disagreement, mentoring, and learning from a reversed decision.                                                                       | M11     | Core  | ☐    |
| C112 | Use AI for requirement analysis, design critique, API review, test ideas, and documentation with appropriate data controls.                                                                             | M11     | Core  | ☐    |
| C113 | Verify AI suggestions against requirements and primary evidence; record accepted, rejected, and uncertain findings.                                                                                     | M11     | Core  | ☐    |
| C114 | Address confidentiality, prompt-injection risk, provenance, human accountability, and quality/adoption measures.                                                                                        | M11     | Core  | ☐    |
| C115 | Defend an unfamiliar, timed architecture with changing constraints.                                                                                                                                     | M12     | Core  | ☐    |
| C116 | Deliver timed leadership, executive, code-review, and technical deep-dive answers; retest weak dimensions.                                                                                              | M12     | Core  | ☐    |
| C117 | Evaluate specific AI tools or formal frameworks only if the interviewer asks about them or they match your real work.                                                                                   | M11     | Depth | ☐    |
| C118 | Identify nodes, network boundaries, request paths, failure domains, and uncertain outcomes.                                                                                                             | M03     | Core  | ☐    |
| C119 | Allocate an end-to-end latency budget across network hops and synchronous call chains.                                                                                                                  | M03     | Core  | ☐    |
| C120 | Reason about availability and linearizable consistency during a network partition; avoid blanket CAP labels.                                                                                            | M03     | Core  | ☐    |
| C121 | Explain clock uncertainty, causal ordering, and why timestamps alone are insufficient for correctness.                                                                                                  | M03     | Core  | ☐    |
| C122 | Diagnose lost updates and concurrent retry races; compare optimistic and pessimistic control.                                                                                                           | M03     | Core  | ☐    |
| C123 | Use leases, distributed locks, and fencing tokens when stale owners can still act.                                                                                                                      | M03     | Depth | ☐    |
| C124 | Compare replica layouts and sync/async updates, lag, and recovery behavior.                                                                                                                             | M04     | Core  | ☐    |
| C125 | Specify strong/linearizable or eventual read/write semantics and allowed staleness.                                                                                                                     | M04     | Core  | ☐    |
| C126 | Discuss quorum, network partitions, and split-brain prevention for a particular model.                                                                                                                  | M04     | Core  | ☐    |
| C127 | Explain why leader election/consensus may be needed and what its guarantees cover.                                                                                                                      | M04     | Depth | ☐    |
| C128 | Select shard keys and detect skew and hot partitions.                                                                                                                                                   | M04     | Core  | ☐    |
| C129 | Evaluate cross-shard transactions, fan-out reads, IDs, and rebalance safety.                                                                                                                            | M04     | Core  | ☐    |
| C130 | Address cache staleness and invalidation when the scenario needs cached reads.                                                                                                                          | M04     | Depth | ☐    |
| C131 | Durable request identity, parameter consistency, concurrent deduplication, and retry safety.                                                                                                            | M05     | Core  | ☐    |
| C132 | Resolve external-action uncertainty through status checks, reconciliation, and escalation.                                                                                                              | M05     | Core  | ☐    |
| C133 | Trace broker partitions, consumer acknowledgment/offset behavior, retention, lag, and replay.                                                                                                           | M06     | Core  | ☐    |
| C134 | Design safe consumers with ordering assumptions, schema evolution, and deduplication.                                                                                                                   | M06     | Core  | ☐    |
| C135 | End-to-end deadlines, bounded backoff/jitter, retry budgets, and circuit breakers.                                                                                                                      | M08     | Core  | ☐    |
| C136 | Queue limits, bulkheads, backpressure, safe rejection, and overload recovery.                                                                                                                           | M08     | Core  | ☐    |
| C137 | Match failover topology to assumed recovery targets and validate recovery.                                                                                                                              | M09     | Core  | ☐    |
| C138 | Define a single authority for risky writes, split-brain prevention, and failback.                                                                                                                       | M09     | Core  | ☐    |
| C139 | Correlate request IDs, distributed traces, state changes, lag, and business impact.                                                                                                                     | M09     | Core  | ☐    |
| C140 | Safely test delays, duplicates, stuck consumers, and region loss with rollback controls.                                                                                                                | M09     | Core  | ☐    |
| C141 | Build and defend end-to-end distributed-system design under consistency, scale, and outage constraints.                                                                                                 | M12     | Core  | ☐    |

---

## Appendix B. Beginner articulation notebook and progress record

Do not use a senior scorecard for every beginner lesson. Save only a few lines:

```text
Lesson ID / Topic:
The example we used:
My explanation in my own words (1–3 sentences):
Technical idea I understood:
Technical idea still unclear:
Speaking help I needed (starter / outline / none):
One corrected sentence I can say aloud:
Next lesson or review:
```

### My 20-second practice pattern

1. “A **[term]** is **[plain definition]**.”
2. “We use it to **[purpose]**.”
3. “For example, **[familiar example]**.”

Only after this is comfortable, add a fourth line: “A problem to watch for is **[limitation/failure]**.”

**Example:** “A database is a system for storing and finding organized data. An application uses it to keep information
after the program stops. For example, a purchase app can store purchase records and look them up later.”

This is a practice explanation, not a complete treatment of databases. Accuracy matters more than sophisticated
vocabulary.

### Feedback format for the tutor

```text
UNDERSTANDING: Correct / Partly correct / Needs a different explanation
SPECIFIC FIX: [the one most important missing concept]
SPEAKING: [one simple rewrite of my idea, with short natural sentences]
TRY AGAIN: [one question about the topic already taught]
NEXT: [stay on this concept / continue to next micro-lesson]
```

---

## Appendix C. Senior scorecard, log, and advanced tutor commands

### Scorecard: copy after each drill or mock

```text
Date / Prompt / Scenario variant / Time used:
Known / assumed / unknown:
Business invariant:
Proposed design and simpler alternative:
Failure injected and observed consequence:
Evidence used:
Score (0–4 or N/A):
  Problem & business:
  Correctness & data:
  Design & trade-offs:
  Failure & recovery:
  Security & risk:
  Operations & delivery:
  Communication:
Blocking safety mistake (yes/no):
Most important error:
Corrected explanation in 60–90 seconds:
New variant to test:
Retest on (1/3/7/21 days):
```

### Useful tutor commands (beginner commands first)

```text
START L01         Begin from the first concept. Teach before asking any questions.
CONTINUE           Teach the next small concept in lesson order.
SAY IT             Help me explain the current concept in my own words.
SIMPLER            Use a smaller example and fewer new terms.
SPEAKING PRACTICE  Help me turn my rough sentence into clear interview English.
TEACH M05          Go to M05 only if earlier prerequisite concepts are secure.
BREAK THIS        Inject a new failure into my current design; don't solve it.
CODE REVIEW M10   Give me 30 lines of flawed Python and ask me to find the risks.
MOCK M12          Start a cold timed interview; no hints or feedback until the end.
GRADE             Score my committed answer, identify safety gaps, and force a retry.
RETRIEVE          Test a weak idea from prior sessions using a different case.
EXECUTIVE         Make me give a 90-second decision summary and challenge it.
PARK              Return to the current mission; list off-topic issues separately.
```

### How to adapt the guide as the interview becomes clearer

If an official recruiter message or job posting becomes available, extract **verifiable** role duties, interview stages,
technical stack expectations, coding depth, leadership signals, and dates. Map them to missions and adjust **effort**,
not correctness standards. If time is limited, target the weakest high-impact skills first: **unknown financial
outcomes, atomic deduplication, data authority, API/tenant security, recovery, decision trade-offs, and clear spoken
answers**.

**The success condition has two stages:** First I can explain familiar ideas clearly and accurately in my own words.
Later I can make safe, testable decisions in unfamiliar cases. Number of pages read and words recognized are not
evidence of either stage.
