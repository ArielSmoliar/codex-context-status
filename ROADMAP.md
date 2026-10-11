# Development roadmap

Implemented: observed-field compatibility checks, exact-session/read failure diagnostics, latest-usage model attribution, recent model transitions, and a waiting state after model changes.

1. **Efficient refresh:** benchmark large session logs, then consider incremental reads with correct handling of compaction, truncation, and rotation.
2. **Installation and upgrades:** detect existing installations, preserve user modifications, and explain when the desktop needs to reload tools or views.
3. **Version coverage:** test additional Codex releases and document which local record formats have been verified; do not infer incompatibility solely from missing events.
4. **Session advice:** validate the usefulness of handoff prompts; keep thresholds explicit and avoid implying a known automatic compaction limit.

Implementation order can change with user feedback. No exact occupancy, token-attribution, or cache-cause claims should be added without a supporting data source.
