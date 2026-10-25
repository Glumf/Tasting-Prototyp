"""Kopiert den gemeinsamen Datenblock (Farbwelten, Wein- und Bier-Daten) aus der App in die Web-Ansicht.

Aufruf: python3 daten_abgleichen.py ../quellen/Prototyp.dc.html ../quellen/Web.dc.html
"""
import sys
START, END = "// DATEN-ANFANG", "// DATEN-ENDE"
app, web = sys.argv[1], sys.argv[2]
a = open(app, encoding="utf-8").read()
block = a[a.index(START):a.index(END) + len(END)]
w = open(web, encoding="utf-8").read()
w = w[:w.index(START)] + block + w[w.index(END) + len(END):]
open(web, "w", encoding="utf-8").write(w)
print("Daten abgeglichen:", web)
