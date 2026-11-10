# GBU Lernstudio

Eine interaktive Lernplattform zur Vorbereitung auf die Lehrveranstaltung Grundlagen der Betriebs- und Unternehmensführung an der TU Wien. Das Lernstudio verbindet strukturierte Lerninhalte, adaptive Übungsfragen und Prüfungssimulationen mit einem übersichtlichen Lernfortschritt.

**Unabhängiges studentisches Lernprojekt. Keine offizielle Anwendung der TU Wien.**

Das Projekt hilft dabei, eigene Lernmaterialien wiederholt zu bearbeiten und den persönlichen Übungsstand im Blick zu behalten. Das Repository enthält die Fragenbank `questions.json` sowie eine selbst formulierte Demonstrationsfrage als Fallback. Die Original-PDF und lokale Prüfprotokolle bleiben ausgeschlossen.

## Funktionen

- Dashboard mit Lernstand, Tagesziel und Themenübersicht.
- Adaptives Training mit einer einfachen Gewichtung bisheriger Fehler und Erfolge; alternativ zufälliges oder kapitelweises Training.
- Zufällige Antwortreihenfolge, unmittelbare Rückmeldung im Training und optionale Anzeige der Anzahl richtiger Antworten.
- Lesebuch mit Kapitel- und Textfilter, Markierung gelesener Fragen sowie Feldern für Erklärungen und Beispiele.
- Prüfungssimulation mit vier Fragen je vorhandenem Kapitel, Teilpunkten und abschließender Auswertung. Für die vorgesehene 48-Fragen-Simulation werden zwölf Kapitel mit jeweils mindestens vier geeigneten Fragen benötigt. Mit den Demodaten ist sie nicht verfügbar.
- Statistik nach Kapitel und Lerntag. Als beherrscht gelten Fragen, die an zwei verschiedenen UTC-Kalendertagen vollständig richtig beantwortet wurden.
- Anzeige von Import-Prüfhinweisen, JSON-Export der Versuche und Einstellungen, Hell-/Dunkelmodus und Tastaturbedienung.
- Web-App-Manifest und Service Worker für den Offlinebetrieb der öffentlichen Oberfläche einschließlich Demodaten nach erfolgreichem Erstladen.

## Technologien und Voraussetzungen

HTML, CSS und Vanilla JavaScript; JSON als Fragenformat, LocalStorage für den Lernstand und Cache Storage für die PWA. Kein Backend, kein Framework, kein Paketmanager und kein Buildprozess.

Benötigt werden ein moderner Browser und für den folgenden lokalen Start Python 3. Der optionale PDF-Importer benötigt zusätzlich PyMuPDF. Für die App selbst müssen keine Dependencies installiert werden.

## Installation und Start

```sh
git clone https://github.com/senkvalentin/gbu-lernstudio.git
cd gbu-lernstudio
python3 -m http.server 8080 --bind 127.0.0.1
```

Anschließend [localhost:8080](http://localhost:8080) öffnen. Beenden mit `Ctrl+C`. Die HTML-Datei nicht direkt über `file://` öffnen. Einen Buildbefehl gibt es nicht.

Die mitgelieferte `questions.json` wird beim Start geladen. Ohne diese Datei lädt die App `examples/questions.demo.json`. Eigene autorisierte Daten werden wie in [Datenformat und Import](docs/DATEN.md) beschrieben lokal bereitgestellt. Der Python-Webserver stellt auch ignorierte Dateien im gewählten Ordner bereit: nur lokal betreiben und bei öffentlichem Hosting ausschließlich freigegebene Dateien hochladen.

## Bedienung und Lernmodi

1. Im Dashboard den Lernstand ansehen oder ein Training beginnen.
2. Unter **Training** Modus, Kapitel und Umfang wählen. Mit `1`–`4` Antworten auswählen und mit `Enter` prüfen beziehungsweise weitergehen. `Esc` beendet die laufende Sitzung.
3. Im **Lesebuch** Inhalte durchsuchen und als gelesen markieren; `←` und `→` wechseln die Frage.
4. Unter **Prüfung** eine Simulation starten, sobald genügend geeignete Fragen vorhanden sind. Bei weniger als vier geeigneten Fragen in einem Kapitel wird der Start abgelehnt.
5. **Statistik** zeigt Versuche und Ergebnisse; **Prüffälle** zeigt hinterlegte Hinweise. **Export** lädt Versuche und Einstellungen als JSON herunter.

Die Teilpunkte pro Frage sind `max(0, richtige Auswahl / Anzahl richtiger Antworten − falsche Auswahl / Anzahl falscher Antworten)`. Die Notengrenzen liegen bei 88 %, 77 %, 62 % und 50 %. Dies sind implementierte Übungsregeln, keine Zusicherung einer offiziellen Prüfungsbewertung.

## Projektstruktur

```text
index.html                    Oberfläche und Navigation
app.js                        Lernmodi, Auswertung und lokale Speicherung
style.css                     Layout und Farbschemata
manifest.webmanifest          PWA-Metadaten
sw.js                         Offline-Cache
icon.svg                      App-Symbol
questions.json                Fragenbank
examples/questions.demo.json  Eigener, öffentlicher Beispieldatensatz
build_data.py                 Optionaler historischer PDF-Importer
docs/DATEN.md                Datenformat und lokale Quelldaten
.gitignore                    Ausschlüsse für private Daten und Artefakte
```

## Datenhaltung und Datenschutz

Versuche enthalten Frage-ID, Zeitstempel, Antwortauswahl, Korrektheit, Punkte und Modus. Sie werden mit Einstellungen und Lesemarkierungen im Browser gespeichert (`gbu-study-v1`); Farbschema und letzte Antwortreihenfolge verwenden weitere LocalStorage-Schlüssel. Es gibt keine Konten, Synchronisierung oder eingebauten Analyse- und Trackingdienste. Der Webserver erhält übliche Dateianfragen; externe Links werden beim Öffnen extern abgerufen.

Browserdaten sind weder verschlüsselt noch geräteübergreifend gesichert. Der JSON-Export enthält **nicht** die Lesemarkierungen, die letzte Antwortreihenfolge oder das separat gespeicherte Farbschema; eine Import-/Wiederherstellungsfunktion ist nicht implementiert. Löschen der Website-Daten entfernt den lokalen Fortschritt. Fragenbank-IDs nach Beginn des Lernens stabil halten.

Die Fragenbank `questions.json` wird mit Git versioniert. PDFs bleiben durch `.gitignore` lokal. Sie werden beim Aufrufen vom jeweiligen Webserver an den Browser ausgeliefert. Die öffentliche Offline-Vorablage enthält nur Oberfläche und Demo; private Fragen und PDFs werden nicht gezielt für Offlinebetrieb vorab gespeichert. Service Worker und Installierbarkeit benötigen HTTPS oder localhost; Unterstützung und Installation hängen vom Browser ab.

## Bekannte Einschränkungen

- Automatische PDF-Extraktion kann Texte, Lösungen und Kapitel falsch zuordnen. Inhalte vor Nutzung manuell prüfen; keine fachliche Richtigkeits- oder Erfolgsgarantie.
- PDF-Links in der Oberfläche setzen eine eigene autorisierte `betriebs-u-fragen.pdf` voraus; in der öffentlichen Demo führen sie ohne diese Datei ins Leere.
- Prüfungsdatum (12.11.2026), Zielnote und UI-Angaben zur 48-Fragen-Prüfung sind fest im Code hinterlegt. Die tatsächliche Fragenzahl hängt von der Zahl der bereitgestellten Kapitel ab.
- Kein Zeitlimit in der Simulation. Kein Backend, Fortschrittsimport oder Abgleich zwischen Geräten.
- Keine vorhandene automatisierte Browser-Testsuite. Für diese Veröffentlichung wurden Syntax, Datenformat und Kernlogik geprüft. Ein lokaler HTTP-Start wurde versucht, aber die Ausführungsumgebung blockiert das Öffnen eines Serverports. HTTP-, visuelle Browser- und Gerätetests stehen daher aus.

## Weiterentwicklung

Mögliche nächste Schritte sind ein konfigurierbares Prüfungsdatum, Validierung eigener Datensätze, vollständiger Fortschrittsimport und automatisierte Browsertests. Diese Funktionen sind noch nicht implementiert. Änderungen sollten ohne private Lernmaterialien eingereicht und gegen Demo sowie eigene autorisierte Daten geprüft werden.

## Lizenzstatus

Es wurde keine Open-Source-Lizenz festgelegt; das öffentliche Repository erteilt keine zusätzliche pauschale Nutzungslizenz. Rechte an fremden Lernmaterialien verbleiben bei den jeweiligen Rechteinhabern. Eine spätere Lizenzwahl für den eigenen Code muss separat erfolgen und kann keine Rechte an fremden Inhalten einräumen.
