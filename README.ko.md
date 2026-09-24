# shadow-ai-scan

회사 안에서 AI 를 호출하는 곳이 몇 군데입니까? 숫자가 떠올랐나요——기억해 두세요.

이 도구는 저장소 하나를 처음부터 끝까지 읽고, AI 를 쓰는 줄을 전부 나열한 뒤, 각각이 얼마나 급하고
누구에게 넘겨야 하는지 알려 줍니다. 처음 돌려 본 사람의 가장 흔한 반응은 "숫자가 안 맞는다"입니다.

Python 파일 하나뿐입니다. 설치할 것 없고, 네트워크도 안 쓰고, 아무것도 밖으로 보내지 않습니다. 인터페이스는 6개 언어.

다른 언어: [繁體中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) ·
[简体中文](README.zh-CN.md) · [Deutsch](README.de.md)

---

## 일단 한 번, 30초

1. 위의 `shadow_ai_scan.py` 를 열고 오른쪽 위 **Raw** 를 눌러 저장하세요. 바탕화면이면 됩니다.
2. 터미널을 엽니다 (Windows 는 "터미널" 또는 "PowerShell", Mac 은 "터미널").
3. 이 한 줄을 치세요. 끝은 내 저장소 경로로:

```bash
python3 shadow_ai_scan.py /path/to/your/repo      # macOS / Linux
py shadow_ai_scan.py C:\path\to\your\repo         # Windows (py 가 안 되면 python)
```

경로를 모르겠다면? 그 폴더를 **터미널 창에 끌어다 놓으면** 저절로 입력됩니다.

Python 이 없다면? 아래 〈Python 이 아직 없다면〉으로.

---

## 무엇이 나오는가

목록입니다. 각 건에 파일, 줄 번호, 그 줄의 내용, 그리고 "이것이 무슨 뜻인지" 한 문장.
목록은 세 등급으로 나뉩니다. 보기 좋으라고가 아니라, 움직여야 할 사람이 셋이기 때문입니다.

**높음: 키가 코드에 적혀 있음.** 파일을 여는 사람마다 키를 손에 넣습니다. 오늘 교체, 논의할 것 없음.
**보안팀**에게.

**중간: 코드가 외부 AI 로 데이터를 확실히 보냄.** 꼭 나쁜 건 아니지만 세 가지를 물어야 합니다.
그 AI 회사와 계약이 있는가, 법무가 데이터 처리 조항을 읽었는가, 보내는 것에 고객 개인정보가 있는가.
**법무와 구매**에게.

**낮음: 패키지가 깔려 있거나, 코드에 흔적은 있는데 돌지 않음.** 급하진 않지만 누군가에게 물어야 합니다.
누가 깔았는지, 무엇에 쓰려고, 아직 쓰는지. **엔지니어링 책임자**에게.

급한 등급만 먼저 보려면:

```bash
python3 shadow_ai_scan.py /path/to/your/repo --level high
```

---

## 어떻게 찾는가

사람에게 묻지 않습니다. 설문으로는 안 나옵니다——엔지니어는 자기 기준의 "AI"로 답하고,
그의 눈에 그건 그냥 코딩이니까요. 보는 건 기계가 남긴 흔적, 세 곳:

1. **코드의 참조.** AI 서비스를 쓰면 코드는 반드시 그 패키지를 참조합니다. 예를 들어 `from openai import OpenAI`. 숨길 수 없습니다.
2. **설정 파일의 주소.** 코드는 얼마든지 깊이 감쌀 수 있지만 트래픽에는 출구가 필요하고, `api.openai.com` 같은 주소는 설정 파일에 남습니다.
3. **키 자체.** 회사마다 키 접두사가 정해져 있습니다. OpenAI 는 `sk-proj-`, Anthropic 은 `sk-ant-`, Google 은 `AIza`.
   이런 문자열이 있으면 누군가 쓰고 있고, 쓰는 방식에도 문제가 있다는 뜻입니다.

셋을 합치면 맨 위의 질문에 답할 수 있습니다.

---

## 이 도구가 보지 못하는 것

바로 말하겠습니다. 이건 키워드 대조지 깊은 분석이 아닙니다. 전체 실행이 끝날 때마다 못 보는 네 가지를 스스로 맨 아래에 출력합니다.

1. **직접 감싼 AI 호출.** 코드에는 `from vendor.llm_client import ask` 라고만 있고, 아래가 어느 서비스인지 보이지 않습니다.
   예를 들어 누군가 2년 전에 내부 모듈을 만들고 퇴사해서, 지금은 그게 어디로 연결되는지 아무도 모르는 경우.
2. **실행할 때 정해지는 패키지 이름.** 환경 변수나 설정에서 오면 import 줄에 대조할 것이 없습니다.
3. **줄 끝 주석, 여러 줄 문자열 속 주석.** 줄 앞만 보기 때문에 틀립니다.
4. **깔렸다고 쓰는 것은 아님.** 의존 목록은 설치 사실만 증명합니다.

그래서 열 개를 찾았어도 실제로는 더 있을 수 있습니다. **이 목록은 조사의 출발점이지 전부가 아닙니다.**
저장소에 `vendor/`, `internal/` 같은 디렉터리가 있다면 거기는 사람이 열어 봐야 하는 곳입니다.

앞의 둘은 게으름이 아닙니다. 꿰뚫어 보려면 파일을 넘나드는 데이터 흐름 분석이 필요하고, 그건 하루 오후에 쓸 수 있는 도구가 아닙니다.

---

## Python 이 아직 없다면

Python 본체만 있으면 됩니다. 패키지는 필요 없습니다.

| 운영체제 | 어디에 입력하나 | 먼저 확인 | 없으면 |
|---|---|---|---|
| Windows | 시작 버튼 우클릭 → "터미널" 또는 "PowerShell" | `py --version` | [python.org](https://www.python.org/downloads/) 에서 받고, 설치 때 Add python.exe to PATH 를 **체크** |
| macOS | Command + 스페이스로 "터미널" 검색 | `python3 --version` | `brew install python` 또는 python.org |
| Linux | 평소 쓰는 터미널 | `python3 --version` | 보통 이미 있음. 없으면 `sudo apt install python3` |

3.9 이상이면 됩니다. 2021년 이후 버전이면 다 됩니다.

가장 많이 막히는 세 곳:

- Windows 에서 `python` 을 치면 Microsoft Store 가 열린다? `py` 로 치세요. 그래도 안 되면 Python 을 다시 설치하고 이번엔 PATH 를 체크.
- Mac 에서 `python` 을 못 찾는다고 한다? Mac 에는 `python3` 만 있습니다. 정상입니다.
- 글자가 깨진다? 대개 옛 명령 프롬프트입니다. 가장 쉬운 건 **Windows 터미널**(Windows 11 기본, 시작 버튼 우클릭)로 바꾸는 것;
  못 바꾸면 먼저 `chcp 65001` 을 치세요. 깨진 글자가 아니라 네모 상자가 보이면 옛 창의 글꼴에 그 글자가 없는 것뿐입니다. 글꼴 메뉴를 뒤질 필요 없습니다. Windows 터미널은
  시스템에 있는 글꼴을 자동으로 찾아 쓰니, 그쪽으로 바꾸면 끝입니다. macOS 터미널도 마찬가지. Linux 에서 상자가 보이면 글꼴을 한 번 설치하세요: `sudo apt install fonts-noto-cjk`.

⚠ 출력에는 키의 일부가 포함됩니다. 캡처하거나 어디에 붙여넣기 전에 한 번 보세요.

---

## 조금 더

**언어 바꾸기**: 繁體中文, English, 日本語, 한국어, 简体中文, Deutsch. 지정하지 않으면 OS 를 따르고, 판별하지 못하면 영어.

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # 환경 변수도 됩니다
```

`--level` 은 여섯 언어 표기를 다 받습니다: `--level high`, `--level 高`, `--level 높은 위험` 모두 같습니다.

**CI 에 연결**: 오늘 깨끗해도 석 달 뒤면 다시 자랍니다. CI 에 넣으면 AI 호출을 추가한 사람의 커밋이 그 자리에서 막힙니다——
분기마다 전수 점검하는 것보다 훨씬 쌉니다. '높음'이 있으면 종료 코드 1, 없으면 0. 인자 오류나 경로 없음은 2.

```bash
python3 shadow_ai_scan.py . --level high || echo "키 유출 발견. 이 커밋은 막습니다"
```

**고치기**: 파일 맨 위의 목록들이 설정의 전부입니다. AI 회사 하나, 도메인 하나, 확장자 하나 더하고 싶으면 적어 넣으면 됩니다.
고치라고 거기 둔 것입니다.

---

## 어떤 파일을 여는가 (범위를 확인하려는 분께)

**확장자나 파일 이름으로 정해집니다. 아래에 없는 파일은 열리지도 않습니다.**

- 코드: `.py` `.ipynb` `.js` `.ts` `.tsx` `.go` `.rb` `.java` `.cs` `.vb` `.php` `.rs` `.kt` `.kts` `.swift` `.scala` `.dart` `.c` `.cc` `.cpp` `.h` `.hpp` `.sh` `.ps1`
- 설정 파일: `.yaml` `.yml` `.json` `.toml` `.ini` `.txt` `.config` `.xml` `.properties` `.gradle` `.tf` `.tfvars` `.env`／`.env.*`(`.env.local`, `.env.production` 포함), `Dockerfile`
- 의존 목록: `requirements.txt` `Pipfile` `pyproject.toml` `package.json` `go.mod` `Gemfile` `*.csproj` `*.vbproj` `*.fsproj` `packages.config` `pom.xml` `build.gradle(.kts)` `composer.json` `Cargo.toml` `Package.swift`

`.md` 는 일부러 뺐습니다. 문서에 `api.openai.com` 이 나오는 건 흔한 일이라 잡음만 쌓입니다. 2 MB 넘는 파일은 건너뜁니다.
`.git`, `node_modules`, `__pycache__`, `.venv`, `venv`, `dist`, `build` 에는 들어가지 않습니다.

세 단서의 범위는 다릅니다. 키 패턴과 AI 도메인은 **언어와 무관**하게 위의 모든 파일에 적용됩니다
(키는 Anthropic, OpenAI 신·구, Google 네 접두사뿐. 도메인은 일곱 개).
SDK 참조는 `import` / `from` / `require` / `using` / `use` 다섯 키워드를 대소문자 무시로 보므로 Python, JS/TS, Go, Ruby, Java, Kotlin, Swift, Scala, Dart, C#/VB.NET, Rust, PHP 를 다룹니다.
참조 줄과 의존 목록에서는 벤더 이름을 부분 문자열로 맞춰 Rust 의 `async_openai`, Swift 의 `OpenAIKit`, C# 의 `Anthropic.SDK` 도 잡힙니다. 나머지는 단어 단위.
의존 목록은 항상 낮은 위험으로 보고합니다.

---

## 라이선스

MIT. 수정하든, 사내에서 쓰든, 자체 도구에 넣든 모두 자유입니다.

---

## 이 도구의 출처

어느 한 편의 영상에 딸린 도구입니다. 그 편의 주제는 회사 안에 등록되지 않은 AI 호출이 실제로 몇 건이나 있는지,
그리고 왜 금지 공지로는 막히지 않는지——카메라 한 대 없는 골목에 "주차 금지" 표지판을 붙이는 것과 같으니까요.

이 도구는 의도적으로 저장소 하나만 보고 끝납니다. 대상이 이백 개이고, 정기 실행이 필요하고, 감사에 견디는 기록이 필요하고,
오탐이 다시 돌아오지 않아야 한다면 그건 다른 층위의 문제입니다. 그래서 우리는 **ForgeHelm** 을 만들었습니다.

하지만 먼저 이 저장소 하나를 훑어 보세요. 처음의 그 숫자로 돌아가서——아직도 맞다고 생각하십니까?
