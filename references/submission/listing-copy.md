# Proposed directory listing

Draft copy for the local Codex product, conditional on eligibility. Not an active
manifest and not a claim of OpenAI approval. Validate category and publisher
identity in the portal before use.

| Field | Proposed value |
| --- | --- |
| Stable package name | `context-status` |
| Display name | Context Status |
| Short description | Visibility into Codex sessions |
| Developer name | Ariel Smoliar — must match verified identity |
| Category | Productivity — confirm against the dashboard |
| Website | https://codex-context-status.major-cabin-5392.chatgpt.site/ |
| Support | https://github.com/ArielSmoliar/codex-context-status/issues |
| Privacy policy / terms | Pending maintainer approval and publication; no URLs assigned |
| Primary / composer icon | `./assets/logo.svg` |
| Dark primary / composer icon | `./assets/logo-dark.svg` |

The icon paths apply only after copying this packet's assets into the plugin
root. They are not currently declared by the installed package.

## Long description

Context Status helps people working on long tasks in Codex desktop understand
their session's recorded context usage and prepare for a fresh chat.

Open a compact inspector showing estimated capacity, remaining space, input
cache reuse, model changes, and compaction activity. Refresh updates the same
view. Auto-refresh starts on, checks every 15 seconds while visible, and pauses
when hidden. Timestamps show when usage was recorded.

Choose whether your next step continues the task, starts substantial work, or
switches topics. The inspector offers advisory guidance and copyable prompts
for preparing and reviewing a handoff. It does not create chats or transfer
conversation history automatically.

The plugin runs a local server that reads the selected Codex session's log and
returns limited telemetry to Codex. It requires local Codex desktop with MCP Apps,
Node.js 20+, Python 3.10+ with timezone data, and the default Codex data directory.
Custom data directories need the separate standalone installation for in-place
refresh. Chats without readable local logs report unavailable data. Desktop
compatibility evidence is currently limited to one macOS build.

Capacity is an estimate of the last recorded request, not exact live occupancy.
Cached input still uses context. The tool does not diagnose model-quality decline,
predict automatic compaction, or guarantee that starting a new chat improves
results. It is an independent community project.

## Starter prompts

- Show the context-status inspector for this chat.
- Show this chat's recorded context usage and cache reuse.
- Open context-status so I can review the guidance before a large step.

## Proposed release notes

Initial directory listing candidate for the existing local Codex inspector:
recorded usage and cache bars, in-place refresh, default-on polling, model and
compaction diagnostics, and intent-based handoff guidance. Exact submitted version
and eligible platform scope will be set after eligibility and review preparation.
