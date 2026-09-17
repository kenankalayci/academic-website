# Project handover

Last updated: 17 September 2026 (Australia/Brisbane)

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

## Open design proposal

`reports/design-proposal-typography-and-layout.md` is a **draft, not
implemented**. It covers two independent changes:

- **Change A, raise the type scale** — root to 118%, shell to 1140px, 108% below
  620px. Tested and measured; body copy goes 16.6px to 19.6px. The last two edits
  are not optional, they fix regressions the first one causes.
- **Change B, remove the card containers** — scoped but never prototyped. Roughly
  six rules carry the card chrome, but the page background, inner panels, nav
  pills and page gutter all have to follow.

Neither is in `main`. The stylesheet is untouched by them.

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
  keyboard focus styling, and 44px mobile interaction targets.
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
  WordPress paths.
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
Generated pages:             16
Generated aliases:           10
Processed images:            2
Tracked URL validation:      62 checked, 0 failures, 0 warnings
Generated HTML validation:   23 files checked, passed
JSON validation:             passed
git diff --check:            passed
Deployed commit:             d865282
Production spot-check:       header/title/footer/JSON-LD and contact page all
                             render “Kalaycı”, no mojibake
```

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

- Update publications in `data/publications.json`.
- Update working papers in `data/working_papers.json`.
- **The homepage does not read those files.** `content/_index.md` hand-maintains
  its own copies of the publications and current-research lists, so every
  research change means editing the JSON *and* the homepage. Adding a new data
  key also needs a matching render block in `layouts/_default/single.html`, or it
  renders nothing.
- The same split applies to CSS. The JSON-driven pages wrap entries in
  `.citation-list`; the homepage's hand-written lists have no such wrapper, so a
  rule scoped to `.citation-list` silently skips every research link on the
  homepage. Check both when styling research links, and verify against built HTML
  in `public/` rather than a single page.
- Update general profile metadata and navigation in `hugo.toml`. Note that
  `title` there is the displayed name and propagates widely through
  `.Site.Title`.
- Put new static downloads under `static/`, and page content under `content/`.
- Preserve aliases when changing a published URL.
- Let the deployment validators block releases with broken internal paths or HTML
  regressions.
