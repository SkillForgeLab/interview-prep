---
name: mcp-tutor
description: Teach MCP protocol concepts, MCP Apps, and App Bridge by clarifying component responsibilities, request flow, and integration boundaries.
---

# MCP Tutor

Use this skill for MCP-specific concepts and learning tracks. Follow
`AGENTS.md` for routing. Apply `first-principles-learning` for shared learner
preferences, modes, pacing, and exercises. Apply `tech-stack-curriculum` when
teaching MCP or FastMCP as part of the workspace stack.

## Select a track

Read [MCP Learning Tracks](MCP-LEARNING-TRACKS.md) and load only the track
relevant to the request. Teach a later track directly after covering only the
prerequisites it needs; do not require completing every track.

## Teach responsibilities before tools

- **MCP:** Explain the roles of host, client, server, tools, resources, prompts,
  transport, and request/result flow. Distinguish the host from its MCP client
  and server.
- **MCP Apps:** Explain how an MCP interaction can present a visual interface
  and how that UI relates to the host and server.
- **App Bridge:** Explain how the host-side
  `@modelcontextprotocol/ext-apps/app-bridge` connects an embedded MCP App UI
  with its MCP server. Keep responsibilities distinct: the host manages the
  iframe, sandboxing, permissions, and security policy; the bridge carries tool
  calls and results between the UI and server.

Do not treat MCP, MCP Apps, App Bridge, and conventional HTTP APIs as
interchangeable. Start from the user's client and interaction needs. Explain
the underlying protocol and component boundaries before introducing a
framework or library.

## Keep examples scoped

Use the smallest architecture that demonstrates the requested interaction.
Add FastAPI, a database, or external services only when a requirement needs
them. When showing an MCP App backed by a web API, explain the optional
responsibilities in this order:

```text
MCP host
+-- host-side App Bridge
    +-- sandboxed iframe
        +-- MCP App UI
            +-- tool calls via bridge --> MCP server
                                      +-- optional FastAPI/backend
                                          +-- database / external API
```

This is one possible design, not a required stack. Omit layers that do not
solve a real need.
