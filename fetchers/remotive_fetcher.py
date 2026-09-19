# -*- coding: utf-8 -*-
"""
Remotive 远程工作平台抓取器
"""
from fetchers.base_fetcher import BaseFetcher
from matcher import analyze_job

class RemotiveFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(name="Remotive")
        self.api_url = "https://remotive.com/api/remote-jobs?limit=100"

    def crawl(self):
        print(f"[{self.name}] 正在抓取 Remotive 全球远程工作...")
        data = self.fetch_url(self.api_url)
        if not data or "jobs" not in data:
            return []

        jobs = []
        for item in data.get("jobs", []):
            title = item.get("title", "")
            job_id = f"remotive_{item.get('id')}"
            url = item.get("url", "")
            company = item.get("company_name", "Remote Co")
            location = item.get("candidate_required_location", "Worldwide")
            salary = item.get("salary", "")
            raw_tags = item.get("tags", []) + [item.get("category", "")]
            content = self.strip_html(item.get("description", ""))

            analysis = analyze_job(title, content, raw_tags, location)
            
            # 保留有匹配度的岗位
            if analysis["score"] >= 20:
                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "platform": "Remotive",
                    "url": url,
                    "location": location,
                    "salary": salary or "面议 / 灵活时薪",
                    "tags": analysis["display_tags"],
                    "description": content[:500] + "..." if len(content) > 500 else content,
                    "match_score": analysis["score"],
                    "published_at": item.get("publication_date", "")[:10]
                })

        print(f"[{self.name}] 完成抓取，筛选出 {len(jobs)} 个匹配岗位。")
        return jobs
