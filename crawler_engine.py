# -*- coding: utf-8 -*-
"""
远程工作爬虫系统 - 多源并发爬虫调度引擎 (支持实时进度追踪)
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
import concurrent.futures
from database import init_db, save_job, get_stats
from fetchers.greenhouse_fetcher import GreenhouseFetcher
from fetchers.remotive_fetcher import RemotiveFetcher
from fetchers.jobicy_fetcher import JobicyFetcher
from fetchers.remoteok_fetcher import RemoteOKFetcher

# 全局爬虫进度状态
crawler_progress = {
    "is_crawling": False,
    "percent": 0,
    "status_text": "就绪",
    "total_sources": 5,
    "finished_sources": 0,
    "sources_detail": [],
    "total_fetched": 0,
    "new_inserted": 0,
    "last_finished_at": None
}

def get_crawler_progress():
    return crawler_progress.copy()

def get_all_fetchers():
    return [
        GreenhouseFetcher(board_token="scaleai", company_name="Scale AI (Outlier)"),
        GreenhouseFetcher(board_token="invisibletech", company_name="Invisible Technologies"),
        RemotiveFetcher(),
        JobicyFetcher(),
        RemoteOKFetcher()
    ]

def run_crawler_sync():
    """并发执行所有爬虫任务并入库，实时同步进度"""
    global crawler_progress
    init_db()
    fetchers = get_all_fetchers()
    
    total_sources = len(fetchers)
    crawler_progress.update({
        "is_crawling": True,
        "percent": 5,
        "status_text": "正在初始化网络连接与多源调度...",
        "total_sources": total_sources,
        "finished_sources": 0,
        "sources_detail": [],
        "total_fetched": 0,
        "new_inserted": 0
    })

    print("=" * 60)
    print("[Crawler] 启动多源远程岗位爬虫引擎...")
    print("=" * 60)

    total_fetched = 0
    new_inserted = 0

    def fetch_worker(fetcher):
        try:
            crawler_progress["status_text"] = f"正在连接抓取: {fetcher.name}..."
            jobs = fetcher.crawl()
            return fetcher.name, jobs, None
        except Exception as e:
            print(f"[Worker Error] {fetcher.name}: {e}")
            return fetcher.name, [], str(e)

    # 并发抓取
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_fetcher = {executor.submit(fetch_worker, f): f for f in fetchers}
        for future in concurrent.futures.as_completed(future_to_fetcher):
            name, jobs, err = future.result()
            count = len(jobs)
            total_fetched += count
            
            # 入库保存
            for job in jobs:
                if save_job(job):
                    new_inserted += 1

            crawler_progress["finished_sources"] += 1
            crawler_progress["total_fetched"] = total_fetched
            crawler_progress["new_inserted"] = new_inserted
            
            # 计算百分比: 10% ~ 90%
            ratio = crawler_progress["finished_sources"] / total_sources
            crawler_progress["percent"] = int(10 + ratio * 80)
            
            status_desc = f"已完成 {name} (匹配 {count} 个岗位)" if not err else f"{name} 连接异常"
            crawler_progress["sources_detail"].append({
                "name": name,
                "count": count,
                "error": err
            })
            crawler_progress["status_text"] = status_desc

    crawler_progress["percent"] = 95
    crawler_progress["status_text"] = "正在整理索引、计算中文与双语岗位评分..."
    time.sleep(0.5)

    stats = get_stats()
    crawler_progress.update({
        "is_crawling": False,
        "percent": 100,
        "status_text": f"扫描完成！本次共采集 {total_fetched} 个职位，新增/更新 {new_inserted} 个。",
        "last_finished_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    print("=" * 60)
    print(f"[Crawler] 抓取完成！共收集匹配岗位: {total_fetched} 个，本次新增: {new_inserted} 个")
    print(f"[Crawler] 当前数据库总计: {stats['total']} 个有效岗位")
    print("=" * 60)

    return {
        "total_fetched": total_fetched,
        "new_inserted": new_inserted,
        "stats": stats
    }

if __name__ == "__main__":
    run_crawler_sync()
