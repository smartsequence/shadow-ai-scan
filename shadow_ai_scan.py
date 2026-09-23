#!/usr/bin/env python3
"""shadow-ai-scan — scan one repo and list every place it calls an AI service.

掃一個 repo，列出裡面用到 AI 服務的地方。只做這一件事。
不存資料、沒有介面、一次掃一個目錄。設定全寫在下面那一段。

結果分三級，因為三級要找的人不一樣：

  高  金鑰寫在程式碼裡           → 資安
  中  程式碼把資料送到外部 AI    → 法務與採購
  低  裝了套件或留有痕跡         → 工程主管

這支工具靠關鍵字比對。有些用法它看不到，跑完會列在最後面。

Six interface languages: zh-TW, en, ja, ko, zh-CN, de.

    python shadow_ai_scan.py /path/to/repo --lang en
    SHADOW_AI_LANG=ja python shadow_ai_scan.py /path/to/repo

Python 3.9+, standard library only. No install, no network, no telemetry.
"""
from __future__ import annotations

import argparse
import locale
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# 設定：全部寫死在這裡。這是刻意的——加一層設定檔只會讓工具變長。
# Configuration lives here on purpose. A config file would only add moving parts.
# ─────────────────────────────────────────────────────────────

# 直接 import 就代表在用的 SDK
SDK_MODULES = [
    "openai", "anthropic", "cohere", "mistralai", "together",
    "google.generativeai", "vertexai", "langchain", "llama_index", "ollama",
]

# 引入 SDK 的寫法。每種語言不一樣，少一個就少掃一種語言：
#   import / from  Python、JS／TS、Go、Java、Kotlin、Swift
#   require        Ruby、CommonJS
#   using          C#、VB.NET
#   use            Rust、PHP
IMPORT_KEYWORDS = ["import", "from", "require", "using", "use"]

# 廠商名。在「引入」那一行上以**子字串**比對（不要求前後是字界），
# 因為各語言的包裝名長得不一樣：Rust 的 async_openai、Swift 的 OpenAIKit、
# C# 的 Anthropic.SDK——用整詞比對一個都抓不到。
# 只在引入行上這樣放寬，所以誤判成本是「多一筆要人看一眼」，不是滿江紅。
# ⚠ 刻意不放 llm、ai、gpt 這種泛稱，那才會真的滿江紅。
VENDOR_TOKENS = [
    "openai", "anthropic", "claude", "gemini", "mistral", "cohere",
    "ollama", "langchain", "llamaindex", "vertexai", "huggingface",
]

# 出口流量會打的網域。程式碼包得再深，這條線索還是在。
AI_HOSTS = [
    "api.openai.com", "api.anthropic.com", "api.cohere.ai",
    "api.mistral.ai", "generativelanguage.googleapis.com",
    "api.together.xyz", "openai.azure.com",
]

# 金鑰樣式。注意 AI 家的前綴用連字號（sk-），
# Stripe 用底線（sk_test_ / sk_live_）——這一個字元之差就是偽陽性的來源。
KEY_PATTERNS = [
    (re.compile(r"sk-ant-api\d{2}-[A-Za-z0-9_-]{16,}"), "Anthropic API key"),
    (re.compile(r"sk-proj-[A-Za-z0-9_-]{16,}"), "OpenAI project key"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI legacy key"),
    (re.compile(r"AIza[A-Za-z0-9_-]{20,}"), "Google API key"),
]

# 掃哪些副檔名。不在這裡的檔案連開都不會開——所以這張表就是覆蓋範圍本身。
SCAN_SUFFIX = {".py", ".js", ".ts", ".tsx", ".go", ".rb", ".java", ".cs",
               ".php", ".rs", ".kt", ".kts", ".swift",
               ".yaml", ".yml", ".json", ".toml", ".ini", ".env", ".txt", ".example"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
DEP_FILES = {"requirements.txt", "package.json", "pyproject.toml", "go.mod", "Gemfile"}

MAX_BYTES = 2_000_000  # 超過就跳過，避免把產物檔讀進來

# 三個等級的內部代號。顯示文字與派工對象在下面的語言表。
# 掃描產生的是這些代號，不是句子——語言是輸出時才決定的。
LEVELS = ("high", "mid", "low")
RANK = {"high": 0, "mid": 1, "low": 2}

# ─────────────────────────────────────────────────────────────
# 介面語言。六種，鍵完全一致；CJK 在前，拉丁在後。
# Six interface languages, identical key sets in each.
# 選語言的順序：--lang > SHADOW_AI_LANG > 作業系統語系 > en
# ─────────────────────────────────────────────────────────────

STRINGS = {
    "ja": {
        "target": "スキャン対象：",
        "summary": "{files} 個のファイルを読み、{n} 箇所が見つかりました",
        "summary_filtered": "{files} 個のファイルを読み、{n} 箇所が見つかりました。ここでは{level}の {shown} 件のみ表示します",
        "nothing": "見つかりませんでした。AI を使っていない証明にはなりません。このツールに見えないものを下で確認してください。",
        "section": "{name}（{n} 件）",
        "means": "つまり：",
        "route": "→ 担当：{owner}",
        "lv_high": "高リスク", "lv_mid": "中リスク", "lv_low": "低リスク",
        "own_high": "セキュリティ", "own_mid": "法務・調達", "own_low": "エンジニアリング責任者",
        "kind_key": "ハードコードされた{label}",
        "kind_import": "import {mod}",
        "kind_commented": "コメントアウトされた {mod}",
        "kind_dep": "依存パッケージ {mod}",
        "kind_host": "{host} を呼び出し",
        "why_key": "鍵がコードに直接書かれています。リポジトリを見られる人は全員手に入ります。今日中に鍵を差し替え、どのサービスで使われたかを調べてください。",
        "why_import": "このコードは社外の AI サービスへデータを送ります。この AI 企業が調達と法務を通っているか確認してください。",
        "why_host": "自社のトラフィックがこのドメインへ出ます。セキュリティ担当とファイアウォール設定はこれを把握していますか。",
        "why_commented": "今は動いていませんが、誰かが試しています。何を試したのか、社内データが外に出たのかを確認してください。",
        "why_dep": "誰かがこのパッケージを入れました。入れた人、用途、今も使っているかを聞いてください。",
        "filtered_note": "これは絞り込んだ結果で、完全な一覧ではありません。このツールに見えないものは、フィルタなしで実行すると表示されます。",
        "limits_title": "このツールに見えないもの",
        "limit_1": "自前でラップされた AI 呼び出し。コードには from vendor.llm_client import ask としか\n     書かれておらず、どのサービスに繋がるか分かりません。vendor/ や internal/ を人が開いて確認してください。",
        "limit_2": "実行時に決まるパッケージ名。環境変数や設定から来る場合、import 行に照合する文字列がありません。",
        "limit_3": "行末コメントや複数行文字列の中のコメント。行頭しか見ないため誤判定します。",
        "limit_4": "入っている＝使っている、ではありません。依存リストは導入の証拠にしかなりません。",
        "limits_tail": "AI を使っている箇所が {n} 件見つかりました。実際にはもっと多いかもしれません。この一覧は調査の出発点であり、全部ではありません。",
        "desc": "リポジトリをスキャンし、登録されていない AI 呼び出しを洗い出します",
        "help_path": "スキャンするディレクトリ（既定：カレント）",
        "help_level": "この等級だけ表示（high/mid/low、または各言語の表記）",
        "help_color": "色付け。auto（既定）は端末出力のときだけ。パイプに繋ぐときは always",
        "help_lang": "表示言語（既定：auto。SHADOW_AI_LANG でも指定可）",
        "not_a_dir": "ディレクトリが見つかりません：{path}",
        "bad_level": "--level の値が不正です：{value}。使えるのは {choices} です",
    },
    "ko": {
        "target": "스캔 대상: ",
        "summary": "{files}개 파일을 읽어 {n}곳을 찾았습니다",
        "summary_filtered": "{files}개 파일을 읽어 {n}곳을 찾았습니다. 여기서는 {level} {shown}건만 표시합니다",
        "nothing": "찾지 못했습니다. AI를 쓰지 않는다는 뜻은 아닙니다. 이 도구가 보지 못하는 것을 아래에서 확인하세요.",
        "section": "{name}（{n}건）",
        "means": "의미: ",
        "route": "→ 담당: {owner}",
        "lv_high": "높은 위험", "lv_mid": "중간 위험", "lv_low": "낮은 위험",
        "own_high": "보안팀", "own_mid": "법무·구매", "own_low": "엔지니어링 책임자",
        "kind_key": "하드코딩된 {label}",
        "kind_import": "import {mod}",
        "kind_commented": "주석 처리된 {mod}",
        "kind_dep": "의존 패키지 {mod}",
        "kind_host": "{host} 호출",
        "why_key": "키가 코드에 그대로 적혀 있습니다. 저장소를 볼 수 있는 사람은 모두 가져갈 수 있습니다. 오늘 키를 교체하고 어떤 서비스에 쓰였는지 확인하세요.",
        "why_import": "이 코드는 외부 AI 서비스로 데이터를 보냅니다. 이 AI 회사가 구매와 법무를 거쳤는지 확인하세요.",
        "why_host": "회사 트래픽이 이 도메인으로 나갑니다. 보안팀과 방화벽 규칙이 이를 알고 있습니까?",
        "why_commented": "지금은 돌지 않지만 누군가 시도했습니다. 무엇을 시도했는지, 회사 데이터가 나갔는지 물어보세요.",
        "why_dep": "누군가 이 패키지를 설치했습니다. 누가, 무엇에 쓰려고, 지금도 쓰는지 확인하세요.",
        "filtered_note": "이것은 걸러낸 결과이지 전체 목록이 아닙니다. 이 도구가 보지 못하는 것은 필터 없이 실행해야 나옵니다.",
        "limits_title": "이 도구가 보지 못하는 것",
        "limit_1": "직접 감싼 AI 호출. 코드에는 from vendor.llm_client import ask 라고만 적혀 있어\n     어느 서비스에 연결되는지 알 수 없습니다. vendor/, internal/ 디렉터리를 사람이 열어 확인하세요.",
        "limit_2": "실행할 때 정해지는 패키지 이름. 환경 변수나 설정에서 오면 import 줄에 비교할 문자열이 없습니다.",
        "limit_3": "줄 끝 주석이나 여러 줄 문자열 안의 주석. 줄 앞만 보기 때문에 잘못 판단합니다.",
        "limit_4": "설치했다고 쓰는 것은 아닙니다. 의존 목록은 설치 사실만 증명합니다.",
        "limits_tail": "AI를 쓰는 곳 {n}군데를 찾았습니다. 실제로는 더 많을 수 있습니다. 이 목록은 조사의 출발점이지 전부가 아닙니다.",
        "desc": "저장소를 스캔해 등록되지 않은 AI 호출을 찾아냅니다",
        "help_path": "스캔할 디렉터리 (기본: 현재 디렉터리)",
        "help_level": "이 등급만 표시 (high/mid/low 또는 각 언어 표기)",
        "help_color": "색상. auto(기본)는 터미널 출력일 때만. 파이프로 넘길 때는 always",
        "help_lang": "표시 언어 (기본: auto. SHADOW_AI_LANG 으로도 지정 가능)",
        "not_a_dir": "디렉터리를 찾을 수 없습니다: {path}",
        "bad_level": "--level 값이 잘못되었습니다: {value}. 사용할 수 있는 값은 {choices} 입니다",
    },
    "zh-CN": {
        "target": "扫描目标：",
        "summary": "读了 {files} 个文件，找到 {n} 个地方要看",
        "summary_filtered": "读了 {files} 个文件，找到 {n} 个地方要看，这里只列{level}的 {shown} 处",
        "nothing": "没有找到。这不代表公司没在用 AI，往下看工具看不到的地方。",
        "section": "{name}（{n} 处）",
        "means": "这代表：",
        "route": "→ 派给{owner}",
        "lv_high": "高风险", "lv_mid": "中风险", "lv_low": "低风险",
        "own_high": "安全团队", "own_mid": "法务与采购", "own_low": "工程主管",
        "kind_key": "硬编码{label}",
        "kind_import": "import {mod}",
        "kind_commented": "注释掉的 {mod}",
        "kind_dep": "依赖包 {mod}",
        "kind_host": "调用 {host}",
        "why_key": "密钥写在代码里，看得到仓库的人都拿得到。今天就换掉这把密钥，再查它用过哪些服务。",
        "why_import": "这段代码会把数据送到外部 AI 服务。确认这家 AI 公司有没有经过采购和法务。",
        "why_host": "公司的流量会送到这个域名。安全团队和防火墙规则知道这件事吗？",
        "why_commented": "这段没在跑，但有人试过。问一下当时试了什么、公司数据有没有送出去。",
        "why_dep": "有人装了这个包。去问是谁装的、拿来做什么、还在不在用。",
        "filtered_note": "这是筛选过的结果，不是完整清单。这支工具看不到的地方，要跑完整扫描才会列出来。",
        "limits_title": "这支工具看不到的地方",
        "limit_1": "自己包起来的 AI 调用。代码里只写 from vendor.llm_client import ask，\n     看不出底下接的是哪家服务。请人打开 vendor/、internal/ 这类目录看一眼。",
        "limit_2": "运行时才决定的包名。来自环境变量或配置文件的话，import 那一行没东西可比对。",
        "limit_3": "写在行尾或多行字符串里的注释。工具只看行首，这些会判错。",
        "limit_4": "有装不等于有用。依赖清单只能证明装过。",
        "limits_tail": "扫出 {n} 个地方在用 AI，实际上可能不止 {n} 个。这份清单是要查的起点，不是全部。",
        "desc": "扫一个仓库，找出没人登记过的 AI 调用",
        "help_path": "要扫的目录（默认：当前目录）",
        "help_level": "只看这一级（high/mid/low，或各语言的写法）",
        "help_color": "上色。auto（默认）只在输出到终端时上色；接管道时请用 always",
        "help_lang": "界面语言（默认 auto，也可用 SHADOW_AI_LANG 指定）",
        "not_a_dir": "找不到目录：{path}",
        "bad_level": "--level 的值不对：{value}。可用的是 {choices}",
    },
    "zh-TW": {
        "target": "掃描目標：",
        "summary": "讀了 {files} 個檔案，找到 {n} 個地方要看",
        "summary_filtered": "讀了 {files} 個檔案，找到 {n} 個地方要看，這裡只列{level}的 {shown} 處",
        "nothing": "沒有找到。這不代表公司沒在用 AI，往下看工具看不到的地方。",
        "section": "{name}（{n} 處）",
        "means": "這代表：",
        "route": "→ 派給{owner}",
        "lv_high": "高風險", "lv_mid": "中風險", "lv_low": "低風險",
        "own_high": "資安", "own_mid": "法務與採購", "own_low": "工程主管",
        "kind_key": "硬編碼{label}",
        "kind_import": "import {mod}",
        "kind_commented": "註解中的 {mod}",
        "kind_dep": "相依套件 {mod}",
        "kind_host": "呼叫 {host}",
        "why_key": "金鑰寫在程式碼裡，看得到 repo 的人都拿得到。今天就換掉這把金鑰，再查它用過哪些服務。",
        "why_import": "這段程式碼會把資料送到外部 AI 服務。確認這家 AI 公司有沒有經過採購和法務。",
        "why_host": "公司的流量會送到這個網域。資安團隊和防火牆規則知道這件事嗎？",
        "why_commented": "這段沒在跑，但有人試過。問一下當時試了什麼、公司資料有沒有送出去。",
        "why_dep": "有人裝了這個套件。去問是誰裝的、拿來做什麼、還在不在用。",
        "filtered_note": "這是篩選過的結果，不是完整清單。這支工具看不到的地方，要跑完整掃描才會列出來。",
        "limits_title": "這支工具看不到的地方",
        "limit_1": "自己包起來的 AI 呼叫。程式碼裡只寫 from vendor.llm_client import ask，\n     看不出底下接的是哪家服務。請人打開 vendor/、internal/ 這類目錄看一眼。",
        "limit_2": "執行時才決定的套件名稱。來自環境變數或設定檔的話，import 那一行沒東西可比對。",
        "limit_3": "寫在行尾或多行字串裡的註解。工具只看行首，這些會判錯。",
        "limit_4": "有裝不等於有用。相依清單只能證明裝過。",
        "limits_tail": "掃出 {n} 個地方在用 AI，實際上可能不只 {n} 個。這份清單是要查的起點，不是全部。",
        "desc": "掃一個 repo，找出沒人登記過的 AI 呼叫",
        "help_path": "要掃的目錄（預設：目前目錄）",
        "help_level": "只看這一級（high/mid/low，或各語言的寫法）",
        "help_color": "上色。auto（預設）只在輸出到終端機時上色；接管線時請用 always",
        "help_lang": "介面語言（預設 auto，也可用 SHADOW_AI_LANG 指定）",
        "not_a_dir": "找不到目錄：{path}",
        "bad_level": "--level 的值不對：{value}。可用的是 {choices}",
    },
    "en": {
        "target": "Target: ",
        "summary": "Read {files} files, found {n} places to look at",
        "summary_filtered": "Read {files} files, found {n} places to look at; showing only the {shown} at {level}",
        "nothing": "Nothing found. That is not proof nobody here uses AI. Read what this tool cannot see, below.",
        "section": "{name} ({n})",
        "means": "Means: ",
        "route": "-> route to {owner}",
        "lv_high": "High risk", "lv_mid": "Medium risk", "lv_low": "Low risk",
        "own_high": "Security", "own_mid": "Legal and Procurement", "own_low": "Engineering lead",
        "kind_key": "hardcoded {label}",
        "kind_import": "import {mod}",
        "kind_commented": "commented-out {mod}",
        "kind_dep": "dependency {mod}",
        "kind_host": "calls {host}",
        "why_key": "The key is written into the code. Everyone who can read the repo has it. Rotate this key today, then find out which services it was used against.",
        "why_import": "This code sends data to an outside AI service. Check whether that AI company went through procurement and legal.",
        "why_host": "Company traffic leaves for this domain. Do your security team and firewall rules know about it?",
        "why_commented": "This is not running, but somebody tried it. Ask what they tried and whether company data left the building.",
        "why_dep": "Somebody installed this package. Ask who installed it, what for, and whether it is still in use.",
        "filtered_note": "This is a filtered view, not the full list. Run without a filter to see what this tool cannot see.",
        "limits_title": "What this tool cannot see",
        "limit_1": "AI calls wrapped in a module of your own. The code only says from vendor.llm_client import ask,\n     which hides the service underneath. Have someone open vendor/ and internal/ and read them.",
        "limit_2": "Package names resolved at runtime. When the name comes from an environment variable or a config\n     file, the import line has nothing to match against.",
        "limit_3": "Comments at the end of a line, or inside multi-line strings. This tool only looks at the start of a line.",
        "limit_4": "Installed is not the same as used. A dependency list only proves somebody installed it.",
        "limits_tail": "Found {n} places using AI. There may well be more. This list is where the investigation starts, not the whole of it.",
        "desc": "Scan a repo for AI calls nobody registered",
        "help_path": "Directory to scan (default: current directory)",
        "help_level": "Show only this level (high/mid/low, or the word in any supported language)",
        "help_color": "Colour output. auto (default) colours only when writing to a terminal; use always when piping",
        "help_lang": "Interface language (default: auto; SHADOW_AI_LANG also works)",
        "not_a_dir": "Not a directory: {path}",
        "bad_level": "Bad --level value: {value}. Accepted: {choices}",
    },
    "de": {
        "target": "Ziel: ",
        "summary": "{files} Dateien gelesen, {n} Stellen gefunden",
        "summary_filtered": "{files} Dateien gelesen, {n} Stellen gefunden; gezeigt werden nur die {shown} mit {level}",
        "nothing": "Nichts gefunden. Das ist kein Beweis, dass hier niemand KI nutzt. Lesen Sie unten, was dieses Werkzeug nicht sieht.",
        "section": "{name} ({n})",
        "means": "Bedeutet: ",
        "route": "-> zustaendig: {owner}",
        "lv_high": "Hohes Risiko", "lv_mid": "Mittleres Risiko", "lv_low": "Geringes Risiko",
        "own_high": "Security", "own_mid": "Recht und Einkauf", "own_low": "Engineering-Lead",
        "kind_key": "hartcodierter {label}",
        "kind_import": "import {mod}",
        "kind_commented": "auskommentiert: {mod}",
        "kind_dep": "Abhaengigkeit {mod}",
        "kind_host": "ruft {host} auf",
        "why_key": "Der Schluessel steht im Code. Jeder mit Repo-Zugriff hat ihn. Tauschen Sie ihn noch heute aus und pruefen Sie, wofuer er benutzt wurde.",
        "why_import": "Dieser Code sendet Daten an einen externen KI-Dienst. Pruefen Sie, ob dieses KI-Unternehmen durch Einkauf und Rechtsabteilung gegangen ist.",
        "why_host": "Firmen-Traffic geht an diese Domain. Wissen Security-Team und Firewall-Regeln davon?",
        "why_commented": "Laeuft gerade nicht, aber jemand hat es ausprobiert. Fragen Sie, was ausprobiert wurde und ob Firmendaten das Haus verlassen haben.",
        "why_dep": "Jemand hat dieses Paket installiert. Fragen Sie, wer, wofuer und ob es noch benutzt wird.",
        "filtered_note": "Das ist eine gefilterte Ansicht, keine vollstaendige Liste. Ohne Filter ausfuehren, um zu sehen, was dieses Werkzeug nicht sieht.",
        "limits_title": "Was dieses Werkzeug nicht sieht",
        "limit_1": "KI-Aufrufe, die in ein eigenes Modul verpackt sind. Im Code steht nur from vendor.llm_client\n     import ask, der Dienst darunter bleibt verborgen. Lassen Sie jemanden vendor/ und internal/ oeffnen.",
        "limit_2": "Paketnamen, die erst zur Laufzeit feststehen. Kommen sie aus einer Umgebungsvariable oder\n     Konfiguration, gibt es in der import-Zeile nichts zu vergleichen.",
        "limit_3": "Kommentare am Zeilenende oder in mehrzeiligen Strings. Dieses Werkzeug sieht nur den Zeilenanfang.",
        "limit_4": "Installiert heisst nicht benutzt. Eine Abhaengigkeitsliste beweist nur die Installation.",
        "limits_tail": "{n} Stellen gefunden, die KI nutzen. Es koennen mehr sein. Diese Liste ist der Anfang der Untersuchung, nicht ihr Ergebnis.",
        "desc": "Ein Repository nach nicht registrierten KI-Aufrufen durchsuchen",
        "help_path": "Zu durchsuchendes Verzeichnis (Standard: aktuelles)",
        "help_level": "Nur diese Stufe zeigen (high/mid/low oder das Wort in einer der unterstuetzten Sprachen)",
        "help_color": "Farbe. auto (Standard) nur bei Ausgabe ins Terminal; bei Pipes always verwenden",
        "help_lang": "Anzeigesprache (Standard: auto; SHADOW_AI_LANG geht auch)",
        "not_a_dir": "Kein Verzeichnis: {path}",
        "bad_level": "Ungueltiger --level-Wert: {value}. Erlaubt: {choices}",
    },
}

DEFAULT_LANG = "en"

# 作業系統語系 → 介面語言。只比對前綴，zh 要看地區碼所以單獨處理。
_OS_LANG_PREFIX = {"ja": "ja", "ko": "ko", "de": "de", "en": "en"}


def detect_lang(explicit: str | None) -> str:
    """--lang > SHADOW_AI_LANG > 作業系統語系 > en。認不出來就回英文，不猜。"""
    candidates = [explicit, os.environ.get("SHADOW_AI_LANG"),
                  os.environ.get("LC_ALL"), os.environ.get("LC_MESSAGES"),
                  os.environ.get("LANG")]
    # Windows 多半沒有上面那些環境變數，才問作業系統
    try:
        candidates.append(locale.getdefaultlocale()[0])
    except (ValueError, TypeError):
        pass
    for candidate in candidates:
        if candidate:
            resolved = _normalise_lang(candidate)
            if resolved:
                return resolved
    return DEFAULT_LANG


def _normalise_lang(raw: str) -> str | None:
    """把 zh_TW.UTF-8 / zh-Hant / ja_JP 這類寫法收斂成六個代號之一。"""
    tag = raw.replace("_", "-").split(".")[0].strip()
    if not tag:
        return None
    if tag in STRINGS:
        return tag
    low = tag.lower()
    if low.startswith("zh"):
        # 繁體的地區碼與 Hant 都走 zh-TW，其餘（含 zh 本身）走 zh-CN
        if any(m in low for m in ("tw", "hant", "hk", "mo")):
            return "zh-TW"
        return "zh-CN"
    return _OS_LANG_PREFIX.get(low.split("-")[0])


class Text:
    """綁定一種語言的查表器。所有輸出都經過它，沒有第二條路徑。"""

    def __init__(self, lang: str):
        self.lang = lang
        self._s = STRINGS[lang]

    def __call__(self, key: str, **kw) -> str:
        value = self._s[key]
        return value.format(**kw) if kw else value

    def level_name(self, level: str) -> str:
        return self._s["lv_" + level]

    def owner(self, level: str) -> str:
        return self._s["own_" + level]


def level_aliases() -> dict[str, str]:
    """--level 收得下六種語言的寫法，外加 high/mid/low。

    影片裡打的是中文的「高」「中」「低」，各語系的觀眾打自己的字也要能用，
    所以這張表把每一種寫法都對回內部代號。
    """
    table = {lv: lv for lv in LEVELS}
    for strings in STRINGS.values():
        for lv in LEVELS:
            table[strings["lv_" + lv].lower()] = lv
    # 中日韓習慣只打一個字或一個詞；英德用簡寫
    table.update({
        "高": "high", "中": "mid", "低": "low",
        "h": "high", "m": "mid", "l": "low",
        "medium": "mid", "hoch": "high", "mittel": "mid", "gering": "low",
    })
    return table


# ─── 上色 ───
# 觀眾多半不是來讀程式碼的。同一頁裡三種東西的重要性完全不同，用顏色分開：
#   風險等級與檔案位置 → 該等級的顏色，讓人一眼看出嚴重度
#   程式碼片段         → 壓暗，它是證據不是重點
#   「這代表」那一行    → 整行用該等級的顏色加粗，決策者真正要讀的就這行
# 兩條規則：
#   (1) 整行同色。「這代表：」曾經跟後面分兩色，眼睛要解析兩次。
#   (2) 用等級的顏色，不要用白色。白色不帶訊息；紅黃藍本身就在講嚴重度，
#       觀眾不必回頭看標題也知道這行有多急。
_E = chr(27)
_RESET = _E + "[0m"
_DIM = _E + "[2m"
_BOLD = _E + "[1m"
LEVEL_COLOR = {
    "high": _E + "[91m",   # 亮紅
    "mid": _E + "[93m",    # 亮黃
    "low": _E + "[94m",    # 亮藍
}

_use_color = True

# ─── 折行 ───
# 六種語言的句子長度差很多：同一句話中文約 90 欄，英文、德文、日文、韓文會到
# 150 欄以上。不折行的話，終端機會在畫面邊緣硬切，續行掉到第 0 欄，
# 縮排結構就沒了——而「這代表」那一行正是決策者唯一會讀的一行。
# 中日韓沒有空格，所以允許在字元之間斷；拉丁字母只在空白處斷，不切斷單字。

MIN_WIDTH, MAX_WIDTH, PIPE_WIDTH = 60, 120, 100


def _display_width(text: str) -> int:
    """顯示欄寬。中日韓的全形字佔兩欄，不是一欄。"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
               for ch in text)


def term_width() -> int:
    """接到終端機時用實際寬度；接管線或重導向時用固定值。

    用固定值是刻意的：管線情境下 `get_terminal_size` 只會回退到 80，
    那會讓同一份輸出在「直接看」與「接 tail」兩種情況下長得不一樣。
    """
    width = PIPE_WIDTH
    try:
        if sys.stdout.isatty():
            width = shutil.get_terminal_size(fallback=(PIPE_WIDTH, 24)).columns
    except (OSError, ValueError):
        pass
    return max(MIN_WIDTH, min(width, MAX_WIDTH))


def _chunks(text: str):
    """切成折行的最小單位：一個拉丁單字、一個空格，或一個全形字。"""
    buf = ""
    for ch in text:
        if ch == " " or _display_width(ch) == 2:
            if buf:
                yield buf
                buf = ""
            yield ch
        else:
            buf += ch
    if buf:
        yield buf


def clip(text: str, width: int) -> str:
    """把單行截到指定的顯示欄寬。

    用欄寬而不是字元數：一行 88 個中文字是 176 欄，照字元數截還是會滿出去。
    程式碼片段不折行——它是證據，斷成兩行反而難讀，寧可截斷。
    """
    if _display_width(text) <= width:
        return text
    out, used = "", 0
    for ch in text:
        w = _display_width(ch)
        if used + w > width - 1:
            return out + "…"
        out += ch
        used += w
    return out


def wrap(text: str, width: int, first: str = "", cont: str = "") -> list[str]:
    """依顯示欄寬折行，回傳已經加好縮排的整行。

    text 裡原有的換行視為作者刻意的斷點，逐段各自折行——這樣手調過的
    段落（例如限制說明）不會被重新排版，只有超出寬度的才會再斷。
    """
    lines = []
    for para in text.split("\n"):
        prefix, line = first, first
        first = cont  # 第二段起改用續行縮排
        for chunk in _chunks(para):
            if chunk == " " and line == prefix:
                continue  # 續行開頭不留空格
            if line != prefix and _display_width(line + chunk) > width:
                lines.append(line.rstrip())
                prefix, line = cont, cont
                if chunk == " ":
                    continue
            line += chunk
        lines.append(line.rstrip())
    return lines


def c(text: str, *codes: str) -> str:
    """套色。關色時原樣回傳，管線與重導向就不會夾帶控制碼。"""
    if not _use_color or not codes:
        return text
    return "".join(codes) + text + _RESET


class Finding:
    """一筆發現。存的是語言中立的代號與參數，句子要印的時候才組。"""

    __slots__ = ("path", "lineno", "level", "kind_key", "kind_args", "why_key", "excerpt")

    def __init__(self, path, lineno, level, kind_key, kind_args, why_key, excerpt):
        self.path, self.lineno, self.level = path, lineno, level
        self.kind_key, self.kind_args = kind_key, kind_args
        self.why_key, self.excerpt = why_key, excerpt


def _is_commented(line: str) -> bool:
    """這一行是不是註解。只看行首。行尾註解會判錯，限制那段有寫。"""
    return line.lstrip().startswith(("#", "//", "*", "--"))


_IMPORT_RX = re.compile(r"\b(" + "|".join(IMPORT_KEYWORDS) + r")\b", re.IGNORECASE)


def _imported_ai_module(line: str) -> str | None:
    """這一行是不是在引入 AI SDK？是的話回傳引到的名字。

    兩段式：先確認這一行有引入的動作，再看引的東西像不像 AI。
    分兩段是因為「引入」在各語言長得不一樣，「AI」則到處都一樣；
    合成一條正規表示式會變得沒人看得懂，也很難加語言。

    大小寫一律忽略——C# 的 `using OpenAI;` 與 Swift 的 `import OpenAI` 都是
    大寫開頭，用區分大小寫的比對一個都抓不到（2026-09-24 實測）。
    """
    if not _IMPORT_RX.search(line):
        return None
    low = line.lower()
    # 先試完整模組名，報告裡看得出引的是哪一個
    for mod in SDK_MODULES:
        if re.search(rf"\b{re.escape(mod)}\b", low):
            return mod
    # 再退一步用廠商名做子字串比對，接住各語言的包裝名
    for token in VENDOR_TOKENS:
        if token in low:
            return token
    return None


def scan_line(rel: str, lineno: int, line: str, in_deps: bool) -> list[Finding]:
    out = []
    stripped = line.strip()
    commented = _is_commented(line)

    # 1. 金鑰樣式 —— 最高優先，先查
    for pat, label in KEY_PATTERNS:
        if pat.search(line):
            out.append(Finding(rel, lineno, "high", "kind_key", {"label": label},
                               "why_key", stripped))
            return out  # 抓到金鑰就不必再對這行做低階判斷

    # 2. 相依清單裡的 AI 套件
    if in_deps:
        for mod in SDK_MODULES:
            root = mod.split(".")[0]
            if re.search(rf"(^|[\"'\s]){re.escape(root)}\b", stripped):
                out.append(Finding(rel, lineno, "low", "kind_dep", {"mod": root},
                                   "why_dep", stripped))
                break
        return out

    # 3. 引入 AI SDK。先找這一行有沒有引入的動作，再看引的是不是 AI。
    mod = _imported_ai_module(stripped)
    if mod:
        if commented:
            out.append(Finding(rel, lineno, "low", "kind_commented", {"mod": mod},
                               "why_commented", stripped))
        else:
            out.append(Finding(rel, lineno, "mid", "kind_import", {"mod": mod},
                               "why_import", stripped))

    # 4. 設定檔裡的 AI 網域
    for host in AI_HOSTS:
        if host in line:
            out.append(Finding(rel, lineno, "low" if commented else "mid",
                               "kind_host", {"host": host}, "why_host", stripped))
            break

    return out


def scan_repo(root: Path) -> tuple[list[Finding], int]:
    findings, scanned = [], 0
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix not in SCAN_SUFFIX and p.name not in DEP_FILES:
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
            # utf-8-sig：真實 repo 會有帶 BOM 的檔，不吃掉 BOM 的話第一行永遠匹配不到
            text = p.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        scanned += 1
        rel = p.relative_to(root).as_posix()
        in_deps = p.name in DEP_FILES
        for i, line in enumerate(text.splitlines(), 1):
            findings.extend(scan_line(rel, i, line, in_deps))
    findings.sort(key=lambda f: (RANK[f.level], f.path, f.lineno))
    return findings, scanned


def print_limits(t: Text, total: int, width: int) -> None:
    """工具自己承認看不到的四件事。這一段不是免責聲明，是清單的使用說明。"""
    print(c(t("limits_title"), _BOLD))
    print()
    for i in range(1, 5):
        for line in wrap(t(f"limit_{i}"), width, first=f"  {i}. ", cont="     "):
            print(line)
    print()
    for line in wrap(t("limits_tail", n=total), width, first="  ", cont="  "):
        print(c(line, _BOLD))


def _force_utf8_output() -> None:
    """把 stdout/stderr 轉成 UTF-8。

    這不是潔癖：Windows 主控台預設用地區碼頁（繁中是 cp950），
    印日文、韓文或簡體就會丟 UnicodeEncodeError 直接崩潰——
    而這支工具的重點正是六種語言都要能跑。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass  # 已被重導向成不可重設的物件時就維持原樣


def main() -> int:
    _force_utf8_output()
    # 語言要在建 parser 之前決定，說明文字才會跟著換。
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--lang")
    lang = detect_lang(pre.parse_known_args()[0].lang)
    t = Text(lang)

    ap = argparse.ArgumentParser(prog="shadow-ai-scan", description=t("desc"))
    ap.add_argument("path", nargs="?", default=".", help=t("help_path"))
    ap.add_argument("--level", help=t("help_level"))
    ap.add_argument("--color", choices=["auto", "always", "never"], default="auto",
                    help=t("help_color"))
    ap.add_argument("--lang", choices=sorted(STRINGS), help=t("help_lang"))
    args = ap.parse_args()

    level = None
    if args.level:
        level = level_aliases().get(args.level.strip().lower())
        if level is None:
            print(t("bad_level", value=args.level, choices="/".join(LEVELS)), file=sys.stderr)
            return 2

    global _use_color
    _use_color = (args.color == "always"
                  or (args.color == "auto" and sys.stdout.isatty()
                      and not os.environ.get("NO_COLOR")))

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(t("not_a_dir", path=root), file=sys.stderr)
        return 2

    findings, scanned = scan_repo(root)
    shown = [f for f in findings if level is None or f.level == level]
    width = term_width()

    print(c("shadow-ai-scan", _BOLD) + f"  {t('target')}{root.name}")
    if level:
        summary = t("summary_filtered", files=scanned, n=len(findings),
                    level=t.level_name(level), shown=len(shown))
    else:
        summary = t("summary", files=scanned, n=len(findings))
    print("\n".join(wrap(summary, width)) + "\n")

    if not shown:
        print("\n".join(wrap(t("nothing"), width)) + "\n")

    current = None
    for f in shown:
        if f.level != current:
            current = f.level
            count = sum(1 for x in shown if x.level == f.level)
            col = LEVEL_COLOR[f.level]
            head = t("section", name=t.level_name(f.level), n=count)
            print(c("── " + head + " " + "─" * 30, col, _BOLD))
        col = LEVEL_COLOR[f.level]
        kind = t(f.kind_key, **f.kind_args)
        route = t("route", owner=t.owner(f.level))
        print("  " + c(f"{f.path}:{f.lineno}", col) + "  " + kind + "  " + c(route, col))
        print("      " + c(clip(f.excerpt, min(88, width - 6)), _DIM))
        for line in wrap(t("means") + t(f.why_key), width, first="      ", cont="      "):
            print(c(line, col, _BOLD))
    print()
    if level:
        # 篩選過的不是完整盤點。限制說明留給完整掃描，但要留一行指路，
        # 不能讓只跑篩選的人以為這就是全部。
        for line in wrap(t("filtered_note"), width):
            print(c(line, _DIM))
    else:
        print_limits(t, len(findings), width)
    # 有「高」就回非零，方便串進 CI
    return 1 if any(f.level == "high" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
