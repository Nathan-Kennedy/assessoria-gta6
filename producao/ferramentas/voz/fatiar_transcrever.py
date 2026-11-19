# Divide o audio nas pausas (energia) e transcreve cada fala separadamente.
import sys, os, json, numpy as np, soundfile as sf, torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
from faster_whisper import WhisperModel
sys.stdout.reconfigure(encoding="utf-8")
wav, sr = sf.read(sys.argv[1], dtype="float32"); saida = sys.argv[2]
pausa_min = float(sys.argv[3]) if len(sys.argv) > 3 else 0.45
hop = int(sr*0.02); n = len(wav)//hop
db = 20*np.log10(np.sqrt(np.mean(wav[:n*hop].reshape(n, hop)**2, axis=1))+1e-9)
lim = np.percentile(db, 20) + 12  # limiar adaptativo acima do ruido de fundo
voz = db > lim
chunks, i = [], 0
while i < n:
    if voz[i]:
        j = i
        while j < n:
            k = j
            while k < n and not voz[k]: k += 1
            if k - j > pausa_min/0.02 or k >= n: break
            j = k + 1 if k < n else k
            while j < n and voz[j]: j += 1
        if (j - i)*0.02 > 0.3: chunks.append((max(0, i*0.02-0.1), min(len(wav)/sr, j*0.02+0.15)))
        i = j + 1
    else: i += 1
m = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
out = []
for a, b in chunks:
    seg = wav[int(a*sr):int(b*sr)]
    t = " ".join(s.text.strip() for s in m.transcribe(seg, language="pt", beam_size=5, condition_on_previous_text=False)[0])
    out.append({"start": round(a, 2), "end": round(b, 2), "text": t})
    print("%3d %7.2f-%7.2f %s" % (len(out)-1, a, b, t))
json.dump(out, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
