# shadow-ai-scan

你们公司有几个地方在调用 AI？心里有个数字了吗——先记着。

这支工具会把一个仓库从头扫到尾，把每一行在用 AI 的地方列出来，告诉你它有多急、该交给谁。
多数人第一次跑完的反应是：数字不对。

只有一个 Python 文件，不用安装、不连网络、不会把任何东西传出去。界面有六种语言。

其他语言：[繁體中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) ·
[한국어](README.ko.md) · [Deutsch](README.de.md)

---

## 先跑一次，三十秒

1. 点开上面的 `shadow_ai_scan.py`，按右上角的 **Raw**，另存为。存桌面就好。
2. 打开终端（Windows 是「终端」或「PowerShell」，Mac 是「终端」）。
3. 打这一行，把后面换成你仓库的路径：

```bash
python3 shadow_ai_scan.py /path/to/your/repo      # macOS / Linux
py shadow_ai_scan.py C:\path\to\your\repo         # Windows（py 不行就打 python）
```

不知道路径怎么填？把那个文件夹**直接拖进终端窗口**，路径会自己出现。

没有 Python？往下跳到〈还没有 Python〉。

---

## 跑出来你会看到什么

一份清单，每一条都有文件、行号、那一行长什么样，还有一句「这代表什么」。
清单分三级。分级不是为了好看——是因为三级要找的人不一样。

**高风险：密钥写在代码里。** 谁打开文件，谁就拿到密钥。这个今天就要换掉，不用讨论。
交给**安全团队**。

**中风险：代码确定在把数据送到外面的 AI。** 不一定是坏事，但要问三个问题：这家 AI 公司有签约吗？
法务看过他们的数据处理条款吗？送出去的有没有客户个人信息？交给**法务和采购**。

**低风险：装了包，或代码里有痕迹但没在跑。** 不急，但要找人问清楚：谁装的、拿来做什么、
还在不在用。交给**工程主管**。

只想先看最急的那一级：

```bash
python3 shadow_ai_scan.py /path/to/your/repo --level high
```

---

## 它是怎么找的

不是问人——问卷问不出来，工程师会照他自己对「AI」的理解回答，而在他眼里那叫写代码。
它看的是机器留下的痕迹，三个地方：

1. **代码里的引用。** 用了 AI 服务，代码一定会引用它的包，比方说 `from openai import OpenAI`。藏不住。
2. **配置文件里的地址。** 代码可以包得很深，但流量总要有个出口，`api.openai.com` 这种地址会留在配置文件里。
3. **密钥本身。** 每一家的密钥都有固定的开头：OpenAI 是 `sk-proj-`，Anthropic 是 `sk-ant-`，Google 是 `AIza`。
   扫到这种字符串，就是有人在用，而且用的方式有问题。

三条加起来，就能回答开头那个问题。

---

## 它看不到的地方

我直接说：这是关键字比对，不是深度分析。跑完它会自己把看不到的四件事打印在最后面：

1. **自己包起来的 AI 调用。** 代码只写 `from vendor.llm_client import ask`，看不出底下接的是哪一家。
   比方说有人两年前写了一个内部模块，他离职了，现在没人记得它接谁。
2. **运行时才决定的包名。** 名字从环境变量或配置文件来的话，`import` 那一行没东西可比对。
3. **行尾的注释、多行字符串里的注释。** 工具只看行首，这些会判错。
4. **装了不等于在用。** 依赖清单只能证明有人装过。

所以扫出十个，实际上可能不止十个。**这份清单是要查的起点，不是全部。**
你的仓库里如果有 `vendor/`、`internal/` 这种目录，要找人打开来看。

前两点不是偷懒。要看穿它，得做跨文件的数据流分析，那就不是一个下午写得完的工具了。

---

## 还没有 Python？

只要 Python 本身，不用装任何包。

| 你的系统 | 在哪里打命令 | 先确认有没有 | 没有的话 |
|---|---|---|---|
| Windows | 开始键右键 →「终端」或「PowerShell」 | `py --version` | 到 [python.org](https://www.python.org/downloads/) 下载，安装时**记得勾** Add python.exe to PATH |
| macOS | Command + 空格，搜索「终端」 | `python3 --version` | `brew install python`，或一样到 python.org |
| Linux | 你平常用的终端 | `python3 --version` | 多半已内置；没有就 `sudo apt install python3` |

版本 3.9 以上就行，2021 年以后的都可以。

三个最常卡住的地方：

- Windows 打 `python` 跳出 Microsoft Store？改打 `py`；还不行就重装 Python，这次勾 PATH。
- Mac 打 `python` 说找不到？Mac 只有 `python3`，这是正常的。
- 字变乱码？多半是旧的「命令提示符」。最省事的是改用 **Windows 终端**（Windows 11 内置，开始键右键就有）；
  不能换的话先打 `chcp 65001` 再跑一次。如果看到的是方框而不是乱码，那是旧窗口的字体没有那些字——不用去调字体，Windows 终端会自动找系统里有的字体，换过去就没有这个问题。
  Mac 的终端也会自动找。Linux 看到方框就装一次字体：`sudo apt install fonts-noto-cjk`。

⚠ 输出里会有密钥的片段。截图或贴给别人之前，先看一眼。

---

## 再多做一点

**换语言**：界面有繁體中文、English、日本語、한국어、简体中文、Deutsch。不指定就跟你的操作系统走，认不出来就用英文。

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # 用环境变量也行
```

`--level` 六种语言的字都认：`--level 高`、`--level high`、`--level 높은 위험` 一样。

**接进 CI**：今天扫干净，三个月后又会长出来。接进 CI，谁新增了 AI 调用，那次提交就过不了——
比三个月盘点一次便宜得多。有任何高风险就返回退出码 1，其余 0；参数错或路径不存在返回 2。

```bash
python3 shadow_ai_scan.py . --level high || echo "有密钥泄露，这次提交拦下来"
```

**改它**：文件最上面那几个清单就是全部的配置——要加一家 AI 公司、一个域名、一种扩展名，加上去就好。
刻意放在那里，就是让你改的。

---

## 它扫哪些文件（给要确认范围的人）

**看扩展名或文件名决定开不开；不在下面的文件完全不会被打开。**

- 代码：`.py` `.ipynb` `.js` `.ts` `.tsx` `.go` `.rb` `.java` `.cs` `.vb` `.php` `.rs` `.kt` `.kts` `.swift` `.scala` `.dart` `.c` `.cc` `.cpp` `.h` `.hpp` `.sh` `.ps1`
- 配置文件：`.yaml` `.yml` `.json` `.toml` `.ini` `.txt` `.config` `.xml` `.properties` `.gradle` `.tf` `.tfvars` `.env`／`.env.*`（含 `.env.local`、`.env.production`）、`Dockerfile`
- 依赖清单：`requirements.txt` `Pipfile` `pyproject.toml` `package.json` `go.mod` `Gemfile` `*.csproj` `*.vbproj` `*.fsproj` `packages.config` `pom.xml` `build.gradle(.kts)` `composer.json` `Cargo.toml` `Package.swift`

`.md` 刻意不扫：文档里提到 `api.openai.com` 太平常，扫了只会满江红。单个文件超过 2 MB 跳过；
`.git`、`node_modules`、`__pycache__`、`.venv`、`venv`、`dist`、`build` 不进去。

三条线索的范围不一样：密钥样式和 AI 域名**与语言无关**，上面每一种文件都扫（密钥只认 Anthropic、OpenAI 新旧两种、Google 四种前缀；域名七个）。
SDK 引用认 `import` / `from` / `require` / `using` / `use` 五个关键字、忽略大小写，所以 Python、JS／TS、Go、Ruby、Java、Kotlin、Swift、Scala、Dart、C#／VB.NET、Rust、PHP 都涵盖。
引用那一行和依赖清单里，厂商名用子字符串比对，Rust 的 `async_openai`、Swift 的 `OpenAIKit`、C# 的 `Anthropic.SDK` 都抓得到；别的地方仍是整词比对。
依赖清单一律列为低风险。

---

## 许可

MIT。拿去改、拿去内部用、包进你们自己的工具，都可以。

---

## 这支工具从哪来

这是某一集视频的随集工具。那一集在讲：公司里有多少个没人登记过的 AI 调用，以及为什么发公告禁止没有用——
就像在巷口贴「禁止停车」，但整条巷子没有半个监控。

它刻意只做一个仓库、跑完就结束。如果你要管的是两百个仓库、要定时、要留下经得起审计的记录、
要让误报不再一直回来，那是另一个层级的问题。我们做了 **ForgeHelm** 在处理它。

但先把这一个仓库扫过一遍。回到开头那个数字——现在还觉得准吗？
