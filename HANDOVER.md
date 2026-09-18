# Project handover

Last updated: 18 September 2026 (Australia/Brisbane), second pass

## Current state

The Hugo rebuild and website-audit improvement pass are complete. The production
site is deployed from `main` through GitHub Pages.

- Repository: `https://github.com/kenankalayci/academic-website`
- Branch: `main`
- Production branch: `main`
- Production URL: `https://kenankalayci.com/`
- Deployment: pushing to `main` runs `.github/workflows/deploy.yml` and publishes
  through GitHub Pages.

Note on GoDaddy: the DNS cutover already happened in March 2026. The site has been
served from GitHub Pages ever since, and the old GoDaddy cPanel hosting never served
it. Cancelling that hosting plan therefore cannot affect this site. GoDaddy retains
only the domain registration (expires 2027-05-31) and the DNS zone, both separate
products. `CUTOVER_CHECKLIST.md` describes a migration that is already complete and
is kept for historical reference only — in particular its rollback step, restoring
`A @ 148.66.137.114`, is no longer available.

## Recent research updates

- Retitled the August 2026 manuscript to *Algorithmic Advice in Markets with
  Complex Goods* and moved it from a local site download to its SSRN page,
  `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7107878`. The local
  `static/papers/Algorithmic_Third-Party_Advice_Bao_Kalayci_Sun_2026.pdf` was
  deleted; no path on the site still points at it.
- Co-authors are Leo Bao and Ruize Sun, matching the manuscript title page. The
  published 2020 article correctly retains the author name Zhengyang Bao.
- The homepage Current Research section, the Working Papers page, the public CV
  source, and the built `static/CV/KALAYCI_CV.pdf` all carry the new title and
  the SSRN link.
- The repo CV source is the public version (`\publictrue`). The full version used
  for appraisal/promotion lives outside this repo, at
  `~/Library/CloudStorage/OneDrive-TheUniversityofQueensland/Kenan/Personal/Appraisal/Level D/KALAYCI_CV.tex`.
  That copy has now been synced for this paper: same title, SSRN link and
  co-authors, with `\publicfalse` preserved. It was test-compiled (5 pages, no
  LaTeX errors). Its sibling `KALAYCI_CV.pdf` was **not** rebuilt — it was
  already stale (30 May) against its source (27 July) before this change, so the
  status quo was kept rather than sweeping in three months of unrelated edits.
- The two CV copies drift in both directions, so neither is reliably newer.
  Diff them before assuming either is current, and preserve the
  `\publictrue` / `\publicfalse` line, which is the only intended difference
  besides one cosmetic date-column spacing fix present in the repo copy only.

## Presentation and naming (17 September 2026)

- **Card surfaces moved from white to cream** (`#fbf9f4`). The page backdrop was
  already cream but content sits in cards, which were white — so the surface
  actually read on was plain. The `--surface` token alone was not enough:
  `.home-card` and `.research-card` each override it with a hardcoded white
  gradient, so all three needed changing. `--surface-tint` was nudged lighter so
  the research-area boxes still lift against a cream parent; `--surface-strong`
  stays white so nav pills and buttons keep reading as raised. Dark mode is
  unaffected.
- **SSRN links styled like PDF downloads.** `.citation-list` now matches
  `ssrn.com` alongside `.pdf`, so paper-access links look consistent wherever the
  paper lives. Add `doi.org` too if journal titles should also render bold navy —
  deliberately left out, since it restyles every journal name.
- **The displayed name now uses the Turkish dotless ı** (`Dr. Kenan Kalaycı`).
  Editing `title` in `hugo.toml` was enough for the header, footer, page titles,
  `author` meta, `og:site_name`, RSS and JSON-LD `Person.name`, because all read
  `.Site.Title`. The contact page's visible heading and meta description were
  fixed separately. Verified rendered on production with no mojibake.
- **Still ASCII, by omission rather than intent:** the `keywords` array in
  `hugo.toml` (which also feeds JSON-LD `knowsAbout`) and the `og:image:alt` /
  `twitter:image:alt` strings in `layouts/_default/baseof.html`. Domain, email, X
  handle and PDF filenames stay ASCII deliberately and must not change.
- **A rust accent colour was tried and reverted.** Navy and burnt orange pair
  well, but `#FFED00` is a UQ brand colour that has to stay, and navy + rust +
  saturated yellow is a three-way conflict. Recorded so it is not re-attempted
  blind.
- `.claude/` is now git-ignored; it holds local editor and preview config only.

## Flat layout and type scale (18 September 2026)

`reports/design-proposal-typography-and-layout.md` was drafted, reviewed,
revised and **implemented**. It is now an implementation record; superseded
claims are struck through rather than deleted, so the reasoning stays auditable.

- **Flat layout.** Page ground is a solid `--page` token (`#fbf9f4` light,
  `#0d1c30` dark) — solid because a translucent `body` background composites
  against the white canvas. Card backgrounds, borders, radii, shadows and
  `backdrop-filter` are off `.site-header`, `.page-card`, `.home-card` and
  `.research-card`. The per-card 6px accent strip is now a single 2px yellow rule
  under the header. Research areas are ruled columns. Nav pills are flat links.
- **Type.** Body copy 16.6 → 19.6px (18px mobile), `h3` → 22.4px, `h2` minimum →
  24.8px. **The root font size is deliberately untouched.** Root scaling was
  tried and rejected in review: `clamp()` headings with `vw` middle terms ignore
  the root, so body text grows while headings stand still and the ratio
  compresses at mid widths. Leaving the root alone also keeps the homepage hero
  at its 58.4px cap, keeps nav wrapping unchanged, and made the proposed 1140px
  shell widening unnecessary. **Do not reintroduce root scaling.**
- **Kept deliberately:** buttons stay recognisable controls; `.location-card`
  and `.section-link-list` tiles keep a border and small radius for grouping but
  lose gradient and shadow; yellow survives as the header rule and nav hover.

## Navigation restructure (18 September 2026)

Navigation went from nine tabs to four: **About · Research · Supervision ·
Links**.

- `/publications/` and `/workingpapers/` merged into **`/research/`**, which
  renders both data files plus a Public Writing section. `single.html` gained a
  `data_file: research` mode that renders both sets; the old single-purpose
  values still work.
- Public Writing is driven by a `research_writing: true` page param, not
  hardcoded. Tagging a future article adds it to `/research/` automatically.
- `/contact/` merged into **`/about/`** as a `## Contact` section, carrying the
  address, phone, email and the Google Maps panel.
- `/vitae/` **deleted** — its content was already elsewhere (CV download is a
  homepage button; the snapshot facts are in the About prose).
- `/grants-awards-fellowships/` **deleted at the owner's request**. Note: the
  three teaching awards and the grant figures ($358k DECRA, $20k UQ ECR) existed
  nowhere else on the site and now survive only in the CV PDF. Restore from git
  if wanted.
- `/blog-posts/` listing page removed; the Confusopoly article keeps its own URL
  and is linked from `/research/`.

Every retired URL redirects rather than 404s:

| Old | Now |
|---|---|
| `/publications/`, `/workingpapers/`, `/blog-posts/` | `/research/` |
| `/contact/`, `/contact-2/`, `/contact-3/`, `/location/`, `/kenan/` | `/about/` |

`/vitae/` and `/grants-awards-fellowships/` are fully gone; nothing linked to
them. **`/contact/` was the canonical contact URL and is now a redirect** — if
it appears on business cards, a course profile or the UQ staff page, those still
work, but the URL people land on has changed.

### The mobile disclosure menu is gone, and with it all JavaScript

With four items a menu was unnecessary, so the tabs sit inline at every width and
wrap to a second row only below about 340px.

**The site now ships zero behavioural JavaScript.** The hamburger handler was the
only script, and a companion script existed solely to add a `.js` class so CSS
could hide the nav when JS was available. Both are gone, along with the
`.nav-toggle` / `.nav-toggle-icon` rules and the `.js`-scoped nav rules. Built
pages carry only JSON-LD `<script type="application/ld+json">` blocks — verified
on production across all five pages. Navigation no longer depends on JS to work.

If a future change reintroduces a script, that claim stops being true; the
`validate_built_site.py` privacy checks do not currently assert it.

Header height across the old breakpoint cliff is now flat:

| Width | 320px | 390px | 620px | 621px | 1010px |
|---|---|---|---|---|---|
| Nav rows | 2 | 1 | 1 | 1 | 1 |
| Header | 259px | 183px | 183px | 184px | 188px |

The 620/621 step is 1px, against 67px before this change and 142px under the
rejected root scaling. No horizontal overflow at any width tested.

## Audit work completed

### Performance and privacy

- Moved the profile photograph into Hugo's asset pipeline.
- Generate appropriately sized WebP and JPEG variants instead of serving the
  original 1084px image at 80px.
- Self-hosted the Fraunces and Source Serif 4 fonts.
- Removed Google Fonts, the embedded Google Maps iframe, and the inherited
  `counter.theconversation.edu.au` tracking pixel.
- Replaced the map embed with a lightweight location card linking to Google Maps.

### Accessibility and responsive design

- Ensured every generated content page has exactly one `<h1>`.
- Added an accessible mobile navigation button, `aria-current` navigation state,
  keyboard focus styling, and 44px mobile interaction targets. *Superseded
  18 September 2026: the navigation button is gone — see "Navigation restructure"
  above. `aria-current`, focus styling and 44px targets all remain.*
- Added dark-mode and reduced-motion support.
- Added a branded 404 page with navigation back into the site.
- Checked the site at desktop and 390px mobile widths; no horizontal overflow was
  found.

### Content, URLs, and SEO

- Reworked the homepage into a concise academic profile with clear calls to action,
  research areas, selected publications, current research, and supervision.
- Updated the About, Publications, Working Papers, Blog, Contact, Teaching, Vitae,
  Grants, and Links content.
- Established `/contact/` as the canonical contact URL, with aliases for the old
  WordPress paths. *Superseded 18 September 2026: `/contact/` now redirects to
  `/about/` — see the navigation restructure above.*
- Redirected `/kenan/` to the homepage and removed empty or obsolete content,
  including `/mturkfeedback/`, `/contact-3/`, duplicate Confusopoly content, and
  unused taxonomy pages.
- Repaired known broken Confusopoly references using DOI or Internet Archive links.
- Added richer Person structured data, canonical metadata, favicon, RSS discovery,
  Open Graph image, and a large Twitter/X card.
- Added the sitemap directive through Hugo's generated `robots.txt`.

### Visual assets

- Added `static/images/kenan-kalayci-social-card.jpg` at 1200×630.
- Added `static/favicon.svg`.
- Added local font files under `static/fonts/`.

### Automated checks

- Added `scripts/validate_built_site.py` to check generated HTML for headings,
  descriptions, canonical URLs, social images, image alternatives, safe external
  links, privacy regressions, and unresolved internal links.
- Strengthened `scripts/validate_site_links.py` so failures return a non-zero exit
  status and current Hugo routes/static assets are checked.
- Added both validators to the GitHub Pages workflow before artifact upload.
- Regenerated `reports/link-validation.md` and
  `reports/link-validation.csv`.

## Latest verification

Run locally with Hugo 0.164.0:

```text
Hugo production build:       passed
Generated pages:             11
Generated aliases:           14
Processed images:            2
Tracked URL validation:      56 checked, 0 failures, 0 warnings
Generated HTML validation:   22 files checked, passed
JSON validation:             passed
git diff --check:            passed
Responsive check:            1440/1200/1010/900/700/621/620/390/375/320px,
                             no horizontal overflow at any width
Colour schemes:              light and dark both verified
Behavioural JavaScript:      none (JSON-LD blocks only), checked on production
Deployed commit:             1a7b8c2
Not yet proofed:             print (no @media print block exists)
```

Two traps when verifying CSS changes locally, both of which produced wrong
readings during this work:

- The Hugo dev server serves `static/css/site.css` cached, and
  `location.reload(true)` is ignored by modern browsers. Measurements can reflect
  the *previous* stylesheet. Swap the `<link>` href with a cache-busting query to
  get true values.
- Screenshots can lag DOM reflow after a stylesheet swap or a colour-scheme
  switch. Trust computed styles over a screenshot when they disagree.

The committed link report checks internal/site-owned URLs. Known broken external
article links were repaired manually. A fully live external-link crawl is not part
of the deployment gate because third-party sites can block automated requests or
fail transiently.

## Publish procedure

1. Review the working-tree diff and preview locally if desired:

   ```bash
   hugo server --disableFastRender
   ```

2. Re-run the production checks:

   ```bash
   python3 scripts/validate_site_links.py \
     --content-dir content \
     --inventory data/content-inventory.json \
     --static-dir static \
     --site-domain kenankalayci.com \
     --out-csv reports/link-validation.csv \
     --out-md reports/link-validation.md

   hugo --minify --cleanDestinationDir
   python3 scripts/validate_built_site.py --public-dir public
   git diff --check
   ```

3. Commit and push to `main`.
4. Confirm the GitHub Pages workflow completes successfully.
5. Check the homepage, contact page, publications, PDFs, legacy redirects, custom
   404 page, `robots.txt`, and `sitemap.xml` on the production domain.
6. Confirm both `kenankalayci.com` and `www.kenankalayci.com` still work over HTTPS.

No DNS work is required to publish. `CUTOVER_CHECKLIST.md` documents the completed
March 2026 migration and is retained for history only.

## Future maintenance

- Update publications in `data/publications.json` and working papers in
  `data/working_papers.json`. Both now render on the single `/research/` page.
- **The homepage does not read those files.** `content/_index.md` hand-maintains
  its own copies of the publications and current-research lists, so every
  research change means editing the JSON *and* the homepage. Adding a new data
  key also needs a matching render block in `layouts/_default/single.html`, or it
  renders nothing.
- The same split applies to CSS. `/research/` wraps entries in `.citation-list`;
  the homepage's hand-written lists have no such wrapper, so a rule scoped to
  `.citation-list` silently skips every research link on the homepage. Check
  both when styling research links, and verify against built HTML in `public/`
  rather than a single page.
- To add a public article, give its page `research_writing: true` and it appears
  in the Public Writing section of `/research/` automatically.
- Update general profile metadata and navigation in `hugo.toml`. Note that
  `title` there is the displayed name and propagates widely through
  `.Site.Title`.
- Put new static downloads under `static/`, and page content under `content/`.
- Preserve aliases when changing a published URL.
- Let the deployment validators block releases with broken internal paths or HTML
  regressions.
