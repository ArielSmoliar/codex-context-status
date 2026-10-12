# Try context-status in your workflow

Context-status is a community-maintained inspector for local Codex desktop chats. It shows
recorded context estimates and offers prompts for preparing and resuming a handoff.
We want to learn whether installation works for you and whether it helps you carry
work into a fresh chat. Problems and non-use are useful results.

You will try two comparable task transitions: one your usual way and one using
context-status. The facilitator will tell you which comes first. Keep using your
normal tools for the usual-method task. Do not paste these instructions or your
scorecard into the receiving model; they are for you.

## Before the assisted task: install

This pilot uses **plugin 0.1.2**, pinned to `bd55ab5bdd87b7366baa533b4db4d7650e377bd3`.
Use these participant instructions; the source checkout at that product commit
contains earlier pilot instructions for a different candidate. The facilitator records the revision
of this packet separately from the product being installed.

Start recording installation time when you reach these instructions. Requirements:
Git, Node.js 20+, Python 3.10+ with IANA timezone data, a Codex CLI with `plugin add`
(tested on 0.160.0), and local Codex desktop with MCP Apps and readable local logs.
Record prerequisite setup time separately. Prior live verification covers macOS
desktop 26.1007.21159; record your actual build, including unsuccessful attempts.

Check prerequisites from the environment that launches Codex:

```sh
git --version
node --version
python3 --version
python3 -c "from zoneinfo import ZoneInfo; ZoneInfo('UTC')"
codex --version
codex plugin add --help
```

If a check fails, ask for help and record the intervention before continuing.
The plugin needs the default `~/.codex` data directory. If your Codex installation
uses a custom `CODEX_HOME`, stop this plugin installation attempt and record it as
UNAVAILABLE with the reason “custom data directory.” Do not change your data
location to fit the pilot. A separate standalone trial may be arranged, but does
not count as a successful plugin installation.

If you already have context-status installed as a standalone skill, a manually
registered MCP server, or a plugin/marketplace, stop and ask the facilitator to
review it first. Preserve existing files and configuration. Record any migration
or change of marketplace ref as an intervention; do not silently replace it or
run both installations. The pinned [migration and recovery guide](https://github.com/ArielSmoliar/codex-context-status/blob/bd55ab5bdd87b7366baa533b4db4d7650e377bd3/references/plugin.md)
explains how to retain and restore a standalone installation.

For a new installation, run the first command and confirm it succeeds before
running the second:

```sh
codex plugin marketplace add ArielSmoliar/codex-context-status --ref bd55ab5bdd87b7366baa533b4db4d7650e377bd3
codex plugin add context-status@codex-context-status --json
```

The install result should report version **0.1.2**. Confirm the marketplace was
added with the exact commit above; a version number alone does not identify a
commit. Retain command results locally. If the pin or version is different or
cannot be verified, stop and ask for help. Do not run marketplace upgrades during
the pilot. No npm installation or manual MCP registration is needed.

Verify the cached marketplace commit with this read-only check (it prints only
the commit SHA):

```sh
python3 - <<'VERIFY_PIN'
import json, subprocess
result = subprocess.check_output(
    ["codex", "plugin", "marketplace", "list", "--json"], text=True)
market = next(item for item in json.loads(result)["marketplaces"]
              if item["name"] == "codex-context-status")
print(subprocess.check_output(
    ["git", "-C", market["root"], "rev-parse", "HEAD"], text=True).strip())
VERIFY_PIN
```

The result must be `bd55ab5bdd87b7366baa533b4db4d7650e377bd3`.
The marketplace listing alone does not display this commit. If the check errors
or differs, stop and ask the facilitator; keep it as a recorded setup issue.

Restart Codex if needed, open a local chat, and select the installed Context Status
skill (it may appear as `context-status:context-status`), or ask “Show the
context-status inspector for this chat.” Record any restart or discovery trouble.

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

## After the trial

You may keep the pinned plugin for the seven-day follow-up or remove it at any
point. Choosing removal is valid feedback. For a new installation created only
for this pilot:

```sh
codex plugin remove context-status@codex-context-status
codex plugin marketplace remove codex-context-status
```

Close the inspector and restart Codex if needed. Removal does not delete chats,
logs, or saved handoffs. If you had an existing setup, ask the facilitator to
restore its recorded state using the migration/recovery guide instead. Record
removal or restoration failures; do not delete unrelated configuration.

## What to share

Use brief observations on the private scorecard. No chat transcripts, personal
paths, session IDs, or telemetry screenshots are requested. You review any notes
before public sharing, and you may skip questions or stop participating.

Tell us what helped, what was confusing, and whether you would use the meter,
handoff prompts, both, or neither again. Around seven days later, we will ask whether
you chose to reuse it. You do not need to keep using it for the pilot to be useful.
