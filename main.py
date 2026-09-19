# -*- coding: utf-8 -*-
"""
远程工作监控与爬虫系统 - 主程序入口
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import argparse
import webbrowser
import threading
import time
from database import init_db, get_stats
from crawler_engine import run_crawler_sync
from server import start_server
from config import SERVER_HOST, SERVER_PORT

def scheduled_crawler(interval_hours=2):
    """后台定时自动抓取任务"""
    while True:
        time.sleep(interval_hours * 3600)
        print("\n[Scheduler] 触发周期性全网岗位抓取...")
        try:
            run_crawler_sync()
        except Exception as e:
            print(f"[Scheduler Error] {e}")

def main():
    parser = argparse.ArgumentParser(description="全球远程 AI 训练 / 数据标注 / 中文双语岗位监控系统")
    parser.add_argument("--scan", action="store_true", help="立即执行一次全网岗位抓取并入库")
    parser.add_argument("--serve", action="store_true", help="启动本地 Web 可视化控制台")
    parser.add_argument("--daemon", action="store_true", help="启动服务并启用后台定时周期抓取")
    args = parser.parse_args()

    init_db()
    stats = get_stats()

    if args.scan:
        run_crawler_sync()
        return

    # 默认模式：如果数据库为空则先抓取一次，然后启动服务并自动打开浏览器
    if stats.get("total", 0) == 0:
        print("[System] 本地数据库为空，正在进行初次全网岗位抓取...")
        run_crawler_sync()

    if args.daemon:
        threading.Thread(target=scheduled_crawler, args=(2,), daemon=True).start()
        print("[System] 后台定时抓取任务已启用 (每 2 小时轮询一次最新职位)。")

    # 自动在系统默认浏览器中打开控制台
    dashboard_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
    print("=" * 60)
    print(f"✨ 远程工作雷达系统已就绪！")
    print(f"🌐 访问控制台: {dashboard_url}")
    print("=" * 60)

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(dashboard_url)

    threading.Thread(target=open_browser, daemon=True).start()
    start_server()

if __name__ == "__main__":
    main()
