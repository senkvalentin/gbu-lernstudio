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

Training und Simulation berücksichtigen nur vier Antwortoptionen, ein bis drei richtige Antworten und passende Lösungsschlüssel. Kontextwarnungen und bestimmte Prüfhinweise schließen Fragen aus. IDs und Lösungsindizes mit `python3 scripts/validate_catalog.py` prüfen. Das versionierte JSON-Schema liegt unter `schemas/questions.schema.json`; die Validierung prüft zusätzlich fachliche Sperren, Audit-Zuordnungen und stabile Alt-IDs. Die Laufzeit-App verwirft ungültige Schlüssel für bewertete Modi.

Für die vorgesehene Simulation zwölf Kapitel mit jeweils mindestens vier geeigneten Fragen bereitstellen. Mit anderen Kapitelzahlen erzeugt die bestehende Logik vier Fragen pro Kapitel; die Oberfläche nennt weiterhin 48 Fragen.

## Original-PDF

Die mitgelieferte `betriebs-u-fragen.pdf` wird mit Git versioniert und dient als Ziel der Seitenlinks. Andere PDFs bleiben durch `.gitignore` ausgeschlossen.

`build_data.py` ist ein historischer, heuristischer Importer mit festen Pfaden unter `/mnt/data`. Er ist kein allgemeiner oder verlustfreier PDF-Konverter und rekonstruiert die späteren manuellen Überarbeitungen nicht. Zur Verwendung eine lokale Kopie unter `private/` anlegen, Ein- und Ausgabepfad darin anpassen und eine virtuelle Umgebung mit `python3 -m venv .venv` erstellen. Danach `.venv/bin/python -m pip install PyMuPDF` und `.venv/bin/python private/build_data.py` ausführen. Ergebnis einschließlich Lösungen und Seitenzuordnung manuell prüfen. Die Web-App braucht diesen Importer nicht.

## Öffentliche Bereitstellung

Nur die geprüften Git-Dateien deployen, beispielsweise aus einem frischen Clone. Niemals den gesamten lokalen Arbeitsordner einschließlich ignorierter Dateien hochladen. Eigene vertrauliche Quelldaten gehören nicht in ein öffentliches Hosting. Nach Austausch der Fragenbank neu laden; bei einer alten Installation gegebenenfalls Service Worker und Website-Cache in den Browserwerkzeugen entfernen.

## Stabile IDs, Quellen und historische Ergebnisse

Bestehende Frage-IDs und die Reihenfolge bestehender `options` bleiben unverändert. Antworten in Versuchen sind nullbasierte Originalindizes, keine Anzeigenummern. Eine andere Sortierung der Frageobjekte wäre möglich; IDs daraus neu abzuleiten ist unzulässig.

Optionale Audit-Felder: `assessmentStatus` (`verified`, `source-only`, `unresolved`), `catalogRevision`, `auditSources` und `source`. `unresolved` bzw. eine Kontextwarnung sperrt die Bewertung. `verified` bezeichnet die im Audit benannte Prüfung; es behauptet keine offizielle Musterlösung. `source-only` kennzeichnet eine belegte Textwiederherstellung ohne unabhängige Bestätigung des gesamten Schlüssels. Drei oder fünf Optionen bleiben im Lesebuch. `page: 0` ist bei einer reinen Importquelle ohne exakte PDF-Stelle erlaubt; die Oberfläche verlinkt dann den Audit.

Die Originaldatei unter `imported-questions/` wurde nicht verändert. Neue IDs #274–278 sind fest vergeben und werden nicht aus einer erneuten Importreihenfolge erzeugt. Der Audit bewahrt alle alten Optionspositionen und Schlüssel. Historische `points` und `full` bleiben unverändert; sie werden nicht anhand des neuen Katalogs neu berechnet. Neue Versuche erhalten `questionRevision`, `answerKey` und `correctCount`.

Der Export behält seine bisherigen Top-Level-Felder und exportiert zusätzlich die vollständige DB sowie rohe Werte für alle App-Storage-Schlüssel unter `backup.storage` (`backup.version: 2`). Das ist eine lesende Sicherung, kein Zurücksetzen und keine automatische Migration. Nur App-Schlüssel werden exportiert, keine anderen Daten derselben Origin. Echte Browserdaten wurden während dieses Audits nicht gelesen.
