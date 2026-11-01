Extend the attached learning plan to cover Apache Iceberg.

Apply its teaching rules, communication style, default technology stack, Mac portability requirements, source
verification, and interview phrasing requirements.

Treat me as a beginner. Do not begin with a knowledge assessment.

For this session, create the learning cards only. Do not start teaching yet.

First identify the required prerequisites. Reuse relevant concepts from B03 and T05. Add short prerequisite lessons for
concepts that the existing plan does not cover.

Create a sequence of small cards covering:

1. Data foundations: analytical workloads, data lakes, object storage, and column-oriented files.
2. Why Iceberg exists: the problems it addresses and when it is useful.
3. Table structure: data files, metadata, snapshots, and catalogs.
4. Reading and writing: how a table changes and how simultaneous writes are handled.
5. Table evolution: changing columns and data partitioning.
6. Historical reads and recovery: snapshots, time travel, and rollback.
7. Python practice using PyIceberg.
8. Operations: maintenance, performance, monitoring, security, and cost.
9. Architecture decisions: integration, alternatives, limitations, and failure cases.
10. Interview preparation: explanations, design questions, and follow-up challenges.

Define every technical term when teaching it.

For each card, include:

- A unique ID, such as ICE01.
- Prerequisites.
- An explicit subtopic checklist.
- Small lessons suitable for separate chats.
- A worked example and a guided exercise.
- An “Interview phrasing” example.
- A completion check.
- Official sources.

Verify version-specific features and commands. Distinguish Iceberg concepts from features supported by a particular tool
or version. Explain why each additional tool is needed before introducing it.

Finish by showing exactly which card I should start with and what I should paste into that learning chat.

> Note: For the Python exercises, PyIceberg is a Python implementation for accessing Iceberg tables. Its official
> guide includes a local practice setup. The tutor should verify the chosen setup for both Macs before giving
> installation commands. PyIceberg documentation.