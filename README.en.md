# shadow-ai-scan

Scan one repo, list every line that calls an AI service, and tag each finding with a risk level and the team it should go to.

One Python file, standard library only. No install, no network, nothing phoned home.

**Six interface languages**: English, 繁體中文, 日本語, 한국어, 简体中文, Deutsch.

Other languages: [繁體中文](README.md) · [日本語](README.ja.md) ·
[한국어](README.ko.md) · [简体中文](README.zh-CN.md) · [Deutsch](README.de.md)

---

## Thirty seconds (if you already have Python)

Download the one file: open `shadow_ai_scan.py`, hit **Raw** at the top right, save it. Anywhere is fine — the desktop will do. Cloning the repo works just as well.

Then open a terminal and run:

```bash
# macOS / Linux
python3 shadow_ai_scan.py /path/to/your/repo

# Windows (if `py` does not work, use `python`)
py shadow_ai_scan.py C:\path\to\your\repo
```

**Do not know the path to your repo?** Drag the folder into the terminal window and the path types itself.

Only the urgent level:

```bash
python3 shadow_ai_scan.py /path/to/your/repo --level high
```

The examples below all say `python3`; on Windows use `py` instead.

## No Python yet?

There is nothing to install beyond Python itself. No packages, no network.

| System | Where to type | Check first | If it is missing |
|---|---|---|---|
| Windows | Right-click Start, pick Terminal or PowerShell | `py --version` | Get it from [python.org](https://www.python.org/downloads/); **tick** Add python.exe to PATH during setup |
| macOS | Command + Space, search for Terminal | `python3 --version` | `brew install python`, or python.org |
| Linux | Your usual terminal | `python3 --version` | Usually already there; otherwise `sudo apt install python3` or your package manager |

Python 3.9 or newer (anything from 2021 onward).

**The three things people get stuck on**

- Typing `python` on Windows opens the Microsoft Store: use `py` instead, or reinstall Python with the PATH box ticked.
- Typing `python` on macOS says command not found: macOS only ships `python3`. That is normal.
- Non-Latin text comes out as mojibake in the old Command Prompt: run `chcp 65001` first, or use Windows Terminal.

⚠ The output contains fragments of real keys. Look before you screenshot it or paste it somewhere.

---

## What it looks for

Three clues. Machines do not lie, and everything that ran left a trace.

1. **Code** — official SDK imports such as `from openai import OpenAI` or `import anthropic`.
2. **Config** — API hosts such as `api.openai.com`. Code can be wrapped as deep as you like; the traffic still needs a way out.
3. **Keys** — every vendor's keys start the same way: `sk-ant-api03-`, `sk-proj-`, `AIza`.

---

## Three levels, because three different people have to act

If every finding looks equally important, none of them is. So each one carries a level and an owner.

| Level | What it is | Route to | How urgent |
|---|---|---|---|
| High | A key sitting in code or config | Security | Rotate it today, no discussion |
| Medium | Code that definitely sends data to an outside AI | Legal and Procurement | Is there a contract? What is being sent? |
| Low | A package installed, or a trace that is not running | Engineering lead | Not urgent, but somebody has to be asked |

Every finding prints the file, the line number, the offending line, and one sentence on what it means. The list is ready to hand out.

---

## Scope: which languages it actually covers

**An extension allowlist decides everything.** Files outside this list are **never opened**:

`.py` `.js` `.ts` `.tsx` `.go` `.rb` `.java` `.cs` `.php` `.rs` `.kt` `.kts` `.swift` `.yaml` `.yml` `.json` `.toml` `.ini` `.env` `.txt` `.example`

So C/C++, Scala, Elixir, `.xml` (including `pom.xml`), Dockerfiles and shell scripts are not scanned
at all — a hardcoded key in one of those is invisible to this tool.

Within the allowlist, the three clues do not cover the same ground:

| Clue | Coverage |
|---|---|
| Key patterns | **Language agnostic**, any allowlisted file. But only four prefixes: Anthropic, OpenAI (new and legacy), Google |
| AI hosts | **Language agnostic**, seven hosts |
| SDK imports | Five keywords, **case insensitive**: `import` / `from` / `require` / `using` / `use`. Covers Python, JS/TS, Go, Ruby, Java, Kotlin, Swift (`import`), C#/VB.NET (`using`), Rust and PHP (`use`) |
| Dependency lists | Five only: `requirements.txt`, `package.json`, `pyproject.toml`, `go.mod`, `Gemfile`. `pom.xml`, `build.gradle`, `composer.json`, `.csproj` and `Cargo.toml` are not read as dependency lists — `.kts` files are read, but a Gradle `implementation(...)` line is not an import and will not be caught |

On an import line the vendor name is matched as a **substring**, so Rust's `async_openai`, Swift's
`OpenAIKit` and C#'s `Anthropic.SDK` are all caught. That relaxation applies to import lines only;
everywhere else matching stays on whole words.

Two more: files over 2 MB are skipped, and `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`,
`dist` and `build` are not entered.

Widening any of this is easy — those lists at the top of the file are the entire configuration.
They sit there so you can edit them.

---

## What it cannot see

This is a keyword matcher, not deep static analysis. It prints these four limits itself at the end of every full run:

1. **AI calls wrapped in a module of your own.** The code only says `from vendor.llm_client import ask`; the service underneath is invisible.
2. **Package names resolved at runtime.** When the name comes from an environment variable or a config file, the import line has nothing to match.
3. **Comments at the end of a line, or inside multi-line strings.** The tool only looks at the start of a line.
4. **Installed is not used.** A dependency list only proves somebody installed it.

It found N. There may well be more. **This list is where the investigation starts, not the whole of it.**

Limits 1 and 2 are not laziness, they are the boundary of the approach: seeing through them needs cross-file data-flow analysis, which is no longer a tool you write in an afternoon.

---

## In CI

Exit code 1 if anything is High, 0 otherwise; 2 for a bad argument or a missing path.

```bash
python3 shadow_ai_scan.py . --level high || echo "key leak - failing this commit"
```

Clean today, grown back in three months. Wiring this into CI is far cheaper than an audit every quarter.

---

## Switching language

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # environment variable works too
```

With no flag it follows your OS locale, falling back to English.

`--level` accepts the word in any of the six languages: `--level high`, `--level 高`, `--level 높은 위험` all work.

---

## Licence

MIT. Change it, use it internally, fold it into your own tooling — all fine.

---

## Where this came from

This is the companion tool for an episode about how many unregistered AI calls a company is actually running, and why a memo banning them does nothing.

It deliberately handles one repo and stops when it is done. If what you have is two hundred repos, on a schedule, with an audit trail that holds up, and false positives that stop coming back, that is a different class of problem — we built **ForgeHelm** for that.

But scan this one repo first. For most people the first surprise is the same one: the number is wrong.
