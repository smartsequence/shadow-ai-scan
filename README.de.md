# shadow-ai-scan

Durchsucht ein Repository, listet jede Zeile auf, die einen KI-Dienst aufruft, und versieht jeden Fund mit einer Risikostufe und dem zuständigen Team.

Eine Python-Datei, nur Standardbibliothek. Keine Installation, kein Netzwerkzugriff, nichts wird nach Hause gemeldet.

**Sechs Oberflächensprachen**: Deutsch, 繁體中文, English, 日本語, 한국어, 简体中文.

Andere Sprachen: [繁體中文](README.md) · [English](README.en.md) ·
[日本語](README.ja.md) · [한국어](README.ko.md) · [简体中文](README.zh-CN.md)

---

## In dreissig Sekunden (wenn Python schon da ist)

Es ist nur eine Datei. `shadow_ai_scan.py` oeffnen, oben rechts auf **Raw**, speichern. Der Ort ist egal, der Schreibtisch reicht. Das Repository zu klonen geht genauso.

Dann ein Terminal oeffnen und ausfuehren:

```bash
# macOS / Linux
python3 shadow_ai_scan.py /pfad/zu/ihrem/repo

# Windows (falls `py` nicht geht, `python`)
py shadow_ai_scan.py C:\pfad\zu\ihrem\repo
```

**Pfad zum Repository unbekannt?** Ziehen Sie den Ordner in das Terminalfenster, dann steht der Pfad von selbst da.

Nur die dringende Stufe:

```bash
python3 shadow_ai_scan.py /pfad/zu/ihrem/repo --level high
```

Die Beispiele unten schreiben durchgehend `python3`; unter Windows entsprechend `py`.

## Noch kein Python?

Ausser Python selbst ist nichts zu installieren. Keine Pakete, kein Netzwerk.

| System | Wo tippen | Zuerst pruefen | Falls es fehlt |
|---|---|---|---|
| Windows | Rechtsklick auf Start, dann Terminal oder PowerShell | `py --version` | Von [python.org](https://www.python.org/downloads/) holen und bei der Installation Add python.exe to PATH **ankreuzen** |
| macOS | Command + Leertaste, nach Terminal suchen | `python3 --version` | `brew install python`, oder python.org |
| Linux | Ihr uebliches Terminal | `python3 --version` | Meist schon vorhanden, sonst `sudo apt install python3` o. ae. |

Python 3.9 oder neuer (alles ab 2021).

**Die drei haeufigsten Stolpersteine**

- `python` unter Windows oeffnet den Microsoft Store: stattdessen `py` verwenden, oder Python mit gesetztem PATH-Haken neu installieren.
- `python` unter macOS meldet command not found: macOS hat nur `python3`. Das ist normal.
- Nicht-lateinische Zeichen werden in der alten Eingabeaufforderung zu Zeichensalat: vorher `chcp 65001` ausfuehren, oder Windows Terminal benutzen.

⚠ Die Ausgabe enthaelt Bruchstuecke echter Schluessel. Erst hinsehen, dann Screenshot oder Copy-Paste.

---

## Wonach gesucht wird

Drei Spuren. Maschinen lügen nicht, und was gelaufen ist, hat Spuren hinterlassen.

1. **Code** — Importe offizieller SDKs wie `from openai import OpenAI` oder `import anthropic`.
2. **Konfiguration** — API-Domains wie `api.openai.com`. Code lässt sich beliebig tief verpacken, der Datenverkehr braucht trotzdem einen Ausgang.
3. **Schlüssel** — jeder Anbieter hat feste Präfixe: `sk-ant-api03-`, `sk-proj-`, `AIza`.

---

## Drei Stufen, weil drei verschiedene Personen handeln müssen

Wenn jeder Fund gleich wichtig aussieht, ist keiner wichtig. Deshalb trägt jeder Fund eine Stufe und eine Zuständigkeit.

| Stufe | Situation | Zuständig | Dringlichkeit |
|---|---|---|---|
| Hoch | Ein Schlüssel steht im Code oder in der Konfiguration | Security | Heute austauschen, ohne Diskussion |
| Mittel | Code sendet nachweislich Daten an eine externe KI | Recht und Einkauf | Gibt es einen Vertrag? Was wird gesendet? |
| Gering | Paket installiert oder Spur vorhanden, läuft aber nicht | Engineering-Lead | Nicht dringend, aber jemand muss gefragt werden |

Jeder Fund nennt Datei, Zeilennummer, die betreffende Zeile und einen Satz dazu, was das bedeutet. Die Liste ist direkt verteilbar.

---

## Geltungsbereich: welche Sprachen wirklich abgedeckt sind

**Eine Endungs-Whitelist entscheidet alles.** Dateien ausserhalb dieser Liste werden **gar nicht geoeffnet**:

`.py` `.js` `.ts` `.tsx` `.go` `.rb` `.java` `.cs` `.yaml` `.yml` `.json` `.toml` `.ini` `.env` `.txt` `.example`

PHP, Rust, Kotlin, Swift, C/C++, `.xml` (auch `pom.xml`), Dockerfiles und Shell-Skripte werden also
nicht durchsucht. Ein dort hartcodierter Schluessel ist fuer dieses Werkzeug unsichtbar.

Auch innerhalb der Whitelist decken die drei Spuren nicht dasselbe ab:

| Spur | Abdeckung |
|---|---|
| Schluesselmuster | **Sprachunabhaengig**, jede Datei der Whitelist. Aber nur vier Praefixe: Anthropic, OpenAI (neu und alt), Google |
| KI-Domains | **Sprachunabhaengig**, sieben Domains |
| SDK-Importe | Haengt an `import` / `from` / `require` → Python, JS/TS, Go, Ruby, Java funktionieren; **C# benutzt `using` und faellt durch** (`.cs` wird gelesen, aber nur Schluessel und Domains greifen) |
| Abhaengigkeitslisten | Nur fuenf: `requirements.txt`, `package.json`, `pyproject.toml`, `go.mod`, `Gemfile`. `pom.xml`, `build.gradle`, `composer.json`, `.csproj` und `Cargo.toml` werden nicht als Abhaengigkeitsliste gelesen |

Die SDK-Liste enthaelt 10 Eintraege in Python-Schreibweise; JS-Namen mit Scope wie `@anthropic-ai/sdk`
oder `@google/generative-ai` treffen nicht.

Zwei weitere Punkte: Dateien ueber 2 MB werden uebersprungen, und `.git`, `node_modules`,
`__pycache__`, `.venv`, `venv`, `dist` und `build` werden nicht betreten.

Das alles zu erweitern ist einfach — die Listen ganz oben in der Datei sind die gesamte Konfiguration.
Sie stehen dort, damit Sie sie aendern.

---

## Was dieses Werkzeug nicht sieht

Das ist ein Abgleich von Schlüsselwörtern, keine tiefe statische Analyse. Am Ende jedes vollständigen Laufs gibt es diese vier Grenzen selbst aus:

1. **KI-Aufrufe, die in ein eigenes Modul verpackt sind.** Im Code steht nur `from vendor.llm_client import ask`, der Dienst darunter bleibt unsichtbar.
2. **Paketnamen, die erst zur Laufzeit feststehen.** Kommt der Name aus einer Umgebungsvariable oder einer Konfiguration, gibt es in der import-Zeile nichts zu vergleichen.
3. **Kommentare am Zeilenende oder in mehrzeiligen Strings.** Das Werkzeug sieht nur den Zeilenanfang.
4. **Installiert heißt nicht benutzt.** Eine Abhängigkeitsliste beweist nur die Installation.

Es hat N Stellen gefunden. Es können mehr sein. **Diese Liste ist der Anfang der Untersuchung, nicht ihr Ergebnis.**

Punkt 1 und 2 sind keine Bequemlichkeit, sondern die Grenze des Ansatzes: dahinter zu sehen erfordert dateiübergreifende Datenflussanalyse, und das ist kein Werkzeug mehr, das man an einem Nachmittag schreibt.

---

## In der CI

Exit-Code 1, sobald etwas auf Hoch steht, sonst 0; 2 bei falschem Argument oder fehlendem Pfad.

```bash
python3 shadow_ai_scan.py . --level high || echo "Schluesselleck - dieser Commit wird abgelehnt"
```

Heute sauber, in drei Monaten wieder nachgewachsen. Das in die CI zu hängen ist deutlich billiger als eine Inventur pro Quartal.

---

## Sprache wechseln

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # geht auch als Umgebungsvariable
```

Ohne Angabe folgt es der Locale des Betriebssystems und fällt auf Englisch zurück.

`--level` akzeptiert das Wort in allen sechs Sprachen: `--level high`, `--level 高`, `--level 높은 위험` funktionieren alle.

---

## Lizenz

MIT. Ändern, intern einsetzen, in eigene Werkzeuge einbauen — alles erlaubt.

---

## Woher dieses Werkzeug kommt

Es ist das Begleitwerkzeug zu einer Folge darüber, wie viele nicht registrierte KI-Aufrufe in einem Unternehmen tatsächlich laufen und warum ein Verbotsrundschreiben nichts daran ändert.

Es bearbeitet bewusst ein Repository und hört dann auf. Wenn es zweihundert Repositories sind, nach Zeitplan, mit einem Protokoll, das einer Prüfung standhält, und mit Fehlalarmen, die nicht immer wiederkommen, dann ist das eine andere Größenordnung — dafür haben wir **ForgeHelm** gebaut.

Aber scannen Sie zuerst dieses eine Repository. Die erste Überraschung ist bei den meisten dieselbe: die Zahl stimmt nicht.
