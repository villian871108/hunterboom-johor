/* Hunter BOOM JOHOR — 网站统计 tracker + private owner page (zwvh.html).
 * Real hits only, no fake numbers. Backend: Google Apps Script web app (tools/stats_api.gs).
 * Visitors get an anonymous random id in localStorage; no IP, name or phone is sent.
 * The public tracker can only ADD counts; reading anything needs the owner PIN (checked server-side). */
(function(){
'use strict';
/* ===== PASTE the deployed Apps Script Web App URL here (…/exec). Empty = tracking off. ===== */
var API = "https://script.google.com/macros/s/AKfycbxD5lZUXh1E0tjAEkGQD_NIJmOsUczKiD5y4tznS6Y5x_XMBHUW_7VfsRXbcFEXnvhMIg/exec";
/* ========================================================================================== */
var WA = '60177891688', VK = 'hbj_vid_v1', TK = 'hbj_stats_token';
function vid(){
  try{
    var v = localStorage.getItem(VK);
    if(!v || !/^[a-z0-9]{8,40}$/.test(v)){
      var a = new Uint8Array(12), s = '';
      (window.crypto || window.msCrypto).getRandomValues(a);
      for(var i=0;i<a.length;i++) s += (a[i] % 36).toString(36);
      v = s + Date.now().toString(36);
      localStorage.setItem(VK, v);
    }
    return v;
  }catch(e){ return 'nols' + Math.random().toString(36).slice(2, 14); }
}
function send(type, extra){
  try{
    if(!API) return;
    var body = JSON.stringify({op:'hit', type:type, vid:vid(), host:location.hostname, path:(location.pathname||'/').slice(0,200), extra:extra||null});
    var ok = false;
    if(navigator.sendBeacon){ try{ ok = navigator.sendBeacon(API, new Blob([body], {type:'text/plain;charset=UTF-8'})); }catch(e){ ok = false; } }
    if(!ok && window.fetch){ fetch(API, {method:'POST', mode:'no-cors', keepalive:true, headers:{'Content-Type':'text/plain;charset=UTF-8'}, body:body}).catch(function(){}); }
  }catch(e){}
}
/* order hook: cart.js calls this right before window.open(WhatsApp) with the order record
 *   {order_no, time, delivery, delivery_label, ship, items:[{c,n,m,t,u,q,p,line}], subtotal, postage, total}
 * (an old-style plain items array is still accepted). Optional fields order_no / delivery / ship / postage
 * are only stored by the updated tools/stats_api.gs; an older deployment simply ignores them.
 * The 散装 / 整盒 unit is also written into the item name, so even the old sheet shows it. */
var DLV_T = {pickup:'自取（Sutera Mall）', lalamove:'Lalamove（联系客服安排）', post:'邮寄'};
var SHIP_F = [['name','收件人姓名'],['phone','电话'],['addr','地址'],['pc','邮区编号'],['city','城市'],['state','州属']];
window.HBJStats = { order: function(o){
  try{
    if(Object.prototype.toString.call(o) === '[object Array]') o = {items:o};
    o = o || {};
    var list = (o.items || []).filter(function(x){ return x && (x.c || x.n); }).slice(0, 60).map(function(x){
      var n = String(x.n||'') + (x.t ? '（' + x.t + '）' : '');
      return {c:String(x.c||'').slice(0,20), n:n.slice(0,80), q:Math.max(1, parseInt(x.q,10)||1), p:Number(x.p)||0, m:String(x.m||'').slice(0,2)};
    });
    if(!list.length) return;
    var ex = {items:list};
    if(o.order_no) ex.order_no = String(o.order_no).slice(0,24);
    if(DLV_T[o.delivery]){
      ex.delivery = o.delivery;
      ex.postage = o.delivery === 'post' ? 15 : 0;
      if(o.delivery === 'post' && o.ship){ ex.ship = {}; SHIP_F.forEach(function(f){ ex.ship[f[0]] = String(o.ship[f[0]]||'').slice(0,200); }); }
    }
    send('order', ex);
  }catch(e){}
}};
var isStats = document.body && document.body.hasAttribute('data-stats-page');
/* 1 pageview per page load (the server also counts the browser as today's 1 unique visitor) */
if(!isStats){ send('view'); return; }

/* ================= private 店家后台 page (zwvh.html): sales, 单号 lookup, 出货单, visitors ================= */
function $(id){ return document.getElementById(id); }
function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]}); }
function n(x){ return String(Number(x)||0).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
function rm(x){ return 'RM' + (Number(x)||0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
function r2(x){ return Math.round((Number(x)||0)*100)/100; }
var WK = ['日','一','二','三','四','五','六'];
function wk(d){ var p = d.split('-'); return '周' + WK[new Date(Date.UTC(+p[0], +p[1]-1, +p[2])).getUTCDay()]; }
function md(d){ var p = d.split('-'); return (+p[1]) + '/' + (+p[2]); }
function tok(v){ try{ if(v === undefined) return sessionStorage.getItem(TK) || ''; if(v) sessionStorage.setItem(TK, v); else sessionStorage.removeItem(TK); }catch(e){} return v || ''; }
function post(o){
  return fetch(API, {method:'POST', redirect:'follow', cache:'no-store', headers:{'Content-Type':'text/plain;charset=UTF-8'}, body:JSON.stringify(o)})
    .then(function(r){ if(!r.ok) throw new Error('http ' + r.status); return r.json(); });
}
function status(msg, err){ var s = $('st-status'); if(s){ s.textContent = msg; s.className = 'st-status' + (err ? ' err' : ''); } }
function gmsg(msg, err){ var m = $('st-gmsg'); if(m){ m.textContent = msg || ''; m.className = 'st-status' + (msg && err !== false ? ' err' : ''); } }
/* gate: mode "login" | "setup"; the dashboard stays hidden (and empty) until the server accepts a token */
function gate(show, msg, mode){
  $('st-gate').hidden = !show; $('stats').hidden = show;
  if(show){
    var su = mode === 'setup';
    $('st-lg').hidden = su; $('st-su').hidden = !su;
    gmsg(msg);
    var i = $(su ? 'su-code' : 'st-pin'); if(i){ if(!su) i.value = ''; try{ i.focus(); }catch(e){} }
  }
}
/* ---- order helpers ---- */
var UNIT = {l:'散装', b:'整盒', s:'单件'};
function unitOf(x){ if(UNIT[x.m]) return UNIT[x.m]; var m = /（(散装|整盒)）$/.exec(x.n||''); return m ? m[1] : ''; }
function baseName(x){ return String(x.n||'').replace(/（(散装|整盒)）$/, ''); }
function uWord(x){ var u = unitOf(x); return u === '整盒' ? '盒' : '件'; }
function oPost(o){ return o.delivery === 'post' ? (Number(o.postage) || 15) : 0; }
function oGrand(o){ return r2((Number(o.ref_total)||0) + oPost(o)); }
function dlvText(o){ return DLV_T[o.delivery] || ''; }
function waText(o){
  var l = [];
  if(o.order_no) l.push('单号：' + o.order_no);
  l.push('网站订单跟进（' + (o.date ? o.date + ' ' : '') + o.time + '，UTC+8）');
  (o.items||[]).forEach(function(x){ var u = unitOf(x); l.push(x.c + ' ' + baseName(x) + (u && u !== '单件' ? ' ' + u : '') + ' x' + x.q); });
  l.push(''); l.push('商品参考小计：' + rm(o.ref_total));
  if(o.delivery === 'post'){ l.push('邮费：' + rm(oPost(o))); l.push('参考合计：' + rm(oGrand(o)) + '（以店家确认为准）'); }
  else l.push('参考合计：' + rm(o.ref_total) + '（以店家确认为准' + (o.delivery === 'lalamove' ? '，不含 Lalamove 运费' : '') + '）');
  if(dlvText(o)){ l.push(''); l.push('取货方式：' + dlvText(o)); }
  if(o.delivery === 'post' && o.ship){ l.push('邮寄资料：'); SHIP_F.forEach(function(f){ l.push(f[1] + '：' + (o.ship[f[0]] || '')); }); }
  return l.join('\n');
}
function dlvHtml(o){
  var h = '';
  if(dlvText(o)) h += '<p class="od-d">🚚 ' + esc(dlvText(o)) + (o.delivery === 'post' ? ' · 邮费 ' + rm(oPost(o)) : '') + '</p>';
  else h += '<p class="od-d od-na">🚚 取货方式：未记录（旧订单或统计接口未更新）</p>';
  if(o.delivery === 'post' && o.ship){
    h += '<dl class="od-ship">' + SHIP_F.map(function(f){ return '<dt>' + f[1] + '</dt><dd>' + esc(o.ship[f[0]] || '') + '</dd>'; }).join('') + '</dl>';
  }
  return h;
}
var shown = {};   /* id → order, for the 出货单 popup and status buttons */
function orderCard(o){
  var done = o.status === 'done';
  if(o.id) shown[o.id] = o;
  var items = (o.items||[]).map(function(x){ var u = unitOf(x);
    return '<li><b>' + esc(x.c) + '</b> ' + esc(baseName(x)) + (u ? '<span class="tg">' + u + '</span>' : '') + ' <span>× ' + n(x.q) + '</span>' + (x.p ? ' <small>' + rm(x.p) + '/' + uWord(x) + ' = ' + rm(x.p * x.q) + '</small>' : '') + '</li>'; }).join('');
  var no = o.order_no ? '<button type="button" class="od-no" data-slip="' + esc(o.id) + '" title="打开出货单">' + esc(o.order_no) + '</button> ' : '<b class="od-no od-na">无单号</b> ';
  return '<article class="od' + (done ? ' done' : '') + '"><div class="od-h"><span class="od-t">' + no + '🕒 ' + (o.date ? esc(o.date.slice(5)) + ' ' : '') + esc(o.time) + ' <small>UTC+8</small></span>' +
    '<span class="od-s">' + (done ? '✅ 已处理' + (o.handled_at ? ' <small>' + esc(String(o.handled_at).slice(11,16)) + '</small>' : '') : '⏳ 待处理') + '</span></div>' +
    '<ul>' + items + '</ul>' + dlvHtml(o) + '<div class="od-f"><span>商品 <b>' + rm(o.ref_total) + '</b>' + (oPost(o) ? ' + 邮费 ' + rm(oPost(o)) : '') + ' = 合计 <b>' + rm(oGrand(o)) + '</b></span><span class="od-b">' +
    (o.id ? '<button type="button" class="btn ol" data-slip="' + esc(o.id) + '">出货单</button>' : '') +
    '<a class="btn wa" href="https://wa.me/' + WA + '?text=' + encodeURIComponent(waText(o)) + '" target="_blank" rel="noopener">用 WhatsApp 跟进</a>' +
    (o.id ? '<button type="button" class="btn ' + (done ? 'ol' : 'gd') + '" data-oid="' + esc(o.id) + '" data-to="' + (done ? 'pending' : 'done') + '">' + (done ? '改回待处理' : '标记已处理') + '</button>' : '') +
    '</span></div></article>';
}
/* full 出货单 popup (print-friendly) */
function slip(o){
  var rows = (o.items||[]).map(function(x){ var u = unitOf(x) || '—';
    return '<tr><td>' + esc(x.c) + '</td><td>' + esc(baseName(x)) + '</td><td>' + u + '</td><td class="n">' + n(x.q) + ' ' + uWord(x) + '</td><td class="n">' + rm(x.p) + '</td><td class="n">' + rm(x.p * x.q) + '</td></tr>'; }).join('');
  var ship = (o.delivery === 'post' && o.ship) ? '<h3>📦 邮寄资料</h3><dl class="od-ship">' + SHIP_F.map(function(f){ return '<dt>' + f[1] + '</dt><dd>' + esc(o.ship[f[0]] || '') + '</dd>'; }).join('') + '</dl>' : '';
  $('st-slip-in').innerHTML = '<h2>🧾 出货单 ' + esc(o.order_no || '（无单号）') + '</h2>' +
    '<p>下单时间：' + esc((o.date || '') + ' ' + o.time) + '（马来西亚时间 UTC+8）<br>取货方式：<b>' + esc(dlvText(o) || '未记录') + '</b>' +
    (o.delivery === 'lalamove' ? '（新山区 Lalamove 运费自付，客服联系安排）' : o.delivery === 'pickup' ? '（客服约自取时间）' : '') +
    '<br>状态：' + (o.status === 'done' ? '✅ 已处理' : '⏳ 待处理') + '</p>' + ship +
    '<div style="overflow-x:auto"><table><thead><tr><th>编号</th><th>名称</th><th>散装/整盒</th><th class="n">数量</th><th class="n">参考单价</th><th class="n">小计</th></tr></thead><tbody>' + rows + '</tbody></table></div>' +
    '<p class="tot">商品小计 ' + rm(o.ref_total) + (oPost(o) ? '<br>邮费（西马邮寄，任买）' + rm(oPost(o)) : '') + '<br>合计 <b>' + rm(oGrand(o)) + '</b>' + (o.delivery === 'lalamove' ? '<br><small>不含 Lalamove 运费</small>' : '') + '</p>' +
    '<p class="st-status">价格为网站参考价，以店家确认为准。</p>' +
    '<div class="bar"><a class="btn wa" href="https://wa.me/' + WA + '?text=' + encodeURIComponent(waText(o)) + '" target="_blank" rel="noopener">用 WhatsApp 跟进</a><button type="button" class="btn gd" data-print>打印 / 存 PDF</button><button type="button" class="btn ol" data-slip-close>关闭</button></div>';
  $('st-slip').hidden = false;
}
/* breakdown of the selected day, computed only from the recorded orders */
function breakdown(list){
  if(!list.length){ $('od-brk').innerHTML = ''; return; }
  var dv = {}, pr = {}, keys = [];
  list.forEach(function(o){
    var k = dlvText(o) || '未记录';
    dv[k] = dv[k] || {c:0, s:0, p:0}; dv[k].c++; dv[k].s += Number(o.ref_total)||0; dv[k].p += oPost(o);
    (o.items||[]).forEach(function(x){ var u = unitOf(x), id = x.c + '|' + u;
      if(!pr[id]){ pr[id] = {c:x.c, n:baseName(x), u:u, q:0, s:0}; keys.push(id); }
      pr[id].q += Number(x.q)||0; pr[id].s += (Number(x.p)||0) * (Number(x.q)||0); });
  });
  keys.sort(function(a, b){ return pr[b].s - pr[a].s; });
  var t1 = '<table><caption>按取货方式</caption><thead><tr><th>方式</th><th>单数</th><th>商品</th><th>邮费</th></tr></thead><tbody>' +
    Object.keys(dv).map(function(k){ return '<tr><td>' + esc(k) + '</td><td>' + dv[k].c + '</td><td>' + rm(dv[k].s) + '</td><td>' + rm(dv[k].p) + '</td></tr>'; }).join('') + '</tbody></table>';
  var t2 = '<table><caption>按产品（前 10）</caption><thead><tr><th>产品</th><th>数量</th><th>参考金额</th></tr></thead><tbody>' +
    keys.slice(0, 10).map(function(id){ var x = pr[id]; return '<tr><td><b>' + esc(x.c) + '</b> ' + esc(x.n) + (x.u ? ' <small>' + x.u + '</small>' : '') + '</td><td>' + n(x.q) + '</td><td>' + rm(x.s) + '</td></tr>'; }).join('') + '</tbody></table>';
  $('od-brk').innerHTML = t1 + t2;
}
var sel = '', last = null, filt = 'all';
function renderOrders(r){
  var list = r.orders || [], day = r.order_day || {orders:0, order_total:0}, d = r.order_date;
  var isToday = r.today && d === r.today.date;
  $('od-title').textContent = (isToday ? '今天 ' : '') + d + '（' + wk(d) + '）';
  var postSum = list.reduce(function(s, o){ return s + oPost(o); }, 0);
  $('od-count').textContent = n(day.orders);
  $('od-total').textContent = rm(day.order_total);
  $('od-post').textContent = rm(postSum);
  $('od-grand').textContent = rm((Number(day.order_total)||0) + postSum);
  var pend = list.filter(function(o){ return o.status !== 'done'; }).length;
  $('od-pend').textContent = n(pend);
  $('st-pall').textContent = n(r.pending);
  breakdown(list);
  [].forEach.call(document.querySelectorAll('[data-filt]'), function(b){ b.classList.toggle('on', b.getAttribute('data-filt') === filt); });
  var show = list.filter(function(o){ return filt === 'all' || (filt === 'pending' ? o.status !== 'done' : o.status === 'done'); });
  if(!show.length){ $('od-list').innerHTML = '<div class="od-empty">' + (list.length ? '这个筛选下没有订单' : '这一天还没有从网站发出的订单') + '</div>'; return; }
  $('od-list').innerHTML = show.map(orderCard).join('');
}
function render(r){
  last = r;
  var t = r.today || {date:'', views:0, visitors:0, orders:0, order_total:0}, days = r.days || [];
  $('st-orders').textContent = n(t.orders);
  $('st-sales').textContent = rm(t.order_total);
  $('st-visitors').textContent = n(t.visitors);
  $('st-views').textContent = n(t.views);
  $('st-ototal').textContent = '商品参考合计（不含邮费）';
  $('st-date').textContent = t.date + '（' + wk(t.date) + '，马来西亚时间 UTC+8）';
  status('已更新 ' + new Date().toLocaleTimeString('zh-CN', {timeZone:'Asia/Kuala_Lumpur', hour12:false}) + '（UTC+8）');
  var dp = $('od-day');
  dp.innerHTML = days.slice().reverse().map(function(d, i){
    return '<option value="' + d.date + '"' + (d.date === r.order_date ? ' selected' : '') + '>' + (i === 0 ? '今天 ' : '') + d.date + ' ' + wk(d.date) + ' · 下单 ' + d.orders + ' · ' + rm(d.order_total) + '</option>';
  }).join('');
  renderOrders(r);
  var sum = {views:0, visitors:0, orders:0, total:0};
  days.forEach(function(d){ sum.views += d.views; sum.visitors += d.visitors; sum.orders += d.orders; sum.total += d.order_total || 0; });
  $('st-sum').textContent = '近 ' + days.length + ' 天合计：下单 ' + n(sum.orders) + ' 次 · 商品参考销售 ' + rm(sum.total) + ' · 人数 ' + n(sum.visitors) + ' · 浏览 ' + n(sum.views);
  var cd = days.slice(-14), mx = 1;
  cd.forEach(function(d){ mx = Math.max(mx, d.views, d.visitors); });
  var W = 700, H = 220, pad = 26, bw = (W - pad*2) / Math.max(1, cd.length), svg = [];
  svg.push('<svg viewBox="0 0 '+W+' '+(H+40)+'" role="img" aria-label="近 14 天浏览与人数柱状图">');
  svg.push('<line x1="'+pad+'" y1="'+H+'" x2="'+(W-pad)+'" y2="'+H+'" stroke="#f1dcc0"/>');
  cd.forEach(function(d, i){
    var x = pad + i*bw, hv = Math.round((d.views/mx)*(H-30)), hu = Math.round((d.visitors/mx)*(H-30)), w = Math.max(4, bw*0.36);
    svg.push('<rect x="'+(x+bw*0.12)+'" y="'+(H-hv)+'" width="'+w+'" height="'+hv+'" rx="3" fill="#f6c453"><title>'+d.date+' 浏览 '+d.views+'</title></rect>');
    svg.push('<rect x="'+(x+bw*0.12+w+2)+'" y="'+(H-hu)+'" width="'+w+'" height="'+hu+'" rx="3" fill="#c8161d"><title>'+d.date+' 人数 '+d.visitors+'</title></rect>');
    if(d.orders) svg.push('<text x="'+(x+bw/2)+'" y="'+(H-Math.max(hv,hu)-6)+'" text-anchor="middle" font-size="12" font-weight="700" fill="#1fae55">🛒'+d.orders+'</text>');
    svg.push('<text x="'+(x+bw/2)+'" y="'+(H+18)+'" text-anchor="middle" font-size="11" fill="#8a5a4a">'+md(d.date)+'</text>');
  });
  svg.push('</svg>');
  $('st-chart').innerHTML = svg.join('');
  $('st-rows').innerHTML = days.slice().reverse().map(function(d, i){
    return '<tr data-day="'+d.date+'"'+(i===0?' class="today"':'')+'><td>'+d.date+' <small>'+wk(d.date)+(i===0?' · 今天':'')+'</small></td><td><a href="#orders">'+n(d.orders)+'</a></td><td>'+rm(d.order_total)+'</td><td>'+n(d.visitors)+'</td><td>'+n(d.views)+'</td></tr>';
  }).join('');
}
function authFail(r){ if(r && r.error === 'auth'){ tok(null); start('登录已过期，请重新输入密码。'); return true; } return false; }
var busy = false;
function load(){
  if(busy) return;
  if(!API){ gate(false); status('暂时无法读取：统计接口尚未连接（js/stats.js 里的 API 网址未填写）。', true); return; }
  if(!tok()){ start(); return; }
  busy = true;
  post({op:'read', token:tok(), days:30, date:sel})
    .then(function(r){
      busy = false;
      if(r && r.ok){ gate(false); render(r); return; }
      if(authFail(r)) return;
      throw new Error('bad');
    })
    .catch(function(){ busy = false; gate(false); status('暂时无法读取统计数据，请稍后刷新。', true); });
}
/* entry: ask the server whether a PIN exists → login form, or first-time 设置后台密码 */
function start(msg){
  if(!API){ gate(true, '暂时无法读取：统计接口尚未连接。'); return; }
  gate(true, msg || '', 'login');
  post({op:'pin_status'}).then(function(r){
    if(r && r.ok && r.pin_set === false) gate(true, msg || '', 'setup');
  }).catch(function(){});   /* older API without pin_status: keep the login form */
}
$('st-login').addEventListener('submit', function(e){
  e.preventDefault();
  var pin = $('st-pin').value, b = $('st-go');
  if(!pin) return;
  if(!API){ gate(true, '暂时无法读取：统计接口尚未连接。'); return; }
  b.disabled = true; b.textContent = '验证中…';
  post({op:'login', pin:pin}).then(function(r){
    b.disabled = false; b.textContent = '进入';
    if(r && r.ok && r.token){ tok(r.token); load(); return; }
    if(r && r.error === 'pin_not_set'){ start('后台密码还没设置。'); return; }
    gate(true, r && r.error === 'locked' ? '密码错误次数过多，请 15 分钟后再试。' : '密码不正确。', 'login');
  }).catch(function(){ b.disabled = false; b.textContent = '进入'; gate(true, '暂时无法连接，请稍后再试。', 'login'); });
});
$('st-setup').addEventListener('submit', function(e){
  e.preventDefault();
  var code = $('su-code').value.trim(), p1 = $('su-pin').value, p2 = $('su-pin2').value, b = $('su-go');
  if(!code){ gmsg('请输入设置码（在 Google 表格「后台设置」分页）。'); return; }
  if(p1.length < 6 || /\s/.test(p1)){ gmsg('密码至少 6 位，不能有空格。'); return; }
  if(p1 !== p2){ gmsg('两次输入的密码不一样。'); return; }
  b.disabled = true; b.textContent = '设置中…';
  post({op:'setpin', code:code, pin:p1}).then(function(r){
    b.disabled = false; b.textContent = '设置密码并进入';
    if(r && r.ok && r.token){ $('su-pin').value = $('su-pin2').value = ''; tok(r.token); load(); return; }
    var m = {bad_code:'设置码不正确。', weak_pin:'密码至少 6 位，不能有空格。', locked:'错误次数过多，请 15 分钟后再试。'}[r && r.error];
    if(r && r.error === 'pin_already_set'){ gate(true, '后台密码已经设置过，请直接输入密码登录。', 'login'); return; }
    gmsg(m || '暂时无法设置，请稍后再试。');
  }).catch(function(){ b.disabled = false; b.textContent = '设置密码并进入'; gmsg('暂时无法连接，请稍后再试。'); });
});
$('st-chg').addEventListener('submit', function(e){
  e.preventDefault();
  var o = $('pw-old').value, p1 = $('pw-new').value, p2 = $('pw-new2').value, m = $('pw-msg');
  function say(t, bad){ m.textContent = t; m.className = 'st-status' + (bad ? ' err' : ''); }
  if(p1.length < 6 || /\s/.test(p1)){ say('新密码至少 6 位，不能有空格。', 1); return; }
  if(p1 !== p2){ say('两次输入的新密码不一样。', 1); return; }
  post({op:'changepin', token:tok(), old:o, pin:p1}).then(function(r){
    if(r && r.ok){ say('✅ 已改好，下次登录用新密码。'); $('pw-old').value = $('pw-new').value = $('pw-new2').value = ''; return; }
    if(authFail(r)) return;
    say({bad_old:'当前密码不正确。', weak_pin:'新密码至少 6 位，不能有空格。', locked:'错误次数过多，请 15 分钟后再试。'}[r && r.error] || '暂时无法修改（统计接口可能还没更新）。', 1);
  }).catch(function(){ say('暂时无法连接，请稍后再试。', 1); });
});
$('st-find').addEventListener('submit', function(e){
  e.preventDefault();
  var q = $('fq').value.trim().toUpperCase(), out = $('find-res');
  if(q.length < 3){ out.innerHTML = '<p class="st-status err">请输入单号，至少 3 个字（例如后 4 位）。</p>'; return; }
  out.innerHTML = '<p class="st-status">查找中…</p>';
  post({op:'find', token:tok(), q:q}).then(function(r){
    if(authFail(r)) return;
    if(!r || !r.ok){ out.innerHTML = '<p class="st-status err">' + (r && r.error === 'unknown op' ? '统计接口还没更新到新版，暂时不能查单号（见 tools/STATS.md）。' : '查找失败，请再试一次。') + '</p>'; return; }
    var list = r.orders || [];
    out.innerHTML = '<p class="st-status">「' + esc(r.q) + '」找到 ' + list.length + ' 单' + (list.length >= 50 ? '（只显示最新 50 单）' : '') + ' · <button type="button" class="st-out" data-find-clear>清除</button></p>' + list.map(orderCard).join('');
    if(list.length === 1 && list[0].order_no === q) slip(list[0]);
  }).catch(function(){ out.innerHTML = '<p class="st-status err">查找失败，请再试一次。</p>'; });
});
$('st-out').addEventListener('click', function(){ var t = tok(); tok(null); if(t && API) post({op:'logout', token:t}).catch(function(){}); $('od-list').innerHTML = ''; $('find-res').innerHTML = ''; $('st-slip').hidden = true; start(); });
$('od-day').addEventListener('change', function(){ sel = this.value; load(); });
document.addEventListener('keydown', function(e){ if(e.key === 'Escape') $('st-slip').hidden = true; });
document.addEventListener('click', function(e){
  var c = e.target.closest && e.target.closest('[data-slip-close]');
  if(c || e.target === $('st-slip')){ $('st-slip').hidden = true; return; }
  if(e.target.closest && e.target.closest('[data-print]')){ window.print(); return; }
  if(e.target.closest && e.target.closest('[data-find-clear]')){ $('find-res').innerHTML = ''; $('fq').value = ''; return; }
  var sl = e.target.closest && e.target.closest('[data-slip]');
  if(sl){ var o = shown[sl.getAttribute('data-slip')]; if(o) slip(o); return; }
  var f = e.target.closest && e.target.closest('[data-filt]');
  if(f){ filt = f.getAttribute('data-filt'); if(last) renderOrders(last); return; }
  var tr = e.target.closest && e.target.closest('tr[data-day]');
  if(tr){ sel = tr.getAttribute('data-day'); load(); var o2 = $('orders'); if(o2) o2.scrollIntoView({behavior:'smooth'}); return; }
  var b = e.target.closest && e.target.closest('[data-oid]');
  if(b){
    b.disabled = true;
    post({op:'status', token:tok(), id:b.getAttribute('data-oid'), status:b.getAttribute('data-to')}).then(function(r){
      if(r && r.ok){ load(); var fr = $('find-res'); if(fr && fr.innerHTML && $('fq').value) $('st-find').dispatchEvent(new Event('submit', {cancelable:true})); return; }
      if(authFail(r)) return;
      b.disabled = false; status('更新失败，请再试一次。', true);
    }).catch(function(){ b.disabled = false; status('更新失败，请再试一次。', true); });
  }
});
load();
setInterval(function(){ if(!document.hidden && tok()) load(); }, 60000);
})();
