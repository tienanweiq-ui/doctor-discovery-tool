# -*- coding: utf-8 -*-
"""项目配置：评分权重、关键词、证据等级映射。可按需调整。"""

# ---- 质量评分各维度权重（合计 1.0）----
QUALITY_WEIGHTS = {
    "journal": 0.35,     # 期刊层级（IF / 分区）
    "evidence": 0.30,    # 证据等级（研究设计）
    "citation": 0.20,    # 影响力（被引，需 iCite）
    "authorship": 0.15,  # 作者贡献度（第一/通讯）
}

# ---- 临床研究的“阳性”出版物类型 ----
CLINICAL_PUB_TYPES = {
    "randomized controlled trial", "controlled clinical trial", "clinical trial",
    "clinical trial, phase i", "clinical trial, phase ii", "clinical trial, phase iii",
    "clinical trial, phase iv", "pragmatic clinical trial", "observational study",
    "multicenter study", "comparative study", "clinical study", "case reports",
    "meta-analysis", "systematic review",
}

# 明确排除的非临床类型（基础/方法/评论等）
EXCLUDE_PUB_TYPES = {
    "editorial", "comment", "letter", "news", "biography", "retraction of publication",
}

# ---- 研究设计 -> 证据等级（1 最低，5 最高）----
DESIGN_EVIDENCE = {
    "Systematic Review / Meta-analysis": 5,
    "RCT": 5,
    "Cohort": 4,
    "Case-Control": 3,
    "Cross-sectional / Observational": 3,
    "Case Series": 2,
    "Case Report": 1,
    "Other Clinical": 2,
}

# ---- 研究设计识别关键词（标题/摘要/类型）----
DESIGN_RULES = [
    ("Systematic Review / Meta-analysis", ["meta-analysis", "systematic review"]),
    ("RCT", ["randomized controlled trial", "randomised controlled trial", "randomized", "randomised"]),
    ("Cohort", ["cohort", "prospective cohort", "retrospective cohort", "longitudinal"]),
    ("Case-Control", ["case-control", "case control"]),
    ("Case Series", ["case series"]),
    ("Case Report", ["case report", "a case of"]),
    ("Cross-sectional / Observational", ["cross-sectional", "observational", "survey", "registry"]),
]

# ---- 临床医生 vs 纯科研：单位关键词 ----
CLINICAL_AFFIL_KEYWORDS = [
    "hospital", "medical center", "medical centre", "clinic", "department of",
    "医院", "临床", "科",  # 中文单位
]
CLINICAL_DEPT_HINTS = [
    "internal medicine", "surgery", "cardiology", "oncology", "neurology",
    "gastroenterology", "hepatology", "pediatrics", "obstetrics", "gynecology",
    "orthopedics", "dermatology", "ophthalmology", "urology", "respiratory",
    "infectious disease", "endocrinology", "nephrology", "rheumatology",
]
RESEARCH_ONLY_KEYWORDS = [
    "institute of", "laboratory", "school of public health", "college of",
    "center for research", "department of bioinformatics", "academy of sciences",
    "研究所", "实验室", "公共卫生学院",
]

# ---- NCBI E-utilities ----
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ICITE_BASE = "https://icite.od.nih.gov/api/pubs"
# 调用 NCBI 时附带（礼仪要求）。换成你自己的邮箱；如有 API key 可提升频率上限。
NCBI_TOOL = "doctor-discovery"
NCBI_EMAIL = "tienan@sjtu.edu.cn"
