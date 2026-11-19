# Monta o diálogo final Nathan (N) + Rodrigo (R); "NR" = os dois juntos (mix). Gera outro.wav + outro.json (segmentos)
import json, numpy as np, soundfile as sf, librosa
SR = 48000
def load(p):
    # corte suave: só tira silêncio de verdade (-50 dB) e deixa 80 ms de folga nas pontas, com fade curto
    y_raw, _ = librosa.load(p, sr=SR, mono=True); _, (i0, i1) = librosa.effects.trim(y_raw, top_db=50)
    folga = int(0.08 * SR); y = y_raw[max(0, i0 - folga):min(len(y_raw), i1 + folga)].copy()
    f = int(0.012 * SR); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return (y * (0.08 / (np.sqrt(np.mean(y ** 2)) + 1e-9))).astype(np.float32)
N = lambda i: load("escolhidas/nathan/linha_%02d.wav" % i); R = lambda i: load("escolhidas/rodrigo/linha_%02d.wav" % i)
seq = [("N", [N(1)], "Fala, galera! Aqui é o Nathanzim!"), ("R", [R(1)], "Iaê, minha gente! Aqui é o Digão!"),
       ("NR", [N(2), R(2)], "E amanhã estaremos jogando GTA 6!"), ("R", [R(3)], "Teremos gameplay no canal!"),
       ("N", [N(3)], "E vamos explorar até a última gota desse jogo!"), ("R", [R(4)], "Aqui a gente vai entregar só conteúdo de qualidade, parceiro!"),
       ("N", [N(4)], "Então inscreva-se pra não perder nada, e ativa o sininho!"), ("R", [R(5)], "Acompanha nossa jornada nesse jogão imenso de bom!"),
       ("N", [N(5)], "Valeu, galera!"), ("R", [R(6)], "Até amanhã em Leonida!"), ("NR", [N(6), R(7)], "Falou!")]
out, segs, t = [], [], 0.0
for quem, vs, txt in seq:
    n = max(len(v) for v in vs); m = np.zeros(n, np.float32)
    for v in vs: m[:len(v)] += v * (0.75 if len(vs) > 1 else 1.0)
    segs.append({"quem": quem, "t0": round(t, 3), "t1": round(t + n / SR, 3), "texto": txt})
    out += [m, np.zeros(int(0.22 * SR), np.float32)]; t += n / SR + 0.22
a = np.concatenate(out); a *= 0.9 / (np.max(np.abs(a)) + 1e-9) if np.max(np.abs(a)) > 0.9 else 1.0
sf.write("outro.wav", a, SR); json.dump(segs, open("outro.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("outro %.1f s, %d falas" % (len(a) / SR, len(segs)))
