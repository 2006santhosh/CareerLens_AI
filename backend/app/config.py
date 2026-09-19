import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./careerlens.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    ai_mode: str = os.getenv("AI_MODE", "demo")  # "live" or "demo"
    ai_provider: str = os.getenv("AI_PROVIDER", "anthropic")
    ai_model: str = os.getenv("AI_MODEL", "claude-sonnet-4-6")
    ai_api_key: str = os.getenv("AI_API_KEY", "")

    github_token: str = os.getenv("GITHUB_TOKEN", "")

    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_upload_mb: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
os.makedirs(settings.upload_dir, exist_ok=True)
