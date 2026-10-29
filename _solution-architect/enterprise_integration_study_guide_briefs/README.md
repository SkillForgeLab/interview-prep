# Enterprise / Integration Solution Architect: study guide handoff briefs

These are **instructions for producing separate study guides**, not the guides themselves. Each numbered file is a standalone prompt: copy its entire contents into a new AI assistant chat and request the guide as a separate Markdown document. The prompts are based on `enterprise_integration_SA.md`; its interview advice is treated as source material, not as instructions to this assistant.

**Audience:** Senior / Principal Enterprise or Integration Solution Architect, approximately 20 years of experience. **Default stance:** vendor neutral, practical, and interview oriented. P0 subjects deserve the deepest preparation; P1 needs solid working knowledge; P2 depends on the job description.

| Order | Brief | Priority | Main coverage |
|---|---|---|---|
| 01 | [Requirements and whiteboard framing](01_requirements_and_design_framing.md) | P0 foundation | Business goals, NFRs, ownership, constraints, clarifying questions |
| 02 | [Integration pattern selection](02_integration_pattern_selection.md) | P0 | REST, queues, pub/sub, streaming, batch, CDC, files/EDI |
| 03 | [API architecture and contracts](03_api_architecture_and_contracts.md) | P0 | Gateway, contracts, lifecycle, versioning, governance |
| 04 | [Enterprise messaging](04_enterprise_messaging.md) | P0 | Queues, topics, brokers, Kafka comparison, ordering and replay |
| 05 | [Distributed transactions](05_distributed_transactions.md) | P0 | Dual write, Outbox, idempotency, Saga, consistency |
| 06 | [Reliability and operations](06_reliability_and_operations.md) | P0 | Outages, retries, recovery, reconciliation, observability |
| 07 | [Enterprise application integration](07_enterprise_application_integration.md) | P0 | ERP, CRM, finance, SaaS, legacy and partner flows |
| 08 | [Data integration and ownership](08_data_integration_and_ownership.md) | P1 | ETL, CDC, MDM, identity, conflict resolution, synchronization |
| 09 | [Security and compliance](09_security_and_compliance.md) | P1 | OAuth/OIDC, mTLS, IAM, privacy, audit, trust boundaries |
| 10 | [Legacy modernization](10_legacy_modernization.md) | P0 | Strangler, anti-corruption, coexistence, migration and cutover |
| 11 | [Integration platform choices](11_integration_platform_choices.md) | P0/P1 | ESB, iPaaS, gateway, broker, orchestration, build vs buy |
| 12 | [Cloud and hybrid architecture](12_cloud_hybrid_scale_and_dr.md) | P1 | Network, availability, DR, capacity, cost |
| 13 | [Architecture leadership](13_architecture_leadership.md) | P1 | ADRs, standards, stakeholder alignment, risk, TCO |
| 14 | [Interview communication](14_interview_communication.md) | P0 practice | 60-minute whiteboard, three audiences, career stories |
| 15 | [End-to-end order integration exercise](15_order_integration_capstone.md) | P0 practice | E-commerce, SAP, Salesforce, WMS, finance, failure drills |
| 16 | [Vendor-specific platform deep dive](16_vendor_specific_deep_dive.md) | P2 optional | Tailored deep dive for a named product or job description |

## Coverage and use

- For a short preparation window, start with **01–07, 10, 14, and 15**. Add 08–09 and 11–13 for fuller coverage. Use 16 only when a role calls for a named product.
- Have the assistant create **one guide per brief**. Each brief includes its own scope, structure, and practice requirements so it can be handed off independently.
- Treat every sample company, workload, target, and metric as illustrative unless supplied by the actual employer or your own experience. Do not put invented numbers into career stories.
- The guides should support active practice: design choices, rejected alternatives, failure drills, and explanations to business and engineering audiences.

## Suggested seven-day sequence

| Day | Use these briefs | Practice outcome |
|---|---|---|
| 1 | 01, 02, 11 | Frame requirements and defend pattern/platform choices |
| 2 | 04, 06 | Handle messaging, retries, outages, and recovery |
| 3 | 05, 08 | Explain consistency, data ownership, and reconciliation |
| 4 | 07, 10 | Integrate enterprise applications and plan migration |
| 5 | 03, 09, 12 | Cover contracts, security, hybrid scale, and DR |
| 6 | 13, 14 | Practice governance, stakeholder challenges, and career stories |
| 7 | 15 | Run a timed design and failure drill; revisit weak areas |

This is a suggested sequence, not a requirement to compress all 16 full-length guides into one week. Brief 16 is role-specific extra preparation.

## Original interview-question coverage

| Question in source | Primary brief |
|---|---|
| Salesforce, SAP, and legacy order integration | 07 and 15 |
| Kafka versus a traditional queue | 04 |
| Database commit succeeds, event publish fails | 05 |
| One business process across five systems | 05 |
| Modernize 50 point-to-point integrations | 10 |
| ESB versus iPaaS versus gateway versus broker | 11 |
| Synchronize customer data | 08 |
| SAP unavailable for six hours | 06 and 15 |
| Secure SaaS, cloud, partner, and on-prem integration | 09 |
| Prevent the integration platform becoming a bottleneck | 11 and 12 |

## Source coverage map

The original document's preparation priorities and checklist are distributed across 01–13; the full order scenario is 15; the deep-dive topics are in 03, 05, 08–10, and 13; its senior-candidate challenges and career stories are in 13–14; the whiteboard structure is in 14; and the final readiness test is represented by the exercises and answer rubrics in 01–15.
