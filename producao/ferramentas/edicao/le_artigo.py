import sys, asyncio
from playwright.async_api import async_playwright
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="msedge", headless=True)
        pg = await b.new_page(viewport={"width":1280,"height":900})
        await pg.goto(url, wait_until="domcontentloaded", timeout=60000); await pg.wait_for_timeout(4000)
        ps = await pg.eval_on_selector_all("p, time, h1", "els=>els.map(e=>e.tagName+': '+e.innerText.trim()).filter(t=>t.length>4)")
        for t in ps[:45]: print(t[:260])
        await b.close()
asyncio.run(main(sys.argv[1]))
