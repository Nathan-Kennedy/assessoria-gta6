# Corta a narração do DarkPlanner em uma fala por linha usando o SRT por palavra; cria linhas/linha_XX.wav + linhas/linhas.json
import re, json, os, sys, unicodedata, numpy as np, soundfile as sf, subprocess
def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c)); return re.sub(r"[^a-z0-9 ]", " ", t).split()
def srt(p):
    out = []
    for b in re.split(r"\n\s*\n", open(p, encoding="utf-8-sig").read().strip()):
        l = b.strip().splitlines()
        if len(l) < 3: continue
        a, c = [sum(float(x) * m for x, m in zip(re.split("[:,]", s.strip())[:3], (3600, 60, 1))) + int(re.split("[:,]", s.strip())[3]) / 1000 for s in l[1].split("-->")]
        ws = norm(" ".join(l[2:]))
        for k, w in enumerate(ws): out.append((w, a + (c - a) * k / len(ws), a + (c - a) * (k + 1) / len(ws)))
    return out
def cortar(mp3, srtp, linhas_txt, ids, outdir, info):
    wav = mp3.replace(".mp3", ".wav"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ac", "1", "-ar", "48000", wav], check=True)
    a, sr = sf.read(wav, dtype="float32"); W = srt(srtp); i = 0; bounds = []
    for n, t in zip(ids, linhas_txt):
        k = len(norm(t)); s0, e0 = W[i][1], W[min(i + k, len(W)) - 1][2]; bounds.append([n, s0, e0, t]); i += k
    print("palavras srt", len(W), "usadas", i)
    for j, (n, s0, e0, t) in enumerate(bounds):
        ini = (bounds[j - 1][2] + s0) / 2 if j else max(0, s0 - 0.1)
        fim = (e0 + bounds[j + 1][1]) / 2 if j + 1 < len(bounds) else min(len(a) / sr, e0 + 0.4)
        seg = a[int(ini * sr):int(fim * sr)].copy(); f = int(0.01 * sr); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        nome = "linha_%02d.wav" % n; sf.write(os.path.join(outdir, nome), seg, sr)
        info[str(n)] = {"texto": t, "arquivo": nome, "dur": round(len(seg) / sr, 2)}
os.makedirs("linhas", exist_ok=True); info = {}
L1 = [l.strip() for l in open("linhas_v1.txt", encoding="utf-8") if l.strip()]
cortar("darkplanner_audio_09d2aeed.mp3", "Darkplanner_srtsyncpalavra.srt", L1, list(range(1, len(L1) + 1)), "linhas", info)
L = [l.strip() for l in open("linhas.txt", encoding="utf-8") if l.strip()]
ids = [int(x) for x in open("correcoes_ids.txt").read().split(",")]
cortar("correcoes/darkplanner_audio_17dea56d.mp3", "correcoes/Darkplanner_srtsyncpalavra.srt", [L[n - 1] for n in ids], ids, "linhas", info)
json.dump(info, open("linhas/linhas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(info), "falas;", "exemplo 85:", info["85"])
