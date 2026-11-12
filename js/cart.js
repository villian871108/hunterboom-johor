/* Hunter BOOM JOHOR — cart & WhatsApp ordering (no tracking) */
(function(){
'use strict';
var WA='60178270901',K='hbj_cart_v1';
var root=document.body.getAttribute('data-root')||'';
function ld(){try{var a=JSON.parse(localStorage.getItem(K)||'[]');return Array.isArray(a)?a:[]}catch(e){return []}}
function sv(a){try{localStorage.setItem(K,JSON.stringify(a))}catch(e){}render()}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function rm(n){return 'RM'+Number(n||0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,',')}
function total(a){return a.reduce(function(s,x){return s+(x.p||0)*x.q},0)}
function count(a){return a.reduce(function(s,x){return s+x.q},0)}
function waUrl(t){return 'https://wa.me/'+WA+'?text='+encodeURIComponent(t)}
function msg(a){
  var l=['我要下单'];
  a.forEach(function(x){l.push(x.c+' '+x.n+' x'+x.q)});
  l.push('');l.push('参考合计：'+rm(total(a))+'（以店家确认为准）');
  return l.join('\n');
}
var toastT;
function toast(t){var e=document.getElementById('toast');if(!e){e=document.createElement('div');e.id='toast';e.className='toast';e.setAttribute('role','status');document.body.appendChild(e)}
  e.textContent=t;e.classList.add('show');clearTimeout(toastT);toastT=setTimeout(function(){e.classList.remove('show')},1300)}
function add(it,q){
  q=Math.max(1,parseInt(q,10)||1);
  var a=ld(),f=null;
  a.forEach(function(x){if(x.c===it.c)f=x});
  if(f)f.q+=q;else a.push({c:it.c,n:it.n,p:it.p,i:it.i||'',u:it.u||'',q:q});
  sv(a);toast('已加入购物车 ✓ '+it.n+' x'+q);
}
function fromBtn(b){return{c:b.getAttribute('data-sku'),n:b.getAttribute('data-name'),p:parseFloat(b.getAttribute('data-price'))||0,i:b.getAttribute('data-img')||'',u:b.getAttribute('data-url')||''}}
/* drawer markup */
function ensure(){
  if(document.getElementById('dw'))return;
  var d=document.createElement('div');d.id='dw';d.className='dw';d.setAttribute('aria-hidden','true');
  d.innerHTML='<div class="bg" data-close></div><section class="pnl" role="dialog" aria-modal="true" aria-labelledby="dwt">'+
   '<div class="hd"><b id="dwt">🛒 我的购物车</b><button class="x" type="button" data-close aria-label="关闭购物车">×</button></div>'+
   '<div class="ls" id="dwl"></div>'+
   '<div class="ft"><div class="tt"><span>参考合计</span><b id="dwt2">RM0.00</b></div>'+
   '<p>价格依据价目表，最终价格、数量与送货安排以 WhatsApp 确认为准。</p>'+
   '<button class="btn wa send" type="button" id="send">发送订单到 WhatsApp</button>'+
   '<p style="text-align:center;margin:8px 0 0"><button type="button" id="clr" style="border:0;background:none;color:#8a5a4a;text-decoration:underline;cursor:pointer;font-size:12px">清空购物车</button></p></div></section>';
  document.body.appendChild(d);
  d.addEventListener('click',function(e){
    var t=e.target;
    if(t.hasAttribute('data-close')){close();return}
    var c=t.getAttribute('data-c');if(!c)return;
    var a=ld(),i;for(i=0;i<a.length;i++)if(a[i].c===c)break;if(i>=a.length)return;
    if(t.hasAttribute('data-inc'))a[i].q++;
    else if(t.hasAttribute('data-dec')){a[i].q--;if(a[i].q<1)a.splice(i,1)}
    else if(t.hasAttribute('data-rm'))a.splice(i,1);
    sv(a);
  });
  d.addEventListener('change',function(e){var t=e.target,c=t.getAttribute('data-c');if(!c||t.tagName!=='INPUT')return;
    var a=ld();a.forEach(function(x){if(x.c===c)x.q=Math.max(1,parseInt(t.value,10)||1)});sv(a)});
  document.getElementById('send').addEventListener('click',function(){var a=ld();if(!a.length){toast('购物车是空的');return}window.open(waUrl(msg(a)),'_blank','noopener')});
  document.getElementById('clr').addEventListener('click',function(){if(confirm('确定清空购物车？'))sv([])});
}
function open(){ensure();render();var d=document.getElementById('dw');d.classList.add('open');d.setAttribute('aria-hidden','false');document.body.style.overflow='hidden'}
function close(){var d=document.getElementById('dw');if(!d)return;d.classList.remove('open');d.setAttribute('aria-hidden','true');document.body.style.overflow=''}
function render(){
  var a=ld(),n=count(a),t=total(a);
  [].forEach.call(document.querySelectorAll('[data-badge]'),function(b){b.textContent=n;b.classList.toggle('show',n>0)});
  var fc=document.getElementById('fc');if(fc){fc.classList.toggle('show',n>0);var s=fc.querySelector('span');if(s)s.textContent=n+' 件 · '+rm(t)}
  var l=document.getElementById('dwl');if(!l)return;
  document.getElementById('dwt2').textContent=rm(t);
  if(!a.length){l.innerHTML='<div class="em">购物车还是空的<br><small>挑选喜欢的烟花，点「加入购物车」</small></div>';return}
  l.innerHTML=a.map(function(x){
    var th=x.i?'<div class="t" style="background-image:url(\''+esc(root+x.i)+'\')"></div>':'<div class="t"><span>'+esc(x.n.slice(0,6))+'</span></div>';
    return '<div class="ci">'+th+'<div class="n">'+esc(x.n)+'<small>'+esc(x.c)+' · '+rm(x.p)+'</small><button class="rm" type="button" data-rm data-c="'+esc(x.c)+'">移除</button></div>'+
    '<div class="qty"><button type="button" data-dec data-c="'+esc(x.c)+'" aria-label="减少">−</button><input type="number" min="1" inputmode="numeric" value="'+x.q+'" data-c="'+esc(x.c)+'" aria-label="数量"><button type="button" data-inc data-c="'+esc(x.c)+'" aria-label="增加">+</button></div></div>';
  }).join('');
}
/* global clicks */
document.addEventListener('click',function(e){
  var b=e.target.closest?e.target.closest('[data-add]'):null;
  if(b){e.preventDefault();var q=1,qi=b.getAttribute('data-qty-from');if(qi){var el=document.getElementById(qi);if(el)q=el.value}add(fromBtn(b),q);return}
  var o=e.target.closest?e.target.closest('[data-open-cart]'):null;
  if(o){e.preventDefault();open();return}
  var w=e.target.closest?e.target.closest('[data-wa-item]'):null;
  if(w){e.preventDefault();var qq=document.getElementById(w.getAttribute('data-qty-from')||'');var it=fromBtn(w);var q2=Math.max(1,parseInt(qq&&qq.value,10)||1);
    window.open(waUrl('我要下单\n'+it.c+' '+it.n+' x'+q2),'_blank','noopener');return}
  var st=e.target.closest?e.target.closest('[data-step]'):null;
  if(st){var inp=document.getElementById(st.getAttribute('data-for'));if(inp){inp.value=Math.max(1,(parseInt(inp.value,10)||1)+parseInt(st.getAttribute('data-step'),10))}}
});
document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
window.addEventListener('storage',function(e){if(e.key===K)render()});
/* search (home filters in place; other pages go home) */
var grid=document.getElementById('list');
function filter(q){
  q=(q||'').trim().toLowerCase();var any=0;
  [].forEach.call(document.querySelectorAll('#list .pc'),function(c){var m=!q||c.getAttribute('data-s').indexOf(q)>-1;c.style.display=m?'':'none';if(m)any++});
  [].forEach.call(document.querySelectorAll('#list .sec'),function(s){var v=[].some.call(s.querySelectorAll('.pc'),function(c){return c.style.display!=='none'});s.style.display=v?'':'none'});
  var nr=document.getElementById('nores');if(nr)nr.style.display=any?'none':'block';
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
