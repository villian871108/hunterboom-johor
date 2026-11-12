# Hunter BOOM JOHOR 总代理 — 静态网店

新山烟花批发零售店铺网站（Simplified Chinese, `lang="zh-Hans"`）。纯静态 HTML/CSS/JS，可上传到任何静态主机（Cloudflare Pages、Netlify、GitHub Pages、cPanel 等）。

> ⚠️ **域名尚未上线。** 目前没有任何正式域名。`https://hunterboomjohor.com` 只是示例占位，并未注册或启用。

## 目录
- `index.html` 首页（全部 260 款产品、分类、搜索）
- `c/*.html` 10 个分类页 + `c/index.html` 分类总览
- `p/HB001.html … p/HB260.html` 产品详情页
- `about.html` 关于我们 / 下单方式 / FAQ，`404.html`
- `css/style.css`、`js/cart.js`（购物车 + WhatsApp 下单，localStorage，无追踪）
- `img/p/` 产品图（webp，取自 Hunter Boom 年货目录 / TT Fireworks 目录页面裁切），`img/og-cny2027.jpg` 分享图（羊年三阳开泰海报横图）
- `data/products.json` 产品数据（来源：价目表 PDF）
- `sitemap.xml`、`robots.txt`、`site.webmanifest`
- `tools/build_site.py` 生成器（改价或改资料后重跑）

## 发布前必须做：设置域名
`SITE_ORIGIN` 只在 `tools/build_site.py` 一处设定（默认空 = 使用根相对网址 `/p/HB001.html`）。
有了正式域名后执行：

```bash
python3 tools/build_site.py --origin https://你的域名.com
```

这会把 canonical、og:url、og:image、JSON-LD、`sitemap.xml`（协议要求绝对网址）和 `robots.txt` 的 Sitemap 行全部改成绝对网址。然后把整个文件夹（`tools/` 可不上传）上传到主机根目录，并在 Google Search Console 提交 `sitemap.xml`。

## 修改产品 / 价格
编辑 `data/products.json`（`price` 为数字 RM，`packing` 为价目表包装规格），然后 `python3 tools/build_site.py`。

## 下单流程
购物车 → 「发送订单到 WhatsApp」→ 打开 `https://wa.me/60177891688?text=我要下单…`（每行：编号 名称 x数量，附参考合计）。

## 分析代码
未安装任何 analytics。如需要，在 `tools/build_site.py` 的 `<!-- Optional analytics -->` 注释处加入自己的代码再重建。

## 本地预览
```bash
python3 -m http.server 8765   # 然后打开 http://127.0.0.1:8765/
```


预览地址：https://villian871108.github.io/hunterboom-johor/
