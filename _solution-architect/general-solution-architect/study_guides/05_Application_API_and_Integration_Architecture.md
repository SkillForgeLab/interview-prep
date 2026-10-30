# Application, API, and Integration Architecture

**Core learning guide for Solution Architect interviews**

Use this guide to reason about application boundaries and contracts across teams, platforms, legacy systems, and
external partners. It extends [Distributed Application Design](01_Distributed_Application_Design_for_Solution_Architect_Interviews.md)
and [Messaging and Event-Driven Architecture](04_Messaging_and_Event_Driven_Architecture.md).

## Learning outcomes

- Choose an application style based on domain, team, delivery, and operational needs.
- Define API ownership, consumer expectations, versioning, and compatibility.
- Explain integration choices for synchronous, asynchronous, legacy, and partner connections.
- Describe how to evolve a contract without silently breaking consumers.

## 1. Draw boundaries around change and ownership

A monolith, modular monolith, and microservices are deployment choices with different costs—not a maturity ladder.
Start by identifying capabilities, business rules, data owners, teams, release needs, and operational capacity.

**Bounded context:**

> A boundary within which a domain model and its language have a defined meaning. Different contexts may use similar
> terms differently; explicit translation at integration points prevents accidental coupling.

Keep modules together when they share rules, change together, and do not need independent deployment. Consider a
separate service when independent ownership, deployment, scaling, or fault isolation provides a concrete benefit that
outweighs network and operational costs.

## 2. Treat an API as a product contract

An API contract states what a consumer can request, what the provider promises, how errors are represented, and how
security and change are handled. Define the owner and intended consumers before choosing REST, GraphQL, gRPC, or an
event interface.

For a REST-style HTTP API, use resource-oriented paths and HTTP semantics consistently. Define authentication,
authorization, validation, pagination, idempotency where appropriate, error shape, rate limits, and observability.
An API gateway may centralize selected cross-cutting concerns, but it does not replace authorization and validation
at the service that owns the resource.

REST is a common choice for interoperable resource-oriented HTTP APIs. GraphQL can help clients request shaped data
across related resources, but adds schema, resolver, authorization, and query-cost concerns. gRPC provides
schema-defined remote procedure calls and efficient binary communication, but requires compatible client support and
tooling. Choose among them from consumer needs, network constraints, contract evolution, security, and operations—not
from a general claim that one is faster or more modern.

**Compatibility:**

> A change is compatible only relative to the consumer contract. Adding an optional response field may be safe for
> tolerant consumers; changing a field's meaning, removing it, or changing required input can break them.

Prefer additive evolution where possible. If a breaking change is unavoidable, identify consumers, provide a migration
window, measure adoption, and define a retirement date and fallback. Contract tests and consumer coordination help
catch drift; neither replaces clear ownership.

## 3. Integrate with legacy systems and partners deliberately

Map the existing system's actual behavior, data ownership, constraints, and operational support before wrapping or
replacing it. An adapter or anti-corruption layer translates between models; it should not hide unstable ownership or
unbounded dependency risk.

For external partners, define timeouts, retries, rate limits, credentials, data handling, idempotency, reconciliation,
support contacts, and outage behavior. Treat partner responses as untrusted input. Avoid long synchronous chains on a
critical user journey when the business can tolerate a pending workflow.

**Integration decision:**

> Choose a direct API call when the caller needs an immediate answer and dependency coupling is acceptable. Choose an
> asynchronous contract when the work can complete later and the organization can operate its messaging and recovery
> path.

See [Enterprise Modernization and Roadmaps](10_Enterprise_Modernization_and_Roadmaps.md) for staged replacement and
coexistence.

## 4. Practice and self-check

Use the Digital Servicing application-to-application API strategy mentioned in the source prompts as an interview
practice scenario. State assumptions rather than inventing project details. Identify provider and consumer, data
owner, contract, security boundary, version approach, rollout sequence, and failure behavior. Then explain when you
would use an event or integration adapter instead.

**Say it professionally:**

> “I would make the contract and its owner explicit, then choose the interaction style based on whether the consumer
> needs an immediate decision. I would plan compatibility and consumer migration as part of delivery, not as a later
> cleanup.”

Check your answer: Are the API's consumers known? Is authorization enforced where the data owner can make the decision?
Can the provider change safely without assuming every consumer upgrades at once?

## References

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Azure Architecture Center: microservices architecture style](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices)
