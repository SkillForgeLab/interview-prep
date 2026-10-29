# General-purpose Solution Architect interview questions

For a senior Solution Architect candidate. Questions are grouped by the topics in `general-purpose-SA.md`; scenario and
challenge questions are designed for spoken system-design practice.

## 1. Requirements and architecture fundamentals

1. A business sponsor says the platform must be “fast and always available.” What questions would you ask to turn that
   into measurable architecture requirements?
2. A new service expects 2 million daily users but has no traffic forecast. How would you estimate peak requests,
   storage growth, and capacity headroom? Which assumptions would you validate first?
3. Walk through an architecture diagram you would present to both executives and engineers. Which boundaries, data
   flows, trust zones, and failure points must it show?
4. Describe a consequential architecture decision you made. What alternatives did you consider, how did you record the
   decision, and what evidence would cause you to revisit it?

## 2. Distributed systems

5. An order API calls inventory, payment, and shipping services. Which interactions should be synchronous, and which
   should be asynchronous? Why?
6. A client times out after submitting a payment, but the payment may have succeeded. How would you prevent a duplicate
   charge when the client retries?
7. Design a cross-service order workflow without a distributed database transaction. Where would you use a saga, an
   outbox, and compensation? What cannot be undone?
8. A network partition isolates part of your system. Which operations should remain available, which should fail closed,
   and how would you reconcile data afterward?

## 3. Databases and data architecture

9. You are choosing between PostgreSQL, a document database, and a key-value store for a new product. What workload and
   data properties decide the choice? When would you reject each option?
10. A transaction spans customer, order, and payment records. Where should the transaction boundary sit, and what
    isolation level would you choose?
11. Reads are growing ten times faster than writes. Compare indexes, read replicas, caching, partitioning, and sharding.
    What would you try first, and what new failure modes arise?
12. How would you migrate a large production database with no prolonged outage while preserving data correctness,
    rollback options, and auditability?

## 4. Messaging and event-driven architecture

13. When is a queue warranted between two services, and when would a direct API call be simpler or safer?
14. Compare a work queue, publish-subscribe broker, and event stream for order events. What requirements for fan-out,
    retention, replay, and ordering drive the choice?
15. The team proposes Kafka instead of a managed queue such as SQS. What capability would justify the added operational
    complexity, and when would you reject Kafka?
16. A consumer processes the same message twice, then falls behind for six hours. How would you handle deduplication,
    backpressure, dead-letter messages, replay, and recovery?

## 5. Application and integration architecture

17. A team wants to split a mature monolith into microservices. How would you decide whether a modular monolith is the
    better next step?
18. How would you identify bounded contexts and data ownership when two teams both claim the customer record?
19. Compare REST, gRPC, and GraphQL for an internal service, a public partner API, and a mobile application. Which
    contract and versioning risks matter most?
20. An external partner has a slow, unreliable API and strict rate limits. Design the integration, including timeouts,
    retries, idempotency, and operational ownership.

## 6. Scalability and performance

21. A service meets average latency targets but fails at the 99th percentile during traffic spikes. How would you locate
    and remove the bottleneck?
22. What would make you scale vertically, horizontally, or both? How would you prove autoscaling responds quickly enough
    to a sudden tenfold spike?
23. A popular product causes a hot database partition and a cache stampede. What changes would you make, and what
    trade-offs would they introduce?
24. How would you plan and run a performance test that represents realistic user behavior, dependency limits, and
    failure conditions?

## 7. Reliability and disaster recovery

25. A business asks for 99.99% availability. What downtime budget does that imply, and how would it affect architecture,
    operations, and cost?
26. Compare multi-zone, active-passive multi-region, and active-active multi-region designs for a customer-facing
    application. What business requirement would justify each step up?
27. The primary database region fails during a write-heavy period. Walk through detection, failover, data loss limits,
    traffic routing, and recovery of the old region.
28. How would you define SLIs and SLOs for an order-placement journey, then use them to drive alerts, graceful
    degradation, and disaster recovery drills?

## 8. Security architecture

29. Design authentication and authorization for employees, customers, and partner applications. Where do OAuth 2.0,
    OpenID Connect, SSO, and service identities fit?
30. A tenant administrator must see only their organization's data. How would you enforce tenant isolation across APIs,
    databases, caches, logs, and background jobs?
31. How would you apply least privilege, secrets management, encryption, and network controls to an application running
    across cloud services and on-premises systems?
32. Walk through a threat model for a payment or customer-data flow. What abuse cases, audit evidence, and compliance
    constraints would influence the design?

## 9. Cloud and infrastructure

33. A proposed design uses Kubernetes, a managed database, and several managed messaging services. Which components
    would you keep, replace, or simplify for a small team, and why?
34. When would you choose containers, Kubernetes, or serverless for a new workload? Include scaling behavior, workload
    duration, control, cost, and team expertise.
35. How would you design network connectivity and trust boundaries among public clients, private services, cloud
    networks, and an on-premises data center?
36. What would your infrastructure-as-code and deployment pipeline need to prevent configuration drift and unsafe
    production releases?

## 10. Enterprise modernization

37. A legacy monolith handles critical transactions and cannot be stopped for a long migration. How would you identify a
    first capability to extract using an incremental migration approach?
38. How would you move data from an old system to a new one while old and new applications both serve users? Who owns
    writes at each stage?
39. Explain a zero-downtime cutover plan, including backward-compatible contracts, traffic shifting, reconciliation,
    rollback, and the point after which rollback is no longer simple.
40. A hybrid architecture must keep sensitive data on-premises. How would that constraint affect latency, reliability,
    security, and the modernization roadmap?

## 11. Operations and cost

41. An order failed, but logs from five services disagree. What observability design would help an on-call engineer
    reconstruct the full transaction?
42. Compare blue-green and canary releases for a high-risk service. What metrics and automatic stop conditions would you
    use?
43. A proposed architecture costs twice the approved budget. Which costs would you measure first, and how would you
    reduce spend without violating agreed service levels?
44. How would you decide whether to build a capability or buy a managed product, accounting for total cost, operational
    skill, vendor risk, and exit strategy?

## 12. Architecture leadership

45. Present a major architecture choice to a nontechnical executive in two minutes. What business outcome, risk, cost,
    and decision do you emphasize?
46. A respected tech lead disagrees with your design. How do you test the competing ideas and reach a decision without
    bypassing the team?
47. Security, operations, and delivery teams have conflicting requirements. How would you make assumptions and risks
    visible, assign owners, and resolve the conflict?
48. Describe an architecture decision of yours that failed in production. What did you miss, how did you respond, and
    what changed in your design process?

## Timed system-design exercises

49. **E-commerce order and payment platform:** Design checkout for 5,000 orders per minute with external payment and
    inventory systems. Show transaction boundaries, duplicate protection, failure recovery, and five major decisions you
    would defend.
50. **Banking fund transfer:** Design transfers between accounts with strict correctness, complete audit history, and
    retries after uncertain outcomes. Specify consistency, idempotency, reconciliation, and disaster recovery.
51. **Real-time notifications:** Design email, SMS, and push notifications for 20 million users, including fan-out, user
    preferences, provider outages, retries, ordering, and cost controls.
52. **Multi-tenant SaaS:** Design a platform for 1,000 enterprise tenants with different data-residency and isolation
    requirements. Explain identity, data placement, noisy-neighbor controls, observability, and tenant-specific
    recovery.
53. **Legacy monolith modernization:** Move customer and order capabilities from an on-premises monolith to the cloud
    while serving users continuously. Show coexistence, data ownership, cutover, and rollback.
54. **High-volume event ingestion:** Design ingestion for 1 million events per second from devices or applications.
    Cover partitioning, ordering, schema evolution, retention, replay, downstream processing, and cost.

## Interviewer challenge questions

55. Why PostgreSQL instead of MongoDB for this design? What change in requirements would reverse your decision?
56. Why Kafka instead of SQS or RabbitMQ here? Which feature are you using that justifies its operating cost?
57. Why introduce a queue at all? What happens if you remove it?
58. Why microservices instead of a simpler modular monolith? How do your team structure and deployment needs support the
    choice?
59. Why Redis caching? What is the source of truth, how stale may cached data be, and how does the system behave when
    Redis fails?
60. Why Kubernetes instead of serverless or managed containers? What would make you change your mind?
61. Why deploy across multiple regions? Can the stated RTO and RPO be met with a less costly design?
62. How do you maintain consistency across services when messages are delayed, duplicated, or processed out of order?

## Career examples to prepare

63. Tell me about the hardest architecture trade-off you have made. What constraints mattered, who disagreed, and what
    evidence supported the outcome?
64. Tell me about a major outage or architecture mistake you owned. What was the customer impact, how did you recover,
    and what did you change afterward?
65. Tell me about a project where the technically strongest design conflicted with budget, timeline, or organizational
    readiness. What did you ship and why?
