# -*- coding: utf-8 -*-
"""
远程工作爬虫系统 - 本地 Web 控制台服务 (支持实时进度查询接口)
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
import csv
import io
import threading
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import SERVER_HOST, SERVER_PORT, BASE_DIR
from database import get_jobs, get_stats, toggle_star, toggle_applied, hide_job
from crawler_engine import run_crawler_sync, get_crawler_progress

class CrawlerHTTPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filepath, content_type="text/html; charset=utf-8"):
        if not os.path.exists(filepath):
            self.send_error(404, "File Not Found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # 首页
        if path == "/" or path == "/index.html":
            html_path = os.path.join(BASE_DIR, "web", "index.html")
            self._send_file(html_path, "text/html; charset=utf-8")
            return

        # 爬虫实时进度接口
        if path == "/api/progress":
            progress = get_crawler_progress()
            self._send_json({"code": 0, "data": progress})
            return

        # 统计数据接口
        if path == "/api/stats":
            progress = get_crawler_progress()
            stats = get_stats()
            stats["is_crawling"] = progress.get("is_crawling", False)
            self._send_json({"code": 0, "data": stats})
            return

        # 职位列表接口
        if path == "/api/jobs":
            search = qs.get("search", [""])[0]
            tag = qs.get("tag", [""])[0]
            min_score = int(qs.get("min_score", [0])[0])
            only_starred = qs.get("starred", ["0"])[0] == "1"
            only_applied = qs.get("applied", ["0"])[0] == "1"
            limit = int(qs.get("limit", [100])[0])
            offset = int(qs.get("offset", [0])[0])
            
            jobs = get_jobs(
                search=search,
                tag=tag,
                min_score=min_score,
                only_starred=only_starred,
                only_applied=only_applied,
                limit=limit,
                offset=offset
            )
            self._send_json({"code": 0, "data": jobs})
            return

        # 导出 CSV 接口
        if path == "/api/export":
            jobs = get_jobs(limit=1000)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "职位名称", "公司", "平台", "匹配度", "薪资", "地点", "标签", "申请链接", "更新日期", "已投递"])
            for j in jobs:
                tags_str = ", ".join(j.get("tags", []))
                applied_str = "是" if j.get("is_applied") else "否"
                writer.writerow([
                    j.get("job_id"),
                    j.get("title"),
                    j.get("company"),
                    j.get("platform"),
                    f"{j.get('match_score')}分",
                    j.get("salary"),
                    j.get("location"),
                    tags_str,
                    j.get("url"),
                    j.get("published_at"),
                    applied_str
                ])
            csv_data = "\ufeff" + output.getvalue()
            csv_bytes = csv_data.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=remote_jobs_export.csv")
            self.send_header("Content-Length", str(len(csv_bytes)))
            self.end_headers()
            self.wfile.write(csv_bytes)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(post_data)
        except:
            payload = {}

        # 触发爬虫刷新
        if path == "/api/scan":
            progress = get_crawler_progress()
            if progress.get("is_crawling", False):
                self._send_json({"code": 1, "message": "爬虫正在运行中，请查看进度条..."})
                return

            threading.Thread(target=run_crawler_sync, daemon=True).start()
            self._send_json({"code": 0, "message": "全网爬虫已在后台启动！"})
            return

        # 收藏切换
        if path == "/api/job/toggle_star":
            job_id = payload.get("job_id")
            if not job_id:
                self._send_json({"code": 1, "message": "缺少 job_id"}, 400)
                return
            new_state = toggle_star(job_id)
            self._send_json({"code": 0, "is_starred": new_state})
            return

        # 已投递切换
        if path == "/api/job/toggle_applied":
            job_id = payload.get("job_id")
            if not job_id:
                self._send_json({"code": 1, "message": "缺少 job_id"}, 400)
                return
            new_state = toggle_applied(job_id)
            self._send_json({"code": 0, "is_applied": new_state})
            return

        # 忽略职位
        if path == "/api/job/hide":
            job_id = payload.get("job_id")
            if not job_id:
                self._send_json({"code": 1, "message": "缺少 job_id"}, 400)
                return
            hide_job(job_id)
            self._send_json({"code": 0, "success": True})
            return

        self.send_error(404, "Not Found")

def start_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, CrawlerHTTPHandler)
    print(f"[*] 远程工作监控系统控制台已启动: http://{SERVER_HOST}:{SERVER_PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] 服务已停止。")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
