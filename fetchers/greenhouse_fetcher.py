# -*- coding: utf-8 -*-
"""
Greenhouse 职位抓取器 (涵盖 Scale AI / Outlier, Invisible Tech, Welocalize 等头部 AI 标注公司)
"""
from fetchers.base_fetcher import BaseFetcher
from matcher import analyze_job

class GreenhouseFetcher(BaseFetcher):
    def __init__(self, board_token, company_name):
        super().__init__(name=f"Greenhouse-{company_name}")
        self.board_token = board_token
        self.company_name = company_name
        self.api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"

    def crawl(self):
        print(f"[{self.name}] 正在抓取 {self.company_name} 官方开放职位...")
        data = self.fetch_url(self.api_url)
        if not data or "jobs" not in data:
            return []

        jobs = []
        for item in data.get("jobs", []):
            title = item.get("title", "")
            job_id = f"gh_{self.board_token}_{item.get('id')}"
            url = item.get("absolute_url", "")
            location = item.get("location", {}).get("name", "Remote")
            content = self.strip_html(item.get("content", ""))
            
            raw_tags = []
            for dep in item.get("departments", []):
                raw_tags.append(dep.get("name", ""))

            analysis = analyze_job(title, content, raw_tags, location)
            
            # 过滤逻辑：只收集与 AI/标注/中文/语言/或者达到一定评分标准的岗位
            if analysis["score"] >= 20 or any(k in title.lower() for k in ["chinese", "annotator", "trainer", "ai", "specialist", "language", "data"]):
                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": self.company_name,
                    "platform": "Greenhouse",
                    "url": url,
                    "location": location,
                    "salary": "视项目按小时计薪 ($15-$45/hr)",
                    "tags": analysis["display_tags"],
                    "description": content[:500] + "..." if len(content) > 500 else content,
                    "match_score": analysis["score"],
                    "published_at": item.get("updated_at", "")[:10]
                })

        print(f"[{self.name}] 完成抓取，筛选出 {len(jobs)} 个匹配岗位。")
        return jobs
