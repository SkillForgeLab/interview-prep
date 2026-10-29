# Communicating Enterprise Integration Architecture in Interviews

**Audience:** Senior or principal architect with 20 years of experience  
**Purpose:** Practice a 60-minute whiteboard answer and turn career experience into evidence.  
**Use rule:** Sample systems and decisions are hypothetical. Fill career-story blanks with verifiable facts; never
present the sample as your work.

## 1. The response spine: nine parts you can reuse

Keep these labels on the board so you can resume after an interruption.

1. **Business goal.** Name the user or operational outcome, sponsor, and decision that the design supports. Say what
   success would look like, not just which systems connect.
2. **Scope and promise.** Define the business event, in-scope journeys, and the exact meaning of words such as
   *received*, *accepted*, and *complete*. State exclusions.
3. **Constraints and NFRs.** Capture peak volume and duration, response and propagation deadlines, availability,
   recovery, data protection, budget, deadline, and existing operating capabilities. Mark unknowns.
4. **Ownership and boundaries.** Show who owns each fact and decision, who merely receives a copy, and which trust or
   organizational boundaries each flow crosses.
5. **Design and flow.** Draw the smallest end-to-end path: entry, durable state, integration, target systems, status
   return, and exception path. Narrate one normal transaction.
6. **Choices and alternatives.** Give the criterion, selected option, rejected option, cost or operational consequence,
   and the condition that would change your choice.
7. **Failure and controls.** Walk through a dependency outage, duplicate, poison record, data leak, and peak burst.
   Explain detection, containment, recovery, and owner.
8. **Delivery and measures.** Describe a safe migration sequence, rollback or pause point, operational ownership, and
   measures with a baseline and target to be agreed.
9. **Risks and next decisions.** Close with top assumptions, residual risks, evidence needed, decision owner, and next
   checkpoint. Invite a challenge to the weakest assumption.

Protect the final ten minutes for delivery and decisions.

## 2. A minute-by-minute whiteboard facilitation script

Speak in full sentences and write only decision-bearing words. Mark each unknown **A** (assumed), **O** (open), or **C
** (confirmed).

### 0–10: requirements and nonfunctional requirements

| Minute | Say, ask, or draw                                                                |
|--------|----------------------------------------------------------------------------------|
| 0–1    | “What business result must change, and who owns that result?” Write the goal.    |
| 1–2    | Ask who the users and affected operations teams are.                             |
| 2–3    | Define the triggering event and what the user is promised immediately.           |
| 3–4    | Ask which journeys are in scope: create, amend, cancel, refund, reconcile.       |
| 4–5    | List systems; ask which owns each business fact and decision.                    |
| 5–6    | Ask normal and peak rate, burst duration, growth, and payload size.              |
| 6–7    | Ask response time and downstream completion deadlines separately.                |
| 7–8    | Ask outage tolerance, recovery targets, and whether pending work is acceptable.  |
| 8–9    | Ask data sensitivity, trust boundaries, budget, deadlines, and fixed platforms.  |
| 9–10   | Restate goal, promise, top constraints, and open assumptions; invite correction. |

### 10–25: high-level design

| Minute | Say, ask, or draw                                                         |
|--------|---------------------------------------------------------------------------|
| 10–11  | Draw actors and system boundaries; place the business event at the left.  |
| 11–12  | Mark the authoritative owner of the initial record and its identifier.    |
| 12–13  | Draw the immediate response path; label what it can truthfully promise.   |
| 13–14  | Mark the durable handoff before acknowledging work, if required.          |
| 14–15  | Draw the downstream flow and its contract at each boundary.               |
| 15–16  | Separate command, event, query, and bulk movement where useful.           |
| 16–17  | Add the target system's authoritative decision and return status.         |
| 17–18  | Draw the customer or operator status read path.                           |
| 18–19  | Add correlation and stable business identifiers across systems.           |
| 19–20  | Mark sensitive fields and identities that cross trust boundaries.         |
| 20–21  | Walk one successful transaction from trigger to final state.              |
| 21–22  | State which steps are synchronous and why.                                |
| 22–23  | State which steps can be delayed and what users see meanwhile.            |
| 23–24  | Point to the owner of exceptions and reconciliation.                      |
| 24–25  | Pause: “Is this promise and ownership model consistent with your intent?” |

### 25–40: choices and alternatives

| Minute | Say, ask, or draw                                                     |
|--------|-----------------------------------------------------------------------|
| 25–26  | Name the first decision criterion: latency, durability, or coupling.  |
| 26–27  | Compare synchronous call with durable asynchronous handoff.           |
| 27–28  | Select one for the named business promise; note its cost.             |
| 28–29  | Explain the rejected path and when it would become preferable.        |
| 29–30  | Address duplicate requests and repeated delivery explicitly.          |
| 30–31  | Choose how state and outbound work remain consistent.                 |
| 31–32  | Compare direct mappings with a governed contract or adapter boundary. |
| 32–33  | Identify who owns schema changes and compatibility.                   |
| 33–34  | Compare a shared platform with team-owned integration for this scope. |
| 34–35  | Name license, infrastructure, support, and change costs to estimate.  |
| 35–36  | State the capacity assumption most likely to alter the design.        |
| 36–37  | Show where ordering matters and where it does not.                    |
| 37–38  | Show how replay or repair avoids unintended business actions.         |
| 38–39  | Mark two decision records: choice, rationale, rejected alternative.   |
| 39–40  | Ask: “Which trade-off would you like me to challenge first?”          |

### 40–50: failure, security, and scale tests

| Minute | Say, ask, or draw                                                       |
|--------|-------------------------------------------------------------------------|
| 40–41  | Remove one dependency: what can still be accepted?                      |
| 41–42  | Trace backlog growth, expiry, and customer-visible status.              |
| 42–43  | Show retry limit, poison-item isolation, and human repair owner.        |
| 43–44  | Test duplicate submission and duplicate downstream delivery.            |
| 44–45  | Test a partial update and explain reconciliation.                       |
| 45–46  | Trace authentication, authorization, and least data exposure.           |
| 46–47  | Identify audit evidence, secret handling, and sensitive-data retention. |
| 47–48  | Increase peak load; locate bottleneck and backpressure point.           |
| 48–49  | State alerts and a recovery drill that prove the claim.                 |
| 49–50  | Summarize residual failure risk and the business owner of the policy.   |

### 50–60: delivery and operations

| Minute | Say, ask, or draw                                                       |
|--------|-------------------------------------------------------------------------|
| 50–51  | Name the smallest end-to-end slice to release first.                    |
| 51–52  | Describe coexistence with current flows and source-of-truth rules.      |
| 52–53  | Specify dual run or shadow comparison if safe and useful.               |
| 53–54  | Set cutover, pause, and rollback criteria.                              |
| 54–55  | Assign runbook, on-call, business exception, and data owners.           |
| 55–56  | Propose measures: user outcome, flow latency, failures, reconciliation. |
| 56–57  | State baseline to collect and target to agree; avoid invented numbers.  |
| 57–58  | Name top two assumptions and how to validate them.                      |
| 58–59  | Name the next decision, owner, and required evidence.                   |
| 59–60  | Close in one sentence: goal, chosen approach, trade-off, next gate.     |

If interrupted, answer, then return to the clock. Compress the drawing if time shrinks.

## 3. Worked answer to an ambiguous prompt

**Prompt:** “Integrate our storefront with ERP, warehouse, CRM, and finance. Orders and status should be real time. We
also have legacy interfaces to replace.” This is illustrative.

**At the start, say:** “What does *real time* mean here? Does acknowledgement mean durable receipt or ERP acceptance?
Who owns price, inventory, and the commercial order?” **Pause.** If unanswered, write: “A1: durable receipt; ERP
confirmation follows. Open: sponsor confirms customer wording.” Add: “Immediate ERP approval would change the response
path.”

**While drawing, say:** “I am separating the short intake path from downstream processing. The storefront sends a
request with a stable request ID to an order intake capability. That capability records the submission and the work to
publish as one recoverable unit, then returns a *received* status. A worker sends the order through a versioned contract
to an ERP adapter. ERP makes the commercial acceptance decision. Warehouse, CRM, and finance receive only the facts they
need from the authoritative owners. Status events update a customer-facing read view and an operations exception view.”
Draw:

```text
Customer → Storefront → Order intake + durable outbound work → ERP adapter → ERP
                              │                                  │
                              └→ status view ← confirmed/rejected ┘
                                       │
                            customer + operations
ERP/warehouse/finance/CRM: each boundary has an owner, contract, and exception path
```

**Pause at the ERP arrow:** “Can ERP reject after *received*? If yes, we need pending and rejected states. If no,
required validation belongs on the response path, or we revise the promise.”

**At the choice discussion, say:** “Durable asynchronous handoff fits the assumed receipt promise. A synchronous ERP
call simplifies immediate confirmation but couples checkout to ERP latency and availability. I would compare peak
traffic, outage duration, platform and support costs, and delayed-order impact. Immediate confirmation would make me
revisit this choice.”

**During the failure test, say:** “ERP failure allows intake only within an agreed backlog policy. Alert on pending age
and backlog growth; bound retries, isolate poison records, and reconcile submissions against ERP outcomes. A stable
business key prevents duplicate commercial actions. Sending a message does not mean *confirmed*.”

**At the close, say:** “I would migrate one flow, compare old and new outcomes by business ID, then expand when
exception, reconciliation, latency, and recovery evidence meet agreed targets. I need the acceptance definition,
authority map, and outage tolerance to finalize the contract and cost.”

## 4. Explain the same design to three audiences

The example remains the assumed storefront-to-ERP design above. Adjust vocabulary and evidence, not the underlying
promise.

**Executive sponsor (about 40 seconds).** “The design gives customers an honest *received* response while the commercial
order is confirmed by ERP. That lets the business keep track of submissions during a temporary ERP outage, subject to a
backlog limit you approve. The trade-off is a period where an order is pending. We will measure customer response time,
time to confirmation, unmatched orders, and the cost of operating the flow. Your key decision is whether *received now,
confirmed later* is an acceptable customer promise.”

**Architecture review board (about 60 seconds).** “The intake record and outbound work share a recoverable boundary,
with stable business IDs across the ERP adapter and status flow. ERP remains authoritative for commercial acceptance;
the read view is a projection. The asynchronous choice serves the assumed receipt promise and isolates a temporary ERP
outage, at the expense of pending states, reconciliation, and support cost. I rejected a direct synchronous
checkout-to-ERP dependency under that assumption. I need evidence for peak and backlog sizing, duplicate handling,
contract compatibility, boundary controls, and recovery. If immediate confirmation is mandatory, I will revisit the
decision.”

**Engineering team (about 60 seconds).** “On submission, persist the request ID, status, and outbound work together,
then return *received*. The sender may deliver more than once, so the ERP-facing command needs a stable business key and
an idempotent outcome lookup or equivalent agreed behavior. Propagate correlation IDs, version contracts, and record
state transitions from ERP's authoritative response. Bound retries; route unrecoverable records to an owned repair
queue. Alert on oldest pending age, failure rate, and reconciliation mismatches. We will test duplicate submissions, ERP
outage and catch-up, partial failure, and rollback before cutover.”

Practice all three aloud. Expand the detail each audience needs to decide or act.

## 5. Career-story worksheets: use only your own evidence

Choose one real example per worksheet. Aim for a two-minute story. Mark unverifiable numbers “unknown,” and distinguish
your contribution from the team's.

### Worksheet A — A difficult architecture choice

| Field         | Fill in from a real decision                                                                                     |
|---------------|------------------------------------------------------------------------------------------------------------------|
| Situation     | Organization/context: ___; business goal: ___; constraint or deadline: ___.                                      |
| Personal role | My decision authority: ___; people consulted: ___; work I personally did: ___.                                   |
| Options       | Option 1: ___; option 2: ___; criteria and costs compared: ___.                                                  |
| Decision      | We chose ___ because ___; I recommended/decided ___; rejected ___ because ___; revisit if ___.                   |
| Outcome       | What happened in delivery and operation: ___; unexpected consequence: ___.                                       |
| Evidence      | Decision record, baseline/after measure, incident trend, cost estimate, or stakeholder sign-off I can cite: ___. |
| Learning      | What I would repeat: ___; what I would change: ___; how I applied it later: ___.                                 |

**Probe yourself:** Who disagreed? What did the rejected option do better? Which assumption proved wrong? Why was extra
cost justified?

### Worksheet B — A production failure or mistake

| Field         | Fill in from an incident you can discuss responsibly                                                     |
|---------------|----------------------------------------------------------------------------------------------------------|
| Situation     | Service and customer/business effect: ___; detection path: ___; what was known at the time: ___.         |
| Personal role | My responsibility before and during the event: ___; action I personally took: ___.                       |
| Options       | Containment choices considered: ___; risk of each: ___; who authorized a business-impacting choice: ___. |
| Decision      | We contained by ___; restored by ___; why this sequence: ___; what I initially got wrong: ___.           |
| Outcome       | Verified recovery condition: ___; unresolved impact or follow-up: ___.                                   |
| Evidence      | Timeline, alert, ticket, reconciliation result, postmortem action, or measured trend: ___.               |
| Learning      | Design/process change: ___; how its effectiveness was checked: ___.                                      |

**Probe yourself:** How did you verify data after recovery? Which alert was missing? What did you tell the business
owner?

### Worksheet C — A business–technical conflict

| Field         | Fill in from a real disagreement                                                                  |
|---------------|---------------------------------------------------------------------------------------------------|
| Situation     | Requested outcome and deadline: ___; technical or operational constraint: ___; stakeholders: ___. |
| Personal role | What I owned: ___; whose decision it ultimately was: ___; how I framed the disagreement: ___.     |
| Options       | Fast path: ___; safer or staged path: ___; cost, risk, and customer impact of each: ___.          |
| Decision      | Agreement reached: ___; concession or explicit risk acceptance: ___; who signed off: ___.         |
| Outcome       | What was delivered: ___; what remained open: ___; observed business result: ___.                  |
| Evidence      | Meeting decision, phased plan, risk record, customer feedback, or measured result: ___.           |
| Learning      | What changed in my stakeholder approach: ___; how I would handle a repeat: ___.                   |

**Probe yourself:** Did you translate risk into business terms and offer an alternative? What did you do after a
decision you opposed?

## 6. Mock follow-ups and practice prompts

Give a 90-second answer and a 30-second challenge response. Name the criterion, alternative, evidence, and decision
owner.

1. **Cost:** “Your design adds a broker and support workload. Defend the total cost against a direct API integration.
   Which volume and outage assumptions would flip your answer?”
2. **Failure handling:** “ERP is down for six hours during a sales peak. What can you still promise? When do you stop
   intake, how do you recover, and how do you prove every order is accounted for?”
3. **Migration:** “There are dozens of existing point-to-point flows. Choose the first migration slice, show coexistence
   and cutover, and defend your rollback threshold.”
4. **Stakeholder decision:** “The sponsor wants instant confirmation, but operations cannot support the dependency's
   availability. What options do you present, who decides, and what do you document?”
5. **Security:** “A partner needs order updates but should not see payment details. Show the trust boundary, data
   minimization, authorization, and audit proof.”
6. **Consistency:** “A customer retries after a timeout. Then a downstream event is delivered twice. Which business
   actions may repeat, and which may not?”
7. **Scale:** “Peak volume doubles for four hours. Identify the first bottleneck, backpressure behavior, operational
   signal, and cost consequence.”
8. **Career evidence:** “What did *you* decide, who disagreed, what happened afterward, and what artifact or measure
   supports your account?”

## 7. Self-review rubric and final check

Score each dimension **1–4**: **1** missing; **2** vague; **3** clear and testable; **4** defended under challenge.
Practice the two lowest scores next.

| Dimension             | A score of 4 sounds like                                                                     |
|-----------------------|----------------------------------------------------------------------------------------------|
| Problem framing       | Defines business promise, user, owner, scope, and the question that changes the design.      |
| Time control          | Covers all five phases and closes with decisions before the hour ends.                       |
| Board clarity         | A listener can trace one normal flow and one exception without a narration rescue.           |
| Trade-offs            | Gives criteria, selected and rejected options, costs, and reversal conditions.               |
| Failure and security  | Explains detection, containment, recovery, data boundaries, and accountable owners.          |
| Delivery and outcomes | Gives staged migration, operational handoff, baseline, proposed measures, and evidence gate. |
| Audience fit          | Uses the same facts while changing emphasis for sponsor, board, and team.                    |
| Career credibility    | Separates personal role from team work and supports outcomes without invented metrics.       |

**Before you finish an answer, check:**

- [ ] I stated the business promise before naming products or patterns.
- [ ] Every product name serves a requirement, constraint, or real installed capability; I could explain the design
  without it.
- [ ] I used one level of drawing detail at a time and stopped when the listener had enough to challenge a decision.
- [ ] I labeled assumptions, facts, and open decisions separately.
- [ ] I named a rejected alternative and the condition that would make it preferable.
- [ ] I stated who owns each important business fact and exception.
- [ ] I gave a measurable outcome with a collection method, baseline to obtain, and decision owner; I did not invent a
  target or result.
- [ ] I described a failure, a recovery check, and a migration pause or rollback point.
- [ ] In a career story, I can point to evidence for the outcome and say exactly what I personally did.

**Final rehearsal:** Run the prompt in 60 minutes, five minutes, and three audience summaries. Explain any changed
decision.
