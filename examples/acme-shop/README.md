# acme-shop — a fictional repo to scan

這是一間虛構電商的 repo，用來讓你第一次執行就看得到結果。
**裡面沒有任何真實資料或有效金鑰**，所有看起來像金鑰的字串都是 `EXAMPLE` 填充的假值。

A made-up e-commerce repo, here so your first run has something to find.
**No real data and no working keys** — every key-shaped string is padded with `EXAMPLE`.

```bash
cd examples/acme-shop
python3 ../../shadow_ai_scan.py .
```

---

它刻意湊齊了五種情況，每一種都在真實的 repo 裡會遇到：

It deliberately covers five cases, all of which happen in real repositories:

| 情況 Case | 檔案 File | 說明 |
|---|---|---|
| 真陽性 True positive | `app/recommend.py`, `services/support_bot.py` | 明著 import AI SDK，其中一支還把金鑰寫死。Imports an AI SDK outright; one also hardcodes a key. |
| 偽陽性：註解 Commented out | `app/legacy_search.py` | import 被註解掉，程式碼沒在跑。The import is commented out; nothing runs. |
| 真陰性：字串 Just a string | `tests/test_vendor_allowlist.py` | 只是供應商名稱字串，不該被報。A vendor name in a string; it should not be flagged. |
| 真陰性：別家金鑰 Another vendor's key | `config/stripe_test.py` | `sk_test_` 是 Stripe 的前綴（底線），AI 家用連字號 `sk-`。一個字元之差。Stripe uses an underscore, AI vendors use a hyphen. One character apart. |
| **偽陰性 False negative** | `vendor/llm_client.py` + `app/pricing.py` | 自建 wrapper ＋ 執行時才決定的 import，關鍵字比對抓不到。A hand-rolled wrapper plus a runtime import — keyword matching cannot see it. |

最後那一組才是重點。掃描器**不會**報 `vendor/llm_client.py`，但它確實在呼叫 AI；
`app/pricing.py` 呼叫它，從那一行也完全看不出來。跑完掃描會看到工具自己把這件事列出來。

The last row is the point. The scanner does **not** flag `vendor/llm_client.py`, yet that file
calls an AI service; `app/pricing.py` calls it and gives nothing away either. The tool lists
this blind spot itself at the end of a full run.

如果你的 repo 裡有 `vendor/`、`internal/` 這類目錄，那裡就是要找人打開來看的地方。

If your repo has a `vendor/` or `internal/` directory, that is where someone has to look by hand.
