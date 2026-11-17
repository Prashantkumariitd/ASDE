import psycopg
from contextlib import contextmanager
from .settings import Settings
@contextmanager
def db():
    if not Settings.database_url: raise RuntimeError("NEON_DATABASE_URL missing")
    with psycopg.connect(Settings.database_url) as conn:
        yield conn
