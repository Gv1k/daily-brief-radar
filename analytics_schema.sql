-- 在你自己的 Supabase 项目（推广所用的那个，不是每个用户各自的项目）里运行一次
-- 用于收集引导页的埋点数据：多少人打开、走到哪一步、填了什么偏好

create table if not exists onboarding_analytics (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  event_type text not null,   -- page_view / step_reached / questionnaire_submitted / star_clicked
  payload jsonb,
  created_at timestamptz default now()
);

-- 允许匿名写入（埋点用），但不允许匿名读取别人的数据
alter table onboarding_analytics enable row level security;

create policy "anon can insert" on onboarding_analytics
  for insert to anon
  with check (true);

-- 你自己在 Supabase Dashboard 后台看数据时用的是 service_role，天然绕过 RLS，不受影响

-- 常用查询示例：
-- 转化漏斗：每个 event_type 的独立会话数
-- select event_type, count(distinct session_id) from onboarding_analytics group by event_type;

-- 内容偏好分布：
-- select jsonb_array_elements_text(payload->'focus') as focus_item, count(*)
-- from onboarding_analytics where event_type = 'questionnaire_submitted'
-- group by focus_item order by count(*) desc;
