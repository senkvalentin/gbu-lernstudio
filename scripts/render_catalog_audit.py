"""Render the reviewed audit. Never changes questions, imports, or browser storage."""
import json
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT / name).read_text())
def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')
def key(indices):
    return ', '.join(str(i + 1) for i in indices) or 'nicht freigegeben'
def render():
    audit = load('data/question-catalog-audit.json')
    catalog = load('questions.json')
    by_id = {q['id']: q for q in catalog}
    summary = audit['summary']
    validation = load('reports/question-catalog-validation.json')
    lines = ['# GBU-Fragenkatalog: vollständiger Vergleich und Korrekturaudit', '',
             'Stand: 10.11.2026. Alle 177 Importdatensätze wurden gelesen und einzeln zugeordnet. '
             'Der Bericht bestätigt keine offizielle Musterlösung: Das vorhandene PDF ist ebenfalls eine studentische Sammlung. '
             'Ein offizielles Skriptum oder eine offizielle Lösung war im Repository nicht verfügbar.', '',
             '## Zusammenfassung', '', '| Kennzahl | Anzahl |', '|---|---:|',
             f"| Bestehende Fragen vor Audit | {summary['existing']} |",
             f"| Importierte Fragen | {summary['imported']} |"]
    labels = {'A': 'Identisch (A)', 'B': 'Semantisch gleichwertige Varianten (B)',
              'C': 'Gleiche Aufgabe mit widersprüchlichem Schlüssel (C)',
              'D': 'Beschädigter/unvollständiger Bestand (D)', 'E': 'Neue geprüfte Fragen (E)',
              'F': 'Unklare oder beschädigte Importfragen (F)'}
    for category, label in labels.items():
        lines.append(f"| {label} | {summary['categories'].get(category, 0)} |")
    lines += [f"| Bestehende Fragen korrigiert (Text/Schlüssel) | {summary['corrected']} |",
              f"| Davon Lösungsschlüssel geändert | 2 |",
              f"| Zusätzliche Bestandssperren, IDs erhalten | {summary['held']} |",
              f"| Ungeklärte Importfälle inkl. offener C/D | {summary['unresolvedImports']} |",
              f"| Final vorhandene Fragen (inkl. Lesebuch/Prüffälle) | {len(catalog)} |",
              f"| Davon bewertbar | {validation['eligibleCount']} |",
              f"| Davon nur Lesebuch | {validation['readingOnlyCount']} |", '',
              'A–F sind disjunkt. Bei unvollständigem Import hat F Vorrang, auch wenn daneben ein Schlüsselkonflikt vorliegt. '
              'D bezeichnet einen belegten Bestandsmangel, nicht automatisch eine erfolgreich reparierte Frage. '
              'B umfasst auch anders kombinierte, bereits abgedeckte richtige Aussagen und geänderte Ablenker; solche Varianten wurden nicht künstlich als neue Wissenslücken gezählt. '
              'Fälle mit unterschiedlichen Negationen wurden ausdrücklich geprüft. Die 12 C-Fälle sind zusätzlich in der Konflikttabelle ausgewiesen; weitere problematische Schlüssel in F stehen dort gesondert.', '',
              'Drei neue Fragen (#274–276) haben drei Optionen und sind ausschließlich im Lesebuch verfügbar. '
              'Zwei neue Fragen (#277–278) sind für Training und Simulation geeignet. Kein bestehender Datensatz wurde entfernt, keine vorhandene Optionsfolge verschoben.', '',
              '## Phase 1: Architektur und Fortschrittsschutz', '',
              '- Statische HTML/CSS/Vanilla-JavaScript-App; kein Paketmanager, Framework, Server-Backend oder ursprünglicher Produktions-Build. '
              '`build_data.py` ist ein heuristischer PDF-Importer mit festen `/mnt/data`-Pfaden und wurde nicht auf den Bestand angewendet.',
              '- `questions.json`: numerische stabile Frage-ID; Antworten sind **nullbasierte Originalindizes** in `options`, keine separat erzeugten Antwort-IDs. '
              'Importantworten haben dagegen explizite IDs (normalerweise 1–n). `rightids` ist ein String mit aneinandergereihten Ziffern.',
              '- `gbu-study-v1` in localStorage enthält `attempts`, `notes`, `settings`, optional `readIds` sowie gegebenenfalls weitere Felder. '
              'Ein Versuch enthält ID, Datum, ausgewählte Originalindizes, `full`, `points` und `mode`. '
              'Es gibt keine IndexedDB, Storage-Migration oder automatische Neuberechnung alter Ergebnisse.',
              '- Zusatzschlüssel: `gbu-color-theme` und `gbu-last-answer-order:<ID>`. Der Service Worker benutzt Cache Storage für Dateien, nicht für den Lernfortschritt. '
              'Origin, Manifest, Deployment-Basis und Storage-Schlüssel bleiben unverändert.',
              '- Training: adaptiv nach bisherigen Fehlern/Erfolgen, zufällig oder kapitelweise. Beherrscht bedeutet zwei volle Erfolge an verschiedenen UTC-Tagen. '
              'Neue Fragen haben keine Versuche und keine Lesemarkierungen. Neue Fragen können lediglich den Nenner der Gesamtfortschrittsanzeige erhöhen.',
              '- Simulation: vier geeignete Fragen pro vorhandenem Kapitel; zwölf Kapitel. '
              'Prüfungsversuche werden sofort einzeln als `mode: exam` gespeichert. Es existieren **keine separat gespeicherten abgeschlossenen Prüfungssitzungen, Gesamtnoten oder Sitzungs-IDs**. '
              'Eine Wiederherstellung dieser früher nie gespeicherten Informationen ist unmöglich. Vorhandene Prüfungsversuche bleiben vollständig erhalten.',
              '- Randomisierung mischt nur eine Kopie der Originalindizes; Auswahl und Speicherung referenzieren stets den ursprünglichen Index. '
              'Vorhandene Optionen wurden deshalb weder ersetzt noch umsortiert, auch bei beschädigten Fragen.',
              '- Unbedenkliche Inhaltsänderungen: neue IDs oberhalb 273, belegte Textkorrekturen, nachvollziehbare aktuelle Schlüssel, Erklärungen und Sperrmetadaten. '
              'Historische Punkte und `full` werden auch bei neuen Schlüsseln **nicht** umgeschrieben. Neue Versuche speichern zusätzlich `questionRevision`, `answerKey` und `correctCount`.',
              '- Alte Versuche besitzen keinen Schlüssel-Snapshot. Der frühere Katalogschlüssel ist im Audit erhalten; es ist jedoch nicht beweisbar, mit welcher noch älteren App-Fassung ein einzelner Browser-Versuch entstanden ist. '
              'Eine rückwirkende Neubewertung oder Behauptung eines damaligen Schlüssels ist daher ausgeschlossen.',
              '- Vor Änderungen wurden `questions.json`, `app.js`, `sw.js`, `index.html`, `README.md` und `docs/DATEN.md` nach `private/catalog-audit-before/` kopiert. '
              'Die Sicherung liegt absichtlich im ignorierten privaten Verzeichnis. Der maschinenlesbare Audit enthält zusätzlich alle ursprünglichen IDs, Optionen, Schlüssel und Objektprüfsummen sowie vollständige Vorher/Nachher-Datensätze jeder Änderung.',
              '- **Kein Zugriff auf echten Browser-Speicher.** Es wurden keine echten Nutzerdaten gesichert oder verändert. '
              'Die automatisierten Kompatibilitätstests verwenden realistische synthetische Daten und die tatsächlichen Funktionen aus `app.js` in einer isolierten DOM/Storage-Testumgebung.',
              '- Der JSON-Export bleibt unter demselben Button verfügbar. Er exportiert jetzt alle DB-Felder einschließlich Lesemarkierungen und Notizen, '
              'außerdem die unveränderten rohen App-Storage-Werte inklusive Theme und letzter Antwortreihenfolgen. '
              'Bestehende Top-Level-Felder `schemaVersion: 1`, `attempts` und `settings` bleiben kompatibel; `backup.version: 2` kennzeichnet die vollständige Ergänzung. '
              'Der Export schreibt nichts in Storage. Keine automatische Wiederherstellung oder Migration wurde hinzugefügt.', '',
              '## Phase 2: Import und Vergleichsmethode', '',
              'Die Originaldatei bleibt bytegenau unverändert (SHA-256 siehe JSON). Einheitlicher äußerer Aufbau: '
              '`{"questions": [{"q": ..., "answers": [{"text": ..., "id": ...}], "rightids": "..."}]}`. '
              '177 Multiple-Choice-Fragen, 167 mit vier, 6 mit fünf, 4 mit drei Optionen. '
              'Keine eigenen Frage-IDs, Kapitel, Seiten oder Erklärungen. `I001` bis `I177` bezeichnen ausschließlich die ursprünglichen 1-basierten Dateipositionen, keine behaupteten Original-IDs.', '',
              'Die normalisierte Arbeitsfassung ist je Zeile unter `normalized` in der JSON-Datei erhalten, zusammen mit dem unveränderten Importobjekt unter `raw`. '
              'Kapitel sind redaktionell vom zugeordneten Bestand abgeleitet; neue Rechnungswesenfragen wurden bewusst „Kosten- und Erfolgsrechnung“ zugeordnet, '
              'statt die aus Seitenbereichen historisch ungenaue Kapitelgrenze zu übernehmen.', '',
              'Kandidatensuche: Unicode-/Leerraum-/Interpunktionsnormalisierung, Vergleich des Stamms und der einzelnen Antworttexte, '
              'anschließend bijektive Optionszuordnung bei gleicher Optionszahl. ε/epsilon und Notationsvarianten werden berücksichtigt. '
              'Es gibt keine vollständigen LaTeX-Aufgaben oder Rechenformeln, deren Bedeutung eine zusätzliche LaTeX-Engine erfordern würde. '
              'Zahlen, Negationen, „vor/nach“, Marktform und kumulierter/periodischer Verlauf wurden anschließend semantisch geprüft. '
              'Die maschinellen `candidate`-Treffer bleiben als Suchprotokoll erhalten; die verbindliche Zuordnung ist `existingId`, nicht der Kandidat. '
              'So wurden unter anderem Oligopol statt Monopol, vertikale statt horizontale Arbeitsteilung und volle statt variable Stückkosten richtiggestellt.', '',
              'Strukturprobleme:', '', '| Import | Auffälligkeit |', '|---|---|']
    for row in audit['questions']:
        if row['structuralIssues']:
            lines.append(f"| I{row['importIndex']:03} | {cell('; '.join(row['structuralIssues']))} |")
    lines += ['', 'Redaktionelle Kapitelzuordnung (keine Kapitelangaben in der Importdatei):', '',
              '| Kapitel | Importfragen | Finaler Bestand | Bewertbar |', '|---|---:|---:|---:|']
    from validate_catalog import eligible
    for chapter, count in audit['importSummary']['chapterAssignments'].items():
        questions = [q for q in catalog if q['chapter'] == chapter]
        lines.append(f"| {chapter} | {count} | {len(questions)} | {sum(eligible(q) for q in questions)} |")
    lines += ['', 'Angekündigte richtige Antworten im Import: '+', '.join(f"{k}: {v} Fragen" for k, v in audit['importSummary']['declaredCorrectCounts'].items())+'.']
    lines += ['', 'Die Strukturerkennung ist nur eine zusätzliche Hilfe: Auch syntaktisch gültige Datensätze können fachlich falsch sein. '
              'Ein Antwort-ID-Fehler besteht bei I142 (`12` statt `1`); I125 kündigt drei richtige Antworten an, enthält aber nur zwei im Schlüssel. '
              'Weitere abgebrochene Texte und falsche Schlüssel sind in der Einzelprüfung dokumentiert.', '',
              '## Phase 3/4: Änderungen am Bestand', '',
              'Die folgenden Einträge geben alle Inhaltsänderungen wieder. Vollständige alte und neue Objekte stehen in `changes` der JSON-Datei. '
              'Antwortnummern in diesem Markdown sind 1-basiert; JSON-Schlüssel bleiben 0-basiert.', '']
    for change in audit['changes']:
        ident = change.get('existingId') or change.get('newId')
        lines += [f"### #{ident}: {change['kind']}", '',
                  f"Kapitel: {change['chapter']}. Import: {', '.join('I'+str(i).zfill(3) for i in change['importIndices']) or 'zusätzliche Bestandsprüfung'}. "
                  f"Status: {change['validationStatus']}.", '', change['reason'], '']
        old, new = change['before'], change['after']
        if old is None:
            lines += ['Vorher: nicht vorhanden.', '', 'Neu: '+new['text'], '']
            for i, option in enumerate(new['options'], 1):
                lines.append(f"- {i}: {option} {'(richtig)' if i-1 in new['answers'] else '(falsch)'}")
        else:
            for field in ['text', 'answers', 'correctCount', 'contextWarning', 'assessmentStatus']:
                if old.get(field) != new.get(field):
                    before = key(old.get(field, [])) if field == 'answers' else old.get(field, 'nicht gesetzt')
                    after = key(new.get(field, [])) if field == 'answers' else new.get(field, 'nicht gesetzt')
                    lines += [f"- `{field}` vorher: {before}", f"- `{field}` nachher: {after}"]
            lines += ['- ID und alle Originaloptionen unverändert.']
        lines += ['', 'Quellen: '+', '.join(change['sources'])+'.', '']
    lines += ['## Konflikte der Lösungsschlüssel', '',
              'Eine andere Zahl allein ist kein Konflikt: Antworten müssen zuerst nach ihrem Text zugeordnet werden. '
              'Die folgende Tabelle enthält die 12 echten C-Zuordnungen. „Bestand bestätigt“ bedeutet eine dokumentierte Ablehnung des Imports, keine Übernahme. '
              'Bei ungeklärten Fällen bleiben alte Quellenschlüssel sichtbar, die automatische Bewertung ist gesperrt.', '',
              '| Import / Bestand / Frage | Alter Bestand | Studentischer Import | Geprüfte Lösung (Bestandsnummern) | Ergebnis und Begründung | Quellen |',
              '|---|---|---|---|---|---|']
    for row in audit['questions']:
        if row['category'] != 'C':
            continue
        lines.append(f"| I{row['importIndex']:03} / #{row['existingId']} / {cell(row['raw']['q'])} | {key(row['existingSolution'])} | {row['raw']['rightids']} (Importnummern) | {key(row['verifiedSolution']) if row['verifiedSolution'] is not None else 'ungeklärt'} | {cell(row['result']+': '+row['reason'])} | {', '.join(row['sources'])} |")
    lines += ['', 'Zusätzliche Konflikte bei beschädigten bzw. nicht gleichwertigen F/D-Varianten (keine künstliche Gleichsetzung der Optionen):', '',
              '| Import / Bestand | Bestandsschlüssel | Importschlüssel | Untersuchung / Ergebnis |', '|---|---|---|---|']
    for row in audit['questions']:
        if row['category'] not in ['F', 'D'] or row['importIndex'] not in [14, 22, 24, 26, 52, 81, 88, 91, 125, 156, 160, 161, 172]:
            continue
        original = next(q for q in audit['baseline']['questions'] if q['id'] == row['existingId'])
        lines.append(f"| I{row['importIndex']:03} / #{row['existingId']} | {key(original['answers'])} | {row['raw']['rightids']} | {cell(row['reason'])} Quellen: {', '.join(row['sources'])} |")
    lines += ['', '## Vollständige Einzelzuordnung aller Importfragen', '',
              'Die Auswahl wird jeweils über die Antworttexte verglichen; Importnummern sind keine Bestandsindizes. '
              'Die JSON-Datei enthält zusätzlich sämtliche Antworttexte, beide Ausgangsschlüssel, normalisierte Arbeitsdaten und Optionszuordnung der Suchkandidaten.', '',
              '| Import | Kategorie | Bestand / neue ID | Kapitel | Frage | Importlösung | Begründung / Aktion |', '|---|---|---|---|---|---|---|']
    for row in audit['questions']:
        ident = '#'+str(row['existingId']) if row['existingId'] else 'neu #'+str(row['newId'])
        lines.append(f"| I{row['importIndex']:03} | {row['category']} | {ident} | {row['chapter']} | {cell(row['raw']['q'])} | {row['raw']['rightids']} | {cell(row['reason'])} |")
    lines += ['', '## Duplikate und Varianten', '',
              f"Exakte interne Dublettengruppen im Import nach Normalisierung und optionsunabhängiger Reihenfolge: {len(audit['duplicates']['importExact'])}. "
              f"Exakte vollständige Dublettengruppen im bisherigen Bestand: {len(audit['duplicates']['existingExact'])}.", '',
              'Nahe Importvarianten mit gleichem normalisiertem Stamm und mindestens 50 % gemeinsamen Optionen:', '',
              '| Importpaar | Gemeinsame Optionen | Einordnung |', '|---|---|---|']
    for pair in audit['duplicates']['importVariants']:
        lines.append(f"| {' / '.join('I'+str(i).zfill(3) for i in pair['importIndices'])} | {pair['sharedOptionFraction']:.0%} | {pair['note']} |")
    lines += ['', 'Zusätzlich sind #151/#152 im Bestand semantische Dubletten (Absatzmenge/verkaufte Menge), '
              '#8/#9/#10/#11 sowie zahlreiche Personal- und Q7-Fragen eng verwandte Varianten. '
              'Sie bleiben mit allen IDs bestehen, weil bereits Fortschritt daran hängen kann. '
              'Doppelte **Antwortoptionen** wurden gesondert geprüft: #173 enthält denselben korrekten Satz an zwei Positionen; #2 enthält Gutenberg in zwei Optionen. '
              'Beide werden nicht automatisch bewertet.', '',
              '## Offene Probleme und Grenzen', '',
              'Nicht übernommene Importfragen (F), offene C-Konflikte und nicht reparierbare D-Fälle:', '',
              '| Import | Bestand | Grund |', '|---|---|---|']
    for row in audit['questions']:
        if row['category'] == 'F' or (row['category'] == 'C' and row['verifiedSolution'] is None) or (row['category'] == 'D' and by_id[row['existingId']].get('assessmentStatus') == 'unresolved'):
            lines.append(f"| I{row['importIndex']:03} | #{row['existingId']} | {cell(row['reason'])} |")
    lines += ['', 'Weitere bereits vorher ausgeschlossene Bestandsfälle #59, #125, #177 und #246 bleiben ungeklärt. '
              '#255 ist bereits im PDF fragmentarisch, nicht lediglich durch die App beschädigt. '
              'Fünf-Optionen-Aufgaben werden weiterhin nur im Lesebuch gezeigt; dies ist eine Formatgrenze, keine fachliche Freigabe. '
              'Insbesondere verkürzte Quellenoptionen in #264/#267, die unsichere Abbildung bei #252, individuelle Lehrmodelle zu Teamperformance/THG '
              'und studentische mMn-Schlüssel sind ohne Originalfolien nicht zuverlässig unabhängig zu prüfen. '
              'Die Aufgaben #223/#225/#242/#249 wurden textlich wiederhergestellt, ihre gesamten fachlichen Lösungen damit nicht unabhängig verifiziert.', '',
              'Der gesamte Bestand wurde strukturell geprüft und mit den Importtreffern abgeglichen. '
              'Das ist keine Behauptung, jede der 278 Lösungen anhand offizieller Lehrmaterialien bestätigt zu haben. '
              'Bestehende generische Erklärungen und aus PDF-Seiten abgeleitete Kapitel sind weiterhin keine individuell belegten LV-Lösungen. '
              'Bei neu gesperrten Fragen wurde die generische Lernhilfe durch den konkreten Unsicherheitshinweis ersetzt; ursprüngliche Quellenerklärungen bleiben lesbar.', '',
              '## Phase 5/6: Validierung und Produktion', '',
              'Ausführbare Prüfungen (ohne npm-Abhängigkeiten):', '',
              '```sh', 'python3 scripts/validate_catalog.py', 'python3 -m unittest discover -s tests', 'node --test tests/catalog.test.cjs',
              'node --check app.js', 'node --check sw.js', 'python3 scripts/build.py', '```', '',
              'Die Python-Validierung prüft Schema-Invarianten, eindeutige IDs, vollständige Aufgaben, Kapitel, Options- und Schlüsselindizes, '
              'Anzahl richtiger Antworten, dokumentierte Altlasten, vollständige Importzuordnung, Import-Hash, alle Bestands-IDs und unveränderte Originaloptionen. '
              'Unvollständige, schon vorhandene Datensätze werden nur als explizit gesperrte Altlasten toleriert.', '',
              'Die Node-Regressionstests laden den echten App-Code mit isoliertem Storage. Sie prüfen alle alten IDs mit synthetischen Versuchen/Lesemarkierungen, '
              'Beherrschung über zwei Tage, neue unbearbeitete Fragen, historische Prüfungsversuche und Statistiken, '
              'DB-Felder auch außerhalb des bekannten Schemas, Randomisierung, Snapshot neuer Ergebnisse und vollständig lesenden Export. '
              'Die Bewertung wird für alle 16 Auswahlen jeder geeigneten Frage gegen die unveränderte Formel geprüft. '
              'Ungültige/mehrdeutige Fragen sowie fehlerhafte und doppelte Auswahlindizes werden zurückgewiesen. '
              'Fragen ohne richtige bzw. ohne falsche Antwort werden nicht bewertet; das ursprüngliche Schema wurde nicht auf neue Sonderformate ausgedehnt.', '',
              'Der neue Produktionsschritt verpackt ausschließlich explizit zugelassene statische Dateien nach `dist/`; '
              'private Sicherungen, Import-Arbeitsdateien und sonstige Workspace-Dateien werden nicht kopiert. '
              'Dies ist ein prüfbares statisches Artefakt, kein Deployment. '
              'Der Service-Worker-Dateicache bekommt eine neue Version und entfernt ausschließlich alte `gbu-public-`-Caches; '
              'localStorage und Origin bleiben unverändert. Ein Cache-Update ist keine Löschung von Website-/Lerndaten.', '',
              '**Ergebnis:** Produktionspaket erfolgreich erstellt; 3 Python-Tests und 9 Node-Tests bestanden, Schema-/Katalogvalidierung und JavaScript-Syntaxprüfungen erfolgreich. Reproduzierbare Zählungen stehen in `reports/question-catalog-validation.json`. '
              'Keine echten Browserdaten, keine grafischen Browser-/Gerätetests; keine automatischen Commits oder Pushes.', '',
              '## Quellenverzeichnis', '']
    for ident, source in audit['sources'].items():
        target = source.get('url', '../'+source.get('path', ''))
        lines += [f"- **{ident}**: [{source['title']}]({target}). "+source.get('authority', 'Abgerufen am 10.11.2026.')]
    (ROOT/'reports/question-catalog-audit.md').write_text('\n'.join(lines)+'\n')
if __name__ == '__main__':
    render()
