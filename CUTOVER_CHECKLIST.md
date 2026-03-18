# GitHub Pages + GoDaddy cutover checklist

This checklist covers the remaining manual steps after a green deployment pipeline.

## 1) Confirm GitHub Pages settings

- Repository: `kenankalayci/academic-website`
- In GitHub, go to Settings -> Pages.
- Source should be GitHub Actions.
- Custom domain should be `kenankalayci.com`.
- Ensure Enforce HTTPS is enabled (or becomes enabled once certificate issuance completes).

## 2) Prepare DNS in GoDaddy

- Go to DNS Management for `kenankalayci.com`.
- Lower TTL for records you will change (for example to 600 seconds) at least 15-30 minutes before cutover.
- Do not change mail-related records:
  - MX
  - SPF TXT
  - DKIM CNAME/TXT
  - DMARC TXT

## 3) Apply DNS records for GitHub Pages

Set apex/root (`@`) A records to:

- 185.199.108.153
- 185.199.109.153
- 185.199.110.153
- 185.199.111.153

Set `www` CNAME to:

- `kenankalayci.github.io`

Notes:
- Remove old hosting A/CNAME targets for `@` and `www` only.
- Keep unrelated subdomains and email records unchanged.

## 4) Wait for propagation and certificate

- DNS can update in minutes but may take longer depending on caches.
- In GitHub Pages settings, wait until the domain check passes.
- Wait until HTTPS is active and Enforce HTTPS is enabled.

## 5) Post-cutover verification

Check these from multiple networks/devices:

- `https://kenankalayci.com/`
- `https://www.kenankalayci.com/`
- Key pages (home, publications, working papers, supervision, contact)
- A sample of PDF links from reports.

Optional terminal checks:

```bash
dig +short kenankalayci.com A
dig +short www.kenankalayci.com CNAME
```

Expected:
- Apex returns GitHub Pages IPs above.
- `www` resolves to `kenankalayci.github.io`.

## 6) Stabilization window (recommended)

- Keep old WordPress hosting active for 2-4 weeks as rollback safety.
- Watch for crawl errors and 404s.
- Patch missing redirects/content quickly.

## 7) After stabilization

- Raise TTL back to a higher value (for example 3600+).
- Optionally transfer registrar later for cost savings.
