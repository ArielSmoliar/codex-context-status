# Installation and upgrades

Run the helper from a trusted checkout of the revision you want to install:

```sh
python3 scripts/install.py
python3 scripts/install.py --apply
```

The first command is a read-only preview. The second repeats the comparison and
applies a conflict-free plan. It installs an explicit list of runtime and support
files into `${CODEX_HOME:-$HOME/.codex}/skills/context-status`, the location used by
the desktop installation verified for this project. Use `--codex-home PATH` for
another known local data directory. It does not download code, install dependencies,
edit `config.toml`, inspect chats, or start/restart Codex.

The helper prints shell-quoted setup commands using the selected home and absolute
Python/Node paths when Node is available. Run the dependency command, inspect any
existing `context-status` MCP registration, and register the installed server when
needed. Preserve custom settings before replacing a registration. Registration uses
the [official Codex MCP CLI](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
Runtime readiness and MCP Apps support still need verification in the desktop.

## Existing installations

| Detected state | Behavior |
| --- | --- |
| No installation | Preview added files; `--apply` creates the managed copy. |
| Managed and unchanged | Upgrade changed package files; preserve extra files and dependencies. |
| Already current | No writes or backup. |
| Local edits or deletions | List conflicts and stop before changing files. |
| Existing copy without a manifest | Leave it alone; `--adopt` enables a comparison. |
| Symlink | Leave the link and its target alone; update that checkout directly. |
| Invalid manifest or managed symlink | Stop; do not guess ownership or follow the link. |

An upgrade uses `.context-status-install.json` hashes to distinguish the previous
package from local changes. Files are replaced or removed only when unchanged from
that manifest, or when already identical to the incoming package. Untracked files
that collide with a new package file also stop the upgrade. There is no force flag.

For a matching older copy:

```sh
python3 scripts/install.py --adopt
python3 scripts/install.py --adopt --apply
```

Adoption accepts only matching packaged files or missing files that can be added.
It cannot establish whether a differing file is a customization or an older
upstream version. Compare reported conflicts manually and keep any edits before
retrying. Extra files remain in place. A copy that differs substantially can instead
be backed up outside the skills directory and replaced with a fresh installation.

## Backups and recovery

The installer prepares a staged directory, verifies it, and checks the existing
tree again before replacement. Each applied upgrade/adoption retains the full
previous directory under `CODEX_HOME/context-status-backups/<unique-id>`, outside
skill discovery. The printed backup path is the recovery copy. Dependencies and
personal files in that directory are included, so upgrades require enough free
space for a complete second copy. Backups are not deleted automatically.

An ordinary failure publishing the staged directory restores the previous one.
A process kill, power loss, or concurrent external edit in the final replacement
interval is not covered by a transactional filesystem guarantee. Avoid editing the
installed directory or running two installers during apply. If interrupted, inspect
the printed destination, backups, and `.context-status-stage-*` directories before
removing a leftover `.context-status-install.lock` and retrying.

To restore a backup, stop the MCP server (or close Codex), move the current
installation to a separate safe location, and move the chosen backup back to the
original `skills/context-status` path. Restore dependency versions with the backup's
lockfile if needed. The installer never changes the MCP registration, so its path
normally remains the same. Reopen Codex and the inspector to verify the result.

## What needs reloading

| Changed component | Next step |
| --- | --- |
| Python telemetry reader | The next refresh starts a new reader process. |
| Inspector HTML, CSS, or bridge | Open a new inspector; an existing view retains its loaded UI. |
| MCP server code or dependencies | Restart the local MCP server through the host, or restart Codex. |
| MCP registration or runtime paths | Reload the host's MCP configuration; restart Codex if tools remain old or unavailable. |
| Skill instructions | Codex detects skill changes; restart if the update does not appear. |

Refresh fetches telemetry; it does not replace an already loaded UI or running
server. The skill reload behavior is described in
[OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).
That documentation also lists other discovery locations, including
`~/.agents/skills`; this helper does not relocate or reconcile installations across
those locations. Avoid creating duplicate copies with the same skill name.
