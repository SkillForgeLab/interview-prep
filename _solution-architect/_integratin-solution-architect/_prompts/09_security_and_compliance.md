# Handoff brief 09 — Security and compliance

Create a **standalone study guide** titled *Securing Enterprise Integrations*. The audience is a senior/principal
Enterprise or Integration Solution Architect preparing for vendor-neutral interviews. Aim for roughly 2,500–3,500 words.
Security standards and regulations can change, so verify precise claims against current primary sources and link them.
Do not offer blanket compliance claims without jurisdiction and context.

**Focus:** Trust boundaries; identity federation; OAuth 2.0 and OpenID Connect roles and flows; mTLS and when it is
useful; service identity and least privilege; API and partner authorization; network segmentation and private
connectivity; encryption; secrets storage and rotation; PII classification, minimization and retention; audit trails;
threat modeling; security monitoring and incident response.

**Include:**

1. A threat-boundary diagram for an external partner submitting orders to an internal ERP through an integration layer.
   Explain how the partner is prevented from gaining broad ERP access.
2. A decision table for OAuth/OIDC, mTLS, API keys, and federation, including what each does and does not prove.
3. A practical control checklist across identity, transport, payload/data, network, operations, and evidence.
4. A failure scenario involving a leaked credential or overprivileged integration account, with containment and recovery
   steps.
5. Interview questions with model answers, common misconceptions, and an exercise with answer key.

Keep legal requirements contextual. Explain how to identify the applicable regulatory obligations rather than inventing
them.
