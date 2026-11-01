import requests
from ...core.settings import Settings
PREFERRED={"reasoning":[("groq","openai/gpt-oss-120b"),("gemini","gemini-3.1-pro-preview")],
           "fast_reasoning":[("gemini","gemini-3.8-flash"),("groq","qwen/qwen3.8-27b")]}
def call_exact(provider,model,prompt):
    if provider=="groq":
        if not Settings.groq_api_key: raise RuntimeError("Groq key missing")
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",
          headers={"Authorization":"Bearer "+Settings.groq_api_key},
          json={"model":model,"messages":[{"role":"user","content":prompt}],"temperature":0.2},timeout=120)
        if r.status_code in (401,403,429): raise RuntimeError(f"Groq auth/quota failure HTTP {r.status_code}")
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    if provider=="gemini":
        if not Settings.gemini_api_key: raise RuntimeError("Gemini key missing")
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={Settings.gemini_api_key}"
        r=requests.post(url,json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.2}},timeout=120)
        if r.status_code in (401,403,429): raise RuntimeError(f"Gemini auth/quota failure HTTP {r.status_code}")
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    raise ValueError("Unknown provider")
