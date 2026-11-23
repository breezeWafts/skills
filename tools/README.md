# tools/ — Skill 同步工具

## `sync_skills.py`

**用途**：落实「每次更新 skill 版本都覆盖 GitHub 上传目录中对应 skill」这一约定。

工作区 `E:\skills\material\aesthetics\build\` 是唯一源码真源；`E:\skills\gitskills\` 是 GitHub 上传目录。本脚本把前者的 skill 目录**逐文件镜像**到后者，并自动刷新 README 中的版本号。

### 常用命令

在 `E:\skills\gitskills` 下执行：

```bash
# 同步全部 5 个 skill（版本更新后的标准动作）
python tools/sync_skills.py

# 只同步刚升版的那个 skill
python tools/sync_skills.py ember-art-solution__skillhub

# 先看看会改什么，不写文件
python tools/sync_skills.py --dry-run

# 覆盖 + 自动提交推送到 main
python tools/sync_skills.py --push "feat: ember-art-solution 升 1.3.0"

# 升版时若有文件被删除，同步删除目标中的旧文件
python tools/sync_skills.py --prune --push
```

### 行为说明

| 行为 | 默认 | 说明 |
|---|---|---|
| 新增 / 覆盖文件 | 是 | 按内容 SHA-256 比对，内容相同则跳过，避免无意义 diff |
| 删除目标中的孤立文件 | 否 | 需显式 `--prune`，且逐文件删除，绝不用递归目录删除 |
| 刷新 skill 内 `README.md` 版本号 | 是 | 目标缺失时从 `templates/SKILL-README.md` 生成 |
| 刷新根 `README.md` 版本表 | 是 | 从各 `SKILL.md` frontmatter 读取真实版本 |
| 提交与推送 | 否 | 需 `--push`；推送走 SSH |

### Git 通道

```
origin  https://github.com/breezeWafts/skills.git          (fetch，用户指定地址)
origin  git@github.com:breezeWafts/skills.git              (push，已配置 SSH 密钥)
```

HTTPS 无凭据，故推送走 SSH；两者指向同一仓库。若换机器，需先配置可访问 `breezeWafts/skills` 的 SSH key，或把 pushurl 改成带 token 的 HTTPS。

### 路径覆盖

可用环境变量覆盖默认路径：

```bash
SKILLS_BUILD_DIR=D:/work/build SKILLS_GIT_DIR=D:/work/gitskills python tools/sync_skills.py
```

### 合并后的两类源码真源

- 美学系 5 个 skill：`E://skills//material//aesthetics//build//<skill>//`
- `ember-reader`（超级读者）：`C://Users//Administrator//.workbuddy//skills//ember-reader//`，可用 `EMBER_READER_DIR` 覆盖

`ember-reader` 沿用其自带文档，不使用 `templates/SKILL-README.md`（该模板面向美学总控 skill）。
推送只 stage 明确的 skill 目录与仓库基建，不会因部分检出而误删远程已有文件。

## `templates/`

| 文件 | 用途 |
|---|---|
| `ROOT-README.md` | 仓库根 README 模板（版本表由脚本刷新） |
| `SKILL-README.md` | skill 目录内 GitHub 展示页模板（`{{当前版本}}` 由脚本刷新） |

> 模板只在目标文件缺失时使用；已存在的 README 只做版本号替换，不会被整体覆盖，便于手工补充内容。

## 约定提醒

1. **先升版、再同步**：工作区完成 SKILL.md / `_meta.json` / `_skillhub_meta.json` / CHANGELOG / zip 打包后，再运行本脚本。
2. **上传包仍从工作区取**：SkillHub 平台上传用 `dist/` 下带版本号的 zip；本仓库只放源码形态，不放 zip。
3. **不要把构建中间产物入库**：根目录下 `_` 开头的目录（OCR 采样、图标草稿、同步脚本快照等）已被 `.gitignore` 排除；skill 目录内以 `_` 开头的必要文件（`_icon.png`、`_meta.json`）不受影响。
