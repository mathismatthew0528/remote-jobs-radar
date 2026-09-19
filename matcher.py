# -*- coding: utf-8 -*-
"""
远程工作爬虫系统 - 智能关键词匹配与评分引擎
"""
import re
from config import KEYWORDS_WEIGHT

def analyze_job(title, description="", raw_tags=None, location=""):
    """
    分析岗位信息，计算契合度打分，并生成精准分类标签
    """
    flat_tags = []
    if raw_tags:
        for t in raw_tags:
            if isinstance(t, list):
                flat_tags.extend([str(x) for x in t if x])
            elif t:
                flat_tags.append(str(t))

    full_text = f"{title} {' '.join(flat_tags)} {description} {location}".lower()
    
    score = 0
    matched_keywords = []
    
    # 计算权重总分
    for kw, weight in KEYWORDS_WEIGHT.items():
        pattern = r"\b" + re.escape(kw) + r"\b" if len(kw) > 3 else re.escape(kw)
        if re.search(pattern, full_text, re.IGNORECASE):
            score += weight
            matched_keywords.append(kw)
            
    # 针对岗位标题核心词加权
    lower_title = title.lower()
    if any(k in lower_title for k in ["chinese", "mandarin", "cantonese"]):
        score += 45
    if any(k in lower_title for k in ["annotation", "trainer", "evaluator", "rlhf", "tutor", "labeler"]):
        score += 35

    # 生成展示标签
    display_tags = []
    
    # 语言标签
    if any(k in full_text for k in ["chinese", "mandarin", "cantonese", "中文", "普通话", "粤语"]):
        display_tags.append("🇨🇳 中文/双语")
    elif "bilingual" in full_text:
        display_tags.append("🌐 双语")
        
    # AI 标注与训练
    if any(k in full_text for k in ["data annotation", "annotator", "annotation", "labeling"]):
        display_tags.append("🏷️ 数据标注")
    if any(k in full_text for k in ["ai trainer", "trainer", "rlhf", "prompt", "llm"]):
        display_tags.append("🤖 AI 训练师")
    if any(k in full_text for k in ["evaluator", "evaluation", "reviewer", "rater"]):
        display_tags.append("⚖️ 模型评测")
    if any(k in full_text for k in ["localization", "translator", "translation", "本地化"]):
        display_tags.append("🌍 翻译/本地化")
    if any(k in full_text for k in ["content moderator", "moderation", "audit", "审核"]):
        display_tags.append("🛡️ 内容审核")
        
    # 工作形态标签
    if any(k in full_text for k in ["part-time", "flexible", "freelance", "contract"]):
        display_tags.append("⏱️ 灵活/兼职")
    if any(k in full_text for k in ["worldwide", "anywhere", "global"]):
        display_tags.append("🌏 全球远程")
    elif "remote" in full_text:
        display_tags.append("🏠 远程可做")
        
    for rt in flat_tags[:3]:
        cleaned = str(rt).strip()
        if cleaned and cleaned not in display_tags and len(cleaned) < 20:
            display_tags.append(cleaned)

    score = min(score, 100)
    
    return {
        "score": score,
        "display_tags": list(dict.fromkeys(display_tags)),
        "matched_keywords": matched_keywords
    }
