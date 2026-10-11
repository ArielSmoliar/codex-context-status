# Codex Context Status

A local context inspector for Codex desktop, with horizontal capacity and cache bars, in-place refresh, and guidance for when to prepare a session handoff.

## What it shows

- Estimated context usage and remaining capacity from the latest recorded request.
- Cached and noncached input, output, and expandable token accounting.
- Current recorded model, reasoning effort, compaction activity, and measurement timestamps.
- Latest-usage model attribution, a waiting state after model changes, and the ten most recent recorded switches.
- Expandable telemetry checks for verified session identity, model metadata, usage, context limit, and cache counters, including when usage is unavailable.
- A teal Refresh button and Auto-refresh enabled by default, every 15 seconds while visible.
- Advisory handoff checkpoints at 80% and 90% estimated usage.

Refresh updates the existing inspector without sending a chat message or invoking a model. Auto-refresh pauses when hidden, can be switched off, and stops after three consecutive failures. Usage numbers and recommendations stay inside the view so chat text does not become stale.

## Requirements

- A Codex desktop build with local MCP server and MCP Apps support.
- Local session logs with the supported telemetry fields. Remote or ephemeral chats may be unavailable.
- Node.js 20+ and Python 3.10+ with IANA timezone data.

This project was verified on macOS with Codex desktop 26.1007.21159. Its local log format is an implementation detail and can change between Codex releases. Browser and reader tests also run on Linux; this is not a claim of full desktop compatibility across platforms.

## Install

Clone this repository and run these commands from its root:

```sh
npm ci --prefix mcp --ignore-scripts
python3 mcp/build_widget.py
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD" "${CODEX_HOME:-$HOME/.codex}/skills/context-status"
codex mcp add context-status \
  --env "CONTEXT_STATUS_PYTHON=$(command -v python3)" \
  -- "$(command -v node)" "$PWD/mcp/server.mjs"
```

The skill link intentionally fails if a skill with that name already exists. For an existing installation, compare it with this checkout and retain any local changes before updating its link or files. Register the MCP server against the installation you intend to use.

If `$context-status` or the new MCP tool is unavailable, start a new turn or restart Codex. Then invoke:

```text
$context-status
```

The skill resolves the current chat ID and opens the inspector. New inspectors start with Auto-refresh on. Existing open views may retain older UI code until reopened. Keep the repository in place while the skill and MCP server reference it.

To unregister the server, run `codex mcp remove context-status`. Removing the skill link is a separate action.

## How to interpret it

**Capacity is an estimate, not exact live occupancy.** It uses the last recorded request footprint and runtime-reported context limit. It excludes unreported work. Cumulative totals measure consumption across requests, not unique context size. Cached input still occupies context.

The 80% and 90% checkpoints are advisory, not Codex's compaction trigger. Save a handoff before switching sessions: goal, decisions, relevant files, and next step. An unrelated task can justify starting a new chat at any usage level.

Model changes are detected when the new model appears in recorded turn metadata, typically after the next message. The previous context limit is cleared, and capacity is withheld until fresh usage and a new limit exist. Older cache measurements retain their model label. The inspector records a switch count and the latest ten transitions; these reflect the available log, not model-picker clicks. Cache-miss causes remain unavailable.

Telemetry checks distinguish observed data, fields not observed yet, and checks that could not run because the log was inaccessible or unverified. Missing evidence does not establish that a Codex version is unsupported. Usage records with explicit turn IDs are accepted for the current turn only; legacy records without turn IDs rely on log order for model attribution.

## Privacy and scope

The MCP server runs locally over stdio. It reads the exact selected session, verifies its identity, and returns allowlisted telemetry. The UI has no external network dependencies. The backend does not modify session logs or return conversation content. Display data omits account quotas and source paths.

This is a personal local tool, not a multi-user service. Do not expose it through a public tunnel or network endpoint. It relies on the local account's filesystem access, not remote-user authentication.

## Development

```sh
npm ci --ignore-scripts
npm ci --prefix mcp --ignore-scripts
npx playwright install chromium
npm run build
npm test
```

Use `CHROME_EXECUTABLE_PATH` to test with an existing Chromium/Chrome binary instead of Playwright's downloaded browser. Run commands from the repository root.

Tests use temporary, synthetic session logs. They never need your Codex account or personal chats. Coverage includes identity validation, partial log records, model changes, compaction, redaction, real stdio tool calls, same-view refresh, default-on polling, pause/resume, failure recovery, and narrow/light/dark presentation.

The generated `mcp/inspector.html` is committed for direct installation. After editing the shared template, bridge, or CSS, rebuild and commit the generated file. CI checks that it matches its sources.

See [telemetry details](references/telemetry.md), [MCP implementation](mcp/README.md), and the [development roadmap](ROADMAP.md).
