# GBU-Fragenkatalog: vollständiger Vergleich und Korrekturaudit

Stand: 10.11.2026. Alle 177 Importdatensätze wurden gelesen und einzeln zugeordnet. Der Bericht bestätigt keine offizielle Musterlösung: Das vorhandene PDF ist ebenfalls eine studentische Sammlung. Ein offizielles Skriptum oder eine offizielle Lösung war im Repository nicht verfügbar.

## Zusammenfassung

| Kennzahl | Anzahl |
|---|---:|
| Bestehende Fragen vor Audit | 273 |
| Importierte Fragen | 177 |
| Identisch (A) | 3 |
| Semantisch gleichwertige Varianten (B) | 121 |
| Gleiche Aufgabe mit widersprüchlichem Schlüssel (C) | 12 |
| Beschädigter/unvollständiger Bestand (D) | 4 |
| Neue geprüfte Fragen (E) | 5 |
| Unklare oder beschädigte Importfragen (F) | 32 |
| Bestehende Fragen korrigiert (Text/Schlüssel) | 8 |
| Davon Lösungsschlüssel geändert | 2 |
| Zusätzliche Bestandssperren, IDs erhalten | 25 |
| Ungeklärte Importfälle inkl. offener C/D | 37 |
| Final vorhandene Fragen (inkl. Lesebuch/Prüffälle) | 278 |
| Davon bewertbar | 203 |
| Davon nur Lesebuch | 75 |

A–F sind disjunkt. Bei unvollständigem Import hat F Vorrang, auch wenn daneben ein Schlüsselkonflikt vorliegt. D bezeichnet einen belegten Bestandsmangel, nicht automatisch eine erfolgreich reparierte Frage. B umfasst auch anders kombinierte, bereits abgedeckte richtige Aussagen und geänderte Ablenker; solche Varianten wurden nicht künstlich als neue Wissenslücken gezählt. Fälle mit unterschiedlichen Negationen wurden ausdrücklich geprüft. Die 12 C-Fälle sind zusätzlich in der Konflikttabelle ausgewiesen; weitere problematische Schlüssel in F stehen dort gesondert.

Drei neue Fragen (#274–276) haben drei Optionen und sind ausschließlich im Lesebuch verfügbar. Zwei neue Fragen (#277–278) sind für Training und Simulation geeignet. Kein bestehender Datensatz wurde entfernt, keine vorhandene Optionsfolge verschoben.

## Phase 1: Architektur und Fortschrittsschutz

- Statische HTML/CSS/Vanilla-JavaScript-App; kein Paketmanager, Framework, Server-Backend oder ursprünglicher Produktions-Build. `build_data.py` ist ein heuristischer PDF-Importer mit festen `/mnt/data`-Pfaden und wurde nicht auf den Bestand angewendet.
- `questions.json`: numerische stabile Frage-ID; Antworten sind **nullbasierte Originalindizes** in `options`, keine separat erzeugten Antwort-IDs. Importantworten haben dagegen explizite IDs (normalerweise 1–n). `rightids` ist ein String mit aneinandergereihten Ziffern.
- `gbu-study-v1` in localStorage enthält `attempts`, `notes`, `settings`, optional `readIds` sowie gegebenenfalls weitere Felder. Ein Versuch enthält ID, Datum, ausgewählte Originalindizes, `full`, `points` und `mode`. Es gibt keine IndexedDB, Storage-Migration oder automatische Neuberechnung alter Ergebnisse.
- Zusatzschlüssel: `gbu-color-theme` und `gbu-last-answer-order:<ID>`. Der Service Worker benutzt Cache Storage für Dateien, nicht für den Lernfortschritt. Origin, Manifest, Deployment-Basis und Storage-Schlüssel bleiben unverändert.
- Training: adaptiv nach bisherigen Fehlern/Erfolgen, zufällig oder kapitelweise. Beherrscht bedeutet zwei volle Erfolge an verschiedenen UTC-Tagen. Neue Fragen haben keine Versuche und keine Lesemarkierungen. Neue Fragen können lediglich den Nenner der Gesamtfortschrittsanzeige erhöhen.
- Simulation: vier geeignete Fragen pro vorhandenem Kapitel; zwölf Kapitel. Prüfungsversuche werden sofort einzeln als `mode: exam` gespeichert. Es existieren **keine separat gespeicherten abgeschlossenen Prüfungssitzungen, Gesamtnoten oder Sitzungs-IDs**. Eine Wiederherstellung dieser früher nie gespeicherten Informationen ist unmöglich. Vorhandene Prüfungsversuche bleiben vollständig erhalten.
- Randomisierung mischt nur eine Kopie der Originalindizes; Auswahl und Speicherung referenzieren stets den ursprünglichen Index. Vorhandene Optionen wurden deshalb weder ersetzt noch umsortiert, auch bei beschädigten Fragen.
- Unbedenkliche Inhaltsänderungen: neue IDs oberhalb 273, belegte Textkorrekturen, nachvollziehbare aktuelle Schlüssel, Erklärungen und Sperrmetadaten. Historische Punkte und `full` werden auch bei neuen Schlüsseln **nicht** umgeschrieben. Neue Versuche speichern zusätzlich `questionRevision`, `answerKey` und `correctCount`.
- Alte Versuche besitzen keinen Schlüssel-Snapshot. Der frühere Katalogschlüssel ist im Audit erhalten; es ist jedoch nicht beweisbar, mit welcher noch älteren App-Fassung ein einzelner Browser-Versuch entstanden ist. Eine rückwirkende Neubewertung oder Behauptung eines damaligen Schlüssels ist daher ausgeschlossen.
- Vor Änderungen wurden `questions.json`, `app.js`, `sw.js`, `index.html`, `README.md` und `docs/DATEN.md` nach `private/catalog-audit-before/` kopiert. Die Sicherung liegt absichtlich im ignorierten privaten Verzeichnis. Der maschinenlesbare Audit enthält zusätzlich alle ursprünglichen IDs, Optionen, Schlüssel und Objektprüfsummen sowie vollständige Vorher/Nachher-Datensätze jeder Änderung.
- **Kein Zugriff auf echten Browser-Speicher.** Es wurden keine echten Nutzerdaten gesichert oder verändert. Die automatisierten Kompatibilitätstests verwenden realistische synthetische Daten und die tatsächlichen Funktionen aus `app.js` in einer isolierten DOM/Storage-Testumgebung.
- Der JSON-Export bleibt unter demselben Button verfügbar. Er exportiert jetzt alle DB-Felder einschließlich Lesemarkierungen und Notizen, außerdem die unveränderten rohen App-Storage-Werte inklusive Theme und letzter Antwortreihenfolgen. Bestehende Top-Level-Felder `schemaVersion: 1`, `attempts` und `settings` bleiben kompatibel; `backup.version: 2` kennzeichnet die vollständige Ergänzung. Der Export schreibt nichts in Storage. Keine automatische Wiederherstellung oder Migration wurde hinzugefügt.

## Phase 2: Import und Vergleichsmethode

Die Originaldatei bleibt bytegenau unverändert (SHA-256 siehe JSON). Einheitlicher äußerer Aufbau: `{"questions": [{"q": ..., "answers": [{"text": ..., "id": ...}], "rightids": "..."}]}`. 177 Multiple-Choice-Fragen, 167 mit vier, 6 mit fünf, 4 mit drei Optionen. Keine eigenen Frage-IDs, Kapitel, Seiten oder Erklärungen. `I001` bis `I177` bezeichnen ausschließlich die ursprünglichen 1-basierten Dateipositionen, keine behaupteten Original-IDs.

Die normalisierte Arbeitsfassung ist je Zeile unter `normalized` in der JSON-Datei erhalten, zusammen mit dem unveränderten Importobjekt unter `raw`. Kapitel sind redaktionell vom zugeordneten Bestand abgeleitet; neue Rechnungswesenfragen wurden bewusst „Kosten- und Erfolgsrechnung“ zugeordnet, statt die aus Seitenbereichen historisch ungenaue Kapitelgrenze zu übernehmen.

Kandidatensuche: Unicode-/Leerraum-/Interpunktionsnormalisierung, Vergleich des Stamms und der einzelnen Antworttexte, anschließend bijektive Optionszuordnung bei gleicher Optionszahl. ε/epsilon und Notationsvarianten werden berücksichtigt. Es gibt keine vollständigen LaTeX-Aufgaben oder Rechenformeln, deren Bedeutung eine zusätzliche LaTeX-Engine erfordern würde. Zahlen, Negationen, „vor/nach“, Marktform und kumulierter/periodischer Verlauf wurden anschließend semantisch geprüft. Die maschinellen `candidate`-Treffer bleiben als Suchprotokoll erhalten; die verbindliche Zuordnung ist `existingId`, nicht der Kandidat. So wurden unter anderem Oligopol statt Monopol, vertikale statt horizontale Arbeitsteilung und volle statt variable Stückkosten richtiggestellt.

Strukturprobleme:

| Import | Auffälligkeit |
|---|---|
| I032 | Fragment/Platzhalter in Antworttext |
| I046 | Fragment/Platzhalter in Antworttext |
| I061 | Fragment/Platzhalter in Antworttext |
| I068 | Fragment/Platzhalter in Antworttext |
| I078 | Fragment/Platzhalter in Antworttext |
| I081 | Fragment/Platzhalter in Antworttext |
| I082 | Fragment/Platzhalter in Antworttext |
| I125 | Angekündigte Anzahl stimmt nicht mit Schlüssel überein |
| I142 | Antwort-IDs nicht fortlaufend 1..n |
| I161 | Fragment/Platzhalter in Antworttext |

Redaktionelle Kapitelzuordnung (keine Kapitelangaben in der Importdatei):

| Kapitel | Importfragen | Finaler Bestand | Bewertbar |
|---|---:|---:|---:|
| Absatzmanagement | 16 | 20 | 17 |
| Finanzmanagement | 14 | 16 | 16 |
| Innovationsmanagement | 14 | 15 | 13 |
| Kosten- und Erfolgsrechnung | 22 | 34 | 29 |
| Logistik | 16 | 22 | 21 |
| Organisation | 13 | 19 | 17 |
| Personalmanagement | 18 | 20 | 19 |
| Produktion | 18 | 18 | 15 |
| Qualitätsmanagement | 15 | 18 | 16 |
| Strategisches Management | 14 | 22 | 19 |
| Unternehmenskooperation | 17 | 28 | 15 |

Angekündigte richtige Antworten im Import: 1: 49 Fragen, 2: 117 Fragen, 3: 11 Fragen.

Die Strukturerkennung ist nur eine zusätzliche Hilfe: Auch syntaktisch gültige Datensätze können fachlich falsch sein. Ein Antwort-ID-Fehler besteht bei I142 (`12` statt `1`); I125 kündigt drei richtige Antworten an, enthält aber nur zwei im Schlüssel. Weitere abgebrochene Texte und falsche Schlüssel sind in der Einzelprüfung dokumentiert.

## Phase 3/4: Änderungen am Bestand

Die folgenden Einträge geben alle Inhaltsänderungen wieder. Vollständige alte und neue Objekte stehen in `changes` der JSON-Datei. Antwortnummern in diesem Markdown sind 1-basiert; JSON-Schlüssel bleiben 0-basiert.

### #51: Korrektur

Kapitel: Qualitätsmanagement. Import: I161. Status: belegt.

Der Fragestamm auf PDF-Seite 15 lautet „Welche Aussage über eines der sieben Qualitätswerkzeuge (Q7) stimmt nicht?“. Die Optionen und Lösung 3 stehen auf Seite 16. Histogramme zeigen Häufigkeitsverteilungen; die regelmäßige Prozessüberwachung gehört zur Regelkarte. Der Import hatte die Negation durch einen anderen Fragetitel ersetzt. Optionen und Schlüssel bleiben erhalten.

- `text` vorher: Welche Aussagen über die sieben Qualitätswerkzeuge (Q7) sind richtig?
- `text` nachher: Welche Aussage über eines der sieben Qualitätswerkzeuge (Q7) stimmt nicht?
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: verified
- ID und alle Originaloptionen unverändert.

Quellen: pdf, q7.

### #67: Korrektur

Kapitel: Absatzmanagement. Import: I151. Status: belegt.

Inverse Nachfrage bildet die Menge auf den erzielbaren Preis ab, also Antwort 3. Antwort 4 ist die direkte Nachfragefunktion; Angebot und Reklamationen sind andere Sachverhalte. Schon der Erklärungstext auf PDF-Seite 21 widerspricht dem dortigen Schlüssel 4.

- `answers` vorher: 4
- `answers` nachher: 3
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: verified
- ID und alle Originaloptionen unverändert.

Quellen: pdf, monopoly.

### #75: Korrektur

Kapitel: Absatzmanagement. Import: I076. Status: belegt.

Im üblichen differenzierbaren Monopolmodell mit nichtnegativen Grenzkosten und positivem Absatz gilt im inneren Gewinnmaximum Grenzerlös = Grenzkosten. Ein inelastischer Bereich mit negativem Grenzerlös ist dann ausgeschlossen. Daher sind 1 und 2 richtig; Grenzerlös = 0 gilt speziell für Erlösmaximierung, Grenzgewinn = Grenzkosten ist keine allgemeine Optimalitätsbedingung. Randlösungen oder negative Grenzkosten fallen nicht unter dieses Lehrmodell.

- `answers` vorher: 2
- `answers` nachher: 1, 2
- `correctCount` vorher: 1
- `correctCount` nachher: 2
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: verified
- ID und alle Originaloptionen unverändert.

Quellen: pdf, monopoly.

### #160: Korrektur

Kapitel: Finanzmanagement. Import: I093. Status: belegt.

Der erste Teil des Fragestamms steht unmittelbar vor den Optionen auf PDF-Seite 49. Wiederhergestellt wird nur der verlorene Satzanfang; Optionen, Schlüssel und IDs bleiben gleich. Die dortigen Tätigkeiten Vergleich, Auswahl einer Anpassung und Abweichungsanalyse gehören zu Check/Act.

- `text` vorher: Liquiditätsmanagements fallen folgende Aufgaben an
- `text` nachher: In der Kontrolle-Aktivität und der Lenkungsaktivität des Liquiditätsmanagements fallen folgende Aufgaben an
- `contextWarning` vorher: Der Fragestamm beginnt mitten im Satz und benötigt die Originalfrage.
- `contextWarning` nachher: 
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: verified
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #223: Korrektur

Kapitel: Unternehmenskooperation. Import: zusätzliche Bestandsprüfung. Status: belegt.

Vollständiger Fragestamm von PDF-Seite 67 wiederhergestellt. Keine Veränderung der Optionen oder des studentischen Lösungsschlüssels; wegen fünf Optionen weiterhin nur Lesebuch. Diese Textreparatur ist keine unabhängige Bestätigung der fachlichen Lösung.

- `text` vorher: Entscheidungsfindung angebracht ist. Welche Kritierien schlagen Sie vor:
- `text` nachher: Situationsgerechtes Führen: vor allem Fachexperten in Führungsrollen sind meistens überzeugt, dass ihre herausragende Expertise die Grundlage für alle Entscheidungen sein sollte und fürchten, dass zu viel Delegation die Arbeitsqualität gefährden könnte. Erklären Sie dieser Zielgruppe die Kriterien auf die Sie achten sollen, um zu entscheiden ob eine autoritäre Alleinentscheidung oder eine Partizpativ-delegative Form der Entscheidungsfindung angebracht ist. Welche Kritierien schlagen Sie vor:
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: source-only
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #225: Korrektur

Kapitel: Unternehmenskooperation. Import: zusätzliche Bestandsprüfung. Status: belegt.

Vollständiger Fragestamm von PDF-Seite 68 wiederhergestellt. Antwortpositionen und bisheriger Schlüssel bleiben erhalten; fünf Optionen bleiben außerhalb bewerteter Modi. Die Textwiederherstellung bestätigt nicht unabhängig den Schlüssel.

- `text` vorher: werden. Welche Rollenbündel wird sie dabei mit ihrem Coach besprechen?
- `text` nachher: Melanie Müller ist eine sehr engagierte Führungskraft bei Rosenbauer Marketing. Sie hat das Ziel als Führungskraft noch wirksamer in ihrer Rolle zu werden. Welche Rollenbündel wird sie dabei mit ihrem Coach besprechen?
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: source-only
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #242: Korrektur

Kapitel: Weitere Themen / Nachhaltigkeit. Import: zusätzliche Bestandsprüfung. Status: belegt.

Verlorenen Beginn des Fragestamms wortgetreu aus PDF-Seite 73 ergänzt. Keine fachliche Neubewertung des studentischen Schlüssels; fünf Optionen bleiben nur im Lesebuch.

- `text` vorher: strategische Perspektive nutzt dann spricht er wovon?
- `text` nachher: Die Strategie von Rosenbauer verfolgt das Wechselspiel aus Effizienzorientierung auf Basis bestehender Kompetenzen (u.a. Kernkompetenzen) und die Innovationsorientierung zur Kreation völlig neuer Kompetenzen. In Zeiten großer Dynamik und hoher Wettbewerbsintensität ist es notwendig, dass ständig an inkrementeller Verbesserungen gearbeitet wird und dennoch auch der Blick für die Entwicklung völlig neuer Kompetenzen für die langfristige Zukunft nicht aus den Augen gerät. Wenn der CEO diese strategische Perspektive nutzt dann spricht er wovon?
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: source-only
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #249: Korrektur

Kapitel: Weitere Themen / Nachhaltigkeit. Import: zusätzliche Bestandsprüfung. Status: belegt.

Satzanfang aus PDF-Seite 75 wiederhergestellt. Die erkennbare Unsicherheit in Option 1 bleibt sichtbar; fünf Optionen werden weiterhin nicht benotet. Keine unabhängige fachliche Freigabe des gesamten Schlüssels.

- `text` vorher: Besonderheiten zu beachten
- `text` nachher: Das EBIT– Performance Management umfasst die Budgetierung und Steuerung der EBIT-Erfolgsgrößen. Bei der EBIT–Budgetierung (Planung) gibt es folgende Besonderheiten zu beachten
- `contextWarning` vorher: Der vollständige Fragestamm ist im Import nicht erhalten. Bis zum 1:1-Abgleich mit der PDF-Seite nicht prüfbar.
- `contextWarning` nachher: Option 1 ist bereits im PDF mit „(erklären?)“ unsicher überliefert; nur Lesebuch.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: source-only
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #83: Bewertung gesperrt

Kapitel: Innovationsmanagement. Import: zusätzliche Bestandsprüfung. Status: ungeklärt; nicht bewerten.

Wie bei #82 ist nicht festgelegt, ob periodische Neuadoptionen oder kumulierte Verbreitung gemeint sind. Glocken- und S-Kurve beziehen sich auf verschiedene Größen; der Zweierschlüssel ist ohne diese Abgrenzung nicht eindeutig.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Wie bei #82 ist nicht festgelegt, ob periodische Neuadoptionen oder kumulierte Verbreitung gemeint sind. Glocken- und S-Kurve beziehen sich auf verschiedene Größen; der Zweierschlüssel ist ohne diese Abgrenzung nicht eindeutig.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #114: Bewertung gesperrt

Kapitel: Strategisches Management. Import: I031. Status: ungeklärt; nicht bewerten.

Abschreibung bildet nutzungsbedingte Wertminderung ab, erzwingt aber keine Ersatzinvestition am Ende einer Nutzungsdauer. Weiterbenutzung oder Stilllegung sind möglich. Die verlangte Zweierlösung setzt einen nicht genannten Ersatzbedarf voraus.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Abschreibung bildet nutzungsbedingte Wertminderung ab, erzwingt aber keine Ersatzinvestition am Ende einer Nutzungsdauer. Weiterbenutzung oder Stilllegung sind möglich. Die verlangte Zweierlösung setzt einen nicht genannten Ersatzbedarf voraus.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, accounting.

### #218: Bewertung gesperrt

Kapitel: Unternehmenskooperation. Import: I088. Status: ungeklärt; nicht bewerten.

Die Aussage „kann zu Terminverlusten und Qualitätseinbußen führen“ beschreibt ein mögliches Kooperationsrisiko und kann nicht generell als unzutreffend gelten. Der Zweierschlüssel markiert sie dennoch als falsch. Keine belegte eindeutige Fassung; Optionen bleiben unverändert.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Die Aussage „kann zu Terminverlusten und Qualitätseinbußen führen“ beschreibt ein mögliches Kooperationsrisiko und kann nicht generell als unzutreffend gelten. Der Zweierschlüssel markiert sie dennoch als falsch. Keine belegte eindeutige Fassung; Optionen bleiben unverändert.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #202: Bewertung gesperrt

Kapitel: Unternehmenskooperation. Import: I078. Status: ungeklärt; nicht bewerten.

Option 4 enthält bereits im PDF einen [?]-Platzhalter. Der genaue Vergleich der Koordinationsformen ist damit nicht vollständig überliefert. Ohne vollständige Antwortoption nicht benoten.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Option 4 enthält bereits im PDF einen [?]-Platzhalter. Der genaue Vergleich der Koordinationsformen ist damit nicht vollständig überliefert. Ohne vollständige Antwortoption nicht benoten.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #208: Bewertung gesperrt

Kapitel: Unternehmenskooperation. Import: I068. Status: ungeklärt; nicht bewerten.

Option 1 enthält bereits im PDF „echten[?]“. Auch ein ungewählter beschädigter Ablenker muss vor automatischer Bewertung vollständig geprüft sein.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Option 1 enthält bereits im PDF „echten[?]“. Auch ein ungewählter beschädigter Ablenker muss vor automatischer Bewertung vollständig geprüft sein.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #268: Bewertung gesperrt

Kapitel: Weitere Themen / Nachhaltigkeit. Import: zusätzliche Bestandsprüfung. Status: ungeklärt; nicht bewerten.

Drei Antwortoptionen brechen mit Auslassungspunkten ab; aus den vorhandenen Angaben lässt sich ihr vollständiger Wahrheitsgehalt nicht sicher beurteilen. Keine bewertete Nutzung.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Drei Antwortoptionen brechen mit Auslassungspunkten ab; aus den vorhandenen Angaben lässt sich ihr vollständiger Wahrheitsgehalt nicht sicher beurteilen. Keine bewertete Nutzung.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #272: Bewertung gesperrt

Kapitel: Weitere Themen / Nachhaltigkeit. Import: zusätzliche Bestandsprüfung. Status: ungeklärt; nicht bewerten.

Die vierte Antwortoption ist auf „Klare Rollendefinitionen ...“ verkürzt. Ohne Volltext ist nicht sicher, warum sie gegenüber Vertrauen, Partizipation und gemeinsamen Werten ausgeschlossen wird.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Die vierte Antwortoption ist auf „Klare Rollendefinitionen ...“ verkürzt. Ohne Volltext ist nicht sicher, warum sie gegenüber Vertrauen, Partizipation und gemeinsamen Werten ausgeschlossen wird.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #1: Bewertung gesperrt

Kapitel: Produktion. Import: I051, I097, I098. Status: ungeklärt; nicht bewerten.

Grundstück ist bei betrieblicher Nutzung selbst ein Betriebsmittel bzw. Produktionsfaktor. Der Schlüssel mit genau zwei Antworten schließt es ohne Modellabgrenzung aus. Die PDF-Faktorliste nennt Betriebsmittel. Keine willkürliche Änderung des Originals.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Grundstück ist bei betrieblicher Nutzung selbst ein Betriebsmittel bzw. Produktionsfaktor. Der Schlüssel mit genau zwei Antworten schließt es ohne Modellabgrenzung aus. Die PDF-Faktorliste nennt Betriebsmittel. Keine willkürliche Änderung des Originals.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #2: Bewertung gesperrt

Kapitel: Produktion. Import: I022. Status: ungeklärt; nicht bewerten.

Gutenberg ist ausdrücklich eine bekannte Produktionsfunktion (auch laut Erklärung auf PDF-Seite 1), wird aber als Option 2 ausgeschlossen; Option 1 enthält schon zwei Funktionsnamen. Original und Import haben unterschiedliche Optionen und Anzahlen. Ohne belegte eindeutige Fassung nicht bewerten.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Gutenberg ist ausdrücklich eine bekannte Produktionsfunktion (auch laut Erklärung auf PDF-Seite 1), wird aber als Option 2 ausgeschlossen; Option 1 enthält schon zwei Funktionsnamen. Original und Import haben unterschiedliche Optionen und Anzahlen. Ohne belegte eindeutige Fassung nicht bewerten.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #12: Bewertung gesperrt

Kapitel: Produktion. Import: I067. Status: ungeklärt; nicht bewerten.

PPS wickelt Kundenaufträge ab; „generiert Kundenaufträge“ in Option 4 ist damit nicht gleichbedeutend. Der PDF-Schlüssel 3 & 4 und der Import 1 & 2 sind beide nicht ausreichend belegt. Option 3 ist sicher, zweite Antwort ungeklärt.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: PPS wickelt Kundenaufträge ab; „generiert Kundenaufträge“ in Option 4 ist damit nicht gleichbedeutend. Der PDF-Schlüssel 3 & 4 und der Import 1 & 2 sind beide nicht ausreichend belegt. Option 3 ist sicher, zweite Antwort ungeklärt.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, pps.

### #40: Bewertung gesperrt

Kapitel: Logistik. Import: I134. Status: ungeklärt; nicht bewerten.

PDF nennt 3, Import nennt 4. Lieferantenbeziehungen zu verbessern ist grundsätzlich mit Entwicklung vereinbar; „Unterstützung durch den Lieferanten“ bezeichnet die umgekehrte Richtung. Ohne konkrete Lehrdefinition des Maßnahmenkatalogs bleibt der genaue Prüfungswortlaut strittig; alten Schlüssel nicht still übernehmen.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: PDF nennt 3, Import nennt 4. Lieferantenbeziehungen zu verbessern ist grundsätzlich mit Entwicklung vereinbar; „Unterstützung durch den Lieferanten“ bezeichnet die umgekehrte Richtung. Ohne konkrete Lehrdefinition des Maßnahmenkatalogs bleibt der genaue Prüfungswortlaut strittig; alten Schlüssel nicht still übernehmen.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, supplier.

### #45: Bewertung gesperrt

Kapitel: Qualitätsmanagement. Import: I014. Status: ungeklärt; nicht bewerten.

Import schreibt in Check „vor“, Original „nach“. Das ist fachlich entscheidend. Check prüft Ergebnisse nach Do. Die Abgrenzung von „Act = umsetzen“ und „Plan = Voraussetzungen schaffen“ ist im Original unscharf gegenüber gängigen PDCA-Definitionen. Keine eindeutige Zweierlösung ohne LV-Konvention.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Import schreibt in Check „vor“, Original „nach“. Das ist fachlich entscheidend. Check prüft Ergebnisse nach Do. Die Abgrenzung von „Act = umsetzen“ und „Plan = Voraussetzungen schaffen“ ist im Original unscharf gegenüber gängigen PDCA-Definitionen. Keine eindeutige Zweierlösung ohne LV-Konvention.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, pdca.

### #56: Bewertung gesperrt

Kapitel: Qualitätsmanagement. Import: I160. Status: ungeklärt; nicht bewerten.

Die Antworten 3 und 4 sind allgemeine Aussagen über Q7-Werkzeuge und sachlich zumindest teilweise zutreffend, aber keine M7-Zuordnung. Zudem sind Eingriffs- und Toleranzgrenzen zu unterscheiden. Der Fragetext grenzt dies nicht klar ab. Keine eindeutige Zweierbewertung.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Die Antworten 3 und 4 sind allgemeine Aussagen über Q7-Werkzeuge und sachlich zumindest teilweise zutreffend, aber keine M7-Zuordnung. Zudem sind Eingriffs- und Toleranzgrenzen zu unterscheiden. Der Fragetext grenzt dies nicht klar ab. Keine eindeutige Zweierbewertung.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, q7, m7.

### #69: Bewertung gesperrt

Kapitel: Absatzmanagement. Import: I016. Status: ungeklärt; nicht bewerten.

PDF und Import wählen Marktgleichgewicht als einzige Antwort. Zugleich ist Preisnehmerschaft eine Standardannahme vollständiger Konkurrenz. „Vollkommener Markt“ und Wettbewerb werden hier ohne explizite LV-Definition vermischt. Nicht durch eine allgemeine externe Definition überschreiben.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: PDF und Import wählen Marktgleichgewicht als einzige Antwort. Zugleich ist Preisnehmerschaft eine Standardannahme vollständiger Konkurrenz. „Vollkommener Markt“ und Wettbewerb werden hier ohne explizite LV-Definition vermischt. Nicht durch eine allgemeine externe Definition überschreiben.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, monopoly.

### #74: Bewertung gesperrt

Kapitel: Absatzmanagement. Import: I118. Status: ungeklärt; nicht bewerten.

Die fallende inverse Nachfrage in Option 2 ist ebenfalls ein Hinweis auf Marktmacht. Verdrängung in Option 4 ist weder zwingend noch eine allgemeine Definition. Der Zweier-Schlüssel 1 & 4 bleibt ohne LV-Kontext zweifelhaft.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Die fallende inverse Nachfrage in Option 2 ist ebenfalls ein Hinweis auf Marktmacht. Verdrängung in Option 4 ist weder zwingend noch eine allgemeine Definition. Der Zweier-Schlüssel 1 & 4 bleibt ohne LV-Kontext zweifelhaft.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, monopoly.

### #82: Bewertung gesperrt

Kapitel: Innovationsmanagement. Import: I008. Status: ungeklärt; nicht bewerten.

Glockenkurve beschreibt neue Adoptionen pro Periode, S-Kurve die kumulierte Verbreitung. „im Zeitablauf“ unterscheidet diese Größen nicht. Markteinführung und breite Diffusion sind außerdem nicht gleichzusetzen. PDF und Import stimmen zwar überein, aber das beweist die Dreierlösung nicht.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Glockenkurve beschreibt neue Adoptionen pro Periode, S-Kurve die kumulierte Verbreitung. „im Zeitablauf“ unterscheidet diese Größen nicht. Markteinführung und breite Diffusion sind außerdem nicht gleichzusetzen. PDF und Import stimmen zwar überein, aber das beweist die Dreierlösung nicht.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #112: Bewertung gesperrt

Kapitel: Strategisches Management. Import: I081. Status: ungeklärt; nicht bewerten.

Nicht lagerbar in Option 1 ist für Material unzutreffend; der Import kehrt die Aussage um. Nicht jeder verbrauchte Betriebsstoff geht körperlich ins Produkt ein. Der pauschale Schlüssel und die beschädigten Importoptionen erlauben keine zuverlässige Bewertung.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Nicht lagerbar in Option 1 ist für Material unzutreffend; der Import kehrt die Aussage um. Nicht jeder verbrauchte Betriebsstoff geht körperlich ins Produkt ein. Der pauschale Schlüssel und die beschädigten Importoptionen erlauben keine zuverlässige Bewertung.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #113: Bewertung gesperrt

Kapitel: Strategisches Management. Import: I116. Status: ungeklärt; nicht bewerten.

Umsatz ist gewöhnlich Umsatzerlös. „zum Umsatz die Umsatzkosten addiert“ ist dann falsch. Die PDF-Erklärung meint offenbar Umsatzergebnis statt Umsatz. Das Wort darf ohne belegte Originalfassung nicht still ersetzt werden; Import wiederholt die Unschärfe.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Umsatz ist gewöhnlich Umsatzerlös. „zum Umsatz die Umsatzkosten addiert“ ist dann falsch. Die PDF-Erklärung meint offenbar Umsatzergebnis statt Umsatz. Das Wort darf ohne belegte Originalfassung nicht still ersetzt werden; Import wiederholt die Unschärfe.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, cost.

### #134: Bewertung gesperrt

Kapitel: Kosten- und Erfolgsrechnung. Import: I061. Status: ungeklärt; nicht bewerten.

Optionen 2 und 3 enthalten bereits im PDF [?]/[??]. Das 1-Faktormodell erklärt zwar die Absatzmenge, ersetzt aber die fehlenden Antworttexte nicht. Bis zur vollständigen Originalfassung nicht benoten.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Optionen 2 und 3 enthalten bereits im PDF [?]/[??]. Das 1-Faktormodell erklärt zwar die Absatzmenge, ersetzt aber die fehlenden Antworttexte nicht. Bis zur vollständigen Originalfassung nicht benoten.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #173: Bewertung gesperrt

Kapitel: Organisation. Import: I052. Status: ungeklärt; nicht bewerten.

Optionen 1 und 3 sind bis auf Interpunktion identisch, aber nur 1 wird als richtig gewertet. Der Fehler steht schon im PDF. Die andere Importoption ist keine belegte Wiederherstellung; Optionen bleiben aus Rücksicht auf historische Antwortindizes erhalten.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Optionen 1 und 3 sind bis auf Interpunktion identisch, aber nur 1 wird als richtig gewertet. Der Fehler steht schon im PDF. Die andere Importoption ist keine belegte Wiederherstellung; Optionen bleiben aus Rücksicht auf historische Antwortindizes erhalten.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #185: Bewertung gesperrt

Kapitel: Personalmanagement. Import: I125. Status: ungeklärt; nicht bewerten.

Pensionierungen verändern den Personalbestand/Ersatzbedarf, Effizienz und Organisationsstruktur den Einsatzbedarf. PDF nennt Pensionierungen und Struktur; Import hat dieselbe Auswahl, aber widersprüchlich drei richtige Antworten angekündigt. Ohne präzise LV-Begriffsdefinition kein gesicherter Schlüssel.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Pensionierungen verändern den Personalbestand/Ersatzbedarf, Effizienz und Organisationsstruktur den Einsatzbedarf. PDF nennt Pensionierungen und Struktur; Import hat dieselbe Auswahl, aber widersprüchlich drei richtige Antworten angekündigt. Ohne präzise LV-Begriffsdefinition kein gesicherter Schlüssel.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #205: Bewertung gesperrt

Kapitel: Unternehmenskooperation. Import: I172. Status: ungeklärt; nicht bewerten.

Die gewählten Merkmale Dezentralität und Reversibilität passen eher zu Netzwerken als zu Hierarchien. PDF und Import scheinen die Vergleichsrichtung zu vertauschen. Der Wortlaut wird nicht spekulativ umgekehrt; genaue Zweierlösung ungeklärt.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Die gewählten Merkmale Dezentralität und Reversibilität passen eher zu Netzwerken als zu Hierarchien. PDF und Import scheinen die Vergleichsrichtung zu vertauschen. Der Wortlaut wird nicht spekulativ umgekehrt; genaue Zweierlösung ungeklärt.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #207: Bewertung gesperrt

Kapitel: Unternehmenskooperation. Import: I150. Status: ungeklärt; nicht bewerten.

Neue Institutionenökonomie umfasst auch den Transaktionskostenansatz. Sie pauschal als keinen Erklärungsansatz zu markieren ist ohne enge LV-Taxonomie problematisch. PDF und Import stimmen überein, eine offizielle Definition fehlt.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Neue Institutionenökonomie umfasst auch den Transaktionskostenansatz. Sie pauschal als keinen Erklärungsansatz zu markieren ist ohne enge LV-Taxonomie problematisch. PDF und Import stimmen überein, eine offizielle Definition fehlt.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #255: Bewertung gesperrt

Kapitel: Weitere Themen / Nachhaltigkeit. Import: zusätzliche Bestandsprüfung. Status: ungeklärt; nicht bewerten.

Das PDF beginnt ebenfalls nur mit „Produktionskoeffizient dient in der“. Es gibt keinen verlorenen Satzanfang, der aus diesem Material belegbar ergänzt werden könnte. Spezialmodell und Lösung sind ohne Folien nicht ausreichend prüfbar.

- `contextWarning` vorher: Der Fragestamm endet mitten im Satz und ist ohne den restlichen Originaltext nicht eindeutig.
- `contextWarning` nachher: Das PDF beginnt ebenfalls nur mit „Produktionskoeffizient dient in der“. Es gibt keinen verlorenen Satzanfang, der aus diesem Material belegbar ergänzt werden könnte. Spezialmodell und Lösung sind ohne Folien nicht ausreichend prüfbar.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf.

### #256: Bewertung gesperrt

Kapitel: Weitere Themen / Nachhaltigkeit. Import: zusätzliche Bestandsprüfung. Status: ungeklärt; nicht bewerten.

Option 3 nennt Vermögen = Eigenkapital weniger Schulden. Richtig wäre Vermögen = Eigenkapital plus Schulden. PDF-Schlüssel 3 & 4 ist daher offensichtlich widersprüchlich. Originaloption bleibt unverändert; eine eindeutige Zweierlösung ist nicht vorhanden.

- `contextWarning` vorher: nicht gesetzt
- `contextWarning` nachher: Option 3 nennt Vermögen = Eigenkapital weniger Schulden. Richtig wäre Vermögen = Eigenkapital plus Schulden. PDF-Schlüssel 3 & 4 ist daher offensichtlich widersprüchlich. Originaloption bleibt unverändert; eine eindeutige Zweierlösung ist nicht vorhanden.
- `assessmentStatus` vorher: nicht gesetzt
- `assessmentStatus` nachher: unresolved
- ID und alle Originaloptionen unverändert.

Quellen: pdf, accounting.

### #274: Ergänzung

Kapitel: Kosten- und Erfolgsrechnung. Import: I015. Status: belegt; nur Lesebuch (3 Optionen).

Die GuV erfasst periodische Erträge und Aufwendungen. Antwort 3 trifft den im lokalen Katalog verwendeten Kostenbegriff; 1 und 2 behaupten jeweils unzutreffend nur ein Gliederungsverfahren. Fachlich ist Aufwand von kalkulatorischen Kosten zu unterscheiden.

Vorher: nicht vorhanden.

Neu: Die G&V ...

- 1: kann nur nach dem Gesamtkostenverfahren gegliedert werden. (falsch)
- 2: kann nur nach dem Umsatzkostenverfahren gegliedert werden (falsch)
- 3: zeigt die im Zuge der Leistungserstellung angefallenen Kosten (richtig)

Quellen: pdf, accounting.

### #275: Ergänzung

Kapitel: Kosten- und Erfolgsrechnung. Import: I059. Status: belegt; nur Lesebuch (3 Optionen).

Potenzialfaktoren werden zur Leistungserstellung gebraucht. Verkaufen oder einmaliges Verbrauchen beschreibt ihre Funktion nicht. Personal und Betriebsmittel sind Beispiele; Verschleiß steht dem wiederholten Gebrauch nicht entgegen.

Vorher: nicht vorhanden.

Neu: Potenzialfaktoren werden im Zuge der Leisungserstellung

- 1: gebraucht (richtig)
- 2: verkauft (falsch)
- 3: verbraucht (falsch)

Quellen: pdf.

### #276: Ergänzung

Kapitel: Kosten- und Erfolgsrechnung. Import: I075. Status: belegt; nur Lesebuch (3 Optionen).

Im hier verwendeten GuV-Schema folgt auf EBIT das Finanzergebnis und anschließend die Ertragsteuer. Beide erklären die Differenz zum Jahresüberschuss/-fehlbetrag. Die Antworten 2 und 3 lassen jeweils einen Bestandteil aus; Sondereffekte anderer Rechnungslegungsschemata sind nicht Gegenstand dieses Schemas.

Vorher: nicht vorhanden.

Neu: Die Differenz zwischen EBIT und dem Jahresüberschuss/-fehlbetrag ...

- 1: wird durch das Finanzergebnis und Ertragssteuern begründet (richtig)
- 2: wird nur durch Ertragssteern begründet (falsch)
- 3: wird nur durch das Finanzergebnis begründet (falsch)

Quellen: pdf, income.

### #277: Ergänzung

Kapitel: Kosten- und Erfolgsrechnung. Import: I168. Status: belegt; Training/Prüfung.

Bei einer einheitlichen Produktart und positiver Absatzmenge gilt Umsatz = Preis × Absatzmenge, also Preis = Umsatz / Absatzmenge. Variable Kosten pro Menge sind variable Stückkosten; fixe plus variable Stückkosten ergeben volle Stückkosten; das Addieren von Kosten liefert keinen Verkaufspreis.

Vorher: nicht vorhanden.

Neu: Der Verkaufspreis Einheit rechnet sich indem...

- 1: Variable Umsatzkosten durch Absatzmenge (falsch)
- 2: der Umsatz durch die Absatzmenge dividiert wird. (richtig)
- 3: fixe Einheitskosten plus variable Einheitskosten (falsch)
- 4: Umsatzkosten plus Selbstkosten (falsch)

Quellen: pdf, cost.

### #278: Ergänzung

Kapitel: Qualitätsmanagement. Import: I177. Status: belegt; Training/Prüfung.

Regelkarte, Fehlersammelliste und Stratifikation gehören zu den klassischen Q7. PDCA ist ein Verbesserungszyklus. Varianten der siebten Werkzeugliste ändern diese Abgrenzung nicht.

Vorher: nicht vorhanden.

Neu: Welches der folgenden Tools zählt nicht zu den sieben Qualitätswerkzeugen (Q7)?

- 1: Qualitätsregelkarte (falsch)
- 2: Fehlersammelliste oder Aufnahmebogen (falsch)
- 3: PDCA-Zyklus (richtig)
- 4: Grafische Darstellung/Stratifikation (falsch)

Quellen: q7, pdca.

## Konflikte der Lösungsschlüssel

Eine andere Zahl allein ist kein Konflikt: Antworten müssen zuerst nach ihrem Text zugeordnet werden. Die folgende Tabelle enthält die 12 echten C-Zuordnungen. „Bestand bestätigt“ bedeutet eine dokumentierte Ablehnung des Imports, keine Übernahme. Bei ungeklärten Fällen bleiben alte Quellenschlüssel sichtbar, die automatische Bewertung ist gesperrt.

| Import / Bestand / Frage | Alter Bestand | Studentischer Import | Geprüfte Lösung (Bestandsnummern) | Ergebnis und Begründung | Quellen |
|---|---|---|---|---|---|
| I044 / #118 / Eine lineare Kostenfunktion besitzt ... (2) | 1, 3 | 14 (Importnummern) | 1, 3 | Bestand bestätigt: Bei K(x)=Kf+kv*x ist K′(x)=kv konstant. Bestand 1,3 richtig; Import 1,4 verwechselt konstante mit veränderten variablen Stückkosten. | import, pdf, cost |
| I056 / #55 / Welche der folgenden Aussagen über eines der sieben neuen Qualitätswerkzeuge (M7/N7) sind richtig? (2) | 2, 4 | 34 (Importnummern) | 2, 4 | Bestand bestätigt: Zuordnung zur richtigen Bestandsvariante #55, nicht zur negierten #58. Import markiert Fehlererfassung und kritischen Pfad; korrekt im M7-Sinn sind Verknüpfung von Arbeitspaketen und kritischer Pfad. | import, pdf, q7, m7 |
| I067 / #12 / Die Produktionsplanung und -steuerung ... (2) | 3, 4 | 12 (Importnummern) | ungeklärt | ungeklärt: Nach Optionenzuordnung Import Lean und Terminplanung, Bestand Terminplanung und generiert Kundenaufträge. Beide Zweierlösungen unzureichend belegt; #12 gesperrt. | import, pdf, pps |
| I076 / #75 / Setzt ein Unternehmen im Monopol den Preis für sein Produkt gewinnoptimal, dann ... (2) | 2 | 12 (Importnummern) | 1, 2 | korrigiert: Bestand markiert nur Grenzerlös = Grenzkosten. Im Standardmodell ist auch Ausschluss des inelastischen Bereichs richtig. #75 auf 1,2 und Anzahl 2 korrigiert. | import, pdf, monopoly |
| I113 / #175 / Welche Aussagen zu lateralen Koordinationsmechanismen treffen zu? (2) | 2, 4 | 13 (Importnummern) | 2, 4 | Bestand bestätigt: Bestand wählt Abstimmung und Produktkoordination; Import Weisungserteilung über Fayol-Brücke und Abstimmung. Fayol-Brücke schafft kein eigenes Weisungsrecht. Bestehende redaktionelle Entscheidung #175 beibehalten. | import, pdf |
| I121 / #58 / Welche der folgenden Aussagen über eines der sieben neuen Qualitätswerkzeuge (M7/N7) sind falsch? (1) | 1, 2 | 4 (Importnummern) | 1, 2 | Bestand bestätigt: Nur eine falsche Aussage im Import angekündigt; Bestand #58 nennt zwei. Im M7-Abgrenzungssinn sind Fehlererfassung/-analyse und garantierte Termineinhaltung beide falsch. Bestand beibehalten; Import nicht als Einantwortfrage übernehmen. | import, pdf, q7, m7 |
| I127 / #11 / Die Arbeitsplanung... (2) | 1, 4 | 14 (Importnummern) | 1, 4 | Bestand bestätigt: Import wählt Auftragsneutralität und mengen-/termin-/kapazitätsmäßige Planung. Bestand #11 wählt Auftragsneutralität und wirtschaftliche Gestaltung. PDF S.3–4 erklärt die Auftragsneutralität; bestehende redaktionelle Lösung beibehalten. | import, pdf, pps |
| I133 / #125 / Wenn Plan- und ist-Werte beim Faktorpreis und beim Faktoreinsatz voneinander abweichen, bestehen die Ist-Kosten aus (1) | nicht freigegeben | 3 (Importnummern) | ungeklärt | ungeklärt: Bestand enthält bewusst keinen freigegebenen Schlüssel: PDF nennt 2 (oder 3). Import wählt 3. Abweichungszerlegung und Sollkostenbezug bleiben konventionsabhängig; #125 weiter gesperrt. | import, pdf |
| I134 / #40 / Was ist keine Maßnahme der Lieferantenentwicklung? (1) | 3 | 4 (Importnummern) | ungeklärt | ungeklärt: Gleiche Optionen, PDF/Bestand 3 gegenüber Import 4. Richtung der finanziellen Unterstützung und Maßnahmendefinition strittig; #40 gesperrt statt studentischen Schlüssel zu kopieren. | import, pdf |
| I143 / #52 / Welche Aussage entspricht nicht der Wahrheit? (1) | 1 | 4 (Importnummern) | 1 | Bestand bestätigt: Korrelationsdiagramm kann keine ABC-Analyse ersetzen; Import 4 ist daher keine Falschaussage. Ishikawa ordnet Ursachen, Pareto priorisiert. Bestand #52 mit Antwort 1 beibehalten. | import, pdf, q7, m7 |
| I145 / #13 / Die Produktionsplanung und -steuerung... (2) | 2, 3 | 34 (Importnummern) | 2, 3 | Bestand bestätigt: Import wählt Zielkonflikte und Lean, Bestand Einsteuerung von Aufträgen und Zielkonflikte. Auftragssteuerung ist Kernaufgabe der PPS, Lean nicht ihre allgemeine Definition. Bestand #13 beibehalten. | import, pdf, pps |
| I151 / #67 / Als inverse Nachfragefunktion bezeichnet man ... (1) | 4 | 3 (Importnummern) | 3 | korrigiert: Inverse Nachfrage p(x) statt direkte Nachfrage x(p): Bestand #67 von Antwort 4 auf 3 korrigiert, Originaloptionen unverändert. | import, pdf, monopoly |

Zusätzliche Konflikte bei beschädigten bzw. nicht gleichwertigen F/D-Varianten (keine künstliche Gleichsetzung der Optionen):

| Import / Bestand | Bestandsschlüssel | Importschlüssel | Untersuchung / Ergebnis |
|---|---|---|---|
| I014 / #45 | 1, 2 | 12 | Check vor/nach Durchführung ist inhaltlich verschieden. Der Import-Schlüssel 12 ist mit „vor“ nicht tragfähig; Bestand #45 ebenfalls gesperrt. Quellen: import, pdf |
| I022 / #2 | 1, 4 | 135 | Bestand enthält Gutenberg zweimal, aber nicht beide als richtig. Fünf Importoptionen lösen die unklare Originalfassung nicht; #2 gesperrt. Quellen: import, pdf |
| I024 / #24 | 3, 4 | 345 | Fünfte Importoption reduziert Lieferantenbestände; dies ist keine zwingende Definition bzw. allgemeine SCM-Folge. Anzahl 3 nicht gesichert. Bestand #24 bleibt als eigene Vieroptionenfassung erhalten. Quellen: import, pdf |
| I026 / #39 | 1, 2 | 125 | Import schließt hohe Produktqualität aus und markiert Nähe zum Endkunden; fachlich sind Qualität, Liefertreue und Flexibilität relevant. Standortnähe kann situationsabhängig ebenfalls relevant sein; kein gesicherter Dreierschlüssel. Bestand #39 hat andere Optionen und wird nicht ersetzt. Quellen: import, pdf |
| I052 / #173 | 1, 2 | 23 | Bestand #173 hat doppelte Antwortoptionen. Import ersetzt eine durch eine andere Aussage; keine belegte Originalkorrektur. #173 gesperrt. Quellen: import, pdf |
| I081 / #112 | 2, 3 | 13 | Import ändert nicht lagerbar zu lagerbar und enthält „werden ... enthalten“ sowie abgeschnittene Mehrfachverwendung. Das ist keine reine Umstellung; Bestand #112 ebenfalls nicht zuverlässig. Quellen: import, pdf |
| I088 / #218 | 1, 4 | 23 | „Kann zu Terminverlusten und Qualitätseinbußen führen“ ist nicht dasselbe wie „Kunde muss meist Kompromisse eingehen“. Risikoaussage nicht generell falsch. Negierter Zweierschlüssel daher ungeklärt. Quellen: import, pdf |
| I091 / #209 | 2, 4 | 14 | Import markiert auch Kosten der Leistungserstellung als Transaktionskosten. Das ist ohne Abgrenzung zu Produktionskosten nicht tragfähig; nur Koordinationskosten eindeutig. #209 hat eine andere zweite richtige Option. Quellen: import, pdf |
| I125 / #185 | 1, 4 | 13 | Angekündigt drei richtige, Schlüssel enthält nur zwei. Zusätzlich Bedarfs-/Bestandsabgrenzung strittig; #185 gesperrt. Quellen: import, pdf |
| I156 / #76 | 3, 4 | 13 | Importoption 3 bricht nach „gleich“ ab. Zudem markiert Import Grenzerlös = Grenzkosten statt Grenzerlös = 0; richtige vollständige Fassung bereits #76. Keine Übernahme. Quellen: import, pdf, monopoly |
| I160 / #56 | 1, 2 | 34 | M7-Stamm mit zwei Q7-Aussagen vermischt; Import ignoriert zugleich richtige Netzplanverknüpfung. Ohne klare Aussage „gehört zu M7“ keine eindeutige Zweierlösung; #56 ebenfalls gesperrt. Quellen: import, pdf, q7, m7 |
| I161 / #51 | 3 | 13 | Bestand #51 hat verlorene Negation über Seitenumbruch, aus PDF S.15–16 repariert. Import ist selbst beschädigt (???), anderer Fragetyp und falsches Histogramm; nicht als Reparaturquelle verwendet. Quellen: import, pdf, q7, m7 |
| I172 / #205 | 2, 4 | 13 | Andere Optionen als #205, aber gleiche mutmaßlich umgekehrte Vergleichsrichtung. Für Hierarchien passen die markierten Netzwerkmerkmale nicht; #205 gesperrt. Quellen: import, pdf |

## Vollständige Einzelzuordnung aller Importfragen

Die Auswahl wird jeweils über die Antworttexte verglichen; Importnummern sind keine Bestandsindizes. Die JSON-Datei enthält zusätzlich sämtliche Antworttexte, beide Ausgangsschlüssel, normalisierte Arbeitsdaten und Optionszuordnung der Suchkandidaten.

| Import | Kategorie | Bestand / neue ID | Kapitel | Frage | Importlösung | Begründung / Aktion |
|---|---|---|---|---|---|---|
| I001 | B | #19 | Logistik | Welche Aussagen zu Lean Production sind richtig? (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I002 | B | #216 | Unternehmenskooperation | Eine Fluglinie, eine Hotelkette und ein Mietwagenunternehmen kooperieren miteinander und bieten Rabette, wenn Kunden Leistungen von mindestens zwei Kooperationspartnern gemeinsam beziehen. Es handelt sich dabei um ein... (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I003 | B | #151 | Finanzmanagement | Die Betriebs-Cash Flow-Funktion modelliert den Betriebs-Cash Flow in Abhängigkeit von... (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I004 | B | #145 | Finanzmanagement | Durch Realisation eines schlechten Absatzszenarios in der ersten Subperiode... (1) | 2 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I005 | B | #193 | Personalmanagement | Bestandteile der Vorauswahlphase in Personalbeschaffungsprozessen sind (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I006 | B | #190 | Personalmanagement | Was spricht für die Rekrutierung über den externen statt dem internen Arbeitsmarkt? (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I007 | B | #163 | Organisation | Nach dem institutionellen Organisationsbegriff... (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I008 | F | #82 | Innovationsmanagement | Diffusion ... (3) | 123 | Beide Quellen haben denselben Schlüssel, aber Diffusionsrate und kumulierter Diffusionsgrad sind im Wortlaut nicht unterschieden. Bestand #82 gesperrt. |
| I009 | B | #107 | Strategisches Management | Echte Preisdifferenzierung liegt vor, wenn ... (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I010 | A | #26 | Logistik | Die Verbrauchsabweichung ... (2) | 23 | Wortlaut, Optionsfolge und Lösung identisch (Anzahlsuffix/Leerraum separat normalisiert). |
| I011 | B | #110 | Strategisches Management | Betrachten Sie das Modell des "Straßendorfs von Hotelling". Die Analyse zeigt, dass ... (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I012 | B | #169 | Organisation | Das Phasenschema der Aufgabenverteilung umfasst die folgenden Schritte (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I013 | B | #188 | Personalmanagement | Bei der Rekrutierung von Mitarbeitern am internen Arbeitsmarkt ... (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I014 | F | #45 | Qualitätsmanagement | Was bedeuten die Begriffe des PDCA-Zyklus? (2) | 12 | Check vor/nach Durchführung ist inhaltlich verschieden. Der Import-Schlüssel 12 ist mit „vor“ nicht tragfähig; Bestand #45 ebenfalls gesperrt. |
| I015 | E | neu #274 | Kosten- und Erfolgsrechnung | Die G&V ... (1) | 3 | Drei Optionen vollständig; im PDF S.35 vorhanden, historischer Import hat die Frage ausgelassen. |
| I016 | F | #69 | Absatzmanagement | Ein vollkommener Markt, ist ein Markt ... (1) | 1 | Gleicher Schlüssel ist keine fachliche Bestätigung: Abgrenzung Marktgleichgewicht/Preisnehmerschaft ungeklärt; #69 gesperrt. |
| I017 | B | #127 | Kosten- und Erfolgsrechnung | Die Bilanz ... (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I018 | B | #16 | Produktion | Welche der folgenden Aussagen sind wahr? (1) | 4 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I019 | B | #176 | Organisation | Was versteht man unter einer "Fayol'schen Brücke"? (1) | 2 | Fayolsche Brücke: direkter Informationsaustausch ohne Weisungsbeziehung. Import nennt Einliniensystem explizit; gleiche Kernantwort, andere Ablenker. |
| I020 | B | #217 | Unternehmenskooperation | Welche der folgenden Aussagen treffen auf virtuelle Unternehmungen zu? (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I021 | B | #31 | Logistik | Welche Aussage ist korrekt? (1) | 4 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I022 | D | #2 | Produktion | Identifizieren Sie bekannte Produktionsfunktionen! (3) | 135 | Bestand enthält Gutenberg zweimal, aber nicht beide als richtig. Fünf Importoptionen lösen die unklare Originalfassung nicht; #2 gesperrt. |
| I023 | B | #164 | Organisation | Arbeitsteilung führt zu ... (2) | 14 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I024 | F | #24 | Logistik | Wodurch definiert sich Supply Chain Management? (3) | 345 | Fünfte Importoption reduziert Lieferantenbestände; dies ist keine zwingende Definition bzw. allgemeine SCM-Folge. Anzahl 3 nicht gesichert. Bestand #24 bleibt als eigene Vieroptionenfassung erhalten. |
| I025 | B | #94 | Strategisches Management | Stage-Gate-Prozesse ... (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I026 | F | #39 | Logistik | Welche der folgenden Kriterien sind relevant für die Lieferantenbewertungen? (3) | 125 | Import schließt hohe Produktqualität aus und markiert Nähe zum Endkunden; fachlich sind Qualität, Liefertreue und Flexibilität relevant. Standortnähe kann situationsabhängig ebenfalls relevant sein; kein gesicherter Dreierschlüssel. Bestand #39 hat andere Optionen und wird nicht ersetzt. |
| I027 | B | #61 | Absatzmanagement | Folgendes sind Funktionen des Handels (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I028 | B | #137 | Kosten- und Erfolgsrechnung | Unter der Break-Even Punkt ... (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I029 | B | #98 | Strategisches Management | Welche der folgenden sind Ursachen für Markteintrittsbarrieren? (2) | 14 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I030 | B | #103 | Strategisches Management | Die grundlegenden Strategien eines Unternehmens sind ... (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I031 | F | #114 | Strategisches Management | Die nutzungsbedingte Wertminderung einer Anlage ... (2) | 24 | Nutzungsbedingte Wertminderung erzwingt keine spätere Investition. Beide studentischen Quellen wählen zwar gleich, aber die zweite richtige Antwort ist ohne Ersatzannahme nicht gesichert; #114 gesperrt. |
| I032 | F | #49 | Qualitätsmanagement | Welche Aussagen über die sieben Qualitätswerkzeuge (Q7) sind wahr? (2) | 13 | Ursache und ??? ist unvollständig. Bestand #49 enthält Wirkung bereits korrekt; keine Übernahme. |
| I033 | F | #78 | Innovationsmanagement | Das Dorfman-Steiner Theoream sagz aus ... (2) | 34 | Letzte Option bricht bei „optimale“ ab; keine verlässliche Rekonstruktion aus studentischem Import. Bestand #78 bleibt bestehen. |
| I034 | B | #204 | Unternehmenskooperation | Eigenschaften der an einer Transaktion beteiligten Akteure sind (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I035 | B | #150 | Finanzmanagement | In der REA-Aktivitätsdiagrammen werden die Aktivitäten dargestellt als ... (1) | 2 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I036 | B | #84 | Innovationsmanagement | Frühkäufer ... (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I037 | B | #20 | Logistik | Teilbereiche der Logistik sind ... (3) | 134 | Zusätzliche Beschaffungslogistik ist im Bestand bereits #21 vertreten; Variante der Teilbereichslisten, kein fehlender Lerninhalt. |
| I038 | B | #21 | Logistik | Teilbereiche der Logistik sind ... (3) | 134 | Entsorgungs-, Transport- und Lagerlogistik stehen bereits zusammen in #21. Andere Kombination, keine inhaltliche Lücke. |
| I039 | B | #21 | Logistik | Teilbereiche der Logistik sind ... (3) | 134 | Distribution, Beschaffung und Materialwirtschaft stehen bereits in der vollständigen Teilbereichsliste der Erklärung #21 (PDF S.6–7). Andere Kombination derselben bekannten Teilbereiche; kein zusätzlicher Lerninhalt. |
| I040 | A | #5 | Produktion | Nennen Sie Formalziele der Produktionsstrategie! (2) | 34 | Wortlaut, Optionsfolge und Lösung identisch (Anzahlsuffix/Leerraum separat normalisiert). |
| I041 | B | #41 | Qualitätsmanagement | Nennen Sie Dimensionen der Qualität! (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I042 | B | #158 | Finanzmanagement | Im Liquiditätsmanagement handelt es sich bei der Stellgröße um ... (2) | 14 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I043 | B | #153 | Finanzmanagement | Investitionen sind dadruch gekennzeichnet, dass sie ... (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I044 | C | #118 | Kosten- und Erfolgsrechnung | Eine lineare Kostenfunktion besitzt ... (2) | 14 | Bei K(x)=Kf+kv*x ist K′(x)=kv konstant. Bestand 1,3 richtig; Import 1,4 verwechselt konstante mit veränderten variablen Stückkosten. |
| I045 | B | #71 | Absatzmanagement | Die Preiselastizität der Nachfrage epsilon sagt aus, dass ... (1) | 2 | epsilon und ε sind alternative Notation; gleiche Aussagen und Auswahl unter der im Katalog benutzten Betragskonvention. |
| I046 | F | #182 | Personalmanagement | Personalplanung umfasst ... (1) | 2 | Richtige Importoption endet mit P???. Bestand #182 vollständig; nicht ergänzen. |
| I047 | B | #140 | Kosten- und Erfolgsrechnung | Ein proaktives Erfolgsmanagement hat ... (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I048 | A | #79 | Innovationsmanagement | Zu den 5 Schumpeterschen Suchfeldern zählen unter anderem ... (2) | 13 | Wortlaut, Optionsfolge und Lösung identisch (Anzahlsuffix/Leerraum separat normalisiert). |
| I049 | B | #57 | Qualitätsmanagement | Welche Aussage über die sieben neuen Qualitätswerkzeuge (M7/N7) ist falsch? (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I050 | B | #203 | Unternehmenskooperation | Welche dieser Aussagen zu Unternehmensnetzwerken sind richtig? (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I051 | F | #1 | Produktion | Welche der folgenden Begriffe stellen Produktionsfaktoren dar? (2) | 12 | Grundstück kann Betriebsmittel sein; genau zwei Antworten nicht gesichert. Bestand #1 gesperrt. |
| I052 | D | #173 | Organisation | Welche der folgenden Aussagen zu Vor- und Nachteilen des Einsatzes von Stabstellen sind korrekt? (2) | 23 | Bestand #173 hat doppelte Antwortoptionen. Import ersetzt eine durch eine andere Aussage; keine belegte Originalkorrektur. #173 gesperrt. |
| I053 | B | #65 | Absatzmanagement | Als Preis-Absatz-Relation bezeichnet man ... (1) | 4 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I054 | B | #27 | Logistik | Welche Aussage ist korrekt? (1) | 4 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I055 | B | #88 | Innovationsmanagement | Am Beginn eines neuen Technologiezyklus ... (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I056 | C | #55 | Qualitätsmanagement | Welche der folgenden Aussagen über eines der sieben neuen Qualitätswerkzeuge (M7/N7) sind richtig? (2) | 34 | Zuordnung zur richtigen Bestandsvariante #55, nicht zur negierten #58. Import markiert Fehlererfassung und kritischen Pfad; korrekt im M7-Sinn sind Verknüpfung von Arbeitspaketen und kritischer Pfad. |
| I057 | B | #166 | Organisation | Horizontale Arbeitsteilung bedeutet ... (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I058 | B | #104 | Strategisches Management | Das Standardmodell zur Analyse von Strategien im Preissetzungswettbewerb ist das ... (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I059 | E | neu #275 | Kosten- und Erfolgsrechnung | Potenzialfaktoren werden im Zuge der Leisungserstellung (1) | 1 | Vollständige Dreierfrage aus PDF S.36; im bisherigen heuristischen Import nicht enthalten. |
| I060 | B | #180 | Personalmanagement | Welche der Folgenden sind nach Scholz (2000) Aufgabenfelder des Personalmanagement? (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I061 | F | #134 | Kosten- und Erfolgsrechnung | In der Betriebsergebnisfunktion (1) | 4 | Unvollständige Fixkosten[?]/variablen[??]-Optionen in beiden Quellen. Bestand #134 gesperrt. |
| I062 | B | #89 | Innovationsmanagement | Technologie-Push (2) | 34 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I063 | B | #159 | Finanzmanagement | Im Rahmen der Planung-Aktivität des Liquiditäts-Managements fällt an ... (3) | 123 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I064 | B | #6 | Produktion | Welche Aussage betreffend Produktionsorganisation ist richtig? (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I065 | B | #9 | Produktion | Nennen Sie die Aufgaben/Funktionen der Arbeitsplanung (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I066 | B | #186 | Personalmanagement | Phasen des Personalbeschaffungsprozesses sind (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I067 | C | #12 | Produktion | Die Produktionsplanung und -steuerung ... (2) | 12 | Nach Optionenzuordnung Import Lean und Terminplanung, Bestand Terminplanung und generiert Kundenaufträge. Beide Zweierlösungen unzureichend belegt; #12 gesperrt. |
| I068 | F | #208 | Unternehmenskooperation | Eine Leistung ist dann spezifisch wenn sie (2) | 24 | Ungewählte Antwort enthält im Original und Import [?]. Vollständigkeit reicht nicht für Bewertung; #208 gesperrt. |
| I069 | B | #142 | Kosten- und Erfolgsrechnung | Die Modellierung der Unsicherheit in der Absazmenge über eine Baumarktstruktur führt bei drei Subperioden zu ... (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I070 | B | #33 | Logistik | Nennen Sie Gründe der Lagerhaltung (2) | 14 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I071 | B | #62 | Absatzmanagement | Ein Unternehmen ist Monopolist, wenn ... (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I072 | B | #157 | Finanzmanagement | Ein Agio liegt vor, wenn ... (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I073 | B | #212 | Unternehmenskooperation | Welche Aussagen bezüglich der Klassifikation von Netzwerken sind korrekt? (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I074 | B | #92 | Innovationsmanagement | Lead User ... (2) | 13 | Import stimmt mit bereits redaktionell korrigiertem Lead-User-Schlüssel #92 überein. Früh kaufen allein ist kein Lead-User-Kriterium. |
| I075 | E | neu #276 | Kosten- und Erfolgsrechnung | Die Differenz zwischen EBIT und dem Jahresüberschuss/-fehlbetrag ... (1) | 1 | Vollständige Dreierfrage aus PDF S.39; Bestand hatte sie ausgelassen. |
| I076 | C | #75 | Absatzmanagement | Setzt ein Unternehmen im Monopol den Preis für sein Produkt gewinnoptimal, dann ... (2) | 12 | Bestand markiert nur Grenzerlös = Grenzkosten. Im Standardmodell ist auch Ausschluss des inelastischen Bereichs richtig. #75 auf 1,2 und Anzahl 2 korrigiert. |
| I077 | B | #191 | Personalmanagement | Welche Methoden können für die Personalsuche verwendet werden? (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I078 | F | #202 | Unternehmenskooperation | Nach der Definition von Sydow aus dem Jahr 1992 ... (2) | 23 | Ungewählte Antwort enthält bereits im PDF [?]. Wortlaut nicht ausreichend überprüfbar; #202 gesperrt. |
| I079 | B | #43 | Qualitätsmanagement | Was bedeutet Leiten und Lenken einer Organisation bezüglich der Qualität? (2) | 12 | Qualitätsziele und Qualitätssicherung sind dieselben richtigen Inhalte; Zertifizierung und Orientierung an ISO-Politik sind abweichende Ablenker. |
| I080 | B | #199 | Personalmanagement | Welche der Folgenden sind Erscheinungsformen des Haio-Effekts? (2) | 24 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I081 | F | #112 | Strategisches Management | Repetierfaktoren ... (2) | 13 | Import ändert nicht lagerbar zu lagerbar und enthält „werden ... enthalten“ sowie abgeschnittene Mehrfachverwendung. Das ist keine reine Umstellung; Bestand #112 ebenfalls nicht zuverlässig. |
| I082 | F | #122 | Kosten- und Erfolgsrechnung | Die Sollkosten ... (2) | 13 | Zwei Optionen enden mit „an ...“; entscheidende Funktionsargumente fehlen. Vollständiger Bestand #122 bleibt bestehen. |
| I083 | B | #193 | Personalmanagement | Bestandteile der Vorauswahlphase in Personalbeschaffungsprozessen sind (2) | 23 | Referenzen-/Empfehlungsanalyse ist eine alternative Bewerbungsunterlage zur Lebenslaufanalyse in #193. Gleicher Lerngegenstand Vorauswahl; keine zusätzliche Bewertungsfrage notwendig. |
| I084 | B | #186 | Personalmanagement | Phasen des Personalbeschaffungsprozesses sind (2) | 14 | Kandidatensuche und Tests gegenüber Austrittsinterview/Aufgabensynthese: schon durch #186/#187 abgedeckter Beschaffungsprozess; Negation beim automatischen Match korrigiert. |
| I085 | B | #186 | Personalmanagement | Phasen des Personalbeschaffungsprozesses sind (2) | 23 | Andere Zusammenstellung bereits vorhandener Phasen aus #186/#187, keine neue fachliche Lücke. |
| I086 | B | #189 | Personalmanagement | Was spricht für die Rekrutierung über den internen statt dem externen Arbeitsmarkt? (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I087 | B | #217 | Unternehmenskooperation | Welche der folgenden Aussagen treffen nicht auf virtuelle Unternehmungen zu? (2) | 12 | Negierte Variante der Aussagen aus #217: zeitlich unbegrenzt und meist erzwungene Qualitätskompromisse treffen nicht zu. Die Risikoformulierung „kann“ in #218 ist dagegen nicht gleichwertig und wurde gesondert gesperrt. |
| I088 | F | #218 | Unternehmenskooperation | Welche der folgenden Aussagen treffen nicht auf virtuelle Unternehmungen zu? (2) | 23 | „Kann zu Terminverlusten und Qualitätseinbußen führen“ ist nicht dasselbe wie „Kunde muss meist Kompromisse eingehen“. Risikoaussage nicht generell falsch. Negierter Zweierschlüssel daher ungeklärt. |
| I089 | B | #167 | Organisation | Vertikale  Arbeitsteilung bedeutet ... (1) | 3 | Vertikale Arbeitsteilung mit #167 vergleichen, nicht horizontale #166. Trennung koordinierender und ausführender Tätigkeiten entspricht gleicher Aussage. |
| I090 | B | #99 | Strategisches Management | Welche der folgenden sind Ursachen für Markteintrittsbarrieren? (2) | 13 | Lizenzen und Investitionskosten wie #99; abweichende ungewählte Ablenker, gleicher Lerninhalt. |
| I091 | F | #209 | Unternehmenskooperation | Transaktionskosten... (2) | 14 | Import markiert auch Kosten der Leistungserstellung als Transaktionskosten. Das ist ohne Abgrenzung zu Produktionskosten nicht tragfähig; nur Koordinationskosten eindeutig. #209 hat eine andere zweite richtige Option. |
| I092 | B | #4 | Produktion | Nennen Sie Sachziele der Produktionsstrategie! (2) | 24 | Produktqualität und Arbeitsumgebung sind Sachziele wie #4. Neuer Ablenker ändert keine richtige Aussage. |
| I093 | D | #160 | Finanzmanagement | Im Rahmen der Kontroll-Aktivität und der Lenkungs-Aktivität des Liquiditäts-Managements fällt an ... (3) | 124 | Beschädigter Beginn von #160 im PDF S.49 wiedergefunden; repariert. Import hat Auswahl der Funktion statt Messung des Soll-Cashflows als Ablenker. Check/Act-Lerngegenstand identisch. |
| I094 | B | #159 | Finanzmanagement | Im Rahmen der Planung-Aktivität des Liquiditäts-Managements fällt an ... (2) | 13 | Plan-Cashflow und Absatzleistung sind bekannte Schritte; Funktionsauswahl/Kalibrierung und Absatzabhängigkeit stehen bereits in #159/#151. Andere Antwortzusammenstellung; nicht als Ersatz verwenden. |
| I095 | F | #71 | Absatzmanagement | Die Preiselastizität der Nachfrage epsilon sagt aus, dass ... (2) | 23 | Pauschales Sinken der Nachfrage setzt normale fallende Nachfrage und ceteris paribus voraus. Zwei richtige Antworten ohne Vorzeichen-/Betragskonvention nicht eindeutig; keine neue Übernahme. |
| I096 | B | #76 | Absatzmanagement | Setzt ein Unternehmen im Monopol den Preis für sein Produkt erlösoptimal, dann ... (2) | 34 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I097 | F | #1 | Produktion | Welche der folgenden Begriffe stellen Produktionsfaktoren dar? (2) | 12 | Grundstück kann Betriebsmittel sein. Informations-/Betriebsmittelfassung hat daher ohne Modellabgrenzung mehr plausible Antworten als angegeben. |
| I098 | F | #1 | Produktion | Welche der folgenden Begriffe stellen Produktionsfaktoren dar? (2) | 23 | Liegenschaften können Betriebsmittel sein. Studentische Zweierlösung nicht ausreichend; #1 als verwandter Problemfall gesperrt. |
| I099 | B | #63 | Absatzmanagement | Ein Unternehmen ist Oligopolist, wenn ... (2) | 12 | Oligopol mit #63 statt Monopol #62 zugeordnet. Wenige Anbieter und gegenseitiger Einfluss sind dieselben korrekten Inhalte. |
| I100 | B | #180 | Personalmanagement | Welche der Folgenden sind nach Scholz (2000) Aufgabenfelder des Personalmanagement? (2) | 23 | Positive Variante derselben Scholz-Aufgabenfelder, bestehende #180/#181 nennen Entwicklung/Veränderung in Erklärung. Kein Konflikt allein aufgrund umgekehrter Negation. |
| I101 | B | #181 | Personalmanagement | Welche der Folgenden sind nach Scholz (2000) Aufgabenfelder des Personalmanagement? (2) | 13 | Komplement zu #181: Aufgabenfelder statt keine Aufgabenfelder. Personalkosten und Personalveränderung sind dort gerade die nicht gewählten Aufgabenfelder. Kein Schlüsselwiderspruch. |
| I102 | F | #7 | Produktion | Welche Aussage betreffend Produktionsorganisation ist falsch? (3) | 124 | „Wiederholfertigung“ ist ohne LV-Definition nicht zwingend geringe Stückzahl. Drei Falschaussagen daher nicht sicher; bekannte übrige Aussagen sind in #6/#7 enthalten. |
| I103 | B | #7 | Produktion | Welche Aussage betreffend Produktionsorganisation ist richtig? (2) | 13 | Positive Variante der korrekten Einzelfertigung/Variantenfertigung aus #7; abweichender Ablenker Wiederholfertigung. Keine notwendige neue Frage. |
| I104 | B | #9 | Produktion | Nennen Sie die Aufgaben/Funktionen der Arbeitsplanung (2) | 13 | Arbeitsstättenplanung und Materialbedarf stehen bereits in #8/#9 einschließlich Erklärung. Abweichende Antwortkombination, gleicher Lerngegenstand. |
| I105 | B | #8 | Produktion | Nennen Sie die Aufgaben/Funktionen der Arbeitsplanung (2) | 14 | Arbeitspläne und Kostenplanung entsprechen #8; andere falsche Kundenauftragsoption verändert die richtige Kernaussage nicht. |
| I106 | B | #10 | Produktion | Die Arbeitsplanung... (2) | 14 | Kostenminimierung und Auftragsneutralität entsprechen #10/#11, Terminplanung gehört zur PPS. Keine neue fachliche Lücke. |
| I107 | B | #12 | Produktion | Die Produktionsplanung und -steuerung... (2) | 13 | PPS-Terminplanung und Zielkonflikte bereits durch #12/#13 abgedeckt. Variante mit neu kombinierten vorhandenen Antworten. |
| I108 | B | #157 | Finanzmanagement | Ein Agio liegt vor, wenn ... (2) | 24 | Agio: Barwert/Auszahlungsbetrag über Nennwert. Zwei Formulierungen sind positiv äquivalent zu #157; kein Konflikt durch andere Negationsrichtung. |
| I109 | B | #154 | Finanzmanagement | Finanzierungen  sind dadruch gekennzeichnet, dass sie ... (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I110 | B | #105 | Strategisches Management | Das Standardmodell zur Analyse von Strategien im Mengensetzungswettbewerb ist das ... (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I111 | B | #146 | Finanzmanagement | Geld(Cash) bezieht sich in der Kapitalflussrechnung auf... (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I112 | B | #44 | Qualitätsmanagement | Welche der folgenden Aussagen ist korrekt? (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I113 | C | #175 | Organisation | Welche Aussagen zu lateralen Koordinationsmechanismen treffen zu? (2) | 13 | Bestand wählt Abstimmung und Produktkoordination; Import Weisungserteilung über Fayol-Brücke und Abstimmung. Fayol-Brücke schafft kein eigenes Weisungsrecht. Bestehende redaktionelle Entscheidung #175 beibehalten. |
| I114 | B | #35 | Logistik | Nennen Sie wesentliche Aufgaben und Bereiche des Einkaufs! (2) | 34 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I115 | B | #161 | Organisation | Im Portfolio-Management geht es um die Planung, Kontrolle und Lenkung von ... (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I116 | F | #113 | Strategisches Management | Die Umsatzerlöse werden ermittelt, indem ... (1) | 3 | Beide Quellen benutzen Umsatz, wo die Erklärung offenbar Umsatzergebnis meint. Keine richtige Rechenregel ohne begriffliche Korrektur belegbar. Bestand #113 gesperrt. |
| I117 | B | #147 | Finanzmanagement | Im Liquiditätsmanagement geht es um die Planung, Kontrolle und Lenkung von ... (2) | 34 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I118 | F | #74 | Absatzmanagement | Man sagt, Firmen haben Marktmacht, wenn ... (2) | 24 | Beide Quellen stimmen nach Permutation überein, aber zwei eindeutige Marktmachtmerkmale sind nicht gesichert. Bestand #74 gesperrt. |
| I119 | B | #168 | Organisation | Aufgabenverteilung bedeutet ... (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I120 | B | #165 | Organisation | Die Konsequenzen von Arbeitsteilung sind ... (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I121 | C | #58 | Absatzmanagement | Welche der folgenden Aussagen über eines der sieben neuen Qualitätswerkzeuge (M7/N7) sind falsch? (1) | 4 | Nur eine falsche Aussage im Import angekündigt; Bestand #58 nennt zwei. Im M7-Abgrenzungssinn sind Fehlererfassung/-analyse und garantierte Termineinhaltung beide falsch. Bestand beibehalten; Import nicht als Einantwortfrage übernehmen. |
| I122 | B | #85 | Innovationsmanagement | Käufergruppen im Hauptmarkt des Diffusionsprozesses sind ... (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I123 | B | #115 | Kosten- und Erfolgsrechnung |  Wenn die Herstellkosten-Funktion eine positive Steigung besitzt, sind ... (2) | 14 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I124 | B | #152 | Finanzmanagement | Die Betriebs-Cash Flow-Funktion modelliert den Betriebs-Cash Flow in Abhängigkeit von ... (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I125 | F | #185 | Personalmanagement | Welche Faktoren haben direkten Einfluß auf den Personaleinsatzbedarf? (3) | 13 | Angekündigt drei richtige, Schlüssel enthält nur zwei. Zusätzlich Bedarfs-/Bestandsabgrenzung strittig; #185 gesperrt. |
| I126 | B | #21 | Logistik | Funktionsbereiche der Logistik sind ... (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I127 | C | #11 | Produktion | Die Arbeitsplanung... (2) | 14 | Import wählt Auftragsneutralität und mengen-/termin-/kapazitätsmäßige Planung. Bestand #11 wählt Auftragsneutralität und wirtschaftliche Gestaltung. PDF S.3–4 erklärt die Auftragsneutralität; bestehende redaktionelle Lösung beibehalten. |
| I128 | B | #73 | Absatzmanagement | Ist die Kreuzpreiselastizität epsilon_ij positiv, dann ... (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I129 | B | #116 | Kosten- und Erfolgsrechnung | Eine anlagenintensive Technologie besitzt in der Regel ... (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I130 | B | #63 | Absatzmanagement | Ein Unternehmen ist Oligopolist, wenn ... (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I131 | B | #195 | Personalmanagement | Welche Kriterien werden in der Personalvorauswahl berücksichtigt? (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I132 | B | #108 | Strategisches Management | Preisdifferenzierung dritten Grades liegt vor, wenn (1) | 1 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I133 | C | #125 | Kosten- und Erfolgsrechnung | Wenn Plan- und ist-Werte beim Faktorpreis und beim Faktoreinsatz voneinander abweichen, bestehen die Ist-Kosten aus (1) | 3 | Bestand enthält bewusst keinen freigegebenen Schlüssel: PDF nennt 2 (oder 3). Import wählt 3. Abweichungszerlegung und Sollkostenbezug bleiben konventionsabhängig; #125 weiter gesperrt. |
| I134 | C | #40 | Logistik | Was ist keine Maßnahme der Lieferantenentwicklung? (1) | 4 | Gleiche Optionen, PDF/Bestand 3 gegenüber Import 4. Richtung der finanziellen Unterstützung und Maßnahmendefinition strittig; #40 gesperrt statt studentischen Schlüssel zu kopieren. |
| I135 | B | #25 | Logistik | Welche Aussage über Supply Chain Management ist wahr? (1) | 2 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I136 | B | #99 | Strategisches Management | Welche der Folgenden sind Ursachen für Markteintrittsbarrieren? (2) | 14 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I137 | B | #92 | Innovationsmanagement | Ein Lead User... (2) | 34 | Lead-User-Expertenwissen und Freude am Innovieren entsprechen #92; geänderter Nischenmarkt-Ablenker rechtfertigt keinen Schlüsselwechsel. |
| I138 | B | #135 | Kosten- und Erfolgsrechnung | Der einheitsbezogene Deckungsbeitrag errechnet sich aus der Differenz zwischen ... (1) | 4 | Preis minus variable Stückkosten ist identisch; zweiter Ablenker anders, richtige Antwort unverändert. |
| I139 | B | #183 | Personalmanagement | Personalveränderung umfasst... (1) | 3 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I140 | B | #178 | Organisation | Welche Aussagen charakterisieren Projektorganisationen? (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I141 | B | #90 | Innovationsmanagement | Technology-Push... (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I142 | F | #88 | Innovationsmanagement | Am Beginn eines neuen Technologiezyklus... (2) | 34 | Erste Antwort-ID lautet 12 statt 1. Schlüssel 34 lässt sich zwar lesen, aber die Struktur ist beschädigt. Keine automatische ID-Reparatur im Original; Inhalt bereits #88. |
| I143 | C | #52 | Qualitätsmanagement | Welche Aussage entspricht nicht der Wahrheit? (1) | 4 | Korrelationsdiagramm kann keine ABC-Analyse ersetzen; Import 4 ist daher keine Falschaussage. Ishikawa ordnet Ursachen, Pareto priorisiert. Bestand #52 mit Antwort 1 beibehalten. |
| I144 | B | #197 | Personalmanagement | Welche der folgenden Aussagen über Interviews sind korrekt? (2) | 23 | Jury-Interview und Strukturierung wie #197; andere falsche Option 4, kein abweichender Lerninhalt. |
| I145 | C | #13 | Produktion | Die Produktionsplanung und -steuerung... (2) | 34 | Import wählt Zielkonflikte und Lean, Bestand Einsteuerung von Aufträgen und Zielkonflikte. Auftragssteuerung ist Kernaufgabe der PPS, Lean nicht ihre allgemeine Definition. Bestand #13 beibehalten. |
| I146 | B | #215 | Unternehmenskooperation | Was sind Charakteristika eines dynamischen Netzwerkes? (2) | 12 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I147 | B | #219 | Unternehmenskooperation | Typische steuernde Rollen in Unternehmensnetzwerken sind ... (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I148 | B | #97 | Strategisches Management | Untersuchungen zum Strategischen Management ... (2) | 34 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I149 | B | #32 | Logistik | Welche der folgenden Aussagen ist wahr? (1) | 2 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I150 | F | #207 | Unternehmenskooperation | Keine Ansätze zur Erklärung der Existenz von Unternehmensnetzwerken sind... (2) | 14 | Auch bei gleicher Auswahl ist Ausschluss der Neuen Institutionenökonomie ohne LV-Taxonomie nicht gesichert; #207 gesperrt. |
| I151 | C | #67 | Absatzmanagement | Als inverse Nachfragefunktion bezeichnet man ... (1) | 3 | Inverse Nachfrage p(x) statt direkte Nachfrage x(p): Bestand #67 von Antwort 4 auf 3 korrigiert, Originaloptionen unverändert. |
| I152 | B | #211 | Unternehmenskooperation | Wie beeinflussen Informationstechnologien die Transaktionskosten? (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I153 | B | #48 | Qualitätsmanagement | Welches der folgenden Tools zählt nicht zu den sieben Qualitätswerkzeugen (Q7)? (1) | 4 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I154 | B | #141 | Kosten- und Erfolgsrechnung | Die Erfolgsabweichung entspricht ... (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I155 | B | #131 | Kosten- und Erfolgsrechnung | Ausschüttungen an die Eigenkapitalgeber... (1) | 4 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I156 | F | #76 | Absatzmanagement | Setzt ein Unternehmen im Monopol den Preis für sein Produkt erlösoptimal, dann ... (2) | 13 | Importoption 3 bricht nach „gleich“ ab. Zudem markiert Import Grenzerlös = Grenzkosten statt Grenzerlös = 0; richtige vollständige Fassung bereits #76. Keine Übernahme. |
| I157 | B | #130 | Kosten- und Erfolgsrechnung | Ein negativer Jahreserfolg verringert ... (1) | 4 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I158 | B | #206 | Unternehmenskooperation | Ansätze zur Erklärung der Existenz von Unternehmensnetzwerken sind... (2) | 23 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I159 | B | #132 | Kosten- und Erfolgsrechnung | Das Eigenkapital nimmt zu wenn der Jahresüberschuss... (2) | 13 | Fragetext und Antwortbedeutungen geprüft; Unterschiede beschränken sich auf Schreibweise, Reihenfolge oder gleichwertige Ablenker. Richtige Inhalte stimmen nach Zuordnung überein. |
| I160 | F | #56 | Qualitätsmanagement | Welche der folgenden Aussagen über eines der sieben neuen Qualitätswerkzeuge (M7/N7) sind richtig? (2) | 34 | M7-Stamm mit zwei Q7-Aussagen vermischt; Import ignoriert zugleich richtige Netzplanverknüpfung. Ohne klare Aussage „gehört zu M7“ keine eindeutige Zweierlösung; #56 ebenfalls gesperrt. |
| I161 | D | #51 | Qualitätsmanagement | Welche Aussagen über die sieben Qualitätswerkzeuge (Q7) sind wahr? (2) | 13 | Bestand #51 hat verlorene Negation über Seitenumbruch, aus PDF S.15–16 repariert. Import ist selbst beschädigt (???), anderer Fragetyp und falsches Histogramm; nicht als Reparaturquelle verwendet. |
| I162 | B | #119 | Kosten- und Erfolgsrechnung | Bei einer Linearen Kostenfunktion... (2) | 34 | Konstante Grenzkosten = variable Stückkosten bei linearem Modell wie #119. Andere negative-Steigung-Option ist nur Ablenker. |
| I163 | B | #64 | Absatzmanagement | Ein Polypol ist eine Marktform.... (1) | 2 | Polypol mit vielen kleinen Anbietern wie #64. Drei statt vier Optionen, gleiches Lernziel; keine neue Frage. |
| I164 | B | #30 | Logistik | Welche Aussage ist falsch? (2) | 14 | Primär-/Sekundärbedarf bereits #28/#29/#30. Zweite Falschaussage ist ausdrückliche Negation einer richtigen Aussage; reine Kombination vorhandener Lerninhalte. |
| I165 | F | #54 | Qualitätsmanagement | Zu den Hauptproblemquellen gehören (2) | 24 | Hauptproblemquellen ohne Bezug auf Ishikawa/5M nicht eigenständig vollständig. Gemeint sind Maschine und Material, fachlich bereits in #54 enthalten. |
| I166 | F | #54 | Qualitätsmanagement | Nicht zu den Hauptproblemquellen gehören (2) | 13 | Negierter Fragestamm ohne Bezugsmodell. 5M wäre nachvollziehbar, ist aber im Import nicht genannt; Bestand #53/#54 hat den Kontext. |
| I167 | F | #54 | Qualitätsmanagement | Zu den Hauptproblemquellen gehören (2) | 24 | Hauptproblemquellen ohne Bezugsmodell; Maschine und Mensch wären im 5M-Kontext richtig. Kontext nicht als angeblichen Originaltext ergänzen. |
| I168 | E | neu #277 | Kosten- und Erfolgsrechnung | Der Verkaufspreis Einheit rechnet sich indem... (1) | 2 | Vollständige Preisrechnung; im PDF S.36 nur eine Option überliefert. Vier Importoptionen werden unverändert übernommen, richtige Rechnung zusätzlich algebraisch geprüft. |
| I169 | B | #124 | Kosten- und Erfolgsrechnung | Die variablen Einheitskosten errechnen sich mit.. (1) | 3 | Variable Umsatzkosten / Absatzmenge entspricht #124. Andere falsche Kostenkombinationen sind keine neue Wissenslücke. |
| I170 | B | #123 | Kosten- und Erfolgsrechnung | Die vollen Einheitskosten errechnen sich mit (2) | 34 | Mit #123 statt #124 verglichen. Volle Stückkosten = Umsatzkosten / Absatzmenge = fixe plus variable Stückkosten; identische zwei richtige Inhalte. |
| I171 | B | #162 | Organisation | Zum Working Capital zählen nicht... (1) | 2 | Maschinen sind Anlagevermögen wie #162. Kasse als Ablenker hängt von Brutto-/Netto-/operativem Working-Capital-Begriff ab; keine neue bewertete Fassung übernehmen. |
| I172 | F | #205 | Unternehmenskooperation | Gegenüber Netzwerken weisen Hierarchien... (2) | 13 | Andere Optionen als #205, aber gleiche mutmaßlich umgekehrte Vergleichsrichtung. Für Hierarchien passen die markierten Netzwerkmerkmale nicht; #205 gesperrt. |
| I173 | B | #201 | Unternehmenskooperation | Personalentwicklungsmöglichkeiten im Bereich der Arbeitsgestaltung sind (2) | 13 | Job Enrichment/Enlargement entsprechen #201; Job Sharing statt anderer falscher Option verändert den geprüften Kern nicht. |
| I174 | B | #79 | Innovationsmanagement | Zu den 5 Schrumpeterschen Suchfeldern zählen unter anderem... (2) | 13 | Markt-/Prozessinnovation trotz Schreibfehler Schrumpeter wie #79. |
| I175 | B | #80 | Innovationsmanagement | Zu den 5 Schrumpeterschen Suchfeldern zählen unter anderem... (2) | 13 | Produktinnovation als weitere Schumpeter-Kategorie ist bereits im Bestand #81 und im Suchfeldkontext #79/#80 erklärt; alternative Paarbildung, keine neue Lernlücke. |
| I176 | B | #80 | Innovationsmanagement | Zu den 5 Schrumpeterschen Suchfeldern zählen unter anderem... (2) | 13 | Neue Inputs als Schumpeter-Suchfeld stehen bereits in der Erklärung #79/#80; alternative Zusammenstellung desselben Suchfeldkatalogs. |
| I177 | E | neu #278 | Qualitätsmanagement | Welches der folgenden Tools zählt nicht zu den sieben Qualitätswerkzeugen (Q7)? (1) | 3 | Neue vollständige Q7-Abgrenzung PDCA gegenüber Regelkarte, Sammelliste und Stratifikation. Vier Optionen und ASQ-Quellen geprüft. |

## Duplikate und Varianten

Exakte interne Dublettengruppen im Import nach Normalisierung und optionsunabhängiger Reihenfolge: 0. Exakte vollständige Dublettengruppen im bisherigen Bestand: 0.

Nahe Importvarianten mit gleichem normalisiertem Stamm und mindestens 50 % gemeinsamen Optionen:

| Importpaar | Gemeinsame Optionen | Einordnung |
|---|---|---|
| I005 / I083 | 75% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I029 / I090 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I032 / I161 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I037 / I039 | 80% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I051 / I097 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I055 / I142 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I056 / I160 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I060 / I100 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I060 / I101 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I065 / I104 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I066 / I085 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I072 / I108 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I087 / I088 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I090 / I136 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I097 / I098 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I100 / I101 | 75% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I165 / I167 | 75% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I174 / I175 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I174 / I176 | 50% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |
| I175 / I176 | 75% | Thematische Varianten; gemeinsame Formulierung allein beweist keine Dublette. Negationen und gewählte Aussagen siehe Einzelprüfung. |

Zusätzlich sind #151/#152 im Bestand semantische Dubletten (Absatzmenge/verkaufte Menge), #8/#9/#10/#11 sowie zahlreiche Personal- und Q7-Fragen eng verwandte Varianten. Sie bleiben mit allen IDs bestehen, weil bereits Fortschritt daran hängen kann. Doppelte **Antwortoptionen** wurden gesondert geprüft: #173 enthält denselben korrekten Satz an zwei Positionen; #2 enthält Gutenberg in zwei Optionen. Beide werden nicht automatisch bewertet.

## Offene Probleme und Grenzen

Nicht übernommene Importfragen (F), offene C-Konflikte und nicht reparierbare D-Fälle:

| Import | Bestand | Grund |
|---|---|---|
| I008 | #82 | Beide Quellen haben denselben Schlüssel, aber Diffusionsrate und kumulierter Diffusionsgrad sind im Wortlaut nicht unterschieden. Bestand #82 gesperrt. |
| I014 | #45 | Check vor/nach Durchführung ist inhaltlich verschieden. Der Import-Schlüssel 12 ist mit „vor“ nicht tragfähig; Bestand #45 ebenfalls gesperrt. |
| I016 | #69 | Gleicher Schlüssel ist keine fachliche Bestätigung: Abgrenzung Marktgleichgewicht/Preisnehmerschaft ungeklärt; #69 gesperrt. |
| I022 | #2 | Bestand enthält Gutenberg zweimal, aber nicht beide als richtig. Fünf Importoptionen lösen die unklare Originalfassung nicht; #2 gesperrt. |
| I024 | #24 | Fünfte Importoption reduziert Lieferantenbestände; dies ist keine zwingende Definition bzw. allgemeine SCM-Folge. Anzahl 3 nicht gesichert. Bestand #24 bleibt als eigene Vieroptionenfassung erhalten. |
| I026 | #39 | Import schließt hohe Produktqualität aus und markiert Nähe zum Endkunden; fachlich sind Qualität, Liefertreue und Flexibilität relevant. Standortnähe kann situationsabhängig ebenfalls relevant sein; kein gesicherter Dreierschlüssel. Bestand #39 hat andere Optionen und wird nicht ersetzt. |
| I031 | #114 | Nutzungsbedingte Wertminderung erzwingt keine spätere Investition. Beide studentischen Quellen wählen zwar gleich, aber die zweite richtige Antwort ist ohne Ersatzannahme nicht gesichert; #114 gesperrt. |
| I032 | #49 | Ursache und ??? ist unvollständig. Bestand #49 enthält Wirkung bereits korrekt; keine Übernahme. |
| I033 | #78 | Letzte Option bricht bei „optimale“ ab; keine verlässliche Rekonstruktion aus studentischem Import. Bestand #78 bleibt bestehen. |
| I046 | #182 | Richtige Importoption endet mit P???. Bestand #182 vollständig; nicht ergänzen. |
| I051 | #1 | Grundstück kann Betriebsmittel sein; genau zwei Antworten nicht gesichert. Bestand #1 gesperrt. |
| I052 | #173 | Bestand #173 hat doppelte Antwortoptionen. Import ersetzt eine durch eine andere Aussage; keine belegte Originalkorrektur. #173 gesperrt. |
| I061 | #134 | Unvollständige Fixkosten[?]/variablen[??]-Optionen in beiden Quellen. Bestand #134 gesperrt. |
| I067 | #12 | Nach Optionenzuordnung Import Lean und Terminplanung, Bestand Terminplanung und generiert Kundenaufträge. Beide Zweierlösungen unzureichend belegt; #12 gesperrt. |
| I068 | #208 | Ungewählte Antwort enthält im Original und Import [?]. Vollständigkeit reicht nicht für Bewertung; #208 gesperrt. |
| I078 | #202 | Ungewählte Antwort enthält bereits im PDF [?]. Wortlaut nicht ausreichend überprüfbar; #202 gesperrt. |
| I081 | #112 | Import ändert nicht lagerbar zu lagerbar und enthält „werden ... enthalten“ sowie abgeschnittene Mehrfachverwendung. Das ist keine reine Umstellung; Bestand #112 ebenfalls nicht zuverlässig. |
| I082 | #122 | Zwei Optionen enden mit „an ...“; entscheidende Funktionsargumente fehlen. Vollständiger Bestand #122 bleibt bestehen. |
| I088 | #218 | „Kann zu Terminverlusten und Qualitätseinbußen führen“ ist nicht dasselbe wie „Kunde muss meist Kompromisse eingehen“. Risikoaussage nicht generell falsch. Negierter Zweierschlüssel daher ungeklärt. |
| I091 | #209 | Import markiert auch Kosten der Leistungserstellung als Transaktionskosten. Das ist ohne Abgrenzung zu Produktionskosten nicht tragfähig; nur Koordinationskosten eindeutig. #209 hat eine andere zweite richtige Option. |
| I095 | #71 | Pauschales Sinken der Nachfrage setzt normale fallende Nachfrage und ceteris paribus voraus. Zwei richtige Antworten ohne Vorzeichen-/Betragskonvention nicht eindeutig; keine neue Übernahme. |
| I097 | #1 | Grundstück kann Betriebsmittel sein. Informations-/Betriebsmittelfassung hat daher ohne Modellabgrenzung mehr plausible Antworten als angegeben. |
| I098 | #1 | Liegenschaften können Betriebsmittel sein. Studentische Zweierlösung nicht ausreichend; #1 als verwandter Problemfall gesperrt. |
| I102 | #7 | „Wiederholfertigung“ ist ohne LV-Definition nicht zwingend geringe Stückzahl. Drei Falschaussagen daher nicht sicher; bekannte übrige Aussagen sind in #6/#7 enthalten. |
| I116 | #113 | Beide Quellen benutzen Umsatz, wo die Erklärung offenbar Umsatzergebnis meint. Keine richtige Rechenregel ohne begriffliche Korrektur belegbar. Bestand #113 gesperrt. |
| I118 | #74 | Beide Quellen stimmen nach Permutation überein, aber zwei eindeutige Marktmachtmerkmale sind nicht gesichert. Bestand #74 gesperrt. |
| I125 | #185 | Angekündigt drei richtige, Schlüssel enthält nur zwei. Zusätzlich Bedarfs-/Bestandsabgrenzung strittig; #185 gesperrt. |
| I133 | #125 | Bestand enthält bewusst keinen freigegebenen Schlüssel: PDF nennt 2 (oder 3). Import wählt 3. Abweichungszerlegung und Sollkostenbezug bleiben konventionsabhängig; #125 weiter gesperrt. |
| I134 | #40 | Gleiche Optionen, PDF/Bestand 3 gegenüber Import 4. Richtung der finanziellen Unterstützung und Maßnahmendefinition strittig; #40 gesperrt statt studentischen Schlüssel zu kopieren. |
| I142 | #88 | Erste Antwort-ID lautet 12 statt 1. Schlüssel 34 lässt sich zwar lesen, aber die Struktur ist beschädigt. Keine automatische ID-Reparatur im Original; Inhalt bereits #88. |
| I150 | #207 | Auch bei gleicher Auswahl ist Ausschluss der Neuen Institutionenökonomie ohne LV-Taxonomie nicht gesichert; #207 gesperrt. |
| I156 | #76 | Importoption 3 bricht nach „gleich“ ab. Zudem markiert Import Grenzerlös = Grenzkosten statt Grenzerlös = 0; richtige vollständige Fassung bereits #76. Keine Übernahme. |
| I160 | #56 | M7-Stamm mit zwei Q7-Aussagen vermischt; Import ignoriert zugleich richtige Netzplanverknüpfung. Ohne klare Aussage „gehört zu M7“ keine eindeutige Zweierlösung; #56 ebenfalls gesperrt. |
| I165 | #54 | Hauptproblemquellen ohne Bezug auf Ishikawa/5M nicht eigenständig vollständig. Gemeint sind Maschine und Material, fachlich bereits in #54 enthalten. |
| I166 | #54 | Negierter Fragestamm ohne Bezugsmodell. 5M wäre nachvollziehbar, ist aber im Import nicht genannt; Bestand #53/#54 hat den Kontext. |
| I167 | #54 | Hauptproblemquellen ohne Bezugsmodell; Maschine und Mensch wären im 5M-Kontext richtig. Kontext nicht als angeblichen Originaltext ergänzen. |
| I172 | #205 | Andere Optionen als #205, aber gleiche mutmaßlich umgekehrte Vergleichsrichtung. Für Hierarchien passen die markierten Netzwerkmerkmale nicht; #205 gesperrt. |

Weitere bereits vorher ausgeschlossene Bestandsfälle #59, #125, #177 und #246 bleiben ungeklärt. #255 ist bereits im PDF fragmentarisch, nicht lediglich durch die App beschädigt. Fünf-Optionen-Aufgaben werden weiterhin nur im Lesebuch gezeigt; dies ist eine Formatgrenze, keine fachliche Freigabe. Insbesondere verkürzte Quellenoptionen in #264/#267, die unsichere Abbildung bei #252, individuelle Lehrmodelle zu Teamperformance/THG und studentische mMn-Schlüssel sind ohne Originalfolien nicht zuverlässig unabhängig zu prüfen. Die Aufgaben #223/#225/#242/#249 wurden textlich wiederhergestellt, ihre gesamten fachlichen Lösungen damit nicht unabhängig verifiziert.

Der gesamte Bestand wurde strukturell geprüft und mit den Importtreffern abgeglichen. Das ist keine Behauptung, jede der 278 Lösungen anhand offizieller Lehrmaterialien bestätigt zu haben. Bestehende generische Erklärungen und aus PDF-Seiten abgeleitete Kapitel sind weiterhin keine individuell belegten LV-Lösungen. Bei neu gesperrten Fragen wurde die generische Lernhilfe durch den konkreten Unsicherheitshinweis ersetzt; ursprüngliche Quellenerklärungen bleiben lesbar.

## Phase 5/6: Validierung und Produktion

Ausführbare Prüfungen (ohne npm-Abhängigkeiten):

```sh
python3 scripts/validate_catalog.py
python3 -m unittest discover -s tests
node --test tests/catalog.test.cjs
node --check app.js
node --check sw.js
python3 scripts/build.py
```

Die Python-Validierung prüft Schema-Invarianten, eindeutige IDs, vollständige Aufgaben, Kapitel, Options- und Schlüsselindizes, Anzahl richtiger Antworten, dokumentierte Altlasten, vollständige Importzuordnung, Import-Hash, alle Bestands-IDs und unveränderte Originaloptionen. Unvollständige, schon vorhandene Datensätze werden nur als explizit gesperrte Altlasten toleriert.

Die Node-Regressionstests laden den echten App-Code mit isoliertem Storage. Sie prüfen alle alten IDs mit synthetischen Versuchen/Lesemarkierungen, Beherrschung über zwei Tage, neue unbearbeitete Fragen, historische Prüfungsversuche und Statistiken, DB-Felder auch außerhalb des bekannten Schemas, Randomisierung, Snapshot neuer Ergebnisse und vollständig lesenden Export. Die Bewertung wird für alle 16 Auswahlen jeder geeigneten Frage gegen die unveränderte Formel geprüft. Ungültige/mehrdeutige Fragen sowie fehlerhafte und doppelte Auswahlindizes werden zurückgewiesen. Fragen ohne richtige bzw. ohne falsche Antwort werden nicht bewertet; das ursprüngliche Schema wurde nicht auf neue Sonderformate ausgedehnt.

Der neue Produktionsschritt verpackt ausschließlich explizit zugelassene statische Dateien nach `dist/`; private Sicherungen, Import-Arbeitsdateien und sonstige Workspace-Dateien werden nicht kopiert. Dies ist ein prüfbares statisches Artefakt, kein Deployment. Der Service-Worker-Dateicache bekommt eine neue Version und entfernt ausschließlich alte `gbu-public-`-Caches; localStorage und Origin bleiben unverändert. Ein Cache-Update ist keine Löschung von Website-/Lerndaten.

**Ergebnis:** Produktionspaket erfolgreich erstellt; 3 Python-Tests und 9 Node-Tests bestanden, Schema-/Katalogvalidierung und JavaScript-Syntaxprüfungen erfolgreich. Reproduzierbare Zählungen stehen in `reports/question-catalog-validation.json`. Keine echten Browserdaten, keine grafischen Browser-/Gerätetests; keine automatischen Commits oder Pushes.

## Quellenverzeichnis

- **pdf**: [Vorhandener Fragenkatalog (studentische Sammlung, keine offizielle Musterlösung)](../betriebs-u-fragen.pdf). Lokales Original mit Lösungen und studentischen Kommentaren; angegebene Skriptseiten sind kein Zugriff auf das offizielle Skript.
- **import**: [Zusätzlicher studentischer JSON-Katalog](../imported-questions/grundlagen_der_betriebs_und_unternehmensfuerung_fragenkatalog.json). Studentische Lösung, ungeprüfte Ausgangsquelle
- **q7**: [ASQ: Seven Basic Quality Tools](https://asq.org/quality-resources/seven-basic-quality-tools). Abgerufen am 10.11.2026.
- **m7**: [ASQ: Seven New Management and Planning Tools](https://asq.org/quality-resources/new-management-planning-tools). Abgerufen am 10.11.2026.
- **pdca**: [ASQ: Continuous Improvement](https://asq.org/quality-resources/continuous-improvement). Abgerufen am 10.11.2026.
- **monopoly**: [Martin J. Osborne, University of Toronto: Profit-maximizing monopolist](https://mjo.osborne.economics.utoronto.ca/index.php/tutorial/index/2/mon/t). Abgerufen am 10.11.2026.
- **accounting**: [OpenStax: Prepare an Income Statement](https://openstax.org/books/principles-financial-accounting/pages/2-3-prepare-an-income-statement-statement-of-owners-equity-and-balance-sheet). Abgerufen am 10.11.2026.
- **income**: [OpenStax: The Income Statement](https://openstax.org/books/introduction-business/pages/14-5-the-income-statement). Abgerufen am 10.11.2026.
- **cost**: [OpenStax: Calculate a Break-Even Point in Units and Dollars](https://openstax.org/books/principles-managerial-accounting/pages/3-2-calculate-a-break-even-point-in-units-and-dollars). Abgerufen am 10.11.2026.
- **pps**: [Leibniz Universität Hannover: Produktionsplanung und -steuerung](https://plabs.uni-hannover.de/ilias.php?baseClass=illmpresentationgui&cmd=layout&lang=en&obj_id=96986&ref_id=45846). Abgerufen am 10.11.2026.
- **supplier**: [Fraunhofer IML: Lieferantenauswahl im Wertschöpfungsnetzwerk](https://www.iml.fraunhofer.de/de/abteilungen/b2/supply_chain_engineering/supply_chain_management/Lieferantenauswahl.html). Abgerufen am 10.11.2026.
- **fishbone**: [ASQ: Fish(bone) Stories](https://asq.org/quality-progress/articles/fishbone-stories?id=5c9adae78e3242588621ab300378d40b). Abgerufen am 10.11.2026.
