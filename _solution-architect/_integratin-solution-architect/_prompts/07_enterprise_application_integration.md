# Handoff brief 07 — Enterprise application integration

Create a **standalone study guide** titled *Integrating ERP, CRM, Finance, SaaS, Legacy, and Partners*. The audience is
a senior/principal Enterprise or Integration Solution Architect preparing for vendor-neutral interviews. Aim for roughly
2,500–3,500 words. Use realistic but clearly illustrative examples; do not assume specific product behavior without
verifying it from primary documentation.

**Focus:** Enterprise application boundaries and systems of record; differing identifiers and data models; adapters and
mapping; synchronous validation versus asynchronous propagation; SaaS API limits and webhooks; legacy batch/files;
partner contracts, acknowledgements and error handling; financial controls; ownership of transformations and support;
reconciliation across applications.

**Include:**

1. A worked Salesforce–SAP–legacy order scenario: state who owns customer, order, product, and financial data, then
   trace a cross-system order flow.
2. A mapping and identity strategy for inconsistent customer IDs, missing reference data, duplicate events, and
   divergent records.
3. An interface inventory template covering purpose, protocol, owner, contract, rate/volume, data classification,
   failure impact, and recovery owner.
4. Options for connecting SaaS, on-prem ERP, external partners, and legacy finance systems; show at least two
   alternatives for major boundaries.
5. Interview follow-ups on partial success, downstream outages, support ownership, and partner failures, with model
   answers and an exercise with answer key.

Emphasize business semantics and ownership rather than a particular connector catalog or vendor product.
