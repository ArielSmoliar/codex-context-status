# Context Status privacy notice

Publisher: Ariel Smoliar. This notice describes the Context Status plugin and
standalone skill distributed from the
[project repository](https://github.com/ArielSmoliar/codex-context-status).
It applies to the software described here; OpenAI and GitHub operate their own
services under their own policies.

## Purpose and data processed

Context Status provides recorded context-usage diagnostics for a selected local
Codex chat. It receives the exact chat identifier and an IANA timezone. It looks
up that chat's local rollout path in Codex's state database using a read-only
connection, or searches session filenames for that exact identifier, and verifies
the log's recorded identity.

The reader opens a fixed-size snapshot of the JSONL file and parses its records.
The file can contain prompts, messages, tool results, and other conversation data.
These records are encountered during local parsing; the inspector does not return
conversation bodies, instructions, tool outputs, or compaction summaries.

The MCP response contains allowlisted token counters, estimates, cache metrics,
recorded model/reasoning metadata, event timestamps, compaction/model-transition
counts, compatibility diagnostics, and the chat identifier and timezone needed to
bind and display the inspector. It omits source paths and account quota records.

## Recipients and network activity

The local server returns display data to the Codex host. The initial tool result
is available to Codex like other tool results and is subject to the user's OpenAI
plan, settings, and applicable policies. This plugin does not change those rules
or promise that every tool result stays solely on the device.

The plugin adds no remote telemetry endpoint, analytics collector, or external UI
resources. GitHub is contacted by the installation/update workflow to obtain the
package. The local inspector's refresh operation does not start a model turn.

## Retention and controls

The MCP reader does not modify session logs or create a separate persistent
telemetry database. It reads a new snapshot for each refresh. The open inspector
holds display state in memory; Codex may retain tool results in its own chat and
application storage under its own retention rules. We do not set a deletion period
for records controlled by Codex.

The optional inline fallback writes a local HTML snapshot at the selected output
path. It remains until the user deletes it. Any handoff saved by the user or Codex
is a separate artifact and remains until removed by its owner.

Users can turn Auto-refresh off, close the inspector, disable or uninstall the
plugin, and delete any saved fallback artifacts. Auto-refresh pauses while hidden
and stops after three consecutive failures. Uninstalling does not delete Codex
logs, chat history, saved handoffs, or a separate standalone installation.

## Handoffs and support

Copying a handoff prompt does not send a message. Submitting the prompt in Codex
uses the normal Codex workflow and data handling. Review any generated handoff
before sharing it or pasting it into another chat.

General support is available through
[GitHub issues](https://github.com/ArielSmoliar/codex-context-status/issues).
Content posted there is public and subject to GitHub's terms and retention rules.
Do not attach logs, chat identifiers, credentials, private paths, or personal
telemetry screenshots.

For private privacy requests, email
[ariel.smoliar@gmail.com](mailto:ariel.smoliar@gmail.com). The publisher uses your
email address and the information you choose to send to respond to your request.
Those messages are handled through the publisher's email provider; they are not
automatically collected by the plugin. Please describe the issue without sending
raw conversation logs or credentials. You can use this address to request removal
of information you sent to the publisher; records controlled by OpenAI or GitHub
need to be managed through those services.
