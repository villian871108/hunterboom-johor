#!/usr/bin/env python3
"""Static site generator for Hunter BOOM JOHOR 总代理.

Usage:
  python3 tools/build_site.py                     # SITE_ORIGIN below (default: empty = relative URLs)
  python3 tools/build_site.py --origin https://your-domain.com   # set real domain before publishing

All pages are generated from data/products.json.
"""
import json, os, sys, html, datetime

# ===== The ONE place to set the public domain (no trailing slash). =====
# Empty = root-relative canonical URLs. Set to the real domain once it is live,
# e.g. "https://hunterboomjohor.com" (placeholder, NOT live yet), then rebuild.
SITE_ORIGIN = ""
if "--origin" in sys.argv:
    SITE_ORIGIN = sys.argv[sys.argv.index("--origin") + 1].rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "products.json"), encoding="utf-8"))
P = D["products"]; CATS = D["categories"]
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
    img = og_img or "img/og.jpg"
    img_abs = (SITE_ORIGIN + "/" + img) if SITE_ORIGIN else root + img
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
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(img_abs)}">
<link rel="icon" href="{root}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}img/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="{root}img/apple-touch-icon.png">
<link rel="manifest" href="{root}site.webmanifest">
<link rel="stylesheet" href="{root}css/style.css?v=2">
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
<div class="ann" role="note"><div class="in"><span>🧧 <b>{CNY}</b> 年货烟花现正接单</span><span>🏮 新山批发零售</span><span>📍 依斯干达公主城</span><span>📲 <a href="{WA}" target="_blank" rel="noopener">WhatsApp {PHONE_D}</a></span></div></div>
"""

def footer(root, active=None):
    cats = "".join(f'<a href="{root}c/{c["id"]}.html">{e(c["name"])}</a>' for c in CATS)
    def on(x): return ' class="on"' if active == x else ""
    return f"""<footer><div class="in">
<div><h2>{SHOP}</h2><p>{TAG}</p><p>新山烟花批发零售，柔佛地区可安排送货（如五福城、Sutera、依斯干达公主城一带），详情请 WhatsApp 询问。</p></div>
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
<script src="{root}js/cart.js?v=2" defer></script>
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

def card(p, root, idx=0):
    s = f"{p['sku']} {p['name']} {p['title']} {p['name_en']} {CAT[p['category']]['name']}".lower()
    en = f'<div class="en" lang="en">{e(p["name_en"])}</div>' if p["name_en"] else '<div class="en">&nbsp;</div>'
    return (f'<article class="pc" data-s="{e(s)}"><a class="im" href="{root}p/{p["sku"]}.html">{img_block(p, root, eager=idx<4)}<span class="cd2">{p["sku"]}</span></a>'
            f'<div class="b"><h3><a href="{root}p/{p["sku"]}.html">{e(p["title"])}</a></h3>{en}'
            f'<div class="row"><div><div class="pr">{rm(p["price"])}</div><div class="pk">包装 {e(p["packing"])}</div></div>'
            f'<button type="button" class="add" data-add {btn_attrs(p, root)} aria-label="把 {e(p["title"])} 加入购物车">加入购物车</button></div></div></article>')

STORE_LD = {
    "@context": "https://schema.org", "@type": "Store", "@id": absu("") + "#store",
    "name": SHOP, "alternateName": ["Hunter BOOM JOHOR", "Hunter Boom Johor 新山烟花", "猎人烟花 新山"],
    "description": f"{TAG}。新山烟花批发零售：红炮礼炮、Pop Pop 沙炮、手持烟花、喷泉、盆花与大盆花，WhatsApp 下单。",
    "url": absu(""), "image": (SITE_ORIGIN + "/img/og.jpg") if SITE_ORIGIN else "/img/og.jpg",
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
SHELVES = [
    ("hot", "🔥", "最畅销", "热门口碑款，十个分类都有", "c/index.html", "浏览全部分类 ›",
     ["HB013", "HB040", "HB048", "HB071", "HB102", "HB123", "HB168", "HB181", "HB253", "HB011"]),
    ("must", "✨", "必玩推荐", "沙炮、趣味飞天、手持，好看又好玩", "c/fly.html", "看飞天趣味 ›",
     ["HB042", "HB066", "HB090", "HB086", "HB103", "HB112", "HB085", "HB118", "HB064", "HB046", "HB107", "HB068"]),
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
    icons = "".join(f'<a href="c/{c["id"]}.html"><span>{c["icon"]}</span>{e(c["name"])}</a>' for c in CATS)
    secs = []; idx = 0
    for sid, icon, title, lead, more_href, more_txt, skus in SHELVES:
        html, idx = cards_for(skus, root, idx)
        secs.append(
            f'<section class="sec shelf" id="{sid}" aria-labelledby="h-{sid}">'
            f'<h2 id="h-{sid}">{icon} {e(title)} <small>{e(lead)}</small>'
            f'<a class="more" href="{more_href}">{e(more_txt)}</a></h2>'
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
<section class="hero" aria-labelledby="h1">
<span class="tag">🐐 {CNY}</span>
<h1 id="h1"><em>新山烟花</em>批发零售 · Hunter BOOM JOHOR 总代理</h1>
<p>{TAG}。柔佛烟花、猎人烟花（Hunter Boom）羊年烟花一站购齐：红炮礼炮、沙炮、手持烟花、喷泉与盆花，依斯干达公主城出货，柔佛送货请 WhatsApp 询问。</p>
<div class="cd" id="cd" aria-live="polite"></div>
<div class="btns"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">{IC_WA.replace('<svg','<svg width="18" height="18"')} WhatsApp {PHONE_D}</a><a class="btn gd" href="#hot">看精选推荐</a></div>
</section>
<nav class="ic" aria-label="分类快捷入口">{icons}</nav>
<div class="info"><div><b>🏮 批发 · 零售</b>整箱批发与零售都可询价</div><div><b>🚚 柔佛送货</b>五福城、Sutera、公主城等，运费请询问</div><div><b>📲 WhatsApp 下单</b>选好产品一键发送订单</div></div>
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
    tiles = "".join(f'<a href="{c["id"]}.html" class="pc" style="padding:14px;text-align:center"><span style="font-size:34px">{c["icon"]}</span><h2 style="margin:6px 0 2px;font-size:16px;color:#8f0d13">{e(c["name"])}</h2><span class="pk">{len(BYCAT[c["id"]])} 款 · {rm(min(p["price"] for p in BYCAT[c["id"]]))} 起</span></a>' for c in CATS)
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

# ---------------- product pages ----------------
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
<p class="note">价目表价 · 包装 {e(p['packing'])}。最终价格、数量与送货请以 WhatsApp 确认为准。</p>
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
<section class="desc"><h2>产品说明</h2>
<p>{e(p['title'])}{('（' + e(p['name_en']) + '）') if p['name_en'] else ''}属于 Hunter BOOM JOHOR 总代理「{e(c['name'])}」系列，包装规格 {e(p['packing'])}，价目表价 {rm(p['price'])}。</p>
<p>新山、柔佛顾客可 WhatsApp <a href="{WA}" target="_blank" rel="noopener" style="color:#1fae55;font-weight:700">{PHONE_D}</a> 询问现货、批发数量与送货安排（依斯干达公主城、五福城、Sutera 等）。{img_src}。</p>
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
           ("有送货吗？", "柔佛地区可安排送货，如五福城、Sutera、依斯干达公主城一带；运费与时间请 WhatsApp 询问。"),
           ("价格是最终价格吗？", "网站价格依据最新价目表，包装栏位（PACKING）为原表规格；最终价格、数量与送货安排以店家 WhatsApp 回复为准。")]
    ld = [STORE_LD, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
          bc_ld([("首页", ""), ("关于我们", "about.html")])]
    body = f"""<body data-root="">
{topbar(root)}
<main class="wrap"><nav class="bc" aria-label="面包屑"><a href="index.html">首页</a> › <span>关于我们</span></nav>
<article class="txt"><h1>关于 Hunter BOOM JOHOR 总代理</h1>
<p><b>{TAG}</b></p>
<p>Hunter BOOM JOHOR 总代理位于柔佛新山依斯干达公主城（Iskandar Puteri），提供新山烟花、柔佛烟花批发与零售，产品包括红炮礼炮、Pop Pop 沙炮、手持烟花、喷泉喷花、飞天趣味、响声系列、盆花与大盆花等，迎接{CNY}。</p>
<h2>下单方式</h2><ol><li>浏览产品，点「加入购物车」，可调整数量。</li><li>打开购物车，点「发送订单到 WhatsApp」。</li><li>店家通过 WhatsApp 确认价格、数量、取货或送货安排。</li></ol>
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
    urls = [("", "1.0"), ("c/index.html", "0.6"), ("about.html", "0.5")] + [(f"c/{c['id']}.html", "0.8") for c in CATS] + [(f"p/{p['sku']}.html", "0.7") for p in P]
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

if __name__ == "__main__":
    home(); catpages(); products(); about(); n = meta_files()
    print(f"built {len(P)} products, {len(CATS)} categories, sitemap urls={n}, SITE_ORIGIN={SITE_ORIGIN or '(relative)'}")
