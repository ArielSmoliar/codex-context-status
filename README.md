# Codex Context Status

A local context inspector for Codex desktop, with horizontal capacity and cache bars, in-place refresh, and guidance for when to prepare a session handoff.

## What it shows

- Estimated context usage and remaining capacity from the latest recorded request.
- Cached and noncached input, output, and expandable token accounting.
- Current recorded model, reasoning effort, compaction activity, and measurement timestamps.
- Latest-usage model attribution, a waiting state after model changes, and the ten most recent recorded switches.
- Expandable telemetry checks for verified session identity, model metadata, usage, context limit, and cache counters, including when usage is unavailable.
- Session-recorded producer version and evidence for known usage formats; unreadable newer measurements withhold capacity advice until recovery.
- A teal Refresh button and Auto-refresh enabled by default, every 15 seconds while visible.
- Advisory handoff checkpoints at 80% and 90% estimated usage.

Refresh updates the existing inspector without sending a chat message or invoking a model. Auto-refresh pauses when hidden, can be switched off, and stops after three consecutive failures. Usage numbers and recommendations stay inside the view so chat text does not become stale.

## Requirements

- A Codex desktop build with local MCP server and MCP Apps support.
- Local session logs with the supported telemetry fields. Remote or ephemeral chats may be unavailable.
- Node.js 20+ and Python 3.10+ with IANA timezone data.

This project was verified on macOS with Codex desktop 26.1007.21159. Its local log format is an implementation detail and can change between Codex releases. Browser and reader tests also run on Linux; this is not a claim of full desktop compatibility across platforms.

See the [compatibility matrix](references/compatibility.md) for live release evidence, synthetic format coverage, and how to verify another release. Currently only one desktop build has documented live verification.

## Install

Clone a trusted revision of this repository and run these commands from its root:

```sh
python3 scripts/install.py
python3 scripts/install.py --apply
```

The first command previews changes without writing. Apply creates a managed copy in `${CODEX_HOME:-$HOME/.codex}/skills/context-status`. Then run the dependency and MCP setup commands printed by the helper. Inspect any existing MCP registration before replacing it; the helper leaves Codex configuration untouched. File installation alone does not verify runtime readiness or desktop support.

For upgrades, run the same commands from the desired revision. Local edits stop an upgrade; extra files are preserved, and the previous installation is kept as a backup. Older copies require an explicit `--adopt` comparison; symlink installations are left untouched. See [installation and recovery](references/installation.md) for migration, conflicts, backups, and component-specific reload steps.

If `$context-status` or the new MCP tool is unavailable, start a new turn or restart Codex. Then invoke:

```text
$context-status
```

The skill resolves the current chat ID and opens the inspector. New inspectors start with Auto-refresh on. Existing open views retain older UI code until reopened; Refresh updates telemetry only. Keep the installed copy in place while the skill and MCP server reference it. A developer using a symlink must also retain its source checkout.

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

Run `npm run benchmark` to measure reader and one-shot CLI latency using temporary synthetic logs. See [refresh performance](references/performance.md) for paired comparisons, measured results, and scope. The reader still scans a fresh size-bounded snapshot on each refresh.

The generated `mcp/inspector.html` is committed for direct installation. After editing the shared template, bridge, or CSS, rebuild and commit the generated file. CI checks that it matches its sources.

See [telemetry details](references/telemetry.md), [MCP implementation](mcp/README.md), and the [development roadmap](ROADMAP.md).
