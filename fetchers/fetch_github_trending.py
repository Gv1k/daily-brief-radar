"""
抓取 GitHub Trending（每日热门项目）
数据源：https://github.com/trending
不需要 API key，直接解析公开页面
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import random
import time

def fetch_github_trending(language="", since="daily"):
    """
    抓取 GitHub Trending 榜单
    language: 留空=所有语言, 也可以传 "python" / "javascript" 等
    since: daily / weekly / monthly
    """
    # 跑之前先随机等一下，避免每次都是掐着点的固定间隔请求，行为更接近真人访问
    time.sleep(random.uniform(1, 4))

    url = f"https://github.com/trending/{language}"
    params = {"since": since}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://github.com/",
    }

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    repo_list = soup.select("article.Box-row")
    results = []

    for repo in repo_list:
        # 仓库名（形如 "owner / repo"）
        title_tag = repo.select_one("h2 a")
        if not title_tag:
            continue
        full_name = title_tag.get("href", "").strip("/")
        repo_url = f"https://github.com/{full_name}"

        # 描述
        desc_tag = repo.select_one("p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # 语言
        lang_tag = repo.select_one("[itemprop='programmingLanguage']")
        repo_language = lang_tag.get_text(strip=True) if lang_tag else "未标注"

        # 总 star 数
        star_tag = repo.select_one("a[href$='/stargazers']")
        stars = star_tag.get_text(strip=True) if star_tag else "0"

        # 今日新增 star（在页面底部一个 float-sm-right 的 span 里）
        today_star_tag = repo.select_one("span.d-inline-block.float-sm-right")
        today_stars = today_star_tag.get_text(strip=True) if today_star_tag else ""

        results.append({
            "name": full_name,
            "url": repo_url,
            "description": description,
            "language": repo_language,
            "total_stars": stars,
            "today_stars": today_stars,
        })

    return results


if __name__ == "__main__":
    trending = fetch_github_trending(since="daily")

    print(f"抓取到 {len(trending)} 个热门项目\n")
    for i, repo in enumerate(trending[:10], 1):
        print(f"{i}. {repo['name']} ({repo['language']}) - {repo['today_stars']}")
        print(f"   {repo['description']}")
        print(f"   {repo['url']}\n")

    # 存成 json，方便后续接入 AI 摘要环节
    output = {
        "fetched_at": datetime.now().isoformat(),
        "source": "github_trending",
        "items": trending,
    }
    with open("github_trending.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"已保存到 github_trending.json（共 {len(trending)} 条）")
