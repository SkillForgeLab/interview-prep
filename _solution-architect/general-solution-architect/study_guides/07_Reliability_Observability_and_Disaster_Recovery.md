# Reliability, Observability, and Disaster Recovery

**Core learning guide for Solution Architect interviews**

Reliability means delivering an agreed capability despite faults and recovering within business limits. This guide
builds on [Requirements and Quality Attributes](02_Requirements_Quality_Attributes_and_Capacity.md) and
[Distributed Application Design](01_Distributed_Application_Design_for_Solution_Architect_Interviews.md).

## Learning outcomes

- Define service-level indicators, objectives, and operational signals.
- Reason about dependency failures, graceful degradation, and recovery.
- Compare availability zones and regions without treating redundancy as a recovery plan.
- Explain how to prove a backup and disaster-recovery strategy works.

## 1. Define reliability from the user's perspective

A **service-level indicator (SLI)** is a measured signal, such as successful requests or latency. A **service-level
objective (SLO)** is the target for that signal over a stated window. An **error budget** is the remaining allowed
unreliability under that objective and can inform release risk decisions.

Choose indicators that reflect user outcomes. A host being up does not prove that a customer can complete a payment.
Define the eligible requests, measurement window, exclusions, and alert threshold with the service owner.

## 2. Design for failure and bounded recovery

Map critical dependencies and ask what the user sees when each is slow, unavailable, or returning invalid results.
Use bounded timeouts, retries for transient errors, backoff, idempotency, and isolation where they address the failure
mode. Avoid retry storms and cascades. Decide which capabilities can degrade and which must fail safely.

**Graceful degradation:**

> Continue a reduced but truthful capability when a non-essential dependency is unavailable. It is not appropriate if
> the reduced behavior violates a business or safety invariant.

Make ownership explicit for alerts, incident response, communications, restoration, and post-incident learning.
Runbooks should help operators decide and act, not just list dashboards.

## 3. Distinguish high availability from disaster recovery

Multiple instances or availability zones can reduce some local failure risks, but shared control planes, credentials,
data corruption, deployment errors, or a regional event can still affect all copies. A second region can improve
recovery options but adds cost, replication lag, data-residency questions, routing, and failover complexity.

Choose active-active or active-passive based on business recovery targets, write-conflict behavior, dependency
availability, and operational readiness. Define who declares a disaster, what is failed over, how consistency is
checked, how clients are redirected, and how normal service is restored.

Backups protect against some deletion, corruption, and regional failure cases; replication may copy a bad change
quickly. Specify backup isolation, retention, encryption, restore access, and tested restoration time. Verify RPO and
RTO by exercise rather than asserting them from an architecture diagram.

## 4. Connect observability to action

Logs describe events, metrics show trends and saturation, and distributed traces show a request's path across
components. Combine them with consistent identifiers while avoiding unnecessary personal or secret data in logs.
Alert on actionable user impact or risk, not every noisy internal signal.

**Say it professionally:**

> “I would start from the service's user-facing objectives, map its critical dependencies, and test the recovery
> procedures against the agreed RTO and RPO. Redundancy helps only when detection, decision authority, data recovery,
> and failback are also designed and exercised.”

## 5. Practice and self-check

For a multi-tenant SaaS service, define one SLI and SLO, then trace database and region failure. State what is degraded,
what is unavailable, the recovery owner, and how you would verify the restored data and service.

Check your answer: Are availability, backup, replication, and disaster recovery treated as distinct controls? Is the
recovery target measurable and tested? Could monitoring or failover expose sensitive data or create conflicting writes?

## References

- [Google SRE Workbook: implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [AWS Well-Architected Framework: reliability pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Azure Well-Architected Framework: reliability](https://learn.microsoft.com/en-us/azure/well-architected/reliability/)
