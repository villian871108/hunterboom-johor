#!/usr/bin/env python3
"""Static site generator for Hunter BOOM JOHOR 总代理.

Usage:
  python3 tools/build_site.py                     # SITE_ORIGIN below (default: empty = relative URLs)
  python3 tools/build_site.py --origin https://your-domain.com   # set real domain before publishing

All pages are generated from data/products.json.
"""
import json, os, sys, html, datetime, urllib.parse

# ===== The ONE place to set the public domain (no trailing slash). =====
# Empty = root-relative canonical URLs. Set to the real domain once it is live,
# e.g. "https://hunterboomjohor.com" (placeholder, NOT live yet), then rebuild.
SITE_ORIGIN = ""
if "--origin" in sys.argv:
    SITE_ORIGIN = sys.argv[sys.argv.index("--origin") + 1].rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
PHONE_D = "017-827 0901"; PHONE_I = "+60178270901"; WA = "https://wa.me/60178270901"
FB = "https://www.facebook.com/profile.php?id=61585987514444"
ADDR = "Iskandar Puteri, Johor Bahru, Malaysia, 81200"
ADDR_ZH = "柔佛新山 依斯干达公主城（Iskandar Puteri）81200"
CNY = "羊年春节（2027年2月6日）"
# Delivery as stated by the shop (12 Nov 2026). Do not invent East Malaysia or free meetup.
SHIP_FACE = "五福城（Sutera）可面交，请先 WhatsApp 约时间"
SHIP_JB = "新山区可用 Lalamove，运费自付"
SHIP_WM = "西马邮费一律 RM15，买多少都是 RM15"
SHIP_LINE = "五福城（Sutera）可面交；新山区可用 Lalamove（运费自付）；西马邮费一律 RM15（任买）。"

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
def rm(x): return "RM{:,.2f}".format(x)
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
    img_abs = (SITE_ORIGIN + "/" + img) if SITE_ORIGIN else root + img
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
<meta name="robots" content="index,follow,max-image-preview:large">
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
<link rel="icon" href="{root}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}img/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="{root}img/apple-touch-icon.png">
<link rel="manifest" href="{root}site.webmanifest">
<link rel="stylesheet" href="{root}css/style.css?v=6">
{''.join(jd(x) for x in extra_ld)}
<!-- Optional analytics: none installed. Add your own tag here if needed. -->
</head>
"""

def topbar(root, active=None, home=False):
    tabs = []
    href = (lambda c: f"{root}c/{c['id']}.html")
    tabs.append(f'<a href="{root}index.html"{" class=on" if active=="home" else ""}>全部</a>')
    for c in CATS:
        tabs.append(f'<a href="{href(c)}"{" class=on" if active==c["id"] else ""}>{e(c["name"])}</a>')
    act = "" if home else f' action="{root}index.html"'
    return f"""<header class="top"><div class="in">
<a class="lg" href="{root}index.html" aria-label="{SHOP} 首页">{LOGO}<span class="wm"><b>Hunter BOOM</b><small>JOHOR 总代理 · 新山</small></span></a>
<form class="sb" role="search"{act} method="get"><label class="sr" for="q">搜索产品</label><input id="q" name="q" type="search" placeholder="搜索名称或编号，如 HB001、红炮、加特林" autocomplete="off"><button type="submit">搜索</button></form>
<nav class="tabs" aria-label="产品分类">{''.join(tabs)}</nav>
</div></header>
<div class="ann" role="note"><div class="in"><span>🧧 <b>{CNY}</b> 年货烟花现正接单</span><span>🏮 新山批发零售</span><span>🤝 五福城（Sutera）面交</span><span>📦 西马邮费 RM15 任买</span><span>📲 <a href="{WA}" target="_blank" rel="noopener">WhatsApp {PHONE_D}</a></span></div></div>
"""

def footer(root, active=None):
    cats = "".join(f'<a href="{root}c/{c["id"]}.html">{e(c["name"])}</a>' for c in CATS)
    def on(x): return ' class="on"' if active == x else ""
    return f"""<footer><div class="in">
<div><h2>{SHOP}</h2><p>{TAG}</p><p>新山烟花批发零售。{SHIP_LINE}</p></div>
<div><h3>联系我们</h3>
<address style="font-style:normal"><p>📍 {ADDR}<br><small>{ADDR_ZH}</small></p>
<p>📲 WhatsApp / 电话：<a href="{WA}" target="_blank" rel="noopener">{PHONE_D}</a></p>
<p>👍 Facebook：<a href="{FB}" target="_blank" rel="noopener">{SHOP}</a></p>
<p>🕒 营业时间：Facebook 主页显示 Always open，来取货前请先 WhatsApp 约时间。</p></address></div>
<div><h3>产品分类</h3><p class="cats">{cats}</p><p><a href="{root}about.html">关于我们 · 下单方式</a></p></div>
<p class="legal">温馨提示：燃放烟花请遵守当地法律法规及燃放时间、地点规定；购买前请自行确认所选产品在您所在地区允许使用。价格依据最新价目表（PACKING 为原表包装规格），最终价格、数量与送货安排以 WhatsApp 确认为准。本站为 {SHOP} 店铺网站，并非 Hunter Boom 品牌总部官网。© {datetime.date.today().year} {BRAND}</p>
</div></footer>
<button class="fc" id="fc" type="button" data-open-cart aria-label="打开购物车">{IC_CART.replace('<svg','<svg width="20" height="20"')}<span>0 件</span></button>
<nav class="bn" aria-label="底部导航">
<a href="{root}index.html"{on('home')}>{IC_HOME}首页</a>
<a href="{root}c/index.html"{on('cats')}>{IC_CAT}分类</a>
<button type="button" data-open-cart>{IC_CART}购物车<i class="bdg" data-badge>0</i></button>
<a class="wa" href="{WA}" target="_blank" rel="noopener">{IC_WA}WhatsApp</a>
</nav>
<script src="{root}js/cart.js?v=5" defer></script>
"""

def img_block(p, root, big=False, lazy=True, eager=False):
    if p.get("image"):
        src = p["thumb"] if not big else p["image"]
        w, h = (p["thumb_size"] if not big else p["image_size"])
        alt = f"{p['name']} {p['name_en']} 烟花产品图（Hunter BOOM JOHOR 新山）".replace("  ", " ")
        ld = 'loading="lazy" decoding="async"' if lazy and not eager else 'fetchpriority="high"'
        return f'<img src="{root}{src}" width="{w}" height="{h}" alt="{e(alt)}" {ld}>'
    return f'<div class="ph" role="img" aria-label="{e(p["name"])}（暂无产品图）">{BURST}<b>{e(p["name"])}</b><i>产品图待更新</i></div>'

def btn_attrs(p, root):
    i = p["thumb"] if p.get("image") else ""
    return f'data-sku="{p["sku"]}" data-name="{e(p["title"])}" data-price="{p["price"]:.2f}" data-img="{e(i)}"'


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
            f'<div class="row"><div><div class="pr">{rm(p["price"])}</div><div class="pk">包装 {e(p["packing"])}</div></div>'
            f'<button type="button" class="add" data-add {btn_attrs(p, root)} aria-label="把 {e(p["title"])} 加入购物车">加入购物车</button></div></div></article>')

STORE_LD = {
    "@context": "https://schema.org", "@type": "Store", "@id": absu("") + "#store",
    "name": SHOP, "alternateName": ["Hunter BOOM JOHOR", "Hunter Boom Johor 新山烟花", "猎人烟花 新山"],
    "description": f"{TAG}。新山烟花批发零售：红炮礼炮、Pop Pop 沙炮、手持烟花、喷泉、盆花与大盆花，WhatsApp 下单。",
    "url": absu(""), "image": (SITE_ORIGIN + "/img/og-cny2027.jpg") if SITE_ORIGIN else "/img/og-cny2027.jpg",
    "logo": (SITE_ORIGIN + "/img/icon-512.png") if SITE_ORIGIN else "/img/icon-512.png",
    "telephone": PHONE_I, "priceRange": "RM{:,.0f} – RM{:,.0f}".format(min(p["price"] for p in P), max(p["price"] for p in P)),
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
    fp = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(s)

KW = "新山烟花, 柔佛烟花, 猎人烟花, Hunter Boom Johor, 依斯干达公主城, 烟花批发, 羊年烟花, Johor Bahru fireworks, mercun Johor"

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
    title = "新山烟花批发零售 | Hunter BOOM JOHOR 总代理 | 柔佛依斯干达公主城"
    desc = f"Hunter BOOM JOHOR 总代理：新山烟花、柔佛烟花批发零售，{len(P)} 款羊年烟花——红炮礼炮、Pop Pop 沙炮、手持烟花、喷泉、盆花与大盆花。依斯干达公主城，WhatsApp {PHONE_D} 下单。"
    item_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Hunter BOOM JOHOR 产品分类",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c["name"], "url": absu(f"c/{c['id']}.html")} for i, c in enumerate(CATS)]}
    body = f"""<body data-root="">
{topbar(root, 'home', home=True)}
<main class="wrap">
<figure class="cny-poster">
<a href="img/cny2027-poster.jpg" target="_blank" rel="noopener">
<picture>
<source srcset="img/cny2027-poster.webp" type="image/webp">
<img src="img/cny2027-poster.jpg" width="1200" height="2278" alt="Hunter BOOM JOHOR 羊年春节海报：三阳开泰，总代理·新山，2027年2月6日，WhatsApp 017-827 0901" decoding="async">
</picture>
</a>
</figure>
<section class="hero" aria-labelledby="h1">
<span class="tag">🐐 {CNY}</span>
<h1 id="h1"><em>新山烟花</em>批发零售 · Hunter BOOM JOHOR 总代理</h1>
<p>{TAG}。柔佛烟花、猎人烟花（Hunter Boom）羊年烟花一站购齐：红炮礼炮、沙炮、手持烟花、喷泉与盆花，依斯干达公主城出货。{SHIP_LINE}</p>
<div class="cd" id="cd" aria-live="polite"></div>
<div class="btns"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">{IC_WA.replace('<svg','<svg width="18" height="18"')} WhatsApp {PHONE_D}</a><a class="btn gd" href="#hot">看精选推荐</a></div>
</section>
<nav class="ic" aria-label="分类快捷入口">{icons}</nav>
<div class="info"><div><b>🏮 批发 · 零售</b>整箱批发与零售都可询价</div><div><b>🚚 送货方式</b>五福城面交 · 新山 Lalamove 自付 · 西马 RM15</div><div><b>📲 WhatsApp 下单</b>选好产品一键发送订单</div></div>
<section class="ship" id="ship" aria-labelledby="h-ship">
<h2 id="h-ship">🚚 送货方式</h2>
<ul>
<li><b>🤝 面交</b>五福城（Sutera），请先 WhatsApp 约时间</li>
<li><b>🛵 新山区</b>可用 Lalamove，运费自付</li>
<li><b>📦 西马</b>邮费一律 RM15，买多少都是 RM15</li>
</ul>
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
        prices = [p["price"] for p in items]
        title = f"{c['name']}烟花 | 新山烟花批发零售 | Hunter BOOM JOHOR 总代理"
        sample = "、".join(p["name"] for p in items[:4])
        desc = f"新山 {c['name']}：{len(items)} 款，价目表价 {rm(min(prices))} 起，如 {sample} 等。Hunter BOOM JOHOR 总代理，柔佛依斯干达公主城，WhatsApp {PHONE_D} 下单。"
        ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{c['name']} | {BRAND}", "url": absu(f"c/{c['id']}.html"), "inLanguage": "zh-Hans",
               "isPartOf": {"@type": "WebSite", "name": BRAND, "url": absu("")},
               "mainEntity": {"@type": "ItemList", "numberOfItems": len(items),
                              "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absu(f"p/{p['sku']}.html"), "name": p["title"]} for i, p in enumerate(items)]}},
              bc_ld([("首页", ""), (c["name"], f"c/{c['id']}.html")])]
        others = " · ".join(f'<a href="{x["id"]}.html" style="color:#c8161d">{e(x["name"])}</a>' for x in CATS if x["id"] != c["id"])
        body = f"""<body data-root="../">
{topbar(root, c['id'])}
<main class="wrap">
<nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <span>{e(c['name'])}</span></nav>
<section class="sec"><h1 style="font-size:21px;margin:4px 2px 4px;color:#8f0d13">{c['icon']} {e(c['name'])} · 新山烟花 <small style="font-size:13px;color:#8a5a4a">({len(items)} 款)</small></h1>
<p style="margin:0 2px 12px;color:#8a5a4a;font-size:13.5px">Hunter BOOM JOHOR 总代理 {e(c['name'])}系列，价目表价 {rm(min(prices))} – {rm(max(prices))}。依斯干达公主城出货，羊年烟花批发零售，加入购物车后一键 WhatsApp 下单。</p>
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
    tiles = kids_tile + "".join(f'<a href="{c["id"]}.html" class="pc" style="padding:14px;text-align:center"><span style="font-size:34px">{c["icon"]}</span><h2 style="margin:6px 0 2px;font-size:16px;color:#8f0d13">{e(c["name"])}</h2><span class="pk">{len(BYCAT[c["id"]])} 款 · {rm(min(p["price"] for p in BYCAT[c["id"]]))} 起</span></a>' for c in CATS)
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"全部分类 | {BRAND}", "url": absu("c/index.html"),
           "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absu(f"c/{c['id']}.html"), "name": c["name"]} for i, c in enumerate(CATS)]}},
          bc_ld([("首页", ""), ("全部分类", "c/index.html")])]
    body = f"""<body data-root="../">
{topbar(root)}
<main class="wrap"><nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <span>全部分类</span></nav>
<h1 style="font-size:21px;margin:4px 2px 12px;color:#8f0d13">烟花分类 · 新山 Hunter BOOM JOHOR</h1>
<div class="g">{tiles}</div></main>
{footer(root, 'cats')}
</body></html>"""
    write("c/index.html", head("烟花分类 | 新山烟花批发零售 | Hunter BOOM JOHOR 总代理", f"浏览 Hunter BOOM JOHOR 总代理全部 {len(CATS)} 个烟花分类：红炮礼炮、Pop Pop 沙炮、手持烟花、喷泉喷花、盆花、大盆花等，新山依斯干达公主城 WhatsApp 下单。", "c/index.html", root, extra_ld=ld, keywords=KW) + body)

    # 小朋友专区 collection (editorial merchandising, not a formal category)
    kids_items = [BY_SKU[s] for s in KIDS_ALL]
    prices = [p["price"] for p in kids_items]
    kids_title = "小朋友专区 | 新山烟花 | Hunter BOOM JOHOR 总代理"
    kids_desc = f"Hunter BOOM JOHOR 小朋友专区：{len(kids_items)} 款较温和的手持、喷泉和趣味小品，价目表价 {rm(min(prices))} 起。请由成人操作或家长看护，遵守当地规定。新山依斯干达公主城，WhatsApp {PHONE_D} 下单。"
    kids_ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"小朋友专区 | {BRAND}", "url": absu("c/kids.html"), "inLanguage": "zh-Hans",
                "isPartOf": {"@type": "WebSite", "name": BRAND, "url": absu("")},
                "description": KIDS_NOTE,
                "mainEntity": {"@type": "ItemList", "numberOfItems": len(kids_items),
                               "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absu(f"p/{p['sku']}.html"), "name": p["title"]} for i, p in enumerate(kids_items)]}},
               bc_ld([("首页", ""), ("小朋友专区", "c/kids.html")])]
    kids_body = f"""<body data-root="../">
{topbar(root)}
<main class="wrap">
<nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <span>小朋友专区</span></nav>
<section class="sec"><h1 style="font-size:21px;margin:4px 2px 4px;color:#8f0d13">🧒 小朋友专区 · 新山烟花 <small style="font-size:13px;color:#8a5a4a">({len(kids_items)} 款)</small></h1>
<p class="shelf-note" style="margin:0 2px 14px">{e(KIDS_NOTE)} 价目表价 {rm(min(prices))} – {rm(max(prices))}。</p>
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
            "description": f"{p['title']}（{p['sku']}）烟花燃放效果视频，Hunter BOOM JOHOR 新山。",
            "thumbnailUrl": thumb, "embedUrl": p["video_embed"], "url": p["video"], "isPartOf": absu(url)}

def products():
    root = "../"
    for i, p in enumerate(P):
        c = CAT[p["category"]]
        en = f" {p['name_en']}" if p["name_en"] else ""
        title = f"{p['title']}{en} | {c['name']} | 新山烟花 Hunter BOOM JOHOR"
        desc = f"{p['title']}{('（' + p['name_en'] + '）') if p['name_en'] else ''}，编号 {p['sku']}，包装 {p['packing']}，价目表价 {rm(p['price'])}。Hunter BOOM JOHOR 总代理，新山依斯干达公主城烟花批发零售，WhatsApp {PHONE_D} 下单。"
        url = f"p/{p['sku']}.html"
        prod = {"@context": "https://schema.org", "@type": "Product", "name": p["title"] + en, "sku": p["sku"],
                "description": desc, "category": c["name"], "url": absu(url),
                "offers": {"@type": "Offer", "price": f"{p['price']:.2f}", "priceCurrency": "MYR", "url": absu(url),
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
        body = f"""<body data-root="../">
{topbar(root, c['id'])}
<main class="wrap">
<nav class="bc" aria-label="面包屑"><a href="../index.html">首页</a> › <a href="../c/{c['id']}.html">{e(c['name'])}</a> › <span>{e(p['title'])}</span></nav>
<article class="pd">
<div class="im{' big' if not p.get('image') else ''}">{img_block(p, root, big=True, lazy=False)}<span class="cd2">{p['sku']}</span></div>
<div class="pi">
<span class="cd2" style="position:static;display:inline-block">{p['sku']}</span>
<h1>{e(p['title'])}</h1>
{f'<p class="en" lang="en">{e(p["name_en"])}</p>' if p['name_en'] else ''}
<div class="pr">{rm(p['price'])}</div>
<p class="note">价目表价 · 包装 {e(p['packing'])}。{e(SHIP_LINE)}最终价格与数量以 WhatsApp 确认为准。</p>
<div class="act"><div class="qty"><button type="button" data-step="-1" data-for="qty" aria-label="减少数量">−</button><input id="qty" type="number" min="1" value="1" inputmode="numeric" aria-label="数量"><button type="button" data-step="1" data-for="qty" aria-label="增加数量">+</button></div></div>
<div class="act"><button type="button" class="btn gd" data-add data-qty-from="qty" {btn_attrs(p, root)}>加入购物车</button>
<button type="button" class="btn wa" data-wa-item data-qty-from="qty" {btn_attrs(p, root)}>WhatsApp 下单此款</button></div>
<table class="sp"><caption class="sr">产品资料</caption>
<tr><th>编号</th><td>{p['sku']}</td></tr>
<tr><th>中文名</th><td>{e(p['name'])}</td></tr>{en_row}
<tr><th>包装</th><td>{e(p['packing'])}</td></tr>
<tr><th>价目表价</th><td>{rm(p['price'])}</td></tr>
<tr><th>分类</th><td><a href="../c/{c['id']}.html" style="color:#c8161d">{e(c['name'])}</a></td></tr>
</table>
</div></article>
{video_section(p)}
<section class="desc"><h2>产品说明</h2>
<p>{e(intro(p))}。</p>
<p>{e(p['title'])}{('（' + e(p['name_en']) + '）') if p['name_en'] else ''}属于 Hunter BOOM JOHOR 总代理「{e(c['name'])}」系列，包装规格 {e(p['packing'])}，价目表价 {rm(p['price'])}。</p>
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
    faq = [("怎么下单？", "在网站挑选产品加入购物车，点「发送订单到 WhatsApp」，系统会把产品编号与数量整理成一段文字，发送给 017-827 0901，店家确认价格、数量与交货方式后完成下单。"),
           ("可以批发吗？", "可以。Hunter BOOM JOHOR 总代理提供批发与零售，整箱数量请 WhatsApp 询价。"),
           ("有送货吗？", SHIP_FACE + "。" + SHIP_JB + "。" + SHIP_WM + "。"),
           ("价格是最终价格吗？", "网站价格依据最新价目表，包装栏位（PACKING）为原表规格；最终价格与数量以店家 WhatsApp 回复为准。西马邮费一律 RM15（任买）；新山区 Lalamove 运费自付。")]
    ld = [STORE_LD, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
          bc_ld([("首页", ""), ("关于我们", "about.html")])]
    body = f"""<body data-root="">
{topbar(root)}
<main class="wrap"><nav class="bc" aria-label="面包屑"><a href="index.html">首页</a> › <span>关于我们</span></nav>
<article class="txt"><h1>关于 Hunter BOOM JOHOR 总代理</h1>
<p><b>{TAG}</b></p>
<p>Hunter BOOM JOHOR 总代理位于柔佛新山依斯干达公主城（Iskandar Puteri），提供新山烟花、柔佛烟花批发与零售，产品包括红炮礼炮、Pop Pop 沙炮、手持烟花、喷泉喷花、飞天趣味、响声系列、盆花与大盆花等，迎接{CNY}。</p>
<h2>下单方式</h2><ol><li>浏览产品，点「加入购物车」，可调整数量。</li><li>打开购物车，点「发送订单到 WhatsApp」。</li><li>店家通过 WhatsApp 确认价格、数量与送货安排。</li></ol>
<h2>送货方式</h2>
<ul>
<li><b>面交：</b>五福城（Sutera），请先 WhatsApp 约时间</li>
<li><b>新山区：</b>可用 Lalamove，运费自付</li>
<li><b>西马：</b>邮费一律 RM15，买多少都是 RM15</li>
</ul>
<h2>常见问题</h2>{''.join(f'<h3 style="font-size:15px;margin:12px 0 4px">{e(q)}</h3><p style="margin:0">{e(a)}</p>' for q, a in faq)}
<h2>联系资料</h2><address style="font-style:normal"><p>店名：{SHOP}<br>地址：{ADDR}（{ADDR_ZH}）<br>WhatsApp / 电话：<a href="{WA}" target="_blank" rel="noopener" style="color:#1fae55;font-weight:700">{PHONE_D}</a><br>Facebook：<a href="{FB}" target="_blank" rel="noopener" style="color:#c8161d">{SHOP}</a><br>营业时间：Facebook 主页显示 Always open（来取货前请先 WhatsApp 约时间）</p></address>
<p><a class="btn wa" href="{WA}" target="_blank" rel="noopener">WhatsApp {PHONE_D}</a></p>
</article></main>
{footer(root)}
</body></html>"""
    write("about.html", head("关于我们 · 下单方式 | Hunter BOOM JOHOR 总代理 | 新山烟花", f"Hunter BOOM JOHOR 总代理：柔佛新山依斯干达公主城烟花批发零售。了解 WhatsApp 下单方式、柔佛送货与联系资料：{PHONE_D}。", "about.html", root, extra_ld=ld, keywords=KW) + body)
    nf = head("找不到页面 | Hunter BOOM JOHOR", "页面不存在，返回 Hunter BOOM JOHOR 新山烟花首页。", "404.html", "/").replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')
    write("404.html", nf + f"""<body data-root="/">{topbar('/')}<main class="wrap"><div class="txt"><h1>找不到这个页面</h1><p>链接可能已更改。<a href="/index.html" style="color:#c8161d">返回首页</a>，或 <a href="{WA}" style="color:#1fae55">WhatsApp {PHONE_D}</a> 询问。</p></div></main>{footer('/')}</body></html>""")

def meta_files():
    urls = [("", "1.0"), ("c/index.html", "0.6"), ("c/kids.html", "0.8"), ("about.html", "0.5")] + [(f"c/{c['id']}.html", "0.8") for c in CATS] + [(f"p/{p['sku']}.html", "0.7") for p in P]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr in urls:
        sm.append(f"<url><loc>{e(absu(u))}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>")
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
    for fp in glob.glob(os.path.join(ROOT, "p", "*.html")):
        sku = os.path.splitext(os.path.basename(fp))[0]
        if sku not in live_skus:
            os.remove(fp); removed.append("p/" + os.path.basename(fp))
    for fp in glob.glob(os.path.join(ROOT, "c", "*.html")):
        cid = os.path.splitext(os.path.basename(fp))[0]
        if cid not in live_cats:
            os.remove(fp); removed.append("c/" + os.path.basename(fp))
    return removed

if __name__ == "__main__":
    home(); catpages(); products(); about(); n = meta_files()
    gone = cleanup_unpublished()
    print(f"built {len(P)} products, {len(CATS)} categories, sitemap urls={n}, SITE_ORIGIN={SITE_ORIGIN or '(relative)'}")
    if gone:
        print("removed unpublished:", ", ".join(gone))
