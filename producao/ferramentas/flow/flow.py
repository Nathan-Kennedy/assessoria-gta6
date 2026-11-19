import sys, json, urllib.request, time, base64, os
sys.path.insert(0, r'C:\Projetos Dev\Roupas\modelos-ia\scripts')
from cdp_aba import Aba
S = os.path.dirname(os.path.abspath(__file__))

def aba():
    l = [t for t in json.load(urllib.request.urlopen('http://127.0.0.1:9333/json/list')) if t['type'] == 'page' and 'flow.google.com' in t['url']]
    a = Aba(l[0]); a.cmd('Emulation.setFocusEmulationEnabled', enabled=True)
    a.cmd('Page.enable'); a.cmd('Page.setWebLifecycleState', state='active')
    return a

def shot(a, n):
    r = a.cmd('Page.captureScreenshot', format='jpeg', quality=60)
    open(os.path.join(S, n), 'wb').write(base64.b64decode(r['data']))

def clicar_txt(a, txt):
    return a.js('''(()=>{const el=[...document.querySelectorAll("button,a,[role=button],div,span,p")].filter(e=>e.innerText&&e.innerText.trim()==%s&&e.offsetParent!==null).pop();if(!el)return null;(el.closest("button,a,[role=button]")||el).click();return "ok"})()''' % json.dumps(txt))

def botoes(a):
    return a.js('''[...document.querySelectorAll("button,[role=button],[role=combobox],input,textarea")].filter(e=>e.offsetParent!==null).map(e=>(e.tagName+"|"+(e.getAttribute("aria-label")||"")+"|"+(e.innerText||e.placeholder||e.type||"").trim().replace(/\\s+/g," ").slice(0,50))).join("\\n")''')
