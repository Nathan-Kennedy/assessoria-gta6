# -*- coding: utf-8 -*-
"""MOSS-Image (SFT int8) + edit LoRA no ComfyUI local, com ate 4 imagens de referencia (template oficial image_moss_image_edit).
Licenca Apache-2.0. Precisa do ComfyUI 0.43+ (TextEncodeMOSSImageEdit).

Uso: python comfy_moss.py <saida.png> <prompt.txt> <img1> [img2 img3 img4] [--w 896 --h 1152 --passos 30 --cfg 4 --seed 42 --ref-mp 0.5 --validar]
(--ref-mp: megapixels de cada referencia; 1.0 estoura os 8 GB da RTX 4060 com 3 refs)
"""
import json, os, sys, time, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comfy_look import upload, post, mem, gpu_c, URL, COMMIT_MIN_GB, GPU_MAX_C, TEMPO_MAX_S

NEGATIVO = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

def arg(op, padrao):
    return sys.argv[sys.argv.index(op) + 1] if op in sys.argv else padrao

def workflow(prompt, imgs, w, h, passos, cfg, seed, ref_mp=0.5):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "moss_image_sft_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "moss_image_edit_lora_rank_64_bf16.safetensors", "strength_model": 1.0}},
        "3": {"class_type": "SkipLayerGuidanceDiTSimple", "inputs": {"model": ["2", 0], "double_layers": "", "single_layers": "22", "start_percent": 0.0, "end_percent": 1.0}},
        "4": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3.5_9b_w4a8_gptq.safetensors", "type": "moss_image", "device": "default"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "flux2-vae_small.safetensors"}},
        "8": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "9": {"class_type": "KSampler", "inputs": {"model": ["3", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["8", 0],
              "seed": seed, "steps": passos, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["5", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "missangel/moss"}},
    }
    pos = {"clip": ["4", 0], "prompt": prompt, "edit_format": "Moss-Image-Edit", "image_strength": 1.0, "vae": ["5", 0]}
    neg = dict(pos, prompt=NEGATIVO)
    for i, nome in enumerate(imgs):
        wf["2%d" % i] = {"class_type": "LoadImage", "inputs": {"image": nome}}
        wf["3%d" % i] = {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["2%d" % i, 0], "upscale_method": "lanczos", "megapixels": ref_mp, "resolution_steps": 16}}
        pos["images.image_%d" % i] = ["3%d" % i, 0]; neg["images.image_%d" % i] = ["3%d" % i, 0]
    wf["6"] = {"class_type": "TextEncodeMOSSImageEdit", "inputs": pos}
    wf["7"] = {"class_type": "TextEncodeMOSSImageEdit", "inputs": neg}
    return wf

def main():
    pos = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and not sys.argv[i - 1].startswith("--")]
    saida, ptxt, imgs = pos[0], pos[1], pos[2:6]
    prompt = open(ptxt, encoding="utf-8").read().strip()
    nomes = [upload(x) for x in imgs]
    wf = workflow(prompt, nomes, int(arg("--w", 896)), int(arg("--h", 1152)), int(arg("--passos", 30)), float(arg("--cfg", 4.0)), int(arg("--seed", 42)), float(arg("--ref-mp", 0.5)))
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
