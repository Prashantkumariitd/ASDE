
import os


def _int_env(name, default, minimum=0, maximum=100000):
    try:
        value = int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


class Settings:
    # Persistent storage
    database_url = os.environ.get("NEON_DATABASE_URL", "")

    # Approved inference providers
    groq_api_key = os.environ.get("GROQ_API_KEY", "")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")

    # GitHub integration
    github_token = os.environ.get("GITHUB_TOKEN", "")
    github_token_2 = os.environ.get("GITHUB_TOKEN_2", "")
    github_provisioner_token = os.environ.get(
        "GITHUB_PROVISIONER_TOKEN", ""
    )

    # Agent capacity
    max_registered_agents = _int_env(
        "ASDE_MAX_REGISTERED_AGENTS", 1000, 1, 10000
    )
    max_active_agents = _int_env(
        "ASDE_MAX_ACTIVE_AGENTS", 5, 1, 1000
    )

    # Worker capacity
    max_workers = _int_env("ASDE_MAX_WORKERS", 3, 1, 64)
    hard_max_workers = _int_env(
        "ASDE_HARD_MAX_WORKERS", 8, 1, 128
    )

    # Inference concurrency
    max_concurrent_calls = _int_env(
        "ASDE_MAX_CONCURRENT_CALLS", 2, 1, 32
    )
    groq_max_concurrent_calls = _int_env(
        "ASDE_GROQ_MAX_CONCURRENT_CALLS", 2, 1, 32
    )
    openrouter_max_concurrent_calls = _int_env(
        "ASDE_OPENROUTER_MAX_CONCURRENT_CALLS", 1, 1, 32
    )

    # Run and discussion limits
    max_concurrent_runs = _int_env(
        "ASDE_MAX_CONCURRENT_RUNS", 1, 1, 32
    )
    max_discussion_rounds = _int_env(
        "ASDE_MAX_DISCUSSION_ROUNDS", 3, 1, 20
    )
    max_calls_per_run = _int_env(
        "ASDE_MAX_CALLS_PER_RUN", 30, 1, 10000
    )
    max_tokens_per_run = _int_env(
        "ASDE_MAX_TOKENS_PER_RUN", 50000, 1000, 10000000
    )

    # Worker lifecycle
    worker_heartbeat_seconds = _int_env(
        "ASDE_WORKER_HEARTBEAT_SECONDS", 30, 5, 300
    )
    task_lease_seconds = _int_env(
        "ASDE_TASK_LEASE_SECONDS", 180, 30, 3600
    )
    task_timeout_seconds = _int_env(
        "ASDE_TASK_TIMEOUT_SECONDS", 600, 30, 7200
    )
    max_task_attempts = _int_env(
        "ASDE_MAX_TASK_ATTEMPTS", 2, 1, 10
    )
    max_runtime_seconds = _int_env(
        "ASDE_MAX_RUNTIME_SECONDS", 3600, 60, 43200
    )

    # Conservative runtime memory budgeting
    memory_reserve_mb = _int_env(
        "ASDE_MEMORY_RESERVE_MB", 1536, 256, 65536
    )
    memory_per_worker_mb = _int_env(
        "ASDE_MEMORY_PER_WORKER_MB", 512, 128, 8192
    )
