"""Alinhamento forcado (torchaudio MMS_FA) das palavras transcritas pelo Whisper: corrige o tempo de cada palavra.
O Whisper erra o inicio das palavras em ate ~0,5 s; o alinhador acha o trecho exato de cada palavra no audio.
Uso (python com torch/torchaudio, ex. o .venv do ComfyUI):
    python alinhar_palavras.py transcricao.json audio16k.wav saida_alinhada.json [cpu|cuda]
Mesmo formato do transcrever.py; palavras sem letras (numeros) ficam entre as vizinhas.
"""
import json, sys, unicodedata, re
import torch, torchaudio
import torchaudio.functional as F
from torchaudio.pipelines import MMS_FA as BUNDLE
import scipy.io.wavfile as wavfile
import numpy as np

trans, wav, saida = sys.argv[1:4]
dev = sys.argv[4] if len(sys.argv) > 4 else "cpu"
model = BUNDLE.get_model(with_star=False).to(dev).eval()
dic = BUNDLE.get_dict(star=None)
sr, x = wavfile.read(wav)
assert sr == 16000
x = torch.from_numpy(x.astype(np.float32) / 32768.0)
if x.ndim > 1: x = x.mean(1)


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return "".join(c for c in w if dic.get(c, 0) != 0)   # 0 = blank (o '-' cai nele)


segs = json.load(open(trans, encoding="utf-8"))
PAD = 0.6
for si, seg in enumerate(segs):
    ws = seg["words"]
    a = max(0.0, seg["start"] - PAD); b = min(len(x) / sr, seg["end"] + PAD)
    idx = [i for i, w in enumerate(ws) if norm(w["w"])]
    if not idx: continue
    toks = [norm(ws[i]["w"]) for i in idx]
    chunk = x[int(a * sr):int(b * sr)].unsqueeze(0).to(dev)
    with torch.inference_mode():
        em, _ = model(chunk)
    em = em.cpu()
    alvo = torch.tensor([[dic[c] for t in toks for c in t]], dtype=torch.int32)
    if alvo.shape[1] > em.shape[1]: continue
    ali, sc = F.forced_align(em, alvo, blank=0)
    spans = F.merge_tokens(ali[0], sc[0].exp())
    fps = em.shape[1] / chunk.shape[1] * sr          # quadros do modelo por segundo (~50)
    k = 0
    for i, t in zip(idx, toks):
        sp = spans[k:k + len(t)]; k += len(t)
        ws[i]["s_whisper"], ws[i]["e_whisper"] = ws[i]["s"], ws[i]["e"]
        ws[i]["s"] = round(a + sp[0].start / fps, 3)
        ws[i]["e"] = round(a + sp[-1].end / fps, 3)
        ws[i]["alinhado"] = True
    # palavras sem letras: entre as vizinhas alinhadas
    for i, w in enumerate(ws):
        if not w.get("alinhado"):
            ant = next((ws[j]["e"] for j in range(i - 1, -1, -1) if ws[j].get("alinhado")), w["s"])
            pos = next((ws[j]["s"] for j in range(i + 1, len(ws)) if ws[j].get("alinhado")), w["e"])
            w["s"], w["e"] = ant, max(ant, pos)
    print("%3d/%d %7.2f %s" % (si + 1, len(segs), seg["start"], seg["text"][:50]), flush=True)

json.dump(segs, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", saida)
