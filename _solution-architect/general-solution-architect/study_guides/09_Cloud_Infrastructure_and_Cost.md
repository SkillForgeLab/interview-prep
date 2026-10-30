# Cloud, Infrastructure, and Cost

**Core learning guide for Solution Architect interviews**

This guide focuses on provider-neutral infrastructure decisions: where workloads run, what is managed, how networks
and identity are shaped, and how cost is governed. It builds on
[Requirements and Capacity](02_Requirements_Quality_Attributes_and_Capacity.md) and
[Reliability and Recovery](07_Reliability_Observability_and_Disaster_Recovery.md).

## Learning outcomes

- Compare managed services, containers, virtual machines, and serverless against workload and operating needs.
- Explain network, identity, deployment, and infrastructure-as-code boundaries.
- Include security, resilience, portability, operational capacity, and cost in platform decisions.
- Make cloud cost measurable and attributable rather than a late-stage surprise.

## 1. Choose an operating model for the workload

Managed services transfer some infrastructure operations to a provider, but not responsibility for architecture,
configuration, data, access, or recovery. Virtual machines offer operating-system control. Containers package
applications consistently but require a platform and lifecycle. Serverless can reduce server management for suitable
event-driven or variable workloads, but introduces runtime, concurrency, and platform constraints.

Choose based on workload shape, latency, state, scaling pattern, compliance constraints, team skills, deployment
frequency, support model, and expected total cost. “Managed” does not mean “no operations,” and “portable” is not
automatically cheaper or simpler.

**Kubernetes or serverless?**

> Kubernetes can fit when teams need a shared container platform, workload control, or consistent orchestration and
> have the skills to operate its control plane and platform practices. Serverless can fit event-driven or variable
> workloads when its runtime, concurrency, networking, and execution limits meet the need. Compare idle and peak cost,
> startup behavior, observability, deployment, portability, and support burden; do not assume either is inherently
> cheaper.

## 2. Design foundational boundaries

Establish account or subscription structure, environment separation, network segmentation, identity, secrets,
logging, policy, and connectivity to existing systems. Prefer explicit ownership for shared platform services. Limit
administrative access and make production changes traceable.

Infrastructure as code (IaC) makes infrastructure definitions reviewable and repeatable. Treat modules, state,
credentials, drift detection, approval, and rollback as part of its design. A deployment pipeline should promote
validated changes with environment-specific controls rather than rely on undocumented console edits.

## 3. Compare cost as an architecture attribute

Estimate cost from traffic, storage, data transfer, availability targets, licensing, support, and people needed to
operate the system. Include non-production environments, backup, logging, observability, and growth. Compare build,
buy, and managed options over the same period and workload assumptions.

Use budgets, tags or allocation metadata, usage dashboards, and accountable owners to make spend visible. Cost
optimization can change reliability, latency, and engineering effort; treat it as a tradeoff and set guardrails.
Multi-region replication, extensive logs, always-on capacity, and data egress can dominate a bill in ways a compute
estimate misses.

Hybrid or multi-cloud designs may be required by existing investments, residency obligations, acquisition history, or
a defined resilience objective. They also add identity, networking, data movement, observability, governance, and
skills costs. Name the requirement they satisfy and compare it with a simpler single-platform design before accepting
the additional operating model.

**Say it professionally:**

> “I would choose the operating model that fits the workload and the team's ability to run it. I would compare total
> cost—including resilience, data movement, support, and operations—against the service targets, then make cost
> ownership and review part of ongoing governance.”

## 4. Practice and self-check

Compare containers and a managed/serverless option for a bursty notification workload. State assumptions about
runtime duration, state, traffic, latency, network access, and team skills. Compare cost drivers, failure modes,
scaling limits, and operating responsibilities. Explain what evidence would change your choice.

Check your answer: Did you include data movement and operational cost? Are network and identity responsibilities
clear? Does the provider choice follow a real requirement rather than habit?

## References

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Google Cloud Architecture Framework](https://docs.cloud.google.com/architecture/framework)
