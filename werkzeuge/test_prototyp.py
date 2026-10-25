"""Automatischer Klick-Test für App und Web-Ansicht.

Aufruf: python3 test_prototyp.py ../index.html testbilder
Klickt die wichtigsten Wege durch, prüft sichtbare Texte und meldet jeden Fehler.
Endet mit "Klick-Test ohne Fehler" oder mit einer Liste der Probleme.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

FILE = os.path.abspath(sys.argv[1])
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
problems = []


async def click(page, name, exact=True, nth=0, role="button"):
    loc = page.get_by_role(role, name=name, exact=exact).nth(nth)
    await loc.click()
    await page.wait_for_timeout(120)


async def expect(page, text, label):
    if await page.get_by_text(text, exact=False).count() == 0:
        problems.append(f"{label}: Text „{text}“ fehlt")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()

        def watch(pg):
            pg.on("pageerror", lambda e: problems.append("Skriptfehler: " + str(e)))
            pg.on("console", lambda m: problems.append("Konsole: " + m.text) if m.type == "error" else None)

        ctx = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); watch(pg)
        await pg.goto("file://" + FILE + "?app&look=light"); await pg.wait_for_timeout(400)
        await click(pg, "Los geht's")
        await expect(pg, "Bitte bestätige zuerst dein Alter", "Altersabfrage")
        await pg.get_by_label("Ich bin mindestens 18 Jahre alt.").check()
        await click(pg, "Los geht's")
        await click(pg, "Erfahren Regler für alle Merkmale, rund 40 Aromen")
        for ans in ["Schwarz", "Grapefruit", "Zartbitter", "Zitronenlimo"]:
            await click(pg, ans)
            nxt = "Fertig" if ans == "Zitronenlimo" else "Nächste Frage"
            await click(pg, nxt)
        await expect(pg, "Was trinkst du heute?", "Start")
        await pg.screenshot(path=f"{OUT}/a1-start.png")
        await click(pg, "Verkosten Geführt, Schritt für Schritt")
        await click(pg, "Etikett fotografieren (Vorschau) Die App liest Name und Jahrgang vom Etikett")
        await expect(pg, "Erkannt", "Etikett")
        await click(pg, "Tasting starten")
        await click(pg, "Hellgelb"); await click(pg, "Klar"); await click(pg, "Weiter")
        await expect(pg, "Aromen", "Nase (Erfahren)")
        await click(pg, "Zitrone"); await click(pg, "Apfel"); await click(pg, "Weiter")
        for ax in ["Süße 1 von 5", "Säure 5 von 5", "Tannin 1 von 5", "Körper 2 von 5"]:
            await click(pg, ax)
        await click(pg, "Weiter"); await click(pg, "Mittel"); await click(pg, "Weiter")
        await click(pg, "Auflösung ansehen")
        await expect(pg, "Bitte vergib noch Sterne", "Sterne-Pflicht")
        await click(pg, "4 Sterne"); await click(pg, "Nochmal")
        await click(pg, "Auflösung ansehen")
        await expect(pg, "Gut gerochen!", "Auflösung")
        await pg.screenshot(path=f"{OUT}/a2-aufloesung.png")
        await click(pg, "Im Notizbuch speichern")
        await expect(pg, "6 Verkostungen", "Notizbuch nach Speichern")
        await click(pg, "Liste"); await click(pg, "4+ Sterne")
        await click(pg, "Riesling trocken [Weingut] · Heute · Nochmal ★★★★★", exact=False)
        await expect(pg, "Nochmal verkosten", "Detail")
        await click(pg, "Zurück")
        await click(pg, "Bier")
        await expect(pg, "4 Verkostungen", "Bier-Notizbuch")
        await click(pg, "Geschmack", exact=False, nth=0)
        await expect(pg, "Du magst fruchtige", "Geschmack Bier")
        await click(pg, "Session IPA", exact=False)
        await expect(pg, "Aussehen und Schaum", "Tasting aus Empfehlung")
        await click(pg, "Zurück")
        await click(pg, "Zurück")
        await click(pg, "Start", exact=True)
        await click(pg, "Schnell notieren Foto, Sterne, fertig")
        await click(pg, "Speichern")
        await expect(pg, "mindestens einen Stern", "Schnell notieren Pflicht")
        await click(pg, "3 Sterne"); await click(pg, "Speichern")
        await expect(pg, "5 Verkostungen", "Schnell notieren gespeichert")
        await click(pg, "Profil", exact=True)
        await click(pg, "Premium holen")
        await click(pg, "Abo abschließen (Vorschau)")
        await expect(pg, "Premium ist aktiv", "Abo")
        if await pg.get_by_text("[Werbebanner]").count():
            problems.append("Werbung trotz Premium sichtbar")
        await click(pg, "Dunkel"); await click(pg, "Schiefer")
        await click(pg, "Kerzenlicht"); await click(pg, "Tiefschwarz"); await click(pg, "Kräftig")
        await pg.screenshot(path=f"{OUT}/a3-profil-dunkel.png")
        await click(pg, "Hell")
        await click(pg, "Wein")

        # Tasting-Stile
        await click(pg, "Start", exact=True)
        await click(pg, "Verkosten Geführt, Schritt für Schritt")
        await click(pg, "Riesling trocken [Weingut] · Weißwein · 2023", exact=False)
        await click(pg, "Karten"); await expect(pg, "Schritt 1 von 5", "Karten-Stil")
        await click(pg, "Weiter")
        await click(pg, "Aromarad")
        await pg.get_by_role("button", name="Zitrone", exact=True).first.click(); await pg.wait_for_timeout(120)
        await pg.get_by_role("button", name="Zitrus", exact=True).first.click(); await pg.wait_for_timeout(120)
        await expect(pg, "2 Aromen gewählt", "Aromarad")
        await pg.screenshot(path=f"{OUT}/a4-aromarad.png")
        await click(pg, "Zuhören")
        await expect(pg, "Zum Weitergehen irgendwo tippen", "Zuhör-Modus")
        await pg.get_by_text("Zum Weitergehen irgendwo tippen").click(); await pg.wait_for_timeout(150)
        await expect(pg, "Schritt 3 von 5", "Zuhör-Modus weiter")
        await click(pg, "Glas")
        await click(pg, "Zurück"); await click(pg, "Zurück"); await click(pg, "Zurück"); await click(pg, "Zurück")

        # Neue Bereiche
        await click(pg, "Was passt zum Essen?")
        await click(pg, "Fisch"); await expect(pg, "Zu Fisch", "Essen")
        await click(pg, "Merken", nth=0)
        await click(pg, "Zurück")
        await click(pg, "Tasting-Abend")
        await click(pg, "+ Person"); await click(pg, "Abend starten")
        await click(pg, "Nächstes Glas"); await expect(pg, "Bitte lass alle bewerten", "Tasting-Abend Pflicht")
        for g in range(3):
            for name in ["Du", "[Name 2]", "[Name 3]", "[Name 4]"]:
                await click(pg, f"{name}: 4 Sterne")
            await click(pg, "Nächstes Glas" if g < 2 else "Ergebnis zeigen")
        await expect(pg, "Die Rangliste", "Tasting-Abend Ergebnis")
        await pg.screenshot(path=f"{OUT}/a5-rangliste.png")
        await click(pg, "Zurück")
        await click(pg, "Lernen und Abzeichen"); await expect(pg, "Abzeichen", "Lernen"); await click(pg, "Zurück")
        await click(pg, "Mein Jahr"); await click(pg, "Rückblick teilen"); await click(pg, "Als Bild teilen"); await click(pg, "Zurück")
        await click(pg, "Premium Mein Weinkeller"); await expect(pg, "Trinkfenster", "Keller"); await click(pg, "Zurück")
        await click(pg, "Notizbuch", exact=True)
        await click(pg, "Grauburgunder", exact=False)
        await click(pg, "Als Karte teilen"); await click(pg, "Für die Story")
        await ctx.close()

        ctx = await b.new_context(viewport={"width": 1440, "height": 900})
        pg = await ctx.new_page(); watch(pg)
        await pg.goto("file://" + FILE + "?look=light"); await pg.wait_for_timeout(400)
        await expect(pg, "Kostenlos oder Premium", "Web-Startseite")
        await click(pg, "Anmelden")
        await click(pg, "Anmelden (Vorschau)")
        await expect(pg, "Hallo [Name]", "Web-Übersicht")
        await click(pg, "Notizbuch")
        await click(pg, "Spätburgunder")
        await expect(pg, "Etwas zu herb für mich.", "Web-Detail")
        await click(pg, "Bier")
        await click(pg, "Mein Geschmack")
        await expect(pg, "Du magst fruchtige", "Web-Geschmack")
        await click(pg, "Konto und Abo")
        await click(pg, "Abmelden")
        await expect(pg, "Schmecken lernen", "Web-Abmelden")
        await click(pg, "App-Ansicht")
        await expect(pg, "Ich bin mindestens 18 Jahre alt.", "Wechsel zur App")
        await pg.screenshot(path=f"{OUT}/w1-app-im-rahmen.png")
        await ctx.close()
        await b.close()

    if problems:
        print("Probleme:"); [print(" -", x) for x in problems]; sys.exit(1)
    print("Klick-Test ohne Fehler")

asyncio.run(main())
