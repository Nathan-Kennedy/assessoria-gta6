# Corta as falas boas (tsv: inicio fim texto), ajusta as bordas no silencio mais proximo, normaliza e gera clipes + arquivo unico + metadata.
import sys, os, json, numpy as np, soundfile as sf
src, tsv, outdir, prefixo = sys.argv[1:5]
wav, sr = sf.read(src, dtype="float32"); os.makedirs(outdir, exist_ok=True)
hop = int(sr*0.01); n = len(wav)//hop
db = 20*np.log10(np.sqrt(np.mean(wav[:n*hop].reshape(n, hop)**2, axis=1))+1e-9)
quieto = np.percentile(db, 20) + 8
def borda(t, direcao, limite):
    i = int(t/0.01)
    for _ in range(int(limite/0.01)):
        if 0 <= i < n and db[i] < quieto: return i*0.01
        i += direcao
    return t + direcao*limite
linhas = [l.rstrip("\n").split("\t") for l in open(tsv, encoding="utf-8") if l.strip()]
meta, juntos = [], []
for k, (a, b, txt) in enumerate(linhas, 1):
    a = max(0, borda(float(a)-0.05, -1, 0.35) - 0.08); b = min(len(wav)/sr, borda(float(b)+0.05, 1, 0.45) + 0.12)
    clip = wav[int(a*sr):int(b*sr)].copy()
    f = int(sr*0.015); clip[:f] *= np.linspace(0, 1, f); clip[-f:] *= np.linspace(1, 0, f)
    nome = "%s_%02d.wav" % (prefixo, k); sf.write(os.path.join(outdir, nome), clip, sr)
    meta.append({"audio": nome, "text": txt, "inicio": round(a, 2), "fim": round(b, 2)})
    juntos += [clip, np.zeros(int(sr*0.6), dtype=np.float32)]
sf.write(os.path.join(outdir, prefixo + "_completo.wav"), np.concatenate(juntos), sr)
with open(os.path.join(outdir, prefixo + "_metadata.jsonl"), "w", encoding="utf-8") as fh:
    for m in meta: fh.write(json.dumps(m, ensure_ascii=False) + "\n")
print("%d falas, %.1fs de fala" % (len(meta), sum(m["fim"]-m["inicio"] for m in meta)))
