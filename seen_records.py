"""
当天早晚去重的"已看记录"小工具（云端版）
- 【云端改造】GitHub Actions 每次运行都是全新环境，本地文件存不住，
  所以改成存到 Supabase（复用看板已经在用的同一个项目）
- 格式：每天一行记录，date 主键 + items(jsonb)
- 只保留最近 3 天的记录，更早的自动清掉
- 如果 Supabase 一时连不上，打印警告后跳过记录，不影响正常发邮件

首次使用前，需要在 Supabase 的 SQL Editor 里运行一次建表语句：

create table if not exists seen_records (
  date text primary key,
  items jsonb not null default '[]',
  updated_at timestamptz default now()
);
"""
import requests
from datetime import datetime, timedelta

from supabase_config import SUPABASE_URL, SUPABASE_ANON_KEY

KEEP_DAYS = 3
_TABLE_URL = f"{SUPABASE_URL}/rest/v1/seen_records"
_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}


def get_seen_today():
    """返回今天已经看过的内容列表：[{"title": "...", "url": "..."}, ...]"""
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        resp = requests.get(
            _TABLE_URL,
            headers=_HEADERS,
            params={"date": f"eq.{today}", "select": "items"},
            timeout=10,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0]["items"] if rows else []
    except Exception as e:
        print(f"⚠️ 读取云端去重记录失败（{e}），当作今天还没记录处理")
        return []


def record_today(date_str, items):
    """把某天看过的内容记下来（date_str 形如 2026-08-08）"""
    if not items:
        return
    try:
        resp = requests.post(
            _TABLE_URL,
            headers=_HEADERS,
            json={"date": date_str, "items": items, "updated_at": datetime.now().isoformat()},
            timeout=10,
        )
        resp.raise_for_status()
        print(f"✅ 已把今天看过的 {len(items)} 条记到云端，晚上会自动避开这些内容")
        _prune_old_records()
    except Exception as e:
        print(f"⚠️ 记录写入云端失败（{e}），这次跳过记录，今晚去重可能不完整")


def _prune_old_records():
    """清掉 KEEP_DAYS 天之前的旧记录，避免表越积越大"""
    cutoff = (datetime.now().date() - timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")
    try:
        requests.delete(
            _TABLE_URL,
            headers=_HEADERS,
            params={"date": f"lt.{cutoff}"},
            timeout=10,
        )
    except Exception:
        pass  # 清理失败不影响主流程，下次还会再试
