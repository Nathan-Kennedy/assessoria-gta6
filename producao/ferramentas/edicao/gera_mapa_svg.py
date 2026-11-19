# Gera SVGs do sul da Flórida + Keys (Natural Earth, domínio público) para colar no EffectCraft como shape layers.
import json, math, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "mapa")
LON0, LON1, LAT0, LAT1 = -83.0, -79.6, 24.35, 27.3          # recorte
W, H = 1920, 1080
kx = math.cos(math.radians((LAT0 + LAT1) / 2))
sx = W / ((LON1 - LON0) * kx); sy = H / (LAT1 - LAT0); s = min(sx, sy) * 0.98
ox = (W - (LON1 - LON0) * kx * s) / 2; oy = (H - (LAT1 - LAT0) * s) / 2
def xy(lon, lat): return (ox + (lon - LON0) * kx * s, oy + (LAT1 - lat) * s)
def aneis(geom):
    t, c = geom["type"], geom["coordinates"]
    polys = [c] if t == "Polygon" else c if t == "MultiPolygon" else []
    for p in polys:
        for ring in p: yield ring
def dentro(ring):
    return any(LON0 - 0.5 <= x <= LON1 + 0.5 and LAT0 - 0.5 <= y <= LAT1 + 0.5 for x, y in ring)
paths = []
for f in ("ne_10m_land.geojson", "ne_10m_minor_islands.geojson"):
    for feat in json.load(open(os.path.join(D, f), encoding="utf-8"))["features"]:
        for ring in aneis(feat["geometry"]):
            if not dentro(ring): continue
            # recorta pontos muito fora pra não gerar paths gigantes
            pts = [xy(x, y) for x, y in ring if LON0 - 1 <= x <= LON1 + 1 and LAT0 - 1 <= y <= LAT1 + 1]
            if len(pts) < 3: continue
            paths.append("M" + " L".join("%.1f %.1f" % p for p in pts) + " Z")
def svg(body): return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>' % (W, H, W, H, body)
open(os.path.join(D, "terra.svg"), "w").write(svg('<path d="%s" fill="#2b0f45" stroke="#19e3d3" stroke-width="2.5"/>' % " ".join(paths)))
# Overseas Highway (aprox.): Florida City → Key Largo → Islamorada → Marathon → Seven Mile → Big Pine → Key West
rota = [(-80.48, 25.45), (-80.40, 25.20), (-80.44, 25.09), (-80.55, 24.98), (-80.63, 24.92), (-80.78, 24.84), (-80.93, 24.76),
        (-81.09, 24.71), (-81.17, 24.70), (-81.28, 24.655), (-81.36, 24.67), (-81.52, 24.63), (-81.66, 24.58), (-81.78, 24.555)]
open(os.path.join(D, "rota.svg"), "w").write(svg('<path d="M%s" fill="none" stroke="#ff3d8b" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>' % " L".join("%.1f %.1f" % xy(*p) for p in rota)))
seven = [(-81.165, 24.705), (-81.22, 24.68), (-81.285, 24.655)]
open(os.path.join(D, "seven.svg"), "w").write(svg('<path d="M%s" fill="none" stroke="#ff8a3d" stroke-width="10" stroke-linecap="round"/>' % " L".join("%.1f %.1f" % xy(*p) for p in seven)))
pins = {"MIAMI": (-80.19, 25.77), "KEY LARGO": (-80.44, 25.09), "MARATHON": (-81.09, 24.71), "KEY WEST": (-81.78, 24.555), "SEVEN MILE": (-81.22, 24.68)}
json.dump({k: xy(*v) for k, v in pins.items()} | {"_escala_px_por_grau_lat": s}, open(os.path.join(D, "pins.json"), "w"), indent=1)
print("paths", len(paths), "pins", {k: tuple(round(c) for c in xy(*v)) for k, v in pins.items()})
