"""
Config renderers for 5 AI agents.
Each function takes (provider_base_url, model_id, placeholder_key) and returns (filename, content).
"""


def render_opencode(provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    provider_name = "openrouter"
    filename = "opencode.json"
    content = f'''{{
  "$schema": "https://opencode.ai/config.json",
  "provider": {{
    "{provider_name}": {{
      "npm": "@ai-sdk/openai-compatible",
      "name": "OpenRouter",
      "options": {{
        "baseURL": "{provider_base_url}",
        "apiKey": "{key_placeholder}"
      }},
      "models": {{
        "{model_id}": {{ "name": "{model_id}" }}
      }}
    }}
  }},
  "model": "{provider_name}/{model_id}"
}}'''
    return filename, content


def render_hermes(provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    filename = "config.yaml"
    base_url_line = f"  base_url: \"{provider_base_url}\"" if provider_base_url else "  base_url: \"\""
    content = f"""model:
  provider: openrouter
  default: {model_id}
{base_url_line}
  api_key: {key_placeholder}
  api_mode: chat_completions\""""
    return filename, content


def render_openclaw(provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    filename = "openclaw.json5"
    content = f"""\
{{
  models: {{
    mode: "merge",
    providers: {{
      openrouter: {{
        baseUrl: "{provider_base_url}",
        apiKey: "{key_placeholder}",
        models: [
          {{ id: "{model_id}", contextTokens: 131072 }},
        ],
      }},
    }},
  }},
  agents: {{
    defaults: {{ model: {{ primary: "openrouter/{model_id}" }} }},
  }},
}}\""""
    return filename, content


def render_pi(provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    filename = "models.json"
    content = f'''{{
  "providers": {{
    "openrouter": {{
      "baseUrl": "{provider_base_url}",
      "api": "openai-completions",
      "apiKey": "$OPENROUTER_API_KEY",
      "models": [
        {{ "id": "{model_id}", "name": "{model_id}" }}
      ]
    }}
  }}
}}'''
    return filename, content


def render_cline(provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    """Cline is configured via UI, but we provide a text guide."""
    filename = "cline-setup.txt"
    content = f"""Cline Setup — OpenRouter (OpenAI Compatible)

1. Open Cline → Settings (gear icon)
2. API Provider: OpenAI Compatible
3. Base URL: {provider_base_url}
4. API Key: [your OpenRouter key from https://openrouter.ai/keys]
5. Model ID: {model_id}
"""
    return filename, content


def render_kilo(provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    """Kilo Code — kilo.jsonc (JSONC with comments)."""
    filename = "kilo.jsonc"
    content = f"""\
{{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "openrouter/{model_id}",
  "provider": {{
    "openrouter": {{
      "name": "OpenRouter",
      "options": {{
        "baseURL": "{provider_base_url}",
        "apiKey": "{key_placeholder}"
      }},
      "models": {{
        "{model_id}": {{
          "name": "{model_id}"
        }}
      }}
    }}
  }}
}}
// API key via env: OPENROUTER_API_KEY"""
    return filename, content


def render_roocode(provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    """RooCode — roo-code-settings.json."""
    filename = "roo-code-settings.json"
    content = f"""\
{{
  "apiProviderProfiles": {{
    "openrouter": {{
      "apiProvider": "openrouter",
      "apiKey": "{key_placeholder}",
      "modelId": "{model_id}"
    }}
  }}
}}
"""
    return filename, content


RENDERERS = {
    "opencode": render_opencode,
    "hermes": render_hermes,
    "openclaw": render_openclaw,
    "pi": render_pi,
    "cline": render_cline,
    "kilo": render_kilo,
    "roocode": render_roocode,
}
