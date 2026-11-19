import sys, json, time
from flow import *

def enviar_arquivo(a, caminho, clicar_js):
    """Intercepta o seletor de arquivo do navegador e entrega o arquivo."""
    a.cmd('Page.setInterceptFileChooserDialog', enabled=True)
    a.cmd('DOM.enable')
    i = 900001
    a.ws.send(json.dumps({'id': i, 'method': 'Runtime.evaluate', 'params': {'expression': clicar_js, 'userGesture': True}}))
    t0 = time.time(); node = None
    while time.time() - t0 < 15:
        m = json.loads(a.ws.recv())
        if m.get('method') == 'Page.fileChooserOpened':
            node = m['params'].get('backendNodeId'); break
    if node is None:
        a.cmd('Page.setInterceptFileChooserDialog', enabled=False)
        return 'sem seletor'
    r = a.cmd('DOM.setFileInputFiles', backendNodeId=node, files=[caminho])
    a.cmd('Page.setInterceptFileChooserDialog', enabled=False)
    return 'ok' if 'error' not in r else str(r)

if __name__ == '__main__':
    a = aba()
    img = sys.argv[1]
    if not a.js('[...document.querySelectorAll("button")].some(e=>/Enviar mídia/.test(e.innerText))'): clicar_txt(a, 'Início'); time.sleep(2)
    js = '(()=>{const b=[...document.querySelectorAll("button")].find(e=>/Enviar mídia/.test(e.innerText));b.click();return 1})()'
    print(enviar_arquivo(a, img, js))
    time.sleep(8)
    shot(a, 'flow9.jpg')
    print(botoes(a)[-600:])
