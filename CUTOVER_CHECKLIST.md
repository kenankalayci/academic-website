# GitHub Pages + GoDaddy cutover checklist

This checklist covers the remaining manual steps after a green deployment pipeline.

---

## 1) Confirm GitHub Pages settings

In GitHub: **Settings → Pages**

| Setting | Required value |
|---|---|
| Source | GitHub Actions |
| Custom domain | `kenankalayci.com` |
| Enforce HTTPS | Enabled (activates after certificate issues) |

---

## 2) Your existing GoDaddy DNS — exact change table

Go to **DNS Management** for `kenankalayci.com`. Here is every row from your current zone and what to do with it:

| Type | Name | Current value | Action |
|---|---|---|---|
| A | @ | 148.66.137.114 | **DELETE** this record, then add 4 new A records below |
| A | becop | 148.66.137.114 | Leave unchanged |
| A | mturkfeedback | 148.66.137.114 | Leave unchanged |
| NS | @ | ns47.domaincontrol.com | Leave (uneditable) |
| NS | @ | ns48.domaincontrol.com | Leave (uneditable) |
| CNAME | calendar | calendar.secureserver.net | Leave (email service) |
| CNAME | email | email.secureserver.net | Leave (email service) |
| CNAME | fax | fax.secureserver.net | Leave (email service) |
| CNAME | files | files.secureserver.net | Leave (email service) |
| CNAME | ftp | kenankalayci.com | Leave (harmless old artifact) |
| CNAME | imap | imap.secureserver.net | Leave (email service) |
| CNAME | mobilemail | mobilemail-v01.prod.mesa1.secureserver.net | Leave (email service) |
| CNAME | pop | pop.secureserver.net | Leave (email service) |
| CNAME | smtp | smtp.secureserver.net | Leave (email service) |
| CNAME | www | kenankalayci.com | **EDIT** → change value to `kenankalayci.github.io` |
| CNAME | _domainconnect | _domainconnect.gd.domaincontrol.com | Leave (GoDaddy service) |
| SOA | @ | ns47.domaincontrol.com | Leave (uneditable) |
| MX | @ | smtp.secureserver.net (Priority 0) | **Leave — do not touch** |
| MX | @ | mailstore1.secureserver.net (Priority 10) | **Leave — do not touch** |

**Summary: only 2 things to do** — delete/replace the one A @ record, and edit the www CNAME.

---

## 3) New A records to add for @ (apex)

After deleting the old `A @ 148.66.137.114`, add these four records (all with Name `@`):

| Type | Name | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

Set TTL to 600 seconds initially. You can raise it to 3600 after 1-2 weeks of confirmed stability.

---

## 4) Wait for propagation and certificate

- DNS usually updates within minutes but ISP caches can hold old values temporarily.
- Back in GitHub Pages settings, wait for the domain check to show green.
- HTTPS certificate will issue automatically once DNS resolves correctly.
- Do not click Enforce HTTPS until the certificate is shown as active.

---

## 5) Post-cutover verification

Check from multiple networks/devices (mobile data is a useful secondary check):

- `https://kenankalayci.com/`
- `https://www.kenankalayci.com/`
- Publications, working papers, supervision, contact pages
- A few PDF links

Optional terminal spot-checks:

```bash
dig +short kenankalayci.com A
# Expected: 185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153

dig +short www.kenankalayci.com CNAME
# Expected: kenankalayci.github.io.
```

---

## 6) Stabilization window (2-4 weeks)

- Keep old GoDaddy WordPress hosting active as a read-only rollback.
- Watch for 404s and crawl errors via Google Search Console.
- If you need to roll back: restore `A @ 148.66.137.114` and revert `www CNAME` to `kenankalayci.com`.

---

## 7) After stabilization

- Raise A record TTL back to 3600+.
- Optionally transfer registrar from GoDaddy to a lower-cost provider.
- Cancel WordPress hosting plan on GoDaddy.
