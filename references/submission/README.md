# OpenAI plugin submission readiness

Prepared October 11, 2026. **Not submitted; eligibility unresolved.** This is a
review packet, not an uploadable plugin ZIP. It does not change the installed
plugin, collect telemetry, contact OpenAI, or publish policy documents.

Candidate: plugin 0.1.0 from
`0b6b3bfd5e915f041c64e7f2009c850bd4fdfce3` (merged PR #13).
The GitHub installation remains the supported distribution path.

## Resolve eligibility before preparing a portal upload

| Question | Current evidence | Required next action |
| --- | --- | --- |
| Local MCP transport | The package runs a local stdio server. The normal public submission route requires a remote HTTPS endpoint; the package guide directs local-server developers to their OpenAI contact. | Confirm an approved local MCP submission route. Do not tunnel or upload logs to qualify. |
| Session-log access | The reader locates the exact requested chat, reads and parses its JSONL records, and returns allowlisted telemetry. It does not reconstruct conversation text, but the underlying file contains it. The guidelines restrict MCP access to full chat logs. | Ask whether this specific telemetry extraction is eligible, or whether a host-provided telemetry resource is required. Do not assume allowlisting grants an exception. |
| Codex-only platform scope | The inspector needs local Codex storage and MCP Apps. Guidelines call for ChatGPT desktop and mobile reliability. | Confirm whether a Codex-desktop-only listing is supported. Do not claim web/mobile compatibility. |

Sources checked on the preparation date:

- [Package guide: local MCP](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks)
- [Plugin guidelines: data handling and testing](https://developers.openai.com/plugins/plugin-guidelines)
- [Upload, listing, and review requirements](https://developers.openai.com/plugins/deploy/submission)

See [the ready-to-send inquiry](eligibility-inquiry.md). No recipient has been
selected and no message has been sent. The proposed next step is for the maintainer
to send it to an existing OpenAI contact or obtain the appropriate support route.

## Materials prepared

- [Listing copy](listing-copy.md), with a subtitle within the 30-character limit.
- [Five positive and three negative review cases](review-cases.json).
- [Evidence and walkthrough plan](review-guide.md), separating automated tests
  from unrun reviewer trials and an unrecorded video.
- [Privacy notice draft](privacy-draft.md), describing local processing and Codex
  host handling without promising that tool results never leave the device.
- [Publisher decisions](publisher-decisions.md), including terms and licensing.
- `assets/logo.svg` and `assets/logo-dark.svg`: square 64 × 64 SVGs derived from
  the existing site mark. These can serve as listing and composer icons.

## Remaining submission gaps

| Item | Status |
| --- | --- |
| Eligibility for local transport, log access, and Codex-only scope | Awaiting OpenAI guidance; blocks the ordinary submission path. |
| Verified developer identity and owning organization/project | Not checked in the Platform account. Display name must match the selected verified identity. |
| Listing metadata | Draft prepared. Current manifest subtitle is 40 characters; submission limit is 30. Long description and listing icon fields are not yet present. |
| Product and support URLs | Existing website and GitHub issues page proposed in listing copy. |
| Privacy and terms URLs | No final published pages supplied. Both are required for MCP review. Do not use invented URLs or draft documents as approved policies. |
| First-party license | No root LICENSE file was found at the candidate revision. Maintainer must choose licensing; do not infer MIT from third-party notices. |
| Desktop compatibility | One documented macOS build. Default `~/.codex` only for the plugin; custom-home users need the standalone installer for in-place Refresh. |
| Reviewer cases and recording | Eight cases drafted; reviewer executions and a video remain NOT RUN / NOT RECORDED. |
| Independent-user evidence | P01–P03 pilot is prepared, not run. It is not a documented portal requirement, but remains useful release evidence. |

The source package intentionally stays unchanged until the eligibility path is
known. After approval of the path, resolve publisher decisions, publish accurate
policies, incorporate the listing/review fields and icons into `packaging/`, bump
the plugin version, and regenerate with `npm run build`. Re-run product and plugin
lifecycle checks. Then exercise the agreed reviewer setup and record the video.

Upload through [OpenAI Platform Plugins](https://platform.openai.com/plugins)
only after the required gaps are resolved. If the plugin uses MCP, include it in
the initial submission: the documented process cannot add MCP to an existing
skills-only plugin. Do not submit a skills-only placeholder to bypass eligibility.
Portal validation, policy attestations, review approval, and publication remain
separate steps. No approval or acceptance is implied by this packet.
