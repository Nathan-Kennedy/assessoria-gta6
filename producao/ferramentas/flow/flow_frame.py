"""Coloca uma imagem como primeiro quadro no Flow. Uso: python flow_frame.py <imagem>"""
import sys, os, time
from flow import *
from flow_up import enviar_arquivo
img = sys.argv[1]; nome = os.path.splitext(os.path.basename(img))[0][:18]
a = aba()
# limpa um primeiro quadro anterior, se houver
if not a.js('[...document.querySelectorAll("button")].some(e=>/Enviar mídia/.test(e.innerText))'):
    clicar_txt(a, 'Início'); time.sleep(2)
js = '(()=>{const b=[...document.querySelectorAll("button")].find(e=>/Enviar mídia/.test(e.innerText));b.click();return 1})()'
print('envio:', enviar_arquivo(a, img, js), flush=True)
for i in range(30):
    time.sleep(2)
    ok = a.js('''(()=>{const el=[...document.querySelectorAll("*")].filter(e=>e.children.length<4&&(e.innerText||"").includes(%r)&&e.offsetParent!==null).pop();if(!el)return null;el.click();return "ok"})()''' % nome)
    if ok: break
time.sleep(3)
b = a.js('(()=>{const b=[...document.querySelectorAll("button")].find(e=>/Incluir no comando/.test(e.innerText)&&e.offsetParent!==null);if(b&&!b.disabled){b.click();return "incluido"}return "auto"})()')
print('selecionado:', ok, b); time.sleep(2); shot(a, 'flow_frame.jpg')
