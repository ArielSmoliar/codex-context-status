# Install as a Codex plugin

Context Status is distributed through this repository's Git marketplace. It runs
a local stdio MCP server; there is no hosted telemetry service, analytics, API key,
install hook, or runtime dependency download. Node 20+ and Python 3.10+ with IANA
timezone data must be on the PATH available to Codex. The desktop must support
local MCP Apps. Remote chats without local logs can report unavailable telemetry.

## Install

Use a Codex CLI with `codex plugin add` support (tested with 0.160.0):

```sh
codex plugin marketplace add ArielSmoliar/codex-context-status --ref main
codex plugin add context-status@codex-context-status
```

Restart Codex if it does not discover the new skill or server. Select the
context-status skill in the composer, or ask “Show the context-status inspector
for this chat.” The host can namespace the skill as `context-status:context-status`.
The inspector opens in place with auto-refresh enabled. Refresh reads new data;
it does not load a new version of the widget.

For a reproducible installation, set `--ref` to a reviewed commit SHA or release
tag. A pinned ref stays pinned when the marketplace refreshes.

## Upgrade

```sh
codex plugin marketplace upgrade codex-context-status
codex plugin add context-status@codex-context-status
```

Refresh the marketplace first, then install the selected version. Restart Codex
and reopen the inspector so both the server and UI use the new package. Do not
edit the installed plugin cache: upgrades can replace it. Keep customizations in
a fork. To change a ref or roll back, remove the marketplace source first, then
re-add it with a known-good `--ref` and install again:

```sh
codex plugin marketplace remove codex-context-status
codex plugin marketplace add ArielSmoliar/codex-context-status --ref REVIEWED_COMMIT_OR_TAG
codex plugin add context-status@codex-context-status
```

Plugin releases must increment `packaging/plugin.json`'s version.

## Remove

```sh
codex plugin remove context-status@codex-context-status
codex plugin marketplace remove codex-context-status
```

The first command uninstalls the plugin and removes its cache. The second removes
the repository source from configured marketplaces. Restart Codex and close open
inspectors. These actions do not delete session logs, saved handoffs, standalone
skill installations, or manually registered MCP servers.

## Migrate an existing standalone installation

Use one installation mode at a time. First inspect `codex mcp get context-status
--json` and the standalone skill under your Codex home's `skills/context-status`.
Save the existing registration and move the skill to a backup directory outside
`skills/` (preserve local edits and symlinks). Then run `codex mcp remove
context-status` and install the plugin. Do not delete the old copy until the plugin
works in a new inspector. If switching back, remove the plugin, restore the
standalone skill, and restore its saved MCP registration. The plugin installer
does not migrate or overwrite those separate installations automatically.

## Privacy and troubleshooting

The server reads existing logs for an exact validated chat ID and returns
allowlisted display telemetry to the local Codex host. It never returns chat
bodies, credentials, or source paths, and does not write to the logs. The initial
tool result is available to Codex like any other tool result; this does not change
Codex's own data handling. In-place refresh makes no model call. The package adds
no network endpoint and no external UI resources. GitHub is contacted when Codex
downloads or upgrades the package, not when the inspector reads telemetry.

If startup fails, check `node --version`, `python3 --version`, and
`python3 -c "from zoneinfo import ZoneInfo; ZoneInfo('UTC')"` from the environment
that launches Codex. Installing Node/Python after Codex started may require a full
restart. If logs live in a custom Codex home, launch Codex with that existing
`CODEX_HOME` setting; never hard-code a user's path or a chat ID into the manifest.
Missing telemetry must remain unavailable, not substituted with another chat.

Packaging follows the [official plugin guide](https://developers.openai.com/plugins/build/plugins).
This GitHub distribution is separate from submission to OpenAI's public directory.
