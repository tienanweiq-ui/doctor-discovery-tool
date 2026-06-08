# -*- coding: utf-8 -*-
"""命令行入口：医生临床研究画像 MVP 全流程。

在线（你本机）：
  python -m doctor_discovery.main --name "Zhang Wei" --affiliation "Shanghai Sixth People's Hospital" --citations

离线演示（无网络，用内置样例数据）：
  python -m doctor_discovery.main --name "Zhang Wei" --affiliation "Shanghai Sixth People's Hospital" --offline
"""
import argparse
import os

from . import pubmed_client, parse, classify, quality, identity, profile

_SAMPLE = os.path.join(os.path.dirname(__file__), "data", "sample_efetch.xml")


def run(name, affiliation, retmax=100, offline=False, use_citations=False,
        api_key=None, outdir="."):
    # 1) 采集
    if offline:
        with open(_SAMPLE, encoding="utf-8") as f:
            xml_text = f.read()
        pmids_for_cite = []
    else:
        pmids = pubmed_client.esearch_pmids(name, affiliation, retmax=retmax, api_key=api_key)
        print(f"esearch 命中 {len(pmids)} 篇")
        xml_text = pubmed_client.efetch_xml(pmids, api_key=api_key)
        pmids_for_cite = pmids

    # 2) 解析
    papers = parse.parse_articles(xml_text)
    print(f"解析得到 {len(papers)} 篇")

    # 3) 作者匹配 + 临床研究识别
    matched = []
    affils_for_role = []
    for p in papers:
        hit, pos, author = identity.match_author(p, name, affiliation)
        if not hit:
            continue
        p.target_author_pos = pos
        affils_for_role.append(author.affiliation)
        classify.classify(p)
        matched.append(p)
    print(f"匹配到目标医生的论文 {len(matched)} 篇")

    # 4) 被引（可选）
    citations = {}
    if use_citations and not offline:
        citations = pubmed_client.fetch_citations([p.pmid for p in matched])

    # 5) 质量评分
    tiers = quality.load_journal_tiers()
    for p in matched:
        quality.score_paper(p, tiers, citations or None)

    # 6) 画像 + 报告
    prof = profile.build_profile(name, affiliation, matched)
    conf, signals = identity.clinical_doctor_signal(affils_for_role)
    prof.clinical_role_confidence = conf
    prof.role_signals = signals

    os.makedirs(outdir, exist_ok=True)
    safe = name.replace(" ", "_")
    md_path = os.path.join(outdir, f"画像_{safe}.md")
    json_path = os.path.join(outdir, f"画像_{safe}.json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(profile.to_markdown(prof))
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(profile.to_json(prof))
    print(f"[OK] 报告已生成：{md_path}")
    print(f"[OK] 数据已生成：{json_path}")
    return prof


def main():
    ap = argparse.ArgumentParser(description="中国优秀医生发现计划 · 医生临床研究画像 MVP")
    ap.add_argument("--name", required=True, help='作者姓名，如 "Zhang Wei"')
    ap.add_argument("--affiliation", default="", help="单位关键词，用于消歧")
    ap.add_argument("--max", type=int, default=100, dest="retmax")
    ap.add_argument("--offline", action="store_true", help="用内置样例数据离线演示")
    ap.add_argument("--citations", action="store_true", help="抓取 iCite 被引（需联网）")
    ap.add_argument("--api-key", default=None, help="NCBI API key（可选，提升频率）")
    ap.add_argument("--out", default="output", help="输出目录")
    args = ap.parse_args()
    run(args.name, args.affiliation, retmax=args.retmax, offline=args.offline,
        use_citations=args.citations, api_key=args.api_key, outdir=args.out)


if __name__ == "__main__":
    main()
