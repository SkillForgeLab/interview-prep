# Cross-platform projects: Solution Architect interview prep

**Scope:** Built only from the resume versions in this folder. The wording below treats “cross-platform” as architecture
and integration across enterprise applications and services. The resumes do not establish that you built one application
for iOS, Android, Windows, and macOS.

## Your core message

> My cross-platform experience is in enterprise payments and servicing. At American Express, I partnered with a
> portfolio architect on a cross-platform Commercial Payments architecture proposal that led to a $2.35 million
> product-funded release strategy. I also led API strategy for application-to-application services on the Digital
> Servicing platform and worked on integrations between client-facing applications and backend services. My focus was
> aligning business needs, application boundaries, APIs, security, and delivery teams.

This is a strong **enterprise platform integration** answer. If an interviewer means “one application that runs on
several operating systems or mobile platforms,” clarify that your resume primarily demonstrates enterprise integration
experience.

## Evidence you can draw on

| Project                                       | Resume-supported cross-platform angle                                                                                                                                            | Your documented role and result                                                                                                                                                                                     | Boundary to respect                                                                                                                                            |
|-----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Commercial Payments architecture              | Explicitly called a “cross-platform architecture proposal” in your resumes; an earlier version describes four corporate payment products and enterprise application interfacing. | Partnered with the portfolio architect; proposal led to a **$2.35M product-funded release strategy**.                                                                                                               | The resumes do not name the exact systems in the proposal, the target architecture, or your individual design decisions. Be ready to supply those from memory. |
| Digital Servicing A2A services                | Application-to-application services and API strategy across the Digital Servicing platform.                                                                                      | Led API strategy and implementation. An earlier resume says the APIs provided traceability across business and systems-of-record functions.                                                                         | Do not claim specific protocols, API contracts, or performance results unless you can substantiate them.                                                       |
| Commercial User Management Center             | React/Redux client application connected to backend services through REST APIs; role management and self-service capabilities.                                                   | Led design and development; resume reports a **30% reduction in corporate client onboarding time**. Another version reports a **35% reduction in response times** for frequently accessed data after Redis caching. | This is a concrete multi-tier integration example. Call it cross-platform only if you explain the separate application and service boundaries.                 |
| Reconciliation migration                      | Third-party BTA-Connect clients migrated toward an in-house reconciliation platform.                                                                                             | Led roadmap execution or MVP migration strategy, depending on resume version; reduced vendor dependency and operational dependencies.                                                                               | The resumes do not describe the migration interface, data conversion, cutover mechanics, or final adoption figures.                                            |
| IAM and MFA across payment and reconciliation | Shared security needs across critical corporate payment and reconciliation platforms.                                                                                            | Led implementation of IAM and MFA; certificate renewal automation reduced manual effort by **90%**.                                                                                                                 | Do not imply a single shared identity service or particular authentication protocol unless that was actually the design.                                       |
| Earlier enterprise data integration           | Harbor Payments SaaS applications used EDI/XML integrations; a migration moved data transformation from Mercator to Informatica tools.                                           | Developed SaaS solutions and led a **$3M migration**.                                                                                                                                                               | Useful as a backup story for interoperability, though older than the Amex examples.                                                                            |

## A 45-second answer to “Tell me about a cross-platform project”

> At American Express, I worked across several enterprise payment and servicing platforms. The clearest example is
> Commercial Payments: I partnered with the portfolio architect on a cross-platform architecture proposal that resulted in
> a $2.35 million product-funded release strategy. My broader work included leading API strategy for
> application-to-application services on Digital Servicing and designing user-management capabilities where a React
> frontend communicated with backend services through REST APIs. I approached these projects by understanding each
> platform’s responsibilities, aligning stakeholders on the integration points, and ensuring the resulting solution could
> support the business roadmap. The resumes document the funding and onboarding results; I can walk through the specific
> architecture choices for whichever project is most relevant.

## A deeper answer: Commercial Payments architecture

Use this as a **framework**, then fill the bracketed items from your own recollection. The resume does not contain those
details.

> **Situation:** Commercial Payments involved multiple payment products and application interfaces. The organization
> needed architecture alignment for future releases.
>
> **My role:** I partnered with the portfolio architect on a cross-platform architecture proposal.
>
> **What I did:** We identified [the actual systems and boundaries],
> evaluated [the real integration and modernization options], and aligned [the actual stakeholders]
> on [the specific proposed design or roadmap]. I personally
> owned [your concrete design artifacts, decisions, or reviews].
>
> **Result:** The proposal led to a $2.35 million product-funded release strategy.
>
> **What I learned:** [A real tradeoff or lesson you can defend.]

**Important distinction:** The documented result is a funded release strategy. State implementation or production
outcomes only if you can describe what was delivered and how you measured it.

## A second story: User Management Center integration

> We were building self-service user management for corporate clients. I led design and development of the client-facing
> experience, including React/Redux features and role management, and contributed to REST API integration between the UI
> and backend services. That integration let the portal support dashboards, demographic updates, and account management.
> The resume reports a 30% reduction in client onboarding time. It also records Redis caching that reduced response times
> by 35% for frequently accessed data. This example shows how I worked across presentation, service, and data concerns
> while partnering with UX and product teams.

If asked how you achieved the metrics, be ready to describe the baseline, measurement period, and what other changes
contributed. The resumes do not provide that methodology.

## How to handle an architecture deep dive

For whichever real project you choose, walk the interviewer through these points in order. Fill them from your own
experience; the resumes do not specify all the answers.

1. **Business need and scope:** Who used the capability, and which platforms had to cooperate?
2. **System boundaries:** Which application owned each function and each piece of data? What changed and what stayed in
   place?
3. **Integration contract:** What crossed the boundary, through which API or interface, and how were errors and changes
   handled?
4. **Quality attributes:** What did security, latency, scale, traceability, and availability require? Which tradeoff
   mattered most?
5. **Delivery and governance:** How did you align product, architects, and delivery teams? What did you review or
   validate before release?
6. **Outcome:** Separate the architecture decision, funding, shipped capability, and measured business result. Say only
   what you can demonstrate for that project.

## Likely interview questions and answer cues

1. **What do you mean by cross-platform?** “I mean integration and architectural alignment across enterprise
   applications and services: payment products, servicing applications, APIs, backend systems, and shared security
   capabilities.”
2. **Which project is your best example?** Start with the Commercial Payments architecture proposal because your resume
   explicitly calls it cross-platform. Then offer Digital Servicing APIs or User Management Center for deeper
   implementation detail.
3. **What was your personal contribution?** Distinguish “partnered with the portfolio architect” from “led API strategy”
   and “led design and development.” Name the exact artifacts and decisions you personally owned from memory.
4. **How did you decide where an API should sit?** Use a real Digital Servicing or User Management Center example.
   Explain the consumer, provider, data owner, access rules, error handling, and operational ownership. Do not imply
   those were all documented in the resume.
5. **How did you handle disagreements between platforms or teams?** Your resume supports cross-organizational alignment,
   work with product and UX, and an LAC market architecture decision that avoided a reported $500K cost. Prepare the
   actual disagreement, alternatives, and decision process.
6. **How did you address security?** Describe your documented IAM, MFA, and certificate automation work. Be precise
   about whether security controls were shared across platforms or separately implemented.
7. **How did you prove the architecture worked?** Choose real evidence you can explain: the funded roadmap, onboarding
   time, response time, operational effort, or a release outcome. Know how each measure was collected.
8. **Did you build for multiple devices or operating systems?** “My principal cross-platform experience was enterprise
   system integration. My resume also describes responsive design work across devices, but it does not claim native
   mobile or multi-OS application delivery.”

## Details to prepare before the interview

Your resumes leave the following questions open. Write one or two factual sentences for each:

- Which exact platforms were in the $2.35M Commercial Payments proposal? Which were consumers, providers, or systems of
  record?
- What problem was the proposal solving? What alternatives were considered and why did your team choose the proposed
  approach?
- What did **you** design or decide, versus what the portfolio architect or other teams owned?
- Which API design choices did you own for Digital Servicing A2A services? How were authentication, errors, versioning,
  and observability handled in that project?
- What was the baseline and measurement method for the 30% onboarding improvement and 35% response-time improvement?
- Which parts of the cross-platform proposal were implemented, and which remained a roadmap?
- For any migration story, what was the actual transition path and how did you maintain service continuity?

## Source notes

Primary current resume: [Sreedhar_Suswaram_R.pdf](Sreedhar_Suswaram_R.pdf). Supporting
detail: [Sree-Resume.pdf](Sree-Resume.pdf), [Sree.pdf](Sree.pdf), and [sree_resume-1.pdf](sree_resume-1.pdf). Some
versions describe the same accomplishments differently. Before the interview, choose the wording and metrics you can
personally verify, especially for the Commercial Payments savings and the scope of completed work.
