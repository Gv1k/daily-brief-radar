# ============================================================
# Supabase 云备份配置（可选，不填也能用）
# ------------------------------------------------------------
# 不填：数据照常存在 D 盘本地，一切功能正常。
# 填了：每次保存都会多一份云备份——你写的灵感、AI 提炼的 idea、
#       划掉/状态改动，全部同步到 Supabase 云端，换电脑也不丢。
#
# 怎么开通（大约 5 分钟，免费）：
#   1. 打开 https://supabase.com 登录，进入 Dashboard
#      免费版最多只能建 2 个项目，但每个项目里可以建无数张表。
#      所以【不用新建项目】——打开你已有的两个项目里的任意一个，
#      在左侧找到 SQL Editor（SQL 编辑器）
#   2. 把最下面注释里的建表 SQL 复制进去，Run 运行一次（重复运行也没事）
#   3. 左侧点 Project Settings -> API，
#      复制 Project URL 和 anon public key 填到下面两个引号里
#   4. 保存后重启看板（重新双击"启动看板.bat"），右上角会显示"云备份已连接"
# ============================================================

import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://pfvrfurkncmwnyzgldhc.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

# ---- 在 Supabase 的 SQL Editor 里运行下面这段（只需一次）----
# create table if not exists ideas (
#   id text primary key,
#   type text not null,
#   title text not null,
#   description text default '',
#   source_url text default '',
#   source_brief text default '',
#   tags text default '[]',
#   status text not null default '新想法',
#   created_at text default '',
#   updated_at text default ''
# );