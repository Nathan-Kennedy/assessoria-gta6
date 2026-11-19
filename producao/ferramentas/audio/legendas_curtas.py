"""Gera legendas curtas (poucas palavras) sincronizadas com a linha do tempo do FilmCraft.
Entradas: transcricao.json (transcrever.py, tempos do arquivo original), audio wav do original,
sequencia.json (filmcraft-cli inspect sequence). Saida: SRT na linha do tempo editada.
Uso: python legendas_curtas.py transcricao.json audio.wav sequencia.json saida.srt [correcoes.json]"""
import sys, json, re
import numpy as np, scipy.io.wavfile as wavfile

TICKS = 254016000000
MAX_PAL, MAX_CAR, MAX_SEG = 3, 20, 1.8

trans, wav, seqf, saida = sys.argv[1:5]
corr = json.load(open(sys.argv[5], encoding='utf-8')) if len(sys.argv) > 5 else {}

# energia em janelas de 10 ms para ajustar o inicio/fim de cada palavra
sr, x = wavfile.read(wav)
x = x.astype(np.float32) / 32768
if x.ndim > 1: x = x.mean(1)
hop = sr // 100
n = len(x) // hop
db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
voz = db > -45

def ajustar(s, e):
    i, j = int(s * 100), int(e * 100)
    a = i
    while a < j and a < n and not voz[a]: a += 1        # inicio caiu no silencio: avanca
    b = j
    while b > a and b - 1 < n and not voz[b - 1]: b -= 1  # fim caiu no silencio: recua
    if b - a < 8: return s, e                            # palavra muito curta: confia no whisper
    return a / 100, b / 100

pal = []
for seg in json.load(open(trans, encoding='utf-8')):
    for w in seg['words']:
        t = w['w'].strip()
        if not t: continue
        # alinhado (alinhar_palavras.py) ja e exato; so o tempo cru do whisper passa pelo ajuste de energia
        s, e = (w['s'], w['e']) if w.get('alinhado') else ajustar(w['s'], w['e'])
        pal.append([t, s, e])
# o alinhamento e feito por trecho com folga; na emenda de dois trechos uma palavra pode cair antes da anterior
for k in range(1, len(pal)):
    pal[k][1] = max(pal[k][1], pal[k - 1][2])
    pal[k][2] = max(pal[k][2], pal[k][1] + 0.05)

# correcoes de texto (frase -> frase), aplicadas palavra a palavra em sequencia
texto = [p[0] for p in pal]
for de, para in corr.items():
    d, pa = de.split(), para.split()
    i = 0
    while i <= len(texto) - len(d):
        if [re.sub(r'[^\w]', '', t).lower() for t in texto[i:i + len(d)]] == [re.sub(r'[^\w]', '', t).lower() for t in d]:
            pont = re.sub(r'^[\w-]+', '', texto[i + len(d) - 1])
            novos = pa[:-1] + [pa[-1] + pont]
            s, e = pal[i][1], pal[i + len(d) - 1][2]
            dur = (e - s) / len(novos)
            pal[i:i + len(d)] = [[t, s + k * dur, s + (k + 1) * dur] for k, t in enumerate(novos)]
            texto = [p[0] for p in pal]
            i += len(novos)
        else:
            i += 1

# mapa origem -> linha do tempo pelos clipes de video
q = json.load(open(seqf, encoding='utf-8'))
clipes = [(c['sourceIn'] / TICKS, c['sourceOut'] / TICKS, c['start'] / TICKS, c['speed'])
          for c in q['video'][0]['items']]

def mapear(s, e):
    for si, so, st, v in clipes:
        a, b = max(s, si), min(e, so)
        if b - a > 0.5 * (e - s) or (b > a and b - a > 0.15):
            return st + (a - si) / v, st + (b - si) / v, v
    return None

lt = []
for t, s, e in pal:
    m = mapear(s, e)
    if m and m[2] == 1.0: lt.append([t, m[0], m[1]])   # trecho acelerado (3x) fica sem legenda

# agrupar em blocos curtos
blocos, cur = [], []
def fecha():
    global cur
    if cur: blocos.append(cur); cur = []
for k, (t, s, e) in enumerate(lt):
    if cur:
        txt = ' '.join(p[0] for p in cur + [[t]])
        if (len(cur) >= MAX_PAL or len(txt) > MAX_CAR or e - cur[0][1] > MAX_SEG or s - cur[-1][2] > 0.35):
            fecha()
    cur.append([t, s, e])
    if re.search(r'[.?!,;:]$', t): fecha()
fecha()

# palavra de ligacao no fim do bloco passa para o proximo (le melhor: "a ideia", nao "ideia e a")
LIGA = {'a','e','o','os','as','de','da','do','das','dos','que','para','pra','um','uma','no','na','nos','nas',
        'em','com','por','ao','se','mas','ou','eu','ele','ela','nós','vai','é','à','lá'}
nu = lambda t: re.sub(r'[^\w]', '', t).lower()
mudou = True
while mudou:
    mudou = False
    for i in range(len(blocos) - 1):
        b, c = blocos[i], blocos[i + 1]
        if len(b) > 1 and nu(b[-1][0]) in LIGA and not re.search(r'[.?!,;:]$', b[-1][0])            and c[0][1] - b[-1][2] < 0.35 and len(c) < MAX_PAL + 1:
            c.insert(0, b.pop()); mudou = True
    # bloco de uma palavra curta gruda no vizinho mais proximo
    for i in range(len(blocos)):
        b = blocos[i]
        if len(b) == 1 and len(nu(b[0][0])) <= 3 and i + 1 < len(blocos) and            blocos[i + 1][0][1] - b[0][2] < 0.35 and not re.search(r'[.?!,;:]$', b[0][0]):
            blocos[i + 1][:0] = b; blocos[i] = []; mudou = True
    blocos = [b for b in blocos if b]

def limpa(b):
    s = ' '.join(p[0] for p in b)
    s = re.sub(r'[,;:]$', '', s)
    s = re.sub(r'\.$', '', s)
    s = re.sub(r'(\d) %', r'\1%', s)
    return s

legs = []
for i, b in enumerate(blocos):
    s, e = b[0][1], b[-1][2] + 0.12
    if i + 1 < len(blocos):
        prox = blocos[i + 1][0][1]
        if prox - e < 0.3: e = prox - 0.02          # cola no proximo para nao piscar
    e = max(e, s + 0.45)
    if i + 1 < len(blocos): e = min(e, blocos[i + 1][0][1] - 0.02)
    legs.append((s, e, limpa(b)))

def tc(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); ss, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, ss, ms)
with open(saida, 'w', encoding='utf-8') as f:
    for i, (s, e, t) in enumerate(legs, 1):
        f.write('%d\n%s --> %s\n%s\n\n' % (i, tc(s), tc(e), t))
print(len(legs), 'legendas ->', saida)
