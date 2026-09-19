# -*- coding: utf-8 -*-
"""
生成供 GitHub Pages 静态网站使用的 jobs.json 数据
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import json
from database import init_db, get_stats, get_jobs
from crawler_engine import run_crawler_sync
from config import BASE_DIR, DATA_DIR, WEB_DIR

def export_static_data():
    print("[Export] 正在执行全网爬虫抓取...")
    crawl_res = run_crawler_sync()
    
    stats = get_stats()
    jobs = get_jobs(limit=1000)
    
    data = {
        "updated_at": crawl_res.get("stats", {}).get("last_updated") or "",
        "stats": stats,
        "jobs": jobs
    }
    
    # 写入数据到 web/data/jobs.json
    web_data_dir = os.path.join(WEB_DIR, "data")
    os.makedirs(web_data_dir, exist_ok=True)
    
    output_path = os.path.join(web_data_dir, "jobs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"[Export] 静态数据生成成功: {output_path} (共 {len(jobs)} 个有效岗位)")

if __name__ == "__main__":
    export_static_data()
