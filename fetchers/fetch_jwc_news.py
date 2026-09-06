"""
抓取西南交通大学教务网 - 通知公告列表页（新版：本科生院官网）
数据源：https://bksy.swjtu.edu.cn/tzgg/qb.htm （"通知公告-全部"栏目，静态渲染，不需要登录）

【2026-09 改版说明】
学校教务网从旧的 WebAction 动态接口（jwc.swjtu.edu.cn）换成了新的静态化CMS
（bksy.swjtu.edu.cn，本科生院官网），页面结构完全不同，主要变化：
1. 新闻详情链接从含 "newsDetail" 关键字，变成 "/info/栏目ID/文章ID.htm" 这种路径
2. 日期不再是从父容器文字里单独摘取，而是直接拼接在标题文字末尾，
   例如 "关于XXX的通知 2025/02/25"，用 "/" 分隔（旧版是 "-" 分隔）
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import json
import re
import random
import time

# 日期出现在标题文字末尾，形如 "... 2025/02/25"
_DATE_SUFFIX_RE = re.compile(r"\s*(\d{4})/(\d{2})/(\d{2})\s*$")


def fetch_jwc_news():
    time.sleep(random.uniform(1, 3))

    url = "https://bksy.swjtu.edu.cn/tzgg/qb.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = resp.apparent_encoding  # 避免中文乱码
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []

    # 关键点：新版每条通知的详情链接都指向 "/info/栏目ID/文章ID.htm"
    # 用这个路径特征找真正的新闻标题链接
    news_links = soup.find_all("a", href=lambda h: h and re.search(r"/info/\d+/\d+\.htm", h))

    for link in news_links:
        raw_text = link.get_text(strip=True)
        if not raw_text or len(raw_text) < 4:
            continue

        # 标题和日期在同一段文字里，末尾形如 " 2025/02/25"，切分开来
        date_match = _DATE_SUFFIX_RE.search(raw_text)
        if date_match:
            title = raw_text[:date_match.start()].strip()
            date_str = "-".join(date_match.groups())  # 统一成 2025-02-25 格式，方便和旧数据兼容
        else:
            title = raw_text
            date_str = ""

        if not title:
            continue

        href = link["href"]
        full_url = urljoin(url, href)

        results.append({
            "title": title,
            "date": date_str,
            "url": full_url,
        })

    # 去重（同一条新闻的标题链接可能重复出现）
    seen = set()
    deduped = []
    for item in results:
        if item["title"] not in seen:
            seen.add(item["title"])
            deduped.append(item)

    return deduped


if __name__ == "__main__":
    news = fetch_jwc_news()

    print(f"抓取到 {len(news)} 条教务网通知\n")
    for i, item in enumerate(news[:20], 1):
        print(f"{i}. [{item['date']}] {item['title']}")
        print(f"   {item['url']}\n")

    output = {
        "fetched_at": datetime.now().isoformat(),
        "source": "jwc_swjtu",
        "items": news,
    }
    with open("jwc_news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"已保存到 jwc_news.json（共 {len(news)} 条）")
