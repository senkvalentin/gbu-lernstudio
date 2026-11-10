# Fragenbank und lokale Lernmaterialien

Nur Material verwenden, für das du die erforderlichen Nutzungsrechte hast. Eine lokale Nutzungserlaubnis ist keine Freigabe für öffentliche Weitergabe. Die Fragenbank `questions.json` ist Bestandteil des Repositorys. Das Original-PDF `betriebs-u-fragen.pdf` ist ebenfalls enthalten. Lokale Prüfprotokolle bleiben ausgeschlossen.

## Fragenbank

Die mitgelieferte Datei `questions.json` im Projektstamm enthält die Fragenbank. Für eine neue Fragenbank kann `examples/questions.demo.json` als Ausgangspunkt dienen. Beide Dateien enthalten ein JSON-Array. `questions.json` wird mit Git versioniert und hat beim Laden Vorrang vor der Demo.

Pflichtfelder je Frage:

| Feld | Format |
| --- | --- |
| `id` | Eindeutige, stabile Zahl |
| `chapter` | Kapitelname als String |
| `page` | PDF-Seitennummer, ab 1 |
| `text` | Fragetext |
| `correctCount` | Anzahl richtiger Antworten |
| `options` | Array mit Antworttexten |
| `answers` | Array mit nullbasierten Indizes richtiger Optionen |
| `sourceAnswer` | Lösungshinweis als String |
| `explanation` | Hintergrundtext als String, auch leer möglich |
| `flags` | Array mit Prüfhinweisen, auch leer möglich |

Optionale Felder sind `independentExplanation`, `memoryExample`, `explanationStatus`, `contextTopic`, `contextWarning` und `editorialDecision` (Strings). Quellen und Zusatzhinweise nur aufnehmen, wenn deren Verwendung erlaubt ist.

Training und Simulation berücksichtigen nur vier Antwortoptionen, ein bis drei richtige Antworten und passende Lösungsschlüssel. Kontextwarnungen und bestimmte Prüfhinweise schließen Fragen aus. IDs und Lösungsindizes selbst prüfen: Die App enthält keine umfassende Schema-Validierung.

Für die vorgesehene Simulation zwölf Kapitel mit jeweils mindestens vier geeigneten Fragen bereitstellen. Mit anderen Kapitelzahlen erzeugt die bestehende Logik vier Fragen pro Kapitel; die Oberfläche nennt weiterhin 48 Fragen.

## Original-PDF

Die mitgelieferte `betriebs-u-fragen.pdf` wird mit Git versioniert und dient als Ziel der Seitenlinks. Andere PDFs bleiben durch `.gitignore` ausgeschlossen.

`build_data.py` ist ein historischer, heuristischer Importer mit festen Pfaden unter `/mnt/data`. Er ist kein allgemeiner oder verlustfreier PDF-Konverter und rekonstruiert die späteren manuellen Überarbeitungen nicht. Zur Verwendung eine lokale Kopie unter `private/` anlegen, Ein- und Ausgabepfad darin anpassen und eine virtuelle Umgebung mit `python3 -m venv .venv` erstellen. Danach `.venv/bin/python -m pip install PyMuPDF` und `.venv/bin/python private/build_data.py` ausführen. Ergebnis einschließlich Lösungen und Seitenzuordnung manuell prüfen. Die Web-App braucht diesen Importer nicht.

## Öffentliche Bereitstellung

Nur die geprüften Git-Dateien deployen, beispielsweise aus einem frischen Clone. Niemals den gesamten lokalen Arbeitsordner einschließlich ignorierter Dateien hochladen. Eigene vertrauliche Quelldaten gehören nicht in ein öffentliches Hosting. Nach Austausch der Fragenbank neu laden; bei einer alten Installation gegebenenfalls Service Worker und Website-Cache in den Browserwerkzeugen entfernen.
