#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ember-reader local knowledge base: index / domains / sections / query / sync.

Progressive disclosure is the whole point: the five libraries total ~470 KB, so
never load one wholesale. `query` returns only the best-matching sections, each
with an exact file + heading path + line range so the skill can cite them.

Standard library only. UTF-8 in and out.

  python scripts/knowledge.py index
  python scripts/knowledge.py domains
  python scripts/knowledge.py sections --domain it
  python scripts/knowledge.py query "等保 上线检查" --domain it --top 5 --max-chars 6000
  python scripts/knowledge.py query "构图 光比" --text "摄影构图与布光" --json
  python scripts/knowledge.py sync --from "E:/skills/material/knowledge/dist"
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KDIR = ROOT / "knowledge"
INDEX = KDIR / "index.json"
HEADING = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
SPLIT = re.compile(r"[\s,，、;；/|]+")

# Domain metadata doubles as the domain-routing table for the skill.
DOMAINS = [
    {
        "id": "it",
        "file": "IT类.md",
        "name": "IT 解决方案 · 架构 · 服务器 · 安全合规 · 界面设计",
        "entry": "方案评审用第一篇，上线用第二篇检查清单，安全用第三篇，界面走查用第四篇",
        "keywords": ["架构", "解决方案", "分层", "服务器", "操作系统", "Linux", "内核", "性能调优",
                     "部署", "运维", "可观测性", "高可用", "高并发", "可靠性", "容灾", "安全", "等保",
                     "网安法", "数据安全", "个人信息", "漏洞", "OWASP", "渗透", "攻防", "零信任",
                     "界面设计", "UI", "UX", "无障碍", "WCAG", "设计系统", "云原生", "容器", "微服务",
                     "数据库", "中间件", "网络", "算法", "编程", "代码", "上线检查"],
    },
    {
        "id": "data",
        "file": "数据分析类.md",
        "name": "数据分析 · 统计实验 · 建模 · 可视化 · 数据治理",
        "entry": "先定决策与口径，再按章节取方法，收尾用流程清单验收",
        "keywords": ["数据分析", "数据工程", "统计", "指标", "口径", "A/B", "实验", "假设检验",
                     "回归", "因果", "可视化", "图表", "BI", "建模", "机器学习", "深度学习",
                     "数据仓库", "湖仓", "采集", "治理", "ETL", "特征", "预测", "聚类", "时间序列",
                     "运筹", "优化", "样本", "显著性", "指标体", "数据质量"],
    },
    {
        "id": "aesthetics",
        "file": "美学艺术类.md",
        "name": "美学底层逻辑 · 艺术表现方法 · 创作标准与自检",
        "entry": "立意用第一篇，选形式用第二篇，流程与评审用第三篇",
        "keywords": ["美学", "艺术", "审美", "设计", "配色", "色彩", "版式", "字体", "构图", "比例",
                     "黄金分割", "建筑", "绘画", "创意", "形式", "意境", "禅", "侘寂", "物哀",
                     "留白", "雕塑", "视觉", "范畴", "理念", "神显", "味论"],
    },
    {
        "id": "photography",
        "file": "摄影类.md",
        "name": "摄影表达 · 布光 · 构图摆姿 · 后期与交付",
        "entry": "拍摄前查第 2~7 章，组图策划查第 8 章，后期交付查第 9~10 章",
        "keywords": ["摄影", "拍照", "相机", "镜头", "焦段", "光圈", "快门", "曝光", "布光", "光位",
                     "光比", "影棚", "自然光", "景深", "RAW", "后期", "修图", "人像", "摆姿",
                     "组图", "闪光灯", "直方图", "白平衡", "感光度", "选片"],
    },
    {
        "id": "film",
        "file": "影视类.md",
        "name": "影视创作 · 电影语言 · 剧本分镜 · 剪辑声音",
        "entry": "开发期用剧本章，筹备期用分镜章，拍摄后期用调度与剪辑章",
        "keywords": ["影视", "电影", "剧本", "编剧", "分镜", "蒙太奇", "长镜头", "剪辑", "导演",
                     "演员", "调度", "声音", "短视频", "纪录片", "镜头语言", "类型片", "场记",
                     "试片", "连续性", "对白", "叙事"],
    },
]

BY_ID = {d["id"]: d for d in DOMAINS}

# Short book-side terms often differ from the wording used inside the libraries
# (e.g. "等保" vs "网络安全等级保护"). Expansion terms carry half the weight.
SYNONYMS = {
    "等保": ["等级保护", "合规", "安全体系"],
    "上线检查": ["安全检查", "检查清单", "上线基线"],
    "安全合规": ["合规", "攻防", "漏洞"],
    "UI": ["界面", "人因", "无障碍"],
    "WCAG": ["无障碍", "对比度"],
    "A/B": ["实验", "假设检验", "随机"],
    "口径": ["指标", "数据质量", "定义"],
    "建模": ["模型", "算法选型"],
    "构图": ["观看路径", "视觉关系", "主体"],
    "布光": ["光位", "光比", "光质"],
    "光比": ["布光", "光位"],
    "蒙太奇": ["剪辑", "镜头"],
    "剧本": ["人物", "冲突", "结构"],
    "留白": ["虚实", "余白", "空白"],
    "配色": ["色彩", "明度"],
}


def read_lines(path):
    return path.read_text(encoding="utf-8").splitlines()


def split_sections(lines):
    """Cut a library into sections at ## / ### / #### headings; keep heading path.

    The block before the first heading holds each library's usage notes and
    reading order, so it is indexed as an explicit preamble section too.
    """
    sections = []
    preamble_end = len(lines)
    for number, line in enumerate(lines, 1):
        if HEADING.match(line):
            preamble_end = number - 1
            break
    if preamble_end > 0:
        sections.append({
            "level": 2,
            "title": "库使用说明与导航",
            "path": ["库使用说明与导航"],
            "start": 1,
            "end": preamble_end,
        })
    stack = {}
    current = None
    for number, line in enumerate(lines, 1):
        match = HEADING.match(line)
        if not match:
            continue
        if current is not None:
            current["end"] = number - 1
            sections.append(current)
        level = len(match.group(1))
        title = match.group(2).strip()
        stack[level] = title
        for existing in list(stack):
            if existing > level:
                del stack[existing]
        current = {
            "level": level,
            "title": title,
            "path": [stack[k] for k in sorted(stack)],
            "start": number,
            "end": len(lines),
        }
    if current is not None:
        sections.append(current)
    return sections


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def build_index():
    KDIR.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "source": "knowledge/*.md", "domains": []}
    for domain in DOMAINS:
        path = KDIR / domain["file"]
        if not path.exists():
            raise SystemExit("missing knowledge file: %s" % path)
        lines = read_lines(path)
        sections = split_sections(lines)
        payload["domains"].append({
            "id": domain["id"],
            "file": domain["file"],
            "name": domain["name"],
            "entry": domain["entry"],
            "keywords": domain["keywords"],
            "lines": len(lines),
            "bytes": path.stat().st_size,
            "sha256_12": file_digest(path),
            "sections": sections,
        })
    INDEX.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(d["lines"] for d in payload["domains"])
    count = sum(len(d["sections"]) for d in payload["domains"])
    print("index ok: %d domains, %d sections, %d lines -> %s" %
          (len(payload["domains"]), count, total, INDEX.relative_to(ROOT)))
    return payload


def load_index():
    if not INDEX.exists():
        return build_index()
    return json.loads(INDEX.read_text(encoding="utf-8"))


def domain_hits(text):
    scores = {}
    for domain in DOMAINS:
        scores[domain["id"]] = sum(text.count(k) for k in domain["keywords"])
    return scores


def section_text(lines, section):
    return "\n".join(lines[section["start"] - 1:section["end"]]).strip()


def query(terms, domain_ids, top, max_chars, as_json, expand=True):
    weighted = [(term, 1.0) for term in terms]
    if expand:
        seen = set(terms)
        for term in terms:
            for extra in SYNONYMS.get(term, []):
                if extra not in seen:
                    weighted.append((extra, 0.5))
                    seen.add(extra)
    index = load_index()
    meta = {d["id"]: d for d in index["domains"]}
    selected = domain_ids or [d["id"] for d in index["domains"]]
    cache = {}
    results = []
    for domain_id in selected:
        if domain_id not in meta:
            raise SystemExit("unknown domain: %s (try: domains)" % domain_id)
        info = meta[domain_id]
        cache[domain_id] = read_lines(KDIR / info["file"])
        lines = cache[domain_id]
        for section in info["sections"]:
            heading = " ".join(section["path"])
            body = section_text(lines, section)
            score = 0.0
            for term, weight in weighted:
                score += (min(heading.count(term), 3) * 4
                          + min(body.count(term), 6)) * weight
            if score:
                results.append({
                    "domain": domain_id,
                    "file": info["file"],
                    "path": section["path"],
                    "start": section["start"],
                    "end": section["end"],
                    "score": round(score, 1),
                    "text": body,
                })
    results.sort(key=lambda r: (-r["score"], r["file"], r["start"]))
    total_matches = len(results)
    results = results[:top]
    budget = max(400, max_chars)
    per = max(200, budget // max(1, len(results)))
    for item in results:
        if len(item["text"]) > per:
            item["text"] = item["text"][:per].rstrip() + "\n…（片段截断，按行号回查原文）"
            item["truncated"] = True
        else:
            item["truncated"] = False
    if as_json:
        print(json.dumps({"terms": terms, "expanded": expand, "domains": selected,
                          "total_matches": total_matches, "results": results},
                         ensure_ascii=False, indent=2))
        return
    print("terms: %s%s" % (" / ".join(terms), " (+synonyms)" if expand else ""))
    print("domains: %s" % ", ".join(selected))
    print("matched sections: %d (showing %d, char budget %d)\n" %
          (total_matches, len(results), budget))
    if not results:
        print("NO MATCH. Try: sections --domain <id> to browse headings, or fewer/different terms.")
        return
    for number, item in enumerate(results, 1):
        print("[%d] %s › %s  (L%d-%d, score %.1f)" %
              (number, item["file"], " › ".join(item["path"]),
               item["start"], item["end"], item["score"]))
        print(item["text"])
        print()


def main():
    parser = argparse.ArgumentParser(description="ember-reader local knowledge base")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("index", help="rebuild knowledge/index.json from the .md files")
    sub.add_parser("domains", help="list the five domains and their routing keywords")

    p_sections = sub.add_parser("sections", help="browse the heading tree of one domain")
    p_sections.add_argument("--domain", help="domain id; omit to list all")

    p_query = sub.add_parser("query", help="retrieve cited sections for given terms")
    p_query.add_argument("keywords", help="space/comma separated terms")
    p_query.add_argument("--domain", action="append", help="restrict to a domain id (repeatable)")
    p_query.add_argument("--text", default="", help="optional book summary used to auto-detect domains")
    p_query.add_argument("--top", type=int, default=5)
    p_query.add_argument("--max-chars", type=int, default=6000)
    p_query.add_argument("--json", action="store_true")
    p_query.add_argument("--no-expand", action="store_true", help="disable synonym expansion")

    p_sync = sub.add_parser("sync", help="copy .md files from the source dist dir, then rebuild index")
    p_sync.add_argument("--from", dest="source", required=True)

    args = parser.parse_args()

    if args.command == "index":
        build_index()
    elif args.command == "domains":
        index = load_index()
        for domain in index["domains"]:
            print("%-12s %-6s %5d lines %4d sections  %s" %
                  (domain["id"], domain["file"], domain["lines"],
                   len(domain["sections"]), domain["name"]))
            print("   entry: %s" % domain["entry"])
            print("   keywords: %d" % len(domain["keywords"]))
    elif args.command == "sections":
        index = load_index()
        for domain in index["domains"]:
            if args.domain and domain["id"] != args.domain:
                continue
            print("=== %s (%s) ===" % (domain["id"], domain["file"]))
            for section in domain["sections"]:
                indent = "  " * (section["level"] - 1)
                print("%sL%-5d %s" % (indent, section["start"], section["title"]))
    elif args.command == "query":
        terms = [t for t in SPLIT.split(args.keywords.strip()) if t]
        if not terms:
            raise SystemExit("no keywords given")
        domain_ids = args.domain
        if not domain_ids and args.text:
            scores = domain_hits(args.text)
            best = max(scores.values()) if scores else 0
            if best > 0:
                domain_ids = [k for k, v in scores.items() if v >= max(1, best * 0.4)]
                print("auto-detected domains from --text: %s\n" % ", ".join(domain_ids))
        query(terms, domain_ids, args.top, args.max_chars, args.json,
              expand=not args.no_expand)
    elif args.command == "sync":
        source = Path(args.source)
        if not source.is_dir():
            raise SystemExit("not a directory: %s" % source)
        KDIR.mkdir(parents=True, exist_ok=True)
        copied = []
        for path in sorted(source.glob("*.md")):
            shutil.copy2(path, KDIR / path.name)
            copied.append(path.name)
        print("copied: %s" % ", ".join(copied))
        build_index()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
