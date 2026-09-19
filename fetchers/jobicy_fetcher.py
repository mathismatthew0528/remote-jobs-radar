# -*- coding: utf-8 -*-
"""
Jobicy 远程工作平台抓取器
"""
from fetchers.base_fetcher import BaseFetcher
from matcher import analyze_job

class JobicyFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(name="Jobicy")
        self.api_url = "https://jobicy.com/api/v2/remote-jobs?count=50"

    def crawl(self):
        print(f"[{self.name}] 正在抓取 Jobicy 远程工作...")
        data = self.fetch_url(self.api_url)
        if not data or "jobs" not in data:
            return []

        jobs = []
        for item in data.get("jobs", []):
            title = item.get("jobTitle", "")
            job_id = f"jobicy_{item.get('id')}"
            url = item.get("url", "")
            company = item.get("companyName", "Jobicy Partner")
            location = item.get("jobGeo", "Anywhere")
            salary = f"{item.get('annualSalaryMin', '')}-{item.get('annualSalaryMax', '')} {item.get('salaryCurrency', '')}".strip("- ")
            raw_tags = [item.get("jobCategory", ""), item.get("jobType", "")]
            content = self.strip_html(item.get("jobDescription", ""))

            analysis = analyze_job(title, content, raw_tags, location)
            
            if analysis["score"] >= 20:
                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "platform": "Jobicy",
                    "url": url,
                    "location": location,
                    "salary": salary or "面议 / 远程月薪",
                    "tags": analysis["display_tags"],
                    "description": content[:500] + "..." if len(content) > 500 else content,
                    "match_score": analysis["score"],
                    "published_at": item.get("pubDate", "")[:10]
                })

        print(f"[{self.name}] 完成抓取，筛选出 {len(jobs)} 个匹配岗位。")
        return jobs
