# -*- coding: utf-8 -*-
"""Clean & condense OCR / text-layer output into per-book evidence sheets."""
import os, re, glob, json, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
OCR = os.path.join(ROOT, 'ocr2')
TXT = os.path.join(ROOT, 'text2')
OUT = os.path.join(ROOT, 'condensed.md')

TERMS = """意境 气韵 气韵生动 留白 余白 虚实 阴阳 天人合一 儒道互补 积淀
有意味的形式 无我之境 有我之境 三远 散点透视 借景 框景 障景 对景 漏景
可游可居 山水 园林 造园 枯山水 作庭 侘寂 物哀 幽玄 阴翳 微 并 气 间 秘 素 假 破
一期一会 无常 不对称 简素 空 无 禅 禅宗 直觉 不立文字 无分别 一即多 本来面目
理念的感性显现 象征型 古典型 浪漫型 情致 理想 崇高 悲剧 艺术美 自然美 理念
色相 明度 纯度 彩度 对比 调和 色调 冷暖 前进色 后退色 膨胀色 收缩色 面积对比
孟塞尔 色立体 补色 识别性 诱目性 视认性 演色性 同化效果 色彩心理 色彩力
节奏感 运动感 丰富感 线条 视线引导 空间感 疏密 动势 构图 形式美
文学 诗经 楚辞 唐诗 宋词 陶渊明 王维 李白 苏轼 孤独 温柔 情动于中
极简 素材 材质 自然 时间 死亡 生命 秩序 偶然 余韵 静默 无我 修行
茶道 俳句 水墨 书法 文人 风骨 魏晋风度 盛唐 狞厉之美 礼乐 仁学 深情
新感性 悦耳悦目 悦心悦意 悦志悦神 美感 审美 美学 形式 内容 象征 通感
""".split()

def clean(t):
    t = t.replace('\u3000', ' ')
    # remove spaces between CJK chars (Windows OCR inserts them)
    for _ in range(3):
        t = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', t)
    t = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[，。、；：！？）」』])', '', t)
    t = re.sub(r'(?<=[（「『])\s+(?=[\u4e00-\u9fff])', '', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()

def load_book(bid, has_text):
    chunks = []
    # full text layer first (highest quality), capped
    fp = os.path.join(TXT, bid + '.txt')
    if has_text and os.path.exists(fp):
        chunks.append(clean(open(fp, encoding='utf-8').read()))
    for p in sorted(glob.glob(os.path.join(OCR, bid + '_p*.txt'))):
        chunks.append(clean(open(p, encoding='utf-8').read()))
    for p in sorted(glob.glob(os.path.join(TXT, bid + '_p*.txt'))):
        chunks.append(clean(open(p, encoding='utf-8').read()))
    return '\n'.join(chunks)

def headings(text):
    lines = []
    for raw in text.splitlines():
        l = raw.strip()
        if not (4 <= len(l) <= 46):
            continue
        if re.search(r'(第[一二三四五六七八九十百0-9]+[章节讲部篇]|CONTENTS|目\s*录|序章|绪论|前言|后记|附录)', l):
            lines.append(l)
        elif re.search(r'^[一二三四五六七八九十]+[、．.]', l) and re.search(r'[\u4e00-\u9fff]{3,}', l):
            lines.append(l)
        elif re.search(r'[\u4e00-\u9fff].*[／/]\s*\d+\s*$', l):
            lines.append(l)
    # dedupe, keep order
    seen = set(); out = []
    for l in lines:
        k = re.sub(r'\s+', '', l)[:30]
        if k in seen: continue
        seen.add(k); out.append(l)
    return out[:28]

def sentences(text):
    parts = re.split(r'[。！？\n；]', text)
    good = []
    for s in parts:
        s = s.strip(' ，,、：:（）()「」『』“”"')
        if not (18 <= len(s) <= 95): continue
        if len(re.findall(r'[\u4e00-\u9fff]', s)) < 12: continue
        if sum(s.count(t) for t in TERMS) < 1: continue
        if re.search(r'(ISBN|出版社|版权|著者|图书在版|www\.|http|@)', s): continue
        good.append(s)
    seen = set(); out = []
    for s in good:
        k = s[:16]
        if k in seen: continue
        seen.add(k); out.append(s)
    return out[:14]

manifest = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
sections = []
global_hits = collections.Counter()
for m in manifest:
    text = load_book(m['id'], m['has_text'])
    hits = collections.Counter({t: text.count(t) for t in TERMS if text.count(t) > 0})
    global_hits.update(hits)
    hs = headings(text)
    ss = sentences(text)
    src = '文本层全文' if m['has_text'] else '扫描页OCR'
    sections.append(
        '## %s %s\n\n- 文件：`%s`｜%d 页｜主来源：%s｜采样 %d 页\n'
        '- 命中术语（前 18）：%s\n\n### 目录 / 章节线索\n%s\n\n### 正文可归纳片段\n%s\n'
        % (m['id'], m['name'], m['file'], m['pages'], src, len(m['sampled']),
           '、'.join('%s(%d)' % (k, v) for k, v in hits.most_common(18)) or '无',
           '\n'.join('- ' + h for h in hs) or '- （未识别到清晰目录行）',
           '\n'.join('- ' + s for s in ss) or '- （未提取到可用长句）'))

head = ('# 理论 PDF 内容浓缩证据表（自动生成，仅供归纳）\n\n'
        '- 来源：工作区 `理论/` 下 22 个 PDF（原 23 册含 1 个重复副本）。\n'
        '- 方法：PyMuPDF 渲染扫描页 → Windows OCR（zh-Hans-CN）识别；有文本层的书直接导出全文。\n'
        '- 清洗：去除 OCR 在汉字间插入的空格、版权页与噪声。\n'
        '- 用途：据此合并相似论述、提炼可执行结论；**原文引用须回原书核对**。\n\n'
        '## 全局术语频次（前 60）\n\n%s\n\n---\n\n'
        % '、'.join('%s(%d)' % (k, v) for k, v in global_hits.most_common(60)))

open(OUT, 'w', encoding='utf-8').write(head + '\n---\n\n'.join(sections))
print('written', OUT, os.path.getsize(OUT), 'bytes')
print('books', len(sections))
