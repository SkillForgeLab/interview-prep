# Interview Preparation: Four AI and MCP projects

This guide helps you explain four AI and MCP projects in an interview. It is based on the source code in all four
project ZIP files, not only on the README files.

The focus is on:

- solution architecture and engineering decisions,
- AI governance and security,
- system integration.

For each project, you will find the same parts:

1. The main skill and the key message.
2. A 60-second explanation to say aloud.
3. An architecture diagram.
4. Technical points, with the code that proves them.
5. Likely interview questions, from basic to deep.
6. Limitations, and how to describe them correctly.

---

## 1. The common story across all four projects

Do not present these as four separate applications. Present them as four connected areas of learning.

**Travel Planner MCP:** AI orchestration, separation of duties, service integration, and agent guardrails.

**CodeGuard:** AI-assisted engineering governance, evidence collection, and output validation.

**MCP Studio:** Protocol-level integration, Streamable HTTP, and asynchronous communication.

**ADK Calendar Assistant:** Agent development, enterprise identity integration, and delegated authorization.

**Closing statement to connect the projects:**

> These projects helped me explore different parts of responsible AI integration in an enterprise.
>
> Travel Planner focused on keeping AI decisions separate from controlled execution. CodeGuard focused on using
> reliable, tool-based evidence to support AI decisions. MCP Studio helped me understand communication protocols and
> streaming. The Calendar Assistant focused on identity, delegated access, and conversation state.
>
> In all four projects, I followed one main principle: AI reasoning stays separate from authentication, authorization,
> validation, and service execution.

---

## 2. Key terms

Each term is also explained briefly the first time it appears in a project.

**MCP (Model Context Protocol):** A standard protocol that lets an AI application discover and call tools and data
sources on separate servers.

**POC (proof of concept):** A small working version that tests an idea. It is not ready for production.

**Deterministic:**
Always gives the same output for the same input. Normal code is deterministic. LLM output is not; it is probabilistic.

**ReAct:**
An agent pattern: Reason → Act → Observe, repeated. The model decides on a step, the system runs it, and the result is
used for the next decision.

**JSON-RPC:**
A simple protocol for calling a remote method by name, with parameters, using JSON messages.

**stdio:**
Standard input and output. Here, the gateway starts each MCP server as a local process and talks to it through stdio.

**Pydantic:**
A Python library that checks that data has the expected fields and types.

**JSON Schema:**
A formal description of the expected structure of a JSON document. Code can check a document against it.

**Tree-sitter:**
A parser that turns source code into a syntax tree. Code can then read functions, parameters, and structure from the
tree.

**OSV (Open Source Vulnerabilities):**
A public database of known security vulnerabilities in open-source packages.

**Entropy:**
A measure of how random a string looks. Secrets such as API keys usually have high entropy.

**ASGI:**
The standard interface between Python web servers and async web applications such as FastAPI.

**Middleware:**
Code that sits between the server and the application and can inspect or change each request.

**Streamable HTTP:**
An MCP transport that sends protocol messages over HTTP. It can stream several messages in one response.

**SSE (Server-Sent Events):**
A standard way for a server to send a stream of events to a client over one HTTP response, using the `text/event-stream`
format.

**ADK (Agent Development Kit):**
Google's framework for building AI agents with tools and conversation sessions.

**OIDC (OpenID Connect):**
A standard sign-in protocol built on OAuth. Microsoft Entra ID uses it to prove who the user is.

**OAuth (delegated access):**
A standard that lets a user allow an application to access their data in another service, such as Google Calendar,
without sharing their password.

**PKCE:**
An extra OAuth security step. It stops an attacker from using a stolen authorization code.

**Scope:**
The exact permission an OAuth token grants, for example `calendar.readonly`.

**Sentinel:**
A special return value that signals a condition. Here, it means "authentication is required".

**Least privilege:**
Give a component only the permissions it needs, and nothing more.

---

## 3. Travel Planner MCP

**Main skill:**
AI agent architecture. This is the strongest project for this topic.

**Key message:**
An LLM should suggest actions. Services that the application controls should check and run them.

### 60-second explanation

I built a proof of concept for a travel planning agent. I wanted to see how an LLM can coordinate several services
without direct access to how they work.

I split the workflow into four logical roles: Planner, Critic, Executor, and Summarizer. The Planner chooses the next
action. The Critic reviews it. The Executor prepares the tool arguments. The Summarizer writes the final answer, based
on the collected evidence.

The orchestrator sends requests to a FastAPI gateway using JSON-RPC. The gateway checks that each request is allowed.
Then it sends the request to the correct MCP server: calendar, weather, or travel.

I also added Pydantic response contracts, tool authorization, a step limit, timeouts, evidence tracking, and logs linked
by a shared request ID.

My main goal was to keep AI reasoning, which is unpredictable, separate from service execution and authorization, which
must be predictable.

### Architecture

```text
             User Request
                  |
           ReAct Orchestrator
                  |
             Planner (LLM)
                  |
             Critic (LLM)
                  |
            Executor (LLM)
                  |
            FastAPI Gateway
            JSON-RPC over HTTP
                  |
            Catalog + Policy
                  |
               MCP Router
                  |
            MCP stdio clients
                  |
      +-----------+-----------+
      |           |           |
   Calendar    Weather      Travel
   Resource      Tool        Tool
      |           |           |
      +-----------+-----------+
                  |
             Evidence Store
                  |
            Summarizer (LLM)
                  |
              Final Answer
```

### Technical points and code evidence

**ReAct loop with a step limit:**
`src/orchestrator/react_loop.py` — `run_react_loop()`, `max_steps=8`

**Four role-based LLM calls:**
`src/orchestrator/reasoning_adapter.py` — `plan_next_step()`, `review_step()`, `build_tool_args()`, `summarize()`

**Structured AI outputs:**
`src/orchestrator/schemas.py` — `NextStep`, `CriticDecision`, `ToolArgs`, `FinalAnswer`

**Catalog authorization:**
`src/gateway/catalog.py` and `src/gateway/policy.py`

**MCP service isolation:**
`src/gateway/mcp_router.py` — `ClientSession`, `stdio_client`

**Timeouts:**
`src/gateway/mcp_router.py` — `asyncio.wait_for()`

**Correlated logging (logs linked by request ID):**
`src/shared/logging.py`, `src/orchestrator/react_loop.py`

**Evidence tracking:**
`src/orchestrator/memory.py` — `EvidenceStore`

### Likely interview questions

**Question: How does ReAct work in this project?**

The loop follows Reason → Act → Observe. The Planner chooses an action. The system runs it through the gateway. The
result is stored as evidence for the next step.

Today, the code follows a fixed order: calendar → weather → travel → finish. It is not fully open-ended planning.

**Question: Why did you create four roles instead of one AI agent?**

I wanted each role to have one clear responsibility. Planning, reviewing, preparing tool arguments, and summarizing have
different needs. Separate prompts and output contracts make each step easier to inspect and test.

However, these are four logical roles that use the same reasoning adapter. They are not four separately deployed agents.

**Question: Why put a gateway between the LLM and the MCP servers?**

The gateway is a controlled boundary. It accepts JSON-RPC requests, checks the parameters, checks the catalog, finds the
right domain, and then runs the call through an MCP session. The LLM cannot choose any server process it wants.

**Question: How did you prevent hallucinated tool calls?**

I gave the Planner the list of allowed tools, and I limited its output with Pydantic models. More importantly, the
gateway rejects unknown tool names on its own. Checking the model output and authorizing the call are two separate
controls.

### Limitations

- Calendar, weather, and flight responses are fixed, simulated data. They are not live bookings or forecasts.
- The Critic is an LLM. The predictable control is the gateway authorization.
- The policy checks a static catalog. It does not apply permissions per tenant.
- Evidence is stored in memory only while the workflow runs.
- The gateway exposes its own JSON-RPC methods, such as `tools.call`. The router uses the MCP SDK internally.

**Avoid saying:**

"A fully autonomous multi-agent system." Or: "Production-grade tenant security."

**Say instead:**

"A role-separated ReAct workflow with a fixed execution order." And: "A catalog authorization prototype; per-tenant
controls are future work."

---

## 4. CodeGuard Code Review Assistant

**Main skill:**
Governance of AI-assisted engineering. This is the strongest project for this topic.

**Key message:**
Use predictable tools to collect evidence. Use AI to help interpret it. Keep a clear validation step and a human review
step.

### 60-second explanation

I built a Python proof of concept for AI-assisted code review. It combines reliable, tool-based data collection with
LLM-based risk interpretation.

The system compares two Git revisions. It parses Python code with Tree-sitter. It looks for possible hardcoded secrets
with regular expressions. It also checks Python dependencies against the OSV vulnerability database.

The system does not send raw source code to the LLM. Instead, it builds structured metadata: complexity metrics, risk
indicators, secret findings, and vulnerability data.

The triage step uses either OpenAI or Claude to write an assessment. The output is checked against a JSON Schema. If it
is invalid, the system retries. Then it produces JSON and Markdown reports.

The key design decision was this: the LLM interprets evidence that was already collected. It does not have to find every
issue in raw code by itself.

### Architecture

```text
         Repository + Git SHAs
                  |
          Metadata Extraction
                  |
     +------------+------------+
     |            |            |
  Git Diff    Tree-sitter   Regex Secrets
     |            |            |
     |        Complexity       |
     |          Metrics        |
     |            |            |
     +------------+------------+
                  |
          Dependency Scanner
                  |
                OSV API
                  |
          Structured Metadata
                  |
           OpenAI OR Claude
                  |
           JSON Assessment
                  |
        JSON Schema Validation
             /          \
          Valid        Invalid
            |             |
            |           Retry
            |
       Markdown Report
```

### Technical points and code evidence

**Three-stage review pipeline:**
`src/run.py` — `run_pipeline()`

**Git revision comparison:**
`extract_structure.py` and `extract_secrets.py` — `get_diff_files()`

**Tree-sitter analysis:**
`src/extractors/extract_structure.py`

**Cyclomatic complexity and nesting depth:**
`calculate_cyclomatic_complexity()`, `calculate_nesting_depth()`

**Redacted secret findings:**
`src/extractors/extract_secrets.py` — `scan_file_for_secrets()`

**Dependency vulnerability lookup:**
`src/extractors/extract_dependencies.py` — `query_osv_api()`

**Alternative LLM providers:**
`src/llm/triage_agent.py`, `triage_agent_openai.py`

**Validation and retry:**
`src/validators/validate_schema.py`, `assess_risk()`

**Evidence-based reports:**
`src/reporters/generate_report.py`

### Likely interview questions

**Question 1: Does the system use OpenAI and Claude together?**

No. The command-line tool selects one provider for each run. The two adapters are alternative implementations of the
same triage step. There is no voting or agreement between models.

**Question 2: Why use Tree-sitter instead of asking an LLM to review all the code?**

Tree-sitter gives the same structural facts every time: function boundaries, parameters, complexity, and nesting depth.
So the system does not depend on the LLM for facts that normal code can extract.

**Question 3: How did you reduce the exposure of sensitive source code?**

The pipeline sends only derived metadata to the LLM. For secrets, it records the finding ID, file location, secret type,
entropy, and confidence. It does not record the secret value itself.

So the design sends as little data as possible. But file paths and other metadata can still be sensitive.

**Question 4: Why use JSON Schema validation and retries?**

LLM responses are not always valid application data. The code parses the assessment and checks it against a defined
schema. If parsing or validation fails, it retries and includes the error in the new prompt.

This checks the structure only. It does not prove that every risk claim is true.

**Question 5: How do security findings become merge recommendations?**

The LLM produces risk levels, findings, recommendations, and an `allow_merge` result. It uses the extracted metadata and
the rules in the prompt. This is only advice. It is not a merge gate that CI/CD enforces.

### Limitations

The implementation is a Python-focused proof of concept.

- Git diff analysis finds the changed files. It does not analyze only the changed lines.
- Tree-sitter scans the Python files in the working tree.
- The dependency scanner reads `requirements.txt` and checks direct dependencies only.

**Avoid saying:**

"A complete automated secure code review." Or: "Both LLMs assess the risks together."

**Say instead:**

"An AI-assisted, metadata-based risk assessment POC." And: "Selectable OpenAI or Claude triage adapters."

### Fix before the demo

I found two code issues. Fix them before you show the project live.

**API key printed to the output:**

`src/llm/triage_agent_openai.py`, line 49, prints the raw OpenAI API key. This is a security issue. Remove that line,
and rotate any key that may have reached the logs.

**Wrong schema path for Claude:**

The Claude adapter uses a schema path that does not match the schema directory of `SchemaValidator`. This can make
Claude validation fail.

---

## 5. MCP Studio

**Main skill:**

MCP protocol and streaming integration.

**Key message:**

Reliable distributed integrations need the protocol design, session management, streaming behavior, and reverse-proxy
settings to work together.

### 60-second explanation

I built MCP Studio to understand the MCP client-server lifecycle and how Streamable HTTP behaves.

The first part shows an MCP client that opens a session, initializes the protocol, discovers tools, and calls tools. The
server is an MCP server hosted in FastAPI.

I also wrote ASGI middleware that prints HTTP headers and request bodies. This makes protocol behavior easier to
troubleshoot.

The second part is about streaming. I wrote one shared async function that generates progress events. I exposed it in
two ways: as MCP progress notifications, and as a standard REST endpoint with Server-Sent Events.

Finally, I ran the services in containers with Docker Compose. I configured Nginx to turn off response buffering, so
progress updates reach clients one by one.

### Architecture

```text
Part 1: Streamable HTTP basics

    MCP client (command line)
               |
       Streamable HTTP
               |
        Request inspector
        (ASGI middleware)
               |
     FastAPI-hosted MCP server
               |
 initialize -> list_tools -> call tool


Part 2: Streaming progress

    MCP client        REST client
         |                 |
         +-----------------+
                  |
                 Nginx
        (buffering disabled)
                  |
             FastAPI server
               |         |
          MCP tool    REST SSE endpoint
       (MCP progress) (text/event-stream)
               |         |
               +---------+
                    |
       Shared async progress generator
```

### Technical points and code evidence

**Stateful MCP HTTP server:**

`streamable_basics/src/mcp_studio/foundation/server.py`

**Session initialization and tool discovery:**

`streamable_basics/src/mcp_studio/foundation/client.py`

**Request inspection:**

`streamable_basics/src/mcp_studio/debug/request_inspector.py`

**Shared async progress generator:**

`streaming_response/server/src/services/number_stream.py`

**MCP progress notifications:**

`streaming_response/server/src/tools/stream_tool.py`

**REST SSE endpoint:**

`streaming_response/server/src/main.py`

**Docker service networking:**

`streaming_response/docker-compose.yaml`

**Streaming proxy configuration:**

`streaming_response/nginx/nginx.conf`

### Likely interview questions

**Question: What happens during MCP initialization?**

The client opens the Streamable HTTP transport and creates a `ClientSession`. It calls `initialize()` and receives the
server information. Then it calls `list_tools()`. Finally, it calls a selected tool with typed arguments. The SDK
handles the protocol lifecycle.

**Question: How is MCP progress different from REST SSE?**

MCP progress is a notification inside the MCP protocol, linked to one MCP operation. In this project, the tool calls
`ctx.report_progress()`. The MCP client receives the updates through a progress callback.

REST SSE is a normal HTTP streaming response. The FastAPI endpoint sends `text/event-stream` frames directly.

Both use the same progress generator. They only expose it through different protocols.

**Question: Why turn off Nginx buffering?**

With buffering, Nginx can hold response chunks before it forwards them. Then the client does not get progress updates
one by one, which is the whole point of streaming.

The Nginx configuration turns off proxy buffering and caching for the MCP and REST paths. It also allows longer read
times for streaming connections.

**Question: What did you learn about ASGI middleware?**

The inspector wraps the ASGI `receive` function. It sees each incoming body chunk, but it does not replace the MCP SDK's
protocol handling. This helps me separate transport-level troubleshooting from MCP application logic.

### Limitations

- The MCP clients are command-line applications. The **servers** are hosted in FastAPI.
- The streaming example sends numbered progress events. It does not stream LLM-generated tokens.
- The request inspector prints raw headers and request bodies. Before production use, it needs redaction and controlled
  logging.
- The code demonstrates protocol behavior. It is not a complete, production MCP security platform.

**Avoid saying:**

"A production-ready MCP platform."

**Say instead:**

"Experiments with MCP protocol and streaming integration."

---

## 6. ADK Calendar Assistant

**Main skill:**

Agent development with enterprise identity and delegated authorization.

**Key message:**

An agent's access to tools should depend on who the user is, what the user allowed, and the smallest permission needed (
least privilege).

### 60-second explanation

I built a read-only calendar assistant with Google's Agent Development Kit (ADK), Gemini, FastAPI, and the Google
Calendar API.

Users can ask in natural language for their upcoming events, or for the events on a specific date.

The interesting part was the identity integration. Sign-in has two stages. First, the user signs in with Microsoft Entra
ID. Second, the user gives the app read-only access to Google Calendar through Google OAuth.

I used an authentication sentinel. This means the agent asks for authentication only when a calendar tool really needs
credentials.

I also added token refresh, in-memory ADK conversation sessions, and a browser chat flow. The browser saves the user's
question before sign-in and sends it again after the user returns.

### Architecture

```text
             Browser Chat
                  |
             FastAPI /chat
                  |
           Google ADK Agent
             Gemini Model
                  |
          Calendar Tool Needed?
             /           \
            No           Yes
            |             |
       Normal Reply   Credentials?
                       /        \
                     Yes         No
                      |           |
                 Calendar API  Auth Required
                                  |
                            Entra ID login
                                  |
                             Google OAuth
                                  |
                            Token Storage
                                  |
                            Browser replays
                            pending question
```

### Technical points and code evidence

**ADK agent powered by Gemini:**

`agent/calendar_agent.py` – `create_calendar_agent()`

**Read-only Google Calendar operations:**

`agent/calendar_tools.py`

**Entra ID OIDC authentication:**

`auth/entra_oidc.py`

**Delegated Google OAuth with PKCE:**

`auth/google_oauth.py`

**Token refresh:**

`agent/calendar_tools.py` – `_service()`

**ADK session reuse:**

`agent/runner.py` – `InMemorySessionService`

**Authentication callback handling:**

`server/app.py`

**Pending-question replay:**

`server/static/chat.html`

### Likely interview questions

**Question: Why use two authentication providers?**

Entra ID proves who the user of the application is. Google OAuth gives separate permission to read that user's Google
Calendar. So the user's identity in the app is separate from access to an external resource.

**Question: Why request read-only calendar permissions?**

The assistant only needs to read events. The code requests the `calendar.readonly` scope. It has no tools to create,
update, or delete events. This limits what the assistant is allowed to do.

**Question: How does token refresh work?**

Before the code builds the Calendar API service, it checks whether the stored credentials have expired. If a refresh
token is available, it calls the Google credentials refresh method.

**Question: How does the assistant continue after authentication?**

When a calendar tool needs authorization, it returns an authentication sentinel. The runner turns this into an
`auth_required` response.

The browser saves the question in `sessionStorage` and starts sign-in. After the OAuth redirects finish, it sends the
question again.

This is **question replay**. The interrupted ADK tool call is not restored.

### Limitations

The date check reads up to 50 upcoming events and filters them by date. It does not use Google's FreeBusy API, and it
does not query the full time range of the requested day. So, call it a basic date-based event check. It is not a
reliable availability service.

The session store and token store are in memory. This is fine for a demo. For production, the project needs:

- persistent storage,
- stronger session isolation,
- an explicit check that the Google OAuth callback belongs to the correct signed-in Entra user.

**Avoid saying:**

"A full calendar availability engine." Or: "Agent execution resumes after OAuth."

**Say instead:**

"Upcoming-event retrieval and basic date-based availability checks." And: "The browser replays the pending question
after sign-in."

---

## 7. Five deeper architecture questions

These questions are especially likely in a senior solutions architecture interview.

1. **Where do you enforce authorization when an AI agent calls tools?**  
   Explain why a prompt alone is not enough. Use two different authorization boundaries as examples: the gateway policy
   in Travel Planner, and the delegated OAuth in the ADK Calendar Assistant.

2. **How do you validate decisions that AI generates?**  
   Compare the Pydantic output models in Travel Planner with the JSON Schema validation and retry loop in CodeGuard.
   Explain that valid structure does not mean the content is true.

3. **How do you handle failures in distributed AI workflows?**  
   Use the examples from Travel Planner: the maximum step limit, MCP call timeouts, JSON-RPC error handling, and
   correlated logs. Say clearly that retries, circuit breakers, and recovery are not fully implemented.

4. **How do you protect sensitive enterprise information when you use LLMs?**  
   Describe how CodeGuard sends only metadata, and how the ADK assistant uses the smallest Google scope. Also mention
   the risk of logging credentials or raw request bodies.

5. **How would you turn these prototypes into an enterprise platform?**  
   Discuss central authorization, isolation per tenant, audit logging, persistent state, repeatable evaluation, human
   approval for high-impact actions, observability, automated security tests, and controlled deployment.

---

## 8. Final checklist: claims that need careful wording

These are the most important differences between what you might say and what the code actually does. Review them just
before the interview.

**Travel Planner – autonomy:**

Avoid: "Fully autonomous multi-agent system."

Say: "Role-separated ReAct workflow with a fixed execution order."

**Travel Planner — security:**

Avoid: "Production-grade tenant security."

Say: "Catalog authorization prototype; per-tenant controls are future work."

**CodeGuard — scope:**

Avoid: "Complete automated secure code review."

Say: "AI-assisted, metadata-based risk assessment POC."

**CodeGuard — LLM providers:**

Avoid: "Both LLMs assess the risks together."

Say: "Selectable OpenAI or Claude triage adapters."

**MCP Studio — maturity:**

Avoid: "Production-ready MCP platform."

Say: "Experiments with MCP protocol and streaming integration."

**ADK Calendar — availability:**

Avoid: "Full calendar availability engine."

Say: "Upcoming-event retrieval and basic date-based availability checks."

**ADK Calendar — after OAuth:**

Avoid: "Agent execution resumes after OAuth."

Say: "The browser replays the pending question after sign-in."
