# Escolhe a melhor de 3 versões por fala: texto ouvido (whisper) + não pode terminar/começar cortada. Copia para escolhidas/<voz>/
import os, glob, site, shutil, re, difflib, unicodedata, json
for sp in site.getsitepackages():
    for d in glob.glob(os.path.join(sp, 'nvidia', '*', 'bin')): os.add_dll_directory(d); os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
import torch; tl = os.path.join(os.path.dirname(torch.__file__), 'lib'); os.add_dll_directory(tl); os.environ['PATH'] = tl + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel
import numpy as np, soundfile as sf; from scipy.signal import resample_poly
def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c)); return re.sub(r"[^a-z0-9 ]", " ", t).split()
m = WhisperModel('medium', device='cuda', compute_type='int8_float16', download_root='C:/deps/whisper/modelos')
rel = {}
for voz in ("nathan", "rodrigo"):
    linhas = [l.strip() for l in open(voz + ".txt", encoding="utf-8") if l.strip()]
    os.makedirs("escolhidas/" + voz, exist_ok=True)
    for i, txt in enumerate(linhas, 1):
        cands = []
        for take in "abc":
            f = "takes/%s_%s/linha_%02d.wav" % (voz, take, i)
            if not os.path.exists(f): continue
            a, sr = sf.read(f, dtype="float32"); pk = np.max(np.abs(a)) + 1e-9
            fim = np.sqrt(np.mean(a[-int(0.04 * sr):] ** 2)) / pk; ini = np.sqrt(np.mean(a[:int(0.03 * sr)] ** 2)) / pk
            s, _ = m.transcribe(resample_poly(a, 16000, sr).astype("float32"), language="pt", beam_size=5)
            ouv = " ".join(x.text.strip() for x in s); r = difflib.SequenceMatcher(None, norm(txt), norm(ouv)).ratio()
            nota = r - (0.35 if fim > 0.12 else 0) - (0.2 if ini > 0.12 else 0)
            cands.append((nota, take, round(r, 2), round(fim, 3), ouv, f))
        cands.sort(reverse=True); best = cands[0]
        shutil.copy(best[5], "escolhidas/%s/linha_%02d.wav" % (voz, i))
        rel["%s %d" % (voz, i)] = [(c[1], c[2], c[3], c[4]) for c in cands]
        print(voz, i, "->", best[1], best[2], "fim", best[3], "|", best[4])
json.dump(rel, open("escolha.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
