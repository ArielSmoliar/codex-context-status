# Compatibility evidence

Local session storage is an implementation detail. This matrix separates observed
desktop behavior from synthetic parser tests; passing fixtures does not establish
support for an untested Codex release.

## Release evidence

| Desktop | CLI / producer | Evidence | Scope |
| --- | --- | --- | --- |
| 26.1007.21159 on macOS | 0.162.0-alpha.17.2 | Live verification recorded October 10, 2026 | Inspector rendering and in-place Refresh; advancing `event_msg/token_count` and `token_usage_record` in the selected chat. |
| Not identified separately | Session metadata: 0.162.0-alpha.17.2 | Metadata rechecked October 11, 2026 | Same producer version; this is not evidence for another desktop release. |
| Other releases | Unverified | No live verification recorded | Missing telemetry alone does not prove incompatibility. |

`session_meta.payload.cli_version`, when present, describes the recorded producer.
It is not the installed desktop version and may predate an app update. Only a
bounded version-shaped string is exposed; paths, instructions, and arbitrary
metadata are omitted. Unknown version numbers do not disable an otherwise readable
format. Version strings alone never establish compatibility.

## Synthetic format coverage

The hand-authored cases in `tests/fixtures/compatibility.json` contain invented
identities, versions, model names, and token values. They are not exported chats.

| Format / condition | Expected behavior |
| --- | --- |
| `event_msg/token_count` with request counters and limit | Estimate latest request capacity; cache counters remain subsets. |
| Matching `token_usage_record` with current turn ID | Read counters; capacity requires a separately reported limit. |
| Mixed known formats | Use latest accepted measurement and report evidence for both families. |
| Missing cache counters | Cache unavailable; capacity may still be available. |
| No usage or unknown outer event name | No fabricated usage; absent known formats are reported as not observed. |
| Non-null usage with no valid known counters | Count an unreadable measurement; withhold capacity advice if this is a newer applicable record. |
| Wrong `info` container type | Count an unreadable legacy measurement; withhold capacity advice. |
| Absent/null usage or quota-only update | Preserve earlier usage without treating an absent measurement as a format failure. |
| Malformed earlier-turn usage | Record format evidence without invalidating the current turn's measurement. |
| Wrong-thread usage | Ignore it, including in the compatibility counters. |
| Valid usage after an unreadable record | Resume estimates if a valid context limit is available. |
| Future version with known shape | Parse it; do not claim that release has been verified. |
| Untrusted producer text | Omit it from the report. |

Additional regression tests cover incomplete trailing records, malformed complete
lines, model switches, compaction, file rotation, and identity failures. Identity
failures discard format/version evidence from that file. Browser tests exercise
unreadable-to-readable recovery in the same inspector.

## Reading the diagnostics

The JSON/MCP `compatibility` object reports a sanitized `recorded_cli_version`,
counts for each of the two known `usage_formats`, and whether the size-bounded read
ended with an incomplete record. Each format reports total records, readable
measurements, and unreadable measurements. Counts cover the available log, so
historical problems remain visible after recovery. Readable format evidence may
include a delayed prior-turn record that is not accepted as the latest measurement.

The existing **Telemetry checks & model changes** panel displays producer and
format evidence. `awaiting_readable_usage` means an applicable newer record had
unreadable counters. Earlier measurements remain labeled with their original
timestamp, but capacity and capacity-based advice are withheld until recovery.
Model-switch waiting takes precedence when the latest readable measurement belongs
to an older model epoch.

Unknown event names and missing/null fields cannot reliably distinguish a changed
schema from an idle chat or a quota-only update. The reader does not search message
contents for possible counters or export unknown field names. Complete malformed
lines and incomplete trailing writes are distinct; neither alone proves a release
is unsupported. This is recorded evidence, not automatic detection of every future
schema change.

## Adding a verified release

1. Record the desktop version, platform, date, and session-recorded producer version
   separately. If one is unavailable, leave it unknown.
2. Verify the selected chat's identity and that measurements advance after a
   completed response. Check opening the inspector and refreshing it in place.
3. Test model-change and compaction behavior if making claims about them; record
   any untested behavior as such.
4. Add minimal synthetic reproductions of any new structural shape. Never commit
   actual logs, chat IDs, user paths, prompts, tool output, or screenshots containing
   personal telemetry.
5. Run `npm test`, then add the narrowly supported evidence to the release table.

The current CI runs synthetic tests on Linux with Node 20/Python 3.10 and Node
22/Python 3.12. That checks the implementation and
test host; it does not certify Linux Codex desktop or any additional app version.
