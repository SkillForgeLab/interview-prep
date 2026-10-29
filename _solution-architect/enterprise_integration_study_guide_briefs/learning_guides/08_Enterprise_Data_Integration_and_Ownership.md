# Enterprise Data Integration and Ownership

**Study guide for senior/principal Enterprise and Integration Solution Architect interviews**  
**Scope:** Vendor-neutral design for operational data shared across applications. Examples are illustrative. Standards and platform-specific references were checked on **28 October 2026**.

## 1. Frame the ownership decision before choosing technology

An application can be the **system of engagement** without owning the resulting fact. A CRM may collect a customer's correction; an ERP may own the legal billing name used on an invoice. The system of record (SoR) is authoritative for a *fact at a specified stage*, not necessarily the oldest database or the system with the best user interface. Authority can differ by attribute, lifecycle state, geography, or legal entity.

Before selecting an MDM product, integration platform, or canonical schema, secure decisions from business and data owners:

1. Define the business meaning and grain of each entity: a customer as a legal party, a selling account, a billing account, or a contact are different things.
2. Assign a named accountable steward for each attribute and the team authorized to approve corrections. Identify the process that can create, merge, split, or retire a record.
3. Decide identifiers, matching evidence, survivorship rules, and what uncertainty requires human review. Agree which relationships must survive a merge.
4. Set consumer freshness and availability needs, acceptable stale behavior, reconciliation tolerance, retention, and privacy requirements.
5. Agree who funds quality remediation and responds when a source is wrong or an integration misses a change.

**Master data management (MDM)** is the governance and operation of trusted shared entities, identifiers, stewardship, and distribution. A registry can hold cross-references; a coexistence design can compose trusted attributes; a centralized design can accept writes. A dedicated platform is optional. The critical test is whether competing writers can create contradictory facts and whether someone can correct them.

## 2. Identity, models, reference data, and quality

**Identity matching is a decision with consequences.** Keep immutable source IDs and an enterprise party ID in a cross-reference table: `(source, source_id) → enterprise_party_id`. Do not use an email address, phone number, or name as the primary enterprise key; these change and may be shared. Start with deterministic links where evidence is strong, such as a verified tax identifier within the correct jurisdiction and legal-entity scope. Use probabilistic candidates for weaker combinations of normalized name, address, and contact details. Set thresholds for automatic match, possible match review, and no match; record the features and rule version that led to each decision. A false positive merge can expose one customer's data to another and corrupt order history, so favor review when evidence is ambiguous.

Deduplication is more than deleting a row. Preserve source IDs, aliases, merge history, and a reversible mapping. Resolve dependent orders, invoices, consent, and credit exposure by business rule. A split must restore correct links. Distinguish a *party* (identity), *account* (relationship), *contact* (person or channel), and *address* (role-specific location). Multiple billing accounts may legitimately refer to one party.

A **canonical model** can reduce repeated transformations for a stable shared concept, but can flatten domain distinctions and create a central change queue. Domain-owned contracts may fit better: a `CustomerRegistered` event, order API, and invoice projection need different fields. Share identifiers and a semantic glossary; document units, currency, timezone, null versus absent, effective dates, and enum meaning. Version contracts when meaning changes, even if parsing succeeds.

**Reference data** such as country codes, payment terms, tax categories, and product status needs authority, effective dates, and mapping rules. `ACTIVE` in CRM may mean marketable; in ERP it may mean billable. Reject unknown values rather than inventing a default. Measure completeness, validity, uniqueness, consistency, timeliness, and accuracy against evidence. Define each measure's denominator, threshold, owner, and remediation path; a low null rate does not prove accuracy.

## 3. Worked customer master: CRM and ERP disagree

**Scenario assumptions:** CRM owns prospect and sales engagement data. ERP owns accepted billing accounts, invoices, and credit decisions. An enterprise identity registry links records but does not authorize arbitrary edits. CRM customer `C-1842` and ERP account `E-9081` map to party `P-402`. CRM shows **Acme Industrial LLC**, `sales@acme.example`, Phoenix shipping address, and `Net 45`; ERP shows **Acme Industrial Inc.**, `ap@acme.example`, Dallas billing address, and `Net 30`. A salesperson changed CRM yesterday. These are invented values; they are not proof of a match or of which source is correct.

| Attribute or relationship | Authority and allowed writer | Conflict rule and consumer behavior |
|---|---|---|
| Legal billing name, tax ID, bill-to address | ERP account team after verified evidence | ERP wins for invoices. CRM may propose a correction, never overwrite ERP directly. Preserve prior value and effective date for issued documents. |
| Display name, sales segment, account owner | CRM sales operations | CRM wins for engagement views; do not substitute display name for a legal invoice name. |
| Contact email | Domain scoped: CRM owns sales contact; ERP owns accounts-payable contact | Keep both with role and verification status. Never choose one generic `email` by latest timestamp. |
| Ship-to address | Order/customer operations through an approved address workflow; order captures a snapshot | A valid ship-to need not equal bill-to. Validate use for the order and retain the address used at booking. |
| Payment terms, credit limit, billing status | ERP finance/credit team | ERP wins for order acceptance and invoicing. CRM displays a read-only projection with source version and freshness. |
| Enterprise party link and duplicate/merge status | Data stewardship/identity service | Steward-approved match or split updates the cross-reference; neither application may infer a merge solely from a changed name. |

The legal-name disagreement is **not** resolved by the newest timestamp. The CRM change becomes a correction case with the proposal, evidence, submitter, and reason. The account steward validates it; the ERP account team updates ERP if justified. Integration updates CRM's projection after the committed change and verifies both versions. If rejected, CRM records the reason. Issued documents retain their original legal-name snapshot; amendments follow the finance process.

Prevent a loop with field-level write permissions, read-only projected fields, and `source_system`, `source_record_id`, `source_version`, `effective_at`, and `change_id` on updates. Consumers apply only newer authorized versions, suppress echoes, and quarantine unauthorized writes. A UI edit to an ERP-owned field creates a **correction request**. Where APIs cannot enforce this, use a controlled workflow and monitor unauthorized changes.

## 4. Choose synchronization by semantics and recovery

| Option | Data semantics | Typical timeliness | Failure recovery | Coupling and best fit |
|---|---|---|---|---|
| **API request** | Command or query with explicit validation and immediate response; success means the endpoint accepted its contract, not every downstream projection is current | Synchronous call, bounded by network and service latency | Retry only with safe/idempotent semantics or an application idempotency key; reconcile ambiguous timeouts against a business ID | Caller depends on endpoint availability and contract; best when a decision must be made now, such as credit approval |
| **Business event** | Domain fact such as `CustomerBillingStatusChanged`, with business meaning and source version | Usually seconds to minutes, subject to publish and consume lag | Durable delivery, replay within retention, dedupe by event ID, ordered/version-aware application, dead-letter repair | Consumers depend on published meaning rather than source tables; best for distributing committed facts |
| **CDC** | Insert/update/delete at the database boundary; may lack the business reason or operation | Usually near real time but asynchronous | Persist log offset/checkpoint, retain source log long enough, replay idempotently, use a new snapshot if retention is exceeded | Strong coupling to source schema and database operations; useful when application events are unavailable or for bulk replication |
| **ETL/batch** | Snapshot or extract over a defined time window; transforms can apply business rules | Scheduled, often hours or daily | Restart from a known watermark, stage/validate, compare counts and hashes, rerun a partition atomically | Looser runtime coupling but dependent on extract format and schedule; useful for large backfills, analytics, or low urgency feeds |

These are design ranges, not guarantees. CDC is not a business event: a row update may be a correction, state transition, or maintenance job. SQL Server's CDC reads committed transaction-log changes asynchronously and exposes log sequence metadata; monitor capture latency and retention. Validate other products' guarantees separately. [Microsoft SQL Server CDC](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/track-data-changes-sql-server), [CDC operation and retention details](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server/).

For HTTP APIs, `PUT` has idempotent intended semantics under RFC 9110; `POST` does not automatically become safe to retry. A business idempotency key or query-by-business-ID can resolve the ambiguous case where the server committed but the response was lost. [RFC 9110, §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2). CloudEvents, if selected as an event envelope, requires `id`, `source`, `specversion`, and `type`; `source` plus `id` identifies a distinct event and can support duplicate detection. It does **not** define delivery, ordering, or the business payload for you. [CloudEvents specification](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

**Freshness is measured end to end.** Define `source_committed_at`, `published_at`, `received_at`, and `applied_at`; measure source-to-visible lag per record and the oldest unapplied committed record, not merely average message age. A target can be caught up at its broker while still behind the source. Set a consumer-specific objective, for example: billing-status projection visible in CRM within five minutes for 99% of committed changes, with an alert at ten minutes and a sales UI warning when its last verified source version is older. Keep an explicit stale-state policy: block credit-dependent order submission or query ERP live, while allowing a sales dashboard to show a timestamped stale value. Use snapshot plus incremental catch-up for initial loads; establish a source-consistent watermark, apply changes after it, and verify before cutover.

For **schema evolution**, publish contracts with semantic definitions, examples, and compatibility tests. Additive optional fields may still break strict consumers or alter defaults. Renaming a field, narrowing its domain, changing currency, or reinterpreting `status` is a breaking change even if JSON parsing succeeds. Run old and new consumers in parallel for a migration window and retain a replayable history or transformation for late consumers. CloudEvents' primer recommends changing event type for backward-incompatible data changes and allows a distinct `dataschema` URI; this is guidance for that envelope, not a substitute for consumer testing. [CloudEvents primer: versioning](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/primer.md#versioning-of-cloudevents).

## 5. Concrete lineage and ownership matrix

**Scenario assumptions:** The same enterprise has CRM, ERP, product information management (PIM), an identity registry, an integration layer, and a warehouse. `→` means a governed data flow; the warehouse is a derived copy. Each row names the business owner who resolves content errors, distinct from the integration team that repairs transport failures.

| Entity and grain | Authoritative creation and attributes | Lineage to consumers and identifiers | Correction owner and control |
|---|---|---|---|
| **Customer**: party plus separate billing account and contacts | CRM creates prospect/engagement attributes; ERP creates accepted billing account, legal billing identity, terms; registry assigns enterprise party link | CRM `C-1842` + ERP `E-9081` → registry `P-402` → CRM/ERP projections and warehouse; retain source IDs, versions, and match decision | Sales ops corrects engagement; account/finance team corrects billing; data steward approves merge/split |
| **Order**: one accepted order with lines and revisions | Order service/ERP owns accepted order ID, lines, price snapshot, status; CRM may own opportunity ID but not booked order | Portal/CRM command → order API → ERP `O-7751` → `OrderAccepted` event → CRM status and warehouse; preserve partner request ID and revision | Order operations corrects order state; finance approves monetary adjustment; integration team repairs failed delivery |
| **Product**: sellable SKU and effective catalog version | PIM/product team owns description, classification, lifecycle; ERP owns finance-specific cost and tax treatment | PIM `SKU-73`/catalog version → catalog API or event → CRM, commerce, ERP mapping, warehouse; order stores SKU/version snapshot | Product steward fixes taxonomy/content; finance corrects cost/tax mapping; no silent SKU reuse |
| **Invoice**: issued financial document and lines | ERP finance owns invoice number, legal entity, amount, tax, issued/cancelled state | ERP `INV-4402` → `InvoiceIssued` event or governed extract → portal and warehouse; reference order ID and customer billing snapshot | Finance issues credit/rebill or correction per policy; integration team only repairs copies |

The lineage record for each transformation should retain input dataset or event IDs, source version, mapping version, run/correlation ID, output ID, timestamps, and responsible service/team. This is enough to answer “which ERP value produced this CRM display?” and “which invoices used the old address?” W3C PROV provides a useful vocabulary of **entities**, **activities**, and **agents** for recording data derivation and responsibility; the architecture can use a simpler implementation with the same questions answered. [W3C PROV-O](https://www.w3.org/TR/prov-o/).

## 6. Reconciliation that leads to a repair

Reconciliation compares a **source-consistent slice** with its intended target state. It must account for in-flight updates: choose a watermark `W` representing changes committed through a point both sides can identify, wait for the target to apply through `W`, then compare. For a batch feed, compare the same partition and extract manifest. Never call a legitimately lagging row “missing” without the cutoff. Keep a daily full or partitioned comparison even if continuous processing appears healthy.

| Detection | Concrete test | First response and resolution owner |
|---|---|---|
| **Missing** | Anti-join authorized source IDs at `W` to target source-ID cross-references; compare counts by entity, date, and state | Integration operations checks backlog, dead letters, checkpoint, mapping rejects, and replay; source owner handles a record absent from its own extract |
| **Duplicate** | Count repeated `(source, source_id)` mappings, repeated event application, and multiple enterprise IDs with high-confidence shared identity evidence | Integration operations removes duplicate projection after tracing delivery; data steward reviews identity merge; domain owner checks duplicate source creation |
| **Mismatched** | Compare normalized, field-scoped hashes and versions only for attributes the source owns; separately compare money, currency, effective date, and status semantics | Integration team fixes transform/version ordering; authoritative domain owner corrects wrong source value; steward decides disputed identity or meaning |

Store each discrepancy as a case with entity IDs, source/target versions, watermark, observed values or protected hashes, classification, severity, owner, due time, and repair outcome. Automatic replay is appropriate for a missed authorized change; it is not appropriate for deciding whether a legal name is true. After a repair, verify the specific record and the next aggregate run, then close with evidence. Track unresolved cases by age and business impact, not only the mismatch count. Sample sensitive fields through controlled views; a reconciliation dashboard should not become an uncontrolled copy of personal data.

## 7. Conflict resolution, privacy, and audit

Use a **policy order**: validate writer authority, identify the entity and attribute scope, check source version and effective date, apply the permitted value, and route an exception for business judgment. A global “last write wins” rule is unsafe across independent clocks and different meanings. Even version order cannot tell whether a legally verified correction is true; it only tells which authorized source change came later. For concurrent changes in one owned domain, use compare-and-swap or an expected version, then require the caller to reload and retry or resolve the conflict. Preserve the losing proposal as evidence; never silently discard it.

Personal data flows need a purpose and a bounded audience. Distribute only the attributes needed by each consumer, record lawful basis and retention with the privacy team, and propagate corrections, access restrictions, and deletion requests across projections and backups according to applicable policy. Keep an identity-link history under strict access because matches can reveal relationships. Audit who changed an authoritative value, who approved a merge, the before/after reference or protected digest, the rule version, and the downstream propagation outcome. Encrypt and restrict logs; avoid dumping raw customer profiles into dead-letter queues. If GDPR applies, its Article 5 principles include data minimization, accuracy, storage limitation, integrity/confidentiality, and accountability, while Article 30 addresses records of processing activities. Those are legal obligations to interpret with counsel for the actual jurisdiction and role. [EU GDPR, Articles 5 and 30](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng).

## 8. Interview questions with model answers

**Q1. Which system is the customer master: CRM or ERP?**  
**Answer:** Ask what “customer” means and which attribute and lifecycle stage matter. CRM can own a prospect and relationship fields; ERP can own billable account, legal identity, and terms. Put those choices in an ownership matrix, enforce write paths, and reconcile copies. A golden record is a composed view with provenance, not a license for every system to edit everything.

**Q2. When would you introduce MDM?**  
**Answer:** Start with identity ambiguity, cross-domain reuse, quality cost, and the need for stewardship. If a registry and governed APIs solve a small number of flows, a platform may add unnecessary complexity. Introduce broader MDM capabilities when matching, merge/split, survivorship, workflow, and lineage exceed what domain teams can reliably operate. Decide ownership and correction rights first.

**Q3. Would you use CDC to publish `CustomerApproved`?**  
**Answer:** A row change alone does not prove an approval occurred. Prefer an application event committed with the business decision. If CDC is the only available capture path, translate database changes through a governed state machine and document the inference; do not label any update as an approval. Preserve offsets and source versions, and reconcile missed windows.

**Q4. What happens if an event is delivered twice or out of order?**  
**Answer:** Deduplicate by stable event identity, then apply only a valid newer source version for the affected entity. Keep an inbox or applied-version record atomically with the projection update. If a gap matters, hold and fetch the current authoritative state. Replay should converge to the same result; it should not create a second customer or invoice.

**Q5. How do you prove the integration is current and correct?**  
**Answer:** Instrument commit-to-visible lag and oldest unapplied change, then reconcile a consistent watermark for missing, duplicate, and mismatched records. Assign transport faults to integration operations, bad source facts to the domain owner, and identity disputes to stewardship. Report aged unresolved cases and business effect.

## 9. Common data-model traps

- Calling one `Customer` table the SoR for every field; ownership often changes by attribute and state.
- Collapsing party, account, contact, bill-to, and ship-to into one mutable object.
- Treating email or tax ID alone as a universal key, or merging on a fuzzy match without a split path.
- Using the newest timestamp as a truth rule across unsynchronized systems.
- Mistaking CDC row operations for business events, or assuming an event broker supplies business semantics.
- Declaring an additive field safe without testing strict consumers and defaults.
- Sharing reference-data codes without their scope, effective date, and meaning.
- Measuring transport uptime while ignoring source-to-visible lag and unresolved discrepancies.
- Letting a derived warehouse or a UI overwrite an authoritative operational attribute.

## 10. Practice exercise and answer key

**Exercise (10–15 minutes):** A retailer has CRM, ERP, PIM, a customer portal, and a warehouse. CRM and ERP each contain a customer called Northstar Supply; CRM has two records with different emails, while ERP has one billing account. PIM changed a SKU's tax category at 09:00. At 09:05 the portal displays the new category, but ERP booked an order using the old category. An `InvoiceIssued` event was replayed twice after an outage. Design: (a) the customer match decision and ownership; (b) the synchronization and stale-data policy for product tax; (c) duplicate-invoice handling; (d) one reconciliation query or comparison for each fault; and (e) the business and technical owners for repair. State assumptions.

**Answer key:** Assume the two CRM records might be separate contacts or selling accounts; do not merge from name alone. Link both to the ERP billing account only after evidence such as verified legal identity, address, and account relationship is reviewed. Keep both CRM IDs, the ERP ID, match confidence, and the steward decision. CRM owns sales contacts; ERP owns billing terms and account state; PIM owns product classification, while finance owns the tax rule applied to an order. If tax category is actually finance-owned in this enterprise, change that ownership explicitly before implementing.

Publish a versioned PIM product change and have ERP acknowledge the catalog or tax-mapping version it can use. At booking, ERP applies its authoritative tax decision and stores the product/catalog and tax-rule versions on the order. If stale tax data creates material risk, block booking for an unacknowledged version or query the authoritative service; showing a newer portal category does not make ERP current. Reconcile PIM-versus-ERP SKU/version at a common watermark and compare orders booked after 09:00 against their applied version and effective-date rule. Product/finance owners decide whether to correct or credit affected orders; integration operations repairs a missed feed.

For invoices, deduplicate the replay by `(event source, event ID)` and invoice ID/version; the portal and warehouse should have one projection for one ERP invoice, not create financial documents. Reconcile ERP invoice IDs and versions against portal/warehouse IDs, count duplicate target rows, and compare amount, currency, and status. Integration operations removes an accidental duplicate projection and fixes replay behavior; ERP finance alone decides whether a real duplicate invoice was issued and how to reverse it. Close each case only after record-level verification and a clean comparison through the agreed watermark.
