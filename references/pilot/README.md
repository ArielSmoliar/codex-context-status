# Three-person pilot: facilitator packet

Status: **PREPARED, NOT RUN**. P01–P03 are placeholders, not enrolled participants.
No invitations or follow-ups have been sent. Use this alongside the
[validation protocol](../validation.md); the six synthetic CLI passes are a
separate result, not a substitute for these real-task observations.

## Candidate

Use `b19f0a01a18c126a2c69615eef3f4285c73b2c61` for every installation. This is the
reviewed PR #9 head, whose [CI run](https://github.com/ArielSmoliar/codex-context-status/actions/runs/38179557458)
passed Node 20/Python 3.10 and Node 22/Python 3.12. The candidate is frozen even if
`main` advances. Record any deviation and assess it separately. Only macOS desktop
26.1007.21159 has prior live verification; record other builds as new evidence.

## Recruit and arrange

Choose daily Codex desktop users who already restart long tasks. Prefer people
who did not build this tool. Confirm their local desktop, OS, ability to install
Node/Python dependencies, and two upcoming task boundaries. Record prior exposure
to context-status. Names and contact details stay outside this repository.

Invitation draft, for the maintainer to send when ready:

> I’m testing context-status, an open-source context inspector and handoff aid for
> Codex desktop. Would you try installing it and continuing two comparable tasks
> in fresh chats, once your usual way and once using its handoff prompts? Plan for
> about 30–45 minutes, possibly split across natural task boundaries, plus a short
> check-in seven days later. Use work you’re comfortable testing; you can stop at
> any point. We’ll ask for brief observations, not chat transcripts. Setup failures
> are useful feedback too. It estimates recorded usage; it does not diagnose model
> quality. Would this fit how you work?

The time estimate is for scheduling, not a success criterion. Participant model
usage remains subject to their usual Codex limits. Agree on timing and permission
to share sanitized observations; agreement to participate is not publication consent.

| Placeholder | Proposed order | Enrollment | Session date | Seven-day check-in |
| --- | --- | --- | --- | --- |
| P01 | Usual method → assisted | NOT ENROLLED | Unscheduled | Unscheduled |
| P02 | Assisted → usual method | NOT ENROLLED | Unscheduled | Unscheduled |
| P03 | Usual method → assisted | NOT ENROLLED | Unscheduled | Unscheduled |

Give each person [participant instructions](participant.md) and a private copy of
the [scorecard](scorecard.md). Keep completed cards outside any repository and
outside the receiving chat's workspace. Replace the alias and planned order in
each copy. The participant scores their work; the facilitator records help given.

## Run the session

1. Ask for one recent restart: what went wrong, what they tried, and what happened
   next. Record a short account without inferring that context caused the problem.
2. Select two different, comparable real task boundaries before starting. Avoid
   replaying the same completed action. Record differences in task complexity,
   history length, model, and effort. Keep their normal tools available.
3. Follow the assigned order. For P01/P03, do the usual-method transition before
   installation or product coaching where practical. P02 sees the product first;
   record learning carryover when they later use their usual method. Do not ban
   techniques they normally use or coach the baseline into a weaker approach.
4. For each transition, have the participant privately predeclare the important
   facts and observable expectations on their scorecard. Keep this rubric, the
   packet, and the other task's history out of the receiving model's inputs.
5. Time installation from the candidate instructions. Record prerequisite setup
   separately. Observe without coaching initially; when help is needed, provide it
   and record exactly when and what. Do not leave someone stuck to protect a metric.
6. Score the actual preparation and receiver behavior separately. Preserve original
   handoffs locally when useful, but do not collect transcripts. A question can be
   the correct next action. Record any correction or assistance before transfer.
7. Ask what they would use again, what felt unnecessary, and whether the meter
   influenced a decision. Do not lead with our desired answer or success thresholds.

If installation is unavailable or fails, retain the attempt and its build in the
denominator. The usual-method transition may still run; mark an unattempted assisted
transition NOT RUN and explain why. Do not silently replace a participant or count
an unavailable inspector as working. Additional participants are a separate cohort.

Stop an assisted trial if it overwrites unrelated work, invents verification,
silently chooses a pending decision, or acts beyond the current request. Let the
participant direct recovery. Document the cause, fix, and successful focused rerun
before promoting reliability. Never reset a real workspace to recreate a trial.

## Follow up and decide

Seven days after each person's assisted trial, manually ask: Did you voluntarily
use context-status again? What did you use, the meter, handoff, or both? Describe
one occasion. If not, what got in the way? Would you keep it installed, and why?
Record dates, responses, and reminders if any; an unanswered question is UNKNOWN.
This packet does not schedule or send anything.

| Observation | Planned | Attempted | Successful | Failed / inconclusive | Not run |
| --- | --- | --- | --- | --- | --- |
| Working inspector installations | 3 | 0 | 0 | 0 | 3 |
| Usual-method transitions | 3 | 0 | 0 | 0 | 3 |
| Assisted transitions | 3 | 0 | 0 | 0 | 3 |
| Seven-day reuse responses | 3 | 0 | 0 | 0 | 3 |

Keep actual results in the private packet. Success targets from the approved plan:
all three get a working inspector, at least two within ten minutes with prerequisites
ready and without maintainer intervention; at least two assisted transitions
preserve every observable critical fact and reach the right next action within two
exchanges; zero unresolved prohibited-action failures. Two voluntary returning
users would support expanding the pilot. Report baseline results alongside assisted
results and distinguish responses received from confirmed reuse.

These are directional targets for three people, not causal or reliability claims.
Fix setup obstacles first, then observed continuation failures. If handoff is reused
but the meter is ignored, reconsider direct handoff access. If neither is reused,
investigate the need before adding features. Missing participants or follow-up means
validation remains incomplete. Only participant-approved, sanitized findings may
be shared publicly; omit transcripts, personal paths, chat IDs, and live telemetry.
