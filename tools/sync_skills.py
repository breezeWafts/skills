#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_skills.py — Skill 版本同步器

约定：每次 skill 版本更新后，用两处源码真源的最新版本，
      覆盖 GitHub 上传目录 E:/skills/gitskills/ 中对应的 skill 目录。

用法（在本仓库根目录或任意目录执行均可）：
    python tools/sync_skills.py                       # 同步全部 5 个 skill
    python tools/sync_skills.py ember-art-solution__skillhub   # 只同步指定 skill
    python tools/sync_skills.py --dry-run            # 只比对并报告，不写任何文件
    python tools/sync_skills.py --force              # 内容一致也强制重写
    python tools/sync_skills.py --prune              # 同时删除目标中源已不存在的旧文件
    python tools/sync_skills.py --push "提交说明"     # 覆盖后自动 commit + push 到 main

默认行为：逐文件镜像（新增 / 覆盖 / 保持不变），不删除目标中的孤立文件；
          --prune 才删除。绝不使用递归目录删除，避免误伤。

推送通道：origin 的 fetch URL 为 HTTPS（用户指定），pushurl 为 SSH
          git@github.com:breezeWafts/skills.git（已配置密钥，可免密推送）。
"""

import os
import re
import sys
import shutil
import hashlib
import argparse
import subprocess
from pathlib import Path

# ---------------------------------------------------------------- 路径配置
WORKSPACE = Path(os.environ.get("SKILLS_BUILD_DIR", r"E:/skills/material/aesthetics/build"))
GITROOT = Path(os.environ.get("SKILLS_GIT_DIR", r"E:/skills/gitskills"))
TEMPLATES = Path(__file__).resolve().parent / "templates"

PKGS = [
    "ember-art-solution__skillhub",
    "ember-writer__skillhub",
    "ember-storyboard-build__skillhub",
    "ember-photography-posing__skillhub",
    "evan-design__skillhub",
    "ember-reader",
]

# 合并两路来源：美学系来自 aesthetics/build，超级读者来自已安装 skills 目录
SOURCE_ROOTS = {p: WORKSPACE / p for p in PKGS if p != "ember-reader"}
SOURCE_ROOTS["ember-reader"] = Path(os.environ.get(
    "EMBER_READER_DIR", r"C:/Users/Administrator/.workbuddy/skills/ember-reader"))

# 不参与镜像的目标侧顶层文件/目录（由脚本单独维护或属于仓库基建）
KEEP_TOP = {".git", ".gitignore", ".gitattributes", "README.md", "tools"}

# 复制时忽略的临时文件
IGNORE_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def read_version(skill_md: Path) -> str:
    """从 SKILL.md frontmatter 读取 version。"""
    if not skill_md.exists():
        return ""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?m)^version:\s*\"?([\d.]+)", text)
    return m.group(1) if m else ""


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path):
    """相对路径 -> 绝对路径，递归遍历普通文件。"""
    out = {}
    if not root.is_dir():
        return out
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git"}]
        for fn in files:
            if fn in IGNORE_NAMES or fn.endswith((".pyc", ".pyo")):
                continue
            full = Path(base) / fn
            rel = full.relative_to(root).as_posix()
            out[rel] = full
    return out


def mirror(src: Path, dst: Path, *, force=False, prune=False, dry=False):
    """把 src 逐文件镜像到 dst，返回 (新增, 更新, 未变, 删除)。"""
    src_files = iter_files(src)
    dst_files = iter_files(dst)
    added = updated = same = removed = 0

    for rel, sfile in sorted(src_files.items()):
        dfile = dst / rel
        if not dfile.exists():
            added += 1
            if not dry:
                dfile.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sfile, dfile)
        elif force or digest(sfile) != digest(dfile):
            updated += 1
            if not dry:
                shutil.copy2(sfile, dfile)
        else:
            same += 1

    stale = sorted(set(dst_files) - set(src_files))
    if prune:
        for rel in stale:
            removed += 1
            if not dry:
                (dst / rel).unlink(missing_ok=True)
    return added, updated, same, removed, stale


def read_frontmatter(skill_md: Path) -> dict:
    """读取 SKILL.md frontmatter 里的 name / displayName / version。"""
    out = {}
    if not skill_md.exists():
        return out
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    for key in ("name", "displayName", "version"):
        m = re.search(r"(?m)^" + key + r":\s*\"?([^\"\r\n]+?)\"?\s*$", text)
        if m:
            out[key] = m.group(1).strip()
    return out


def ensure_skill_readme(dst_pkg: Path, pkg: str, ver: str, dry=False):
    """保证 skill 目录内有 GitHub 展示用 README.md，并刷新版本号。

    目标缺失时用 tools/templates/SKILL-README.md 生成（填充占位符）；
    目标已存在（例如主 skill 的详细手写 README）只刷新版本号，不整体覆盖。
    """
    target = dst_pkg / "README.md"
    tpl = TEMPLATES / "SKILL-README.md"
    created = False
    if not target.exists():
        if not tpl.exists():
            return "模板缺失，跳过"
        fm = read_frontmatter(dst_pkg / "SKILL.md")
        cmd = "/" + pkg.replace("__skillhub", "")
        display = fm.get("displayName") or fm.get("name") or cmd
        text = (tpl.read_text(encoding="utf-8")
                .replace("{{DISPLAY}}", display)
                .replace("{{NAME}}", pkg)
                .replace("{{CMD}}", cmd)
                .replace("{{VERSION}}", ver))
        if dry:
            return "将新建 README.md（" + ver + "）"
        target.write_text(text, encoding="utf-8", newline="\n")
        created = True

    text = target.read_text(encoding="utf-8")
    # 兼容两种写法：表格「| 当前版本 | **1.2.0** |」与行内「版本 **1.2.0**」
    new = re.sub(r"(\*\*)\d+\.\d+\.\d+(\*\*)",
                 lambda m: m.group(1) + ver + m.group(2), text)
    new = re.sub(r"(\|\s*当前版本\s*\|\s*)[\d.]+(\s*\|)",
                 lambda m: m.group(1) + ver + m.group(2), new, count=1)
    if new != text and not dry:
        target.write_text(new, encoding="utf-8", newline="\n")
    return ("新建" if created else "刷新") + " README -> " + ver


def update_root_readme(versions: dict, dry=False):
    """把根 README.md 版本表中的版本号刷新为工作区实际版本。"""
    root_readme = GITROOT / "README.md"
    tpl = TEMPLATES / "ROOT-README.md"
    if not root_readme.exists():
        if not tpl.exists():
            return "模板缺失，跳过"
        if dry:
            return "将新建根 README.md"
        root_readme.write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    lines = root_readme.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        hit = next((p for p in PKGS if f"`{p}/`" in line and line.lstrip().startswith("|")), None)
        if hit and versions.get(hit):
            line = re.sub(r"\b\d+\.\d+\.\d+\b", versions[hit], line, count=1)
        out.append(line)
    new = "\n".join(out) + "\n"
    if new != root_readme.read_text(encoding="utf-8") and not dry:
        root_readme.write_text(new, encoding="utf-8", newline="\n")
    return "版本表已刷新"


def git_push(message: str, fetch_first=False):
    """提交并推送到 main（pushurl 走 SSH）。

    默认不做 fetch：本仓库体积较大时一次 fetch 可能耗时数分钟，而本地
    通常已是最新。若远程可能被他人更新过，用 --fetch-first 显式开启。
    """
    def run(*args):
        r = subprocess.run(["git", "-C", str(GITROOT), *args],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()

    if fetch_first:
        code, out = run("fetch", "--depth", "1", "git@github.com:breezeWafts/skills.git", "main")
        if code != 0:
            print("  [warn] fetch 失败（继续尝试提交）：", out[:200])
    # 明确路径，避免 no-checkout / 部分检出仓库把远程已有文件误判为删除
    paths = list(PKGS) + ["README.md", "tools", ".gitignore", ".gitattributes"]
    code, out = run("add", "-A", "--", *paths)
    if code != 0:
        return False, "git add 失败: " + out
    code, out = run("status", "--porcelain")
    if not out.strip():
        return True, "无变更，无需提交"
    code, out = run("commit", "-m", message)
    if code != 0:
        return False, "git commit 失败: " + out
    code, out = run("push", "origin", "HEAD:main")
    return code == 0, ("推送成功" if code == 0 else "推送失败: " + out) + "\n" + out[-400:]


def main():
    ap = argparse.ArgumentParser(description="同步 skill 源码到 GitHub 上传目录")
    ap.add_argument("pkgs", nargs="*", help="指定 skill 目录名；留空表示全部 5 个")
    ap.add_argument("--dry-run", action="store_true", help="只比对，不写文件")
    ap.add_argument("--force", action="store_true", help="内容一致也强制重写")
    ap.add_argument("--prune", action="store_true", help="删除目标中源已不存在的旧文件")
    ap.add_argument("--push", metavar="MSG", nargs="?", const="", help="覆盖后自动提交并推送")
    ap.add_argument("--fetch-first", action="store_true", help="推送前先 fetch（远程可能被他人更新时用）")
    args = ap.parse_args()

    targets = args.pkgs or PKGS
    unknown = [p for p in targets if p not in PKGS]
    if unknown:
        print("未知 skill:", ", ".join(unknown))
        print("可选:", ", ".join(PKGS))
        return 2

    if not WORKSPACE.is_dir():
        print("工作区 build 目录不存在:", WORKSPACE)
        return 2
    if not GITROOT.is_dir():
        GITROOT.mkdir(parents=True, exist_ok=True)
        print("已创建上传目录:", GITROOT)

    print("工作区 :", WORKSPACE)
    print("上传目录:", GITROOT)
    print("模式   :", "DRY-RUN" if args.dry_run else ("覆盖 + 推送" if args.push is not None else "覆盖"))
    print("-" * 74)

    versions = {}
    changed = []
    for pkg in targets:
        src = SOURCE_ROOTS[pkg]
        dst = GITROOT / pkg
        if not (src / "SKILL.md").exists():
            print(f"[跳过] {pkg}: 源目录缺少 SKILL.md")
            continue
        ver = read_version(src / "SKILL.md")
        old = read_version(dst / "SKILL.md") if dst.exists() else "(不存在)"
        versions[pkg] = ver
        a, u, s, d, stale = mirror(src, dst, force=args.force, prune=args.prune, dry=args.dry_run)
        if pkg == "ember-reader":
            note = "外部来源，沿用 skill 自带文档（不套美学模板）"
        else:
            note = ensure_skill_readme(dst, pkg, ver, dry=args.dry_run)
        flag = "变更" if (a or u or d) else "一致"
        print(f"[{flag}] {pkg:42s} {old:>9s} -> {ver:<9s} "
              f"新增{a:3d} 更新{u:3d} 未变{s:3d} 删除{d:3d} | {note}")
        if stale and not args.prune:
            print(f"         提示：目标有 {len(stale)} 个源已不存在的文件，未删除"
                  f"（如需清理加 --prune）：{', '.join(stale[:3])}")
        if a or u or d or old == "(不存在)":
            changed.append(f"{pkg} {old}->{ver}")

    # 根 README 版本表：总是读取全部 5 个 skill 的实际版本
    for p in PKGS:
        if p not in versions:
            for base in (GITROOT, WORKSPACE):
                v = read_version(base / p / "SKILL.md")
                if v:
                    versions[p] = v
                    break
    if not args.dry_run:
        print("-" * 74)
        print("根 README:", update_root_readme(versions))

    if args.push is not None and not args.dry_run:
        msg = args.push or ("sync: 更新 " + "; ".join(changed) if changed else "sync: 例行同步 skill 源码")
        print("-" * 74)
        ok, info = git_push(msg, fetch_first=args.fetch_first)
        print("推送:", info)
        return 0 if ok else 1

    print("-" * 74)
    print("完成。上传目录已与工作区最新源码对齐。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
