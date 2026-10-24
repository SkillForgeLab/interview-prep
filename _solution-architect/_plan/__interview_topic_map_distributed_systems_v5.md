# Senior Solutions Architect I Interview — Distributed Systems First (Beginner to Senior)

**Interview depth target:** Practice judgment associated with an architect who has 20+ years of experience; this is a
preparation standard, not a verified minimum for the vacancy.  
**Starting point:** No prior topic knowledge is assumed.  
**Target role:** Sr Solutions Architect I, American Express Global Commercial Services (GCS).  
**Revision:** v4 — 2026-10-24. Distributed-systems-first revision of v3; all original coverage is retained.  
**Primary focus:** Distributed systems, correctness under failure, consistency, scaling, and senior system design.  
**Coverage:** 35 cards (25 retained + 10 DS cards). Checklist C001–C141 (C001–C117 retained + C118–C141 added).  
**Recommended effort split:** About **70%** distributed-system learning, design exercises, and fault analysis; **30%**
foundations, business context, security, payments, leadership, and interview communication. This is a study priority,
**not** a verified interview weighting.

## Learning rules

- **Distributed systems are the spine of the course.** Organize APIs, databases, payments, reliability,
  security, and cloud around decisions made by cooperating services under failure.
- Begin with basic software, networking, databases, and business requirements; move quickly to distributed system
  models.
- Do not equate distributed systems with microservices: a modular monolith may be the safer option for some workflows.
- Require students to state the failure boundary, consistency requirement, request identity, and recovery mechanism
  in every substantial design problem.

- Start from basics. Build toward senior interview depth through examples and trade-offs.
- Teach prerequisites before the concept that needs them.
- A trade-off is a choice that improves one quality but costs something else.
- Use a verified official job posting as role context when supplied. Do not assert a requirement from an unverified or
  unavailable posting.
- Verify company facts. Use hypothetical systems for practice.
- Use industry-standard designs and architecture, citing current primary references for claims about standards.
- An API, or application programming interface, is a contract for how software communicates.

The **syllabus describes the target role** as emphasizing APIs, integration, platform roadmaps, design reviews,
mentoring, and responsible AI-tool use; this wording is not a substitute for the verified job posting.
The syllabus also covers payments, data, security, reliability, and delivery.


## Communication and Teaching Guidelines

### 1. Language and Clarity

- Assume the learner is a non-native English speaker.
- Use direct, clear, and simple English.
- Write short sentences and short sections.
- Avoid unnecessary jargon, complex grammar, and filler.
- Explain difficult concepts in small, logical steps.
- Keep explanations technically accurate without making them unnecessarily complex.

### 2. Structure and Formatting

- Prefer bullet points, numbered steps, and small tables.
- Use focused diagrams when they improve understanding.
- Present one main idea at a time.
- Highlight important points without repeating information.
- Use headings that clearly describe the content.

### 3. Technical Terms and Accuracy

- Keep standard technical terms. Do not replace them with informal words.
- Define each technical term when it first appears in a new session.
- Expand each abbreviation on first use.
- Explain technical concepts in plain English without losing accuracy.
- Clearly separate facts, assumptions, and recommendations.

### 4. Step-by-Step Teaching Process

For each concept, follow this sequence:

**Step 1 — Purpose and Prerequisites**

- Explain what the concept is used for.
- Explain why it matters and when it is useful.
- Identify the knowledge or tools required before learning it.
- Briefly explain any missing prerequisite.

**Step 2 — Terms and Fundamentals**

- Define important terms in plain English.
- Explain the core idea before introducing advanced details.
- Connect new ideas to concepts already covered.

**Step 3 — Worked Example**

- Show a small, practical example.
- Choose the clearest format for the concept:
    - A focused ASCII diagram.
    - Python code for backend concepts.
    - Self-contained HTML with plain JavaScript for user interface concepts; do not require React or TSX files.
    - A small table or step-by-step walkthrough.
- Explain the example line by line or step by step when needed.
- Keep examples minimal, correct, and easy to reproduce.

**Step 4 — Guided Exercise**

- Provide a small exercise to apply the concept.
- State the goal and expected outcome.
- Give clear instructions without immediately revealing the full solution.
- Offer hints when needed.
- Review the learner's answer and explain mistakes constructively.

**Step 5 — Failure Cases and Trade-offs**

- Introduce these only after the fundamentals are clear.
- Show one realistic failure case, limitation, or common mistake.
- Explain why it happens.
- Explain how to identify, prevent, or fix it.
- Discuss trade-offs when multiple solutions are possible.

**Step 6 — Interview Phrasing**

- Include an **Interview Phrasing** section after each useful concept, question, or correction.
- Provide a short, polished, natural model answer.
- Use professional English and correct technical terms.
- Make the answer easy to memorize and speak confidently.
- Explain what the model answer means in plain English.
- Connect the answer to the concept and practical example.
- Avoid robotic, overly academic, or unnecessarily long responses.

### 5. Interview Preparation Standards

- Prioritize understanding before memorization.
- Teach the learner to explain both **how something works** and **why it is used**.
- Include practical reasoning instead of definitions alone.
- Use natural phrasing that an experienced professional would use in an interview.
- Keep interview answers concise but technically complete.
- Distinguish between a beginner-friendly explanation and a professional interview answer.

### 6. Learning Progression

Follow this sequence:

**Understand → Explain → Demonstrate → Practice → Evaluate → Memorize**

1. **Understand:** Learn the purpose, prerequisites, terminology, and fundamentals.
2. **Explain:** Understand how the concept works and why it matters.
3. **Demonstrate:** Study a small worked example with code or a diagram.
4. **Practice:** Complete a guided exercise.
5. **Evaluate:** Examine failures, limitations, mistakes, and trade-offs.
6. **Memorize:** Learn a concise, professional interview answer and understand its meaning.

### 7. Teaching Principles

- Build knowledge progressively, from basic to advanced.
- Do not assume understanding without evidence.
- Avoid introducing too many new concepts at once.
- Adjust explanation depth based on the learner's responses.
- Correct technical misunderstandings clearly and directly.
- Prefer practical understanding over memorized definitions.
- Do not force code, diagrams, exercises, or interview sections when they add no learning value.
- Keep the learner focused on one concept before moving to the next.

### 8. Binding learning-guide production contract

Produce **one series of short, cumulative lessons per card**, not a large one-shot explanation. Use the card's required
checklist crosswalk as the lesson inventory. No original checklist item may be silently skipped.

For **each checklist item**, teach and evaluate the following sequence:

1. **Purpose and prerequisites:** why it exists; teach the missing prerequisite first.
2. **Terms and fundamentals:** define each technical term and expand each abbreviation at first use.
3. **Worked example:** small example with a line-by-line or step-by-step walkthrough; use ASCII diagrams by default.
4. **Guided exercise:** clear goal, steps, expected result, and hints; review the learner's work.
5. **Failure and trade-off:** what can fail, how to detect/recover, and why an alternative may be better under a
   different constraint.
6. **Interview phrasing:** short spoken answer, plain-English explanation, and realistic follow-up question.

After the six steps, perform the **Senior decision test** written on that card. Ask the learner to state (a) the
business goal, (b) assumptions and missing facts, (c) at least two realistic options, (d) the decision and trade-off,
(e) failure/security/data implications when relevant, (f) evidence or experiment, and (g) accountable owners and
measurable outcomes. For foundational cards, keep the technical scale beginner-friendly but still require a reasoned
choice.

**Progression per lesson:** beginner explanation → applied example → senior decision challenge. The senior answer is
earned through reasoning, not memorizing terminology. Separate **Core** checklist items from **Depth** items. Teach all
Core items. Study Depth items when relevant to the scenario, interview evidence, or a demonstrated weakness; preserve
them in the guide for later use. Every checkbox is passed only if the learner can **explain**, **apply**, and **defend a
trade-off** without notes. A card passes when its Core items, practice task, and senior decision test pass; mark Depth
items separately.

### If the chat drifts

Paste: **“Return to this card. Teach only the next prerequisite or small concept. Put other issues in the parking
lot.”**

## Learning sequence and prerequisites

Follow the order below. Stages are prerequisite groups, not fixed weeks. The **DS** cards are the dominant learning
path.

| Stage | Cards, in learning order     | Purpose                                                                          |
|-------|------------------------------|----------------------------------------------------------------------------------|
| 1     | **B01 → B02 → B03**          | Basic Python, networks, HTTP, databases, SQL, and transactions                   |
| 2     | **F01 → F02 → T01**          | Requirements, diagrams, architecture styles, and service boundaries              |
| 3     | **DS01 → DS02 → T02 → DS05** | Distributed failure models, time, concurrency, idempotency, and transactions     |
| 4     | **DS03 → DS04 → T05**        | Replication, consistency, quorum decisions, partitioning, and data ownership     |
| 5     | **T03 → T04 → DS06**         | API contracts, events, message delivery, replay, and recovery                    |
| 6     | **DS07 → T07 → DS08**        | Resilience patterns, recovery objectives, failover, and multi-region correctness |
| 7     | **T08 → T09 → DS09**         | Performance, observability, incident response, and failure testing               |
| 8     | **D01 → D02 → T06**          | Apply the system to commercial payments, financial integrity, and security       |
| 9     | **T10 → T11 → E01**          | Deployment, code review, and safe modernization                                  |
| 10    | **E02 → L01 → A01 → L02**    | Governance, leadership, AI-assisted reviews, and interview communication         |
| 11    | **DS10 → X01 → X02**         | End-to-end distributed design and two evidence-based senior mock assessments     |

**Prerequisite rules:**

- Finish B01 before B02/B03. Finish B02 before T01/DS01; finish B03 before DS03/DS04/T05.
- T02 still introduces practical reliability and correctness patterns; DS02 and DS05 deepen these through failure
  timelines and implementable invariants. Complete T02 before DS05.
- Study DS03 before DS04. T03 requires T02, T04 requires T02 and T03, and DS06 requires T04.
- DS07 requires DS05 and DS06. T07 requires T02 and T04; DS08 requires DS03, DS07, and T07.
- T08 and T09 retain their original prerequisites. Study DS09 after T09 and DS08.
- D02 still requires D01, T02, and T05. T06 still requires T03 and T05.
- T11 remains advanced code-reading and review. E01 retains its original prerequisites.
- DS10 requires DS01–DS09 plus D02, T06, and T11. Do X01/X02 after DS10 and their original prerequisites.
- Keep cloud-neutral examples first. Never infer American Express implementation details from public products.

## Distributed-systems-first study contract

**Recommended study allocation (planning assumption):** Spend roughly seven of every ten study sessions on the
DS01–DS10 sequence or distributed-system deep dives within T01/T02/T04/T05/T07/T08/T09/T11. Spend the remaining
three on prerequisites, payments/security context, architectural governance, and interview communication. Adjust
only from demonstrated gaps or verified interview scope.

For every distributed-system lesson, answer these questions:

1. **Correctness:** What business or data invariant must never be broken?
2. **Boundaries:** Which service, datastore, message stream, and team owns each state transition?
3. **Failure:** What if a message is duplicated, delayed, lost, reordered, or its outcome is unknown?
4. **Consistency:** Which reads/writes must be fresh? Where is staleness acceptable?
5. **Scale:** Which partition, dependency, queue, or request path becomes the bottleneck?
6. **Recovery:** How can a second engineer detect, reconcile, and repair the fault?
7. **Decision:** What is the simpler alternative, what does it sacrifice, and what evidence supports the choice?

**Technical progression:** request/response across machines → time and concurrency → replication/consistency →
partitioning → idempotent workflows → event delivery → resilience → regional failure → observability → full system
design.

**Practice case (hypothetical):** The existing commercial spending platform remains the shared example. Model it
as cooperating policy, purchase, payment, and reporting capabilities, but do not assume this is any real company's
internal architecture. Use explicit assumptions and compare both a modular monolith and separated services.

```text
  Employee/Client
       |
       v
  Purchase API ---> Policy/Limit decision
       |                  |
       v                  v
  Durable request <--- State and audit record
       |
       +----> Payment adapter (may succeed before a timeout)
       |
       +----> Outbox / events ---> Reporting projection
                                (may be delayed or replayed)

  Review every arrow for: timeout, duplicate, ordering, access, owner, recovery.
```

**Evaluation and evidence:** At least 4/5 on every applicable rubric dimension in a senior decision test. Keep
one invariant/failure timeline, one architecture decision record, and one executable or precisely testable scenario
per DS card. Do not mark checklist items complete from reading alone; require explanation, application, and defense.

**Verified external references for this track (checked 2026-10-24):**

- [Microsoft — Saga distributed transactions](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga):
  local transactions and compensations; compensations themselves can fail.
- [Microsoft — Circuit breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker):
  stop repeated calls to a failing dependency.
- [Microsoft — Sharding](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding):
  partition-key choice and cross-shard complexity.
- [Google Cloud — Spanner and external consistency](https://docs.cloud.google.com/spanner/docs/true-time-external-consistency):
  example of a specifically documented, strong consistency model; not a universal database guarantee.
- [AWS — Transactional outbox](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/cloud-design-patterns/cloud-design-patterns.pdf):
  atomic local state/event intent and duplicate-tolerant consumers.

**Source status:** The focus and timing are **Recommendations**. Exercises and system sizing are **Hypothetical
practice assumptions**. Official links verify only the technical patterns they document. The precise role and
interview format remain **unverified**, as described in the v3 evidence rules.

## Detailed category-by-category coverage checklist

This is the preparation inventory behind the session cards. The card ID in parentheses tells you where to study an item.
Check an item only when you can **explain it, apply it to a scenario, and defend a trade-off** without reading notes.
The **98 original v2 checklist items are retained**. Additional v3 items fill prerequisite and role-relevant holes.
Study **Core** items first. Study **Depth** items when a concrete scenario, official interview scope, or a mock result
justifies them. The tutor must define the listed terms before teaching them. No fixed list can predict every interview
question.

**Coverage rule:** A card's **Required checklist coverage** subsection later in this file reproduces every checklist
item assigned to that card. Each becomes an explicit lesson or assessment unit; items assigned to multiple cards must be
applied in each card's context.

### 1. Technical foundations — new in v3

- [ ] Explain hardware, operating systems, programs, processes, memory, files, and how an application executes. (B01)
- [ ] Use Python variables, basic types, operators, conditions, loops, functions, and simple collections. (B01)
- [ ] Read code, trace inputs and outputs, catch errors, and distinguish a defect from an expected result. (B01)
- [ ] Write, run, and test a small Python function with normal, invalid, and boundary inputs. (B01)
- [ ] Explain client, server, browser, backend, process, network address, port, and request/response. (B02)
- [ ] Trace Domain Name System (DNS), Transmission Control Protocol (TCP), Transport Layer Security (TLS), and Hypertext
  Transfer Protocol (HTTP) at a beginner level. (B02)
- [ ] Understand HTTP verbs, response status, headers, JSON bodies, and network failure versus application error. (B02)
- [ ] Explain what an application programming interface (API) contract specifies. (B02)
- [ ] Distinguish relational databases, tables, records, columns, relationships, and data ownership. (B03)
- [ ] Design primary keys, foreign keys, and basic one-to-many relationships for a tiny business case. (B03)
- [ ] Write Structured Query Language (SQL) SELECT, WHERE, JOIN, INSERT, and UPDATE examples. (B03)
- [ ] Explain database transactions, atomicity, constraints, and what a partial update would break. (B03)
- [ ] Explain beginner-level indexes, safe queries, and basic data correctness checks. (B03)

### 2. Business analysis and architecture practice

- [ ] Identify customer types, user roles, business capabilities, and end-to-end journeys. (F01)
- [ ] Map stakeholders, decision owners, affected teams, and conflicting objectives. (F01)
- [ ] Elicit functional requirements, constraints, assumptions, and open questions. (F01)
- [ ] Write measurable quality-attribute scenarios for availability, latency, security, data freshness, and
  changeability; rank them by business impact. (F01)
- [ ] Define business key performance indicators (KPIs) and technical measures that show whether the solution worked.
  (F01)
- [ ] Produce context, component, data-flow, sequence, and deployment views for different audiences. (F02)
- [ ] Compare options using explicit criteria; write architecture decision records with consequences and revisit
  triggers. (F02)
- [ ] Trace requirements to design decisions, tests, risks, dependencies, and owners. (F02)
- [ ] **Depth:** Practice a formal architecture review and evaluate whether a design is ready to implement. (F02)

### 3. Commercial services and payments domain

- [ ] Explain corporate and small-business spending needs, including travel and expense, employee purchasing, and
  administrative controls. (D01)
- [ ] Model customer, administrator, employee, finance, supplier, and servicing journeys. (D01)
- [ ] Understand organization hierarchies, spend policies, limits, entitlements, approval flows, and exception handling.
  (D01)
- [ ] Understand supplier payments, B2B payables, virtual-card use cases, cash-flow needs, and working-capital concepts
  at a business level. (D01)
- [ ] Identify onboarding, billing, statements, transaction visibility, and customer-service touchpoints. (D01)
- [ ] Identify where credit, fraud, risk, and finance teams affect a commercial payment journey. (D01, D02)
- [ ] Explain authorization, clearing, settlement, and reconciliation as distinct stages. (D02)
- [ ] Handle declines, timeouts, reversals, refunds, disputes, and chargeback-style exception workflows at a conceptual
  level. (D02)
- [ ] Model payment state transitions, financial integrity, ledger/audit concepts, duplicate prevention, and discrepancy
  repair. (D02)
- [ ] Map accounts payable (AP) from supplier invoice through validation, approval, payment instruction, and
  reconciliation; connect it to enterprise resource planning (ERP) at a conceptual level. (D01)
- [ ] Distinguish virtual-card payments from non-card bank payment rails such as Automated Clearing House (ACH) and
  check, and identify differences in state, settlement, exceptions, and control boundaries. (D01, D02)
- [ ] **Depth:** Discuss cross-border payments, currency conversion, cutoffs, and regional variation when relevant to a
  prompt. (D01, D02)
- [ ] **Depth:** Study detailed network messages or product rules only if the actual interview scope calls for them.
  (D02)

### 4. Application architecture and distributed systems

- [ ] Compare layered/multi-tier systems, service-oriented architecture (SOA), modular monoliths, microservices, and
  event-driven designs. (T01)
- [ ] Derive service boundaries from capabilities, ownership, change patterns, and data boundaries. (T01)
- [ ] Account for tenant isolation, organizational hierarchy, shared platform capabilities, and product-specific
  behavior. (T01)
- [ ] Explain sync versus async communication and where each belongs in a user journey. (T02, T04)
- [ ] Explain partial failure, timeouts, bounded retries, retry storms, circuit breaking, and backpressure. (T02)
- [ ] Design idempotency keys, deduplication, safe retry behavior, and concurrency control. (T02)
- [ ] Explain ordering guarantees, replay, eventual consistency, and the limits of “exactly once” claims. (T02)
- [ ] Choose transaction boundaries and use compensation or saga-style workflows where appropriate. (T02)
- [ ] Explain transactional outbox and change-data-capture concepts when a database change must produce an event. (T02,
  T04)
- [ ] **Depth:** Evaluate Command Query Responsibility Segregation (CQRS) or event sourcing when a concrete requirement
  justifies the extra complexity. (T02, T05)

### 4A. Distributed systems — v4 additions and primary emphasis

The items below are **new**. Their required lesson crosswalk appears in the DS01–DS10 cards. Original C001–C117
requirements and all original 25 cards remain valid.

- [ ] **C118 · Core:** Identify nodes, network boundaries, request paths, failure domains, and why a distributed
  operation can have an uncertain outcome. (DS01)
- [ ] **C119 · Core:** Allocate an end-to-end latency budget across network hops and identify amplification through
  synchronous call chains. (DS01)
- [ ] **C120 · Core:** Explain the availability-versus-linearizable-consistency decision during a network partition;
  avoid blanket CAP labels. (DS01)
- [ ] **C121 · Core:** Explain clock uncertainty, causal ordering, and why wall-clock timestamps alone cannot establish
  safe distributed order. (DS02)
- [ ] **C122 · Core:** Detect lost updates, concurrent retries, write races, and compare optimistic versus pessimistic
  concurrency controls. (DS02)
- [ ] **C123 · Depth:** Explain leases, distributed locks, and fencing tokens when a stale owner could still act. (DS02)
- [ ] **C124 · Core:** Compare leader/follower, synchronous/asynchronous replication, replica lag, and failure recovery.
  (DS03)
- [ ] **C125 · Core:** Specify read and write guarantees, including strong/linearizable versus eventual consistency, and
  defend allowed staleness. (DS03)
- [ ] **C126 · Core:** Analyze quorum reads/writes, partitions, and split-brain prevention against a stated datastore
  model. (DS03)
- [ ] **C127 · Depth:** Describe leader election and consensus at conceptual level; do not claim universal guarantees
  for a vendor. (DS03)
- [ ] **C128 · Core:** Pick a stable partition/shard key; detect hot partitions, skew, and reassignment risk. (DS04)
- [ ] **C129 · Core:** Evaluate cross-partition transactions, fan-out queries, global identifiers, and online
  rebalancing. (DS04)
- [ ] **C130 · Depth:** Design cache invalidation and stale-read policy for a replicated or partitioned read path.
  (DS04)
- [ ] **C131 · Core:** Implement durable idempotency identity, request validation, concurrent deduplication, and safe
  retries. (DS05)
- [ ] **C132 · Core:** Resolve uncertain external financial actions with state queries, reconciliation, and explicit
  escalation. (DS05)
- [ ] **C133 · Core:** Trace message delivery, offsets/acknowledgments, broker partitions, backlog growth, and safe
  replay. (DS06)
- [ ] **C134 · Core:** Specify event schema evolution, ordering scope, duplicate-tolerant consumers, and dead-letter
  recovery. (DS06)
- [ ] **C135 · Core:** Design timeouts, propagated deadlines, retry budgets/backoff/jitter, and circuit breakers for a
  call chain. (DS07)
- [ ] **C136 · Core:** Select queue limits, backpressure, bulkheads, load shedding, and fail-safe behavior during
  overload. (DS07)
- [ ] **C137 · Core:** Compare active/passive and active/active regional recovery using stated RTO, RPO, and recovery
  tests. (DS08)
- [ ] **C138 · Core:** Prevent conflicting writes and split brain during failover; define data authority and
  return-to-primary rules. (DS08)
- [ ] **C139 · Core:** Correlate logs, traces, state transitions, consumer lag, and business signals to find distributed
  failures. (DS09)
- [ ] **C140 · Core:** Test selected failures safely, including delayed replies, event duplicates, stalled consumers,
  and region loss. (DS09)
- [ ] **C141 · Core:** Produce and defend an end-to-end distributed-system design under changing consistency,
  throughput, and outage constraints. (DS10)

### 5. API strategy and cross-platform integration

- [ ] Identify API consumers, ownership, developer experience, onboarding, documentation, and support model. (T03)
- [ ] Design resources/operations, Hypertext Transfer Protocol (HTTP) behavior, pagination, filtering, errors, and
  idempotent requests. (T03)
- [ ] Define contracts with OpenAPI and manage schemas, backward compatibility, versioning, deprecation, and consumer
  communication. (T03)
- [ ] Select authentication and authorization mechanisms, scopes/claims, gateway policies, quotas, and rate limits.
  (T03, T06)
- [ ] Use contract testing and consumer-driven feedback to prevent breaking changes. (T03, T11)
- [ ] Compare request/response APIs, events, webhooks, file/batch exchange, and adapters for legacy or partner systems.
  (T04)
- [ ] Design event names, schemas, ownership, ordering assumptions, evolution rules, and retention/replay policy. (T04)
- [ ] Handle dead-letter queues, poison messages, duplicate delivery, delayed consumers, and recovery. (T04)
- [ ] Define integration-level monitoring, partner dependencies, service expectations, and escalation paths. (T04, T09)
- [ ] Distinguish authentication (who/what you are) from authorization (what you may do); explain delegated access
  versus login and object-level access checks. (T03, T06)
- [ ] Introduce OAuth 2.0, OpenID Connect (OIDC), and mutual Transport Layer Security (mTLS); describe their purpose and
  appropriate use without assuming a required company implementation. (T03, T06)
- [ ] **Depth:** Compare gRPC or GraphQL with REST only if the scenario makes the choice relevant. (T03)

### 6. Data architecture and information governance

- [ ] Define logical and physical data models for core entities and their relationships. (T05)
- [ ] Name the authoritative source, owner, update path, and consumer for each critical data item. (T05)
- [ ] Distinguish operational data, events, caches, analytical stores, and reporting projections. (T05)
- [ ] Plan schema evolution, reference/master data, and data contracts across teams. (T05)
- [ ] Define correctness, freshness, completeness, and reconciliation checks; detect and repair discrepancies. (T05,
  D02)
- [ ] Design auditability, lineage, retention, deletion, privacy classification, and access controls. (T05, T06)
- [ ] Explain batch versus streaming trade-offs and the effect of delayed or missing events on reports. (T05)
- [ ] **Depth:** Use partitioning, replication, indexing, or CDC details to resolve a demonstrated scale or integration
  need. (T05, T08)

### 7. Security, privacy, and risk

- [ ] Draw trust boundaries and trace sensitive data through each component and third party. (T06)
- [ ] Explain identity federation, authentication, service identity, least privilege, and role-based access control
  (RBAC) and attribute-based access control (ABAC). (T06)
- [ ] Test object-level and function-level authorization, tenant isolation, and administrative entitlements. (T06)
- [ ] Design secrets/key handling, encryption in transit and at rest, tokenization, and data minimization. (T06)
- [ ] Threat-model API abuse, fraud-related misuse, sensitive business flows, and unsafe dependencies. (T06)
- [ ] Understand payment-data environment boundaries and the need to verify current Payment Card Industry (PCI)
  requirements with official sources. (T06)
- [ ] Address privacy, audit evidence, third-party and software-supply-chain risk in the delivery process. (T06, T11)
- [ ] State residual risk, control owner, review evidence, and when to seek security or compliance specialists. (T06)
- [ ] **Depth:** Study jurisdiction-specific rules or deep cryptographic implementation only if the role or interview
  identifies them. (T06)

### 8. Reliability, performance, and 24/7 operations

- [ ] Define user-journey service level indicators (SLIs), service level objectives (SLOs), error budgets, and alert
  thresholds. (T07)
- [ ] Conduct failure-mode analysis and choose graceful degradation or safe failure behavior. (T07)
- [ ] Compare high-availability and failover options, including active/passive and active/active trade-offs. (T07)
- [ ] Set recovery time objectives (RTO) and recovery point objectives (RPO), backup/restore strategy, disaster-recovery
  drills, and recovery evidence. (T07)
- [ ] Estimate peak demand, throughput, concurrency, storage growth, and latency budgets. (T08)
- [ ] Diagnose tail latency, network/database bottlenecks, hot partitions, cache behavior, and resource saturation.
  (T08)
- [ ] Apply load shedding, queueing/backpressure, scaling, and capacity tests when justified. (T08)
- [ ] Connect performance choices to cost drivers and operational complexity. (T08)
- [ ] Instrument logs, metrics, traces, and business-journey telemetry; detect failures that infrastructure metrics
  miss. (T09)
- [ ] Design actionable alerts, runbooks, on-call ownership, incident communication, and post-incident learning. (T09)
- [ ] **Depth:** Analyze multi-region consistency or fault-injection testing when the design requires it. (T07, T09)

### 9. Cloud, infrastructure, and engineering delivery

- [ ] Explain deployment topology, network zones, service-to-service communication, hybrid/on-premises dependencies, and
  blast radius. (T10)
- [ ] Compare managed services, containers, and other runtime choices against team skill, control, cost, and
  reliability. (T10)
- [ ] Use infrastructure as code, configuration management, secrets, and environment promotion responsibly. (T10)
- [ ] Define platform ownership, shared capabilities, support model, and operational boundaries. (T10)
- [ ] Build hands-on depth in Python. Start with simple code, then add concurrency and failure handling. (T11)
- [ ] Review code for correctness, concurrency, failure handling, security, readability, and observability. (T11)
- [ ] Select unit, integration, contract, performance, security, and resilience tests for a change. (T11)
- [ ] Explain continuous integration and continuous delivery (CI/CD) controls, dependency checks, release strategies,
  feature flags, rollback, and post-release verification. (T11)
- [ ] Debug a production-style fault from symptoms through evidence, hypothesis, fix, and regression test. (T11)
- [ ] Read and modify a production-style Python API handler, explain its input/output and dependency calls, and defend
  its error handling. (T11)
- [ ] Demonstrate an evidence-based code review with tests for concurrency, timeout uncertainty, retry duplicates,
  authorization, and safe rollback. (T11)
- [ ] **Depth:** Prepare vendor-specific cloud services or algorithm drills only after the interview process or chosen
  technology discipline justifies them. (T10, T11)

### 10. Modernization, enterprise governance, and roadmap

- [ ] Inventory legacy dependencies, consumers, data flows, and business risk before migration. (E01)
- [ ] Use adapters, strangler-style migration, coexistence, and contract compatibility to reduce cutover risk. (E01)
- [ ] Plan data migration, parallel run, reconciliation, feature flags, rollback, decommissioning, and exit criteria.
  (E01)
- [ ] Align business, data, application, and technology architecture to platform blueprints and company roadmaps. (E02)
- [ ] Define architecture standards, review criteria, decision rights, exceptions/waivers, and evidence of adoption.
  (E02)
- [ ] Compare build/buy, technical-debt reduction, cost, business benefit, and delivery sequencing. (E02)
- [ ] Produce an incremental roadmap with dependencies, milestones, owners, risks, and measurable outcomes. (E02)
- [ ] **Depth:** Discuss portfolio-level economics or vendor negotiation after the core roadmap concepts are understood.
  (E02)

### 11. Leadership, AI-assisted architecture, and interview execution

- [ ] Influence product, business, security, data, operations, and engineering stakeholders without relying on title
  alone. (L01)
- [ ] Resolve disagreements using constraints, evidence, decision owners, and documented follow-through. (L01)
- [ ] Run design/code reviews that improve quality without becoming a bottleneck. (L01, E02)
- [ ] Mentor junior architects by developing their judgment and independence. (L01)
- [ ] Explain architecture decisions to executives through customer impact, options, cost, risk, and a clear
  recommendation. (L02)
- [ ] Prepare truthful examples of decisions, incidents, modernization, disagreement, mentoring, and learning from a
  reversed decision. (L02)
- [ ] Use AI for requirement analysis, design critique, API review, test ideas, and documentation with appropriate data
  controls. (A01)
- [ ] Verify AI suggestions against requirements and primary evidence; record accepted, rejected, and uncertain
  findings. (A01)
- [ ] Address confidentiality, prompt-injection risk, provenance, human accountability, and quality/adoption measures.
  (A01)
- [ ] Deliver an unfamiliar timed system design and defend it under changing constraints. (X01)
- [ ] Deliver timed leadership, executive, code-review, and technical deep-dive answers; retest weak dimensions. (X02)
- [ ] **Depth:** Evaluate specific AI tools or formal frameworks only if the interviewer asks about them or they match
  your real work. (A01)

## Running practice case

Use this as a **hypothetical** recurring exercise: A commercial platform lets business administrators define spending
controls, employees initiate purchases, and finance teams view transactions and reconcile records. The solution
integrates with identity, risk, payment, and reporting capabilities and needs continuous service.

The tutor should teach the case in small steps. State every practice assumption. Explain new terms before using them.
Reuse this case to see how design decisions connect, then use unfamiliar prompts in X01 and X02.

### B01 — Software, Python, and programming basics

**Prerequisites:** None. Assume the learner has never written code or studied computer systems.

**Prepare:**

- Hardware, operating system, program, running process, memory, and file.
- Python interpreter, source code, input/output, variables, simple data types, and expressions.
- Conditions, loops, functions, lists/dictionaries, exceptions, and simple debugging.
- Running a script and a few tests; expected results versus bugs.

**Required checklist coverage (binding crosswalk):**

- **C001 · Core:** Explain hardware, operating systems, programs, processes, memory, files, and how an application
  executes.
- **C002 · Core:** Use Python variables, basic types, operators, conditions, loops, functions, and simple collections.
- **C003 · Core:** Read code, trace inputs and outputs, catch errors, and distinguish a defect from an expected result.
- **C004 · Core:** Write, run, and test a small Python function with normal, invalid, and boundary inputs.

**Practice:** Write a tiny Python function that receives an amount and a spending limit and returns an allowed/declined
result. Test a normal request, an invalid amount, and the exact boundary. Explain the logic line by line.

**Pass:** I can run and explain simple code, modify it safely, and demonstrate tests. I can say what a process,
function, input, output, and error are without memorized jargon.

**Interview challenge:** “A spending rule must reject a purchase above a limit. How would you explain and test the
decision logic?”

**Interview phrasing**

> “I would express the business rule as a small, testable function. I would test normal, invalid, and boundary inputs
> before placing it in a larger service.”

**Keep outside this session:** Distributed concurrency, production frameworks, and performance tuning. **Primary
reference:** [Python tutorial](https://docs.python.org/3/tutorial/).

**Senior decision test:** A business rule is implemented in one Python function or copied into three callers. Compare
clarity, change risk, and tests; choose one, and describe evidence that the rule works.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### B02 — Web and network basics

**Prepare:**

- A client, server, process, network address, and port.
- A request and response.
- DNS, TCP, and TLS at a basic level. Expand and define each term.
- HTTP methods, status codes, headers, and message bodies.
- JSON as a data format.
- An API as a communication contract.

**Required checklist coverage (binding crosswalk):**

- **C005 · Core:** Explain client, server, browser, backend, process, network address, port, and request/response.
- **C006 · Core:** Trace Domain Name System (DNS), Transmission Control Protocol (TCP), Transport Layer Security (TLS),
  and Hypertext Transfer Protocol (HTTP) at a beginner level.
- **C007 · Core:** Understand HTTP verbs, response status, headers, JSON bodies, and network failure versus application
  error.
- **C008 · Core:** Explain what an application programming interface (API) contract specifies.

**Practice:** Draw one request from a browser to Python. Label the address, request, processing step, and response.

**Pass:** I must be able to explain how a screen gets data from a backend. I must be able to distinguish a network error
from an application response.

**Interview phrasing**

> “The user interface sends a request to the backend. The backend checks the input and returns a response. I would
> define the expected success and error responses clearly.”

**Senior decision test:** An API caller sees a timeout but the backend might have processed the request. Contrast
blindly retrying with checking the request state, and explain how you would distinguish a network error from a server
rejection.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### B03 — Database and SQL fundamentals

**Prerequisites:** B01 and B02. Explain persistent storage before database terminology.

**Prepare:**

- A database, relational table, record, column, key, and relationship.
- Primary and foreign keys; one-to-many relationships; basic data ownership.
- SQL SELECT, WHERE, JOIN, INSERT, UPDATE, and simple queries with parameters.
- Transactions, atomicity, consistency constraints, indexes, and basic data-quality checks.

**Required checklist coverage (binding crosswalk):**

- **C009 · Core:** Distinguish relational databases, tables, records, columns, relationships, and data ownership.
- **C010 · Core:** Design primary keys, foreign keys, and basic one-to-many relationships for a tiny business case.
- **C011 · Core:** Write Structured Query Language (SQL) SELECT, WHERE, JOIN, INSERT, and UPDATE examples.
- **C012 · Core:** Explain database transactions, atomicity, constraints, and what a partial update would break.
- **C013 · Core:** Explain beginner-level indexes, safe queries, and basic data correctness checks.

**Practice:** Define small `business`, `spend_policy`, and `purchase` tables. Add sample rows. Query purchases for one
business using a JOIN. Show how to update a policy in a transaction and what must happen if an operation fails.

**Pass:** I can explain table relationships, write a small SQL query, and identify how a partial update could leave
records inconsistent. I distinguish an index from a uniqueness rule.

**Interview challenge:** “Should a business administrator be allowed to update a spending limit without an auditable
history?”

**Interview phrasing**

> “I would give each record a clear key and owner. I would use a transaction to keep related updates consistent and
> preserve an appropriate history for financially sensitive changes.”

**Keep outside this session:** Distributed database replication, event sourcing, and large-scale partitioning; these
come later. **Primary references:** [SQLite SQL language](https://www.sqlite.org/lang.html)
and [Python sqlite3](https://docs.python.org/3/library/sqlite3.html).

**Senior decision test:** A policy edit and audit-history write need to succeed together. Compare separate writes with
one database transaction and explain the recovery path if the second write fails.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### F01 — Business framing, requirements, and quality attributes

**Distributed-systems lens (v4):** Phrase business goals as latency, correctness, freshness, recovery, and security
requirements for a distributed design.

**Prerequisites:** Start with plain business examples.

**Prepare:**

- Users, business capabilities, and customer journeys.
- Requirements, constraints, assumptions, and open questions.
- Measurable business outcomes.
- Quality attributes such as availability, latency, and security.

**Required checklist coverage (binding crosswalk):**

- **C014 · Core:** Identify customer types, user roles, business capabilities, and end-to-end journeys.
- **C015 · Core:** Map stakeholders, decision owners, affected teams, and conflicting objectives.
- **C016 · Core:** Elicit functional requirements, constraints, assumptions, and open questions.
- **C017 · Core:** Write measurable quality-attribute scenarios for availability, latency, security, data freshness, and
  changeability; rank them by business impact.
- **C018 · Core:** Define business key performance indicators (KPIs) and technical measures that show whether the
  solution worked.

**Practice:** For the running case, write a one-page problem brief. Ask ten clarifying questions, then rank the top
three quality attributes and explain the business reason for each.

**Pass:** I must be able to start an ambiguous design question by discovering the problem before selecting technology.
I must be able to state what is known, assumed, and still open.

**Interview challenge:** “The business wants real-time transaction visibility. What does real-time mean to each user,
and how would you measure success?”

**Interview phrasing**

> “I would first identify the users and the business outcome. Then I would turn ‘real time’ into a measurable target. I
> would confirm which trade-offs the business can accept.”

**Keep outside this session:** Detailed component design.

**Senior decision test:** Finance says “real time,” engineering proposes a five-minute delay, and risk wants stronger
checks. Define measurable alternatives and who approves the business trade-off.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### F02 — Architecture method, views, and decision records

**Distributed-systems lens (v4):** Always show data authority, synchronous/async paths, failover regions, and how faults
propagate.

**Prerequisites:** F01.

**Prepare:**

- Architecture views and their purpose.
- Context, component, sequence, data-flow, and deployment diagrams.
- Comparing options and writing decision records.
- Linking requirements to decisions, risks, and tests.

**Required checklist coverage (binding crosswalk):**

- **C019 · Core:** Produce context, component, data-flow, sequence, and deployment views for different audiences.
- **C020 · Core:** Compare options using explicit criteria; write architecture decision records with consequences and
  revisit triggers.
- **C021 · Core:** Trace requirements to design decisions, tests, risks, dependencies, and owners.
- **C022 · Depth:** Practice a formal architecture review and evaluate whether a design is ready to implement.

**Practice:** Create a context diagram, a transaction sequence diagram, and one decision record comparing two plausible
choices for the running case. Give a ten-minute verbal walkthrough.

**Pass:** Every diagram has an audience and answers a question. The decision record states the decision, alternatives,
consequences, and a condition that would cause reconsideration.

**Interview challenge:** “Your diagram looks clean, but where are data ownership, failure handling, and deployment
boundaries?”

**Interview phrasing**

> “I would use a context diagram to show system boundaries. A sequence diagram would show the transaction steps. I would
> record the decision, its alternatives, and when we should review it.”

**Keep outside this session:** Exhaustive notation or diagramming tools.

**Senior decision test:** A proposed design looks simple but omits an owner for transaction state. Choose the smallest
additional architecture views and tests needed for a design-review decision.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### D01 — Commercial services and business workflows

**Prerequisites:** F01.

**Prepare:**

- Business customer types and user roles.
- Commercial spending, travel and expense, employee purchasing, and supplier payments.
- Organization hierarchy, spend controls, approvals, credit/risk checks, and exception journeys.
- Accounts payable (AP): supplier onboarding, invoice capture/validation, invoice approval, payment instruction, payment
  status, and finance reconciliation.
- Enterprise resource planning (ERP) and accounting integration: supplier records, invoice identifiers, payment
  references, reconciliation files/events, and system-of-record boundaries.
- Compare virtual-card transactions with non-card Automated Clearing House (ACH) and check payments at a **business**
  level; do not assume they share payment-network state machines.
- Servicing, billing, statements, working capital, cash-flow needs, and risk touchpoints.

**Required checklist coverage (binding crosswalk):**

- **C023 · Core:** Explain corporate and small-business spending needs, including travel and expense, employee
  purchasing, and administrative controls.
- **C024 · Core:** Model customer, administrator, employee, finance, supplier, and servicing journeys.
- **C025 · Core:** Understand organization hierarchies, spend policies, limits, entitlements, approval flows, and
  exception handling.
- **C026 · Core:** Understand supplier payments, B2B payables, virtual-card use cases, cash-flow needs, and
  working-capital concepts at a business level.
- **C027 · Core:** Identify onboarding, billing, statements, transaction visibility, and customer-service touchpoints.
- **C028 · Core:** Identify where credit, fraud, risk, and finance teams affect a commercial payment journey.
- **C032 · Core:** Map accounts payable (AP) from supplier invoice through validation, approval, payment instruction,
  and reconciliation; connect it to enterprise resource planning (ERP) at a conceptual level.
- **C033 · Core:** Distinguish virtual-card payments from non-card bank payment rails such as Automated Clearing House
  (ACH) and check, and identify differences in state, settlement, exceptions, and control boundaries.
- **C034 · Depth:** Discuss cross-border payments, currency conversion, cutoffs, and regional variation when relevant to
  a prompt.

**Practice:** Build a capability map and three customer journeys: (1) employee purchase with policy controls, (2)
supplier invoice through AP approval and payment instruction, and (3) finance reconciliation. Show the ERP/accounting
boundary and compare a virtual-card versus an ACH/check path. Mark product, risk, finance, and operations stakeholders'
different outcomes. All products and rules are hypothetical except explicitly cited public examples.

**Pass:** I must be able to translate a business workflow into technical requirements and explain why a small-business
use case may differ from a large-enterprise one.

**Interview challenge:** “Which capabilities should be shared platform services, and which should remain
product-specific?”

**Interview phrasing**

> “I would map the administrator, employee, and finance journeys first. Then I would identify common capabilities, such
> as spending controls. I would keep customer rules configurable where business needs differ.”

**Keep outside this session:** Payment-network message specifications. **Primary public business
reference:** [American Express One AP](https://www.americanexpress.com/en-us/business/one-ap/); use its documented
capabilities as domain examples only.

**Senior decision test:** A customer needs both virtual-card supplier payments and ACH invoice payments. Decide which
capabilities are shared versus rail-specific, and defend the boundaries with business, risk, and reconciliation
concerns.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T01 — Service boundaries and architecture styles

**Distributed-systems lens (v4):** Use service boundaries to compare a modular monolith with separate services. Mark new
network failure boundaries.

**Prerequisites:** F02.

**Prepare:**

- Business boundaries and data ownership.
- Layered systems and service-oriented architecture.
- Modular monoliths and microservices.
- Shared platform capabilities and build-versus-buy decisions.

**Required checklist coverage (binding crosswalk):**

- **C036 · Core:** Compare layered/multi-tier systems, service-oriented architecture (SOA), modular monoliths,
  microservices, and event-driven designs.
- **C037 · Core:** Derive service boundaries from capabilities, ownership, change patterns, and data boundaries.
- **C038 · Core:** Account for tenant isolation, organizational hierarchy, shared platform capabilities, and
  product-specific behavior.

**Practice:** Decompose the running case in two ways. Compare team ownership, data ownership, change frequency, latency,
operational overhead, and migration difficulty.

**Pass:** I must be able to justify a boundary by business capability and change patterns, not by a technology slogan. I
must be able to identify the cost of too many services.

**Interview challenge:** “Why is your proposed policy service separate from transaction processing?”

**Interview phrasing**

> “I would define boundaries around business responsibilities and data ownership. I would separate a service when
> independent change provides a clear benefit. I would also account for the extra coordination and failure handling.”

**Keep outside this session:** Detailed event delivery semantics; that is T04.

**Senior decision test:** Two teams propose a single service versus separate spending-policy and transaction services.
Pick a boundary based on ownership and change patterns, and say when you would reverse the choice.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T02 — Distributed-system correctness and failure semantics

**Distributed-systems lens (v4):** Use DS01/DS02 as models and DS05 as the deeper correctness test; retain all original
C039–C045 lessons.

**Prerequisites:** T01.

**Prepare:**

- Partial failure, timeouts, and retries.
- Idempotency, duplicates, concurrency, and ordering.
- Consistency and transaction boundaries.
- Compensation, failure isolation, and backpressure.

**Required checklist coverage (binding crosswalk):**

- **C039 · Core:** Explain sync versus async communication and where each belongs in a user journey.
- **C040 · Core:** Explain partial failure, timeouts, bounded retries, retry storms, circuit breaking, and backpressure.
- **C041 · Core:** Design idempotency keys, deduplication, safe retry behavior, and concurrency control.
- **C042 · Core:** Explain ordering guarantees, replay, eventual consistency, and the limits of “exactly once” claims.
- **C043 · Core:** Choose transaction boundaries and use compensation or saga-style workflows where appropriate.
- **C044 · Core:** Explain transactional outbox and change-data-capture concepts when a database change must produce an
  event.
- **C045 · Depth:** Evaluate Command Query Responsibility Segregation (CQRS) or event sourcing when a concrete
  requirement justifies the extra complexity.

**Practice:** Trace a purchase request that times out after the downstream action succeeds. Then trace a duplicated and
out-of-order event. Specify state transitions, identifiers, retry rules, and a repair path.

**Pass:** I must be able to explain what the customer sees, what the system knows, what it does not know, and how it
reaches a correct state. You do not claim “exactly once” without defining the boundary and mechanism.

**Interview challenge:** “If the caller retries, how do you prevent a duplicate financial action?”

**Interview phrasing**

> “A timeout leaves the result uncertain. I would use a durable request identifier and confirm how each system handles
> retries. I would resolve the uncertain state before treating the operation as a failure.”

**Keep outside this session:** Vendor-specific broker configuration.

**Senior decision test:** A purchase times out after an external financial action succeeds. Compare retry,
query-before-retry, and manual reconciliation; define idempotency scope and the uncertain state.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T03 — API product and contract strategy

**Distributed-systems lens (v4):** Treat API retry semantics, error states, and authorization as distributed contracts,
not just endpoint syntax.

**Prerequisites:** T02.

**Prepare:**

- API consumers and contracts.
- Resources, operations, errors, and pagination.
- Authentication (identity verification) versus authorization (permission); consumer, user, and workload identity.
- OAuth 2.0 (delegated authorization), OpenID Connect (authentication layer), and mutual TLS (certificate-based client
  authentication), compared by purpose; introduce credentials, scopes, claims, token validation, and per-object checks.
- Access rules, retries, rate limits, gateways, and API abuse resistance.
- OpenAPI contracts, schema changes, backward compatibility, versioning, deprecation, consumer tests, and API ownership.

**Required checklist coverage (binding crosswalk):**

- **C046 · Core:** Identify API consumers, ownership, developer experience, onboarding, documentation, and support
  model.
- **C047 · Core:** Design resources/operations, Hypertext Transfer Protocol (HTTP) behavior, pagination, filtering,
  errors, and idempotent requests.
- **C048 · Core:** Define contracts with OpenAPI and manage schemas, backward compatibility, versioning, deprecation,
  and consumer communication.
- **C049 · Core:** Select authentication and authorization mechanisms, scopes/claims, gateway policies, quotas, and rate
  limits.
- **C050 · Core:** Use contract testing and consumer-driven feedback to prevent breaking changes.
- **C055 · Core:** Distinguish authentication (who/what you are) from authorization (what you may do); explain delegated
  access versus login and object-level access checks.
- **C056 · Core:** Introduce OAuth 2.0, OpenID Connect (OIDC), and mutual Transport Layer Security (mTLS); describe
  their purpose and appropriate use without assuming a required company implementation.
- **C057 · Depth:** Compare gRPC or GraphQL with REST only if the scenario makes the choice relevant.

**Practice:** Define a small API for spending policies and transaction status. Include an example request/response,
error model, authorization rule, idempotency behavior, and a backward-compatible change plan.

**Pass:** A consumer could implement against your contract and understand what happens on retries, errors, and version
changes.

**Interview challenge:** “How would you evolve this API when a major corporate customer needs a new policy field?”

**Interview phrasing**

> “I would define the API contract around the consumer's workflow. The contract would explain errors, retries, and
> access rules. I would check compatibility before introducing a change.”

**Keep outside this session:** Internal Amex API standards; do not assume them.  
**Primary
references:** [OpenAPI Specification](https://spec.openapis.org/oas/), [OAuth 2.0 RFC 6749](https://www.rfc-editor.org/rfc/rfc6749), [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html),
and [OAuth mTLS RFC 8705](https://www.rfc-editor.org/rfc/rfc8705).

**Senior decision test:** A large customer requests a new field and stronger authentication. Propose a
backward-compatible API evolution and justify OAuth/OIDC/mTLS selection by security objective rather than popularity.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T04 — Cross-platform integration and event architecture

**Distributed-systems lens (v4):** Use DS06 to test actual delivery, replay, and consumer correctness, not just event
diagrams.

**Prerequisites:** T02 and T03.

**Prepare:**

- Synchronous and asynchronous communication.
- Messages, events, and event contracts.
- Replay, dead-letter handling, and recovery.
- Partner adapters, legacy integration, and workflow coordination.

**Required checklist coverage (binding crosswalk):**

- **C039 · Core:** Explain sync versus async communication and where each belongs in a user journey.
- **C044 · Core:** Explain transactional outbox and change-data-capture concepts when a database change must produce an
  event.
- **C051 · Core:** Compare request/response APIs, events, webhooks, file/batch exchange, and adapters for legacy or
  partner systems.
- **C052 · Core:** Design event names, schemas, ownership, ordering assumptions, evolution rules, and retention/replay
  policy.
- **C053 · Core:** Handle dead-letter queues, poison messages, duplicate delivery, delayed consumers, and recovery.
- **C054 · Core:** Define integration-level monitoring, partner dependencies, service expectations, and escalation
  paths.

**Practice:** Draw purchase-to-reporting flows for both normal operation and a downstream outage. Compare an API-led and
event-led solution. Define delivery and ordering assumptions explicitly.

**Pass:** I must be able to show how a missing or duplicate message is detected and repaired and explain why you chose
each integration mode.

**Interview challenge:** “What happens if reporting is down for six hours while purchases continue?”

**Interview phrasing**

> “If reporting can be delayed, purchases could continue during a reporting outage. I would retain the events and
> process them safely after recovery. I would monitor the backlog and show how current the report is.”

**Keep outside this session:** Rebuilding the entire enterprise integration landscape.

**Senior decision test:** Reporting is down for six hours while purchases continue. Choose an event or synchronous
integration strategy, and explain loss prevention, replay, ordering, and operational responsibility.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T05 — Data architecture, ownership, and reporting

**Distributed-systems lens (v4):** Apply DS03 and DS04 to distinguish source of truth, replication, partitioning, and
projection freshness.

**Prerequisites:** B03, T01, and T02.

**Prepare:**

- Transactional and analytical data.
- Data ownership and authoritative sources.
- Schemas, quality, freshness, and lineage.
- Audit trails, retention, privacy, and reconciliation.

**Required checklist coverage (binding crosswalk):**

- **C045 · Depth:** Evaluate Command Query Responsibility Segregation (CQRS) or event sourcing when a concrete
  requirement justifies the extra complexity.
- **C058 · Core:** Define logical and physical data models for core entities and their relationships.
- **C059 · Core:** Name the authoritative source, owner, update path, and consumer for each critical data item.
- **C060 · Core:** Distinguish operational data, events, caches, analytical stores, and reporting projections.
- **C061 · Core:** Plan schema evolution, reference/master data, and data contracts across teams.
- **C062 · Core:** Define correctness, freshness, completeness, and reconciliation checks; detect and repair
  discrepancies.
- **C063 · Core:** Design auditability, lineage, retention, deletion, privacy classification, and access controls.
- **C064 · Core:** Explain batch versus streaming trade-offs and the effect of delayed or missing events on reports.
- **C065 · Depth:** Use partitioning, replication, indexing, or CDC details to resolve a demonstrated scale or
  integration need.

**Practice:** Create a data ownership matrix for policies, transactions, statuses, and reports. Design a reporting
pipeline with a freshness target and checks for missing or conflicting records.

**Pass:** I must be able to identify the source of truth for each critical fact, specify allowed staleness, and explain
how
discrepancies are found and corrected.

**Interview challenge:** “Two systems disagree about transaction status. Which is authoritative, and how do you resolve
it?”

**Interview phrasing**

> “I would define the system of record for each state. This is the authoritative source. If the financial record defines
> payment completion, reconciliation would use it to correct stale operational status.”

**Keep outside this session:** Specific proprietary data models.

**Senior decision test:** Two systems disagree about a transaction status. Identify the authoritative source for each
fact, reconcile without silently overwriting evidence, and state the allowed reporting delay.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### D02 — Payment lifecycle, state, and reconciliation

**Distributed-systems lens (v4):** Connect payment state correctness to DS05 uncertain outcomes and DS06 replay and
reconciliation.

**Prerequisites:** D01, T02, and T05.

**Prepare:**

- Authorization, clearing, and settlement.
- Reversals, refunds, disputes, and reconciliation.
- Payment states and financial records.
- Conceptual contrast between card authorization/clearing/settlement and ACH/check or other non-card payment flows;
  verify any rail-specific details against primary sources when needed.
- Auditability, missing records, and repair.

**Required checklist coverage (binding crosswalk):**

- **C028 · Core:** Identify where credit, fraud, risk, and finance teams affect a commercial payment journey.
- **C029 · Core:** Explain authorization, clearing, settlement, and reconciliation as distinct stages.
- **C030 · Core:** Handle declines, timeouts, reversals, refunds, disputes, and chargeback-style exception workflows at
  a conceptual level.
- **C031 · Core:** Model payment state transitions, financial integrity, ledger/audit concepts, duplicate prevention,
  and discrepancy repair.
- **C033 · Core:** Distinguish virtual-card payments from non-card bank payment rails such as Automated Clearing House
  (ACH) and check, and identify differences in state, settlement, exceptions, and control boundaries.
- **C034 · Depth:** Discuss cross-border payments, currency conversion, cutoffs, and regional variation when relevant to
  a prompt.
- **C035 · Depth:** Study detailed network messages or product rules only if the actual interview scope calls for them.
- **C062 · Core:** Define correctness, freshness, completeness, and reconciliation checks; detect and repair
  discrepancies.

**Practice:** Draw a state machine from purchase initiation through final reconciliation. Include timeout, duplicate,
reversal, delayed settlement, and missing-event cases. Define a daily reconciliation control and manual exception
workflow.

**Pass:** I must be able to explain the difference between an immediate customer-facing status and a final financial
state, with detection and repair paths.

**Interview challenge:** “The customer sees success, but the settlement record is absent. What happens next?”

**Interview phrasing**

> “Authorization, settlement, and reconciliation are different stages. I would compare the missing settlement record
> with the expected processing window. If it remains unresolved, I would investigate and preserve the audit trail.”

**Keep outside this session:** Assertions about Amex's actual network or ledger design.

**Senior decision test:** A user sees “approved,” but there is no final settlement record. Explain which state is
confirmed, what must not be claimed, how the exception is traced, and when escalation is warranted.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T06 — Security, privacy, and payment-data risk

**Distributed-systems lens (v4):** Review security and identity across every inter-service trust boundary and during
degraded operation.

**Prerequisites:** T03, and T05.

**Prepare:**

- Trust boundaries and sensitive data.
- Authentication versus authorization, identity federation, service identity, least privilege, role-based and
  attribute-based access control, and tenant isolation.
- OAuth 2.0, OpenID Connect (OIDC), mutual Transport Layer Security (mTLS), credential storage/rotation, scope/claim
  validation, and object/function-level authorization checks.
- Secrets, keys, encryption, tokenization, data classification, and data minimization.
- Threat modeling, third-party risk, and payment-data scope.

**Required checklist coverage (binding crosswalk):**

- **C049 · Core:** Select authentication and authorization mechanisms, scopes/claims, gateway policies, quotas, and rate
  limits.
- **C055 · Core:** Distinguish authentication (who/what you are) from authorization (what you may do); explain delegated
  access versus login and object-level access checks.
- **C056 · Core:** Introduce OAuth 2.0, OpenID Connect (OIDC), and mutual Transport Layer Security (mTLS); describe
  their purpose and appropriate use without assuming a required company implementation.
- **C063 · Core:** Design auditability, lineage, retention, deletion, privacy classification, and access controls.
- **C066 · Core:** Draw trust boundaries and trace sensitive data through each component and third party.
- **C067 · Core:** Explain identity federation, authentication, service identity, least privilege, and role-based access
  control (RBAC) and attribute-based access control (ABAC).
- **C068 · Core:** Test object-level and function-level authorization, tenant isolation, and administrative
  entitlements.
- **C069 · Core:** Design secrets/key handling, encryption in transit and at rest, tokenization, and data minimization.
- **C070 · Core:** Threat-model API abuse, fraud-related misuse, sensitive business flows, and unsafe dependencies.
- **C071 · Core:** Understand payment-data environment boundaries and the need to verify current Payment Card Industry
  (PCI) requirements with official sources.
- **C072 · Core:** Address privacy, audit evidence, third-party and software-supply-chain risk in the delivery process.
- **C073 · Core:** State residual risk, control owner, review evidence, and when to seek security or compliance
  specialists.
- **C074 · Depth:** Study jurisdiction-specific rules or deep cryptographic implementation only if the role or interview
  identifies them.

**Practice:** Mark sensitive data and trust boundaries on the running-case design. Identify at least five plausible
threats, controls, residual risks, and owners. Review object-level and function-level API authorization.

**Pass:** Each proposed control addresses a named threat. I must be able to explain what remains at risk and which
specialists must review the design.

**Interview challenge:** “How would you reduce the amount of payment data your new service touches?”

**Interview phrasing**

> “I would identify sensitive data and trust boundaries first. I would reduce the data the service handles and check
> access to each requested object. Each control would address a specific threat.”

**Keep outside this session:** Legal conclusions or certification claims.  
**Primary
references:** [PCI Security Standards Council](https://www.pcisecuritystandards.org/standards/pci-dss/), [OWASP API Security Top 10](https://api-security.owasp.org/editions/2023/en/0x03-introduction/), [OAuth 2.0 Security BCP RFC 9700](https://www.rfc-editor.org/rfc/rfc9700),
and [mutual TLS RFC 8705](https://www.rfc-editor.org/rfc/rfc8705).

**Senior decision test:** A new reporting endpoint could expose one company's data to another. Compare boundary
controls, validate object-level access, and state residual risk and the approving owner.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T07 — Reliability, SLOs, and disaster recovery

**Distributed-systems lens (v4):** Use DS07/DS08 to prove graceful degradation and regional write authority.

**Prerequisites:** T02 and T04.

**Prepare:**

- Customer-journey reliability measures.
- Service level targets and error budgets.
- Failure isolation and graceful degradation.
- Recovery objectives, failover, and recovery tests.

**Required checklist coverage (binding crosswalk):**

- **C075 · Core:** Define user-journey service level indicators (SLIs), service level objectives (SLOs), error budgets,
  and alert thresholds.
- **C076 · Core:** Conduct failure-mode analysis and choose graceful degradation or safe failure behavior.
- **C077 · Core:** Compare high-availability and failover options, including active/passive and active/active
  trade-offs.
- **C078 · Core:** Set recovery time objectives (RTO) and recovery point objectives (RPO), backup/restore strategy,
  disaster-recovery drills, and recovery evidence.
- **C085 · Depth:** Analyze multi-region consistency or fault-injection testing when the design requires it.

**Practice:** Set one customer-journey SLO, a latency budget, and recovery objectives for the running case. Walk through
a dependency outage and a regional outage: detection, customer impact, mitigation, recovery, and evidence of success.

**Pass:** I must be able to explain why the chosen targets match business needs and how the architecture and operating
model support them.

**Interview challenge:** “A dependency fails during peak purchasing. Which capabilities continue, and which must stop
safely?”

**Interview phrasing**

> “I would set reliability targets for the customer journey. Then I would examine each dependency and its failure
> impact. The design would define which actions can continue safely and how we prove recovery works.”

**Keep outside this session:** Premature vendor service selection.  
**Primary reference:** [Google SRE SLO resources](https://sre.google/resources/book-update/slos/).

**Senior decision test:** The primary region fails during a peak purchase period. Decide which functions fail closed or
continue, state recovery targets as assumptions, and describe how to prove recovery.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T08 — Performance, capacity, and cost

**Distributed-systems lens (v4):** Use DS04/DS07 to test shard hotspots, tail latency, and retry amplification.

**Prerequisites:** T02, T05, and T07.

**Prepare:**

- Demand estimates and traffic patterns.
- Throughput, concurrency, and latency.
- Bottlenecks, caching, and load tests.
- Scaling decisions and cost.

**Required checklist coverage (binding crosswalk):**

- **C065 · Depth:** Use partitioning, replication, indexing, or CDC details to resolve a demonstrated scale or
  integration need.
- **C079 · Core:** Estimate peak demand, throughput, concurrency, storage growth, and latency budgets.
- **C080 · Core:** Diagnose tail latency, network/database bottlenecks, hot partitions, cache behavior, and resource
  saturation.
- **C081 · Core:** Apply load shedding, queueing/backpressure, scaling, and capacity tests when justified.
- **C082 · Core:** Connect performance choices to cost drivers and operational complexity.

**Practice:** State assumptions for peak requests and data volume. Estimate required throughput and a latency budget,
then identify likely bottlenecks and an experiment to validate each. Compare two scaling options on performance and
cost.

**Pass:** I must be able to defend at least one quantitative estimate and explain which assumptions matter most.

**Interview challenge:** “Traffic triples for one hour each month. What do you change first, and what evidence would you
gather?”

**Interview phrasing**

> “I would estimate peak demand using stated assumptions. Then I would measure where time and resources are spent. I
> would choose a scaling change based on the bottleneck, cost, and test results.”

**Keep outside this session:** Memorizing a cloud price list.

**Senior decision test:** Traffic triples temporarily and the database is slow. Compare query/index changes, caching,
scaling, and load shedding using measurements and estimated cost.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T09 — Observability, incidents, and operating a 24/7 service

**Distributed-systems lens (v4):** Use DS09 to verify business outcomes across trace and event boundaries.

**Prerequisites:** T07.

**Prepare:**

- Logs, metrics, traces, and business monitoring.
- Useful alerts and runbooks.
- On-call ownership and incident response.
- Operational readiness and learning after incidents.

**Required checklist coverage (binding crosswalk):**

- **C054 · Core:** Define integration-level monitoring, partner dependencies, service expectations, and escalation
  paths.
- **C083 · Core:** Instrument logs, metrics, traces, and business-journey telemetry; detect failures that infrastructure
  metrics miss.
- **C084 · Core:** Design actionable alerts, runbooks, on-call ownership, incident communication, and post-incident
  learning.
- **C085 · Depth:** Analyze multi-region consistency or fault-injection testing when the design requires it.

**Practice:** Create a monitoring and runbook outline for the purchase journey. Identify a symptom that infrastructure
metrics would miss. Simulate a production incident and deliver a two-minute stakeholder update.

**Pass:** I must be able to detect business impact, localize a fault, mitigate safely, and describe how the design
changes after the incident.

**Interview challenge:** “All services show green, but customers cannot complete purchases. How would you know?”

**Interview phrasing**

> “I would monitor successful purchases as well as service health. A service can respond successfully while the business
> journey fails. Alerts should show customer impact and lead to a clear recovery action.”

**Keep outside this session:** Tool-specific dashboard setup.

**Senior decision test:** All infrastructure dashboards show green while purchase failures rise. Define customer-journey
alerting, incident roles, mitigation, and measurable follow-up.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T10 — Cloud, hybrid infrastructure, and platform engineering

**Distributed-systems lens (v4):** Evaluate fault domains, deployment blast radius, and data/compute placement for DS08.

**Prerequisites:** T06, T07, and T08.

**Prepare:**

- Deployment topology and network boundaries.
- Runtime and hosting choices.
- Configuration, secrets, and infrastructure as code.
- Regional design, hybrid systems, and platform ownership.

**Required checklist coverage (binding crosswalk):**

- **C086 · Core:** Explain deployment topology, network zones, service-to-service communication, hybrid/on-premises
  dependencies, and blast radius.
- **C087 · Core:** Compare managed services, containers, and other runtime choices against team skill, control, cost,
  and reliability.
- **C088 · Core:** Use infrastructure as code, configuration management, secrets, and environment promotion responsibly.
- **C089 · Core:** Define platform ownership, shared capabilities, support model, and operational boundaries.
- **C097 · Depth:** Prepare vendor-specific cloud services or algorithm drills only after the interview process or
  chosen technology discipline justifies them.

**Practice:** Draw a deployment view and explain release, rollback, failure domains, observability, and ownership.
Compare a managed service with a self-operated alternative.

**Pass:** I must be able to identify the infrastructure dependencies behind the logical diagram and defend a platform
choice
against reliability, security, cost, and team skills.

**Interview challenge:** “What changes if a required system remains on premises?”

**Interview phrasing**

> “I would map the deployment, network connections, and failure boundaries. For an on-premises dependency, I would
> examine latency and connection failures. I would choose the runtime based on reliability, cost, and team skills.”

**Keep outside this session:** Guessing Amex's hosting choices.  
**Primary
reference:** [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/definitions.html)
or [Azure Architecture Center patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/).

**Senior decision test:** A legacy dependency remains on-premises. Compare a managed deployment with a self-operated
deployment while accounting for network failure, control, cost, and ownership.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### T11 — SDLC, code review, and hands-on technical depth

**Distributed-systems lens (v4):** Use DS05/DS06 failure timelines for Python handler tests and event-consumer review.

**Prerequisites:** B01, B02, B03, T02, and T03. Begin with code-reading exercises before concurrency tests.

**Prepare:**

- **Advanced Python application:** functions/modules, control flow, exceptions, type hints, dependency calls, and
  runtime behavior; B01 already introduced Python basics.
- Review and modify a small API handler and event consumer; study concurrency, race conditions, durable idempotency,
  transaction boundaries, and timeout uncertainty.
- Test normal, invalid, duplicate, parallel, unauthorized, and failed-dependency paths; review correctness, security,
  readability, observability, and regression evidence.
- Debug a production-style problem from symptoms to hypothesis, repro, fix, and tests.
- CI/CD, dependencies, release controls, feature flags, rollback, and post-release verification.

**Required checklist coverage (binding crosswalk):**

- **C050 · Core:** Use contract testing and consumer-driven feedback to prevent breaking changes.
- **C072 · Core:** Address privacy, audit evidence, third-party and software-supply-chain risk in the delivery process.
- **C090 · Core:** Build hands-on depth in Python. Start with simple code, then add concurrency and failure handling.
- **C091 · Core:** Review code for correctness, concurrency, failure handling, security, readability, and observability.
- **C092 · Core:** Select unit, integration, contract, performance, security, and resilience tests for a change.
- **C093 · Core:** Explain continuous integration and continuous delivery (CI/CD) controls, dependency checks, release
  strategies, feature flags, rollback, and post-release verification.
- **C094 · Core:** Debug a production-style fault from symptoms through evidence, hypothesis, fix, and regression test.
- **C095 · Core:** Read and modify a production-style Python API handler, explain its input/output and dependency calls,
  and defend its error handling.
- **C096 · Core:** Demonstrate an evidence-based code review with tests for concurrency, timeout uncertainty, retry
  duplicates, authorization, and safe rollback.
- **C097 · Depth:** Prepare vendor-specific cloud services or algorithm drills only after the interview process or
  chosen technology discipline justifies them.

**Practice:** Implement or review a small idempotent handler or event consumer. Test duplicate delivery, timeout,
concurrency, invalid authorization, and rollback behavior. Explain how the change is released and observed.

**Pass:** I must be able to reason from architecture to code and tests without losing correctness at the edge cases. I
must be able to explain a defect and a minimal safe fix.

**Interview challenge:** “Review this retry implementation. Under what conditions can it duplicate a business action?”

**Interview phrasing**

> “I would review how the code behaves when requests overlap or a dependency times out. Tests should check duplicate
> actions and access failures. I would also define how we release, observe, and reverse the change.”

**Keep outside this session:** Algorithm drills unrelated to your likely technology discipline unless the actual
interview process calls for them.

**Senior decision test:** Review a Python handler that retries after timeouts. Identify duplicate-payment and race
risks, propose the smallest safe change, and show tests and rollback evidence.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### DS01 — Distributed-system boundaries, latency, and partition trade-offs

**Prerequisites:** B01, B02, F02, and T01. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C118 · Core:** Identify nodes, network boundaries, request paths, failure domains, and uncertain outcomes.
- **C119 · Core:** Allocate an end-to-end latency budget across network hops and synchronous call chains.
- **C120 · Core:** Reason about availability and linearizable consistency during a network partition; avoid blanket CAP
  labels.

**Prepare:** Node, request hop, process crash, partial failure, communication delay, timeout, retry uncertainty,
network partition, availability, and consistency. Compare one process versus multiple processes across machines.
Explain that a timeout is lack of confirmation, not proof the operation failed.

**Worked example:** Draw a purchase API calling a policy service and a payment adapter. Mark two independent network
links; trace a delayed payment reply. Budget latency by step using clearly labeled hypothetical numbers.

**Guided practice:** Record the result the customer sees, the actual state, and the unknown facts for three failure
timelines. Compare a direct synchronous chain to a durable-workflow variant. Validate by injecting a delayed reply.

**Failure and trade-off:** More independently deployable services add network and operational failure points. During a
partition, specify which side can safely serve a write instead of calling an entire database simply “AP” or “CP.”

**Interview phrasing:** “I would identify the business invariant and every failure boundary. A timeout creates
uncertainty. I would choose the consistency and availability behavior for the affected operation, then verify it by
simulating the failure.”

**Senior decision test:** Purchase approval must finish quickly but a risk dependency becomes unreachable. Choose
between waiting, safe denial, and conditional degradation; compare latency, business risk, and recovery ownership.

**Pass evidence:** Explain each new Core item, draw a normal and failed request timeline, defend alternatives, name
monitoring and an owner; score at least 4/5 per applicable dimension.

### DS02 — Distributed time, ordering, races, and coordination

**Prerequisites:** DS01. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C121 · Core:** Explain clock uncertainty, causal ordering, and why timestamps alone are insufficient for
  correctness.
- **C122 · Core:** Diagnose lost updates and concurrent retry races; compare optimistic and pessimistic control.
- **C123 · Depth:** Use leases, distributed locks, and fencing tokens when stale owners can still act.

**Prepare:** Wall-clock time versus logical/causal order, concurrent execution, request versions, conditional writes,
compare-and-swap, optimistic version checks, row locks, leases, and stale lock holders. Define the terms before use.

**Worked example:** Two business administrators edit the same spending limit. Construct a two-column event timeline:
both read version 4; one writes version 5; the other must detect a conflict rather than silently overwrite it.

**Guided practice:** Design and test an update with expected-version checks, including simultaneous writers and a
replayed request. For Depth, simulate a lease expiring while the previous worker is paused.

**Failure and trade-off:** Locking can simplify one invariant but increases contention and risks unavailable lock
management. Optimistic updates need explicit conflict handling; physical timestamps do not eliminate races.

**Interview phrasing:** “I would protect concurrent changes with a database-supported conditional update. For
cross-node ownership, I would not trust a lease alone if an expired worker can still mutate state.”

**Senior decision test:** Two workers both think they own an expensive reconciliation task. Compare a database claim,
lease plus fencing, and idempotent task execution. Define what the downstream state store enforces.

**Pass evidence:** Core item explanations, tested race timeline, chosen control, failure case, owner, and 4/5 scores.

### DS03 — Replication, consistency, quorum, and consensus

**Prerequisites:** B03, DS02, and T02. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C124 · Core:** Compare replica layouts and sync/async updates, lag, and recovery behavior.
- **C125 · Core:** Specify strong/linearizable or eventual read/write semantics and allowed staleness.
- **C126 · Core:** Discuss quorum, network partitions, and split-brain prevention for a particular model.
- **C127 · Depth:** Explain why leader election/consensus may be needed and what its guarantees cover.

**Prepare:** Replicas, leaders, followers, acknowledgments, quorum, staleness, read-your-writes, linearizability,
serializability, partitions, and failover. Be precise: a specific database's guarantees must come from its docs.

**Worked example:** A policy update is written to a primary node while a reporting replica lags. Show a stale read,
a leader failure, and which reads/writes the chosen consistency contract permits.

**Guided practice:** Compare one leader with asynchronous replicas against a documented strongly consistent design.
State allowed stale-data duration and behavior during a partition; write a verification test for both.

**Failure and trade-off:** Replication aids survival but does not by itself guarantee correct concurrent writes.
Stronger consistency may increase latency or reduce write availability under some failures.

**Interview phrasing:** “I would write the required consistency contract first. Then I would select replication and
failover behavior that satisfies it, including how stale reads and conflicting writers are handled.”

**Senior decision test:** A spend-limit update must be enforced before another purchase, while finance reporting may
lag. Choose the read authority and test both a partition and a replica delay.

**Pass evidence:** State guarantees and counterexamples; compare two alternatives, failure tests, recovery owner,
and scores of at least 4/5.

### DS04 — Partitioning, hot keys, and distributed scale

**Prerequisites:** B03 and DS03. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C128 · Core:** Select shard keys and detect skew and hot partitions.
- **C129 · Core:** Evaluate cross-shard transactions, fan-out reads, IDs, and rebalance safety.
- **C130 · Depth:** Address cache staleness and invalidation when the scenario needs cached reads.

**Prepare:** Horizontal partitioning, routing, shard key, tenant ID, hotspots, skew, fan-out, rebalancing, and
cross-partition operations. Distinguish data capacity from request rate and storage from ownership.

**Worked example:** Compare shard-by-tenant and shard-by-transaction for a hypothetical commercial platform with one
very large tenant. Trace a policy lookup and a tenant-level finance report under both designs.

**Guided practice:** Sketch routing and a rebalance plan. Estimate a simple hypothetical traffic distribution.
Write the normal and failure path if the shard map is stale during migration.

**Failure and trade-off:** More partitions do not repair a bad partition key. Spreading one tenant across shards can
improve load distribution but complicate organization-wide queries and atomic updates.

**Interview phrasing:** “I would choose a partition key from access patterns and measured hotspots, not only table
size. I would budget for cross-partition queries, migrations, and the consistency of routing metadata.”

**Senior decision test:** One corporate customer causes 40% of peak traffic (hypothetical). Decide whether to isolate
the tenant, subdivide it, or optimize the current path, and show a load test plus rollback plan.

**Pass evidence:** Key choice, access-pattern matrix, hot-key test, alternate design, owner, 4/5 scores.

### DS05 — Idempotency, workflow state, and distributed transactions

**Prerequisites:** DS02 and T02. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C041 · Core (reapply):** Idempotency keys, deduplication, safe retries, and concurrency.
- **C043 · Core (reapply):** Transaction boundaries, sagas, and compensation.
- **C044 · Core (reapply):** Transactional outbox and change-data capture concepts.
- **C131 · Core:** Durable request identity, parameter consistency, concurrent deduplication, and retry safety.
- **C132 · Core:** Resolve external-action uncertainty through status checks, reconciliation, and escalation.

**Prepare:** Idempotent operation, durable request record, uniqueness constraint, in-progress state, request
fingerprint, external correlation ID, compensation, saga, outbox, and audit evidence.

**Worked example:** A payment adapter executes an action, then the API loses the response. Trace the first request,
timeout, retry, same-key/different-body request, and the source of truth for the final outcome.

**Guided practice:** Write a small Python handler or pseudocode with durable idempotency state and atomic reservation.
Test parallel requests, crash between local commit and event publish, and uncertain downstream state.

**Failure and trade-off:** A unique key in volatile memory does not survive process restart. An outbox reduces
local dual-write risk but requires consumer deduplication. Compensation is not the same as rolling back an external
financial action and may itself fail.

**Interview phrasing:** “I would assign a durable business request ID, enforce atomic claim and deduplication, and
persist an uncertain state until reconciliation confirms the external outcome. I would not retry blindly.”

**Senior decision test:** An external payment succeeded but the caller timed out and immediately retried. Compare
status query, provider-supported idempotent retry, and manual intervention. Choose according to verified contract.

**Pass evidence:** Correct failure timeline, request-state model, concurrent test, audit/reconcile plan, owner, 4/5.

### DS06 — Event streams, delivery semantics, and replay

**Prerequisites:** T04 and DS05. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C052 · Core (reapply):** Event contract, naming, schema versioning, and ordering scope.
- **C053 · Core (reapply):** Poison messages, dead-letter paths, delayed and duplicate consumers.
- **C133 · Core:** Trace broker partitions, consumer acknowledgment/offset behavior, retention, lag, and replay.
- **C134 · Core:** Design safe consumers with ordering assumptions, schema evolution, and deduplication.

**Prepare:** Command versus event, publisher, broker, topic, partition, offset, acknowledgment, at-least-once
delivery, consumer group, backlog, replay, poison message, and dead-letter queue. Avoid unqualified “exactly once.”

**Worked example:** A committed purchase generates an event. Reporting is offline and later replays records, including
one duplicate and one old event arriving after a newer state transition.

**Guided practice:** Define an event envelope with entity ID, event ID, version, occurrence time, schema version,
and producer. Write consumer rules for ordering and idempotence. Simulate lag and recovery.

**Failure and trade-off:** A broker acknowledgment is not necessarily proof the downstream business effect committed.
Ordering often has a defined partition/key scope; replay can reconstruct or corrupt a projection depending on the
consumer's state model.

**Interview phrasing:** “I would define the event contract and ordering scope, then make consumers safe under replay.
I would monitor consumer lag and keep a recovery path for poison or missing events.”

**Senior decision test:** Reporting is down six hours while purchases continue. Compare synchronous blocking with
event buffering and replay; prove no unaccounted events remain after recovery.

**Pass evidence:** Contract, timeline, replay plan, duplicate handling, reconciliation owner, 4/5.

### DS07 — Cascading failure, overload, and backpressure

**Prerequisites:** DS05 and DS06. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C040 · Core (reapply):** Partial failure, timeouts, bounded retries, circuit breaking, and backpressure.
- **C081 · Core (reapply):** Queueing, load shedding, and capacity controls.
- **C135 · Core:** End-to-end deadlines, bounded backoff/jitter, retry budgets, and circuit breakers.
- **C136 · Core:** Queue limits, bulkheads, backpressure, safe rejection, and overload recovery.

**Prepare:** Timeout versus deadline, caller cancellation, retry amplification, exponential backoff, jitter,
circuit breaker, bulkhead isolation, queue capacity, saturation, and load shedding.

**Worked example:** A request passes through three services, each retrying three times. Trace the potential
amplification and show how a propagated deadline and one controlled retry owner reduce work.

**Guided practice:** Draw a queue growing while reporting slows. Choose limits, backpressure signal, user-visible
response, and alerts. Exercise partial and total dependency outages.

**Failure and trade-off:** Unlimited queues hide overload until latency becomes unacceptable. Aggressive retries can
harm the dependency they are trying to reach. Reject or degrade work deliberately where data integrity permits.

**Interview phrasing:** “I would allocate an end-to-end deadline, set bounded retries with jitter, isolate failing
dependencies, and shed excess load safely rather than building an unbounded backlog.”

**Senior decision test:** A downstream risk service becomes slow during a traffic spike. Preserve financial safety
while comparing fail-closed behavior, cached risk results, and delayed processing under explicit assumptions.

**Pass evidence:** Deadline/queue arithmetic, failure tests, safe state, alert owner, 4/5.

### DS08 — Regional failure, failover, and split brain

**Prerequisites:** DS03, DS07, and T07. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C077 · Core (reapply):** High availability and active/passive versus active/active.
- **C078 · Core (reapply):** Recovery time, recovery point, backup, and restore evidence.
- **C085 · Depth (reapply):** Multi-region consistency and fault-injection when justified.
- **C137 · Core:** Match failover topology to assumed recovery targets and validate recovery.
- **C138 · Core:** Define a single authority for risky writes, split-brain prevention, and failback.

**Prepare:** Region, failure domain, recovery time objective (RTO), recovery point objective (RPO), active/passive,
active/active, data replication lag, traffic routing, fencing, and failback.

**Worked example:** The active purchase region stops responding while asynchronous replicas trail. Distinguish
requests known to be committed from uncertain ones; decide whether the secondary may accept new financial writes.

**Guided practice:** Write a failover runbook with triggers, writer ownership, customer-facing state, reconciliation,
measured recovery, and return-to-primary validation. Run a tabletop exercise.

**Failure and trade-off:** Active/active does not automatically solve conflicting financial writes. Recovery targets
are assumptions until tested; failover can preserve availability while risking inconsistent authority.

**Interview phrasing:** “I would derive failover from business RTO and RPO, define write authority during a partition,
and prove the data and customer journey are correct before accepting normal traffic.”

**Senior decision test:** The primary region is partitioned rather than fully down. Compare writable failover with
safe read-only operation and deferred action; explain split-brain controls and reconciliation evidence.

**Pass evidence:** Architecture, runbook, writer-fencing plan, drill measurements, owner, 4/5.

### DS09 — Observability, debugging, and failure experiments

**Prerequisites:** T09 and DS08. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C083 · Core (reapply):** Logs, metrics, traces, and customer-journey signals.
- **C084 · Core (reapply):** Alerts, runbooks, incident ownership, and learning.
- **C085 · Depth (reapply):** Fault injection or multi-region validation when justified.
- **C139 · Core:** Correlate request IDs, distributed traces, state changes, lag, and business impact.
- **C140 · Core:** Safely test delays, duplicates, stuck consumers, and region loss with rollback controls.

**Prepare:** Trace/span, correlation ID, service-level indicator (SLI), consumer lag, cardinality, audit trail,
incident timeline, rollback guardrail, and recovery verification.

**Worked example:** Infrastructure shows green, but purchases remain pending. Follow one request ID from ingress
through downstream timeout to outbox and reporting consumer; find the business-level failure.

**Guided practice:** Build a minimal incident evidence pack: timeline, hypothesis, log/trace fields, dashboards,
repro, mitigation, and regression test. Inject a duplicate event in a controlled test environment.

**Failure and trade-off:** Server uptime is not customer success. Excess logs can expose sensitive data or increase
cost; telemetry must follow least privilege and protect confidential financial information.

**Interview phrasing:** “I would correlate technical traces with business state and measure end-to-end outcomes.
The incident is resolved only when the business invariant and recovery path are verified.”

**Senior decision test:** All service health checks pass, while one cohort of customers cannot complete purchases.
Identify the missing signal, isolate the failure, and define a safe controlled test and owner.

**Pass evidence:** Traceable incident timeline, actionable alert, failure-injection plan, owner, 4/5.

### DS10 — Senior distributed-system design capstone

**Prerequisites:** DS01–DS09, D02, T06, and T11. **Priority:** Primary.

**Required checklist coverage (binding crosswalk):**

- **C115 · Core (reapply):** Defend an unfamiliar, timed architecture with changing constraints.
- **C141 · Core:** Build and defend end-to-end distributed-system design under consistency, scale, and outage
  constraints.

**Prepare:** Tie requirements, invariants, data ownership, consistency, partitioning, idempotency, asynchronous
integration, regional failover, SLOs, threat modeling, operations, and delivery sequencing into one argument.

**Worked example:** Draft a cloud-neutral commercial purchase platform. Compare a modular monolith with independently
deployed services. Label transaction authority, reporting freshness, recovery, and deployment boundaries.

**Guided practice:** Complete two distinct 45–60 minute design exercises (not only the original running case).
Change a constraint mid-design: region failure, 10x traffic, strict freshness, unavailable payment partner, or
new audit obligation. Treat any numeric load or latency as a hypothetical assumption.

**Failure and trade-off:** A diagram without invariants, failure handling, data authority, or ownership is not a
senior design. Naming patterns without showing their costs and validation is insufficient.

**Interview phrasing:** “I would first confirm the business invariant and measurable quality targets. Then I would
show ownership, consistency, failure behavior, and recovery, compare viable designs, and propose measured delivery.”

**Senior decision test:** Receive an unfamiliar problem; identify missing facts, two viable architectures, failure
cases, test evidence, accountable teams, and phased adoption under timed follow-ups.

**Pass evidence:** Score at least 4/5 on every applicable dimension for **two separate capstones**. Then complete
X01 and X02 using the existing mock standards, without coaching during the timed mock.

### E01 — Modernization and incremental migration

**Distributed-systems lens (v4):** Migration must preserve transaction invariants, idempotency, replay, and safe
coexistence.

**Prerequisites:** T03, T04, T05, T07, and T11.

**Prepare:**

- Legacy coexistence and migration patterns.
- API compatibility and data cutover.
- Parallel run, feature flags, and rollback.
- Phase owners, tests, and exit criteria.

**Required checklist coverage (binding crosswalk):**

- **C098 · Core:** Inventory legacy dependencies, consumers, data flows, and business risk before migration.
- **C099 · Core:** Use adapters, strangler-style migration, coexistence, and contract compatibility to reduce cutover
  risk.
- **C100 · Core:** Plan data migration, parallel run, reconciliation, feature flags, rollback, decommissioning, and exit
  criteria.

**Practice:** Make a three-phase plan to replace one capability in the running case while the existing platform stays
live. For each phase, list owner, dependency, risk, test, customer effect, success measure, and rollback trigger.

**Pass:** The plan reduces risk step by step and can be executed by teams rather than only drawn by an architect.

**Interview challenge:** “A critical downstream team cannot migrate on your schedule. What do you do?”

**Interview phrasing**

> “I would move one capability at a time. Each phase would have compatibility checks, reconciliation, and a rollback
> condition. I would retire the old path after its consumers and data are accounted for.”

**Keep outside this session:** A hypothetical full rewrite without constraints.

**Senior decision test:** A dependent consumer cannot move by the cutover date. Select coexistence versus forced
migration, show compatibility and reconciliation gates, and define exit criteria.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### E02 — Enterprise architecture, governance, and roadmap alignment

**Prerequisites:** F01, F02, and E01.

**Prepare:**

- Business, data, application, and technical architecture.
- Platform blueprints and roadmap alignment.
- Decision rights, reviews, and exceptions.
- Build-versus-buy, technical debt, and sequencing.

**Required checklist coverage (binding crosswalk):**

- **C101 · Core:** Align business, data, application, and technology architecture to platform blueprints and company
  roadmaps.
- **C102 · Core:** Define architecture standards, review criteria, decision rights, exceptions/waivers, and evidence of
  adoption.
- **C103 · Core:** Compare build/buy, technical-debt reduction, cost, business benefit, and delivery sequencing.
- **C104 · Core:** Produce an incremental roadmap with dependencies, milestones, owners, risks, and measurable outcomes.
- **C105 · Depth:** Discuss portfolio-level economics or vendor negotiation after the core roadmap concepts are
  understood.
- **C108 · Core:** Run design/code reviews that improve quality without becoming a bottleneck.

**Practice:** Create a 12–18 month capability roadmap and a lightweight design-review checklist for the running case.
Present a recommendation to a fictional product and technology steering group with alternatives, cost/risk,
dependencies, and decision requests.

**Pass:** Your governance mechanism catches material risk without becoming an approval bottleneck, and the roadmap
connects technical work to business outcomes.

**Interview challenge:** “Two product teams want exceptions to the platform API standard. When would you allow them?”

**Interview phrasing**

> “I would connect each roadmap item to a business outcome. Standards would address shared risks and integration needs.
> An exception would have a clear reason, owner, and review date.”

**Keep outside this session:** Claims about Amex's actual governance process.

**Senior decision test:** Two products want exceptions to the same API standard. Explain decision rights, quantified
benefits/risks, a time-bound waiver, and a roadmap outcome.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### L01 — Stakeholder influence and mentoring

**Prerequisites:** E02. Teach leadership methods before role-play.

**Prepare:**

- Stakeholders and decision owners.
- Influence, negotiation, and conflict resolution.
- Design-review facilitation.
- Mentoring and adoption across teams.

**Required checklist coverage (binding crosswalk):**

- **C106 · Core:** Influence product, business, security, data, operations, and engineering stakeholders without relying
  on title alone.
- **C107 · Core:** Resolve disagreements using constraints, evidence, decision owners, and documented follow-through.
- **C108 · Core:** Run design/code reviews that improve quality without becoming a bottleneck.
- **C109 · Core:** Mentor junior architects by developing their judgment and independence.

**Practice:** Role-play a disagreement among product speed, security review, and engineering capacity. Then coach a
junior architect whose design omits data ownership and failure recovery.

**Pass:** I must be able to reach a decision with clear owners and follow-through while improving the other person's
judgment.

**Interview challenge:** “Tell me about a time you changed an architecture decision after another team challenged you.”

**Interview phrasing**

> “I would make the disagreement specific: the constraint, the risk, and the options. Then I would agree on the decision
> owner and the evidence needed. When mentoring, I would ask the architect to explain each choice.”

**Keep outside this session:** Generic management theory.

**Senior decision test:** Security and engineering disagree about a release. Explain how to get evidence, reach a
documented decision, and mentor both teams without bypassing accountability.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### A01 — AI-assisted architecture with verification and controls

**Prerequisites:** F02, T03, and T06.

**Prepare:**

- AI help for requirements, reviews, and documentation.
- Validation, confidentiality, and traceability.
- Human decision ownership and design risk.
- Evaluation and measuring team benefit.

**Required checklist coverage (binding crosswalk):**

- **C112 · Core:** Use AI for requirement analysis, design critique, API review, test ideas, and documentation with
  appropriate data controls.
- **C113 · Core:** Verify AI suggestions against requirements and primary evidence; record accepted, rejected, and
  uncertain findings.
- **C114 · Core:** Address confidentiality, prompt-injection risk, provenance, human accountability, and
  quality/adoption measures.
- **C117 · Depth:** Evaluate specific AI tools or formal frameworks only if the interviewer asks about them or they
  match your real work.

**Practice:** Give an AI assistant a fictional architecture brief. Keep a finding log with accepted, rejected, and
unverified suggestions; show how each accepted suggestion was checked. Propose a team workflow and a measure of its
effect on review quality or cycle time.

**Pass:** I must be able to explain when AI help is useful, where it is unsafe, what a human verifies, and how you would
teach these habits to other architects.

**Interview challenge:** “An AI tool recommends an architecture change that appears elegant but conflicts with a
security constraint. What is your process?”

**Interview phrasing**

> “I would check the AI suggestion against the requirement and security constraint. I would verify the evidence before
> adopting it. I would record accepted, rejected, and uncertain findings for team review.”

**Keep outside this session:** Claims that AI output is authoritative or compliant by itself.  
**Primary
reference:** [NIST AI Risk Management Framework and Generative AI Profile](https://www.nist.gov/itl/ai-risk-management-framework).

**Senior decision test:** An AI assistant suggests weakening a control to simplify an API. Compare accepted/rejected
recommendations, primary evidence, privacy safeguards, and human approval.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### L02 — Senior-level stories and executive communication

**Prerequisites:** L01. Teach the story structure before asking for stories.

**Prepare:**

- A clear story structure.
- Truthful examples and your own contribution.
- Short and longer versions of an answer.
- Executive recommendations, outcomes, and lessons.

**Required checklist coverage (binding crosswalk):**

- **C110 · Core:** Explain architecture decisions to executives through customer impact, options, cost, risk, and a
  clear recommendation.
- **C111 · Core:** Prepare truthful examples of decisions, incidents, modernization, disagreement, mentoring, and
  learning from a reversed decision.

**Practice:** First learn the story structure. Practice with a clearly labeled fictional example. Then write eight real
story outlines using situation, your role, constraints, options, decision, execution, outcome, and lesson. Present one
architecture recommendation to an executive in three minutes and answer objections.

**Pass:** Learn the story format with labeled practice scenarios. For real interview stories, use only truthful details
about your contribution and outcomes. I must be able to explain technical risk in business terms without hiding material
uncertainty.

**Interview challenge:** “What decision are you most proud of, and what would you do differently now?”

**Interview phrasing**

> “My responsibility was [actual responsibility]. I chose [actual option] because [reason]. The result
> was [verified outcome]. I learned [lesson]. I would now improve [specific point].”

**Keep outside this session:** Invented achievements or polished but untestable claims.

**Senior decision test:** An executive challenges your decision after a production incident. Answer with verified
personal responsibility, alternatives, measurable outcomes, and what you would change.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### X01 — Integrated system-design mock

**Distributed-systems lens (v4):** At least one unfamiliar mock must stress consistency under partition,
duplicate requests, event recovery, capacity, and region failover. Keep the original two-prompt pass rule.

**Prerequisites:** The technical and enterprise cards. Use mocks after teaching.

**Prepare:**

- An unfamiliar system-design problem.
- Business needs, workflows, and data ownership.
- Failure, security, operations, and trade-offs.
- An incremental delivery plan under timed questioning.

**Required checklist coverage (binding crosswalk):**

- **C115 · Core:** Deliver an unfamiliar timed system design and defend it under changing constraints.

**Practice:** Run a 45–60 minute mock. Start with requirements, estimate scale, design workflows and interfaces, handle
failure/security/operations, compare alternatives, and close with a phased delivery plan. Ask the tutor to challenge you
rather than guide you.

**Pass:** Score at least 4/5 on business framing, requirements, technical depth, trade-offs, security/reliability,
delivery, and communication on two different prompts.

**Interview phrasing**

> “I would first confirm the business goal and main constraints. Then I would explain the workflow, data ownership, and
> failure behavior. I would close with the key trade-offs and an incremental delivery plan.”

**Keep outside this session:** Teaching during the mock; hold feedback until the end.

**Senior decision test:** With a new commercial-payment prompt and late-changing constraint, produce requirements,
alternatives, key risks, ownership, delivery phases, and a defensible choice within the timed mock.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.

### X02 — Leadership, deep-dive, and gap-closure mock

**Distributed-systems lens (v4):** Make the technical deep dive a distributed-system decision or failure-oriented
Python handler/event-consumer review. Retain leadership questions and two consecutive passing mocks.

**Prerequisites:** L01, A01, L02, and X01.

**Prepare:**

- Leadership and executive questions.
- Technical deep dives and Python code review.
- Follow-up questions and changing constraints.
- Retesting weak areas after review.

**Required checklist coverage (binding crosswalk):**

- **C116 · Core:** Deliver timed leadership, executive, code-review, and technical deep-dive answers; retest weak
  dimensions.

**Practice:** Run timed questions about disagreement, roadmap governance, mentoring, an incident, API strategy, and
AI-assisted architecture. Include a 20-minute deep dive into a design or code artifact. Record weak answers and redo
them in a second mock.

**Pass:** I must be able to answer with specific evidence and sound technical reasoning under follow-up questions; no
readiness dimension remains below 4/5 in two consecutive mocks.

**Interview phrasing**

> “My recommendation is [option]. It supports [business outcome] and carries [main risk]. I would validate it
> through [evidence or experiment] before making the next commitment.”

**Keep outside this session:** New broad topics in the final days unless a mock reveals a decisive gap.

**Senior decision test:** Defend one real leadership story and one technical artifact under follow-up questioning;
distinguish your observed evidence from assumptions, then restate a clearer decision.

**Assessment evidence:** A decision with stated assumptions, at least two options, a clear trade-off, a failure or
control consideration, how to validate it, and a named accountable owner. Score the decision on the standard card
rubric; log follow-up weaknesses.
