"""
Database connection — Supabase (Coolify self-host) atau Postgres langsung.
Prioritas: SUPABASE_URL + SUPABASE_SERVICE_KEY > DATABASE_URL.
"""

from supabase import create_client, Client
from app.config import settings

_supabase: Client | None = None


def get_supabase() -> Client:
    """Return Supabase client (pakai service key — server-side only)."""
    global _supabase
    if _supabase is None:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise RuntimeError(
                "SUPABASE_URL dan SUPABASE_SERVICE_KEY belum di-set di .env"
            )
        _supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
    return _supabase


# Placeholder untuk Postgres direct (via SQLAlchemy nanti)
# def get_db():
#     ...
