# -*- coding: utf-8 -*-
"""
RemoteOK 远程工作平台抓取器
"""
from fetchers.base_fetcher import BaseFetcher
from matcher import analyze_job

class RemoteOKFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(name="RemoteOK")
        self.api_url = "https://remoteok.com/api"

    def crawl(self):
        print(f"[{self.name}] 正在抓取 RemoteOK 职位...")
        data = self.fetch_url(self.api_url)
        if not data or not isinstance(data, list):
            return []

        jobs = []
        for item in data:
            if not isinstance(item, dict) or not item.get("id"):
                continue
                
            title = item.get("position", "")
            job_id = f"remoteok_{item.get('id')}"
            url = item.get("url", "")
            company = item.get("company", "Remote Company")
            location = item.get("location", "Worldwide")
            salary = f"${item.get('salary_min', '')} - ${item.get('salary_max', '')}".strip("$ -")
            raw_tags = item.get("tags", [])
            content = self.strip_html(item.get("description", ""))

            analysis = analyze_job(title, content, raw_tags, location)
            
            if analysis["score"] >= 20:
                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "platform": "RemoteOK",
                    "url": url,
                    "location": location,
                    "salary": salary or "面议",
                    "tags": analysis["display_tags"],
                    "description": content[:500] + "..." if len(content) > 500 else content,
                    "match_score": analysis["score"],
                    "published_at": item.get("date", "")[:10]
                })

        print(f"[{self.name}] 完成抓取，筛选出 {len(jobs)} 个匹配岗位。")
        return jobs
