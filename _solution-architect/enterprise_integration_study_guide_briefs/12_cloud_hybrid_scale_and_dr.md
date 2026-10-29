# Handoff brief 12 — Cloud, hybrid, scale, and disaster recovery

Create a **standalone study guide** titled *Cloud and Hybrid Integration: Scale and Recovery*. The audience is a senior/principal Enterprise or Integration Solution Architect in vendor-neutral interviews. Aim for roughly 2,500–3,500 words. Clearly mark sample figures as illustrative; verify current service claims with primary sources.

**Focus:** On-prem/cloud/SaaS/partner network boundaries; private versus public connectivity; latency and egress considerations; managed versus self-operated services; availability zones/regions; failure domains; capacity planning; horizontal scaling; partitioning and consumer concurrency; dependency rate limits; backpressure; RPO/RTO; disaster recovery; retention; performance testing; and cost trade-offs.

**Include:**

1. A hybrid reference design linking an on-prem ERP, cloud order service, SaaS CRM, and an external partner. Identify trust boundaries and failure domains.
2. A capacity worksheet with formulas or clear methods for peak throughput, backlog storage, drain time, and recovery capacity. Use explicitly hypothetical numbers only to illustrate the method.
3. A comparison of active/passive and active/active recovery choices, including data consistency and operational complexity.
4. A six-hour downstream outage and regional-failure exercise; show continuity decisions, DR activation criteria, recovery, and reconciliation.
5. Interview questions with model answers, common sizing mistakes, and a self-check exercise with answer key.

Keep this at architecture level rather than turning it into one cloud provider's configuration tutorial.
