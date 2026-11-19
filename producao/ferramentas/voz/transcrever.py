# Transcreve com timestamps por palavra. Le o wav com soundfile (evita bug do PyAV). Saida: JSON.
import sys, os, json, soundfile as sf, numpy as np
import torch  # carrega as DLLs de CUDA (cublas/cudnn) que o ctranslate2 precisa
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
from faster_whisper import WhisperModel
wav, sr = sf.read(sys.argv[1], dtype="float32")
assert sr == 16000
m = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
segs, _ = m.transcribe(wav, language="pt", beam_size=5, word_timestamps=True, vad_filter=False, condition_on_previous_text=False)
out = [{"start": s.start, "end": s.end, "text": s.text.strip(), "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]} for s in segs]
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for s in out: print("%7.2f-%7.2f %s" % (s["start"], s["end"], s["text"]))
