# -*- coding: utf-8 -*-
"""把 knowledge/dist 三份精炼知识库融合进 4 个 skill，并升版重打包。

K 层 = 通用创作规则 + 领域可执行硬参数，横切既有能力栈；
不改动任何既有数值权威、工作流主干与图标。
"""
import json
import os
import re
import shutil
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = 'E:/skills/material/knowledge/dist'
BUILD = os.path.join(ROOT, 'build')
DIST = os.path.join(ROOT, 'dist')

BOOKS = {
    'aesthetics-art.md': '美学艺术类.md',
    'photography.md': '摄影类.md',
    'film-video.md': '影视类.md',
}
PKG_MAIN = 'ember-art-solution__skillhub'
PKG_SUB = ['ember-photography-posing__skillhub',
           'ember-storyboard-build__skillhub',
           'evan-design__skillhub']
PKGS = [PKG_MAIN] + PKG_SUB
MAIN_VER, SUB_VER = '1.2.0', '2.2.0'

# ---------------------------------------------------------------- 融合总纲数据
COMMON_INTRO = (
    '> 本 skill 已融合 `E:\\skills\\material\\knowledge\\dist` 的三份精炼知识库。'
    '它们由 587 册书籍全文、56 个网页教程与联网补充资料提炼而成，'
    '只保留规则、参数、规范与检查清单，不收故事轶事。\n'
    '> **K 层定位**：通用创作规则 + 领域可执行硬参数，横切既有能力栈；'
    '补「怎么落地、怎么验收」，不改「体系归属与审美立意」。\n'
    '> 完整路由、相似信息合并对照与冲突裁决以本文件为准。'
)

CFG = {
PKG_MAIN: dict(
    skill='ember-art-solution', ver=MAIN_VER, domain='全场景总控（A–N）',
    role=[('aesthetics-art.md', '美学艺术类.md', '832 行 / 三篇 19 章', '**总纲通用库**：美学底层逻辑、表现方法、创作标准与自检 30 条', 'P2 P5 P6 P7'),
          ('photography.md', '摄影类.md', '698 行 / 10 章', '**F/G 领域硬参数**：表达、单张流程、布光、构图、摆姿、组图、后期、交付', 'P4 P7 P8'),
          ('film-video.md', '影视类.md', '565 行 / 8 章', '**D/E 领域硬参数**：电影语言、剧本、分镜、调度、剪辑声音、短视频检查表', 'P4 P7 P8')],
    routing=[
        ('P2 美学定位', '美学艺术类 第一篇第一～六章', '价值路径、审美心理、中西范畴的可操作定义，补 core-00 的哲学论证'),
        ('P3 选规格', '美学艺术类 第三篇第十四章', '通用创作流程与任务书最小字段'),
        ('P4 领域执行', '影视类 全八章 / 摄影类 全十章', 'D/E 与 F/G 的现场硬参数、流程与检查表'),
        ('P5 创作深化', '美学艺术类 第二篇第八、十七章', '创意生成机制、从经典提取规则而非抄袭'),
        ('P6 形式落地', '美学艺术类 第二篇第七、九～十三章', '设计、建筑、绘画、配色、字体版式、信息图的可执行规则'),
        ('P7 质量门禁', '美学艺术类 第十五、十六章 + 结尾自检 30 条；影视类 8.9；摄影类 10.7', '各媒介检查清单、评审标准、最终验收'),
        ('P8 交付', '摄影类 第十章；影视类 8.10', '命名、备份、隐私、输出发布与归档'),
    ],
    merge=[
        ('core-00 / core-05', '美学艺术类 第一、四、五、六章', '互补：前者是体系与流派谱系，后者是哲学命题→设计规则的转译', '体系归属以 core-00 为准；转译规则取新库'),
        ('core-03 三套传统色', '美学艺术类 第十一章', '互补：前者给真实色名 HEX，后者给属性／关系／语义／媒介通用规则', '取色以 core-03 为准；配色关系判断取新库'),
        ('core-04 画面六法', '美学艺术类 第十章、摄影类 第五章', '相似：都讲构图与观看', '合并为同一条取更严者；东方留白三法不降级'),
        ('core-07 创作方法论', '美学艺术类 第八、十四、十七章', '相似：都讲创意生成', 'core-07 主「意境与美感机制」，新库主「问题结构与流程」，并联使用'),
        ('core-10 三重门禁', '美学艺术类 第十五、十六章 + 自检 30 条', '相似：都是验收', 'core-10 仍为总门禁，30 条作为通用项追加，不替代三重校验'),
        ('domain/photo/（11）', '摄影类 全十章', '互补：前者审美形态驱动，后者现场参数与交付', '见下方冲突裁决表'),
        ('domain/video/（9）', '影视类 全八章', '同上', '同上'),
        ('domain/ui/（4）', '美学艺术类 第七、十一、十二、十三章', '互补', 'evan-design 数值权威不变'),
        ('scene-11 空间 / scene-13 平面', '美学艺术类 第九、十二、十三章', '互补', '造景八法与缩略图测试优先，新库补比例与栅格论证'),
    ],
    conflict=[
        ('新库的西方形式法则（对称、黄金比例、焦点透视）与东方／伊斯兰体系冲突', '按 core-00 三大体系底层逻辑裁决；刻意反向须写明目的', '底层逻辑优先于符号与单一公式'),
        ('新库数值（摄影参数、影视节奏、配色比例）与 core-* 数值冲突', '领域硬参数以新库为「试拍／试片起点」，审美比例与色板以 core-* 为准；现场实测优先', '新库明确所有数值均为起点'),
        ('组合交付中同一参数在不同领域库不一致', '共享同一张美学定位卡，按 core-02 组合交付规则统一；冲突回 P2 重新定位', '总控唯一'),
        ('新库提到 WCAG 2.2 等现行标准', '作增强建议；J 类交付以 evan-design 的 WCAG 2.1 AA 实测表为底线', '数值权威在 evan-design'),
    ],
    hooks=[
        '**P3 → P4**：按交付 ID 加读对应知识库章节，硬参数写入方案并标注〔知识库·起点〕来源。',
        '**P5 → P6**：用美学艺术类第二篇补形式论证，第三篇第十四章约束流程顺序。',
        '**P7 → P8**：叠加自检 30 条与领域交付检查表，形成最终验收清单。',
    ],
    gate=[
        '每一项硬参数是否标注「试拍／试片起点」属性，而非当成固定规则',
        '通用自检 30 条中与本次交付相关的项是否逐条有结论',
        '组合交付各子件是否共享同一张定位卡、领域库参数是否互相矛盾',
        '摄影／影视类交付是否写明交付规格、命名、备份与隐私保护',
    ]),

'ember-photography-posing__skillhub': dict(
    skill='ember-photography-posing', ver=SUB_VER, domain='静态摄影（F/G）',
    role=[('photography.md', '摄影类.md', '698 行 / 10 章', '**本领域主库**：现场参数、标准流程与交付规范', 'Step 1 / 3–4 / 6–7'),
          ('aesthetics-art.md', '美学艺术类.md', '832 行 / 19 章', '**通用底层**：审美心理、中西范畴、配色与创作自检', 'Step 2 / 5 / 6'),
          ('film-video.md', '影视类.md', '565 行 / 8 章', '跨领域参考：动态影像的场面调度与声画关系；组合交付时转总控', '组合交付')],
    routing=[
        ('Step 1 解析需求', '摄影类 1.1–1.6', '一句话任务定义、意图分类、拍摄简报最小字段'),
        ('Step 2–3 情绪→视觉', '美学艺术类 第一篇第二、五章', '审美心理机制与中国范畴，补 aesthetic-forms 的论证'),
        ('Step 3–4 现场参数', '摄影类 2.1–2.11、3.1–3.8、4.1–4.8、5.1–5.6、6.1–6.9、7.1–7.5', '曝光起点、光位光比、构图、摆姿、情绪引导的硬参数'),
        ('Step 4 套图', '摄影类 8.1–8.5', '组图视觉统一、叙事结构、选片硬标准与排序'),
        ('Step 5 创作深化', '美学艺术类 第八、十七章', '创意机制与灵感提取规则'),
        ('Step 6 双重校验', '摄影类 9.7、10.7；美学艺术类 第十五章 + 自检 30 条', '输出前质检、最终验收、跨媒介自检'),
        ('Step 7 交付', '摄影类 10.1–10.6', '网络／印刷规格、文件命名、3-2-1-1-0 备份、EXIF 隐私'),
    ],
    merge=[
        ('composition-guide.md', '摄影类 第五章', '相似：构图法与边界', '合并取更严者；既有「体系→构图」映射不降级'),
        ('lighting-guide.md', '摄影类 第三、四章', '互补：前者情绪→布光方向，后者光位／光比／附件／自然光硬参数', '方向由前者定、数值由后者给，现场实测优先'),
        ('pose-library.md / expression-guide.md', '摄影类 第六、七章', '相似：摆姿与情绪', '既有审美形态映射为准，新库补身体管理、口令与情绪调度'),
        ('output-template.md', '摄影类 2.11 / 第十章', '互补', '模板字段不变，新增交付规格／命名／备份／隐私字段'),
        ('aesthetic-forms.md / aesthetic-creative.md', '美学艺术类 第一、二篇', '互补', '形态与意境仍由既有主干裁决'),
        ('aesthetics-evan-design.md', '美学艺术类 第七、十二章', '相似', '界面化转译仍以 evan-design 为准'),
    ],
    conflict=[
        ('既有「情绪→布光」方向与新库光比／光位参数起点不一致', '先按情绪方向定光型，再用新库参数做试拍起点，以直方图／放大检查／输出测试修正', '环境可行性优先；新库明确数值均为试拍起点'),
        ('新库光比定义（主辅入射光强之比）与既有文档口径不同', '统一采用新库定义并记录测量方法；不得把反射亮度比与入射比混写', '摄影类 3.3'),
        ('东方体系「消解光影」（禁硬轮廓光与强明暗交界线）与新库经典布光法冲突', '以体系逻辑裁决；刻意反向须写明目的', 'core-00 底层逻辑优先'),
        ('新库商业／交付规范与用户指定的客户输出规范冲突', '以客户和输出方规范为准', '摄影类 使用说明 / 10.1'),
        ('新库白平衡／影调建议与 core-03 传统色板冲突', '色名与 HEX 以 core-03 为准，白平衡与影调以新库为准', '两层不冲突'),
    ],
    hooks=[
        '**Step 1 之后**：按摄影类 1.6 补齐拍摄简报最小字段，缺项按〔推断〕标注。',
        '**Step 3–4**：先由既有情绪／形态映射定方向，再从摄影类对应章节取硬参数起点，逐项标注〔知识库·试拍起点〕。',
        '**Step 6–7**：在双重审美校验之外，追加摄影类 9.7 / 10.7 与自检 30 条相关项。',
    ],
    gate=[
        '光比是否注明「主辅入射光强之比」及测量方法',
        '所有曝光／焦段／景深数值是否标注为全画幅基准的试拍起点',
        '套图是否写明视觉统一基准与选片硬标准（8.2 / 8.4）',
        '交付是否含文件命名、3-2-1-1-0 备份、EXIF GPS 与设备序列清理（10.4–10.6）',
        '人像是否遵守精修适度原则与客户资料最小权限（9.6 / 10.6）',
    ]),

'ember-storyboard-build__skillhub': dict(
    skill='ember-storyboard-build', ver=SUB_VER, domain='视频分镜（D/E）',
    role=[('film-video.md', '影视类.md', '565 行 / 8 章', '**本领域主库**：电影语言、剧本、分镜、调度、剪辑声音与全流程检查表', 'Step 1 / 3–4 / 6–7'),
          ('aesthetics-art.md', '美学艺术类.md', '832 行 / 19 章', '**通用底层**：审美心理、中西范畴、创意机制与自检 30 条', 'Step 2 / 5 / 6'),
          ('photography.md', '摄影类.md', '698 行 / 10 章', '跨领域参考：剧照、布光与静态构图；组合交付时转总控', '组合交付')],
    routing=[
        ('Step 1 解析规格', '影视类 1.1–1.4 / 8.1', '创作意图、目标观众、时长媒介、立项筛选'),
        ('Step 2–3 情绪→视听', '美学艺术类 第一篇第二、五、六章', '审美心理与中西范畴，补 emotion-map'),
        ('Step 3–4 视听方案', '影视类 2.1–2.8、4.1–4.5、5.1–5.4', '景别／视点／蒙太奇／连续性／分镜字段／运动禁忌／演员调度'),
        ('Step 4 分镜', '影视类 3.1–3.6', '场景卡、人物弧、对白潜文本（叙事型）'),
        ('Step 5 创作深化', '美学艺术类 第八、十七章', '创意机制与灵感提取规则'),
        ('Step 6 三重校验', '影视类 2.6、6.5、8.9', '轴线与连续性、母版检查、无讲解试片验收'),
        ('Step 7 交付', '影视类 7.6 / 8.10', '竖屏安全区与字幕、输出发布归档'),
    ],
    merge=[
        ('cinematic-language.md', '影视类 第二章', '相似：蒙太奇／长镜头／连续性', '合并取更严者；30° 法则与不越轴保持 MUST'),
        ('shooting-kit.md', '影视类 4.2–4.5', '互补', '设备选择与动作覆盖取新库，可拍性以既有为准'),
        ('performance.md', '影视类 第五章', '相似：表演与调度', '视线与空间统一取新库更细条目'),
        ('emotion-map.md', '影视类 3.2 / 6.3', '互补', '情绪映射仍由既有主干裁决，新库补人物弧与声画关系'),
        ('output-template.md', '影视类 4.1', '相似：分镜字段', '字段合并，既有模板结构不降级'),
        ('aesthetic-forms.md', '美学艺术类 第一、六章', '互补', 'E 类意境型仍以总纲为准'),
    ],
    conflict=[
        ('新库 2.6「约三十度作为排查跳切的参考」与既有 30° 法则', '一致，合并为同一条；且新库明确「不以角度数字代替画面检查」，取更严者', '双重校验'),
        ('E 类 MUST 留 0.5–1.5 s 时间气口 与 新库 7.6「强节拍不等于持续快切」', '一致，气口规范保留为 MUST', '总纲情绪规范，新库支持'),
        ('新库允许「为情绪／断裂感有意破坏连续性」与既有不越轴 MUST', '允许，但须保持其他定位线索稳定、保留覆盖镜头，并写明目的', '影视类 2.6 + 总纲「刻意反向须写明目的」'),
        ('平台竖屏规格／时长与新库 7.6 不一致', '以发布平台现行规范为准，新库仅作通用原则', '影视类 使用说明'),
        ('新库剧本结构（人物弧／因果链）与总纲「意境型弱化因果」冲突', 'E 类以总纲意境四步为准，D 类叙事型取新库结构工具', '按交付类型分流'),
    ],
    hooks=[
        '**Step 1**：按影视类 1.1 / 8.1 固定创作意图、受众、时长、媒介与不可牺牲项。',
        '**Step 3–4**：由既有情绪／形态映射定视听方向，再从影视类第二／四／五章取硬规则，分镜字段按 4.1 补齐。',
        '**Step 6–7**：三重校验之外追加 2.6 轴线标注、8.9 试片验收与 7.6 竖屏检查。',
    ],
    gate=[
        '分镜是否标注主要行动轴／关系轴／屏幕方向，越轴是否有过渡镜头',
        '每场是否保留可重建空间的覆盖镜头',
        '动作接点是否核对起势／速度／轨迹／重心／完成阶段',
        '竖屏是否检查字幕安全区、无声观看与前段内容承诺',
        '输出前是否走 8.9 完整母版检查与 8.10 归档',
    ]),

'evan-design__skillhub': dict(
    skill='evan-design', ver=SUB_VER, domain='互联网产品 UI（J）',
    role=[('aesthetics-art.md', '美学艺术类.md', '832 行 / 19 章', '**本领域主库**：美学底层逻辑、设计／配色／字体版式／信息图、检查清单与自检 30 条', '步骤 2 / 4–5 / 6'),
          ('photography.md', '摄影类.md', '698 行 / 10 章', '跨媒介视觉参考（光影、构图、色彩管理），**不作为 UI 数值依据**', '仅参考'),
          ('film-video.md', '影视类.md', '565 行 / 8 章', '跨媒介参考（时序节奏、声画、竖屏），**不作为 UI 数值依据**', '仅参考')],
    routing=[
        ('定立意 L0', '美学艺术类 第一篇第一～六章', '价值路径、审美心理、中西范畴可操作定义，补 aesthetic-creation.md'),
        ('定气质 L1', '美学艺术类 第五章 / 第十九章', '中国范畴与当代补充规范'),
        ('立秩序 L2', '美学艺术类 第二篇第七、九、十二章', '功能—形式—语义—体验、比例、网格层级留白'),
        ('落感知 L3', '美学艺术类 第十一、十三章', '配色属性关系语义媒介、信息图与数据美学'),
        ('写界面代码', 'design-system.md / examples.md + assets/tokens.css', '**本 skill 唯一数值权威**'),
        ('逐条校验', '美学艺术类 第三篇第十五、十六章 + 结尾自检 30 条', '各媒介检查清单与评审标准'),
    ],
    merge=[
        ('aesthetic-creation.md（L0）', '美学艺术类 第一篇 / 第十七章', '相似：审美判断、范畴、灵感', '既有六步创作法为准，新库补「历史命题→设计规则」转译表与灵感边界'),
        ('design-system.md', '美学艺术类 第七、十一、十二、十三章', '相似：配色、字体、网格、留白', '**数值一律以本 skill 为准**；新库只补原理与论证'),
        ('eight-aesthetics.md', '美学艺术类 第五章 / 日本审美范畴', '互补', '八意识量化阈值不改'),
        ('examples.md', '美学艺术类 第十五章', '相似：检查清单', '检查清单追加，示例不改'),
        ('第六节无障碍', '美学艺术类 第十九章（含 WCAG 2.2 等当代规范）', '相似', '本 skill 仍以 WCAG 2.1 AA 实测表为交付底线；2.2 条目作增强建议'),
    ],
    conflict=[
        ('新库给出的色值／字号／间距／比例与本 skill Token 不一致', '**一律以 assets/tokens.css 与 design-system.md 实测表为准**', '本 skill 是 WorkBuddy 视觉语言唯一数值权威'),
        ('新库提到 WCAG 2.2 而本 skill 规定 2.1 AA', '2.1 AA 为 MUST 底线；2.2 新增条目可作增强建议，不得据此放宽 2.1 AA', '第六节 MUST'),
        ('新库「破格／张力」表述与八意识「破至多 1 处、其余 100% 合规」冲突', '以八意识联检为准', '1.2 冲突裁决口径'),
        ('新库西方形式法则（黄金比例等）与东方 L1 意境冲突', '按 L1 → L2 → L3 顺序推导，L1 气质优先', '设计哲学内核'),
        ('摄影类／影视类知识库中的画面参数', '不作为 UI 数值依据，仅作跨媒介视觉参考', '领域边界'),
    ],
    hooks=[
        '**步骤 2 定立意**：用美学艺术类第一篇把「好看」拆成可论证的价值路径与心理机制。',
        '**步骤 4–5**：用第二篇第七／十一／十二／十三章补形式论证，但所有数值仍取 Token。',
        '**步骤 6**：在既有速查表 + 八意识联检 + 反模式之外，追加自检 30 条中界面相关项。',
    ],
    gate=[
        '灰阶层级是否先于色相检查（自检 30 条第 18 条）',
        '字体是否完成真实词组／小字号／全字符／混排／授权测试（第 19 条）',
        '五秒内是否有唯一视觉入口、一分钟内能否理解主要关系（第 15 条）',
        '信息是否不只依赖颜色／悬停／运动并具备等价通道（第 23 条）',
        '是否以真实尺寸、设备与任务完成测试（第 22 条）',
        '所有数值是否仍引用 Token、无硬编码（第四节 MUST）',
    ]),
}


def table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |',
           '|' + '|'.join(['---'] * len(headers)) + '|']
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


def make_doc(cfg):
    L = [f"# K 层 · 知识库融合总纲（{cfg['skill']} · v{cfg['ver']}）", '', COMMON_INTRO, '']
    L += ['## 一、三库清单与本 skill 角色', '',
          f"四包各收全量三库，本 skill 的角色分配如下（领域：**{cfg['domain']}**）。", '',
          table(['本包文件', '源文件', '规模', '本 skill 中的角色', '主要读取阶段'],
                cfg['role']), '']
    L += ['## 二、章节路由速查（按需读取）', '',
          '**MUST NOT**：不要把三份库全文塞进上下文。按当前阶段只读取下表对应章节；'
          '跨领域或组合交付转 `/ember-art-solution` 总控。', '',
          table(['阶段', '读取章节', '解决什么'], cfg['routing']), '']
    L += ['## 三、相似信息合并对照（融合而非堆叠）', '',
          '下表标明既有 reference 与新库章节的重复／互补关系及取舍口径；'
          '「取更严者」指同时满足两边要求，不降低任一侧的 MUST。', '',
          table(['既有 reference', '新库对应章节', '关系', '裁决'], cfg['merge']), '']
    L += ['## 四、冲突裁决表（MUST）', '',
          table(['冲突情形', '裁决', '依据'], cfg['conflict']), '']
    L += ['## 五、三个接入点（写入既有工作流）', '']
    L += [f'{i}. {h}' for i, h in enumerate(cfg['hooks'], 1)]
    L += ['', '## 六、质量门禁追加（在既有门禁之后执行）', '']
    L += [f'- [ ] {g}' for g in cfg['gate']]
    L += ['', '## 七、来源、边界与维护', '',
          '- 来源：`knowledge/dist` 由 587 册书籍全文（文字层提取／GPU OCR／EPUB）、56 个网页教程与联网补充的现行标准提炼；三库只保留规则、参数、规范与检查清单。',
          '- 文件名映射：源文件 美学艺术类.md、摄影类.md、影视类.md 在本包内分别重命名上述英文文件名，正文标题与章节编号保持原样。',
          '- 三库在包内自包含，无外部文件引用；不需要任何 MCP、API Key 或网络访问即可使用。',
          '- **所有数值均为试拍／试片／实测起点**，不替代现场直方图、放大检查、输出测试与真实设备验证；引用具体数值前建议回查原书。',
          '- 法规、无障碍标准、平台规范与版权要求以项目所在地现行版本与合同为准；知识库记录的是撰写时有效版本。',
          '- 本层只补「可执行规则与领域硬参数」，既不改变体系归属与审美立意，也不改动既有 Token、色值、阈值、模板与图标。',
          '', f"总纲 `ember-art-solution` v{MAIN_VER} · 本 skill v{cfg['ver']} · 2026-11-23"]
    return '\n'.join(L) + '\n'


# ---------------------------------------------------------------- 1. 注入三库
def inject():
    for pkg in PKGS:
        d = os.path.join(BUILD, pkg, 'references', 'knowledge')
        os.makedirs(d, exist_ok=True)
        for en, zh in BOOKS.items():
            shutil.copy2(os.path.join(SRC, zh), os.path.join(d, en))
        cfg = CFG[pkg]
        with open(os.path.join(d, 'KNOWLEDGE-INTEGRATION.md'), 'w', encoding='utf-8') as f:
            f.write(make_doc(cfg))
        print('inject', pkg, '->', len(os.listdir(d)), 'files')


DESC_ADD = ('；已融合 knowledge/dist 三份精炼知识库（美学艺术类／摄影类／影视类）作为 K 层'
            '通用创作规则与领域硬参数，含章节路由、相似信息合并对照与冲突裁决。'
            '触发词：知识库、创作前自检30条、拍摄简报、光比、布光参数、分镜字段、'
            '轴线、竖屏短视频、3-2-1-1-0备份、EXIF隐私、WCAG走查。')

SECTION_SUB = '''## 〇之二、知识库融合（K 层 · v{ver}）

本 skill 已融合 `references/knowledge/` 下三份精炼知识库，作为**通用创作规则 + 领域可执行硬参数**横切既有工作流。
完整章节路由、相似信息合并对照与冲突裁决见 `references/knowledge/KNOWLEDGE-INTEGRATION.md`（**接入前必读**）。

| 文件 | 本 skill 中的角色 |
|---|---|
| `knowledge/{main}` | {main_role} |
| `knowledge/{aux}` | {aux_role} |
| `knowledge/{ref}` | {ref_role} |
| `knowledge/KNOWLEDGE-INTEGRATION.md` | **融合总纲**：章节路由、相似信息合并对照、冲突裁决表、门禁追加项 |

### K.1 三个接入点（MUST）

{hooks}

### K.2 按需读取（MUST NOT）

不要把三份库全文塞进上下文。按 `KNOWLEDGE-INTEGRATION.md` 第二节的章节路由，只读取当前阶段对应章节。

### K.3 冲突裁决摘要

{conflict}

### K.4 质量门禁追加（在既有校验之后执行）

{gate}

---

'''


def patch_skill_md():
    # ---- 主 skill ----
    p = os.path.join(BUILD, PKG_MAIN, 'SKILL.md')
    t = open(p, encoding='utf-8').read()
    t = re.sub(r'(?m)^version:.*$', 'version: ' + MAIN_VER, t, count=1)
    m = re.search(r'(?m)^description: ".*"$', t)
    line = m.group(0); i = line.rfind('"')
    t = t.replace(line, line[:i] + DESC_ADD + line[i:], 1)
    t = t.replace('### 1.2 五层能力栈', '### 1.2 五层能力栈 ＋ K 层横切', 1)
    t = t.replace('| **L4 质量与交付** | 三重校验、模板、成品 | `core-10` `assets/*` |',
                  '| **L4 质量与交付** | 三重校验、模板、成品 | `core-10` `assets/*` |\n'
                  '| **K 知识库层（横切 L1–L4）** | 通用创作规则、领域硬参数、各媒介检查清单 | `references/knowledge/` |', 1)
    t = t.replace('**每一项参数都要有出处或〔补全〕标注**',
                  '**K 层补充（v1.2.0）**：按交付 ID 加读 `references/knowledge/` 对应章节'
                  '（D/E → film-video、F/G → photography、其余 → aesthetics-art），'
                  '硬参数写入方案并标注〔知识库·起点〕。章节路由与裁决见 '
                  '`references/knowledge/KNOWLEDGE-INTEGRATION.md`。\n\n'
                  '**每一项参数都要有出处或〔补全〕标注**', 1)
    t = t.replace('- `core-08` 八意识过一遍，破格 ≤1 处且目的明确。',
                  '- `core-08` 八意识过一遍，破格 ≤1 处且目的明确。\n'
                  '- `references/knowledge/aesthetics-art.md` 第二篇（设计／建筑／绘画／配色／字体版式／信息图）'
                  '补可执行形式规则；与 `core-03` 色板冲突时按体系逻辑裁决。', 1)
    t = t.replace('**任一 MUST 项不过 → 回 P4–P6 修正后重跑，不得带病交付**',
                  '**K 层追加**：叠加 `aesthetics-art.md` 结尾「创作前自检 30 条」通用项、'
                  '影视类 8.9 / 摄影类 10.7 领域验收项；详见 '
                  '`references/knowledge/KNOWLEDGE-INTEGRATION.md` 第六节。\n\n'
                  '**任一 MUST 项不过 → 回 P4–P6 修正后重跑，不得带病交付**', 1)
    t = t.replace('### references/domain/ · 四套完整领域库（自四个 skill 全量融入）',
                  '### references/knowledge/ · K 层知识库（v1.2.0 融合）\n\n'
                  '| 文件 | 内容 | 何时读 |\n|---|---|---|\n'
                  '| `KNOWLEDGE-INTEGRATION.md` | **融合总纲**：三库角色、章节路由、相似信息合并对照、冲突裁决、门禁追加 | **P4 / P7 必读** |\n'
                  '| `aesthetics-art.md` | 美学艺术类：三篇 19 章，底层逻辑／表现方法／创作标准与自检 30 条 | P2 P5 P6 P7 |\n'
                  '| `photography.md` | 摄影类：10 章，表达／单张流程／布光／构图／摆姿／组图／后期／交付 | F/G 的 P4 P7 P8 |\n'
                  '| `film-video.md` | 影视类：8 章，电影语言／剧本／分镜／调度／剪辑声音／短视频检查表 | D/E 的 P4 P7 P8 |\n\n'
                  '> 三库为规则／参数／检查清单型文本，包内自包含；**按章节读取，禁止全文载入**。\n\n'
                  '### references/domain/ · 四套完整领域库（自四个 skill 全量融入）', 1)
    t = t.replace('| `icons/ember-art-solution-icon.svg` | 技能图标（宣纸白圆角卡 + 靛青 + 焦墨 + 朱砂单点，与四个子 skill 同源） |',
                  '| `icons/ember-art-solution-icon.svg` | 技能图标（宣纸白圆角卡 + 靛青 + 焦墨 + 朱砂单点，与四个子 skill 同源） |\n'
                  '| `icons/ember-art-solution-icon-v2.svg` / `.png` / `ICON-DESIGN.md` | 图标 v2 候选（evan-design 规范重设计）；**根目录 `_icon.png` 未替换** |', 1)
    t = t.rstrip() + '\n\n' + CHANGE_MAIN
    open(p, 'w', encoding='utf-8').write(t)
    print('patch SKILL.md', PKG_MAIN)

    # ---- 三个子 skill ----
    SUBMETA = {
        'ember-photography-posing__skillhub': dict(
            main='photography.md', main_role='**本领域主库**：现场参数、标准流程与交付规范',
            aux='aesthetics-art.md', aux_role='通用底层：审美心理、中西范畴、配色与创作前自检 30 条',
            ref='film-video.md', ref_role='跨领域参考；组合交付转 `/ember-art-solution`'),
        'ember-storyboard-build__skillhub': dict(
            main='film-video.md', main_role='**本领域主库**：电影语言、分镜、调度与全流程检查表',
            aux='aesthetics-art.md', aux_role='通用底层：审美心理、中西范畴、创意机制与自检 30 条',
            ref='photography.md', ref_role='跨领域参考（剧照／布光）；组合交付转 `/ember-art-solution`'),
        'evan-design__skillhub': dict(
            main='aesthetics-art.md', main_role='**本领域主库**：美学底层逻辑、设计／配色／字体版式、检查清单与自检 30 条',
            aux='photography.md', aux_role='跨媒介视觉参考（光影、构图、色彩管理），不作 UI 数值依据',
            ref='film-video.md', ref_role='跨媒介参考（时序节奏、声画、竖屏），不作 UI 数值依据'),
    }
    for pkg in PKG_SUB:
        p = os.path.join(BUILD, pkg, 'SKILL.md')
        t = open(p, encoding='utf-8').read()
        t = re.sub(r'(?m)^version:.*$', 'version: "' + SUB_VER + '"', t, count=1)
        t = t.replace('artSolution: "ember-art-solution@1.1.0"',
                      'artSolution: "ember-art-solution@1.2.0"', 1)
        t = t.replace('（ember-art-solution 统摄 · v2.1.0）',
                      '（ember-art-solution 统摄 · v2.2.0）', 1)
        t = t.replace('（美学主导全场景方案总控，v1.1.0）',
                      '（美学主导全场景方案总控，v1.2.0）', 1)
        m = re.search(r'(?m)^description: ".*"$', t)
        line = m.group(0); i = line.rfind('"')
        t = t.replace(line, line[:i] + DESC_ADD + line[i:], 1)
        meta = SUBMETA[pkg]
        cfg = CFG[pkg]
        sec = SECTION_SUB.format(
            ver=SUB_VER, **meta,
            hooks='\n'.join(f'{i}. {h}' for i, h in enumerate(cfg['hooks'], 1)),
            conflict='\n'.join(f'- **{c[0]}** → {c[1]}（{c[2]}）'
                               for c in cfg['conflict'][:3]),
            gate='\n'.join(f'- [ ] {g}' for g in cfg['gate'][:4]))
        anchor = '\n## Overview\n' if '\n## Overview\n' in t else '\n## When to Use\n'
        t = t.replace(anchor, '\n' + sec + anchor.lstrip('\n'), 1)
        # Resources 追加 K 层清单
        res = ('### references/knowledge/（K 层 · v2.2.0 融合）\n'
               '- `KNOWLEDGE-INTEGRATION.md` — **融合总纲**：章节路由、相似信息合并对照、冲突裁决、门禁追加（接入前必读）\n'
               '- `aesthetics-art.md` — 美学艺术类：三篇 19 章 + 创作前自检 30 条\n'
               '- `photography.md` — 摄影类：10 章，现场参数／标准流程／交付规范\n'
               '- `film-video.md` — 影视类：8 章，电影语言／分镜／调度／全流程检查表\n\n')
        t = t.replace('### assets/\n', res + '### assets/\n', 1)
        t = t.rstrip() + '\n\n' + CHANGE_SUB.format(pkg=pkg, domain=cfg['domain'])
        open(p, 'w', encoding='utf-8').write(t)
        print('patch SKILL.md', pkg)


CHANGE_MAIN = '''## [1.2.0] 增量 · 2026-11-23

融合 `E:\\skills\\material\\knowledge\\dist` 三份精炼知识库，新增 **K 层（知识库层）**：

- 新增 `references/knowledge/`：`aesthetics-art.md`（美学艺术类 832 行 / 19 章）、`photography.md`（摄影类 698 行 / 10 章）、`film-video.md`（影视类 565 行 / 8 章），以及 `KNOWLEDGE-INTEGRATION.md` 融合总纲（章节路由、相似信息合并对照、冲突裁决、门禁追加）。
- SKILL.md：能力栈新增横切 K 层；P4 按交付 ID 路由到对应知识库、P6 用第二篇补形式规则、P7 叠加自检 30 条与领域验收项；Resources 新增 K 层清单；description 增补触发词。
- 明确裁决：core-00 仍是体系最高依据；新库数值均为「试拍／试片起点」，现场实测优先；J 类数值权威仍在 evan-design；组合交付共享同一张定位卡。
- 原有 12 份 core、3 份 scene、32 份领域库、5 个模板、色值与调用方式**均不变**；根目录 `_icon.png` 未替换，`assets/icons/` 下的 v2 候选图标仅作为资产随包保留。
'''

CHANGE_SUB = '''### 2.2.0 增量（2026-11-23）

融合 `E:\\skills\\material\\knowledge\\dist` 三份精炼知识库，新增 **K 层（知识库层）**：

- 新增 `references/knowledge/`：三库全量 + `KNOWLEDGE-INTEGRATION.md` 融合总纲（本 skill 专属的章节路由、相似信息合并对照、冲突裁决表、门禁追加项）。
- SKILL.md 新增「〇之二、知识库融合」章节：三个接入点、按需读取约束、冲突裁决摘要、门禁追加项；Resources 增补 K 层清单；description 增补触发词；`artSolution` 指向 `ember-art-solution@1.2.0`。
- 领域：{domain}。原有工作流主干、既有 references、模板、Token、色值、量化阈值与图标**全部保留**；K 层只补「可执行规则与硬参数」，不改体系归属与审美立意。
'''


def patch_aux():
    # bridge / README 追加 K 层指向；元数据与 CHANGELOG 升版
    for pkg in PKGS:
        d = os.path.join(BUILD, pkg)
        is_main = pkg == PKG_MAIN
        ver = MAIN_VER if is_main else SUB_VER
        if not is_main:
            for fn in ['references/art-solution/bridge.md', 'references/art-solution/README.md']:
                fp = os.path.join(d, fn)
                t = open(fp, encoding='utf-8').read()
                if 'K 层知识库' not in t:
                    t = t.rstrip() + ('\n\n---\n\n## K 层知识库（v2.2.0）\n\n'
                        '本 skill 另融合 `references/knowledge/` 三份精炼知识库（aesthetics-art / photography / film-video）。'
                        '总纲章节路由、相似信息合并对照与冲突裁决见 '
                        '`references/knowledge/KNOWLEDGE-INTEGRATION.md`；'
                        '本文件与 `art-solution/` 仍是体系归属与立意的裁决依据，K 层只补可执行规则与硬参数。\n')
                    open(fp, 'w', encoding='utf-8').write(t)
        for fn in ['_meta.json', '_skillhub_meta.json']:
            fp = os.path.join(d, fn)
            obj = json.load(open(fp, encoding='utf-8'))
            obj['version'] = ver
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
        cp = os.path.join(d, 'CHANGELOG.md')
        old = open(cp, encoding='utf-8').read()
        entry = CHANGE_MAIN if is_main else CHANGE_SUB.format(domain=CFG[pkg]['domain'])
        if f'[{ver}]' not in old and f'## {ver}' not in old and f'### {ver}' not in old:
            open(cp, 'w', encoding='utf-8').write(old.rstrip() + '\n\n---\n\n' + entry)
        print('aux', pkg, '->', ver)


def pack():
    os.makedirs(DIST, exist_ok=True)
    for pkg in PKGS:
        ver = MAIN_VER if pkg == PKG_MAIN else SUB_VER
        d = os.path.join(BUILD, pkg)
        out = os.path.join(DIST, f'{pkg}_v{ver}.zip')
        root = os.path.basename(d)
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            z.writestr(root + '/', '')
            for base, dirs, files in os.walk(d):
                dirs.sort(); files.sort()
                for fn in files:
                    full = os.path.join(base, fn)
                    rel = os.path.relpath(full, d)
                    z.write(full, root + '/' + '/'.join(rel.split(os.sep)))
        with zipfile.ZipFile(out) as z:
            n = len([x for x in z.namelist() if not x.endswith('/')])
        print('PACK', os.path.basename(out), os.path.getsize(out), 'bytes |', n, 'files')


BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_backup')
BACKUP_FILES = ['SKILL.md', 'CHANGELOG.md', '_meta.json', '_skillhub_meta.json',
                'references/art-solution/bridge.md', 'references/art-solution/README.md']


def backup():
    if os.path.exists(BACKUP):
        print('backup already exists -> skip')
        return
    for pkg in PKGS:
        for rel in BACKUP_FILES:
            s = os.path.join(BUILD, pkg, rel)
            if not os.path.exists(s):
                continue
            o = os.path.join(BACKUP, pkg, rel.replace('/', os.sep))
            os.makedirs(os.path.dirname(o), exist_ok=True)
            shutil.copy2(s, o)
    print('backup ->', BACKUP)


def restore():
    for pkg in PKGS:
        for rel in BACKUP_FILES:
            s = os.path.join(BACKUP, pkg, rel.replace('/', os.sep))
            if os.path.exists(s):
                shutil.copy2(s, os.path.join(BUILD, pkg, rel.replace('/', os.sep)))
    print('restored from', BACKUP)


if __name__ == '__main__':
    import sys
    if '--restore' in sys.argv:
        restore()
    else:
        backup()
        inject()
        patch_skill_md()
        patch_aux()
        pack()
