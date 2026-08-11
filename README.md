# 每日AI雷达 · Daily AI Radar

一个跑在你自己 GitHub 账号上的**个性化每日简报**：每天早晚自动从 GitHub Trending、
Hacker News、AI/科技媒体 RSS、（可选）你学校的教务网抓取内容，交给 AI 按你的个人
画像筛选、解读、给行动建议，发到你自己的邮箱。

**完全免费、完全在你自己的账号里跑、没有中间服务器碰你的数据。**

## 3 分钟看懂它在做什么

1. 你 fork 这个仓库
2. 填一份 2 分钟的问卷，告诉 AI 你的身份、目标、关注领域、不想看什么
3. 把生成的配置粘进你仓库的 GitHub Secrets
4. GitHub Actions 每天定时（默认北京时间 7:30 / 21:00）自动跑：抓取 → AI 摘要 → 发邮件

## 快速开始

👉 **[打开设置引导页](https://gv1k.github.io/daily-brief/)** ——一步步教你 fork、拿 API key、填问卷、配置 Secrets。

## 项目结构

```
run_all.py              一键运行入口（抓取→摘要→发信）
fetch_*.py               各信息源抓取脚本
summarize.py             调用 DeepSeek 生成结构化简报（按你的个性化画像筛选）
send_email.py            解析简报、渲染成邮件HTML、发送
seen_records.py          早晚去重（存在你自己的 Supabase 项目里）
.github/workflows/       定时任务配置
index.html               设置引导页（GitHub Pages 托管）
```

## 需要的账号（都免费或几块钱）

- GitHub 账号（fork + 跑 Actions）
- DeepSeek API key（充1~5元即可用很久）
- QQ邮箱（用于发信，拿SMTP授权码）
- Supabase 项目（可选，用于早晚去重，不填也能正常收信）

## 支持的教务网

目前内置西南交通大学教务网抓取（`fetch_jwc_news.py`）。如果你是别的学校，
把这个文件里的目标网址和页面结构改成你学校的即可，其余部分不用动。

## License

MIT
