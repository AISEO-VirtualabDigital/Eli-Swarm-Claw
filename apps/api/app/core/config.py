"""
Application configuration settings.
Loaded from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Eli Claw API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://eliclaw.virtualabdigital.com",
        "https://virtualabdigital.com"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://eliclaw:password@localhost:5432/eliclaw_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Crawler Settings
    CRAWLER_USER_AGENT: str = "EliClawBot/1.0 (+https://eliclaw.virtualabdigital.com/bot)"
    CRAWLER_TIMEOUT: int = 30
    CRAWLER_MAX_PAGES: int = 1000
    CRAWLER_MAX_DEPTH: int = 5
    CRAWLER_DELAY_MS: int = 100
    ALLOWED_FILE_TYPES: List[str] = [".html", ".htm", ".php", ".asp", ".aspx"]
    BLOCKED_FILE_TYPES: List[str] = [".pdf", ".jpg", ".png", ".gif", ".css", ".js", ".zip", ".exe"]
    
    # Security - SSRF Protection
    BLOCK_PRIVATE_IPS: bool = True
    ALLOWED_HOSTS: Optional[List[str]] = None
    
    # Redis (for caching and queues)
    REDIS_URL: Optional[str] = None
    
    # AI/LLM Settings
    LLM_PROVIDER: str = "openai"  # openai, anthropic, google, local
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_TEMPERATURE: float = 0.7
    
    # External APIs (optional)
    INDEXNOW_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_CONSOLE_API_KEY: Optional[str] = None
    
    # Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@eliclaw.virtualabdigital.com"
    
    # Stripe (optional)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
