import pytest

from asde.integrations.models import router


def test_routing_uses_groq_then_openrouter_then_cloudflare(monkeypatch):
    calls = []

    def fake_post(provider, model, prompt, context=None, fallback_used=False):
        calls.append((provider, model, fallback_used))
        if provider in {"groq", "openrouter"}:
            raise RuntimeError("simulated provider outage")
        return "verified transport response"

    monkeypatch.setattr(router, "_post_chat_completion", fake_post)

    result = router.call_routed("reasoning", "test prompt")

    assert [item[0] for item in calls] == [
        "groq", "openrouter", "cloudflare"
    ]
    assert calls[0][2] is False
    assert calls[1][2] is True
    assert calls[2][2] is True
    assert result["provider"] == "cloudflare"
    assert result["model"] == router.CLOUDFLARE_MODEL
    assert result["fallback_used"] is True
    assert result["content"] == "verified transport response"


def test_router_pauses_when_all_providers_fail(monkeypatch):
    def always_fail(provider, model, prompt, context=None, fallback_used=False):
        raise RuntimeError("simulated outage")

    monkeypatch.setattr(router, "_post_chat_completion", always_fail)

    with pytest.raises(RuntimeError, match="All configured inference providers failed"):
        router.call_routed("reasoning", "test prompt")
