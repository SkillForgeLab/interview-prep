# Handoff brief 02 — Choosing integration patterns

Create a **standalone study guide** titled *Choosing Enterprise Integration Patterns*. The reader is a senior/principal Enterprise or Integration Solution Architect preparing for vendor-neutral design interviews. Aim for roughly 2,500–3,500 words. Make decisions and trade-offs the center of the guide. Label assumptions; verify time-sensitive claims with current primary sources and link them. Do not invent employer constraints.

**Focus:** How to choose among synchronous REST/API, asynchronous queue/command, publish-subscribe business events, retained event streaming, batch/ETL, CDC, and file/SFTP/EDI exchange. Explain command versus event versus query versus bulk data movement; immediate response needs; freshness; throughput; coupling; ordering; replay; delivery guarantees; operational complexity; data ownership; and partner or legacy constraints.

**Include:**

1. A decision tree and comparison matrix with good fit, poor fit, failure modes, and key questions for every pattern.
2. Clear distinctions between a queue and a topic, pub/sub and event streaming, CDC and a business event, and a file handoff and an API.
3. Three worked choices: order submission requiring immediate validation, downstream order propagation during ERP outages, and overnight partner data exchange. For each, compare at least two plausible alternatives and defend the selection.
4. Hybrid designs where patterns legitimately coexist, including how state and ownership remain clear.
5. Interview questions, strong sample answers, counterarguments, and a self-check quiz with answer key.

Avoid product administration details. Explicitly challenge “use Kafka because we have microservices” and “add a queue” without a business or resilience reason.
