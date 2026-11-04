# Design 5 — Real-Time Fraud Detection System

## Stream Processor

A stream processor is a program that continuously reads incoming events,
processes them in near real time, and produces updated results.

In your fraud detection example, it calculates recent card activity as new
transactions arrive.

### How it works

```
Transaction Events
        |
        v
      Kafka
        |
        v
  Stream Processor
        |
        |-- Count attempts in last 1 minute
        |
        |-- Sum amounts in last 5 minutes
        |
        |-- Count declines in last 10 minutes
        |
        v
 Online Feature Store
        |
        v
 Fraud Detection Service
```

#### Example

Suppose card `C123` makes these transactions:

| Time     | Amount | Status   |
|----------|--------|----------|
| 10:00:05 | $100   | Approved |
| 10:00:12 | $200   | Declined |
| 10:00:20 | $150   | Declined |
| 10:00:35 | $300   | Approved |
| 10:00:50 | $500   | Declined |

At 10:00:50, the stream processor can calculate:

- Attempts in last 1 minute: 5
- Total amount in last 5 minutes: $1,250
- Declines in last 10 minutes: 3

It updates these values as new events arrive.

The fraud detection service can then use them to calculate a fraud risk score.

### Kafka vs. Stream Processor

| Kafka                                | Stream Processor                                |
|--------------------------------------|-------------------------------------------------|
| Stores and delivers events           | Reads and processes events                      |
| Acts as an event transport and log   | Performs calculations and aggregations          |
| Example: Receives transaction events | Example: Counts transactions in the last minute |

### Is a stream processor a separate technology?

Yes. You can use different technologies to implement stream processing, such as:

- Apache Flink
- Kafka Streams
- Spark Structured Streaming

Kafka Streams is a library that runs inside your application. Flink is a
separate stream processing engine.

Key takeaway: Kafka delivers the transaction events. The stream processor turns
those events into continuously updated information that the fraud service can
use.

Source: [Apache Kafka official Streams documentation](https://kafka.apache.org/44/streams/?utm_source=chatgpt.com)

## Online Feature Store

An online feature store is a database optimized to store and retrieve the latest
machine learning features in real time, often in milliseconds.

It is optimized for low-latency reads and writes.

In your fraud detection system, it stores the latest calculated activity for
each card so the fraud service can make real-time decisions.

### 1. How it works

```
Transaction Events
        |
        v
      Kafka
        |
        v
 Stream Processor
 (Calculates features)
        |
        v
 Online Feature Store
 (Stores latest values)
        |
        v
 Fraud Detection Service
 (Reads features quickly)
        |
        v
   Fraud ML Model
```

### 2. Example

The stream processor calculates these features for card `C123`:

| Feature                        | Current value |
|--------------------------------|---------------|
| Card ID                        | C123          |
| Attempts in last 1 minute      | 5             |
| Total amount in last 5 minutes | $1,250        |
| Declines in last 10 minutes    | 3             |

The online feature store keeps these values.

When a new transaction arrives, the fraud detection service can request:

`Get features for card C123`

The store returns the latest values without requiring the fraud service to
calculate them from raw transactions.

### 3. Why not just use Kafka?

Because Kafka and the online feature store have different responsibilities.

| Kafka                              | Online Feature Store                   |
|------------------------------------|----------------------------------------|
| Stores transaction events in a log | Stores calculated feature values       |
| Supports consuming event streams   | Supports fast lookups by card ID       |
| Allows event replay                | Provides the latest available features |
| Example: Transaction of $200       | Example: 5 attempts in 1 minute        |

### 4. Online vs. Offline Feature Store

| Online Feature Store  | Offline Feature Store       |
|-----------------------|-----------------------------|
| Real-time predictions | Model training and analysis |
| Latest feature values | Historical feature values   |
| Low-latency lookups   | Large historical queries    |

These roles are described in the
official [AWS SageMaker Feature Store documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store.html?utm_source=chatgpt.com)

### 5. Is an online feature store a separate technology?

Not necessarily. It is an architectural component that can be implemented using:

- Redis as a low-latency storage backend
- Feast as a feature store system
- Amazon SageMaker Feature Store as a managed service

**Key distinction:**

- **Kafka:** What transactions happened?
- **Stream Processor:** What do these transactions mean right now?
- **Online Feature Store:** What are the latest calculated values for this card?
- **Fraud Service:** Is this transaction suspicious?

**One important detail:** an online feature store does not automatically
calculate features or guarantee they are current. The stream processor must
update them, and processing delays can make stored values stale.

## Are Redis and Feast both required?

You can use Redis alone or Redis together with Feast.

They serve different purposes.

|              | Redis                             | Feast                                 |
|--------------|-----------------------------------|---------------------------------------|
| What is it?  | Fast key-value database           | Feature store framework               |
| Main job     | Store and retrieve feature values | Manage, define, and serve ML features |
| Stores data? | Yes                               | Uses a database such as Redis         |
| Required?    | No, other databases can be used   | No, it is optional                    |

### Option 1: Redis only

```
Kafka
  |
  v
Stream Processor
  |
  v
Redis
  |
  v
Fraud Detection Service
```

Your stream processor writes calculated features directly into Redis.

Your fraud service reads them directly from Redis.

This is a valid online feature storage architecture.

### Option 2: Feast + Redis

```
Kafka
  |
  v
Stream Processor
  |
  v
Feast ingestion integration
  |
  v
Redis (Online Storage)
  |
  v
Feast Feature Server / SDK
  |
  v
Fraud Detection Service
```

Here:

- Redis stores the actual feature values.
- Feast defines features, manages their metadata, and provides standardized
  retrieval APIs.
- Your stream processor still calculates the rolling transaction features.

Feast supports Redis as one of several online database backends.

### Which should you choose?

For your fraud detection example:

- **Simple system:** Redis alone can be sufficient.
- **Larger ML platform:** Feast + Redis may help when multiple models and teams
  share features and need consistent feature definitions.

**Remember:**

- Redis is the storage engine.
- Feast is the feature management layer.
-

Feast does not require Redis specifically;
it also supports other online stores such as DynamoDB and SQLite.

**Official documentation:**
[Feast Online Stores](https://docs.feast.dev/reference/online-stores?utm_source=chatgpt.com).

## Does stream processor guarantee that features are always up to date?

A stream processor is good for calculating recent activity, but it cannot
guarantee that a transaction limit is never exceeded.

This is because stream processing is asynchronous. The fraud service might
receive a new transaction before the stream processor has updated the counter.

### 1. Example: Maximum 5 attempts per minute

Suppose your business rule is:

Allow at most 5 purchase attempts per card in any rolling 60-second period.
Reject the 6th attempt.

Your architecture is:

```
Transaction
     |
     v
   Kafka
     |
     v
Stream Processor
     |
     v
Redis (Counter)
     |
     v
Fraud Service reads counter
```

Imagine the following sequence:

| Time     | Actual attempts | Redis counter |
|----------|-----------------|---------------|
| 10:00:01 | 1               | 1             |
| 10:00:10 | 2               | 2             |
| 10:00:20 | 3               | 3             |
| 10:00:30 | 4               | 4             |
| 10:00:40 | 5               | 4             |
| 10:00:41 | 6               | 4             |

At 10:00:41:

- There have actually been 6 attempts.
- Redis still says 4 attempts.
- The stream processor has not processed the latest events.
- The fraud service might incorrectly allow the 6th attempt.

This is called **stale data**.

The important distinction is that the stream processor may eventually calculate
the correct value of 6, but that update arrives too late to prevent the 6th
attempt.

### 2. Solution: Atomic counting

Instead of waiting for Kafka, check and update the limit synchronously before
allowing each attempt.

```
New Purchase Attempt
         |
         v
    Fraud Service
         |
         v
 Redis: Atomic Check
 and Update
         |
         v
  Count below 5?
      /       \
    Yes        No
     |          |
 Update       Reject
 counter      attempt
     |
   Allow
```

The check and update must be one atomic operation. That means two simultaneous
requests cannot both see 4 and independently decide they are the 5th attempt.

Redis supports atomic commands and Lua scripts for this purpose.

### 3. Why keep Kafka and the stream processor?

They still serve a different purpose.

| Component                | Responsibility                          |
|--------------------------|-----------------------------------------|
| Redis atomic enforcement | Enforce the strict 5-attempt limit      |
| Kafka                    | Transport and retain transaction events |
| Stream Processor         | Calculate recent fraud features         |
| Online Feature Store     | Serve features for fraud scoring        |
| Fraud ML Model           | Estimate fraud risk                     |

**One important detail:** a simple counter with a 60-second expiration does not
necessarily enforce an exact rolling 60-second window. For that, use an atomic
sliding-window algorithm that tracks attempt timestamps. Also define how failed
requests and retries are counted.

See
the [official Redis rate-limiting documentation](https://redis.io/docs/latest/develop/use-cases/rate-limiter/?utm_source=chatgpt.com).

**Bottom line:** Use stream processing to calculate fraud signals. Use
synchronous, authoritative enforcement when the business rule must never allow a
6th attempt.

## What happens if the ML service is down?

The key point is:

A stream processor is good for calculating recent activity, but it cannot
guarantee that a transaction limit is never exceeded.

This is because stream processing is asynchronous. The fraud service might
receive a new transaction before the stream processor has updated the counter.

### 1. Example: Maximum 5 attempts per minute

Suppose your business rule is:

Allow at most 5 purchase attempts per card in any rolling 60-second period.
Reject the 6th attempt.

Your architecture is:

```
Transaction
     |
     v
   Kafka
     |
     v
Stream Processor
     |
     v
Redis (Counter)
     |
     v
Fraud Service reads counter
```

Imagine the following sequence:

| Time     | Actual attempts | Redis counter |
|----------|-----------------|---------------|
| 10:00:01 | 1               | 1             |
| 10:00:10 | 2               | 2             |
| 10:00:20 | 3               | 3             |
| 10:00:30 | 4               | 4             |
| 10:00:40 | 5               | 4             |
| 10:00:41 | 6               | 4             |

At 10:00:41:

- There have actually been 6 attempts.
- Redis still says 4 attempts.
- The stream processor has not processed the latest events.
- The fraud service might incorrectly allow the 6th attempt.

This is called stale data.

The important distinction is that the stream processor may eventually calculate
the correct value of 6, but that update arrives too late to prevent the 6th
attempt.

### 2. Solution: Atomic counting

Instead of waiting for Kafka, check and update the limit synchronously before
allowing each attempt.

```
New Purchase Attempt
         |
         v
    Fraud Service
         |
         v
 Redis: Atomic Check
 and Update
         |
         v
  Count below 5?
      /       \
    Yes        No
     |          |
 Update       Reject
 counter      attempt
     |
   Allow
```

The check and update must be one atomic operation. That means two simultaneous
requests cannot both see 4 and independently decide they are the 5th attempt.

Redis supports atomic commands and Lua scripts for this purpose.&#x20;

### 3. Why keep Kafka and the stream processor?

They still serve a different purpose.

| Component                | Responsibility                          |
|--------------------------|-----------------------------------------|
| Redis atomic enforcement | Enforce the strict 5-attempt limit      |
| Kafka                    | Transport and retain transaction events |
| Stream Processor         | Calculate recent fraud features         |
| Online Feature Store     | Serve features for fraud scoring        |
| Fraud ML Model           | Estimate fraud risk                     |

One important detail: a simple counter with a 60-second expiration does not
necessarily enforce an exact rolling 60-second window. For that, use an atomic
sliding-window algorithm that tracks attempt timestamps. Also define how failed
requests and retries are counted.

See
the [official Redis rate-limiting documentation](https://redis.io/docs/latest/develop/use-cases/rate-limiter/?utm_source=chatgpt.com).

Bottom line: Use stream processing to calculate fraud signals. Use synchronous,
authoritative enforcement when the business rule must never allow a 6th attempt.