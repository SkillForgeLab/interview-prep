# Choosing Enterprise Integration Patterns

*A decision guide for senior and principal architects preparing for vendor-neutral design interviews*

## The decision starts with the business promise

An integration pattern is a way to make a promise across a system boundary. Before naming a transport, state what the
sender needs to know, when it needs to know it, who owns the resulting state, and what must happen if either side is
unavailable.

**Assumptions for this guide:** The examples describe hypothetical organizations. No particular employer’s latency
target, transaction boundary, partner contract, technology estate, or regulatory obligation is assumed. Where those
facts would change the design, the guide calls them out.

Classify the interaction first:

- A **command** asks a specific owner to do something: “Submit this order.” It can be rejected. A queue can carry it
  when the requester can wait for the outcome.
- An **event** states a fact that the owner has already committed: “Order accepted.” Interested consumers decide what to
  do next. An event must not quietly become a command requiring every subscriber to succeed.
- A **query** asks for information without requesting a business state change. A synchronous API is often a natural fit
  when the answer must be current. HTTP defines `GET` as read-oriented and distinguishes safe methods from idempotent
  ones. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)
- **Bulk data movement** transfers a set of records, usually for loading, reconciliation, reporting, or partner
  exchange. Its unit of control is often a dataset or processing window rather than one business action.

These are meanings, not transports. An HTTP request can submit a command; a file can contain business events; a stream
can carry CDC records. The meaning determines the contract. The transport determines how that contract behaves under
load and failure.

## Decision tree

Read from the top. More than one branch can apply to different stages of the same workflow.

1. **Must the caller receive an authoritative answer before continuing?** If yes, use a synchronous API to reach the
   system that can make that decision within the response deadline. If the response only means “received for later
   work,” say so and expose status; HTTP `202 Accepted` does not mean processing has
   completed. [RFC 9110, §15.3.3](https://www.rfc-editor.org/rfc/rfc9110.html#name-202-accepted)
2. **Is one identified owner being asked to perform work that may wait?** Prefer an asynchronous command through a queue
   when buffering, retry, and independent recovery solve a real problem.
3. **Has the owner committed a business fact that several independent consumers need?** Publish a business event. Use
   subscriber-specific durable delivery where missed events matter.
4. **Must consumers reprocess history or build independent views from an ordered sequence?** Consider retained event
   streaming. Define retention, partitioning, and replay policy before choosing it.
5. **Is the requirement to copy database changes because the application cannot publish a suitable contract?** Consider
   CDC. Treat its schema and lifecycle as a data integration contract, or transform an application-owned outbox record
   into a business event.
6. **Is freshness measured in hours or days, or is the payload a large snapshot?** Prefer batch/ETL when scheduled
   extraction, transformation, and reconciliation meet the need.
7. **Does an external partner or legacy application require a document, interchange, or scheduled handoff?** Use the
   agreed file/SFTP/EDI exchange. Do not introduce an API merely to disguise the same nightly batch.

Then ask whether the design meets the outage, duplicate, ordering, and ownership requirements. If it does not, revisit
the branch.

## Comparison matrix

| Pattern                              | Good fit                                                                                                                                             | Poor fit                                                                                                             | Typical failure mode                                                                                                              | Key interview question                                                           |
|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| **Synchronous REST/API**             | Immediate validation, current query, or a command whose owner can finish within a caller’s deadline.                                                 | Long-running work or a dependency that may be unavailable for extended periods.                                      | Timeout leaves the caller unsure whether the operation committed; chained calls spread latency and failure.                       | “What exactly does success mean, and can the owner decide before timeout?”       |
| **Asynchronous queue/command**       | One logical owner must perform work; backlog and retry let the sender and worker recover independently.                                              | Caller needs the final decision now, or multiple independent consumers each need the same fact.                      | Duplicate delivery, poison messages, growing backlog, or a false belief that enqueueing equals completion.                        | “Who owns the command, and how will we report its eventual outcome?”             |
| **Publish-subscribe business event** | A committed fact should trigger independent reactions, such as fulfillment, notification, and analytics.                                             | One recipient is obligated to execute a requested action, or old events must be replayed without a retained history. | A subscriber misses delivery, interprets an event as a command, or depends on undocumented fields.                                | “What fact has already happened, and which service is authoritative for it?”     |
| **Retained event streaming**         | Several consumers need independent positions, high sustained volume, or bounded replay to rebuild projections.                                       | A simple one-worker job, an immediate transaction result, or a use case with no justified retention and replay need. | Retention expires before recovery; partitioning breaks expected order; replay repeats external side effects.                      | “Who needs replay, for how long, and what is the ordering key?”                  |
| **Batch/ETL**                        | Large datasets, transformations, historical loads, or freshness measured by a processing window.                                                     | Per-order decisions or continuous propagation with a tight freshness limit.                                          | Partial loads, overlapping runs, stale data, or a success signal that ignores rejected rows.                                      | “What is the allowable staleness, and how is each load reconciled?”              |
| **CDC**                              | Incremental replication from a database whose application cannot expose the needed change feed, or capture of an outbox table.                       | A stable, intention-rich business contract when only table mutations are available.                                  | Schema changes leak into consumers; a row update is mistaken for a business milestone; snapshots and live changes are mishandled. | “Are consumers entitled to database structure, or do they need a business fact?” |
| **File/SFTP/EDI exchange**           | A partner or legacy contract specifies scheduled files or structured interchanges; large bounded transfers need explicit receipt and reconciliation. | Interactive validation or low-latency, record-by-record decisions.                                                   | Partial files, duplicate pickup, missing acknowledgments, rejected records, or mismatched versions.                               | “What constitutes a complete handoff and accepted business processing?”          |

The matrix describes *fit*, not guaranteed behavior. For example, a queue does not automatically preserve useful
business order under concurrent consumption and retries. RabbitMQ’s queue documentation explicitly notes that requeueing
and consumer configuration can affect observed order. [RabbitMQ queues](https://www.rabbitmq.com/docs/queues)

## Distinctions interviewers expect

**Queue versus topic.** A queue is a work destination: competing workers normally share its workload, and each work item
should be handled by one logical consumer. A topic is a distribution address or named stream: multiple independent
subscribers may each need the same publication. Implementations vary. In an AMQP-style broker, an exchange can route a
publication to several queues; each subscriber can have its own queue. In a retained log, consumer groups can read the
same topic at independent positions. The decisive question is whether this is *one obligation* or *one fact with several
interested
parties*. [RabbitMQ exchanges](https://www.rabbitmq.com/docs/exchanges); [Apache Kafka consumer groups](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)

**Pub/sub versus event streaming.** Pub/sub describes the relationship between publisher and subscribers. It does not,
by itself, promise retained history. A broker may fan out an event and remove each subscriber’s copy after
acknowledgment. Event streaming adds a retained, ordered log and independent consumer positions, allowing replay while
records remain available. Retention is finite unless deliberately configured otherwise; replay also requires consumers
whose side effects can safely run again. Current Kafka documentation describes time- and size-based retention, while its
design documentation qualifies delivery guarantees at external
destinations. [Apache Kafka topic retention](https://kafka.apache.org/44/configuration/topic-configs/); [Apache Kafka delivery semantics](https://kafka.apache.org/41/design/design/)

**CDC versus a business event.** CDC reports a data change, such as an inserted or updated row. A business event reports
a domain fact, such as `OrderAccepted`, with meaning chosen by the owning service. A row changing to `status=2` does not
necessarily reveal whether an order was accepted, corrected, migrated, or replayed. CDC can be valuable for replication
and for carrying an outbox record, but exposing raw tables as an enterprise contract couples consumers to internal
storage. Debezium documents both row-level change capture and an outbox approach that connects committed application
state to published
events. [Debezium CDC](https://debezium.io/documentation/reference/stable/index.html); [Debezium outbox pattern](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html)

**File handoff versus API.** A file exchange transfers an artifact for later pickup or processing, commonly with a
cutoff, manifest, receipt, and reconciliation. An API exposes an operation with a request and response; the response can
be immediate even if processing is deferred. Sending a file over HTTP does not make it an interactive API, and offering
an upload endpoint does not remove batch semantics. EDI also describes structured business documents, not one required
transport: the AS2 standard, for example, specifies exchanging EDI or other structured data over HTTP with receipt
mechanisms. [RFC 4130](https://www.rfc-editor.org/rfc/rfc4130.html)

## Test the trade-offs before selecting

**Response and freshness.** Separate “the caller needs acknowledgment” from “the caller needs the final business
result.” A durable acceptance can be immediate while fulfillment is eventual, provided the contract names that
distinction. Define freshness in measurable terms: maximum age of a read model, maximum time until ERP receipt, or
deadline for a partner load. Avoid calling any asynchronous path “real time” without a bound.

**Throughput and backpressure.** A synchronous dependency consumes caller time and capacity while it works. A queue
absorbs bursts only until its storage or recovery window is exhausted; backlog is deferred work, not free capacity.
Streaming supports independent consumers and sustained feeds but adds retention, partition, lag, and replay decisions.
Batch amortizes per-record overhead yet concentrates load at cutoffs. Ask for peak arrival rate, payload size,
processing rate, and recovery time after an outage before sizing any path.

**Coupling and ownership.** An API couples a caller to an endpoint’s availability and response contract. A command still
couples the sender to the receiving capability’s meaning, even when delivery is asynchronous. A business event reduces
knowledge of subscribers, but consumers still depend on its semantics and schema. Raw CDC often couples consumers most
tightly to the owner’s database. For every copy, name the system of record and whether the copy is a cache, projection,
analytical dataset, or independent business record.

**Ordering and guarantees.** Specify the narrowest ordering that matters, usually per order or account. Global order
restricts parallelism and is seldom a business requirement. Distinguish producer acknowledgment, broker durability,
consumer acknowledgment, and the downstream business commit. Under retries, design for duplicates with stable
identifiers and idempotent effects. “Exactly once” is a claim about a defined boundary, not an end-to-end property of
any transport. Kafka’s documentation, for example, says an external destination must cooperate to coordinate consumed
position with stored output. [Apache Kafka delivery semantics](https://kafka.apache.org/41/design/design/)

**Operations.** Every asynchronous design needs a policy for lag, retries, dead letters or quarantine, alerting, repair,
and reconciliation. Every synchronous design needs timeouts and a way to resolve an ambiguous outcome. Every batch or
file design needs run identity, completeness checks, reject handling, and restart rules. Choose the least complex
pattern that meets the business promise under the required failure conditions.

## Three worked choices

### 1. Order submission requires immediate validation

**Assumption:** An order service owns the rules for accepting an order and can validate and commit an acceptance
decision within the caller’s deadline. ERP posting and other downstream work are separate. If ERP itself owns
acceptance, this assumption is false.

**Choice:** Submit the order through a synchronous API to the order owner. Validate the required fields and business
rules, commit the order with a stable order ID, and return a clear accepted or rejected result. Use a client-supplied
idempotency key or another defined duplicate-detection rule so a timeout followed by retry does not create two orders.
Publish an `OrderAccepted` event after the commit, ideally through a transactionally written outbox, for downstream
consumers.

**Alternative: queue the submission and return immediately.** This handles bursts and a temporarily unavailable worker,
but the caller receives only “queued,” not the required validation result. It is a good choice only if the business can
change the promise to pending acceptance and provide a status lookup or later notification. An HTTP `202` is suitable
for that narrower promise; it must not be presented as a completed
order. [RFC 9110, §15.3.3](https://www.rfc-editor.org/rfc/rfc9110.html#name-202-accepted)

**Alternative: call the ERP synchronously.** Choose this if ERP must authorize the order or allocate inventory before
acceptance. Otherwise, it makes the user-facing decision depend on a downstream outage and increases latency. State
which checks truly belong in the immediate decision; do not move authoritative rules into the order service merely to
improve availability.

**Defensible interview answer:** “I would first establish who can authoritatively accept an order. Under the stated
assumption, I use a synchronous API for that decision and make retries safe. I decouple subsequent ERP posting with an
event or queued command. The response promises an accepted order, not completed ERP processing.”

### 2. Downstream order propagation must survive ERP outages

**Assumption:** The order service has already accepted the order, ERP integration may be unavailable for hours, and the
business permits delayed ERP posting. Each accepted order must eventually be posted or visibly escalated.

**Choice:** Persist the accepted order and an outbound intent together. An ERP adapter consumes a durable **command
queue** such as `PostOrderToERP`, retries recoverable failures with controlled backoff, and records the ERP reference or
a terminal failure. Key the command by order ID; make the ERP write idempotent where the interface permits, or maintain
a deduplication record. Track oldest backlog age, failed attempts, and reconciliation between accepted orders and ERP
postings. The order service remains the source of accepted-order state; the ERP owns its own posting state.

**Alternative: synchronous ERP API call on submission.** It gives immediate ERP confirmation when healthy, but makes an
ERP outage an order-submission outage. Use it only if ERP confirmation is part of the business acceptance promise.

**Alternative: publish `OrderAccepted` to a shared event topic and let ERP subscribe.** This is appropriate if the ERP
adapter is one of several independent consumers of that committed fact. The adapter still needs its own durable work
state, retry policy, and reconciliation. A topic alone does not establish who is responsible for the ERP posting. A
retained stream is worth its extra machinery if replay and multiple independently positioned consumers are requirements;
it is not required merely because the ERP can go down. Pub/sub is designed to deliver a publication to multiple
interested consumers without requiring an immediate
response. [AWS publish-subscribe pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/publish-subscribe.html)

**Defensible interview answer:** “The business needs order acceptance to survive ERP downtime, so I separate those
transactions. I queue an explicit ERP posting obligation, make retries and duplicates safe, and measure backlog against
an agreed delay limit. I may also publish `OrderAccepted` for other consumers, but I do not rely on an unowned event
subscription as the sole record of the ERP obligation.”

### 3. Overnight partner data exchange

**Assumption:** The partner accepts a daily dataset, has an agreed cutoff and file or EDI contract, and does not require
record-level responses during the day. The required data is available by the cutoff. The exact format and transport must
be confirmed with the partner.

**Choice:** Generate a bounded export and hand it off using the agreed file/SFTP or EDI route. Give each run a unique
identifier and defined business date. Produce a manifest with record count and integrity check, make the complete
artifact visible only after generation finishes, and retain a copy for resend. Record transport receipt separately from
business acceptance. Reconcile the partner’s accepted and rejected records against the export; reruns must specify
whether they replace or supplement an earlier run.

**Alternative: per-record API calls overnight.** An API can work if the partner offers one and needs individual
transactions, but thousands of calls create retry, rate, and partial-completion questions without improving freshness
when the partner processes only once a day. A bulk upload API may be a valid transport while retaining the same batch
control model.

**Alternative: stream each change throughout the day.** Choose this if the partner can consume continuously and the
freshness requirement justifies it. Otherwise, streaming adds an always-on contract, replay policy, and partner
operating burden without changing the overnight business outcome.

**Defensible interview answer:** “I would honor the partner’s actual exchange contract. For a nightly dataset, the
architecture centers on completeness, receipt, rejection, and reconciliation. I would only replace it with an API or
stream after confirming a business need for fresher or interactive processing.”

## Hybrid designs with clear state

Patterns commonly coexist because they solve different stages of one workflow. An API can decide an order; an outbox can
reliably expose the committed fact; a pub/sub route can fan it out; a queue can hold an ERP adapter’s work; CDC can
populate an analytical replica; and a nightly file can satisfy a partner. This is coherent if each boundary has one
named meaning.

Document the ownership ledger: **order service** owns order acceptance; **ERP** owns ERP posting; **reporting store**
owns a rebuildable projection; **partner** owns its processing result. Record the transition that creates each
obligation. The order commit must not be considered atomic with ERP posting or partner receipt unless a real shared
transaction exists. When that is unavailable, use stable IDs, explicit states, and reconciliation.

Do not emit a business event before its fact is committed. A transactional outbox makes the event record part of the
same local commit as business state, reducing the risk that the database says “accepted” while the event is never
published. It does not make subscriber processing atomic with that
commit. [Debezium outbox pattern](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html)

## Interview questions, answers, and counterarguments

**Q: “We have microservices. Should we use Kafka?”**  
**Strong answer:** “Microservices do not establish a replay, retention, throughput, or multi-consumer requirement. I
would identify the business interaction first. A synchronous API may be right for an immediate decision; a queue may be
right for one delayed obligation; pub/sub may be right for independent reactions. I would select retained streaming when
consumers need independent positions or replay within a defined retention period, and I would budget for lag, schemas,
partition keys, and replay-safe effects.”  
**Counterargument:** “A shared stream could simplify future consumers.” That may be true if future consumers and history
needs are credible. Speculative flexibility alone is weak justification for operating a retained log.

**Q: “Why not just add a queue?”**  
**Strong answer:** “What failure or load condition does it solve? If the caller must know the final result now, a queue
moves the decision after the response. If the receiver is a single owner and delayed work is acceptable, a queue can
absorb an outage or burst. I would define the acceptance state, backlog limit, retry policy, and eventual-result
channel.”  
**Counterargument:** “Queues always improve resilience.” They improve one form of isolation while adding delayed
failure, duplicate handling, and backlog risk. Resilience must be measured against the business deadline.

**Q: “Can we guarantee exactly once?”**  
**Strong answer:** “I would ask: exactly once *where*? A broker may deduplicate publication or transactionally process
within its own boundary, but an external ERP write and consumer position must still be coordinated. I would plan for
redelivery, use stable IDs and idempotent business effects, and reconcile outcomes.”  
**Counterargument:** “The platform advertises exactly-once processing.” That can be valid within its documented scope;
it does not settle the end-to-end business
effect. [Apache Kafka delivery semantics](https://kafka.apache.org/41/design/design/)

**Q: “Why publish a business event if CDC already exposes the table?”**  
**Strong answer:** “CDC is useful for moving changes, but the table records storage operations. Consumers need to know
whether an authoritative business transition occurred. If the owner can publish that transition, I prefer a versioned
business event. If it cannot, I would document CDC as a coupling to the source schema and translate it at a controlled
boundary.”  
**Counterargument:** “CDC avoids application changes.” Correct; that may outweigh semantic purity for a legacy source.
The cost is ongoing interpretation and schema coordination.

## Self-check quiz

1. A caller must know whether an order is valid before showing confirmation. What must the response represent?
2. One ERP adapter must process every accepted order, but ERP may be offline for hours. Queue, topic, or API alone?
3. Two teams need to rebuild independent projections from six months of changes. What capability drives the pattern?
4. A database row changes from `status=1` to `status=2`. Is that automatically an `OrderAccepted` event?
5. A partner confirms file receipt but later rejects 4% of records. Has the exchange succeeded?
6. When does an HTTP `202` mean the business action is complete?

**Answer key:** (1) An authoritative acceptance or rejection by the owning capability, under a stated response deadline.
(2) A durable queued obligation for the ERP adapter, with outcome tracking; an event may coexist for other consumers.
(3) Retained history, independent positions, and replay for a defined period. (4) No; the owning business semantics must
establish what transition occurred. (5) Transport receipt succeeded, while business processing is partial and requires
reconciliation. (6) It does not: `202` means the request was accepted for processing, which may finish or fail
later. [RFC 9110, §15.3.3](https://www.rfc-editor.org/rfc/rfc9110.html#name-202-accepted)

**Interview rule to remember:** Name the business promise, the owner, the deadline, and the failure behavior first.
Select the integration pattern that can keep that promise.