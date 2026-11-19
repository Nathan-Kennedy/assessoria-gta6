# -*- coding: utf-8 -*-
# Utilitario (21/10/2026): fala DIRETO com uma aba do Opera GX (porta 9333) pelo CDP, sem o Playwright (que demora para conectar com
# dezenas de abas abertas). js(aba, codigo) avalia JavaScript (com await) e devolve o valor.
import json, urllib.request, itertools
from websockets.sync.client import connect
_ids = itertools.count(1)
def abas(filtro=""):
    return [t for t in json.load(urllib.request.urlopen("http://127.0.0.1:9333/json/list")) if t["type"] == "page" and filtro in t["url"]]
class Aba(object):
    def __init__(self, t): self.ws = connect(t["webSocketDebuggerUrl"], max_size=None, open_timeout=30); self.url = t["url"]
    def cmd(self, metodo, **p):
        i = next(_ids); self.ws.send(json.dumps({"id": i, "method": metodo, "params": p}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == i: return m.get("result", m)
    def js(self, codigo):
        r = self.cmd("Runtime.evaluate", expression=codigo, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r or "error" in r: return None          # erro no JS conta como "ainda nao"
        return r.get("result", {}).get("value")
