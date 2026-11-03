# Standard 10-minute system design template

Focus on architecture decisions, why we made them, alternatives,
and key points to remember.

No assessments or unnecessary theory.

## Rules for all future designs

| Principle                | How we'll apply it                                                   |
|--------------------------|----------------------------------------------------------------------|
| 10-minute answer         | Keep details proportional to their importance                        |
| Why over what            | Every major design choice needs a reason                             |
| Simple before complex    | Start with the baseline, add complexity only when justified          |
| Concepts in context      | Define technical terms briefly where used                            |
| Trade-offs               | Compare meaningful alternatives, not every technology                |
| Breadth                  | Avoid repeating concepts already covered                             |
| Solution Architect focus | Include integration, reliability, security, and operational concerns |
| No assessments           | Explanation only                                                     |
| Key points               | End with five easy-to-recall takeaways                               |

Use this standard 10-minute system design template.

---

# System Design — [Problem Name]

## 1. Problem & Requirements

**Problem:** [One or two sentences describing what we are designing.]

**Functional requirements:**

- [Core functionality 1]
- [Core functionality 2]
- [Core functionality 3]

**Non-functional requirements:**

- Latency: [Target or requirement]
- Scale: [Traffic, users, data volume]
- Consistency: [Strong / Eventual — where and why]
- Availability: [Expected reliability]

**Key assumption:** [Most important assumption influencing the design.]

## 2. High-Level Architecture

Draw a simple ASCII architecture diagram showing the major components and
connections.

For every important component, explain:

- **What:** What does it do?
- **Why:** Why is it needed?

Avoid adding technology without a clear reason.

## 3. Key Design Decisions — Most Important Section

| Decision      | Choice                  | Why      | Alternative / Trade-off |
|---------------|-------------------------|----------|-------------------------|
| Communication | [REST / gRPC / Events]  | [Reason] | [Alternative]           |
| Database      | [SQL / NoSQL]           | [Reason] | [Alternative]           |
| Consistency   | [Strong / Eventual]     | [Reason] | [Trade-off]             |
| Caching       | [Redis / None]          | [Reason] | [Trade-off]             |
| Messaging     | [Kafka / Queue / None]  | [Reason] | [Alternative]           |
| Scaling       | [Horizontal / Sharding] | [Reason] | [Trade-off]             |

Only include decisions relevant to this problem.

**Explain critical concepts briefly when introduced.**

## 4. End-to-End Request Flow

Explain what happens from the initial request to the final response.

1. [Request enters the system]
2. [Validation and business logic]
3. [Data access or coordination]
4. [Persistence and consistency]
5. [Response]
6. [Asynchronous processing, if applicable]

Highlight where correctness, latency, or concurrency affects the flow.

## 5. Data Model & Correctness

**Core entities:** [Main tables, documents, or keys]

**Source of truth:** [Authoritative data store]

**Critical invariant:** [What must never go wrong?]

**Concurrency handling:** [Atomic update / Lock / Versioning / Other]

Keep schema details minimal unless they drive an important architectural
decision.

## 6. Failure Handling, Scalability & Security

| Scenario                  | Design response | Why      |
|---------------------------|-----------------|----------|
| Component failure         | [Approach]      | [Reason] |
| Duplicate/retried request | [Approach]      | [Reason] |
| Database failure          | [Approach]      | [Reason] |
| Traffic spike             | [Approach]      | [Reason] |
| Security threat           | [Approach]      | [Reason] |

Include only relevant scenarios. Explain any important recovery or
degraded-operation trade-offs.

## 7. Key Points to Remember

Five memorable takeaways:

1. **[Most important architectural decision]** — [Why]
2. **[Critical correctness or consistency decision]** — [Why]
3. **[Scalability decision]** — [Why]
4. **[Reliability/security decision]** — [Why]
5. **[Most important trade-off]** — [Why]

## 8. Interview Closing Summary

A concise paragraph covering:

- What architecture was chosen.
- Why the most important technology decisions fit.
- How correctness and reliability are maintained.
- How the system can scale.
- What trade-off was accepted.