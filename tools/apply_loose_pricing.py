#!/usr/bin/env python3
"""把盒装打散：给 data/products.json 每款产品加上散装/整盒价格字段（可重复运行，结果不变）。

规则（店家 2026-11-13）：散装卖价 = (价目表箱价 ÷ 一盒件数) × 1.40，Decimal ROUND_HALF_UP 到 2 位小数。
- PACKING 为 N/1：piece_qty = N。
    N > 1 → sale_mode "dual"：散装按件卖（loose_price），也可按原价目表箱价买整盒（carton_price）。
    N = 1 → sale_mode "single"：本身就是单件，只卖 loose_price（= 箱价 × 1.40），不另设整盒。
- 其他 PACKING（12/50/35、30/12、72/6、1/2 …）：件数不明，不推算。sale_mode "carton"，
  只按原价目表箱价卖整盒，loose_qty_pending = true（散装件数待确认），piece_qty / loose_price 为 null。
原价目表箱价保留在 carton_price（以及原来的 price 字段，不改动）。
"""
import json, os, re
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(ROOT, "data", "products.json")
MARKUP = Decimal("1.40")
NOTE = ("价目表价为整盒（箱）价。散装卖价 = 价目表箱价 ÷ 一盒件数 × 1.40（四舍五入到 RM0.01）；"
        "整盒按价目表箱价。包装为 N/1 的产品可买散装或整盒（1/1 为单件，只卖散装卖价）；"
        "其他包装规格的散装件数待确认，暂时只卖整盒。实际价格与数量以 WhatsApp 店家确认为准。")

def loose(carton, n):
    return float((Decimal(str(carton)) / Decimal(n) * MARKUP).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def apply(p):
    carton = p.get("carton_price", p["price"])
    p["carton_price"] = carton
    m = re.fullmatch(r"(\d+)/1", p["packing"].strip())
    if m and int(m.group(1)) > 0:
        n = int(m.group(1))
        p["piece_qty"] = n
        p["loose_price"] = loose(carton, n)
        p["loose_qty_pending"] = False
        p["sale_mode"] = "single" if n == 1 else "dual"
    else:
        p["piece_qty"] = None
        p["loose_price"] = None
        p["loose_qty_pending"] = True   # 散装件数待确认
        p["sale_mode"] = "carton"
    return p

if __name__ == "__main__":
    d = json.load(open(FP, encoding="utf-8"))
    for p in d["products"]:
        apply(p)
    d["price_note"] = NOTE
    d["pricing_rule"] = {"loose_markup": 1.40, "rounding": "ROUND_HALF_UP 0.01",
                         "formula": "loose_price = carton_price / piece_qty * 1.40", "set": "2026-11-13"}
    json.dump(d, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(p["sale_mode"] for p in d["products"]))
