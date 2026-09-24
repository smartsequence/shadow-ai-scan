# shadow-ai-scan

How many places in your company call an AI service? Got a number in your head? Hold on to it.

This tool reads one repo end to end, lists every line that uses AI, and tells you how urgent each one is
and who should deal with it. The most common reaction after the first run: the number was wrong.

One Python file. Nothing to install, no network, nothing sent anywhere. Interface in six languages.

Other languages: [繁體中文](README.md) · [日本語](README.ja.md) · [한국어](README.ko.md) ·
[简体中文](README.zh-CN.md) · [Deutsch](README.de.md)

---

## Run it once, thirty seconds

1. Open `shadow_ai_scan.py` above, hit **Raw** at the top right, save it. The desktop is fine.
2. Open a terminal (Windows: "Terminal" or "PowerShell"; Mac: "Terminal").
3. Type this, with the path to your repo at the end:

```bash
python3 shadow_ai_scan.py /path/to/your/repo      # macOS / Linux
py shadow_ai_scan.py C:\path\to\your\repo         # Windows (if py fails, use python)
```

Not sure what the path is? **Drag the folder into the terminal window** and it types itself.

No Python yet? Skip down to "No Python yet".

---

## What you get back

A list. Every item has the file, the line number, what that line looks like, and one sentence on what it means.
The list comes in three levels — not for decoration, but because three different people have to act.

**High: a key written into the code.** Whoever opens the file has the key. Rotate it today, no discussion.
Hand it to **Security**.

**Medium: code that definitely sends data to an outside AI.** Not necessarily bad, but three questions:
is there a contract with that AI company? Has Legal read their data-processing terms? Is customer data in what gets sent?
Hand it to **Legal and Procurement**.

**Low: a package installed, or a trace in the code that is not running.** Not urgent, but somebody has to be asked:
who installed it, what for, is it still in use. Hand it to the **Engineering lead**.

Only the urgent level for now:

```bash
python3 shadow_ai_scan.py /path/to/your/repo --level high
```

---

## How it finds them

Not by asking people — a survey does not work, engineers answer by their own idea of "AI",
and in their eyes that is just writing code. It looks at the traces machines leave behind, in three places:

1. **Imports in the code.** Use an AI service and the code imports its package, say `from openai import OpenAI`. That cannot hide.
2. **Hosts in config files.** Code can be wrapped as deep as you like, but the traffic needs a way out,
   and a host like `api.openai.com` ends up in a config file.
3. **The keys themselves.** Every vendor's keys start the same way: OpenAI `sk-proj-`, Anthropic `sk-ant-`, Google `AIza`.
   A string like that means somebody is using it, and using it badly.

Three clues together answer the question at the top.

---

## What it cannot see

Let me be direct: this is keyword matching, not deep analysis. At the end of every full run it prints the four things it cannot see:

1. **AI calls wrapped in a module of your own.** The code only says `from vendor.llm_client import ask`;
   which service sits underneath is invisible. Say somebody wrote an internal module two years ago, left, and nobody remembers what it connects to.
2. **Package names resolved at runtime.** If the name comes from an environment variable or a config file, the import line has nothing to match.
3. **Comments at the end of a line, or inside multi-line strings.** It only looks at the start of a line, so it gets these wrong.
4. **Installed is not the same as used.** A dependency list only proves somebody installed it.

So it finds ten; there may well be more. **This list is where the investigation starts, not the whole of it.**
If your repo has a `vendor/` or `internal/` directory, that is where someone has to look by hand.

The first two are not laziness. Seeing through them takes cross-file data-flow analysis, and that is no longer a tool you write in an afternoon.

---

## No Python yet?

Only Python itself. No packages.

| Your system | Where to type | Check first | If it is missing |
|---|---|---|---|
| Windows | Right-click Start → "Terminal" or "PowerShell" | `py --version` | Get it from [python.org](https://www.python.org/downloads/); **tick** Add python.exe to PATH during setup |
| macOS | Command + Space, search "Terminal" | `python3 --version` | `brew install python`, or python.org |
| Linux | Your usual terminal | `python3 --version` | Usually already there; otherwise `sudo apt install python3` |

3.9 or newer, so anything from 2021 onward.

The three places people get stuck:

- Windows: typing `python` opens the Microsoft Store? Use `py`; if that fails, reinstall Python and tick PATH this time.
- Mac: `python` says command not found? Mac only has `python3`. That is normal.
- Garbled non-Latin text? Almost always the old Command Prompt. Easiest fix: use **Windows Terminal** (built into Windows 11, right-click Start);
  if you cannot, run `chcp 65001` first. Boxes instead of garbage means the font has no glyphs for that script — pick a font that does.

⚠ The output contains fragments of real keys. Look before you screenshot it or paste it anywhere.

---

## A little more

**Switch language**: 繁體中文, English, 日本語, 한국어, 简体中文, Deutsch. With no flag it follows your OS and falls back to English.

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # the environment variable works too
```

`--level` accepts the word in any of the six languages: `--level high`, `--level 高`, `--level 높은 위험` are the same.

**Wire it into CI**: clean today, grown back in three months. In CI, whoever adds an AI call fails that commit —
far cheaper than an audit every quarter. Exit code 1 if anything is High, 0 otherwise; 2 for a bad argument or a missing path.

```bash
python3 shadow_ai_scan.py . --level high || echo "key leak - failing this commit"
```

**Change it**: the lists at the top of the file are the entire configuration. Another AI vendor, another host, another extension —
just add it. They sit there so you can edit them.

---

## Which files it opens (for anyone checking the scope)

**The extension or file name decides; anything not listed below is never opened.**

- Code: `.py` `.ipynb` `.js` `.ts` `.tsx` `.go` `.rb` `.java` `.cs` `.vb` `.php` `.rs` `.kt` `.kts` `.swift` `.scala` `.dart` `.c` `.cc` `.cpp` `.h` `.hpp` `.sh` `.ps1`
- Config: `.yaml` `.yml` `.json` `.toml` `.ini` `.txt` `.config` `.xml` `.properties` `.gradle` `.tf` `.tfvars` `.env` / `.env.*` (including `.env.local`, `.env.production`), `Dockerfile`
- Dependency lists: `requirements.txt` `Pipfile` `pyproject.toml` `package.json` `go.mod` `Gemfile` `*.csproj` `*.vbproj` `*.fsproj` `packages.config` `pom.xml` `build.gradle(.kts)` `composer.json` `Cargo.toml` `Package.swift`

`.md` is skipped on purpose: docs mention `api.openai.com` all the time. Files over 2 MB are skipped;
`.git`, `node_modules`, `__pycache__`, `.venv`, `venv`, `dist` and `build` are not entered.

The three clues have different reach. Key patterns and AI hosts are **language agnostic** and apply to every file type above
(keys: four prefixes only — Anthropic, OpenAI new and legacy, Google; hosts: seven).
SDK imports key on `import` / `from` / `require` / `using` / `use`, case insensitive, which covers Python, JS/TS, Go, Ruby, Java, Kotlin, Swift, Scala, Dart, C#/VB.NET, Rust and PHP.
On import lines and in dependency lists the vendor name is matched as a substring, so Rust's `async_openai`, Swift's `OpenAIKit` and C#'s `Anthropic.SDK` are caught; everywhere else it is whole words.
Dependency lists are always reported as low risk.

---

## Licence

MIT. Change it, use it internally, fold it into your own tooling — all fine.

---

## Where this came from

This is the companion tool for an episode about how many unregistered AI calls a company is really running,
and why a memo banning them does nothing — like a "No Parking" sign in an alley with no cameras.

It deliberately handles one repo and stops. If what you have is two hundred repos, on a schedule, with an audit trail that holds up,
and false positives that stop coming back, that is a different class of problem. We built **ForgeHelm** for that.

But scan this one repo first. Back to the number you were holding — still think it is right?
