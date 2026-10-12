# Local MCP eligibility inquiry

**Sent through the Help Center; escalated to a support specialist October 11, 2026.**
Awaiting a substantive reply. This is the reusable inquiry text, not a support
transcript; the actual exchange and account artifacts are kept private.
No account identifiers, personal logs, or live telemetry are needed as attachments.

**Subject: Local MCP support for Context Status — uploaded plugin draft**

Hello,

I maintain Context Status, a GitHub-distributed plugin for Codex desktop. It shows
estimated context capacity, cache reuse, recorded model changes and compaction
activity, with in-place refresh and session-handoff guidance.

The plugin uses a local stdio MCP server. Given the exact current chat ID, it
queries local Codex state read-only to locate that session's log, verifies its
identity, and parses the local JSONL records. Those records can contain
conversation content; the plugin returns only selected usage counters, model
metadata, timestamps, diagnostics, and the chat ID needed to bind Refresh. It
does not return message bodies, instructions, tool output, or source paths.
It adds no remote telemetry service. Initial tool results remain subject to
Codex's own data handling; in-place refresh does not start a model turn.

I have uploaded the current package directly through OpenAI Platform under my
verified individual publisher identity. The draft was created successfully, but
its blocking findings include:

> Command MCP Server detected: We recommend using MCP servers with an URL. Please contact your OpenAI representative to submit plugins with command line MCPs.

Plugin ID: `plugins_6acc2135f1008191a51a1284f57fb595`

Draft: https://platform.openai.com/plugins/manage/plugins_6acc2135f1008191a51a1284f57fb595

The uploaded draft is version 0.1.1. Its metadata corrections cleared the reported
listing findings, but the local command MCP blocker remains and the skill scan was
last observed pending. The local stdio architecture is unchanged. No review has
been submitted.

Could you route this to the team supporting local MCP submissions and clarify:

1. Can this draft be enabled for local command/stdio MCP review, and what package
   configuration or approval is required?
2. Does this telemetry-only extraction from a user-selected local session comply
   with the chat-log data-boundary requirement? If not, is there a supported
   host-provided telemetry resource or integration we should use?
3. Can the listing be explicitly limited to Codex desktop, given that it cannot
   operate in ChatGPT web/mobile or chats without local logs?
4. What isolated reviewer setup and evidence would you require for this scope?

The current package supports the default Codex data directory, requires Node 20+
and Python 3.10+, and has limited macOS desktop compatibility evidence. We can
provide synthetic fixtures, lifecycle test evidence, and a walkthrough. We would
like to preserve local telemetry processing rather than expose users' logs through
a hosted endpoint.

Source: https://github.com/ArielSmoliar/codex-context-status

Website: https://codex-context-status.major-cabin-5392.chatgpt.site/

Thank you,
Ariel Smoliar
