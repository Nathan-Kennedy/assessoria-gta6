import sys, time, numpy as np, soundfile as sf, torch
from voxcpm import VoxCPM
roteiro, ref_wav, ref_txt, saida = sys.argv[1:5]
paras = [l.strip() for l in open(roteiro, encoding="utf-8") if l.strip()]
ref_text = open(ref_txt, encoding="utf-8").read().strip()
t0 = time.time()
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
sr = m.tts_model.sample_rate
print("modelo carregado em %.0fs" % (time.time()-t0), flush=True)
partes = []
t1 = time.time()
for p in paras:
    wav = m.generate(text=p, prompt_wav_path=ref_wav, prompt_text=ref_text, reference_wav_path=ref_wav)
    partes += [np.asarray(wav, dtype=np.float32), np.zeros(int(sr*0.45), dtype=np.float32)]
audio = np.concatenate(partes)
sf.write(saida, audio, sr)
print("audio %.1fs gerado em %.0fs, pico VRAM %.1f GB" % (len(audio)/sr, time.time()-t1, torch.cuda.max_memory_allocated()/1e9))
