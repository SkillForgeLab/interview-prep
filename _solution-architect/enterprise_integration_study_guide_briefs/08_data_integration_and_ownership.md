# Handoff brief 08 — Data integration and ownership

Create a **standalone study guide** titled *Enterprise Data Integration and Ownership*. The audience is a senior/principal Enterprise or Integration Solution Architect in vendor-neutral interviews. Aim for roughly 2,500–3,500 words. Label assumptions and use current primary sources for standards or platform-specific assertions.

**Focus:** Systems of record versus engagement; master data management; authoritative attributes; customer identity matching and deduplication; canonical versus domain-specific models; reference data; data quality; CDC, APIs, events, and ETL/batch as synchronization options; freshness and lag; schema evolution; conflict resolution; privacy and audit implications; reconciliation.

**Include:**

1. A customer master example where CRM and ERP disagree. Define ownership by attribute, conflict rules, correction workflow, and prevention of competing updates.
2. A comparison table for API, business event, CDC, and batch synchronization, including data semantics, timeliness, failure recovery, and coupling.
3. A concrete data lineage and ownership matrix for customer, order, product, and invoice entities.
4. A reconciliation plan that detects missing, duplicate, and mismatched records and assigns resolution ownership.
5. Interview questions with model answers, common data-model traps, and a practice exercise with answer key.

Avoid treating a canonical model or MDM platform as mandatory. Explain the organizational decisions that must be made before technology selection.
