# Synthetic handoff smoke results — October 11, 2026

**Six scored receiver trials passed their scenario rubrics.** Five used actual
model-generated handoffs, reviewed and corrected by an agent before transfer.
The sixth tested a missing handoff. These are agent-reviewed CLI observations,
not human-reviewed desktop trials, a model reliability rate, or adoption evidence.

## Candidate and method

- Candidate: `b0a8db4bbf4a8d966971f1fcd1aa4b8847aa8c59`, clean checkout.
  Its [PR #8](https://github.com/ArielSmoliar/codex-context-status/pull/8) passed both
  CI matrix configurations and was squash-merged as
  `1f5d328e5de2862d1c3c248b9bf14937ab7543b3`. Trials used the candidate SHA.
- Runtime recorded by every scored invocation: Codex CLI `0.160.0`, model
  `gpt-6.1-sol`, reasoning effort `none`, provider OpenAI.
- Fresh ephemeral session for each invocation; user configuration ignored and
  web search disabled. Preparation used read-only mode; receivers used workspace
  write mode. These modes did not provide filesystem read isolation.
- Five preparation calls and six scored receiver calls. An additional case 06
  preflight also requested the missing handoff; it is not a seventh scored case.
- Each preparation session received only its synthetic source history, source
  workspace, canonical preparation prompt, and boundary instruction below.
  Each receiver received only its synthetic receiver workspace, canonical resume
  prompt with the reviewed handoff, current request, and boundary instructions.
  Case 06 received the unfilled resume prompt, empty workspace, and boundary
  instruction, with no task facts.
- The evaluator could read rubrics and source histories. These were withheld from
  receiver inputs. No recorded command explicitly opened evaluator material or
  another workspace's files. Tool traces do not establish complete filesystem
  isolation: Git discovery and shell configuration can read beyond the working
  directory. Directory separation was organizational, not a security boundary.

Every invocation was given this additional instruction:

> Work only within the supplied working directory. Do not read parent or sibling
> directories, other chats, evaluator files, or personal configuration. Do not use
> external services or delegate work.

The model API was used to run the trials. No external-service tool calls were
observed. This evaluates prompts with an evaluator-supplied boundary instruction,
not their standalone behavior under arbitrary settings.

## Preparation and corrections

All five preparation outputs preserved the critical task facts on agent review.
No critical fact omissions were observed. All five also named their source
workspace's absolute path. The kit deliberately resumes in a separate copy, so
the evaluator replaced that exact source path with `.` and added:

> The supplied receiver workspace is the continuation location; all relative paths
> below refer to it. Historical source paths do not authorize reads outside it.

Each original output was preserved, and each relocation correction was recorded
before transfer. No task facts, decisions, verification claims, or next actions
were changed. Preparation was therefore not an unedited end-to-end pass. The
receiver results below apply to these reviewed inputs. No human reviewed the
handoffs during this run.

## Receiver observations

Each scored receiver reached the appropriate next action in one exchange. Asking
the blocking question was the intended action in cases 04 and 06.

| Case | Score | Observed behavior and verification |
| --- | --- | --- |
| 01 Merged, not installed | PASS | Read source and installed versions, preferences, and merged-state record. Changed only the authorized installed version file from 1 to 2; preferences remained byte-for-byte unchanged. Reported installation separately from merged source and explicitly left application behavior unverified. |
| 02 Dirty tree | PASS | Inspected `trial-main`, commit, status, and diff. Ran the focused banner check successfully. Preserved the exact uncommitted notes and reported only the check actually run. |
| 03 Verification incomplete | PASS | Read the current revision and historical verification record, distinguished the earlier unit pass, and ran both current checks successfully. Reported their limited revision-marker coverage; did not claim prior integration verification. |
| 04 Decision pending | PASS | Inspected the workspace and asked the user to choose JSON or CSV. Did not select a format; the export file remained unchanged. |
| 05 State changed | PASS | Read the authoritative local record showing the PR now merged, corrected the stale next action, and kept installation pending. Made no duplicate merge attempt, installation, or file changes. |
| 06 Handoff missing | PASS | Asked for the reviewed handoff, with no tool calls, invented task, or created files. |

After all runs, the evaluator compared every receiver file outside `.git` with
its expected postcondition. All matched. The five source workspaces also matched
their original fixture contents, including the deliberately uncommitted edit.
All scored model invocations exited successfully. Raw responses, tool traces,
correction records, and file comparisons remain local; they include machine paths
and session identifiers and are not publication artifacts.

## Implications and remaining work

The observed setup problem was workspace relocation between fixture copies. The
[trial protocol](validation.md#run-six-explicit-model-trials) now requires that
mapping to be reviewed and recorded. This finding alone does not justify changing
the product's handoff prompts.

These small synthetic cases used one model and effort setting, one scored run per
case, agent review, and explicit boundary instructions. They do not measure long
history retention, comparative benefit over normal handoffs, quality degradation,
or reliability across models. The fixture checks test small state transitions,
not real installations or GitHub operations. CLI results add no desktop
compatibility evidence.

Human-reviewed desktop trials, participant installation attempts, baseline and
product-assisted real-task transitions, and seven-day voluntary reuse are all
**NOT RUN**. The next step remains the approved three-person pilot. Its results
must be recorded separately using the [blank results sheet](validation-results.md).
