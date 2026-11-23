# ember-art-solution · 美学主导的全场景方案总控

> **把「一句感觉」变成「一份可直接执行、且经得起审美推敲的交付方案」。**

| | |
|---|---|
| 调用 | `/ember-art-solution` |
| 当前版本 | **1.2.0** |
| 类型 | 纯知识型 Skill（零外部依赖） |
| 平台 | WorkBuddy / Claude Skills / 兼容 SKILL.md 规范 |
| 入口文件 | [`SKILL.md`](./SKILL.md) |

## 一句话使用

```
/ember-art-solution 给我一份【风格 / 氛围 / 感觉】的【产品】方案，（内容 / 用途 / 约束…）
```

不必懂美学，不必指定体系，甚至可以说「风格根据作品内容制定」。Skill 负责把模糊的感觉 **归一化 → 定位 → 落参数 → 出成品**，缺信息按规则推断并标注〔推断〕，全程不打断追问。

**示例**

- `给我生成一份 30 秒的视频分镜脚本，故事内容为 XXX，需要东方美学意境`
- `给我生成一套摄影作品展示的网站，风格根据作品内容制定`
- `要一张有「雨后空山」感觉的专辑封面方案`
- `做一个侘寂氛围的茶室室内方案，35㎡ 朝北`
- `写一篇让人看完能静下来的散文，宋式极简`

## 覆盖的 14 类交付

| 组 | 交付物 |
|---|---|
| A–C | 文章 / 散文、小说 / 故事、文案与品牌叙事 |
| D–E | 长视频分镜、30 秒短视频分镜脚本 |
| F–G | 单张照片拍摄方案、组照 / 系列写真 |
| H–I | 海报、封面 / 装帧 |
| J | 互联网产品 UI / 网站 / 落地页 / 仪表盘 |
| K–M | 室内设计、园林设计、造景陈设 |
| N | 声景与听觉方案 |

支持**组合交付**（如「网站＋海报＋封面」），各子件共享同一张美学定位卡。凡通过视觉或听觉承载的内容，都可注入美学表达。

## 执行工作流

固定八步，不可跳步：

```
P1 解析需求（不追问） → P2 美学定位（定位卡） → P3 选交付规格 → P4 领域执行
→ P5 创作深化 → P6 形式与色彩落地 → P7 三重质量门禁 → P8 输出交付
```

**美学定位卡**是核心：主体系（东方 / 西方 / 阿拉伯-伊斯兰）→ 三级流派 → 四条底层逻辑（色彩观念 / 光影 / 空间 / 终极目标）→ 主情绪与审美形态 → 传统色板（色名＋HEX）→ 形式手法 → 目标观者反应。

> **底层逻辑永远优先于表面符号。** 贴青花、贴枯山水却仍用焦点透视＋满构图＋高饱和，判为「有形无意」，不合格。

## 目录结构

```
ember-art-solution__skillhub/
├── SKILL.md                         # 入口：frontmatter + P1–P8 + Resources
├── README.md                        # 本文件（GitHub 展示）
├── CHANGELOG.md                     # 1.0.0 → 1.1.0 → 1.2.0
├── _meta.json / _skillhub_meta.json # 平台发布元数据
├── _icon.png                        # 技能图标
├── references/
│   ├── core-00 … core-10            # 总纲 12 份：架构 / 路由 / 交付矩阵 / 色彩 / 形式
│   │                                #   / 理论索引与精炼结论 / 形态 / 创作法 / 八意识
│   │                                #   / 情绪全感官 / 质量门禁
│   ├── scene-11 / 12 / 13           # 空间 / 声景 / 平面 扩展场景
│   ├── domain/                      # 四套领域库 32 份（writing / video / photo / ui）
│   └── knowledge/                   # K 层：美学艺术 / 摄影 / 影视 + 融合总纲
└── assets/
    ├── *-template.md                # 通用 / 写作 / 分镜 / 摄影 交付骨架
    ├── tokens.css                   # 设计 Token（UI 产出时引用）
    └── icons/                       # 图标 SVG / PNG 与 ICON-DESIGN.md 设计说明
```

## 知识底座与来源

- **主架构**：工作区《美学分类组织架构总表.xlsx》完整转写于 `references/core-00-architecture.md`。
- **色彩**：三套传统色库真实 HEX（中国 526 色 / 日式 250 色 / 伊斯兰 30 色），取色要求色名可溯源。
- **理论**：22 册美学原典经全文 TXT 核实后，合并去重为 T1–T9 九个主题族，含可执行转译参数与四级来源标注，见 `references/core-05-theory-digest.md`。
- **K 层**：三份精炼知识库（美学艺术 / 摄影 / 影视）提供现场硬参数与检查清单；与总纲的相似信息合并与冲突裁决见 `references/knowledge/KNOWLEDGE-INTEGRATION.md`。

原书扫描件、全文 TXT 与三套色表原件**不随本仓库分发**。若需引用原书具体页码，须回原书核对，不得编造。

## 与四个子 skill 的关系

本 skill 是**总控**，已完整融入下列四个 skill 的全部功能；四者亦各自回融本总纲：

| 子 skill | 本包中的落点 |
|---|---|
| `ember-writer` | `references/domain/writing/` (8) ＋ `assets/writer-template.md` |
| `ember-storyboard-build` | `references/domain/video/` (9) ＋ `assets/storyboard-template.md` |
| `ember-photography-posing` | `references/domain/photo/` (11) ＋ `assets/photo-plan-template.md` |
| `evan-design` | `references/domain/ui/` (4) ＋ `assets/tokens.css` |

单一领域任务可直用子 skill；**跨领域、组合交付，或用户只给「感觉」不给领域参数时，应使用本总控**。

## 硬约束（六条）

1. 不追问 — 缺信息按规则推断，标注〔推断〕
2. 体系必下沉 — 定位到三级流派，不许停在「东方美学」四字
3. 底层逻辑优先 — 四条逻辑必须与 `core-00` 一致
4. 色值可溯源 — 每个 HEX 有色名或流派色表出处
5. 一种形态为主 — 跨体系混搭须写主次比、接缝与理由
6. 美学不压可用性 — 可读性 / 可操作性 / 可拍性 / 可通行性永远优先

## 安装

将本目录整体放入 Agent 平台的 skills 目录即可（无需 API Key、无需网络、无需 MCP）。SkillHub 平台上传请使用工作区 `dist/` 下带版本号的 zip 包，而非本仓库源码目录。

---

*变更记录见 [CHANGELOG.md](./CHANGELOG.md) · 版本同步规则见仓库根 [README.md](../README.md)*
