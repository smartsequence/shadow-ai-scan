"""內部 LLM 客戶端。當初包的人已經離職，現在沒人記得它底下接的是哪一家。"""
import importlib
import os

# 後端由部署設定決定，換一家 AI 公司不用改程式碼
_BACKEND = importlib.import_module(os.environ["LLM_BACKEND"])


def ask(prompt: str, model: str = "gpt-4o-mini") -> str:
    client = _BACKEND.OpenAI()
    r = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
