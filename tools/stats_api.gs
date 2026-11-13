/**
 * Hunter BOOM JOHOR — 网站统计 API (Google Apps Script Web App)
 * ---------------------------------------------------------------
 * Counts, per Malaysia day (Asia/Kuala_Lumpur, UTC+8):
 *   下单 orders   = orders submitted on the site (购物车「提交订单」; recorded here BEFORE any WhatsApp)
 *   人数 visitors = unique anonymous browser IDs (vid) seen that day
 *   浏览 views    = page views (capped at VIEW_CAP per vid per day)
 * All numbers are real hits. Nothing is seeded. There is NO reset/delete endpoint:
 * to correct data, the owner edits the spreadsheet directly.
 *
 * Spreadsheet: "Hunter BOOM JOHOR 网站统计"
 *   https://docs.google.com/spreadsheets/d/16_7iC4omnsluDDrX5F1SWNmQD0u-nBmjcGmEI_7pRTE/edit
 *   Tabs: daily | events | visitors | 说明 | orders   (headers already created)
 *
 * API
 *   POST (text/plain JSON) {op:"hit", type:"view"|"visit"|"order", vid, host, path, extra}
 *        order extra = {items:[{c:SKU, n:name, q:qty, p:unit price, m:"l"|"b"|"s"}], empty items are rejected,
 *                       optional: order_no:"HBJ-YYYYMMDD-XXXX", delivery:"pickup"|"lalamove"|"post",
 *                       ship:{name,phone,addr,pc,city,state} for post (postage fixed server-side RM15),
 *                            {name,phone} for pickup / lalamove}
 *        → {ok, counted, whatsapp:{shop, customer}}  (never returns any totals)
 *          whatsapp.* is true only when the Cloud API accepted that message (see notify below)
 *        → {ok, dup:true}  same 单号 already recorded (resubmit) — not counted again
 *   OWNER ONLY (PIN stored in Script Properties → OWNER_PIN, never in the website/repo):
 *   POST {op:"login", pin} → {ok, token}  (session 6 h; 8 wrong PINs in 15 min locks login)
 *   POST {op:"read", token, days:30, date:"YYYY-MM-DD"}
 *        → {ok, today, days:[{date,views,visitors,orders,order_total}], order_date, order_day, pending,
 *           orders:[{id,status:"pending"|"done",handled_at,ts,time,qty,ref_total,items:[{c,n,q,p,m}],
 *                    order_no,delivery,postage,grand_total,ship}]}
 *   POST {op:"status", token, id, status:"done"|"pending"}  → mark 已处理 / 待处理
 *   POST {op:"pay", token, id, pay:"paid"|"unpaid"}        → 确认收款 / 改回待收款 (must happen before 备货出货)
 *   POST {op:"find", token, q:"HBJ-20261113-9F4F" | partial}  → {ok, q, orders:[…]}  (search by 单号)
 *   POST {op:"changepin", token, old, pin}
 *   POST {op:"logout", token}
 *   FIRST-TIME PIN (public, safe): POST {op:"pin_status"} → {ok, pin_set}
 *        POST {op:"setpin", code, pin} → {ok, token}; only while OWNER_PIN is unset and only with the
 *        one-time 设置码 from the private spreadsheet tab「后台设置」(also printed by running setup()).
 *   GET → {ok:false, error:"auth_required"}  (no data without login)
 *   Orders with delivery "post" store the customer's 邮寄资料 (name/phone/address) in the private
 *   orders tab (owner-only; returned only after PIN login). Pickup / Lalamove orders store 姓名 + 电话 the same
 *   way (ship_json). No IP is stored. Nothing is exposed publicly.
 *
 * OPTIONAL WhatsApp Cloud API notify (Script Properties; never commit values):
 *   WA_TOKEN (or WA_ACCESS_TOKEN)  permanent/system-user access token
 *   WA_PHONE_NUMBER_ID             Cloud API sender phone-number id (a separate system number, NOT 017-789 1688)
 *   WA_TO                          客服 number to notify, default 60177891688
 *   PAY_HOLDER / PAY_BANK / PAY_ACCOUNT  付款资料 for the customer auto-reply (empty = "客服会联系安排付款")
 *   PAY_QR_URL                     optional public https URL of the payment QR image (sent as an image message)
 *   If WA_TOKEN or WA_PHONE_NUMBER_ID is missing, nothing is sent and orders work exactly the same.
 *
 * DEPLOY (see tools/STATS.md for the full checklist):
 *   1. Open the spreadsheet → Extensions → Apps Script (or script.google.com → New project).
 *   2. Replace Code.gs with this whole file. Save.
 *   3. Project Settings → Time zone → (GMT+08:00) Kuala Lumpur  (the code also forces TZ below).
 *   4. Owner PIN: EITHER open /zwvh.html →「设置后台密码」with the one-time 设置码 from the spreadsheet
 *      tab「后台设置」(created on first visit / by setup()), OR Project Settings → Script Properties →
 *      OWNER_PIN = <owner's private PIN>. Login is refused while it is empty. Never commit the PIN.
 *   5. Run `setup` once from the editor and accept the permission prompt (Sheets access).
 *   6. Deploy → New deployment → type "Web app"
 *        Execute as: Me (loting87@gmail.com)
 *        Who has access: Anyone
 *      Copy the Web app URL (https://script.google.com/macros/s/…/exec).
 *   7. Paste it into js/stats.js:  var API = "…/exec";  then commit/push.
 *   After editing this code later: Deploy → Manage deployments → Edit → Version: New version
 *   (keeps the same /exec URL).
 *
 * CORS: Apps Script cannot read the Origin header nor answer OPTIONS. Google's
 * ContentService responses already carry `Access-Control-Allow-Origin: *`. The site
 * therefore sends POST bodies as text/plain (a "simple" request → no preflight) and
 * includes `host`; hits whose host is not in ALLOWED_HOSTS are ignored. This is a
 * soft filter (anyone can fake it) — the real protection is the per-vid caps below.
 */

var SPREADSHEET_ID = '16_7iC4omnsluDDrX5F1SWNmQD0u-nBmjcGmEI_7pRTE';
var TZ = 'Asia/Kuala_Lumpur';
var VIEW_CAP = 80;          // max counted page views per vid per day
var ORDER_CAP = 30;         // max counted orders per vid per day
var ORDER_DEBOUNCE_S = 10;  // identical order payload from same vid within N s = one order
var MAX_DAYS = 90;
var ALLOWED_HOSTS = ['hunterboom.my', 'www.hunterboom.my', 'villian871108.github.io', 'localhost', '127.0.0.1'];

function ss_() { return SpreadsheetApp.openById(SPREADSHEET_ID); }
function today_() { return Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd'); }
function now_() { return Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd'T'HH:mm:ss'+08:00'"); }
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function str_(v, n) { return String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').slice(0, n); }

function sheet_(name, header) {
  var ss = ss_(), sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); }
  if (sh.getLastRow() === 0) { sh.appendRow(header); sh.setFrozenRows(1); }
  return sh;
}
function daily_() { return sheet_('daily', ['date', 'views', 'visitors', 'orders', 'order_total', 'updated_at']); }
function events_() { return sheet_('events', ['timestamp', 'date', 'type', 'path', 'vid', 'extra']); }
function visitors_() { return sheet_('visitors', ['key', 'date', 'vid', 'views', 'orders', 'first_seen', 'last_seen']); }
var ORDER_HEAD = ['timestamp', 'date', 'time', 'qty', 'ref_total', 'items', 'items_json', 'path', 'vid', 'id', 'status', 'handled_at',
                  'order_no', 'delivery', 'postage', 'grand_total', 'ship_json', 'pay_status', 'paid_at'];
var ORDER_COLS = ORDER_HEAD.length;   // 19; M–Q added 2026-11-13, R pay_status (unpaid|paid) + S paid_at added in V3 (old rows empty = 待收款)
var DELIVERY = { pickup: '自取（Sutera Mall）', lalamove: 'Lalamove（联系客服安排）', post: '邮寄' };
var POSTAGE_POST = 15;               // 西马邮费一律 RM15（任买）
var SHIP_KEYS = ['name', 'phone', 'addr', 'pc', 'city', 'state'];
var CONTACT_KEYS = ['name', 'phone'];   // 自取 / Lalamove contact
function orders_() {
  var sh = sheet_('orders', ORDER_HEAD);
  if (sh.getLastColumn() < ORDER_COLS) {   // older sheet: append the new header cells, keep existing data
    var have = sh.getLastColumn();
    sh.getRange(1, have + 1, 1, ORDER_COLS - have).setValues([ORDER_HEAD.slice(have)]);
  }
  return sh;
}

/** Run once from the editor to authorize and make sure tabs/formats exist. Writes no counts. */
function setup() {
  daily_().getRange('A:A').setNumberFormat('@');
  events_().getRange('A:B').setNumberFormat('@');
  visitors_().getRange('A:C').setNumberFormat('@');
  orders_().getRange('A:C').setNumberFormat('@');
  orders_().getRange('M:N').setNumberFormat('@');
  orders_().getRange('R:S').setNumberFormat('@');
  Logger.log('OK: ' + ss_().getUrl() + ' today=' + today_());
  if (!PropertiesService.getScriptProperties().getProperty('OWNER_PIN')) {
    Logger.log('后台密码未设置。打开 /zwvh.html →「设置后台密码」，输入设置码：' + setupCode_() + '（也写在表格「后台设置」分页）');
  }
}

function findRow_(sh, text) {
  if (sh.getLastRow() < 2) return 0;
  var r = sh.getRange(2, 1, sh.getLastRow() - 1, 1).createTextFinder(text).matchEntireCell(true).findNext();
  return r ? r.getRow() : 0;
}
function dateStr_(v) { return v instanceof Date ? Utilities.formatDate(v, TZ, 'yyyy-MM-dd') : String(v); }
function num_(v) { return Number(v) || 0; }
function r2_(x) { return Math.round(x * 100) / 100; }

/** Returns [row, views, visitors, orders, order_total] for date, creating a zero row if missing. Caller holds lock. */
function dayRow_(sh, date) {
  var row = findRow_(sh, date);
  if (!row) {
    row = sh.getLastRow() + 1;
    sh.getRange(row, 1).setNumberFormat('@');
    sh.getRange(row, 1, 1, 6).setValues([[date, 0, 0, 0, 0, now_()]]);
    return [row, 0, 0, 0, 0];
  }
  var v = sh.getRange(row, 2, 1, 4).getValues()[0];
  return [row, num_(v[0]), num_(v[1]), num_(v[2]), num_(v[3])];
}

function readToday_() {   // internal helper (not exposed publicly)
  var date = today_(), sh = daily_(), row = findRow_(sh, date);
  if (!row) return { date: date, views: 0, visitors: 0, orders: 0, order_total: 0 };
  var v = sh.getRange(row, 2, 1, 4).getValues()[0];
  return { date: date, views: num_(v[0]), visitors: num_(v[1]), orders: num_(v[2]), order_total: num_(v[3]) };
}

/** Clean the order items sent by the site: [{c:sku, n:name, q:qty, p:unit price}] (max 60 lines). */
function cleanItems_(extra) {
  var list = (extra && Object.prototype.toString.call(extra.items) === '[object Array]') ? extra.items : [];
  var out = [];
  for (var i = 0; i < list.length && out.length < 60; i++) {
    var x = list[i] || {};
    var q = Math.max(1, Math.min(9999, parseInt(x.q, 10) || 1));
    var pr = Math.max(0, Math.min(100000, Number(x.p) || 0));
    var c = str_(x.c, 20), n = str_(x.n, 80);
    if (!c && !n) continue;
    var m = /^[lbs]$/.test(String(x.m || '')) ? String(x.m) : '';
    out.push(m ? { c: c, n: n, q: q, p: r2_(pr), m: m } : { c: c, n: n, q: q, p: r2_(pr) });
  }
  return out;
}

/** Optional order meta from the site: 单号, 取货方式, 邮寄资料. Unknown/invalid values are dropped. */
function cleanMeta_(extra) {
  extra = extra || {};
  var no = String(extra.order_no || '').toUpperCase();
  var d = DELIVERY[extra.delivery] ? String(extra.delivery) : '';
  var ship = null;
  if (d && extra.ship && typeof extra.ship === 'object') {
    ship = {};
    (d === 'post' ? SHIP_KEYS : CONTACT_KEYS).forEach(function (k) { ship[k] = str_(extra.ship[k], 200); });
    if (d !== 'post' && !ship.name && !ship.phone) ship = null;
  }
  return { order_no: /^HBJ-\d{8}-[0-9A-Z]{4}$/.test(no) ? no : '', delivery: d, postage: d === 'post' ? POSTAGE_POST : 0, ship: ship };
}

function hit_(b) {
  var type = String(b.type || '');
  if (['view', 'visit', 'order'].indexOf(type) < 0) return { ok: false, error: 'bad type' };
  var vid = String(b.vid || '');
  if (!/^[a-z0-9]{8,40}$/.test(vid)) return { ok: false, error: 'bad vid' };
  var host = String(b.host || '').toLowerCase();
  if (ALLOWED_HOSTS.indexOf(host) < 0) return { ok: false, error: 'host not allowed' };
  var path = str_(b.path, 200);
  var date = today_(), ts = now_();
  var items = [], qty = 0, total = 0, meta = null;

  if (type === 'order') {
    items = cleanItems_(b.extra);
    meta = cleanMeta_(b.extra);
    if (!items.length) return { ok: false, error: 'empty order' };   // never count an empty cart
    items.forEach(function (x) { qty += x.q; total += x.q * x.p; });
    total = r2_(total);
    // debounce double click / duplicate send: same vid + same items within N seconds = one order
    var cache = CacheService.getScriptCache();
    var sig = 'o_' + Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, vid + '|' + meta.order_no + '|' + JSON.stringify(items)));
    if (cache.get(sig)) return { ok: true, dup: true };
    cache.put(sig, '1', ORDER_DEBOUNCE_S);
  }

  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return { ok: false, error: 'busy' };
  var res, newOrder = null;
  try {
    // same 单号 already in the orders tab (customer resubmitted after a slow/failed reply) → do not count twice
    if (type === 'order' && meta.order_no && orderNoRow_(meta.order_no)) return { ok: true, dup: true };
    var dsh = daily_(), vsh = visitors_();
    var d = dayRow_(dsh, date);
    var views = d[1], visitors = d[2], orders = d[3], otot = d[4];
    var key = date + '|' + vid, vrow = findRow_(vsh, key), vv = 0, vo = 0, first = ts, counted = [];
    if (!vrow) {
      vrow = vsh.getLastRow() + 1;
      vsh.getRange(vrow, 1, 1, 3).setNumberFormat('@');
      visitors++; counted.push('visit');           // first hit of the day from this browser = 1 人数
    } else {
      var cur = vsh.getRange(vrow, 4, 1, 3).getValues()[0];
      vv = num_(cur[0]); vo = num_(cur[1]); first = cur[2] || ts;
    }
    if (type === 'view' && vv < VIEW_CAP) { vv++; views++; counted.push('view'); }
    if (type === 'order' && vo < ORDER_CAP) { vo++; orders++; otot = r2_(otot + total); counted.push('order'); }
    vsh.getRange(vrow, 1, 1, 7).setValues([[key, date, vid, vv, vo, first, ts]]);
    dsh.getRange(d[0], 2, 1, 5).setValues([[views, visitors, orders, otot, ts]]);
    var ev = events_(), rows = [];
    counted.forEach(function (t) {
      if (t === 'view') return;                     // views are only aggregated (keeps the log small)
      rows.push([ts, date, t, path, vid, t === 'order' ? JSON.stringify({ qty: qty, ref_total: total, order_no: meta.order_no, delivery: meta.delivery }) : '']);
    });
    if (rows.length) {
      var start = ev.getLastRow() + 1;
      ev.getRange(start, 1, rows.length, 2).setNumberFormat('@');
      ev.getRange(start, 1, rows.length, 6).setValues(rows);
    }
    if (counted.indexOf('order') > -1) {
      var osh = orders_(), orow = osh.getLastRow() + 1;
      var text = items.map(function (x) { return x.c + ' ' + x.n + ' x' + x.q; }).join('；');
      osh.getRange(orow, 1, 1, 3).setNumberFormat('@');
      osh.getRange(orow, 10, 1, 2).setNumberFormat('@');
      osh.getRange(orow, 13, 1, 2).setNumberFormat('@');
      osh.getRange(orow, 18, 1, 2).setNumberFormat('@');
      osh.getRange(orow, 1, 1, ORDER_COLS).setValues([[ts, date, ts.slice(11, 19), qty, total, text, JSON.stringify(items), path, vid,
        Utilities.getUuid().replace(/-/g, '').slice(0, 12), 'pending', '',
        meta.order_no, meta.delivery, meta.postage, r2_(total + meta.postage), meta.ship ? JSON.stringify(meta.ship) : '',
        'unpaid', '']]);
      newOrder = { ts: ts, items: items, total: total, meta: meta };
    }
    SpreadsheetApp.flush();
    res = { ok: true, counted: counted };   // public tracker never gets totals back
  } finally {
    lock.releaseLock();
  }
  // Only for a NEW order that is already written: WhatsApp notify (never fails the order)
  if (newOrder) res.whatsapp = notifyOrder_(newOrder);
  return res;
}

function orderNoRow_(no) {
  var sh = orders_(), last = sh.getLastRow();
  if (last < 2) return 0;
  var c = sh.getRange(2, 13, last - 1, 1).createTextFinder(no).matchEntireCell(true).findNext();
  return c ? c.getRow() : 0;
}

/* ---------------- WhatsApp Cloud API (optional; Script Properties only) ---------------- */
var WA_API = 'https://graph.facebook.com/v21.0/';
function waCfg_() {
  var p = PropertiesService.getScriptProperties();
  return { token: p.getProperty('WA_TOKEN') || p.getProperty('WA_ACCESS_TOKEN') || '', pid: p.getProperty('WA_PHONE_NUMBER_ID') || '',
    to: (p.getProperty('WA_TO') || '60177891688').replace(/\D/g, ''),
    holder: p.getProperty('PAY_HOLDER') || '', bank: p.getProperty('PAY_BANK') || '', acct: p.getProperty('PAY_ACCOUNT') || '',
    qr: p.getProperty('PAY_QR_URL') || '' };
}
/** Malaysian phone as typed at checkout → WhatsApp number (012… → 6012…). '' if unusable. */
function waNum_(phone) {
  var d = String(phone || '').replace(/\D/g, '');
  if (d.length < 9 || d.length > 15) return '';
  if (d.indexOf('60') === 0) return d;
  if (d.charAt(0) === '0') return '6' + d;
  if (d.charAt(0) === '1') return '60' + d;
  return d;
}
/** POST one message. Returns true only when Meta accepted it. Never throws, never logs the token. */
function waSend_(cfg, to, payload) {
  try {
    payload.messaging_product = 'whatsapp';
    payload.to = to;
    var r = UrlFetchApp.fetch(WA_API + encodeURIComponent(cfg.pid) + '/messages', {
      method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      headers: { Authorization: 'Bearer ' + cfg.token }, payload: JSON.stringify(payload) });
    var code = r.getResponseCode();
    if (code >= 200 && code < 300) return true;
    Logger.log('WhatsApp send failed: HTTP ' + code + ' ' + String(r.getContentText()).slice(0, 300));
  } catch (e) { Logger.log('WhatsApp send error: ' + String(e && e.message || e).slice(0, 200)); }
  return false;
}
/* NOTE: type "text" only works inside the 24-hour customer-service window (the recipient messaged this
 * business number in the last 24 h). Business-initiated messages outside it need an APPROVED TEMPLATE
 * ({type:"template", template:{name, language:{code:"zh_CN"}, components:[…]}}) — switch here later. */
function notifyWhatsApp_(text) {
  var cfg = waCfg_();
  if (!cfg.token || !cfg.pid || !cfg.to) return false;     // not configured: do nothing
  return waSend_(cfg, cfg.to, { type: 'text', text: { preview_url: false, body: String(text).slice(0, 4000) } });
}
function orderLines_(o) {
  var m = o.meta, l = [];
  l.push('单号：' + (m.order_no || '（无单号）'));
  l.push('时间：' + o.ts.slice(0, 10) + ' ' + o.ts.slice(11, 19) + '（马来西亚时间 UTC+8）');
  o.items.forEach(function (x) { l.push(x.c + ' ' + x.n + ' x' + x.q + '（RM' + x.p.toFixed(2) + '）'); });
  l.push('商品参考小计：RM' + o.total.toFixed(2));
  if (m.postage) l.push('邮费：RM' + m.postage.toFixed(2));
  l.push('参考合计：RM' + r2_(o.total + m.postage).toFixed(2) + (m.delivery === 'lalamove' ? '（不含 Lalamove 运费）' : ''));
  l.push('取货方式：' + (DELIVERY[m.delivery] || '未选'));
  return l;
}
/** Called once per NEW order: notify 客服, then auto-reply to the customer. Returns {shop, customer}. */
function notifyOrder_(o) {
  var out = { shop: false, customer: false };
  try {
    var cfg = waCfg_();
    if (!cfg.token || !cfg.pid) return out;
    var m = o.meta, ship = m.ship || {};
    // 1) 客服 017-789 1688
    var l = ['🧾 网站新订单（已提交，待收款）'].concat(orderLines_(o));
    if (ship.name || ship.phone) { l.push('顾客：' + (ship.name || '') + ' ' + (ship.phone || '')); }
    if (m.delivery === 'post') l.push('邮寄：' + [ship.addr, ship.pc, ship.city, ship.state].join(' '));
    l.push('请确认收款后再备货出货。');
    out.shop = notifyWhatsApp_(l.join('\n'));
    // 2) customer auto-reply (phone typed at checkout)
    var to = waNum_(ship.phone);
    if (to) {
      var c = ['感谢您在 Hunter BOOM JOHOR 下单！' + (ship.name ? '（' + ship.name + '）' : '')].concat(orderLines_(o));
      c.push('');
      if (cfg.holder && cfg.bank && cfg.acct) {
        c.push('付款资料：'); c.push('户名：' + cfg.holder); c.push('银行：' + cfg.bank); c.push('户口号码：' + cfg.acct);
        c.push('付款后请把付款截图回复到这里或 WhatsApp 017-789 1688，并注明单号。');
      } else c.push('客服会通过 WhatsApp 017-789 1688 联系您安排付款（或自取时付款）。');
      c.push('⚠️ 客服确认款项后才会备货及出货。');
      out.customer = waSend_(cfg, to, { type: 'text', text: { preview_url: false, body: c.join('\n').slice(0, 4000) } });
      // payment QR as an image message — hook, only if PAY_QR_URL is set (or switch to an uploaded media id later)
      if (out.customer && cfg.qr) waSend_(cfg, to, { type: 'image', image: { link: cfg.qr, caption: '付款 QR · 单号 ' + (m.order_no || '') } });
    }
  } catch (e) { Logger.log('notifyOrder_ error: ' + String(e && e.message || e).slice(0, 200)); }
  return out;
}

/** Orders of one Malaysia date (newest first). Reads only the tail of the orders tab. */
function ordersFor_(date) {
  var sh = orders_(), last = sh.getLastRow(), out = [];
  if (last < 2) return out;
  var row = sh.getRange(2, 2, last - 1, 1).createTextFinder(date).matchEntireCell(true).findNext();
  if (!row) return out;
  var first = row.getRow();
  var vals = sh.getRange(first, 1, last - first + 1, ORDER_COLS).getValues();
  vals.forEach(function (r) {
    if (dateStr_(r[1]) !== date) return;
    out.push(orderRow_(r));
  });
  return out.reverse().slice(0, 500);
}

/** One orders-tab row → order object for the owner page. */
function orderRow_(r) {
  var items = [], ship = null;
  try { items = JSON.parse(r[6] || '[]'); } catch (x) { items = []; }
  try { ship = r[16] ? JSON.parse(r[16]) : null; } catch (x) { ship = null; }
  var paidAt = r[18] instanceof Date ? Utilities.formatDate(r[18], TZ, "yyyy-MM-dd'T'HH:mm:ss'+08:00'") : String(r[18] || '');
  return { id: String(r[9] || ''), status: r[10] === 'done' ? 'done' : 'pending', handled_at: String(r[11] || ''),
    ts: String(r[0]), date: dateStr_(r[1]), time: String(r[2]).slice(0, 8), qty: num_(r[3]), ref_total: num_(r[4]), items: items,
    order_no: String(r[12] || ''), delivery: String(r[13] || ''), postage: num_(r[14]), grand_total: num_(r[15]) || num_(r[4]), ship: ship,
    pay_status: r[17] === 'paid' ? 'paid' : 'unpaid', paid_at: paidAt };
}

/** OWNER ONLY: find orders by 单号 (full or partial, e.g. "HBJ-20261113" or "9F4F"). Newest first, max 50. */
function find_(q) {
  q = String(q || '').toUpperCase().replace(/[^0-9A-Z-]/g, '').slice(0, 24);
  if (q.length < 3) return { ok: false, error: 'query_short' };
  var sh = orders_(), last = sh.getLastRow(), out = [];
  if (last < 2) return { ok: true, q: q, orders: out };
  var cells = sh.getRange(2, 13, last - 1, 1).createTextFinder(q).matchCase(false).findAll();
  var rows = cells.map(function (c) { return c.getRow(); }).sort(function (a, b) { return b - a; }).slice(0, 50);
  rows.forEach(function (row) { out.push(orderRow_(sh.getRange(row, 1, 1, ORDER_COLS).getValues()[0])); });
  return { ok: true, q: q, orders: out };
}

function read_(days, date) {
  days = Math.max(1, Math.min(MAX_DAYS, parseInt(days, 10) || 30));
  var sh = daily_(), map = {};
  if (sh.getLastRow() >= 2) {
    sh.getRange(2, 1, sh.getLastRow() - 1, 5).getValues().forEach(function (r) {
      var k = dateStr_(r[0]);
      map[k] = { date: k, views: num_(r[1]), visitors: num_(r[2]), orders: num_(r[3]), order_total: num_(r[4]) };
    });
  }
  var out = [], base = new Date();
  for (var i = days - 1; i >= 0; i--) {
    var k = Utilities.formatDate(new Date(base.getTime() - i * 864e5), TZ, 'yyyy-MM-dd');
    out.push(map[k] || { date: k, views: 0, visitors: 0, orders: 0, order_total: 0 });
  }
  var today = out[out.length - 1];
  var sel = /^\d{4}-\d{2}-\d{2}$/.test(String(date || '')) ? String(date) : today.date;
  var selDay = map[sel] || { date: sel, views: 0, visitors: 0, orders: 0, order_total: 0 };
  return { ok: true, tz: TZ, today: today, days: out, order_date: sel, order_day: selDay, orders: ordersFor_(sel),
    pending: pendingCount_(), generated_at: now_() };
}

/** Number of 待处理 orders over the whole log (column K). */
function pendingCount_() {
  var sh = orders_(), last = sh.getLastRow();
  if (last < 2) return 0;
  return sh.getRange(2, 11, last - 1, 1).getValues().filter(function (r) { return r[0] !== 'done'; }).length;
}

/* ---------------- owner auth (PIN in Script Properties, never in the site) ---------------- */
var SESSION_S = 21600;   // 6 h (CacheService max)
var MAX_FAILS = 8;       // wrong PINs per 15 min (global) before login is locked

function login_(b) {
  var pin = PropertiesService.getScriptProperties().getProperty('OWNER_PIN') || '';
  if (!pin) return { ok: false, error: 'pin_not_set' };
  var cache = CacheService.getScriptCache(), fails = parseInt(cache.get('pin_fails') || '0', 10);
  if (fails >= MAX_FAILS) return { ok: false, error: 'locked' };
  if (String(b.pin || '') !== pin) {
    cache.put('pin_fails', String(fails + 1), 900);
    Utilities.sleep(800);
    return { ok: false, error: 'auth' };
  }
  return { ok: true, token: newSession_(), expires_in: SESSION_S };
}
/* ---- first-time 设置后台密码 ----
 * While OWNER_PIN is unset, the owner sets it from /zwvh.html. To stop a stranger from setting it first,
 * setting it also needs a one-time 设置码 that only the owner can read: it is written into the PRIVATE
 * spreadsheet (tab「后台设置」) and logged by setup(). After a PIN is set, the code is deleted and
 * setpin is refused; OWNER_PIN stays a Script Property exactly as before (can still be set by hand). */
var PIN_MIN = 6, PIN_MAX = 32;
function setupSheet_() { return sheet_('后台设置', ['项目', '值', '说明']); }
function setupCode_() {
  var props = PropertiesService.getScriptProperties(), code = props.getProperty('SETUP_CODE');
  if (!code) {
    var A = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ', raw = Utilities.getUuid().replace(/-/g, '') + Utilities.getUuid().replace(/-/g, '');
    code = '';
    for (var i = 0; i < 10; i++) code += A[parseInt(raw.substr(i * 2, 2), 16) % 32];
    props.setProperty('SETUP_CODE', code);
    var sh = setupSheet_();
    sh.getRange(2, 1, 1, 3).setValues([['后台设置码', code, '第一次打开 /zwvh.html「设置后台密码」时输入；设置成功后自动作废。不要外传。']]);
  }
  return code;
}
function pinStatus_() {
  var set = !!PropertiesService.getScriptProperties().getProperty('OWNER_PIN');
  if (!set) setupCode_();          // make sure the owner has a code waiting in the private sheet
  return { ok: true, pin_set: set };
}
function newSession_() {
  var token = Utilities.getUuid().replace(/-/g, '') + Utilities.getUuid().replace(/-/g, '');
  CacheService.getScriptCache().put('sess_' + token, '1', SESSION_S);
  return token;
}
function validPin_(p) { p = String(p || ''); return p.length >= PIN_MIN && p.length <= PIN_MAX && !/\s/.test(p); }
function setPin_(b) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return { ok: false, error: 'busy' };
  try {
    var props = PropertiesService.getScriptProperties();
    if (props.getProperty('OWNER_PIN')) return { ok: false, error: 'pin_already_set' };
    var cache = CacheService.getScriptCache(), fails = parseInt(cache.get('pin_fails') || '0', 10);
    if (fails >= MAX_FAILS) return { ok: false, error: 'locked' };
    var code = setupCode_();
    if (String(b.code || '').toUpperCase().replace(/\s/g, '') !== code) {
      cache.put('pin_fails', String(fails + 1), 900);
      Utilities.sleep(800);
      return { ok: false, error: 'bad_code' };
    }
    if (!validPin_(b.pin)) return { ok: false, error: 'weak_pin' };
    props.setProperty('OWNER_PIN', String(b.pin));
    props.deleteProperty('SETUP_CODE');
    setupSheet_().getRange(2, 1, 1, 3).setValues([['后台设置码', '（已使用）', '后台密码已于 ' + now_() + ' 设置。忘记密码：Apps Script → 项目设置 → 脚本属性 → 修改 OWNER_PIN。']]);
    return { ok: true, token: newSession_(), expires_in: SESSION_S };
  } finally { lock.releaseLock(); }
}
/** OWNER ONLY: change the PIN (needs the current one). */
function changePin_(b) {
  var props = PropertiesService.getScriptProperties(), cur = props.getProperty('OWNER_PIN') || '';
  var cache = CacheService.getScriptCache(), fails = parseInt(cache.get('pin_fails') || '0', 10);
  if (fails >= MAX_FAILS) return { ok: false, error: 'locked' };
  if (!cur || String(b.old || '') !== cur) { cache.put('pin_fails', String(fails + 1), 900); Utilities.sleep(800); return { ok: false, error: 'bad_old' }; }
  if (!validPin_(b.pin)) return { ok: false, error: 'weak_pin' };
  props.setProperty('OWNER_PIN', String(b.pin));
  return { ok: true };
}

function authed_(b) {
  var t = String((b && b.token) || '');
  return /^[a-f0-9]{64}$/.test(t) && CacheService.getScriptCache().get('sess_' + t) === '1';
}

/** Mark an order 待处理 (pending) / 已处理 (done). */
function setStatus_(b) {
  var id = String(b.id || ''), st = b.status === 'done' ? 'done' : 'pending';
  if (!/^[a-f0-9]{12}$/.test(id)) return { ok: false, error: 'bad id' };
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return { ok: false, error: 'busy' };
  try {
    var sh = orders_(), last = sh.getLastRow();
    if (last < 2) return { ok: false, error: 'not found' };
    var cell = sh.getRange(2, 10, last - 1, 1).createTextFinder(id).matchEntireCell(true).findNext();
    if (!cell) return { ok: false, error: 'not found' };
    sh.getRange(cell.getRow(), 11, 1, 2).setValues([[st, st === 'done' ? now_() : '']]);
    return { ok: true, id: id, status: st, pending: pendingCount_() };
  } finally { lock.releaseLock(); }
}

/** OWNER ONLY: 确认收款 (paid) / 改回待收款 (unpaid). Payment must be confirmed before 备货 / 出货. */
function setPay_(b) {
  var id = String(b.id || ''), st = b.pay === 'paid' ? 'paid' : 'unpaid';
  if (!/^[a-f0-9]{12}$/.test(id)) return { ok: false, error: 'bad id' };
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return { ok: false, error: 'busy' };
  try {
    var sh = orders_(), last = sh.getLastRow();
    if (last < 2) return { ok: false, error: 'not found' };
    var cell = sh.getRange(2, 10, last - 1, 1).createTextFinder(id).matchEntireCell(true).findNext();
    if (!cell) return { ok: false, error: 'not found' };
    sh.getRange(cell.getRow(), 18, 1, 2).setNumberFormat('@');
    sh.getRange(cell.getRow(), 18, 1, 2).setValues([[st, st === 'paid' ? now_() : '']]);
    return { ok: true, id: id, pay_status: st };
  } finally { lock.releaseLock(); }
}

function doGet(e) {
  // Stats are private: reading needs POST {op:"login"} then {op:"read", token}. GET returns nothing useful.
  // (Apps Script cannot set an HTTP 401 status; the body says auth_required.)
  return json_({ ok: false, error: 'auth_required' });
}

function doPost(e) {
  try {
    var b = {};
    try { b = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (x) { return json_({ ok: false, error: 'bad json' }); }
    if (b.op === 'hit') return json_(hit_(b));                 // public, write-only, rate-limited
    if (b.op === 'login') return json_(login_(b));
    if (b.op === 'pin_status') return json_(pinStatus_());            // public: only says whether a PIN exists
    if (b.op === 'setpin') return json_(setPin_(b));                  // public, but needs the private 设置码

    if (b.op === 'logout') { if (authed_(b)) CacheService.getScriptCache().remove('sess_' + b.token); return json_({ ok: true }); }
    if (!authed_(b)) return json_({ ok: false, error: 'auth' });
    if (b.op === 'read') return json_(read_(b.days, b.date));
    if (b.op === 'status') return json_(setStatus_(b));
    if (b.op === 'pay') return json_(setPay_(b));
    if (b.op === 'find') return json_(find_(b.q));
    if (b.op === 'changepin') return json_(changePin_(b));
    return json_({ ok: false, error: 'unknown op' });
  } catch (err) { return json_({ ok: false, error: String(err) }); }
}
