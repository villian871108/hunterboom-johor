#!/usr/bin/env python3
"""把网站订单归档成出货单（每个单号一个文件），存到私人文件夹（默认 /workspace/hunterboom-orders/）。

订单含顾客姓名、电话、地址 → 只存在 box 的私人文件夹，绝对不要放进公开的 GitHub repo。

输入（任选一种）：
  python3 tools/file_order.py order.json              # 购物车订单记录 / 统计接口订单 JSON（单个或数组）
  python3 tools/file_order.py --text wa.txt           # 顾客发到客服 WhatsApp 的订单文字（以「单号：」开头）
  python3 tools/file_order.py --sheet-csv orders.csv  # Google 表格 orders 分页导出的 CSV（有 order_no 栏的行）
  … - 表示从 stdin 读。  --dir DIR 改归档文件夹；--force 覆盖已存在且内容不同的单。

输出：DIR/YYYY-MM/HBJ-YYYYMMDD-XXXX.md（出货单）+ 同名 .json；DIR/index.csv 追加一行索引。
"""
import argparse, csv, io, json, os, re, sys
from decimal import Decimal, ROUND_HALF_UP

DEFAULT_DIR = "/workspace/hunterboom-orders"
POSTAGE_POST = Decimal("15.00")   # 西马邮费一律 RM15（任买）
DLV = {"pickup": "自取（Sutera Mall）", "lalamove": "Lalamove（联系客服安排）", "post": "邮寄"}
DLV_BY_LABEL = {v: k for k, v in DLV.items()}
MODES = {"l": ("散装", "件"), "b": ("整盒", "盒"), "s": ("", "件")}
SHIP_F = [("name", "收件人姓名"), ("phone", "电话"), ("addr", "地址"), ("pc", "邮区编号"), ("city", "城市"), ("state", "州属")]
NO_RE = re.compile(r"^HBJ-\d{8}-[0-9A-Z]{4}$")

def D(x): return Decimal(str(x if x not in (None, "") else 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
def rm(x): return "RM{:,.2f}".format(D(x))

def norm_item(x):
    m = x.get("m") or ""
    n = str(x.get("n", ""))
    # stats payload writes the unit into the name: 8尺红炮（散装）
    mm = re.search(r"（(散装|整盒)）$", n)
    if mm:
        n = n[:mm.start()]
        m = m or ("l" if mm.group(1) == "散装" else "b")
    if m not in MODES:
        t = x.get("t") or ""
        m = "l" if t == "散装" else "b" if t == "整盒" else "s"
    q = int(x.get("q") or 1); p = D(x.get("p"))
    return {"c": str(x.get("c", "")), "n": n, "m": m, "t": MODES[m][0], "u": MODES[m][1], "q": q, "p": float(p), "line": float(D(p * q))}

def norm(o):
    no = str(o.get("order_no", "")).strip().upper()
    if not NO_RE.match(no):
        raise ValueError(f"没有有效单号 order_no：{no!r}")
    items = [norm_item(x) for x in (o.get("items") or [])]
    if not items: raise ValueError(f"{no}：订单没有产品")
    dv = o.get("delivery") or DLV_BY_LABEL.get(o.get("delivery_label", ""), "")
    ship = o.get("ship") if dv == "post" else None
    sub = D(sum(Decimal(str(x["line"])) for x in items))
    post = POSTAGE_POST if dv == "post" else Decimal("0.00")
    t = str(o.get("time") or o.get("ts") or "")
    t = t.replace("T", " ").replace("+08:00", "")[:19]
    if not t: t = f"{no[4:8]}-{no[8:10]}-{no[10:12]}（具体时间未记录）"
    return {"order_no": no, "time": t, "tz": "Asia/Kuala_Lumpur (UTC+8)", "delivery": dv, "delivery_label": DLV.get(dv, "未记录"),
            "ship": ({k: str((ship or {}).get(k, "")) for k, _ in SHIP_F} if dv == "post" else None),
            "items": items, "subtotal": float(sub), "postage": float(post), "total": float(sub + post),
            "status": o.get("status", ""), "source": o.get("_source", "")}

def parse_text(s):
    lines = [l.strip() for l in s.replace("\r", "").split("\n")]
    o = {"items": [], "_source": "whatsapp"}
    item_re = re.compile(r"^(HB\d{3,})\s+(.+?)(?:\s+(散装|整盒))?\s+x(\d+)（RM([\d,]+\.\d{2})/(件|盒)，小计 RM([\d,]+\.\d{2})）$")
    ship, in_ship = {}, False
    labels = {v: k for k, v in SHIP_F}
    for l in lines:
        if l.startswith("单号："): o["order_no"] = l[3:].strip()
        elif l.startswith("我要下单（"): o["time"] = l[len("我要下单（"):].split("，")[0]
        elif l.startswith("取货方式："): o["delivery_label"] = l[5:].strip()
        elif l.startswith("邮寄资料"): in_ship = True
        elif in_ship and "：" in l and l.split("：", 1)[0] in labels:
            k, v = l.split("：", 1); ship[labels[k]] = v.strip()
        else:
            m = item_re.match(l)
            if m:
                c, n, t, q, p, u, _ = m.groups()
                mode = "l" if t == "散装" else "b" if t == "整盒" else "s"
                o["items"].append({"c": c, "n": n, "m": mode, "q": int(q), "p": p.replace(",", "")})
    if ship: o["ship"] = ship
    return [o]

def parse_csv(s):
    out = []
    for r in csv.DictReader(io.StringIO(s)):
        if not r.get("order_no"): continue
        out.append({"order_no": r["order_no"], "time": r.get("timestamp") or (r.get("date", "") + " " + r.get("time", "")),
                    "delivery": r.get("delivery", ""), "ship": json.loads(r["ship_json"]) if r.get("ship_json") else None,
                    "items": json.loads(r.get("items_json") or "[]"), "status": r.get("status", ""), "_source": "sheet"})
    return out

def render_md(o):
    L = [f"# 出货单 {o['order_no']}", "", f"- 单号：**{o['order_no']}**", f"- 下单时间：{o['time']}（马来西亚时间 UTC+8）",
         f"- 取货方式：**{o['delivery_label']}**"]
    if o["delivery"] == "lalamove": L.append("- 备注：新山区 Lalamove 运费自付，客服联系安排")
    if o["delivery"] == "pickup": L.append("- 备注：自取 Sutera Mall，客服约时间")
    if o["status"]: L.append(f"- 统计页状态：{o['status']}")
    if o["ship"]:
        L += ["", "## 邮寄资料", ""] + [f"- {lab}：{o['ship'].get(k, '')}" for k, lab in SHIP_F]
    L += ["", "## 产品", "", "| 编号 | 名称 | 散装/整盒 | 数量 | 单价（参考） | 小计 |", "|---|---|---|---:|---:|---:|"]
    for x in o["items"]:
        L.append(f"| {x['c']} | {x['n']} | {x['t'] or '单件'} | {x['q']} {x['u']} | {rm(x['p'])}/{x['u']} | {rm(x['line'])} |")
    L += ["", f"- 商品小计：{rm(o['subtotal'])}"]
    if o["delivery"] == "post": L.append(f"- 邮费（西马邮寄，任买）：{rm(o['postage'])}")
    L += [f"- **合计：{rm(o['total'])}**" + ("（不含 Lalamove 运费）" if o["delivery"] == "lalamove" else ""), "",
          "> 价格为网站参考价，以店家确认为准。", ""]
    return "\n".join(L)

def file_one(o, d, force=False):
    o = norm(o)
    sub = os.path.join(d, o["order_no"][4:8] + "-" + o["order_no"][8:10])
    os.makedirs(sub, exist_ok=True)
    md_p = os.path.join(sub, o["order_no"] + ".md"); js_p = md_p[:-3] + ".json"
    body = render_md(o); js = json.dumps(o, ensure_ascii=False, indent=1) + "\n"
    if os.path.exists(md_p):
        if open(md_p, encoding="utf-8").read() == body: return md_p, "unchanged"
        if not force: return md_p, "exists (different content; use --force)"
    open(md_p, "w", encoding="utf-8").write(body); open(js_p, "w", encoding="utf-8").write(js)
    os.chmod(md_p, 0o600); os.chmod(js_p, 0o600)
    idx = os.path.join(d, "index.csv"); new = not os.path.exists(idx)
    with open(idx, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["order_no", "time", "delivery", "recipient", "subtotal", "postage", "total", "file"])
        w.writerow([o["order_no"], o["time"], o["delivery_label"], (o["ship"] or {}).get("name", ""), o["subtotal"], o["postage"], o["total"], os.path.relpath(md_p, d)])
    return md_p, "filed"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?", default="-"); ap.add_argument("--text", action="store_true"); ap.add_argument("--sheet-csv", action="store_true")
    ap.add_argument("--dir", default=DEFAULT_DIR); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    s = sys.stdin.read() if a.src == "-" else open(a.src, encoding="utf-8").read()
    if a.text: orders = parse_text(s)
    elif a.sheet_csv: orders = parse_csv(s)
    else:
        j = json.loads(s); j = j.get("orders", j) if isinstance(j, dict) and "orders" in j else j
        orders = j if isinstance(j, list) else [j]
        orders = [x.get("extra", x) if isinstance(x, dict) and "extra" in x else x for x in orders]
    os.makedirs(a.dir, exist_ok=True); os.chmod(a.dir, 0o700)
    rc = 0
    for o in orders:
        try:
            p, st = file_one(o, a.dir, a.force); print(f"{st}: {p}")
        except Exception as ex:
            rc = 1; print(f"skip: {ex}", file=sys.stderr)
    sys.exit(rc)

if __name__ == "__main__":
    main()
