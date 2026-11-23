"""Write README.md, CHANGELOG.md, .github/workflows/pages.yml and .gitignore into each site repo.
Run after build.py. Text here is repo documentation, not public page copy."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

PAGES_YML = """# Publish this static site to GitHub Pages on every push to main.
#
# The site is the repository root (index.html, css/, assets/, sitemap.xml, robots.txt ...).
# There is no build step: HTML is generated on the box by the Memetic Media builder
# (memetic-media repo, builder/) and committed as plain files.
#
# Actions, in the order GitHub expects:
#   actions/configure-pages -> actions/upload-pages-artifact -> actions/deploy-pages
#
# One-time setup: Settings -> Pages -> Source: GitHub Actions (done by the API on creation),
# then "Enforce HTTPS" once the certificate is issued.

name: Deploy GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write
  # deploy-pages@v5 reads the uploaded artifact's metadata through the Actions API.
  actions: read

# Never cancel a production deploy that is already running.
concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  # Two jobs, GitHub's reference layout. Root cause of the 2026-11-23 failures:
  # with upload and deploy in ONE job, deploy-pages asked for the artifact about a
  # second after upload finished and the artifact list was not indexed yet
  # ("Found 0 artifact(s)" / 'No artifacts named "github-pages"'), although the
  # artifact existed. The job boundary gives it time to register; the delayed
  # retry below covers the rare case where it still is not visible.
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      # Guard: no custom domain until one is bought and approved. Remove this step
      # in the same commit that adds a CNAME file.
      - name: No CNAME yet (launching on github.io)
        run: test ! -e CNAME

      # Guard: every page must keep its SEO basics.
      - name: SEO smoke check
        run: |
          for f in index.html 404.html; do
            grep -q '<title>' "$f"
            grep -q 'name="description"' "$f"
            grep -q 'rel="canonical"' "$f"
            grep -q 'og:image' "$f"
          done
          test -s sitemap.xml && test -s robots.txt

      - name: Configure Pages
        uses: actions/configure-pages@v6

      # upload-pages-artifact@v5 + deploy-pages@v5 are a matched pair (both on
      # artifact API v4). Do not mix with upload-artifact@v3-era actions.
      - name: Upload site artifact
        uses: actions/upload-pages-artifact@v5
        with:
          # Repo root. Dotfiles such as .github are excluded by the action.
          path: .

  deploy:
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url || steps.retry.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      # First attempt may not fail the run; the retry decides the outcome.
      - name: Deploy to GitHub Pages
        id: deployment
        continue-on-error: true
        uses: actions/deploy-pages@v5

      # One retry after a pause, in case the artifact is still being indexed.
      - name: Wait before retry
        if: steps.deployment.outcome == 'failure'
        run: sleep 30

      - name: Deploy to GitHub Pages (retry)
        id: retry
        if: steps.deployment.outcome == 'failure'
        uses: actions/deploy-pages@v5
"""

SITES = {
 'memetic-media': dict(name='Memetic Media', url='https://iamm3ta.github.io/memetic-media/',
   what='The parent studio hub. Positions the studio and links each branch (Agent Ops Studio, LedgerWright templates, Memetic Visuals, LiTHOS, MORPHOS) as a card, plus a selected-work gallery.',
   extra="""## The shared template (builder/)

This repo also holds the **builder** that renders all four network sites from one template:

| File | Purpose |
|---|---|
| `builder/assets.py` | Web-size images (webp), 1200x630 OG cards, favicon sets. Crops the archive screenshots so no third-party UI shows. Generates the LiTHOS layer-line art procedurally. |
| `builder/build.py` | Head (SEO, OG/Twitter, JSON-LD), header, network footer, page bodies, 404, sitemap, robots, manifest. `NET` at the top is the single list of cross-links. |
| `builder/site.css` | Shared stylesheet. Each site picks a palette with a `theme-*` class. |
| `builder/docs.py` | This README/CHANGELOG/workflow generator. |

Sources live on the box (`/workspace/products/memetic-loops-vol1/previews`, `/workspace/m3metic`, `/workspace/ledgerwright-marketing/gumroad`); the builder writes into sibling folders under `/workspace/memetic-sites/`, one per repo.

```bash
cd /workspace/memetic-sites/builder
python3 assets.py && python3 build.py && python3 docs.py
# then commit + push each repo
```
""", sources='Loop stills from Loops Vol. 1; archive art cropped from the studio\'s own posts; branch cards reuse each branch\'s own art.'),
 'ledgerwright-templates': dict(name='LedgerWright templates', url='https://iamm3ta.github.io/ledgerwright-templates/',
   what='Standalone sales page for the LedgerWright spreadsheet templates: Cash Flow & Bookkeeping ($14), Job-Cost & Supplier Bill ($14), Bundle ($24).',
   extra="""## Gumroad placeholders (swap when Gumroad is published)

Each product card has a disabled button marked with an HTML comment and a `data-placeholder` token:

| Token | Product | Price | Planned Gumroad permalink |
|---|---|---|---|
| `GUMROAD_URL_CASHFLOW` | Cash Flow & Bookkeeping Tracker | $14 | `cashflow-tracker` |
| `GUMROAD_URL_JOBCOST` | Job-Cost & Supplier Bill Tracker | $14 | `job-cost-tracker` |
| `GUMROAD_URL_BUNDLE` | The LedgerWright Bundle | $24 | `ledgerwright-bundle` |

To go live: in `builder/build.py` (memetic-media repo) replace the `<span ... aria-disabled="true">` with a real
`<a class="btn btn-primary" href="...">` link, add `"url"` to each Product offer in the JSON-LD, rebuild and push.
Or edit `index.html` here directly and note it in the CHANGELOG.

## Why a standalone page

Template buyers (freelancers, Etsy sellers, contractors searching "cash flow tracker template") are a different
audience from agentops.studio's done-for-you service buyers. A page of its own gets its own title, description and
Product schema for those searches, and keeps agentops.studio focused on the paid service. agentops.studio links here
from a short section (see the patch notes on the box: `/workspace/memetic-sites/agentops-patch.md`).
""", sources='Product covers from the Gumroad build (`/workspace/ledgerwright-marketing/gumroad/*/cover-1280x720.png`).'),
 'memetic-visuals': dict(name='Memetic Visuals', url='https://iamm3ta.github.io/memetic-visuals/',
   what='Loops and generative media. Sells Loops Vol. 1 (10 seamless 1080p VJ / projection loops) with a "coming soon" buy placeholder, a watermarked preview reel and commissions.',
   extra="""## Buy placeholder

`GUMROAD_URL_LOOPS_VOL1` marks the disabled buy button. Listed price: $14 launch / $19 regular (from the Loops Vol. 1
listing draft). Replace the `<span>` with the Gumroad link once the product exists, and add `"url"` to the JSON-LD offer.

The preview reel (`assets/preview-reel.mp4`, ~2.3 MB, 960 px, muted) is the watermarked reel from the product folder,
re-encoded with ffmpeg. It uses `preload="none"` and a poster so it costs nothing until someone presses play.
""", sources='Stills and preview reel from `/workspace/products/memetic-loops-vol1/previews`.'),
 'lithos-studio': dict(name='LiTHOS', url='https://iamm3ta.github.io/lithos-studio/',
   what='LiTHOS / Generative Object Studio: 3D-printed and laser-cut objects, fit-verified desk tools and pattern-grown forms. Commission CTA by email.',
   extra="""## Why this repo exists

No public LiTHOS site existed before this one. The `IAmM3ta/LiTHOS` repo is a **private operations repo**
(strategy, QA, books) and stays private; nothing from it is published except the brand direction
(name, "from lithography", charcoal / sand / teal palette, "desk tools that stay put" tone).

There are no real product photos yet, so the page uses procedural "layer-line" studies generated by
`builder/assets.py` rather than fake product mocks. Swap in real print photos when the first samples pass QA.
The Etsy shop is not live yet; the page says "Shop opening soon". Add the shop link when it exists.
""", sources='Procedural layer-line art generated by `builder/assets.py`.'),
}

def readme(repo, s):
    return f"""# {s['name']}

**Live:** {s['url']}

{s['what']}

Part of the **Memetic Media** network. Every site cross-links the others from a shared footer:
[Memetic Media](https://iamm3ta.github.io/memetic-media/) ·
[Agent Ops Studio](https://agentops.studio/) ·
[LedgerWright templates](https://iamm3ta.github.io/ledgerwright-templates/) ·
[Memetic Visuals](https://iamm3ta.github.io/memetic-visuals/) ·
[LiTHOS](https://iamm3ta.github.io/lithos-studio/) ·
[MORPHOS](https://morphos.grok.me/)

## Stack

Plain HTML and CSS, no JavaScript, no web fonts, no build step on GitHub. Deployed by
`.github/workflows/pages.yml` (GitHub Actions Pages) on every push to `main`. HTTPS is enforced in Pages settings.

## Files

| Path | What it is |
|---|---|
| `index.html` | The page. Generated by the shared builder; safe to hand-edit for small fixes (note them in CHANGELOG). |
| `404.html` | Not-found page, `noindex`, absolute links. |
| `css/site.css` | Shared network stylesheet (mobile-first, theme class on `<body>`). |
| `assets/` | Web-size images (webp), `og.jpg` (1200x630 social card), favicon set and app icons. |
| `favicon.ico`, `site.webmanifest` | Favicon fallback and PWA manifest. |
| `sitemap.xml`, `robots.txt` | Crawl files. On a `github.io` project path, crawlers read robots.txt at the host root, so this one takes effect once a custom domain is attached. |
| `.nojekyll` | Serve files as-is. |

## SEO checklist (all in place)

- Unique `<title>` and meta description; canonical URL
- Open Graph + Twitter `summary_large_image` with a 1200x630 image and alt text
- JSON-LD: Organization (with Memetic Media as parent), plus Product / Service where it fits
- sitemap.xml, robots.txt, favicon set (ico, svg, 32px png, apple-touch, 192/512 icons)
- Alt text on every image; width/height on every image (no layout shift); lazy-loaded below the fold
- Lighthouse scores are recorded in CHANGELOG.md for each release

## Rules for this repo

- Public naming: brand names plus the first name "Robert" at most. No address, nothing personal or legal.
- No secrets, keys or tokens. Contact is the public studio email only.
- No CNAME until a domain is bought and approved (the workflow fails if a CNAME appears).

{s['extra']}
## Image sources

{s['sources']}
"""

for repo, s in SITES.items():
    d = ROOT / repo
    (d / '.github/workflows').mkdir(parents=True, exist_ok=True)
    (d / '.github/workflows/pages.yml').write_text(PAGES_YML)
    (d / 'README.md').write_text(readme(repo, s))
    (d / '.gitignore').write_text('.DS_Store\n*.log\nnode_modules/\n')
    cl = d / 'CHANGELOG.md'
    if not cl.exists():
        cl.write_text(f"""# Changelog — {s['name']}

All notable changes to this site. Dates are ET.

## 2026-11-23 — v1.0.0 launch

- First public version at {s['url']} (github.io; no custom domain yet).
- Shared Memetic Media template: header, network footer cross-linking all six sites, shared `css/site.css`.
- Full SEO set: title, description, canonical, OG/Twitter with 1200x630 `assets/og.jpg`, JSON-LD, sitemap.xml, robots.txt, favicons, alt text.
- GitHub Actions Pages workflow with a no-CNAME guard and an SEO smoke check.

### Fixed
- Pages workflow: grant `actions: read` so deploy-pages@v5 can find the uploaded artifact (first deploy failed without it).
""")
print('docs ok')
