# Handoff brief 15 — End-to-end order integration capstone

Create a **standalone, exercise-led study guide** titled *Enterprise Order Integration: Full System Design Capstone*. The audience is a senior/principal Enterprise or Integration Solution Architect preparing for a 60-minute vendor-neutral whiteboard interview. Aim for roughly 3,000–4,000 words. Clearly distinguish scenario facts from assumptions and alternatives. Use primary sources for precise standards or current platform claims.

**Scenario facts:** An e-commerce application, SAP ERP, Salesforce CRM, a warehouse management system, and a legacy finance application must exchange orders reliably. SAP can be unavailable. The business needs end-to-end visibility for each order. Do not assume asynchronous acceptance is permitted until it is clarified. Payment and financial workflows may require different consistency rules.

**Include:**

1. The initial clarifying questions: meaning of “accepted,” authoritative order state, validation, throughput, latency, RPO/RTO, retention, payment/inventory boundaries, and partial-success policy.
2. Two defensible designs: one allowing durable order acceptance and asynchronous downstream propagation, and one requiring ERP confirmation before acceptance. Draw each as an annotated text or Mermaid diagram.
3. For the asynchronous design, evaluate gateway, order state store, Outbox, broker, SAP/CRM/WMS adapters, idempotent consumers, DLQ, tracing, audit, and reconciliation. State why each exists and what could replace it.
4. Failure drills: SAP down six hours; database commit succeeds but event publish fails; duplicate event; CRM succeeds while WMS fails; stale backlog; finance discrepancy; regional failure. Give recovery steps and ownership.
5. A migration and operating plan, cost/risk trade-offs, a complete model whiteboard answer, skeptical interviewer questions, and a scoring rubric.

The reader should be able to reuse the method on a different enterprise scenario, not memorize one diagram.
