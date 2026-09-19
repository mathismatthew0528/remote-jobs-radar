# -*- coding: utf-8 -*-
"""
远程工作爬虫系统 - 全局配置
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
WEB_DIR = os.path.join(BASE_DIR, "web")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "remote_jobs.db")
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5888

# 关键词权重
KEYWORDS_WEIGHT = {
    # 核心目标：中文/双语相关 (权重最高)
    "chinese": 50,
    "mandarin": 50,
    "cantonese": 45,
    "bilingual": 40,
    "localization": 30,
    "translator": 30,
    "translation": 30,
    
    # 核心目标：AI 训练 / 数据标注 / 评测
    "data annotation": 40,
    "annotation": 35,
    "annotator": 35,
    "ai trainer": 40,
    "rlhf": 40,
    "prompt engineer": 35,
    "prompt engineering": 35,
    "model evaluation": 35,
    "evaluator": 30,
    "llm": 25,
    "ai tutor": 35,
    "language expert": 35,
    "data labeling": 35,
    
    # 通用技术与远程优势加分
    "remote": 10,
    "worldwide": 20,
    "anywhere": 20,
    "work from home": 15,
    "part-time": 15,
    "flexible": 15,
    "contractor": 15,
    "freelance": 15
}

# 监控源配置
TARGET_BOARDS = [
    {
        "name": "Scale AI (Outlier 母公司)",
        "platform": "Greenhouse",
        "url": "https://boards-api.greenhouse.io/v1/boards/scaleai/jobs",
        "company": "Scale AI"
    },
    {
        "name": "Invisible Technologies (AI 训练与标注)",
        "platform": "Greenhouse",
        "url": "https://boards-api.greenhouse.io/v1/boards/invisibletechnologies/jobs",
        "company": "Invisible Technologies"
    },
    {
        "name": "Remotive API",
        "platform": "Remotive",
        "url": "https://remotive.com/api/remote-jobs",
        "company": "Multiple"
    },
    {
        "name": "Jobicy API",
        "platform": "Jobicy",
        "url": "https://jobicy.com/api/v2/remote-jobs?count=50",
        "company": "Multiple"
    },
    {
        "name": "RemoteOK API",
        "platform": "RemoteOK",
        "url": "https://remoteok.com/api",
        "company": "Multiple"
    }
]

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
}
