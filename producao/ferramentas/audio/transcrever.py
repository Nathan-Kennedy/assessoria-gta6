"""Transcreve um audio com faster-whisper (GPU) e salva palavras com tempo em JSON.
Uso: C:/deps/whisper/venv/Scripts/python.exe transcrever.py <audio> <saida.json> [modelo]"""
import os, sys, json, glob
# DLLs do CUDA instaladas pelo pip (nvidia-cublas / nvidia-cudnn)
import site
for sp in site.getsitepackages():
    for d in glob.glob(os.path.join(sp, 'nvidia', '*', 'bin')):
        os.add_dll_directory(d); os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel

audio, saida = sys.argv[1], sys.argv[2]
modelo = sys.argv[3] if len(sys.argv) > 3 else 'large-v3'
m = WhisperModel(modelo, device='cuda', compute_type='float16', download_root='C:/deps/whisper/modelos')
segs, info = m.transcribe(audio, language='pt', word_timestamps=True, vad_filter=False,
                          beam_size=5, condition_on_previous_text=True)
out = []
for s in segs:
    out.append({'start': s.start, 'end': s.end, 'text': s.text.strip(),
                'words': [{'w': w.word.strip(), 's': w.start, 'e': w.end, 'p': w.probability} for w in s.words]})
    print('%7.2f %s' % (s.start, s.text.strip()), flush=True)
json.dump(out, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', len(out), 'segmentos')
