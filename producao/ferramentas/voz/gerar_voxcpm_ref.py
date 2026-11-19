# Clona so pelo audio (sem transcricao). Uso: roteiro ref.wav saida.wav ["descricao de estilo"]
import sys, time, numpy as np, soundfile as sf, torch
from voxcpm import VoxCPM
roteiro, ref_wav, saida = sys.argv[1:4]
estilo = sys.argv[4] if len(sys.argv) > 4 else ""
paras = [l.strip() for l in open(roteiro, encoding="utf-8") if l.strip()]
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
sr = m.tts_model.sample_rate
partes, t1 = [], time.time()
for p in paras:
    txt = "(%s)%s" % (estilo, p) if estilo else p
    wav = m.generate(text=txt, reference_wav_path=ref_wav)
    partes += [np.asarray(wav, dtype=np.float32), np.zeros(int(sr*0.45), dtype=np.float32)]
audio = np.concatenate(partes)
sf.write(saida, audio, sr)
print("audio %.1fs em %.0fs" % (len(audio)/sr, time.time()-t1), flush=True)
