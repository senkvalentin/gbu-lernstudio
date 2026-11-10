# Veröffentlichung und Repository-Einstellungen

Für die öffentliche Erstveröffentlichung wurden ausschließlich diese Dateien geprüft: `.gitignore`, `README.md`, `app.js`, `build_data.py`, `docs/`, `examples/questions.demo.json`, `icon.svg`, `index.html`, `manifest.webmanifest`, `style.css`, `sw.js`.

Die Original-PDF, die daraus abgeleitete `questions.json`, Audit-CSV-Dateien, Konfliktentscheidungen und lokale Versions-/Import-/Reparaturprotokolle bleiben ausgeschlossen. Es lag keine lokale Git-Historie vor; das Zielrepository wurde vor Veröffentlichung als leer gemeldet. In den geprüften Veröffentlichungsdateien wurden keine Zugangsdaten gefunden. Dies ist keine umfassende Rechteprüfung der ursprünglichen privaten Lernmaterialien.

JavaScript-Syntax, Demo-Daten, Dashboard, Bewertung, Prüfungssperre und Lesebuch wurden geprüft; `git diff --cached --check` war erfolgreich. Es gibt keinen Buildprozess und keine bestehende Testsuite. Die Sandbox blockierte das Binden eines lokalen HTTP-Ports und das Anlegen von `.git` im ursprünglichen Projektordner. Die Git-Staging-Prüfung erfolgte deshalb in einer temporären Arbeitskopie. Für einen dauerhaften lokalen Git-Checkout nach der Veröffentlichung einen frischen Clone in einem neuen Ordner anlegen; private Materialien nur lokal ergänzen.

## Beschreibung und Topics

Die verbundene GitHub-Schnittstelle bietet keine Änderung der Repository-Metadaten. Im Repository unter **About → Zahnrad** setzen:

Beschreibung:

> Interaktives Lernstudio für Grundlagen der Betriebs- und Unternehmensführung (TU Wien) mit Übungen, Lernfortschritt und Prüfungsvorbereitung.

Topics: `tu-wien`, `learning-app`, `study-tool`, `exam-preparation`, `education`, `pwa`.

Alternativ bei installierter und authentifizierter GitHub CLI:

```sh
gh repo edit senkvalentin/gbu-lernstudio --description 'Interaktives Lernstudio für Grundlagen der Betriebs- und Unternehmensführung (TU Wien) mit Übungen, Lernfortschritt und Prüfungsvorbereitung.' --add-topic tu-wien --add-topic learning-app --add-topic study-tool --add-topic exam-preparation --add-topic education --add-topic pwa
```

## Weitere lokale Prüfung

```sh
git clone https://github.com/senkvalentin/gbu-lernstudio.git gbu-lernstudio-public
cd gbu-lernstudio-public
node --check app.js
node --check sw.js
python3 -m http.server 8080 --bind 127.0.0.1
```

`http://localhost:8080` im Browser öffnen und Training, Lesebuch sowie Offlinebetrieb mit Demodaten testen. Node.js ist nur für diese Syntaxprüfung nötig. Eine Lizenzentscheidung steht aus; GitHub Pages wurde nicht aktiviert.

## Ergebnis des Übertragungsversuchs

Die GitHub-App konnte das öffentliche Repository lesen, aber das Schreiben wurde mit `403 Resource not accessible by integration` abgelehnt. Im Terminal konnte `github.com` nicht aufgelöst werden; `gh` war nicht installiert. Es wurden über die App keine Dateien angelegt.

Der geprüfte Release ist als lokales Git-Bundle unter `private/gbu-public-release.bundle` gesichert. Dieser Pfad ist ignoriert. Nach Wiederherstellung von Netzwerk und eigener Git-Authentifizierung lässt er sich in einem neuen Ordner veröffentlichen:

```sh
git clone /absoluter/pfad/zum/gbu-lernapp/private/gbu-public-release.bundle gbu-lernstudio-release
cd gbu-lernstudio-release
git remote set-url origin https://github.com/senkvalentin/gbu-lernstudio.git
git ls-remote origin
# Wenn das Repository weiterhin leer ist:
git push -u origin main
```

Falls das Ziel inzwischen Commits enthält, zuerst `git fetch origin` ausführen und die Historien prüfen; keinen Force-Push verwenden. Für HTTPS eine vorhandene Credential-Manager-Anmeldung verwenden oder GitHub CLI installieren und `gh auth login` sowie `gh auth setup-git` ausführen. Keine Tokens in Dateien oder Remote-URLs eintragen.
