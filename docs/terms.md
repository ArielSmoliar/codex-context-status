# Context Status terms of use

Publisher: Ariel Smoliar. These terms cover Context Status, the local Codex plugin
and standalone skill distributed through the
[project repository](https://github.com/ArielSmoliar/codex-context-status).

## Intended use

Context Status helps you inspect recorded context usage in a local Codex chat and
prepare a handoff. Use it only with local session data you are authorized to
access. Installing this plugin does not grant access to another person's chats
or change your permissions in Codex.

## Requirements and limitations

The plugin requires a compatible local Codex desktop environment with MCP Apps,
Node.js 20+, and Python 3.10+ with timezone data. The packaged MCP server currently
supports the default Codex data directory. Compatibility evidence is limited;
see the [compatibility record](../references/compatibility.md).

The inspector reports the last available telemetry. Capacity is an estimate,
and missing or delayed data can affect its advice. It does not diagnose model
quality, predict automatic compaction, or guarantee that a fresh chat will improve
results. Review its guidance and any generated handoff before relying on them.

## Privacy and your choices

The [privacy notice](privacy.md) explains local log processing, the limited data
returned to Codex, and optional saved artifacts. You can stop polling, close the
inspector, or uninstall the plugin. Removal does not delete Codex history or
separate artifacts you saved.

## Support and third-party services

Report problems through [GitHub issues](https://github.com/ArielSmoliar/codex-context-status/issues).
Do not include private logs, identifiers, credentials, or personal telemetry in
public reports. This community project does not provide a guaranteed support
response time or service availability commitment.

Context Status is an independent project by Ariel Smoliar. OpenAI operates Codex,
and GitHub hosts the repository. Their services remain subject to their own terms
and policies. A directory draft or upload does not imply OpenAI approval.

## Source code and changes

These product-use terms do not establish an open-source license for the original
source code. The repository currently has no first-party LICENSE file. Bundled
third-party software remains governed by the licenses in
[THIRD_PARTY_NOTICES.md](../plugins/context-status/THIRD_PARTY_NOTICES.md).

Future releases may change compatibility, behavior, or these documents. Review
the version and repository history when upgrading. These terms do not claim to
waive rights that cannot be waived under applicable law.
