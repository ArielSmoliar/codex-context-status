# Development roadmap

The current inspector works locally. Priorities for broader use:

1. **Compatibility diagnostics:** report whether session discovery, model metadata, usage events, and context limits are supported by the installed Codex version.
2. **Model provenance:** distinguish the active recorded model from the model that produced the latest usage; show a switch history and a waiting-for-telemetry state without attributing old cache measurements to a new model.
3. **Efficient refresh:** benchmark large session logs, then consider incremental reads with correct handling of compaction, truncation, and rotation.
4. **Installation and upgrades:** detect existing installations, preserve user modifications, and explain when the desktop needs to reload tools or views.
5. **Session advice:** validate the usefulness of handoff prompts; keep thresholds explicit and avoid implying a known automatic compaction limit.

Implementation order can change with user feedback. No exact occupancy, token-attribution, or cache-cause claims should be added without a supporting data source.
