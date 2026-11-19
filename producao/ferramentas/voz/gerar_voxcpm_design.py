# 1) cria uma voz pela descricao (Voice Design); 2) usa essa voz como referencia pra narrar o roteiro inteiro com voz consistente
import sys, time, numpy as np, soundfile as sf, torch, librosa
from voxcpm import VoxCPM
roteiro, saida_prefixo = sys.argv[1:3]
descricoes = dict(a.split("=", 1) for a in sys.argv[3:])
paras = [l.strip() for l in open(roteiro, encoding="utf-8") if l.strip()]
REF_TXT = "Olá, pessoal. Hoje eu vou contar uma história que pouca gente conhece, e que muda a forma como a gente enxerga esse jogo."
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
sr = m.tts_model.sample_rate
for nome, desc in descricoes.items():
    t1 = time.time()
    ref = m.generate(text="(%s)%s" % (desc, REF_TXT))
    ref_path = "%s_%s_referencia.wav" % (saida_prefixo, nome)
    sf.write(ref_path, librosa.resample(np.asarray(ref, dtype=np.float32), orig_sr=sr, target_sr=16000), 16000)
    partes = []
    for p in paras:
        wav = m.generate(text=p, prompt_wav_path=ref_path, prompt_text=REF_TXT, reference_wav_path=ref_path)
        partes += [np.asarray(wav, dtype=np.float32), np.zeros(int(sr*0.45), dtype=np.float32)]
    audio = np.concatenate(partes)
    sf.write("%s_%s.wav" % (saida_prefixo, nome), audio, sr)
    print("%s: audio %.1fs em %.0fs" % (nome, len(audio)/sr, time.time()-t1), flush=True)
