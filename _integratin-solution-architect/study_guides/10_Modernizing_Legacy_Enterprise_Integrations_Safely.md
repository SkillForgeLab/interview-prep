# Modernizing Legacy Enterprise Integrations Safely

**Study guide for senior/principal Enterprise and Integration Solution Architect interviews**  
**Scope:** Vendor-neutral replacement of legacy interfaces while business transactions continue. Numbers and system
names below are illustrative assumptions, not facts about a particular company.

## 1. Frame modernization as a controlled change in business behavior

A legacy integration may encode an “accepted order” rule, manual correction, batch cutoff, undocumented parsing
behavior, and a recovery path operators trust. Replacing its protocol without discovering those behaviors can produce a
healthy platform with missing orders. Start an interview answer with the business capability, authoritative record,
consumers, and acceptable interruption. Then describe the migration boundary and evidence of correct outcomes.

**Assumptions for the 50-interface plan:** A company has 50 point-to-point integrations among CRM, order applications,
mainframe ERP, warehouse, finance, and reporting. They use calls, MQ messages, and files. Twelve carry customer or
financial transactions; three are critical order/settlement paths. The ERP stays. Two delivery squads and a
platform/operations group are funded. The outcome sought is fewer bespoke dependencies, clearer ownership, and lower
operational risk. Confirm inventory, capacity, and targets in discovery.

**Define success in business and technical terms:** missing or duplicate bookings, mismatch repair time, incident
minutes, change lead time, unsupported consumers, and old middleware cost. HTTP success cannot prove that the ERP booked
the right amount. Baseline these measures. For each interface, decide whether to **retire**, **replace**, **wrap**, *
*consolidate**, or **retain with controls**.

The Strangler Fig approach inserts a seam so functionality can be routed from old to new in increments. An
anti-corruption layer (ACL) translates between different domain models without forcing the new domain to inherit legacy
meanings. Neither is a universal proxy: a façade adds an operational dependency, and an ACL can become a permanent
tangle if translation rules have no owner or retirement decision. Microsoft documents both patterns and their
trade-offs; Fowler's revised Strangler Fig description emphasizes gradual
displacement. [Strangler Fig pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig), [Anti-Corruption Layer pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer), [Fowler, Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html).

## 2. Build an inventory that can drive decisions

Create an **interface register**, an **application/dependency graph**, and a **business transaction map**. Do not rely
only on diagrams or an application catalog. Cross-check repository configurations, gateway and broker routes, scheduler
entries, file drops, database jobs, network flow records, traces, support tickets, and interviews with operators and
business users. Sample a full month-end or quarter-end cycle if it changes behavior. A nominally unused feed may run
once per quarter; an unregistered spreadsheet or shared database read may be a real consumer. Record each finding's
evidence and confidence level. AWS's portfolio-discovery guidance likewise calls for criticality, dependency mapping,
migration groups, and a wave plan that matures as evidence
improves. [AWS detailed portfolio discovery](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-migration/detailed-portfolio-discovery.html).

| Record for every interface               | Questions that change the migration plan                                                                                       |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Business function and owner              | What decision or obligation does this connection satisfy? Who accepts a changed outcome?                                       |
| Producer, consumers, and actual versions | Which applications, batch jobs, partners, reports, and manual processes depend on it? Who can change them?                     |
| Source of truth and write authority      | Which system owns each fact? Are there hidden writes, triggers, or side effects?                                               |
| Contract and semantics                   | Protocol, schema, units, identifiers, ordering, validation, error behavior, replay, retention, and undocumented defaults?      |
| Timing and load                          | Peak and normal rates, business cutoff, latency target, maintenance window, seasonality, and backlog tolerance?                |
| Fragility and controls                   | Incident history, unsupported runtime, single expert, secret handling, test coverage, manual repair, and monitoring gaps?      |
| Dependency and cutover boundary          | Which routes share credentials, database tables, transactions, middleware, or deployment windows? Can one consumer move alone? |
| Evidence and decision                    | Traffic samples, logs, owner sign-off, confidence level, disposition, estimated effort, and next review date?                  |

Draw **runtime edges** and **change edges**. A finance feed may not call the order API, yet its reconciliation assumes
the order ID format. Shared credentials or schemas can link separate routes; a compatibility adapter may create a seam.
Unknown ownership or source of truth blocks a critical write-path cutover.

Use **criticality** for business harm (money, legal duty, customer promise, recovery deadline) and **fragility** for
likelihood and difficulty of failure (obscure transforms, manual steps, aging runtime, coupling, weak tests). A
critical, well-run route might move late; a low-value brittle route might be retired early.

## 3. Set target principles and explicit seams

1. **One owner per business fact and one active writer per cohort.** Declare who can create a booking, change an amount,
   and correct it. Shadow reads or calculations may run twice; irreversible writes should not occur twice merely to
   compare implementations. If dual writes are unavoidable, prove idempotency and compensation under failure, and
   document which side is authoritative.
2. **Contracts express meaning, not just shape.** Define stable business IDs, units, time zones, ordering keys, terminal
   states, retryable errors, authorization, replay policy, and version lifecycle. Describe HTTP APIs with OpenAPI,
   asynchronous channels/messages with AsyncAPI, and use a consistent event envelope such as CloudEvents when it suits
   the estate. These describe different aspects of a contract; none proves that old consumers understand a changed
   meaning. [OpenAPI Specification 3.2.1](https://spec.openapis.org/oas/v3.2.1.html), [AsyncAPI Specification 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0), [CloudEvents specification](https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md?plain=1).
3. **Keep legacy semantics at the edge.** An ACL maps old status codes, fixed-width records, and identifiers into
   explicit domain concepts. Preserve a raw payload and a mapping version for audit and replay, with access controls
   appropriate to the data. Reject ambiguous mappings instead of inventing values. Put business eligibility with the
   capability owner, not in a generic gateway script.
4. **Make coexistence observable.** A façade or adapter needs routing by operation/cohort, correlation and business IDs,
   metrics by old/new path, independent health checks, and a documented fail position. It must not hide which system
   decided the business outcome. A compatibility adapter may stay longer than expected; give it an owner, SLO, security
   patch plan, and retirement criteria.
5. **Expand, migrate, contract.** Add the replacement alongside the old contract, move consumers and verify their actual
   traffic, then retire the old surface. Version a contract when its meaning or required shape cannot be preserved.
   Fowler describes this as parallel
   change. [Fowler, Parallel Change](https://martinfowler.com/bliki/ParallelChange.html).

Standardize catalog metadata, IDs, schema review, security, test gates, observability, and deprecation. Domain teams own
payload meaning. Avoid a “canonical” object full of meaningless fields; document lossy mappings such as “legacy status
`A` combines accepted and pending fulfillment.”

## 4. A phased plan for 50 point-to-point integrations

**Counts and timing are planning assumptions.** Track “migrated,” “retired,” “wrapped and retained,” and “not started”
separately. Consolidating three routes still requires three consumer exits.

| Phase and illustrative timing                                     | Work and dependency rule                                                                                                                                                                                                       | Measurable exit criterion                                                                                                                                                                                                                        |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **0. Mandate and safety baseline (weeks 1–2)**                    | Sponsor names business, application, operations, security, and data owners. Freeze only unmanaged interface creation; urgent changes continue through review. Define incident, rollback, and data-correction authority.        | Scope, business outcomes, funding capacity, critical-route owners, and decision log approved.                                                                                                                                                    |
| **1. Discover and classify (weeks 2–8)**                          | Inventory all 50 and their consumers; observe normal and closing-cycle traffic. Map source-of-truth and shared infrastructure; label unknown edges. Baseline incidents, volume, latency, and discrepancies.                    | 50/50 routes registered; 100% of critical routes have named owners and source of truth; ≥95% of observed traffic assigned to a known route; unknown critical consumers investigated or isolated. Thresholds are illustrative and must be agreed. |
| **2. Define seams and pilot (weeks 6–14)**                        | Choose contract baseline, routing façade, ACL template, telemetry, reconciliation ledger, and deployment/runbook conventions. Pilot 4 low-to-medium criticality routes with representative protocols. Prove one real rollback. | Four route dispositions accepted; contract and replay tests pass; routing reversal rehearsed; no unowned discrepancies; on-call can distinguish old/new traffic.                                                                                 |
| **3. Wave A: simplify (months 4–6; 12 routes)**                   | Retire duplicate/unused feeds and move simple read or notification paths. Dependency order: consumer discovery → replacement contract → adapter → consumer move → traffic proof → retirement.                                  | 12 additional routes exited; zero unknown active consumers on retired endpoints; agreed SLO met for two business cycles; old schedules/credentials disabled after evidence review.                                                               |
| **4. Wave B: shared capabilities (months 6–9; 18 routes)**        | Consolidate high-value clusters behind owned APIs/events; migrate producers and consumers by cohort. Keep compatibility output for slow consumers. Address coupled data models and security changes before cutover.            | 18 additional routes exited; each migrated write path reconciled at business-key level; tested recovery time and incident ownership; old dependency reduced as planned.                                                                          |
| **5. Wave C: critical and constrained (months 9–12+; 16 routes)** | Move critical write paths after pilot evidence, tests, dual-run comparison, rehearsal, and a suitable window. Retain a constrained route with documented risk if prerequisites fail.                                           | All 50 have a signed disposition: four pilots, 30 routes in A+B, and 16 in C. Critical-route retirement requires reconciliation, rollback proof, and operational acceptance.                                                                     |

**Arithmetic:** pilot 4 + A 12 + B 18 + C 16 = 50 dispositions. Report physical removals separately. By year-end, some
constrained routes may remain behind owned adapters; a disposition is not a cutover.

Maintain a weekly dependency board with prerequisites, consumer confirmation, owner, mapping, window, rollback, and
exception date. A monthly architecture forum resolves cross-domain semantics; automated checks handle routine contracts.
The sponsor owns funding and risk acceptance; the service owner authorizes cutover. Stop a wave when incident,
discrepancy, or on-call limits fail.

## 5. Migration-wave scorecard

Use the scorecard to **sequence work**, not decide go-live. Score factors 1–5. **Risk** is migration hazard; **coupling
** is dependency rigidity; **window** is ease of finding a safe window; **readiness** covers owner, telemetry, runbook,
support, and reconciliation. Five means high for each. Illustrative index:
`3 × value + 2 × fragility + window + readiness − 2 × risk − coupling`. High value creates urgency; risk reduces
early-wave suitability.

| Candidate route (illustrative)   | Value | Fragility | Risk | Coupling | Window | Readiness | Index | Decision                                                                    |
|----------------------------------|------:|----------:|-----:|---------:|-------:|----------:|------:|-----------------------------------------------------------------------------|
| Redundant nightly product export |     2 |         4 |    1 |        1 |      5 |         4 |    20 | Retire early after proving no active consumer.                              |
| Warehouse inventory read         |     4 |         3 |    2 |        2 |      4 |         4 |    20 | Good pilot or Wave A candidate.                                             |
| Mainframe order booking          |     5 |         5 |    5 |        5 |      2 |         2 |    14 | High urgency, but prepare seams and evidence before Wave C.                 |
| Regulatory settlement feed       |     5 |         2 |    5 |        4 |      1 |         3 |     9 | Retain temporarily; secure and monitor while resolving window and evidence. |

For example, the order-booking index is `15 + 10 + 2 + 2 − 10 − 5 = 14`. Add **hard gates**: named owner, known writer,
cohort consumer inventory, testable contract, repair strategy, approved window, and operations staff. Re-score as
adapters reduce coupling and telemetry improves readiness.

## 6. Worked example: replace critical order booking while old consumers remain

**Scenario assumptions:** A sales portal sends `BOOK` records over MQ to a mainframe ERP. The ERP books the order and
publishes a fixed-width `BOOKED` confirmation to eight consumers. Two warehouse applications cannot change for 18
months. The ERP owns booked order number and financial amount; booking must never occur twice. Peak load is 120
bookings/minute. The business permits a 20-minute booking decision target and a 30-minute planned cutover window. These
numbers must be measured and approved in a real program.

**Target:** A new Order Booking service validates requests and invokes the ERP's supported booking interface through an
ACL. It publishes a documented `OrderBooked` event for modern consumers. A **legacy-output adapter** renders the
existing fixed-width `BOOKED` record for the two warehouse consumers. A routing façade receives the portal's stable
request contract and selects old or new path by tenant cohort. The ERP remains the authoritative book of record. The
façade does not decide credit policy, and the new service does not declare success before the ERP outcome is known or
durably recorded as pending under a separately approved promise.

**Before moving traffic:** Capture `BOOK` and `BOOKED` examples covering malformed input, cancellations, currency
precision, duplicate sends, timeout after ERP commit, and month-end cutoff. Specify field widths, padding, code pages,
timestamps, and error codes. Map legacy status to new states, flag unrepresentable cases, and relate a stable operation
ID to the ERP order number. Prove idempotency and ERP outcome lookup; otherwise reconcile before retrying an ambiguous
request.

**Coexistence sequence:**

1. Put the façade in front of the old route with 100% traffic still going old. Verify that this seam alone does not
   change booking, latency, or error behavior; rehearse bypass if the façade fails.
2. Run the new mapping and booking logic in **shadow mode without an ERP write**. Feed it a copy of requests, produce
   predicted validation/mapping results, and compare with real old-path decisions by operation ID. This catches semantic
   differences without creating two bookings. For external side effects that cannot be safely shadowed, test against a
   controlled ERP test environment and recorded cases.
3. For a small opted-in tenant, route writes only through the new service. Keep old-route invocation disabled for that
   cohort. The new service calls the same authoritative ERP. Assign exactly one legacy-confirmation publisher per
   cohort: if the ERP still emits `BOOKED`, forward that record and disable adapter publication; otherwise the adapter
   emits it after confirmed booking. Link the modern event and legacy record to the same ERP order ID, and prevent a
   consumer subscribed to both from acting twice. Compare ERP records, modern events, and legacy confirmations by order
   ID, amount, tenant, and time window.
4. Increase cohorts only after reconciliation and operations gates pass. Migrate the other six consumers to the modern
   event or API on their own schedule. Watch actual traffic and contract acknowledgements; a declared migration is not
   evidence that a nightly consumer stopped reading the old record.
5. Retire the input old route only after all portal cohorts have moved and no alternate producer uses it. Keep the
   legacy-output adapter until the two warehouse consumers migrate or the business formally accepts a longer-lived
   compatibility service. Its owner patches, tests, monitors, and budgets it like any production integration.

**Rollback boundary:** Before a new-path request reaches the ERP, the façade can route the next request back to the old
path. For an in-flight or confirmed booking, never “roll back” by replaying `BOOK` on the old path: that may create a
second ERP order. Stop new cohort traffic, drain or quarantine in-flight operations, query ERP outcome by operation ID,
and repair missing confirmations from the authoritative record. If the new service has written a status that the old
path cannot read, implement a tested reverse projection or use a forward-fix plan; a traffic switch alone is not data
rollback. Keep the old adapter and route runnable until the observation and rollback window closes. Microsoft notes that
parallel deployment can aid fallback but introduces data synchronization and decommissioning
work. [Microsoft modernization planning](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/modernize/plan-cloud-modernization).

## 7. Test what must remain true

Test business invariants: one ERP booking per intended order; amount and currency preserved; no release without booking;
cancellation applied to the correct version; and every accepted request reaches a terminal or approved pending state.
Run old consumers against generated records and new readers against historical events. A schema diff misses changed
meaning and unknown consumers.

Use mapping golden files, contract checks, ERP integration tests, failure injection, peak and recovery load, security
checks, operator rehearsal, and business acceptance. Distinguish simulated from production-like tests. For critical
routes, cover a closing cycle and ambiguous ERP timeout. Maintain a known-differences register so comparison noise does
not hide faults.

Name the parallel mode. **Shadow computation** compares decisions without side effects. **Parallel projection** compares
derived views from one authoritative write. **Dual publication** sends old and new notifications from one business
event, with identities that prevent double processing. **Dual write** to two authoritative systems needs proven
idempotency, ordering, reconciliation, and conflict ownership.

## 8. Dual-run reconciliation and controlled cutover checklist

**Illustrative acceptance thresholds:** For the critical booking example, require 14 consecutive days scheduled to
include peak traffic and a closing cycle; 100% of accepted requests matched to an ERP terminal or approved pending
state; zero unexplained duplicate bookings or unauthorized releases; zero unowned financial differences; and p99
decision latency within the agreed 20-minute business target. Numeric thresholds are examples. The business owner, not
the architecture team alone, approves tolerance for late nonfinancial records. Row counts alone are insufficient:
compare business keys and values. Database migration tooling illustrates that source/target validation compares records
and consumes additional source/target capacity; plan reconciliation load
accordingly. [AWS DMS validation guidance](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html).

| Step                           | Evidence or action                                                                                                                                                                                                                                                                                                    | Accountable owner                                                                                                    |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| **1. Define comparison**       | List authoritative system for each field; match by stable operation and ERP order IDs. Normalize only approved differences such as timestamp precision. Compare counts **and** per-order amount, currency, status, version, and confirmation presence.                                                                | Business data owner and integration lead.                                                                            |
| **2. Classify every mismatch** | Missing, duplicate, divergent value, late within settlement window, or ambiguous outcome. Preserve source records and transform version. Set severity and repair deadline; no silent suppression.                                                                                                                     | Reconciliation lead; finance owner for monetary differences.                                                         |
| **3. Prepare cutover**         | Confirm contract tests, peak/load tests, backfill, access, capacity, dashboards, support notice, change window, frozen configuration, active writer per cohort, and named incident commander. Rehearse route reversal and in-flight drain.                                                                            | Service owner signs; operations lead executes.                                                                       |
| **4. Establish baseline**      | Snapshot route configuration, offsets/checkpoints, in-flight IDs, last old-path sequence, ERP totals, and unresolved discrepancy list. Verify the old route remains runnable.                                                                                                                                         | Operations and data owners.                                                                                          |
| **5. Canary and ramp**         | Move one cohort; compare requests, ERP outcomes, new events, and old-format confirmations. Hold at each ramp step for a business-relevant interval; monitor customer outcomes, p99 latency, retries, adapter errors, queue age, and mismatches.                                                                       | Operations lead with business owner.                                                                                 |
| **6. Trigger stop/rollback**   | Stop expansion for any duplicate booking, unauthorized release, lost accepted request, unowned money mismatch, broken old consumer, sustained target breach, or inability to determine ERP outcome. Pre-agree numeric latency/error limits from baseline. Route *new* requests back only after in-flight disposition. | Incident commander declares; service owner approves traffic reversal.                                                |
| **7. Correct data**            | Query source of truth; use an approved, audited correction manifest with affected IDs, before/after state, operator, and approval. Reissue missing notifications only after confirming booking. Never replay ambiguous writes blindly.                                                                                | ERP/business record owner authorizes; designated data repair operator executes; finance validates money corrections. |
| **8. Close observation**       | Reconcile again after late arrivals and closing cycle; verify no unknown effects or unowned exceptions. Archive evidence, update catalog and runbook, notify consumers, then schedule old-route retirement separately.                                                                                                | Business owner accepts; operations owns ongoing support.                                                             |

**A rollback trigger is a decision rule.** Account for accepted requests, in-flight messages, and records already
published. Audit manual corrections so two teams do not “fix” the same order. If shipment or invoicing occurred, code
rollback cannot undo it; use approved cancellation, reversal, or forward correction.

## 9. Ownership, exceptions, and risk management

The **business capability owner** defines acceptable outcomes, criticality, correction policy, and cutover acceptance.
The **producer/service owner** owns the contract, change, SLO, idempotency, and compatibility adapter. **Consumer owners
** declare dependencies, test their behavior, and migrate. **Platform** supplies routing, catalog, schema checks,
observability, and repeatable deployment controls. **Operations** owns production execution, monitoring, rollback
rehearsal, and incident response. **Data/finance owners** authorize corrections to authoritative records. **Security and
compliance** review access, retention, audit, and regulated windows. An architecture board can resolve cross-domain
trade-offs, but cannot substitute for an operational owner.

Keep a risk register with probability, impact, evidence, mitigation, trigger, owner, and review date. A retained
interface needs an on-call owner, contract, access review, telemetry, reconciliation, runbook, and re-evaluation date.
Retention is responsible when change during financial close adds greater risk, a consumer is contractually frozen, or
write behavior is unknown. Record its cost and residual risk.

An all-at-once rewrite could be justified only if the old estate has an indivisible dependency boundary, incremental
seams are technically impossible or more dangerous, a hard external event forces replacement, and the business can
tolerate the outage and recovery model. Even then, require full inventory, production-like rehearsal, data validation,
capacity proof, dual-run where safe, a frozen source or write authority, an explicit rollback/forward-repair boundary,
and executive acceptance of residual loss and downtime. Without those conditions, the organization is betting business
continuity on one unverified event.

## 10. Interview follow-ups and model answers

**“The CTO says all 50 must be replaced in one year. What do you say?”** “I would align on the outcome behind the date:
lower incident risk, faster change, cost reduction, or vendor exit. In the first six to eight weeks I would validate all
50 routes and critical dependencies, then publish waves and measurable gates. We can commit to a disposition and
governed owner for every route by year-end; I would only commit to physical retirement of each route after consumer and
data evidence. I would show monthly counts of migrated, retired, and retained exceptions, plus incident and
reconciliation trends. If the date is a legal shutdown, I would fund temporary compatibility and contingency capacity
and escalate any impossible dependency early.”

**“The most critical interface cannot be changed. Can you still modernize?”** “Yes, if I can create a safe seam around
it. I would treat its contract and write authority as fixed, use an ACL or adapter to isolate its semantics, modernize
adjacent consumers and operational controls, and keep one active writer. I would add traffic visibility and
reconciliation first. If even a façade risks the interface, leave the critical path in place and migrate independent
routes. I would document the residual risk, owner, and date to revisit it rather than call a wrapper a replacement.”

**“Budget is cut by 30%. What is the first thing you remove?”** “I would re-score the portfolio using business value and
risk, retire genuinely unused feeds, and reuse a small set of contract, test, routing, and telemetry patterns. I would
delay cosmetic protocol conversions and low-value rewrites. I would protect discovery of critical consumers,
reconciliation, rollback rehearsal, and operational ownership because removing those savings creates incident and
data-correction costs. I would give leadership two explicit scopes with cost, residual risk, and achievable exit
criteria.”

**“There is a production incident during Wave B. Continue the planned cutovers?”** “Pause expansion, declare an incident
with one commander, stabilize the current writer and route, and identify affected business IDs. Reconcile
source-of-truth outcomes, classify ambiguous writes, and correct data under the named owner. Roll back only new traffic
where safe; do not replay completed bookings. Resume after the cause is understood, the test/runbook gap is fixed, and
the business owner accepts a fresh canary. If the incident is unrelated, prove that with evidence before continuing.”

## 11. Five-minute exercise with answer key

**Prompt:** You inherit 50 point-to-point routes. A nightly customer-address file feeds billing, shipping, and
analytics. Billing and shipping can migrate this quarter; analytics is owned by a partner and cannot change for six
months. The old file occasionally drops records without an error. Propose the first wave, compatibility path, comparison
method, cutover gate, and rollback trigger. State one assumption you would verify.

**Model answer:** “I would confirm the CRM's write authority, stable customer ID, effective-date semantics, and impact
of late changes. I would inventory all three consumers, quantify file drops, and reconcile by customer ID and change
version. Billing and shipping get an owned address-change contract; an ACL translates old codes. An adapter generates
the unchanged partner file from the same authoritative change and has an owner and six-month review date. I would
shadow-compare outputs, then canary one consumer. Cutover requires no unexplained lost changes, correct effective dates,
partner compatibility, and an operator runbook. A missing billing change or wrong effective date stops expansion. Before
routing back, check which changes each consumer applied; never resend an entire file blindly.”
