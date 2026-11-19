# Mix do vídeo 03: voz IA + músicas (troca a cada 2 blocos) com ducking + memes nas pausas + SFX (whoosh no relógio)
import json, os, numpy as np, soundfile as sf, librosa
from scipy.ndimage import uniform_filter1d
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = "C:/Projetos Dev/Videos/2026-11-13_video01-lugares-gta6/assets"; SR = 48000
db = lambda x: 10 ** (x / 20)
def load(p): y, _ = librosa.load(p, sr=SR, mono=True); return y.astype(np.float32)
T = json.load(open(B + "/scripts/tempos.json", encoding="utf-8")); DUR = T["dur"]; N = int(DUR * SR)
voz = load(B + "/narracao_dp/narracao.wav"); v = np.zeros(N, np.float32); v[:min(N, len(voz))] = voz[:N]; voz = v
voz *= db(-18) / np.sqrt(np.mean(voz[np.abs(voz) > 0.01] ** 2))
TR = ["706", "159", "131", "173", "400", "318", "369", "76"]
cortes = [0.0] + T["blocos"][1::2] + [DUR]
mus = np.zeros(N, np.float32); XF = 1.2
for k in range(len(cortes) - 1):
    a, b = cortes[k], cortes[k + 1]
    y = load(A + "/musica/mixkit_%s.mp3" % TR[k % len(TR)])[int(0.4 * SR):]; y *= db(-18) / np.sqrt(np.mean(y[:SR * 30] ** 2))
    i0, i1 = int(max(0, a - (1.0 if k else 0)) * SR), min(N, int((b + 0.4) * SR)); n = i1 - i0
    while len(y) < n: y = np.concatenate([y, y])
    seg = y[:n].copy(); fx = int(XF * SR); seg[:fx] *= np.linspace(0, 1, fx); seg[-fx:] *= np.linspace(1, 0, fx); mus[i0:i1] += seg
M = {"25": ("memes/meme_e_o_que.mp3", -16), "47": ("memes/meme_que_fase_milton_leite.mp3", -16), "58": ("memes/ratinho/ratinho_rapaz.mp3", -15), "75": ("memes/meme_curb_your_enthusiasm_tururu.mp3", -17)}
memes = np.zeros(N, np.float32)
for k, (a, b) in T["memes"].items():
    f, d = M[k]; a += 0.1
    s = load(A + "/" + f); s /= np.max(np.abs(s)) + 1e-9; n = int((b - a) * SR)
    if len(s) > n: s = s[:n].copy(); fo = min(int(0.3 * SR), n); s[-fo:] *= np.linspace(1, 0, fo)
    i = int(a * SR); j = min(N, i + len(s)); memes[i:j] += s[:j - i] * db(d)
env = uniform_filter1d(np.abs(voz) + np.abs(memes), size=int(0.05 * SR))
ativo = uniform_filter1d((env > db(-38)).astype(np.float32), size=int(0.35 * SR))
g = (db(-22) * (1 - ativo) + db(-29) * ativo) * 3.2
g *= np.clip((N - np.arange(N)) / (2.5 * SR), 0, 1)
for a, b in T["memes"].values(): g[int(a * SR):int(b * SR)] *= 0.4
mus *= g
S = A + "/sfx/"; ev = [("impacto_logo_intro_2900.mp3", 0.05, 0.05, -24)]
for t in T["relogios"][1:]: ev += [("whoosh_ar_1489.mp3", 0.72, t + 0.05, -28), ("pop_texto_3005.mp3", 0.06, t + 0.9, -32)]
for t0, tam in T["cards"]:
    if tam >= 150: ev.append(("pop_texto_3005.mp3", 0.06, t0, -34))
sfx = np.zeros(N, np.float32)
for fn, pico, t, d in ev:
    s = load(S + fn); s /= np.max(np.abs(s)) + 1e-9; i = int((t - pico) * SR)
    if i < 0: s = s[-i:]; i = 0
    j = min(N, i + len(s)); sfx[i:j] += s[:j - i] * db(d)
mix = voz + mus + sfx + memes
sf.write(B + "/render/mix_raw.wav", np.stack([mix, mix], 1), SR, subtype="PCM_24")
print("ok dur %.2f pico %.2f" % (DUR, np.max(np.abs(mix))))
