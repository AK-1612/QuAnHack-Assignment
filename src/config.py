"""
Centralized configuration using Pydantic Settings.
Supports multiple environments (dev, test, prod).
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Travel Itinerary Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    PORT: int = 8000
    WORKERS: int = 4
    LOG_LEVEL: str = "INFO"
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "Travel Itinerary Assistant API"
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./travelai.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Twilio Settings
    TWILIO_ACCOUNT_SID: str = "your_sid"
    TWILIO_AUTH_TOKEN: str = "your_token"
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
    TWILIO_WEBHOOK_URL: str = "https://your-url.ngrok.io/api/v1/webhooks/whatsapp/incoming"
    
    # Gemini API Settings
    GEMINI_API_KEY: str = "your_gemini_key"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_MAX_TOKENS: int = 2000
    GEMINI_TEMPERATURE: float = 0.7
    
    # Email Settings (Optional)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@travelagent.com"
    
    # Security Settings
    SECRET_KEY: str = "supersecretkey"
    API_KEY: str = "your_internal_api_key_for_dashboard"
    API_KEY_HEADER: str = "X-API-Key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Feature Flags
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    ENABLE_SMS_NOTIFICATIONS: bool = False
    ENABLE_CRM_SYNC: bool = False
    ENABLE_BOOKING_INTEGRATION: bool = False
    
    # LLM Caching
    CACHE_LLM_RESPONSES: bool = True
    CACHE_TTL_HOURS: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

settings = get_settings()
