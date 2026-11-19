import sys, time, numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel
roteiro, ref_wav, ref_txt, saida = sys.argv[1:5]
lang = sys.argv[5] if len(sys.argv) > 5 else "Auto"
paras = [l.strip() for l in open(roteiro, encoding="utf-8") if l.strip()]
ref_text = open(ref_txt, encoding="utf-8").read().strip()
t0 = time.time()
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa")
print("modelo carregado em %.0fs" % (time.time()-t0), flush=True)
prompt = m.create_voice_clone_prompt(ref_audio=ref_wav, ref_text=ref_text)
partes, sr = [], None
t1 = time.time()
for p in paras:
    wavs, sr = m.generate_voice_clone(text=p, language=lang, voice_clone_prompt=prompt)
    partes += [wavs[0], np.zeros(int(sr*0.45), dtype=np.float32)]
audio = np.concatenate(partes)
sf.write(saida, audio, sr)
print("audio %.1fs gerado em %.0fs, pico VRAM %.1f GB" % (len(audio)/sr, time.time()-t1, torch.cuda.max_memory_allocated()/1e9))
