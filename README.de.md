# shadow-ai-scan

An wie vielen Stellen ruft Ihr Unternehmen einen KI-Dienst auf? Haben Sie eine Zahl im Kopf? Behalten Sie sie.

Dieses Werkzeug liest ein Repository von vorn bis hinten, listet jede Zeile auf, die KI nutzt, und sagt Ihnen,
wie dringend jede davon ist und wer sich darum kümmern soll. Die häufigste Reaktion nach dem ersten Lauf: die Zahl stimmte nicht.

Eine Python-Datei. Nichts zu installieren, kein Netzwerk, nichts wird irgendwohin geschickt. Oberfläche in sechs Sprachen.

Andere Sprachen: [繁體中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) ·
[한국어](README.ko.md) · [简体中文](README.zh-CN.md)

---

## Einmal laufen lassen, dreißig Sekunden

1. Oben `shadow_ai_scan.py` öffnen, rechts oben auf **Raw**, speichern. Der Desktop reicht.
2. Ein Terminal öffnen (Windows: „Terminal“ oder „PowerShell“; Mac: „Terminal“).
3. Diese Zeile tippen, hinten den Pfad zu Ihrem Repository:

```bash
python3 shadow_ai_scan.py /pfad/zu/ihrem/repo      # macOS / Linux
py shadow_ai_scan.py C:\pfad\zu\ihrem\repo         # Windows (geht py nicht, dann python)
```

Pfad unbekannt? **Den Ordner ins Terminalfenster ziehen**, dann steht er von selbst da.

Noch kein Python? Weiter unten bei „Noch kein Python“.

---

## Was Sie zurückbekommen

Eine Liste. Jeder Eintrag hat Datei, Zeilennummer, die Zeile selbst und einen Satz dazu, was das bedeutet.
Die Liste hat drei Stufen — nicht zur Zierde, sondern weil drei verschiedene Leute handeln müssen.

**Hohes Risiko: ein Schlüssel steht im Code.** Wer die Datei öffnet, hat den Schlüssel. Heute austauschen, ohne Diskussion.
An **Security**.

**Mittleres Risiko: Code sendet nachweislich Daten an eine externe KI.** Nicht zwingend schlimm, aber drei Fragen:
Gibt es einen Vertrag mit diesem KI-Anbieter? Hat die Rechtsabteilung dessen Datenverarbeitungsbedingungen gelesen?
Stecken personenbezogene Kundendaten in dem, was gesendet wird? An **Recht und Einkauf**.

**Geringes Risiko: ein Paket ist installiert, oder es gibt eine Spur im Code, die nicht ausgeführt wird.** Nicht dringend, aber jemand muss gefragt werden:
wer hat es installiert, wofür, wird es noch benutzt. An den **Engineering-Lead**.

Erst einmal nur die dringendste Stufe:

```bash
python3 shadow_ai_scan.py /pfad/zu/ihrem/repo --level high
```

---

## Wie es die Stellen findet

Nicht durch Nachfragen — eine Umfrage bringt nichts, Entwickler antworten nach ihrem eigenen Begriff von „KI“,
und in ihren Augen ist das einfach Programmieren. Es schaut auf die Spuren, die Maschinen hinterlassen, an drei Stellen:

1. **Importe im Code.** Wer einen KI-Dienst nutzt, importiert dessen Paket, etwa `from openai import OpenAI`. Das lässt sich nicht verstecken.
2. **Adressen in Konfigurationsdateien.** Code lässt sich beliebig tief verpacken, aber der Datenverkehr braucht einen Ausgang,
   und eine Adresse wie `api.openai.com` landet in einer Konfigurationsdatei.
3. **Die Schlüssel selbst.** Jeder Anbieter hat feste Präfixe: OpenAI `sk-proj-`, Anthropic `sk-ant-`, Google `AIza`.
   So eine Zeichenkette heißt: jemand benutzt den Dienst, und zwar auf problematische Weise.

Die drei zusammen beantworten die Frage ganz oben.

---

## Was dieses Werkzeug nicht sieht

Ganz offen: das ist ein Abgleich von Schlüsselwörtern, keine tiefe Analyse. Am Ende jedes vollständigen Laufs gibt es selbst die vier Dinge aus, die es nicht sieht:

1. **KI-Aufrufe, die in ein eigenes Modul verpackt sind.** Im Code steht nur `from vendor.llm_client import ask`; welcher Dienst darunter liegt, bleibt unsichtbar.
   Etwa: jemand hat vor zwei Jahren ein internes Modul geschrieben, ist gegangen, und niemand weiß mehr, wohin es sich verbindet.
2. **Paketnamen, die erst zur Laufzeit feststehen.** Kommt der Name aus einer Umgebungsvariable oder Konfiguration, gibt es in der Import-Zeile nichts zu vergleichen.
3. **Kommentare am Zeilenende oder in mehrzeiligen Strings.** Es sieht nur den Zeilenanfang und liegt hier daneben.
4. **Installiert heißt nicht benutzt.** Eine Abhängigkeitsliste beweist nur die Installation.

Findet es also zehn, können es in Wirklichkeit mehr sein. **Diese Liste ist der Anfang der Untersuchung, nicht ihr Ergebnis.**
Hat Ihr Repository ein `vendor/` oder `internal/`, muss dort jemand von Hand hineinsehen.

Die ersten beiden Punkte sind keine Faulheit. Dahinter zu sehen erfordert dateiübergreifende Datenflussanalyse, und das ist kein Werkzeug mehr, das man an einem Nachmittag schreibt.

---

## Noch kein Python?

Nur Python selbst. Keine Pakete.

| Ihr System | Wo tippen | Zuerst prüfen | Falls es fehlt |
|---|---|---|---|
| Windows | Rechtsklick auf Start → „Terminal“ oder „PowerShell“ | `py --version` | Von [python.org](https://www.python.org/downloads/) holen und bei der Installation Add python.exe to PATH **ankreuzen** |
| macOS | Command + Leertaste, „Terminal“ suchen | `python3 --version` | `brew install python`, oder python.org |
| Linux | Ihr übliches Terminal | `python3 --version` | Meist schon vorhanden, sonst `sudo apt install python3` (Ubuntu/Debian; andere Distributionen über ihre eigene Paketverwaltung) |

3.9 oder neuer, also alles ab 2021.

Die drei häufigsten Stolpersteine:

- Windows: `python` öffnet den Microsoft Store? `py` verwenden; geht das nicht, Python neu installieren und diesmal PATH ankreuzen.
- Mac: `python` meldet command not found? Der Mac hat nur `python3`. Das ist normal.
- Zeichensalat? Direkt im Fenster passiert das nicht — das Werkzeug schreibt selbst UTF-8. Es passiert, wenn Sie die Ausgabe in eine Datei speichern
  oder an ein anderes Programm weiterreichen und dort lesen. Dann unter Windows vorher `chcp 65001` ausführen: das stellt das aktuelle Fenster auf UTF-8 um,
  65001 ist schlicht die Nummer, die Windows für UTF-8 vergibt. Nur Windows; macOS und Linux brauchen das nicht.
- Kästchen statt Zeichensalat? Die Schriftart der alten Konsole hat diese Zeichen nicht. Nicht in Schriftmenüs suchen — zu **Windows Terminal** wechseln,
  das nimmt automatisch eine Systemschrift, die sie hat (in Windows 11 enthalten, Rechtsklick auf Start; unter Windows 10 „Windows Terminal“ aus dem Microsoft Store installieren).
  Das Terminal von macOS ebenso. Unter Linux die Schriften einmal installieren: `sudo apt install fonts-noto-cjk` (Ubuntu/Debian).

⚠ Die Ausgabe enthält Bruchstücke echter Schlüssel. Erst hinsehen, dann Screenshot oder Copy-Paste.

---

## Ein Schritt weiter

**Sprache wechseln**: 繁體中文, English, 日本語, 한국어, 简体中文, Deutsch. Ohne Angabe folgt es Ihrem Betriebssystem und fällt sonst auf Englisch zurück.

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # geht auch als Umgebungsvariable (macOS / Linux)
$env:SHADOW_AI_LANG="ko"; py shadow_ai_scan.py .   # so in Windows PowerShell
```

`--level` akzeptiert das Wort in allen sechs Sprachen: `--level high`, `--level 高`, `--level 높음` sind dasselbe; auf Deutsch auch `hoch`, `mittel`, `gering`.

**In die CI hängen**: heute sauber, in drei Monaten wieder nachgewachsen. In der CI fällt der Commit durch, der einen KI-Aufruf hinzufügt —
deutlich billiger als eine Inventur pro Quartal. Exit-Code 1, sobald ein Fund auf „hoch“ steht, sonst 0; 2 bei falschem Argument oder fehlendem Pfad.

```bash
python3 shadow_ai_scan.py . --level high || echo "Schluesselleck - dieser Commit wird abgelehnt"
```

**Anpassen**: die Listen ganz oben in der Datei sind die gesamte Konfiguration. Ein weiterer KI-Anbieter, eine Domain, eine Endung —
einfach ergänzen. Sie stehen dort, damit Sie sie ändern.

---

## Welche Dateien es öffnet (für alle, die den Umfang prüfen wollen)

**Endung oder Dateiname entscheiden; alles, was unten nicht steht, wird nie geöffnet.**

- Code: `.py` `.ipynb` `.js` `.ts` `.tsx` `.go` `.rb` `.java` `.cs` `.vb` `.php` `.rs` `.kt` `.kts` `.swift` `.scala` `.dart` `.c` `.cc` `.cpp` `.h` `.hpp` `.sh` `.ps1`
- Konfiguration: `.yaml` `.yml` `.json` `.toml` `.ini` `.txt` `.config` `.xml` `.properties` `.gradle` `.tf` `.tfvars` `.example` `.env` / `.env.*` (auch `.env.local`, `.env.production`), `Dockerfile` / `Containerfile`
- Abhängigkeitslisten: `requirements.txt` `Pipfile` `pyproject.toml` `package.json` `go.mod` `Gemfile` `*.csproj` `*.vbproj` `*.fsproj` `packages.config` `pom.xml` `build.gradle(.kts)` `composer.json` `Cargo.toml` `Package.swift`

`.md` wird absichtlich ausgelassen: in Dokumentation taucht `api.openai.com` ständig auf, das wäre nur Rauschen. Dateien über 2 MB werden übersprungen;
`.git`, `node_modules`, `__pycache__`, `.venv`, `venv`, `dist` und `build` werden nicht betreten.

Die drei Spuren reichen unterschiedlich weit. Schlüsselmuster und KI-Domains sind **sprachunabhängig** und gelten für jede Dateiart oben
(Schlüssel: nur vier Präfixe — Anthropic, OpenAI neu und alt, Google; Domains: sieben).
SDK-Importe hängen an `import` / `from` / `require` / `using` / `use`, ohne Beachtung der Groß-/Kleinschreibung, und decken damit Python, JS/TS, Go, Ruby, Java, Kotlin, Swift, Scala, Dart, C#/VB.NET, Rust und PHP ab.
In Import-Zeilen und Abhängigkeitslisten wird der Herstellername als Teilzeichenkette gesucht, daher werden Rusts `async_openai`, Swifts `OpenAIKit` und C#s `Anthropic.SDK` gefunden; sonst gelten ganze Wörter.
Abhängigkeitslisten werden immer als geringes Risiko gemeldet.

---

## Lizenz

MIT. Ändern, intern einsetzen, in eigene Werkzeuge einbauen — alles erlaubt.

---

## Woher dieses Werkzeug kommt

Es ist das Begleitwerkzeug zu einer Folge darüber, wie viele nicht registrierte KI-Aufrufe in einem Unternehmen wirklich laufen,
und warum ein Verbotsrundschreiben nichts daran ändert — wie ein „Parken verboten“-Schild in einer Gasse ohne eine einzige Kamera.

Es nimmt sich bewusst nur ein Repository vor und hört dann auf. Wenn es zweihundert Repositories sind, nach Zeitplan, mit einem Protokoll,
das einer Prüfung standhält, und Fehlalarme nicht jedes Mal wiederkommen sollen, ist das eine andere Größenordnung. Dafür haben wir **ForgeHelm** gebaut.

Aber scannen Sie zuerst dieses eine Repository. Zurück zu der Zahl von oben — glauben Sie noch, dass sie stimmt?
