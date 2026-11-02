
import json
import time
import uuid
import requests

from ...core.settings import Settings
from ...core.db import db
from ...core.resource_manager import INFERENCE_GATE


GROQ_MODEL = "openai/gpt-oss-120b"
OPENROUTER_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

PREFERRED = {
    "reasoning": [
        ("groq", GROQ_MODEL),
        ("openrouter", OPENROUTER_MODEL),
    ],
    "fast_reasoning": [
        ("groq", GROQ_MODEL),
        ("openrouter", OPENROUTER_MODEL),
    ],
}

TIMEOUT = (15, 120)


def _record_usage(
    context, provider, model, input_tokens, output_tokens,
    latency_ms, status, fallback_used, error_category=None
):
    if not context or not context.get("run_id"):
        return False

    try:
        metadata = {
            "fallback_used": bool(fallback_used),
            "error_category": error_category,
            "logging_version": 1,
        }

        with db() as conn:
            conn.execute(
                """
                INSERT INTO asde_resource_usage (
                    usage_id, run_id, task_id, attempt_id, agent_id,
                    provider, model_id, input_tokens, output_tokens,
                    latency_ms, request_status, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                """,
                (
                    "usage_" + uuid.uuid4().hex,
                    context["run_id"],
                    context.get("task_id"),
                    context.get("attempt_id"),
                    context.get("agent_id"),
                    provider,
                    model,
                    input_tokens,
                    output_tokens,
                    latency_ms,
                    status,
                    json.dumps(metadata),
                ),
            )
        return True

    except Exception:
        # Observability must never break a successful or failed inference.
        return False


def _post_chat_completion(
    provider, model, prompt, context=None, fallback_used=False
):
    if provider == "groq":
        api_key = Settings.groq_api_key
        endpoint = "https://api.groq.com/openai/v1/chat/completions"

        if not api_key:
            raise RuntimeError("Groq API key is not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    elif provider == "openrouter":
        api_key = Settings.openrouter_api_key
        endpoint = "https://openrouter.ai/api/v1/chat/completions"

        if not api_key:
            raise RuntimeError("OpenRouter API key is not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "ASDE Scientific Discovery Engine",
        }

    else:
        raise ValueError("Provider not approved")

    started = time.monotonic()
    input_tokens = None
    output_tokens = None
    status = "failed"
    error_category = None

    try:
        with INFERENCE_GATE.slot(provider, timeout=150):
            response = requests.post(
                endpoint,
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
                timeout=TIMEOUT,
            )

        if not response.ok:
            error_category = f"http_{response.status_code}"
            raise RuntimeError(
                f"{provider} request failed with HTTP {response.status_code}"
            )

        data = response.json()
        usage = data.get("usage") or {}

        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")

        content = data["choices"][0]["message"]["content"]

        if not isinstance(content, str) or not content.strip():
            error_category = "invalid_or_empty_response"
            raise RuntimeError(f"{provider} returned empty or invalid content")

        status = "success"
        return content

    except Exception as exc:
        if error_category is None:
            error_category = (
                "timeout" if isinstance(exc, requests.Timeout)
                else "request_or_response_error"
            )
        raise

    finally:
        latency_ms = int((time.monotonic() - started) * 1000)
        _record_usage(
            context=context,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status=status,
            fallback_used=fallback_used,
            error_category=error_category,
        )


def call_exact(provider, model, prompt, *, context=None):
    """Call exactly the requested provider/model."""
    return _post_chat_completion(
        provider, model, prompt, context=context, fallback_used=False
    )


def call_routed(task, prompt, *, context=None):
    """
    Groq primary -> OpenRouter fallback.
    Each actual provider attempt is logged independently when context is supplied.
    """
    if task not in PREFERRED:
        raise ValueError(f"Unknown routing task: {task}")

    primary_provider, primary_model = PREFERRED[task][0]
    fallback_provider, fallback_model = PREFERRED[task][1]

    try:
        content = _post_chat_completion(
            primary_provider, primary_model, prompt,
            context=context, fallback_used=False
        )

        return {
            "content": content,
            "provider": primary_provider,
            "model": primary_model,
            "fallback_used": False,
        }

    except Exception:
        try:
            content = _post_chat_completion(
                fallback_provider, fallback_model, prompt,
                context=context, fallback_used=True
            )

            return {
                "content": content,
                "provider": fallback_provider,
                "model": fallback_model,
                "fallback_used": True,
            }

        except Exception:
            raise RuntimeError(
                "Both approved inference providers failed. "
                "Pause the task and checkpoint before retrying."
            ) from None
