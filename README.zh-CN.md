# shadow-ai-scan

扫一个仓库，列出里面哪几行在调用 AI 服务，并给每一条标上风险等级和该找谁处理。

只有一个 Python 文件，只用标准库。不用安装、不连网络、不回传任何东西。

**六种界面语言**：简体中文、繁體中文、English、日本語、한국어、Deutsch。

其他语言：[繁體中文](README.md) · [English](README.en.md) ·
[日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md)

---

## 三十秒开始（已经有 Python 的话）

下载这一个文件：点开 `shadow_ai_scan.py` → 右上角 **Raw** → 另存为。存哪里都可以，桌面就行。整个 `git clone` 也一样。

然后打开终端，执行：

```bash
# macOS / Linux
python3 shadow_ai_scan.py /path/to/your/repo

# Windows（`py` 用不了就改打 `python`）
py shadow_ai_scan.py C:\path\to\your\repo
```

**不知道仓库的路径？** 把那个文件夹直接拖进终端窗口，路径会自己贴上。

只看最急的那一级：

```bash
python3 shadow_ai_scan.py /path/to/your/repo --level high
```

下面的例子一律写 `python3`，Windows 请自行换成 `py`。

## 还没有 Python？

不用装任何包，也不会连网络，只要有 Python 本身就够了。

| 系统 | 在哪里打命令 | 先确认有没有 | 没有的话 |
|---|---|---|---|
| Windows | 开始键右键 →「终端」或「PowerShell」 | `py --version` | 到 [python.org](https://www.python.org/downloads/) 下载，安装时**记得勾** Add python.exe to PATH |
| macOS | Command + 空格，搜索「终端」 | `python3 --version` | `brew install python`，或一样到 python.org |
| Linux | 你平常用的终端 | `python3 --version` | 多半已内置；没有就 `sudo apt install python3` 之类 |

版本要 3.9 以上（2021 年以后的都可以）。

**三个最常卡住的地方**

- Windows 打 `python` 跳出 Microsoft Store：改打 `py`；还是不行就重装 Python 并勾 PATH。
- macOS 打 `python` 说找不到：macOS 只有 `python3`，这是正常的。
- 中文变成乱码（旧的「命令提示符」）：先打 `chcp 65001` 再跑一次，或改用 Windows 终端。

⚠ 输出里会有密钥的片段。截图或贴给别人之前先看一眼。

---

## 它在找什么

三条线索。机器不会说谎，凡走过必留下痕迹。

1. **代码**——`from openai import OpenAI`、`import anthropic` 这类官方 SDK 的引用。
2. **配置文件**——`api.openai.com` 这类 API 域名。代码可以包得很深，流量总要有个出口。
3. **密钥**——每一家的密钥都有固定的开头，`sk-ant-api03-`、`sk-proj-`、`AIza`。

---

## 分三级，因为三级要找的人不一样

不管几条，每一条看起来都一样重要，就等于没有一条重要。所以每一条都标了等级和派工对象。

| 等级 | 什么情况 | 派给谁 | 多急 |
|---|---|---|---|
| 高 | 密钥写在代码或配置文件里 | 安全团队 | 今天就换掉，不用讨论 |
| 中 | 代码确定会把数据送到外部 AI | 法务与采购 | 有签约吗？送了什么？ |
| 低 | 装了包，或有痕迹但没在跑 | 工程主管 | 不急，但要找人问清楚 |

输出每一条都有文件、行号、原始那一行，以及一句「这代表什么」。直接可以派工。

---

## 它看不到的地方

这支工具靠关键字比对，不是深度静态分析。跑完它会自己把这四件事打印出来：

1. **自己包起来的 AI 调用。** 代码里只写 `from vendor.llm_client import ask`，看不出底下接的是哪一家。
2. **运行时才决定的包名。** 名字来自环境变量或配置文件的话，`import` 那一行没东西可比对。
3. **行尾注释与多行字符串里的注释。** 工具只看行首，这些会判错。
4. **有装不等于有用。** 依赖清单只能证明有人装过。

扫出 N 个，实际上可能不止 N 个。**这份清单是要查的起点，不是全部。**

第 1 点和第 2 点不是偷懒，是这个做法的边界：要看穿它得做跨文件的数据流分析，那就不是一个下午写得完的工具了。

---

## 接进 CI

有任何「高」风险就返回退出码 1，其余返回 0；参数错误或路径不存在返回 2。

```bash
python3 shadow_ai_scan.py . --level high || echo "有密钥泄露，这次提交拦下来"
```

今天扫干净，三个月后又会长出来。接进 CI 比三个月盘点一次便宜得多。

---

## 换语言

```bash
python3 shadow_ai_scan.py . --lang ja          # ja / ko / en / de / zh-TW / zh-CN
SHADOW_AI_LANG=ko python3 shadow_ai_scan.py .  # 也可以用环境变量
```

不指定就按操作系统的语言走，认不出来就用英文。

`--level` 收得下六种语言的写法，`--level 高`、`--level high`、`--level 높은 위험` 都可以。

---

## 许可

MIT。拿去改、拿去内部用、拿去包进你们自己的工具，都可以。

---

## 这支工具从哪来

这是某一集视频的随集工具，视频在讲：公司里有多少个没人登记过的 AI 调用，以及为什么发公告禁止没有用。

它刻意只做一个仓库、跑完就结束。如果你要管的是两百个仓库、要定时、要留下经得起审计的记录、要让误报不再一直回来，那是另一个层级的问题，我们做了 **ForgeHelm** 在处理它。

但先把这一个仓库扫过一遍——多数人会发现的第一件事是：数字不对。
