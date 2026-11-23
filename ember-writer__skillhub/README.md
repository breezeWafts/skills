# Ember Writer · 超级作家（美学总纲版）

> `ember-writer__skillhub` · Skill 源码镜像 · 版本 **2.1.0**

本目录是 [WorkBuddy](https://www.workbuddy.cn/) / SkillHub 技能的源码形态。仓库总览与版本同步规则见 [仓库根 README](../../README.md)。

## 调用方式

```
/ember-writer 说明你要生成的方案，以及风格 / 氛围 / 感觉
```

主入口总控 skill 是 `/ember-art-solution`：跨领域、组合交付，或只给「感觉」不给领域参数时应使用总控；单一领域任务可直接用本 skill。

## 目录结构

```
ember-writer__skillhub/
├── SKILL.md                 # 技能入口：frontmatter + 执行工作流（务必先读）
├── README.md                # 本文件（GitHub 展示）
├── CHANGELOG.md             # 版本变更记录
├── _meta.json               # 平台发布元数据
├── _skillhub_meta.json
├── _icon.png                # 技能图标
├── references/              # 领域知识库
└── assets/                  # 模板、Token、图标源文件
```

> 实际文件以本目录为准；`SKILL.md` 的 `Resources` 段给出完整的按需读取指引。

## 依赖与安装

- **运行时依赖：无。** 纯知识型 skill，不调用 MCP、API 或网络，无需 API Key。
- 安装：将本目录整体放入 Agent 平台的 skills 目录即可。
- SkillHub 平台上传请使用工作区 `dist/` 下带版本号的 zip 包，而非本仓库源码目录。

## 版本同步

本目录由仓库根 `tools/sync_skills.py` 从工作区 `build/ember-writer__skillhub/` 镜像同步。每次 skill 升版后，覆盖本目录并刷新本文件的版本号；原有工作流、模板、色值与数值规范保持不变。

---

*变更记录见 [CHANGELOG.md](./CHANGELOG.md) · 当前版本 **2.1.0***
