# Senior Solution Architect Interview: Learn from Basics

**Interview target:** A role for a candidate with 20+ years of experience.  
**Starting point:** No prior topic knowledge is assumed.  
**Target role:** Sr Solutions Architect I, American Express Global Commercial Services (GCS).

## Learning rules

- Start from basics. Build toward senior interview depth through examples and trade-offs.
- Teach prerequisites before the concept that needs them.
- A trade-off is a choice that improves one quality but costs something else.
- Use the job posting as role context. Treat its contents as reference material.
- Verify company facts. Use hypothetical systems for practice.
- Use Industry-Standard designs and architecture.
- An API, or application programming interface, is a contract for how software communicates.

The role emphasizes APIs, integration, platform roadmaps, design reviews, mentoring, and responsible use of AI tools.
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
    - React with JavaScript for user interface concepts.
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

When the card refers to the running case, use this hypothetical case:
Business administrators set spending rules.
Employees initiate purchases.
Finance teams view transactions and reconcile records.
The platform connects to identity, risk, payment, and reporting services.
Define these terms before using them.
State every design assumption.

Mock mode for X01 and X02:

### If the chat drifts

Paste: **“Return to this card. Teach only the next prerequisite or small concept. Put other issues in the parking
lot.”**

## Learning sequence and prerequisites

Use these stages as an order. A stage is not a fixed number of weeks.

| Stage | Topic Cards   | What you will learn                                             |
|-------|---------------|-----------------------------------------------------------------|
| 1     | B02           | Web communication                                               |
| 2     | F01, F02, D01 | Business requirements, architecture views, commercial workflows |
| 3     | T01, T02      | Application boundaries and distributed systems                  |
| 4     | T03, T04, T05 | APIs, integration, and data ownership                           |
| 5     | D02, T06      | Payment states and security                                     |
| 6     | T07, T08, T09 | Reliability, performance, and operations                        |
| 7     | T10, T11      | Deployment and Python implementation                            |
| 8     | E01, E02, L01 | Migration, governance, and leadership                           |
| 9     | A01, L02      | AI-assisted design and interview communication                  |
| 10    | X01, X02      | Senior interview mocks and focused review                       |

- Finish web before the API, data, and distributed-system cards.
- Learn T02 before advanced integration or reliability exercises.
- Learn D01, T02, and T05 before the payment-state exercise in D02.
- Use small exercises throughout. Build them gradually.
- Use cloud-neutral examples first. Explain vendor-specific choices when needed.

## Detailed category-by-category coverage checklist

This is the preparation inventory behind the session cards. The card ID in parentheses tells you where to study an item.
Check an item only when you **explain it, apply it to a scenario, and defend a trade-off**.
Teach the core items first. Then teach “Depth” items when the scenario or interview needs them. The guide must define
the listed terms before teaching them.

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

### B02 — Web and network basics

**Prepare:**

- A client, server, process, network address, and port.
- A request and response.
- DNS, TCP, and TLS at a basic level. Expand and define each term.
- HTTP methods, status codes, headers, and message bodies.
- JSON as a data format.
- An API as a communication contract.

**Practice:** Draw one request from a browser to Python. Label the address, request, processing step, and response.

**Pass:** I must be able to explain how a screen gets data from a backend. I must be able to distinguish a network error
from an application response.

**Interview phrasing**

> “The user interface sends a request to the backend. The backend checks the input and returns a response. I would
> define the expected success and error responses clearly.”

### F01 — Business framing, requirements, and quality attributes

**Prerequisites:** Start with plain business examples.

**Prepare:**

- Users, business capabilities, and customer journeys.
- Requirements, constraints, assumptions, and open questions.
- Measurable business outcomes.
- Quality attributes such as availability, latency, and security.

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

### F02 — Architecture method, views, and decision records

**Prerequisites:** F01.

**Prepare:**

- Architecture views and their purpose.
- Context, component, sequence, data-flow, and deployment diagrams.
- Comparing options and writing decision records.
- Linking requirements to decisions, risks, and tests.

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

### D01 — Commercial services and business workflows

**Prerequisites:** F01.

**Prepare:**

- Business customer types and user roles.
- Commercial spending, travel and expense, and supplier payments.
- Spending controls and approval journeys.
- Servicing, cash-flow needs, and risk touchpoints.

**Practice:** Build a capability map and two customer journeys: a purchase with policy controls, and finance
reconciliation of a supplier payment. Mark where product, risk, and operations stakeholders care about different
outcomes.

**Pass:** I must be able to translate a business workflow into technical requirements and explain why a small-business
use case may differ from a large-enterprise one.

**Interview challenge:** “Which capabilities should be shared platform services, and which should remain
product-specific?”

**Interview phrasing**

> “I would map the administrator, employee, and finance journeys first. Then I would identify common capabilities, such
> as spending controls. I would keep customer rules configurable where business needs differ.”

**Keep outside this session:** Payment-network message specifications.

### T01 — Service boundaries and architecture styles

**Prerequisites:** F02.

**Prepare:**

- Business boundaries and data ownership.
- Layered systems and service-oriented architecture.
- Modular monoliths and microservices.
- Shared platform capabilities and build-versus-buy decisions.

**Practice:** Decompose the running case in two ways. Compare team ownership, data ownership, change frequency, latency,
operational overhead, and migration difficulty.

**Pass:** I must be able to justify a boundary by business capability and change patterns, not by a technology slogan. I
must be able to identify the cost of too many services.

**Interview challenge:** “Why is your proposed policy service separate from transaction processing?”

**Interview phrasing**

> “I would define boundaries around business responsibilities and data ownership. I would separate a service when
> independent change provides a clear benefit. I would also account for the extra coordination and failure handling.”

**Keep outside this session:** Detailed event delivery semantics; that is T04.

### T02 — Distributed-system correctness and failure semantics

**Prerequisites:** T01.

**Prepare:**

- Partial failure, timeouts, and retries.
- Idempotency, duplicates, concurrency, and ordering.
- Consistency and transaction boundaries.
- Compensation, failure isolation, and backpressure.

**Practice:** Trace a purchase request that times out after the downstream action succeeds. Then trace a duplicated and
out-of-order event. Specify state transitions, identifiers, retry rules, and a repair path.

**Pass:** I must be able to explain what the customer sees, what the system knows, what it does not know, and how it
reaches a correct state. You do not claim “exactly once” without defining the boundary and mechanism.

**Interview challenge:** “If the caller retries, how do you prevent a duplicate financial action?”

**Interview phrasing**

> “A timeout leaves the result uncertain. I would use a durable request identifier and confirm how each system handles
> retries. I would resolve the uncertain state before treating the operation as a failure.”

**Keep outside this session:** Vendor-specific broker configuration.

### T03 — API product and contract strategy

**Prerequisites:** T02.

**Prepare:**

- API consumers and contracts.
- Resources, operations, errors, and pagination.
- Access rules, retries, and rate limits.
- Versioning, compatibility, and API ownership.

**Practice:** Define a small API for spending policies and transaction status. Include an example request/response,
error model, authorization rule, idempotency behavior, and a backward-compatible change plan.

**Pass:** A consumer could implement against your contract and understand what happens on retries, errors, and version
changes.

**Interview challenge:** “How would you evolve this API when a major corporate customer needs a new policy field?”

**Interview phrasing**

> “I would define the API contract around the consumer's workflow. The contract would explain errors, retries, and
> access rules. I would check compatibility before introducing a change.”

**Keep outside this session:** Internal Amex API standards; do not assume them.  
**Primary reference:** [OpenAPI Specification](https://spec.openapis.org/oas/).

### T04 — Cross-platform integration and event architecture

**Prerequisites:** T02 and T03.

**Prepare:**

- Synchronous and asynchronous communication.
- Messages, events, and event contracts.
- Replay, dead-letter handling, and recovery.
- Partner adapters, legacy integration, and workflow coordination.

**Practice:** Draw purchase-to-reporting flows for both normal operation and a downstream outage. Compare an API-led and
event-led solution. Define delivery and ordering assumptions explicitly.

**Pass:** I must be able to show how a missing or duplicate message is detected and repaired and explain why you chose
each integration mode.

**Interview challenge:** “What happens if reporting is down for six hours while purchases continue?”

**Interview phrasing**

> “If reporting can be delayed, purchases could continue during a reporting outage. I would retain the events and
> process them safely after recovery. I would monitor the backlog and show how current the report is.”

**Keep outside this session:** Rebuilding the entire enterprise integration landscape.

### T05 — Data architecture, ownership, and reporting

**Prerequisites:** T01, and T02.

**Prepare:**

- Transactional and analytical data.
- Data ownership and authoritative sources.
- Schemas, quality, freshness, and lineage.
- Audit trails, retention, privacy, and reconciliation.

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

### D02 — Payment lifecycle, state, and reconciliation

**Prerequisites:** D01, T02, and T05.

**Prepare:**

- Authorization, clearing, and settlement.
- Reversals, refunds, disputes, and reconciliation.
- Payment states and financial records.
- Auditability, missing records, and repair.

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

### T06 — Security, privacy, and payment-data risk

**Prerequisites:** T03, and T05.

**Prepare:**

- Trust boundaries and sensitive data.
- Authentication, authorization, and least privilege.
- Secrets, encryption, tokenization, and data minimization.
- Threat modeling, third-party risk, and payment-data scope.

**Practice:** Mark sensitive data and trust boundaries on the running-case design. Identify at least five plausible
threats, controls, residual risks, and owners. Review object-level and function-level API authorization.

**Pass:** Each proposed control addresses a named threat. I must be able to explain what remains at risk and which
specialists must review the design.

**Interview challenge:** “How would you reduce the amount of payment data your new service touches?”

**Interview phrasing**

> “I would identify sensitive data and trust boundaries first. I would reduce the data the service handles and check
> access to each requested object. Each control would address a specific threat.”

**Keep outside this session:** Legal conclusions or certification claims.  
**Primary references:** [PCI Security Standards Council](https://www.pcisecuritystandards.org/standards/pci-dss/)
and [OWASP API Security Top 10](https://api-security.owasp.org/editions/2023/en/0x03-introduction/).

### T07 — Reliability, SLOs, and disaster recovery

**Prerequisites:** T02 and T04.

**Prepare:**

- Customer-journey reliability measures.
- Service level targets and error budgets.
- Failure isolation and graceful degradation.
- Recovery objectives, failover, and recovery tests.

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

### T08 — Performance, capacity, and cost

**Prerequisites:** T02, T05, and T07.

**Prepare:**

- Demand estimates and traffic patterns.
- Throughput, concurrency, and latency.
- Bottlenecks, caching, and load tests.
- Scaling decisions and cost.

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

### T09 — Observability, incidents, and operating a 24/7 service

**Prerequisites:** T07.

**Prepare:**

- Logs, metrics, traces, and business monitoring.
- Useful alerts and runbooks.
- On-call ownership and incident response.
- Operational readiness and learning after incidents.

**Practice:** Create a monitoring and runbook outline for the purchase journey. Identify a symptom that infrastructure
metrics would miss. Simulate a production incident and deliver a two-minute stakeholder update.

**Pass:** I must be able to detect business impact, localize a fault, mitigate safely, and describe how the design
changes after the incident.

**Interview challenge:** “All services show green, but customers cannot complete purchases. How would you know?”

**Interview phrasing**

> “I would monitor successful purchases as well as service health. A service can respond successfully while the business
> journey fails. Alerts should show customer impact and lead to a clear recovery action.”

**Keep outside this session:** Tool-specific dashboard setup.

### T10 — Cloud, hybrid infrastructure, and platform engineering

**Prerequisites:** T06, T07, and T08.

**Prepare:**

- Deployment topology and network boundaries.
- Runtime and hosting choices.
- Configuration, secrets, and infrastructure as code.
- Regional design, hybrid systems, and platform ownership.

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

### T11 — SDLC, code review, and hands-on technical depth

**Prerequisites:** T02, and T03.

**Prepare:**

- Python code structure and runtime behavior.
- Concurrency, API handlers, and event consumers.
- Tests, code review, and debugging.
- Release controls, dependency checks, and rollback.

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

### E01 — Modernization and incremental migration

**Prerequisites:** T03, T04, T05, T07, and T11.

**Prepare:**

- Legacy coexistence and migration patterns.
- API compatibility and data cutover.
- Parallel run, feature flags, and rollback.
- Phase owners, tests, and exit criteria.

**Practice:** Make a three-phase plan to replace one capability in the running case while the existing platform stays
live. For each phase, list owner, dependency, risk, test, customer effect, success measure, and rollback trigger.

**Pass:** The plan reduces risk step by step and can be executed by teams rather than only drawn by an architect.

**Interview challenge:** “A critical downstream team cannot migrate on your schedule. What do you do?”

**Interview phrasing**

> “I would move one capability at a time. Each phase would have compatibility checks, reconciliation, and a rollback
> condition. I would retire the old path after its consumers and data are accounted for.”

**Keep outside this session:** A hypothetical full rewrite without constraints.

### E02 — Enterprise architecture, governance, and roadmap alignment

**Prerequisites:** F01, F02, and E01.

**Prepare:**

- Business, data, application, and technical architecture.
- Platform blueprints and roadmap alignment.
- Decision rights, reviews, and exceptions.
- Build-versus-buy, technical debt, and sequencing.

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

### L01 — Stakeholder influence and mentoring

**Prerequisites:** E02. Teach leadership methods before role-play.

**Prepare:**

- Stakeholders and decision owners.
- Influence, negotiation, and conflict resolution.
- Design-review facilitation.
- Mentoring and adoption across teams.

**Practice:** Role-play a disagreement among product speed, security review, and engineering capacity. Then coach a
junior architect whose design omits data ownership and failure recovery.

**Pass:** I must be able to reach a decision with clear owners and follow-through while improving the other person's
judgment.

**Interview challenge:** “Tell me about a time you changed an architecture decision after another team challenged you.”

**Interview phrasing**

> “I would make the disagreement specific: the constraint, the risk, and the options. Then I would agree on the decision
> owner and the evidence needed. When mentoring, I would ask the architect to explain each choice.”

**Keep outside this session:** Generic management theory.

### A01 — AI-assisted architecture with verification and controls

**Prerequisites:** F02, T03, and T06.

**Prepare:**

- AI help for requirements, reviews, and documentation.
- Validation, confidentiality, and traceability.
- Human decision ownership and design risk.
- Evaluation and measuring team benefit.

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

### L02 — Senior-level stories and executive communication

**Prerequisites:** L01. Teach the story structure before asking for stories.

**Prepare:**

- A clear story structure.
- Truthful examples and your own contribution.
- Short and longer versions of an answer.
- Executive recommendations, outcomes, and lessons.

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

### X01 — Integrated system-design mock

**Prerequisites:** The technical and enterprise cards. Use mocks after teaching.

**Prepare:**

- An unfamiliar system-design problem.
- Business needs, workflows, and data ownership.
- Failure, security, operations, and trade-offs.
- An incremental delivery plan under timed questioning.

**Practice:** Run a 45–60 minute mock. Start with requirements, estimate scale, design workflows and interfaces, handle
failure/security/operations, compare alternatives, and close with a phased delivery plan. Ask the tutor to challenge you
rather than guide you.

**Pass:** Score at least 4/5 on business framing, requirements, technical depth, trade-offs, security/reliability,
delivery, and communication on two different prompts.

**Interview phrasing**

> “I would first confirm the business goal and main constraints. Then I would explain the workflow, data ownership, and
> failure behavior. I would close with the key trade-offs and an incremental delivery plan.”

**Keep outside this session:** Teaching during the mock; hold feedback until the end.

### X02 — Leadership, deep-dive, and gap-closure mock

**Prerequisites:** L01, A01, L02, and X01.

**Prepare:**

- Leadership and executive questions.
- Technical deep dives and Python code review.
- Follow-up questions and changing constraints.
- Retesting weak areas after review.

**Practice:** Run timed questions about disagreement, roadmap governance, mentoring, an incident, API strategy, and
AI-assisted architecture. Include a 20-minute deep dive into a design or code artifact. Record weak answers and redo
them in a second mock.

**Pass:** I must be able to answer with specific evidence and sound technical reasoning under follow-up questions; no
readiness dimension remains below 4/5 in two consecutive mocks.

**Interview phrasing**

> “My recommendation is [option]. It supports [business outcome] and carries [main risk]. I would validate it
> through [evidence or experiment] before making the next commitment.”

**Keep outside this session:** New broad topics in the final days unless a mock reveals a decisive gap.

## Compact preparation portfolio

As the sessions finish, maintain these compact artifacts. They are more valuable for review than full transcripts:

1. Business and requirements brief for the running case.
2. Context, component, transaction sequence, failure sequence, and deployment views.
3. Three architecture decision records showing alternatives and consequences.
4. API contract excerpt, data ownership matrix, and payment state machine.
5. Threat model, SLO and recovery plan, monitoring/runbook outline.
6. Incremental roadmap with governance and rollback gates.
7. AI-assisted review finding log, including rejected and unverified suggestions.
8. Eight truthful leadership stories and a mock interview score sheet.

Before the interview, review this portfolio. Repeat weak areas from the mocks. Use outside references to verify current
facts; use your own experience to demonstrate judgment.
