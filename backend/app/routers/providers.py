from fastapi import APIRouter, HTTPException, Query
from app.database import get_supabase
from app.data.providers import PROVIDERS
from app.routers.models import _fmt_rate
from app.healthcheck import get_cached_health
from app.cache import cached

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("")
@cached()
def list_providers(sort: str = ""):
    """List all providers with their free models grouped underneath.
    sort: 'newest' = models ordered by first_seen_at DESC."""
    supabase = get_supabase()
    result = []

    for pid, pconfig in PROVIDERS.items():
        query = (
            supabase.table("t0_models")
            .select("id, model_id, display_name, capabilities, input_modalities, context_length, first_seen_at")
            .eq("provider_id", pid)
            .eq("is_free", True)
            .eq("is_active", True)
        )
        if sort == "newest":
            query = query.order("first_seen_at", desc=True)
        else:
            query = query.order("display_name")

        db_models = query.execute()

        # Skip providers with 0 free models
        if not db_models.data:
            continue

        result.append({
            "id": pid,
            "name": pconfig["name"],
            "logo_url": pconfig.get("logo_url", ""),
            "website_url": pconfig["website_url"],
            "signup_url": pconfig["signup_url"],
            "api_keys_url": pconfig["api_keys_url"],
            "base_url": pconfig["base_url"],
            "requires_credit_card": pconfig["requires_credit_card"],
            "requires_phone": pconfig["requires_phone"],
            "trains_on_data": pconfig["trains_on_data"],
            "model_count": len(db_models.data),
            "models": [
                {
                    "id": m["id"],
                    "model_id": m["model_id"],
                    "display_name": m["display_name"],
                    "capabilities": m.get("capabilities", []),
                    "input_modalities": m.get("input_modalities", ["text"]),
                    "first_seen_at": m.get("first_seen_at"),
                }
                for m in db_models.data
            ],
        })

    return result


@router.get("/{provider_id}/health")
def provider_health(provider_id: str):
    """Check if a provider's API is reachable (no token needed)."""
    if provider_id not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")
    pconfig = PROVIDERS[provider_id]
    return {
        "provider_id": provider_id,
        "name": pconfig["name"],
        **get_cached_health(provider_id, pconfig["base_url"]),
    }


@router.get("/{provider_id}")
def get_provider(provider_id: str):
    """Get one provider with full model details."""
    if provider_id not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    pconfig = PROVIDERS[provider_id]
    supabase = get_supabase()

    db_models = (
        supabase.table("t0_models")
        .select("id, model_id, display_name, description, context_length, max_output, "
                "capabilities, input_modalities, is_free, pricing, rate_limits, "
                "first_seen_at, last_seen_at, free_since")
        .eq("provider_id", provider_id)
        .eq("is_free", True)
        .eq("is_active", True)
        .order("display_name")
        .execute()
    )

    return {
        "id": provider_id,
        **pconfig,
        "models": [
            {
                "id": m["id"],
                "model_id": m["model_id"],
                "display_name": m["display_name"],
                "description": m.get("description"),
                "context_length": m.get("context_length"),
                "capabilities": m.get("capabilities", []),
                "input_modalities": m.get("input_modalities", ["text"]),
                "rate_limits": _fmt_rate(m.get("rate_limits")),
            }
            for m in db_models.data
        ],
    }
