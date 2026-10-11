# New-user landing page

Public page: https://codex-context-status.major-cabin-5392.chatgpt.site

Buildless HTML, CSS, and JavaScript. Serve this directory with a static HTTP server
to preview it. No chat access, analytics, external assets, or runtime dependencies.
The interactive inspector is an explicitly synthetic, simplified illustration.

The install example pins the pilot candidate to
`b19f0a01a18c126a2c69615eef3f4285c73b2c61`. Update it only after reviewing the next
candidate and its CI. Keep claims aligned with the compatibility and telemetry
documents; never substitute real readings or screenshots containing user data.

The GitHub repository holds the canonical page source. Sites publication uses a
separate checkout with `index.html`, `style.css`, `script.js`, `icon.svg`,
`robots.txt`, `sitemap.xml`, `social-card.png`, and `404.html` under `dist/`, plus its own hosting manifest.
Copy changes there, verify the page, and use the Sites source/version workflow.
Do not run that workflow against this repository's Git remote. This site was made
public at the maintainer's request. Preserve that audience on subsequent updates.

Verification: `npm run test:landing` from the repository root uses the existing
Playwright dependency. Set `CHROME_EXECUTABLE_PATH` when needed, as for UI tests.

The [SEO plan](../references/seo-plan.md) defines positioning, crawl checks,
Search Console setup, a first-month measurement cadence, and publishing ownership.
Regenerate `social-card.png` with `node scripts/render_social_card.mjs` when needed.
Search Console verification and actual indexing remain separate from deployment.

## Design choices

Audience: a daily Codex user evaluating a small utility beside their editor in
normal daytime light. A light mint surface and the inspector's existing teal make
the page familiar. Native system typography preserves the product's visual voice.
The section numbers form a short reading sequence: visibility, continuity, limits,
installation. The product example carries the imagery; decorative stock assets
would add no useful evidence. Motion is limited to link feedback and scrolling,
with reduced-motion support. The three example buttons and FAQ use native controls.
