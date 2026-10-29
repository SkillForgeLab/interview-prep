# Handoff brief 01 — Requirements and design framing

Create a **standalone study guide** titled *Requirements and Design Framing for Enterprise Integration Interviews*. The reader is a senior/principal Enterprise or Integration Solution Architect with about 20 years of experience. Write for a vendor-neutral system design interview. Target approximately 2,000–3,000 words of useful instruction, plus concise checklists. Use concrete enterprise examples; clearly label assumptions. Do not fabricate employer requirements or personal achievements. Verify any time-sensitive standards or product claims against current primary sources and link them.

**Focus:** Turning an ambiguous business request into an architecture problem before drawing components. Cover business outcomes and stakeholders; functional requirements; measurable NFRs (throughput, peak load, latency, availability, durability, RPO/RTO, retention, compliance, cost); systems of record and data ownership; trust and network boundaries; constraints from existing platforms, skills, licensing, and delivery dates. Show how acceptance semantics (for example, what “order accepted” means) change a design.

**Include:**

1. A practical sequence for the first ten minutes of a whiteboard interview, with high-value clarifying questions and what each answer changes.
2. A one-page requirements worksheet, an assumptions/risks/decisions log, and a system/data ownership matrix.
3. Two contrasting mini-scenarios: immediate validation required versus eventual downstream propagation allowed. Show how each affects design.
4. A worked exercise using an e-commerce app, ERP, CRM, warehouse, and finance system. Start from ambiguous requirements, derive NFRs, identify ownership, and state unresolved decisions.
5. Five interviewer follow-ups, model responses, common weak responses, and a self-scoring rubric.

Keep detailed broker, API, Saga, and cloud implementation material as pointers for later study. The outcome of this guide should be a defensible problem statement and design criteria, not a full architecture.
