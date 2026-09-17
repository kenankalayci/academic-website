# Design proposal: type scale and flat layout

Drafted 17 September 2026. Revised after review, then **implemented**,
17 September 2026. Reference site: <https://kevinbryanecon.com/>.

**Status: applied.** The review's direction was followed — flat layout first,
then type tuned against it. Measured results are in "As implemented" below.

Superseded claims are struck through rather than deleted, so the reasoning
stays auditable. Every corrected figure below was re-measured in a live build.

---

## Review outcome

The review accepted both objectives and rejected both implementations as
written. Four factual errors in the first draft were confirmed and are corrected
below. Agreed direction:

1. Keep the proposed body sizes.
2. Cap the homepage headline near its current maximum.
3. Fix navigation as its own problem, not by widening the shell.
4. Prototype the flat layout first, then tune type, headline, nav and width
   together against it.

### Errors in the first draft

| Claim | Status |
|---|---|
| "Scaling the root preserves every ratio" | **Wrong.** Headings use `clamp()` with `vw` middle terms, which ignore root size. |
| Type table omitted the homepage hero | **Wrong.** It is the largest text on the site and moves the most. |
| "Header height 60 → 71px" | **Mislabelled.** That is `.site-nav`. `.site-header` is 210 → 232px. |
| "Remove card padding and every page loses its margins" | **Wrong.** `.site-shell` already has `padding: 1.4rem`. |
| Change B scope table | **Incomplete.** Omitted `.location-card` and the hover effects. |

---

## Change A — raise the body type

### Problem

Body copy is 16.6px. The reference site runs 20px. The section rhythm here is
already close; the body text is the gap.

### ~~First draft~~ (superseded)

> ~~1. `html { font-size: 118% }`~~
> ~~2. `.site-shell { max-width: 1140px }` (was 980px)~~
> ~~3. `html { font-size: 108% }` inside the 620px block~~
>
> ~~Scaling the root preserves every ratio.~~

Root scaling was rejected. It is untargeted — it moves margins, padding and
controls as well as text — and it interacts badly with the existing `clamp()`
headings. Where a `clamp()`'s `vw` term is the active one, the heading does not
respond to root size at all, so body text grows while headings stand still and
the ratio *compresses*:

| Viewport | h1 : body | Hero : body |
|---|---|---|
| 768px | 1.92 → 1.92 | 2.31 → 1.97 |
| 1010px | 2.43 → **2.06** | 3.03 → **2.57** |
| 1200px | 2.60 → **2.44** | 3.51 → **3.05** |
| 1440px | 2.60 → 2.60 | 3.51 → 3.51 |

It also dragged in two regressions that then needed two more edits to paper
over — the shell width and the mobile step-down existed only to repair damage
root scaling caused.

### Revised approach

Set the sizes that should change, and leave everything else alone. Root stays
at browser default.

This resolves three of the review's objections for free:

- **The hero stops moving.** `.home-intro h2` is `clamp(2.05rem, 5vw, 3.65rem)`;
  at a 16px root its maximum is 58.4px, exactly where it is today. Not scaling
  the root caps it without touching the rule.
- **Navigation stops regressing.** The pills keep their current size, so
  wrapping behaviour is unchanged from today's.
- **The shell can stay at 980px.** 1140px was only ever a nav workaround. At
  19.6px body the `70ch` measure is ~690px, which fits inside the current card
  comfortably.

Headings still need adjusting, because raising body copy past `h3` would invert
the hierarchy — `h3` is 18.6px against a proposed 19.6px body.

### Navigation is a standing defect, not collateral damage

Measured on the homepage, header = `.site-header` element:

| Width | Today | Under root scaling |
|---|---|---|
| 1440px | 1 row, 210px | 1 row, 232px |
| 1010px | 1 row, 210px | 2 rows, 294px |
| 621px | 2 rows, 236px | 3 rows, 329px |
| 620px | mobile menu | mobile menu, 187px |

The 621→620 discontinuity already exists at 236→~180px. Root scaling deepens it
to 329→187 but did not create it. Nine pills in a 980px shell is the underlying
problem and should be fixed on its own terms — most likely as part of Change B,
since flattening replaces the pills anyway.

---

## Change B — flatten the layout

### Rationale (sharpened by review)

The first draft argued from "cards look dated". The stronger argument is
structural: **the header and the main article are continuous page sections, not
separate objects.** Large rounded containers, shadows, gradients and a repeated
accent strip imply a separation that isn't there. A flat cream ground with
restrained section rules matches the content.

### Flatten these

| Location | What it does |
|---|---|
| `.site-header, .page-card` (110-111) | background, border, radius, shadow, `backdrop-filter` |
| `.site-header::before, .page-card::before` (121) | the 6px navy→yellow strip |
| `.page-card` (274-275) | `padding: clamp(1.4rem, 2.8vw, 2.25rem)` |
| `.home-card` (384) | cream gradient |
| `.research-card` (539) | cream gradient |
| `body` (37) | two radial gradients + linear wash, designed to sit behind floating cards |
| dark-mode block (790+) | re-applies the above |

### Keep these — flattening is not uniform

The review's key correction. Removing every panel and rounded control would
strip useful structure:

- **Research areas** → columns with spacing or a light rule, not boxes.
- **CV and contact buttons** → stay recognisable controls.
- **`.location-card` (643)** → keeps its grouping; it is a real object. *Omitted
  from the first draft's scope table.*
- **Navigation** → needs explicit hover, focus and current-page states once the
  pills go. This is where the wrapping problem gets solved.
- **Yellow** → retained as a restrained brand accent.

### Two corrections to the first draft's mechanics

- ~~"Remove card padding and every page loses its margins; the gutter has to
  move to `.site-shell`."~~ `.site-shell` already has `padding: 1.4rem`. The
  real effect is the gutter tightening from up to 36px down to 22px, so it
  needs raising, not creating.
- The scope table omitted `.location-card` and several hover effects
  (`.section-link-list a:hover`, `.button-link:hover`, `.site-nav a:hover`),
  all of which assume a raised surface to lift from.

### Estimate

An hour is reasonable for a first prototype, optimistic for a checked finish.
Dark mode, print, and every page other than the homepage still need visual
verification.

---

## As implemented

Flat layout first, then type tuned against it, as the review directed.

### Measured, homepage, `.site-header` element

| Width | Nav rows, before | Nav rows, after | Header, before | Header, after |
|---|---|---|---|---|
| 1440px | 1 | 1 | 210px | 188px |
| 1200px | 1 | 1 | 210px | 188px |
| 1010px | 1 | 1 | 210px | 188px |
| 900px | 1 | 1 | 210px | 188px |
| 700px | 2 | 2 | 267px | 236px |
| 621px | 2 | 2 | 236px | 236px |
| 620px | menu | menu | ~180px | 169px |
| 375px | menu | menu | — | 175px |

No horizontal overflow at any width. The 621→620 discontinuity is 236→169px,
against 236→~180px before and 329→187px under the rejected root scaling.

### Type

| | Before | After |
|---|---|---|
| Body copy | 16.6px | 19.6px |
| Body copy, mobile | 16.6px | 18.0px |
| `h3` | 18.6px | 22.4px |
| `h2` | 21.6–28.8px | 24.8–30.4px |
| `h1` | 32.0–43.2px | unchanged |
| Homepage hero | 58.4px max | **unchanged** |
| Homepage lede | 17.3–19.5px | 19.2–23.2px |
| Shell width | 980px | **unchanged** |

Root font size untouched. The hero cap, nav stability and 980px shell all follow
from not scaling the root, exactly as the revised approach predicted.

`.home-lede` had to be raised: at 19.5px max it would have fallen *below* the new
19.6px body copy and stopped reading as a lede. Not anticipated in either draft.

### Flattened

Page ground is now a solid `--page` token (`#fbf9f4` light, `#0d1c30` dark) —
solid because a translucent `body` background composites against the white
canvas. Card backgrounds, borders, radii, shadows and `backdrop-filter` removed
from `.site-header`, `.page-card`, `.home-card`, `.research-card`. The per-card
6px accent strip is replaced by a single 2px yellow rule under the header.
Research areas are columns with a top rule. Nav pills are flat links with
underline hover and a navy current-page underline.

### Kept

Buttons remain controls. `.location-card` and `.section-link-list a` keep a
border and a smaller radius for grouping, but lose gradient and shadow so they
are not the only floating objects left. Yellow survives as the header rule and
the nav hover. Hover states that lifted off a surface now shift background
instead.

### Verified

Both colour schemes; widths 1440/1200/1010/900/700/621/620/375; homepage,
publications, about, contact, supervision, blog. Link validator 62 URLs, 0
failures. Built-site validator 23 files. No `@media print` block exists — the
flat layout prints without shadows or fills, which is an improvement, but print
has not been visually proofed.

### Bug found and fixed during implementation

The dark-mode override carried `border-color: transparent` on `.site-header`,
which silently killed the new yellow rule in dark mode only. The base rule
already sets `border: 0`, so the line was both redundant and harmful.

---

## Not proposed

**Switching fonts.** Keep Fraunces and Source Serif 4. Both are self-hosted
already and pair at least as well as the reference site's Literata. That site's
mono appears only on small action links; its meta lines are italic serif and its
uppercase labels are letter-spaced serif, both of which Source Serif 4 does.
Confirmed by review.

**A rust accent colour.** Tried on 17 September 2026 and reverted. `#FFED00` is
a UQ brand colour that has to stay, and navy + rust + saturated yellow is a
three-way conflict.

---

## Remaining spelling inconsistency

The site title and contact page now use the Turkish dotless ı. These still carry
an ASCII `i`:

| Location | Visible? |
|---|---|
| `hugo.toml:12` — `keywords` array | No, feeds meta + JSON-LD `knowsAbout` |
| `layouts/_default/baseof.html:29,34` — `og:image:alt`, `twitter:image:alt` | No |
| `description` front matter in `_index.md`, `about`, `blog-posts` | No, search snippets |

Domain, email, X handle and PDF filenames correctly stay ASCII.
