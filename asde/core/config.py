"""Central configuration. Secrets are loaded from environment at runtime."""
import os

def get_env(name, default=None):
    return os.environ.get(name, default)
