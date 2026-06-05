from pydantic_settings import BaseSettings, SettingsConfigDict

# Decrypt .env.enc ke memory dulu (sebelum Settings init)
from app.sops_decrypt import load_sops_env

load_sops_env()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""

    # CORS
    cors_origins: str = "*"

    # Rate limit
    rate_limit: str = "60/minute"

    # Operator keys
    groq_api_key: str = ""
    gemini_api_key: str = ""
    cerebras_api_key: str = ""
    mistral_api_key: str = ""
    nvidia_api_key: str = ""
    cohere_api_key: str = ""
    github_models_token: str = ""
    cloudflare_api_token: str = ""


settings = Settings()
