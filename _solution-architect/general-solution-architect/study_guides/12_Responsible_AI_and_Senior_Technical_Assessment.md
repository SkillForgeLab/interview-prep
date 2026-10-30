# Responsible AI-Assisted Architecture and Senior Technical Assessment

**Core learning guide for Solution Architect interviews**

This guide covers responsible use of AI for architecture analysis and preparation, plus the focused technical
assessment expected of a senior architect. It complements
[Security Architecture](08_Security_Privacy_and_Compliance.md) and
[Architecture Leadership](11_Architecture_Governance_Leadership_and_Agile_Delivery.md).

## Learning outcomes

- Use AI to accelerate bounded analysis while retaining human accountability.
- Validate generated diagrams, recommendations, assumptions, and citations.
- Protect sensitive information when using AI tools.
- Explain how programming fundamentals and code review connect to system architecture.

## 1. Use AI for drafts, not authority

AI may help organize requirements, propose alternative designs, summarize supplied material, or create a first diagram.
Its output can omit constraints, invent facts, cite irrelevant sources, or produce a plausible but invalid design.
Treat it as a hypothesis that requires review.

```text
Bounded task -> approved, minimized input -> generated draft
             -> verify facts and constraints -> human decision and record
```

Give the tool only the context it needs and only through an approved environment. Do not submit confidential business
data, personal data, credentials, source code, or regulated information unless the tool and organizational policy
explicitly permit it. Follow the relevant data-handling rules.

## 2. Validate every consequential output

For an AI-generated architecture:

1. Compare each component and assumption with the requirements and system context.
2. Verify service capabilities, limits, security claims, and citations against authoritative sources.
3. Check data ownership, trust boundaries, failure behavior, cost, and operational support.
4. Ask a qualified owner to review high-impact security, privacy, compliance, or business decisions.
5. Record what was accepted, changed, or rejected and why.

Do not treat a generated diagram or fluent explanation as evidence that the design meets an SLO or compliance
obligation. Keep human accountability for recommendations and decisions.

## 3. Connect code review to architecture

A senior technical assessment may test one programming discipline and the ability to reason from code to system
behavior. Be prepared to discuss correctness, error handling, data access, concurrency, security, observability, and
testability. Explain how a local implementation choice affects an API contract, data invariant, resource limit, or
failure boundary.

Keep the review focused: identify the highest-impact issue, explain the observable consequence, propose a proportionate
change, and state how a test would verify it. Avoid rewriting code to express personal style when there is no
meaningful correctness or maintainability benefit.

**Say it professionally:**

> “I use AI to accelerate bounded analysis, but I validate its claims against requirements and primary sources. I
> keep sensitive information out unless the approved environment permits it, and I remain accountable for the final
> architecture decision.”

## 4. Practice and self-check

Use an AI assistant to draft a high-level design for an illustrative notification system, without using confidential
material. Review it for missing assumptions, unsupported service claims, data flow, failure handling, cost, and
operational ownership. Write down what you changed and which evidence supports the final recommendation.

Then review a small code change from a project you are permitted to discuss. Identify one architecture-level
consequence and one test that would expose it. Do not claim the illustrative design as personal work.

Check your answer: Did you verify every consequential claim? Did you protect the input? Can you distinguish a tool's
suggestion from your own evidence-backed decision?

## References

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Playbook](https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook)
- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
