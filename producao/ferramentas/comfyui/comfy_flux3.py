# -*- coding: utf-8 -*-
"""FLUX 3 Image Klein (int8) no ComfyUI local, edicao com ate 4 imagens de referencia (workflow oficial flux3_klein_int8_mi2i).
Licenca FLUX Kommunity: uso comercial das saidas liberado para Qualifying User (< US$ 5 mi/ano), com revisao das imagens
e aviso de IA quando a lei exigir; PROIBIDO usar as saidas para treinar/melhorar outra IA. Ver workflows/FLUX3_KOMMUNITY_LICENSE.md.

Uso: python comfy_flux3.py <saida.png> <prompt.txt> <img1> [img2 img3 img4] [--w 960 --h 1200 --passos 16 --seed 7 --validar]
"""
import json, os, sys, time, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comfy_look import upload, post, mem, gpu_c, URL, COMMIT_MIN_GB, GPU_MAX_C, TEMPO_MAX_S

def arg(op, padrao):
    return sys.argv[sys.argv.index(op) + 1] if op in sys.argv else padrao

def workflow(prompt, imgs, w, h, passos, seed):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux3-image-klein-int8-convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_int8_convrot.safetensors", "type": "flux3", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "4": {"class_type": "ModelSamplingFlux", "inputs": {"model": ["1", 0], "max_shift": 2.77259, "base_shift": 2.77259, "width": 1024, "height": 1024}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "8": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "9": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["7", 0], "negative": ["7", 1], "latent_image": ["8", 0],
              "seed": seed, "steps": passos, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["3", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "missangel/flux3"}},
    }
    rml = {"positive": ["5", 0], "negative": ["6", 0], "vae": ["3", 0], "resolution": "resize", "resolution.megapixels": 1.0}
    for i, nome in enumerate(imgs, 1):
        wf["2%d" % i] = {"class_type": "LoadImage", "inputs": {"image": nome}}
        rml["images.image%d" % i] = ["2%d" % i, 0]
    wf["7"] = {"class_type": "ReferenceMultiLatent", "inputs": rml}
    return wf

def main():
    pos = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and not sys.argv[i - 1].startswith("--")]
    saida, ptxt, imgs = pos[0], pos[1], pos[2:6]
    prompt = open(ptxt, encoding="utf-8").read().strip()
    nomes = [upload(x) for x in imgs]
    wf = workflow(prompt, nomes, int(arg("--w", 960)), int(arg("--h", 1200)), int(arg("--passos", 16)), int(arg("--seed", 7)))
    try:
        r = json.load(post("/prompt", {"prompt": wf}))
    except urllib.error.HTTPError as e:
        raise SystemExit("VALIDACAO FALHOU: " + e.read().decode("utf-8", "replace")[:1500])
    pid = r["prompt_id"]
    if "--validar" in sys.argv:
        post("/queue", {"delete": [pid]}); print("VALIDO (retirado da fila)", pid); return
    t0 = time.time(); pico = {"commit": 99, "gpu": 0}
    while True:
        m = mem(); com, g = m.ullAvailPageFile / 2**30, gpu_c()
        pico["commit"] = min(pico["commit"], com); pico["gpu"] = max(pico["gpu"], g)
        if com < COMMIT_MIN_GB or g > GPU_MAX_C or time.time() - t0 > TEMPO_MAX_S:
            try: post("/interrupt", {}); post("/free", {"unload_models": True, "free_memory": True})
            except Exception: pass
            raise SystemExit("PARADO pelo vigia: commit livre %.1f GB, GPU %d C, %d s" % (com, g, time.time() - t0))
        h = json.load(urllib.request.urlopen(URL + "/history/" + pid))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise SystemExit("ERRO " + json.dumps(st.get("messages", [])[-1:], ensure_ascii=False)[:900])
            for no in h[pid]["outputs"].values():
                for im in no.get("images", []):
                    q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im["subfolder"], "type": im["type"]})
                    open(saida, "wb").write(urllib.request.urlopen(URL + "/view?" + q).read())
                    print("OK %s %d s · commit livre min %.1f GB · GPU max %d C" % (saida, time.time() - t0, pico["commit"], pico["gpu"]), flush=True)
                    post("/free", {"unload_models": True, "free_memory": True})
                    return
            raise SystemExit("sem imagem na saida")
        time.sleep(3)

if __name__ == "__main__":
    main()
