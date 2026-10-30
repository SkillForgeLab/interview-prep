# Requirements, Quality Attributes, and Capacity

**Core learning guide for Solution Architect interviews**

Use this guide to turn an ambiguous business request into explicit architecture constraints. It follows
[Distributed Application Design](01_Distributed_Application_Design_for_Solution_Architect_Interviews.md), which covers
component boundaries and interactions.

## Learning outcomes

After studying this guide, you should be able to:

- Separate business outcomes, functional requirements, and quality attributes.
- Turn vague quality goals into measurable targets and clarify who accepts the tradeoffs.
- Estimate first-order traffic and storage needs with stated assumptions.
- Explain how requirements change the design rather than selecting technologies first.

No specific cloud provider or project history is assumed.

## 1. Start with the decision the business needs

A request such as “make checkout faster and more reliable” is a goal, not an architecture requirement. Establish the
user, business outcome, current pain, constraints, and evidence of success before drawing components.

```text
Business outcome -> user journey -> system behavior -> measurable target -> design choices
```

For example, “reduce checkout abandonment” may lead to a target for checkout response time, but the business must
specify the measured population, percentile, time window, and acceptable error rate. Averages alone can hide a poor
experience for a significant portion of users.

**Functional requirement:**

> A behavior the system must provide, such as accepting an order, calculating a quote, or letting an operator cancel a
> request.

**Quality attribute:**

> A property of that behavior, such as how quickly it responds, how often it is available, how it recovers, or what
> data it protects.

## 2. Make quality attributes testable

Ask what must happen, under which conditions, for which users, and how the result will be measured. A useful requirement
describes a scenario, not just a label.

| Attribute            | Questions that make it concrete                                                |
|----------------------|--------------------------------------------------------------------------------|
| Latency              | Which journey or operation? What percentile and time window?                   |
| Throughput           | Sustained and peak requests or events per second? Which request mix?           |
| Availability         | Which service and user-visible capability? What measurement window?            |
| Recovery             | What are the recovery time objective (RTO) and recovery point objective (RPO)? |
| Security and privacy | Which data, users, threats, obligations, and accountable owners?               |
| Cost                 | Which cost boundary, utilization assumptions, and budget owner?                |
| Changeability        | Which teams release independently, and what change failure rate is acceptable? |

An **RTO** is the target time to restore a service after disruption. An **RPO** is the maximum targeted loss of
recently changed data, expressed as a time interval. Neither is a synonym for availability; confirm which business
process and data each target applies to.

Avoid unsupported absolutes such as “zero downtime” or “infinite scale.” Ask which event is in scope, what users
experience, and what budget or operational capacity is available.

## 3. Estimate capacity without pretending to know exact demand

Early estimates reveal dominant costs and likely bottlenecks. They are hypotheses to validate with product analytics,
load tests, and operational data.

1. Estimate active users or clients in a representative time window.
2. Estimate actions per user and the fraction that reach each operation.
3. Convert the busiest interval into peak requests per second (RPS).
4. Estimate request size, retained data, growth, and replication or backup overhead.
5. Add explicit headroom for bursts, recovery, and uncertainty.

**Illustrative estimate:**

> Suppose 100,000 active users generate 12 requests each over a 10-hour day. The average is about 33 requests per
> second (`100,000 × 12 ÷ 36,000`). If a measured or assumed peak-to-average factor is 5, plan to test near 165 RPS.
> This is not a forecast: the traffic shape, retries, background jobs, and endpoint mix can change it substantially.

Storage estimates need the retained record size, write volume, retention period, indexes, replicas, and backups. State
whether units are decimal or binary and whether data compression is assumed. Do not equate request volume with database
write volume; one request can cause several reads and writes.

## 4. Trace requirements into design and validation

Keep a short chain from the business need to the implementation decision:

```text
Checkout must remain usable during a payment-provider slowdown
  -> define acceptable checkout behavior and latency
  -> decide whether payment must be confirmed synchronously
  -> define timeout, pending state, retry and recovery behavior
  -> test degraded dependency behavior and measure customer impact
```

The design may expose a pending status, queue work, use a fallback, or reject the request safely. Which option is right
depends on business invariants. Make the owner of each requirement and the evidence for acceptance explicit.

**Say it professionally:**

> “Before choosing a platform, I would agree on the business journey, its measurable service targets, and the
> constraints we cannot violate. I would then compare options against those targets and validate the highest-risk
> assumptions with data or a focused test.”

## 5. Practice and self-check

Choose one scenario from [System Design Practice](13_System_Design_Practice_and_Interview_Synthesis.md). Write five
questions that clarify its scope, then define three measurable quality targets. Estimate its average and peak traffic
using visible assumptions. For each target, name one design implication and one way to test it.

Check your answer: Are units, time windows, user populations, and owners clear? Did you distinguish a target from a
measured fact? Can you explain which decision would change if a target were relaxed?

## References

- [AWS Well-Architected Framework pillars](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Google Cloud Architecture Framework](https://docs.cloud.google.com/architecture/framework)
