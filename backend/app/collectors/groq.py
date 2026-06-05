"""
Groq collector — fetch free models from Groq API.
Endpoint: GET https://api.groq.com/openai/v1/models (auth: Bearer token)
The list endpoint returns context_window + max_completion_tokens — no hardcoded details needed.
Free tier detection uses known model IDs (Groq API has no free/paid signal).
"""

import os
import httpx
from app.collectors.base import CollectorBase

GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"

# Groq API doesn't signal which models are free. We maintain this list manually.
# Source: https://github.com/cheahjs/free-llm-api-resources + Groq docs
KNOWN_FREE_IDS: set[str] = {
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-safeguard-20b",
    "whisper-large-v3",
    "whisper-large-v3-turbo",
    "groq/compound",
    "groq/compound-mini",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-prompt-guard-2-22m",
    "meta-llama/llama-prompt-guard-2-86m",
    "qwen/qwen3-32b",
    "canopylabs/orpheus-arabic-saudi",
    "canopylabs/orpheus-v1-english",
    "allam-2-7b",
}


class GroqCollector(CollectorBase):
    def __init__(self, supabase):
        super().__init__(supabase, "groq")

    def fetch_models(self) -> list[dict]:
        """Fetch all models from Groq API using the operator's API key."""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not found in environment (check .env.enc)")

        with httpx.Client(
            timeout=30,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "TokenZero/1.0 (free-model-directory)",
            },
        ) as client:
            resp = client.get(GROQ_MODELS_URL)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])

    def is_free(self, raw: dict) -> bool:
        """Groq free models are identified by known model IDs."""
        return raw.get("id", "") in KNOWN_FREE_IDS

    def normalize(self, raw: dict) -> dict:
        """Convert Groq model to our schema. All fields from API response."""
        mid = raw.get("id", "")
        ctx = raw.get("context_window")
        max_out = raw.get("max_completion_tokens")

        # Display name: use model ID, strip vendor prefix for cleanliness
        display_name = mid
        if "/" in mid:
            display_name = mid.split("/", 1)[1]
        display_name = display_name.replace("-", " ").replace("_", " ")

        # Capability heuristics (same approach as OpenRouter collector)
        caps = self._derive_capabilities(mid, display_name)

        # Modality heuristics
        mods = self._derive_modalities(mid)

        return {
            "provider_id": "groq",
            "model_id": mid,
            "display_name": display_name,
            "description": None,
            "context_length": ctx,
            "max_output": max_out,
            "input_modalities": mods,
            "capabilities": caps,
            "is_free": True,
            "pricing": {"input_tokens": 0, "output_tokens": 0},
            "rate_limits": {"note": "Free tier: see https://console.groq.com/docs/models for per-model limits"},
            "source": "api",
        }

    @staticmethod
    def _derive_capabilities(mid: str, display_name: str) -> list[str]:
        """Heuristic capability detection from model ID."""
        caps = []
        text = (mid + " " + display_name).lower()

        # Coding
        if any(kw in text for kw in ["coder", "code", "gpt-oss", "compound", "qwen3"]):
            caps.append("coding")
        # Reasoning
        if any(kw in text for kw in ["reasoning", "r1", "think", "qwq", "gpt-oss", "compound", "qwen3"]):
            caps.append("reasoning")
        # Vision
        if any(kw in text for kw in ["vision", "visual", "scout", "vl", "multimodal", "llava"]):
            caps.append("vision")

        # "text" always last
        caps.append("text")
        return caps

    @staticmethod
    def _derive_modalities(mid: str) -> list[str]:
        """Heuristic modality detection from model ID."""
        mid_lower = mid.lower()
        # Audio models (speech-to-text / text-to-speech)
        if "whisper" in mid_lower or "orpheus" in mid_lower:
            return ["audio"]
        # Vision-capable models
        if "scout" in mid_lower:
            return ["text", "image"]
        # Default: text-only
        return ["text"]
