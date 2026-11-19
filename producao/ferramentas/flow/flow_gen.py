"""Digita o prompt no Flow, gera e espera o vídeo; baixa para o caminho de saída.
Uso: python flow_gen.py <prompt.txt> <saida.mp4>"""
import sys, time, base64
from flow import *

prompt = open(sys.argv[1], encoding='utf-8').read().strip()
saida = sys.argv[2]
a = aba()
antes = a.js('[...document.querySelectorAll("video")].map(v=>v.currentSrc||v.src).filter(Boolean)') or []
a.js('(()=>{const e=[...document.querySelectorAll("[contenteditable=true]")].find(x=>x.offsetParent!==null);e.focus();return 1})()')
a.cmd('Input.insertText', text=prompt)
time.sleep(1.5)
print('enviar:', a.js('(()=>{const b=document.querySelector("[aria-label=\'Iniciar geração\']");if(!b||b.disabled)return "desabilitado";b.click();return "ok"})()'), flush=True)
t0 = time.time(); src = None
while time.time() - t0 < 600:
    time.sleep(8)
    vids = a.js('[...document.querySelectorAll("video")].map(v=>v.currentSrc||v.src).filter(Boolean)') or []
    novos = [v for v in vids if v not in antes]
    if novos:
        src = novos[0]; break
    falha = a.js('(()=>{const t=document.body.innerText;const m=t.match(/(não foi possível|falha|failed|violat|política|policy)[^\\n]{0,120}/i);return m?m[0]:null})()')
    if falha and time.time() - t0 > 30:
        print('aviso:', falha, flush=True)
print('tempo:', int(time.time() - t0), 's · src:', (src or '')[:80], flush=True)
shot(a, 'flow_gen.jpg')
if src:
    d = a.js('(async()=>{const r=await fetch(' + repr(src).replace("'", '"') + ');const b=await r.blob();return await new Promise(ok=>{const f=new FileReader();f.onload=()=>ok(f.result);f.readAsDataURL(b)})})()')
    if d:
        open(saida, 'wb').write(base64.b64decode(d.split(',', 1)[1]))
        print('salvo', saida)
    else:
        print('não consegui baixar pelo fetch')
