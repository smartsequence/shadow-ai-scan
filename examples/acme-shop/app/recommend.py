"""商品推薦：依使用者瀏覽紀錄產生推薦清單。"""
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def recommend(user_id: str, viewed: list[str]) -> list[str]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"使用者看過 {viewed}，推薦五件商品"}],
    )
    return resp.choices[0].message.content.split("\n")
