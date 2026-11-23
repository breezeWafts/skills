#!/usr/bin/env python3
"""
ember-reader · 分层内容池确定性导出器

把分层内容池 JSON 转成：精简知识库 Markdown、Mermaid 脑图、OPML 脑图、规范化 JSON。
仅使用 Python 标准库；不联网、不改写内容、不补全缺失信息、不生成书籍观点。

用法：
  python export_knowledge.py --input layers.json --outdir ./out [--prefix name] [--force]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def text(value, default=""):
    if value is None:
        return default
    return str(value).strip()


def mermaid_safe(value):
    s = text(value).replace("\n", " ")
    for old, new in (("(", "（"), (")", "）"), ("[", "【"), ("]", "】"),
                     ("{", "｛"), ("}", "｝"), ('"', "'")):
        s = s.replace(old, new)
    return re.sub(r"\s+", " ", s).strip()


def slug(value):
    s = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text(value)).strip("-")
    return s or "ember-reader"


def display_title(value):
    raw = text(value, "未命名书籍")
    return raw if raw.startswith("《") else f"《{raw}》"


def load_data(path):
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("内容池根节点必须是 JSON 对象")
    for key in ("l1", "l2", "l3"):
        if not isinstance(data.get(key, []), list):
            raise ValueError(f"字段 {key} 必须是数组")
    return data


def validate(data):
    errors = []
    l1_ids = {text(item.get("id")) for item in data.get("l1", [])}
    for item in data.get("l1", []):
        if text(item.get("certainty")) == "推断":
            errors.append(f"{text(item.get('id'))} 为推断内容，不得进入 L1")
    for key in ("l2", "l3"):
        for item in data.get(key, []):
            parent = text(item.get("parent"))
            if parent and parent not in l1_ids:
                errors.append(f"{text(item.get('id'))} 的 parent={parent} 指向不存在的 L1 编号")
    return errors


def build_knowledge_base(data):
    book = data.get("book", {})
    title = display_title(book.get("title"))
    lines = [
        f"# {title} · 精简知识库",
        "",
        f"- 作者：{text(book.get('author'), '未标注')}",
        f"- 类型：{text(book.get('type'), '未标注')}",
        f"- 生成日期：{text(book.get('generated_at'), '未标注')}",
        f"- 覆盖度声明：{text(book.get('coverage'), '未标注')}",
    ]
    sources = book.get("sources") or []
    if sources:
        lines.append("- 材料来源：" + "；".join(text(s) for s in sources))
    lines.append("")

    keywords = [text(k) for k in data.get("keywords", []) if text(k)]
    quotes = [text(q) for q in data.get("quotes", []) if text(q)]
    if keywords or quotes:
        lines += ["## 一页纸", ""]
        if keywords:
            lines += [f"### {len(keywords)} 关键词", "", " · ".join(keywords), ""]
        if quotes:
            lines += [f"### {len(quotes)} 金句", ""]
            lines += [f"{i}. {q}" for i, q in enumerate(quotes, 1)]
            lines.append("")

    l1 = data.get("l1", [])
    if l1:
        lines += ["## L1 · 主干（作者想传达什么）", ""]
        for item in l1:
            tail = f"　〔{text(item.get('source'))}〕" if text(item.get("source")) else ""
            lines.append(f"- **{text(item.get('id'))}** {text(item.get('text'))}{tail}")
        lines.append("")

    l2 = data.get("l2", [])
    if l2:
        lines += ["## L2 · 三栏式知识点笔记", ""]
        grouped = {}
        for item in l2:
            grouped.setdefault(text(item.get("parent"), "未挂载"), []).append(item)
        for parent, items in grouped.items():
            lines += [f"### 挂载于 {parent}", "", "| 知识点 | 内容（原文主干 + 修饰） | 感悟（改变了什么理解） | 行动（做点什么） | 出处 |",
                      "|---|---|---|---|---|"]
            for item in items:
                cell = lambda v: text(v).replace("|", "\\|").replace("\n", " ")
                lines.append("| {} | {} | {} | {} | {} |".format(
                    cell(item.get("knowledge_point")), cell(item.get("content")),
                    cell(item.get("insight")), cell(item.get("action")),
                    cell(item.get("source"))))
            lines.append("")

    l3 = data.get("l3", [])
    if l3:
        lines += ["## L3 · 例证 / 故事 / 类比", "", "| 编号 | 挂载主干 | 类型 | 内容 | 把什么讲具体了 | 出处 |",
                  "|---|---|---|---|---|---|"]
        for item in l3:
            cell = lambda v: text(v).replace("|", "\\|").replace("\n", " ")
            lines.append("| {} | {} | {} | {} | {} | {} |".format(
                cell(item.get("id")), cell(item.get("parent")), cell(item.get("kind")),
                cell(item.get("content")), cell(item.get("supports")), cell(item.get("source"))))
        lines.append("")

    l4 = data.get("l4", {}) or {}
    labels = (("consensus", "共识"), ("divergence", "分歧"),
              ("supplement", "补充"), ("counterexample", "反例"))
    if any(l4.get(k) for k, _ in labels):
        lines += ["## L4 · 同类对照", ""]
        for key, label in labels:
            rows = l4.get(key) or []
            if not rows:
                continue
            lines += [f"### {label}", ""]
            for row in rows:
                src = text(row.get("source")) if isinstance(row, dict) else ""
                body = text(row.get("text")) if isinstance(row, dict) else text(row)
                lines.append(f"- {body}" + (f"　〔来源：{src}〕" if src else ""))
            lines.append("")

    plan = data.get("study_plan", {}) or {}
    if plan:
        lines += ["## 学习与复习方案", ""]
        for key, label in (("path", "学习路径"), ("schedule", "时间排程"), ("review", "复习节奏")):
            if text(plan.get(key)):
                lines += [f"### {label}", "", text(plan.get(key)), ""]
        checks = plan.get("checks") or []
        if checks:
            lines += ["### 检验清单", ""] + [f"- [ ] {text(c)}" for c in checks] + [""]

    return "\n".join(lines).rstrip() + "\n"


def build_mindmap(data):
    book = data.get("book", {})
    title = mermaid_safe(display_title(book.get("title")))
    lines = ["mindmap", f"  root(({title}))", "    L1 主干"]
    by_parent = {}
    for item in data.get("l2", []):
        by_parent.setdefault(text(item.get("parent")), []).append(item)
    l3_by_parent = {}
    for item in data.get("l3", []):
        l3_by_parent.setdefault(text(item.get("parent")), []).append(item)
    for item in data.get("l1", []):
        lid = text(item.get("id"))
        lines.append(f"      {mermaid_safe(lid + ' ' + text(item.get('text')))}")
        l2s = by_parent.get(lid, [])
        if l2s:
            lines.append("        L2 知识点")
            for l2 in l2s:
                lines.append(f"          {mermaid_safe(text(l2.get('id')) + ' ' + text(l2.get('knowledge_point')))}")
        l3s = l3_by_parent.get(lid, [])
        if l3s:
            lines.append("        L3 例证")
            for l3 in l3s:
                lines.append(f"          {mermaid_safe(text(l3.get('id')) + ' ' + text(l3.get('kind')) + '：' + text(l3.get('content')))}")
    l4 = data.get("l4", {}) or {}
    labels = (("consensus", "共识"), ("divergence", "分歧"),
              ("supplement", "补充"), ("counterexample", "反例"))
    if any(l4.get(k) for k, _ in labels):
        lines.append("    L4 同类对照")
        for key, label in labels:
            rows = l4.get(key) or []
            if not rows:
                continue
            lines.append(f"      {label}")
            for row in rows:
                body = text(row.get("text")) if isinstance(row, dict) else text(row)
                lines.append(f"        {mermaid_safe(body)}")
    return "\n".join(lines) + "\n"


def opml_outline(node_text, children=None, level=2):
    pad = "  " * level
    attrs = 'text="{}"'.format(escape(node_text, {'"': "&quot;"}))
    if not children:
        return [f"{pad}<outline {attrs} />"]
    out = [f"{pad}<outline {attrs}>"]
    for child in children:
        out.extend(opml_outline(child[0], child[1], level + 1))
    out.append(f"{pad}</outline>")
    return out


def build_opml(data):
    book = data.get("book", {})
    title = display_title(book.get("title"))
    by_parent = {}
    for item in data.get("l2", []):
        by_parent.setdefault(text(item.get("parent")), []).append(item)
    l3_by_parent = {}
    for item in data.get("l3", []):
        l3_by_parent.setdefault(text(item.get("parent")), []).append(item)

    l1_children = []
    for item in data.get("l1", []):
        lid = text(item.get("id"))
        children = []
        l2s = by_parent.get(lid, [])
        if l2s:
            children.append(("L2 知识点", [
                (text(l2.get("id")) + " " + text(l2.get("knowledge_point"))
                 + "｜" + text(l2.get("content")), None) for l2 in l2s]))
        l3s = l3_by_parent.get(lid, [])
        if l3s:
            children.append(("L3 例证", [
                (text(l3.get("id")) + " " + text(l3.get("kind"))
                 + "：" + text(l3.get("content")), None) for l3 in l3s]))
        l1_children.append((lid + " " + text(item.get("text")), children or None))

    root_children = [("L1 主干", l1_children or None)]
    l4 = data.get("l4", {}) or {}
    labels = (("consensus", "共识"), ("divergence", "分歧"),
              ("supplement", "补充"), ("counterexample", "反例"))
    l4_children = []
    for key, label in labels:
        rows = l4.get(key) or []
        if rows:
            l4_children.append((label, [(text(r.get("text")) if isinstance(r, dict) else text(r), None)
                                        for r in rows]))
    if l4_children:
        root_children.append(("L4 同类对照", l4_children))

    head = ['<?xml version="1.0" encoding="UTF-8"?>', '<opml version="2.0">',
            "  <head>", f"    <title>{escape(title)}</title>", "  </head>", "  <body>"]
    body = opml_outline(title, root_children, level=2)
    tail = ["  </body>", "</opml>"]
    return "\n".join(head + body + tail) + "\n"


def main():
    parser = argparse.ArgumentParser(description="ember-reader 分层内容池导出器")
    parser.add_argument("--input", required=True, help="分层内容池 JSON 路径")
    parser.add_argument("--outdir", required=True, help="输出目录")
    parser.add_argument("--prefix", default=None, help="输出文件名前缀（默认取书名）")
    parser.add_argument("--force", action="store_true", help="允许覆盖同名文件")
    args = parser.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        print(f"[错误] 输入文件不存在：{src}")
        return 1
    try:
        data = load_data(src)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"[错误] 内容池解析失败：{exc}")
        return 1

    errors = validate(data)
    if errors:
        for err in errors:
            print(f"[校验失败] {err}")
        return 1

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or slug(data.get("book", {}).get("title"))
    outputs = {
        f"{prefix}-knowledge-base.md": build_knowledge_base(data),
        f"{prefix}-mindmap.mmd": build_mindmap(data),
        f"{prefix}-mindmap.opml": build_opml(data),
        f"{prefix}-layers.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    }
    existing = [name for name in outputs if (outdir / name).exists()]
    if existing and not args.force:
        print("[错误] 以下同名文件已存在，未覆盖：" + "、".join(existing))
        print("       请先询问用户，确认后加 --force 重新运行。")
        return 2

    for name, content in outputs.items():
        (outdir / name).write_text(content, encoding="utf-8")
        print(f"[已生成] {outdir / name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
