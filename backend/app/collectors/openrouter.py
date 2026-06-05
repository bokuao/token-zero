"""
OpenRouter collector — fetch free models from public API.
Endpoint: GET https://openrouter.ai/api/v1/models (no auth needed)
"""

import httpx
from app.collectors.base import CollectorBase

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


class OpenRouterCollector(CollectorBase):
    def __init__(self, supabase):
        super().__init__(supabase, "openrouter")

    def fetch_models(self) -> list[dict]:
        """Fetch all models from OpenRouter public API."""
        with httpx.Client(
            timeout=30,
            headers={"User-Agent": "TokenZero/1.0 (free-model-directory)"},
        ) as client:
            resp = client.get(OPENROUTER_MODELS_URL)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])

    def is_free(self, raw: dict) -> bool:
        """OpenRouter free models: id ends with ':free' OR pricing is 0."""
        rid = raw.get("id", "")
        if rid.endswith(":free"):
            return True
        pricing = raw.get("pricing", {})
        prompt = float(pricing.get("prompt", -1))
        completion = float(pricing.get("completion", -1))
        return prompt == 0 and completion == 0

    def normalize(self, raw: dict) -> dict:
        """Convert OpenRouter model to our schema."""
        rid = raw.get("id", "")
        name = raw.get("name", rid)
        desc = raw.get("description", "")
        ctx = raw.get("context_length")
        max_out = raw.get("top_provider", {}).get("max_completion_tokens")
        pricing = raw.get("pricing", {})
        arch = raw.get("architecture", {})

        # Capabilities heuristics
        caps = []
        rid_lower = rid.lower()
        name_lower = name.lower()
        desc_lower = desc.lower()
        text = rid_lower + " " + name_lower + " " + desc_lower

        # Coding
        if any(kw in text for kw in ["coder", "code", "codestral", "starcoder", "wizardcoder", "deepseek-coder", "program"]):
            caps.append("coding")
        # Reasoning
        if any(kw in text for kw in ["reasoning", "r1", "think", "qwq", "deepseek-r1", "o1-", "o3-"]):
            caps.append("reasoning")
        # Vision
        if any(kw in text for kw in ["vision", "visual", "flash", "gemini-2", "vl", "multimodal", "llava", "cogvlm", "ocr"]):
            caps.append("vision")

        # Always add "text" as baseline — every LLM handles text
        caps.append("text")

        modalities = arch.get("modality", "text")
        if modalities == "multimodal" or "image" in str(raw.get("input_modalities", [])):
            mods = ["text", "image"]
        else:
            mods = ["text"]

        return {
            "provider_id": "openrouter",
            "model_id": rid,
            "display_name": name,
            "description": desc or None,
            "context_length": ctx,
            "max_output": max_out,
            "input_modalities": mods,
            "capabilities": caps,
            "is_free": True,
            "pricing": pricing,
            "rate_limits": {"note": "200 req/day on free tier"},
            "source": "api",
        }
