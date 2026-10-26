# TastingPath · Klick-Prototyp

Ein klickbarer Prototyp von TastingPath, der Wein- und Bier-App. Er zeigt den Umfang von Version 1: vom ersten Start über die Vorbereitung und das geführte Tasting bis zum Notizbuch mit Keller und Merkliste, zum Geschmacksprofil, zum Tasting-Abend und zum Abo. Ein Schalter oben wechselt zwischen Wein und Bier, alkoholfreie Getränke findet man über den Filter „Alkoholfrei“.

Zum Ausprobieren einfach die Seite öffnen: https://glumf.github.io/Tasting-Prototyp/ Am Handy läuft die App im Vollbild, am Computer in einem Handy-Rahmen. Die Web-Ansicht für Premium-Nutzer kommt erst nach Version 1. Man sieht sie über den Knopf oben rechts oder mit `?web` am Ende der Adresse.

Hersteller, Preise und Texte sind Platzhalter. Bereiche für später (Karte der Herkunft, Mein Jahr, Als Karte teilen, Abend teilen) stecken noch im Code, sind in Version 1 aber ausgeblendet.

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

Einen bestimmten Zustand direkt öffnen, zum Beispiel für Bilder: `index.html?screen=step2&world=bier&level=Erfahren&look=dark`.
