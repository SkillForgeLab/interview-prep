# Core 1: Distributed design

**Read first.** We will discuss and practice this guide after you have had time to read it. No quiz is needed now.

## What you should gain from this guide

By the end, you should be able to:

1. **Understand** components, communication, data ownership, and failure.
2. **Explain** how one request travels across a system.
3. **Defend** a decision to keep components together or separate them.

The job posting asks for end-to-end design of complex distributed systems, platform integration, REST APIs,
service-oriented architecture, and performance. This guide builds the foundation for those discussions.

## 1. Beginner explanation: What is a distributed application?

An **application** helps a user complete a task. A **distributed application** uses multiple parts that run separately
and communicate over a network to complete that task.

For example, a user interface can call an API, which can call another service and read data from a database. Each part
has a job. Because the parts are separate, a request must travel between them. That travel takes time, and any
connection can fail.

Think of a restaurant. A small restaurant may have one person take orders, cook, and serve. A larger restaurant divides
the work. Specialization helps, but the handoffs must be clear. Software services also need clear handoffs.

**Key idea:** Splitting an application can improve ownership and flexibility. It also creates communication and
coordination work. A senior architect explains both sides.

### Words to know

| Term                | Plain meaning                                                                                                     |
|---------------------|-------------------------------------------------------------------------------------------------------------------|
| **Component**       | A part of a system with a defined responsibility. It might be a user interface, API, service, database, or cache. |
| **Service**         | A component that performs a business or technical function for other components.                                  |
| **API**             | An agreed way for one component to request data or an action from another.                                        |
| **REST API**        | A common API style that uses HTTP requests and resources, such as a request to retrieve or update a user.         |
| **Network call**    | Communication between separately running components. It can be slow, interrupted, or time out.                    |
| **Source of truth** | The system whose record is authoritative for a particular fact.                                                   |
| **Cache**           | A faster copy of data, used to reduce repeated work. A cache may be out of date.                                  |

## 2. A project anchor from your experience

Your application résumé states that you built self-service user-management capabilities at American Express that reduced
corporate client onboarding time by **30%**. An older résumé adds project context about a React/Redux interface, REST
API integration, role-management features, and Redis caching. Those older details are useful for learning, but we will
confirm your exact contribution and the production design before using them in an interview story.

The diagram below is a **teaching model based on that project**, not a claim that it was the exact production
architecture:

```text
Corporate client administrator
          |
          v
  User-management interface
          |
       REST request
          |
          v
  User-management API and logic
          |
          v
  Authoritative user/role system  <- exact ownership to confirm
          |
          v
       Response to user
```

Imagine the administrator changes a user's access. Follow the request one step at a time:

1. The interface collects the requested change.
2. It sends a REST request to an API. The request includes the user's identity, the requested action, and the data
   needed to make the change.
3. The API checks who is making the request, validates the data, and applies the business rules.
4. The responsible component reads or updates the authoritative record. **We have not established which actual system
   owned that record in your project.**
5. The API returns a result. The interface tells the administrator whether the change succeeded.

The important architectural question is not just *which boxes exist*. It is **which box owns each decision and each
piece of data**.

### How to explain a request path clearly

Use this order when speaking:

> “A user starts an action in the interface. The interface calls the API. The API checks access and validates the
> request. The responsible service applies the business rule and updates the authoritative data. It returns a result, and
> the interface shows the outcome. I also consider what happens if a call is slow or fails.”

That is a general explanation, not a claim about an undocumented component in your project.

## 3. Components: Where should responsibilities go?

Good component boundaries follow **responsibilities**. A component should have a clear reason to change.

For user management, possible responsibilities include presenting screens, checking permissions, applying
user-management rules, and storing authoritative user or role data. An architect asks which team owns each
responsibility and which systems already provide it. The answer may lead to one application with well-defined modules or
several services.

A common mistake is to create a separate service for every small function. This increases network calls and operational
work without necessarily improving the design. Another mistake is to put unrelated business rules in one large component
until every change affects everything else.

## 4. Communication: How do components work together?

Two useful patterns are:

| Pattern                           | How it works                                                    | Good fit                                                                   | Main cost                                                               |
|-----------------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **Synchronous call**              | Component A asks B and waits for an answer, often through REST. | The user needs the result before continuing.                               | A becomes dependent on B's speed and availability.                      |
| **Asynchronous message or event** | A records work or sends a message; B handles it later.          | Work can finish after the immediate user response, such as a notification. | Results arrive later; tracking and duplicate handling become important. |

For an access change, the user needs a trustworthy outcome. A synchronous request may be appropriate for the core
change. A noncritical notification might be handled later. This is an example of the tradeoff, **not a statement about
how your project implemented it**.

An **API contract** states what a request means, what data it accepts, what it returns, and which errors callers should
expect. Clear contracts allow teams to work independently. We will study API design in Core 2.

## 5. Data ownership: Who is allowed to change the record?

Suppose two services both write a user's role. They can disagree. When that happens, it becomes hard to answer a basic
question: “What access does this user actually have?”

An architect identifies the **source of truth** for each important fact. Other components request a change through an
agreed interface or keep a copy for a specific purpose. A copy is useful, but it needs a rule for how it stays current.

For your user-management example, we need to confirm whether the platform owned role assignments or requested changes
from another identity system. Until we know, we should discuss both designs as alternatives rather than claim either was
used.

Redis appears in an older résumé as a cache used for frequently accessed data. A cache can improve response time, but an
architect must ask how it is refreshed. For access data, stale information can become a security problem. The design
should state which data may be cached, for how long, and what happens after an access change.

## 6. Failure: What happens when a handoff breaks?

In a distributed application, one component can be healthy while another is slow or unavailable. A request can also time
out after the receiving component has already completed the work. The caller may not know whether to retry.

Consider an access-change request:

- **API unavailable:** The interface should show a clear failure instead of pretending the change succeeded.
- **Downstream call is slow:** A timeout prevents the request from waiting forever. The system needs a sensible limit
  and an error response.
- **Timeout after a successful change:** Blindly repeating the request could cause duplicate work. An **idempotent**
  operation produces the same intended result when repeated; an idempotency key or a safe “set role to X” operation can
  help, depending on the design.
- **Cache unavailable or stale:** The system needs a defined fallback. For security decisions, it must not silently
  accept outdated access data.

These are design questions to raise, not incidents claimed from your employment.

A senior architect also asks how the team will **observe** the request: logs, metrics, and a trace that connects work
across components. Otherwise, a user may report “it failed,” but the team cannot see where it failed.

## 7. Keep components together or separate them?

Three common choices are:

| Choice                  | When it can be sensible                                                                                       | Main tradeoff                                                                               |
|-------------------------|---------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **One application**     | The product is small, the team is small, and parts change together.                                           | Simple communication, but boundaries may become unclear as it grows.                        |
| **Modular application** | Different responsibilities need clear boundaries, but independent deployment is not yet valuable.             | Simpler operation than separate services; modules still deploy together.                    |
| **Separate services**   | Responsibilities have distinct owners, change at different rates, or need independent scaling or reliability. | Flexible deployment, but network failures, data coordination, and operating costs increase. |

**Do not start with a fixed answer such as “microservices are best.”** Start with the business outcome and constraints.
Separation should solve a real problem that is worth its cost.

Questions a senior architect uses to defend the decision:

1. Do these responsibilities change together or independently?
2. Do they have different owners or security boundaries?
3. Must they scale independently?
4. What is the cost of a network call or temporary inconsistency here?
5. Can the team deploy, monitor, and support the added components?
6. Does the choice align with platform standards and the company roadmap?

## 8. How senior judgment builds on the basics

In an interview, move from **requirements to decision**:

1. **Name the business outcome.** For your real project, faster corporate client onboarding is an outcome stated in the
   application résumé.
2. **Name the rules that must hold.** For access management, changes must be authorized and recorded correctly.
3. **Choose boundaries.** Put related rules and their authoritative data under clear ownership.
4. **Choose communication.** Use immediate calls where the result is needed now; consider later processing where it is
   safe.
5. **Design for failure.** Define timeouts, safe retries, error behavior, and recovery.
6. **Plan operation and delivery.** Include monitoring, reviews, rollout, and compliance needs.
7. **Explain the tradeoff.** State why the chosen level of separation is worth its cost.

This is the difference between knowing a diagram and making an architectural recommendation.

## Interview Phrasing

> “I start by defining the business capability, the rules it must preserve, and the system that owns each important
> piece of data. Then I map the request across components and identify where network calls can fail or slow down. I keep
> closely related logic together unless independent ownership, scaling, or delivery makes separation valuable. If I do
> separate services, I define clear API contracts, failure behavior, and monitoring so the design remains operable.”

Speak this naturally. It is a **professional design answer**, while the restaurant example and request walkthrough are
tools for building your understanding. You do not need to memorize the wording.

## Keep these four points in mind

- A distributed application has multiple parts communicating across a network.
- Every important fact needs a clear owner or source of truth.
- Network communication adds delay and failure possibilities.
- The right boundary depends on business needs, team ownership, and operational cost.

When you are ready for interactive learning, we will begin with a simple teach-back in your own words. I will refine
your explanation with you before moving to design challenges.

## Source notes

- Primary role priorities: `job_posting.txt`.
- Authoritative experience and outcomes: `Sreedhar_Suswaram_R.pdf`.
- Additional user-management implementation context, pending your confirmation: `Sree-Resume.pdf`.
