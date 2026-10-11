# New-user landing page

Buildless HTML, CSS, and JavaScript. Serve this directory with a static HTTP server
to preview it. No chat access, analytics, external assets, or runtime dependencies.
The interactive inspector is an explicitly synthetic, simplified illustration.

The install example pins the pilot candidate to
`b19f0a01a18c126a2c69615eef3f4285c73b2c61`. Update it only after reviewing the next
candidate and its CI. Keep claims aligned with the compatibility and telemetry
documents; never substitute real readings or screenshots containing user data.

The GitHub repository holds the canonical page source. Sites publication uses a
separate checkout with these four assets under `dist/` and its own hosting manifest.
Copy changes there, verify the page, and use the Sites source/version workflow.
Do not run that workflow against this repository's Git remote. A deployed preview
starts owner-private; public access is a separate audience decision.

Verification: `npm run test:landing` from the repository root uses the existing
Playwright dependency. Set `CHROME_EXECUTABLE_PATH` when needed, as for UI tests.

## Design choices

Audience: a daily Codex user evaluating a small utility beside their editor in
normal daytime light. A light mint surface and the inspector's existing teal make
the page familiar. Native system typography preserves the product's visual voice.
The section numbers form a short reading sequence: visibility, continuity, limits,
installation. The product example carries the imagery; decorative stock assets
would add no useful evidence. Motion is limited to link feedback and scrolling,
with reduced-motion support. The three example buttons and FAQ use native controls.
