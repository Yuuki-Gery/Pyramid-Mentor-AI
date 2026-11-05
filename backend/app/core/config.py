from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# 仅用于本地开发。生产环境必须通过环境变量提供独立的强密钥。
DEV_JWT_SECRET_KEY = "dev-only-insecure-secret-do-not-use-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Pyramid Mentor AI"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Chroma
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000

    # LLM
    LLM_PROVIDER: str = "agnes"
    DEFAULT_MODEL: str = "agnes-2.0-flash"

    # Agnes
    AGNES_API_KEY: str = ""
    AGNES_BASE_URL: str = "https://apihub.agnes-ai.com/v1"

    # OpenAI Compatible
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""

    # Claude (reserved; no provider client is implemented yet)
    ANTHROPIC_API_KEY: str = ""

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./pyramid.db"

    # JWT
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # CORS: comma-separated explicit origins. Wildcard is intentionally rejected
    # because the application enables credentialed CORS.
    CORS_ALLOW_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    # Routes used only for local debugging and knowledge ingestion. They are
    # always disabled when ENVIRONMENT=production.
    ENABLE_DEBUG_ENDPOINTS: bool = True

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() in {"production", "prod"}

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_security_settings(self):
        if self.is_production:
            secret = self.JWT_SECRET_KEY.strip()
            if (
                not secret
                or secret == DEV_JWT_SECRET_KEY
                or len(secret) < 32
                or "change" in secret.lower()
            ):
                raise ValueError(
                    "生产环境必须设置 JWT_SECRET_KEY（至少 32 个随机字符），"
                    "且不能使用示例或开发默认值"
                )
        elif not self.JWT_SECRET_KEY:
            # Development stays convenient without silently leaking the same
            # fallback into production; production validation above fails closed.
            self.JWT_SECRET_KEY = DEV_JWT_SECRET_KEY

        origins = self.cors_origins
        if not origins:
            raise ValueError("CORS_ALLOW_ORIGINS 至少需要配置一个来源")
        if "*" in origins:
            raise ValueError(
                "allow_credentials=True 时不能使用通配符 CORS 来源，"
                "请在 CORS_ALLOW_ORIGINS 中填写明确的前端地址"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
