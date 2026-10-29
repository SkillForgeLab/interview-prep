# Handoff brief 03 — API architecture and contracts

Create a **standalone study guide** titled *API Architecture, Contracts, and Governance*. The audience is a senior/principal Enterprise or Integration Solution Architect in a vendor-neutral interview. Aim for roughly 2,500–3,500 words. Use practical examples, label assumptions, and cite current primary sources for standards or changing product behavior.

**Focus:** API gateway responsibilities; contract-first design; resource and operation boundaries; authentication and authorization touchpoints; throttling and quotas; pagination, errors, timeouts, idempotency keys; API ownership and lifecycle; versioning and deprecation; consumer-driven contract testing; schema registries and event contract compatibility where relevant. Distinguish gateway policy from business logic and integration mediation.

**Include:**

1. An API design and lifecycle checklist from discovery through retirement, with named producer and consumer responsibilities.
2. A concrete order API contract sketch (requests, responses, error model, idempotency and correlation IDs) and a separate event contract sketch. Explain how they evolve safely.
3. A worked change where a producer changes a field type and many consumers might fail. Show prevention, detection, rollout, and rollback.
4. Trade-offs for versioning versus additive evolution and for centralized standards versus team autonomy.
5. A whiteboard diagram, five interview questions with model answers, mistakes to avoid, and a short exercise with answer key.

Keep OAuth internals in the separate security guide and broker internals in the messaging guide. The reader should finish able to explain who owns a contract and how to change it without breaking consumers.
