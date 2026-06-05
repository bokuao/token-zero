from fastapi import APIRouter, HTTPException, Query
from app.database import get_supabase
from app.data.providers import PROVIDERS


def _fmt_rate(rate_limits):
    """Convert JSONB rate_limits to readable string."""
    if not rate_limits:
        return None
    if isinstance(rate_limits, str):
        return rate_limits
    if isinstance(rate_limits, dict):
        parts = []
        for k, v in rate_limits.items():
            if k == "note":
                return str(v)
            parts.append(f"{k}: {v}")
        return ", ".join(parts) if parts else None
    return str(rate_limits)


router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
def list_models(
    provider: str | None = Query(None),
    capability: str | None = Query(None),
    q: str | None = Query(None),
):
    """Flat list of all free models, optional filter."""
    supabase = get_supabase()
    query = (
        supabase.table("t0_models")
        .select("id, provider_id, model_id, display_name, description, "
                "context_length, capabilities, input_modalities, rate_limits")
        .eq("is_free", True)
        .eq("is_active", True)
        .order("display_name")
    )

    if provider:
        query = query.eq("provider_id", provider)

    result = query.execute()

    models = []
    for m in result.data:
        caps = m.get("capabilities", [])
        if capability and capability not in caps:
            continue
        if q:
            ql = q.lower()
            name = (m.get("display_name") or "").lower()
            mid = (m.get("model_id") or "").lower()
            if ql not in name and ql not in mid:
                continue
        models.append({
            "id": m["id"],
            "provider_id": m["provider_id"],
            "model_id": m["model_id"],
            "display_name": m.get("display_name"),
            "description": m.get("description"),
            "context_length": m.get("context_length"),
            "capabilities": caps,
            "input_modalities": m.get("input_modalities", ["text"]),
            "rate_limits": _fmt_rate(m.get("rate_limits")),
        })

    return models


@router.get("/{model_id}")
def get_model(model_id: int):
    """Get one model with full details + provider info."""
    supabase = get_supabase()
    result = (
        supabase.table("t0_models")
        .select("*, t0_providers!inner(id, name)")
        .eq("id", model_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Model not found")

    m = result.data[0]
    provider_id = m["provider_id"]
    provider_name = (
        m["t0_providers"]["name"]
        if isinstance(m.get("t0_providers"), dict)
        else ""
    )
    return {
        "id": m["id"],
        "model_id": m["model_id"],
        "display_name": m.get("display_name"),
        "description": m.get("description"),
        "context_length": m.get("context_length"),
        "max_output": m.get("max_output"),
        "capabilities": m.get("capabilities", []),
        "input_modalities": m.get("input_modalities", ["text"]),
        "rate_limits": _fmt_rate(m.get("rate_limits")),
        "provider": {
            "id": provider_id,
            "name": provider_name,
            "base_url": PROVIDERS.get(provider_id, {}).get("base_url", ""),
        },
    }
