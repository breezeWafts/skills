# -*- coding: utf-8 -*-
"""Sync the full-text-verified digest into all 5 skill packages, bump versions, repack."""
import os, re, json, glob, shutil, zipfile, sys

BUILD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # build/
PROJ = os.path.dirname(BUILD)
MAIN = os.path.join(BUILD, 'ember-art-solution__skillhub')
SUBS = ['ember-writer__skillhub', 'ember-storyboard-build__skillhub',
        'ember-photography-posing__skillhub', 'evan-design__skillhub']
DIST = os.path.join(PROJ, 'dist')
os.makedirs(DIST, exist_ok=True)

MAIN_V, SUB_V = '1.1.0', '2.1.0'


def edit(path, pairs, label):
    t = open(path, encoding='utf-8').read()
    for old, new in pairs:
        n = t.count(old)
        if n != 1:
            raise RuntimeError('%s: expect exactly 1 occurrence, got %d for: %s'
                               % (label, n, old[:70]))
        t = t.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(t)
    print('  edited', label, len(t), 'chars')


def append(path, text, label):
    t = open(path, encoding='utf-8').read().rstrip()
    open(path, 'w', encoding='utf-8').write(t + '\n\n' + text.strip() + '\n')
    print('  appended', label)


def set_meta(d, v):
    for fn in ['_meta.json', '_skillhub_meta.json']:
        p = os.path.join(d, fn)
        o = json.load(open(p, encoding='utf-8'))
        o['version'] = v
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(o, f, ensure_ascii=False, indent=2)
    print('  meta ->', v)


# ---------------------------------------------------------------- main package
print('=== MAIN', os.path.basename(MAIN), '===')
edit(os.path.join(MAIN, 'SKILL.md'), [
    ('version: 1.0.0', 'version: 1.1.0'),
    ('并已回融本总纲（v2.0.0）', '并已回融本总纲（v%s）' % SUB_V),
    ('- 理论电子书原件（《美的历程》《日本的八个审美意识》、铃木大拙系列等 23 册）与三套色表原件在工作区素材目录，**不在 skill 包内**；可执行结论已提炼进 `core-*`，索引见 `core-05`。',
     '- 理论原典共 22 册：工作区 `理论/` 已转换为 **21 册全文 TXT**，《美的历程》以课程整理材料与联网资料间接覆盖；原 PDF／全文 TXT 与三套色表原件**不随包分发**。合并去重后的精炼结论见 `core-05-theory-digest.md`，书目与回溯路径见 `core-05-theory-index.md`。'),
    ('| `core-05-theory-index.md` | 23 册理论电子书＋应用场景资料总目、按需求回溯索引 | 需要论证/理论依据时 |',
     '| `core-05-theory-index.md` | 22 册理论原典（21 册全文 TXT）＋应用场景资料总目、按需求回溯索引 | 需要论证/理论依据时 |\n'
     '| `core-05-theory-digest.md` | **全文核实的精炼结论库**：22 册合并为 T1–T9 九族、可执行转译参数、来源标注与引用规范 | **P2 / P5 建议读** |'),
], 'main SKILL.md')

append(os.path.join(MAIN, 'SKILL.md'), '''
## [1.1.0] 增量 · 2026-11-23

理论 PDF 已全部转换为全文 TXT。本版据此把「采样 OCR ＋ 网络补全」升级为**全文核实版知识库**：

- 新增 `core-05-theory-digest.md`：22 册原典合并为 T1–T9 九个主题族，逐族给出核心命题、可执行转译参数、误用警示与来源标注；〔全文〕／〔间接〕／〔整理〕／〔网络〕四级可信度。
- 更新 `core-05-theory-index.md`：修正 23 册重复副本口径，登记 21 册全文 TXT，说明《美的历程》该册无同名 TXT、由课程整理与联网资料间接覆盖。
- 主入口 SKILL.md 增补 digest 引用与知识库分层说明；其余 11 份 core、3 份 scene、四套领域库、模板、图标与调用方式**均不变**。
''', 'main SKILL.md changelog tail')

append(os.path.join(MAIN, 'CHANGELOG.md'), '''
---

## [1.1.0] — 2026-11-23

**升级原因：用户已把理论 PDF 全部转换为全文 TXT，用全文核实并精炼后纳入知识库。**

### 提取与核实
- 工作区 `理论/` 得到 **21 册同名全文 TXT**（UTF-8，约 9 MB）；逐册全文检索核对命题，原书原文可支撑者标注〔全文〕。
- 前一轮 243 页扫描采样 OCR（Windows zh-Hans-CN，243/243 成功）与 10 册文本层导出降为交叉校验。
- **《美的历程》无同名 TXT**，原 PDF 已移除、旧文本层为乱码；改由扫描采样 OCR、工作区 `美的历程-美学导论-完整整理.html`（18 讲课程整理，非原书）与联网补全覆盖，标注〔间接〕，引用须回原书核对。
- 按书名联网补全的 9 组资料，绝大多数已被全文 TXT 核实升级为〔全文〕，仅第 3 卷门类论与《美的历程》时代谱保留〔网络〕／〔间接〕。

### 新增
- `references/core-05-theory-digest.md`：**22 册 → 9 主题族**的合并去重结论库。含合并映射表、T1–T9 精炼命题与可执行转译表、体系裁决速查、风格取用速查、来源标注与引用规范。
- 新增可核对的原文级结论：三层积淀（原始／艺术／生活）、有意味的形式原书界定、悦耳悦目→悦心悦意→悦志悦神、有我／无我之境、禅庭七美原文（不均齐／简素／枯槁／自然／幽玄／脱俗／静寂）、三远与《作庭记》、以小营造大、八意识原书目录（隐秘是花／秘与间或留白／守破离）、禅宗四圣句、明度九大调色阶、东西心理直觉／逻辑对照。

### 修改
- `core-05-theory-index.md`：修正书目计数与"原件不在包内"表述。
- `SKILL.md`：frontmatter 1.0.0 → **1.1.0**；L1 资源表新增 digest 行；§资源边界段改写；子 skill 回融版本引用 v2.0.0 → v2.1.0。
- `_meta.json` / `_skillhub_meta.json` → 1.1.0。

### 未改动
组织架构（`core-00`）、风格路由、交付矩阵、色彩体系、画面六法、审美形态、创作方法、八意识、情绪感官、质量门禁、三个扩展场景、四套领域库、5 个模板与图标均保持不变。
''', 'main CHANGELOG')
set_meta(MAIN, MAIN_V)

# ---------------------------------------------------------------- index update
idx = os.path.join(MAIN, 'references', 'core-05-theory-index.md')
edit(idx, [
    ('> **诚实标注**：PDF 原件不在 skill 包内（体积过大且多为扫描/嵌字版），本索引提供的是**主题级定位 + 已提炼的可执行结论**；引用具体页码须用户自行核对原书。',
     '> **诚实标注**：理论 PDF 已由用户转换为 **21 册全文 TXT**（工作区 `理论/`），但全文与扫描件体积过大，**不随 skill 包分发**；包内提供的是主题级定位（`core-05-theory-index.md`）＋**全文核实的精炼结论**（`core-05-theory-digest.md`）。引用具体页码、原句仍须回原书／全文 TXT 核对。'),
    ('## 一、理论电子书总目（23 册，按主题分组）',
     '## 一、理论原典总目（22 册；21 册已有全文 TXT，按主题分组）'),
    ('| 《美的历程》李泽厚 |', '| 《美的历程》李泽厚〔无同名 TXT，见下方说明〕 |'),
], 'main core-05 index')
append(idx, '''
---

## 五、全文 TXT 与精炼结论库（1.1.0 新增）

| 材料 | 位置 | 用途 |
|---|---|---|
| 21 册全文 TXT | 工作区 `理论/*.txt`（UTF-8，约 9 MB） | 命题核实、目录与章节回溯、原文检索；**不随包分发** |
| 《美的历程》 | 工作区 `美的历程-美学导论-完整整理.html`（18 讲课程整理，非原书）＋ `美学资料要点总结.md` | 该册无同名 TXT；以〔间接〕来源覆盖时代气质谱与核心观点，引用须回原书核对 |
| `core-05-theory-digest.md` | 本包 `references/` | **结论侧**：22 册合并为 T1–T9 九族，逐族给出可执行转译参数、误用警示、四级来源标注（〔全文〕/〔间接〕/〔整理〕/〔网络〕） |
| 课程整理材料 | 工作区 `美学原理30讲-详细归纳文案.html`、`美学资料要点总结.md` | 接受侧补充：审美疲劳与「度」、高峰体验、养眼→养心→养神、移情说／直觉说／心理距离／格式塔 |

> **本节要点**：上一版依赖「243 页扫描采样 OCR ＋ 按书名联网补全」；本版以全文 TXT 为主依据，扫描 OCR 与联网资料降为交叉校验。日常生成直接读 digest 的 T9 速查表，需要论证时按本索引回溯书目。
''', 'main core-05 index tail')

# ---------------------------------------------------------------- sub packages
digest_src = os.path.join(MAIN, 'references', 'core-05-theory-digest.md')
for pkg in SUBS:
    d = os.path.join(BUILD, pkg)
    art = os.path.join(d, 'references', 'art-solution')
    print('=== SUB', pkg, '===')
    shutil.copy2(digest_src, os.path.join(art, 'core-05-theory-digest.md'))
    shutil.copy2(idx, os.path.join(art, 'core-05-theory-index.md'))
    print('  synced digest + index')

    edit(os.path.join(d, 'SKILL.md'), [
        ('version: "2.0.0"', 'version: "%s"' % SUB_V),
        ('artSolution: "ember-art-solution@1.0.0"', 'artSolution: "ember-art-solution@%s"' % MAIN_V),
        ('（美学主导全场景方案总控，v1.0.0）', '（美学主导全场景方案总控，v%s）' % MAIN_V),
        ('## 〇、美学总纲（ember-art-solution 统摄 · v2.0.0）',
         '## 〇、美学总纲（ember-art-solution 统摄 · v%s）' % SUB_V),
        ('| `core-05-theory-index.md` | 23 册理论电子书与应用场景资料索引 |',
         '| `core-05-theory-index.md` | 22 册理论原典与应用场景资料索引（21 册已有全文 TXT） |\n'
         '| `core-05-theory-digest.md` | **全文核实的精炼结论库**：22 册合并为 T1–T9 九族、可执行转译参数与来源标注 |'),
    ], pkg + ' SKILL.md')

    append(os.path.join(d, 'SKILL.md'), '''
### %s 增量（2026-11-23）

同步总纲 v%s：新增 `references/art-solution/core-05-theory-digest.md`（22 册原典全文 TXT 核实后的九族精炼结论库），更新同目录 `core-05-theory-index.md`；§0.5 资源表新增 digest 行，版本引用统一到总纲 v%s。原有领域主干、模板、数值规范与图标不变。
''' % (SUB_V, MAIN_V, MAIN_V), pkg + ' SKILL.md tail')

    edit(os.path.join(art, 'README.md'), [
        ('| 理论 | `core-05-theory-index.md` | 理论电子书与场景资料索引 |',
         '| 理论索引 | `core-05-theory-index.md` | 22 册理论原典与场景资料索引（21 册已有全文 TXT） |\n'
         '| 理论结论 | `core-05-theory-digest.md` | **全文核实的精炼结论库**：22 册合并为 T1–T9 九族与可执行转译参数 |'),
        ('总纲 v1.0.0 · 本 skill v2.0.0 · 2026-11-22',
         '总纲 v%s · 本 skill v%s · 2026-11-23' % (MAIN_V, SUB_V)),
    ], pkg + ' art-solution README')

    append(os.path.join(d, 'CHANGELOG.md'), '''
---

## [%s] — 2026-11-23

**升级原因：回融 `ember-art-solution` v%s 的全文核实版理论结论库。**

- 用户已把理论 PDF 全部转换为 **21 册全文 TXT**；总纲据此把上一版「243 页扫描采样 OCR ＋ 联网补全」升级为全文核实，新增 `core-05-theory-digest.md`（22 册 → T1–T9 九族合并去重、可执行转译、误用警示、〔全文〕/〔间接〕/〔整理〕/〔网络〕四级标注）。
- `references/art-solution/` 同步新增 digest 与更新后的 `core-05-theory-index.md`；README 资源表与版本行同步。
- `SKILL.md`：frontmatter %s，§0 版本引用、总控版本、`artSolution` 指向 `ember-art-solution@%s`；§0.5 资源表新增 digest 行。
- 《美的历程》无同名 TXT，以课程整理材料与联网资料〔间接〕覆盖，引用须回原书核对。
- **原有领域主干、全部 references、模板、Token、色值、对比度实测表与图标保持不变**；总纲只补理论结论层。
''' % (SUB_V, MAIN_V, SUB_V, MAIN_V), pkg + ' CHANGELOG')
    set_meta(d, SUB_V)

# ---------------------------------------------------------------- pack
print('=== PACK ===')
targets = [(MAIN, MAIN_V)] + [(os.path.join(BUILD, p), SUB_V) for p in SUBS]
for d, v in targets:
    root = os.path.basename(d)
    out = os.path.join(DIST, '%s_v%s.zip' % (root, v))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(root + '/', '')
        for base, dirs, files in os.walk(d):
            dirs.sort(); files.sort()
            for fn in files:
                full = os.path.join(base, fn)
                rel = os.path.relpath(full, d)
                z.write(full, root + '/' + '/'.join(rel.split(os.sep)))
    print(' ', os.path.basename(out), os.path.getsize(out), 'bytes')
print('DONE')
