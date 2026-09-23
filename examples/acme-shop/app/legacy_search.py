"""舊版搜尋。半年前評估過 AI 排序，後來放棄了，import 留著沒刪。"""
# from openai import OpenAI          # 2026-03 評估後棄用，改用 BM25
# client = OpenAI(api_key=...)

from .ranking import bm25_rank


def search(keyword: str, limit: int = 20) -> list[dict]:
    return bm25_rank(keyword, limit)
