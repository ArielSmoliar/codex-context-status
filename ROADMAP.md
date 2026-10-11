# Development roadmap

Implemented: observed-field compatibility checks, exact-session/read failure diagnostics, latest-usage model attribution, recent model transitions, and a waiting state after model changes.

Refresh performance: added repeatable synthetic benchmarks and reduced per-record file-position overhead. See [measurements](references/performance.md). Incremental caching is deferred until evidence justifies its added state and invalidation rules.

1. **Installation and upgrades:** detect existing installations, preserve user modifications, and explain when the desktop needs to reload tools or views.
2. **Version coverage:** test additional Codex releases and document which local record formats have been verified; do not infer incompatibility solely from missing events.
3. **Session advice:** validate the usefulness of handoff prompts; keep thresholds explicit and avoid implying a known automatic compaction limit.

Implementation order can change with user feedback. No exact occupancy, token-attribution, or cache-cause claims should be added without a supporting data source.
