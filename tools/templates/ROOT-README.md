# Ember Aesthetics Skills

> 一套以「美学主导」为核心的内容生成方案 Skills，覆盖文章、小说、分镜、摄影、海报封面、UI、室内、园林、造景、声景等全场景。

本仓库是 [WorkBuddy](https://www.workbuddy.cn/) / SkillHub 平台的技能源码镜像，用于版本留存与分发。**上传包（zip）由工作区单独构建，本仓库存放解压后的源码形态。**

## 调用方式

主入口是总控 skill：

```
/ember-art-solution 给我一份【风格 / 氛围 / 感觉】的【产品】方案，（内容 / 用途 / 约束…）
```

用户不必懂美学，也不必指定体系；只说一句「感觉」即可，缺信息由 skill 自行推断补全，不打断追问。

```
/ember-art-solution 给我生成一份 30 秒的视频分镜脚本，故事内容为 XXX，需要东方美学意境
/ember-art-solution 给我生成一套摄影作品展示的网站，风格根据作品内容制定
/ember-art-solution 要一张有「雨后空山」感觉的专辑封面方案
```

单一领域任务也可以直接使用对应的子 skill。

## 仓库内容

| 目录 | Skill | 版本 | 定位 |
|---|---|---|---|
| [`ember-art-solution__skillhub/`](./ember-art-solution__skillhub/) | `/ember-art-solution` | **1.2.0** | 美学主导全场景方案总控（主 skill） |
| [`ember-writer__skillhub/`](./ember-writer__skillhub/) | `/ember-writer` | 2.1.0 | 文章 / 小说 / 文案内容生成 |
| [`ember-storyboard-build__skillhub/`](./ember-storyboard-build__skillhub/) | `/ember-storyboard-build` | 2.2.0 | 长短视频分镜脚本 |
| [`ember-photography-posing__skillhub/`](./ember-photography-posing__skillhub/) | `/ember-photography-posing` | 2.2.0 | 单张 / 组照拍摄方案 |
| [`evan-design__skillhub/`](./evan-design__skillhub/) | `/evan-design` | 2.2.0 | 东方美学界面与视觉规范 |

每个目录的标准结构：

```
<skill>/
├── SKILL.md                 # 技能入口（frontmatter + 执行工作流）
├── CHANGELOG.md             # 版本变更记录
├── _meta.json               # 平台发布元数据
├── _skillhub_meta.json
├── _icon.png                # 技能图标
├── references/              # 知识库（core / scene / domain / knowledge / art-solution）
└── assets/                  # 模板、Token、图标源文件、设计说明
```

## 主 skill 的能力结构

- **主架构**：《美学分类组织架构总表》— 东方 / 西方 / 阿拉伯-伊斯兰三大体系、15 个三级流派，以及「色彩观念 / 光影处理 / 空间构图 / 终极目标」四条底层逻辑对照。**底层逻辑优先于表面符号**。
- **14 类交付（A–N）**：文章散文、小说故事、文案品牌叙事、长视频分镜、30 秒短视频分镜、单张照片、组照系列、海报、封面装帧、UI / 网站 / 落地页、室内设计、园林设计、造景陈设、声景听觉，支持组合交付。
- **知识库**：12 份 `core-*` 总纲、3 份 `scene-*` 扩展场景、32 份四套领域库、4 份 K 层知识库（美学艺术 / 摄影 / 影视 / 融合总纲）。含三套传统色库（中国 526 色 / 日式 250 色 / 伊斯兰 30 色）、画面审美六法、留白三法、八大审美意识、三重质量门禁。
- **理论底座**：22 册美学理论原典合并去重为 T1–T9 九个主题族，已用全文 TXT 核实，见 `references/core-05-theory-digest.md`。原书扫描件与全文 TXT **不随仓库分发**，引用具体页码须回原书核对。
- **零外部依赖**：纯知识型 skill，不调用 MCP、API、网络；安装即用，无需 API Key。

## 版本同步约定

本仓库与本地工作区 `E:\skills\material\aesthetics\build\` 保持镜像关系：

> **每次 skill 版本更新，都会用工作区最新源码覆盖本仓库中对应的 skill 目录，并同步更新根 README 版本表与目录内 README。**

同步由 `tools/sync_skills.py` 执行，支持全量 / 指定 skill / 仅比对 / 自动提交推送。详见 [tools/README.md](./tools/README.md)。

## 依赖与许可

- 运行时依赖：**无**（纯 Markdown / CSS / 图标资产）
- 平台：WorkBuddy / Claude Skills / 兼容 SKILL.md 规范的 Agent 平台
- 理论原典、图片素材版权归原作者所有；本仓库仅收录**归纳转译后的结论**，不含原书扫描件
- 本仓库代码与文档的使用许可由仓库所有者另行声明

---

*仓库地址：https://github.com/breezeWafts/skills.git · 默认分支：`main`*
