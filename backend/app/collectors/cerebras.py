"""
Cerebras collector — fetch free-tier models from public Cerebras API.
Endpoint: GET https://api.cerebras.ai/public/v1/models (NO auth required)
Models have paid pricing on public API, but generous free tier exists via account.
We maintain known free-tier model IDs manually.
"""

import httpx
from app.collectors.base import CollectorBase

CEREBRAS_MODELS_URL = "https://api.cerebras.ai/public/v1/models"

# Models with free tier access on Cerebras (per free-llm-api-resources + Cerebras docs)
# These have paid pricing on public API but free tier with rate limits.
KNOWN_FREE_TIER_IDS: set[str] = {
    "gpt-oss-120b",      # 30 RPM, 14.4K RPD, 1M TPD free tier (free-llm-api-resources)
    "zai-glm-4.7",       # Also has free tier
    # "llama-3.1-8b",     # Not currently on public endpoint
}


class CerebrasCollector(CollectorBase):
    def __init__(self, supabase):
        super().__init__(supabase, "cerebras")

    def fetch_models(self) -> list[dict]:
        """Fetch all models from public Cerebras API (no auth)."""
        with httpx.Client(
            timeout=30,
            headers={"User-Agent": "TokenZero/1.0 (free-model-directory)"},
        ) as client:
            resp = client.get(CEREBRAS_MODELS_URL)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])

    def is_free(self, raw: dict) -> bool:
        """Cerebras models with free tier are in our known set."""
        return raw.get("id", "") in KNOWN_FREE_TIER_IDS

    def normalize(self, raw: dict) -> dict:
        """Convert Cerebras model to our schema. Rich data from public API."""
        mid = raw.get("id", "")
        name = raw.get("name", mid)
        desc = raw.get("description")
        ctx = raw.get("limits", {}).get("max_context_length")
        max_out = raw.get("limits", {}).get("max_completion_tokens")

        # Pricing from public API (per-token USD) — converted to per-token strings
        pricing = raw.get("pricing", {})
        inp = float(pricing.get("prompt", 0))
        out = float(pricing.get("completion", 0))

        # Input modalities from architecture
        arch = raw.get("architecture", {})
        mods = ["text", "image"] if arch.get("modality") != "text" else ["text"]

        # Capability heuristics from capabilities dict + model ID
        caps = self._derive_capabilities(mid, raw.get("capabilities", {}))

        # Clean display name
        display_name = name

        return {
            "provider_id": "cerebras",
            "model_id": mid,
            "display_name": display_name,
            "description": desc,
            "context_length": ctx,
            "max_output": max_out,
            "input_modalities": mods,
            "capabilities": caps,
            "is_free": True,  # free tier available
            "pricing": {"input_tokens": inp, "output_tokens": out},
            "rate_limits": {"note": "Free tier: generous limits (e.g., 14.4K req/day for gpt-oss-120b)"},
            "source": "api",
        }

    @staticmethod
    def _derive_capabilities(mid: str, caps_dict: dict) -> list[str]:
        """Derive capabilities from API capabilities dict + model ID heuristics."""
        caps = []

        # From API capabilities
        if caps_dict.get("reasoning"):
            caps.append("reasoning")
        if caps_dict.get("function_calling") or caps_dict.get("tools"):
            caps.append("coding")
        if caps_dict.get("vision"):
            caps.append("vision")

        # Heuristics from model ID
        mid_lower = mid.lower()
        if any(kw in mid_lower for kw in ["coder", "code", "gpt-oss", "glm"]):
            if "coding" not in caps:
                caps.append("coding")
        if any(kw in mid_lower for kw in ["reason", "r1", "think", "glm", "gpt-oss"]):
            if "reasoning" not in caps:
                caps.append("reasoning")

        # "text" always last
        caps.append("text")
        return caps
