# Wein- & Bier-App · Klick-Prototyp

Ein klickbarer Prototyp der Wein- & Bier-App. Er zeigt den Weg vom ersten Start über das geführte Tasting bis zum Notizbuch, zum eigenen Geschmacksprofil und zum Abo. Ein Schalter oben wechselt zwischen Wein und Bier.

Zum Ausprobieren einfach die Seite öffnen. Am Handy läuft die App-Ansicht im Vollbild. Am Computer öffnet sich die Web-Ansicht für Premium-Nutzer. Über „App-Ansicht“ oben rechts sieht man dort auch die App in einem Handy-Rahmen. Mit `?app` am Ende der Adresse zeigt die Seite immer die App.

App-Name, Hersteller, Preise und Texte sind Platzhalter.

## Was wo liegt

- `index.html`: der fertige Prototyp, den GitHub Pages anzeigt. Diese Datei wird gebaut, nicht von Hand geändert.
- `quellen/`: die Entwurfsdateien aus dem Design-Canvas. `Prototyp.dc.html` ist die App, `Web.dc.html` die Web-Ansicht. Die übrigen Dateien sind die einzelnen Bildschirme und Farbwelten für die Doku, `canvas.json` ordnet sie im Canvas an.
- `werkzeuge/`: Skripte zum Bauen, für die Bilder der Doku und für den Klick-Test.

## Änderungen machen

Geändert wird in `quellen/Prototyp.dc.html` und `quellen/Web.dc.html`. Danach:

```
cd werkzeuge
npm install
python3 daten_abgleichen.py ../quellen/Prototyp.dc.html ../quellen/Web.dc.html
python3 entwuerfe_erzeugen.py ../quellen
python3 build_combined.py ../quellen/Prototyp.dc.html ../quellen/Web.dc.html "$PWD/node_modules/@fontsource" ../index.html
python3 test_prototyp.py ../index.html testbilder
```

- `daten_abgleichen.py` kopiert die gemeinsamen Daten (Farbwelten, Wein- und Bier-Inhalte) aus der App in die Web-Ansicht.
- `entwuerfe_erzeugen.py` schreibt die einzelnen Bildschirm-Entwürfe und `canvas.json` neu.
- `build_combined.py` baut daraus die `index.html`.
- `test_prototyp.py` klickt App und Web-Ansicht durch und meldet am Ende „Klick-Test ohne Fehler“.

Bilder für die Doku (braucht Playwright mit Chromium):

```
python3 render.py ../index.html bilder
```

Einen bestimmten Zustand direkt öffnen, zum Beispiel für Bilder: `index.html?app&screen=step2&world=bier&pal=Schiefer&look=dark`.
