# -*- coding: utf-8 -*-
"""论文质量多维评分。"""
import csv
import math
import os
from typing import Dict, Optional

from .models import Paper
from . import config

_DATA = os.path.join(os.path.dirname(__file__), "data", "journal_tiers.csv")


def load_journal_tiers(path: str = _DATA) -> Dict[str, dict]:
    tiers = {}
    if not os.path.exists(path):
        return tiers
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            key = (row.get("journal") or "").strip().lower()
            if key:
                tiers[key] = row
    return tiers


def _journal_score(paper: Paper, tiers: Dict[str, dict]) -> float:
    """0-100。优先 ISO 简称，其次全称匹配。"""
    rec = tiers.get(paper.journal_iso.lower()) or tiers.get(paper.journal_title.lower())
    if not rec:
        return 40.0  # 未知期刊给中性偏低分
    if str(rec.get("predatory", "0")) == "1":
        return 0.0   # 预警/掠夺性期刊
    # 用 JCR 分区映射，缺失则用 IF 粗略映射
    q = (rec.get("jcr_quartile") or "").upper()
    qmap = {"Q1": 95, "Q2": 75, "Q3": 55, "Q4": 40}
    if q in qmap:
        return float(qmap[q])
    try:
        iff = float(rec.get("impact_factor") or 0)
    except ValueError:
        iff = 0
    if iff >= 20:
        return 95.0
    if iff >= 10:
        return 85.0
    if iff >= 5:
        return 70.0
    if iff >= 2:
        return 55.0
    return 35.0


def _evidence_score(paper: Paper) -> float:
    return {5: 100, 4: 80, 3: 60, 2: 40, 1: 25}.get(paper.evidence_level, 30)


def _citation_score(paper: Paper, citations: Optional[Dict[str, int]]) -> Optional[float]:
    if not citations or paper.pmid not in citations:
        return None
    c = citations[paper.pmid]
    # 对数压缩：100 次引用约 ~92 分
    return min(100.0, 20 * math.log10(c + 1) * 1.0 + (40 if c > 0 else 0))


def _authorship_score(paper: Paper) -> float:
    pos = paper.target_author_pos
    return {"first": 100, "last": 90, "middle": 45, "none": 30}.get(pos, 40)


def score_paper(paper: Paper, tiers: Dict[str, dict],
                citations: Optional[Dict[str, int]] = None) -> Paper:
    w = dict(config.QUALITY_WEIGHTS)
    parts = {
        "journal": _journal_score(paper, tiers),
        "evidence": _evidence_score(paper),
        "authorship": _authorship_score(paper),
    }
    cit = _citation_score(paper, citations)
    if cit is None:
        # 无被引数据：把 citation 权重按比例分摊给其余维度
        w.pop("citation")
        total_w = sum(w.values())
        w = {k: v / total_w for k, v in w.items()}
    else:
        parts["citation"] = cit

    score = sum(parts[k] * w[k] for k in w)

    # 学术诚信否决：撤稿大幅扣分
    if "Retracted" in paper.flags:
        score *= 0.1

    paper.quality_score = round(score, 1)
    paper.quality_detail = {k: round(parts[k], 1) for k in parts}
    return paper
