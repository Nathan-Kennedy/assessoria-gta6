# Gera uma fala por linha (voz clonada hi-fi), aplica dicionario de pronuncia, salva wav por linha + json com duracoes.
import sys, os, json, time, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pronuncia_ptbr import aplicar
from voxcpm import VoxCPM
linhas_txt, ref_wav, ref_txt, outdir = sys.argv[1:5]
so = set(int(x) for x in sys.argv[5].split(",")) if len(sys.argv) > 5 else None
os.makedirs(outdir, exist_ok=True)
linhas = [l.strip() for l in open(linhas_txt, encoding="utf-8") if l.strip()]
prompt = open(ref_txt, encoding="utf-8").read().strip()
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False); sr = m.tts_model.sample_rate
info_path = os.path.join(outdir, "linhas.json")
info = json.load(open(info_path, encoding="utf-8")) if os.path.exists(info_path) else {}
for i, l in enumerate(linhas, 1):
    if so and i not in so: continue
    t = time.time()
    wav = np.asarray(m.generate(text=aplicar(l), prompt_wav_path=ref_wav, prompt_text=prompt, reference_wav_path=ref_wav, cfg_value=2.0, inference_timesteps=10), dtype=np.float32)
    f = os.path.join(outdir, "linha_%02d.wav" % i); sf.write(f, wav, sr)
    info[str(i)] = {"texto": l, "arquivo": os.path.basename(f), "dur": round(len(wav)/sr, 2)}
    print("%02d %.1fs (%.0fs) %s" % (i, len(wav)/sr, time.time()-t, l[:60]), flush=True)
json.dump(info, open(info_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
