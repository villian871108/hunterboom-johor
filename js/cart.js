/* Hunter BOOM JOHOR — cart & WhatsApp ordering (order reported to js/stats.js)
 * Cart lines are keyed by SKU + unit mode, so 散装 and 整盒 of the same product never merge:
 *   m "l" 散装 (per piece) · "b" 整盒 (per box, 价目表箱价) · "s" 单件 (1/1 products)
 * Checkout: the customer must pick exactly one 取货方式; 邮寄 needs full 邮寄资料 and adds RM15 postage.
 * Each send gets an order number 单号 HBJ-YYYYMMDD-XXXX (Malaysia date, UTC+8). */
(function(){
'use strict';
var WA='60177891688',K='hbj_cart_v2',SK='hbj_ship_v1',LK='hbj_last_order_v1',POST_FEE=15;
try{localStorage.removeItem('hbj_cart_v1')}catch(e){} /* old cart held wholesale carton prices */
var root=document.body.getAttribute('data-root')||'';
var MODES={l:{t:'散装',u:'件'},b:{t:'整盒',u:'盒'},s:{t:'',u:'件'}};
var DLV={
  pickup:{t:'自取（Sutera Mall）',h:'请先 WhatsApp 约时间'},
  lalamove:{t:'Lalamove（联系客服安排）',h:'新山区 Lalamove 运费自付'},
  post:{t:'邮寄',h:'西马邮费一律 RM15（任买），需填写邮寄资料'}
};
var SHIP_F=[['name','收件人姓名'],['phone','电话'],['addr','地址'],['pc','邮区编号'],['city','城市'],['state','州属']];
var STATES=['Johor 柔佛','Kedah 吉打','Kelantan 吉兰丹','Melaka 马六甲','Negeri Sembilan 森美兰','Pahang 彭亨','Perak 霹雳','Perlis 玻璃市','Pulau Pinang 槟城','Selangor 雪兰莪','Terengganu 登嘉楼','Kuala Lumpur 吉隆坡','Putrajaya 布城'];
function md(m){return MODES[m]||MODES.b}
function key(c,m){return c+'|'+m}
function ld(){try{var a=JSON.parse(localStorage.getItem(K)||'[]');return Array.isArray(a)?a.filter(function(x){return x&&x.c&&MODES[x.m]}):[]}catch(e){return []}}
function hideOk(){var k=document.getElementById('dwok');if(k)k.hidden=true}
function sv(a){try{localStorage.setItem(K,JSON.stringify(a))}catch(e){}hideOk();render()}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function r2(n){return Math.round((Number(n)||0)*100)/100}
function rm(n){return 'RM'+Number(n||0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,',')}
function total(a){return r2(a.reduce(function(s,x){return s+(x.p||0)*x.q},0))}
function count(a){return a.reduce(function(s,x){return s+x.q},0)}
function waUrl(t){return 'https://wa.me/'+WA+'?text='+encodeURIComponent(t)}
function ss(v){try{if(v===undefined)return JSON.parse(sessionStorage.getItem(SK)||'{}')||{};sessionStorage.setItem(SK,JSON.stringify(v))}catch(e){}return v||{}}
/* ---- 单号 HBJ-YYYYMMDD-XXXX: Malaysia date + 4 random chars (32-char alphabet, no 0/O/1/I) ---- */
function myNow(){var d=new Date(Date.now()+8*36e5),p=function(n){return(n<10?'0':'')+n};
  return{ymd:d.getUTCFullYear()+p(d.getUTCMonth()+1)+p(d.getUTCDate()),
         txt:d.getUTCFullYear()+'-'+p(d.getUTCMonth()+1)+'-'+p(d.getUTCDate())+' '+p(d.getUTCHours())+':'+p(d.getUTCMinutes())+':'+p(d.getUTCSeconds())}}
function newNo(ymd){var A='23456789ABCDEFGHJKLMNPQRSTUVWXYZ',s='',b=new Uint8Array(4),i;
  try{(window.crypto||window.msCrypto).getRandomValues(b)}catch(e){for(i=0;i<4;i++)b[i]=Math.floor(Math.random()*256)}
  for(i=0;i<4;i++)s+=A[b[i]%32];return 'HBJ-'+ymd+'-'+s}
/* ---- order record (also sent to stats.js → Google Sheet, and fileable by tools/file_order.py) ---- */
function build(a,dv,ship){
  var now=myNow(),sub=total(a),post=dv==='post'?POST_FEE:0;
  var lines=a.map(function(x){var m=md(x.m);return{c:x.c,n:x.n,m:x.m,t:m.t,u:m.u,q:x.q,p:r2(x.p),line:r2(x.p*x.q)}});
  var o={order_no:'',time:now.txt,tz:'Asia/Kuala_Lumpur (UTC+8)',delivery:dv,delivery_label:DLV[dv].t,
         ship:dv==='post'?ship:null,items:lines,subtotal:sub,postage:post,total:r2(sub+post)};
  /* same cart + same delivery sent again (e.g. WhatsApp did not open) keeps the same 单号 */
  var sig=JSON.stringify([lines,dv,o.ship]),last={};
  try{last=JSON.parse(localStorage.getItem(LK)||'{}')||{}}catch(e){}
  o.resend=!!(last.sig===sig&&last.no&&last.no.indexOf('HBJ-'+now.ymd+'-')===0);
  o.order_no=o.resend?last.no:newNo(now.ymd);
  try{localStorage.setItem(LK,JSON.stringify({no:o.order_no,sig:sig}))}catch(e){}
  return o;
}
function lineTxt(x){return x.c+' '+x.n+(x.t?' '+x.t:'')+' x'+x.q+'（'+rm(x.p)+'/'+x.u+'，小计 '+rm(x.line)+'）'}
function msg(o){
  var l=['单号：'+o.order_no,'我要下单（'+o.time+'，马来西亚时间）',''];
  o.items.forEach(function(x){l.push(lineTxt(x))});
  l.push('');
  l.push('商品参考小计：'+rm(o.subtotal));
  if(o.delivery==='post')l.push('邮费：'+rm(o.postage)+'（西马邮寄，任买）');
  l.push('参考合计：'+rm(o.total)+'（产品价格以店家确认为准'+(o.delivery==='lalamove'?'，不含 Lalamove 运费':'')+'）');
  l.push('');
  l.push('取货方式：'+o.delivery_label);
  if(o.delivery==='pickup')l.push('请客服约自取时间。');
  if(o.delivery==='lalamove')l.push('新山区 Lalamove 运费自付，请客服联系安排。');
  if(o.delivery==='post'){l.push('邮寄资料：');SHIP_F.forEach(function(f){l.push(f[1]+'：'+o.ship[f[0]])})}
  return l.join('\n');
}
function stat(o){try{if(window.HBJStats&&o&&o.items.length)window.HBJStats.order(o)}catch(e){}}
var toastT;
function toast(t){var e=document.getElementById('toast');if(!e){e=document.createElement('div');e.id='toast';e.className='toast';e.setAttribute('role','status');document.body.appendChild(e)}
  e.textContent=t;e.classList.add('show');clearTimeout(toastT);toastT=setTimeout(function(){e.classList.remove('show')},1500)}
function add(it,q){
  q=Math.max(1,parseInt(q,10)||1);
  if(!MODES[it.m])it.m='b';
  var a=ld(),f=null,k=key(it.c,it.m);
  a.forEach(function(x){if(key(x.c,x.m)===k)f=x});
  if(f){f.q+=q;f.p=it.p}else a.push({c:it.c,n:it.n,m:it.m,p:it.p,i:it.i||'',q:q});
  sv(a);var m=md(it.m);toast('已加入购物车 ✓ '+it.n+(m.t?' '+m.t:'')+' x'+q+m.u);
}
function fromBtn(b){
  var it={c:b.getAttribute('data-sku'),n:b.getAttribute('data-name'),m:b.getAttribute('data-mode')||'b',p:parseFloat(b.getAttribute('data-price'))||0,i:b.getAttribute('data-img')||''};
  var g=b.getAttribute('data-mode-from'),r=g&&document.querySelector('input[name="'+g+'"]:checked');
  if(r){it.m=r.value;it.p=parseFloat(r.getAttribute('data-price'))||it.p}
  return it;
}
/* ---- delivery form ---- */
function dlvHtml(){
  var ops=Object.keys(DLV).map(function(k,i){return '<label class="op"><input type="radio" name="dlv" value="'+k+'"><span>'+(i+1)+'. '+esc(DLV[k].t)+'<small>'+esc(DLV[k].h)+'</small></span></label>'}).join('');
  var f=SHIP_F.map(function(x){
    var id='sh-'+x[0],w=(x[0]!=='pc'&&x[0]!=='city')?' class="w"':'',inp;
    if(x[0]==='addr')inp='<textarea id="'+id+'" data-f="addr" rows="2" autocomplete="street-address"></textarea>';
    else if(x[0]==='state')inp='<select id="'+id+'" data-f="state"><option value="">请选择（只限西马）</option>'+STATES.map(function(s){return '<option>'+esc(s)+'</option>'}).join('')+'</select>';
    else inp='<input id="'+id+'" data-f="'+x[0]+'" '+({name:'autocomplete="name"',phone:'type="tel" inputmode="tel" autocomplete="tel"',pc:'inputmode="numeric" maxlength="5" autocomplete="postal-code"',city:'autocomplete="address-level2"'}[x[0]]||'')+'>';
    return '<label'+w+' for="'+id+'">'+esc(x[1])+' *'+inp+'</label>';
  }).join('');
  return '<fieldset class="dlv"><legend>取货方式 <i>*</i>（请选一项）</legend>'+ops+'</fieldset>'+
    '<div class="shp" id="shp" hidden><b style="grid-column:1/-1;color:#8f0d13;font-size:14px">📦 邮寄资料（全部必填）</b>'+f+'</div>';
}
function getDlv(){var r=document.querySelector('#dw input[name="dlv"]:checked');return r?r.value:''}
function getShip(){var o={};SHIP_F.forEach(function(f){var el=document.getElementById('sh-'+f[0]);o[f[0]]=el?String(el.value||'').trim().replace(/\s+/g,' '):''});return o}
function saveForm(){ss({d:getDlv(),f:getShip()})}
function restoreForm(){var s=ss();if(s.d&&DLV[s.d]){var r=document.querySelector('#dw input[name="dlv"][value="'+s.d+'"]');if(r)r.checked=true}
  if(s.f)SHIP_F.forEach(function(f){var el=document.getElementById('sh-'+f[0]);if(el&&s.f[f[0]])el.value=s.f[f[0]]});syncDlv()}
function syncDlv(){var d=getDlv(),sh=document.getElementById('shp');if(sh)sh.hidden=d!=='post';err('');hideOk();render()}
function err(t,el){var e=document.getElementById('dwe');if(!e)return;e.textContent=t;e.hidden=!t;
  [].forEach.call(document.querySelectorAll('#shp .bad'),function(x){x.classList.remove('bad')});
  if(el){el.classList.add('bad');try{el.focus()}catch(x){}}
  else if(t){var d=document.querySelector('#dw .dlv');if(d&&d.scrollIntoView)d.scrollIntoView({behavior:'smooth',block:'center'})}}
function validate(){
  var d=getDlv();
  if(!DLV[d])return{e:'请先选择取货方式：自取（Sutera Mall）、Lalamove（联系客服安排）或邮寄。'};
  if(d!=='post')return{d:d,ship:null};
  var s=getShip(),i;
  for(i=0;i<SHIP_F.length;i++){var f=SHIP_F[i];if(!s[f[0]])return{e:'选择邮寄需填写邮寄资料：请填写「'+f[1]+'」。',el:document.getElementById('sh-'+f[0])}}
  if(s.phone.replace(/\D/g,'').length<9)return{e:'请填写正确的电话号码。',el:document.getElementById('sh-phone')};
  if(!/^\d{5}$/.test(s.pc))return{e:'邮区编号应为 5 位数字。',el:document.getElementById('sh-pc')};
  return{d:d,ship:s};
}
function send(){
  var a=ld();if(!a.length){toast('购物车是空的');return}
  var v=validate();if(v.e){err(v.e,v.el);return}
  err('');var o=build(a,v.d,v.ship);
  if(!o.resend)stat(o);   /* re-sending the same 单号 is not a new order */
  var ok=document.getElementById('dwok');
  if(ok){ok.innerHTML='✅ 已生成单号 <b>'+esc(o.order_no)+'</b><br>请在 WhatsApp 按「发送」把订单发给客服 017-789 1688。没打开的话再点一次下面的按钮（单号不变）。';ok.hidden=false}
  window.open(waUrl(msg(o)),'_blank','noopener');
}
/* drawer markup */
function ensure(){
  if(document.getElementById('dw'))return;
  var d=document.createElement('div');d.id='dw';d.className='dw';d.setAttribute('aria-hidden','true');
  d.innerHTML='<div class="bg" data-close></div><section class="pnl" role="dialog" aria-modal="true" aria-labelledby="dwt">'+
   '<div class="hd"><b id="dwt">🛒 我的购物车</b><button class="x" type="button" data-close aria-label="关闭购物车">×</button></div>'+
   '<div class="ls"><div id="dwl"></div><div class="dlv-w" id="dwd">'+dlvHtml()+'</div></div>'+
   '<div class="ft"><div class="sub"><span>商品小计</span><span id="dws">RM0.00</span></div>'+
   '<div class="sub" id="dwp" hidden><span>邮费（西马邮寄，任买）</span><span>RM15.00</span></div>'+
   '<div class="tt"><span>参考合计</span><b id="dwt2">RM0.00</b></div>'+
   '<p>散装按件、整盒按盒计价。产品价格以店家确认为准。取货：自取（Sutera Mall）；Lalamove（联系客服安排，新山区运费自付）；西马邮寄 RM15 任买（需填写邮寄资料）。</p>'+
   '<p class="err" id="dwe" role="alert" hidden></p><p class="ok" id="dwok" role="status" hidden></p>'+
   '<button class="btn wa send" type="button" id="send">发送订单到 WhatsApp</button>'+
   '<p style="text-align:center;margin:8px 0 0"><button type="button" id="clr" style="border:0;background:none;color:#8a5a4a;text-decoration:underline;cursor:pointer;font-size:12px">清空购物车</button></p></div></section>';
  document.body.appendChild(d);
  d.addEventListener('click',function(e){
    var t=e.target;
    if(t.hasAttribute('data-close')){close();return}
    var k=t.getAttribute('data-k');if(!k)return;
    var a=ld(),i;for(i=0;i<a.length;i++)if(key(a[i].c,a[i].m)===k)break;if(i>=a.length)return;
    if(t.hasAttribute('data-inc'))a[i].q++;
    else if(t.hasAttribute('data-dec')){a[i].q--;if(a[i].q<1)a.splice(i,1)}
    else if(t.hasAttribute('data-rm'))a.splice(i,1);
    sv(a);
  });
  d.addEventListener('change',function(e){var t=e.target;
    if(t.name==='dlv'){saveForm();syncDlv();return}
    if(t.getAttribute('data-f')){saveForm();return}
    var k=t.getAttribute('data-k');if(!k||t.tagName!=='INPUT')return;
    var a=ld();a.forEach(function(x){if(key(x.c,x.m)===k)x.q=Math.max(1,parseInt(t.value,10)||1)});sv(a)});
  d.addEventListener('input',function(e){if(e.target.getAttribute('data-f')){saveForm();e.target.classList.remove('bad')}});
  document.getElementById('send').addEventListener('click',send);
  document.getElementById('clr').addEventListener('click',function(){if(confirm('确定清空购物车？'))sv([])});
  restoreForm();
}
function open(focusDlv){ensure();render();var d=document.getElementById('dw');d.classList.add('open');d.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';
  if(focusDlv&&!getDlv()){var f=d.querySelector('.dlv');if(f&&f.scrollIntoView)setTimeout(function(){f.scrollIntoView({behavior:'smooth',block:'center'})},60)}}
function close(){var d=document.getElementById('dw');if(!d)return;d.classList.remove('open');d.setAttribute('aria-hidden','true');document.body.style.overflow=''}
function render(){
  var a=ld(),n=count(a),t=total(a);
  [].forEach.call(document.querySelectorAll('[data-badge]'),function(b){b.textContent=n;b.classList.toggle('show',n>0)});
  var fc=document.getElementById('fc');if(fc){fc.classList.toggle('show',n>0);var s=fc.querySelector('span');if(s)s.textContent=a.length+' 项 · '+rm(t)}
  var l=document.getElementById('dwl');if(!l)return;
  var post=getDlv()==='post'&&a.length;
  document.getElementById('dws').textContent=rm(t);
  document.getElementById('dwp').hidden=!post;
  document.getElementById('dwt2').textContent=rm(post?t+POST_FEE:t);
  document.getElementById('dwd').hidden=!a.length;
  var ok=document.getElementById('dwok');if(ok&&!a.length)ok.hidden=true;
  if(!a.length){l.innerHTML='<div class="em">购物车还是空的<br><small>挑选喜欢的烟花，选散装或整盒加入购物车</small></div>';return}
  l.innerHTML=a.map(function(x){
    var m=md(x.m),k=esc(key(x.c,x.m));
    var th=x.i?'<div class="t" style="background-image:url(\''+esc(root+x.i)+'\')"></div>':'<div class="t"><span>'+esc(x.n.slice(0,6))+'</span></div>';
    return '<div class="ci">'+th+'<div class="n">'+esc(x.n)+(m.t?'<span class="u'+(x.m==='b'?' b':'')+'">'+m.t+'</span>':'')+'<small>'+esc(x.c)+' · '+rm(x.p)+'/'+m.u+' · 小计 '+rm(x.p*x.q)+'</small><button class="rm" type="button" data-rm data-k="'+k+'">移除</button></div>'+
    '<div class="qty"><button type="button" data-dec data-k="'+k+'" aria-label="减少">−</button><input type="number" min="1" inputmode="numeric" value="'+x.q+'" data-k="'+k+'" aria-label="数量（'+m.u+'）"><button type="button" data-inc data-k="'+k+'" aria-label="增加">+</button></div></div>';
  }).join('');
}
/* global clicks */
document.addEventListener('click',function(e){
  var b=e.target.closest?e.target.closest('[data-add]'):null;
  if(b){e.preventDefault();var q=1,qi=b.getAttribute('data-qty-from');if(qi){var el=document.getElementById(qi);if(el)q=el.value}add(fromBtn(b),q);return}
  var o=e.target.closest?e.target.closest('[data-open-cart]'):null;
  if(o){e.preventDefault();open();return}
  /* product page「WhatsApp 下单此款」: add to cart, then the customer picks 取货方式 in the cart before sending */
  var w=e.target.closest?e.target.closest('[data-wa-item]'):null;
  if(w){e.preventDefault();var qq=document.getElementById(w.getAttribute('data-qty-from')||'');add(fromBtn(w),qq&&qq.value);open(true);toast('请选择取货方式后发送订单');return}
  var st=e.target.closest?e.target.closest('[data-step]'):null;
  if(st){var inp=document.getElementById(st.getAttribute('data-for'));if(inp){inp.value=Math.max(1,(parseInt(inp.value,10)||1)+parseInt(st.getAttribute('data-step'),10))}}
});
/* product page 散装 / 整盒 picker: update the qty unit label */
document.addEventListener('change',function(e){var t=e.target;if(t.name==='mode'&&t.type==='radio'){var u=document.getElementById('qu');if(u)u.textContent=t.value==='b'?'盒（整盒）':'件（散装）'}});
document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
window.addEventListener('storage',function(e){if(e.key===K)render()});
/* search (home filters in place; other pages go home) */
var grid=document.getElementById('list');
function filter(q){
  q=(q||'').trim().toLowerCase();
  var feat=document.getElementById('featured');
  var cat=document.getElementById('catalog');
  var nr=document.getElementById('nores');
  if(!cat){ /* category / other pages with a #list of sections */
    var any=0;
    [].forEach.call(document.querySelectorAll('#list .pc'),function(c){var m=!q||c.getAttribute('data-s').indexOf(q)>-1;c.style.display=m?'':'none';if(m)any++});
    [].forEach.call(document.querySelectorAll('#list .sec'),function(s){var v=[].some.call(s.querySelectorAll('.pc'),function(c){return c.style.display!=='none'});s.style.display=v?'':'none'});
    if(nr)nr.style.display=any?'none':'block';
    return;
  }
  if(!q){
    if(feat)feat.hidden=false;
    cat.hidden=true;
    [].forEach.call(cat.querySelectorAll('.pc'),function(c){c.style.display=''});
    if(nr)nr.hidden=true;
    return;
  }
  if(feat)feat.hidden=true;
  cat.hidden=false;
  var any=0;
  [].forEach.call(cat.querySelectorAll('.pc'),function(c){
    var m=c.getAttribute('data-s').indexOf(q)>-1;
    c.style.display=m?'':'none';
    if(m)any++;
  });
  if(nr)nr.hidden=!!any;
}
[].forEach.call(document.querySelectorAll('form.sb'),function(f){
  var i=f.querySelector('input');
  f.addEventListener('submit',function(e){if(grid){e.preventDefault();filter(i.value);var t=document.getElementById('list');if(t&&i.value)t.scrollIntoView({behavior:'smooth'})}});
  if(grid)i.addEventListener('input',function(){filter(i.value)});
});
if(grid){var qs=(location.search.match(/[?&]q=([^&]*)/)||[])[1];if(qs){qs=decodeURIComponent(qs.replace(/\+/g,' '));var si=document.querySelector('form.sb input');if(si)si.value=qs;filter(qs)}}
/* tab highlight */
var tabs=document.querySelectorAll('.tabs a[href*="#"]');
if('IntersectionObserver' in window&&tabs.length&&grid){
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){var id=en.target.id;[].forEach.call(tabs,function(t){var on=t.getAttribute('href').split('#')[1]===id;t.classList.toggle('on',on);if(on&&t.scrollIntoView&&t.parentNode.scrollTo){t.parentNode.scrollTo({left:t.offsetLeft-40,behavior:'smooth'})}})}})},{rootMargin:'-130px 0px -60% 0px'});
  [].forEach.call(document.querySelectorAll('#list .sec'),function(s){io.observe(s)});
}
/* CNY countdown: 6 Feb 2027 00:00 Malaysia time (UTC+8) */
var cd=document.getElementById('cd');
if(cd){var T=Date.UTC(2027,1,5,16,0,0);var d=Math.ceil((T-Date.now())/864e5);
  cd.innerHTML=d>0?'距离羊年春节还有 <b>'+d+'</b> 天':(d>-15?'🎉 羊年春节快乐！':'');}
render();
window.HBJ={open:open,add:add};
})();
