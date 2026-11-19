# -*- coding: utf-8 -*-
"""Veste uma modelo oficial com um look no ComfyUI local (Qwen-Image-Edit 2511 GGUF + Lightning 4 passos).
Base: receita do Casa3D (projetos/casa-sirius/scripts/e05_comfy_fachadas.py), com o vigia de RAM/commit/GPU.

Uso: python comfy_look.py <saida.png> <prompt.txt> <img1_corpo> <img2_look> [img3_rosto] [--seed N] [--passos N] [--unet ARQ]
  img1 = corpo da modelo (vira a base da imagem: trava corpo, enquadramento e proporcao)
  img2 = foto do look (roupa, bolsa, fundo)  ·  img3 = rosto de perto da modelo (identidade)
"""
import ctypes, json, os, subprocess, sys, time, uuid, urllib.request, urllib.parse

URL = "http://127.0.0.1:8188"
COMMIT_MIN_GB, GPU_MAX_C, TEMPO_MAX_S = 6.0, 85, 2400

def arg(op, padrao):
    return sys.argv[sys.argv.index(op) + 1] if op in sys.argv else padrao

UNET = arg("--unet", "qwen-image-edit-2511-Q3_K_M.gguf")
TE = "Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf"
LORA = arg("--lora", "Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors")  # --lora nenhuma = qualidade maxima
CFG = float(arg("--cfg", 1.0))

class _Mem(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

def mem():
    m = _Mem(); m.dwLength = ctypes.sizeof(_Mem); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); return m

def gpu_c():
    try: return int(subprocess.check_output(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"], timeout=5).split()[0])
    except Exception: return 0

def post(rota, dados):
    return urllib.request.urlopen(urllib.request.Request(URL + rota, json.dumps(dados).encode(), {"Content-Type": "application/json"}))

def upload(caminho):
    nome = "mal_" + os.path.basename(caminho).replace(" ", "_")
    b = uuid.uuid4().hex
    corpo = (("--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/png\r\n\r\n" % (b, nome)).encode()
             + open(caminho, "rb").read() + ("\r\n--%s\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--%s--\r\n" % (b, b)).encode())
    return json.load(urllib.request.urlopen(urllib.request.Request(URL + "/upload/image", corpo, {"Content-Type": "multipart/form-data; boundary=" + b})))["name"]

def workflow(prompt, imgs, seed, passos):
    w = {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": UNET}},
        "2": {"class_type": "CLIPLoaderGGUF", "inputs": {"clip_name": TE, "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "9": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.1}},
        "10": {"class_type": "CFGNorm", "inputs": {"model": ["9", 0], "strength": 1.0}},
    }
    if LORA != "nenhuma":
        w["15"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["10", 0], "lora_name": LORA, "strength_model": 1.0}}
    pos = {"clip": ["2", 0], "prompt": prompt, "vae": ["3", 0]}
    neg = {"clip": ["2", 0], "prompt": "", "vae": ["3", 0]}
    for i, nome in enumerate(imgs, 1):
        w["4%d" % i] = {"class_type": "LoadImage", "inputs": {"image": nome}}
        w["5%d" % i] = {"class_type": "FluxKontextImageScale", "inputs": {"image": ["4%d" % i, 0]}}
        pos["image%d" % i] = ["5%d" % i, 0]; neg["image%d" % i] = ["5%d" % i, 0]
    w["6"] = {"class_type": "TextEncodeQwenImageEditPlus", "inputs": pos}
    w["7"] = {"class_type": "TextEncodeQwenImageEditPlus", "inputs": neg}
    w["16"] = {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["6", 0], "reference_latents_method": "index_timestep_zero"}}
    w["17"] = {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["7", 0], "reference_latents_method": "index_timestep_zero"}}
    w["8"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["51", 0], "vae": ["3", 0]}}
    w["11"] = {"class_type": "KSampler", "inputs": {"model": ["15", 0] if LORA != "nenhuma" else ["10", 0], "positive": ["16", 0], "negative": ["17", 0], "latent_image": ["8", 0],
               "seed": seed, "steps": passos, "cfg": CFG, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}}
    w["12"] = {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}}
    w["13"] = {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": "missangel/look"}}
    return w

def main():
    pos_args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and not sys.argv[i - 1].startswith("--")]
    saida, ptxt, imgs = pos_args[0], pos_args[1], pos_args[2:5]
    prompt = open(ptxt, encoding="utf-8").read().strip()
    seed, passos = int(arg("--seed", 7)), int(arg("--passos", 4))
    nomes = [upload(x) for x in imgs]
    pid = json.load(post("/prompt", {"prompt": workflow(prompt, nomes, seed, passos)}))["prompt_id"]
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
