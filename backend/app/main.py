from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import providers, models, config
from app.config import settings
from app.database import get_supabase
from app.scheduler import start_scheduler, stop_scheduler
from app.middleware import AntiBotMiddleware
from app.cache import cached


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit, "5/second"],  # burst protection
)

app = FastAPI(
    title="TokenZero API",
    description="Free LLM directory + config generator",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

# Anti-bot (block crawlers/scrapers)
app.add_middleware(AntiBotMiddleware)

# CORS — open for SPA frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Rate limiter — global
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(providers.router)
app.include_router(models.router)
app.include_router(config.router)


@app.get("/stats")
@cached()
@limiter.limit("10/minute")
def stats(request: Request):
    supabase = get_supabase()
    providers_count = (
        supabase.table("t0_providers")
        .select("id", count="exact")
        .eq("status", "active")
        .execute()
    )
    models_count = (
        supabase.table("t0_models")
        .select("id", count="exact")
        .eq("is_free", True)
        .eq("is_active", True)
        .execute()
    )
    return {
        "providers": providers_count.count if hasattr(providers_count, 'count') else 0,
        "models": models_count.count if hasattr(models_count, 'count') else 0,
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
