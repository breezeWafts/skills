# -*- coding: utf-8 -*-
"""用 PIL 4x 超采样精确绘制图标 v2，输出透明四角 PNG（512 / 128）。"""
import math
import os
import random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, 'build', 'ember-art-solution__skillhub', 'assets', 'icons')
TMP = os.path.join(ROOT, 'build', '_icon_v2')
S = 4                      # 超采样倍率
W = 512
CX = CY = 256

# ---- Token: assets/tokens.css ----
PAPER = (250, 248, 243)   # --color-bg-base 宣纸白
INK = (28, 28, 28)        # --color-text-primary 焦墨
INDIGO = (46, 74, 107)    # --color-accent 靛青
CINNABAR = (176, 58, 46)  # --accent-ha 朱砂（唯一破格）


def mix(fg, bg, a):
    """把 alpha 前景预混到宣纸白底，避免 RGBA 逐层覆盖失真。"""
    return tuple(int(round(fg[i] * a + bg[i] * (1 - a))) for i in range(3))


def sc(v):
    return int(round(v * S))


def pt(r, deg):
    a = math.radians(deg)
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def arc_points(r, a0, a1, step=1.0):
    d = a0
    out = []
    while d < a1:
        out.append(pt(r, d))
        d += step
    out.append(pt(r, a1))
    return [(sc(x), sc(y)) for x, y in out]


def draw_arc(draw, r, a0, a1, w, color):
    pts = arc_points(r, a0, a1)
    draw.line(pts, fill=color, width=sc(w), joint='curve')
    rad = sc(w) / 2
    for x, y in (pts[0], pts[-1]):          # 圆头端点＝「微」
        draw.ellipse([x - rad, y - rad, x + rad, y + rad], fill=color)


# 整幅先铺宣纸白：圆角外的 RGB 也是纸色，最后靠 alpha 遮罩裁形，
# 这样 LANCZOS 缩放时边缘只插值 alpha、不会渗出暗边或纸纹杂点。
img = Image.new('RGBA', (W * S, W * S), PAPER + (255,))
d = ImageDraw.Draw(img)

# 1. 圆角卡片
d.rounded_rectangle([sc(24), sc(24), sc(488), sc(488)],
                    radius=sc(104), fill=PAPER + (255,))

# 2. 纸纹 3%（--noise-opacity），按 6px 网格复刻 SVG pattern
random.seed(20261123)
grain = [mix(INK, PAPER, a) + (255,) for a in (0.030, 0.026, 0.028)]
for gx in range(24, 488, 6):
    for gy in range(24, 488, 6):
        for (ox, oy, rr), col in zip([(1, 1, 0.6), (4, 3, 0.5), (2.5, 5, 0.45)], grain):
            x, y, r = sc(gx + ox), sc(gy + oy), sc(rr)
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)

# 3. 三层柔和气韵：向外递减＝「假」的消逝 / 「气」的三层
for r, a in [(168, 0.075), (140, 0.05), (196, 0.032)]:
    c = mix(INDIGO, PAPER, a) + (255,)
    d.ellipse([sc(CX - r), sc(CY - r), sc(CX + r), sc(CY + r)],
              outline=c, width=sc(1.5))

# 4. 三段内弧（气口与外弧错位 30°）
ci = mix(INDIGO, PAPER, 0.24) + (255,)
for s, e in [(-33, 63), (87, 183), (207, 303)]:
    draw_arc(d, 78, s, e, 2.4, ci)

# 5. 三段外弧：三大体系各据一方、共同让出中心的「间」
co = mix(INDIGO, PAPER, 0.92) + (255,)
for s, e in [(-3, 93), (117, 213), (237, 333)]:
    draw_arc(d, 104, s, e, 9, co)

# 6. 唯一破格 / 唯一焦点：朱砂一点，落在卡片黄金分割交点 (310.75, 201.25)
d.ellipse([sc(311.15 - 9), sc(200.85 - 9), sc(311.15 + 9), sc(200.85 + 9)],
          fill=CINNABAR + (255,))

# 7. 内缘极淡描边，避免「边缘硬切」
d.rounded_rectangle([sc(24.5), sc(24.5), sc(487.5), sc(487.5)],
                    radius=sc(103.5),
                    outline=mix(INDIGO, PAPER, 0.05) + (255,), width=sc(1))

# 8. 圆角 alpha 遮罩：抹去圆角外溢出的纸纹，保留平滑抗锯齿边缘
mask = Image.new('L', (W * S, W * S), 0)
ImageDraw.Draw(mask).rounded_rectangle(
    [sc(24), sc(24), sc(488), sc(488)], radius=sc(104), fill=255)
img.putalpha(mask)

img512 = img.resize((W, W), Image.LANCZOS)
out512 = os.path.join(ASSETS, 'ember-art-solution-icon-v2.png')
img512.save(out512, optimize=True)

img128 = img.resize((128, 128), Image.LANCZOS)
out128 = os.path.join(TMP, 'preview-128.png')
img128.save(out128, optimize=True)

print('PNG512 ->', out512, os.path.getsize(out512), 'bytes',
      '| corner alpha', img512.getpixel((0, 0))[3],
      '| card', img512.getpixel((256, 40))[:3])
print('PNG128 ->', out128, os.path.getsize(out128), 'bytes')
