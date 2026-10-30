# Enterprise Modernization and Architecture Roadmaps

**Core learning guide for Solution Architect interviews**

Modernization changes a working system while the business still depends on it. This guide covers current-state
discovery, migration options, transition architecture, and roadmaps. It builds on
[Application and Integration Architecture](05_Application_API_and_Integration_Architecture.md) and
[Data Architecture](03_Data_Architecture_and_Database_Selection.md).

## Learning outcomes

- Assess a legacy system's business role, dependencies, data, risk, and constraints.
- Compare incremental and replacement approaches without assuming one universal migration path.
- Plan coexistence, compatibility, data movement, cutover, rollback, and retirement.
- Explain a phased roadmap in terms of business outcomes and measurable exit criteria.

## 1. Understand the system before changing it

Map capabilities, users, business rules, integrations, data flows, operational ownership, critical batch windows,
recovery requirements, and known failure points. Separate verified facts from assumptions. Include undocumented
interfaces and manual processes; they may be part of the actual system contract.

Establish why change is needed: cost, delivery speed, risk, resilience, capability gaps, or an expiring platform.
Compare urgency and value with the risk of changing a system whose behavior is not fully understood.

## 2. Select a migration approach by constraint

Common migration “R” labels include **rehost** (move with limited change), **replatform** (make bounded platform
changes), **refactor** (substantially change the design), **repurchase** (move to a replacement product), **retire**
(remove the capability), and **retain** (keep it for now). Some frameworks add other categories. The labels are less
important than the target outcome, constraints, and operating model; do not use a category as a substitute for a
migration plan.

The **Strangler Fig** approach replaces parts of a legacy capability incrementally. A routing or facade layer directs
selected behavior to the new implementation while the old system continues to serve the rest. It can reduce a risky
single cutover, but creates a period of dual operation, routing complexity, and data consistency work.

Choose a bounded slice with clear ownership, a reversible rollout, and measurable value. Do not split by technology
alone if business behavior and data ownership remain unclear.

## 3. Design the transition, not just the target

For each phase, identify:

- Business outcome and included capability.
- Prerequisites, owner, dependencies, and decision authority.
- Data source of truth and synchronization or migration method.
- API and message compatibility requirements.
- Test, rollout, rollback, and support plan.
- Risks, exit criteria, and conditions to stop or change course.

During coexistence, prevent ambiguous writes. Define whether the old or new system owns each fact, how mismatches are
reconciled, and how the team knows the migration is complete. For cutover, rehearse data validation, traffic switching,
monitoring, rollback limits, and retirement of replaced components. A rollback may be impossible after irreversible
data changes; state that boundary in advance.

## 4. Build a roadmap that makes tradeoffs visible

Sequence increments around business value, risk reduction, dependencies, delivery capacity, and operational readiness.
Include temporary transition costs and keep critical existing services supported until the new path meets its exit
criteria.

**Roadmap check:**

> Each phase should have a business result, accountable owner, dependencies, risk controls, and evidence for moving
> forward. A technology list is not a roadmap.

**Say it professionally:**

> “I would first establish the current behavior, owners, and constraints. Then I would choose a migration slice that
> delivers measurable value, make coexistence and data ownership explicit, and use rehearsed exit criteria to decide
> when to expand or retire the legacy path.”

## 5. Practice and self-check

Plan a zero-downtime modernization of a legacy customer-service workflow. Draw current and target states, identify an
incremental slice, assign data ownership during coexistence, and describe validation and rollback. State what
“zero downtime” means for users and which limitations require business agreement.

Check your answer: Did you account for hidden integrations and manual work? Is every phase independently supportable?
Can the team determine from evidence when it is safe to cut over and retire the old system?

## References

- [Azure Architecture Center: cloud adoption and migration guidance](https://learn.microsoft.com/en-us/azure/architecture/cloud-adoption/)
- [AWS Prescriptive Guidance: migration strategies](https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-retiring-applications/migration-strategies.html)
- [Azure Architecture Center: design patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
