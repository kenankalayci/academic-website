# kenankalayci.com static migration (Hugo)

This repository contains the static rebuild of kenankalayci.com from a WordPress XML export.

## Current status

- Hugo scaffold created.
- Automated XML import script available in `scripts/import_wordpress.py`.
- Local upload downloader available in `scripts/download_local_uploads.py`.
- Redirect map generator available in `scripts/build_redirect_map.py`.
- First-pass content generation has been run from `drkenankalayc.WordPress.2026-03-18.xml`.

## Run the migration scripts

```bash
python3 scripts/import_wordpress.py \
  --xml drkenankalayc.WordPress.2026-03-18.xml \
  --content-dir content \
  --data-dir data \
  --reports-dir reports

python3 scripts/extract_research_data.py \\
  --publications content/publications/index.md \\
  --workingpapers content/workingpapers/index.md \\
  --out-dir data

python3 scripts/download_local_uploads.py \
  --url-csv reports/url-inventory.csv \
  --out-dir static \
  --base-url https://kenankalayci.com

python3 scripts/build_redirect_map.py \
  --inventory data/content-inventory.json \
  --out reports/redirect-map.csv

python3 scripts/build_redirect_artifacts.py \\
  --xml drkenankalayc.WordPress.2026-03-18.xml \\
  --inventory data/content-inventory.json \\
  --out-csv reports/legacy-redirects.csv \
  --out-md reports/legacy-redirects.md

python3 scripts/validate_site_links.py \\
  --content-dir content \\
  --inventory data/content-inventory.json \\
  --static-dir static \\
  --site-domain kenankalayci.com \\
  --check-external \\
  --out-csv reports/link-validation.csv \
  --out-md reports/link-validation.md

python3 scripts/normalize_internal_links.py \\
  --content-dir content
```

## Generated artifacts

- `content/` first-pass Hugo pages/posts from published WordPress content.
- `data/content-inventory.json` page/post inventory for auditing.
- `data/publications.json` structured publications entries.
- `data/working_papers.json` structured working-paper and work-in-progress entries.
- `reports/url-inventory.csv` local-upload and PDF link inventory.
- `reports/pdf-inventory.csv` PDF link list with local-domain flags.
- `reports/import-report.txt` import counts and summary.
- `reports/redirect-map.csv` path-level redirect candidates.
- `reports/legacy-redirects.csv` legacy GUID/permalink redirect candidates.
- `reports/legacy-redirects.md` readable redirect candidate table.
- `reports/link-validation.csv` machine-readable link check results.
- `reports/link-validation.md` pre-cutover link validation report.
- `static/redirects.txt` human-maintained redirect mapping reference for cutover.

The internal-link normalizer rewrites absolute `kenankalayci.com` links in page bodies to canonical or root-relative links, while leaving `wordpress_link` front matter untouched for traceability.

Note: GitHub Pages does not natively apply `redirects.txt`. Use this file as a migration checklist and implement redirects through equivalent static page redirects, edge rules, or preserving old paths.

## Deploy

Push to `main`; GitHub Actions workflow in `.github/workflows/deploy.yml` builds and deploys to GitHub Pages.
