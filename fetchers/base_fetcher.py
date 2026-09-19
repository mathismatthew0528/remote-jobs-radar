# -*- coding: utf-8 -*-
"""
远程工作爬虫系统 - 基础抓取模块
使用 Python 原生 urllib，零第三方依赖，高度稳定可靠
"""
import urllib.request
import urllib.parse
import json
import ssl
import re
from config import REQUEST_HEADERS

class BaseFetcher:
    def __init__(self, name="BaseFetcher"):
        self.name = name
        self.headers = REQUEST_HEADERS.copy()
        
    def fetch_url(self, url, is_json=True, timeout=15):
        """发送 HTTP GET 请求获取内容"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            # 忽略自签名证书校验，防止企业代理干扰
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
                raw_data = response.read().decode("utf-8", errors="replace")
                if is_json:
                    return json.loads(raw_data)
                return raw_data
        except Exception as e:
            print(f"[{self.name}] 抓取失败 {url}: {e}")
            return None

    def strip_html(self, text):
        """清洗 HTML 标签，提取干净的正文纯文本"""
        if not text:
            return ""
        clean = re.sub(r"<[^>]+>", " ", text)
        clean = re.sub(r"&[a-z]+;", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean
