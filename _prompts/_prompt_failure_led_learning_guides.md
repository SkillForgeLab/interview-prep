# Reusable prompt: Learn architecture through failures

Use this prompt to create a problem-solving version of an existing topic guide without replacing it.
It requests independent enterprise cases and full worked solutions, not an interactive quiz.
Include cases that need complementary protections and others that compare competing architectures,
where the source topic supports both.

## How to use it

Replace `[SOURCE_GUIDE_PATH]` with the guide that defines the topic.
Replace `[NEW_GUIDE_PATH]` with a different Markdown output path.
Paste the prompt below into your coding assistant and attach or tag the source guide.

## What this prompt should produce

A reader should be able to explain the weak design's appeal, identify the exact failure,
distinguish protections that must work together from architectures that compete for the same role,
and compare three relevant approaches or options. They should be able to defend both the architecture
choice and its required protections, including business costs, security limits, recovery, and ownership.

The result should remain within the source topic. It should not turn every guide into the same
outbox-and-retry tutorial or imply that every enterprise problem needs more services.

## Copy-ready prompt

```
[SOURCE_GUIDE_PATH]:

[NEW_GUIDE_PATH]:


Use [SOURCE_GUIDE_PATH] as the scope and conceptual reference.
Create a new Markdown learning guide at [NEW_GUIDE_PATH].
Do not modify the source guide or any existing PDFs or archived material.
If the output already exists, ask whether to revise it or use a new path.

GOAL

Teach this topic by solving problems rather than mainly reading definitions.
Use several independent, hypothetical enterprise cases, with complete worked
solutions. Use distributed-system failures as the main learning engine where
they are relevant to the source topic. Do not force unrelated patterns into it.

READ AND MAP THE SOURCE FIRST

Read the guide and applicable repository authoring instructions.
Identify its learning objectives, assumptions, exclusions, prerequisites,
important distinctions, and technical guarantees.
Preserve that scope and conceptual coverage without copying its lesson order.
Choose enough distinct cases to teach the objectives without repetitive filler.
Introduce definitions when a case needs them, with a compact reference at the end.

PLAN A DELIBERATE MIX OF CASES

Include distinct cases for both complementary protections and competing
architectures where the source scope supports them. Do not make every case
the same kind of comparison or substitute one mixed case for the entire mix.
If the source cannot support one category, explain that limitation rather
than inventing an irrelevant architecture comparison.

Complementary-protection cases address different failure gaps with controls
that work together. For example, durable work storage prevents forgotten
notifications, duplicate handling limits repeated delivery, and reconciliation
repairs unresolved outcomes where evidence permits, escalating the rest.
Explain what each control contributes and what breaks if it is omitted.
They are not competing substitutes or individual end-to-end guarantees.

Competing-architecture cases compare different ways to organize or deliver
the same capability under the same business requirements. For example, decide
whether a capability belongs in a modular backend, an independently owned
service, or an existing enterprise platform when those are genuine options.
Compare ownership, deployment and data boundaries, communication failure
behavior, security, recovery, and business costs, not just technology names.

Mixed cases make an architecture decision and then identify the complementary
protections needed within that choice. Keep these two decision levels separate.
For example, choosing a notification worker or a shared notification service
does not remove the need for durable obligations and safe delivery recovery.

Do not invent personal experience, employer facts, production incidents,
interview questions, metrics, numerical targets, or technical guarantees.
Clearly label hypothetical requirements and stakeholder decisions.
Ask focused questions if an ambiguity materially changes the scope or approach.

FOR EACH CASE

1. Establish the business problem and success promise.

State the user outcome, constraints, invariant, and teaching assumptions.
Explain what must happen immediately and what may finish later.
Identify the business decision owner and authoritative data owner.
Label the case "Complementary protections", "Competing architectures", or
"Mixed", and state the decision the reader is learning to make.

2. Start with a plausible weak design.

Show a small diagram and trace the normal request path.
Identify responsibilities, local calls, network/process boundaries,
authoritative records, copies, and missing or ambiguous ownership.
Explain why a team might initially choose this design.
Do not call a design weak merely because it is simple or not microservices.

3. Inject a specific failure.

Use a precise sequence: for example, a lost reply after commit,
a crash between writes, stale data, overlapping changes, or a slow dependency.
Track committed state, user-visible state, and what each participant knows.
Distinguish an uncertain outcome from confirmed failure or rollback.
Give a few short diagnosis questions, immediately followed by a full solution.
Do not require me to answer before I can read the explanation.

4. Explain why the design fails.

Connect the root weakness to the violated guarantee and observed symptoms.
Explain business impact, customer harm, costs, operational burden,
security risks, recovery needs, and ownership gaps.
Keep the discussion proportionate to the source topic.

5. Compare three relevant remediation approaches or architecture options.

Choose the comparison level that fits the case: complementary protections,
competing architectures, or clearly separated decisions in a mixed case.
Include established remediation mechanisms and different architecture options
across the guide; do not force three controls plus three architectures into
every case.

For each approach, explain:
- How it works and which part of the failure it prevents or mitigates.
- Its guarantee boundary, residual failures, and unmet requirements.
- When it fits, when it does not, and the assumptions it requires.
- Technical and business trade-offs, including delivery and operating costs.
- Security implications, safe recovery, and the accountable operating owner.

For complementary protections, map each control to its specific failure gap
and show why the required combination is stronger than any control alone.
Trace what remains unsafe if one required protection is removed.

For competing architectures, show a small diagram for each option and trace
the same failure through each under the same requirements. Explain why one
fits better, when another would win, and which protections all options still
need. A service boundary, broker, or platform does not itself provide every
correctness and recovery guarantee.

For mixed cases, distinguish choosing an architecture from selecting its
required protections. Do not present a local transaction and microservices,
for example, as equivalent alternatives at the same decision level.

Do not claim a universal "top three" ranking or substitute a vendor shortlist.
Explain whether the approaches are alternatives, complementary controls,
or layers that should be combined. Do not treat detection as prevention,
or imply that each partial mitigation independently solves the whole case.
An option that violates the current requirements must be labeled unsuitable
unless those requirements explicitly change.
Do not manufacture three near-identical options or expand beyond scope just
to fill the comparison; explain and resolve a genuine mismatch if it arises.

6. Recommend and demonstrate an improvement.

For complementary cases, recommend the minimum sufficient combination.
For architecture cases, select the best-fitting option under the assumptions
and name its required protections. For mixed cases, explain both decisions.
Show the improved design and trace the same failure through it.
Explain why its outcome differs from the weak design.
State remaining risks and who accepts them.
Name the evidence or requirement changes that would alter the recommendation.

7. Make recovery operationally concrete.

Explain detection signals, authoritative evidence, containment,
safe retry or repair, permanent-failure handling, and escalation.
Identify who owns the data, operates the component, authorizes repair,
communicates with affected users, and confirms completion.
Distinguish restoring service availability from resolving unfinished
or uncertain business work.
Provide an observable acceptance condition for the injected failure.
Do not invent service-level or recovery targets; identify needed agreements.

8. Help me explain the reasoning.

Finish with a concise architect-style explanation and one follow-up question
with a worked answer. Emphasize the decision, cause, guarantee, cost, and owner,
not a memorized list of technologies.

ACCURACY AND BOUNDARIES

Use primary technical references for important guarantees.
Keep source links near the claims they support and distinguish sourced
mechanisms from teaching assumptions and your recommendations.
Do not claim that a queue guarantees business completion, that a timeout
means no commit, or that a local transaction covers remote side effects.
Distinguish idempotency from concurrency control, stale display from
authorization, and compensation from transaction rollback when applicable.
Never promise end-to-end exactly-once behavior without defining its scope
and the cooperation required from every relevant participant.
If a dimension does not apply, explain why rather than adding filler.

FINISH THE GUIDE

Include a compact concept reference and a source-coverage map.
Add a design-defense exercise with a full worked answer.
Preserve the distinction between hypothetical designs and verified experience.
Link back to the unchanged original guide for foundational reference.

Use clear headings, short paragraphs, small diagrams, and bold-led
explanation blocks. Avoid wide tables and dense nested lists.
Use numbered steps for sequences, not for every explanatory paragraph.
Follow the repository's Markdown style and keep diagrams readable at A4 width.

Review source coverage and the deliberate mix of case types.
Check that each case explicitly identifies its comparison level and explains
three substantive approaches or options without manufacturing alternatives.
Verify control-to-failure mapping and omission consequences for complementary
cases, and comparable diagrams and failure traces for architecture cases.
Review guarantee limits, business/security trade-offs, recovery ownership,
and links.
Confirm the source remains unchanged.
Produce Markdown only; do not create or regenerate PDFs unless requested.
```
