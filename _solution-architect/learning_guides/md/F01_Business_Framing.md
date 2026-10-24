# F01 — Business Framing, Requirements, and Quality Attributes

**Complete progressive reference guide | Topic map v3 | Prepared 2026-10-24**  
**Status:** Reference document, not a live lesson or a completed assessment.  
**Target:** Beginner foundations → senior Solution Architect interview reasoning.  
**Scope:** F01 only: **C014, C015, C016, C017, C018**, all **Core**.  
**Authority:** `__interview_topic_map_v3.md`, section **F01** and its learning/assessment rules.

> **Important ID correction — Source requirement:** The request names `B01 (C014–C018)`. In the authoritative map, **B01
has C001–C004** (software/Python basics), whereas **F01 has C014–C018**. This guide follows **F01/C014–C018** without
> adding B01's software curriculum. No syllabus IDs have been reassigned.

## How to use this reference

Read lessons **L01 → L17** in order. For each lesson, use the sequence **understand → explain → demonstrate → practice →
evaluate → memorize**. Work through its example, finish its exercise without looking at the solution, use the answer key
only afterward, then answer its interview follow-up aloud. A lesson is **not passed** simply because you read it. The
goal is to explain, apply, and defend a trade-off **without notes**. The cumulative brief and senior decision challenge
come after the lessons.

**Source labels used throughout:**

- **[Source requirement]** = mandatory scope or teaching/assessment rule from topic map v3.
- **[Verified external fact]** = supported by an identified primary source `[R#]` in the references, checked
  **2026-10-24**.
- **[Hypothetical practice assumption]** = fictional actors, business rules, targets, budgets, measurements, or
  scenarios. Never treat them as American Express or industry commitments.
- **[Recommendation]** = a proposed method or professional judgment. Test against a real organization before adoption.

**[Source requirement]** The map's role label is *Sr Solutions Architect I, American Express Global Commercial
Services*. The exact vacancy, company internal standards, interview format, and technology stack are **not independently
verified**. This guide does not claim to describe them. The exercise is fictional; a public American Express page is
optional domain context only [R7].

### What is inside and outside F01?

**Inside:** discover the business problem and target outcome; distinguish customers and users; map journeys and
stakeholders; elicit and classify requirements; specify and rank availability, latency, security, data freshness, and
changeability; connect business key performance indicators to technical measures; defend trade-offs and owners.

**Outside:** implementation-level component diagrams and architecture decision records (F02); detailed
commercial-payment rules (D01/D02); network/API implementation (B02/T03); detailed data models (B03/T05);
security-control design (T06); production service-level-objective engineering (T07); advanced Python (T11). We use
minimal terminology only where F01 needs it.

## Prerequisite check — before L01

**No prior business-analysis knowledge is assumed.** You only need to understand these everyday words:

| Word      | Simple meaning                                      | Example                                                                |
|-----------|-----------------------------------------------------|------------------------------------------------------------------------|
| Business  | An organization providing products or services      | A company buys office supplies                                         |
| Customer  | A person or organization receiving value            | A company buys a spending-management service                           |
| Goal      | Something the organization wants to achieve         | Reduce manual expense reviews                                          |
| Problem   | Something stopping the goal                         | Transactions appear too late for finance                               |
| System    | People, processes, and/or software working together | A spending-control service and the people using it                     |
| Data      | Recorded facts                                      | Purchase amount and event time                                         |
| Measure   | A number or observation used to judge results       | Minutes until a purchase becomes visible                               |
| Trade-off | Gain one benefit by giving up some other benefit    | Faster display can mean showing preliminary, not verified, information |

**Prerequisite questions (P0; self-check):** (1) What is the difference between a business goal and a software feature?
(2) Why can two users of one system have different needs? (3) Why is “make it fast” not enough to test a solution?
Answers are in **AK-P0**.

## Running case and scope of assumptions

**[Source requirement]** The map defines a hypothetical commercial platform in which business administrators set
spending rules, employees initiate purchases, finance teams view and reconcile transactions, and the platform connects
to identity, risk, payment, and reporting capabilities.

**New words:** A **spending rule** is a business limit on spending. **Identity** establishes which user is acting.
**Risk checks** assess whether an activity requires more review. **Payment** here means the business capability involved
in handling the purchase; its internal processing is deliberately unspecified. **Reporting** displays recorded
transactions. **Reconciliation** means checking that two sets of relevant records agree and investigating differences.
An **integration** is a connection between capabilities. No technical integration design is required in F01.

**[Hypothetical practice assumptions]** Our fictional client is **Northstar Office Group**, which has multiple employee
teams. Its administrators can define a spending policy; employees request purchases; risk may require a check; finance
sees a transaction record and investigates exceptions. The fictional starting complaint is **“Finance cannot see
purchases soon enough.”** No baseline performance or official target has yet been confirmed. All proposed times,
quantities, percentages, costs, and organization roles below are invented for practice and **not claimed as facts**.

**Important distinction:** A **record is visible** when the system displays it. **Verified** means it has passed the
agreed checks. **Final** means the relevant business process has reached a final state; *visibility does not prove final
payment or settlement*. The detailed financial lifecycle belongs to D02.

```text
Business administrator --sets rules-->
                                      [Fictional spending platform]
Employee -------------requests------> [   policy / status      ]
Finance ---------------reads--------> [   transaction view     ]
                                          |      |      |      |
                                      identity  risk  payment reporting
                                  (external capabilities; no design assumed)
```

---

# Module A — Understand the business and its users (C014)

## L01 — Customer types versus user roles

**Checklist:** C014 · **Assessment:** A01.

### 1. Purpose and prerequisites

**Purpose:** Know *who receives value* and *who does the work* before choosing a solution. Requires only the
prerequisite definitions above.

### 2. Terms and fundamentals

- **Customer type** groups customers by a meaningful need or context: for example, a small organization and a
  multi-department enterprise. These are *segments*, not verified Amex categories.
- **User** is the person interacting with a solution. **User role** is what that person is allowed or expected to do in
  a particular task.
- **Persona** is a short, evidence-based description of a user type. A fictional persona can help practice, but do not
  mistake it for customer research.
- **Buyer**, **payer**, and **user** need not be the same person. The buyer chooses the product; the payer funds it; a
  user operates it.
- **Need** is the problem to solve. **Feature** is one possible capability provided by software. A feature does not
  automatically prove value.

**[Verified external fact]** The International Institute of Business Analysis (IIBA) defines end users and stakeholders
separately, and distinguishes business needs from solution features [R1].

### 3. Worked example — step by step

| Category                  | Fictional example                  | Need, not feature                           |
|---------------------------|------------------------------------|---------------------------------------------|
| Customer type: small firm | One office, one finance generalist | Fewer manual checks                         |
| Customer type: enterprise | Many departments and reviewers     | Consistent spending governance across teams |
| Administrator role        | Sets spending limits               | Prevent unauthorized spending               |
| Employee role             | Requests a purchase                | Know quickly whether to proceed             |
| Finance role              | Checks transaction records         | Trust timely, correct information           |

**Walkthrough:** (1) First identify the paying organization as customer. (2) Divide customers only where the need
changes. (3) List roles within that organization. (4) State one job and expected outcome for each role. (5) Do not
assume every employee can change a limit: a *role* is not automatically a permission.

### 4. Guided exercise E01

**Goal:** Separate three customer types/roles without guessing permissions. **Steps:** For a university with several
departments, write the *customer organization*, two possible user roles, each role's need, and one unresolved permission
question. **Expected:** One customer type, two roles, two needs, one open question. **Hint:** “Who pays?” and “Who
uses?” differ.

### 5. Failure, detection, recovery, trade-off

**Failure:** You call “finance” the customer and ignore employees. **Detection:** Employee needs vanish from acceptance
discussions. **Recovery:** Map buyer and every operating role. **Trade-off:** More segmentation improves fit but makes
discovery and support more complex. Segment when user needs materially differ.

### 6. Interview Phrasing

> “I separate the customer organization from the users and their roles. That helps me test whether the solution meets
> both the buyer’s outcome and the day-to-day needs of administrators, employees, and finance.”

**Plain English:** A company buys the solution; several people use it for different jobs. **Follow-up F01:** Can one
person have two roles? What must you verify? **Answer check:** AK-E01/F01.

## L02 — Business capabilities, not technology boxes

**Checklist:** C014 · **Assessment:** A02.

### 1. Purpose and prerequisites

**Purpose:** Describe what the organization must be able to do without prematurely choosing software. Requires L01's
customers and roles.

### 2. Terms and fundamentals

- A **business capability** is an ability the organization needs, such as *manage spending policies*. It answers
  **what**, not necessarily **how**.
- A **business process** is an ordered series of tasks: *request → check → decide*.
- A **feature** is a software behavior such as a “Change limit” button.
- A **capability map** groups related abilities; it is not a deployment diagram.

**[Verified external fact]** The IIBA glossary describes capabilities and business processes as different concepts [R1].

### 3. Worked example — step by step

```text
Desired outcome: Control employee spending and reduce manual review
    |
    +-- Manage spending policies       [business capability]
    |     +-- define / update policy    [business activities]
    +-- Check purchase requests
    |     +-- apply policy to request
    +-- Show transaction information
    |     +-- label status and time
    +-- Investigate discrepancies
          +-- review unmatched records
```

(1) Start with a *business outcome*. (2) Name capabilities as verb+noun: “Manage policies.” (3) Name activities needed
inside them. (4) Avoid implementation nouns such as “microservice,” “database cluster,” or “dashboard technology.” (5)
Test each capability by asking which business outcome it supports.

### 4. Guided exercise E02

**Goal:** Produce a small capability map. **Steps:** From the Northstar case, identify four capabilities, one task per
capability, and one user role helped by each. **Expected:** Four capabilities with traceable user value. **Hint:** The
case mentions rules, purchases, records, and exceptions.

### 5. Failure, detection, recovery, trade-off

**Failure:** Treating “build a mobile application” as the business capability. **Detection:** The list says nothing
about why customers need it. **Recovery:** Restate as “Submit purchase request from a device,” then ask if mobile access
is necessary. **Trade-off:** Broad capability maps communicate strategy; detailed ones improve planning but risk
becoming solution designs. Stop at the level needed to frame F01.

### 6. Interview Phrasing

> “I would describe the needed business capabilities first, such as policy management and transaction visibility. That
> keeps the discussion focused on outcomes before we decide how to implement them.”

**Plain English:** Describe the work before picking a tool. **Follow-up F02:** Could one capability be provided by
several systems? **Answer:** AK-E02/F02.

## L03 — End-to-end customer and user journeys

**Checklist:** C014 · **Assessment:** A03.

### 1. Purpose and prerequisites

**Purpose:** Find missing steps, delays, handoffs, and exceptions. Requires L01 roles and L02 capabilities.

### 2. Terms and fundamentals

- A **journey** is the sequence of experiences and actions from a starting need to a meaningful result.
- **Trigger** starts the journey; **touchpoint** is a point of interaction; **handoff** moves work between
  roles/capabilities.
- **Happy path** is the expected successful route. **Exception path** handles failures or special cases.
- **End-to-end** means covering the whole business result, not just one software screen.
- A **pain point** is a step causing delay, confusion, cost, or risk.

### 3. Worked example — step by step

```text
TRIGGER: employee needs office supplies
  1. Employee creates request
  2. Spending rule is checked
     +-- rule allows ------> 3. Purchase may proceed
     +-- rule blocks ------> 3a. Show reason / next action
     +-- review needed ---> 3b. Wait for authorized review
  4. Transaction status becomes available to finance
  5. Finance checks record and resolves any discrepancy
  END: purchase is handled and finance has usable information
```

(1) Name the trigger and the user. (2) Record what they do and what they expect at each step. (3) Show decisions and
exceptions. (4) Mark the transition to finance. (5) Define what “done” means for each user. **No payment-processing
internals are assumed.**

| Step        | Role               | Desired result         | Risk/pain point           | Discovery question                |
|-------------|--------------------|------------------------|---------------------------|-----------------------------------|
| Request     | Employee           | Clear next action      | Unclear rejection         | Is an explanation needed?         |
| Rule check  | Admin/policy owner | Consistent application | Wrong policy              | Which policy version applies?     |
| Status view | Finance            | Reliable information   | Stale or provisional data | What status and age may be shown? |
| Exception   | Finance/risk       | Safe resolution        | Missing owner             | Who decides escalation?           |

### 4. Guided exercise E03

**Goal:** Make an end-to-end journey with an exception. **Steps:** Draw at least five steps from administrator changing
a limit to employee receiving a decision and finance viewing a result. Mark one rejection or review branch, one handoff,
and the distinct outcomes for two users. **Expected:** A journey, not a list of screens. **Hint:** Ask what happens if a
rule change is not yet effective.

### 5. Failure, detection, recovery, trade-off

**Failure:** Ending the diagram at “request accepted” while finance sees nothing. **Detection:** The last step cannot
prove the business outcome. **Recovery:** Walk from first trigger through downstream users and exception resolution.
**Trade-off:** A very broad journey exposes hidden work; too much detail obscures the important decisions. Choose one
high-value journey, then expand the risky steps.

### 6. Interview Phrasing

> “I would map the journey from the user’s first action to the business outcome, including approvals, rejected requests,
> and finance visibility. That reveals handoffs and missing requirements.”

**Plain English:** The system is only successful when the whole task works. **Follow-up F03:** What if the employee sees
‘accepted’ but finance cannot find the record? **Answer:** AK-E03/F03.

---

# Module B — Identify stakeholders and decision authority (C015)

## L04 — Stakeholder map and affected teams

**Checklist:** C015 · **Assessment:** A04.

### 1. Purpose and prerequisites

**Purpose:** Ask the right people; prevent requirements being approved by people who do not own their impacts. Requires
L03 journey and handoffs.

### 2. Terms and fundamentals

- A **stakeholder** is a person/group with an interest in or impact from a change, even if they never use the software.
- **Decision owner** is the role authorized to accept or reject a defined business decision.
- **Affected team** must change its work or absorb an effect. **Consulted team** provides expertise.
- **Sponsor** backs and funds the initiative. **Subject matter expert (SME)** knows an area well.
- **Accountable** means answerable for the outcome; **responsible** means does the work. **Consulted** gives input;
  **informed** receives updates. These form **RACI** (Responsible, Accountable, Consulted, Informed) [R1].

### 3. Worked example — step by step

| Fictional stakeholder   | Need/concern                 | Decision or contribution                                   | Affected? |
|-------------------------|------------------------------|------------------------------------------------------------|-----------|
| Business sponsor        | Lower operating cost         | Funds and owns outcome                                     | Yes       |
| Product owner           | Usable purchase experience   | Prioritizes product needs                                  | Yes       |
| Finance lead            | Current, trustworthy records | Defines finance-visibility acceptance                      | Yes       |
| Risk lead               | Review uncertain purchases   | Owns risk-policy acceptance                                | Yes       |
| Security specialist     | Restrict access              | Advises/approves relevant security controls per governance | Yes       |
| Engineering lead        | Deliverable within capacity  | Estimates delivery options and technical evidence          | Yes       |
| Operations/support lead | Diagnosable exceptions       | Defines support and escalation needs                       | Yes       |
| Employees/admins        | Complete daily tasks         | Validate real journeys                                     | Yes       |

(1) Extract stakeholders from each journey step. (2) Add teams that govern risk, support, or delivery. (3) Write a
need—not just a job title. (4) Distinguish *input* from *approval*. (5) Verify actual decision rights with the
organization; table roles are **[Hypothetical practice assumptions]**.

### 4. Guided exercise E04

**Goal:** Build an impact map. **Steps:** Name six stakeholder groups for faster transaction visibility. For each, write
one need, whether it is affected or consulted, and one question to ask. **Expected:** Include a non-user group.
**Hint:** Who handles a record that is displayed incorrectly at 2 a.m.?

### 5. Failure, detection, recovery, trade-off

**Failure:** Only the product owner attends discovery. **Detection:** Late objections from risk, finance, support, or
users. **Recovery:** Perform impact mapping and scheduled targeted consultation. **Trade-off:** Many reviewers raise
quality but can slow decisions; use clear consultation windows and one owner per decision.

### 6. Interview Phrasing

> “I would map people who use, approve, secure, operate, and depend on the workflow. I would identify who provides input
> and who has the authority to accept each trade-off.”

**Plain English:** Being affected is not the same as being allowed to approve a risk. **Follow-up F04:** Why should
support participate before design? **Answer:** AK-E04/F04.

## L05 — Conflicting objectives and decision rights

**Checklist:** C015 · **Assessment:** A05.

### 1. Purpose and prerequisites

**Purpose:** Reach a justified decision when stakeholder goals collide. Requires L04's stakeholder map.

### 2. Terms and fundamentals

- **Objective** is a desired result. **Constraint** is a limit that must be respected.
- **Conflict** means two desired outcomes cannot both be fully satisfied under current conditions.
- **Decision right** is explicit authority over a decision. **Escalation** moves unresolved choices to an authorized
  owner.
- **Risk acceptance** means formally deciding to tolerate a known remaining risk. An architect must not silently accept
  a business/security risk for its owner.
- **Evidence** means observations, tests, research, or agreed policy that supports a claim.

### 3. Worked example — step by step

**[Hypothetical practice assumptions]** Finance wants transaction rows within **30 seconds**; engineering estimates
**five minutes** with current capacity; risk requires uncertain items to be marked and reviewed before being called
*verified*.

| Goal                           | Why it matters             | Potential conflict                 |
|--------------------------------|----------------------------|------------------------------------|
| Finance: fast visibility       | Faster investigations      | Data may still be provisional      |
| Engineering: feasible delivery | Cost and reliability       | More speed may require more effort |
| Risk: correct status label     | Avoid misleading decisions | Verification can take longer       |

**Reasoning:** (1) Ask whether “visible” means *any record* or *verified record*. (2) Keep risk's prohibition on false
verified labels as a condition, not a preference to trade away. (3) Compare “fast provisional status” with “slower
verified status.” (4) Estimate business consequences and validation steps. (5) Have the designated finance/product
decision owner approve the user-experience trade-off, with risk/security approval for their controls. (6) Record
unresolved facts and a review trigger.

### 4. Guided exercise E05

**Goal:** Produce a decision-rights note. **Steps:** Write two options, each stakeholder's concern, an accountable
business decision owner (by role), a risk/control reviewer, one experiment, and a condition for revisiting.
**Expected:** No silent decision by the architect. **Hint:** A label such as “pending verification” may separate speed
from certainty.

### 5. Failure, detection, recovery, trade-off

**Failure:** Engineering declares five minutes “acceptable” without customer approval. **Detection:** No business
evidence or acceptance sign-off. **Recovery:** Present choices with measurable impact to the authorized owner.
**Trade-off:** Fast provisional display aids finance but requires clear labeling, strong permissions, and later
correction; delayed confirmed display simplifies interpretation but harms timely visibility.

### 6. Interview Phrasing

> “When objectives conflict, I turn each request into a measurable outcome or a hard constraint. I compare feasible
> options, make residual risk visible, and ask the accountable owner to approve the business trade-off.”

**Plain English:** Show the real choices and get agreement from the right people. **Follow-up F05:** Can the finance
lead override a mandatory security restriction? **Answer:** AK-E05/F05.

---

# Module C — Turn uncertainty into testable requirements (C016)

## L06 — Elicitation: discover before proposing

**Checklist:** C016 · **Assessment:** A06.

### 1. Purpose and prerequisites

**Purpose:** Find real needs rather than accepting the first requested technology. Requires journeys (L03) and
stakeholders (L04).

### 2. Terms and fundamentals

- **Elicitation** means drawing out information from stakeholders, observation, documents, and examples. It is not
  merely asking for a feature list [R1].
- **Current state** means how work operates today. **Desired state** is the improved future.
- **Open question** has no verified answer yet. **Assumption** is treated as true temporarily but is unverified [R1].
- **Probe** is a follow-up question to uncover details. **Acceptance** means a defined owner agrees a result meets the
  stated need.

### 3. Worked example — step by step

A stakeholder says, “We need real-time transaction visibility.” A weak reply is, “We will build streaming dashboards.”
That selects a technique without confirming the problem.

**Better discovery:** (1) “What business action depends on seeing the transaction?” (2) “Which roles need it?” (3) “When
does the clock start?” (4) “Does pending information help?” (5) “How old is data today?” (6) “What happens during an
exception?” (7) “What is the acceptable delay?” (8) “Which status must be verified?” (9) “Which team is accountable?”
(10) “How will we measure benefit?”

**Why these matter:** Answering (1) reveals value; (2) reveals users; (3)/ (7) define a measurable interval; (4)/ (8)
separate speed from correctness; (5) supplies a baseline; (6) covers failure; (9) secures governance; (10) defines
success.

### 4. Guided exercise E06

**Goal:** Write *your own* ten clarifying questions for a new complaint: “Managers spend too much time reviewing
purchases.” **Steps:** Include current workflow, users, cost/delay baseline, rule exceptions, compliance, priority,
outcome, and owner. **Expected:** Ten open questions, not ten technology proposals. **Hint:** Ask “how often” and “what
happens if.”

### 5. Failure, detection, recovery, trade-off

**Failure:** Asking leading questions (“Do you want a real-time message bus?”). **Detection:** Stakeholders agree to a
design they cannot evaluate. **Recovery:** Rephrase around tasks, current pain, acceptable outcomes, and exceptions.
**Trade-off:** Workshops expose cross-team conflicts quickly but some users speak less; combine workshops with brief
one-to-one interviews and direct observation when possible.

### 6. Interview Phrasing

> “Before proposing a design, I would clarify the user action, the current delay, the consequence of that delay, and the
> conditions under which data can be treated as correct.”

**Plain English:** Find what is wrong and what “fixed” means. **Follow-up F06:** What if stakeholders cannot give an
exact target? **Answer:** AK-E06/F06.

## L07 — Functional requirements and acceptance criteria

**Checklist:** C016 · **Assessment:** A07.

### 1. Purpose and prerequisites

**Purpose:** State behavior clearly enough to test. Requires L06's discovery notes.

### 2. Terms and fundamentals

- **Business requirement:** a business goal or result. **Stakeholder requirement:** need of a stakeholder group.
- **Functional requirement:** behavior or information the solution must provide. **Non-functional requirement/quality
  attribute:** how well it must perform.
- **Acceptance criteria:** observable conditions that must hold for a requirement to be accepted.
- **Actor:** user or external party acting in a task. **Trigger:** event that starts behavior. **Outcome:** observable
  result.

**[Verified external fact]** IIBA separates business, stakeholder, and solution requirements (including functional and
non-functional), plus transition requirements [R2]. This guide focuses on the types needed for F01.

### 3. Worked example — step by step

**Business objective [hypothetical]:** Reduce hours finance spends searching for purchase records.

**Stakeholder need:** Finance must find a purchase's latest *known* status.

**Functional requirement FR-01:** “When an authorized finance user searches for a purchase identifier, the system shall
display its known status, the time that status was last updated, and whether it is provisional or verified.”

**Acceptance criteria:** (a) An authorized finance user can find a known test purchase; (b) the display contains a
status and timestamp; (c) a provisional status is distinguishable from verified; (d) an unauthorized user cannot see the
record; (e) unknown identifiers return a defined ‘not found’ result. **Note:** Authorization is mentioned as a business
acceptance concern, not a detailed security design.

**Walkthrough:** The word *when* gives the trigger; *authorized finance user* gives the actor; *search* gives the
behavior; *status/time/label* gives output; criteria make the claim testable. A target such as “within 120 seconds”
belongs in a **quality scenario**, not hidden in FR-01.

### 4. Guided exercise E07

**Goal:** Write two functional requirements and three criteria for each. **Steps:** Write one for an administrator
editing a spending limit and one for an employee receiving a blocked-request explanation. Include actor, trigger,
behavior, output, and one misuse case. **Expected:** Requirements do not prescribe a programming language or
infrastructure. **Hint:** “When [actor] does [task], the system shall [result].”

### 5. Failure, detection, recovery, trade-off

**Failure:** “System shall provide a fast, easy-to-use dashboard.” **Detection:** No actor, trigger, measurable test, or
clear output. **Recovery:** Split into functional behavior and measurable quality scenarios. **Trade-off:**
Over-detailed requirements constrain good design choices; under-detailed requirements permit incompatible
interpretations. Specify business-observable behavior and agreed acceptance results.

### 6. Interview Phrasing

> “I write functional requirements around an actor, a trigger, and an observable result. I add acceptance criteria so
> the business and delivery team can agree what correct behavior means.”

**Plain English:** Say who needs what and how you will check it. **Follow-up F07:** Is “response in two seconds” a
functional requirement? **Answer:** AK-E07/F07.

## L08 — Constraints, assumptions, open questions, and validation

**Checklist:** C016 · **Assessment:** A08.

### 1. Purpose and prerequisites

**Purpose:** Prevent guesses from silently becoming architecture commitments. Requires L07's requirements and L05's
decision ownership.

### 2. Terms and fundamentals

- **Constraint:** a non-negotiable boundary, *if confirmed*, such as a fixed launch date or a policy forbidding
  unverified results from being labeled verified.
- **Assumption:** unconfirmed working belief. It requires an owner, evidence plan, and a date/review trigger.
- **Open question:** information that must be obtained before making a commitment.
- **Dependency:** another team, activity, or external event needed for success.
- **Risk:** a possible harmful consequence under uncertainty. **Validation:** confirm a requirement contributes to the
  business value; **verification:** check that it is clearly and correctly stated [R1].

### 3. Worked example — step by step

| ID    | Type                | Statement                                                        | Evidence needed / accountable role          |
|-------|---------------------|------------------------------------------------------------------|---------------------------------------------|
| R-01  | Requirement         | Authorized finance can see a timestamped status                  | Finance acceptance test / Finance lead      |
| CO-01 | Proposed constraint | Unverified status must not be labeled “verified”                 | Risk policy confirmation / Risk lead        |
| AS-01 | Assumption          | Most new transaction records can be displayed within 120 seconds | Sample journey data / Engineering + Finance |
| OQ-01 | Open question       | Does finance need provisional items or only reviewed records?    | Interview / Finance lead                    |
| DP-01 | Dependency          | Source of event timestamps must be identified                    | Data/system owner                           |
| RK-01 | Risk                | Bad status labels could cause wrong finance action               | Review/control test / Risk + Finance        |

**Walkthrough:** (1) Tag each statement. (2) Never present proposed constraint CO-01 as an official policy before
confirmation. (3) Assign a real role, not a fictitious person. (4) Record when to revisit. (5) Validate requirements
against the journey and verify clarity with test cases.

### 4. Guided exercise E08

**Goal:** Classify eight statements. **Steps:** Label each as requirement, constraint, assumption, or open question,
then name its confirmation owner: (a) “Finance shall see a status timestamp”; (b) “The release date cannot move, per
sponsor approval”; (c) “We think all users have stable connectivity”; (d) “Who owns policy approval?”; (e) “Risk checks
are always instant”; (f) “Employees shall see a reason when declined”; (g) “Company policy forbids cross-company record
access, pending policy review”; (h) “How many purchases arrive at peak?” **Expected:** Two requirements; one confirmed
constraint; two assumptions; two open questions; one *proposed/unverified constraint*. **Hint:** Unverified policy
claims must be marked as such.

### 5. Failure, detection, recovery, trade-off

**Failure:** Treating “risk checks are instant” as an agreed fact. **Detection:** No source or observation.
**Recovery:** Log assumption, seek timing evidence, design the decision to tolerate uncertainty. **Trade-off:** Early
assumptions let teams explore options; unchecked assumptions become expensive rework. Use short decision gates instead
of stopping all planning.

### 6. Interview Phrasing

> “I keep requirements, hard constraints, assumptions, and unanswered questions in separate lists. Each important
> assumption has an owner and a way to validate it before we commit to a design.”

**Plain English:** A guess is not a fact. **Follow-up F08:** What if the launch date and security policy conflict?
**Answer:** AK-E08/F08.

---

# Module D — Write measurable quality attributes (C017)

## L09 — Quality attributes and scenario structure

**Checklist:** C017 · **Assessment:** A09.

### 1. Purpose and prerequisites

**Purpose:** Replace “fast,” “always available,” “secure,” and “easy to change” with scenarios that can guide choices
and be tested. Requires L07 requirements and L08 uncertainty labels.

### 2. Terms and fundamentals

- A **quality attribute** describes how well a system serves a purpose, not merely one feature. Examples are
  availability, performance, security, freshness, and changeability.
- A **quality-attribute scenario** states what happens, under which conditions, and how success is measured.
- **Stimulus** is something that happens. **Environment** is the operating condition. **Response** is how the system
  behaves. **Response measure** is the numeric or observable pass rule.
- **Source** generates the stimulus; **artifact** is what is affected. A common architecture scenario template uses
  **six fields**: source, stimulus, environment, artifact, response, response measure. We use it as a learning template;
  we do not claim ISO prescribes this wording.
- **Threshold** is a boundary value. **Measurement window** is the period over which results are counted.

**[Verified external fact]** Carnegie Mellon Software Engineering Institute (SEI) uses stakeholder-generated scenarios
to identify and prioritize architecturally important quality needs before architecture exists [R3]. ISO/IEC 25010:2023
provides a product quality model to specify and evaluate quality [R4]. The complete ISO standard text was not accessed.

### 3. Worked example — step by step

**Vague:** “The transaction view must be real time.”

**Precise [Hypothetical practice assumption]:**

| Field            | Example                                                                              |
|------------------|--------------------------------------------------------------------------------------|
| Source           | A newly recorded purchase                                                            |
| Stimulus         | Its record becomes available at the agreed source boundary                           |
| Environment      | Normal operation during expected business traffic                                    |
| Artifact         | Finance transaction-status view                                                      |
| Response         | The view displays a **provisional** record and its source timestamp                  |
| Response measure | At least 99% of eligible records become visible within 120 seconds, measured monthly |

**Walkthrough:** (1) Identify the business need. (2) Define the clock's start and stop. (3) Specify eligible records,
including how to count missing records. (4) State operating conditions. (5) Define the response. (6) Include threshold,
proportion, period, and measure source. (7) Seek owner agreement before calling it accepted.

### 4. Guided exercise E09

**Goal:** Turn “the system should be reliable” into a six-field scenario. **Steps:** Choose a purchase-request decision;
define the stimulus, environment, response, and measure. **Expected:** All six fields and a clear observation window.
**Hint:** Is “no server crash” the same as successful purchase processing?

### 5. Failure, detection, recovery, trade-off

**Failure:** “99% real time” without definitions of events or timing. **Detection:** Two teams compute different
results. **Recovery:** Define the six fields and reproducible calculation. **Trade-off:** Stricter targets may improve
experience but increase cost; choose targets by evidence and impact.

### 6. Interview Phrasing

> “I turn quality expectations into scenarios with a trigger, operating condition, response, and measurable result. That
> lets us compare options against user impact instead of debating adjectives.”

**Plain English:** Describe exactly what happens and what counts as good enough. **Follow-up F09:** Why specify the
clock start and population? **Answer:** AK-E09/F09.

## L10 — Availability: can the user complete the task?

**Checklist:** C017, availability · **Assessment:** A10.

### 1. Purpose and prerequisites

**Purpose:** State when a required journey is usable. Requires L03 journey and L09 scenario template.

### 2. Terms and fundamentals

- **Availability** is ability to use a service when needed, under an agreed definition.
- A **successful user journey** means the required business action completes correctly, not just that a server responds.
- A **service level indicator (SLI)** measures service behavior. A **service level objective (SLO)** gives a target for
  that indicator.
- **Denominator** is all eligible attempts. **Numerator** is the attempts satisfying the rule. A **maintenance window**
  is planned downtime; do not exclude it silently.

**[Verified external fact]** Google SRE discusses availability SLIs and SLOs tied to critical user functionality [R5].
Detailed SLO operations belong to T07.

### 3. Worked example — step by step

**[Hypothetical practice assumption]** At expected load, at least **99.5% of eligible valid employee purchase
submissions return a correct, usable business response per calendar month**. The denominator counts valid authorized
submissions at the agreed observation boundary. An intentional policy decline **may count as success** if the rule was
applied correctly and a usable explanation was shown.

```text
Employee submits a request
       |
       v
Correct business result?
    yes = successful journey
    no  = failed journey
```

**Example [invented]:** 9,950 correct results / 10,000 eligible attempts = 99.5%. Beware of failures that never reach
server logs; agree how to observe those too.

### 4. Guided exercise E10

**Goal:** Specify availability for editing a policy. **Steps:** Fill all six scenario fields, define eligible attempts
and success, and propose a hypothetical target and period. **Expected:** Business-facing pass/fail rule. **Hint:**
Returning the wrong saved limit is not success.

### 5. Failure, detection, recovery, trade-off

**Failure:** An error screen counts as “available.” **Detection:** User complaints disagree with service health.
**Recovery:** Measure the completed journey. **Trade-off:** Higher targets can cost more; never bypass required risk
checks to improve the availability score.

### 6. Interview Phrasing

> “I define availability by whether customers can correctly complete a critical journey. Then I agree on eligible
> attempts, the observation period, and a measurable target.”

**Plain English:** A server can respond and the task can still fail. **Follow-up F10:** Is a legitimate policy decline
an outage? **Answer:** AK-E10/F10.

## L11 — Latency: how long the user waits

**Checklist:** C017, latency · **Assessment:** A11.

### 1. Purpose and prerequisites

**Purpose:** Express waiting time as a user-facing requirement. Requires L09 and L10's eligible population.

### 2. Terms and fundamentals

- **Latency** is elapsed time between named start and stop events.
- **End-to-end latency** covers the user experience; **internal processing time** covers one system step.
- A **percentile** indicates a portion of observed timings. **95th percentile (p95)** is a threshold approximately 95%
  of measured events meet, under a declared calculation method.
- A **timeout** means a waiting limit expired; it does **not** prove downstream processing failed.

**[Verified external fact]** Google SRE discusses latency percentiles and measurement locations close to user
experience [R5].

### 3. Worked example — step by step

**[Hypothetical practice assumption]** During expected peak traffic, **95% of valid purchase submissions show a correct
initial decision within 2 seconds** of pressing Submit, measured over a rolling 28-day window. A “pending review”
response can meet an *initial-response* target but must **not** be counted as a completed approval.

**Invented timings:** 1.0, 1.2, 1.5, 1.8, 9.0 seconds. Average is 2.9 seconds; only four of five (80%) meet 2 seconds.
Five observations are too few to estimate a production p95 reliably.

### 4. Guided exercise E11

**Goal:** Replace “fast search” with a latency scenario. **Steps:** Define clock boundaries for finance search; select a
hypothetical percentile, threshold, load and window; describe slow requests. **Expected:** Measurable user-level
latency. **Hint:** Displaying a spinner is not displaying usable results.

### 5. Failure, detection, recovery, trade-off

**Failure:** Timing only backend processing. **Detection:** Users experience much longer screen waits. **Recovery:**
Measure full user response as well as internal timings. **Trade-off:** A quick preliminary response can improve
responsiveness, but it cannot be called final.

### 6. Interview Phrasing

> “I measure latency for the action the user actually experiences, use percentiles rather than only averages, and
> distinguish an early acknowledgement from a final business decision.”

**Plain English:** Time the task, not one hidden part. **Follow-up F11:** Why can an average hide poor experience?
**Answer:** AK-E11/F11.

## L12 — Security: who may see or change what?

**Checklist:** C017, security · **Assessment:** A12.

### 1. Purpose and prerequisites

**Purpose:** Express a business-facing security outcome, before technology design. Requires roles L01, owners L04,
scenarios L09.

### 2. Terms and fundamentals

- **Authentication** checks identity. **Authorization** checks permission to perform a specific action.
- **Confidentiality** restricts information to authorized parties. **Integrity** protects from unauthorized
  modification. **Availability** ensures timely authorized access.
- **Least privilege** means giving only the access needed. **Audit evidence** is a trustworthy record that assists an
  investigation.
- **Negative test** attempts a forbidden action. Positive tests check permitted actions still work. Neither proves
  absence of every vulnerability.

**[Verified external fact]** NIST frames information security with confidentiality, integrity, and availability [R6].
Detailed controls belong in T06.

### 3. Worked example — step by step

**Scenario [Hypothetical practice assumption]:** A finance user from organization A attempts to view organization B's
record. In normal operation, the transaction view **denies access and returns no details**. All defined automated
cross-organization negative tests must pass, with reviewable evidence. This is an **acceptance test**, not a promise of
zero production vulnerability.

**Walkthrough:** (1) Identify the sensitive data. (2) Identify role and forbidden action. (3) State safe response. (4)
Define a test set and owner. (5) Add a positive authorized case. (6) Record remaining risk for specialist review.

### 4. Guided exercise E12

**Goal:** Write two access scenarios. **Steps:** One permits an administrator to update its organization's limit; one
rejects an employee trying to do so. For each specify response, evidence, reviewer. **Expected:** Positive and negative
acceptance cases. **Hint:** Being logged in does not imply edit rights.

### 5. Failure, detection, recovery, trade-off

**Failure:** Treating login as enough to read every organization's data. **Detection:** Unauthorized cross-company reads
in negative tests. **Recovery:** Define per-record authorization requirements and security review. **Trade-off:** Strong
controls may increase complexity or latency; mandatory protection cannot be silently waived for speed.

### 6. Interview Phrasing

> “I describe security as allowed and forbidden business actions, including cross-company access. I define negative
> tests and involve the authorized security owner in accepting remaining risk.”

**Plain English:** Say what must never be exposed and test it. **Follow-up F12:** Is login alone enough? **Answer:**
AK-E12/F12.

## L13 — Data freshness: how recent is the displayed fact?

**Checklist:** C017, data freshness · **Assessment:** A13.

### 1. Purpose and prerequisites

**Purpose:** Make “real time” precise for finance. Requires journey L03 and scenario L09.

### 2. Terms and fundamentals

- **Event time** is when an event occurs at a defined source. **Source timestamp** is the recorded event time.
- **First-visible time** is when a user can first see the relevant record.
- **Publication lag** = first-visible time − source time. **Displayed age** = viewing time − timestamp of the latest
  relevant update. These are **different** measures.
- **Freshness** means how current the displayed data is. **Completeness** means whether expected records are present; a
  fresh report can omit important items.
- **Provisional** information is not fully verified. **Stale** data exceeds the accepted freshness threshold.

**[Verified external fact]** Google SRE discusses freshness and correctness measures for data pipelines [R5]. The data
model and reconciliation procedures belong to T05/D02.

### 3. Worked example — step by step

**Scenario [Hypothetical practice assumption]:** A purchase becomes eligible for reporting at an agreed source boundary.
Under normal load, the finance view shows a correctly labeled provisional or verified row **within 120 seconds for at
least 99% of eligible records each month**. The view shows a timestamp and a freshness warning when the threshold is
breached.

```text
Purchase recorded       First visible in finance       Finance opens screen
     10:00:00 ----------------- 10:01:15 --------------------- 10:10:00
                 75 sec publication lag       viewing occurs 10 min later
```

**Walkthrough:** (1) Define the source event. (2) Define first visibility. (3) Count *all eligible records*, including
those not visible. (4) Mark provisional versus verified. (5) Compute lag; note viewing-time age is separate. (6) Ask
whether missing/incorrect rows should block acceptance.

### 4. Guided exercise E13

**Goal:** Distinguish two freshness measures. **Steps:** A record occurs at 10:00, first appears at 10:04, and is viewed
at 10:12 without any later update. Calculate publication lag and displayed age. Explain how to count a record that never
appears, and give one quality safeguard. **Expected:** Two different elapsed times and treatment of missing records.
**Hint:** Missing items need their own failure count.

### 5. Failure, detection, recovery, trade-off

**Failure:** Measuring only records already displayed. **Detection:** Missing items disappear from the denominator.
**Recovery:** Compare known eligible event identifiers with visible records; report delayed *and missing* counts.
**Trade-off:** Quick provisional visibility helps finance, but status labels, subsequent correction, and access controls
must prevent misleading use.

### 6. Interview Phrasing

> “I ask which event starts the clock and how current the finance view must be. I measure missing records as well as
> delays, and distinguish provisional status from verified status.”

**Plain English:** A quick report still fails if it silently misses purchases. **Follow-up F13:** Can data be fresh but
incorrect? **Answer:** AK-E13/F13.

## L14 — Changeability: can business rules evolve safely?

**Checklist:** C017, changeability · **Assessment:** A14.

### 1. Purpose and prerequisites

**Purpose:** Express “easy to change” as a measurable business requirement. Requires capabilities L02, requirements L07,
scenarios L09.

### 2. Terms and fundamentals

- **Changeability** here is the ease and safety of changing needed business behavior. **Modifiability** is a related
  architecture term [R3]; they are not asserted to be identical formal standard labels.
- **Lead time** is elapsed time between explicitly defined change start/end points.
- **Change scope** says which rules or outputs are affected. **Regression** is an unintended break in previously correct
  behavior.
- **Rollback** reverses a problematic change. **Configuration** stores behavior-affecting values separately from code;
  it is one possible implementation, not an F01 mandate.

### 3. Worked example — step by step

**Scenario [Hypothetical practice assumption]:** After an authorized administrator's standard spending-limit update has
completed required approval, the new validated limit becomes effective **within one business day for 95% of eligible
changes per quarter**, with no change to unrelated policies. Previous and new values remain inspectable for authorized
review.

**Walkthrough:** (1) Define the change class: *standard limit value*, not arbitrary new rules. (2) Start the clock after
required approvals. (3) End when business behavior actually uses the new value. (4) Verify unrelated rules still work.
(5) Decide who may reverse an unsafe change. (6) Confirm that the business values this time target.

### 4. Guided exercise E14

**Goal:** Write a changeability scenario for adding an optional approval step. **Steps:** Define “small change,” clock
start/end, proposed target, a regression check, and rollback trigger. **Expected:** A concrete change with measurable
outcome and safety checks. **Hint:** “Code deployed” is not the same as “new rule works correctly.”

### 5. Failure, detection, recovery, trade-off

**Failure:** Promising “all changes in one day” without considering safety approvals and scope. **Detection:** Complex
changes routinely fail targets or bypass checks. **Recovery:** Define separate change classes and necessary reviews.
**Trade-off:** Configuration can shorten standard changes but increases the number of rule combinations that must be
controlled and tested.

### 6. Interview Phrasing

> “I define changeability using a specific class of business change, its approval point, the time until it becomes
> effective, and how we avoid regression. I would not give one estimate for every change.”

**Plain English:** Ask how quickly a *specific* change can happen safely. **Follow-up F14:** When can configurability
increase risk? **Answer:** AK-E14/F14.

## L15 — Prioritize quality by business impact

**Checklist:** C017, ranking · **Assessment:** A15.

### 1. Purpose and prerequisites

**Purpose:** Decide what is truly important when not every target can be maximized. Requires L10–L14's five scenarios
and L05's decision rights.

### 2. Terms and fundamentals

- **Business impact** is the effect on customers, operations, financial results, or obligations if a quality target is
  missed.
- **Severity** is how harmful a failure would be. **Likelihood** describes how likely it is. **Urgency** means how
  quickly action is needed.
- **Hard constraint** is not freely traded. **Priority** guides investment among negotiable improvements.
- **Impact ranking** is a defensible ordering, *not* a substitute for testing or approval.
- **Revisit trigger** is a change in business or technical facts that causes reassessment.

**[Verified external fact]** SEI's Quality Attribute Workshop prioritizes stakeholder quality scenarios using business
drivers [R3].

### 3. Worked example — step by step

**[Hypothetical practice assumptions; this is one defensible ranking, not a company policy]:**

|       Rank | Quality goal   | Business failure if unmet                           | Status / rationale                                        |
|-----------:|----------------|-----------------------------------------------------|-----------------------------------------------------------|
| Constraint | Security       | Cross-company exposure or false verified label      | Must pass agreed security/control review; not traded away |
|          1 | Data freshness | Finance cannot investigate purchases in time        | Directly addresses stated complaint                       |
|          2 | Availability   | Employees or finance cannot complete critical tasks | High business disruption                                  |
|          3 | Latency        | Employees wait too long for decisions               | Important, but early pending responses may help           |
|          4 | Changeability  | Standard rule updates take too long                 | Valuable, possibly less urgent for initial fix            |

**Walkthrough:** (1) Identify the business complaint and harm. (2) Separate mandatory controls from negotiable target
levels. (3) Ask each stakeholder for examples of impact. (4) Compare feasibility and costs of improvements. (5) Get
decision-owner confirmation. (6) Revisit if major new evidence emerges. A different business case may rank changeability
first.

### 4. Guided exercise E15

**Goal:** Rank the five qualities under a changed scenario. **Steps:** Suppose **[Hypothetical practice assumption]** a
client updates policies daily, but finance reviews records only once a week. Rank the top three, state business evidence
you need, and flag at least one non-negotiable security constraint. **Expected:** Reasoned order with uncertainty and
owner. **Hint:** A requirement's business urgency changes with the workflow.

### 5. Failure, detection, recovery, trade-off

**Failure:** The architect assigns priorities alone using invented weights. **Detection:** No customer impact,
stakeholder validation, or measurement. **Recovery:** Compare consequence, affected population, feasible targets, and
cost, then get agreement. **Trade-off:** Improving freshness may raise complexity or show provisional data; improving
certainty may delay visibility. Ranking selects an investment focus, not permission to break controls.

### 6. Interview Phrasing

> “I prioritize quality attributes by the cost of failing the business journey, not by technical fashion. I treat
> required security controls as constraints, compare the negotiable targets, and confirm the ranking with the
> accountable
> owner.”

**Plain English:** Rank the pain and risk, not favorite technologies. **Follow-up F15:** Can security be below freshness
in the ranking? **Answer:** AK-E15/F15.

---

# Module E — Prove business and technical success (C018)

## L16 — Business KPIs, baselines, and ownership

**Checklist:** C018 · **Assessment:** A16.

### 1. Purpose and prerequisites

**Purpose:** Decide if the solution helped the business, not just whether software was delivered. Requires L01 users,
L03 journeys, and L07 requirements.

### 2. Terms and fundamentals

- A **key performance indicator (KPI)** is a selected measure of progress toward an important business outcome.
- **Metric** is any measure. A metric only becomes a meaningful KPI when tied to a goal and owner.
- **Baseline** is an agreed measurement of current results before a change.
- **Target** is the desired future value, with a deadline and measurement rule.
- **Leading measure** can signal future results (e.g., faster status availability). **Lagging measure** shows an outcome
  after it occurs (e.g., fewer finance hours spent investigating).
- **Countermetric/guardrail** checks whether improving one result harms another (e.g., faster visibility but more
  incorrect status).
- **Unit**, **population**, **measurement window**, **data source**, and **owner** make a KPI usable.

**[Verified external fact]** IIBA defines metrics as quantifiable indicators and separates business objectives from
solution requirements [R1, R2].

### 3. Worked example — step by step

**Business goal [hypothetical]:** Reduce manual transaction investigations for Northstar finance.

| Measure                                            | Type                        | Hypothetical example definition                                    | Proposed owner        |
|----------------------------------------------------|-----------------------------|--------------------------------------------------------------------|-----------------------|
| Weekly minutes spent locating transactions         | Business KPI (lagging)      | Minutes per finance analyst-week, measured via sampled time logs   | Finance lead          |
| Percentage of transactions located without support | Business KPI                | Successful independent lookups / eligible lookup attempts          | Finance lead          |
| Record-visible-within-120s ratio                   | Technical freshness measure | Eligible records visible within 120s / all eligible source records | Engineering + Finance |
| Wrong status-label rate                            | Guardrail                   | Confirmed incorrect labels / reviewed records                      | Risk + Finance        |
| Access violation test results                      | Security guardrail          | Unauthorized test cases exposing any data                          | Security lead         |

**[Hypothetical practice assumption]** Baseline is **90 minutes per analyst-week**; proposed target **45 minutes within
90 days** of launch. These are **invented**, not measured. Do not claim success until a real baseline and follow-up
measurement exist.

**Walkthrough:** (1) Name the business outcome. (2) Choose a measure affected by that outcome. (3) Define what counts in
numerator and denominator or measurement unit. (4) Obtain a baseline. (5) Agree target and time period. (6) Name
accountable owner. (7) Add guardrails to detect harmful shortcuts.

### 4. Guided exercise E16

**Goal:** Write a KPI card. **Steps:** Pick the outcome “less time investigating missing transactions.” Provide business
measure, exact calculation or time-log rule, baseline collection plan, hypothetical target, time period, owner, and
guardrail. **Expected:** Can be computed without guessing. **Hint:** Number of dashboards opened is not the outcome.

### 5. Failure, detection, recovery, trade-off

**Failure:** Calling “number of deployed features” a business KPI. **Detection:** It can rise while finance effort stays
high. **Recovery:** Tie the KPI to the user's job and business outcome. **Trade-off:** A simple KPI is easier to
maintain but may miss nuance; combine a few meaningful outcome and guardrail measures, not dozens of vanity metrics.

### 6. Interview Phrasing

> “I would agree on a business KPI before choosing the technology, capture the baseline, set a time-bound target, and
> pair it with technical indicators and safety guardrails.”

**Plain English:** Decide what business improvement must be proven, and check that shortcuts do not cause harm.
**Follow-up F16:** Why is deployment count a poor measure of value? **Answer:** AK-E16/F16.

## L17 — Measurement design: link technical signals to business outcomes

**Checklist:** C018 · **Assessment:** A17.

### 1. Purpose and prerequisites

**Purpose:** Show what to measure, how to compute it, and what evidence supports a claim of success. Requires L13
freshness and L16 KPIs. **Python is optional**; the code is a tiny learning tool, not an F01 programming requirement.

### 2. Terms and fundamentals

- An **event record** stores a fact and time. A **timestamp** is a recorded date/time; a **time zone** prevents
  ambiguous clock values.
- A **data collection plan** states how records are sampled and checked.
- A **leading indicator** (freshness) can improve before the **business outcome** (reduced finance effort). Correlation
  alone does not prove causation.
- **Segmentation** means checking groups separately (customer type, team, high-volume periods) so averages do not hide
  poor experience.
- **Validation evidence** may include direct observation, controlled pilots, matched before/after samples, and
  negative-case tests.

**[Verified external fact]** Google SRE distinguishes end-to-end user-oriented signals from narrower server measures and
describes pipeline freshness indicators [R5, R8].

### 3. Worked example — metric definition, code, and line-by-line explanation

**[Hypothetical practice assumption]** This dataset contains three eligible purchase records. We will check how many
first became visible within **120 seconds**. For missing records in a production measure, they must remain in the source
population and count as failures; this miniature example has none missing.

Save the following as `freshness_example.py`, then run `python freshness_example.py` (a Python installation is needed;
the code uses the standard library only).

```python
from datetime import datetime

records = [
    ("P1", "2026-10-01T10:00:00+00:00", "2026-10-01T10:01:00+00:00"),
    ("P2", "2026-10-01T11:00:00+00:00", "2026-10-01T11:03:30+00:00"),
    ("P3", "2026-10-01T12:00:00+00:00", "2026-10-01T12:01:30+00:00"),
]

def publication_lag_seconds(event_time, visible_time):
    start = datetime.fromisoformat(event_time)
    end = datetime.fromisoformat(visible_time)
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Timezone required")
    lag = (end - start).total_seconds()
    if lag < 0:
        raise ValueError("Visible time is before event time")
    return lag

lags = [publication_lag_seconds(event, visible) for _, event, visible in records]
on_time = sum(lag <= 120 for lag in lags)
rate = on_time / len(records)
print("Publication lag (seconds):", lags)
print("Within 120 seconds:", f"{rate:.1%}")
assert lags == [60.0, 210.0, 90.0]
assert rate == 2 / 3
```

**Explain every executable line or block:**

1. `from datetime import datetime` imports the standard-library timestamp parser.
2. `records = [` starts a small collection; each row contains ID, event time, first-visible time.
3. The `P1` row is 60 seconds late; `+00:00` means its time is explicitly in the UTC offset zero time zone.
4. The `P2` row is 210 seconds late.
5. The `P3` row is 90 seconds late.
6. `]` closes the list.
7. `def publication_lag_seconds(...)` defines a reusable calculation from two timestamps.
8. `start = ...` parses the source timestamp.
9. `end = ...` parses the first-visible timestamp.
10. `if ... tzinfo ...` checks that both timestamps contain time-zone information.
11. `raise ValueError(...)` rejects ambiguous timestamps if the check fails.
12. `lag = ... total_seconds()` subtracts start from end and converts the duration to seconds.
13. `if lag < 0` finds an impossible negative lag in this simplified example.
14. `raise ValueError(...)` stops on this data-quality problem instead of treating it as fast performance.
15. `return lag` gives the validated number back to the caller.
16. `lags = [...]` processes each record once. The underscore `_` discards the identifier because this example only
    needs times.
17. `on_time = sum(...)` counts records with lag no larger than 120 seconds; `True` behaves as 1 here.
18. `rate = ...` divides successes by eligible rows. A production implementation must also handle an empty population
    and missing records.
19. First `print(...)` displays raw lag values so they can be inspected.
20. Second `print(...)` displays the success ratio as a percentage to one decimal place.
21. First `assert` verifies the exact expected lag list; if false, execution stops with an assertion error.
22. Second `assert` checks the fraction is two thirds.

**Expected output:**

```text
Publication lag (seconds): [60.0, 210.0, 90.0]
Within 120 seconds: 66.7%
```

**Business interpretation:** Only two of three fictional events meet the sample 120-second threshold. That alone **does
not** show the finance team's hours fell. The business KPI needs its own baseline and outcome study. **Important
limitation:** A genuine production freshness SLI must be based on an authoritative eligible-event inventory and an
explicit policy for missing, duplicate, invalid, and late timestamps, plus segmentation and data-quality checks. This
code is not production monitoring.

### 4. Guided exercise E17

**Goal:** Evaluate a changed threshold and a missing row. **Steps:** (a) Without code, compute how many of these three
records meet 240 seconds; (b) propose a fourth eligible record with no visible timestamp and define how it affects the
denominator; (c) identify a separate finance business KPI and an adverse-effect guardrail; (d) optionally modify the
code to compute only part (a). **Expected:** Honest calculation and data-quality caveat. **Hint:** A missing row should
never improve the success percentage.

### 5. Failure, detection, recovery, trade-off

**Failure:** “Freshness improved, therefore finance productivity improved.” **Detection:** No before/after finance
outcome evidence; sample sizes or case mix changed. **Recovery:** Collect comparable finance effort measurements, check
status accuracy, segment users, and inspect explanations other than the software change. **Trade-off:** More detailed
measurement improves confidence but increases data-collection cost and privacy exposure; measure only what is necessary
and obtain appropriate approval.

### 6. Interview Phrasing

> “I would instrument the user journey and connect freshness and correctness measures to a business outcome such as
> finance investigation time. I would establish a baseline, use guardrails, and validate whether the improvement
> actually
> occurred.”

**Plain English:** Better technology measurements are useful evidence, but not proof of business value. **Follow-up
F17:** What if freshness improves while finance time gets worse? **Answer:** AK-E17/F17.

---

# Module F — Independent application and senior-level judgment

## The F01 one-page problem brief — cumulative exercise CE01

**[Source requirement]** For the running case, produce a one-page problem brief, ask **ten clarifying questions**, then
rank the **top three quality attributes** with business reasons. This is the required F01 card practice. **Do not read
the model solution until you have produced your own.**

### Required one-page structure

| Heading                          | What to write                                                                                                           |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Problem and business goal        | What is wrong today? What should change for the business?                                                               |
| Customer types / users           | Name at least two customer contexts and three operating roles                                                           |
| End-to-end journey               | Trigger, at least five steps, successful outcome, one exception                                                         |
| Capabilities                     | At least four business abilities; no software-component choices                                                         |
| Stakeholders and decision rights | Sponsor, finance, risk/security, product, engineering, operations, user validation                                      |
| Requirements                     | Three testable functional requirements and their acceptance criteria                                                    |
| Uncertainty log                  | At least two confirmed/proposed constraints, three assumptions, three open questions; clearly label verification status |
| Quality attribute scenarios      | One each for availability, latency, security, data freshness, and changeability; include conditions and measures        |
| Top-three quality priorities     | Business impact, constraint treatment, conflict/trade-off, approval owner                                               |
| Success measures                 | Two business KPIs, two technical measures, at least one guardrail, baseline/target/window/owner                         |
| Evidence and next decision       | Which facts need verifying, which experiment, who decides, when to revisit                                              |

**Deliverable CE01:** One page for the executive-facing brief **plus** an appendix containing the full scenarios,
journey, questions, and measurement definitions. Do not shrink required evidence merely to fit one page. Place a
one-paragraph recommendation at the top, but no component design.

### Ten clarifying-question prompts (answer by writing your own questions)

1. Business consequence of a late transaction?
2. Distinct needs of an employee and finance user?
3. Current source of delays and baseline?
4. Difference between first visible and verified?
5. Start and end of each proposed clock?
6. Missing or incorrect records?
7. Access boundary between customer organizations?
8. What can the business tolerate when risk checks are pending?
9. Who owns approval and escalation?
10. Which business KPI proves the outcome?

**Evaluation CE01:** Must include **10 fully written questions**, not just these prompts; five testable quality
scenarios; an owned uncertainty log; rank top three with explicit business reasons; and a defensible measurement
approach. Compare with **AK-CE01** only after drafting.

## Practice questions PQ01–PQ20

Answer aloud or in writing **without notes**. Mark the primary checklist item in brackets.

| ID   | Question                                                                                              | Item |
|------|-------------------------------------------------------------------------------------------------------|------|
| PQ01 | A company buys a service, but staff operate it. Who is customer and who is user?                      | C014 |
| PQ02 | Differentiate capability, process, and feature using a spend-control example.                         | C014 |
| PQ03 | Trace a purchase journey from request through a finance exception. Where are handoffs?                | C014 |
| PQ04 | Name a non-user stakeholder for transaction visibility and why they matter.                           | C015 |
| PQ05 | Finance, engineering, and risk disagree. Who contributes and who approves?                            | C015 |
| PQ06 | What is wrong with accepting “we need streaming” as the first requirement?                            | C016 |
| PQ07 | Write one functional requirement and two acceptance tests for finance search.                         | C016 |
| PQ08 | Classify “risk checks take zero time” when nobody has confirmed it.                                   | C016 |
| PQ09 | Explain verification versus validation of a requirement.                                              | C016 |
| PQ10 | Give all six fields of a measurable quality-attribute scenario.                                       | C017 |
| PQ11 | Is a correct business decline a service outage? Explain your denominator.                             | C017 |
| PQ12 | Why measure user-facing p95 instead of only mean backend latency?                                     | C017 |
| PQ13 | State a positive and negative authorization scenario.                                                 | C017 |
| PQ14 | Explain publication lag versus displayed age, with clocks.                                            | C017 |
| PQ15 | Write a changeability target for routine policy updates, without skipping approval.                   | C017 |
| PQ16 | Rank three quality attributes for a time-critical finance review and defend your order.               | C017 |
| PQ17 | Business KPI versus technical measure: give one linked pair.                                          | C018 |
| PQ18 | What must be defined before claiming “99% of records visible in two minutes”?                         | C018 |
| PQ19 | Why can a faster dashboard fail to improve business results?                                          | C018 |
| PQ20 | A 5-minute option is cheaper, a 30-second option is faster, but risk has concerns. How do you decide? | All  |

**PQ scoring:** For each question award 0 = no accurate answer, 1 = correct explanation, 2 = explanation with a concrete
example, 3 = explanation + example + justified trade-off/evidence. Maximum **60**. This diagnostic practice score does
**not** replace the standard 1–5 card rubric or the independent senior decision test. Answer sketches: **AK-PQ**.

## Mandatory F01 senior decision challenge — SD01

**[Source requirement]** Original F01 decision test: **Finance says “real time,” engineering proposes a five-minute
delay, and risk wants stronger checks. Define measurable alternatives and who approves the business trade-off.**

**Case facts:** Only the three stated positions are known.
**[Hypothetical practice assumptions, to be tested rather than claimed]:** Finance sometimes acts on provisional
transaction status; risk may delay verification; engineering can compare a 30-second provisional target and a
five-minute verified target. The purchase record is **not** evidence of final financial settlement. Do **not** infer
American Express technology, contractual targets, or policy.

### Your response must contain all seven required elements

1. **Business goal:** Who needs what business outcome? State “visible” versus “verified.”
2. **Known/assumed/open:** Separate observed facts, provisional numerical assumptions, and missing evidence.
3. **At least two feasible options:** Include measurable percentages, windows, status meanings, and failure behavior.
4. **Recommendation and trade-off:** Compare speed, correctness, risk, feasibility, costs, and user consequences.
5. **Failure, security, and data implications:** Missing rows, misleading provisional labels, wrong access, delayed risk
   decisions, record-quality controls.
6. **Evidence/experiment:** Interview users; baseline; realistic pilot/sample; compare late/missing/wrong-status rates
   and real finance effort.
7. **Owners and measurable outcomes:** Name a business approver, control approver, engineering evidence owner,
   support/data owner, business KPI, technical measures, decision revisit point.

### Decision template (fill before opening the answer key)

| Field                                               | Your answer |
|-----------------------------------------------------|-------------|
| Business goal and user                              |             |
| Known facts / practice assumptions / open questions |             |
| Option A (targets, labels, failure cases)           |             |
| Option B (targets, labels, failure cases)           |             |
| Optional Option C / phased approach                 |             |
| Decision and main sacrifice                         |             |
| Mandatory security/risk guardrails                  |             |
| What to measure / evidence needed                   |             |
| Accountable business approver                       |             |
| Risk/security control approver                      |             |
| Technical/data/operations owners                    |             |
| Review trigger                                      |             |

**Interview simulation:** Give a two-minute recommendation. Then respond to each change **without changing the meaning
of “verified”**: (i) risk checks now take 15 minutes for 5% of requests; (ii) finance reports missing transactions after
deployment; (iii) the sponsor cuts delivery capacity by 30%. The numbers are **fictional change prompts**, not observed
facts. This is a standalone **untimed practice challenge**, not X01/X02 timed-mock mode.

**Pass standard:** Independently achieve **at least 4/5 on every applicable standard dimension** in the rubric near the
end. The answer key contains one possible model defense; reasonable alternatives may also pass if evidenced.

---

# Answer key — open only after practicing

The examples below are **model exercises, not actual evidence** of Northstar or an employer. Multiple reasoned answers
can be correct. Each gives a model result, a correction point, and the interview follow-up answer.

## AK-P0 — prerequisite check

1. **Goal**: reduce finance effort; **feature**: a search screen. The screen can exist and the effort might not fall.
2. Employee wants quick next action; finance wants trusted transaction status. Both can use one service differently.
3. “Fast” lacks a named action, time boundary, threshold, population, and measurement window.

## AK-E01/F01 — customer types and roles

**Model:** Customer: a university administration buying purchasing controls. User role 1: department manager requests
purchases and wants a clear response. User role 2: central finance reviewer checks spending and wants reliable records.
Question: “May the department manager approve their own request?” **Typical correction:** Do not assume that a role name
grants permissions. **Follow-up:** Yes, one person may act in multiple roles, but applicable permissions and
separation-of-duties rules require validation.

## AK-E02/F02 — capabilities

**Model:** Manage spending policy (administrator defines limit); check requests (employee gets decision); display
purchase status (finance reviews status); manage exceptions (support/finance investigates a missing record). **Typical
correction:** “Build a React screen” is not a business capability. **Follow-up:** Yes, several systems may support one
business capability; F01 does not decide their boundaries.

## AK-E03/F03 — journey

**Model:** Admin proposes limit → authorized approval → new value becomes effective → employee submits → rule
evaluated → allowed / blocked / held for review → outcome shown → finance receives status → missing status sent for
investigation. **Roles:** Admin, employee, reviewer, finance. **Handoff:** Review decision or finance status. **Typical
correction:** A request receipt does not prove completion. **Follow-up:** Finance visibility failure is an unresolved
journey; measure it and provide an owned exception route.

## AK-E04/F04 — stakeholders

**Model:** Finance lead (status quality; affected); employees (feedback; affected); administrators (policy change;
affected); risk lead (correct verification label; affected); security team (data access; consulted/control owner);
engineering lead (feasibility; affected); support lead (recovery; affected). Ask each about failure impact and
acceptance. **Typical correction:** Excluding operations hides 24-hour support needs. **Follow-up:** Support knows how
broken or disputed records reach human repair, and whether the design is diagnosable.

## AK-E05/F05 — conflict and owners

**Model:** A = five-minute verified-only view, simpler status interpretation but slow. B = a provisional row within a
proposed 60 seconds, then update after completed risk checks; faster but additional correctness/access controls.
Product/finance sponsor approves business user-experience and cost trade-off; authorized risk/security owners must
approve applicable controls; engineering supplies estimates/tests; support owns exception procedures. Pilot both with
fake data. **Typical correction:** Engineering cannot accept all business/security risks alone. **Follow-up:** No.
Mandatory policies or legal obligations cannot be waived by an unrelated business owner; follow formal control
governance.

## AK-E06/F06 — elicitation

**Model ten questions:** (1) What review work takes the most time? (2) Which teams review it? (3) How many cases per
week? (4) What is the current median and long-tail review time? (5) Which policies trigger review? (6) What information
is missing? (7) How often is an exception legitimate? (8) What happens when review is delayed? (9) Who can change or
approve rules? (10) What reduction in effort would count as success? **Typical correction:** Avoid “Would a new
dashboard solve it?” **Follow-up:** Propose candidate targets as assumptions; collect baseline or run a low-cost user
study before approval.

## AK-E07/F07 — functional requirements

**FR-A model:** “When an authorized administrator submits an approved new limit, the system records it and shows its
effective value/time.” Tests: correct value after approval; unauthorized edit is rejected; invalid/negative limit
produces defined rejection. **FR-B:** “When an employee request is blocked by a spending rule, the system shows a
permitted reason and a next action.” Tests: matched reason; no exposure of restricted policy details; request remains
blocked. **Typical correction:** Do not force a database/technology choice into the requirement. **Follow-up:**
“Response within two seconds” is a measurable quality/latency requirement; the behavior itself is functional.

## AK-E08/F08 — uncertainty classification

**Model:** (a) requirement; (b) confirmed constraint **only if sponsor approval is real and recorded**; (c) assumption;
(d) open question; (e) assumption; (f) requirement; (g) proposed/unverified constraint because policy review is pending;
(h) open question. **Typical correction:** Claimed approvals without evidence remain unverified. **Follow-up:** Escalate
the conflict to authorized business and security decision owners; adjust scope/date rather than silently bypass policy.

## AK-E09/F09 — scenario anatomy

**Model:** Source = authorized employee; stimulus = submits valid request; environment = normal operation at forecast
peak; artifact = purchase-decision journey; response = returns correct allowed/blocked/pending result; measure = at
least 99.5% of eligible attempts yield a correct usable response per calendar month. **Typical correction:** “No crash”
does not measure correctness. **Follow-up:** Without the clock and denominator, teams can inflate results by ignoring
slow/missing attempts.

## AK-E10/F10 — availability

**Model:** Authorized administrator submits approved standard change at normal/peak load. The policy update journey
returns the saved correct value/time for at least a **fictional 99% of eligible attempts per month**. Monitor errors and
incorrect saves. **Typical correction:** Returning a success screen while storing an old value is a failure.
**Follow-up:** A correct policy decline is not an outage for a request/response availability SLI; define the success
rule clearly and do not count a wrong decline as correct.

## AK-E11/F11 — latency

**Model:** When a finance user submits a valid lookup, during expected peak, 95% of lookups display usable status/age
within **2 seconds**, measured monthly from action to display. Slow or missing results are tracked separately. All
numbers are fictional. **Typical correction:** Timing only server response misses screen delay. **Follow-up:** A few
very slow waits can be hidden by many quick ones; check distribution/percentiles.

## AK-E12/F12 — security

**Model positive:** An authenticated and authorized admin updates a limit for their organization; it succeeds and can be
reviewed. **Negative:** An employee tries to edit the limit; denied without modification, with appropriate evidence.
Security/control lead approves the relevant authorization requirement. **Typical correction:** Login does not grant
cross-role or cross-organization access. **Follow-up:** No. Check permission for the exact action and business object.

## AK-E13/F13 — freshness

**Model:** Publication lag = **4 minutes** (10:00→10:04). Displayed age at 10:12 = **12 minutes** since that source
event (assuming no later update). A missing eligible record has no valid publication lag observation; count it as a
**freshness failure / missing record**, not remove it from the denominator. Add source-to-view completeness comparison
and explicit status labels. **Typical correction:** A fresh view can miss records or display incorrect data.
**Follow-up:** Yes, a recent but incorrect value is fresh and wrong.

## AK-E14/F14 — changeability

**Model:** A small change = adding a predefined optional approval step for a known role. After required business/risk
approval, the change becomes effective within a **fictional two business days for 90% of eligible changes per quarter**.
Tests verify the new approval route, unrelated policy behavior, and a safe reversal when unexpected rejections rise.
**Typical correction:** Approval cannot be excluded merely to improve elapsed time if the business requires it.
**Follow-up:** Configuration increases the number of combinations/permissions that may need testing, and a bad value can
cause broad disruption.

## AK-E15/F15 — ranking

**Model for changed client:** Top three could be (1) changeability because policy changes are daily; (2) availability
because policy editing and purchase responses remain critical; (3) latency for employee decisions. Data freshness may
move down if weekly finance review is genuinely adequate, **but this must be validated**. Security remains a mandatory
constraint and needs its own acceptance tests. **Typical correction:** Do not conflate priority ranking with permission
to violate a control. **Follow-up:** A security improvement can be lower on a discretionary investment list once
baseline obligations are met, but mandatory safeguards cannot be overruled by a freshness preference.

## AK-E16/F16 — KPI card

**Model:** Business KPI = finance minutes per eligible exception investigated. Definition = total sampled analyst
minutes / number of eligible exception cases; collect two comparable pre-change weeks, segment by complexity, then check
four weeks after rollout. **Fictional target:** improve from 20 to 12 minutes per case by 90 days. Owner = finance lead.
Technical predictor = eligible records visible within 120 seconds. Guardrail = incorrect status-label rate does not
rise. **Typical correction:** Without case mix and baseline, a drop might not be caused by the product. **Follow-up:**
More features do not demonstrate less time or better customer outcomes.

## AK-E17/F17 — measurements

**(a)** All three records are within **240 seconds**, so 3/3 = **100%**. **(b)** With a fourth eligible record never
visible, success is **3/4 = 75%**; retain it in the denominator and label it missing. **(c)** Example business KPI =
weekly minutes finance spends searching for purchase records; guardrail = proportion of incorrect provisional/verified
status labels. **Typical correction:** Filtering away missing rows creates survivorship bias. **Follow-up:** Investigate
user workflow, correctness, missing records, process changes, and measurement differences; freshness alone did not prove
a business result.

## AK-CE01 — model one-page problem brief (fictional)

> **Everything in this example is a [Hypothetical practice assumption] unless it is a statement of what is still
unknown. It is not a description of American Express systems.**

**Problem:** Northstar Office Group says finance sees employee purchases too late to investigate exceptions. Existing
delay and case volume are **unknown** and require baseline measurement.

**Outcome:** Reduce finance time locating a purchase while maintaining correct status labels, appropriate access, and
safe risk review.

**Customer types and roles:** Small organization with one finance generalist and a larger organization with separate
finance teams are two possible customer contexts. Administrator sets limits; employee requests purchases; finance
locates/checks records; risk reviewer handles exceptions.

**Journey:** Employee needs supplies → enters request → policy checked → request allowed/blocked/needs review → business
result displayed → status recorded/updated → finance finds record → any discrepancy is investigated. **Exception:** A
pending or missing status is explicitly labeled and routed to an owner.

**Capabilities:** Manage policies; evaluate requests; view statuses; investigate exceptions.

**Stakeholder and governance view:** Product sponsor owns investment outcome; finance lead accepts user workflow and
finance visibility target; risk lead owns risk-verification acceptance; security lead reviews access requirements;
engineering lead produces feasibility/measurement evidence; operations owns escalation; users validate real tasks.
Actual governance is **unknown until confirmed**.

**Three example functional requirements:**

- `FR-01`: An authorized finance user can search a known purchase ID and see status, timestamp, and provisional/verified
  label. **Tests:** known record appears; missing record has a defined response; wrong organization cannot see it.
- `FR-02`: An authorized administrator can submit an approved spending-limit change and see effective value/time.
  **Tests:** approved valid change becomes effective; invalid amount is rejected; unauthorized change is rejected.
- `FR-03`: An employee whose request is blocked sees an appropriate reason and next action. **Tests:** clear response
  for blocked request; no misleading “approved” label; restricted business details are not disclosed.

**Uncertainty log:** `CO-01` *proposed constraint*: no unauthorized cross-company data view—confirm exact mandatory
policy with security; `CO-02` *proposed constraint*: verified label requires named risk checks—confirm with risk.
`AS-01` records can be first displayed within 120 seconds; `AS-02` some finance tasks benefit from provisional records;
`AS-03` timestamps can be correlated across capabilities. `OQ-01` what is today's delay? `OQ-02` what exactly is
“verified”? `OQ-03` what use cases need faster-than-five-minute visibility? **Owners:** Engineering/data for
baseline/time; Finance for user tasks; Risk for label criteria.

**Five quality scenarios (fictional numerical proposals; not commitments):**

| Quality        | Trigger / environment / response                                                             | Measure and boundary                                                                                |
|----------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Availability   | Employee submits valid purchase during expected load; usable correct decision returned       | At least 99.5% of eligible attempts per calendar month                                              |
| Latency        | Employee submits valid request; correct initial result shown                                 | p95 at most 2 seconds, action-to-display, rolling 28 days                                           |
| Security       | User from organization A attempts to read organization B's record; access denied, no details | All agreed unauthorized automated cases pass, reviewed by security; residual risk assessed          |
| Data freshness | Eligible purchase event recorded; provisional/verified finance row appears with timestamp    | At least 99% visible within 120 seconds each month, missing records counted as failures             |
| Changeability  | Approved routine spending-limit update; new value safely effective                           | At least 95% within one business day after final approval per quarter, no unrelated rule regression |

**Top three among negotiable improvements:** (1) Data freshness, because it directly addresses the complaint; (2)
availability, because users cannot complete critical tasks when it fails; (3) latency, because purchase decisions need
timely responses. **Mandatory security and risk rules remain constraints**, not lower-priority optional work.
Changeability is still measured but may be less urgent unless stakeholder research changes this order.

**KPI plan:** Business KPI 1 = median/typical finance minutes per eligible exception case (baseline not measured;
**proposed**, not actual, improvement target of 25% after pilot). KPI 2 = percentage of finance lookup attempts
completed without support (baseline not measured; fictional target 90%). Technical signals = eligible records visible
within 120 seconds, successful purchase journey ratio. Guardrails = wrong-status labeling and unauthorized data exposure
tests. Confirm population, sample sizes, collection method, window, and owners before claiming improvement.

**Evidence and decision request:** Conduct interviews with finance/employee/admin users; sample actual source-to-visible
delays and missing IDs; measure finance effort before rollout; run a controlled pilot of provisional and
delayed-confirmed views; review correctness and access. Ask finance/product decision owner to select acceptable
visibility behavior after risk/security control review. **Revisit:** if missing records, wrong labels, or finance
benefit fail agreed pilot acceptance.

### Ten fully worded model clarifying questions

1. What decision does a finance employee make after seeing a new transaction?
2. Which tasks need the information first: employee confirmation, finance review, or exception repair?
3. How long do records currently take to become visible, including the worst cases and missing records?
4. Can finance act on a clearly marked provisional status, or must the status be verified first?
5. Which source event starts the freshness clock, and which screen event stops it?
6. What should a finance user see if an expected record is absent or an earlier status was corrected?
7. Which organization and role boundaries must be enforced on transaction searches?
8. Which risk checks or approvals must finish before a status can be called verified?
9. Which roles approve business timing targets, risk controls, and unresolved exceptions?
10. Which finance time/cost measure will prove that faster visibility created real business value?

**Reviewer notes:** A good independent submission need not match this ranking or values. It must keep unknowns explicit,
name five qualities, define measurements, and explain trade-offs. Do not copy fictional “baselines” into an interview as
if they were measured.

## AK-PQ — short answer sketches

| ID   | Core point expected                                                                                                                               |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| PQ01 | Organization is customer; administrator/employee/finance are users with task-specific roles.                                                      |
| PQ02 | Capability = manage policies; process = submit-review-approve; feature = edit-limit screen.                                                       |
| PQ03 | Trigger, policy decision, exception branch, status visibility, finance investigation; name handoffs.                                              |
| PQ04 | Security or support is a stakeholder even without being an end user.                                                                              |
| PQ05 | Finance defines business acceptance, risk/security approves controls, engineering provides feasibility; actual decision rights must be confirmed. |
| PQ06 | Technology request skips discovery of business need and alternatives.                                                                             |
| PQ07 | Actor+trigger+observable result, plus allowed and denied tests.                                                                                   |
| PQ08 | Unverified assumption with evidence owner, not a confirmed fact.                                                                                  |
| PQ09 | Verification = requirement is clear/correctly specified; validation = it supports a real need.                                                    |
| PQ10 | Source, stimulus, environment, artifact, response, response measure.                                                                              |
| PQ11 | Correct rule-based decline may be successful processing; wrongful decline or no response may be failure.                                          |
| PQ12 | Tail/user experience matters; averages and server-only timings hide bad waits.                                                                    |
| PQ13 | Own-organization authorized read allowed; other-organization read denied with no disclosure.                                                      |
| PQ14 | Source-to-first-visible versus most recent source-update-to-viewing time.                                                                         |
| PQ15 | Approved small-rule change becomes effective within stated time and without regression.                                                           |
| PQ16 | Rank by effect on user and business outcome; keep mandatory controls separate.                                                                    |
| PQ17 | Finance investigation minutes (KPI) linked to publication-lag ratio (technical measure).                                                          |
| PQ18 | Eligible population, clock boundaries, status correctness, thresholds, period, exclusions, missing-data policy, owner.                            |
| PQ19 | Correctness, adoption, process, training, case mix, or data gaps may offset speed improvement.                                                    |
| PQ20 | Define alternatives, quantify trade-offs, validate with finance/risk, and obtain authorized approval; monitor outcomes.                           |

## AK-SD01 — sample senior decision defense (fictional)

**1. Business goal:** “Finance needs timely, trustworthy purchase visibility to investigate exceptions. ‘First visible’
is separate from ‘risk verified’ and must not imply final payment completion.”

**2. Know versus assume:** Known from the fictional prompt: finance wants “real time,” engineering proposes five
minutes, risk requires stronger checks. **Not known:** existing lag, allowable provisional action, risk-check duration,
volume, cost, source completeness, and status semantics. **Proposed thresholds below are assumptions.**

**3. Options:**

| Option                | Hypothetical user-visible contract                                                                                                                | Main benefits                                   | Main costs/risks                                                 |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|------------------------------------------------------------------|
| A — verified only     | At least 99% of eligible records visible **within 5 minutes after risk verification completes**, monthly; show no “verified” record before checks | Simple meaning, avoids premature verified label | Total delay can exceed 5 minutes from purchase; finance may wait |
| B — early provisional | At least 99% of eligible source records visible as clearly **provisional within 60 seconds**; separately update verified status after checks      | Fast awareness; early exception detection       | More status handling, user education, risk of misleading use     |
| C — staged pilot      | Start with B for internal finance test group; compare outcomes, then expand or fall back to A                                                     | Evidence before broad commitment                | Additional pilot support and dual workflows                      |

**Precision:** Option A's five-minute clock starts **after** verification, while B's starts at the agreed **source-event
boundary**. They are **not directly comparable as end-to-end delay targets**. For a fair business comparison also
measure event-to-first-usable-record and event-to-verified-status across both options. If engineering's actual proposal
meant five minutes from the event, verify and correct the contract before deciding.

**4. Decision:** Recommend **Option C**, conditional on finance confirming provisional rows help its work and
risk/security approving safe labels and access. Pilot Option B with explicit “pending verification,” while retaining a
verified-only view or clear filter for actions that require certainty. If the pilot shows many misleading records or
poor benefit, choose verified-only presentation or narrow provisional access. Trade-off: better visibility at extra
complexity, not weaker verification.

**5. Safety and data:** Enforce role/organization access in requirements; make provisional status unmistakable; never
silently change historical meaning; show data age; account for missing and late records; specify what users can do while
verification is pending; involve risk and security in applicable approval. Report failure counts and a
recovery/escalation owner. **Do not claim final financial settlement based on a visible row.**

**6. Evidence:** Observe a sample of real finance tasks (with approved access), measure current event-to-visible and
event-to-verified durations, count missing/wrong-labeled records against the source population, compare finance time per
case, test high-volume and degraded scenarios, and verify that controls work. Define the pilot target and decision date
*before* observing results.

**7. Ownership:** Finance product/sponsor role approves business utility and budget trade-off; risk lead approves
risk-verification semantics and permissible actions; security lead approves required access controls; engineering lead
owns feasibility and technical evidence; data owner defines eligible source records; operations owns
monitoring/escalation; finance lead owns KPI and user acceptance. Exact governance must be confirmed in the actual
company.

**Fictional outcome targets (not real commitments):** Reduce finance minutes per exception by at least 25% relative to
an actually collected baseline; record at least 99% of eligible items as visible within 60 seconds during pilot; keep
agreed wrong-label and unauthorized-exposure negative tests passing; have zero *uninvestigated* critical missing-record
exceptions at pilot review, without claiming zero risk.

**Changed-constraint defense:**

- **15-minute risk checks for 5% of requests:** Keep them *pending* until verified; report verified-status latency
  separately. Do not redefine verified or silently exclude slow cases.
- **Finance sees missing transactions:** Stop claiming success from visible rows alone; compare eligible source IDs with
  view IDs, identify gap, document impact, escalate, and decide rollback/limitation according to pre-agreed rules.
- **30% less capacity:** Protect mandatory controls and measurement. Reduce pilot population or optional features, or
  choose the five-minute verified-only option if it meets evidenced finance need. Seek sponsor approval for reduced
  benefits and schedule.

**A natural two-minute interview answer:**

> “I would first clarify what finance means by real time: seeing a purchase quickly or seeing a fully verified result.
> Those are different needs. I would compare a delayed verified view with a faster provisional view that clearly shows
> pending status. I would not weaken required risk checks to hit a display target. My initial recommendation would be a
> limited pilot, with source-to-visible time, missing records, incorrect statuses, access tests, and finance
> investigation
> time measured together. Finance and the product sponsor would approve the business experience and investment
> trade-off,
> while risk and security would approve their control requirements. I would revisit the choice if provisional data
> misleads users or if the benefit is not measurable.”

**Why this sounds senior:** It names the business purpose; distinguishes appearance from correctness; refuses false
certainty; compares real options; requests evidence; identifies who accepts which risk; and states a reversal condition.
It does not recite technology names or claim personal experience.

---

# Coverage matrix — authoritative checklist ID → lesson → assessment

**[Source requirement]** Each required item receives an explicit lesson and an independent
explanation/application/trade-off check. All five are **Core**; there are **no F01 Depth checklist IDs**. Lesson
subdivisions preserve each original item's full meaning rather than silently combining it.

| Checklist ID    | Required text (preserved from v3 in substance)                                                                                               | Lessons                                                                                                         | Specific independent assessments and evidence                                                                                                                                                | Status of guide coverage                                        |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| **C014 · Core** | Identify customer types, user roles, business capabilities, and end-to-end journeys                                                          | L01 customer types/roles; L02 capabilities; L03 journeys                                                        | E01/A01 roles; E02/A02 capability map; E03/A03 full journey + exception; PQ01–PQ03; CE01 customers/capabilities/journey; interview F01–F03                                                   | **Taught / exercised / answer-keyed; learner not yet assessed** |
| **C015 · Core** | Map stakeholders, decision owners, affected teams, and conflicting objectives                                                                | L04 affected teams, stakeholder map, decision roles; L05 conflicts, authority, escalation                       | E04/A04 impact map; E05/A05 conflict/decision-rights note; PQ04–PQ05; CE01 stakeholder map; SD01 ownership defense; F04–F05                                                                  | **Taught / exercised / answer-keyed; learner not yet assessed** |
| **C016 · Core** | Elicit functional requirements, constraints, assumptions, and open questions                                                                 | L06 discovery/elicitation; L07 functional requirements/tests; L08 constraints/assumptions/open questions        | E06/A06 ten questions; E07/A07 functional requirements/acceptance; E08/A08 classifications; PQ06–PQ09; CE01 requirements and uncertainty log; F06–F08                                        | **Taught / exercised / answer-keyed; learner not yet assessed** |
| **C017 · Core** | Write measurable quality-attribute scenarios for availability, latency, security, data freshness, and changeability; rank by business impact | L09 scenario syntax; L10 availability; L11 latency; L12 security; L13 freshness; L14 changeability; L15 ranking | E09/A09 scenario template; E10/A10 availability; E11/A11 latency; E12/A12 security; E13/A13 freshness; E14/A14 changeability; E15/A15 ranking; PQ10–PQ16; five CE01 scenarios; SD01; F09–F15 | **Taught / exercised / answer-keyed; learner not yet assessed** |
| **C018 · Core** | Define business key performance indicators (KPIs) and technical measures that show whether the solution worked                               | L16 KPI, baseline/owner/guardrail; L17 calculation and business evidence                                        | E16/A16 KPI card; E17/A17 metric calculation; Python sample and checks; PQ17–PQ19; CE01 business/technical measures; SD01 evidence; F16–F17                                                  | **Taught / exercised / answer-keyed; learner not yet assessed** |

**Explicit sub-coverage checklist:**

- [x] C014 customer *types*, user *roles*, business *capabilities*, and end-to-end *journeys*, including exception
  paths.
- [x] C015 stakeholder map, decision owners, affected teams, conflict identification, authority, and escalation.
- [x] C016 elicitation questions, functional requirements, constraints, assumptions, unanswered questions, acceptance,
  verification versus validation.
- [x] C017 scenario grammar; **availability**; **latency**; **security**; **data freshness**; **changeability**; ranking
  based on business impact and hard controls.
- [x] C018 outcome-focused business KPIs, technical measures, numerator/denominator, baselines, guardrails, evidence,
  owners, and evaluation.
- [x] Every lesson has purpose/prerequisites, terminology, worked example, guided exercise, failure/trade-off, interview
  phrasing and follow-up.
- [x] Separate answer key for every exercise, cumulative practice, follow-up, and senior challenge.
- [x] One cumulative brief, ten questions, quality ranking, senior test, scoring rubric, references, and final audit.

**Important:** `[x]` above means **the reference document contains the requested teaching/assessment unit**, **not**
that the learner has passed it.

# Standard scoring rubric, evidence, and completion criteria

## Five-level rubric required by topic map v3

| Score   | Observable evidence                                                                                                                                 |
|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **1/5** | Cannot explain the concept accurately, even with prompts.                                                                                           |
| **2/5** | Knows basic terms, but needs help applying them or misses assumptions/risks.                                                                        |
| **3/5** | Proposes a workable answer, but compares options or failure cases weakly.                                                                           |
| **4/5** | Independently explains, applies, compares realistic choices, and defends a trade-off using checks/evidence.                                         |
| **5/5** | Meets 4/5 and adapts under new constraints, identifying second-order business, data, security, operations, and delivery consequences when relevant. |

## Score each applicable dimension separately

| Dimension                        | What earns at least 4/5 in F01                                                                               | Evidence location            |
|----------------------------------|--------------------------------------------------------------------------------------------------------------|------------------------------|
| Business framing                 | States customer, user journey, business problem and target outcome without jumping to technology             | A01–A03, CE01, SD01          |
| Technical correctness            | Correctly distinguishes requirement types, five quality scenarios, clocks, populations, and KPI calculations | A06–A17, PQ, SD01            |
| Trade-offs                       | Names at least two realistic options; explains who gains/loses and changed constraints                       | A05, A15, SD01               |
| Failure, security, and data risk | Includes exception path, access prohibition, provisional/missing/wrong status, risk/control ownership        | A03, A05, A12, A13, SD01     |
| Evidence                         | Names baseline, sample/data source, acceptance test, metric and uncertainty check                            | A08–A17, CE01, SD01          |
| Execution and ownership          | Assigns decision, data, control, support, and measurement roles; includes review trigger                     | A04, A05, CE01, SD01         |
| Communication                    | Explains decision in simple, correct terms and handles follow-ups without inventing facts                    | F01–F17, SD01 spoken defense |

## Completion gate (not automatically achieved)

A learner **passes F01** only when **all** of the following are true:

1. **Every Core checklist item C014–C018 has evidence of three abilities without notes:** explain it accurately, apply
   it to a new example, **and** defend at least one relevant trade-off or choice. Record a score of **at least 4/5** for
   each item.
2. **All 17 guided exercises** have been attempted and checked with the answer key or a reviewer. Incorrect answers have
   been corrected and retested. The learner can explain each corrected result, rather than merely copying it.
3. The **CE01 cumulative practice** contains the one-page brief, **ten fully worded questions**, top-three impact
   ranking, all five quality scenarios, requirement/assumption/owner tables, business KPIs and technical measures. Its
   reasoning must independently meet **4/5** on applicable dimensions.
4. **SD01 senior decision test** addresses all seven requested elements, includes at least two quantified options and
   ownership, responds to the three changed-constraint prompts, and scores **at least 4/5 in every applicable rubric
   dimension**.
5. The learner can distinguish **verified fact, source requirement, hypothetical assumption, and recommendation** and
   does not invent employer systems, personal projects, or achievements.
6. Record any remaining gaps, evidence needed, owners and retest dates. **Only then** mark the F01 card complete.
   **Depth items:** none assigned to F01.

**Why the threshold is demanding:** The topic map asks for senior judgment, not memorized terminology. A 3/5 answer may
be useful practice but is **not** a passing senior answer. No simulated score is presented as an actual learner result.

## Blank completion scorecard (fill after independent assessment)

| Unit                            | Current score (1–5) | Explain without notes? | Apply? | Defend trade-off? | Evidence / missed point / retest |
|---------------------------------|---------------------|------------------------|--------|-------------------|----------------------------------|
| C014                            | Not assessed        | —                      | —      | —                 |                                  |
| C015                            | Not assessed        | —                      | —      | —                 |                                  |
| C016                            | Not assessed        | —                      | —      | —                 |                                  |
| C017                            | Not assessed        | —                      | —      | —                 |                                  |
| C018                            | Not assessed        | —                      | —      | —                 |                                  |
| CE01 cumulative                 | Not assessed        | —                      | —      | —                 |                                  |
| SD01 business framing           | Not assessed        | —                      | —      | —                 |                                  |
| SD01 technical correctness      | Not assessed        | —                      | —      | —                 |                                  |
| SD01 trade-offs                 | Not assessed        | —                      | —      | —                 |                                  |
| SD01 failure/security/data risk | Not assessed        | —                      | —      | —                 |                                  |
| SD01 evidence                   | Not assessed        | —                      | —      | —                 |                                  |
| SD01 execution/ownership        | Not assessed        | —                      | —      | —                 |                                  |
| SD01 communication              | Not assessed        | —                      | —      | —                 |                                  |

**Suggested gap log fields [Recommendation]:** date; checklist ID; failed explanation/test; misconception; corrected
answer; evidence still needed; next practice scenario; reviewer; retest result. This is a simple study log, not an extra
F01 requirement.

---

# Primary references and verification record

**Verification date for the external pages below: 2026-10-24.** References establish industry/business-analysis
terminology and methods. They **do not** establish the fictional Northstar numbers, any implementation at American
Express, or the specific interview requirements.

| Ref    | Issuing body and official primary page                                                                                                                                                                                                     | Verified claim and limits                                                                                                                                                                                                                                                      |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **R1** | **IIBA**, [BABOK Guide glossary](https://www.iiba.org/career-resources/a-business-analysis-professionals-foundation-for-success/babok/glossary/)                                                                                           | Definitions of stakeholder, actor/end user, assumption, elicitation, capability, business process, functional/non-functional requirement, acceptance criteria, KPI-related metric, requirement verification/validation, RACI. Official glossary; examples in lessons are ours. |
| **R2** | **IIBA**, [The Business Analysis Standard, section 4.4](https://www.iiba.org/knowledgehub/the-business-analysis-standard/4-implementing-business-analysis/4-4-understanding-requirements-and-designs/)                                     | Distinction between business, stakeholder, and solution requirements, including functional and non-functional. No claim that a single wording template is mandatory.                                                                                                           |
| **R3** | **Carnegie Mellon SEI**, [Quality Attribute Workshop collection](https://sei.cmu.edu/library/quality-attribute-workshop-collection/) and [QAWs Third Edition](https://sei.cmu.edu/library/quality-attribute-workshops-qaws-third-edition/) | Stakeholder-originated quality scenarios, business drivers, refinement, ranking, and trade-offs before choosing architecture. Six-field template is a standard teaching form; not presented as an ISO quotation.                                                               |
| **R4** | **ISO**, [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html)                                                                                                                                                                     | Published standard provides an ICT/software product quality model to support specification and evaluation. **Only publicly accessible abstract and metadata verified; not full paid standard.** This guide does not reproduce the standard's complete taxonomy.                |
| **R5** | **Google SRE team**, [Implementing SLOs](https://sre.google/workbook/implementing-slos/)                                                                                                                                                   | SLI/SLO methods; user-relevant availability and latency measures; percentile and pipeline freshness examples. Specific targets in this guide are fictional.                                                                                                                    |
| **R6** | **U.S. National Institute of Standards and Technology (NIST)**, [Information security glossary](https://csrc.nist.gov/glossary/term/information_security)                                                                                  | Confidentiality, integrity, and availability as core information security properties. Does not validate detailed control design for a company.                                                                                                                                 |
| **R7** | **American Express**, [One AP public product page](https://www.americanexpress.com/en-us/business/one-ap/)                                                                                                                                 | Publicly described virtual cards, invoice-backed payments, and ACH/check choices. **Domain context only**; no American Express internal architecture or F01 numerical targets inferred.                                                                                        |
| **R8** | **Google SRE team**, [Product-Focused Reliability for SRE](https://sre.google/resources/practices-and-processes/product-focused-reliability-for-sre/)                                                                                      | Distinguishes more user-oriented, end-to-end product measures from narrower system indicators; recognizes measurement cost/coverage trade-offs.                                                                                                                                |

**[Recommendation]** Before a real interview, recheck primary pages for changes and obtain the actual job posting if
available. Do not read the public One AP examples as requirements for an internal team.

# Final completeness and verification audit — as of 2026-10-24

## Scope and coverage audit

| Check                                                           | Result                         | Evidence / limitation                                                                                                                         |
|-----------------------------------------------------------------|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Correct master map used                                         | **PASS**                       | v3 authoritative F01 card and learning contract. The user’s `B01 (C014–C018)` mismatch is explicitly corrected in scope note.                 |
| Original F01 checklist inventory preserved                      | **PASS**                       | All five **C014–C018**, all **Core**, no invented Depth items.                                                                                |
| Every sub-item taught independently                             | **PASS**                       | C014 L01–L03; C015 L04–L05; C016 L06–L08; C017 L09–L15 (five separate quality sections + prioritization); C018 L16–L17.                       |
| Six learning steps per lesson                                   | **PASS**                       | Purpose/prerequisites; terms; step-by-step example; guided exercise; failure/trade-off; interview phrasing/follow-up, L01–L17.                |
| Beginner-first progression                                      | **PASS**                       | Everyday definitions → users → workflows → authority → requirements → measured qualities → outcome proof.                                     |
| Practice and solutions separated                                | **PASS**                       | E01–E17, CE01, PQ01–PQ20, SD01 precede consolidated AK sections.                                                                              |
| Topic-map F01 practice task                                     | **PASS**                       | CE01 requires one-page brief, ten original clarifying questions, ranked top three attributes with business reasons.                           |
| Topic-map F01 senior decision test                              | **PASS**                       | SD01 includes 7 required elements, options, approvals, changed conditions, answer model, and seven-dimension scoring.                         |
| Official primary-source grounding                               | **PASS with limitation**       | IIBA, SEI, ISO metadata, Google SRE, NIST, optional Amex public page. Full ISO 25010 text **not** independently verified.                     |
| Quantitative examples clearly fictional                         | **PASS**                       | Targets/costs/volumes/users are marked hypothetical; no actual employer measurements or achievements claimed.                                 |
| Technology scope unchanged                                      | **PASS**                       | No F02 component design, D02 payment implementation, T06 security architecture, T07 operational design, or B01 full curriculum.               |
| Code is executable Python, line-explained                       | **PASS — executed 2026-10-24** | L17 sample compiled and ran with Python; output `[60.0, 210.0, 90.0]` and `66.7%`, and both assertions passed. Code is standard-library only. |
| Interview statements accurate and natural                       | **PASS (editorial audit)**     | Every lesson has spoken phrasing and plain-English translation; senior example avoids false company claims.                                   |
| Actual learner mastery                                          | **NOT ASSESSED**               | No interactive teaching or scored learner responses were requested. The blank scorecard must remain blank until real evidence exists.         |
| Actual vacancy requirements/internal company stack              | **NOT VERIFIED**               | Requisition/interview plan/internal data unavailable. No unsupported assertions made.                                                         |
| Actual source-to-visible baseline, risk policy, owner approvals | **NOT VERIFIED**               | These are precisely the questions and validation work of F01; practice case is fictional.                                                     |

## Remaining missing or unverified items — explicit list

1. **No F01 checklist content is missing from this guide** according to the authoritative five-ID crosswalk. This is a
   **document coverage** finding, not a learner competency finding.
2. **Full ISO/IEC 25010:2023 standard text not verified.** Only its official published metadata/abstract support the
   limited claim cited. No proprietary normative text is required for this F01 learning guide.
3. **Actual job requisition, hiring expectations, internal architecture, and internal policies remain unverified.** They
   must not be inferred from product marketing or the target-role label.
4. **Northstar practice numbers and constraints are unverified by design.** They are learning assumptions; in an actual
   engagement, replace them with stakeholder-approved definitions and measured baselines.
5. **Learner's completion is unknown.** No exercises, senior challenge, or interview explanations have been submitted or
   scored. Every checklist item remains **unpassed until demonstrated**.
6. **Python sample runtime check completed.** The extracted code compiled, ran, printed the documented result, and
   passed both assertions on 2026-10-24. This does not validate the example as a production monitoring system.

**Final scope gate:** F01 ends at requirements, trade-off framing, and measurement definitions. The next syllabus card,
F02, covers detailed architecture views and decision records. Do **not** treat this guide as a substitute for those
later cards.

**End of guide.**
