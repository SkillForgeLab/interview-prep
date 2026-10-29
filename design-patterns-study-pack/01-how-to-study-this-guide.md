# Design patterns and backend architecture

**Chapter 1: How to study this guide**

Practice designs, not claims about an employer.

## 1. How to study this guide

**Design principle** = a rule for making choices, such as keeping responsibilities clear. **Design pattern** = a
reusable way to organize classes or objects for a recurring problem. **Architecture pattern** = a way to organize larger
components and their communication. An implementation may use several patterns, but every pattern should solve a named
problem.

In the upcoming technical round, prepare to explain a design choice while coding or discussing a project. For the later
system-design round, practice drawing boundaries, data flow, failure paths, and tradeoffs. Do not spend this week
memorizing a pattern catalog. Learn the problem, the mechanism, the cost, and when to avoid the pattern.

### Fit into the existing 20-hour plan

**During Java fundamentals — 35 minutes.** Study SOLID, composition, immutability, Strategy, Factory, Builder.
*Checkpoint:* Refactor one conditional-heavy example aloud.

**During Spring and API study — 35 minutes.** Study layering, Adapter, Repository, dependency inversion, transactions.
*Checkpoint:* Trace a request and name each responsibility.

**During project-story practice — 30 minutes.** Connect one real decision to its tradeoff and test. *Checkpoint:* Give a
two-minute design story with personal ownership.

**During production review — 35 minutes.** Study outbox, retry, circuit breaker, bulkhead, idempotency. *Checkpoint:*
Explain timeout and duplicate-event behavior.

**During a mock follow-up — 15 minutes.** Practice selecting and critiquing patterns. *Checkpoint:* Answer without
buzzwords.

That is **2 hours 30 minutes** inside your 20-hour plan. For the later system-design round, revisit the architecture
section more deeply. If the interviewer asks about a technology you used, give its actual implementation details before
naming a pattern.

Use this answer structure: **"The problem was __. I chose __ because __. The cost was __. I handled failure by __. We
verified it with __."** Speaking the tradeoff is what makes an answer sound senior.
