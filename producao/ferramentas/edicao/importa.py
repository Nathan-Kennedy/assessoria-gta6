# Importa no projeto-base do video 02 as artes, o trailer Pre-Load e memes extras; grava ids em scripts/itens.json
import json, subprocess, os, glob
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = r"C:\deps\effectcraft\0.16.0\effectcraft-0.16.0-windows-x64-portable\effectcraft-cli.exe"
V1 = os.path.join(os.path.dirname(B), "2026-11-13_video01-lugares-gta6")
JA = json.load(open(os.path.join(B, "scripts/itens.json")))
A = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(B, "assets/graficos/*.png")) if not os.path.basename(p).startswith("_")}
A["thumb_v01"] = os.path.join(V1, "thumbnail/thumb_A_comparacao.jpg")
for k in ("img_travolta_confuso.jpg", "img_monkey_puppet.jpg", "img_mulher_gritando_com_gato.jpg"): A[k[:-4]] = os.path.join(V1, "assets/memes/imagens", k)
A["preload"] = os.path.join(os.path.dirname(B), "_ferramentas/gta6-footage/trailers-oficiais-rockstar/20261110 - Grand Theft Auto VI： Pre-Load Now [_yl5ELcmugI].mp4")
for k in ("doge_bonk", "gato_gritando", "reacao_gretchen_dancando", "gato_vibing", "cachorro_sorrindo", "reacao_bob_esponja_imaginacao"):
    A[k] = os.path.join(V1, "assets/memes/reacoes/%s.mp4" % k)
for p in glob.glob(os.path.join(B, "motion/out/[RC][0-9]*.mp4")): A[os.path.splitext(os.path.basename(p))[0]] = p
for p in glob.glob(os.path.join(B, "motion/out/v2/*.mp4")): A[os.path.splitext(os.path.basename(p))[0]] = p
for p in glob.glob(os.path.join(B, "motion/out/v3/*.mp4")): A[os.path.splitext(os.path.basename(p))[0]] = p
A = {k: p for k, p in A.items() if k not in JA}
for k, p in A.items(): assert os.path.exists(p), p
js = "var r={};\n" + "".join("var it=app.project.importFile(new ImportOptions(new File('%s'))); r['%s']=[it.id,it.width,it.height,it.duration||0];\n"
      % (p.replace("\\", "/"), k) for k, p in A.items()) + "JSON.stringify(r)"
open(os.path.join(B, "scripts/importa.jsx"), "w", encoding="utf-8").write(js)
dst = os.path.join(B, "edicao/video03_base.ecproj")
out = subprocess.run([CLI, "script", os.path.join(B, "scripts/importa.jsx"), dst, "--save"], capture_output=True, text=True, encoding="utf-8")
print(out.stderr[-1500:])
txt = out.stdout.strip().splitlines()[0].strip()
r = json.loads(json.loads(txt) if txt.startswith('"') else txt)
JA.update(r); json.dump(JA, open(os.path.join(B, "scripts/itens.json"), "w"), indent=1); print(r)
