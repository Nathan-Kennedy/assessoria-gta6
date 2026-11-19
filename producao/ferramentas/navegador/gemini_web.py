# -*- coding: utf-8 -*-
"""Gera uma imagem no Gemini web (Nano Banana Pro) pelo Opera GX (CDP na porta 9333).
Um chat novo por imagem. Uso:
  python gemini_web.py <saida.png> <prompt.txt> [anexo1.png anexo2.png ...]
O link do chat fica em <saida>_chat.txt.
"""
import sys, os, time, json, base64, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp_aba import Aba

BASE = "http://127.0.0.1:9333/json/"
SAIDA, PROMPT, ANEXOS = os.path.abspath(sys.argv[1]), sys.argv[2], [os.path.abspath(x) for x in sys.argv[3:]]
for x in ANEXOS:
    if not os.path.isfile(x): raise SystemExit("anexo nao existe: " + x)
texto = open(PROMPT, encoding="utf-8").read().strip()

JS_IMGS = """[...document.querySelectorAll('generated-image img, single-image img, .generated-image img, img.image')]
  .filter(i => i.naturalWidth > 400 && !i.closest('rich-textarea') && !i.closest('uploader-file-preview, .file-preview-container'))
  .map(i => i.src)"""
JS_PARANDO = "!!document.querySelector('button[aria-label*=\"Parar\"], button[aria-label*=\"Stop\"], .stop-icon')"

def espera(a, js, seg):
    t0 = time.time()
    while time.time() - t0 < seg:
        v = a.js(js)
        if v: return v
        time.sleep(1)
    return None

# indice da conta Google no Opera (u/N). No notebook a conta nathan.sarlie e a u/4; mude com GEMINI_CONTA.
CONTA = os.environ.get("GEMINI_CONTA", "4")

def modo_pro(a):
    """Escolhe o modo Pro (Nano Banana Pro). Se nao houver, fica no melhor disponivel e avisa."""
    a.js("document.querySelector('button[aria-label^=\"Abrir seletor de modo\"]')?.click()"); time.sleep(1.5)
    js = """(()=>{const it=[...document.querySelectorAll('[role=menuitem],[role=menuitemradio],[role=option]')];
      const ok=it.filter(e=>e.getAttribute('aria-disabled')!='true'&&!e.disabled);
      const alvo=ok.find(e=>/[0-9.]+ *Pro/.test(e.textContent))||ok.find(e=>/Flash(?!.*Lite)/.test(e.textContent));
      if(!alvo) return null; alvo.click(); return alvo.textContent.trim().replace(/\s+/g,' ');})()"""
    v = a.js(js); time.sleep(1.5)
    atual = a.js("document.querySelector('button[aria-label^=\"Abrir seletor de modo\"]')?.textContent.trim()")
    print("modo:", atual or v, "" if (atual and "Pro" in atual) else "(AVISO: sem Pro, usando outro)", flush=True)

TRAVA = os.path.join(os.environ.get("TEMP", "."), "gemini_web.lock")

def main():
    # o Browser.setDownloadBehavior vale para o navegador todo: duas execucoes em paralelo trocam os arquivos.
    # Esta trava faz cada execucao esperar a anterior terminar.
    while True:
        try:
            fd = os.open(TRAVA, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.close(fd); break
        except FileExistsError:
            if time.time() - os.path.getmtime(TRAVA) > 900: os.remove(TRAVA); continue
            time.sleep(3)
    try:
        return _main()
    finally:
        try: os.remove(TRAVA)
        except OSError: pass

def _main():
    t = json.load(urllib.request.urlopen(urllib.request.Request(BASE + "new?https://gemini.google.com/u/%s/images" % CONTA, method="PUT")))
    a = Aba(t)
    try:
        a.cmd("Emulation.setDeviceMetricsOverride", width=1280, height=900, deviceScaleFactor=1, mobile=False)
        a.cmd("Page.enable"); a.cmd("DOM.enable")
        if not espera(a, "!!document.querySelector('.ql-editor')", 90): raise RuntimeError("campo do prompt nao apareceu")
        time.sleep(3)
        modo_pro(a)
        if ANEXOS:
            # o input de arquivo so existe depois de abrir o menu "+"
            a.js("document.querySelector('button[aria-label=\"Envio e ferramentas\"]')?.click()"); time.sleep(1.5)
            a.js("[...document.querySelectorAll('button,[role=menuitem]')].find(b=>/Enviar arquivos|Upload files|Fazer upload/i.test(b.innerText||b.getAttribute('aria-label')||''))?.click()"); time.sleep(1.5)
            doc = a.cmd("DOM.getDocument", depth=-1, pierce=True)["root"]["nodeId"]
            nid = a.cmd("DOM.querySelector", nodeId=doc, selector='input[type="file"]').get("nodeId")
            if not nid: raise RuntimeError("input de arquivo nao encontrado")
            a.cmd("DOM.setFileInputFiles", files=ANEXOS, nodeId=nid)
            a.cmd("Input.dispatchKeyEvent", type="keyDown", key="Escape"); a.cmd("Input.dispatchKeyEvent", type="keyUp", key="Escape")
            ok = espera(a, "document.querySelectorAll('uploader-file-preview, .file-preview-container img, [data-test-id*=file-preview]').length >= %d" % len(ANEXOS), 90)
            if not ok: print("aviso: nao confirmei a previa dos anexos", flush=True)
            time.sleep(4)
        a.js("document.querySelector('.ql-editor').focus()")
        a.cmd("Input.insertText", text=texto); time.sleep(1.5)
        js_env = "(()=>{const b=document.querySelector('button[aria-label*=\"Enviar\"], button.send-button, button[aria-label*=\"Send\"]'); return !!(b && !b.disabled && b.getAttribute('aria-disabled')!='true')})()"
        if not espera(a, js_env, 120): raise RuntimeError("botao de enviar nao habilitou")
        a.js("document.querySelector('button[aria-label*=\"Enviar\"], button.send-button, button[aria-label*=\"Send\"]').click()")
        print(os.path.basename(SAIDA), "enviado com", len(ANEXOS), "anexos", flush=True)
        t0 = time.time(); ultimo = None
        while time.time() - t0 < int(os.environ.get("GEMINI_ESPERA", "600")):
            time.sleep(8)
            srcs = a.js(JS_IMGS) or []
            if srcs and not a.js(JS_PARANDO):
                if srcs[-1] == ultimo: break
                ultimo = srcs[-1]
        else:
            open(SAIDA[:-4] + "_chat.txt", "w").write(a.js("location.href") or "")
            print("SEM IMAGEM (%s s)" % os.environ.get("GEMINI_ESPERA", "600"), flush=True)
            print((a.js("document.querySelector('main')?.innerText.slice(-600)") or ""), flush=True)
            return 1
        # baixa no tamanho original pelo botao do Gemini (o blob da pagina e so a previa)
        import glob, shutil, tempfile
        from websockets.sync.client import connect
        tmp = tempfile.mkdtemp(prefix="gem_dl_")
        bws = json.load(urllib.request.urlopen(BASE + "version"))["webSocketDebuggerUrl"]
        bw = connect(bws, max_size=None)
        bw.send(json.dumps({"id": 1, "method": "Browser.setDownloadBehavior", "params": {"behavior": "allow", "downloadPath": tmp, "eventsEnabled": True}})); bw.recv()
        time.sleep(2)
        a.js("[...document.querySelectorAll('button')].filter(b=>/tamanho original|full size/i.test(b.getAttribute('aria-label')||'')).pop().click()")
        f = []
        for _ in range(90):
            f = [x for x in glob.glob(tmp + "/*") if not x.endswith(".crdownload")]
            if f: break
            time.sleep(1)
        bw.close()
        if not f: raise RuntimeError("download nao chegou")
        ext = os.path.splitext(f[0])[1].lower() or ".jpg"
        SAIDA_F = os.path.splitext(SAIDA)[0] + ext
        shutil.move(f[0], SAIDA_F)
        open(SAIDA[:-4] + "_chat.txt", "w").write(a.js("location.href") or "")
        print("OK", SAIDA_F, round(time.time() - t0), "s", flush=True)
        return 0
    finally:
        try: a.ws.close()
        except Exception: pass
        try: urllib.request.urlopen(BASE + "close/" + t["id"])
        except Exception: pass

if __name__ == "__main__":
    sys.exit(main())
