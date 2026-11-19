"""Gera musica instrumental com ACE-Step 1.5 Turbo pelo ComfyUI (API HTTP em 127.0.0.1:8188).

Modelos em ComfyUI-Shared/models (Comfy-Org/ace_step_1.5_ComfyUI_files): diffusion_models/acestep_v1.5_turbo,
text_encoders/qwen_0.6b_ace15 + qwen_1.7b_ace15, vae/ace_1.5_vae. Fluxo = template oficial
audio_ace_step_1_5_split.json. Licenca do modelo: Apache-2.0 (ACE-Step/Ace-Step1.5).
Uso: python gerar_musica_ace.py <saida.flac> <segundos> <bpm> "<tom>" <seed> "<tags>"
"""
import json, os, shutil, sys, time, urllib.request

API = "http://127.0.0.1:8188"
OUT_COMFY = os.path.join(os.environ["LOCALAPPDATA"], "Comfy-Desktop", "ComfyUI-Shared", "output")
saida, seg, bpm, tom, seed, tags = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6]

wf = {
    "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "acestep_v1.5_turbo.safetensors", "weight_dtype": "default"}},
    "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "qwen_0.6b_ace15.safetensors",
                                                     "clip_name2": "qwen_1.7b_ace15.safetensors", "type": "ace", "device": "default"}},
    "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ace_1.5_vae.safetensors"}},
    "4": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3}},
    "5": {"class_type": "TextEncodeAceStepAudio1.5", "inputs": {
        "clip": ["2", 0], "tags": tags, "lyrics": "[Instrumental]", "seed": seed, "bpm": bpm, "duration": seg,
        "timesignature": "4", "language": "en", "keyscale": tom, "generate_audio_codes": True,
        "cfg_scale": 2.0, "temperature": 0.85, "top_p": 0.9, "top_k": 0, "min_p": 0.0}},
    "6": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["5", 0]}},
    "7": {"class_type": "EmptyAceStep1.5LatentAudio", "inputs": {"seconds": seg, "batch_size": 1}},
    "8": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0],
                                               "latent_image": ["7", 0], "seed": seed, "steps": 8, "cfg": 1.0,
                                               "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
    "9": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
    "10": {"class_type": "SaveAudio", "inputs": {"audio": ["9", 0], "filename_prefix": "videos/musica_s%d" % seed}},
}

req = urllib.request.Request(API + "/prompt", json.dumps({"prompt": wf}).encode(), {"Content-Type": "application/json"})
pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
t0 = time.time()
while True:
    h = json.loads(urllib.request.urlopen(API + "/history/" + pid).read())
    if pid in h and h[pid].get("status", {}).get("completed") is not None:
        break
    time.sleep(2)
st = h[pid]["status"]
if not st.get("completed"):
    print(json.dumps(st, ensure_ascii=False)[:3000]); sys.exit(1)
f = h[pid]["outputs"]["10"]["audio"][0]
shutil.copy(os.path.join(OUT_COMFY, f["subfolder"], f["filename"]), saida)
json.dump({"modelo": "ACE-Step 1.5 Turbo (Comfy-Org repackaged), Apache-2.0", "tags": tags, "bpm": bpm, "tom": tom,
           "seed": seed, "segundos": seg}, open(os.path.splitext(saida)[0] + ".json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("ok", saida, "%.0fs" % (time.time() - t0))
