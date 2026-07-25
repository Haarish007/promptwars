"""
Anchor — Environment-driven configuration.

All secrets and settings are loaded from environment variables (or .env file).
See .env.example for the full list of configuration keys.
Never commit real secrets. Only .env.example (placeholders) is tracked.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── App ──────────────────────────────────────────────────────
    app_env: str = Field(default="development", description="development | staging | production")
    app_name: str = Field(default="anchor")
    api_v1_prefix: str = Field(default="/promptwars/api/v1")
    backend_host: str = Field(default="127.0.0.1")
    backend_port: int = Field(default=8100, ge=1, le=65535)
    log_level: str = Field(default="info")

    # ── CORS / Frontend (Wildcard * allowed) ─────────────────────
    frontend_origin: str = Field(default="*")
    cors_allowed_origins: str = Field(default="*")

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.cors_allowed_origins or self.cors_allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    # ── Database (AWS RDS PostgreSQL) ────────────────────────────
    database_url: str = Field(default="postgresql+asyncpg://localhost:5432/anchor")
    db_pool_size: int = Field(default=10, ge=1)
    db_max_overflow: int = Field(default=20, ge=0)

    # ── Auth / JWT ───────────────────────────────────────────────
    jwt_secret: str = Field(default="CHANGE_ME")
    jwt_algorithm: str = Field(default="HS256")
    access_token_ttl_minutes: int = Field(default=15, gt=0)
    refresh_token_ttl_days: int = Field(default=30, gt=0)
    password_hash_scheme: str = Field(default="argon2id")

    # ── Field-level encryption ───────────────────────────────────
    field_encryption_key: str = Field(default="REPLACE_WITH_BASE64_32BYTE_KEY")

    # ── LLM Provider ─────────────────────────────────────────────
    llm_provider: str = Field(default="gemini")
    gemini_api_key: str = Field(default="REPLACE_WITH_PROVIDER_KEY")
    llm_model: str = Field(default="REPLACE_WITH_MODEL_NAME")
    llm_classifier_model: str = Field(default="REPLACE_WITH_FAST_MODEL_NAME")
    llm_timeout_seconds: int = Field(default=30, gt=0)
    llm_max_retries: int = Field(default=2, ge=0)

    # ── RAG / Knowledge base ─────────────────────────────────────
    rag_top_k: int = Field(default=4, ge=1)
    embeddings_enabled: bool = Field(default=False)

    # ── Safety ────────────────────────────────────────────────────
    safety_fail_mode: str = Field(default="cautious")
    crisis_default_region: str = Field(default="US")

    # ── Rate limiting ─────────────────────────────────────────────
    rate_limit_auth_per_minute: int = Field(default=10, ge=1)
    rate_limit_ai_per_minute: int = Field(default=20, ge=1)
    rate_limit_sos_per_minute: int = Field(default=30, ge=1)

    # ── Notifications ─────────────────────────────────────────────
    nudge_max_per_day: int = Field(default=3, ge=0)

    # ── AWS ────────────────────────────────────────────────────────
    s3_bucket: str = Field(default="pentagonp")
    cloudfront_distribution_id: str = Field(default="d3oe15tpdv4npj.cloudfront.net")
    aws_region: str = Field(default="ap-south-1")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"debug", "info", "warning", "error", "critical"}
        if v.lower() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.lower()

    model_config = {
        "env_file": ("../.env", ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


# Singleton — import this everywhere
settings = Settings()
