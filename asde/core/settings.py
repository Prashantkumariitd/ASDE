import os
class Settings:
    database_url=os.environ.get("NEON_DATABASE_URL","")
    groq_api_key=os.environ.get("GROQ_API_KEY","")
    gemini_api_key=os.environ.get("GEMINI_API_KEY","")
    github_token=os.environ.get("GITHUB_TOKEN","")
    github_provisioner_token=os.environ.get("GITHUB_PROVISIONER_TOKEN","")
    max_concurrent_calls=int(os.environ.get("ASDE_MAX_CONCURRENT_CALLS","2"))
