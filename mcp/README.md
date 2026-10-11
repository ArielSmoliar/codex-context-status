# Local context-status MCP App

This local stdio server provides an MCP App whose Refresh button rereads the selected chat's recorded telemetry and redraws the existing view. It sends no follow-up chat message and does not invoke a model. No web server, tunnel, API key, or browser network request is used.

## Setup

Follow the [repository installation instructions](../README.md#install). Invoke `$context-status` to open the MCP inspector. The inline fallback creates separate snapshots and cannot update a previous inline chart in place.

## Session guidance

- Below 80% recorded estimated capacity: continue focused work.
- At 80%: prepare a handoff and switch at a task boundary.
- At 90%: start a new session soon, before substantial additional work.
- Unknown capacity, including after compaction or a model change: withhold capacity-based guidance until fresh telemetry exists.

These are advisory checkpoints chosen for this inspector, not OpenAI's automatic compaction threshold. The app cannot predict the next request's size or guarantee when a new session is needed. Save the goal, decisions, relevant files, and next step before moving sessions.

## Implementation

- `server.mjs`: official MCP SDK; two read-only tools and one HTML resource.
- `bridge.js`: standard MCP Apps JSON-RPC bridge. Only the initial open tool has `ui.resourceUri`; refresh returns data only.
- `build_widget.py`: builds `inspector.html` from the shared chart template plus the MCP bridge and host-aware theme.
- `../scripts/mcp_snapshot.py`: allowlists numeric usage and display metadata. It omits account quotas, source paths, and message content.

Each view is bound to an explicitly supplied, validated thread UUID. The Python reader verifies the log's session identity. The UI refuses a response that would change that binding. It retains the last snapshot after a refresh failure, supports retry, and distinguishes the last usage timestamp from the latest check time.

The backend reads the available log for manual Refresh and Auto-refresh. Auto-refresh starts enabled in every new view, can be turned off, and runs every 15 seconds while the view is visible, pauses while hidden, and stops when disabled or closed. Reads never overlap. Three consecutive failures turn the option off with an explanation; it can be reenabled to retry. The setting lasts for the current view only. This is local UI polling, not an app-server event subscription or scheduled chat automation. Log access may fail for remote, ephemeral, or unavailable sessions.

## Develop

From this directory, with Node 20+ and Python 3.10+ with IANA timezone data:

```sh
npm ci --ignore-scripts
npm run build
npm start
```

The MCP configuration should use absolute Node and Python paths. If those runtimes move, update the MCP command and `CONTEXT_STATUS_PYTHON` environment setting. The reader uses the default local Codex home unless `CODEX_HOME` is explicitly set for the server.

## Verification performed

The local SDK client verified tool metadata, resource loading, fresh reads from isolated synthetic sessions, field redaction, exact identity, and invalid-input handling. A Chrome test host exercised the actual stdio server with a synthetic session log: same-DOM refresh, retained expanded details, failure/retry, unavailable-to-available recovery, session guidance, light/dark theme, 320px width, and no follow-up messages. The reader/render regression tests and skill validation passed.

Manual verification on Codex desktop confirmed the inspector renders and Refresh updates the existing view. Automated browser tests use a test MCP host; they do not replace desktop compatibility checks after Codex updates.

To unregister the app without deleting the skill: `codex mcp remove context-status`.
