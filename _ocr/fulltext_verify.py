# -*- coding: utf-8 -*-
"""Verify digest claims against the full-text TXT conversions."""
import os, re, glob, json, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(ROOT))
THEORY = os.path.join(PROJ, '理论')
OUT = os.path.join(ROOT, 'fulltext_evidence.md')

# recover mojibake copy of 美的历程 (raw UTF-8 bytes had been decoded as latin1)
mi_src = os.path.join(ROOT, 'text2', 'b11.txt')
mi_dst = os.path.join(ROOT, 'text2', 'b11_fixed.txt')
books = []
for f in sorted(glob.glob(os.path.join(THEORY, '*.txt'))):
    t = open(f, 'rb').read().decode('utf-8-sig', errors='replace')
    books.append((os.path.basename(f)[:-4], t))
if os.path.exists(mi_src) and not os.path.exists(mi_dst):
    raw = open(mi_src, 'rb').read().decode('utf-8', errors='replace')
    try:
        fixed = raw.encode('latin1', errors='replace').decode('utf-8', errors='replace')
    except Exception:
        fixed = raw
    open(mi_dst, 'w', encoding='utf-8').write(fixed)
if os.path.exists(mi_dst):
    t = open(mi_dst, encoding='utf-8').read()
    if sum(1 for c in t if '\u4e00' <= c <= '\u9fff') > 50000:
        books.append(('美的历程（全文修复）', t))
        print('美的历程 recovered, chars=', len(t))

CLAIMS = """儒道互补 礼乐传统 积淀 有意味的形式 悦耳悦目 悦心悦意 悦志悦神 天人合一
人的自然化 自然的人化 情理 文质 狞厉的美 人的觉醒 魏晋风度 盛唐之音 无我之境 有我之境
三远 散点透视 可游可居 借景 框景 障景 掇山 理水 移天缩地 写意 枯山水 作庭 不对称 脱俗 寂静 枯高 幽玄 物哀 侘寂 余白 一期一会 无常
微 并 气 间 秘 素 假 破 八意识 一即多 不立文字 直指人心 非逻辑 直觉 公案 无分别 简素 阴翳
理念的感性显现 艺术美 自然美 象征型 古典型 浪漫型 崇高 情致 典型 理想 艺术解体 物质性
色相 明度 纯度 彩度 色调 对比 调和 九大调 孟塞尔 奥斯特瓦德 补色 面积对比 冷暖 前进色 后退色 膨胀色 收缩色 识别性 诱目性 视认性 同化 演色性 色彩心理 色彩力
线条 视线引导 空间感 节奏感 运动感 丰富感 疏密 形式美
诗经 楚辞 汉乐府 陶渊明 王维 李白 苏轼 宋词 红楼梦 漫长的准备期 孤独 温柔
极简 素材 时间 死亡 生命 秩序 偶然 余韵 静默 无我 修行 茶道 俳句 水墨 书法
养眼 养心 养神 高峰体验 审美疲劳""".split()

global_hits = collections.Counter()
sections = []
for name, t in books:
    hits = collections.Counter({c: t.count(c) for c in CLAIMS if t.count(c) > 0})
    global_hits.update(hits)
    # chapter-like headings
    heads = []
    for m in re.finditer(r'第[一二三四五六七八九十百零0-9]+[章节讲部篇][^\n]{0,32}', t):
        h = m.group(0).strip()
        if h not in heads: heads.append(h)
    # contexts for high-value claims
    KEY = ['儒道互补', '积淀', '有意味的形式', '悦耳悦目', '悦志悦神', '无我之境', '三远',
           '可游可居', '不对称', '幽玄', '物哀', '侘寂', '理念的感性显现', '象征型',
           '古典型', '浪漫型', '九大调', '膨胀色', '收缩色', '一即多', '不立文字',
           '间', '秘', '素', '假', '破', '作庭', '漫长的准备期', '借景', '框景']
    ctx = []
    for k in KEY:
        if hits.get(k, 0) == 0: continue
        m = re.search(re.escape(k), t)
        if not m: continue
        s = max(0, m.start() - 55); e = min(len(t), m.end() + 75)
        frag = ' '.join(t[s:e].split())
        if len(frag) > 20:
            ctx.append('[%s] …%s…' % (k, frag))
    sections.append(
        '## %s\n\n- 全文字数 %d｜命中命题 %d 项｜前 20：%s\n\n### 章节结构（前 12）\n%s\n\n### 关键命题原文片段\n%s\n'
        % (name, len(t), len(hits),
           '、'.join('%s(%d)' % (k, v) for k, v in hits.most_common(20)) or '无',
           '\n'.join('- ' + h for h in heads[:12]) or '- （无规范章节标题）',
           '\n'.join('- ' + c for c in ctx[:14]) or '- （无）'))

head = ('# 全文 TXT 佐证表（自动生成）\n\n'
        '- 来源：`理论/*.txt` 21 册全文转换 ＋《美的历程》乱码修复全文，共 %d 册。\n'
        '- 用途：核对 core-05-theory-digest.md 的命题是否有原书全文支撑，据此把〔网络〕标注升级为〔全文〕。\n\n'
        '## 全局命题频次（前 80）\n\n%s\n\n---\n\n'
        % (len(books), '、'.join('%s(%d)' % (k, v) for k, v in global_hits.most_common(80))))
open(OUT, 'w', encoding='utf-8').write(head + '\n---\n\n'.join(sections))
print('books', len(books), 'written', OUT, os.path.getsize(OUT), 'bytes')
