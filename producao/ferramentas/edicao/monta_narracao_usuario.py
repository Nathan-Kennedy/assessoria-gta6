# Monta a narração do usuário a partir das gravações 4-9: escolhe takes (EDL) e corta erros/comentários.
import json, numpy as np, soundfile as sf, librosa, os
D = os.path.dirname(os.path.abspath(__file__)) + "/../narracao/usuario/"; SR = 48000
EDL = [
 # [01] GANCHO
 (4,1.10,7.74),(4,8.78,25.56),(4,25.56,35.64),(2,8.06,23.58),(4,76.58,82.42),(4,84.76,105.12),(4,111.48,116.94),"BLOCO",
 # [02] POR QUE A FLÓRIDA
 (4,141.64,165.62),(4,169.52,183.62),(4,195.36,200.10),('RAW',4,201.0,209.95),('RAW',4,218.95,220.95),('RAW',4,224.4,228.05),('RAW',4,229.75,231.95),"BLOCO",
 # [03] VICE CITY
 (4,240.72,266.72),(4,268.08,286.52),(4,297.96,301.44),(4,307.18,313.90),(4,319.06,328.44),(4,335.12,340.84),
 (2,28.14,32.40),(4,363.80,369.98),(4,376.00,380.74),(4,388.74,394.28),("CLONE","southbeach"),(4,414.62,422.04),(4,422.04,441.54),
 (5,1.46,16.78),(5,20.30,25.38),(5,27.74,33.16),(5,46.30,55.76),(5,59.62,95.78),(5,107.42,125.10),(6,0.0,6.62),
 (7,2.50,20.90),(7,30.00,33.10),(7,61.62,69.22),"BLOCO",
 # [04] KEYS
 (8,0.0,2.84),(8,11.98,12.92),(8,17.28,23.12),('RAW',2,231.45,234.9),(8,25.64,45.54),(8,68.28,83.00),(8,94.40,100.86),(8,131.32,136.14),(8,140.28,143.32),(2,111.66,117.28),
 (8,159.70,180.14),(8,181.26,192.90),('RAW',8,200.45,211.3),(2,47.94,55.90),(8,225.30,230.30),(8,240.46,242.70),(8,253.18,265.48),(8,271.60,284.36),(8,285.44,292.36),
 (8,296.80,298.44),"BLOCO",
 # [05] GRASSRIVERS
 (8,302.76,309.82),(8,337.48,347.3),(8,364.44,365.98),(2,126.20,129.10),(8,370.82,372.86),(8,382.12,385.40),('RAW',2,135.15,135.9),('RAW',8,386.0,388.3),(8,397.90,408.66),(8,409.94,414.72),
 (8,429.46,445.74),(2,172.14,176.22),(2,194.14,198.94),(8,467.82,475.00),(8,479.30,483.52),"BLOCO",
 # [06] AMBROSIA
 (8,484.86,494.90),('RAW',8,499.5,501.55),('RAW',8,507.25,513.35),(8,517.72,521.36),('RAW',2,155.45,156.1),('RAW',8,521.96,525.95),(8,536.74,543.50),(8,550.54,568.38),(8,570.92,601.66),"BLOCO",
 # [07] PORT GELLHORN
 (8,607.34,609.48),(2,68.54,79.24),(8,631.08,647.04),(8,652.34,660.10),"BLOCO",
 # [08] MOUNT KALAGA
 (8,664.22,680.90),(8,687.40,691.52),(8,693.60,694.88),(8,698.18,703.70),(8,712.94,718.82),(8,737.40,767.66),"BLOCO",
 # [09] FECHAMENTO
 (8,774.00,780.60),(8,795.92,805.24),('RAW',8,809.3,810.74),('RAW',2,135.15,135.9),('RAW',8,812.1,815.6),(8,842.14,852.94),(8,853.64,858.50),(8,859.92,867.14),(8,867.14,873.12),
 (8,873.12,877.02),(8,880.84,886.42),(8,896.10,900.18),(8,910.04,926.40),(8,939.04,942.54),(9,7.42,11.62),(9,23.60,26.46)]
aud, words = {}, {}
for i in (2,4,5,6,7,8,9):
    nm = "regrav_2" if i == 2 else "parte_%d" % i
    y,_ = librosa.load(D+nm+"_48k.wav", sr=SR, mono=True); aud[i] = y.astype(np.float32)
    words[i] = [w for s in json.load(open(D+nm+".json",encoding="utf-8")) for w in s["words"]]
z = lambda s: np.zeros(int(s*SR), np.float32)
out, log, t = [], [], 0.0
for p in EDL:
    if p == "BLOCO": out.append(z(0.6)); t += 0.6; continue
    if p[0] == "RAW":
        _,f,a,b = p; seg = aud[f][int(a*SR):int(b*SR)].copy(); log.append([round(t,2), f, a, b, "RAW"])
    elif p[0] == "CLONE":
        y,_ = librosa.load(D+"clone_%s.wav"%p[1], sr=SR); idx=np.where(np.abs(y)>0.01)[0]; y=y[idx[0]:idx[-1]]
        y *= np.sqrt(np.mean(out[-2][np.abs(out[-2])>0.01]**2)+1e-9)/np.sqrt(np.mean(y[np.abs(y)>0.01]**2)+1e-9)
        seg = y
    else:
        f,a,b = p; W = [w for w in words[f] if w["s"] >= a-0.06 and w["e"] <= b+0.3]
        s0 = max(0, W[0]["s"]-0.15); nxt = [w["s"] for w in words[f] if w["s"] > W[-1]["e"]+0.01]
        s1 = min(W[-1]["e"]+0.3, (nxt[0]-0.05) if nxt else 1e9)
        seg = aud[f][int(s0*SR):int(s1*SR)].copy()
        log.append([round(t,2), f, round(s0,2), round(s1,2), "".join(w["w"] for w in W).strip()])
    if p[0] not in ("CLONE",):  # encurta silêncios longos dentro do take
        env = np.convolve(np.abs(seg), np.ones(480)/480, "same"); thr = max(0.006, np.percentile(env, 90)*0.06)
        sil = env < thr; keep = np.ones(len(seg), bool); i = 0
        while i < len(seg):
            if sil[i]:
                j = i
                while j < len(seg) and sil[j]: j += 1
                if j - i > int(0.45*SR): keep[i+int(0.2*SR): j-int(0.15*SR)] = False
                i = j
            else: i += 1
        seg = seg[keep]
    n = min(int(0.012*SR), len(seg)//4); seg[:n] *= np.linspace(0,1,n); seg[-n:] *= np.linspace(1,0,n)
    out.append(seg); out.append(z(0.18)); t += len(seg)/SR + 0.18
y = np.concatenate(out)
sf.write(D+"NARRACAO_USUARIO_montada.wav", y, SR)
json.dump(log, open(D+"edl_log.json","w",encoding="utf-8"), ensure_ascii=False, indent=0)
print("dur %.1f s, %d trechos" % (len(y)/SR, len(log)))
