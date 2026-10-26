"""Bilder für die Doku: einzelne Bildschirme, Web-Ansicht und Farbwelten.

Aufruf: python3 render.py ../index.html bilder
Braucht Playwright mit Chromium (pip install playwright, playwright install chromium).
Die Bilder entstehen direkt aus dem gebauten Prototyp. Welcher Zustand gezeigt wird,
steht in der Adresse (screen, world, pal, look), siehe Liste unten.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

FILE = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])

APP = [
    ("01-erster-start.png", "screen=welcome"),
    ("01b-geschmacksfrage.png", "screen=onboard"),
    ("02-start-wein.png", "screen=home"),
    ("02b-start-bier.png", "screen=home&world=bier"),
    ("02c-schnell-notieren.png", "screen=quick"),
    ("03-verkosten-starten.png", "screen=begin-snap"),
    ("03b-empfehlungen.png", "screen=begin-rec"),
    ("03c-vorbereitung.png", "screen=prep"),
    ("04-tasting-aussehen.png", "screen=step1"),
    ("04b-tasting-nase-einsteiger.png", "screen=step2-kurz"),
    ("04c-tasting-nase-erfahren-bier.png", "screen=step2-kurz&world=bier&level=Erfahren"),
    ("04d-tasting-gaumen-bier.png", "screen=step3&world=bier"),
    ("05-aufloesung.png", "screen=result"),
    ("06-notizbuch.png", "screen=journal"),
    ("06b-notizbuch-keller.png", "screen=cellar"),
    ("06c-notizbuch-merkliste.png", "screen=merk"),
    ("07-geschmack.png", "screen=taste"),
    ("08-profil.png", "screen=profile"),
    ("08b-premium.png", "screen=paywall"),
    ("09-essen.png", "screen=food"),
    ("10-tasting-abend.png", "screen=party"),
    ("10b-tasting-abend-einladen.png", "screen=party-share"),
    ("10c-tasting-abend-bewerten.png", "screen=party-rate"),
    ("10d-tasting-abend-rangliste.png", "screen=party-result"),
    ("12-mein-jahr.png", "screen=year"),
    ("13-teilen.png", "screen=share"),
    ("14-lernen.png", "screen=learn"),
    ("14b-nasen-training.png", "screen=train"),
    ("15-karte.png", "screen=map"),
]
WEB = [
    ("web-1-startseite.png", "web=guest"),
    ("web-2-uebersicht.png", "web=home"),
    ("web-3-notizbuch.png", "web=journal"),
    ("web-4-geschmack.png", "web=taste&world=bier"),
    ("web-5-konto.png", "web=account"),
]
PALS = [("Kellerei", "Warmes Creme mit Bordeaux und Bernstein", False),
        ("Schiefer", "Kühles Grau mit Pflaume und Kupfer", False),
        ("Landgut", "Heller Sand mit Weinrose und Hopfengrün", True)]
DARK = [("standard", "Standard"), ("kraeftig", "Kräftig"), ("kerze", "Kerzenlicht"), ("tief", "Tiefschwarz")]


async def shot_app(page, query, path):
    await page.goto("file://" + FILE + "?app&look=light&" + query)
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(300)
    await page.locator("#device").screenshot(path=path)


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        app = await b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        for name, q in APP:
            await shot_app(app, q, os.path.join(OUT, name))
            print("ok", name)
        web = await b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
        for name, q in WEB:
            await web.goto("file://" + FILE + "?look=light&" + q)
            await web.evaluate("document.fonts.ready")
            await web.wait_for_timeout(300)
            await web.screenshot(path=os.path.join(OUT, name))
            print("ok", name)
        # Farbwelten: Start-Bildschirm Wein und Bier, jeweils hell und dunkel
        tmp = os.path.join(OUT, "_tmp")
        os.makedirs(tmp, exist_ok=True)
        for i, (pal, sub, current) in enumerate(PALS, 1):
            cells = []
            for world in ("wein", "bier"):
                for look in ("light", "dark"):
                    f = os.path.join(tmp, f"{pal}-{world}-{look}.png")
                    await app.goto("file://" + FILE + f"?app&screen=home&world={world}&pal={pal}&look={look}")
                    await app.evaluate("document.fonts.ready")
                    await app.wait_for_timeout(250)
                    await app.locator("#device").screenshot(path=f)
                    cells.append((f, ("Wein" if world == "wein" else "Bier") + " · " + ("Hell" if look == "light" else "Dunkel")))
            title = pal + (" (aktuell)" if current else "")
            figs = "".join(f"<figure><img src='file://{f}'><figcaption>{cap}</figcaption></figure>" for f, cap in cells)
            html = f"""<!doctype html><html lang='de'><head><meta charset='utf-8'><style>
body{{margin:0;background:#FFFFFF;font-family:'Atkinson Hyperlegible',sans-serif;color:#1A1D21}}
#c{{width:880px;box-sizing:border-box;padding:28px}}
h1{{margin:0;font-size:26px}} p{{margin:4px 0 0;font-size:15px;color:#4D535B}}
.g{{margin-top:18px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
figure{{margin:0}} img{{width:100%;border-radius:18px;display:block;border:1px solid #E3E3E3}}
figcaption{{margin-top:6px;font-size:13px;font-weight:700;text-align:center}}
</style></head><body><div id='c'><h1>{title}</h1><p>{sub}</p><div class='g'>{figs}</div></div></body></html>"""
            hp = os.path.join(tmp, f"{pal}.html")
            open(hp, "w", encoding="utf-8").write(html)
            await web.goto("file://" + hp)
            await web.wait_for_timeout(300)
            name = f"farben-{i}-{pal.lower()}.png"
            await web.locator("#c").screenshot(path=os.path.join(OUT, name))
            print("ok", name)
        # Dunkel-Varianten der aktuellen Farbwelt
        cells = []
        for world in ("wein", "bier"):
            for ds, label in DARK:
                f = os.path.join(tmp, f"dunkel-{world}-{ds}.png")
                await app.goto("file://" + FILE + f"?app&screen=home&world={world}&pal=Landgut&look=dark&ds={ds}")
                await app.evaluate("document.fonts.ready")
                await app.wait_for_timeout(250)
                await app.locator("#device").screenshot(path=f)
                cells.append((f, ("Wein" if world == "wein" else "Bier") + " · " + label))
        figs = "".join(f"<figure><img src='file://{f}'><figcaption>{cap}</figcaption></figure>" for f, cap in cells)
        html = f"""<!doctype html><html lang='de'><head><meta charset='utf-8'><style>
body{{margin:0;background:#FFFFFF;font-family:'Atkinson Hyperlegible',sans-serif;color:#1A1D21}}
#c{{width:880px;box-sizing:border-box;padding:28px}}
h1{{margin:0;font-size:26px}} p{{margin:4px 0 0;font-size:15px;color:#4D535B}}
.g{{margin-top:18px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
figure{{margin:0}} img{{width:100%;border-radius:18px;display:block;border:1px solid #E3E3E3}}
figcaption{{margin-top:6px;font-size:13px;font-weight:700;text-align:center}}
</style></head><body><div id='c'><h1>Dunkel-Varianten (Landgut, entschieden: Tiefschwarz)</h1><p>Standard, Kräftig, Kerzenlicht und Tiefschwarz, jeweils für Wein und Bier</p><div class='g'>{figs}</div></div></body></html>"""
        hp = os.path.join(tmp, "dunkel.html")
        open(hp, "w", encoding="utf-8").write(html)
        await web.goto("file://" + hp)
        await web.wait_for_timeout(300)
        await web.locator("#c").screenshot(path=os.path.join(OUT, "farben-4-dunkel-varianten.png"))
        print("ok farben-4-dunkel-varianten.png")
        await b.close()

asyncio.run(main())
