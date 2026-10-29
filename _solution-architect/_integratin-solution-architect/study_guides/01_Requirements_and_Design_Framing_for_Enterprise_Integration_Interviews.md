# Requirements and Design Framing for Enterprise Integration Interviews

**Audience:** Senior or principal Enterprise / Integration Solution Architect  
**Purpose:** Turn an ambiguous business request into a defensible problem statement and design criteria before drawing
components.  
**Example policy:** All companies, volumes, dates, targets, and platform conditions below are illustrative assumptions
for practice. They are not employer requirements or claims about the reader's experience.

## 1. Start with the promise the business is making

An interviewer may open with: “Connect our e-commerce platform to ERP, CRM, warehouse, and finance.” That names systems,
not a design problem. A useful opening response is: “I will clarify the customer promise, the owner of each decision,
the volume and failure targets, and the boundaries we must cross. Then I can state what the integration must guarantee.”
This gives the interviewer a reason to answer questions and shows you can control scope without pretending every fact is
known.

First identify the **outcome** and the person who measures it. “Reduce abandoned checkouts” differs from “eliminate
manual re-entry,” even if both involve an order interface. Ask who is affected: shopper, contact center, operations,
finance, compliance, and support. Identify a business owner who can choose between speed, accuracy, and cost when those
conflict. Translate the outcome into observable behavior: “A shopper receives an order number and a precise status”;
“finance can reconcile every accepted order to an invoice or an exception”; “operations can see orders stuck beyond the
agreed time.” Avoid turning these into implementation choices yet.

Next define the **business event** and its completion point. “Order accepted” might mean (A) the storefront durably
recorded a request, (B) stock and credit were validated, or (C) ERP created a sales order. These are different promises.
Ask whether an order can later be declined, whether the customer may be charged before fulfillment, and what message the
customer sees during a downstream outage. If acceptance requires ERP approval, ERP latency and availability sit on the
checkout path. If acceptance means durable receipt, ERP processing can occur later, but the UI must say “received” or
“pending validation” until the stronger condition is met. Never hide a weaker promise behind a stronger status label.

Frame each functional requirement as an actor, trigger, input, decision, observable result, and failure behavior. For
example: “When an authenticated shopper submits a cart, the order capability validates required fields, records a unique
request, and returns an order reference; a retry with the same business intent does not create another order.” Then ask
whether prices, tax, inventory, customer eligibility, fraud, and credit must be checked before that response. The
answers determine which data must be current and which owners must participate.

## 2. The first ten minutes at the whiteboard

Use the clock to prioritize questions that change the design. Write the answers in a small “confirmed / assumed / open”
corner of the board. If the interviewer withholds a detail, state a reversible assumption and proceed.

| Time       | Ask or do                                                                                                         | What the answer changes                                                                                                 |
|------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| 0:00–1:00  | “What business result is this meant to improve, and who owns the decision?”                                       | Defines success measure, trade-off authority, and whether checkout, operations, or reporting dominates.                 |
| 1:00–2:15  | “What does the user see when we say **accepted**? Can it later be rejected?”                                      | Defines the transaction boundary, response status, customer wording, and whether downstream validation may be deferred. |
| 2:15–3:15  | “Which actions are in scope: create, update, cancel, return, refund, and reconciliation?”                         | Prevents a vague “order integration” from silently including every lifecycle flow.                                      |
| 3:15–4:30  | “Who owns order identity, price, customer, available inventory, shipment, and financial posting?”                 | Exposes conflicting authorities, duplicate records, mapping rules, and where an invariant must be checked.              |
| 4:30–5:45  | “What is normal volume, peak rate and duration, payload size, and expected growth?”                               | Sizes capacity and buffers; separates daily totals from the actual burst to design for.                                 |
| 5:45–7:00  | “What are response-time and propagation deadlines, availability, recoverable data loss, and restoration targets?” | Defines synchronous dependency budget, backlog tolerance, resilience, and recovery investment.                          |
| 7:00–8:00  | “What sensitive data crosses which organization, cloud, or network boundary?”                                     | Determines identity, authorization, encryption, audit, residency, and security review scope.                            |
| 8:00–9:00  | “Which platforms, licenses, skills, contracts, and delivery dates are fixed?”                                     | Rules out designs the organization cannot operate or deliver; highlights procurement and partner lead times.            |
| 9:00–10:00 | Restate the problem, assumptions, and top two open decisions; request correction.                                 | Creates a reviewable contract for the rest of the interview.                                                            |

Ask for ranges if exact numbers are unavailable: “Is peak tens, hundreds, or thousands of orders per second?” Ask for *
*duration** as well as rate; a five-second burst and a four-hour promotion stress different resources. Ask what happens
when a dependency is down for six hours: stop taking orders, accept pending orders, or use a controlled fallback? That
answer often matters more than the preferred technology.

## 3. Make nonfunctional requirements testable

“Fast,” “highly available,” and “no data loss” are prompts for negotiation, not design criteria. Give each target a
measurement boundary, percentile or time window, and a named owner. Keep customer-facing response time distinct from
downstream completion time. Define the point at which an operation counts as successful and how exceptions are counted.

| Dimension                | Question and testable expression                                                                                                                                                                                                                                                                                                                                                                         |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Throughput and peak load | Orders per day **and** maximum accepted orders/second for a stated duration; line items, payload size, burst factor, and growth horizon. Check whether updates and retries multiply traffic.                                                                                                                                                                                                             |
| Latency                  | For example, p95 checkout acknowledgement under 2 seconds and p99 under 5 seconds at the stated peak, measured from edge receipt to response; separately, 99% of accepted orders visible to ERP within 5 minutes during normal operations. Both are provisional until business confirmation.                                                                                                             |
| Availability             | For example, 99.95% monthly availability for **order intake**, excluding or including planned maintenance as explicitly agreed. State whether a degraded “pending” response counts as available. Do not reuse this number for end-to-end fulfillment.                                                                                                                                                    |
| Durability               | Specify which accepted facts must survive a process failure or site loss. “No acknowledged order disappears” requires evidence in the write and recovery path, not just a reliable-sounding product name.                                                                                                                                                                                                |
| RPO and RTO              | RPO is the recoverable point of data after disruption; RTO is the maximum resource outage before unacceptable impact. Ask separately for order intake, downstream processing, and reporting. See [NIST SP 800-34 Rev. 1](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final).                                                                                                                            |
| Retention                | Identify operational, audit, customer, and finance records; set periods, deletion triggers, and legal holds with the data owner. Do not treat a queue's retention as the business archive.                                                                                                                                                                                                               |
| Compliance and security  | Identify jurisdictions, regulated data, contractual controls, access roles, audit evidence, and residency. Have legal and security confirm applicability. For example, GDPR's storage limitation and security provisions may matter for EU personal data; applicability cannot be inferred from the system names alone. [EU GDPR, Articles 5 and 32](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng). |
| Cost                     | Obtain a monthly run-rate ceiling, change budget, and cost-per-order view at normal and peak load. Include existing license terms, support, observability, network transfer, and operational labor in the estimate.                                                                                                                                                                                      |

The NFRs are coupled. A zero-loss promise for acknowledged orders may demand a stronger durable write and tested
recovery; a two-second acknowledgement may forbid a slow ERP round trip. If both are demanded, challenge the semantics
or obtain investment for a genuinely fast and resilient authoritative validation path. Interview strength lies in naming
this tension early.

## 4. Map ownership and boundaries before drawing connections

For each business fact, record its **system of record**, the owner who can change it, the point when it becomes
authoritative, and the consumers that need a copy. Distinguish a source of truth from a cache or view. An ERP may own
the commercial order while the storefront owns a submission record. A warehouse may own physical pick and ship facts
while ERP owns sellable inventory. Two systems can each own different fields of a “customer” object; saying “CRM owns
customer” is too coarse.

Mark trust boundaries explicitly: public client to enterprise edge; application to internal services; cloud to
on-premises; enterprise to SaaS; enterprise to partner; production to analytics. At each boundary ask who authenticates
the caller, which identity is propagated, who authorizes the business action, what data is exposed, and who operates the
connection. Note whether a return path is possible, whether a private network link exists, and who approves firewall or
allowlist changes. A diagram that shows an arrow across a boundary without these answers is incomplete.

Constraints deserve the same visibility as requirements. Record the installed platforms and supported versions, existing
licenses, team operating skills, support model, procurement timing, vendor or partner change windows, and delivery date.
Ask which are genuinely fixed and which are preferences. A delivery deadline can make a staged scope more credible than
a replacement of every integration. A license can make a platform economical, but only after its capacity, support, and
operating fit are checked.

### One-page requirements worksheet

Use one sheet or one whiteboard panel. Fill blanks with **TBD + owner + decision date**, rather than invented precision.

| Field                      | Capture in a phrase or number                                                                                 |
|----------------------------|---------------------------------------------------------------------------------------------------------------|
| Business outcome / sponsor | Desired measurable change; accountable decision-maker; affected users and operations teams.                   |
| In-scope journey           | Trigger → required validations → promised response → later states → exceptions; explicit exclusions.          |
| Acceptance meaning         | Exact condition for “received,” “accepted,” “confirmed,” and “fulfilled”; whether later rejection is allowed. |
| Scale                      | Normal/day; peak/second and duration; payload; retry/update multiplier; growth horizon.                       |
| Service targets            | Acknowledgement p95/p99; downstream deadline; intake availability; degraded-mode rule.                        |
| Recovery and records       | Durability point; RPO/RTO per capability; backlog catch-up; reconciliation; retention and deletion owner.     |
| Data ownership             | IDs and authoritative owner for order, price, customer, inventory, shipment, payment, invoice.                |
| Boundaries and controls    | Public/internal/SaaS/on-prem/partner crossings; sensitive fields; identity; residency; audit.                 |
| Delivery constraints       | Existing platforms, licenses, skills, support hours, migration dependencies, date and budget.                 |
| Decision gate              | Top unresolved questions, owner and due date; assumptions that would change the design.                       |

### Assumptions, risks, and decisions log

Keep these categories separate. An **assumption** is a temporary input to design; a **risk** is a possible adverse
outcome with likelihood and impact; a **decision** selects a course of action and records why. In an interview, a
compact log makes uncertainty visible without stalling.

| ID / type          | Statement                                                                | Why it matters                                                 | Owner / next evidence                          |
|--------------------|--------------------------------------------------------------------------|----------------------------------------------------------------|------------------------------------------------|
| A1 / assumption    | “Accepted” means durable storefront receipt; ERP may validate afterward. | Allows a short response path; requires honest pending status.  | Product sponsor confirms customer promise.     |
| R1 / risk          | ERP outage may create a backlog that misses shipping cutoffs.            | Needs quantified outage and catch-up criteria.                 | Operations supplies cutoff and outage history. |
| D1 / decision      | Use separate “received” and “confirmed” statuses for the exercise.       | Avoids claiming inventory or credit approval before it exists. | Revisit if immediate validation is mandatory.  |
| O1 / open decision | Who may override a stock mismatch, and which record wins?                | Changes exception workflow and audit responsibility.           | ERP and warehouse owners agree policy.         |

### System and data ownership matrix

This is an **illustrative hypothesis**, to be validated with application owners. “Writes” means the system is allowed to
create or correct the authoritative fact; other systems may hold copies.

| Business fact                             | Proposed authoritative owner                        | Other users / copies     | Clarify before design                                      |
|-------------------------------------------|-----------------------------------------------------|--------------------------|------------------------------------------------------------|
| Submission ID and customer-facing receipt | E-commerce/order intake                             | ERP, CRM, support        | Does receipt imply a commercial order?                     |
| Sales order number and commercial status  | ERP                                                 | E-commerce, CRM, finance | Can ERP reject a received order?                           |
| Customer contact and consent              | CRM                                                 | E-commerce, support      | Does another master own legal identity or billing account? |
| Price and tax at commitment               | ERP or dedicated pricing/tax owner — **unresolved** | E-commerce, finance      | Which quote is binding, and for how long?                  |
| Sellable inventory / allocation           | ERP — **assumed**                                   | E-commerce, warehouse    | Is allocation real-time or batch, and who can release it?  |
| Pick, pack, shipment and physical stock   | Warehouse system                                    | ERP, e-commerce, CRM     | Which event proves shipment and what if scans are late?    |
| Invoice, ledger posting, settlement       | Finance system                                      | ERP, support             | Which system creates the invoice and reversals?            |

## 5. Same request, two different architecture problems

**Scenario A — immediate validation required.** Assumption: the business promises “confirmed order” only after current
stock allocation and credit eligibility are approved. The interviewer says a later rejection is unacceptable. The
response path therefore depends on authoritative validation or a delegated reservation capability with well-defined
authority. Ask for its latency and availability budget, how an ambiguous timeout is resolved, and whether a temporary
hold is permitted. A dependency outage may force a clear “unable to confirm” response rather than a false success.
Record the exact committed state and how to prevent duplicate allocations on retries. This drives a tighter cross-system
contract, stronger failure handling, and likely a lower achievable checkout availability unless the authoritative
service is highly resilient. It does **not** dictate a particular API, broker, or vendor.

**Scenario B — eventual downstream propagation allowed.** Assumption: the business accepts “request received”
immediately and permits ERP to confirm or reject later. The intake path must durably store the request and return a
stable reference; the customer can view “pending validation.” ERP, CRM, warehouse, and finance receive only facts
appropriate to their stage. Set a propagation deadline, a maximum backlog, a policy for late rejection, and a
reconciliation owner. An ERP outage need not stop intake if the business accepts growing pending work and storage
capacity is planned. The design now needs explicit status transitions and operational exception handling; it still
cannot call an order “confirmed” until the required authority says so.

The decisive interview move is to say what changed: **acceptance semantics altered the dependency on the response path,
the failure promise, and the NFR boundary**. The technology discussion follows from those criteria.

## 6. Worked exercise: five-system order flow

**Ambiguous prompt:** “Our website needs to send orders to ERP, keep CRM updated, tell the warehouse what to ship, and
get transactions into finance. It must be real-time and never lose an order.”

**Clarify the words first.** Ask the sponsor whether “real-time” means checkout acknowledgement, ERP creation, warehouse
release, or finance visibility. Ask what “order” means at each stage and who can reject it. Ask whether card payment
authorization or capture is in scope; do not infer a payment processor from the prompt. Ask for cancellation, returns,
partial shipment, and duplicate submission rules. Ask which system supplies customer identity, prices, tax, inventory,
and account credit. Request peak timing, shipping cutoffs, allowed data loss, and outage behavior. These questions turn
a slogan into bounded obligations.

**Illustrative answers supplied for practice, not employer facts:** The storefront may acknowledge durable receipt
before ERP confirmation; ERP can reject invalid price or stock. CRM needs an order status view, warehouse acts only on
ERP-confirmed orders, and finance records invoice and settlement after the appropriate commercial event. Assume 120,000
submissions on an ordinary day, a promotional peak of 100 submissions/second for 30 minutes on a higher-volume day,
three line items/order, and 2× retry traffic during an incident. Assume a 12-month growth horizon of 2×. The peak window
alone contains 180,000 submissions; incident traffic could reach 200 request attempts/second, and line-item processing
roughly 300 lines/second before retries. These are capacity inputs, not a platform selection.

**Candidate design criteria to confirm:** p95 receipt under 2 seconds and p99 under 5 seconds at the stated peak; 99% of
received orders reach an ERP outcome within 5 minutes in normal operation; order intake availability of 99.95% per
calendar month; no loss of an acknowledged receipt after a single service failure; proposed RPO of zero acknowledged
receipts and RTO of 15 minutes for intake after a site-level disruption. These last two are ambitious provisional
targets, requiring recovery evidence and cost review. A 99.95% target allows about 22 minutes of unavailability in a
30-day month, so one 15-minute recovery would consume most of that allowance. During a six-hour ERP outage, intake may
continue in “pending” status **only if** the sponsor accepts delayed confirmation; at 100 new orders/second throughout
that outage, the worst-case backlog is 2.16 million orders, so storage, catch-up time, shipping cutoff, and customer
communication must be revisited. A promotion peak lasting only 30 minutes does not justify assuming six hours at peak
without asking.

**Records and controls:** Assume operational order details are retained for 90 days and financial records for seven
years **solely as placeholders**; legal, records, and finance owners must set actual periods and deletion rules.
Classify customer contact and order details; determine whether any regulated payment data enters these flows. Map
public-to-edge, cloud-to-on-prem ERP, cloud-to-CRM SaaS, and enterprise-to-warehouse/finance boundaries. Confirm the
allowed connectivity, identity, audit, and regional handling at each crossing. For cost, require a forecast of monthly
fixed and variable run rate and cost per 1,000 receipts at ordinary and 2× volume. The sponsor must still supply the
spending ceiling and license terms.

**Problem statement to put on the board:** “Provide a durable, traceable order-receipt capability for the e-commerce
channel. Return a stable receipt within the agreed latency at promotional peak. ERP owns confirmation or rejection; only
confirmed orders become eligible for warehouse fulfillment, while CRM receives an appropriate customer view and finance
records its authorized business events. Preserve acknowledged receipts through defined failures, expose pending and
exception states, meet a negotiated propagation deadline, and reconcile every receipt to an ERP outcome. Confirm
ownership, recovery, retention, security, and cost targets with the named business and system owners.”

**Unresolved decisions that could change the design:** (1) Does checkout need stock or credit approval before any
success response? (2) Which system owns binding price and inventory allocation? (3) What is the maximum acceptable
pending time and late-rejection policy? (4) Does a six-hour ERP outage permit continued intake, and what shipping cutoff
applies? (5) What are the actual legal retention and data-residency obligations? (6) What monthly cost and delivery date
are binding? Put these next to the problem statement. Do not draw a definitive component map until the first two are
answered or explicitly assumed.

## 7. Interviewer follow-ups: practice your response

| Follow-up                                                                          | Model response                                                                                                                                                                                                                                                   | Common weak response                                                   |
|------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| “The business says no order can ever be lost. What does that mean?”                | “I would define the acknowledgement point and failure scope. Once we issue a receipt, can we recover its content and status after a process, node, or site failure? I would seek an RPO and test the recovery path, plus reconciliation for uncertain outcomes.” | “The broker guarantees zero loss.”                                     |
| “ERP is unavailable for six hours during a promotion. Do you still accept orders?” | “Only if the sponsor permits pending orders. I would calculate backlog from the actual peak duration, state a customer-facing status, protect capacity, set a catch-up deadline, and define the cutoff and exception owner.”                                     | “We queue everything, so there is no impact.”                          |
| “Can you make this real-time?”                                                     | “Which observable deadline matters: checkout receipt, ERP outcome, warehouse release, or finance posting? I would assign each a percentile or deadline and measure it at that boundary.”                                                                         | “Yes, we will use events.”                                             |
| “Both CRM and ERP edit customer addresses. Which wins?”                            | “I would separate contact, shipping, and billing address ownership and ask whether changes are effective for existing orders. Then define conflict and correction rules with business owners.”                                                                   | “We synchronize bidirectionally.”                                      |
| “We have an integration platform license and a three-month deadline. Use it?”      | “I would check supported capabilities, throughput, operating skills, contract limits, and change lead time. If it meets the criteria, reuse reduces delivery risk; if not, I would expose the gap and propose a staged scope.”                                   | “Always use the existing platform,” or “replace it with a modern one.” |

### Self-scoring rubric

Score each dimension **0–2**: 0 = absent or asserted without evidence; 1 = mentioned but unmeasured or ownerless; 2 =
explicit, testable, and tied to a design consequence. **16–20:** ready to frame; **11–15:** revisit gaps; **0–10:**
repeat the exercise before drawing components.

| Dimension                | A two-point answer shows                                                           |
|--------------------------|------------------------------------------------------------------------------------|
| Outcome and stakeholders | Business success, affected users, and decision authority.                          |
| Acceptance semantics     | Exact meaning of receipt/confirmation and later rejection rule.                    |
| Functional scope         | Lifecycle actions, required validations, and exception behavior.                   |
| Scale                    | Normal and peak rate, duration, payload, retries, growth.                          |
| Latency and availability | Separate customer and downstream measures with measurement boundaries.             |
| Durability and recovery  | Acknowledgement point, failure scope, RPO/RTO, reconciliation.                     |
| Data ownership           | Field-level authority, IDs, copies, conflict owner.                                |
| Trust and compliance     | Boundaries, sensitive data, control owners, applicability questions.               |
| Delivery and cost        | Platforms, licenses, skills, date, operating budget.                               |
| Communication            | Concise problem statement, labeled assumptions, and highest-impact open decisions. |

**Final whiteboard check:** Can another architect read your problem statement and know what must be true at the moment
of acknowledgement, what may finish later, who owns each fact, which failures are tolerated, and how success will be
measured? If yes, the design conversation can begin. Detailed API contracts, broker choices, Saga mechanics, cloud
topology, and recovery implementation belong in later study, once these criteria are agreed.
