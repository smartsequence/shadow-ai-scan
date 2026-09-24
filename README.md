# shadow-ai-scan

你們公司有幾個地方在呼叫 AI？心裡有個數字了嗎——先記著。

這支工具會把一個 repo 從頭掃到尾，把每一行在用 AI 的地方列出來，告訴你它有多急、該交給誰。
多數人第一次跑完的反應是：數字不對。

只有一個 Python 檔，不用安裝、不連網路、不會把任何東西傳出去。介面有六種語言。

其他語言：[English](README.en.md) · [日本語](README.ja.md) · [한국어](README.ko.md) ·
[简体中文](README.zh-CN.md) · [Deutsch](README.de.md)

---

## 先跑一次，三十秒

1. 點開上面的 `shadow_ai_scan.py`，按右上角的 **Raw**，另存新檔。存桌面就好。
2. 打開終端機（Windows 是「終端機」或「PowerShell」，Mac 是「終端機」）。
3. 打這一行，把後面換成你 repo 的路徑：

```bash
python3 shadow_ai_scan.py /path/to/your/repo      # macOS / Linux
py shadow_ai_scan.py C:\path\to\your\repo         # Windows（py 不行就打 python）
```

不知道路徑怎麼填？把那個資料夾**直接拖進終端機視窗**，路徑會自己出現。

沒有 Python？往下跳到〈還沒有 Python〉。

---

## 跑出來你會看到什麼

一份清單，每一筆都有檔案、行號、那一行長什麼樣，還有一句「這代表什麼」。
清單分三級。分級不是為了好看——是因為三級要找的人不一樣。

**高風險：金鑰寫在程式碼裡。** 誰打開檔案，誰就拿到金鑰。這個今天就要換掉，不用討論。
交給**資安**。

**中風險：程式碼確定在把資料送到外面的 AI。** 不一定是壞事，但要問三個問題：這家 AI 公司有簽約嗎？
法務看過他們的資料處理條款嗎？送出去的有沒有客戶個資？交給**法務和採購**。

**低風險：裝了套件，或程式碼裡有痕跡但沒在跑。** 不急，但要找人問清楚：誰裝的、拿來做什麼、
還在不在用。交給**工程主管**。

只想先看最急的那一級：

```bash
python3 shadow_ai_scan.py /path/to/your/repo --level high
```

---

## 它是怎麼找的

不是問人——問卷問不出來，工程師會照他自己對「AI」的理解回答，而在他眼裡那叫寫程式。
它看的是機器留下的痕跡，三個地方：

1. **程式碼裡的引用。** 用了 AI 服務，程式碼一定會引用它的套件，比方說 `from openai import OpenAI`。藏不住。
2. **設定檔裡的網址。** 程式碼可以包得很深，但流量總要有個出口，`api.openai.com` 這種網址會留在設定檔裡。
3. **金鑰本身。** 每一家的金鑰都有固定的開頭：OpenAI 是 `sk-proj-`，Anthropic 是 `sk-ant-`，Google 是 `AIza`。
   掃到這種字串，就是有人在用，而且用的方式有問題。

三條加起來，就能回答開頭那個問題。

---

## 它看不到的地方

我直接說：這是關鍵字比對，不是深度分析。跑完它會自己把看不到的四件事印在最後面：

1. **自己包起來的 AI 呼叫。** 程式碼只寫 `from vendor.llm_client import ask`，看不出底下接的是哪一家。
   比方說有人兩年前寫了一個內部模組，他離職了，現在沒人記得它接誰。
2. **執行時才決定的套件名稱。** 名字從環境變數或設定檔來的話，`import` 那一行沒東西可比對。
3. **行尾的註解、多行字串裡的註解。** 工具只看行首，這些會判錯。
4. **裝了不等於在用。** 相依清單只能證明有人裝過。

所以掃出十個，實際上可能不只十個。**這份清單是要查的起點，不是全部。**
你的 repo 裡如果有 `vendor/`、`internal/` 這種目錄，要找人打開來看。

前兩點不是偷懶。要看穿它，得做跨檔案的資料流分析，那就不是一個下午寫得完的工具了。

---

## 還沒有 Python？

只要 Python 本身，不用裝任何套件。

| 你的系統 | 在哪裡打指令 | 先確認有沒有 | 沒有的話 |
|---|---|---|---|
| Windows | 開始鍵按右鍵 →「終端機」或「PowerShell」 | `py --version` | 到 [python.org](https://www.python.org/downloads/) 下載，安裝時**記得勾** Add python.exe to PATH |
| macOS | Command + 空白鍵，搜尋「終端機」 | `python3 --version` | `brew install python`，或一樣到 python.org |
| Linux | 你平常用的終端機 | `python3 --version` | 多半已內建；沒有就 `sudo apt install python3` |

版本 3.9 以上就行，2021 年以後的都可以。

三個最常卡住的地方：

- Windows 打 `python` 跳出 Microsoft Store？改打 `py`；還不行就重裝 Python，這次勾 PATH。
- Mac 打 `python` 說找不到？Mac 只有 `python3`，這是正常的。
- 中文變亂碼？你在用舊的「命令提示字元」。先打 `chcp 65001` 再跑一次，或改用 Windows 終端機。

⚠ 輸出裡會有金鑰的片段。截圖或貼給別人之前，先看一眼。

---

## 再多做一點

**換語言**：介面有繁體中文、English、日本語、한국어、简体中文、Deutsch。不指定就跟你的作業系統走，認不出來就用英文。

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # 用環境變數也行
```

`--level` 六種語言的字都認：`--level 高`、`--level high`、`--level 높은 위험` 一樣。

**接進 CI**：今天掃乾淨，三個月後又會長出來。接進 CI，誰新增了 AI 呼叫，那次提交就過不了——
比三個月盤點一次便宜得多。有任何高風險就回離開碼 1，其餘 0；參數錯或路徑不存在回 2。

```bash
python3 shadow_ai_scan.py . --level high || echo "有金鑰外洩，這次提交擋下來"
```

**改它**：檔案最上面那幾個清單就是全部的設定——要加一家 AI 公司、一個網域、一種副檔名，加上去就好。
刻意放在那裡，就是讓你改的。

---

## 它掃哪些檔（給要確認範圍的人）

**看副檔名或檔名決定開不開；不在下面的檔案完全不會被打開。**

- 程式碼：`.py` `.ipynb` `.js` `.ts` `.tsx` `.go` `.rb` `.java` `.cs` `.vb` `.php` `.rs` `.kt` `.kts` `.swift` `.scala` `.dart` `.c` `.cc` `.cpp` `.h` `.hpp` `.sh` `.ps1`
- 設定檔：`.yaml` `.yml` `.json` `.toml` `.ini` `.txt` `.config` `.xml` `.properties` `.gradle` `.tf` `.tfvars` `.env`／`.env.*`（含 `.env.local`、`.env.production`）、`Dockerfile`
- 相依清單：`requirements.txt` `Pipfile` `pyproject.toml` `package.json` `go.mod` `Gemfile` `*.csproj` `*.vbproj` `*.fsproj` `packages.config` `pom.xml` `build.gradle(.kts)` `composer.json` `Cargo.toml` `Package.swift`

`.md` 刻意不掃：文件裡提到 `api.openai.com` 太平常，掃了只會滿江紅。單檔超過 2 MB 跳過；
`.git`、`node_modules`、`__pycache__`、`.venv`、`venv`、`dist`、`build` 不進去。

三條線索的範圍不一樣：金鑰樣式和 AI 網域**與語言無關**，上面每一種檔都掃（金鑰只認 Anthropic、OpenAI 新舊兩種、Google 四種前綴；網域七個）。
SDK 引用認 `import` / `from` / `require` / `using` / `use` 五個關鍵字、忽略大小寫，所以 Python、JS／TS、Go、Ruby、Java、Kotlin、Swift、Scala、Dart、C#／VB.NET、Rust、PHP 都涵蓋。
引入那一行和相依清單裡，廠商名用子字串比對，Rust 的 `async_openai`、Swift 的 `OpenAIKit`、C# 的 `Anthropic.SDK` 都抓得到；別的地方仍是整詞比對。
相依清單一律列為低風險。

---

## 授權

MIT。拿去改、拿去內部用、包進你們自己的工具，都可以。

---

## 這支工具從哪來

這是某一集影片的隨集工具。那一集在講：公司裡有多少個沒人登記過的 AI 呼叫，以及為什麼發公告禁止沒有用——
就像在巷口貼「禁止停車」，但整條巷子沒有半支監視器。

它刻意只做一個 repo、跑完就結束。如果你要管的是兩百個 repo、要排程、要留下稽核得了的紀錄、
要讓誤報不再一直回來，那是另一個層級的問題。我們做了 **ForgeHelm** 在處理它。

但先把這一個 repo 掃過一遍。回到開頭那個數字——現在還覺得準嗎？
