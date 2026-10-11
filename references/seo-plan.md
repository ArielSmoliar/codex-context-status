# SEO plan for context-status

Owner: project maintainer. Prepared October 11, 2026. Audience: daily Codex desktop
users looking for context visibility or help continuing a long task in a fresh chat.
Goal: help relevant users understand the tool and reach installation guidance.
Search visibility is not adoption; the three-person pilot measures a different step.

## Positioning and search intent

These are initial query hypotheses, not measured search-volume claims. Keep the
user-approved headline, “Visibility into your Codex session.” Explain specific
capabilities and their limits in natural language rather than repeating keywords.

| Intent | Candidate queries | Current destination | Next useful content |
| --- | --- | --- | --- |
| Find the tool | context-status, Codex context status | Landing page and GitHub README | Keep names and links consistent. |
| Inspect usage | Codex context window usage, Codex context monitor | Capacity example and capabilities | Explain recorded estimates versus live occupancy. |
| Continue work | Codex session handoff, start a new Codex chat | Handoff section and linked guide | A tested, synthetic end-to-end walkthrough based on pilot questions. |
| Install or troubleshoot | context-status install, Codex MCP context inspector | Installation section and pinned guide | Expand only from observed setup failures and verified build evidence. |

Do not target “fix Codex quality” or promise a restart threshold. Avoid unsupported
claims about exact occupancy, cross-platform compatibility, cache causes, or model
performance. No invented customer counts, ratings, testimonials, or benchmark wins.

## Technical foundation

The source in `site/` is canonical for maintenance. The public origin is
`https://codex-context-status.major-cabin-5392.chatgpt.site/`.

- Serve complete readable HTML; JavaScript only enhances the synthetic demo and
  copy button. Keep headings, copy, FAQ answers, and install links in the response.
- Use one descriptive title and description, one primary heading, a root canonical,
  matching Open Graph URL, and a 1200×630 synthetic social card. Maintain image alt
  descriptions for shared previews.
- Publish `robots.txt` and a sitemap listing only the canonical home page. Section
  anchors are not separate pages. Omit invented update dates and priority values.
- Include truthful WebSite and SoftwareSourceCode JSON-LD with the real repository.
  This describes the project; it is not a promise of a Google rich result. No fake
  offer, review, license, or FAQ eligibility claims are included.
- Keep assets local, images sized, and interactions keyboard accessible. Test small
  screens and reduced motion. No external fonts or analytics scripts are required.
- Provide `404.html` with `noindex`, but verify actual hosted status codes. A local
  file or passing browser test does not prove the hosting platform uses it.

Google describes [canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
as signals for consolidating duplicate URLs, not an absolute instruction. Its
[sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
supports listing canonical, fully qualified URLs. Keep these signals consistent.

## Launch gates and ownership

| Action | Owner | Status / evidence |
| --- | --- | --- |
| Page public, no sign-in required | Maintainer | Verified October 11; public access explicitly approved. |
| GitHub contains website source and preview link | Maintainer | PR #10 merged October 11 at `b297cef527f0c15e17d8f17ada77f95516a23527`. |
| Metadata, canonical, sitemap, robots, social image | Maintainer | Live and verified October 11; all six non-HTML assets match source bytes. |
| Unknown URL returns an actual 404 | Maintainer / hosting platform | Verified October 11: nonexistent path returns HTTP 404 with our noindex error page. |
| GitHub About website | Maintainer | Set to the public landing URL October 11. |
| Search Console property ownership | Maintainer's Google account | IN PROGRESS. URL-prefix property created; Google-issued HTML tag added to the home page. Ownership confirmation is pending. |
| Sitemap submission and URL Inspection | Maintainer | PENDING verified property and live-file checks. |
| Indexing / impressions / clicks | Google / measured in Search Console | UNKNOWN. A successful deployment does not establish indexing. |

After deployment, check the anonymous responses for `/`, `/robots.txt`,
`/sitemap.xml`, `/social-card.png`, and one nonexistent path. Confirm HTTP status,
content type, no blocking `X-Robots-Tag` on the home page, correct canonical, and
actual file contents. Repeat the home request using a crawler user agent as a
limited access check; this does not replace Google's own URL Inspection.

Deployment audit, October 11, 2026:

- `/`: HTTP 200, `text/html`, complete page and metadata, no blocking
  `X-Robots-Tag`. A Googlebot user-agent request also returned 200; actual Google
  crawling is still unverified.
- `/robots.txt`, `/sitemap.xml`, and `/social-card.png`: HTTP 200 with appropriate
  text, XML, and PNG content types; exact source-byte matches. CSS, JavaScript,
  and SVG also match the repository source.
- A nonexistent path: HTTP 404 with the intended `noindex,follow` error page.
  This resolves the initial home-page fallback with HTTP 200.
- The host injects a Cloudflare challenge script into HTML. The only observed
  difference from source is that injection; raw HTML hashes therefore differ.
  This is hosting behavior, not project analytics. Recheck access in Search
  Console before concluding that search engines can crawl reliably.

## First 30 days

1. **After deployment:** the repository’s About website is already set. Verify a
   URL-prefix Search Console property for the exact public origin,
   using an owner-issued HTML verification tag or file. Commit only the intended
   public verification artifact, redeploy, then confirm ownership in Search Console.
   Do not invent a token or claim verification. Submit `/sitemap.xml` and inspect
   the canonical home page. Address crawling or indexing explanations first.
2. **During the pilot:** ask how participants found the tool. Record setup and
   terminology questions; improve this page or the linked guide where evidence
   warrants it. No transcript publication, keyword stuffing, or automatic outreach.
3. **Weekly for the first month, manually:** record Search Console indexing state,
   query/page impressions, clicks, and CTR over matching date ranges. Separate
   branded from non-branded queries where data permits. Low-volume or withheld
   queries remain unknown. These are visits from search, not installs.
4. **At 30 days:** use impressions without clicks to investigate intent/title fit;
   use clicks with pilot setup failures to prioritize onboarding. If not indexed,
   troubleshoot access/canonical/indexing reports before rewriting the pitch. Small
   samples do not justify rank or conversion claims. Expand content only for a
   demonstrated unanswered user question.

The cadence is a plan, not a scheduled automation. There are no analytics events,
outreach messages, paid placements, or Search Console changes in this implementation.
Install conversion and retention require participant evidence; they cannot be
inferred from GitHub views, stars, or Search Console clicks.

Google's [SEO starter guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
recommends useful, understandable content and explains that indexing and ranking
are not guaranteed. Treat this plan as an iteration process rather than a ranking
forecast. Keep a short monthly record of actions, dates, and observed results.

## Maintenance

Every website change belongs in `site/` on GitHub, then the same assets are copied
to the existing Sites checkout and published. Run `npm run test:landing` before
publishing; compare deployed asset hashes with source afterward, inspecting any
HTML differences introduced by the host. Avoid editing only
the hosted copy. Regenerate the social image with `node scripts/render_social_card.mjs`
when its wording or styling changes (uses the existing Playwright dependency).

If adopting a custom domain later, choose it before broad promotion where possible.
Update canonical, sitemap, robots sitemap URL, structured IDs, social URLs, and
GitHub links together; configure redirects only through supported hosting controls
and verify them. Domain purchase and migration are outside this initial plan.
