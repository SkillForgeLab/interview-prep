# Security Architecture, Privacy, and Compliance

**Core learning guide for Solution Architect interviews**

This guide provides a risk-based way to place security and privacy controls across an architecture and its lifecycle.
It complements [Application and API Architecture](05_Application_API_and_Integration_Architecture.md) and
[Reliability and Recovery](07_Reliability_Observability_and_Disaster_Recovery.md).

## Learning outcomes

- Identify assets, data flows, trust boundaries, threats, and business impact.
- Choose preventive, detective, and recovery controls proportionate to risk.
- Explain identity, authorization, data protection, and secure operations as system-wide concerns.
- Connect applicable obligations to owners and evidence without claiming unsupported compliance.

## 1. Establish what is at risk

Start with business context, users, assets, data classification, dependencies, and operating assumptions. Trace what
data is collected, processed, stored, copied, shared, logged, retained, and deleted. Mark trust boundaries where
control, identity, or assumptions change.

```text
User -> public API | trust boundary | service -> data store -> partner
                     identity check      data access    protected transfer
```

Threat modeling asks how a system could be misused or fail and what impact follows. Consider confidentiality,
integrity, availability, privacy, and abuse. Prioritize credible threats by likelihood and impact; do not treat a
checklist as proof that the design is safe.

## 2. Put controls at the right boundaries

Authenticate users and services; authorize each action at the component that owns the resource. Use least privilege,
separate human and service identities, review privileged access, and remove access when it is no longer needed.

For user sign-in, OpenID Connect (OIDC) adds an identity layer on top of OAuth 2.0. OAuth 2.0 is primarily an
authorization framework for delegated access; it is not, by itself, a user-authentication protocol. Single sign-on
(SSO) describes a user experience and deployment capability, not one specific protocol. Select flows and token
handling for the client type and threat model, and validate them against current security guidance.

Validate input at trust boundaries. Protect API and service-to-service traffic, isolate workloads, restrict
administrative paths, and manage secrets and encryption keys separately from source code. Minimize collected data and
retention. Encryption in transit and at rest are important controls, but do not prevent misuse by an already
authorized identity or replace key management and access control.

Zero-trust architecture is an approach that avoids granting trust solely because a request originates inside a network.
Continuously evaluate identity, device or workload context, authorization, and policy at relevant access points; it is
not a single product or a reason to ignore network segmentation.

Log security-relevant events with appropriate access and retention. Avoid recording credentials and unnecessary
sensitive data. Define detection, alerting, incident response, backup, recovery, vulnerability management, and
third-party dependency responsibilities.

## 3. Integrate security into delivery

Include security requirements in architecture review, threat analysis, coding and dependency practices, testing,
release approval, and operations. Assign owners to controls and verify them with evidence such as test results, access
reviews, incident exercises, and monitoring records.

An exception should name the risk, compensating controls, approving owner, expiry or review date, and remediation path.
An exception with no owner or end condition becomes an untracked permanent design.

## 4. Treat compliance as an evidence question

Applicability depends on the system, data, contracts, jurisdictions, and organization. Confirm obligations with
qualified legal, privacy, risk, and compliance owners. Map each applicable requirement to a system control, owner, and
evidence. Do not infer compliance from a cloud service, encryption setting, or checklist alone.

**Say it professionally:**

> “I would identify the sensitive assets and trust boundaries, assess credible threats and impact, then assign
> proportionate controls and owners. For compliance, I would confirm what applies with the responsible specialists and
> map those obligations to verifiable system evidence.”

## 5. Practice and self-check

Sketch a service that accepts personal data through an API, stores it, and shares part with a partner. Mark data flow,
identities, authorization checks, encryption and key ownership, retention and deletion, audit events, monitoring, and
incident response. Name the review owners and state assumptions instead of inventing regulatory duties.

Check your answer: Can you name an asset, threat, impact, control, owner, and evidence for each major risk? Have you
considered least privilege, data minimization, safe logging, recovery, third parties, and residual risk?

## References

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [NIST SP 800-30: Guide for Conducting Risk Assessments](https://csrc.nist.gov/pubs/sp/800/30/r1/final)
- [Azure Well-Architected Framework: security](https://learn.microsoft.com/en-us/azure/well-architected/security/)
