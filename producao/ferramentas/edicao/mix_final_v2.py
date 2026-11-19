# Mix do vídeo final: voz do usuário (com trechos de "voz zuada") + músicas com ducking + SFX baixos + memes + CJ/jacaré
import json, os, numpy as np, soundfile as sf, librosa
from scipy.ndimage import uniform_filter1d
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000
db = lambda x: 10 ** (x / 20)
def load(p): y, _ = librosa.load(p, sr=SR, mono=True); return y.astype(np.float32)
T = json.load(open(B + "/scripts/final_tempos_v2.json", encoding="utf-8"))
L = {int(k): v for k, v in T["linhas"].items()}; ini = lambda n: L[n]; DUR = T["dur"]; N = int(DUR * SR)
voz = load(B + "/narracao/usuario/NARRACAO_FINAL_V2.wav"); v = np.zeros(N, np.float32); v[:len(voz)] = voz[:N]; voz = v
voz *= db(-18) / np.sqrt(np.mean(voz[np.abs(voz) > 0.01] ** 2))
# voz zuada: tom mais agudo + leve eco curto
for a, b in T["voz_zuada"]:
    i, j = int(a * SR), int(b * SR); seg = voz[i:j].copy()
    z = librosa.effects.pitch_shift(seg, sr=SR, n_steps=4.5)
    d = int(0.07 * SR); z2 = z.copy(); z2[d:] += 0.25 * z[:-d]
    f = int(0.03 * SR); w = np.ones(len(z2)); w[:f] = np.linspace(0, 1, f); w[-f:] = np.linspace(1, 0, f)
    voz[i:j] = seg * (1 - w) + z2 * w * 1.05
M = B + "/assets/musica/mixkit_%s.mp3"
G0 = T["G0"]
plano = [("706", 0, G0 + 0.5, 0.0), ("159", G0 - 0.8, ini(7), 0.4), ("131", ini(7) - 0.8, ini(20), 0.4), ("173", ini(20) - 1.5, ini(37) - 0.5, 0.4),
         ("400", ini(37) - 1.5, ini(52) - 0.5, 0.4), ("318", ini(52) - 1.5, ini(64) - 0.5, 0.4), ("369", ini(64) - 1.5, ini(77), 0.4),
         ("76", ini(77) - 1.5, ini(88), 0.4), ("131", ini(88) - 1.5, DUR, 30.0)]
mus = np.zeros(N, np.float32); XF = 1.5
for f, a, b, off in plano:
    y = load(M % f)[int(off * SR):]; y *= db(-18) / np.sqrt(np.mean(y[:SR * 30] ** 2))
    i0, i1 = int(max(0, a) * SR), min(N, int(b * SR)); n = i1 - i0
    while len(y) < n: y = np.concatenate([y, y])
    seg = y[:n].copy(); fx = int(XF * SR); seg[:fx] *= np.linspace(0, 1, fx); seg[-fx:] *= np.linspace(1, 0, fx)
    mus[i0:i1] += seg
# memes / efeitos de cena
ev = []
for x in T["audios"]: ev.append((B + "/" + x[0], 0.0, x[1], x[2], x[3] if len(x) > 3 else None))
m = T["jacare_mordida"]; j0 = T["jacare_ini"]; J = B + "/assets/memes/sfx_jacare/"; CJ = B + "/assets/memes/cj/"
ev += [(J + "jacare_splash_agua.mp3", 0.0, j0 + 0.1, -24, None), (J + "jacare_rosnado.mp3", 0.0, j0 + 0.3, -26, None),
       (J + "jacare_mordida_crunch.mp3", 0.0, m - 0.05, -20, None), (CJ + "cj_grito_longo.mp3", 0.0, m + 0.05, -15, None),
       (CJ + "cj_grito_dor_02.mp3", 0.0, m + 1.35, -17, None), (J + "jacare_splash_agua_2.mp3", 0.0, m + 0.9, -25, None), (CJ + "cj_grito_dor_05.mp3", 0.0, m + 2.3, -18, None)]
memes = np.zeros(N, np.float32)
for f, pico, t, d, mx in ev:
    s = load(f); s /= np.max(np.abs(s)) + 1e-9
    if mx:   # som do meme só dura a pausa dele: corta com fade de 0,3 s
        n = int(mx * SR)
        if len(s) > n: s = s[:n].copy(); fo = min(int(0.3 * SR), n); s[-fo:] *= np.linspace(1, 0, fo)
    i = int((t - pico) * SR)
    if i < 0: s = s[-i:]; i = 0
    j = min(N, i + len(s)); memes[i:j] += s[: j - i] * db(d)
# ducking da música pela voz e pelos memes
env = uniform_filter1d(np.abs(voz) + np.abs(memes), size=int(0.05 * SR))
ativo = uniform_filter1d((env > db(-38)).astype(np.float32), size=int(0.35 * SR))
g = (db(-22) * (1 - ativo) + db(-29) * ativo) * 3.2
g *= np.clip((N - np.arange(N)) / (2.5 * SR), 0, 1)
for a, b in T["preto"]:   # nos momentos de fundo preto a música quase some
    i, j = int(a * SR), int(b * SR); g[i:j] *= 0.35
mus *= g
# SFX baixinhos (nunca whoosh_rapido_1490)
S = B + "/assets/sfx/"; ev = []
for a, b in T["titulos"].values(): ev.append(("whoosh_ar_1489.mp3", 0.72, a, -30))
for t0, tam in T["cards"]:
    if tam == 160: ev.append(("pop_texto_3005.mp3", 0.06, t0, -34))
tit = [a for a, b in T["titulos"].values()]
for t in T["whips"]:
    if not any(abs(t - x) < 0.1 for x in tit): ev.append(("sweep_curto_166.mp3", 0.30, t, -35))
ev += [("heartbeat_impacto_498.mp3", 0.10, ini(78) + 0.2, -25), ("riser_trailer_790.mp3", 2.49, T["titulos"]["79"][0], -28),
       ("impacto_grande_788.mp3", 2.20, T["titulos"]["79"][0] + 0.05, -24), ("impacto_grande_788.mp3", 2.20, ini(93) + 0.75, -24)]
sfx = np.zeros(N, np.float32)
for fn, pico, t, d in ev:
    s = load(S + fn); s /= np.max(np.abs(s)) + 1e-9; i = int((t - pico) * SR)
    if i < 0: s = s[-i:]; i = 0
    j = min(N, i + len(s)); sfx[i:j] += s[: j - i] * db(d)
mix = voz + mus + sfx + memes
sf.write(B + "/render/final_mix_v2_raw.wav", np.stack([mix, mix], 1), SR, subtype="PCM_24")
print("ok dur %.2f pico %.2f" % (DUR, np.max(np.abs(mix))))
