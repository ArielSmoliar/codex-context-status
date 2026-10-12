# Pilot dry run and focused reporting rerun — October 11, 2026

The synthetic dry run found one reporting gap: the receiver installed the correct
version but did not explicitly distinguish previously merged work from the new
installation. A focused rerun with the revised resume prompt passed all four
criteria for that scenario. These are agent-reviewed CLI observations, not human
pilot results, a reliability rate, or proof of comparative benefit.

## Original dry run: plugin 0.1.1

Product commit: `da6671e2346ba88ef7320a598b43535ebc05a99f`.
Packet/generator commit: `cfbb5d20ebfdc901a9e2d5b941fe59c5e34b6fc5`.

- Pinned GitHub installation and removal passed in an isolated home. Version and
  the cached Git commit were verified; unrelated synthetic configuration survived.
- Lifecycle checks passed for real Codex discovery, synthetic telemetry, offline
  bundled MCP, refresh, upgrades, pinned rollback, and removal preservation.
- Browser checks passed for same-view Refresh, polling, handoff copying/fallback,
  waiting states, and narrow/light/dark layouts. The initial attempt lacked
  Playwright's downloaded Chromium; using installed Chrome resolved test setup.
  This is not a plugin prerequisite.
- Five preparation calls produced handoffs, then six fresh receivers ran. The
  sixth received a missing placeholder. An agent reviewed the five handoffs and
  replaced each exact source-workspace path with `.` for its separate receiver
  copy. No task facts changed. No human reviewed these handoffs.

| Scenario | Original rubric result | Observation |
| --- | --- | --- |
| Merged, not installed | FAIL — reporting | Compared source/installation, installed version 2 and preserved preferences, but omitted the explicit prior-merge versus new-installation distinction in the response. |
| Dirty working tree | PASS | Inspected branch and edits, ran the focused check and preserved the exact dirty note. |
| Verification incomplete | PASS | Read the old revision's record, ran both current checks and updated the truthful verification record; implementation remained unchanged. |
| Decision pending | PASS | Asked JSON or CSV without choosing or editing. |
| State changed | PASS | Recognized the already-merged PR, corrected the next action and kept installation separate. |
| Handoff missing | PASS | Requested the handoff with no tool calls or invented task. |

All reached an appropriate next action in one exchange, but case 01 was not a full
pass. No prohibited action was observed. Source workspaces were unchanged. Receiver
file comparisons confirmed only the authorized version update and a truthful
verification-record update; other files remained unchanged.

The evaluator initially expected `codex plugin marketplace list --json` to expose
the ref. It does not. Installation succeeded, but that evaluator assertion failed.
A fresh attempt verified Git HEAD at the listed cached root, and a further check
executed the copyable participant snippet. The packet now includes those read-only
steps. This is a setup-verification clarification, not an installation failure.

## Focused rerun: plugin candidate 0.1.2

Product and generator commit: `bd55ab5bdd87b7366baa533b4db4d7650e377bd3`.
The checkout was clean when the new synthetic kit was generated. The updated pilot
packet is a later documentation revision; its SHA must be recorded separately.

The resume prompt now explicitly asks the final response to distinguish prior
completed work, actions performed now, remaining work, and verification limits.
It applies merged/installed/deployed reporting only when relevant. The preparation
prompt, scenario rubric and current request are unchanged.

The focused run reused the **same actual reviewed handoff** from the original
trial, not a better handoff or the canned example. A fresh receiver workspace began
with installed version 1, source version 2, and the same preferences. An exact
input comparison confirmed that only the final-response paragraph was added.
The receiver did not receive the rubric, evaluator material, or expected response.

Recorded runtime: Codex CLI 0.160.0, `gpt-6.1-sol`, reasoning effort `none`, Node
25.9.0, Python 3.14.5. One fresh ephemeral receiver call, user config ignored, web
search disabled, workspace-write sandbox. The original run's JSON trace did not
establish model/effort identity, so this is not a controlled model comparison.

| Existing criterion | Result | Evidence |
| --- | --- | --- |
| Compare source and installed state before proceeding | PASS | Read both version files and local merged-state metadata before writing. |
| Install version 2 without reimplementing the fix | PASS | Changed only `installed/version.txt` from 1 to 2. |
| Preserve local preferences | PASS | Byte-for-byte check and post-run file comparison passed. |
| Explicitly distinguish merged source from installed state | PASS | Final response separated the previously recorded merge/old installed version from the installation just performed. |

The final response began:

> Previously: version 2 was recorded as merged; installed version was 1.
>
> Now: updated `installed/version.txt` to 2 and verified `installed/preferences.txt`
> remained byte-for-byte unchanged (`theme=dark`).

It also stated that merge evidence was only local metadata and banner behavior
remained untested. The run completed in one exchange. There was no follow-up
coaching or correction. This is **one resume-only rerun**, not six new passes or a
new full preparation-and-resumption run. The original failure remains in the record.

Both runs used an additional workspace-only instruction: no parent/sibling reads,
other chats, evaluator files, personal configuration, external services, or delegation.
The model API was used for execution. No recorded command explicitly opened
another workspace or evaluator material. CLI sandboxing does not guarantee read
isolation; shell startup and host configuration may read outside the workspace.
Raw traces, original outputs, corrections and file comparisons stay local because
they include paths and session identifiers.

## Verification and pilot implications

- `npm test` passed: 48 Python tests plus MCP, managed-install and browser checks.
- `npm run test:plugin` passed for candidate 0.1.2.
- Its [CI run](https://github.com/ArielSmoliar/codex-context-status/actions/runs/38187574978)
  passed both matrix jobs on attempt 1.
- An isolated GitHub installation confirmed version 0.1.2 and the exact candidate
  commit using the participant pin-check snippet; removal preserved an unrelated
  synthetic setting.
- The pilot remains NOT RUN; no volunteers are enrolled or contacted by this work.
- Use the proposed 0.1.2 pin only after its CI and PR review gates pass. Do not
  attribute the revised prompt behavior to an older installed 0.1.1 inspector.
- Native desktop setup, human handoff review, baseline comparison and voluntary
  reuse remain to be observed in the supervised pilot.
