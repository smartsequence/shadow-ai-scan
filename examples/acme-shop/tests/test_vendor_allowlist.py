"""採購白名單測試：列管的供應商都要簽過 DPA。"""
from config.vendors import ALLOWED_VENDORS


def test_ai_vendors_require_dpa():
    """列在這裡的供應商必須簽 DPA 才能用。"""
    for name in ("openai", "anthropic", "google"):
        assert ALLOWED_VENDORS[name]["dpa_signed"] is True
