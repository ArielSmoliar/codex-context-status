# Telemetry source and limits

Validated 2026-10-10 against a live Codex Desktop chat, CLI 0.162.0-alpha.17.2. The standard daemon control socket was absent. The chat's readable session log contained advancing `event_msg/token_count` and `token_usage_record` entries. This establishes access to persisted events, not a direct subscription. Other installations must be checked by running the helper.

The helper queries `state*.sqlite` read-only for the exact thread's `rollout_path`, then falls back to matching filenames in `sessions` and `archived_sessions`. It verifies `session_meta.payload.id`. It prints allowlisted telemetry only, never messages, instructions, tool output, credentials, or compaction summaries. It reads a fixed file-size snapshot and ignores an unfinished trailing line.

Supported local record shapes:

- `event_msg`, payload type `token_count`: `info.last_token_usage`, `info.total_token_usage`, `info.model_context_window`; optional `rate_limits`.
- `token_usage_record`: matching `thread_id`, `usage`, `turn_token_usage`, `thread_token_usage`. Usage with an explicit turn ID is accepted only for the currently recorded turn, preventing delayed prior-turn records from being attributed to a newly selected model; the separately recorded window is retained only if no model change intervened.
- `turn_context`: model, effort, and current turn identity.
- `compacted`, or `event_msg/context_compaction`: timestamps only.

Local storage formats are implementation details, not a stable public API. Missing fields stay unavailable. Revalidate after Codex changes.

The capacity estimate uses latest `total_tokens` (or input + output if total is absent). It describes the last recorded request footprint, not the exact next request. Reasoning retention, removed items, new tool results, and compaction can change occupancy. Remaining capacity is arithmetic headroom, not guaranteed usable output space. The reported runtime window may differ from the published model maximum. Cache reuse is cached input / input. Cumulative totals include repeatedly processed context, not unique context size. Per-turn totals are shown only for the current turn.

Unavailable: exact live occupancy, per-file/instruction/tool token attribution, compaction content diffs, automatic compaction threshold, and cache-miss causes. Missing data is not evidence of zero consumption.

Official interfaces for a future integration:

- [Codex app-server events](https://learn.chatgpt.com/docs/app-server#turn-events): `thread/tokenUsage/updated`; the generated schema contains `total`, `last`, nullable `modelContextWindow`, and token breakdowns. Compaction has an item lifecycle. A separate app-server does not automatically monitor the desktop's active thread.
- [Responses token counting](https://developers.openai.com/api/docs/guides/token-counting): counts a supplied request, not arbitrary desktop chats.
- [Prompt-cache diagnostics](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics): supported API requests only; not automatically available in Codex logs.

## Presentation

`scripts/render_status.py` combines the fresh measurements with `assets/inspector.html`. It includes only presentation fields, excluding the thread ID, session path, and account quota records. JSON is escaped before embedding; displayed strings use DOM textContent. The renderer requires only Python's standard library and browser-native APIs.

The user chose a compact inspector after consultation with Impeccable: capacity first, cache second, expandable technical details, Codex's theme, readable labels, keyboard access, and minimal motion. The capacity bar splits cached input, noncached input, and output only when the measured parts sum to the reported footprint. Otherwise it shows a single used segment. Segment widths are proportional, even when output is tiny. Cached tokens still occupy context; cache and capacity bars have different, explicit denominators. The capacity bar caps visually at the reported limit but preserves the true percentage and an over-limit label. Detailed accounting keeps reasoning and cached tokens labeled as subsets.

Keep this as a diagnostic chart: no oversized summary metrics, nested cards, unmeasured claims, or animated entrance. The MCP App preserves disclosure state while refreshing. Its Refresh and default-on Auto-refresh use `tools/call` to read fresh telemetry into the same view; they do not start an agent turn. Auto-refresh runs every 15 seconds while visible, pauses while hidden, and stops after three consecutive failures.

The **inline fallback** uses `window.openai.sendFollowUpMessage({prompt, title})`, which may require host confirmation and creates a new snapshot in the chat. It cannot update the old report in place and does not offer automatic refresh. Preserve this distinction when describing the two modes. Report generation must never modify session telemetry.

## Model provenance and compatibility evidence

`latest_usage_model` identifies the model recorded when accepted usage arrived. `usage_state` distinguishes recorded usage, waiting after a model switch, waiting after compaction, and absent usage. Model transitions have a total count and a bounded list of the latest ten transitions; duplicate metadata is not a transition. Switching away and back still requires fresh usage. Empty or unrecognized counter dictionaries do not satisfy that requirement. Legacy token-count records without explicit turn IDs rely on log order.

`diagnostics` reports observed fields, fields not observed in the current snapshot, and checks not performed after a read or identity failure. It does not declare a Codex release incompatible just because telemetry is absent. Failure codes distinguish missing home, unresolved session, identity mismatch, and read failure. Public failure messages exclude exception paths.
