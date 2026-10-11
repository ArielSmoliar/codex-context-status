# Try context-status in your workflow

Context-status is an open-source inspector for local Codex desktop chats. It shows
recorded context estimates and offers prompts for preparing and resuming a handoff.
We want to learn whether installation works for you and whether it helps you carry
work into a fresh chat. Problems and non-use are useful results.

You will try two comparable task transitions: one your usual way and one using
context-status. The facilitator will tell you which comes first. Keep using your
normal tools for the usual-method task. Do not paste these instructions or your
scorecard into the receiving model; they are for you.

## Before the assisted task: install

Start recording installation time when you reach these candidate instructions.
Prerequisites are Git, Node.js 20+, Python 3.10+ with timezone data, the Codex CLI
for MCP registration, and a local Codex desktop with MCP Apps support and accessible
local telemetry. Record time spent obtaining prerequisites separately. Prior live
verification covers macOS desktop 26.1007.21159; your build may differ.

In a folder where you keep checkouts, run:

```sh
git clone https://github.com/ArielSmoliar/codex-context-status.git codex-context-status-pilot-b19f0a0 &&
cd codex-context-status-pilot-b19f0a0 &&
git checkout --detach b19f0a01a18c126a2c69615eef3f4285c73b2c61 &&
git rev-parse HEAD &&
git status --short
```

The SHA should match and status should be empty. If the destination folder already
exists, use a new folder name rather than replacing it. Once those checks match, preview the installation:

```sh
python3 scripts/install.py
```

If the preview reports conflicts, stop and ask for help; retain your existing
settings. If it is correct:

```sh
python3 scripts/install.py --apply
```

Run the dependency command printed by the helper. Inspect any existing
`context-status` MCP registration before running its printed registration command;
preserve custom settings. Restart Codex if needed, open a local chat, and invoke
`$context-status`. Full [setup, reload, and recovery instructions](https://github.com/ArielSmoliar/codex-context-status/blob/b19f0a01a18c126a2c69615eef3f4285c73b2c61/references/installation.md)
are part of this candidate. Ask for help whenever needed; record that intervention.

Confirm the inspector belongs to this chat and its Telemetry checks show verified
identity. After a completed response, check that a new recorded timestamp appears
and Refresh updates the same inspector. Auto-refresh starts on and polls every
15 seconds while visible. An unavailable reading is worth reporting, not a reason
to guess. Stop timing at a working, correctly bound inspector or a clear failed or
unavailable result. Keep prerequisite time and help separate.

## Your two transitions

Choose different tasks with reasonably similar complexity and a clear next action.
Before each transition, privately write the critical facts on your scorecard:
goal, decisions, current files or work state, checks actually run, pending choices,
and intended next action. Mark irrelevant items N/A. Note your model and effort.
The new chat should receive only what your chosen handoff method normally supplies
and your current request, never the scoring notes or the other task's history.

For the **usual-method transition**, start a fresh chat the way you normally would.
Use your usual notes, summaries, or tools. Record what happens without changing
your method to make it easier to compare.

For the **assisted transition**:

1. Open the inspector and inspect the timestamp, capacity estimate, and Next step
   choice. Decide for yourself whether this is a sensible task boundary. Do not
   wait for a particular percentage. Capacity is estimated, and the advice is not
   a diagnosis of declining quality or a known compaction threshold.
2. Expand **Handoff checklist & prompts**, select **Current chat**, and send its
   preparation prompt in the source chat. Review the result. Note omissions and
   unsupported claims before making corrections. Record every correction.
3. Select **New chat**, copy the resume prompt, and replace its placeholder with
   your reviewed handoff. Open a fresh chat in the intended workspace and add your
   current request. Check any workspace paths before sending. Files, history, and
   instructions are not transferred automatically.
4. Observe the first completed response and score what actually happened. If a
   clarification is needed, answer it and record the next exchange. A necessary
   question can be the right next step; do not force the model to act prematurely.

Stop and tell the facilitator if it changes unrelated work, claims checks it did
not run, makes a decision you left open, or acts beyond your request. You decide
how to recover your work. Keep ordinary workspace protections in place.

## What to share

Use brief observations on the private scorecard. No chat transcripts, personal
paths, session IDs, or telemetry screenshots are requested. You review any notes
before public sharing, and you may skip questions or stop participating.

Tell us what helped, what was confusing, and whether you would use the meter,
handoff prompts, both, or neither again. Around seven days later, we will ask whether
you chose to reuse it. You do not need to keep using it for the pilot to be useful.
