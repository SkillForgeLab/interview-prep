## System Design Tutor — Package created

The package includes both folder-based and filename-based routing.

**System Design Tutor package**

ZIP · Both layouts, installation instructions, and original roadmap

### Separate downloads

- Native skill — directory structure
- ChatGPT Project — flat-file version

The package includes 8 learning modules, all 73 design cases, 16 detailed anchor
references, and 4 shared concept references.

### How to use it with ChatGPT Projects

1. Extract the `chatgpt-project-flat` folder.
2. Copy `PROJECT_INSTRUCTIONS.txt` into your ChatGPT Project Instructions.
3. Upload `SKILL.md`, `sdt-catalog.md`, and the relevant module files.
4. Add individual anchor and concept files as needed.

Routing example:

```
Request: Design a payment gateway
  |
  +-- SKILL.md
  +-- sdt-module-02-payments.md
  +-- sdt-anchor-05-payment-gateway.md
```

Unrelated design files should not be requested.


> **Limitation:**
> In **ChatGPT Projects**, this is instruction-based routing, not guaranteed
> automatic skill activation.
>
> **Native Agent Skills** support structured references; Project Sources use
> uploaded files and Project Instructions.

### Anchor distribution

| Module                   | Anchors created                                        | Count |
|--------------------------|--------------------------------------------------------|-------|
| 1. Foundations           | Shared concepts, not anchor designs                    | 0     |
| 2. Payments & Finance    | Authorization, Ledger, Settlement, Fraud, Gateway      | 5     |
| 3. Scalable Applications | Rate Limiter, Checkout, Notifications, Chat, News Feed | 5     |
| 4. Distributed Workflows | Ticket Booking                                         | 1     |
| 5. Data & Streaming      | Search Indexing, Streaming Analytics                   | 2     |
| 6. Cloud & Reliability   | Multi-region Architecture                              | 1     |
| 7. Security & Enterprise | Enterprise IAM, Legacy Modernization                   | 2     |
| 8. Advanced Systems      | No dedicated anchor                                    | 0     |
| Total                    |                                                        | 16    |

### Do you need to create more anchors?

No, not initially.

The intended structure is:

- **Module:** Covers all design cases in that category.
- **Anchor:** Provides a detailed worked reference for an important design.
- **Shared concepts:** Explain reusable patterns across designs.
- **Tutor skill:** Generates a full worked design for cases without dedicated
  anchors.

> **For example:**
> Design a URL Shortener has no anchor file.
> The tutor uses Module 3 and the common design method to teach it.

### My recommendation

Keep the existing 16 anchors for now. Create additional anchors only when a
design introduces important concepts not sufficiently covered by existing ones.

**One distinction:** The anchor files are worked architecture references, not
complete, fixed lessons covering every possible requirement. The tutor is
expected to build explanations from them.

You can continue with the existing package. No additional files are required.