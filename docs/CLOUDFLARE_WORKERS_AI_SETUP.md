# Cloudflare Workers AI provider setup

This adds Cloudflare Workers AI as the third inference lane:

1. Groq — primary: `openai/gpt-oss-120b`
2. OpenRouter — fallback: `nvidia/nemotron-3-ultra-550b-a55b:free`
3. Cloudflare Workers AI — final fallback: `@cf/meta/llama-3.1-8b-instruct-fp8-fast`

Gemini and Mistral remain disabled. Provider/model provenance is returned by the router and each provider attempt is written independently to `asde_resource_usage` when run context is supplied.

## Required Colab Secrets

Create a Cloudflare account, open Workers AI in the dashboard, choose **Use REST API**, create a Workers AI API token, and copy the Account ID. Add these two secrets to Colab Secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Do not paste either value into notebook cells, GitHub, logs, or chat. Load them into environment variables before importing ASDE modules:

```python
import os
from google.colab import userdata

os.environ["CLOUDFLARE_API_TOKEN"] = userdata.get("CLOUDFLARE_API_TOKEN")
os.environ["CLOUDFLARE_ACCOUNT_ID"] = userdata.get("CLOUDFLARE_ACCOUNT_ID")
```

Optional configuration:

- `ASDE_CLOUDFLARE_MODEL` (default: `@cf/meta/llama-3.1-8b-instruct-fp8-fast`)
- `ASDE_CLOUDFLARE_MAX_OUTPUT_TOKENS` (default: `1200`, bounded 128–4096)
- `ASDE_CLOUDFLARE_MAX_CONCURRENT_CALLS` (default: `1`)

## Free allowance and practical throughput

Cloudflare Workers AI currently includes 10,000 Neurons/day on the Workers Free plan. It is a compute allowance, not a fixed requests-per-day quota; actual call count depends on model and prompt/output length. The selected Llama 3.1 8B model is listed at 4,119 Neurons per million input tokens and 34,868 Neurons per million output tokens. As a planning estimate, 100 calls averaging 2,500 input tokens and 1,000 output tokens would consume about 4,517 Neurons. Actual usage varies, so monitor the Workers AI dashboard and retain ASDE's own call/token budget gates.

The selected 8B model is a quota-efficient overflow lane, not a substitute for Groq's 120B model or independent mathematical computation. Treat its output as a proposal; SymPy/Python checks and independent verification remain mandatory.

## Smoke test

Run only after adding the two Colab Secrets:

```python
from asde.integrations.models.router import call_exact
from asde.core.settings import Settings

assert Settings.cloudflare_api_token
assert Settings.cloudflare_account_id

answer = call_exact(
    "cloudflare",
    Settings.cloudflare_model,
    "Return exactly: ASDE_CLOUDFLARE_OK",
)
print(answer)
```

This direct smoke test does not mutate research tasks. After it succeeds, run a small bounded test task and confirm a Cloudflare row appears in `asde_resource_usage`. Only then resume the saved research run.

## Resume safety

Do not reset or recreate the Neon database. Do not blindly rerun completed tasks. First inspect the run's queued/failed tasks and retry eligibility. The audited run ID is `run_asde_superdet_v1_2dae291bcdc9`; its 26 completed tasks and their outputs should remain immutable. Retry only eligible failed/queued work using the existing resume mechanism after provider smoke testing and a fresh DB health check.
