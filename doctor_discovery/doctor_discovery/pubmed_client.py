# -*- coding: utf-8 -*-
"""PubMed 数据采集：基于 NCBI E-utilities 的 esearch + efetch，以及可选的 iCite 被引。

注意：需要能访问 eutils.ncbi.nlm.nih.gov（在你本机运行即可）。
"""
import time
from typing import List, Dict, Optional

import requests

from . import config


def _params(extra: dict) -> dict:
    p = {"tool": config.NCBI_TOOL, "email": config.NCBI_EMAIL}
    p.update(extra)
    return p


def esearch_pmids(name: str, affiliation: str = "", retmax: int = 100,
                  api_key: Optional[str] = None) -> List[str]:
    """按作者姓名（+ 单位）检索 PMID 列表。"""
    term = f"{name}[Author]"
    if affiliation:
        term += f" AND ({affiliation}[Affiliation])"
    extra = {"db": "pubmed", "term": term, "retmax": str(retmax), "retmode": "json"}
    if api_key:
        extra["api_key"] = api_key
    r = requests.get(f"{config.EUTILS_BASE}/esearch.fcgi", params=_params(extra), timeout=30)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])


def efetch_xml(pmids: List[str], api_key: Optional[str] = None) -> str:
    """按 PMID 批量抓取文章 XML。"""
    if not pmids:
        return "<PubmedArticleSet></PubmedArticleSet>"
    out = []
    # NCBI 建议每批不超过 ~200 个 id
    for i in range(0, len(pmids), 150):
        batch = pmids[i:i + 150]
        extra = {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"}
        if api_key:
            extra["api_key"] = api_key
        r = requests.get(f"{config.EUTILS_BASE}/efetch.fcgi", params=_params(extra), timeout=60)
        r.raise_for_status()
        out.append(r.text)
        time.sleep(0.34 if not api_key else 0.1)  # 遵守频率限制
    # 合并多批：去掉重复的根标签
    if len(out) == 1:
        return out[0]
    bodies = []
    for x in out:
        s = x.find("<PubmedArticleSet>")
        e = x.rfind("</PubmedArticleSet>")
        bodies.append(x[s + len("<PubmedArticleSet>"):e] if s != -1 and e != -1 else x)
    return "<PubmedArticleSet>" + "".join(bodies) + "</PubmedArticleSet>"


def fetch_citations(pmids: List[str]) -> Dict[str, int]:
    """通过 NIH iCite 获取被引次数（可选）。失败则返回空。"""
    if not pmids:
        return {}
    result: Dict[str, int] = {}
    try:
        for i in range(0, len(pmids), 100):
            batch = pmids[i:i + 100]
            r = requests.get(config.ICITE_BASE, params={"pmids": ",".join(batch)}, timeout=30)
            r.raise_for_status()
            for rec in r.json().get("data", []):
                pmid = str(rec.get("pmid", ""))
                result[pmid] = int(rec.get("citation_count", 0) or 0)
            time.sleep(0.2)
    except Exception:
        pass
    return result
