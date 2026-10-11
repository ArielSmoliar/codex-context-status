# New-user landing page

Public page: https://codex-context-status.major-cabin-5392.chatgpt.site

Buildless HTML, CSS, and JavaScript. Serve this directory with a static HTTP server
to preview it. No chat access, analytics, external assets, or runtime dependencies.
The interactive inspector is an explicitly synthetic, simplified illustration.

The primary install example uses the GitHub marketplace on `main`, matching
[the plugin guide](../references/plugin.md). It requires a Codex CLI with plugin
support and the default `~/.codex` data directory. Custom `CODEX_HOME` users are
linked to the standalone installer; existing standalone users are linked to the
migration steps. The guide also covers pinned installs, upgrades, and removal.
Keep these instructions aligned with that guide and the compatibility record.
Never substitute real readings or screenshots containing user data.

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
Keep the Google-issued `google-site-verification` meta tag in the home page across
future deployments; Google periodically checks it to retain ownership verification.

## Design choices

Audience: a daily Codex user evaluating a small utility beside their editor in
normal daytime light. A light mint surface and the inspector's existing teal make
the page familiar. Native system typography preserves the product's visual voice.
The section numbers form a short reading sequence: visibility, continuity, limits,
installation. The product example carries the imagery; decorative stock assets
would add no useful evidence. Motion is limited to link feedback and scrolling,
with reduced-motion support. The three example buttons and FAQ use native controls.
