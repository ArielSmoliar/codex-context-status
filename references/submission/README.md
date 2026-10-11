# OpenAI plugin submission readiness

Updated October 11, 2026. **Draft uploaded; not submitted for review or published.**
The direct upload flow accepted plugin 0.1.0 under the verified individual
publisher identity. [The draft](https://platform.openai.com/plugins/manage/plugins_6acc2135f1008191a51a1284f57fb595)
reports the local command MCP server as a blocking finding.

This directory contains supporting review documents, not an uploadable plugin
ZIP. The generated package is `plugins/context-status/`. Version 0.1.1 prepares
the listing corrections; its policy pages must be approved and available at the
manifest's URLs before a replacement upload. GitHub installation remains the
supported distribution path. No OpenAI inquiry has been sent.

## Resolve eligibility before submitting for review

| Question | Current evidence | Required next action |
| --- | --- | --- |
| Local MCP transport | The live portal accepted the ZIP as a draft but reports: “Command MCP Server detected” and requests an OpenAI representative for submission. | Confirm an approved local MCP submission route. Do not tunnel or upload logs to qualify. |
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
| Verified developer identity | Direct upload used Individual — ARIEL SMOLIAR; Generate Runbook is already published in the same account. |
| Listing metadata | Version 0.1.1 adds a 30-character subtitle, long description, and bundled light/dark listing and composer icons. Portal revalidation is pending. |
| Product and support URLs | Manifest now points to the public product website and GitHub issues. |
| Privacy and terms URLs | `docs/privacy.md` and `docs/terms.md` prepared for publisher review. Manifest uses their stable main-branch GitHub URLs; the private contact is confirmed; review and merge/publication must happen before upload. |
| First-party license | No root LICENSE file was found at the candidate revision. Maintainer must choose licensing; do not infer MIT from third-party notices. |
| Desktop compatibility | One documented macOS build. Default `~/.codex` only for the plugin; custom-home users need the standalone installer for in-place Refresh. |
| Reviewer cases and recording | Eight cases drafted; reviewer executions and a video remain NOT RUN / NOT RECORDED. |
| Independent-user evidence | P01–P03 pilot is prepared, not run. It is not a documented portal requirement, but remains useful release evidence. |

Before a replacement upload, review the policies and merge the pages so their main-branch URLs resolve, and validate the package.
The local MCP declaration must remain included. Do not submit a skills-only
placeholder to bypass the command-MCP finding. Revalidate the uploaded 0.1.1
metadata and preserve any remaining findings in the inquiry.

The [review guide](review-guide.md) still requires agreed synthetic reviewer
trials and a recording. Upload validation, policy attestations, review approval,
and publication are separate steps. No approval or acceptance is implied here.
