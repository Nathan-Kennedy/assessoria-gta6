import sys, base64, json, os
sys.path.insert(0, r"C:\Projetos Dev\Roupas\modelos-ia\scripts")
from cdp_aba import Aba, abas
a = Aba(abas(os.environ.get("ABA","studio.youtube.com"))[0])
op = sys.argv[1]
if op == "shot":
    a.cmd("Page.bringToFront")
    r = a.cmd("Page.captureScreenshot", format="png")
    open(sys.argv[2], "wb").write(base64.b64decode(r["data"])); print("ok")
elif op == "js":
    code = open(sys.argv[2], encoding="utf-8").read()
    r = a.cmd("Runtime.evaluate", expression=code, awaitPromise=True, returnByValue=True)
    print(json.dumps(r.get("result", r), ensure_ascii=False)[:6000])
elif op == "file":   # file <css selector> <path>  -> set file on input
    doc = a.cmd("DOM.getDocument", depth=-1, pierce=True)["root"]["nodeId"]
    n = a.cmd("DOM.querySelectorAll", nodeId=doc, selector=sys.argv[2])["nodeIds"]
    print("nodes", n)
    print(a.cmd("DOM.setFileInputFiles", nodeId=n[int(sys.argv[4]) if len(sys.argv)>4 else 0], files=[sys.argv[3]]))
elif op == "click":  # click x y
    x, y = float(sys.argv[2]), float(sys.argv[3])
    for t in ("mousePressed", "mouseReleased"):
        a.cmd("Input.dispatchMouseEvent", type=t, x=x, y=y, button="left", clickCount=1)
    print("ok")
if op == "type":   # type <selector-js-expr-file> <textfile>: focus element returned by js, insert text
    a.cmd("Runtime.evaluate", expression=open(sys.argv[2], encoding="utf-8").read(), awaitPromise=True)
    a.cmd("Input.insertText", text=open(sys.argv[3], encoding="utf-8").read()); print("typed")
if op == "tags":
    a.cmd("Runtime.evaluate", expression="(()=>{const t=document.querySelector('ytcp-uploads-dialog #tags-container input'); t.focus(); t.select(); return 1})()")
    a.cmd("Input.dispatchKeyEvent", type="keyDown", key="Backspace", code="Backspace", windowsVirtualKeyCode=8); a.cmd("Input.dispatchKeyEvent", type="keyUp", key="Backspace", code="Backspace", windowsVirtualKeyCode=8)
    for tg in open(sys.argv[2], encoding="utf-8").read().split(","):
        tg = tg.strip()
        if not tg: continue
        a.cmd("Input.insertText", text=tg)
        a.cmd("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13, text="\r")
        a.cmd("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter", windowsVirtualKeyCode=13)
    print("tags ok")
if op == "enter":
    a.cmd("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13, text="\r")
    a.cmd("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter", windowsVirtualKeyCode=13); print("enter")
if op == "nav":
    a.cmd("Page.navigate", url=sys.argv[2]); print("nav")
if op == "hashtags":
    for tg in sys.argv[2].split(","):
        a.cmd("Input.insertText", text="#" + tg); import time; time.sleep(1.2)
        a.cmd("Input.dispatchKeyEvent", type="keyDown", key="Escape", code="Escape", windowsVirtualKeyCode=27); a.cmd("Input.dispatchKeyEvent", type="keyUp", key="Escape", code="Escape", windowsVirtualKeyCode=27)
        a.cmd("Input.insertText", text=" ")
    print("ok")
if op == "fullshot":
    a.cmd("Page.bringToFront")
    lm = a.cmd("Page.getLayoutMetrics")["cssContentSize"]
    r = a.cmd("Page.captureScreenshot", format="jpeg", quality=60, captureBeyondViewport=True, clip={"x":0,"y":0,"width":lm["width"],"height":lm["height"],"scale":0.4})
    open(sys.argv[2], "wb").write(base64.b64decode(r["data"])); print(lm)
