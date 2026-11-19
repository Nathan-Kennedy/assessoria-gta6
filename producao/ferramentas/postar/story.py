# Posta uma imagem como story no Instagram simulando celular (mobile web), tudo numa conexão CDP só.
import sys, time, base64, json
sys.path.insert(0, r"C:\Projetos Dev\Roupas\modelos-ia\scripts")
from cdp_aba import Aba, abas
IMG, PREF = sys.argv[1], sys.argv[2]
a = Aba(abas("instagram.com")[0])
def shot(n):
    r = a.cmd("Page.captureScreenshot", format="png"); open(f"{PREF}_{n}.png", "wb").write(base64.b64decode(r["data"]))
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
a.cmd("Network.enable"); a.cmd("Network.setUserAgentOverride", userAgent=UA, platform="iPhone")
a.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True, screenWidth=390, screenHeight=844, screenOrientation={"type": "portraitPrimary", "angle": 0})
a.cmd("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
a.cmd("Page.navigate", url="https://www.instagram.com/"); time.sleep(8); shot(1)
acc = a.js("[...document.querySelectorAll('input[type=file]')].map(e=>e.accept)")
print("inputs", acc)
idx = next((i for i, x in enumerate(acc or []) if x and "video" not in x), None)
if idx is None: print("sem input de story"); sys.exit(1)
doc = a.cmd("DOM.getDocument", depth=-1, pierce=True)["root"]["nodeId"]
nodes = a.cmd("DOM.querySelectorAll", nodeId=doc, selector="input[type=file]")["nodeIds"]
a.cmd("DOM.setFileInputFiles", nodeId=nodes[idx], files=[IMG]); time.sleep(7); shot(2)
print("botoes", a.js("[...document.querySelectorAll('button, div[role=button], a')].map(e=>(e.getAttribute('aria-label')||e.innerText||'').trim()).filter(Boolean).slice(0,40)"))
r = a.js("""(async()=>{ const b=[...document.querySelectorAll('button, div[role=button], span')].find(e=>/^(Adicionar ao seu story|Seu story|Compartilhar no story|Add to your story|Your story)$/i.test((e.innerText||'').trim()));
 if(!b) return 'sem botao'; (b.closest('button,div[role=button]')||b).click(); await new Promise(r=>setTimeout(r,9000)); return 'clicou '+location.href; })()""")
print(r); shot(3)
a.cmd("Emulation.clearDeviceMetricsOverride"); a.cmd("Network.setUserAgentOverride", userAgent="")
