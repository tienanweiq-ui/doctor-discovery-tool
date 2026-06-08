# -*- coding: utf-8 -*-
"""
医生临床研究画像 · 在线工具
Online tool for doctor research profiling
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# 导入 doctor_discovery 核心模块
from doctor_discovery import pubmed_client, parse, classify, quality, identity, profile

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
_SAMPLE = os.path.join(os.path.dirname(__file__), "doctor_discovery", "data", "sample_efetch.xml")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search_doctor():
    """
    API 端点：搜索医生研究画像

    请求格式:
    {
        "name": "Zhang Wei",
        "affiliation": "Shanghai Sixth People's Hospital",
        "offline": false,
        "max": 50
    }

    响应格式:
    {
        "success": true,
        "data": {
            "name": "Zhang Wei",
            "affiliation_query": "Shanghai Sixth People's Hospital",
            "total_matched": 32,
            "papers": [...],
            "summary": {...}
        },
        "error": null
    }
    """
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        affiliation = data.get('affiliation', '').strip()
        offline = data.get('offline', False)
        retmax = data.get('max', 50)

        if not name:
            return jsonify({
                'success': False,
                'error': '医生名字不能为空 / Doctor name is required'
            }), 400

        # 1) 采集论文
        if offline:
            with open(_SAMPLE, encoding="utf-8") as f:
                xml_text = f.read()
            pmids_for_cite = []
        else:
            try:
                pmids = pubmed_client.esearch_pmids(name, affiliation, retmax=retmax)
                if not pmids:
                    return jsonify({
                        'success': False,
                        'error': f'未找到匹配的论文 / No papers found for {name}'
                    }), 404
                xml_text = pubmed_client.efetch_xml(pmids)
                pmids_for_cite = pmids
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'PubMed 查询失败: {str(e)}'
                }), 500

        # 2) 解析论文
        papers = parse.parse_articles(xml_text)

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

        # 4) 质量评分
        tiers = quality.load_journal_tiers()
        for p in matched:
            quality.score_paper(p, tiers, None)

        # 5) 构建报告
        prof = profile.build_profile(name, affiliation, matched)
        conf, signals = identity.clinical_doctor_signal(affils_for_role)
        prof.clinical_role_confidence = conf
        prof.role_signals = signals

        # 6) 格式化输出（包含摘要和期刊信息）
        papers_data = []
        for paper in matched:
            papers_data.append({
                'pmid': paper.pmid,
                'title': paper.title,
                'abstract': paper.abstract[:500] if paper.abstract else 'N/A',  # 摘要前 500 字
                'journal': paper.journal_title,
                'journal_iso': paper.journal_iso,
                'year': paper.year,
                'doi': paper.doi,
                'authors': [f"{a.full} ({a.affiliation})" for a in paper.authors[:3]],  # 前 3 位作者
                'study_design': paper.study_design,
                'evidence_level': paper.evidence_level,
                'quality_score': round(paper.quality_score, 1),
                'target_author_pos': paper.target_author_pos,
                'is_clinical': paper.is_clinical,
            })

        return jsonify({
            'success': True,
            'data': {
                'name': prof.name,
                'affiliation': prof.affiliation_query,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_matched': prof.total_matched,
                'clinical_papers': len([p for p in matched if p.is_clinical]),
                'clinical_role_confidence': round(prof.clinical_role_confidence, 2),
                'papers': papers_data,
                'top_papers': papers_data[:10],  # 前 10 篇高质量论文
                'summary': {
                    'total': len(matched),
                    'clinical': len([p for p in matched if p.is_clinical]),
                    'average_quality': round(sum(p.quality_score for p in matched) / len(matched), 1) if matched else 0,
                    'top_journal': max([p.journal_title for p in matched], key=[p.journal_title for p in matched].count) if matched else 'N/A',
                }
            }
        }), 200

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'Doctor Discovery API is running'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
