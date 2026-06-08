# -*- coding: utf-8 -*-
"""聚合医生画像并生成报告（Markdown + JSON）。"""
import json
from collections import Counter
from datetime import datetime
from typing import List, Dict

from .models import Paper, DoctorProfile

DISCLAIMER = (
    "本报告仅基于公开学术文献的客观信息整理，临床研究产出是医生诊疗能力的一个侧面，"
    "并不代表其全部水平；亦不构成对该医生的推荐或评价。是否为坐诊临床医生为启发式推断，"
    "需以医师执业注册信息及本人确认为准。"
)


def build_profile(name: str, affiliation: str, papers: List[Paper]) -> DoctorProfile:
    prof = DoctorProfile(name=name, affiliation_query=affiliation,
                         generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                         total_matched=len(papers))
    clinical = [p for p in papers if p.is_clinical]
    prof.clinical_papers = sorted(clinical, key=lambda p: p.quality_score, reverse=True)
    prof.excluded_papers = [p for p in papers if not p.is_clinical]

    # 擅长方向：临床论文 MeSH 词频（排除通用词）
    stop = {"Humans", "Animals", "Mice", "Male", "Female", "Adult", "Middle Aged", "Aged"}
    mesh_counter = Counter()
    for p in clinical:
        for m in p.mesh:
            if m not in stop:
                mesh_counter[m] += 1

    years = [p.year for p in clinical if p.year]
    first_last = sum(1 for p in clinical if p.target_author_pos in ("first", "last"))
    high_q = sum(1 for p in clinical if p.quality_score >= 70)
    best_evidence = max((p.evidence_level for p in clinical), default=0)
    retracted = [p for p in clinical if "Retracted" in p.flags]

    prof.summary = {
        "clinical_count": len(clinical),
        "first_or_last_author": first_last,
        "high_quality_count": high_q,
        "avg_quality": round(sum(p.quality_score for p in clinical) / len(clinical), 1) if clinical else 0,
        "best_evidence_level": best_evidence,
        "active_years": [min(years), max(years)] if years else [],
        "top_topics": [t for t, _ in mesh_counter.most_common(8)],
        "design_distribution": dict(Counter(p.study_design for p in clinical)),
        "retracted_count": len(retracted),
    }
    return prof


def to_markdown(prof: DoctorProfile) -> str:
    s = prof.summary
    L = []
    L.append(f"# 医生临床研究画像 · {prof.name}")
    L.append("")
    L.append(f"> 单位检索词：{prof.affiliation_query or '（未指定）'}　|　生成时间：{prof.generated_at}")
    L.append("")
    L.append(f"> ⚠️ {DISCLAIMER}")
    L.append("")
    L.append("## 一、执业身份（启发式）")
    L.append(f"- 是否坐诊临床医生（推断置信度）：**{prof.clinical_role_confidence}**")
    for sig in prof.role_signals:
        L.append(f"  - {sig}")
    L.append("")
    L.append("## 二、研究概览")
    L.append(f"- 命中论文总数：{prof.total_matched}，其中临床研究：**{s['clinical_count']}**")
    L.append(f"- 主导论文（第一/通讯位）：**{s['first_or_last_author']}**")
    L.append(f"- 高质量论文（评分≥70）：**{s['high_quality_count']}**，平均质量分：{s['avg_quality']}")
    if s["active_years"]:
        L.append(f"- 活跃年份：{s['active_years'][0]} – {s['active_years'][1]}")
    if s["top_topics"]:
        L.append(f"- 研究主题（擅长方向 · 推断）：{ '、'.join(s['top_topics']) }")
    if s["design_distribution"]:
        dist = "，".join(f"{k}:{v}" for k, v in s["design_distribution"].items())
        L.append(f"- 研究设计分布：{dist}")
    L.append(f"- 最高证据等级：{s['best_evidence_level']} / 5")
    if s["retracted_count"]:
        L.append(f"- ⚠️ 含撤稿论文：{s['retracted_count']} 篇（已大幅降权）")
    L.append("")
    L.append("## 三、代表性临床研究（按质量分排序）")
    L.append("")
    L.append("| 质量分 | 设计 | 证据 | 位置 | 年份 | 期刊 | 标题 |")
    L.append("|---:|---|:--:|:--:|:--:|---|---|")
    for p in prof.clinical_papers[:10]:
        pos = {"first": "第一", "last": "通讯/末", "middle": "参与"}.get(p.target_author_pos, "-")
        flag = " 🚩撤稿" if "Retracted" in p.flags else ""
        title = (p.title[:48] + "…") if len(p.title) > 48 else p.title
        L.append(f"| {p.quality_score} | {p.study_design} | {p.evidence_level} | {pos} | "
                 f"{p.year or '-'} | {p.journal_iso or p.journal_title} | {title}{flag} |")
    L.append("")
    if prof.excluded_papers:
        L.append(f"## 四、未纳入（非临床研究）：{len(prof.excluded_papers)} 篇")
        for p in prof.excluded_papers[:8]:
            L.append(f"- [{p.pmid}] {p.title}")
    L.append("")
    return "\n".join(L)


def to_json(prof: DoctorProfile) -> str:
    def paper_dict(p: Paper):
        return {
            "pmid": p.pmid, "title": p.title, "journal": p.journal_iso or p.journal_title,
            "year": p.year, "doi": p.doi, "study_design": p.study_design,
            "evidence_level": p.evidence_level, "author_position": p.target_author_pos,
            "quality_score": p.quality_score, "quality_detail": p.quality_detail,
            "flags": p.flags,
        }
    return json.dumps({
        "name": prof.name, "affiliation_query": prof.affiliation_query,
        "generated_at": prof.generated_at,
        "clinical_role_confidence": prof.clinical_role_confidence,
        "role_signals": prof.role_signals,
        "summary": prof.summary,
        "clinical_papers": [paper_dict(p) for p in prof.clinical_papers],
        "disclaimer": DISCLAIMER,
    }, ensure_ascii=False, indent=2)
