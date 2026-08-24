"""
抓取西南交通大学教务网 - 新闻列表页
数据源：https://jwc.swjtu.edu.cn/vatuu/WebAction?setAction=newsList
这个页面是静态渲染的完整列表（不像首页需要等JS加载），不需要登录
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import random
import time

def fetch_jwc_news():
    time.sleep(random.uniform(1, 3))

    url = "https://jwc.swjtu.edu.cn/vatuu/WebAction?setAction=newsList"
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

    # 关键点：每条新闻的详情链接里都包含 "setAction=newsDetail"
    # 用这个特征找真正的新闻标题链接，比瞎猜标题关键词准得多
    news_links = soup.find_all("a", href=lambda h: h and "newsDetail" in h)

    for link in news_links:
        title = link.get_text(strip=True)
        if not title or len(title) < 4:
            continue

        href = link["href"]
        full_url = href if href.startswith("http") else "https://jwc.swjtu.edu.cn" + href

        # 日期通常出现在这条新闻所在的父容器文字里，格式类似 2026-08-02 10:50:16
        container = link.find_parent(["div", "li", "dd"]) or link.parent
        container_text = container.get_text(" ", strip=True) if container else ""
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", container_text)
        date_str = date_match.group() if date_match else ""

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
