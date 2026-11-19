# Confere se cada clipe de fundo cobre o quadro 1920x1080 inteiro (início e fim do zoom)
import json, re, sys
p = json.load(open(sys.argv[1], encoding="utf-8")); edl = json.load(open(sys.argv[2], encoding="utf-8"))
comp = p["items"][str(p["activeComp"])]; TK = 254016000000
centro = {(round(c["t0"], 2), c["item"]) for c in edl["clips"] if c.get("centro")}
def tr(l, m): return next(c for c in next(n for n in l["props"]["children"] if n["match"] == "transform")["children"] if c["match"] == m)
ruins, n = [], 0
for l in comp["kind"]["layers"]:
    if not re.fullmatch(r"C\d{3}", l["name"]): continue
    n += 1; it = p["items"][str(l["source"]["item"])]; w = it["kind"].get("width") or 1920; h = it["kind"].get("height") or 1080
    ax, ay = tr(l, "anchor")["value"]["v"][:2]; px, py = tr(l, "position")["value"]["v"][:2]
    sc = tr(l, "scale"); e = sc.get("expr")
    vals = [float(x) for x in re.findall(r"linear\(time,inPoint,outPoint,([\d.]+),([\d.]+)\)", e["text"])[0]] if e else [sc["value"]["v"][0]]
    t0 = l["in_point"] / TK
    if (round(t0, 2), it["id"]) in centro: continue
    for s in vals:
        k = s / 100; x0, y0 = px - ax * k, py - ay * k; x1, y1 = x0 + w * k, y0 + h * k
        if x0 > 0.5 or y0 > 0.5 or x1 < 1919.5 or y1 < 1079.5:
            ruins.append((l["name"], round(t0, 2), it["name"], s, [round(x0), round(y0), round(x1), round(y1)])); break
print("clipes conferidos:", n, "| fora do quadro:", len(ruins))
for r in ruins: print(r)
