# Review evidence and synthetic walkthrough

## Existing evidence

The [PR #13 CI run](https://github.com/ArielSmoliar/codex-context-status/actions/runs/38184824003)
passed both Node 20/Python 3.10 and Node 22/Python 3.12. Its workflow runs unit,
MCP, browser, standalone-installation, landing-page, plugin lifecycle, and benchmark
checks. These are synthetic automated results, not directory review approval or
new-user desktop trials.

| Review behavior | Existing evidence to inspect |
| --- | --- |
| Exact-chat telemetry, response minimization, missing/invalid ID | `tests/test-mcp.mjs`, `tests/test_context_status.py` |
| Model changes and unreadable measurements | `tests/test_compatibility.py`, `tests/test-mcp-ui.mjs` |
| In-place Refresh, visibility-aware polling, failure stop | `tests/test-mcp-ui.mjs` |
| Advice and copying handoff prompts without sending | `tests/test-mcp-ui.mjs` |
| Isolated install, upgrade, removal | `tests/test-plugin.mjs` |
| Limited live desktop evidence | [Compatibility record](../compatibility.md) |
| Independent-user evaluation | [Pilot](../pilot/README.md): prepared, not run |

`review-cases.json` is a proposed set of five positive and three negative cases.
**Those eight reviewer trials have not been executed or recorded.** The fixture
tests cover relevant mechanics; they do not establish prompt routing or a full
reviewer journey. Record each trial's candidate SHA, environment, actual tool
calls, PASS/FAIL/INCONCLUSIVE, and sanitized observations when run.

## Isolated setup

All fixture identities and measurements must be invented. Never record this
maintainer chat or use production session logs for screenshots or video.

For code-level checks, the repository's existing tests create temporary synthetic
Codex homes and clean them up. `npm run test:mcp` exercises the local stdio tools;
`npm run test:ui` drives the real inspector with a synthetic host bridge. Use
`CHROME_EXECUTABLE_PATH` only if the machine needs a local Chrome binary.

The current plugin host does not forward a custom `CODEX_HOME` on the tested CLI.
Therefore a synthetic test server explicitly given a temporary home is **not**
evidence that a plugin install in a custom home works. A desktop reviewer should
use an agreed isolated OS account/environment with its own default Codex home,
or a future OpenAI-approved fixture/telemetry mechanism. Do not place fabricated
logs into the maintainer's normal Codex profile.

The offline handoff demo can be generated with
`python3 scripts/prepare_validation.py --output /tmp/context-status-review-demo`
when that target does not exist. Its `demo.html` is illustrative: it does not
demonstrate live MCP refresh, plugin installation, or successful reviewer trials.
Keep generated participant folders and notes outside version control.

## Walkthrough storyboard — not recorded

1. **Scope and setup:** show the candidate version, supported environment, and a
   visible “Synthetic data” label. Explain the local server and read-only log
   access. Show install/open only in the agreed isolated desktop environment.
2. **Capacity and cache (positive case 1):** open the inspector. Explain the
   recorded timestamp, estimated request footprint, and why cache is a subset.
3. **Refresh (case 2):** advance synthetic telemetry, click Refresh, then show
   Auto-refresh updating the same inspector. Pause/stop polling and show that no
   chat message is created. A simulated host segment must be labeled as such.
4. **Model change (case 3):** show waiting for a new-model limit, then recovery
   after a new synthetic usage event. Do not claim a picker click alone is detected.
5. **Compaction (case 4):** show the recorded event and waiting/recovery behavior.
   Explain that observed compaction is not a prediction of the next threshold.
6. **Handoff (case 5):** choose a large next step, show advisory guidance, copy the
   preparation prompt, and explain human review and separate submission.
7. **Negative cases:** show missing identity, missing/invalid telemetry, and a
   request for raw conversations. No fabricated capacity, guessed chat, or log
   export should occur.
8. **Lifecycle and limitations:** show removal in the isolated environment and
   explain the default-directory restriction, unverified platforms, and support.

A storyboard and existing browser test are not a video deliverable. Record the
agreed setup, review it for private data, host the finished video at a
reviewer-accessible URL, and only then populate `review.demo_recording_url`.
