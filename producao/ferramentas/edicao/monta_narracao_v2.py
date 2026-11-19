# Montagem v2 da narração do usuário (14/11/2026).
# Diferenças da v1 (monta_narracao_usuario.py):
#  - cortes pelos tempos do ALINHAMENTO FORÇADO (MMS_FA, *_alinhado.json), não do whisper: não corta palavra no meio
#    nem deixa pedaço da palavra anterior no começo do trecho;
#  - tira as tentativas repetidas ("esse pântano dourado" 3x, "Miami se apresenta como capital" 2x, "prédio de luxo" 2x);
#  - "6 dias" vira "5 dias" já aqui, com o "cinco" clonado na duração natural (ou com a regravação do usuário, se existir);
#  - PAUSAS (beats) depois das falas que levam meme, pro meme tocar sozinho e não em cima da fala;
#  - silêncios longos encurtados só ENTRE palavras (alinhadas), nunca dentro de uma palavra.
# Saídas: narracao/usuario/NARRACAO_V2.wav, narracao/usuario/v2_palavras.json (tempos de saída de cada palavra),
#         narracao/usuario/v2_beats.json (início/fim de cada pausa de meme)
import json, os, re, unicodedata, numpy as np, soundfile as sf, librosa
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = B + "/narracao/usuario/"; SR = 48000
SP = D   # r2_al.json / p4_al.json: alinhamento com o texto real nas tentativas repetidas

EDL = [
 # [01] GANCHO
 (4,1.10,7.74),
 "INICIO_DIAS",   # "Na vida real. Os letreiros ... Faltando só 5 dias ... nem é isso"
 (4,25.56,35.64),('RAW',2,17.15,23.85),(4,76.58,82.42),(4,84.76,105.12),(4,111.48,116.94),"BLOCO",
 # [02] POR QUE A FLÓRIDA
 (4,141.64,165.62),(4,169.52,183.62),(4,195.36,200.10),('RAW',4,201.0,209.95),('RAW',4,218.95,220.95),('RAW',4,224.4,228.05),('RAW',4,229.75,231.95),"BLOCO",
 # [03] VICE CITY
 (4,240.72,266.72),(4,268.08,286.52),(4,297.96,301.44),(4,307.18,313.90),(4,319.06,328.44),(4,335.12,340.84),
 (2,28.14,32.40),(4,363.80,369.98),(4,376.00,380.74),(4,388.74,394.28),("CLONE","southbeach"),(4,414.62,422.04),
 ('RAW',4,421.89,430.40),('RAW',4,434.50,441.84),
 (5,1.46,16.78),(5,20.30,25.38),(5,27.74,33.16),(5,46.30,55.76),(5,59.62,95.78),(5,107.42,125.10),(6,0.0,6.62),
 (7,2.50,20.90),(7,30.00,33.10),(7,61.62,69.22),"BLOCO",
 # [04] KEYS
 (8,0.0,2.84),(8,11.98,12.92),(8,17.28,23.12),('RAW',2,231.45,234.9),(8,25.64,45.54),(8,68.28,83.00),(8,94.40,100.86),(8,131.32,136.14),(8,140.28,143.32),(2,111.66,117.28),
 (8,159.70,180.14),(8,181.26,192.90),('RAW',8,200.45,211.3),(2,47.94,55.90),(8,225.30,230.30),(8,240.46,242.70),(8,253.18,265.48),(8,271.60,282.70),('RAWB',8,285.93,292.60),
 (8,296.80,298.44),"BLOCO",
 # [05] GRASSRIVERS
 (8,302.76,309.82),(8,337.48,347.3),(8,364.44,365.98),(2,126.20,129.10),(8,370.82,372.86),(8,382.12,385.40),('RAWX',2,135.15,135.9),('RAWB',8,386.0,388.3),(8,397.90,408.66),(8,409.94,414.72),
 (8,429.46,445.74),(2,172.14,176.22),(2,194.14,198.94),(8,467.82,475.00),(8,479.30,483.52),"BLOCO",
 # [06] AMBROSIA
 (8,484.86,494.90),('RAW',8,499.5,501.55),('RAW',8,507.25,513.35),('RAWA',8,519.95,521.36),('RAWX',2,155.45,156.1),('RAWX',8,521.96,525.95),(8,536.74,543.50),(8,550.54,568.38),(8,570.92,601.66),"BLOCO",
 # [07] PORT GELLHORN
 (8,607.34,609.48),(2,68.54,79.24),(8,631.08,647.04),(8,652.34,660.10),"BLOCO",
 # [08] MOUNT KALAGA
 (8,664.22,680.90),(8,687.40,691.52),(8,693.60,694.88),(8,698.18,703.70),(8,712.94,718.82),(8,737.40,767.66),"BLOCO",
 # [09] FECHAMENTO
 (8,774.00,780.60),(8,795.92,805.24),('RAWX',8,809.3,810.74),('RAWX',2,135.15,135.9),('RAWB',8,812.1,815.6),(8,842.14,852.94),(8,853.64,858.50),(8,859.92,867.14),
 "FIM_DIAS",      # "E faltando só 5 dias, a gente tá muito perto ..."
 (8,873.12,877.02),(8,880.84,886.42),(8,896.10,900.18),(8,910.04,926.40),(8,939.04,942.54),(9,7.42,11.62),(9,23.60,26.46)]

# "6 dias" -> "5 dias". Se o usuário regravar, basta salvar em narracao/usuario/regravar/inicio_dias.wav / fim_dias.wav
# (a frase inteira, ex.: "Faltando só 5 dias pro lançamento") e o trecho correspondente é trocado pela gravação nova.
DIAS = {"INICIO_DIAS": [('RAWA',4,9.19,16.55), ('WAV',"cinco/cinco_a.wav","5"), ('RAWB',4,16.97,25.85)],
        "FIM_DIAS":    [('RAWA',8,867.90,868.81), ('WAV',"cinco/cinco_b.wav","5"), ('RAWB',8,869.38,873.12)]}
# regravação do usuário (15/11): a frase INTEIRA vem da gravação nova, sem emenda com a gravação antiga
#  inicio_dias: "Faltando só 4 dias pro lançamento." (o resto continua da gravação original)
#  fim_dias:    "E faltando só 4 dias, a gente tá muito perto de explorar tudo isso de verdade."
REGRAV = {"INICIO_DIAS": ('RAW',4,9.19,15.98, 'regravar/inicio_dias', ('RAW',4,17.64,25.85)),   # regravou só "Faltando só 4 dias pro lançamento"
          "FIM_DIAS": (None, None, None, None, 'regravar/fim_dias', None)}
def acha_regrav(base):
    for ext in (".wav", ".m4a", ".mp3", ".ogg", ".flac"):
        if os.path.exists(D + base + ext):
            if ext != ".wav":
                import subprocess; subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", D + base + ext, "-ac", "1", "-ar", str(SR), D + base + "_conv.wav"], check=True)
                return D + base + "_conv.wav"
            return D + base + ext
    return None

# pausas pros memes: (frase que termina antes da pausa, segundos de pausa, nome)
BEATS = [("a gente percebeu", 0.9, "vine_percebeu"), ("coragem de inventar", 1.2, "rapaz"), ("muito louco", 1.25, "ele_gosta"),
         ("paia ne", 3.6, "paia"), ("em 2 minutos", 1.0, "dirijo"), ("isso e surreal", 1.25, "jesus"), ("meu dinheiro logo", 1.6, "dinheiro"),
         ("cacar cobra", 0.8, "ibama"), ("boa sorte amigo", 2.4, "coffin"), ("clt raiz", 1.5, "irra"), ("105 velho", 1.0, "vine_105")]

def norm(x):
    x = unicodedata.normalize("NFD", x.lower()); x = "".join(c for c in x if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", "", x).strip()

aud, wsp, rms = {}, {}, {}
HOP = 0.01
for i in (2, 4, 5, 6, 7, 8, 9):
    nm = "regrav_2" if i == 2 else "parte_%d" % i
    y, _ = librosa.load(D + nm + "_48k.wav", sr=SR, mono=True); aud[i] = y.astype(np.float32)
    wsp[i] = [w for s in json.load(open(D + nm + ".json", encoding="utf-8")) for w in s["words"]]
    al = [w for s in json.load(open(D + nm + "_alinhado.json", encoding="utf-8")) for w in s["words"]]
    for w, x in zip(wsp[i], al):   # tempo alinhado quando concorda com o whisper (senão o alinhador se perdeu)
        w["as"] = x["s"] if abs(x["s"] - w["s"]) < 0.6 else w["s"]
        w["ae"] = x["e"] if abs(x["e"] - w["e"]) < 0.6 and x["e"] > w["as"] else w["e"]
    h = int(HOP * SR); n = len(y) // h
    e = 20 * np.log10(np.sqrt((y[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    rms[i] = e
# textos das tentativas repetidas (o whisper do take "juntou" as repetições)
EXTRA = {}
for f, arq in ((2, "r2_al.json"), (4, "p4_al.json")):
    EXTRA[f] = [w for s in json.load(open(os.path.join(SP, arq), encoding="utf-8")) for w in s["words"]]

def quieto(f):
    e = rms[f]; return e < np.percentile(e, 95) - 32

def corte_ini(f, t, janela=(0.8, 0.25)):
    """ponto de corte num silêncio de verdade (>= 70 ms) logo antes de t; senão t-0.15"""
    q = quieto(f); a, b = int((t - janela[0]) / HOP), int((t + janela[1]) / HOP)
    melhor = None
    k = max(1, a)
    while k < min(b, len(q)):
        if q[k]:
            m = k
            while m < len(q) and q[m]: m += 1
            if m - k >= 7:
                fim = m * HOP   # fim do silêncio = começo da voz
                if melhor is None or abs(fim - t) < abs(melhor - t): melhor = fim
            k = m
        else: k += 1
    return max(0.0, (melhor - 0.07) if melhor is not None else t - 0.15)

def corte_fim(f, t, janela=(0.15, 0.8), teto=1e9):
    """primeiro silêncio de verdade (>= 70 ms) depois de t; corta 0.12 s dentro dele (deixa o fim da palavra soar)"""
    q = quieto(f); a, b = int((t - janela[0]) / HOP), int((t + janela[1]) / HOP)
    k = max(0, a)
    while k < min(b, len(q)):
        if q[k]:
            m = k
            while m < len(q) and q[m]: m += 1
            if m - k >= 7: return min(teto, k * HOP + min(0.12, (m - k) * HOP / 2))
            k = m
        else: k += 1
    return min(teto, t + 0.25)

def encurta(f, a, b):
    """encurta silêncios reais > 0.5 s dentro do trecho (deixa 0.2 s + 0.15 s); devolve áudio e mapa de tempo"""
    q = quieto(f); i0, i1 = int(a / HOP), int(b / HOP); cortes = []
    k = i0
    while k < i1:
        if q[k]:
            m = k
            while m < i1 and q[m]: m += 1
            if (m - k) * HOP > 0.5 and k > i0 and m < i1: cortes.append((k * HOP + 0.2 - a, m * HOP - 0.15 - a))
            k = m
        else: k += 1
    seg = aud[f][int(a * SR):int(b * SR)].copy()
    if not cortes: return seg, lambda t: t
    keep, x = [], 0.0
    for c0, c1 in cortes: keep.append(seg[int(x * SR):int(c0 * SR)]); x = c1
    keep.append(seg[int(x * SR):])
    def mapa(t):
        d = 0.0
        for c0, c1 in cortes:
            if t >= c1: d += c1 - c0
            elif t > c0: return c0 - d
        return t - d
    return np.concatenate(keep), mapa

def palavras_em(f, a, b):
    base = wsp[f]
    if f in EXTRA:
        ex = EXTRA[f]; lo, hi = ex[0]["s"] - 0.3, ex[-1]["e"] + 0.3
        base = sorted([w for w in base if not lo <= w["s"] <= hi] + ex, key=lambda w: w["s"])
    res = []
    for w in base:
        if not norm(w["w"]): continue
        s_, e_ = w.get("as", w["s"]), w.get("ae", w["e"])
        if a - 0.05 <= (s_ + e_) / 2 <= b + 0.05: res.append(dict(w, s=s_, e=e_))
    return res

z = lambda s: np.zeros(int(s * SR), np.float32)
out, palavras, t, log = [], [], 0.0, []
def emite(f, a, b, gap=0.18, fade=True, encurtar=True):
    global t
    ws = palavras_em(f, a, b)
    if encurtar: seg, mapa = encurta(f, a, b)
    else: seg, mapa = aud[f][int(a * SR):int(b * SR)].copy(), (lambda x: x)
    n = min(int(0.012 * SR), len(seg) // 4)
    if fade and n: seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
    for w in ws: palavras.append({"w": w["w"].strip(), "s": round(t + mapa(max(0, w["s"] - a)), 3), "e": round(t + mapa(min(b, w["e"]) - a), 3)})
    log.append([round(t, 2), f, round(a, 2), round(b, 2), " ".join(w["w"].strip() for w in ws)])
    out.append(seg); t += len(seg) / SR
    if gap: out.append(z(gap)); t += gap

def trecho(p, gap=0.18, fade=True):
    global t
    if p[0] == "RAWX":                     # corte exato, à mão
        _, f, a, b = p; emite(f, a, b, gap, fade, encurtar=False)
    elif p[0] == "RAWA":                   # começo no silêncio, fim exato (emenda com o "cinco")
        _, f, a, b = p; emite(f, corte_ini(f, a, (0.3, 0.3)), b, gap, fade)
    elif p[0] == "RAWB":                   # começo exato, fim no silêncio
        _, f, a, b = p; emite(f, a, corte_fim(f, b, (0.25, 0.5)), gap, fade)
    elif p[0] == "RAW":                    # tempos à mão, ajustados pro silêncio mais próximo
        _, f, a, b = p; emite(f, corte_ini(f, a, (0.3, 0.3)), corte_fim(f, b, (0.25, 0.5)), gap, fade)
    elif p[0] == "WAV":
        y, _ = librosa.load(D + p[1], sr=SR, mono=True); idx = np.where(np.abs(y) > 0.01)[0]; y = y[max(0, idx[0] - 240):idx[-1] + 480]
        palavras.append({"w": p[2], "s": round(t, 3), "e": round(t + len(y) / SR, 3)})
        n = int(0.006 * SR); y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
        out.append(y.astype(np.float32)); t += len(y) / SR
        if gap: out.append(z(gap)); t += gap
    elif p[0] == "CLONE":
        y, _ = librosa.load(D + "clone_%s.wav" % p[1], sr=SR); idx = np.where(np.abs(y) > 0.01)[0]; y = y[idx[0]:idx[-1]]
        ref = np.concatenate(out[-4:]); y *= np.sqrt(np.mean(ref[np.abs(ref) > 0.01] ** 2) + 1e-9) / np.sqrt(np.mean(y[np.abs(y) > 0.01] ** 2) + 1e-9)
        dd = len(y) / SR
        for k, w in enumerate(["É", "South", "Beach."]): palavras.append({"w": w, "s": round(t + dd * k / 3, 3), "e": round(t + dd * (k + 1) / 3, 3)})
        out.append(y.astype(np.float32)); t += dd; out.append(z(0.18)); t += 0.18
    else:                                  # trecho por palavras do whisper do take, cortado em silêncio
        f, a, b = p
        idx = [k for k, w in enumerate(wsp[f]) if w["s"] >= a - 0.06 and w["e"] <= b + 0.3]
        w0, w1 = wsp[f][idx[0]], wsp[f][idx[-1]]
        piso = (wsp[f][idx[0] - 1]["ae"] + 0.02) if idx[0] > 0 else 0.0          # nunca pega a palavra anterior
        teto = (min(wsp[f][idx[-1] + 1]["as"], wsp[f][idx[-1] + 1]["s"]) - 0.03) if idx[-1] + 1 < len(wsp[f]) else 1e9
        s0 = max(piso, corte_ini(f, w0["as"], (0.45, 0.1)))
        s1 = corte_fim(f, max(w1["ae"], w1["e"]) - 0.05, (0.1, 0.8), teto)
        emite(f, s0, s1, gap, fade)

for p in EDL:
    if p == "BLOCO": out.append(z(0.6)); t += 0.6; continue
    if p in DIAS:
        rg = REGRAV[p]
        arq = acha_regrav(rg[4])
        if arq:                          # regravação do usuário
            if rg[0]: trecho(rg[:4], gap=0.12)
            y, _ = librosa.load(arq, sr=SR, mono=True); idx = np.where(np.abs(y) > 0.01)[0]; y = y[max(0, idx[0] - 2400):idx[-1] + 4800]
            # mesma duração da versão já renderizada: o resto do vídeo não sai do lugar (só re-renderiza a parte 1)
            ALVO = {"INICIO_DIAS": 107175 / SR}   # duração exata (em amostras) da versão de 4 dias
            if p in ALVO:
                n_ = int(round(ALVO[p] * SR))
                if len(y) <= n_: y = np.concatenate([y, np.zeros(n_ - len(y), np.float32)])
                else: print("AVISO: regravação %s mais longa que o alvo (%.2f > %.2f s): o vídeo todo muda" % (p, len(y) / SR, ALVO[p]))
            palavras.append({"w": "REGRAVACAO_" + p, "s": round(t, 3), "e": round(t + len(y) / SR, 3)})
            out.append(y.astype(np.float32)); t += len(y) / SR; out.append(z(0.15)); t += 0.15
            if rg[5]: trecho(rg[5])
        else:
            a, w5, b = DIAS[p]
            trecho(a, gap=0, fade=False); trecho(w5, gap=0); trecho(b)
        continue
    trecho(p)
y = np.concatenate(out)

# pausas de meme
NW = [norm(w["w"]) for w in palavras]
beats = {}
for frase, dur, nome in BEATS:
    f = norm(frase).split(); pos = None
    for i in range(len(palavras)):
        if NW[i:i + len(f)] == f: pos = i + len(f) - 1; break
    if pos is None: raise SystemExit("frase do beat não achada: " + frase)
    tc = palavras[pos]["e"] + 0.1
    if pos + 1 < len(palavras): tc = min(tc + 0.3, (palavras[pos]["e"] + palavras[pos + 1]["s"]) / 2)
    # procura o trecho mais quieto (janela de 60 ms) entre o fim da frase e o começo da próxima
    hh = int(0.01 * SR); a_, b_ = int((palavras[pos]["e"] - 0.05) * SR), int(((palavras[pos + 1]["s"] + 0.05) if pos + 1 < len(palavras) else tc + 0.3) * SR)
    if b_ - a_ > 8 * hh:
        en = [np.abs(y[k:k + 6 * hh]).mean() for k in range(a_, b_ - 6 * hh, hh)]
        tc = (a_ + int(np.argmin(en)) * hh + 3 * hh) / SR
    k = int(tc * SR); y = np.concatenate([y[:k], z(dur), y[k:]])
    for w in palavras[pos + 1:]: w["s"] = round(w["s"] + dur, 3); w["e"] = round(w["e"] + dur, 3)
    for b_ in beats.values():
        if b_["ini"] >= tc: b_["ini"] += dur; b_["fim"] += dur; b_["fala"] = [x + dur if x >= tc else x for x in b_["fala"]]
    # "fala" = início e fim da frase que puxa o meme
    beats[nome] = {"ini": round(tc, 3), "fim": round(tc + dur, 3), "fala": [palavras[pos - len(f) + 1]["s"], palavras[pos]["e"]]}

sf.write(D + "NARRACAO_V2.wav", y, SR, subtype="PCM_24")
json.dump([{"start": palavras[0]["s"], "end": palavras[-1]["e"], "words": palavras}], open(D + "v2_palavras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(beats, open(D + "v2_beats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(log, open(D + "v2_edl_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("dur %.1f s, %d palavras, beats %d" % (len(y) / SR, len(palavras), len(beats)))
