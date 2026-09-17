# Design proposal: type scale and flat layout

Status: **draft, not implemented.** Nothing here is in `main`.
Drafted 17 September 2026. Reference site: <https://kevinbryanecon.com/>.

Two independent proposals. Change A is small, tested, and ready to apply.
Change B is larger and has not been prototyped.

---

## Change A — raise the type scale

### Problem

Body copy is 16.6px. The reference site runs 20px. The gap is most of why that
site reads as calm and this one reads as cramped. The section rhythm here is
already close to the reference; the headings are one step small throughout.

### The change

Three edits to `static/css/site.css`.

**1. Scale the root.** Insert immediately before the `body` rule at line 37:

```css
html {
  font-size: 118%;
}
```

**2. Widen the shell** (`.site-shell`, line 100):

```css
max-width: 1140px;   /* was 980px */
```

**3. Step down on small screens.** Add as the first rule inside the existing
`@media (max-width: 620px)` block (line 724):

```css
html {
  font-size: 108%;
}
```

### Why the root and not just paragraphs

Raising only `.page-card p` to `1.2rem` gives 19.2px body copy against an
unchanged 18.6px `h3` — headings would render smaller than the text beneath
them. Scaling the root preserves every ratio. Using a percentage rather than a
px value keeps the site responsive to a reader's own browser font setting,
which a fixed px root would override.

### Why edits 2 and 3 are not optional

They are not styling preferences; each fixes a regression introduced by edit 1.

- **Shell width.** At 980px the enlarged nav wraps from one row to two, and the
  header grows from 60px to 133px, pushing content down. Measured at a 1440px
  viewport, 1140px is the point where it returns to one row. 1060px is not
  enough.
- **Mobile step-down.** At 19.6px on a 375px screen, lines fall to five or six
  words. 108% gives 18px, matching what the reference site does at the same
  breakpoint.

### Measured result

| | Before | After |
|---|---|---|
| Body copy, desktop | 16.6px | 19.6px |
| Body copy, mobile | 16.6px | 18.0px |
| Measure | 601px | 690px |
| h3 | 18.6px | 21.9px |
| h2 | 21.6–28.8px | 25.5–34.0px |
| h1 | 32.0–43.2px | 37.8–51.0px |
| Nav rows at 1440px | 1 | 1 |
| Header height | 60px | 71px |

Reference site for comparison: 20px body, 760px measure, h1 `clamp(36px, 5vw,
52px)`, h2 27px, h3 22px, line-height 1.7.

### Verification already done

Built and checked at 1440px, 1010px, and 375px. No horizontal overflow at
375px. `validate_built_site.py` passes 23 files. Not yet checked: print
stylesheet, and the 700px/900px breakpoints between those tested.

---

## Change B — remove the card containers

### Problem

The floating-card layout reads as dated. The reference site puts content
directly on a flat warm surface with rules between sections and no borders,
shadows, or rounded panels.

### Scope

Smaller than it looks. The card chrome is concentrated in roughly six rules in
`static/css/site.css`:

| Location | What it does |
|---|---|
| `.site-header, .page-card` (110-111) | background, border, radius, shadow, `backdrop-filter` |
| `.site-header::before, .page-card::before` (121) | the 6px navy→yellow strip |
| `.page-card` (274-275) | `padding: clamp(1.4rem, 2.8vw, 2.25rem)` |
| `.home-card` (384) | cream gradient |
| `.research-card` (539) | cream gradient |
| dark-mode block (790+) | re-applies all of the above |

Stripping those is about 20 lines.

### What makes it more than 20 lines

The container is the easy part. Four things have to follow or the result looks
half-finished:

1. **The page background.** `body` carries two radial gradients plus a linear
   wash, designed to sit *behind* floating cards. With nothing floating it
   needs to go flat — most likely a solid `#fbf9f4`, the value the cards
   already use.
2. **The inner panels.** `.research-areas > div` and `.section-link-list a` are
   themselves small cards with borders, radii, and shadows. Removing the outer
   card but keeping these is inconsistent.
3. **The nav pills.** `border-radius: 999px` on nine items is the same visual
   era as the cards.
4. **Spacing.** `.page-card` padding currently provides the page gutter. Remove
   it and every page loses its margins; the gutter has to move to `.site-shell`.

### Estimate

About an hour, 30–40 lines touched out of 854, confined to one file. Fully
revertible through git. Worth prototyping on a branch before deciding, since
the outcome is a matter of taste and cheaper to judge rendered than described.

### Interaction with Change A

Change A widens the shell to 1140px to keep the nav on one row. If Change B
lands, the nav may fit differently once the pills are restyled, so revisit the
width then rather than treating 1140px as settled.

---

## Not proposed

**Switching fonts.** The reference uses Literata plus IBM Plex Mono. Fraunces
and Source Serif 4 are already self-hosted here and pair at least as well. The
mono is used only on that site's small action links — its meta lines are
italic serif and its uppercase labels are letter-spaced serif, both of which
Source Serif 4 already does. There is no typographic reason to switch, and
switching would discard the self-hosting and dark-mode work already done.

**A rust accent colour.** Tried on 17 September 2026 and reverted. Navy and
burnt orange pair well in principle, but `#FFED00` is a UQ brand colour that
has to stay, and navy + rust + saturated yellow is a three-way conflict.

---

## Remaining spelling inconsistency

The site title now uses the Turkish dotless ı (`Dr. Kenan Kalaycı`), which
fixes the header, footer, `<title>` tags, author meta, RSS, and JSON-LD
`Person.name`. These still carry an ASCII `i` and are unresolved:

| Location | Visible? |
|---|---|
| `content/contact/index.md:16` — `### Dr Kenan Kalayci` | **Yes**, rendered heading |
| `hugo.toml:12` — `keywords` array | No, feeds meta + JSON-LD `knowsAbout` |
| `layouts/_default/baseof.html:29,34` — `og:image:alt`, `twitter:image:alt` | No |
| `description` front matter in `_index.md`, `about`, `contact`, `blog-posts` | No, search snippets |

Domain, email, X handle, and PDF filenames correctly stay ASCII and must not
change.
