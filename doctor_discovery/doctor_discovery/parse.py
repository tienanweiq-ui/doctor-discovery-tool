# -*- coding: utf-8 -*-
"""把 PubMed efetch 返回的 XML 解析为 Paper 对象。"""
import xml.etree.ElementTree as ET
from typing import List

from .models import Paper, Author


def _text(node, path, default=""):
    el = node.find(path)
    return el.text.strip() if el is not None and el.text else default


def parse_articles(xml_text: str) -> List[Paper]:
    root = ET.fromstring(xml_text)
    papers: List[Paper] = []

    for art in root.findall(".//PubmedArticle"):
        mc = art.find("./MedlineCitation")
        if mc is None:
            continue
        pmid = _text(mc, "./PMID")
        article = mc.find("./Article")
        if article is None:
            continue

        title = _text(article, "./ArticleTitle")
        abstract = " ".join(
            (e.text or "") for e in article.findall("./Abstract/AbstractText")
        ).strip()
        journal_iso = _text(article, "./Journal/ISOAbbreviation")
        journal_title = _text(article, "./Journal/Title")

        year_txt = _text(article, "./Journal/JournalIssue/PubDate/Year")
        year = int(year_txt) if year_txt.isdigit() else None

        doi = ""
        for eid in article.findall("./ELocationID"):
            if eid.get("EIdType") == "doi" and eid.text:
                doi = eid.text.strip()
                break

        pub_types = [pt.text.strip() for pt in article.findall("./PublicationTypeList/PublicationType") if pt.text]
        mesh = [m.text.strip() for m in mc.findall("./MeshHeadingList/MeshHeading/DescriptorName") if m.text]

        authors: List[Author] = []
        for a in article.findall("./AuthorList/Author"):
            ln = _text(a, "./LastName")
            fn = _text(a, "./ForeName")
            aff = _text(a, "./AffiliationInfo/Affiliation")
            if ln or fn:
                authors.append(Author(last_name=ln, fore_name=fn, affiliation=aff))

        papers.append(Paper(
            pmid=pmid, title=title, abstract=abstract,
            journal_iso=journal_iso, journal_title=journal_title, year=year,
            doi=doi, pub_types=pub_types, mesh=mesh, authors=authors,
        ))
    return papers
