"""Static-site builder for the Memetic Media network.

One shared template (head, header, network footer, site.css) renders four
GitHub Pages sites. Output is plain HTML/CSS committed to each site repo, so
GitHub Pages needs no build step.

    python3 assets.py   # images, OG cards, favicons (once, or when art changes)
    python3 build.py    # HTML, CSS, sitemap.xml, robots.txt, 404, manifest

Naming rule baked in on purpose: brand names plus the first name "Robert" only.
Excluded projects (awaiting patent review) are never mentioned anywhere.
"""
import json, shutil, datetime
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.date(2026, 11, 23).isoformat()
CONTACT = 'robert@agentops.studio'   # already public on agentops.studio
# Free 20-row teardown (2026-11-24): prefilled mailto, no backend. & is HTML-escaped for attributes.
TEARDOWN_MAIL = ("mailto:robert@agentops.studio?subject=Free%2020-row%20teardown%20(LedgerWright)&amp;body=Hi%20Robert%2C%0D%0A%0D%0A"
                 "What%20the%20file%20is%3A%20%0D%0ARough%20number%20of%20rows%3A%20%0D%0AWhat%20the%20clean%20file%20needs%20to%20do%3A%20%0D%0A%0D%0A"
                 "Up%20to%2020%20rows%20pasted%20below%20or%20attached%20(dummy%20data%20is%20fine)%3A%0D%0A")
RESCUE_PAY = 'https://square.link/u/rX4tuObB'   # $150 Spreadsheet Rescue, same link as agentops.studio

# ---- every site in the network: the single source for cross-links ----
NET = [
    # key, name, url, one-line pitch
    ('hub', 'Memetic Media', 'https://iamm3ta.github.io/memetic-media/', 'The parent studio'),
    ('agentops', 'Agent Ops Studio', 'https://agentops.studio/', 'Human-gated AI ops and data cleanup'),
    ('ledgerwright', 'LedgerWright templates', 'https://iamm3ta.github.io/ledgerwright-templates/', 'Cash-flow and job-cost spreadsheets'),
    ('visuals', 'Memetic Visuals', 'https://iamm3ta.github.io/memetic-visuals/', 'Loops and generative media'),
    ('lithos', 'LiTHOS', 'https://iamm3ta.github.io/lithos-studio/', 'Generative object studio'),
    ('morphos', 'MORPHOS', 'https://morphos.grok.me/', 'A playable reaction-diffusion instrument'),
]
URL = {k: u for k, _, u, _ in NET}
ORG_HUB = {"@type": "Organization", "name": "Memetic Media", "url": URL['hub'],
           "logo": URL['hub'] + "assets/icon-512.png"}

def mailto(subject):
    return f"mailto:{CONTACT}?subject={subject.replace(' ', '%20')}"

def head(site, title, desc, path=''):
    """<head> with every SEO tag Lighthouse and social cards look for."""
    url = site['url'] + path
    ld = json.dumps(site['jsonld'], indent=1, ensure_ascii=False)
    preload = (f'<link rel="preload" as="image" href="assets/{site["hero"]}-800.webp" '
               f'imagesrcset="assets/{site["hero"]}-800.webp 800w, assets/{site["hero"]}-1600.webp 1600w" imagesizes="100vw">'
               if site.get('hero') else '')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="{site['theme_color']}">
<!-- Open Graph / Twitter: 1200x630 card in assets/og.jpg -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(site['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site['url']}assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(site['og_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{site['url']}assets/og.jpg">
<meta name="twitter:image:alt" content="{e(site['og_alt'])}">
<!-- favicon set -->
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
{preload}
<link rel="stylesheet" href="css/site.css">
<!-- Structured data (schema.org JSON-LD) -->
<script type="application/ld+json">
{ld}
</script>
</head>"""

def header(site):
    links = ''.join(f'<li><a href="{h}">{e(t)}</a></li>' for t, h in site['nav'])
    return f"""<body class="{site['theme']}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="./">{e(site['wordmark'])}</a>
    <nav aria-label="Main"><ul class="nav">{links}</ul></nav>
  </div>
</header>"""

def footer(site):
    """Network footer: the cross-link block every site shares."""
    items = []
    for k, name, url, pitch in NET:
        cur = ' aria-current="page"' if k == site['key'] else ''
        items.append(f'<li><a href="{url}"{cur}>{e(name)}</a> <span class="fine">· {e(pitch)}</span></li>')
    part = '' if site['key'] == 'hub' else f'<p>{e(site["name"])} is part of <a href="{URL["hub"]}">Memetic Media</a>.</p>'
    return f"""<footer class="site-footer">
  <div class="wrap">
    <h2>The Memetic Media network</h2>
    {part}
    <ul class="network">{''.join(items)}</ul>
    <p class="fine">© 2026 Memetic Media · {e(site['name'])} · <a href="{mailto(site['name'])}">{CONTACT}</a></p>
    {site.get('footnote', '')}
  </div>
</footer>
</body>
</html>
"""

def hero(site, kicker, h1, lede, actions, alt):
    img = ''
    if site.get('hero'):
        h = site['hero']
        img = (f'<img class="hero-media" src="assets/{h}-800.webp" srcset="assets/{h}-800.webp 800w, assets/{h}-1600.webp 1600w" '
               f'sizes="100vw" width="1600" height="900" alt="{e(alt)}" fetchpriority="high"><div class="hero-scrim"></div>')
    btns = ''.join(f'<a class="btn {c}" href="{h}">{e(t)}</a>' for t, h, c in actions)
    return f"""<section class="hero">
  {img}
  <div class="wrap">
    <p class="kicker">{e(kicker)}</p>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    <div class="actions">{btns}</div>
  </div>
</section>"""

def write(site, body, title, desc):
    d = ROOT / site['repo']
    (d / 'css').mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent / 'site.css', d / 'css/site.css')
    (d / 'index.html').write_text(head(site, title, desc) + '\n' + header(site) + '\n<main id="main">\n' + body + '\n</main>\n' + footer(site))
    # 404 page: same chrome, noindex, absolute links because it can be served at any depth
    nf = head(site, f'Page not found · {site["name"]}', f'This page does not exist. Go back to {site["name"]}.').replace(
        '<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"')
    nf = nf.replace('href="favicon.ico"', f'href="{site["url"]}favicon.ico"').replace('href="assets/', f'href="{site["url"]}assets/').replace(
        'href="css/', f'href="{site["url"]}css/').replace('href="site.webmanifest"', f'href="{site["url"]}site.webmanifest"')
    nf = nf.replace('imagesrcset="assets/', f'imagesrcset="{site["url"]}assets/')
    hdr = header(site).replace('href="./"', f'href="{site["url"]}"').replace('href="#', f'href="{site["url"]}#')
    (d / '404.html').write_text(nf + '\n' + hdr + f'\n<main id="main"><section class="band"><div class="wrap"><h1>Page not found</h1><p class="sub">That page is not here. <a href="{site["url"]}">Go to the {e(site["name"])} home page</a>.</p></div></section></main>\n' + footer(site))
    (d / 'robots.txt').write_text(f"# {site['name']}: everything is public. Note: on a github.io project URL, crawlers read\n# the robots.txt at the host root; this file takes effect once a custom domain is attached.\nUser-agent: *\nAllow: /\n\nSitemap: {site['url']}sitemap.xml\n")
    (d / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>{site["url"]}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n  </url>\n</urlset>\n')
    (d / 'site.webmanifest').write_text(json.dumps({"name": site['name'], "short_name": site['wordmark'][:12], "start_url": "./",
        "display": "standalone", "background_color": site['theme_color'], "theme_color": site['theme_color'],
        "icons": [{"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2) + '\n')
    (d / '.nojekyll').write_text('')

def card(href, img, alt, tag, title, text, go):
    return f"""<article class="card link">
  <img src="assets/{img}" width="720" height="405" loading="lazy" decoding="async" alt="{e(alt)}">
  <div class="body"><span class="tag">{e(tag)}</span><h3>{e(title)}</h3><p>{text}</p>
  <a class="go" href="{href}">{e(go)}</a></div>
</article>"""

# =====================================================================
# 1) Memetic Media hub
# =====================================================================
def build_hub():
    s = dict(key='hub', repo='memetic-media', name='Memetic Media', wordmark='Memetic Media', url=URL['hub'],
             theme='theme-dark', theme_color='#0d0d10', hero='hero', og_alt='Memetic Media: things that respond',
             nav=[('Branches', '#branches'), ('Work', '#work'), ('Studio', '#studio'), ('Contact', '#contact')])
    branches = [n for n in NET if n[0] != 'hub']
    s['jsonld'] = {"@context": "https://schema.org", "@graph": [
        {**ORG_HUB, "@id": URL['hub'] + "#org",
         "description": "Memetic Media is a small studio for living visuals, generative objects and human-gated AI systems, run by Robert.",
         "founder": {"@type": "Person", "name": "Robert"}, "email": CONTACT,
         "subOrganization": [{"@type": "Organization", "name": n, "url": u, "description": p} for k, n, u, p in branches]},
        {"@type": "WebSite", "name": "Memetic Media", "url": URL['hub'], "publisher": {"@id": URL['hub'] + "#org"}}]}
    cards = ''.join([
        card(URL['agentops'], 'card-agentops.webp', 'Agent Ops Studio card: messy bills in, a clean job-cost file out',
             'Systems', 'Agent Ops Studio', 'AI agents that do the busywork and stop for a person before anything goes out. Spreadsheet rescue, job-cost files, ops dashboards.', 'Visit Agent Ops Studio'),
        card(URL['ledgerwright'], 'card-ledgerwright.webp', 'LedgerWright Bundle cover showing the cash-flow and job-cost dashboards',
             'Templates', 'LedgerWright templates', 'Cash Flow and Job-Cost trackers for Excel and Google Sheets. Calm books in ten minutes a week. From $14.', 'See the LedgerWright templates'),
        card(URL['visuals'], 'card-visuals.webp', 'Seven-fold quasicrystal pattern in deep blue, a still from Loops Vol. 1',
             'Visuals', 'Memetic Visuals', 'Seamless VJ and projection loops grown from reaction-diffusion and quasicrystal math. Loops Vol. 1 is coming soon.', 'Explore Memetic Visuals'),
        card(URL['lithos'], 'card-lithos.webp', 'Layer-line study in charcoal, sand and teal, like the stacked layers of a 3D print',
             'Objects', 'LiTHOS', 'A generative object studio: 3D-printed and laser-cut pieces, from fit-verified desk tools to pattern-grown forms.', 'Meet LiTHOS'),
        card(URL['morphos'], 'card-morphos.webp', 'MORPHOS living field: pale reaction-diffusion colonies on black',
             'Instrument', 'MORPHOS', 'A living reaction-diffusion field you can play on your phone. A tap or a hold plants growth; touch it to hear it.', 'Play MORPHOS'),
    ])
    work = [('filigree', 'Filigree face: gold lace patterns over a portrait'),
            ('grid-a', 'Texture portrait: cracked enamel colour over a face in profile'),
            ('grid-c', 'Texture portrait: a face behind hands, painted in neon glaze'),
            ('liquid', 'Liquid face: marbled psychedelic colour on a staring face'),
            ('nahual', 'Ritual geometry: a golden figure wrapped by a serpent, with a mandala at the heart'),
            ('projection', 'Projection mapping: generative marble light on a venue wall above a crowd')]
    figs = ''.join(f'<figure class="work"><img src="assets/work-{k}.webp" width="480" height="600" loading="lazy" decoding="async" alt="{e(a)}"><figcaption>{e(a.split(":")[0])}</figcaption></figure>' for k, a in work)
    body = hero(s, 'Memetic Media · studio', 'Things that respond.',
                'Living visuals, objects grown from pattern, and AI systems that keep people in control. Memetic Media is the studio of Robert, artist and engineer.',
                [('See the branches', '#branches', 'btn-primary'), ('Commission work', mailto('Memetic Media commission'), 'btn-ghost')],
                'Blue reaction-diffusion solitons glowing on black, a still from Loops Vol. 1') + f"""
<!-- Branch cards: one per business line. Order = revenue first. URLs come from NET in build.py. -->
<section class="band" id="branches">
  <div class="wrap">
    <p class="kicker">One studio, five branches</p>
    <h2>Pick the part you came for</h2>
    <p class="sub">The same idea runs through all of it: a system that listens, then responds. For a business, that means agents that tidy the books. On a stage, it means light that grows. On a printer bed, it means objects shaped by pattern.</p>
    <div class="grid">{cards}</div>
  </div>
</section>
<!-- Selected archive work. Crops of the studio's own posts, compressed to webp. -->
<section class="band alt" id="work">
  <div class="wrap">
    <p class="kicker">Selected work</p>
    <h2>From the archive</h2>
    <p class="sub">Portrait studies, ritual geometry and live projection: years of generative image-making behind the loops and objects.</p>
    <div class="grid tight">{figs}</div>
  </div>
</section>
<section class="band" id="studio">
  <div class="wrap split">
    <div>
      <p class="kicker">The studio</p>
      <h2>Artist-engineer, physics first</h2>
      <p>Robert trained in physics and engineering, then spent years making large-scale projection and audiovisual work. Memetic Media is where the two halves meet.</p>
      <p>Real-time visuals come from the same equations that grow coral and fingerprints. Those patterns become printable objects. And on the systems side, multi-agent workflows split a job into small, self-checking steps, then stop for a human before anything irreversible goes out.</p>
    </div>
    <ul class="list">
      <li><strong>Visuals:</strong> reaction-diffusion and quasicrystal fields, VJ loops, projection mapping.</li>
      <li><strong>Objects:</strong> 3D print, resin and laser, from measured desk tools to pattern-grown forms.</li>
      <li><strong>Systems:</strong> human-gated AI agents, spreadsheet rescue, ops dashboards.</li>
      <li><strong>Instrument:</strong> MORPHOS, a living field you can touch and hear.</li>
    </ul>
  </div>
</section>
<section class="band alt" id="contact">
  <div class="wrap">
    <p class="kicker">Contact</p>
    <h2>Commissions, licensing, systems work</h2>
    <p class="sub">Projection pieces, custom loops, generative objects or an AI workflow for your business. Send a line about the project and a rough date.</p>
    <div class="actions"><a class="btn btn-primary" href="{mailto('Memetic Media inquiry')}">Email the studio</a><a class="btn btn-ghost" href="{URL['agentops']}">Hire for AI systems</a></div>
  </div>
</section>"""
    write(s, body, 'Memetic Media | Generative art, objects and human-gated AI studio',
          'Memetic Media is a studio for living visuals, generative 3D-printed objects and human-gated AI systems. Explore Agent Ops Studio, LedgerWright, Memetic Visuals, LiTHOS and MORPHOS.')

# =====================================================================
# 2) LedgerWright templates (standalone page; Gumroad checkout)
# =====================================================================
# Live product links, verified 2026-11-23: Cash Flow $14, Job-Cost $14,
# Bundle $24. Do not change prices without approval. Public only after
# a merge to main (GitHub Pages deploys from main).
LW_PRODUCTS = [
    # key, name, price, pitch, bullets, gumroad_url
    ('cashflow', 'Cash Flow & Bookkeeping Tracker', 14,
     'A calm, one-file bookkeeping system for freelancers, solopreneurs and small shops.',
     ['Monthly dashboard: income, expenses, net profit, margin', 'Invoice tracker that flags Paid, Due and Overdue', 'Tax set-aside planner by quarter', '27 ready-made categories'],
     'https://ledgerwright.gumroad.com/l/cashflow-tracker'),
    ('jobcost', 'Job-Cost & Supplier Bill Tracker', 14,
     'Budget vs actual for every job, by cost type. Built for contractors and trades.',
     ['Bills, labor and change orders tagged by job', 'OVER / WATCH / OK flags per cost type', 'Projected profit and margin per job', 'Portfolio view across every job'],
     'https://ledgerwright.gumroad.com/l/job-cost-tracker'),
    ('bundle', 'The LedgerWright Bundle', 24,
     'Both trackers: one for the whole business, one for every job. Save $4.',
     ['Cash Flow + Job-Cost workbooks', 'EXAMPLE and BLANK versions of each', 'Quick-Start Guides (PDF)', 'Best value for project businesses'],
     'https://ledgerwright.gumroad.com/l/ledgerwright-bundle'),
]

def build_ledgerwright():
    s = dict(key='ledgerwright', repo='ledgerwright-templates', name='LedgerWright templates', wordmark='LedgerWright',
             url=URL['ledgerwright'], theme='theme-paper', theme_color='#0f5a4a', og_alt='LedgerWright templates: know your numbers',
             nav=[('Templates', '#templates'), ('How it works', '#how'), ('Free teardown', '#rescue'), ('FAQ', '#faq'), ('Done-for-you', URL['agentops'])])
    org = {"@type": "Organization", "@id": URL['ledgerwright'] + "#org", "name": "LedgerWright", "url": URL['ledgerwright'],
           "logo": URL['ledgerwright'] + "assets/icon-512.png", "parentOrganization": ORG_HUB}
    s['jsonld'] = {"@context": "https://schema.org", "@graph": [org] + [
        {"@type": "Product", "name": f"LedgerWright {n} (Excel + Google Sheets)", "description": p,
         "image": URL['ledgerwright'] + f"assets/{k}.webp", "brand": {"@type": "Brand", "name": "LedgerWright"},
         "offers": {"@type": "Offer", "url": u, "price": f"{pr}.00", "priceCurrency": "USD", "seller": {"@id": URL['ledgerwright'] + "#org"}}}
        for k, n, pr, p, _, u in LW_PRODUCTS]}
    prods = ''
    for k, n, pr, p, bullets, url in LW_PRODUCTS:
        lis = ''.join(f'<li>{e(b)}</li>' for b in bullets)
        prods += f"""<article class="card" id="{k}">
  <img src="assets/{k}.webp" width="960" height="540" loading="lazy" decoding="async" alt="{e(n)}: dashboard preview with sample data">
  <div class="body"><span class="tag">Excel + Google Sheets</span><h3>{e(n)}</h3><p>{e(p)}</p>
  <ul class="list">{lis}</ul>
  <p class="price">${pr} <small>one-time, instant download</small></p>
  <!-- Gumroad checkout: {url}. Prices stay $14 / $14 / $24. -->
  <a class="btn btn-primary" href="{url}" target="_blank" rel="noopener noreferrer">Buy on Gumroad</a></div>
</article>"""
    body = hero(s, 'LedgerWright templates', 'Know your numbers in ten minutes a week.',
                'Spreadsheet templates for freelancers, small shops and contractors. Every number is a live formula. No macros, no subscription, no accounting software.',
                [('See the templates', '#templates', 'btn-primary'), ('File too messy? Free teardown', '#rescue', 'btn-ghost')], '') + f"""
<!-- Product cards. Prices: Cash Flow $14, Job-Cost $14, Bundle $24 (keep in sync with JSON-LD in build.py). -->
<section class="band" id="templates">
  <div class="wrap">
    <p class="kicker">Templates</p>
    <h2>Three ways to get your books straight</h2>
    <p class="sub">Each download includes an EXAMPLE file filled with realistic sample data and a BLANK file for your own numbers, plus a one-page Quick-Start Guide.</p>
    <div class="grid">{prods}</div>
  </div>
</section>
<section class="band alt" id="how">
  <div class="wrap split">
    <div>
      <p class="kicker">How it works</p>
      <h2>Log it once. The workbook does the rest.</h2>
      <p>Enter each sale, bill or expense on one row. Dropdowns keep the categories clean. The dashboards, flags and charts update themselves.</p>
      <p>Formula cells are protected without a password, so you can't break them by accident but can still customise anything.</p>
    </div>
    <dl class="facts">
      <dt>Format</dt><dd>Excel .xlsx, opens in Google Sheets</dd>
      <dt>Macros</dt><dd>None. Every number is a formula.</dd>
      <dt>Currency</dt><dd>Any; fiscal year can start in any month</dd>
      <dt>Delivery</dt><dd>Instant download after checkout</dd>
      <dt>Refunds</dt><dd>File won't open or doesn't match? Fix or full refund within 14 days.</dd>
    </dl>
  </div>
</section>
<!-- Free teardown + $150 Rescue CTA (added 2026-11-24). Remove this section, its nav item and hero button to revert. -->
<section class="band alt" id="rescue">
  <div class="wrap">
    <p class="kicker">Done-for-you</p>
    <h2>Your file too messy for a template?</h2>
    <p class="sub">Send 20 rows of the spreadsheet you have now. Dummy data is fine. Within one business day you get a free 10-minute teardown: what is broken, what a clean version looks like, and a fixed price. A full cleanup of up to 500 rows is a flat $150, back in 48 hours, with every repair labeled and nothing invented.</p>
    <div class="actions"><a class="btn btn-primary" href="{TEARDOWN_MAIL}">Email 20 rows for a free teardown</a><a class="btn btn-ghost" href="{RESCUE_PAY}" target="_blank" rel="noopener noreferrer">Book the $150 Rescue</a></div>
    <p class="fine">Leave out Social Security numbers, full card or bank numbers and passwords. Run by Robert at <a href="{URL['agentops']}">Agent Ops Studio</a>. Not tax, legal or accounting advice.</p>
  </div>
</section>
<section class="band" id="faq">
  <div class="wrap">
    <p class="kicker">FAQ</p>
    <h2>Questions people ask</h2>
    <h3>Who is it for?</h3>
    <p>Freelancers, consultants, makers, Etsy and Shopify sellers, coaches, trades and side hustles that want simple cash-basis books. The Job-Cost tracker is for contractors, builders, remodelers and agencies that bill by project.</p>
    <h3>Who is it not for?</h3>
    <p>Businesses that need double-entry accounting, payroll, inventory valuation or sales-tax filing. Use accounting software or a bookkeeper for those.</p>
    <h3>Would you rather have someone clean up the mess first?</h3>
    <p>That is the done-for-you side: <a href="{URL['agentops']}">Agent Ops Studio's Spreadsheet Rescue</a> takes messy bills and spreadsheets and hands back a categorized, job-tagged file.</p>
    <p class="fine">A planning and record-keeping tool, not tax, legal or accounting advice. Digital download only.</p>
  </div>
</section>"""
    write(s, body, 'Google Sheets & Excel Cash Flow Tracker and Job Cost Templates | LedgerWright',
          'Cash flow tracker and job cost spreadsheet templates for small business, freelancers and contractors. Excel + Google Sheets, live formulas, no macros. From $14.')

# =====================================================================
# 3) Memetic Visuals (Loops Vol. 1, buy button is a placeholder)
# =====================================================================
LOOPS = [('01-living-abyss', 'Living · Abyss'), ('02-solitons-morpho', 'Solitons · Morpho'), ('03-uskate-ember', 'U-Skate · Ember'),
         ('04-holes-silver', 'Holes · Silver'), ('05-fingerprint-morpho', 'Fingerprint · Morpho'), ('06-worms-field', 'Worms · Field'),
         ('07-coral-chlorophyll', 'Coral · Chlorophyll'), ('08-quasiforge-heptad-abyss', 'Quasicrystal 7-fold · Abyss'),
         ('09-quasiforge-pentad-violet', 'Quasicrystal 5-fold · Violet'), ('10-quasiforge-ennead-ember', 'Quasicrystal 9-fold · Ember')]

def build_visuals():
    s = dict(key='visuals', repo='memetic-visuals', name='Memetic Visuals', wordmark='Memetic Visuals', url=URL['visuals'],
             theme='theme-dark theme-visuals', theme_color='#0d0d10', hero='hero', og_alt='Memetic Visuals Loops Vol. 1: 10 seamless 1080p loops',
             nav=[('Loops Vol. 1', '#loops'), ('Preview', '#preview'), ('License', '#license'), ('Commissions', '#commission')])
    org = {"@type": "Organization", "@id": URL['visuals'] + "#org", "name": "Memetic Visuals", "url": URL['visuals'],
           "logo": URL['visuals'] + "assets/icon-512.png", "parentOrganization": ORG_HUB}
    s['jsonld'] = {"@context": "https://schema.org", "@graph": [org, {
        "@type": "Product", "name": "Memetic Visuals Loops Vol. 1: 10 seamless 1080p VJ and projection mapping loops",
        "description": "Ten seamless 12-second 1920x1080 30 fps loops for VJ sets, LED walls and projection mapping, grown from reaction-diffusion and quasicrystal math.",
        "image": URL['visuals'] + "assets/cover.webp", "brand": {"@type": "Brand", "name": "Memetic Visuals"},
        "offers": {"@type": "Offer", "price": "14.00", "priceCurrency": "USD", "seller": {"@id": URL['visuals'] + "#org"}}}]}
    tiles = ''.join(f'<figure><img src="assets/{k}.webp" width="640" height="360" loading="lazy" decoding="async" alt="Loop still: {e(n)}"><figcaption>{e(n)}</figcaption></figure>' for k, n in LOOPS)
    body = hero(s, 'Memetic Visuals · loops and generative media', 'Light that grows.',
                'Seamless VJ and projection-mapping loops grown from reaction-diffusion chemistry and quasicrystal math. Dark palettes, built to sit under a show.',
                [('See Loops Vol. 1', '#loops', 'btn-primary'), ('Watch the preview', '#preview', 'btn-ghost')],
                'Glowing reaction-diffusion field in deep blue on black') + f"""
<section class="band" id="loops">
  <div class="wrap split">
    <div>
      <p class="kicker">Loops Vol. 1</p>
      <h2>Ten seamless loops for live visuals</h2>
      <p>Seven Gray-Scott reaction-diffusion fields from the MORPHOS presets and three quasicrystal fields from the QuasiForge shader. Each one plays end to end without a visible cut.</p>
      <dl class="facts">
        <dt>Clips</dt><dd>10 loops, 12 seconds each</dd>
        <dt>Format</dt><dd>1920×1080, 30 fps, H.264 MP4, no audio</dd>
        <dt>Works in</dt><dd>Resolume, VDMX, MadMapper, TouchDesigner, HeavyM, any looping player</dd>
        <dt>Includes</dt><dd>Contact sheet, preview reel, license, cover still</dd>
      </dl>
      <p class="price">$14 <small>launch price · regular $19</small></p>
      <!-- PLACEHOLDER: GUMROAD_URL_LOOPS_VOL1. Replace the <span> with the Gumroad product link when it exists. -->
      <div class="actions"><span class="btn" aria-disabled="true" data-placeholder="GUMROAD_URL_LOOPS_VOL1">Buy link coming soon</span>
      <a class="btn btn-ghost" href="{mailto('Loops Vol. 1 - notify me')}">Email me at launch</a></div>
    </div>
    <img src="assets/cover.webp" width="640" height="640" loading="lazy" decoding="async" alt="Loops Vol. 1 cover: amber reaction-diffusion worms on dark red">
  </div>
</section>
<section class="band alt" id="preview">
  <div class="wrap">
    <p class="kicker">Preview</p>
    <h2>Watch all ten in eighteen seconds</h2>
    <p class="sub">Watermarked, downscaled preview. The pack itself is clean 1080p.</p>
    <div class="media-frame"><video controls muted loop playsinline preload="none" width="960" height="540" poster="assets/hero-800.webp" aria-label="Preview reel of all ten loops in Loops Vol. 1">
      <source src="assets/preview-reel.mp4" type="video/mp4"></video></div>
    <div class="grid tight">{tiles}</div>
  </div>
</section>
<section class="band" id="license">
  <div class="wrap">
    <p class="kicker">License</p>
    <h2>Use them on stage, on stream, on walls</h2>
    <p class="sub">Royalty-free for live performance, projection mapping, events and streams. You may not resell or redistribute the raw files. These are algorithmic fields, not an AI slideshow: they come from the same equations as the <a href="{URL['morphos']}">MORPHOS living-field instrument</a>.</p>
  </div>
</section>
<section class="band alt" id="commission">
  <div class="wrap">
    <p class="kicker">Commissions</p>
    <h2>Need visuals cut for your venue?</h2>
    <p class="sub">Custom palettes, mapped surfaces, longer loops or 4K renders. Tell us the room, the screen and the date.</p>
    <div class="actions"><a class="btn btn-primary" href="{mailto('Memetic Visuals commission')}">Ask about a commission</a></div>
  </div>
</section>"""
    write(s, body, 'Memetic Visuals | Seamless VJ and Projection Mapping Loops, Vol. 1',
          'Ten seamless 1080p VJ and projection-mapping loops grown from reaction-diffusion and quasicrystal math. Loops Vol. 1 from Memetic Visuals, launching at $14.')

# =====================================================================
# 4) LiTHOS / Generative Object Studio (no prior public site existed)
# =====================================================================
def build_lithos():
    s = dict(key='lithos', repo='lithos-studio', name='LiTHOS', wordmark='LiTHOS', url=URL['lithos'],
             theme='theme-lithos', theme_color='#1d1f21', hero='hero', og_alt='LiTHOS: objects, layer by layer',
             nav=[('Objects', '#objects'), ('Process', '#process'), ('Commission', '#commission')])
    org = {"@type": "Organization", "@id": URL['lithos'] + "#org", "name": "LiTHOS", "alternateName": "LiTHOS Generative Object Studio",
           "url": URL['lithos'], "logo": URL['lithos'] + "assets/icon-512.png", "parentOrganization": ORG_HUB}
    s['jsonld'] = {"@context": "https://schema.org", "@graph": [org, {
        "@type": "Service", "name": "Custom 3D-printed and generative objects", "serviceType": "3D printing and laser fabrication",
        "provider": {"@id": URL['lithos'] + "#org"}, "areaServed": "US", "url": URL['lithos'],
        "description": "Made-to-order 3D-printed desk tools and generative objects, with measured, fit-verified dimensions."}]}
    studies = [('study-1', 'Layer-line study I: terraced charcoal and sand contours'),
               ('study-2', 'Layer-line study II: tight strata with teal bands'),
               ('study-3', 'Layer-line study III: dense contours around a raised peak')]
    figs = ''.join(f'<figure><img src="assets/{k}.webp" width="720" height="720" loading="lazy" decoding="async" alt="{e(a)}"><figcaption>{e(a.split(":")[0])}</figcaption></figure>' for k, a in studies)
    body = hero(s, 'LiTHOS · generative object studio', 'Objects, layer by layer.',
                'LiTHOS, from <em>lithography</em>, makes 3D-printed and laser-cut objects: precise desk tools that stay put, and generative forms grown from pattern.',
                [('See what we make', '#objects', 'btn-primary'), ('Start a commission', '#commission', 'btn-ghost')],
                'Terraced contour layers in charcoal, sand and teal, like a sliced 3D print') + f"""
<section class="band" id="objects">
  <div class="wrap">
    <p class="kicker">Objects</p>
    <h2>Two lines, one standard: it has to fit</h2>
    <div class="grid">
      <article class="card"><div class="body"><span class="tag">Desk tools</span><h3>Fit-verified hardware</h3>
        <p>Cable organizers, device cradles and desk clamps, made to order. Each listing states the measured dimensions from a printed sample, never a guess.</p>
        <p class="placeholder-note">Shop opening soon.</p></div></article>
      <article class="card"><div class="body"><span class="tag">Generative</span><h3>Pattern-grown forms</h3>
        <p>Reaction-diffusion patterns grown in software, then exported as printable meshes and laser files with the open-source <a href="https://github.com/IAmM3ta/turing">TURiNG pipeline</a>.</p></div></article>
      <article class="card"><div class="body"><span class="tag">Custom</span><h3>One-offs and small runs</h3>
        <p>Replacement parts, mounts, signage, gifts and limited editions in PLA, PETG, resin, wood or acrylic.</p></div></article>
    </div>
    <div class="grid tight">{figs}</div>
  </div>
</section>
<section class="band alt" id="process">
  <div class="wrap split">
    <div>
      <p class="kicker">Process</p>
      <h2>Measure, print, check, ship</h2>
      <ol class="list">
        <li><strong>Spec:</strong> lock the critical dimensions first: the pocket, the jaw, the clearance.</li>
        <li><strong>Print:</strong> overnight runs on a small fleet of large-format and high-speed FDM printers, plus resin and laser for detail work.</li>
        <li><strong>Check:</strong> a first-article sample is measured against the spec before anything ships.</li>
        <li><strong>Ship:</strong> with a care card and honest material notes. Doesn't fit as described? Tell us.</li>
      </ol>
    </div>
    <img src="assets/study-2.webp" width="720" height="720" loading="lazy" decoding="async" alt="Contour strata in sand and teal, a visual of stacked print layers">
  </div>
</section>
<section class="band" id="commission">
  <div class="wrap">
    <p class="kicker">Commission</p>
    <h2>Have something that needs to exist?</h2>
    <p class="sub">Send a sketch, a photo of the space and the measurements that matter. We'll reply with a quote and a lead time.</p>
    <div class="actions"><a class="btn btn-primary" href="{mailto('LiTHOS commission')}">Request a quote</a><a class="btn btn-ghost" href="{URL['morphos']}">Play with the patterns in MORPHOS</a></div>
  </div>
</section>"""
    write(s, body, 'LiTHOS | Generative Object Studio for 3D-Printed and Laser-Cut Objects',
          'LiTHOS is a generative object studio: made-to-order 3D-printed desk tools with measured fit, pattern-grown forms and custom laser-cut pieces. Part of Memetic Media.')

if __name__ == '__main__':
    build_hub(); build_ledgerwright(); build_visuals(); build_lithos()
    print('built', [p.name for p in ROOT.iterdir() if (p / 'index.html').exists()])
