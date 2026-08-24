"""
抓取经济 / 政治 / 科学突破类别新闻（阶段一修订版）

【本次改动】
之前经济/政治都用BBC的源，内容偏国际、跟"中国经济趋势""国内时政"关系不大。
这次改成：
- 经济拆两个子类：中国经济（中新网财经RSS）+ 世界经济（BBC Business）
- 政治拆两个子类：国内时政（中新网时政RSS）+ 国际时政（BBC World）
- 科学突破维持BBC科学环境RSS，不拆分（后面summarize.py那边只挑2条）

运行前需要先装：pip install feedparser
"""
import feedparser
from datetime import datetime
import json

# 结构：大类 -> { 子类名: RSS地址 }
CATEGORY_SOURCES = {
    "经济": {
        "中国经济": "https://www.chinanews.com.cn/rss/finance.xml",
        "世界经济": "http://feeds.bbci.co.uk/news/business/rss.xml",
    },
    "政治": {
        "国内时政": "https://www.chinanews.com.cn/rss/china.xml",
        "国际时政": "http://feeds.bbci.co.uk/news/world/rss.xml",
    },
    "科学突破": {
        "科学突破": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    },
}


def fetch_one(category, subcategory, url, max_items=10):
    """抓取单个子类的RSS。max_items留得比展示条数多一些，方便后面AI筛选时有得挑"""
    feed = feedparser.parse(url)

    if feed.bozo and not feed.entries:
        print(f"⚠️ 【{category}-{subcategory}】抓取可能有问题，跳过（{url}）")
        return []

    results = []
    for entry in feed.entries[:max_items]:
        results.append({
            "category": category,
            "subcategory": subcategory,
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "published": entry.get("published", entry.get("updated", "")),
        })
    return results


if __name__ == "__main__":
    all_items = []

    for category, subs in CATEGORY_SOURCES.items():
        for subcategory, url in subs.items():
            print(f"正在抓取【{category}-{subcategory}】...")
            items = fetch_one(category, subcategory, url)
            print(f"  → 抓到 {len(items)} 条")
            all_items.extend(items)

    print(f"\n总共抓取到 {len(all_items)} 条")
    for i, item in enumerate(all_items, 1):
        print(f"{i}. [{item['category']}-{item['subcategory']}] {item['title']}")
        print(f"   {item['url']}\n")

    output = {
        "fetched_at": datetime.now().isoformat(),
        "source": "category_news",
        "items": all_items,
    }
    with open("category_news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"已保存到 category_news.json（共 {len(all_items)} 条）")
