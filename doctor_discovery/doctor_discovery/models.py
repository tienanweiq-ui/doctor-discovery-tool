# -*- coding: utf-8 -*-
"""数据模型：论文、作者、医生画像。"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Author:
    last_name: str = ""
    fore_name: str = ""
    affiliation: str = ""

    @property
    def full(self) -> str:
        return f"{self.fore_name} {self.last_name}".strip()


@dataclass
class Paper:
    pmid: str
    title: str = ""
    abstract: str = ""
    journal_iso: str = ""
    journal_title: str = ""
    year: Optional[int] = None
    doi: str = ""
    pub_types: List[str] = field(default_factory=list)
    mesh: List[str] = field(default_factory=list)
    authors: List[Author] = field(default_factory=list)

    # 分析结果（流水线逐步填充）
    is_clinical: bool = False
    study_design: str = ""        # 如 RCT / Cohort / Case Report
    evidence_level: int = 0       # 1-5，越高证据等级越强
    target_author_pos: str = ""   # first / last / middle / none
    quality_score: float = 0.0    # 0-100
    quality_detail: Dict[str, float] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)  # 如 Retracted / Predatory


@dataclass
class DoctorProfile:
    name: str
    affiliation_query: str
    generated_at: str = ""
    total_matched: int = 0
    clinical_papers: List[Paper] = field(default_factory=list)
    excluded_papers: List[Paper] = field(default_factory=list)
    clinical_role_confidence: float = 0.0  # 是否坐诊临床医生的启发式置信度 0-1
    role_signals: List[str] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)
