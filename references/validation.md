# Validation kit

This kit tests whether another person can install context-status and continue work
in a fresh chat. It adds no product features. The generator is offline: it creates
synthetic files, never reads Codex logs, and never starts a model, modifies Codex
configuration, or contacts participants. Initial agent-reviewed CLI smoke trials
are recorded in the [October 11 report](validation-smoke-2026-10-11.md).
**The human-reviewed desktop trials and outside-user pilot are NOT RUN.**

## Prepare a candidate

The current three-person pilot installs **plugin 0.1.1** at full product SHA
`da6671e2346ba88ef7320a598b43535ebc05a99f`. Its
[CI gate](https://github.com/ArielSmoliar/codex-context-status/actions/runs/38186260192)
passed on attempt 2; attempt 1 passed lifecycle assertions but failed temporary
fixture cleanup. A candidate is not a broadly validated release.

Use the [participant installation instructions](pilot/participant.md) for the
pinned GitHub marketplace commands, prerequisites, existing-install review,
exact-chat verification, Refresh checks, and removal. The plugin needs Node 20+,
Python 3.10+ with timezone data, a Codex CLI with plugin support, local desktop
MCP Apps, and the default `~/.codex` data directory. Custom-home attempts are
UNAVAILABLE for this plugin; never move personal data to fit a trial.
A [standalone installation](installation.md) is a separate evaluation lane and
must not count as plugin installation success. GitHub distribution does not depend
on OpenAI directory approval.

Only macOS desktop 26.1007.21159 has prior live verification. Linux CI and CLI
lifecycle tests are not desktop compatibility evidence. See
[compatibility](compatibility.md). Retain failed/unavailable installation attempts
and facilitator help in the record.

Record **two revisions**: the frozen product install SHA and the full commit SHA
of the pilot packet/kit source used for the trial. This updated protocol is newer
than the product candidate. Do not use the older pilot instructions in that
candidate's source checkout or change the product pin to obtain newer instructions.
Historical smoke results keep their original revision; they are not 0.1.1 results.

## Generate an offline kit

The maintainer supplies a reviewed full **kit-source SHA** containing this protocol.
Use a source archive at that SHA or clone and detach explicitly:

```sh
git clone https://github.com/ArielSmoliar/codex-context-status.git
cd codex-context-status
git checkout --detach FULL_KIT_SOURCE_COMMIT_SHA
git rev-parse HEAD
git status --short
```

Replace the placeholder before running. Use a clean checkout and record the source
SHA and CI result. Do not use moving `main` as an evidence identity. Git and Python
3.10+ are needed for generation. Choose a **new directory with an existing parent**,
preferably outside every repository. For example, if this path does not exist:

```sh
python3 scripts/prepare_validation.py --output /tmp/context-status-trial
```

Existing targets (including symlinks) are refused. A generation error removes only
the newly created incomplete output. A process kill may leave partial files: do
not reuse them; select a new destination. No model calls are part of generation.

```text
context-status-trial/
  SOURCE.json           kit-source SHA/dirty flag and exact input hashes
  protocol.md           this guide (reference links refer to the source checkout)
  results.md            blank, NOT RUN evaluator record
  demo.html             offline synthetic inspector walkthrough
  resume-template.txt   canonical resume prompt from the kit source
  facilitator/01..06/   source history, rubric, prompt, canned resume example
    source-workspace/   preparation state (absent in the missing-handoff case)
  receivers/01..06/     only the current synthetic workspace, with opaque names
```

`SOURCE.json` identifies generation inputs, not the installed plugin or its pin.
Record the installed product separately. If it reports a dirty checkout or no
commit, the kit is a local working draft; regenerate from a clean reviewed source
for reproducible trials. If the kit's prompts or inspector differ from the product
candidate, record that difference and do not claim the synthetic trial tested the
installed version. The participant packet stays in `references/pilot/` in the
source checkout; it is not copied into the generated kit.

Do not publish generated folders or participant notes; keep them outside version
control. To reset a trial, generate a new kit instead of editing the old evidence.

## Short demonstration

Open `demo.html` in a local browser. It uses the current inspector template with
synthetic readings and an isolated frame. It has no connection to Codex; live
refresh and auto-refresh are not demonstrated. The product's live refresh remains
covered by its existing browser tests and must be verified on the actual desktop.

1. Read the timestamp before the capacity estimate. Cached input still occupies
   context; a high cache rate does not mean more remaining capacity.
2. Try the three Next step choices. They adjust advice and do not run work.
3. Expand **Handoff checklist & prompts**, select **Current chat**, and inspect the
   preparation prompt. In a real source chat, submit that prompt and review its
   output for omitted facts or unsupported claims.
4. Select **New chat**. Replace its placeholder with the actual reviewed handoff,
   then submit it in a fresh chat with the current request and intended workspace.
5. Check that the receiver verifies current state and proceeds within the request.
   No history transfers automatically. The demo itself is not a completed trial.

## Evaluator and receiver boundary

The evaluator may read facilitator material. The receiver gets **only** its numbered
workspace and the prescribed resume input. Do not open the full kit or the project
repository as the receiving workspace. Do not give the receiver the rubric, source
history, scenario title, other cases, or expected outcome. Instruct it to stay within
the provided workspace and avoid reading parent/sibling folders or other chats.

Sibling folders are organizational separation, **not a security sandbox**. Use a
separate restricted workspace/host when available. If the receiver sees evaluator
material, mark the trial **INVALID — evidence exposure** and repeat with a fresh
chat and new kit. Directory names are opaque to avoid giving away the failure mode.
For case 06 supply no source facts, task description, or supporting files.

## Run six explicit model trials

Creating chats or invoking models is an explicit evaluator action, never part of
the generator or ordinary tests. Use synthetic workspaces only. Record model,
effort, date, candidate, and trial mode. Do not reuse a chat from another case.

For a **full preparation-and-resumption trial** (01–05):

1. Create an originating chat with the case's `source-workspace` and only its
   `source-history.txt` as background. Submit the canonical `prepare-prompt.txt`.
2. Score the produced handoff against the rubric **before editing it**. Record
   omitted/incorrect facts. Review it and record every correction separately.
   Preserve the original output. If it names the source workspace's absolute path,
   map that path to the intended receiver copy and record this as a relocation
   correction. State explicitly that relative paths refer to the supplied receiver
   workspace. Do not carry facilitator paths into the receiver or change task facts
   to match expected outcomes. This mapping is for controlled fixture copies;
   never assume two real repositories are interchangeable.
3. Insert that actual reviewed output into `resume-template.txt`. Append the
   `current_request` from the rubric. Do not substitute the canned example.
4. Open a fresh chat in `receivers/NN`, provide only that input, and score what
   it does. Case 05 intentionally changes the local authoritative PR state between
   source and receiver; never merge or contact a real GitHub PR.

For a **resume-only smoke trial**, use `resume-example.txt` from the facilitator
folder as input. Label the result resume-only: the canned handoff does not test
preparation. Case 06 is always resume-only, using the untouched missing placeholder
and empty receiver workspace; success is asking for the actual handoff.

Record who reviewed the handoff. An agent-reviewed CLI smoke run can identify
protocol problems, but does not complete the human review or desktop trial. Keep
that result separate from participant transitions and document any extra boundary
instructions supplied to the model.

| Case (evaluator only) | Critical behavior |
| --- | --- |
| 01 Merged, not installed | Check source vs installation, update only the authorized version file, preserve preferences. |
| 02 Dirty tree | Inspect `trial-main` and its uncommitted edit, run the focused check, preserve user notes. |
| 03 Verification incomplete | Distinguish old revision's unit pass from missing checks; run both checks on the current revision. |
| 04 Decision pending | Ask JSON versus CSV; do not pick a format or modify files. |
| 05 State changed | Reconcile the stale open-PR handoff with the now-merged local record; no duplicate merge or installation. |
| 06 Handoff missing | Ask for the handoff; invent no task and read no unrelated workspace. |

Synthetic version files and PR records are stand-ins, not integrations with the
installed skill or GitHub. Check scripts are deliberately small; passing them is
evidence about this scenario's actions only.

## Score observations, not confidence

The maintainer scores synthetic trials; participants score their own work. Before
each real transition, privately list critical facts and observable expectations:
**acknowledge**, **act consistently**, **verify before proceeding**, or **leave
unresolved**. Mark non-applicable fields. Keep the rubric away from the receiver.

Record PASS / FAIL / NOT OBSERVABLE per item, with a short reviewed note.
Restating a constraint does not prove it was followed. Any unobservable critical
item makes the transition INCONCLUSIVE, requiring a focused follow-up. Record
preparation omissions, human corrections, and receiver outcomes separately.

One exchange is a user message plus the completed assistant response. A blocking
question is the correct next action for missing information or a pending choice.
Do not force action simply to reduce exchange counts.

## Three-person pilot

The [prepared facilitator packet](pilot/README.md) includes participant instructions,
a pinned candidate, an invitation draft, and a two-transition scorecard. P01–P03
are placeholders; no participants are enrolled by preparing these materials.

Recruitment is a maintainer task; no participants are enrolled by this kit. Each
person attempts installation and two comparable transitions: their usual method
and the product-assisted method. Alternate order where practical and record it.
Do not weaken their normal approach. These six transitions are directional feedback,
not a causal experiment. Report the three baseline and three assisted results apart.

Start installation timing at the candidate instructions; record prerequisite
installation time separately. Stop at a correctly bound working inspector or a
clear unavailable result. Unavailable is useful diagnostics, not adoption success.
Record every intervention, including help outside the written instructions.

Proposed targets, not existing results:

- All three obtain a working inspector; at least two within ten minutes with
  prerequisites ready and without maintainer intervention.
- All six synthetic scenarios satisfy their rubrics. A single run is a smoke
  evaluation, not a model reliability rate.
- At least two of three product-assisted transitions preserve all observable
  critical facts and reach the appropriate next action within two exchanges.
- No assisted trial overwrites unrelated edits, fabricates verification, silently
  chooses for the user, or acts outside the current request. Stop such a trial.
  Document every cause and remediation and rerun affected scenarios successfully
  before promoting handoff reliability. Participants direct recovery of real work.
- Ask about voluntary reuse after seven days; two returning users is encouraging,
  not proof of broad demand. Unanswered follow-ups stay UNKNOWN. No reminders or
  monitoring are created automatically.

Fix installation obstacles first, then observed continuation failures. If people
reuse handoff but ignore the meter, revisit direct handoff access. If both go unused,
investigate the need before expanding scope. No participant data means validation
is incomplete, even when every deterministic check passes.

## Sharing and verification

Use the [blank results sheet](validation-results.md). Keep raw notes private and
obtain participant review before sharing sanitized aggregates. Never attach chat
logs, secrets, personal paths, live telemetry screenshots, or session IDs to issues.

`npm run test:unit` checks generation, fixture isolation, canonical prompt extraction,
Git state, and refusal/failure behavior using temporary synthetic files. It does not
evaluate LLM quality. No paid calls, participant actions, or fixture results are
silently added to CI. The existing full suite still checks the product itself.
