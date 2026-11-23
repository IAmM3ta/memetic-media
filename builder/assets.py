"""Build web-size images, OG cards and favicons for the Memetic Media sites.

Run:  python3 assets.py
Writes into ../<repo>/assets/. Source images stay untouched.

Sources
- Loop stills:  /workspace/products/memetic-loops-vol1/previews (own work, MORPHOS + QuasiForge)
- Archive art:  /workspace/m3metic (Instagram screenshots of the studio's own posts;
                we crop away every bit of Instagram UI and caption text)
- LedgerWright: /workspace/ledgerwright-marketing/gumroad/*/cover-1280x720.png
- LiTHOS:       generated here (procedural layer-line studies). No product photos exist yet,
                so we do not fake any.
"""
import subprocess, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
WS = Path('/workspace')
PREV = WS / 'products/memetic-loops-vol1/previews'
ARCH = WS / 'm3metic'
LW = WS / 'ledgerwright-marketing/gumroad'
FONT_SERIF = '/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/SourceSerifPro-Bold.ttf'
FONT_SANS = '/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf'

def out(repo, name):
    p = ROOT / repo / 'assets' / name
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def cover(im, w, h):
    """Center-crop to aspect w:h, then resize to exactly w x h."""
    im = im.convert('RGB'); sw, sh = im.size; r = w / h
    if sw / sh > r: nw = int(sh * r); im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else: nh = int(sw / r); im = im.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)

def webp(im, path, q=78):
    im.save(path, 'WEBP', quality=q, method=6)

def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght:
        try: f.set_variation_by_axes([14, wght] if 'opsz' in path else [wght])
        except Exception: pass
    return f

# ---------- LiTHOS procedural "layer-line" art ----------
def lithos_field(w, h, seed):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w] / max(w, h)
    f = np.zeros((h, w))
    for _ in range(7):  # sum of soft waves = smooth terrain
        a, b, ph = rng.uniform(-9, 9), rng.uniform(-9, 9), rng.uniform(0, 6.28)
        f += np.sin(a * x + b * y + ph) * rng.uniform(.3, 1)
    cx, cy = rng.uniform(.3, .7), rng.uniform(.25, .45)
    f += 3.2 * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / .05)
    return (f - f.min()) / (f.max() - f.min())

def lithos_art(w, h, seed, levels=22):
    """Quantize a height field into print-like layers; shade each layer, ink the edges."""
    f = lithos_field(w, h, seed)
    q = np.floor(f * levels) / levels
    charcoal, sand, teal = np.array([34, 36, 38]), np.array([214, 196, 164]), np.array([46, 128, 124])
    t = q[..., None]
    col = charcoal * (1 - t) + sand * t
    col = np.where((np.floor(f * levels) % 6 == 5)[..., None], teal * .55 + col * .45, col)
    edge = (np.abs(np.diff(q, axis=0, prepend=q[:1])) + np.abs(np.diff(q, axis=1, prepend=q[:, :1]))) > 0
    col[edge] = col[edge] * .45
    return Image.fromarray(col.clip(0, 255).astype('uint8')).filter(ImageFilter.SMOOTH)

# ---------- OG card ----------
def og_card(bg, kicker, title, sub, path, dark=True, accent=(230, 190, 120)):
    im = cover(bg, 1200, 630)
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(760):  # left-to-right scrim so text stays readable
        a = int(215 * max(0, 1 - i / 760) ** 1.2)
        d.line([(i, 0), (i, 630)], fill=(10, 10, 12, a) if dark else (246, 243, 238, a))
    im = Image.alpha_composite(im.convert('RGBA'), ov); d = ImageDraw.Draw(im)
    ink = (245, 240, 232) if dark else (36, 31, 28)
    d.text((72, 150), kicker.upper(), font=font(FONT_SANS, 28, 700), fill=accent)
    y = 200
    for line in title.split('\n'):
        d.text((72, y), line, font=font(FONT_SERIF, 76), fill=ink); y += 88
    d.text((72, y + 40), sub, font=font(FONT_SANS, 30, 450), fill=ink)
    im.convert('RGB').save(path, 'JPEG', quality=84, optimize=True, progressive=True)

def lw_og(path):
    """LedgerWright OG: clean paper card, headline left, product shot right (cover has its own text)."""
    im = Image.new('RGB', (1200, 630), (246, 243, 238)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1200, 10], fill=(15, 90, 74))
    shot = Image.open(LW / 'cashflow/cover-1280x720.png').convert('RGB')
    shot = shot.crop((560, 0, 1280, 720)).resize((520, 520), Image.LANCZOS)
    d.rectangle([636, 66, 1170, 600], fill=(222, 215, 204)); im.paste(shot, (640, 60))
    d.text((64, 150), 'LEDGERWRIGHT TEMPLATES', font=font(FONT_SANS, 26, 700), fill=(15, 90, 74))
    d.text((64, 200), 'Know your', font=font(FONT_SERIF, 80), fill=(36, 31, 28))
    d.text((64, 292), 'numbers.', font=font(FONT_SERIF, 80), fill=(36, 31, 28))
    d.text((64, 420), 'Cash Flow + Job-Cost trackers', font=font(FONT_SANS, 30, 450), fill=(58, 52, 46))
    d.text((64, 462), 'Excel + Google Sheets · from $14', font=font(FONT_SANS, 30, 450), fill=(58, 52, 46))
    im.save(path, 'JPEG', quality=86, optimize=True, progressive=True)

# ---------- favicon set ----------
def favicons(repo, letter, bg, fg):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           f'<rect width="64" height="64" rx="14" fill="{bg}"/>'
           f'<text x="32" y="45" font-family="Georgia,serif" font-size="38" font-weight="700" '
           f'text-anchor="middle" fill="{fg}">{letter}</text></svg>')
    out(repo, 'favicon.svg').write_text(svg)
    big = Image.new('RGB', (512, 512), bg); d = ImageDraw.Draw(big)
    f = font(FONT_SERIF, 330); bb = d.textbbox((0, 0), letter, font=f)
    d.text(((512 - bb[2] - bb[0]) / 2, (512 - bb[3] - bb[1]) / 2 - 10), letter, font=f, fill=fg)
    big.resize((180, 180), Image.LANCZOS).save(out(repo, 'apple-touch-icon.png'))
    big.resize((32, 32), Image.LANCZOS).save(out(repo, 'favicon-32.png'))
    big.resize((192, 192), Image.LANCZOS).save(out(repo, 'icon-192.png'))
    big.resize((512, 512), Image.LANCZOS).save(out(repo, 'icon-512.png'))
    big.save(ROOT / repo / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])

def main():
    stills = sorted(p for p in PREV.glob('*-still.png'))
    # --- crops of the archive screenshots: (file, box) art-only regions ---
    arch = [
        ('p_CySWZOYuXQ7_filigree_face.png', (184, 72, 530, 512), 'filigree'),
        ('p_DKMA5DsNfha_nahual_gold.png', (184, 72, 530, 512), 'nahual'),
        ('reel_C1jGdN9uxyr_projection.png', (238, 70, 505, 520), 'projection'),
        ('reel_DJe63e9pd5Z_liquid_face.png', (238, 70, 505, 520), 'liquid'),
        ('grid_bottom.png', (134, 133, 379, 392), 'grid-a'),
        ('grid_bottom.png', (632, 133, 877, 392), 'grid-c'),
    ]
    # ===== Memetic Media hub =====
    hero = Image.open(PREV / '02-solitons-morpho-still.png')
    for w in (1600, 800): webp(cover(hero, w, w * 9 // 16), out('memetic-media', f'hero-{w}.webp'), 70)
    for f, box, name in arch:
        im = Image.open(ARCH / f).convert('RGB').crop(box)
        webp(cover(im, 480, 600), out('memetic-media', f'work-{name}.webp'), 76)
    cards = {
        'agentops': Image.open(WS / 'agentops-studio/assets/og.png'),
        'ledgerwright': Image.open(LW / 'bundle/cover-1280x720.png'),
        'visuals': Image.open(PREV / '08-quasiforge-heptad-abyss-still.png'),
        'lithos': lithos_art(1200, 675, 7),
        'morphos': Image.open(WS / 'morphogen-og.jpg'),
    }
    for k, im in cards.items(): webp(cover(im, 720, 405), out('memetic-media', f'card-{k}.webp'), 78)
    og_card(hero, 'Memetic Media', 'Things that\nrespond.', 'Living visuals · generative objects · human-gated AI',
            out('memetic-media', 'og.jpg'))
    favicons('memetic-media', 'M', '#0d0d10', '#e6be78')

    # ===== Memetic Visuals =====
    for p in stills:
        webp(cover(Image.open(p), 640, 360), out('memetic-visuals', p.name.replace('-still.png', '.webp')), 74)
    webp(cover(Image.open(PREV / '01-living-abyss-still.png'), 1600, 900), out('memetic-visuals', 'hero-1600.webp'), 68)
    webp(cover(Image.open(PREV / '01-living-abyss-still.png'), 800, 450), out('memetic-visuals', 'hero-800.webp'), 70)
    webp(cover(Image.open(PREV / 'cover.png'), 640, 640), out('memetic-visuals', 'cover.webp'), 78)
    og_card(Image.open(PREV / '03-uskate-ember-still.png'), 'Memetic Visuals', 'Loops Vol. 1',
            '10 seamless 1080p VJ and projection loops', out('memetic-visuals', 'og.jpg'))
    favicons('memetic-visuals', 'V', '#0d0d10', '#7fd1c7')
    reel = out('memetic-visuals', 'preview-reel.mp4')
    if not reel.exists():  # 18 s watermarked reel -> small, muted, web-friendly
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(PREV / 'preview-reel.mp4'), '-an',
                        '-vf', 'scale=960:-2', '-c:v', 'libx264', '-crf', '30', '-preset', 'slow',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(reel)], check=True)

    # ===== LedgerWright templates =====
    for k in ('cashflow', 'jobcost', 'bundle'):
        webp(cover(Image.open(LW / k / 'cover-1280x720.png'), 960, 540), out('ledgerwright-templates', f'{k}.webp'), 82)
    lw_og(out('ledgerwright-templates', 'og.jpg'))
    favicons('ledgerwright-templates', 'L', '#0f5a4a', '#f6f3ee')

    # ===== LiTHOS =====
    big = lithos_art(1600, 900, 7)
    webp(big, out('lithos-studio', 'hero-1600.webp'), 74); webp(big.resize((800, 450)), out('lithos-studio', 'hero-800.webp'), 74)
    for i, s in enumerate((11, 23, 42), 1):
        webp(lithos_art(720, 720, s, levels=16 + 4 * i), out('lithos-studio', f'study-{i}.webp'), 76)
    og_card(big, 'LiTHOS', 'Objects, layer\nby layer.', 'Generative object studio · 3D print · laser',
            out('lithos-studio', 'og.jpg'), accent=(127, 209, 199))
    favicons('lithos-studio', 'L', '#222426', '#d6c4a4')

if __name__ == '__main__':
    main()
