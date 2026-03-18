## Plan: Migrate Your WordPress Site to GitHub Pages

Migrate in low-risk order: rebuild as a static site, preserve current URLs/PDF links, cut over DNS while staying at GoDaddy registrar first, then optionally transfer registrar later for lower annual cost.

I could not write to session memory because no workspace is open, so I saved this plan in global memory at /memories/plan.md.

**Steps**
1. Confirm scope and freeze content for migration window.
Include: homepage sections, publications, working papers, grants/awards, supervision page, links/resources, contact, current blog posts.
Exclude: WordPress plugin feature parity and dynamic features.

2. Choose stack and initialize repo.
Recommendation: Hugo + GitHub Actions + GitHub Pages.
Dependency: step 1.

3. Export and inventory existing WordPress content.
Collect XML export, current page URLs, and all PDF/media links.
Dependency: step 1.

4. Rebuild content as static pages with matching slugs.
Preserve current URL structure for key pages like supervision and blog posts.
Model publications as structured data so updates are easy later.
Dependency: steps 2 and 3.

5. Migrate PDFs/media with link stability strategy.
Preferred: keep legacy wp-content/uploads path in static output to avoid broken links.
Alternative: move to /pdfs and create redirects.
Dependency: step 3. Parallel with step 4 where possible.

6. Add SEO and redirect protections.
Set sitemap, robots, canonical metadata, and redirects for any changed URLs.
Dependency: step 4.

7. Configure GitHub Pages and validate before cutover.
Enable deploy workflow, custom domain setup, HTTPS, and full link checks.
Dependency: steps 4, 5, 6.

8. Cut over DNS (hosting first, registrar unchanged).
At GoDaddy DNS, point apex and www to GitHub Pages records.
Keep MX/SPF/DKIM/DMARC unchanged so email keeps working.
Dependency: step 7.

9. Stabilization and monitoring period.
Monitor 404s, crawl errors, and top PDF URLs for 1-2 weeks.
Keep old WordPress hosting as rollback safety for 2-4 weeks.
Dependency: step 8.

10. Optional registrar transfer for cost savings.
After stability, transfer domain from GoDaddy to a lower-cost registrar.
Dependency: step 9.

**Relevant files (new static site repo)**
- hugo.toml or config/default files for base URL and permalink rules
- content/index page files for homepage and sections
- content/supervision page
- content/blog-posts pages
- data/publications data file
- static/wp-content/uploads assets for legacy PDF paths
- static/CNAME for custom domain
- .github/workflows/deploy.yml for build and publish

**Verification**
1. Content parity: all current sections present and accurate.
2. URL parity: major existing URLs still resolve correctly.
3. PDF integrity: publication and working paper links download correctly.
4. DNS/HTTPS: apex and www resolve properly; certificate active.
5. Email continuity: MX/SPF/DKIM/DMARC unchanged and tested.
6. SEO health: sitemap submitted and crawl errors reviewed.
7. Device checks: desktop/mobile layout and navigation validated.

**Decisions captured**
- Migration order: hosting first, registrar transfer later.
- Cost approach: free hosting on GitHub Pages + cheaper registrar renewal.
- Risk control: prioritize URL/PDF continuity over redesign during first launch.

If you want, I can now produce the execution checklist day-by-day (Day 1, Day 2, Cutover Day) so you can follow it without guessing.
