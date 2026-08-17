# Project handover

Last updated: 18 August 2026 (Australia/Brisbane)

## Current state

The Hugo rebuild and website-audit improvement pass are committed and synchronized
with `origin/main`. A new working-paper update is complete in the local working
tree, but has not yet been committed, pushed, or deployed.

- Repository: `https://github.com/kenankalayci/academic-website`
- Branch: `main`
- Current deployed baseline: `d36ac5e`
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

## Pending working-paper update

- Added the August 2026 manuscript *Algorithmic Third-Party Advice in Markets with
  Complex Goods* as a local site download.
- Corrected the co-authors from Zhengyang Bao to Leo Bao and Ruize Sun, matching
  the manuscript title page.
- Updated both the homepage Current Research section and the Working Papers page.
- Latest validation: 61 tracked URLs with zero failures or warnings; 23 generated
  HTML files passed validation; the 30-page PDF is present in the production build.

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
Tracked URL validation:      61 checked, 0 failures, 0 warnings
Generated HTML validation:   23 files checked, passed
JSON validation:             passed
git diff --check:            passed
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
- Update general profile metadata and navigation in `hugo.toml`.
- Put new static downloads under `static/`, and page content under `content/`.
- Preserve aliases when changing a published URL.
- Let the deployment validators block releases with broken internal paths or HTML
  regressions.
