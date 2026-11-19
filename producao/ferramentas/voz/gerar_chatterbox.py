import sys, time, numpy as np, soundfile as sf, torch
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
roteiro, ref_wav, saida = sys.argv[1:4]
paras = [l.strip() for l in open(roteiro, encoding="utf-8") if l.strip()]
t0 = time.time()
m = ChatterboxMultilingualTTS.from_pretrained(device="cuda")
print("modelo carregado em %.0fs" % (time.time()-t0), flush=True)
m.prepare_conditionals(ref_wav, exaggeration=0.5)
partes, sr = [], m.sr
t1 = time.time()
for p in paras:
    wav = m.generate(p, language_id="pt", exaggeration=0.5, cfg_weight=0.5)
    partes += [wav.squeeze(0).cpu().numpy(), np.zeros(int(sr*0.45), dtype=np.float32)]
audio = np.concatenate(partes)
sf.write(saida, audio, sr)
print("audio %.1fs gerado em %.0fs, pico VRAM %.1f GB" % (len(audio)/sr, time.time()-t1, torch.cuda.max_memory_allocated()/1e9))
