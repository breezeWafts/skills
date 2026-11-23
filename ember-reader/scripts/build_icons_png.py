# -*- coding: utf-8 -*-
"""ember-reader PNG icon builder - v1.4.0

Rasterises the app-icon SVG set into platform-ready PNGs with a real alpha
channel. The SVGs are rendered by a headless Chromium-family browser at each
target size (true vector rasterisation, never an upscale), then sliced out of
one transparent contact sheet with Pillow.

Why a browser and not cairosvg: the icon SVGs use CSS custom properties
(var(--icon-ink) etc.). Chromium resolves them; cairosvg does not, and its
Windows build also needs a libcairo DLL that is not always present.

Outputs under assets/png/ by default:
  ember-reader-{16,32,48,64,128,180,192,256,512}.png  master, transparent
  ember-reader-{dark,mono,card}-512.png                 variants
  ember-reader-512-opaque.png                          flattened, no alpha
  level-{1..4}-64.png / -256.png, study-plan, export   six companions
  favicon.ico                                           16/32/48 in one file
  preview.png                                          no-text contact sheet

Run:  python scripts/build_icons_png.py
"""

from pathlib import Path
import argparse
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

MASTER_SIZES = (16, 32, 48, 64, 128, 180, 192, 256, 512)
COMPANION_SIZES = (64, 256)
COMPANIONS = ("level-1", "level-2", "level-3", "level-4", "study-plan", "export")

BROWSER_CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
)

# Headless Chromium's visible viewport is ~70px shorter than --window-size.
# Ask for extra height; cropping coordinates still use the real page height.
VIEWPORT_MARGIN = 140

CARD_BG = (36, 36, 36, 255)       # #242424, the reference card colour
PAPER = (250, 248, 243, 255)      # #FAF8F3, warm-white tile
INDIGO = (82, 104, 131)           # #526883
VERMILION = (181, 72, 58)         # #B5483A


def find_browser():
    for name in ("msedge", "chrome", "chromium", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    for path in BROWSER_CANDIDATES:
        if Path(path).exists():
            return path
    raise SystemExit("No Chromium-family browser found. Install Edge/Chrome "
                     "or pass --browser <path>.")


def targets():
    """(output basename, svg path, edge size in px)."""
    items = []
    for size in MASTER_SIZES:
        items.append(("ember-reader-%d" % size, ASSETS / "icon.svg", size))
    for key, svg in (("dark", "icon-dark.svg"),
                     ("mono", "icon-mono.svg"),
                     ("card", "icon-card.svg")):
        items.append(("ember-reader-%s-512" % key, ASSETS / svg, 512))
    for key in COMPANIONS:
        for size in COMPANION_SIZES:
            items.append(("%s-%d" % (key, size), ASSETS / "icons" / (key + ".svg"), size))
    return items


def svg_at_size(path, size, seq):
    text = path.read_text(encoding="utf-8")
    # <title>/<desc> are accessibility names, not visible text. Drop them so
    # repeated ids across the sheet cannot collide, and keep pixels clean.
    text = re.sub(r"<title[^>]*>.*?</title>\s*", "", text, flags=re.S)
    text = re.sub(r"<desc[^>]*>.*?</desc>\s*", "", text, flags=re.S)
    text = text.replace(' role="img" aria-labelledby="ember-title ember-desc"', "")
    text, n = re.subn(r'width="[^"]*" height="[^"]*"',
                      'width="%d" height="%d"' % (size, size), text, count=1)
    if n != 1:
        raise SystemExit("width/height attributes not found in %s" % path.name)
    return text


def layout(items, gap=24, max_width=1600):
    """Absolute-position every icon so one screenshot yields all sizes."""
    cells, rows, row, row_w = [], [], [], 0
    for item in sorted(items, key=lambda t: -t[2]):
        size = item[2]
        if row and row_w + size + gap > max_width:
            rows.append(row)
            row, row_w = [], 0
        row.append((item, row_w))
        row_w += size + gap
    if row:
        rows.append(row)

    width = max_width + gap
    y = gap
    for row in rows:
        height = max(item[2] for item, _ in row)
        for item, x in row:
            cells.append((item, x + gap, y))
        y += height + gap
    return cells, width, y + gap


def paginate(cells, max_height=900, gap=24):
    """Split the sheet into short pages.

    Some headless builds silently clip content beyond ~1500px of viewport
    height; rendering one giant sheet loses the last row (the 16px icon).
    """
    blocks, current, base, bottom = [], [], None, 0
    for item, x, y in sorted(cells, key=lambda c: c[2]):
        size = item[2]
        if base is None:
            base = y
        if current and y + size - base > max_height:
            blocks.append((current, bottom - base + gap, base))
            current, base, bottom = [], y, y + size
        current.append((item, x, y))
        bottom = max(bottom, y + size)
    if current:
        blocks.append((current, bottom - base + gap, base))
    return blocks


def render_sheet(cells, width, height, workdir, browser, tag="0"):
    parts = [
        "<!doctype html><meta charset=utf-8>",
        "<style>html,body{margin:0;padding:0;background:transparent;"
        "width:%dpx;height:%dpx;overflow:hidden}" % (width, height),
        "div{position:absolute;line-height:0}svg{display:block}</style>",
    ]
    for seq, ((name, path, size), x, y) in enumerate(cells):
        parts.append('<div style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s</div>'
                     % (x, y, size, size, svg_at_size(path, size, seq)))
    html = workdir / "sheet.html"
    html.write_text("\n".join(parts), encoding="utf-8")
    shot = workdir / "sheet.png"
    cmd = [
        browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--no-first-run", "--disable-extensions", "--allow-file-access-from-files",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        "--user-data-dir=" + str(workdir / ("profile-" + tag)),
        "--window-size=%d,%d" % (width, height + VIEWPORT_MARGIN),
        "--screenshot=" + str(shot),
        html.as_uri(),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, timeout=180)
    if proc.returncode != 0 or not shot.exists():
        raise SystemExit("headless browser failed (exit %d)" % proc.returncode)
    return Image.open(shot).convert("RGBA")


def near(pixel, colour, tol=12):
    return all(abs(pixel[i] - colour[i]) <= tol for i in range(3)) and pixel[3] > 200


COLOUR_CHECKS = {
    "ember-reader-512": ((INDIGO, "indigo book"), (VERMILION, "vermilion dot")),
    "ember-reader-dark-512": (((112, 140, 177), "light indigo book"),
                              ((224, 112, 95), "dark vermilion dot")),
    "ember-reader-mono-512": (((28, 28, 28), "ink book"),),
    "ember-reader-card-512": ((INDIGO, "indigo book"), (VERMILION, "vermilion dot")),
}


def verify(path, size, name):
    im = Image.open(path)
    if im.size != (size, size):
        raise SystemExit("bad size: %s -> %s" % (path.name, im.size))
    rgba = im.convert("RGBA")
    counts = rgba.getcolors(maxcolors=size * size + 1) or []
    opaque = sum(count for count, pixel in counts if pixel[3] > 200)
    if opaque < size * size * 0.25:
        raise SystemExit("suspiciously empty icon: %s (%.1f%% opaque)"
                         % (path.name, 100.0 * opaque / (size * size)))
    box = rgba.getchannel("A").getbbox()
    if box and (box[2] - box[0] < size * 0.93 or box[3] - box[1] < size * 0.93):
        raise SystemExit("clipped icon: %s alpha_bbox=%s (expected nearly %dx%d)"
                         % (path.name, box, size, size))
    for colour, label in COLOUR_CHECKS.get(name, ()):
        if not any(near(pixel, colour) for _count, pixel in counts):
            raise SystemExit("missing %s in %s (CSS variables not resolved?)"
                             % (label, path.name))
    return round(100.0 * opaque / (size * size), 1)


def make_opaque(sheet_png, out):
    im = Image.open(sheet_png).convert("RGBA")
    bg = Image.new("RGBA", im.size, PAPER)
    bg.alpha_composite(im)
    bg.convert("RGB").save(out, optimize=True)


def make_favicon(master_512, out):
    Image.open(master_512).save(out, format="ICO",
                                sizes=[(16, 16), (32, 32), (48, 48)])


def make_preview(outdir):
    """Dark contact sheet: 4 master variants on top, 6 companions below. Zero text."""
    top = ["ember-reader-512.png", "ember-reader-dark-512.png",
           "ember-reader-mono-512.png", "ember-reader-card-512.png"]
    bottom = ["%s-256.png" % k for k in COMPANIONS]
    pad, gap, big, small = 24, 24, 176, 96
    slot_big, slot_small = big + gap, small + gap
    W = pad + max(4 * slot_big, 6 * slot_small) + pad
    H = pad + big + gap + small + pad
    canvas = Image.new("RGBA", (W, H), CARD_BG)
    for row, (names, size, slot, y) in enumerate(
            ((top, big, slot_big, pad), (bottom, small, slot_small, pad + big + gap))):
        left = pad + (W - 2 * pad - len(names) * slot) // 2
        for i, name in enumerate(names):
            im = Image.open(outdir / name).convert("RGBA").resize(
                (size, size), Image.LANCZOS)
            canvas.alpha_composite(im, (left + i * slot + (slot - size) // 2, y))
    canvas.convert("RGB").save(outdir / "preview.png", optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=Path, default=ASSETS / "png")
    ap.add_argument("--browser", default=None)
    args = ap.parse_args()

    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    browser = args.browser or find_browser()
    items = targets()
    cells, width, height = layout(items)
    print("browser: %s" % browser)
    print("contact sheet: %d x %d px, %d icons" % (width, height, len(cells)))

    pages = paginate(cells)
    print("pages: %d (max 900 px tall each)" % len(pages))
    with tempfile.TemporaryDirectory(prefix="ember-png-") as tmp:
        work = Path(tmp)
        for page_no, (page_cells, page_h, base) in enumerate(pages, 1):
            rel = [(item, x, y - base) for item, x, y in page_cells]
            sheet = render_sheet(rel, width, page_h, work, browser,
                                 tag=str(page_no))
            if sheet.width < width or sheet.height < page_h:
                raise SystemExit("page %d screenshot too small: %s vs %dx%d"
                                 % (page_no, sheet.size, width, page_h))
            for (name, _path, size), x, y in rel:
                dest = outdir / (name + ".png")
                crop = sheet.crop((x, y, x + size, y + size))
                # Very small tiles can be dropped by the compositor. Fall back
                # to a high-quality Lanczos downscale of the nearest larger
                # master so the favicon sizes are never empty.
                if size <= 16:
                    counts = crop.getcolors(maxcolors=size * size + 1) or []
                    if not any(pixel[3] > 200 for _n, pixel in counts):
                        src = Image.open(outdir / "ember-reader-64.png").convert("RGBA")
                        crop = src.resize((size, size), Image.LANCZOS)
                        print("  ~   %-30s downscaled from 64 px" % dest.name)
                crop.save(dest, optimize=True)
                fill = verify(dest, size, name)
                print("  ok  %-30s %4d px  %5.1f%% opaque" % (dest.name, size, fill))

    make_opaque(outdir / "ember-reader-512.png", outdir / "ember-reader-512-opaque.png")
    make_favicon(outdir / "ember-reader-512.png", outdir / "favicon.ico")
    make_preview(outdir)
    pngs = sorted(outdir.glob("*.png"))
    print("done: %d PNG + favicon.ico + preview.png -> %s" % (len(pngs), outdir))


if __name__ == "__main__":
    main()
