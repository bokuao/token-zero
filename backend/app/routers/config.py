from fastapi import APIRouter, HTTPException
from app.database import get_supabase
from app.data.providers import PROVIDERS
from app.data.agents import AGENTS
from app.renderers import RENDERERS

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/{agent_id}/{model_id}")
def get_config(agent_id: str, model_id: int):
    """Generate config for a specific agent + model."""
    supabase = get_supabase()

    # Get model
    result = (
        supabase.table("t0_models")
        .select("id, model_id, display_name, provider_id")
        .eq("id", model_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Model not found")

    model = result.data[0]
    provider_id = model["provider_id"]

    # Get agent
    agent = AGENTS.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Get renderer
    renderer = RENDERERS.get(agent_id)
    if not renderer:
        raise HTTPException(status_code=501, detail=f"No renderer for agent '{agent_id}'")

    # Get provider config
    pconfig = PROVIDERS.get(provider_id, {})
    base_url = pconfig.get("base_url", "")
    provider_name = pconfig.get("name", provider_id)

    filename, content = renderer(provider_id, provider_name, base_url, model["model_id"], agent["key_placeholder"])

    return {
        "filename": filename,
        "format": filename.rsplit(".", 1)[-1],
        "content": content,
        "agent": agent["name"],
        "model": model.get("display_name", model["model_id"]),
        "paths": agent.get("paths", {}),
    }
