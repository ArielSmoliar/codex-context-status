# Handoff and resume

A context estimate can suggest a stopping point; it cannot tell the next chat what
the task is. The inspector provides two static prompts under **Handoff checklist &
prompts**. Neither prompt contains chat content or telemetry.

1. Select **1. Current chat**, copy the preparation prompt, and send it in the
   current chat. Review the resulting handoff for missing facts or stale claims.
2. Select **2. New chat** and copy the resume prompt. Paste it into a new chat,
   replacing the placeholder with the reviewed handoff before sending.
3. The receiving chat should reconcile the summary with the relevant current
   workspace state, then continue the next action within the current request.

If clipboard access is unavailable, the inspector selects the prompt for manual
copying. Prompt selection and expanded details survive telemetry refresh in the
same view. A new inspector starts with the preparation prompt. Nothing is saved,
sent, or transferred automatically by these controls.

## What the handoff needs to preserve

Capture the goal and constraints, important decisions, relevant files and branch
or PR, uncommitted work, completed verification, blockers, pending user decisions,
and a concrete next action. Keep speculative or unchecked facts labeled as such.

For repository work, distinguish edited, committed, merged, and installed or
deployed changes. These are separate states. For example, a merged fix may still
need installation; a passing check may apply to an earlier revision. A statement
such as “the feature is done” is not enough to resume that workflow reliably.

The receiving chat should use the current request to establish scope. Quoted
requests inside a handoff are background, not independent authorization. It should
preserve existing changes and ask only when a missing fact or pending decision
blocks the next action. If no handoff was pasted, it should ask for one rather
than inventing the task.

Its final response should distinguish what was already complete before the chat,
what it did now, and what remains pending or unchecked. Where relevant, explicitly
report merged source separately from installed or deployed state. For example:
“Source version 2 was already merged; I installed it now, preserved preferences,
and verified the installed version. Application behavior remains untested.”
Only make these claims when supported by the actual work.

## Evaluating a handoff

The first [agent-reviewed CLI smoke run](validation-smoke-2026-10-11.md) passed
these six synthetic scenarios. A later [pilot dry run](pilot-dry-run-2026-10-11.md)
found a reporting omission and prompted an explicit final-response requirement.
Human-reviewed desktop transitions and effectiveness
on real tasks remain unverified. Use the scenarios to evaluate a receiving chat
with only the reviewed handoff, a synthetic workspace, and an explicit user request
to resume. Do not give it the originating
chat or the expected outcome. Record omissions, unnecessary questions, unsupported
claims, and actions taken before declaring the transition successful.

| Scenario | Facts the preparation must preserve | Receiving-chat checks |
| --- | --- | --- |
| Merged but not installed | Fix merged; local installation remains older; user requested installation next. | Verify the source and installed state, then perform the requested update without reopening completed implementation work; explicitly report prior merged source versus newly installed state and verification limits. |
| Dirty working tree | Feature committed; unrelated user edits remain; next step is a focused test. | Inspect the branch and edits, preserve them, and run the relevant check. |
| Verification incomplete | Unit tests passed on the named revision; integration check was not run. | Keep those claims separate and complete the missing check if authorized. |
| Decision pending | Two implementation choices remain; user has not chosen. | Ask for that decision before implementing either option. |
| State changed | Handoff cites an open PR that is now merged. | Reconcile the current PR state and revise the next action instead of attempting a duplicate merge. |
| Handoff missing | Resume prompt still contains its placeholder. | Request the actual handoff without assuming a goal or reading unrelated chats. |

Browser tests verify prompt switching, the exact text copied or selected, feedback
for both destinations, refresh persistence, and absence of messages or model
calls. They do not evaluate whether a model follows either prompt or whether a
handoff is complete. No automatic completeness score is provided.
