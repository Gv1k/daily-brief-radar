"""
抓取 Hacker News 热门榜
数据源：官方公开 API，不需要 key，也不用担心反爬
文档：https://github.com/HackerNews/API
"""
import requests
from datetime import datetime
import json

def fetch_hacker_news(top_n=15):
    # 第一步：拿到热门帖子的 id 列表
    top_ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    resp = requests.get(top_ids_url, timeout=10)
    resp.raise_for_status()
    top_ids = resp.json()[:top_n]

    results = []
    for story_id in top_ids:
        detail_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        r = requests.get(detail_url, timeout=10)
        if r.status_code != 200:
            continue
        item = r.json()
        if not item or item.get("type") != "story":
            continue

        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            "score": item.get("score", 0),
            "comments": item.get("descendants", 0),
        })

    return results


if __name__ == "__main__":
    news = fetch_hacker_news()

    print(f"抓取到 {len(news)} 条 Hacker News 热门\n")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']} ({item['score']}分, {item['comments']}评论)")
        print(f"   {item['url']}\n")

    output = {
        "fetched_at": datetime.now().isoformat(),
        "source": "hacker_news",
        "items": news,
    }
    with open("hacker_news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"已保存到 hacker_news.json（共 {len(news)} 条）")
