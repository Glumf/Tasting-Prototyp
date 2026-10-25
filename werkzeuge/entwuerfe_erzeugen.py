"""Erzeugt die einzelnen Bildschirm-Entwürfe und Farbwelten für den Design-Canvas.

Jeder Entwurf bindet den Klick-Prototyp (Prototyp.dc.html) mit einem festen Startzustand ein.
Ändert man den Prototyp, ändern sich alle Entwürfe mit. Dazu schreibt das Skript canvas.json neu.

Aufruf: python3 entwuerfe_erzeugen.py ../quellen
"""
import json, os, sys

OUT = sys.argv[1]
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Fraunces:opsz,wght@9..144,600;9..144,700&amp;display=swap">'

SCREENS = [
    ("Main.dc.html", "1 · Erster Start", "welcome", "wein"),
    ("Geschmacksfrage.dc.html", "1b · Erfahrung und Geschmacksfrage", "onboard", "wein"),
    ("Start.dc.html", "2 · Start (Wein)", "home", "wein"),
    ("StartBier.dc.html", "2b · Start (Bier)", "home", "bier"),
    ("Schnellnotiz.dc.html", "2c · Schnell notieren", "quick", "wein"),
    ("Verkosten.dc.html", "3 · Verkosten starten", "begin-snap", "wein"),
    ("Empfehlungen.dc.html", "3b · Empfiehl mir was", "begin-rec", "wein"),
    ("Nase.dc.html", "4 · Tasting: Nase", "step2", "wein"),
    ("GaumenBier.dc.html", "4b · Tasting: Geschmack (Bier)", "step3", "bier"),
    ("Aufloesung.dc.html", "5 · Auflösung", "result", "wein"),
    ("Notizbuch.dc.html", "6 · Notizbuch", "journal", "wein"),
    ("Geschmack.dc.html", "7 · Mein Geschmack", "taste", "wein"),
    ("Profil.dc.html", "8 · Profil", "profile", "wein"),
    ("Premium.dc.html", "8b · Premium", "paywall", "wein"),
]
PALS = [("Kellerei", "Warmes Creme mit Bordeaux und Bernstein", True),
        ("Schiefer", "Kühles Grau mit Pflaume und Kupfer", False),
        ("Landgut", "Heller Sand mit Weinrose und Hopfengrün", False)]


def page(title, w, h, body):
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
body{{margin:0}}
</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
"""


boards, order = {}, []
boards["Prototyp.dc.html"] = {"x": -470, "y": 0, "w": 390, "h": 844, "title": "0 · Klick-Prototyp (alles zusammen)", "is_interactive": True}
order.append("Prototyp.dc.html")
for i, (f, title, start, world) in enumerate(SCREENS):
    body = f'<div style="width: 390px; height: 844px; overflow: hidden"><dc-import name="Prototyp" start="{start}" world="{world}" look="light" hint-size="390px,844px"></dc-import></div>'
    open(os.path.join(OUT, f), "w", encoding="utf-8").write(page(title.split(" · ", 1)[1], 390, 844, body))
    boards[f] = {"x": i * 470, "y": 0, "w": 390, "h": 844, "title": title, "is_interactive": True}
    order.append(f)
boards["Web.dc.html"] = {"x": 0, "y": 1324, "w": 1440, "h": 900, "title": "0b · Web-Ansicht am Rechner (Premium)", "is_interactive": True, "expand": "fill"}
order.append("Web.dc.html")
for i, (pal, sub, current) in enumerate(PALS):
    cells = ""
    for world in ("wein", "bier"):
        for look in ("light", "dark"):
            cap = ("Wein" if world == "wein" else "Bier") + " · " + ("Hell" if look == "light" else "Dunkel")
            cells += f'<div style="display: flex; flex-direction: column; gap: 6px"><div style="width: 195px; height: 422px; overflow: hidden; border-radius: 18px; border: 1px solid #E3E3E3"><div style="width: 390px; height: 844px; transform: scale(0.5); transform-origin: 0 0"><dc-import name="Prototyp" start="home" world="{world}" pal="{pal}" look="{look}" hint-size="390px,844px"></dc-import></div></div><span style="font-size: 13px; font-weight: 700; text-align: center">{cap}</span></div>'
    title = pal + (" (aktuell)" if current else "")
    body = f'<div style="width: 880px; height: 560px; box-sizing: border-box; padding: 28px; background: #FFFFFF; color: #1A1D21; font-family: \'Atkinson Hyperlegible\', sans-serif"><h1 style="margin: 0; font-size: 26px">{title}</h1><p style="margin: 4px 0 0; font-size: 15px; color: #4D535B">{sub}</p><div style="margin-top: 18px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">{cells}</div></div>'
    f = f"Farben-{pal}.dc.html"
    open(os.path.join(OUT, f), "w", encoding="utf-8").write(page("Farben " + pal, 880, 560, body))
    boards[f] = {"x": i * 960, "y": 2548, "w": 880, "h": 560, "title": "Farben · " + title}
    order.append(f)

canvas = {
    "v": 3, "createdOnFiles": {"v": 1, "at": "2026-10-25T12:40:00Z"}, "title": "Wein- & Bier-App Entwurf",
    "launch": {"view": "canvas"}, "pages": [], "boards": boards, "order": order,
    "notes": {
        "title": {"x": -470, "y": -300, "text": "Wein- & Bier-App · Klick-Prototyp und Hauptbildschirme", "kind": "title1", "maxW": 6970},
        "web": {"x": 0, "y": 1024, "text": "Web-Ansicht am Rechner", "kind": "title1", "maxW": 1440},
        "farben": {"x": 0, "y": 2248, "text": "Farbwelten · Wein und Bier, hell und dunkel", "kind": "title1", "maxW": 2800}
    },
    "designSystems": []
}
json.dump(canvas, open(os.path.join(OUT, "canvas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Entwürfe:", len(order))
