# 店家后台 · 网站统计 / 下单记录（店家专用）

**后台网址：https://hunterboom.my/zwvh.html**（不在页脚、导航、sitemap；noindex,nofollow；只写在这份文档）

后台能看：
- 今日下单次数、今日销售（商品参考合计）、今日人数、今日浏览。
- 🔎 查单号：输入完整单号或后 4 位（≥3 字），列出订单，点单号打开完整 **出货单**（可打印 / 存 PDF）。
- 🧾 选日期看当天：下单次数、商品小计、邮费、合计（含邮费）、待处理数；按取货方式和按产品（前 10）的小结（只按已记录订单计算）；每单显示单号、时间、产品（编号/名称/散装或整盒/数量/单价/小计）、取货方式、邮寄资料、合计、顾客姓名电话、付款状态（💰 待收款 / 已确认收款）、「出货单」「WhatsApp 联系顾客」「确认收款」「已备货出货（标记已处理）」。**未确认收款不能标记出货**（需 Version 3 脚本；旧版脚本不返回付款状态时保留原来的「标记已处理」）。
- 近 14 天走势图、近 30 天每日明细（原有统计保留）。
- 🔑 修改后台密码。

## 后台密码（OWNER_PIN）
- 存在 Apps Script「脚本属性」`OWNER_PIN`（不在网站、不在 git）。
- **第一次设置**：打开 /zwvh.html，若还没设置密码会显示「设置后台密码」。需要一次性的 **设置码** —— 只写在店家私人 Google 表格的「后台设置」分页 B2 格（在编辑器运行 `setup` 也会在日志显示）。输入设置码 + 新密码（≥6 位）即设置并登录，设置码随即作废，之后不能再用这个方式改密码（防止别人抢先或覆盖）。
- 也可以照旧手动在脚本属性里设 `OWNER_PIN`。忘记密码：到脚本属性直接改。
- 登录后可在后台底部「修改后台密码」（需输入当前密码）。错误 8 次锁 15 分钟。


- 前台追踪：`js/stats.js`（所有页面加载）。每次打开页面记 1 次浏览；同一浏览器每天首次出现记 1 位人数；顾客在购物车点「提交订单」时，`HBJStats.order()` 把订单 POST 到接口并**等待成功**才显示「下单成功」和单号，之后才打开 WhatsApp 让顾客把「下单成功 + 单号」发给客服（不发也不影响订单）。失败会提示重试，单号不变，不会算成功。页脚/导航的普通「WhatsApp 联系」不算下单。
- 后台：Google Apps Script `tools/stats_api.gs`，数据写入 Google 表格 **Hunter BOOM JOHOR 网站统计**
  https://docs.google.com/spreadsheets/d/16_7iC4omnsluDDrX5F1SWNmQD0u-nBmjcGmEI_7pRTE/edit
  （tabs: daily / orders / visitors / events / 说明；表格 ID 已写在脚本 `SPREADSHEET_ID`）
- 私人页面：`/zwvh.html`（不在页脚、导航、sitemap；noindex,nofollow）。需输入店家密码（服务器端 Script Property `OWNER_PIN` 验证），之后用 6 小时的会话 token（sessionStorage）。未登录时 API 不返回任何数字或订单。
- 通知：网站下单成功后会打开 wa.me/60177891688 让顾客发「下单成功 + 单号」给客服。
- **可选：WhatsApp Cloud API 自动通知**（需 Version 3 脚本）。在 Apps Script → 项目设置 → 脚本属性设：`WA_TOKEN`（或 `WA_ACCESS_TOKEN`）、`WA_PHONE_NUMBER_ID`、可选 `WA_TO`（默认 60177891688）。设好后每笔新订单会自动发给客服，并自动回复顾客（感谢下单 + 付款资料 + 「客服确认款项后才会备货及出货」）。付款资料用脚本属性 `PAY_HOLDER` / `PAY_BANK` / `PAY_ACCOUNT`，可选付款 QR 图片网址 `PAY_QR_URL`。没设就不发，订单照常。注意：普通文字消息只在对方 24 小时内发过消息给这个系统号码时才送得到，否则要改用 Meta 审核过的模板。值都不要写进 git。
- 网站下单成功页的付款资料（户名 / 银行 / 户口号码 / QR 图片路径）填在 `js/cart.js` 顶部 `PAY`，空的就显示「客服会联系安排付款」。

## 部署（一次）
1. 打开上面的表格 → 扩展程序 → Apps Script（或 script.google.com 新项目），把 `tools/stats_api.gs` 全部贴到 Code.gs，保存。
2. 项目设置 → 时区选 (GMT+08:00) Kuala Lumpur。
3. 项目设置 → 脚本属性 → 新增 `OWNER_PIN` = 店家密码（不要写进 git / 网站）。
4. 在编辑器运行一次 `setup`，授权访问表格。
5. 部署 → 新部署 → 类型「网页应用」：执行身份 **我**，访问权限 **任何人**。复制 `https://script.google.com/macros/s/…/exec`。
6. 把网址贴到 `js/stats.js` 第 8 行 `var API = "";` 的引号里，提交并推送（不需要重新 build）。
7. 以后改脚本：部署 → 管理部署 → 编辑 → 版本选「新版本」（网址不变）。

## 定义
- 下单 = 在本站提交成功的订单次数（最终成交以店家确认为准）；同一浏览器 10 秒内相同内容只算 1 次，每浏览器每天最多 30 次。
- 人数 = 当日独立访客（马来西亚时间 UTC+8 每天 00:00 重算）。
- 浏览 = 当日页面浏览次数（每浏览器每天最多计 80 次，防刷新灌水；统计页本身不计）。
- 不存 IP。选「邮寄」的订单会把顾客填的邮寄资料（收件人姓名、电话、地址、邮区编号、城市、州属）存进私人表格 orders 分页，只有输入店家密码后的统计页能看到；自取 / Lalamove 订单只存顾客填的姓名、电话（同样在 ship_json，Version 3 起）。orders 分页 R `pay_status`（unpaid / paid）、S `paid_at` 为付款确认（Version 3 新增，旧行留空）。没有任何删除/重置接口；要更正请直接改表格。

## 单号 / 取货方式（2026-11-13 新增）
- 购物车每次发送生成单号 `HBJ-YYYYMMDD-XXXX`（马来西亚日期 + 4 位随机码，字母表去掉 0/O/1/I），放在 WhatsApp 订单第一行；同一购物车+同一取货方式重发沿用同一单号，且不重复记下单。
- 订单 payload 额外字段（可选，旧版脚本会忽略）：`order_no`、`delivery`（pickup / lalamove / post）、`ship`（邮寄资料）、`postage`（服务器固定：邮寄 15，其余 0）、items 里的 `m`（l 散装 / b 整盒 / s 单件）。产品名也带「（散装）/（整盒）」，旧表格也看得出单位。
- orders 分页新增栏：M `order_no`、N `delivery`、O `postage`、P `grand_total`、Q `ship_json`（脚本会自动补表头，旧行留空）。`ref_total` 和每日 `order_total` 仍为商品参考合计（不含邮费）。
- **需要重新部署**：把新版 `tools/stats_api.gs` 贴进 Apps Script → 部署 → 管理部署 → 编辑 → 版本「新版本」（网址不变）。未重新部署前，网站照常记下单，但单号 / 取货方式 / 邮寄资料不会进表格。
- 出货单归档：`python3 tools/file_order.py`（JSON / WhatsApp 文字 / orders 分页 CSV）→ box 私人文件夹 `/workspace/hunterboom-orders/`，每单一个 `.md` + `.json`。
