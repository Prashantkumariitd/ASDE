
import os
import time
import threading
from contextlib import contextmanager

from .settings import Settings


def _available_memory_mb():
    try:
        import psutil
        return int(psutil.virtual_memory().available / (1024 * 1024))
    except Exception:
        return None


def capacity_snapshot():
    cpu_count = max(1, os.cpu_count() or 1)
    available_memory = _available_memory_mb()

    cpu_worker_capacity = cpu_count * 2

    if available_memory is None:
        memory_worker_capacity = Settings.hard_max_workers
    else:
        usable_memory = available_memory - Settings.memory_reserve_mb
        memory_worker_capacity = max(
            0, usable_memory // Settings.memory_per_worker_mb
        )

    worker_capacity = min(
        Settings.max_workers,
        Settings.hard_max_workers,
        cpu_worker_capacity,
        memory_worker_capacity,
    )

    return {
        "cpu_count": cpu_count,
        "available_memory_mb": available_memory,
        "configured_workers": Settings.max_workers,
        "hard_max_workers": Settings.hard_max_workers,
        "cpu_worker_capacity": cpu_worker_capacity,
        "memory_worker_capacity": memory_worker_capacity,
        "safe_worker_capacity": int(worker_capacity),
        "global_model_call_limit": Settings.max_concurrent_calls,
        "groq_call_limit": Settings.groq_max_concurrent_calls,
        "openrouter_call_limit": Settings.openrouter_max_concurrent_calls,
        "max_active_agents": Settings.max_active_agents,
    }


def build_allocation_plan(
    pending_tasks,
    available_agents,
    requested_workers=None,
):
    if not isinstance(pending_tasks, int) or pending_tasks < 0:
        raise ValueError("pending_tasks must be a non-negative integer")

    if not isinstance(available_agents, int) or available_agents < 0:
        raise ValueError("available_agents must be a non-negative integer")

    snapshot = capacity_snapshot()
    target = Settings.max_workers if requested_workers is None else requested_workers

    if not isinstance(target, int) or target < 0:
        raise ValueError("requested_workers must be a non-negative integer")

    workers = min(target, snapshot["safe_worker_capacity"], pending_tasks)
    active_agents = min(
        available_agents, Settings.max_active_agents, pending_tasks
    )
    global_slots = min(Settings.max_concurrent_calls, workers)

    return {
        "pending_tasks": pending_tasks,
        "available_agents": available_agents,
        "active_agents": active_agents,
        "workers": workers,
        "global_model_call_slots": global_slots,
        "groq_model_call_slots": min(
            Settings.groq_max_concurrent_calls, global_slots
        ),
        "openrouter_model_call_slots": min(
            Settings.openrouter_max_concurrent_calls, global_slots
        ),
        "limits": snapshot,
        "execution_started": False,
    }


class InferenceGate:
    """
    Process-local concurrency controller.

    Every request must acquire BOTH the global slot and its provider slot.
    This enforces the global ceiling across Groq and OpenRouter combined.

    For multiple independent runtimes, a distributed database-backed
    limiter will be required; Python semaphores alone are not distributed.
    """

    def __init__(self):
        self.global_limit = max(1, Settings.max_concurrent_calls)

        self.provider_limits = {
            "groq": min(
                self.global_limit,
                max(1, Settings.groq_max_concurrent_calls),
            ),
            "openrouter": min(
                self.global_limit,
                max(1, Settings.openrouter_max_concurrent_calls),
            ),
        }

        self._global = threading.BoundedSemaphore(self.global_limit)
        self._providers = {
            name: threading.BoundedSemaphore(limit)
            for name, limit in self.provider_limits.items()
        }

        self._lock = threading.Lock()
        self._active_global = 0
        self._active_provider = {name: 0 for name in self.provider_limits}
        self._max_global_seen = 0
        self._max_provider_seen = {name: 0 for name in self.provider_limits}

    @contextmanager
    def slot(self, provider, timeout=120):
        if provider not in self._providers:
            raise ValueError("Provider not approved by inference gate")

        deadline = time.monotonic() + timeout
        global_acquired = False
        provider_acquired = False

        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Inference capacity acquisition timed out")

                global_acquired = self._global.acquire(
                    timeout=min(remaining, 0.25)
                )

                if not global_acquired:
                    continue

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Provider capacity acquisition timed out")

                provider_acquired = self._providers[provider].acquire(
                    timeout=min(remaining, 0.25)
                )

                if provider_acquired:
                    break

                # Do not hold a global slot while waiting for provider capacity.
                self._global.release()
                global_acquired = False

            with self._lock:
                self._active_global += 1
                self._active_provider[provider] += 1

                self._max_global_seen = max(
                    self._max_global_seen, self._active_global
                )
                self._max_provider_seen[provider] = max(
                    self._max_provider_seen[provider],
                    self._active_provider[provider],
                )

            yield

        finally:
            if provider_acquired:
                with self._lock:
                    self._active_global -= 1
                    self._active_provider[provider] -= 1

                self._providers[provider].release()

            if global_acquired:
                self._global.release()

    def snapshot(self):
        with self._lock:
            return {
                "global_limit": self.global_limit,
                "provider_limits": dict(self.provider_limits),
                "active_global": self._active_global,
                "active_provider": dict(self._active_provider),
                "max_global_observed": self._max_global_seen,
                "max_provider_observed": dict(self._max_provider_seen),
            }


# One shared gate per Colab Python process.
INFERENCE_GATE = InferenceGate()
