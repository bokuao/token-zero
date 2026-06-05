"""
Collector registry — maps provider_id → Collector class.
To add a new provider, just create a file + register here.
"""

from app.collectors.openrouter import OpenRouterCollector

REGISTRY = {
    "openrouter": OpenRouterCollector,
    # "groq": GroqCollector,        # nanti tinggal uncomment
    # "gemini": GeminiCollector,    # import + register
}
