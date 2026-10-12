# Development roadmap

Updated October 11, 2026. The next milestone is evidence from three daily Codex
desktop users installing the GitHub plugin and continuing real work in a fresh
chat. No participants are enrolled and no pilot results are claimed.

## Available now

- **GitHub plugin distribution:** a self-contained skill and local stdio MCP server with
  bundled JavaScript dependencies and Codex-managed install, upgrade, rollback,
  and removal. The plugin currently needs the default `~/.codex` data directory.
  See [installation and migration](references/plugin.md).
- **Inspector:** estimated recorded capacity, cache reuse, compaction activity,
  exact-chat diagnostics, recorded model attribution and transitions, and a waiting
  state after model changes. Refresh updates the same view; auto-refresh starts on.
- **Session advice and handoff:** task-intent controls, preparation/resume prompts,
  and current-state checks, including merged versus installed work. Browser coverage
  exists; real-task effectiveness is still unverified. See [handoff scenarios](references/handoffs.md#evaluating-a-handoff).
- **Validation foundation:** an offline synthetic demo, six scenarios, and a
  [prepared pilot packet](references/pilot/README.md). The [historical CLI smoke run](references/validation-smoke-2026-10-11.md)
  passed six synthetic cases at its original revision; it is not new 0.1.1 evidence.
- **Standalone alternative:** preview-first copies, conflict detection, retained
  backups, and separate MCP registration. Custom-home users need this route for
  in-place Refresh. Keep its evaluation separate from GitHub plugin results.

## Next, in order

| Priority | Work | Evidence needed to move on |
| --- | --- | --- |
| 1. Run the plugin pilot | Recruit P01–P03; use the reviewed, pinned 0.1.2 participant instructions, record prerequisites, installation help, two comparable transitions per person, and seven-day voluntary reuse. | All attempts retained, baseline and assisted outcomes separate, and participant-approved sanitized findings. Targets: three working inspectors, two unassisted installs within ten minutes with prerequisites ready, and two assisted transitions preserving critical facts within two exchanges. These are directional targets, not reliability claims. |
| 2. Fix observed failures | Address setup/discovery obstacles first, then preparation or continuation failures. Add focused regression coverage for each reproduced defect. | Reproduce the reported issue without personal logs; verify the fix on the affected setup or scenario. Resolve prohibited-action failures before promoting handoff reliability. |
| 3. Extend compatibility evidence | Verify additional desktop builds and operating systems using the existing checklist; retain unavailable states and the custom-home limitation. | A dated live check per claimed build in the [compatibility matrix](references/compatibility.md). CLI and synthetic tests alone do not establish desktop support. |
| 4. Decide the next product investment | Use pilot reuse and failure evidence to choose what to build. Consider direct handoff access if handoff is reused while the meter is ignored; investigate the need if both go unused. | An explicit decision tied to observations, including unanswered follow-ups, rather than more speculative advice thresholds. |

The proposed pilot candidate is plugin **0.1.2** at
`bd55ab5bdd87b7366baa533b4db4d7650e377bd3`, adding an explicit final-response distinction
between prior work, current actions, and remaining verification. Its [CI gate](https://github.com/ArielSmoliar/codex-context-status/actions/runs/38187574978)
passed on attempt 1; PR review and merge remain required before distributing the packet. Record the
packet/kit-source revision separately from the product. The [dry run and focused
rerun](references/pilot-dry-run-2026-10-11.md) retain the original reporting failure;
they do not establish a model reliability rate or participant success.
Only one macOS desktop build has prior live verification; the pilot must still
verify rendering and exact-chat Refresh for the actual installed candidate.

## Parallel distribution work

OpenAI directory: 0.1.1 was uploaded as a **draft**, and the metadata corrections
cleared their reported findings. The local command MCP finding still blocks the
ordinary submission path. The eligibility inquiry was sent through the Help Center
and escalated to a support specialist on October 11; guidance on local transport,
session-log extraction, Codex-only scope, and reviewer setup is pending. The last
observed skill scan was pending. No review approval or publication is implied.
Keep GitHub distribution and the pilot moving independently. See the
[submission status](references/submission/README.md).

Licensing: choose a first-party license before presenting the project as licensed
open source. There is currently no root LICENSE; third-party notices do not grant
a license to this project's code. This remains a maintainer decision.

## Deferred until evidence supports it

Incremental telemetry caching, additional advice heuristics, a guided handoff
artifact workflow, and a multi-chat dashboard are not the next release scope.
[Refresh benchmarks](references/performance.md) already cover the current reader;
add caching only if measurements justify its state and invalidation complexity.

Do not add exact-occupancy, model-quality, compaction-threshold, token-attribution,
or cache-cause claims without a supporting data source. Telemetry processing stays
local; directory eligibility is not a reason to expose session logs remotely.
