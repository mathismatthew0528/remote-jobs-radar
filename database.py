# -*- coding: utf-8 -*-
"""
远程工作爬虫系统 - 数据库模块 (SQLite)
"""
import sqlite3
import json
import os
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        company TEXT,
        platform TEXT,
        url TEXT NOT NULL,
        location TEXT,
        salary TEXT,
        tags TEXT,
        description TEXT,
        match_score INTEGER DEFAULT 0,
        published_at TEXT,
        is_starred INTEGER DEFAULT 0,
        is_applied INTEGER DEFAULT 0,
        is_hidden INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(match_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_hidden ON jobs(is_hidden);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_published ON jobs(published_at);")
    conn.commit()
    conn.close()

def save_job(job):
    """
    保存或更新职位数据
    返回: True (新插入), False (已存在或更新)
    """
    conn = get_connection()
    cursor = conn.cursor()
    tags_json = json.dumps(job.get("tags", []), ensure_ascii=False) if isinstance(job.get("tags"), list) else job.get("tags", "[]")
    
    try:
        cursor.execute("""
        INSERT INTO jobs (job_id, title, company, platform, url, location, salary, tags, description, match_score, published_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            title = excluded.title,
            company = excluded.company,
            platform = excluded.platform,
            url = excluded.url,
            location = excluded.location,
            salary = excluded.salary,
            tags = excluded.tags,
            match_score = excluded.match_score,
            published_at = excluded.published_at
        """, (
            job["job_id"],
            job["title"],
            job.get("company", "Unknown"),
            job.get("platform", "General"),
            job["url"],
            job.get("location", "Remote"),
            job.get("salary", ""),
            tags_json,
            job.get("description", ""),
            int(job.get("match_score", 0)),
            job.get("published_at", "")
        ))
        inserted = cursor.rowcount > 0
        conn.commit()
        return inserted
    except Exception as e:
        print(f"[DB Error] {e}")
        return False
    finally:
        conn.close()

def get_jobs(search="", tag="", min_score=0, only_starred=False, only_applied=False, show_hidden=False, limit=50, offset=0):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = ["SELECT * FROM jobs WHERE 1=1"]
    params = []
    
    if not show_hidden:
        query.append("AND is_hidden = 0")
        
    if min_score > 0:
        query.append("AND match_score >= ?")
        params.append(min_score)
        
    if only_starred:
        query.append("AND is_starred = 1")
        
    if only_applied:
        query.append("AND is_applied = 1")
        
    if tag:
        query.append("AND tags LIKE ?")
        params.append(f"%{tag}%")
        
    if search:
        query.append("AND (title LIKE ? OR company LIKE ? OR description LIKE ?)")
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
        
    query.append("ORDER BY match_score DESC, published_at DESC, id DESC LIMIT ? OFFSET ?")
    params.extend([limit, offset])
    
    cursor.execute(" ".join(query), params)
    rows = [dict(row) for row in cursor.fetchall()]
    
    # 转换 tags JSON
    for r in rows:
        try:
            r["tags"] = json.loads(r["tags"])
        except:
            r["tags"] = []
            
    conn.close()
    return rows

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_hidden = 0")
    stats["total"] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_hidden = 0 AND match_score >= 40")
    stats["high_match"] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_hidden = 0 AND (tags LIKE '%中文%' OR tags LIKE '%Chinese%' OR tags LIKE '%双语%')")
    stats["chinese"] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_starred = 1")
    stats["starred"] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_applied = 1")
    stats["applied"] = cursor.fetchone()[0]
    
    # 统计来源分布
    cursor.execute("SELECT platform, COUNT(*) as cnt FROM jobs WHERE is_hidden = 0 GROUP BY platform ORDER BY cnt DESC")
    stats["platforms"] = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return stats

def toggle_star(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET is_starred = 1 - is_starred WHERE job_id = ?", (job_id,))
    cursor.execute("SELECT is_starred FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return bool(row[0]) if row else False

def toggle_applied(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET is_applied = 1 - is_applied WHERE job_id = ?", (job_id,))
    cursor.execute("SELECT is_applied FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return bool(row[0]) if row else False

def hide_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET is_hidden = 1 WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()
    return True
