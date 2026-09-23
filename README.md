# shadow-ai-scan

掃一個 repo，列出裡面哪幾行在呼叫 AI 服務，並把每一筆標上風險等級與該找誰處理。

只有一個 Python 檔，只用標準函式庫。不用安裝、不連網路、不回傳任何東西。

**六種介面語言**：繁體中文、English、日本語、한국어、简体中文、Deutsch。

其他語言的說明：[English](README.en.md) ·
[日本語](README.ja.md) · [한국어](README.ko.md) ·
[简体中文](README.zh-CN.md) · [Deutsch](README.de.md)

---

## 三十秒開始（已經有 Python 的話）

下載這一個檔：點開 `shadow_ai_scan.py` → 右上角 **Raw** → 另存新檔。存哪裡都可以，桌面就行。
或者整個 `git clone` 也一樣。

然後打開終端機，執行：

```bash
# macOS / Linux
python3 shadow_ai_scan.py /path/to/your/repo

# Windows（`py` 用不了就改打 `python`）
py shadow_ai_scan.py C:\path\to\your\repo
```

**不知道 repo 的路徑？** 把那個資料夾直接拖進終端機視窗，路徑會自己貼上。

只看最急的那一級：

```bash
python3 shadow_ai_scan.py /path/to/your/repo --level high
```

以下的例子一律寫 `python3`，Windows 請自行換成 `py`。

## 還沒有 Python？

不用裝任何套件，也不會連網路，只要有 Python 本身就夠了。

| 系統 | 在哪裡打指令 | 先確認有沒有 | 沒有的話 |
|---|---|---|---|
| Windows | 開始鍵按右鍵 →「終端機」或「PowerShell」 | `py --version` | 到 [python.org](https://www.python.org/downloads/) 下載，安裝時**記得勾** Add python.exe to PATH |
| macOS | Command + 空白鍵，搜尋「終端機」 | `python3 --version` | `brew install python`，或一樣到 python.org |
| Linux | 你平常用的終端機 | `python3 --version` | 多半已內建；沒有就 `sudo apt install python3` 之類 |

版本要 3.9 以上（2021 年以後的都可以）。

**三個最常卡住的地方**

- Windows 打 `python` 跳出 Microsoft Store：改打 `py`；還是不行就重裝 Python 並勾 PATH。
- macOS 打 `python` 說找不到：macOS 只有 `python3`，這是正常的。
- 中文變成亂碼（舊的「命令提示字元」）：先打 `chcp 65001` 再跑一次，或改用 Windows 終端機。

⚠ 輸出裡會有金鑰的片段。截圖或貼給別人之前先看一眼。

---

## 它在找什麼

三條線索。機器不會說謊，但凡走過必留下痕跡。

1. **程式碼**——`from openai import OpenAI`、`import anthropic` 這類官方 SDK 的引用。
2. **設定檔**——`api.openai.com` 這類 API 網域。程式碼可以包得很深，流量總要有個出口。
3. **金鑰**——每一家的金鑰都有固定的開頭，`sk-ant-api03-`、`sk-proj-`、`AIza`。

---

## 分三級，因為三級要找的人不一樣

不管幾筆，每一筆看起來都一樣重要，就等於沒有一筆重要。所以每一筆都標了等級與派工對象。

| 等級 | 什麼情況 | 派給誰 | 多急 |
|---|---|---|---|
| 高 | 金鑰寫在程式碼或設定檔裡 | 資安 | 今天就換掉，不用討論 |
| 中 | 程式碼確定會把資料送到外部 AI | 法務與採購 | 有簽約嗎？送了什麼？ |
| 低 | 裝了套件，或有痕跡但沒在跑 | 工程主管 | 不急，但要找人問清楚 |

輸出每一筆都有檔案、行號、原始那一行，以及一句「這代表什麼」。直接可以派工。

---

## 它看不到的地方

這支工具靠關鍵字比對，不是深度靜態分析。跑完它會自己把這四件事印出來：

1. **自己包起來的 AI 呼叫。** 程式碼裡只寫 `from vendor.llm_client import ask`，看不出底下接的是哪一家。
2. **執行時才決定的套件名稱。** 名字來自環境變數或設定檔的話，`import` 那一行沒東西可比對。
3. **行尾註解與多行字串裡的註解。** 工具只看行首，這些會判錯。
4. **有裝不等於有用。** 相依清單只能證明有人裝過。

掃出 N 個，實際上可能不只 N 個。**這份清單是要查的起點，不是全部。**

第 1 點和第 2 點不是偷懶，是這個做法的邊界：要看穿它得做跨檔案的資料流分析，那就不是一個下午寫得完的工具了。

---

## 接進 CI

有任何「高」風險就回傳離開碼 1，其餘回 0；參數錯誤或路徑不存在回 2。

```bash
python3 shadow_ai_scan.py . --level high || echo "有金鑰外洩，這次提交擋下來"
```

今天掃乾淨，三個月後又會長出來。接進 CI 比三個月盤點一次便宜得多。

---

## 換語言

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # 也可以用環境變數
```

不指定就照作業系統的語系走，認不出來就用英文。

`--level` 收得下六種語言的寫法，`--level 高`、`--level high`、`--level 높은 위험` 都可以。

---

## 授權

MIT。拿去改、拿去內部用、拿去包進你們自己的工具，都可以。

---

## 這支工具從哪來

這是某一集影片的隨集工具，影片在講：公司裡有多少個沒人登記過的 AI 呼叫，以及為什麼發公告禁止沒有用。

它刻意只做一個 repo、跑完就結束。如果你要管的是兩百個 repo、要排程、要留下稽核得了的紀錄、要讓誤報不再一直回來，那是另一個層級的問題，我們做了 **ForgeHelm** 在處理它。

但先把這一個 repo 掃過一遍——多數人會發現的第一件事是：數字不對。
