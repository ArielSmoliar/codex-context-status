# Working on context-status

- This repository is the source for the local Codex skill and MCP App. Installed copies may exist separately; compare before updating them.
- Keep telemetry read-only, allowlisted, and bound to an exact validated thread ID. Never use the latest session or a shared working directory as identity.
- Tests must use synthetic logs in temporary directories, never personal Codex session data.
- Keep numbers and session recommendations inside the refreshable UI, not repeated in chat prose.
- Auto-refresh starts on, runs every 15 seconds while visible, pauses when hidden, and stops after three consecutive failures. It must not send follow-up chat messages or create scheduled automations.
- Capacity is an estimate. Cached input/reasoning output are subsets. Cumulative consumption is not occupancy. Do not guess unavailable fields or compaction thresholds.
- Run `npm run build` after editing the template, bridge, or CSS. Commit the generated MCP HTML.
- Run the relevant tests, and `npm test` for cross-layer changes. Use `CHROME_EXECUTABLE_PATH` when a local Chrome binary is needed.
- Do not publish logs, screenshots with personal telemetry, session IDs, credentials, or machine-specific paths.
