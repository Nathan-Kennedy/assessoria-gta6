# Lista os arquivos que uma comp precisa para renderizar (itens referenciados, recursivo) -> notebook/MANIFESTO_<comp>.txt
import json, sys, os
proj, comp_nome = sys.argv[1], sys.argv[2]
p = json.load(open(proj, encoding="utf-8")); it = p["items"]
def nodes(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from nodes(v)
    elif isinstance(o, list):
        for v in o: yield from nodes(v)
comp = next(v for v in it.values() if v.get("name") == comp_nome)
vistos, fila, arqs = set(), [comp], set()
while fila:
    c = fila.pop()
    for n in nodes(c["kind"].get("layers", [])):
        src = n.get("source")
        if isinstance(src, dict) and "item" in src and src["item"] not in vistos:
            vistos.add(src["item"]); x = it[str(src["item"])]
            if x["kind"]["type"] == "Comp": fila.append(x)
            else:
                path = x["kind"].get("path")
                if path: arqs.add(path)
tot = sum(os.path.getsize(a) for a in arqs if os.path.exists(a))
falta = [a for a in arqs if not os.path.exists(a)]
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notebook", "MANIFESTO_%s.txt" % comp_nome)
open(out, "w", encoding="utf-8").write("\n".join(sorted(arqs)) + "\n")
print(comp_nome, len(arqs), "arquivos, %.2f GB" % (tot / 1e9), "faltando:", falta)
