import sys, os, json, glob, numpy as np, soundfile as sf, torch, librosa
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
from faster_whisper import WhisperModel
sys.stdout.reconfigure(encoding="utf-8")
m = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
for d in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(d, "*_[0-9][0-9].wav"))):
        w, sr = sf.read(f, dtype="float32"); w = librosa.resample(w, orig_sr=sr, target_sr=16000)
        t = " ".join(s.text.strip() for s in m.transcribe(w, language="pt", beam_size=5, condition_on_previous_text=False)[0])
        print("%s (%.1fs): %s" % (os.path.basename(f), len(w)/16000, t))
