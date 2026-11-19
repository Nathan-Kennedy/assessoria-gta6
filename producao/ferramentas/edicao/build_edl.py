# EDL do vídeo 03 ("A madrugada do GTA 6"): narração IA (narracao_ia/), plano de cenas (scripts/plano.json),
# motions Remotion (motion/out/*.mp4, tempos em motion/src/tempos.json), memes, cards, pins e legendas.
# Saídas: scripts/edl.json, scripts/tempos.json (mix) e motion/src/tempos.json atualizado com os beats reais.
import json, os, re, unicodedata
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = os.path.join(B, os.environ.get("NARR", "narracao_dp"))
FALAS = {f["n"]: f for f in json.load(open(os.path.join(N, "falas.json"), encoding="utf-8"))}
PAL = json.load(open(os.path.join(N, "palavras.json"), encoding="utf-8"))
PLANO = json.load(open(os.path.join(B, "scripts/plano.json"), encoding="utf-8"))
ITJ = json.load(open(os.path.join(B, "scripts/itens.json")))
IT = {k: v[0] for k, v in ITJ.items()}; ITD = {k: v[3] for k, v in ITJ.items()}
for _k in [k for k in ITJ if k.endswith("-v2")]: IT[_k[:-3]] = IT[_k]; ITD[_k[:-3]] = ITD[_k]   # motions refeitos (voz da Ana) têm prioridade
for _k in [k for k in ITJ if k.endswith("-v3")]: IT[_k[:-3]] = IT[_k]; ITD[_k[:-3]] = ITD[_k]   # despedida refeita (18/11)
proj = json.load(open(os.path.join(B, "edicao/video03_base.ecproj"), encoding="utf-8"))
DIM = {int(k): (v["kind"].get("width") or 1920, v["kind"].get("height") or 1080) for k, v in proj["items"].items() if v["kind"]["type"] in ("Footage", "Comp")}
ULT = max(FALAS); DUR = round(FALAS[ULT]["t1"] + 3.0, 2)
SRC = {"T1": 223, "T2": 224, "LA": 225, "EL": 12945, "PL": 12991}
COR = {"rosa": "#FF3D8B", "ciano": "#19E3D3", "laranja": "#FF8A3D", "verm": "#FF2D2D"}
MEMES = {"gato_julgando": 12966, "cachorro_huh": 12973, "doge_bonk": IT.get("doge_bonk"), "gato_vibing": IT.get("gato_vibing")}
MEME_PAUSA = {25: "gato_julgando", 47: "cachorro_huh", 58: "doge_bonk", 75: "gato_vibing"}

def norm(x):
    x = unicodedata.normalize("NFKD", x.lower()); x = "".join(c for c in x if not unicodedata.combining(c))
    x = re.sub(r"\b212\b", "duzentos e doze", x); x = re.sub(r"\b16\b", "dezesseis", x); x = re.sub(r"\b19\b", "dezenove", x)
    x = re.sub(r"\b18\b", "dezoito", x); x = re.sub(r"\b5\b", "cinco", x); x = re.sub(r"\b6\b", "seis", x)
    return re.sub(r"[^a-z0-9 ]", " ", x).split()
def acha(n, frase, fim=False):
    ws = [w for w in PAL if w["fala"] == n]; alvo = norm(frase); nw = [norm(w["w"]) for w in ws]
    flat = [(i, t) for i, l in enumerate(nw) for t in l]
    for j in range(len(flat) - len(alvo) + 1):
        if [t for _, t in flat[j:j + len(alvo)]] == alvo:
            return ws[flat[j + len(alvo) - 1][0]]["e"] if fim else ws[flat[j][0]]["s"]
    print("AVISO: nao achei %r na fala %d" % (frase, n)); return FALAS[n]["t0"] + 0.3
def slot(n):
    prox = [k for k in FALAS if k > n]
    return FALAS[n]["t0"], (FALAS[min(prox)]["t0"] if prox else DUR)
def cobre(it, folga=1.03):
    w, h = DIM[it]; return max(1920 / w, 1080 / h) * 100 * folga

clips = []
def add(fonte, src, t0, t1, util, meme=False):
    if t1 - t0 < 0.05: return
    it = MEMES[fonte] if meme else SRC[fonte]
    d = t1 - t0; st = 100
    if d > util + 0.05: st = min(180, round(100 * d / util))
    b = cobre(it); clips.append({"t0": round(t0, 3), "t1": round(t1, 3), "item": it, "src": round(src, 3), "stretch": st, "tipo": "footage",
                                 "escala": [round(b, 2), round(b * (1.06 if meme else 1.08), 2)], "frameblend": st != 100, "meme": meme})

# ---------- cenas por fala ----------
P = {int(k): v for k, v in PLANO["P"].items()}
inicio_bloco = sorted(FALAS[n]["t0"] for n in FALAS if n == min(FALAS) or FALAS[n]["bloco"] != FALAS[max(k for k in FALAS if k < n)]["bloco"])
for n in sorted(FALAS):
    a, b = slot(n)
    if n == min(FALAS): a = 0.0
    if n in MEME_PAUSA:
        b_fala = FALAS[n]["t1"]
        add(MEME_PAUSA[n], 0, b_fala, b, 4.0, meme=True); b = b_fala
    planos = P.get(n) or [["EL", 1545.5, 3.0]]          # falas de motion também ganham cena (fica por baixo / sobra fora do motion)
    tot = sum(p[2] for p in planos); t = a
    for k, (f, s, u) in enumerate(planos):
        e = b if k == len(planos) - 1 else t + (b - a) * u / tot
        add(f, s, t, e, u); t = e

# ---------- motions: relógio no início de cada bloco + conteúdo nas falas ----------
TJ = json.load(open(os.path.join(B, "motion/src/tempos.json"), encoding="utf-8")); TJd = {c["id"]: c for c in TJ}
REL = ["R00", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", "R13", "R14"]
blocos = sorted(set(FALAS[n]["bloco"] for n in FALAS))
MOT = []   # (t0, t1, id)
for i, bl in enumerate(blocos[:14]):
    n0 = min(n for n in FALAS if FALAS[n]["bloco"] == bl)
    t0 = 0.0 if i == 0 else FALAS[n0]["t0"] - 1.6
    MOT.append((t0, t0 + 2.6, REL[i]))
# conteúdo: id -> (fala inicial, fala final, {beat: (fala, frase)})
CONT = {
 "C01-fuso": (7, 8, {"nz": (7, "nova zelandia"), "br": (7, "brasil"), "horas": (7, "dezesseis horas")}),
 "C02-boato": (14, 15, {"insider": (14, "a data"), "boato": (14, "boato"), "nota": (15, "se sairem")}),
 "C03-checklist": (19, 24, {"espaco": (19, "duzentos e doze"), "atualizacao": (21, "atualizacao"), "regiao": (22, "regiao"), "cama": (24, "cama")}),
 "C04-reiniciar": (27, 29, {"botao": (27, "reiniciar"), "elevador": (28, "elevador"), "downloads": (29, "celular")}),
 "C05-cadeado": (32, 34, {"virada": (32, "meia noite"), "abre": (32, "cadeado abre"), "erro": (34, "erro"), "espera": (34, "cinco minutos")}),
 "C06-keys": (39, 40, {"keys": (39, "keys"), "jason": (39, "jason"), "lucia": (40, "lucia")}),
 "C07-loja": (54, 57, {"fundos": (54, "fundos"), "cameras": (54, "cameras"), "testemunha": (55, "alguem ve"), "ladra": (57, "outra ladra")}),
 "C08-estrelas": (60, 63, {"estrelas": (60, "perseguicao"), "seis": (60, "seis estrelas"), "area": (62, "area"), "tiro": (64, "atirar")}),
 "C09-caixa": (67, 69, {"preso": (68, "preso"), "bolso": (68, "bolso"), "caixa": (68, "caixa eletronico"), "banco": (69, "caixa")}),
 "C10-cama": (73, 74, {"cama": (73, "cama"), "dormir": (74, "dormir")}),
 "C11-mapa": (78, 79, {"afasta": (78, "escala"), "amanha": (79, "proxima")}),
 "C12-fecho": (83, 85, {"comenta": (83, "comenta"), "inscreve": (84, "inscreve"), "video": (85, "video de ontem")}),
 "C13-outro": (87, 87, {}),
}
CONT = {k: v for k, v in CONT.items() if v[0] in FALAS}
for cid, (na, nb, beats) in CONT.items():
    t0 = FALAS[na]["t0"]
    t1 = FALAS[nb]["t1"] + (0.35 if nb not in MEME_PAUSA else 0)
    t0 = max(t0, max([b for a, b, _ in MOT if a < t0 + 0.1] + [0]))   # não encavala com o relógio
    MOT.append((t0, t1, cid))
    c = TJd[cid]; c["dur"] = round(t1 - t0 + 0.04, 3)
    for k, (n, fr) in beats.items(): c["props"][k] = round(max(0.05, acha(n, fr) - t0), 3)
    if cid == "C13-outro":
        segs = json.load(open(os.path.join(B, "outro/outro.json"), encoding="utf-8"))
        c["props"]["segs"] = [dict(g, t0=round(g["t0"] + FALAS[87]["t0"] - t0, 3), t1=round(g["t1"] + FALAS[87]["t0"] - t0, 3)) for g in segs]
        c["props"]["sininho"] = next(g["t0"] for g in c["props"]["segs"] if "sininho" in g["texto"])
        c["props"]["liveEm"] = next(g["t0"] for g in c["props"]["segs"] if "gameplay" in g["texto"])
        c["dur"] = round(DUR - t0, 3); t1 = DUR; MOT[-1] = (t0, t1, cid)
for t0, t1, cid in MOT:
    if cid.startswith("R"): TJd[cid]["dur"] = round(t1 - t0 + 0.04, 3)
json.dump(TJ, open(os.path.join(B, "motion/src/tempos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for a, b, k in MOT:
    novo = []
    for c in clips:
        if c["t1"] <= a + 1e-3 or c["t0"] >= b - 1e-3: novo.append(c); continue
        if c["t0"] < a - 0.05: x = dict(c); x["t1"] = round(a, 3); novo.append(x)
        if c["t1"] > b + 0.05:
            x = dict(c); adv = b - c["t0"]; x["t0"] = round(b, 3)
            x["src"] = round(c["src"] + adv * 100 / c["stretch"], 3); novo.append(x)
    if k in IT:
        st = max(100, round(100 * (b - a) / ITD[k], 3)) if ITD.get(k) else 100
        novo.append({"t0": round(a, 3), "t1": round(b, 3), "item": IT[k], "src": 0, "stretch": st, "tipo": "footage", "escala": [100, 100], "frameblend": False, "motion": True})
    clips = sorted(novo, key=lambda c: c["t0"])
dentro = lambda t: any(a - 0.05 <= t < b - 0.05 for a, b, _ in MOT)

# ---------- cards e pins ----------
cards = []
for txt, n, fr, d, cor, tam in PLANO["CARDS"]:
    if n not in FALAS: continue
    t0 = acha(n, fr)
    if dentro(t0) or dentro(t0 + d - 0.2): continue
    cards.append({"t0": round(t0, 3), "t1": round(min(t0 + d, DUR), 3), "texto": txt, "cor": COR[cor], "tamanho": tam, "y": 1000 if tam < 150 else 540})
pins = []
for txt, n, fr, d, cor in PLANO["PINS"]:
    if n not in FALAS: continue
    t0 = acha(n, fr)
    if dentro(t0) or dentro(t0 + d - 0.5): continue
    pins.append({"t0": round(t0, 3), "t1": round(t0 + d, 3), "texto": txt, "cor": COR[cor]})

# ---------- legendas ----------
SEM = sorted([(c["t0"], c["t1"]) for c in clips if c.get("meme") or c.get("motion")])
ws = [dict(w) for w in PAL]
FIX = [(r"\bGTA VI\b", "GTA 6"), (r"\bGTA V\b", "GTA 5"), (r"\bLe[oô]nida\b", "Leonida"), (r"\bNate the Hate\b", "NateTheHate"), (r"\bNathan Hate\b", "NateTheHate"),
       (r"\bDolby Jones\b", "Davy Jones"), (r"\bDave Jones\b", "Davy Jones"),(r"\bNelvo\b", "Nelson"), (r"^[Ss]ilêncio a\b", "Silencia"), (r"\bvai riscar\b", "vai arriscar"),
       (r"\bseu louco\b", "ce loko"), (r"\bcita doido\b", "ce tá doido"), (r"\bcê louco\b", "ce loko"), (r"\b212GB\b", "212 GB")]
grupos, g = [], []
for i, w in enumerate(ws):
    g.append(w); prox = ws[i + 1] if i + 1 < len(ws) else None
    txt = " ".join(x["w"] for x in g)
    if prox is None or prox["fala"] != w["fala"] or prox["s"] - w["e"] > 0.3 or re.search(r"[.,!?:]$", w["w"]) or len(g) >= 4 or len(txt) >= 16:
        grupos.append(g); g = []
legendas = []
for k, g in enumerate(grupos):
    t0 = g[0]["s"]; t1 = g[-1]["e"] + 0.12
    if k + 1 < len(grupos): t1 = min(max(t1, min(grupos[k + 1][0]["s"], t0 + 0.6)), grupos[k + 1][0]["s"])
    if dentro(t0 + 0.1) or any(a <= t0 + 0.1 < b for a, b in SEM): continue
    if any(c["t0"] - 0.05 <= t0 < c["t1"] or t0 < c["t0"] < t1 - 0.1 for c in cards): continue
    texto = " ".join(x["w"] for x in g)
    for a, b in FIX: texto = re.sub(a, b, texto)
    legendas.append({"t0": round(t0, 3), "t1": round(t1, 3), "texto": texto.rstrip(",.").upper(), "y": 905})

whips = sorted(round(a - 0.1, 3) for a, b, k in MOT if k.startswith("R") and a > 0.5)
flashes = []
edl = {"comp": {"name": "VIDEO03", "duration": DUR}, "clips": clips, "legendas": legendas, "cards": cards, "pins": pins,
       "whips": whips, "flashes": flashes, "misterio": [[FALAS[5]["t0"], FALAS[5]["t1"]], [FALAS[67]["t0"], FALAS[67]["t1"]]]}
json.dump(edl, open(os.path.join(B, "scripts/edl.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tempos = {"dur": DUR, "falas": {n: [f["t0"], f["t1"]] for n, f in FALAS.items()}, "blocos": inicio_bloco[1:],
          "memes": {str(n): [FALAS[n]["t1"], slot(n)[1]] for n in MEME_PAUSA}, "cards": [[c["t0"], c["tamanho"]] for c in cards],
          "whips": whips, "flashes": flashes, "relogios": [a for a, b, k in MOT if k.startswith("R")]}
json.dump(tempos, open(os.path.join(B, "scripts/tempos.json"), "w", encoding="utf-8"), indent=1)
cs = sorted(clips, key=lambda c: c["t0"]); prob = [(x["t1"], y["t0"]) for x, y in zip(cs, cs[1:]) if abs(x["t1"] - y["t0"]) > 0.02]
if cs[0]["t0"] > 0.01 or abs(cs[-1]["t1"] - DUR) > 0.02: prob.append(("borda", cs[0]["t0"], cs[-1]["t1"]))
print("dur %.2f | %d clipes (%d motions) | %d legendas | %d cards | %d pins | problemas: %s" % (DUR, len(clips), len(MOT), len(legendas), len(cards), len(pins), prob or "nenhum"))
