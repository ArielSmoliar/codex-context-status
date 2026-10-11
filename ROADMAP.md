# Development roadmap

Implemented: observed-field compatibility checks, exact-session/read failure diagnostics, latest-usage model attribution, recent model transitions, and a waiting state after model changes.

Refresh performance: added repeatable synthetic benchmarks and reduced per-record file-position overhead. See [measurements](references/performance.md). Incremental caching is deferred until evidence justifies its added state and invalidation rules.

Installation and upgrades: preview-first managed copies, hash-based conflict detection, explicit adoption checks, staged replacement with retained backups, and component-specific reload guidance. MCP registration remains a separate, reviewable setup step.

GitHub plugin distribution: generated self-contained skill and local stdio MCP
package, bundled JavaScript dependencies, a repo marketplace, and Codex-managed
install/upgrade/removal. See [plugin lifecycle and standalone migration](references/plugin.md).
The lifecycle test uses real Codex commands and synthetic telemetry in an isolated
home; desktop rendering and new-user adoption still need pilot evidence.

OpenAI directory distribution: a [submission-readiness packet](references/submission/README.md)
and unsent eligibility inquiry are prepared. Local stdio transport, telemetry
extraction from session logs, and Codex-only platform scope need explicit guidance
before submission. Listing and review drafts do not establish eligibility.

Compatibility foundation: documented live evidence separately from synthetic fixtures, exposed sanitized producer/format evidence, and withheld capacity advice after unreadable newer usage. See the [matrix](references/compatibility.md).

Session advice: task-intent controls, explicit waiting-state guidance, and a copyable handoff prompt with manual-copy fallback are implemented. Preparation and resume prompts now cover both sides of the transition, including current-state checks and the distinction between merged and installed work. They have browser workflow coverage; fresh-chat effectiveness across real tasks is still unverified. See the [evaluation scenarios](references/handoffs.md#evaluating-a-handoff).

1. **Version coverage:** gather live verification for additional Codex releases using the documented checklist; only one desktop build is currently verified. Synthetic format tests do not replace that evidence.
2. **Handoff feedback:** the [initial agent-reviewed CLI smoke run](references/validation-smoke-2026-10-11.md) passed six synthetic cases. Next, run the [three-person pilot](references/validation.md#three-person-pilot) at real task boundaries and assess whether the next chat can resume with the goal, decisions, verification, and next action intact. Refine from observed gaps rather than adding more speculative heuristics.

Implementation order can change with user feedback. No exact occupancy, token-attribution, or cache-cause claims should be added without a supporting data source.
