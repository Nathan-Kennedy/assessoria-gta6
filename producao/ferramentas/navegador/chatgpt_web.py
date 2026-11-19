# -*- coding: utf-8 -*-
"""Gera uma imagem no ChatGPT web (GPT Image) pelo Opera GX (CDP na porta 9333). Um chat novo por imagem.
Uso: python chatgpt_web.py <saida.png> <prompt.txt> [anexo1 anexo2 ...]
O link do chat fica em <saida>_chat.txt. Tempo maximo: CHATGPT_ESPERA (s, padrao 420).
"""
import sys, os, time, json, base64, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp_aba import Aba

BASE = "http://127.0.0.1:9333/json/"
SAIDA, PROMPT, ANEXOS = os.path.abspath(sys.argv[1]), sys.argv[2], [os.path.abspath(x) for x in sys.argv[3:]]
for x in ANEXOS:
    if not os.path.isfile(x): raise SystemExit("anexo nao existe: " + x)
texto = open(PROMPT, encoding="utf-8").read().strip()
ESPERA = int(os.environ.get("CHATGPT_ESPERA", "420"))

# imagens geradas ficam na resposta do assistente; os anexos ficam na mensagem do usuario
JS_IMGS = """[...document.querySelectorAll('[data-message-author-role=assistant] img, div[id^=image-] img, img[alt*="gerada"], img[alt*="Generated"]')]
  .filter(i => i.naturalWidth >= 512 && !i.closest('[data-message-author-role=user]')).map(i => i.src)"""
JS_PARANDO = "!!document.querySelector('button[data-testid=stop-button], button[aria-label*=\"Parar\"], button[aria-label*=\"Stop\"]')"
JS_ENVIAR = "document.querySelector('button[data-testid=send-button], button#composer-submit-button, button[aria-label=Enviar], button[aria-label=\\\"Send prompt\\\"]')"

def espera(a, js, seg):
    t0 = time.time()
    while time.time() - t0 < seg:
        v = a.js(js)
        if v: return v
        time.sleep(1)
    return None

def main():
    t = json.load(urllib.request.urlopen(urllib.request.Request(BASE + "new?https://chatgpt.com/", method="PUT")))
    a = Aba(t)
    try:
        a.cmd("Emulation.setDeviceMetricsOverride", width=1280, height=900, deviceScaleFactor=1, mobile=False)
        a.cmd("Page.enable"); a.cmd("DOM.enable")
        if not espera(a, "!!document.querySelector('#prompt-textarea, .ProseMirror')", 90): raise RuntimeError("campo do prompt nao apareceu (login?)")
        time.sleep(2)
        if ANEXOS:
            doc = a.cmd("DOM.getDocument", depth=-1, pierce=True)["root"]["nodeId"]
            ids = a.cmd("DOM.querySelectorAll", nodeId=doc, selector='input[type="file"]').get("nodeIds", [])
            alvo = None
            for nid in ids:  # prefere o input generico (sem accept) ou o de imagem
                at = a.cmd("DOM.getAttributes", nodeId=nid).get("attributes", [])
                d = dict(zip(at[::2], at[1::2]))
                if "video" not in d.get("accept", ""):
                    alvo = nid
                    if not d.get("accept"): break
            if not alvo: raise RuntimeError("input de arquivo nao encontrado")
            a.cmd("DOM.setFileInputFiles", files=ANEXOS, nodeId=alvo)
            # espera as previas subirem (o botao de enviar so habilita depois do upload)
            time.sleep(6)
        a.js("document.querySelector('#prompt-textarea, .ProseMirror').focus()")
        a.cmd("Input.insertText", text=texto); time.sleep(1.5)
        js_ok = "(()=>{const b=%s; return !!(b && !b.disabled)})()" % JS_ENVIAR
        if not espera(a, js_ok, 180): raise RuntimeError("botao de enviar nao habilitou")
        a.js(JS_ENVIAR + ".click()")
        print(os.path.basename(SAIDA), "enviado com", len(ANEXOS), "anexos", flush=True)
        t0 = time.time(); ultimo = None; estavel = 0
        while time.time() - t0 < ESPERA:
            time.sleep(6)
            srcs = a.js(JS_IMGS) or []
            if srcs and not a.js(JS_PARANDO):
                estavel = estavel + 1 if srcs[-1] == ultimo else 0
                ultimo = srcs[-1]
                if estavel >= 2: break
        else:
            open(SAIDA[:-4] + "_chat.txt", "w").write(a.js("location.href") or "")
            print("SEM IMAGEM (%d s)" % ESPERA, flush=True)
            print((a.js("[...document.querySelectorAll('[data-message-author-role=assistant]')].pop()?.innerText.slice(-500)") or ""), flush=True)
            return 1
        # baixa o arquivo original pela URL da imagem (com os cookies da pagina)
        b64 = a.js("""(async()=>{const r=await fetch(%s,{credentials:'include'}); const b=await r.blob();
            return await new Promise(ok=>{const f=new FileReader(); f.onload=()=>ok(f.result); f.readAsDataURL(b);});})()""" % json.dumps(ultimo))
        if not b64: raise RuntimeError("nao consegui baixar a imagem")
        cab, dados = b64.split(",", 1)
        ext = ".png" if "png" in cab else ".webp" if "webp" in cab else ".jpg"
        saida_f = os.path.splitext(SAIDA)[0] + ext
        open(saida_f, "wb").write(base64.b64decode(dados))
        open(SAIDA[:-4] + "_chat.txt", "w").write(a.js("location.href") or "")
        print("OK", saida_f, round(time.time() - t0), "s", flush=True)
        return 0
    finally:
        try: a.ws.close()
        except Exception: pass
        try: urllib.request.urlopen(BASE + "close/" + t["id"])
        except Exception: pass

if __name__ == "__main__":
    sys.exit(main())
