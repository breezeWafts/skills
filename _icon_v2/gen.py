# -*- coding: utf-8 -*-
"""按 evan-design 规范生成 ember-art-solution 图标 v2（SVG + 渲染用 HTML）。"""
import base64
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_SVG = os.path.join(ROOT, 'build', 'ember-art-solution__skillhub',
                       'assets', 'icons', 'ember-art-solution-icon-v2.svg')
OUT_HTML = os.path.join(ROOT, 'build', '_icon_v2', 'render.html')

# ---- Token（全部取自 assets/tokens.css，零自造色值）----
PAPER = '#FAF8F3'   # --color-bg-base 宣纸白
INK = '#1C1C1C'     # --color-text-primary 焦墨（仅用于 3% 纸纹）
INDIGO = '#2E4A6B'  # --color-accent 靛青
CINNABAR = '#B03A2E'  # --accent-ha / --color-danger 朱砂，唯一破格色

CX = CY = 256


def pt(r, deg):
    a = math.radians(deg)
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def arc(r, a0, a1, w, op):
    x0, y0 = pt(r, a0)
    x1, y1 = pt(r, a1)
    return (f'    <path d="M {x0:.2f} {y0:.2f} A {r} {r} 0 0 1 {x1:.2f} {y1:.2f}" '
            f'fill="none" stroke="{INDIGO}" stroke-width="{w}" '
            f'stroke-opacity="{op}" stroke-linecap="round"/>')


# 三段外弧：三大体系各据一方、互不叠压，共同让出中心
outer = '\n'.join(arc(104, s, e, 9, 0.92)
                  for s, e in [(-3, 93), (117, 213), (237, 333)])
# 三段内弧：与外弧错开 30°，气口错位＝「气」的流动；交付物多样而不罗列
inner = '\n'.join(arc(78, s, e, 2.4, 0.24)
                  for s, e in [(-33, 63), (87, 183), (207, 303)])
# 三层柔淡气韵：单色图标中「气 ≥3 层柔和」的转译，向外递减＝「假」的消逝
qi = '\n'.join(
    f'    <circle cx="{CX}" cy="{CY}" r="{r}" fill="none" '
    f'stroke="{INDIGO}" stroke-width="1.5" stroke-opacity="{op}"/>'
    for r, op in [(168, 0.075), (140, 0.05), (196, 0.032)]
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <pattern id="paperGrain" width="6" height="6" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.6" fill="{INK}" opacity="0.030"/>
      <circle cx="4" cy="3" r="0.5" fill="{INK}" opacity="0.026"/>
      <circle cx="2.5" cy="5" r="0.45" fill="{INK}" opacity="0.028"/>
    </pattern>
    <clipPath id="card"><rect x="24" y="24" width="464" height="464" rx="104"/></clipPath>
  </defs>
  <!-- ember-art-solution icon v2 · evan-design 规范版
       三弧不闭合＝东方/西方/阿拉伯-伊斯兰三体系，各据一方而不叠压；
       中心不落一笔＝「间」，万象自此虚处生；
       内弧气口错位＝气韵流动与多场景交付（「秘」，不逐一罗列符号）；
       一点朱砂落于卡片黄金分割交点＝唯一焦点、唯一破格（accent-ha 变量）。 -->
  <rect x="24" y="24" width="464" height="464" rx="104" fill="{PAPER}"/>
  <g clip-path="url(#card)">
    <rect x="24" y="24" width="464" height="464" fill="url(#paperGrain)"/>
{qi}
{inner}
{outer}
    <circle cx="311.15" cy="200.85" r="9" fill="{CINNABAR}"/>
    <rect x="24.5" y="24.5" width="463" height="463" rx="103.5"
          fill="none" stroke="{INDIGO}" stroke-width="1" stroke-opacity="0.05"/>
  </g>
</svg>
'''

os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
with open(OUT_SVG, 'w', encoding='utf-8') as f:
    f.write(svg)

b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii')
html = (
    '<!doctype html><html><head><meta charset="utf-8"><style>'
    'html,body{margin:0;padding:0;width:512px;height:512px;overflow:hidden;'
    'background:transparent}'
    'img{display:block;width:512px;height:512px}'
    '</style></head><body>'
    f'<img src="data:image/svg+xml;base64,{b64}">'
    '</body></html>'
)
with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print('SVG  ->', OUT_SVG, os.path.getsize(OUT_SVG), 'bytes')
print('HTML ->', OUT_HTML, os.path.getsize(OUT_HTML), 'bytes')
