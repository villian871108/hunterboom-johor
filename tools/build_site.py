#!/usr/bin/env python3
"""Static site generator for Hunter BOOM JOHOR 总代理.

Usage:
  python3 tools/build_site.py                     # default origin is the live GitHub Pages shop
  python3 tools/build_site.py --origin https://your-domain.com   # set real domain before publishing

All pages are generated from data/products.json.
"""
import json, os, sys, html, datetime, urllib.parse

# ===== The ONE place to set the public domain (no trailing slash). =====
# Official shop domain. GitHub Pages still serves the same repo as a fallback.
PUBLIC_ORIGIN = "https://hunterboom.my"
SITE_ORIGIN = PUBLIC_ORIGIN
if "--origin" in sys.argv:
    SITE_ORIGIN = sys.argv[sys.argv.index("--origin") + 1].rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Unlisted staff-demo path. Customers see a maintenance poster at the domain root.
# Do not add this slug to the public sitemap or robots Allow list.
DEMO_SLUG = "hfkd"
OUT_DIR = ROOT
DEMO_MODE = False
# When the shop is built under DEMO_SLUG, CSS/JS/images stay at the domain root.
PAGE_ASSET = ""
D = json.load(open(os.path.join(ROOT, "data", "products.json"), encoding="utf-8"))
# unpublished (published: false) stay in the data file but are not built into the public shop
ALL_P = D["products"]
P = [p for p in ALL_P if p.get("published", True)]
CATS = [c for c in D["categories"] if any(p["category"] == c["id"] for p in P)]
CAT = {c["id"]: c for c in CATS}
BYCAT = {c["id"]: [p for p in P if p["category"] == c["id"]] for c in CATS}
TODAY = datetime.date.today().isoformat()

SHOP = "Hunter BOOM JOHOR 总代理"
BRAND = "Hunter BOOM JOHOR"
TAG = "用一分钟的绚烂，治愈一整年的荒芜"
PHONE_D = "017-789 1688"; PHONE_I = "+60177891688"; WA = "https://wa.me/60177891688"
FB = "https://www.facebook.com/profile.php?id=61585987514444"
ADDR = "Iskandar Puteri, Johor Bahru, Malaysia, 81200"
ADDR_ZH = "柔佛新山 依斯干达公主城（Iskandar Puteri）81200"
CNY = "羊年春节（2027年2月6日）"
# Delivery as stated by the shop (12–13 Nov 2026). Checkout must pick exactly one of these 3 (js/cart.js).
# Do not invent East Malaysia or other fees.
SHIP_FACE = "自取（Sutera Mall），客服会联系约自取时间"
SHIP_JB = "Lalamove（联系客服安排，新山区运费自付）"
SHIP_WM = "西马邮寄 RM15 任买（需填写邮寄资料）"
SHIP_LINE = "自取（Sutera Mall）；Lalamove（联系客服安排，新山区运费自付）；西马邮寄 RM15 任买（需填写邮寄资料）。"

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
def rm(x): return "RM{:,.2f}".format(x)

# ---- 散装 / 整盒 pricing (fields written by tools/apply_loose_pricing.py) ----
# sale_mode "dual":   N/1 with N>1 → 散装 loose_price /件 + 整盒 carton_price /盒
# sale_mode "single": 1/1          → one unit, loose_price (= 箱价 × 1.40) /件
# sale_mode "carton": other packing → 整盒 only at carton_price; 散装件数待确认
def mode(p): return p.get("sale_mode") or "carton"
def carton(p): return p.get("carton_price", p["price"])
def main_price(p):
    """Primary customer price: 散装卖价 for N/1 products, 整盒价 for packing still 待确认."""
    return p["loose_price"] if mode(p) in ("dual", "single") else carton(p)
def price_txt(p):
    """Plain-text price summary for meta descriptions."""
    m = mode(p)
    if m == "dual": return f"散装卖价 {rm(p['loose_price'])}/件，整盒 {rm(carton(p))}/盒（{p['piece_qty']}件）"
    if m == "single": return f"卖价 {rm(p['loose_price'])}/件"
    return f"整盒价 {rm(carton(p))}/盒（散装件数待确认）"
def absu(path):  # path like "p/HB001.html" or "" for home
    return (SITE_ORIGIN + "/" + path) if SITE_ORIGIN else "/" + path
def jd(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"

LOGO = ('<svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="16" fill="#fff3d0"/>'
        '<g stroke="#c8161d" stroke-width="3.4" stroke-linecap="round"><path d="M32 8v12M32 44v12M8 32h12M44 32h12M15 15l8.5 8.5M40.5 40.5L49 49M49 15l-8.5 8.5M23.5 40.5L15 49"/></g>'
        '<circle cx="32" cy="32" r="6.5" fill="#f6b52e"/></svg>')
BURST = ('<svg viewBox="0 0 64 64" aria-hidden="true"><g stroke="#ffd77a" stroke-width="2.6" stroke-linecap="round">'
         '<path d="M32 6v14M32 44v14M6 32h14M44 32h14M13.6 13.6l9.9 9.9M40.5 40.5l9.9 9.9M50.4 13.6l-9.9 9.9M23.5 40.5l-9.9 9.9"/></g>'
         '<circle cx="32" cy="32" r="6" fill="#fff0c8"/></svg>')
IC_HOME = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>'
IC_CAT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/></svg>'
IC_CART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 4h2l2.4 11.2a1 1 0 0 0 1 .8h9.2a1 1 0 0 0 1-.8L20 8H6"/><circle cx="9" cy="20" r="1.4"/><circle cx="17" cy="20" r="1.4"/></svg>'
IC_WA = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.2c0-.1-.2-.2-.5-.3z"/></svg>'

def head(title, desc, path, root, og_img=None, extra_ld=(), og_type="website", keywords=None):
    can = absu(path)
    img = og_img or "img/og-cny2027.jpg"
    pub = PUBLIC_ORIGIN if PUBLIC_ORIGIN else SITE_ORIGIN
    img_abs = (pub + "/" + img) if pub else asset(img)
    og_dims = (
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta property="og:image:type" content="image/jpeg">\n'
        '<meta property="og:image:alt" content="Hunter BOOM JOHOR 总代理 三阳开泰 羊年海报">\n'
        if img.endswith("og-cny2027.jpg") else ""
    )
    kw = f'<meta name="keywords" content="{e(keywords)}">' if keywords else ""
    return f"""<!doctype html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{kw}
<link rel="canonical" href="{e(can)}">
<meta name="robots" content="{'noindex,nofollow,noarchive' if DEMO_MODE else 'index,follow,max-image-preview:large'}">
<meta name="theme-color" content="#c8161d">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="zh_CN">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(can)}">
<meta property="og:image" content="{e(img_abs)}">
{og_dims}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(img_abs)}">
<link rel="icon" href="{asset('img/favicon.svg')}" type="image/svg+xml">
<link rel="icon" href="{asset('img/favicon-48.png')}" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="{asset('img/apple-touch-icon.png')}">
<link rel="manifest" href="{asset('site.webmanifest')}">
<link rel="stylesheet" href="{asset('css/style.css')}?v=9">
{''.join(jd(x) for x in extra_ld)}
<!-- Site stats: js/stats.js -> Google Apps Script (tools/stats_api.gs); see tools/STATS.md -->
</head>
"""

def topbar(root, active=None, home=False):
    tabs = []
    href = (lambda c: f"{root}c/{c['id']}.html")
    tabs.append(f'<a href="{root}index.html"{" class=on" if active=="home" else ""}>全部</a>')
    for c in CATS:
        tabs.append(f'<a href="{href(c)}"{" class=on" if active==c["id"] else ""}>{e(c["name"])}</a>')
    act = "" if home else f' action="{root}index.html"'
    banner = ('<div class="demo-banner" role="note" style="background:#3b0a0d;color:#f6e2a2;text-align:center;'
              'padding:8px 12px;font-size:13px;letter-spacing:.04em;font-weight:600">'
              "此页面仅供工作人员演示学习，不是顾客下单页</div>\n") if DEMO_MODE else ""
    return banner + f"""<header class="top"><div class="in">
<a class="lg" href="{root}index.html" aria-label="{SHOP} 首页">{LOGO}<span class="wm"><b>Hunter BOOM</b><small>JOHOR 总代理 · 新山</small></span></a>
<form class="sb" role="search"{act} method="get"><label class="sr" for="q">搜索产品</label><input id="q" name="q" type="search" placeholder="搜索名称或编号，如 HB001、红炮、炮竹" autocomplete="off"><button type="submit">搜索</button></form>
<nav class="tabs" aria-label="产品分类">{''.join(tabs)}</nav>
</div></header>
<div class="ann" role="note"><div class="in"><span>🧧 <b>{CNY}</b> 年货烟花现正接单</span><span>🏮 新山烟花炮竹批发零售</span><span>🛍️ 自取（Sutera Mall）</span><span>📦 西马邮寄 RM15 任买</span><span>📲 <a href="{WA}" target="_blank" rel="noopener">WhatsApp {PHONE_D}</a></span></div></div>
"""

def footer(root, active=None):
    cats = "".join(f'<a href="{root}c/{c["id"]}.html">{e(c["name"])}</a>' for c in CATS)
    def on(x): return ' class="on"' if active == x else ""
    return f"""<footer><div class="in">
<div><h2>{SHOP}</h2><p>{TAG}</p><p>新山烟花炮竹批发零售。{SHIP_LINE}</p></div>
<div><h3>联系我们</h3>
<address style="font-style:normal"><p>📍 {ADDR}<br><small>{ADDR_ZH}</small></p>
<p>📲 WhatsApp / 电话：<a href="{WA}" target="_blank" rel="noopener">{PHONE_D}</a></p>
<p>👍 Facebook：<a href="{FB}" target="_blank" rel="noopener">{SHOP}</a></p>
<p>🕒 营业时间：Facebook 主页显示 Always open，来取货前请先 WhatsApp 约时间。</p></address></div>
<div><h3>产品分类</h3><p class="cats">{cats}</p><p><a href="{root}about.html">关于我们 · 下单方式</a></p></div>
<p class="legal">温馨提示：燃放烟花请遵守当地法律法规及燃放时间、地点规定；购买前请自行确认所选产品在您所在地区允许使用。整盒按价目表箱价；散装卖价 = 箱价 ÷ 一盒件数 × 1.40（PACKING 为原表包装规格）。最终价格、数量与送货安排以 WhatsApp 店家确认为准。本站为 {SHOP} 店铺网站，并非 Hunter Boom 品牌总部官网。© {datetime.date.today().year} {BRAND}</p>
</div></footer>
<button class="fc" id="fc" type="button" data-open-cart aria-label="打开购物车">{IC_CART.replace('<svg','<svg width="20" height="20"')}<span>0 项</span></button>
<nav class="bn" aria-label="底部导航">
<a href="{root}index.html"{on('home')}>{IC_HOME}首页</a>
<a href="{root}c/index.html"{on('cats')}>{IC_CAT}分类</a>
<button type="button" data-open-cart>{IC_CART}购物车<i class="bdg" data-badge>0</i></button>
<a class="wa" href="{WA}" target="_blank" rel="noopener">{IC_WA}WhatsApp</a>
</nav>
<script src="{asset('js/stats.js')}?v=3" defer></script>
<script src="{asset('js/cart.js')}?v=9" defer></script>
"""

def img_block(p, root, big=False, lazy=True, eager=False):
    if p.get("image"):
        src = p["thumb"] if not big else p["image"]
        w, h = (p["thumb_size"] if not big else p["image_size"])
        alt = f"{p['name']} {p['name_en']} 烟花产品图（Hunter BOOM JOHOR 新山）".replace("  ", " ")
        ld = 'loading="lazy" decoding="async"' if lazy and not eager else 'fetchpriority="high"'
        return f'<img src="{asset(src)}" width="{w}" height="{h}" alt="{e(alt)}" {ld}>'
    return f'<div class="ph" role="img" aria-label="{e(p["name"])}（暂无产品图）">{BURST}<b>{e(p["name"])}</b><i>产品图待更新</i></div>'

def btn_attrs(p, root, m=None):
    """Cart button data. m: "l" 散装 (per piece), "b" 整盒 (per box), "s" 单件 (1/1). Default = the product's primary unit."""
    i = p["thumb"] if p.get("image") else ""
    if m is None: m = {"dual": "l", "single": "s"}.get(mode(p), "b")
    pr = carton(p) if m == "b" else p["loose_price"]
    return f'data-sku="{p["sku"]}" data-name="{e(p["title"])}" data-mode="{m}" data-price="{pr:.2f}" data-img="{e(i)}"'

def card_price(p):
    m = mode(p)
    if m == "dual":
        return (f'<div class="pr"><small>散装</small> {rm(p["loose_price"])}<small>/件</small></div>'
                f'<div class="pk">整盒 {rm(carton(p))}/盒 · {p["piece_qty"]}件</div>')
    if m == "single":
        return f'<div class="pr">{rm(p["loose_price"])}<small>/件</small></div><div class="pk">单件 · 包装 {e(p["packing"])}</div>'
    return (f'<div class="pr"><small>整盒</small> {rm(carton(p))}<small>/盒</small></div>'
            f'<div class="pk">包装 {e(p["packing"])} · 散装件数待确认</div>')

def card_buttons(p, root):
    t = e(p["title"])
    if mode(p) == "dual":
        return (f'<div class="ab"><button type="button" class="add" data-add {btn_attrs(p, root, "l")} aria-label="把 {t} 散装 1 件加入购物车">+ 散装</button>'
                f'<button type="button" class="add bx" data-add {btn_attrs(p, root, "b")} aria-label="把 {t} 整盒 1 盒加入购物车">+ 整盒</button></div>')
    return f'<button type="button" class="add" data-add {btn_attrs(p, root)} aria-label="把 {t} 加入购物车">加入购物车</button>'


def intro(p):
    """Short catalog blurb from the product's name and category. No invented duration, effects, or safety claims."""
    import re
    sku, n, cat = p["sku"], p["name"], p["category"]
    ov = {
        "HB001": "8尺红炮，开年迎宾常用的条装礼炮",
        "HB002": "8尺红炮礼盒彩箱装，方便送礼和收纳",
        "HB010": "8尺五色混装礼炮，一箱多种颜色",
        "HB011": "五万头礼炮，开年场面更大的礼盒款",
        "HB012": "十万头礼炮，开年响声和场面都更足",
        "HB013": "网红东方巨龙礼炮，特红色，开年很常见",
        "HB014": "网红东方巨龙礼炮，玫瑰粉色",
        "HB015": "网红东方巨龙礼炮，黄金色",
        "HB016": "网红东方巨龙礼炮，五彩色",
        "HB024": "30尺七色精品礼盒，贺岁礼炮",
        "HB032": "88尺九色礼炮，九五至尊款",
        "HB040": "小盒沙炮，地面连续噼啪作响",
        "HB041": "大号沙炮，响声比小沙炮更足",
        "HB042": "加强款沙炮，响声更大",
        "HB043": "地面喷泉，莲花造型慢慢开花",
        "HB046": "会转的彩烟陀螺，边转边冒彩烟",
        "HB048": "小支手持霞光棒，握住慢慢喷花",
        "HB049": "大号手持霞光棒，喷花比小霞光更长",
        "HB050": "手持变色霞光，颜色会变换",
        "HB053": "手持彩色棒，握住燃放",
        "HB054": "7寸手持金色电光花（火花棒）",
        "HB064": "手持舞龙棒，挥动时有火花",
        "HB066": "手持大号花棒，复仇联盟造型",
        "HB068": "拉环五色烟雾，拉一下冒彩烟",
        "HB071": "加特林喷泉，持续往上喷黄金效果",
        "HB075": "7寸冰淇淋造型喷泉，锥形花筒",
        "HB080": "发财树造型喷泉，地面往上喷花",
        "HB085": "趣味喷泉，孔雀下蛋造型",
        "HB086": "趣味喷泉，燃放时像母鸡下蛋",
        "HB087": "小型喷泉，满地珍珠效果",
        "HB088": "MILO罐造型趣味喷泉",
        "HB090": "地面旋转喷花，像风车一样转着开",
        "HB098": "龙蛋造型喷泉，放在地上燃放",
        "HB102": "坦克造型飞天趣味款",
        "HB103": "悟空造型飞天趣味款",
        "HB104": "大黄蜂造型飞天趣味款",
        "HB107": "飞天趣味款，消声月旅行",
        "HB108": "50发飞天鼠，一串串飞出去",
        "HB110": "飞天火箭，狼嚎火箭造型",
        "HB112": "无人机造型飞天趣味款",
        "HB113": "飞天伞花，升空后张开降落伞",
        "HB115": "三层飞机造型飞天趣味款",
        "HB117": "甲壳虫造型飞天趣味款",
        "HB118": "水母造型，飞起来像小UFO",
        "HB119": "超级大水母，飞天UFO造型",
        "HB123": "顺利红，传统响声小炮",
        "HB168": "5寸552发盆花，猎人之花",
        "HB181": "9寸138发盆花，七彩筋斗云",
        "HB188": "10寸盆花盲盒款，效果看燃放才知道",
        "HB249": "9寸238发盆花 DEEPSEEK",
        "HB251": "10寸488发大盆花，大汉风歌压轴款",
        "HB252": "12寸588发大盆花，大唐盛世压轴款",
        "HB253": "2寸洞25发球盒，马皇后",
        "HB256": "2寸洞88发球盒，刘伯温",
        "HB259": "4寸洞16发球盒，龙腾盛世",
        "HB260": "精品4寸洞16发球盒，金意金丝柳",
    }
    if sku in ov:
        return ov[sku]
    if cat == "hongpao":
        m = re.search(r"(\d+)尺", n)
        size = (m.group(1) + "尺") if m else ""
        color = ""
        for k, v in (("玫瑰红", "玫瑰粉色"), ("翡翠玫瑰", "翡翠玫瑰"), ("满地黄金", "满地黄金"),
                     ("黄金满地", "满地黄金"), ("大红大紫", "大红大紫"), ("红宝石", "红宝石特红"),
                     ("王红炮", "王红炮"), ("特红", "特红色"), ("黄金", "黄金色"),
                     ("七星", "七星款"), ("五彩", "五彩色")):
            if k in n:
                color = v
                break
        gift = ("礼盒" in n) or ("彩盒" in n) or ("彩箱" in n)
        if "东方巨龙" in n:
            return "网红东方巨龙礼炮" + (("，" + color) if color else "")
        parts = [(size + "红炮礼炮") if size else "红炮礼炮"]
        if color:
            parts.append(color)
        parts.append("礼盒包装" if gift else "开年迎宾用")
        return "，".join(parts)
    if cat == "poppop":
        return "地面沙炮，连续噼啪作响"
    if cat == "handheld":
        if "电光花" in n:
            inch = re.search(r"(\d+)寸", n)
            return ((inch.group(1) + "寸") if inch else "") + "手持金色电光花（火花棒）"
        if "霞光" in n:
            return "手持霞光棒，握住慢慢喷花"
        if "魔术棒" in n or "流星" in n or "霹雳" in n or "波" in n:
            return "手持花棒，一波波往上喷花"
        if "烟雾" in n or "烟" in n:
            return "手持彩烟，拉环或点燃后冒烟"
        if "火炬" in n:
            return "手持五彩火炬，握住燃放"
        if "瀑布" in n:
            return "手持瀑布效果，火花往下洒"
        return "手持烟花，握住燃放"
    if cat == "fountain":
        if "加特林" in n:
            return "加特林喷泉，持续往上喷花"
        if "冰淇淋" in n or "锥形" in n:
            return "锥形喷泉花筒，放在地上喷花"
        if "孔雀" in n:
            return "孔雀造型地面喷泉"
        if "母鸡" in n:
            return "母鸡造型趣味喷泉"
        if "风车" in n:
            return "旋转喷泉，转着喷花"
        if "龙蛋" in n or "金玉" in n:
            return "龙蛋造型地面喷泉"
        if "发财树" in n or "黄金树" in n:
            return "树形喷泉，地面往上喷花"
        if "铁塔" in n or "巴黎" in n or "东方明珠" in n:
            return "建筑造型地面喷泉"
        if "陀螺" in n:
            return "会转的彩烟陀螺"
        if "火山" in n:
            return "火山造型地面喷泉"
        if "伞" in n:
            return "雨伞造型地面喷泉"
        return "地面喷泉喷花，放在地上燃放"
    if cat == "fly":
        if "火箭" in n:
            return "飞天火箭，点燃后升空"
        if "坦克" in n or "飞机" in n or "无人机" in n or "悟空" in n or "黄蜂" in n or "甲壳虫" in n:
            return "造型飞天趣味款，点燃后会飞"
        if "鼠" in n or "美人" in n:
            return "飞天鼠，一串串飞出去"
        if "水母" in n or "UFO" in n:
            return "飞天水母（UFO）造型"
        if "降落伞" in n or "伞" in n:
            return "飞天伞花，升空后张开"
        if "雷" in n:
            return "飞天响声趣味款"
        return "飞天趣味烟花，点燃后会飞或升空"
    if cat == "sound":
        if "火柴炮" in n:
            return "火柴炮，点燃后发出响声"
        if "雨打芭蕉" in n:
            return "雨打芭蕉，连续响声"
        if "双响" in n:
            return "天地双响，一声接一声"
        if "雷" in n or "炮弹" in n:
            return "响声烟花，以爆响为主"
        return "响声系列，以爆响为主"
    if cat == "bear":
        bare = n.replace("(熊炮)", "").replace("（熊炮）", "").strip()
        return "熊炮系列，" + bare
    shots = re.search(r"(\d+)\s*发", n)
    inch = re.search(r"(\d+(?:\.\d+)?)\s*寸", n)
    bits = []
    if inch:
        bits.append(inch.group(1) + "寸")
    if shots:
        bits.append(shots.group(1) + "发")
    size = "".join(bits)
    tail = re.sub(r"(纸筒|模压|塑模|精品|盆花|高)?", "", n)
    tail = re.sub(r"\d+(\.\d+)?\s*寸(洞|高)?", "", tail)
    tail = re.sub(r"\d+\s*发", "", tail)
    tail = re.sub(r"[-—–]+", " ", tail)
    tail = " ".join(tail.split()).strip(" -·")
    if cat == "shot":
        if not tail or len(tail) < 2:
            return (size + "球盒，洞径更大的升空款").strip()
        return (size + "球盒 · " + tail).strip(" ·")
    if cat == "bigcake":
        if not tail or len(tail) < 2:
            return (size + "大盆花，发数多、场面更大").strip()
        return (size + "大盆花 · " + tail).strip(" ·")
    if not tail or len(tail) < 2:
        return (size + "地面盆花，多发连放升空开花").strip()
    return (size + "盆花 · " + tail).strip(" ·")


def card(p, root, idx=0):
    blurb = intro(p)
    s = f"{p['sku']} {p['name']} {p['title']} {p['name_en']} {CAT[p['category']]['name']} {blurb}".lower()
    en = f'<div class="en" lang="en">{e(p["name_en"])}</div>' if p["name_en"] else '<div class="en">&nbsp;</div>'
    return (f'<article class="pc" data-s="{e(s)}"><a class="im" href="{root}p/{p["sku"]}.html">{img_block(p, root, eager=idx<4)}<span class="cd2">{p["sku"]}</span>{'<span class="vb" title="有视频介绍">▶ 视频</span>' if p.get("video_embed") else ""}</a>'
            f'<div class="b"><h3><a href="{root}p/{p["sku"]}.html">{e(p["title"])}</a></h3>{en}'
            f'<p class="intro">{e(blurb)}</p>'
            f'<div class="row{" dual" if mode(p) == "dual" else ""}"><div>{card_price(p)}</div>'
            f'{card_buttons(p, root)}</div></div></article>')

STORE_LD = {
    "@context": "https://schema.org", "@type": "Store", "@id": absu("") + "#store",
    "name": SHOP, "alternateName": ["Hunter BOOM JOHOR", "Hunter Boom Johor 新山烟花", "猎人烟花 新山", "新山炮竹", "柔佛烟花炮竹"],
    "description": f"{TAG}。新山烟花炮竹、柔佛烟花炮竹批发零售：红炮礼炮、鞭炮、Pop Pop 沙炮、手持烟花、喷泉、盆花与大盆花，可在 hunterboom.my 网上订购，WhatsApp 下单。",
    "url": absu(""), "image": (PUBLIC_ORIGIN + "/img/og-cny2027.jpg") if PUBLIC_ORIGIN else "/img/og-cny2027.jpg",
    "logo": (PUBLIC_ORIGIN + "/img/icon-512.png") if PUBLIC_ORIGIN else "/img/icon-512.png",
    "telephone": PHONE_I, "priceRange": "RM{:,.0f} – RM{:,.0f}".format(min(main_price(p) for p in P), max(main_price(p) for p in P)),
    "currenciesAccepted": "MYR",
    "address": {"@type": "PostalAddress", "addressLocality": "Iskandar Puteri, Johor Bahru", "addressRegion": "Johor", "postalCode": "81200", "addressCountry": "MY"},
    "areaServed": [{"@type": "City", "name": "Johor Bahru"}, {"@type": "Place", "name": "Iskandar Puteri"}, {"@type": "State", "name": "Johor"}],
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}],
    "sameAs": [FB, WA],
    "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE_I, "contactType": "sales", "url": WA, "availableLanguage": ["zh", "ms", "en"], "areaServed": "MY"}],
}
SITE_LD = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "alternateName": SHOP, "url": absu(""), "inLanguage": "zh-Hans"}
if SITE_ORIGIN:
    SITE_LD["potentialAction"] = {"@type": "SearchAction", "target": SITE_ORIGIN + "/index.html?q={search_term_string}", "query-input": "required name=search_term_string"}

def bc_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absu(u)} for i, (n, u) in enumerate(items)]}

def write(rel, s):
    fp = os.path.join(OUT_DIR, rel)
    parent = os.path.dirname(fp)
    if parent:
        os.makedirs(parent, exist_ok=True)
    open(fp, "w", encoding="utf-8").write(s)

def asset(path=""):
    """URL to a root-level static file (css, js, img)."""
    base = PAGE_ASSET if PAGE_ASSET != "" else ""
    return base + path

def data_root(rel=""):
    """cart.js data-root: shop images live at the domain root."""
    return PAGE_ASSET if PAGE_ASSET != "" else rel

KW = "新山烟花, 新山炮竹, 新山鞭炮, 新山烟花批发, 柔佛烟花, 柔佛炮竹, 马来西亚烟花, 马来西亚炮竹, 猎人烟花, Hunter Boom Johor, 依斯干达公主城, Sutera Mall 烟花, 烟花批发, 炮竹批发, 羊年烟花, 新年烟花, 网上买烟花, 网上买炮, Johor Bahru fireworks, mercun Johor, bunga api Johor"

# ---------------- home: curated diverse shelves (not a raw dump) ----------------
# Merchandising picks requested for the shop homepage. These are editorial
# highlights (one face per product family, mixed categories), not audited sales ranks.
BY_SKU = {p["sku"]: p for p in P}

def cards_for(skus, root, start=0):
    out = []; i = start
    for s in skus:
        p = BY_SKU[s]
        if not p:
            raise SystemExit("missing sku " + s)
        out.append(card(p, root, i)); i += 1
    return "".join(out), i

# Each SKU appears in at most one shelf. Families (colorways of the same cake /
# cannon) are represented once. Prefer items that have product photos.
# 小朋友专区 is merchandising (milder handheld, fountain and novelty),
# not an official child-safety certification. Overlapping "必玩" SKUs moved here.
KIDS_HOME = ["HB048", "HB054", "HB053", "HB043", "HB075", "HB086",
             "HB090", "HB085", "HB098", "HB046", "HB068", "HB087"]
KIDS_ALL = ["HB048", "HB049", "HB050", "HB051", "HB053", "HB054", "HB055",
            "HB064", "HB065", "HB068", "HB043", "HB046", "HB075", "HB080",
            "HB085", "HB086", "HB087", "HB088", "HB090", "HB098", "HB118", "HB119"]
KIDS_NOTE = "本专区由店家按较温和的手持、喷泉和趣味款整理，方便家长选购，不是官方童用认证。请由成人操作或在家长看护下燃放，并遵守当地规定。"

SHELVES = [
    ("hot", "🔥", "最畅销", "热门口碑款，多个分类都有", "c/index.html", "浏览全部分类 ›",
     ["HB013", "HB040", "HB079", "HB071", "HB102", "HB123", "HB168", "HB181", "HB253", "HB011"]),
    ("kids", "🧒", "小朋友专区", "手持、喷泉和趣味小品，请在家长看护下燃放", "c/kids.html", "查看全部 ›",
     KIDS_HOME),
    ("must", "✨", "必玩推荐", "沙炮、趣味飞天、喷泉，好看又好玩", "c/fly.html", "看飞天趣味 ›",
     ["HB042", "HB066", "HB103", "HB112", "HB104", "HB115", "HB113", "HB108", "HB094", "HB110", "HB117", "HB107"]),
    ("cannon", "🧧", "贺岁礼炮", "不同尺数各挑一款，颜色不重复", "c/hongpao.html", "全部礼炮 ›",
     ["HB001", "HB010", "HB024", "HB032", "HB012", "HB036"]),
    ("cake", "💐", "盆花精选", "纸筒、彩烟、三军到球盒，系列不扎堆", "c/cake.html", "全部盆花 ›",
     ["HB140", "HB174", "HB193", "HB243", "HB246", "HB188", "HB249", "HB257"]),
    ("finale", "👑", "压轴大秀", "大盆花与球盒压轴款，适合年夜收尾", "c/bigcake.html", "全部大盆花 ›",
     ["HB251", "HB252", "HB189", "HB242", "HB259", "HB260"]),
]

def home():
    root = ""
    # Validate no duplicate SKUs across shelves and all exist with photos preferred
    seen = set()
    for _id, _ic, _t, _d, _u, _m, skus in SHELVES:
        for s in skus:
            if s not in BY_SKU:
                raise SystemExit("unknown sku in shelf: " + s)
            if s in seen:
                raise SystemExit("duplicate sku across shelves: " + s)
            seen.add(s)
    icons = (f'<a href="#kids"><span>🧒</span>小朋友专区</a>'
             + "".join(f'<a href="c/{c["id"]}.html"><span>{c["icon"]}</span>{e(c["name"])}</a>' for c in CATS))
    secs = []; idx = 0
    for sid, icon, title, lead, more_href, more_txt, skus in SHELVES:
        html, idx = cards_for(skus, root, idx)
        note = f'<p class="shelf-note">{e(KIDS_NOTE)}</p>' if sid == "kids" else ""
        secs.append(
            f'<section class="sec shelf" id="{sid}" aria-labelledby="h-{sid}">'
            f'<h2 id="h-{sid}">{icon} {e(title)} <small>{e(lead)}</small>'
            f'<a class="more" href="{more_href}">{e(more_txt)}</a></h2>'
            f'{note}'
            f'<div class="g">{html}</div></section>'
        )
    # Full catalog stays in the page (hidden until search) so the home search still finds all 260.
    cat_cards = "".join(card(p, root, 99) for p in P)
    catalog = (
        f'<section class="sec" id="catalog" hidden>'
        f'<h2>搜索结果 <small>全部 {len(P)} 款</small></h2>'
        f'<div class="g">{cat_cards}</div></section>'
    )
    title = "新山烟花炮竹批发零售 | Hunter BOOM JOHOR | 柔佛"
    desc = f"Hunter BOOM JOHOR 总代理：新山烟花、新山炮竹、柔佛烟花炮竹批发零售，{len(P)} 款羊年新年烟花——红炮礼炮、鞭炮、Pop Pop 沙炮、手持烟花、喷泉、盆花与大盆花。Sutera Mall 自取，西马可邮寄。官网 hunterboom.my，WhatsApp {PHONE_D} 网上订购。"
    item_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Hunter BOOM JOHOR 产品分类",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c["name"], "url": absu(f"c/{c['id']}.html")} for i, c in enumerate(CATS)]}
    body = f"""<body data-root="{data_root()}">
{topbar(root, 'home', home=True)}
<main class="wrap">
<figure class="cny-poster">
<a href="img/cny2027-poster.jpg" target="_blank" rel="noopener">
<picture>
<source srcset="img/cny2027-poster.webp" type="image/webp">
<img src="img/cny2027-poster.jpg" width="1200" height="2278" alt="Hunter BOOM JOHOR 新山烟花炮竹羊年春节海报：三阳开泰，总代理·新山，2027年2月6日，WhatsApp 017-789 1688" decoding="async">
</picture>
</a>
</figure>
<section class="hero" aria-labelledby="h1">
<span class="tag">🐐 {CNY}</span>
<h1 id="h1"><em>新山烟花炮竹</em>批发零售 · Hunter BOOM JOHOR 总代理</h1>
<p>{TAG}。柔佛新山买烟花、买炮竹、买鞭炮，猎人烟花（Hunter Boom）羊年新年烟花一站购齐：红炮礼炮、沙炮、手持烟花、喷泉与盆花，依斯干达公主城出货，官网 hunterboom.my 网上就能订。{SHIP_LINE}</p>
<p lang="en">Hunter BOOM JOHOR is the Johor Bahru authorised dealer for Hunter Boom fireworks and firecrackers — wholesale and retail from Iskandar Puteri. Order online at hunterboom.my or WhatsApp {PHONE_D}. This shop is not the Hunter Boom brand headquarters.</p>
<p lang="ms">Hunter BOOM JOHOR ialah ejen sah Johor Bahru untuk bunga api dan mercun Hunter Boom. Borong dan runcit dari Iskandar Puteri. Tempah dalam talian di hunterboom.my atau WhatsApp {PHONE_D}. Laman ini bukan laman rasmi ibu pejabat jenama Hunter Boom.</p>
<div class="cd" id="cd" aria-live="polite"></div>
<div class="btns"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">{IC_WA.replace('<svg','<svg width="18" height="18"')} WhatsApp {PHONE_D}</a><a class="btn gd" href="#hot">看精选推荐</a></div>
</section>
<nav class="ic" aria-label="分类快捷入口">{icons}</nav>
<div class="info"><div><b>🏮 散装 · 整盒</b>散装按件买，整盒按价目表箱价</div><div><b>🚚 取货 / 送货</b>自取 Sutera Mall · Lalamove 联系客服 · 西马邮寄 RM15</div><div><b>🧾 网站下单</b>选好产品、填好取货方式，一键提交订单</div></div>
<section class="ship" id="ship" aria-labelledby="h-ship">
<h2 id="h-ship">🚚 送货方式</h2>
<ul>
<li><b>🛍️ 自取（Sutera Mall）</b>下单时填写联系电话，客服会联系约自取时间</li>
<li><b>🛵 Lalamove（联系客服安排）</b>新山区 Lalamove 运费自付</li>
<li><b>📦 邮寄</b>西马邮费一律 RM15（任买），下单时需填写邮寄资料</li>
</ul>
</section>
<section class="ship" id="buy" aria-labelledby="h-buy">
<h2 id="h-buy">新山烟花炮竹，网上就能订</h2>
<p>要在新山买烟花、新山买炮竹或柔佛买鞭炮，不用只靠跑店。Hunter BOOM JOHOR 总代理在 <a href="https://hunterboom.my/">hunterboom.my</a> 做柔佛烟花炮竹批发零售，羊年春节新年烟花、红炮礼炮、Pop Pop 沙炮、手持烟花、喷泉喷花和盆花都可以网上选、网上订。自取在 Sutera Mall；新山也可请客服安排 Lalamove（运费自付）；西马邮寄 RM15。WhatsApp {PHONE_D}。</p>
</section>
<a class="kids-banner" href="#kids"><span>🧒</span><span>小朋友专区<small>手持、喷泉和趣味小品，请在家长看护下燃放</small></span></a>
<div id="list"><div id="featured">{''.join(secs)}</div>{catalog}<p class="nores" id="nores" hidden>找不到相关产品，试试其他关键词，或直接 <a href="{WA}" target="_blank" rel="noopener" style="color:#1fae55;font-weight:700">WhatsApp 询问</a>。</p></div>
</main>
{footer(root, 'home')}
</body></html>"""
    write("index.html", head(title, desc, "", root, extra_ld=[STORE_LD, SITE_LD, item_ld], keywords=KW) + body)

# ---------------- category pages ----------------
def catpages():
    root = "../"
    for c in CATS:
        items = BYCAT[c["id"]]
        prices = [main_price(p) for p in items]
        if c["id"] == "hongpao":
            title = "红炮礼炮炮竹 | 新山炮竹批发 | Hunter BOOM JOHOR"
        else:
            title = f"{c['name']} | 新山烟花炮竹批发零售 | Hunter BOOM JOHOR"
        sample = "、".join(p["name"] for p in items[:4])
        desc = f"新山{c['name']}、柔佛烟花炮竹：{len(items)} 款，散装 {rm(min(prices))} 起，如 {sample} 等。Hunter BOOM JOHOR 总代理，依斯干达公主城，可在 hunterboom.my 网上订购，WhatsApp {PHONE_D}。"
        ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{c['name']} | {BRAND}", "url": absu(f"c/{c['id']}.html"), "inLanguage": "zh-Hans",
               "isPartOf": {"@type": "WebSite", "name": BRAND, "url": absu("")},
               "mainEntity": {"@type": "ItemList", "numberOfItems": len(items),
                              "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absu(f"p/{p['sku']}.html"), "name": p["title"]} for i, p in enumerate(items)]}},
              bc_ld([("首页", ""), (c["name"], f"c/{c['id']}.html")])]
        others = " · ".join(f'<a href="{x["id"]}.html" style="color:#c8161d">{e(x["name"])}</a>' for x in CATS if x["id"] != c["id"])
        body = f"""<body data-root="{data_root('../')}">
{topbar(root, c['id'])}
<main class="wrap">
<nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <span>{e(c['name'])}</span></nav>
<section class="sec"><h1 style="font-size:21px;margin:4px 2px 4px;color:#8f0d13">{c['icon']} {e(c['name'])} · 新山烟花炮竹 <small style="font-size:13px;color:#8a5a4a">({len(items)} 款)</small></h1>
<p style="margin:0 2px 12px;color:#8a5a4a;font-size:13.5px">Hunter BOOM JOHOR 总代理{e(c['name'])}，新山、柔佛烟花炮竹批发零售，售价 {rm(min(prices))} – {rm(max(prices))}（包装 N/1 的可买散装或整盒；散装卖价 = 箱价 ÷ 件数 × 1.40）。依斯干达公主城出货，官网 hunterboom.my 网上就能订。</p>
<div class="g">{''.join(card(p, root, i) for i, p in enumerate(items))}</div></section>
<p style="font-size:13px;margin:0 2px 20px">其他分类：{others}</p>
</main>
{footer(root)}
</body></html>"""
        write(f"c/{c['id']}.html", head(title, desc, f"c/{c['id']}.html", root, extra_ld=ld, keywords=KW) + body)
    # category index
    kids_tile = (f'<a href="kids.html" class="pc" style="padding:14px;text-align:center;background:linear-gradient(180deg,#fff8e8,#fff)">'
                 f'<span style="font-size:34px">🧒</span><h2 style="margin:6px 0 2px;font-size:16px;color:#8f0d13">小朋友专区</h2>'
                 f'<span class="pk">{len(KIDS_ALL)} 款 · 手持喷泉小品</span></a>')
    tiles = kids_tile + "".join(f'<a href="{c["id"]}.html" class="pc" style="padding:14px;text-align:center"><span style="font-size:34px">{c["icon"]}</span><h2 style="margin:6px 0 2px;font-size:16px;color:#8f0d13">{e(c["name"])}</h2><span class="pk">{len(BYCAT[c["id"]])} 款 · {rm(min(main_price(p) for p in BYCAT[c["id"]]))} 起</span></a>' for c in CATS)
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"全部分类 | {BRAND}", "url": absu("c/index.html"),
           "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absu(f"c/{c['id']}.html"), "name": c["name"]} for i, c in enumerate(CATS)]}},
          bc_ld([("首页", ""), ("全部分类", "c/index.html")])]
    body = f"""<body data-root="{data_root('../')}">
{topbar(root)}
<main class="wrap"><nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <span>全部分类</span></nav>
<h1 style="font-size:21px;margin:4px 2px 12px;color:#8f0d13">烟花炮竹分类 · 新山 Hunter BOOM JOHOR</h1>
<div class="g">{tiles}</div></main>
{footer(root, 'cats')}
</body></html>"""
    write("c/index.html", head("烟花炮竹分类 | 新山烟花炮竹批发零售 | Hunter BOOM JOHOR", f"浏览 Hunter BOOM JOHOR 总代理全部 {len(CATS)} 个新山烟花炮竹分类：红炮礼炮、鞭炮、Pop Pop 沙炮、手持烟花、喷泉喷花、盆花、大盆花等。柔佛依斯干达公主城，官网网上订购，WhatsApp 下单。", "c/index.html", root, extra_ld=ld, keywords=KW) + body)

    # 小朋友专区 collection (editorial merchandising, not a formal category)
    kids_items = [BY_SKU[s] for s in KIDS_ALL]
    prices = [main_price(p) for p in kids_items]
    kids_title = "小朋友专区 | 新山烟花炮竹 | Hunter BOOM JOHOR"
    kids_desc = f"Hunter BOOM JOHOR 小朋友专区：{len(kids_items)} 款较温和的手持烟花、喷泉和趣味小品，售价 {rm(min(prices))} 起。请由成人操作或家长看护。新山、柔佛烟花网上可订，依斯干达公主城，WhatsApp {PHONE_D}。"
    kids_ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"小朋友专区 | {BRAND}", "url": absu("c/kids.html"), "inLanguage": "zh-Hans",
                "isPartOf": {"@type": "WebSite", "name": BRAND, "url": absu("")},
                "description": KIDS_NOTE,
                "mainEntity": {"@type": "ItemList", "numberOfItems": len(kids_items),
                               "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absu(f"p/{p['sku']}.html"), "name": p["title"]} for i, p in enumerate(kids_items)]}},
               bc_ld([("首页", ""), ("小朋友专区", "c/kids.html")])]
    kids_body = f"""<body data-root="{data_root('../')}">
{topbar(root)}
<main class="wrap">
<nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <span>小朋友专区</span></nav>
<section class="sec"><h1 style="font-size:21px;margin:4px 2px 4px;color:#8f0d13">🧒 小朋友专区 · 新山烟花炮竹 <small style="font-size:13px;color:#8a5a4a">({len(kids_items)} 款)</small></h1>
<p class="shelf-note" style="margin:0 2px 14px">{e(KIDS_NOTE)} 售价 {rm(min(prices))} – {rm(max(prices))}。</p>
<div class="g">{''.join(card(p, root, i) for i, p in enumerate(kids_items))}</div></section>
</main>
{footer(root)}
</body></html>"""
    write("c/kids.html", head(kids_title, kids_desc, "c/kids.html", root, extra_ld=kids_ld, keywords=KW) + kids_body)

# ---------------- product pages ----------------
def video_section(p):
    """「视频介绍」 block for a product page. Real catalog/official video or an honest placeholder."""
    if p.get("video_embed"):
        vert = p.get("video_orientation") == "vertical"
        if p["video_kind"] == "youtube":
            src = p["video_embed"] + "?rel=0&modestbranding=1&playsinline=1"
            allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            open_txt = "在 YouTube 打开"
        else:
            src = p["video_embed"]; allow = "autoplay; encrypted-media; fullscreen"
            open_txt = "在 Google Drive 打开"
        t = f"{p['title']} 燃放视频介绍"
        return (f'<section class="vid" id="video"><h2>视频介绍 <small>{e(p["sku"])}</small></h2>'
                f'<div class="vf {"v916" if vert else "v169"}"><iframe src="{e(src)}" title="{e(t)}" loading="lazy" '
                f'allow="{allow}" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>'
                f'<p class="vs">视频来源：{e("Hunter Boom 官方" if p["video_kind"]=="youtube" else "TT Fireworks 产品目录")}'
                f' · <a href="{e(p["video"])}" target="_blank" rel="noopener">{open_txt}</a></p></section>')
    return (f'<section class="vid" id="video"><h2>视频介绍 <small>{e(p["sku"])}</small></h2>'
            f'<div class="vph">{BURST}<b>视频介绍待更新</b><i>这款暂时还没有官方燃放视频</i>'
            f'<a class="btn wa" href="{WA}?text={e(urllib.parse.quote("你好，想看 " + p["sku"] + " " + p["title"] + " 的燃放视频"))}" target="_blank" rel="noopener">WhatsApp 索取视频</a></div></section>')

def video_ld(p, url):
    if not p.get("video_embed"): return None
    if p["video_kind"] == "youtube":
        vid = p["video_embed"].rsplit("/", 1)[1]; thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
    else:
        fid = p["video_embed"].split("/d/")[1].split("/")[0]; thumb = f"https://drive.google.com/thumbnail?id={fid}&sz=w640"
    return {"@context": "https://schema.org", "@type": "VideoObject", "name": f"{p['title']} 燃放视频介绍",
            "description": f"{p['title']}（{p['sku']}）烟花炮竹燃放效果视频，Hunter BOOM JOHOR 新山。",
            "thumbnailUrl": thumb, "embedUrl": p["video_embed"], "url": p["video"], "isPartOf": absu(url)}

def pd_price(p):
    """Product page price block; for dual products a 散装 / 整盒 picker (radio name="mode")."""
    m = mode(p)
    if m == "dual":
        lp, cp, n = p["loose_price"], carton(p), p["piece_qty"]
        return (f'<fieldset class="um"><legend>选择购买方式</legend>'
                f'<label><input type="radio" name="mode" value="l" data-price="{lp:.2f}" data-unit="件" checked>'
                f'<span><b>散装</b><em>{rm(lp)}</em><small>/件</small></span></label>'
                f'<label><input type="radio" name="mode" value="b" data-price="{cp:.2f}" data-unit="盒">'
                f'<span><b>整盒</b><em>{rm(cp)}</em><small>/盒 · {n}件</small></span></label></fieldset>')
    if m == "single":
        return f'<div class="pr">{rm(p["loose_price"])}<small>/件</small></div>'
    return f'<div class="pr"><small>整盒</small> {rm(carton(p))}<small>/盒</small></div>'

def pd_note(p):
    m = mode(p)
    if m == "dual": return f"散装按件卖（{p['piece_qty']}件一盒），也可整盒买（整盒按价目表箱价）。"
    if m == "single": return "单件卖价。"
    return f"整盒价 · 包装 {p['packing']}。散装件数待确认，暂时只卖整盒，散装请 WhatsApp 询问。"

def pd_unit(p):
    return {"dual": "件（散装）", "single": "件"}.get(mode(p), "盒（整盒）")

def pd_rows(p):
    m = mode(p)
    if m == "dual":
        return (f'<tr><th>一盒件数</th><td>{p["piece_qty"]} 件</td></tr>'
                f'<tr><th>散装卖价</th><td>{rm(p["loose_price"])} / 件</td></tr>'
                f'<tr><th>整盒价</th><td>{rm(carton(p))} / 盒（价目表箱价）</td></tr>')
    if m == "single":
        return f'<tr><th>卖价</th><td>{rm(p["loose_price"])} / 件</td></tr>'
    return (f'<tr><th>整盒价</th><td>{rm(carton(p))} / 盒（价目表箱价）</td></tr>'
            f'<tr><th>散装</th><td>件数待确认，暂只卖整盒</td></tr>')

def products():
    root = "../"
    for i, p in enumerate(P):
        c = CAT[p["category"]]
        en = f" {p['name_en']}" if p["name_en"] else ""
        title = f"{p['title']}{en} | {c['name']} | 新山烟花炮竹"
        desc = f"{p['title']}{('（' + p['name_en'] + '）') if p['name_en'] else ''}，编号 {p['sku']}，包装 {p['packing']}，{price_txt(p)}。Hunter BOOM JOHOR 总代理，新山依斯干达公主城烟花炮竹批发零售，可在 hunterboom.my 网上订购，WhatsApp {PHONE_D}。"
        url = f"p/{p['sku']}.html"
        prod = {"@context": "https://schema.org", "@type": "Product", "name": p["title"] + en, "sku": p["sku"],
                "description": desc, "category": c["name"], "url": absu(url), "brand": {"@type": "Brand", "name": "Hunter Boom"},
                "offers": {"@type": "Offer", "price": f"{main_price(p):.2f}", "priceCurrency": "MYR", "url": absu(url),
                           "itemCondition": "https://schema.org/NewCondition",
                           "seller": {"@type": "Organization", "name": SHOP, "@id": absu("") + "#store"}}}
        if p["name_en"]: prod["alternateName"] = p["name_en"]
        if p.get("image"): prod["image"] = (SITE_ORIGIN + "/" + p["image"]) if SITE_ORIGIN else "/" + p["image"]
        ld = [prod, bc_ld([("首页", ""), (c["name"], f"c/{c['id']}.html"), (p["title"], url)])]
        vld = video_ld(p, url)
        if vld: ld.append(vld)
        rel = [x for x in BYCAT[c["id"]] if x["sku"] != p["sku"]]
        j = BYCAT[c["id"]].index(p)
        rel = (BYCAT[c["id"]][j + 1:] + BYCAT[c["id"]][:j])[:8]
        prv = P[i - 1] if i > 0 else None; nxt = P[i + 1] if i + 1 < len(P) else None
        pn = '<nav class="pn" aria-label="上一款/下一款">' + (f'<a href="{prv["sku"]}.html" rel="prev">‹ {e(prv["title"])}</a>' if prv else "<span></span>") + (f'<a href="{nxt["sku"]}.html" rel="next">{e(nxt["title"])} ›</a>' if nxt else "<span></span>") + "</nav>"
        en_row = f'<tr><th>英文名</th><td lang="en">{e(p["name_en"])}</td></tr>' if p["name_en"] else ""
        img_src = (("产品图片取自 TT Fireworks 产品目录" if p.get("image_source","").startswith("TT") else "产品图片取自 Hunter Boom 年货产品目录") if p.get("image") else "此款暂无目录产品图，实物请 WhatsApp 询问")
        body = f"""<body data-root="{data_root('../')}">
{topbar(root, c['id'])}
<main class="wrap">
<nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <a href="../c/{c['id']}.html">{e(c['name'])}</a> › <span>{e(p['title'])}</span></nav>
<article class="pd">
<div class="im{' big' if not p.get('image') else ''}">{img_block(p, root, big=True, lazy=False)}<span class="cd2">{p['sku']}</span></div>
<div class="pi">
<span class="cd2" style="position:static;display:inline-block">{p['sku']}</span>
<h1>{e(p['title'])}</h1>
{f'<p class="en" lang="en">{e(p["name_en"])}</p>' if p['name_en'] else ''}
{pd_price(p)}
<p class="note">{e(pd_note(p))}{e(SHIP_LINE)}产品价格以店家确认为准。</p>
<div class="act"><div class="qty"><button type="button" data-step="-1" data-for="qty" aria-label="减少数量">−</button><input id="qty" type="number" min="1" value="1" inputmode="numeric" aria-label="数量"><button type="button" data-step="1" data-for="qty" aria-label="增加数量">+</button></div><span class="qu" id="qu">{pd_unit(p)}</span></div>
<div class="act"><button type="button" class="btn gd" data-add data-qty-from="qty" data-mode-from="mode" {btn_attrs(p, root)}>加入购物车</button>
<button type="button" class="btn rd" data-wa-item data-qty-from="qty" data-mode-from="mode" {btn_attrs(p, root)}>加入购物车并下单</button></div>
<table class="sp"><caption class="sr">产品资料</caption>
<tr><th>编号</th><td>{p['sku']}</td></tr>
<tr><th>中文名</th><td>{e(p['name'])}</td></tr>{en_row}
<tr><th>包装</th><td>{e(p['packing'])}</td></tr>
{pd_rows(p)}
<tr><th>分类</th><td><a href="../c/{c['id']}.html" style="color:#c8161d">{e(c['name'])}</a></td></tr>
</table>
</div></article>
{video_section(p)}
<section class="desc"><h2>产品说明</h2>
<p>{e(intro(p))}。</p>
<p>{e(p['title'])}{('（' + e(p['name_en']) + '）') if p['name_en'] else ''}属于 Hunter BOOM JOHOR 总代理「{e(c['name'])}」系列，新山烟花炮竹批发零售，包装规格 {e(p['packing'])}，{e(price_txt(p))}。可在 hunterboom.my 网上订购。</p>
<p>送货：{e(SHIP_LINE)}新山、柔佛顾客可 WhatsApp <a href="{WA}" target="_blank" rel="noopener" style="color:#1fae55;font-weight:700">{PHONE_D}</a> 询问现货与批发数量。{img_src}。</p>
</section>
{pn}
<section class="sec"><h2>同类推荐 <small>{e(c['name'])}</small><a class="more" href="../c/{c['id']}.html">全部 ›</a></h2><div class="g">{''.join(card(x, root, 99) for x in rel)}</div></section>
</main>
{footer(root)}
</body></html>"""
        og = p["image"] if p.get("image") else None
        write(url, head(title, desc, url, root, og_img=og, extra_ld=ld, og_type="product") + body)

# ---------------- about / 404 ----------------
def about():
    root = ""
    faq = [("新山哪里可以买烟花炮竹？", "Hunter BOOM JOHOR 总代理在官网 hunterboom.my 就能订新山烟花、新山炮竹和柔佛鞭炮，不用只靠跑店。自取在 Sutera Mall；新山也可请客服安排 Lalamove（运费自付）；西马邮寄 RM15。WhatsApp 017-789 1688。"),
           ("可以网上买烟花、网上买炮吗？", "可以。打开 hunterboom.my，选好烟花或炮竹，填写取货方式后提交订单即可。客服确认款项后才会备货及出货。"),
           ("怎么下单？", "在网站挑选产品，选散装或整盒加入购物车；打开购物车选好取货方式（自取 Sutera Mall / Lalamove / 邮寄，邮寄需填写邮寄资料），填写姓名和电话（邮寄需填写邮寄资料），点「提交订单」。网站会记录订单并显示单号，同时打开 WhatsApp 方便你把「下单成功」和单号发给客服 017-789 1688。客服确认款项后才会备货及出货。"),
           ("散装和整盒有什么分别？", "包装为 N/1 的产品可以按件买散装，也可以买整盒。整盒按价目表箱价；散装卖价 = 价目表箱价 ÷ 一盒件数 × 1.40。1/1 的产品本身就是单件。其他包装规格的散装件数待确认，暂时只卖整盒，散装请 WhatsApp 询问。"),
           ("有送货吗？", "下单时选一项：" + SHIP_FACE + "；" + SHIP_JB + "；" + SHIP_WM + "。"),
           ("价格是最终价格吗？", "网站价格为参考价，产品价格以店家确认为准。邮寄西马一律 RM15（任买），会算进参考合计；Lalamove 新山区运费自付，由客服联系安排。")]
    ld = [STORE_LD, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
          bc_ld([("首页", ""), ("关于我们", "about.html")])]
    body = f"""<body data-root="{data_root()}">
{topbar(root)}
<main class="wrap"><nav class="bc" aria-label="面包屑"><a href="index.html">首页</a> › <span>关于我们</span></nav>
<article class="txt"><h1>关于 Hunter BOOM JOHOR 总代理</h1>
<p><b>{TAG}</b></p>
<p>Hunter BOOM JOHOR 总代理位于柔佛新山依斯干达公主城（Iskandar Puteri），提供新山烟花、新山炮竹、柔佛烟花炮竹批发与零售，产品包括红炮礼炮、鞭炮、Pop Pop 沙炮、手持烟花、喷泉喷花、飞天趣味、响声系列、盆花与大盆花等，迎接{CNY}。也可以在官网 hunterboom.my 网上买烟花、网上买炮。</p>
<h2>下单方式</h2><ol><li>浏览产品，选散装或整盒，点「加入购物车」，可调整数量。</li><li>打开购物车，选择取货方式：自取（Sutera Mall）、Lalamove（联系客服安排）或邮寄；每单都需填写姓名和电话；选邮寄另需填写邮寄资料（地址、邮区编号、城市、州属）。</li><li>点「提交订单」，网站记录订单并显示「下单成功」和单号，再打开 WhatsApp 方便你把单号发给客服 {PHONE_D}（未发送也不影响订单）。</li><li>客服通过 WhatsApp 确认价格、数量与付款；确认款项后才备货及出货。</li></ol>
<h2>送货方式</h2>
<ul>
<li><b>自取（Sutera Mall）：</b>下单时填写联系电话，客服会联系约自取时间</li>
<li><b>Lalamove（联系客服安排）：</b>新山区 Lalamove 运费自付</li>
<li><b>邮寄：</b>西马邮费一律 RM15（任买），下单时需填写邮寄资料</li>
</ul>
<h2>常见问题</h2>{''.join(f'<h3 style="font-size:15px;margin:12px 0 4px">{e(q)}</h3><p style="margin:0">{e(a)}</p>' for q, a in faq)}
<h2>联系资料</h2><address style="font-style:normal"><p>店名：{SHOP}<br>地址：{ADDR}（{ADDR_ZH}）<br>WhatsApp / 电话：<a href="{WA}" target="_blank" rel="noopener" style="color:#1fae55;font-weight:700">{PHONE_D}</a><br>Facebook：<a href="{FB}" target="_blank" rel="noopener" style="color:#c8161d">{SHOP}</a><br>营业时间：Facebook 主页显示 Always open（来取货前请先 WhatsApp 约时间）</p></address>
<p><a class="btn wa" href="{WA}" target="_blank" rel="noopener">WhatsApp {PHONE_D}</a></p>
</article></main>
{footer(root)}
</body></html>"""
    write("about.html", head("关于我们 · 下单方式 | 新山烟花炮竹 | Hunter BOOM JOHOR", f"Hunter BOOM JOHOR 总代理：柔佛新山烟花炮竹批发零售，Sutera Mall 自取，也可网上订购。了解下单方式、柔佛送货与联系资料：{PHONE_D}，官网 hunterboom.my。", "about.html", root, extra_ld=ld, keywords=KW) + body)
    # 404 is served for any missing path; use the public origin so links do not jump off the GitHub Pages subpath.
    r404 = (SITE_ORIGIN + "/") if SITE_ORIGIN else "/"
    nf = head("找不到页面 | Hunter BOOM JOHOR", "页面不存在，返回 Hunter BOOM JOHOR 新山烟花首页。", "404.html", r404).replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')
    write("404.html", nf + f"""<body data-root="{r404}">{topbar(r404)}<main class="wrap"><div class="txt"><h1>找不到这个页面</h1><p>链接可能已更改。<a href="{r404}index.html" style="color:#c8161d">返回首页</a>，或 <a href="{WA}" style="color:#1fae55">WhatsApp {PHONE_D}</a> 询问。</p></div></main>{footer(r404)}</body></html>""")

# ---------------- 店铺统计 / 下单记录 (zwvh.html): PRIVATE, owner PIN, unlisted, noindex, not in sitemap ----------------
STATS_CSS = """<style>
.st-hd{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:6px}
.st-hd h1{margin:0}
.st-date{color:var(--mut);font-size:13px}
.st-out{border:0;background:none;color:var(--mut);text-decoration:underline;cursor:pointer;font-size:12px}
.st-tiles{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:14px 0}
@media(min-width:700px){.st-tiles{grid-template-columns:repeat(4,1fr)}}
.st-tile{background:linear-gradient(160deg,#c8161d,#8f0d13);color:#fff3d0;border-radius:16px;padding:14px 12px;text-align:center;box-shadow:0 6px 18px #8f0d1333;position:relative;overflow:hidden}
.st-tile:after{content:"";position:absolute;inset:auto -20px -30px auto;width:90px;height:90px;border-radius:50%;background:#f6c45322}
.st-tile span{display:block;font-size:13px;letter-spacing:1px;color:#ffdf8a}
.st-tile b{display:block;font-size:38px;line-height:1.15;margin:6px 0 2px;color:#fff;font-variant-numeric:tabular-nums}
.st-tile small{font-size:11px;color:#f3c9a3}
.st-status{font-size:12.5px;color:var(--mut);margin:4px 0 10px}
.st-status.err{color:#c8161d;font-weight:700;background:#fff3d0;border:1px solid #f6c453;border-radius:10px;padding:8px 10px}
.st-gate{max-width:380px;margin:30px auto;text-align:center}
.st-gate form{display:flex;gap:8px;margin-top:12px}
.st-gate input{flex:1;padding:12px;border:1px solid var(--line);border-radius:12px;font-size:18px;letter-spacing:4px;text-align:center}
.st-chart{background:#fffaf0;border:1px solid var(--line);border-radius:14px;padding:8px 6px 2px;margin:8px 0}
.st-chart svg{width:100%;height:auto;display:block}
.st-key{font-size:12px;color:var(--mut);display:flex;gap:14px;flex-wrap:wrap;margin:4px 2px 0}
.st-key i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
.st-tbl{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px;font-variant-numeric:tabular-nums}
.st-tbl th{background:#c8161d;color:#fff3d0;font-weight:700;padding:8px 6px;text-align:right}
.st-tbl th:first-child,.st-tbl td:first-child{text-align:left}
.st-tbl td{padding:7px 6px;border-bottom:1px solid var(--line);text-align:right}
.st-tbl tr[data-day]{cursor:pointer}
.st-tbl td small{color:var(--mut);font-size:11px}
.st-tbl td a{color:var(--r);font-weight:700}
.st-tbl tr.today td{background:#fff3d0;font-weight:700}
.st-def{font-size:13px;color:var(--ink);background:#fffaf0;border-left:4px solid #f6c453;border-radius:8px;padding:8px 12px;margin:12px 0 0}
.st-def p{margin:3px 0}
.od-box{border:2px solid #f6c453;border-radius:16px;padding:12px;background:#fffdf6;margin:6px 0 14px}
.od-top{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between}
.od-top h2{margin:0}
.od-top select{padding:8px 10px;border-radius:10px;border:1px solid var(--line);font-size:14px;background:#fff;max-width:100%}
.od-sum{display:flex;flex-wrap:wrap;gap:8px 16px;margin:10px 0;font-size:14px}
.od-sum b{color:var(--rd);font-size:18px}
.od-fl{display:flex;gap:6px;margin:6px 0 10px}
.od-fl button{border:1px solid var(--line);background:#fff;border-radius:999px;padding:5px 12px;font-size:13px;cursor:pointer}
.od-fl button.on{background:#c8161d;color:#fff3d0;border-color:#c8161d}
.od{border:1px solid var(--line);border-left:5px solid #c8161d;border-radius:12px;padding:10px 12px;margin:0 0 10px;background:#fff}
.od.done{border-left-color:#1fae55;opacity:.8}
.od-h{display:flex;justify-content:space-between;gap:8px;font-weight:700}
.od-h small{font-weight:400;color:var(--mut)}
.od-s{color:#c8161d}.od.done .od-s{color:#1fae55}
.od-p{color:#b3121b;font-weight:800;margin-left:8px}.od-p.ok{color:#1fae55}
.od-warn{margin:0 0 6px;font-size:13px;font-weight:700;color:#8f4a00;background:#fff3d6;border-radius:8px;padding:4px 8px}
.od-b .btn[disabled]{opacity:.55;cursor:not-allowed}
.od ul{margin:8px 0;padding-left:18px;font-size:14px}
.od li span{font-weight:700;color:var(--rd)}
.od li small{color:var(--mut)}
.od-f{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;font-size:14px}
.od-no{font-family:ui-monospace,Menlo,Consolas,monospace;background:#fff3d0;color:#8f0d13;border-radius:6px;padding:1px 6px;margin-right:4px;letter-spacing:.3px}
.od-na{color:var(--mut);font-weight:500}
.od-d{margin:0 0 6px;font-size:13.5px;font-weight:700;color:#14693a}
.od-ship{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;margin:0 0 8px;font-size:13px;background:#fffaf0;border-radius:8px;padding:6px 10px}
.od-ship dt{color:var(--mut)}.od-ship dd{margin:0;word-break:break-word}
.od-b{display:flex;gap:6px;flex-wrap:wrap}
.od-b .btn{padding:7px 12px;font-size:13px}
.od-empty{text-align:center;color:var(--mut);padding:18px 6px}
@media(max-width:420px){.st-tile b{font-size:30px}.st-tile{padding:12px 6px}}
.st-tile b.rmv{font-size:26px}
@media(max-width:420px){.st-tile b.rmv{font-size:21px}}
.st-gate form.col{flex-direction:column;text-align:left}
.st-gate form.col label{font-size:13px;color:var(--mut);font-weight:600;display:flex;flex-direction:column;gap:4px}
.st-gate form.col input{letter-spacing:1px;font-size:16px;text-align:left}
.st-gate .hint{font-size:13px;color:var(--mut);text-align:left;background:#fffaf0;border-radius:10px;padding:8px 10px;margin:8px 0 0}
.st-find{display:flex;gap:8px;margin:4px 0 6px}
.st-find input{flex:1;min-width:0;padding:10px 12px;border:1.5px solid var(--line);border-radius:12px;font-size:15px;font-family:ui-monospace,Menlo,Consolas,monospace;text-transform:uppercase}
.st-find .btn{padding:9px 14px}
.st-box{border:1px solid var(--line);border-radius:16px;padding:12px;background:#fff;margin:6px 0 14px}
.st-box h2{margin:0 0 6px}
.od-brk{display:grid;gap:10px;margin:6px 0 10px}
@media(min-width:700px){.od-brk{grid-template-columns:1fr 1.4fr}}
.od-brk table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums;background:#fff;border-radius:10px;overflow:hidden}
.od-brk caption{text-align:left;font-weight:800;color:var(--rd);font-size:13.5px;padding:0 0 4px}
.od-brk th,.od-brk td{padding:5px 6px;border-bottom:1px solid var(--line);text-align:right}
.od-brk th{background:#fff3d0;color:#8f0d13}
.od-brk th:first-child,.od-brk td:first-child{text-align:left}
button.od-no{border:0;cursor:pointer;font-size:14px;font-weight:800;text-decoration:underline dotted}
.od li .tg{font-size:11px;background:#fde3c0;color:#8f0d13;border-radius:6px;padding:0 5px;margin-left:3px;font-weight:700}
.st-modal{position:fixed;inset:0;z-index:70;background:#2a0a0699;display:flex;align-items:flex-start;justify-content:center;overflow-y:auto;padding:20px 10px}
.st-modal[hidden]{display:none}
.st-slip{background:#fff;border-radius:16px;max-width:560px;width:100%;padding:16px 18px;box-shadow:0 10px 30px #0005}
.st-slip h2{margin:0 0 6px;color:#8f0d13}
.st-slip table{width:100%;border-collapse:collapse;font-size:13.5px;margin:8px 0;font-variant-numeric:tabular-nums}
.st-slip th,.st-slip td{border-bottom:1px solid var(--line);padding:6px 4px;text-align:left}
.st-slip td.n,.st-slip th.n{text-align:right}
.st-slip .tot{text-align:right;font-size:14px}.st-slip .tot b{font-size:18px;color:var(--r)}
.st-slip .bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.st-pw{margin:16px 0 0;font-size:13px}
.st-pw summary{cursor:pointer;color:var(--mut)}
.st-pw form{display:grid;gap:6px;max-width:320px;margin-top:8px}
.st-pw input{padding:8px 10px;border:1px solid var(--line);border-radius:10px;font-size:15px}
@media print{body *{visibility:hidden}#st-slip,#st-slip *{visibility:visible}#st-slip{position:absolute;inset:0;background:#fff;padding:0}.st-slip{box-shadow:none}.st-slip .bar{display:none}}
</style>"""

def stats_page():
    root = ""
    hd = head("店家后台 | Hunter BOOM JOHOR", "店家内部页面。", "zwvh.html", root)
    hd = hd.replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex,nofollow,noarchive">\n<meta name="referrer" content="no-referrer">')
    hd = hd.replace("</head>", STATS_CSS + "\n</head>")
    body = f"""<body data-root="{data_root()}" data-stats-page>
{topbar(root)}
<main class="wrap">
<section class="txt st-gate" id="st-gate">
<h1>🔒 店家后台</h1>
<div id="st-lg"><p>仅限店家查看，请输入后台密码。</p>
<form id="st-login" autocomplete="off"><label class="sr" for="st-pin">密码</label><input id="st-pin" type="password" autocomplete="current-password" placeholder="密码"><button class="btn gd" id="st-go" type="submit">进入</button></form></div>
<div id="st-su" hidden><p><b>第一次使用：请设置后台密码</b></p>
<p class="hint">为防止别人抢先设置，需要输入一次性的「设置码」。设置码在店家自己的 Google 表格「Hunter BOOM JOHOR 网站统计」→「后台设置」分页（B2 格）。设置成功后设置码自动作废。</p>
<form id="st-setup" class="col" autocomplete="off">
<label for="su-code">设置码<input id="su-code" autocomplete="one-time-code" autocapitalize="characters" spellcheck="false"></label>
<label for="su-pin">新后台密码（至少 6 位，不含空格）<input id="su-pin" type="password" autocomplete="new-password"></label>
<label for="su-pin2">再输入一次<input id="su-pin2" type="password" autocomplete="new-password"></label>
<button class="btn gd" id="su-go" type="submit">设置密码并进入</button></form></div>
<p class="st-status" id="st-gmsg"></p>
</section>
<section class="txt" id="stats" hidden>
<div class="st-hd"><h1>🏪 店家后台</h1><span class="st-date">今天：<b id="st-date">—</b> <button type="button" class="st-out" id="st-out">退出</button></span></div>
<p class="st-status" id="st-status">正在读取…</p>
<div class="st-tiles">
<div class="st-tile"><span>今日下单</span><b id="st-orders">—</b><small>次（网站发出）</small></div>
<div class="st-tile"><span>今日销售</span><b class="rmv" id="st-sales">—</b><small id="st-ototal">商品参考合计</small></div>
<div class="st-tile"><span>今日人数</span><b id="st-visitors">—</b><small>独立访客</small></div>
<div class="st-tile"><span>今日浏览</span><b id="st-views">—</b><small>页面浏览次数</small></div>
</div>
<div class="st-box" id="find"><h2>🔎 查单号</h2>
<form class="st-find" id="st-find" autocomplete="off"><label class="sr" for="fq">单号</label><input id="fq" placeholder="HBJ-20261113-XXXX 或后 4 位" maxlength="24" spellcheck="false"><button class="btn gd" type="submit">查找</button></form>
<div id="find-res"></div></div>
<div class="od-box" id="orders">
<div class="od-top"><h2>🧾 下单记录 · 客服工单</h2><label><span class="sr">选择日期</span><select id="od-day"></select></label></div>
<div class="od-sum"><span id="od-title">—</span><span>下单 <b id="od-count">0</b> 次</span><span>商品小计 <b id="od-total">RM0.00</b></span><span>邮费 <b id="od-post">RM0.00</b></span><span>合计 <b id="od-grand">RM0.00</b></span><span>当天待处理 <b id="od-pend">0</b></span><span>当天待收款 <b id="od-unpaid">0</b></span><span>全部待处理 <b id="st-pall">0</b></span></div>
<div class="od-brk" id="od-brk"></div>
<div class="od-fl"><button type="button" data-filt="all" class="on">全部</button><button type="button" data-filt="unpaid">💰 待收款</button><button type="button" data-filt="pending">⏳ 待处理</button><button type="button" data-filt="done">✅ 已处理</button></div>
<div id="od-list"></div>
<p class="st-status">顾客在网站点「提交订单」后，订单（含单号、姓名、电话）先记在这里，再打开 WhatsApp 让顾客把单号发给客服。流程：💰 待收款 →「确认收款」→ 备货 / 出货 →「已备货出货（标记已处理）」。未确认收款不能标记出货。时间为马来西亚时间（UTC+8）。</p>
</div>
<h2>近 14 天走势</h2>
<div class="st-chart" id="st-chart"></div>
<div class="st-key"><span><i style="background:#f6c453"></i>浏览</span><span><i style="background:#c8161d"></i>人数</span><span>🛒 下单次数</span></div>
<h2>近 30 天每日明细 <small style="font-size:12px;color:var(--mut);font-weight:400">（马来西亚时间 UTC+8，点一行看当天订单）</small></h2>
<p class="st-status" id="st-sum"></p>
<div style="overflow-x:auto"><table class="st-tbl"><thead><tr><th>日期</th><th>下单</th><th>商品参考合计</th><th>人数</th><th>浏览</th></tr></thead><tbody id="st-rows"></tbody></table></div>
<div class="st-def">
<p><b>下单</b> = 在本站提交成功的订单次数（最终成交以店家确认收款为准）</p>
<p><b>人数</b> = 当日独立访客（同一手机/浏览器一天只算一次）</p>
<p><b>浏览</b> = 当日页面浏览次数</p>
<p style="color:var(--mut);font-size:12px">日期按马来西亚时间（UTC+8）每天 00:00 重新计算。数字全部来自真实访问记录，从统计上线当天开始累计；本页本身的打开不计入浏览。参考合计为商品参考价（散装 / 整盒按网站卖价），邮寄单另记邮费 RM15；Lalamove 运费不含。</p>
</div>
<details class="st-pw"><summary>🔑 修改后台密码</summary>
<form id="st-chg" autocomplete="off"><input id="pw-old" type="password" placeholder="当前密码" autocomplete="current-password"><input id="pw-new" type="password" placeholder="新密码（至少 6 位）" autocomplete="new-password"><input id="pw-new2" type="password" placeholder="再输入一次" autocomplete="new-password"><button class="btn ol" type="submit">保存新密码</button><span class="st-status" id="pw-msg"></span></form></details>
</section></main>
<div class="st-modal" id="st-slip" hidden role="dialog" aria-modal="true" aria-label="出货单"><div class="st-slip" id="st-slip-in"></div></div>
{footer(root)}
</body></html>"""
    write("zwvh.html", hd + body)

def meta_files():
    urls = [("", "1.0"), ("c/index.html", "0.6"), ("c/kids.html", "0.8"), ("about.html", "0.5")] + [(f"c/{c['id']}.html", "0.8") for c in CATS] + [(f"p/{p['sku']}.html", "0.7") for p in P]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    img_by_path = {f"p/{p['sku']}.html": p for p in P if p.get("image")}
    for u, pr in urls:
        loc = f"<url><loc>{e(absu(u))}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority>"
        if u == "":
            loc += f'<image:image><image:loc>{e(absu("img/og-cny2027.jpg"))}</image:loc><image:title>Hunter BOOM JOHOR 总代理 三阳开泰 羊年海报</image:title></image:image>'
            loc += f'<image:image><image:loc>{e(absu("img/cny2027-poster.jpg"))}</image:loc><image:title>Hunter BOOM JOHOR 羊年春节海报</image:title></image:image>'
        p = img_by_path.get(u)
        if p:
            title = e(p["title"] + ((" " + p["name_en"]) if p.get("name_en") else "") + " 烟花炮竹产品图")
            loc += f'<image:image><image:loc>{e(absu(p["image"]))}</image:loc><image:title>{title}</image:title></image:image>'
        loc += "</url>"
        sm.append(loc)
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    smloc = (SITE_ORIGIN + "/sitemap.xml") if SITE_ORIGIN else "/sitemap.xml"
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {smloc}\n")
    write("site.webmanifest", json.dumps({"name": SHOP, "short_name": "Hunter BOOM", "lang": "zh-Hans", "start_url": "./index.html", "display": "standalone",
                                          "background_color": "#fdf3e3", "theme_color": "#c8161d",
                                          "icons": [{"src": "img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False, indent=1))
    return len(urls)

def cleanup_unpublished():
    """Delete leftover generated pages for products/categories no longer on the public site."""
    import glob
    live_skus = {p["sku"] for p in P}
    live_cats = {c["id"] for c in CATS} | {"index", "kids"}
    removed = []
    for fp in glob.glob(os.path.join(OUT_DIR, "p", "*.html")):
        sku = os.path.splitext(os.path.basename(fp))[0]
        if sku not in live_skus:
            os.remove(fp); removed.append("p/" + os.path.basename(fp))
    for fp in glob.glob(os.path.join(OUT_DIR, "c", "*.html")):
        cid = os.path.splitext(os.path.basename(fp))[0]
        if cid not in live_cats:
            os.remove(fp); removed.append("c/" + os.path.basename(fp))
    return removed


def maintenance_html():
    """Customer-facing poster: site under maintenance, contact customer service."""
    wa_ask = WA + "?text=" + urllib.parse.quote("你好，我想询问一下。")
    return f"""<!doctype html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>网站正在维护 | Hunter BOOM JOHOR</title>
<meta name="description" content="Hunter BOOM JOHOR 网站正在维护。有询问请联系客服 WhatsApp {PHONE_D}。">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{e(PUBLIC_ORIGIN)}/">
<meta name="theme-color" content="#9a1017">
<meta name="format-detection" content="telephone=yes">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="zh_CN">
<meta property="og:title" content="网站正在维护 | Hunter BOOM JOHOR">
<meta property="og:description" content="网站正在维护。有询问请联系客服 WhatsApp {PHONE_D}。">
<meta property="og:url" content="{e(PUBLIC_ORIGIN)}/">
<meta property="og:image" content="{e(PUBLIC_ORIGIN)}/img/og-cny2027.jpg">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/img/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<style>
  :root {{ --red:#9a1017; --red2:#c8161d; --deep:#5a090e; --gold:#e7c56a; --gold2:#f6e2a2; --cream:#fff3d0; --wa:#1fae55; }}
  * {{ box-sizing:border-box; }}
  html,body {{ margin:0; min-height:100%; }}
  body {{
    min-height:100dvh;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:24px 16px 40px;
    background:
      radial-gradient(ellipse at 50% 12%, #d41c24 0%, var(--red) 42%, var(--deep) 100%);
    font-family:"PingFang SC","Noto Sans SC","Microsoft YaHei","Source Han Sans SC",sans-serif;
    color:var(--cream);
    -webkit-font-smoothing:antialiased;
  }}
  .poster {{
    width:min(560px, 100%);
    text-align:center;
    padding:44px 28px 36px;
    background:linear-gradient(180deg, #b7141b 0%, #8f1016 55%, #7a0d13 100%);
    border:2px solid var(--gold);
    outline:6px solid rgba(90,9,14,.55);
    box-shadow:0 0 0 8px var(--gold), 0 28px 64px rgba(0,0,0,.38);
    border-radius:10px;
  }}
  .logo {{
    width:88px; height:88px;
    margin:0 auto 10px;
    filter:drop-shadow(0 4px 10px rgba(0,0,0,.25));
  }}
  .logo svg {{ width:88px; height:88px; display:block; }}
  .brand {{
    font-family:Georgia,"Noto Serif SC","Songti SC",serif;
    font-size:1.05rem;
    letter-spacing:.22em;
    color:var(--gold);
    font-weight:700;
    margin:0 0 2px;
    text-transform:uppercase;
  }}
  .subbrand {{
    font-size:.85rem;
    letter-spacing:.28em;
    color:var(--gold2);
    margin:0 0 28px;
    opacity:.95;
  }}
  h1 {{
    margin:0 0 16px;
    font-size:clamp(2rem, 8vw, 2.75rem);
    font-weight:800;
    letter-spacing:.18em;
    color:var(--gold2);
    text-shadow:0 2px 0 rgba(90,9,14,.45);
    line-height:1.25;
  }}
  .msg {{
    margin:0 0 28px;
    font-size:1.2rem;
    letter-spacing:.08em;
    line-height:1.7;
    color:#fff8e8;
  }}
  .wa {{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    background:var(--wa);
    color:#fff;
    text-decoration:none;
    font-weight:800;
    font-size:clamp(1.05rem, 4.6vw, 1.25rem);
    letter-spacing:.04em;
    padding:14px 22px;
    border-radius:999px;
    box-shadow:0 8px 22px rgba(0,0,0,.28);
    white-space:nowrap;
  }}
  .wa:hover {{ filter:brightness(1.06); }}
  .wa svg {{ width:26px; height:26px; fill:#fff; }}
  .hint {{
    margin:18px 0 0;
    font-size:.95rem;
    letter-spacing:.06em;
    color:var(--gold2);
    opacity:.9;
  }}
  .domain {{
    margin:22px 0 0;
    font-size:.8rem;
    letter-spacing:.16em;
    color:var(--gold);
    opacity:.75;
  }}
</style>
</head>
<body>
  <main class="poster">
    <div class="logo" aria-hidden="true">{LOGO}</div>
    <p class="brand">Hunter BOOM JOHOR</p>
    <p class="subbrand">总代理 · 新山</p>
    <h1>网站正在维护</h1>
    <p class="msg">有询问请联系客服</p>
    <a class="wa" href="{e(wa_ask)}" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.04 2C6.5 2 2 6.37 2 11.76c0 1.72.46 3.4 1.34 4.88L2 22l5.52-1.44A10.2 10.2 0 0 0 12.04 21.5C17.6 21.5 22 17.13 22 11.75 22 6.37 17.6 2 12.04 2zm5.95 14.18c-.25.7-1.45 1.3-2.02 1.38-.52.07-1.18.1-1.9-.12-.44-.13-1-.32-1.73-.63-3.05-1.32-5.04-4.4-5.19-4.6-.15-.2-1.22-1.62-1.22-3.1 0-1.47.77-2.2 1.04-2.5.27-.3.6-.37.8-.37h.58c.18 0 .43-.07.67.51.25.6.85 2.07.92 2.22.07.15.12.33.02.53-.1.2-.15.33-.3.5-.15.18-.31.4-.44.53-.15.15-.3.32-.13.62.17.3.76 1.25 1.63 2.03 1.12 1 2.07 1.32 2.36 1.47.3.15.47.13.64-.07.17-.2.73-.85.93-1.14.2-.3.4-.25.67-.15.27.1 1.72.81 2.01.96.3.15.5.22.57.35.07.12.07.7-.18 1.4z"/></svg>
      WhatsApp {PHONE_D}
    </a>
    <p class="hint">点击上方按钮即可联系客服</p>
    <p class="domain">hunterboom.my</p>
  </main>
</body>
</html>
"""


def write_customer_pages():
    """Homepage, 404, and previously public shop URLs all show the maintenance poster."""
    poster = maintenance_html()
    write("index.html", poster)
    write("404.html", poster)
    write("about.html", poster)
    # Category and product URLs already indexed by Google: show the same poster,
    # do not leave the live shop at these paths.
    write("c/index.html", poster)
    write("c/kids.html", poster)
    for c in CATS:
        write(f"c/{c['id']}.html", poster)
    for p in P:
        write(f"p/{p['sku']}.html", poster)


def write_public_meta():
    sm = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f"<url><loc>{e(PUBLIC_ORIGIN)}/</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority></url>",
        "</urlset>",
        "",
    ]
    write("sitemap.xml", "\n".join(sm))
    write(
        "robots.txt",
        "User-agent: *\n"
        "Allow: /\n"
        f"Disallow: /{DEMO_SLUG}\n"
        f"Disallow: /{DEMO_SLUG}/\n"
        "Disallow: /zwvh.html\n"
        f"\nSitemap: {PUBLIC_ORIGIN}/sitemap.xml\n",
    )
    # Keep the existing public webmanifest at the domain root (icons, theme).
    write("site.webmanifest", json.dumps({
        "name": SHOP, "short_name": "Hunter BOOM", "lang": "zh-Hans",
        "start_url": "./", "display": "standalone",
        "background_color": "#9a1017", "theme_color": "#9a1017",
        "icons": [
            {"src": "img/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "img/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }, ensure_ascii=False, indent=1))


def build_staff_demo():
    """Full shop under the unlisted demo path, for staff learning only."""
    global SITE_ORIGIN, OUT_DIR, DEMO_MODE, PAGE_ASSET
    DEMO_MODE = True
    PAGE_ASSET = "/"
    SITE_ORIGIN = PUBLIC_ORIGIN + "/" + DEMO_SLUG
    OUT_DIR = os.path.join(ROOT, DEMO_SLUG)
    os.makedirs(OUT_DIR, exist_ok=True)
    home(); catpages(); products(); about()
    # Demo 404 stays inside the demo shop so staff are not sent to the public poster.
    r404 = SITE_ORIGIN + "/"
    nf = head("找不到页面 | Hunter BOOM JOHOR", "页面不存在，返回演示首页。", "404.html", r404)
    write("404.html", nf + f"""<body data-root="{data_root()}">{topbar("")}<main class="wrap"><div class="txt"><h1>找不到这个页面</h1><p>链接可能已更改。<a href="{r404}" style="color:#c8161d">返回演示首页</a>。</p></div></main>{footer("")}</body></html>""")
    write("site.webmanifest", json.dumps({
        "name": SHOP + " 演示", "short_name": "Hunter BOOM", "lang": "zh-Hans",
        "start_url": "./index.html", "display": "standalone",
        "background_color": "#fdf3e3", "theme_color": "#c8161d",
        "icons": [
            {"src": "/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/img/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }, ensure_ascii=False, indent=1))
    gone = cleanup_unpublished()
    return gone


def build_public_site(demo_gone):
    """Customer site at the domain root: maintenance poster + merchant backend."""
    global SITE_ORIGIN, OUT_DIR, DEMO_MODE, PAGE_ASSET
    DEMO_MODE = False
    PAGE_ASSET = ""
    SITE_ORIGIN = PUBLIC_ORIGIN
    OUT_DIR = ROOT
    write_customer_pages()
    write_public_meta()
    stats_page()  # zwvh.html stays at the public origin, unlisted
    return demo_gone


if __name__ == "__main__":
    gone = build_staff_demo()
    build_public_site(gone)
    demo_url = PUBLIC_ORIGIN + "/" + DEMO_SLUG + "/"
    print(f"built {len(P)} products, {len(CATS)} categories")
    print(f"customer site: {PUBLIC_ORIGIN}/  (maintenance poster)")
    print(f"staff demo:    {demo_url}")
    if gone:
        print("removed unpublished from demo:", ", ".join(gone))
