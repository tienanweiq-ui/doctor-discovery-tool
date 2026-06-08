# -*- coding: utf-8 -*-
"""临床研究识别：判断是否临床研究，识别研究设计与证据等级。"""
from .models import Paper
from . import config


def _detect_design(paper: Paper) -> str:
    haystack = " ".join([paper.title, paper.abstract] + paper.pub_types).lower()
    # 出版物类型优先
    pts = {p.lower() for p in paper.pub_types}
    if "meta-analysis" in pts or "systematic review" in pts:
        return "Systematic Review / Meta-analysis"
    if any("randomized controlled trial" == p or "randomised controlled trial" == p for p in pts):
        return "RCT"
    if "case reports" in pts:
        return "Case Report"
    # 再用关键词
    for design, keys in config.DESIGN_RULES:
        if any(k in haystack for k in keys):
            return design
    if "observational study" in pts or "multicenter study" in pts or "comparative study" in pts:
        return "Cross-sectional / Observational"
    return "Other Clinical"


def classify(paper: Paper) -> Paper:
    pts = {p.lower() for p in paper.pub_types}
    mesh = {m.lower() for m in paper.mesh}

    # 撤稿 / 预警标记
    if "retracted publication" in pts:
        paper.flags.append("Retracted")

    # 明确排除类型
    if pts & config.EXCLUDE_PUB_TYPES and not (pts & config.CLINICAL_PUB_TYPES):
        paper.is_clinical = False
        return paper

    # 涉及人类受试者？（有 Animals 而无 Humans 视为基础/动物研究）
    has_humans = "humans" in mesh
    has_animals = "animals" in mesh
    if has_animals and not has_humans:
        paper.is_clinical = False
        return paper

    # 出版物类型命中临床类型，或（有人类 MeSH 且非纯基础）
    type_hit = bool(pts & config.CLINICAL_PUB_TYPES)
    clinical_kw = any(k in (paper.title + " " + paper.abstract).lower()
                      for k in ["patient", "patients", "clinical", "trial", "cohort"])

    paper.is_clinical = type_hit or (has_humans and clinical_kw)
    if paper.is_clinical:
        paper.study_design = _detect_design(paper)
        paper.evidence_level = config.DESIGN_EVIDENCE.get(paper.study_design, 2)
    return paper
