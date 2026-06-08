# -*- coding: utf-8 -*-
"""作者匹配与“是否坐诊临床医生”的启发式判定。

MVP 阶段用单位关键词做启发式；正式版应叠加医师执业注册核验与本人认领。
"""
from typing import List, Tuple

from .models import Paper, Author
from . import config


def _norm(s: str) -> str:
    return " ".join(s.lower().replace(".", " ").replace(",", " ").split())


def match_author(paper: Paper, name: str, affiliation: str = "") -> Tuple[bool, str, Author]:
    """在论文作者中定位目标医生，返回 (是否命中, 位置, 作者对象)。

    位置：first / last / middle。
    名字匹配较宽松（姓 + 名首），单位用于消歧。
    """
    target = _norm(name)
    target_tokens = set(target.split())
    aff_q = _norm(affiliation)

    n = len(paper.authors)
    for idx, a in enumerate(paper.authors):
        full = _norm(a.full)
        tokens = set(full.split())
        # 名字：要求姓氏匹配，且有 token 重叠
        name_ok = target_tokens and target_tokens.issubset(tokens | {t[0] for t in tokens})
        name_ok = name_ok or bool(target_tokens & tokens) and _norm(a.last_name) in target
        if not name_ok:
            # 退一步：姓氏包含
            if _norm(a.last_name) and _norm(a.last_name) in target:
                name_ok = True
        if not name_ok:
            continue
        # 单位消歧（若提供）
        if aff_q:
            key = aff_q.split()[0] if aff_q else ""
            if key and key not in _norm(a.affiliation) and aff_q not in _norm(a.affiliation):
                # 单位不符，跳过该作者（可能是同名他人）
                continue
        pos = "first" if idx == 0 else ("last" if idx == n - 1 and n > 1 else "middle")
        return True, pos, a
    return False, "none", Author()


def clinical_doctor_signal(affiliations: List[str]) -> Tuple[float, List[str]]:
    """根据该医生在各论文中的单位，启发式判断“坐诊临床医生”置信度 (0-1)。"""
    signals = []
    score = 0.0
    joined = " ".join(_norm(a) for a in affiliations if a)

    if any(k in joined for k in [_norm(x) for x in config.CLINICAL_AFFIL_KEYWORDS]):
        score += 0.5
        signals.append("单位含医院/临床科室关键词")
    if any(k in joined for k in config.CLINICAL_DEPT_HINTS):
        score += 0.3
        signals.append("出现具体临床科室")
    if any(k in joined for k in [_norm(x) for x in config.RESEARCH_ONLY_KEYWORDS]):
        score -= 0.3
        signals.append("出现纯科研机构关键词（需排查是否非坐诊）")

    score = max(0.0, min(1.0, score))
    if not signals:
        signals.append("单位信息不足，无法判断")
    return round(score, 2), signals
