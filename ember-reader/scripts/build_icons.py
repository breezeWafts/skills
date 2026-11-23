# -*- coding: utf-8 -*-
"""ember-reader icon builder - v1.2.0

App-icon language, zero visible text:
  warm-white squircle tile + one dark-blue-grey geometric subject + generous
  negative space. No <text> node is emitted in any asset.

Run:  python scripts/build_icons.py
Outputs 12 SVG files under assets/ and validates each one as XML.
"""

from pathlib import Path
import xml.dom.minidom as minidom

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

# One palette family, three adaptive variants. Same geometry, only tokens change.
PALETTES = {
    "light": {
        "bg": "#FAF8F3", "edge": "rgba(28,28,28,0.06)", "ink": "#526883",
        "cut": "#FAF8F3", "ha": "#B5483A", "card": "#1C1C1C",
    },
    "dark": {
        "bg": "#24262A", "edge": "rgba(255,255,255,0.08)", "ink": "#708CB1",
        "cut": "#24262A", "ha": "#E0705F", "card": "#141618",
    },
    "mono": {
        "bg": "#FAF8F3", "edge": "rgba(28,28,28,0.14)", "ink": "#1C1C1C",
        "cut": "#FAF8F3", "ha": "#1C1C1C", "card": "#FFFFFF",
    },
}

TOKEN_KEYS = ("bg", "edge", "ink", "cut", "card")

# rx is an SVG 1.1 geometry attribute: CSS var() inside a presentation attribute
# is not resolved by Chromium, so the tile keeps a literal radius. All colour,
# stroke and card values remain token-driven and can be overridden by the host.
TILE_RADIUS = 20


def token_style(palette):
    pairs = ["--icon-%s:%s" % (k, palette[k]) for k in TOKEN_KEYS]
    pairs.append("--accent-ha:%s" % palette["ha"])
    pairs.append("--icon-stroke:1.5")
    pairs.append("--icon-radius:%dpx" % TILE_RADIUS)
    return ";".join(pairs) + ";"


def head(w, h, size, palette, title, desc):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="%d" height="%d" role="img" aria-labelledby="ember-title ember-desc" '
        'style="%s">\n'
        '  <title id="ember-title">%s</title>\n'
        '  <desc id="ember-desc">%s</desc>\n'
    ) % (w, h, size, size, token_style(palette), title, desc)


CONTAINER = (
    '  <rect x="1" y="1" width="62" height="62" rx="%d" '
    'fill="var(--icon-bg)" stroke="var(--icon-edge)" stroke-width="1"/>\n'
) % TILE_RADIUS

# Shared book-spine baseline: every icon in the set stands on the same book.
SPINE = (
    '  <path d="M21 47 H43" fill="none" stroke="var(--icon-ink)" '
    'stroke-width="var(--icon-stroke)" stroke-linecap="round"/>\n'
)

LINE_OPEN = (
    '  <g fill="none" stroke="var(--icon-ink)" stroke-width="var(--icon-stroke)" '
    'stroke-linecap="round" stroke-linejoin="round">\n'
)


def main_graph():
    """The single subject: a closed book, with the knowledge tree cut out of it."""
    return (
        '  <!-- one closed book: a solid tile; the trunk is cut out of it -->\n'
        '  <rect x="17" y="19" width="30" height="30" rx="9" fill="var(--icon-ink)"/>\n'
        '  <g fill="none" stroke="var(--icon-cut)" stroke-width="var(--icon-stroke)" '
        'stroke-linecap="round" stroke-linejoin="round">\n'
        '    <path d="M32 41 V24"/>\n'
        '    <path d="M32 38 C27 38 23.5 35.5 21.5 32.5"/>\n'
        '    <path d="M32 38 C37 38 40.5 35.5 42.5 32.5"/>\n'
        '    <path d="M32 33 C28.5 33 26 30.5 24.5 28"/>\n'
        '    <path d="M32 33 C35.5 33 38 30.5 39.5 28"/>\n'
        '    <path d="M32 28 C30 28 28.5 26.5 27.5 25"/>\n'
        '    <path d="M32 28 C34 28 35.5 26.5 36.5 25"/>\n'
        '  </g>\n'
        '  <circle cx="32" cy="22" r="1.7" fill="var(--icon-cut)"/>\n'
        '  <path d="M23 52 H41" fill="none" stroke="var(--icon-ink)" '
        'stroke-width="var(--icon-stroke)" stroke-linecap="round"/>\n'
        '  <!-- one controlled break: the only warm dot in the whole system -->\n'
        '  <circle cx="46.5" cy="17" r="2.2" fill="var(--accent-ha)"/>\n'
    )


# Companion glyphs: same tile, same spine, same stroke; shape alone carries meaning.
GLYPHS = {
    "level-1": (
        '  <!-- L1: trunk only, zero branches -->\n'
        + LINE_OPEN
        + '    <path d="M32 43 V25"/>\n'
        + '    <circle cx="32" cy="20.5" r="2.8"/>\n'
        + '  </g>\n'
        + SPINE
    ),
    "level-2": (
        '  <!-- L2: two short branch pairs + four square knowledge points -->\n'
        + LINE_OPEN
        + '    <path d="M32 43 V25"/>\n'
        + '    <path d="M32 36 H25 M32 36 H39 M32 30 H27 M32 30 H37"/>\n'
        + '    <circle cx="32" cy="21" r="2.2"/>\n'
        + '  </g>\n'
        + '  <g fill="var(--icon-ink)">\n'
        + '    <rect x="23.6" y="34.6" width="2.8" height="2.8" rx="0.5"/>\n'
        + '    <rect x="37.6" y="34.6" width="2.8" height="2.8" rx="0.5"/>\n'
        + '    <rect x="25.6" y="28.6" width="2.8" height="2.8" rx="0.5"/>\n'
        + '    <rect x="35.6" y="28.6" width="2.8" height="2.8" rx="0.5"/>\n'
        + '  </g>\n'
        + SPINE
    ),
    "level-3": (
        '  <!-- L3: one long branch pair + two story cards -->\n'
        + LINE_OPEN
        + '    <path d="M32 43 V25"/>\n'
        + '    <path d="M32 36 C26 36 23 33 22 30"/>\n'
        + '    <path d="M32 36 C38 36 41 33 42 30"/>\n'
        + '    <rect x="16.5" y="20" width="11" height="8" rx="2"/>\n'
        + '    <rect x="36.5" y="20" width="11" height="8" rx="2"/>\n'
        + '  </g>\n'
        + SPINE
    ),
    "level-4": (
        '  <!-- L4: three trunks + one dashed cross-reference line -->\n'
        + LINE_OPEN
        + '    <path d="M23 43 V25 M32 43 V21 M41 43 V25"/>\n'
        + '    <path d="M20 33 H44" stroke-dasharray="2 3"/>\n'
        + '  </g>\n'
        + '  <g fill="var(--icon-ink)">\n'
        + '    <circle cx="23" cy="22" r="1.6"/>\n'
        + '    <circle cx="32" cy="18" r="1.6"/>\n'
        + '    <circle cx="41" cy="22" r="1.6"/>\n'
        + '  </g>\n'
        + SPINE
    ),
    "study-plan": (
        '  <!-- spaced review: three decreasing intervals + a cycle start -->\n'
        + LINE_OPEN
        + '    <path d="M21 25 H43 M21 33 H37 M21 41 H31"/>\n'
        + '    <circle cx="43" cy="19" r="2.2"/>\n'
        + '  </g>\n'
        + SPINE
    ),
    "export": (
        '  <!-- authorised export: knowledge box + outward arrow -->\n'
        + LINE_OPEN
        + '    <rect x="17" y="22" width="20" height="20" rx="5"/>\n'
        + '    <path d="M28 32 H46 M42 28 L46 32 L42 36"/>\n'
        + '  </g>\n'
        + SPINE
    ),
}

SPRITE_IDS = {
    "level-1": "ember-reader-l1",
    "level-2": "ember-reader-l2",
    "level-3": "ember-reader-l3",
    "level-4": "ember-reader-l4",
    "study-plan": "ember-reader-study",
    "export": "ember-reader-export",
}

CAPTIONS = {
    "level-1": ("L1", "zero branches: the trunk alone"),
    "level-2": ("L2", "two branch pairs with four square knowledge points"),
    "level-3": ("L3", "one long branch pair carrying two story cards"),
    "level-4": ("L4", "three trunks cross-referenced by a dashed line"),
    "study-plan": ("review", "three decreasing intervals and a cycle start"),
    "export": ("export", "a knowledge box with an outward arrow"),
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    minidom.parseString(text.encode("utf-8"))
    assert "<text" not in text, "visible text found in %s" % path.name
    print("  ok  %-22s %5d bytes" % (str(path.relative_to(ROOT)), len(text.encode("utf-8"))))


def build():
    light = PALETTES["light"]

    # 1. Three adaptive versions of the master icon - identical paths, tokens only.
    master_titles = {
        "icon.svg": ("light", "Ember Reader", "warm-white tile, indigo book, one vermilion dot"),
        "icon-dark.svg": ("dark", "Ember Reader (dark)", "ink tile, light indigo book, one vermilion dot"),
        "icon-mono.svg": ("mono", "Ember Reader (mono)", "warm-white tile, pure ink book, zero breaks"),
    }
    for name, (key, title, desc) in master_titles.items():
        p = PALETTES[key]
        body = head(64, 64, 34, p, title, desc) + CONTAINER + main_graph() + "</svg>\n"
        write(ASSETS / name, body)

    # 2. The six companion icons.
    for name, glyph in GLYPHS.items():
        label, caption = CAPTIONS[name]
        title = "Ember Reader - %s" % label
        desc = "Warm-white squircle, indigo line drawing, %s; no visible text." % caption
        body = head(64, 64, 34, light, title, desc) + CONTAINER + glyph + "</svg>\n"
        write(ICONS / (name + ".svg"), body)

    # 3. Merged sprite (defs only, inline before use).
    sprite = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" '
        'width="0" height="0" aria-hidden="true" style="position:absolute;%s">\n'
        '  <defs>\n'
    ) % token_style(light)
    for name, sid in SPRITE_IDS.items():
        sprite += '    <symbol id="%s" viewBox="0 0 64 64">\n' % sid
        sprite += CONTAINER + GLYPHS[name]
        sprite += '    </symbol>\n'
    sprite += '  </defs>\n</svg>\n'
    write(ICONS / "sprite.svg", sprite)

    # 4. Dark display card: the exact visual rhythm of the reference, zero text.
    card = (
        head(176, 176, 176, light, "Ember Reader - icon card",
             "A dark rounded card holding one warm-white squircle icon. No visible text.")
        + '  <rect x="0" y="0" width="176" height="176" rx="28" fill="var(--icon-card)"/>\n'
        + '  <rect x="1" y="1" width="174" height="174" rx="27" fill="none" '
          'stroke="rgba(255,255,255,0.06)" stroke-width="1"/>\n'
        + '  <g transform="translate(28,28) scale(1.875)">\n'
        + CONTAINER + main_graph()
        + '  </g>\n</svg>\n'
    )
    write(ASSETS / "icon-card.svg", card)


if __name__ == "__main__":
    build()
    print("all 12 SVG assets written and XML-valid; zero <text> nodes.")
