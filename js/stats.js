/* Hunter BOOM JOHOR — 网站统计 tracker + private owner page (stats.html).
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
/* order hook: cart.js calls this right before window.open(WhatsApp) with a non-empty cart */
window.HBJStats = { order: function(items){
  try{
    var list = (items || []).filter(function(x){ return x && (x.c || x.n); }).slice(0, 60).map(function(x){
      return {c:String(x.c||'').slice(0,20), n:String(x.n||'').slice(0,80), q:Math.max(1, parseInt(x.q,10)||1), p:Number(x.p)||0};
    });
    if(list.length) send('order', {items:list});
  }catch(e){}
}};
var isStats = document.body && document.body.hasAttribute('data-stats-page');
/* 1 pageview per page load (the server also counts the browser as today's 1 unique visitor) */
if(!isStats){ send('view'); return; }

/* ================= private 店铺统计 / 下单记录 page ================= */
function $(id){ return document.getElementById(id); }
function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]}); }
function n(x){ return String(Number(x)||0).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
function rm(x){ return 'RM' + (Number(x)||0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
var WK = ['日','一','二','三','四','五','六'];
function wk(d){ var p = d.split('-'); return '周' + WK[new Date(Date.UTC(+p[0], +p[1]-1, +p[2])).getUTCDay()]; }
function md(d){ var p = d.split('-'); return (+p[1]) + '/' + (+p[2]); }
function tok(v){ try{ if(v === undefined) return sessionStorage.getItem(TK) || ''; if(v) sessionStorage.setItem(TK, v); else sessionStorage.removeItem(TK); }catch(e){} return v || ''; }
function post(o){
  return fetch(API, {method:'POST', redirect:'follow', cache:'no-store', headers:{'Content-Type':'text/plain;charset=UTF-8'}, body:JSON.stringify(o)})
    .then(function(r){ if(!r.ok) throw new Error('http ' + r.status); return r.json(); });
}
function status(msg, err){ var s = $('st-status'); if(s){ s.textContent = msg; s.className = 'st-status' + (err ? ' err' : ''); } }
function gate(show, msg){
  $('st-gate').hidden = !show; $('stats').hidden = show;
  var m = $('st-gmsg'); if(m){ m.textContent = msg || ''; m.className = 'st-status' + (msg ? ' err' : ''); }
  if(show){ var i = $('st-pin'); if(i){ i.value = ''; try{ i.focus(); }catch(e){} } }
}
var sel = '', last = null, filt = 'all';
function waText(o){
  var l = ['网站订单跟进（' + o.time + '，UTC+8）'];
  (o.items||[]).forEach(function(x){ l.push(x.c + ' ' + x.n + ' x' + x.q); });
  l.push(''); l.push('参考合计：' + rm(o.ref_total) + '（以店家确认为准，不含运费）');
  return l.join('\n');
}
function renderOrders(r){
  var list = r.orders || [], day = r.order_day || {orders:0, order_total:0}, d = r.order_date;
  var isToday = r.today && d === r.today.date;
  $('od-title').textContent = (isToday ? '今天 ' : '') + d + '（' + wk(d) + '）';
  $('od-count').textContent = n(day.orders);
  $('od-total').textContent = rm(day.order_total);
  var pend = list.filter(function(o){ return o.status !== 'done'; }).length;
  $('od-pend').textContent = n(pend);
  $('st-pall').textContent = n(r.pending);
  [].forEach.call(document.querySelectorAll('[data-filt]'), function(b){ b.classList.toggle('on', b.getAttribute('data-filt') === filt); });
  var show = list.filter(function(o){ return filt === 'all' || (filt === 'pending' ? o.status !== 'done' : o.status === 'done'); });
  if(!show.length){ $('od-list').innerHTML = '<div class="od-empty">' + (list.length ? '这个筛选下没有订单' : '这一天还没有从网站发出的订单') + '</div>'; return; }
  $('od-list').innerHTML = show.map(function(o){
    var done = o.status === 'done';
    var items = (o.items||[]).map(function(x){ return '<li><b>' + esc(x.c) + '</b> ' + esc(x.n) + ' <span>× ' + n(x.q) + '</span>' + (x.p ? ' <small>' + rm(x.p) + '</small>' : '') + '</li>'; }).join('');
    return '<article class="od' + (done ? ' done' : '') + '"><div class="od-h"><span class="od-t">🕒 ' + esc(o.time) + ' <small>UTC+8</small></span>' +
      '<span class="od-s">' + (done ? '✅ 已处理' + (o.handled_at ? ' <small>' + esc(String(o.handled_at).slice(11,16)) + '</small>' : '') : '⏳ 待处理') + '</span></div>' +
      '<ul>' + items + '</ul><div class="od-f"><span>共 ' + n(o.qty) + ' 件 · 参考合计 <b>' + rm(o.ref_total) + '</b></span><span class="od-b">' +
      '<a class="btn wa" href="https://wa.me/' + WA + '?text=' + encodeURIComponent(waText(o)) + '" target="_blank" rel="noopener">用 WhatsApp 跟进</a>' +
      (o.id ? '<button type="button" class="btn ' + (done ? 'ol' : 'gd') + '" data-oid="' + esc(o.id) + '" data-to="' + (done ? 'pending' : 'done') + '">' + (done ? '改回待处理' : '标记已处理') + '</button>' : '') +
      '</span></div></article>';
  }).join('');
}
function render(r){
  last = r;
  var t = r.today || {date:'', views:0, visitors:0, orders:0, order_total:0}, days = r.days || [];
  $('st-orders').textContent = n(t.orders);
  $('st-visitors').textContent = n(t.visitors);
  $('st-views').textContent = n(t.views);
  $('st-ototal').textContent = '参考合计 ' + rm(t.order_total);
  $('st-date').textContent = t.date + '（' + wk(t.date) + '，马来西亚时间 UTC+8）';
  status('已更新 ' + new Date().toLocaleTimeString('zh-CN', {timeZone:'Asia/Kuala_Lumpur', hour12:false}) + '（UTC+8）');
  /* day picker: last 30 days, newest first, with order counts */
  var dp = $('od-day');
  dp.innerHTML = days.slice().reverse().map(function(d, i){
    return '<option value="' + d.date + '"' + (d.date === r.order_date ? ' selected' : '') + '>' + (i === 0 ? '今天 ' : '') + d.date + ' ' + wk(d.date) + ' · 下单 ' + d.orders + '</option>';
  }).join('');
  renderOrders(r);
  var sum = {views:0, visitors:0, orders:0, total:0};
  days.forEach(function(d){ sum.views += d.views; sum.visitors += d.visitors; sum.orders += d.orders; sum.total += d.order_total || 0; });
  $('st-sum').textContent = '近 ' + days.length + ' 天合计：下单 ' + n(sum.orders) + ' 次（参考 ' + rm(sum.total) + '）· 人数 ' + n(sum.visitors) + ' · 浏览 ' + n(sum.views);
  /* chart: last 14 days */
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
var busy = false;
function load(){
  if(busy) return;
  if(!API){ gate(false); status('暂时无法读取：统计接口尚未连接（js/stats.js 里的 API 网址未填写）。', true); return; }
  if(!tok()){ gate(true); return; }
  busy = true;
  post({op:'read', token:tok(), days:30, date:sel})
    .then(function(r){
      busy = false;
      if(r && r.ok){ gate(false); render(r); return; }
      if(r && r.error === 'auth'){ tok(null); gate(true, '登录已过期，请重新输入密码。'); return; }
      throw new Error('bad');
    })
    .catch(function(){ busy = false; gate(false); status('暂时无法读取统计数据，请稍后刷新。', true); });
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
    gate(true, r && r.error === 'locked' ? '密码错误次数过多，请 15 分钟后再试。' : (r && r.error === 'pin_not_set' ? '后台还没有设置密码（OWNER_PIN）。' : '密码不正确。'));
  }).catch(function(){ b.disabled = false; b.textContent = '进入'; gate(true, '暂时无法连接，请稍后再试。'); });
});
$('st-out').addEventListener('click', function(){ var t = tok(); tok(null); if(t && API) post({op:'logout', token:t}).catch(function(){}); gate(true); });
$('od-day').addEventListener('change', function(){ sel = this.value; load(); });
document.addEventListener('click', function(e){
  var f = e.target.closest && e.target.closest('[data-filt]');
  if(f){ filt = f.getAttribute('data-filt'); if(last) renderOrders(last); return; }
  var tr = e.target.closest && e.target.closest('tr[data-day]');
  if(tr){ sel = tr.getAttribute('data-day'); load(); var o = $('orders'); if(o) o.scrollIntoView({behavior:'smooth'}); return; }
  var b = e.target.closest && e.target.closest('[data-oid]');
  if(b){
    b.disabled = true;
    post({op:'status', token:tok(), id:b.getAttribute('data-oid'), status:b.getAttribute('data-to')}).then(function(r){
      if(r && r.ok){ load(); return; }
      if(r && r.error === 'auth'){ tok(null); gate(true, '登录已过期，请重新输入密码。'); return; }
      b.disabled = false; status('更新失败，请再试一次。', true);
    }).catch(function(){ b.disabled = false; status('更新失败，请再试一次。', true); });
  }
});
load();
setInterval(function(){ if(!document.hidden && tok()) load(); }, 60000);
})();
