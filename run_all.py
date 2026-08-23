"""
一键运行：依次执行抓取 → AI摘要 → 发送简报邮件

【阶段三新增】支持"早班/晚班"参数，用于区分早晚两次推送：
- 手动指定：python run_all.py morning  或  python run_all.py evening
- 不传参数：自动按当前时间判断，中午12点前算早班，之后算晚班
  （所以如果用Windows定时任务在固定时间触发，其实可以不用传参数，
  只要早上那次任务和晚上那次任务的触发时间分别在12点前后即可；
  如果想更保险，也可以在任务计划程序里直接写死参数，见下方使用说明）

用法：
  python run_all.py            自动判断早晚班
  python run_all.py morning    强制按早班跑
  python run_all.py evening    强制按晚班跑
"""
import subprocess
import sys
import os
import time
from datetime import datetime

# 每一步最多重试几次、每次重试前等多久（秒）
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 60

# 早晚两次推送内容完全独立，各自重新抓取一遍最新数据（不是早间的复盘）
FETCH_STEPS = [
    ("抓取 GitHub Trending", "fetch_github_trending.py"),
    ("抓取教务网通知", "fetch_jwc_news.py"),
    ("抓取 Hacker News", "fetch_hacker_news.py"),
    ("抓取科技/AI媒体RSS", "fetch_rss_sources.py"),
    ("抓取经济/政治/科学突破新闻", "fetch_category_news.py"),
]

if len(sys.argv) > 1 and sys.argv[1] in ("morning", "evening"):
    slot = sys.argv[1]
else:
    slot = "morning" if datetime.now().hour < 12 else "evening"

slot_label = "早班" if slot == "morning" else "晚班"
print(f"本次运行班次：{slot_label}（{slot}）")

# 【推送频率】DAILY_FREQUENCY 来自问卷生成的 GitHub Secret，值是 "1" 或 "2"
# 没设置时默认按"2"（早晚都发）处理，兼容还没配置这个 secret 的旧用户
daily_frequency = os.environ.get("DAILY_FREQUENCY", "2").strip()
if daily_frequency == "1" and slot == "evening":
    print("你在问卷里选的是「一天1次」，晚班这次直接跳过，不发信、也不算失败。")
    sys.exit(0)

steps = FETCH_STEPS + [
    ("生成AI摘要", "summarize.py", slot),
    ("发送简报邮件", "send_email.py", slot),
]

def run_step_with_retry(step_name, script, extra_args):
    """执行一步，失败就等一会儿重试，重试次数用完才算真正失败"""
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n{'='*40}")
        print(f"▶ 正在执行：{step_name}（第{attempt}次尝试）")
        print('='*40)
        result = subprocess.run([sys.executable, script] + extra_args)
        if result.returncode == 0:
            return True
        print(f"⚠️ {step_name} 第{attempt}次失败（退出码 {result.returncode}）")
        if attempt < MAX_RETRIES:
            print(f"   等待 {RETRY_WAIT_SECONDS} 秒后重试...")
            time.sleep(RETRY_WAIT_SECONDS)
    print(f"❌ {step_name} 重试{MAX_RETRIES}次仍然失败，停止后续步骤")
    return False


all_ok = True
for step in steps:
    step_name, script = step[0], step[1]
    extra_args = list(step[2:])  # 抓取脚本没有额外参数，summarize.py/send_email.py会带上slot
    if not run_step_with_retry(step_name, script, extra_args):
        all_ok = False
        break

if all_ok:
    print(f"\n✅ 全部完成！{slot_label}简报已生成并发送")
    # idea 库：每次运行后归档简报（这一周的简报都会存到 D 盘存档）；
    # 周六早上自动把本周简报提炼成产品 idea 存入 idea 库
    subprocess.run([sys.executable, "extract_ideas.py"])
    if slot == "morning" and datetime.now().weekday() == 5:
        print("\n今天是周六，自动把本周简报提炼成产品 idea 存入 idea 库...")
        subprocess.run([sys.executable, "extract_ideas.py", "--extract"])