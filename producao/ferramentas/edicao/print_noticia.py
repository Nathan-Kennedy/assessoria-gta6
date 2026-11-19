# Abre a matéria no Edge (headless), grifa em amarelo o trecho e salva print da página (viewport largo) + JSON com posições
# Uso: print_noticia.py URL "trecho exato" saida.png [seletor_data]
import sys, json, asyncio
from playwright.async_api import async_playwright
JS = r"""
([trecho]) => {
  // fecha banners de cookie/consentimento comuns
  for (const b of document.querySelectorAll('button, a')) {
    const t = (b.innerText||'').trim().toLowerCase();
    if (['aceitar','accept','i agree','concordo','ok, entendi','prosseguir','accept all','aceito'].includes(t)) { try { b.click(); } catch(e){} }
  }
  for (const s of ['[id*=cookie]','[class*=cookie]','[id*=consent]','[class*=consent]','[class*=newsletter]','[class*=paywall]','[class*=modal]','iframe']) {
    document.querySelectorAll(s).forEach(e => { if (e.getBoundingClientRect().height < 900 || s==='iframe') e.style.display='none'; });
  }
  // esconde anúncios, banners fixos/sticky e caixas de propaganda
  const reAd = /(^|[-_ ])(ad|ads|adv|advert|advertisement|banner|outbrain|taboola|teads|dfp|gpt|sponsor|promo|cookie|consent|popup|modal|overlay)([-_ ]|$)/i;
  document.querySelectorAll('body *').forEach(e => {
    const cs = getComputedStyle(e); const id = (e.id||'') + ' ' + (typeof e.className === 'string' ? e.className : '');
    if (cs.position === 'fixed' || cs.position === 'sticky') { e.style.display = 'none'; return; }
    if (reAd.test(id) && !e.querySelector('h1, p')) e.style.display = 'none';
  });
  window.scrollTo(0, 0);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; while ((n = walker.nextNode())) {
    const i = n.nodeValue.indexOf(trecho);
    if (i >= 0) {
      const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + trecho.length);
      const m = document.createElement('mark');
      m.style.cssText = 'background:#ffe600;color:#000;padding:2px 4px;border-radius:3px;box-shadow:0 0 0 3px #ffe600;';
      r.surroundContents(m);
      const b = m.getBoundingClientRect(); const p = m.closest('p') || m.parentElement; const pb = p.getBoundingClientRect();
      const h1 = document.querySelector('h1'); const hb = h1 ? h1.getBoundingClientRect() : {top:0,bottom:0};
      return {mark:[b.left, b.top + scrollY, b.width, b.height], par:[pb.left, pb.top+scrollY, pb.width, pb.height],
              titulo:[hb.top + scrollY, hb.bottom + scrollY], altura: document.documentElement.scrollHeight};
    }
  }
  return null;
}
"""
JS2 = r"""
([t]) => { const m=[...document.querySelectorAll("mark")].find(x=>x.innerText.includes(t.slice(0,15))); if(!m) return null; const b=m.getBoundingClientRect(); const p=m.closest("p")||m.parentElement; const pb=p.getBoundingClientRect(); const h1=document.querySelector("h1"); const hb=h1?h1.getBoundingClientRect():{top:0,bottom:0}; return {mark:[b.left,b.top+scrollY,b.width,b.height],par:[pb.left,pb.top+scrollY,pb.width,pb.height],titulo:[hb.top+scrollY,hb.bottom+scrollY],altura:document.documentElement.scrollHeight}; }
"""
JS3 = r"""
() => {
  const marks=[...document.querySelectorAll('mark')]; if(!marks.length) return 0;
  const P = marks.map(m => (m.closest('p')||m.parentElement));
  let n=0;
  document.querySelectorAll('body *').forEach(e => {
    if (P.some(p => p.contains(e) || e.contains(p))) return;
    const cs=getComputedStyle(e);
    const flutua = ['fixed','sticky','absolute'].includes(cs.position) || (parseInt(cs.zIndex)||0) > 0;
    if (cs.position==='fixed' || cs.position==='sticky') { e.style.display='none'; n++; return; }
    if (!flutua) return;
    const r=e.getBoundingClientRect();
    for (const p of P) { const q=p.getBoundingClientRect();
      if (r.width>50 && r.height>30 && r.left<q.right && r.right>q.left && r.top<q.bottom && r.bottom>q.top) { e.style.display='none'; n++; break; } }
  });
  return n;
}
"""
JS4 = r"""
() => {
  let n=0;
  for (const m of document.querySelectorAll('mark')) {
    const p = m.closest('p') || m.parentElement;
    for (let k=0;k<30;k++) {
      const q = p.getBoundingClientRect(); let tirou=false;
      for (let fx=0.03; fx<1; fx+=0.04) for (let fy=0.1; fy<1; fy+=0.2) {
        const x=q.left+q.width*fx, y=q.top+q.height*fy;
        if (y<0 || y>innerHeight) continue;
        const top=document.elementFromPoint(x,y);
        if (top && !p.contains(top) && !top.contains(p)) { top.style.display='none'; n++; tirou=true; }
      }
      if(!tirou) break;
    }
  }
  return n;
}
"""
async def main(url, trecho, saida):
    extras = trecho.split("||")[1:]; trecho = trecho.split("||")[0]
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="msedge", headless=True)
        pg = await b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1.5, locale="pt-BR")
        await pg.goto(url, wait_until="domcontentloaded", timeout=60000); await pg.wait_for_timeout(5000)
        info = await pg.evaluate(JS, [trecho])
        if not info: print("TRECHO NAO ENCONTRADO"); await b.close(); return
        for ex in extras: await pg.evaluate(JS, [ex])
        info = await pg.evaluate(JS2, [trecho]) or info
        await pg.wait_for_timeout(2500)
        await pg.evaluate(JS, ['@@nada@@']); print('removidos', await pg.evaluate(JS3))
        for mk in await pg.query_selector_all('mark'):
            await mk.scroll_into_view_if_needed(); await pg.wait_for_timeout(300); print('na frente:', await pg.evaluate(JS4))
        await pg.evaluate('window.scrollTo(0,0)')
        info = await pg.evaluate(JS2, [trecho]) or info
        await pg.wait_for_timeout(500)
        clip_h = min(info["par"][1] + info["par"][3] + 250, info["altura"])
        await pg.screenshot(path=saida, clip={"x": 0, "y": 0, "width": 1280, "height": clip_h}, full_page=True)
        info["clip_h"] = clip_h; info["escala"] = 1.5
        json.dump(info, open(saida.replace(".png", ".json"), "w"), indent=1); print(json.dumps(info))
        await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))
