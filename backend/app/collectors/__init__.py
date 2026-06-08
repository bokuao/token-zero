"""
Collector registry — maps provider_id → Collector class.
To add a new provider, just create a file + register here.
"""

from app.collectors.openrouter import OpenRouterCollector
from app.collectors.groq import GroqCollector
from app.collectors.cerebras import CerebrasCollector

REGISTRY = {
    "openrouter": OpenRouterCollector,
    "groq": GroqCollector,
    "cerebras": CerebrasCollector,
    # "gemini": GeminiCollector,    # import + register
}
