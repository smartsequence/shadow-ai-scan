"""動態定價：參考競品報價給出建議售價。"""
from vendor.llm_client import ask


def suggest_price(sku: str, competitor_prices: list[float]) -> float:
    hint = ask(f"競品價格 {competitor_prices}，{sku} 建議定價？")
    return float(hint.strip().lstrip("$"))
