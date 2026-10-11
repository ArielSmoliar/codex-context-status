# Development roadmap

Implemented: observed-field compatibility checks, exact-session/read failure diagnostics, latest-usage model attribution, recent model transitions, and a waiting state after model changes.

Refresh performance: added repeatable synthetic benchmarks and reduced per-record file-position overhead. See [measurements](references/performance.md). Incremental caching is deferred until evidence justifies its added state and invalidation rules.

Installation and upgrades: preview-first managed copies, hash-based conflict detection, explicit adoption checks, staged replacement with retained backups, and component-specific reload guidance. MCP registration remains a separate, reviewable setup step.

Compatibility foundation: documented live evidence separately from synthetic fixtures, exposed sanitized producer/format evidence, and withheld capacity advice after unreadable newer usage. See the [matrix](references/compatibility.md).

Session advice: task-intent controls, explicit waiting-state guidance, and a copyable handoff prompt with manual-copy fallback are implemented. The prompt has browser workflow coverage; its usefulness across real tasks still needs user feedback.

1. **Version coverage:** gather live verification for additional Codex releases using the documented checklist; only one desktop build is currently verified. Synthetic format tests do not replace that evidence.
2. **Handoff feedback:** try the prompt at real task boundaries and assess whether the next chat can resume with the goal, decisions, verification, and next action intact. Refine from observed gaps rather than adding more speculative heuristics.

Implementation order can change with user feedback. No exact occupancy, token-attribution, or cache-cause claims should be added without a supporting data source.
