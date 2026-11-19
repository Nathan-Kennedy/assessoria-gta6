"""Passa o mouse em cada vídeo da galeria do Flow para revelar o src e baixa. Uso: python flow_baixar2.py <pasta> <nome0> <nome1> ...
Os vídeos aparecem do mais novo para o mais antigo."""
import sys, os, json, time, urllib.request
from flow import *
pasta = sys.argv[1]; nomes = sys.argv[2:]
a = aba()
rects = a.js('''[...document.querySelectorAll("*")].filter(e=>e.children.length==0&&e.innerText&&e.innerText.trim()=="play_circle"&&e.offsetParent!==null).map(e=>{let t=e;for(let i=0;i<6&&t.parentElement;i++){t=t.parentElement;if(t.getBoundingClientRect().width>120)break}const r=t.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})''')
ck = a.cmd('Network.getCookies', urls=['https://flow.google.com', 'https://labs.google'])['cookies']
cab = '; '.join(c['name'] + '=' + c['value'] for c in ck); ua = a.js('navigator.userAgent')
vistos = []
for i, (x, y) in enumerate(rects):
    a.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y); time.sleep(2.5)
    src = a.js('''(()=>{const v=[...document.querySelectorAll("video")].map(v=>[v,v.getBoundingClientRect()]).find(([v,r])=>%f>=r.left&&%f<=r.right&&%f>=r.top&&%f<=r.bottom);return v?(v[0].currentSrc||v[0].src):null})()''' % (x, x, y, y))
    print(i, (src or '')[:70])
    if src and src not in vistos and i < len(nomes):
        vistos.append(src)
        d = urllib.request.urlopen(urllib.request.Request(src, headers={'Cookie': cab, 'User-Agent': ua, 'Referer': 'https://flow.google.com/'}), timeout=90).read()
        p = os.path.join(pasta, nomes[i]); open(p, 'wb').write(d); print('  salvo', p, len(d))
a.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=5, y=5)
