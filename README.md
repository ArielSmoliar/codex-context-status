# Codex Context Status

A local context inspector for Codex desktop, with horizontal capacity and cache bars, in-place refresh, and guidance for when to prepare a session handoff.

[Explore the capabilities and interactive examples](https://codex-context-status.major-cabin-5392.chatgpt.site).

## What it shows

- Estimated context usage and remaining capacity from the latest recorded request.
- Cached and noncached input, output, and expandable token accounting.
- Current recorded model, reasoning effort, compaction activity, and measurement timestamps.
- Latest-usage model attribution, a waiting state after model changes, and the ten most recent recorded switches.
- Expandable telemetry checks for verified session identity, model metadata, usage, context limit, and cache counters, including when usage is unavailable.
- Session-recorded producer version and evidence for known usage formats; unreadable newer measurements withhold capacity advice until recovery.
- A teal Refresh button and Auto-refresh enabled by default, every 15 seconds while visible.
- Task-aware session advice with explicit 80% and 90% advisory checkpoints.
- Expandable handoff checklist with preparation and resume prompts, plus manual-copy fallback.

Refresh updates the existing inspector without sending a chat message or invoking a model. Auto-refresh pauses when hidden, can be switched off, and stops after three consecutive failures. Usage numbers and recommendations stay inside the view so chat text does not become stale.

## Requirements

- A Codex desktop build with local MCP server and MCP Apps support.
- Local session logs with the supported telemetry fields. Remote or ephemeral chats may be unavailable.
- Node.js 20+ and Python 3.10+ with IANA timezone data.

This project was verified on macOS with Codex desktop 26.1007.21159. Its local log format is an implementation detail and can change between Codex releases. Browser and reader tests also run on Linux; this is not a claim of full desktop compatibility across platforms.

See the [compatibility matrix](references/compatibility.md) for live release evidence, synthetic format coverage, and how to verify another release. Currently only one desktop build has documented live verification.

## Install

### Codex plugin (GitHub distribution)

The plugin bundles the skill, local MCP server, and inspector. With Node 20+,
Python 3.10+, and a Codex CLI supporting `plugin add` (tested on 0.160.0):

```sh
codex plugin marketplace add ArielSmoliar/codex-context-status --ref main
codex plugin add context-status@codex-context-status
```

Restart Codex if needed, select the Context Status skill, and open the inspector.
No npm setup or manual MCP registration is needed. Dependencies are bundled;
telemetry reads stay local. The installed skill may appear as
`context-status:context-status`.

See [plugin installation, upgrades, rollback, and removal](references/plugin.md).
Existing standalone users should follow its migration steps before enabling the
plugin to avoid duplicate skills and server registrations. The plugin does not
modify those separate installations automatically.

### Standalone skill (alternative)

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

The 80% and 90% checkpoints are advisory, not Codex's compaction trigger. Choose your **Next step** to distinguish continuing the task, planning a large step, or starting unrelated work. The inspector cannot predict the size of that step. Missing telemetry and compaction counts alone do not mean you should restart.

Expand **Handoff checklist & prompts** for a checklist and prompt to paste into the current chat. The prompt asks for established goals, decisions, files, verification, blockers, and the next action. Copying does not generate a summary, send a message, or open a chat. Review the resulting handoff before pasting it into a new session. If clipboard access is unavailable, the text is selected for manual copying.

Choose **1. Current chat** to prepare the handoff or **2. New chat** for the resume prompt. Add your reviewed handoff to the resume prompt before sending it. The resume prompt asks the next chat to reconcile the summary with current workspace state before continuing. Your intent, prompt selection, and expanded details persist through refreshes within the current view. See [handoff and resume guidance](references/handoffs.md).

Model changes are detected when the new model appears in recorded turn metadata, typically after the next message. The previous context limit is cleared, and capacity is withheld until fresh usage and a new limit exist. Older cache measurements retain their model label. The inspector records a switch count and the latest ten transitions; these reflect the available log, not model-picker clicks. Cache-miss causes remain unavailable.

Telemetry checks distinguish observed data, fields not observed yet, and checks that could not run because the log was inaccessible or unverified. Missing evidence does not establish that a Codex version is unsupported. Usage records with explicit turn IDs are accepted for the current turn only; legacy records without turn IDs rely on log order for model attribution.

## Privacy and scope

The MCP server runs locally over stdio. It reads the exact selected session, verifies its identity, and returns allowlisted telemetry. The UI has no external network dependencies. The backend does not modify session logs or return conversation content. Display data omits account quotas and source paths.

This is a personal local tool, not a multi-user service. Do not expose it through a public tunnel or network endpoint. It relies on the local account's filesystem access, not remote-user authentication.

## Try the validation kit

The [validation guide](references/validation.md) includes pinned-candidate install
instructions, a synthetic walkthrough, six handoff scenarios, and a three-person
pilot protocol. Generate an offline kit into a new directory:

```sh
python3 scripts/prepare_validation.py --output /tmp/context-status-trial
```

Open the generated `demo.html` and `protocol.md`. Generation makes no model calls
and reads no chats. It does **not** establish handoff quality. The first
[agent-reviewed CLI smoke run](references/validation-smoke-2026-10-11.md) passed all
six synthetic cases; real-task effectiveness and outside-user adoption remain
unverified. Use the [results template](references/validation-results.md)
to keep baseline, assisted, and synthetic observations separate.

The [three-person pilot packet](references/pilot/README.md) has participant setup
instructions, a proposed trial order, an invitation draft, and private scorecard
templates. Its P01–P03 slots are placeholders, not enrolled users.

The [new-user landing page source](site/README.md) provides a capability tour,
interactive synthetic examples, and pinned installation commands.
The [SEO plan](references/seo-plan.md) covers search intent, technical setup,
Search Console verification, and the first month of measurement.

## Development

```sh
npm ci --ignore-scripts
npm ci --prefix mcp --ignore-scripts
npx playwright install chromium
npm run build
npm test
npm run test:plugin # requires Codex CLI 0.160.0; uses an isolated synthetic home
```

Use `CHROME_EXECUTABLE_PATH` to test with an existing Chromium/Chrome binary instead of Playwright's downloaded browser. Run commands from the repository root.

Tests use temporary, synthetic session logs. They never need your Codex account or personal chats. Coverage includes identity validation, partial log records, model changes, compaction, redaction, real stdio tool calls, same-view refresh, default-on polling, pause/resume, failure recovery, and narrow/light/dark presentation.

Run `npm run benchmark` to measure reader and one-shot CLI latency using temporary synthetic logs. See [refresh performance](references/performance.md) for paired comparisons, measured results, and scope. The reader still scans a fresh size-bounded snapshot on each refresh.

The generated `mcp/inspector.html` and `plugins/context-status/` are committed for
direct installation. After editing runtime files, rebuild with `npm run build`
and commit generated changes. CI checks source parity. Edit manifests under
`packaging/`; do not edit generated plugin files. The plugin build uses an explicit
file allowlist and preserves bundled dependencies' license notices.

`test:plugin` runs actual Codex install, upgrade, rollback, and removal commands
against a temporary Git marketplace. It verifies host discovery, offline stdio
reads, in-place refresh data, cache cleanup, and preservation of synthetic logs
and unrelated configuration. It makes no model calls or changes to your installed
skill. This is CLI/app-server integration coverage, not a claim that every desktop
release renders MCP Apps correctly.

See [telemetry details](references/telemetry.md), [MCP implementation](mcp/README.md), and the [development roadmap](ROADMAP.md).
