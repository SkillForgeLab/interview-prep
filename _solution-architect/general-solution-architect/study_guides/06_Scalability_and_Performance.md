# Scalability and Performance

**Core learning guide for Solution Architect interviews**

This guide covers how to locate performance constraints and scale the part of a system that needs it. Begin with
[Requirements, Quality Attributes, and Capacity](02_Requirements_Quality_Attributes_and_Capacity.md), then use
[Data Architecture](03_Data_Architecture_and_Database_Selection.md) for storage-specific decisions.

## Learning outcomes

- Distinguish latency, throughput, concurrency, and capacity.
- Identify bottlenecks from measurements instead of guesses.
- Compare vertical and horizontal scaling, caching, and autoscaling.
- Explain the failure and consistency costs that scaling mechanisms can introduce.

## 1. Measure the user-visible journey

Performance is not one number. **Latency** is time to complete an operation; **throughput** is work completed per unit
of time; **concurrency** is work in progress at once; **capacity** is the load a system can sustain while meeting its
targets.

Measure representative user journeys and component boundaries. Use percentiles (such as p95 or p99) alongside error
rates and throughput; averages can hide tail latency. Correlate traces, metrics, and logs with privacy-safe identifiers.
See [Reliability and Disaster Recovery](07_Reliability_Observability_and_Disaster_Recovery.md).

```text
Client -> gateway -> application -> database -> dependency
  measure end-to-end and each segment; locate the dominant wait or saturation
```

Reproduce the request mix and data shape in a load test. A benchmark with unrealistic cache warmth, payload size, or
concurrency can produce misleading capacity claims.

## 2. Scale the constrained resource

Vertical scaling adds resources to one node; it is often operationally simpler but has an upper bound and may preserve
a single failure point. Horizontal scaling adds instances; it can increase capacity and resilience when work is
distributable, but requires routing, coordination, and shared-state decisions.

Before adding instances, determine whether the constraint is CPU, memory, lock contention, database queries, a
downstream quota, or queue backlog. Scaling one tier can move pressure to another.

**Autoscaling:**

> Adjusting capacity in response to demand or a health signal. Define the signal, minimum and maximum bounds,
> provisioning delay, cooldown, and behavior during a rapid spike. Scaling out cannot fix a dependency with a fixed
> quota or an operation that is inherently serialized.

## 3. Use caching and traffic distribution with explicit rules

A cache is useful when repeated reads are expensive and the business can tolerate a defined freshness window. State
the source of truth, key design, expiry or invalidation policy, maximum object size, and behavior during cache
outage. Plan for hot keys, thundering herd, stale data, and cache stampedes. Cache invalidation is a correctness
decision as well as a performance concern.

Load balancers distribute requests across healthy targets; content delivery networks (CDNs) can serve cacheable content
closer to users. Neither helps every workload: dynamic personalized data, session affinity, geographic restrictions,
and origin bottlenecks affect the design.

## 4. Validate performance changes

Use a baseline and an agreed target. Test normal load, expected peak, burst, recovery after saturation, and a
representative dependency failure. Record cost alongside latency and throughput so that faster is not mistaken for
better if the cost exceeds the business value.

**Say it professionally:**

> “I would establish a representative baseline and identify the saturated resource before changing the topology. I
> would test the improvement against the user-facing latency and throughput targets, including the new failure modes
> and operating cost.”

## 5. Practice and self-check

Take a slow checkout scenario. Trace one request, identify what to measure, and propose two competing fixes. Explain
how you would test them and what new constraint each could create—for example, a cache's freshness risk or database
replica lag.

Check your answer: Did you identify a measured bottleneck? Does the proposed scaling mechanism affect the actual
constraint? Can you state a limit at which the design needs a different approach?

## References

- [Google Cloud Architecture Framework: system design](https://docs.cloud.google.com/architecture/framework)
- [AWS Well-Architected Framework: performance efficiency pillar](https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/welcome.html)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
