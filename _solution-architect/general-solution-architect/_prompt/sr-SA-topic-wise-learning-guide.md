# 💡Topic-wise learning guide

## 1. Distributed application design

- **Understand:** Services and components, responsibilities, communication, data ownership, and failure points.
- **Explain aloud:** How a request moves through a system and where its data is owned.
- **Defend:** Why a simpler application or separate services better fit the requirements, including the tradeoffs.
- **Practice:** Draw a simple system and trace a request across its components.

## 2. REST integration and API strategy

- **Understand:** REST contracts, consumers, ownership, security, versioning, compatibility, and service-oriented
  architecture (SOA).
- **Explain aloud:** How platforms integrate, what each platform owns, and what an API promises to its consumers.
- **Defend:** API boundaries, rollout order, and compatibility choices as part of a staged implementation roadmap.
- **Practice:** Walk through the Digital Servicing application-to-application API strategy without overstating your
  role.

## 3. Reliability, performance, and scalability

- **Understand:** Timeouts, retries, monitoring and observability, bottlenecks, capacity, and integration failures.
- **Explain aloud:** How you investigate a slow or failed transaction, including the likely failure path and evidence to
  check.
- **Defend:** Which improvement to make first and what risk or tradeoff it introduces.
- **Practice:** Trace a slow or failed request and describe the order of investigation and fixes.

## 4. Architecture alignment and roadmap

- **Understand the architecture domains:**
    - **Business architecture:** Outcomes, capabilities, processes, users, and the measures that show whether the change
      succeeded.
    - **Information architecture:** Important data, its meaning and ownership, where it is created and consumed, how it
      moves, and its quality, lifecycle, and protection needs.
    - **Application architecture:** Applications and services, their responsibilities and boundaries, integrations, and
      the systems of record.
    - **Technology architecture:** Hosting and runtime platforms, networks, storage, identity, observability, and the
      operational constraints and standards they impose.
    - **Alignment:** A proposal is coherent when the connections between these domains are explicit—for example, a
      business capability depends on an application, which uses data with a clear owner and runs on an approved
      platform.
- **Understand blueprints and roadmaps:** A blueprint describes the intended capabilities, boundaries, standards, and
  target-state relationships. A roadmap turns that direction into sequenced changes from the current state to the target
  state. It should account for dependencies, delivery capacity, risk, value, and the need to keep existing services
  operating during transition.
- **Use a repeatable alignment method:** Start with the business outcome and success measure; establish the current
  state and constraints; identify capability, data, application, and technology impacts; compare viable options; record
  assumptions and decisions; then sequence the work into deliverable increments with owners, dependencies, risks, and
  validation measures.
- **Explain aloud:** Connect a concrete design decision to the business outcome, then trace its effects through
  information, application, and technology architecture. State what changes, what remains, who owns each part, and how
  success and operational health will be measured.
- **Defend:** A choice that balances a local need with platform direction. Make the tradeoff explicit: value and urgency
  versus duplication, integration complexity, support burden, security or compliance risk, and future migration cost.
  Explain why the option is acceptable, what guardrails limit its impact, and what evidence would trigger a different
  decision.
- **Build a phased roadmap:** Separate immediate needs from target-state work. For each phase, name the outcome, scope,
  prerequisites, accountable owner, risks, and exit criteria. Prefer increments that deliver usable value and reduce
  uncertainty; include coexistence, data migration or synchronization, compatibility, testing, rollout, rollback, and
  retirement of replaced components where relevant. Do not describe a roadmap as a list of technologies without business
  outcomes or sequencing rationale.
- **Practice:** Choose a real project and sketch its current and target states. Mark the business capability, key data
  and owner, applications and integrations, and platform constraints. Then propose two or three phases, explain their
  dependencies and tradeoffs, and identify measures that would show each phase worked. If you lack direct experience
  with part of the example, clearly distinguish what you did from what you would recommend.
- **Check your answer:** Can a listener see why the change matters, how the architecture domains fit together, why the
  sequence is practical, and how you will know when to adjust course? Avoid presenting the target state as guaranteed,
  treating standards as substitutes for reasoning, or claiming alignment without naming the relevant constraints and
  decision owners.

## 5. Governance, reviews, and technical leadership

- **Understand:** Standards, design and code reviews, decision records, team responsibilities, collaboration, and
  mentoring.
- **Explain aloud:** How you reach and communicate an architecture decision, document it, and give actionable feedback.
- **Defend:** A decision when product speed, engineering effort, and standards conflict, including when an exception is
  justified.
- **Practice:** Prepare a concise design-review recommendation and explain how you would guide teams through delivery.

## 6. Security and compliance

- **Understand the risk and data:** Identify what the system protects, who may be affected, and what could go wrong.
  Classify data by sensitivity; trace what is collected, processed, stored, copied, shared, and deleted. Consider
  confidentiality, integrity, availability, privacy, and misuse—not only unauthorized access.
- **Use a repeatable security-design method:** Establish business context, data flows, trust boundaries, users,
  dependencies, and operating assumptions. Identify likely threats and their impact; choose preventive, detective, and
  recovery controls proportionate to the risk; assign owners; and validate the controls through testing, monitoring, and
  review. Revisit the assessment when the design or threat context changes.
- **Place controls across the architecture and lifecycle:**
    - **Identity and access:** Authenticate users and services; authorize each action using least privilege and
      appropriate roles or attributes; manage service identities, privileged access, credential rotation, and access
      removal.
    - **Application and integration boundaries:** Validate input and enforce authorization at the service that owns the
      resource. Protect APIs against abuse, limit exposure, and use authenticated, appropriately protected
      service-to-service communication. Treat external services and supplied data as untrusted dependencies.
    - **Data and infrastructure:** Minimize collection and retention; protect data in transit and at rest; manage
      encryption keys and secrets separately from application code; isolate workloads and restrict administrative paths;
      and patch and configure platforms securely.
    - **Operations and recovery:** Record security-relevant events with appropriate access and retention, while avoiding
      unnecessary sensitive data in logs. Monitor and alert on meaningful signals; define incident response, backup,
      recovery, and vulnerability-management responsibilities.
    - **Delivery and change:** Include security requirements in design and review, threat modeling, coding and
      dependency practices, testing, release decisions, and ongoing operations. Define how exceptions are approved,
      time-limited, and tracked to resolution.
- **Connect compliance to evidence:** Determine which laws, regulations, contracts, and organizational policies actually
  apply with the relevant legal, privacy, risk, and compliance owners. Map applicable obligations to system
  requirements, controls, accountable owners, and evidence such as approvals, test results, access reviews, and
  operational records. Do not claim a design is compliant based only on a checklist or a technology choice.
- **Explain aloud:** Walk through a representative data flow and mark the trust boundaries, sensitive data, identities,
  and control points. Describe how controls reduce a named risk, who operates them, what evidence demonstrates they
  work, and how the system detects and responds when a control fails.
- **Defend:** Explain why a control is placed at a particular boundary, why it is proportionate to the risk, and what
  residual risk remains. Compare viable options using security, privacy, usability, delivery effort, operational burden,
  and recovery needs. Clarify compensating controls, ownership, approval, and a path to remove any temporary exception.
- **Practice:** Sketch a service that accepts personal data through an API, stores it, and sends part of it to a third
  party. Mark data classification and flow, trust boundaries, user and service identities, authorization checks,
  encryption and key ownership, retention and deletion, audit events, monitoring, and failure or incident handling. Then
  identify the applicable review owners and the evidence you would gather, stating assumptions rather than inventing
  regulatory requirements.
- **Check your answer:** Can you name the asset, threat, impact, control, owner, and evidence for each key risk? Have
  you considered least privilege, data minimization, safe logging, third-party dependencies, recovery, and residual
  risk? Avoid treating encryption or a compliance label as a complete security design, and distinguish verified
  obligations from assumptions.

## 7. Agile delivery and the software development life cycle

- **Understand:** How architecture work fits planning, implementation, testing, release, and operation.
- **Explain aloud:** How to deliver architecture in usable stages.
- **Defend:** What must be decided now and when to leave room to learn.

## 8. Responsible AI-assisted architecture

- **Understand:** Where AI can help with analysis and documentation, and how to validate its claims and outputs.
- **Explain aloud:** A practical review workflow, including how you check an AI-generated diagram or document.
- **Defend:** Which conclusions need evidence or human review, and how to control incorrect claims, sensitive-data
  exposure, and design risk.
- **Practice:** Use examples from your personal AI projects.

## 9. Senior technical assessment

- **Understand:** One strong programming discipline and its design fundamentals.
- **Explain aloud:** How code choices affect architecture.
- **Defend:** A focused code-review recommendation.

## Final review

Use this as a short review rather than a new study topic:

- Review your system diagrams and five key tradeoffs.
- Rehearse two real project stories and a few concise answers aloud.
- Focus on clear, calm explanations in your own words; avoid new material.
