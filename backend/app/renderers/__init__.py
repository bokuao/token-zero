"""
Config renderers for 7 AI agents.
Each function takes (provider_id, provider_name, provider_base_url, model_id, placeholder_key) and returns (filename, content).
"""


def render_opencode(provider_id: str, provider_name: str, provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    filename = "opencode.json"
    content = f'''{{
  "$schema": "https://opencode.ai/config.json",
  "provider": {{
    "{provider_id}": {{
      "npm": "@ai-sdk/openai-compatible",
      "name": "{provider_name}",
      "options": {{
        "baseURL": "{provider_base_url}",
        "apiKey": "{key_placeholder}"
      }},
      "models": {{
        "{model_id}": {{ "name": "{model_id}" }}
      }}
    }}
  }},
  "model": "{provider_id}/{model_id}"
}}'''
    return filename, content


def render_hermes(provider_id: str, provider_name: str, provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    filename = "config.yaml"
    base_url_line = f"  base_url: \"{provider_base_url}\"" if provider_base_url else "  base_url: \"\""
    content = f"""model:
  provider: {provider_id}
  default: {model_id}
{base_url_line}
  api_key: {key_placeholder}
  api_mode: chat_completions"""
    return filename, content


def render_openclaw(provider_id: str, provider_name: str, provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    filename = "openclaw.json5"
    content = f"""\\
{{
  models: {{
    mode: "merge",
    providers: {{
      {provider_id}: {{
        baseUrl: "{provider_base_url}",
        apiKey: "{key_placeholder}",
        models: [
          {{ id: "{model_id}", contextTokens: 131072 }},
        ],
      }},
    }},
  }},
  agents: {{
    defaults: {{ model: {{ primary: "{provider_id}/{model_id}" }} }},
  }},
}}"""
    return filename, content


def render_pi(provider_id: str, provider_name: str, provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    filename = "models.json"
    content = f'''{{
  "providers": {{
    "{provider_id}": {{
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


def render_cline(provider_id: str, provider_name: str, provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    """Cline is configured via UI, but we provide a text guide."""
    filename = "cline-setup.txt"
    content = f"""Cline Setup — {provider_name} (OpenAI Compatible)

1. Open Cline → Settings (gear icon)
2. API Provider: OpenAI Compatible
3. Base URL: {provider_base_url}
4. API Key: [your {provider_name} key from {provider_name.lower().replace(' ', '')}.ai/keys]
5. Model ID: {model_id}

"""
    return filename, content


def render_kilo(provider_id: str, provider_name: str, provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    """Kilo Code — kilo.jsonc (JSONC with comments)."""
    filename = "kilo.jsonc"
    content = f"""\\
{{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "{provider_id}/{model_id}",
  "provider": {{
    "{provider_id}": {{
      "name": "{provider_name}",
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


def render_roocode(provider_id: str, provider_name: str, provider_base_url: str, model_id: str, key_placeholder: str) -> tuple[str, str]:
    """RooCode — roo-code-settings.json."""
    filename = "roo-code-settings.json"
    content = f"""\\
{{
  "apiProviderProfiles": {{
    "{provider_id}": {{
      "apiProvider": "{provider_id}",
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