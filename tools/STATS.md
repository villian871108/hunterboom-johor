# 网站统计 / 下单记录（店家专用）

- 前台追踪：`js/stats.js`（所有页面加载）。每次打开页面记 1 次浏览；同一浏览器每天首次出现记 1 位人数；顾客在购物车点「发送订单到 WhatsApp」或产品页的 WhatsApp 下单按钮（购物车非空）时记 1 笔下单（含 SKU、名称、数量、参考价）。页脚/导航的普通「WhatsApp 联系」不算下单。
- 后台：Google Apps Script `tools/stats_api.gs`，数据写入 Google 表格 **Hunter BOOM JOHOR 网站统计**
  https://docs.google.com/spreadsheets/d/16_7iC4omnsluDDrX5F1SWNmQD0u-nBmjcGmEI_7pRTE/edit
  （tabs: daily / orders / visitors / events / 说明；表格 ID 已写在脚本 `SPREADSHEET_ID`）
- 私人页面：`/stats.html`（不在页脚、导航、sitemap；noindex,nofollow）。需输入店家密码（服务器端 Script Property `OWNER_PIN` 验证），之后用 6 小时的会话 token（sessionStorage）。未登录时 API 不返回任何数字或订单。
- 人工通知：顾客发单时本来就直接打开 wa.me/60177891688（017-789 1688）把订单文字发给店家；统计页每笔工单另有「用 WhatsApp 跟进」和「标记已处理 / 改回待处理」。

## 部署（一次）
1. 打开上面的表格 → 扩展程序 → Apps Script（或 script.google.com 新项目），把 `tools/stats_api.gs` 全部贴到 Code.gs，保存。
2. 项目设置 → 时区选 (GMT+08:00) Kuala Lumpur。
3. 项目设置 → 脚本属性 → 新增 `OWNER_PIN` = 店家密码（不要写进 git / 网站）。
4. 在编辑器运行一次 `setup`，授权访问表格。
5. 部署 → 新部署 → 类型「网页应用」：执行身份 **我**，访问权限 **任何人**。复制 `https://script.google.com/macros/s/…/exec`。
6. 把网址贴到 `js/stats.js` 第 8 行 `var API = "";` 的引号里，提交并推送（不需要重新 build）。
7. 以后改脚本：部署 → 管理部署 → 编辑 → 版本选「新版本」（网址不变）。

## 定义
- 下单 = 从本站发送到 WhatsApp 的订单次数（最终成交以店家确认为准）；同一浏览器 10 秒内相同内容只算 1 次，每浏览器每天最多 30 次。
- 人数 = 当日独立访客（马来西亚时间 UTC+8 每天 00:00 重算）。
- 浏览 = 当日页面浏览次数（每浏览器每天最多计 80 次，防刷新灌水；统计页本身不计）。
- 不存 IP、姓名、电话。没有任何删除/重置接口；要更正请直接改表格。
